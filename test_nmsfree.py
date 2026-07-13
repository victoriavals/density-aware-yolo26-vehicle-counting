"""
test_nmsfree.py — Uji kebenaran instrumentasi NMS-free (Tahap 2).

  python test_nmsfree.py

  U1  Matcher + DR/CM pada kasus sintetis bernilai pasti (Pers. 3.6-3.7).
  U2  Rumus stabilitas S(t), termasuk konvensi ∅==∅.
  U3  train_format_forward: dict dual-head TANPA mengubah statistik BN.
  U4  Ekstraksi assignment one-to-one: deterministik -> S=1.0 pada bobot sama.
  U5  Pipeline evaluate_dr_cm end-to-end pada dataset mini sintetis di disk.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch

from y26_nmsfree import (DRCMAccumulator, NMSFreeProbe, extract_o2o_assignments, evaluate_dr_cm,
                         load_probe, match_predictions, stability, train_format_forward)

OK = "\033[92mLULUS\033[0m"


def u1_matcher():
    gt = np.array([[10, 10, 50, 50], [100, 100, 160, 160]], np.float32)
    gcls = np.array([0, 1], np.float32)
    # p0,p1 duplikat di gt0 (conf .9/.6); p2 di gt1 (.8); p3 IoU rendah (bg); p4 kelas salah di gt1
    pred = np.array([[11, 11, 51, 51], [8, 12, 49, 52], [101, 99, 159, 161], [300, 300, 340, 340],
                     [100, 100, 160, 160]], np.float32)
    pcls = np.array([0, 0, 1, 0, 0], np.float32)
    conf = torch.tensor([0.9, 0.6, 0.8, 0.7, 0.95])
    m = match_predictions(pred, pcls, gt, gcls, iou_thr=0.5, class_aware=True)
    assert m.tolist() == [0, 0, 1, -1, -1], m.tolist()
    acc = DRCMAccumulator(taus=[0.25, 0.7], tau_main=0.25)
    acc.update(m, conf, n_gt=2, name="img0")
    s = acc.summary()
    assert abs(s["DR"] - 1.5) < 1e-6 and s["miss_frac"] == 0.0 and s["dup_frac"] == 0.5, s
    assert abs(s["taus"]["0.7"]["DR"] - 1.0) < 1e-6, s["taus"]  # τ=0.7: hanya .9 & .8 lolos
    # CM: gt0 = .9-.6 = .3 ; gt1 = .8-0 = .8 -> mean .55
    assert abs(s["cm_mean"] - 0.55) < 1e-6 and s["coverage"] == 1.0, s
    # citra tanpa GT tidak mengubah M
    acc.update(match_predictions(pred, pcls, np.zeros((0, 4), np.float32), np.zeros(0), 0.5, True),
               conf, n_gt=0)
    assert acc.summary()["M"] == 2
    print(f"U1 matcher & DR/CM (nilai pasti) ... {OK}")


def u2_stability():
    keys = {(0, 0), (0, 1), (1, 0)}
    prev = {(0, 0): 10, (0, 1): 55}            # (1,0) = ∅
    cur1 = {(0, 0): 10, (0, 1): 55}            # ∅==∅ -> 3/3
    cur2 = {(0, 0): 10, (0, 1): 99, (1, 0): 7} # 1 sama, 1 beda, ∅->7 beda
    assert stability(prev, cur1, keys) == 1.0
    assert abs(stability(prev, cur2, keys) - 1 / 3) < 1e-9
    assert stability(None, cur1, keys) != stability(None, cur1, keys)  # NaN pada epoch pertama
    print(f"U2 rumus stabilitas S(t) (A-10, konvensi ∅) ... {OK}")


def _tiny_model(nc=1):
    import ultralytics.nn.tasks as tasks
    from ultralytics.cfg import get_cfg

    torch.manual_seed(0)
    m = tasks.DetectionModel(cfg="yolo26s.yaml", ch=3, nc=nc, verbose=False)
    m.args = get_cfg()
    m.eval()
    return m


def u3_internal_forward():
    m = _tiny_model()
    bn = next(mm for mm in m.model[-1].modules() if isinstance(mm, torch.nn.BatchNorm2d))
    before = bn.running_mean.clone()
    out = train_format_forward(m, torch.rand(2, 3, 128, 128))
    assert isinstance(out, dict) and {"one2many", "one2one"} <= set(out), type(out)
    assert torch.equal(bn.running_mean, before), "statistik BN berubah — trik flag gagal!"
    assert m.training is False and m.model[-1].training is False, "mode tidak dipulihkan"
    print(f"U3 forward internal dual-head, BN utuh ... {OK}")


def _fake_probe_batch(n_img=2, n_obj=6):
    g = torch.Generator().manual_seed(1)
    bidx, cls, bb = [], [], []
    for i in range(n_img):
        c = 0.5 + 0.05 * torch.randn(n_obj, 2, generator=g)
        wh = torch.full((n_obj, 2), 0.10)
        for j in range(n_obj):
            bidx.append(i); cls.append([0.0])
            bb.append([c[j, 0].item(), c[j, 1].item(), wh[j, 0].item(), wh[j, 1].item()])
    return dict(img=torch.rand(n_img, 3, 128, 128, generator=g),
                batch_idx=torch.tensor(bidx, dtype=torch.float32),
                cls=torch.tensor(cls), bboxes=torch.tensor(bb).clamp(0.05, 0.95))


def u4_assignment():
    m = _tiny_model()
    batch = _fake_probe_batch()
    a1, s1 = extract_o2o_assignments(m, batch)
    a2, _ = extract_o2o_assignments(m, batch)
    keys = {(i, k) for i in range(2) for k in range(6)}
    assert s1["assigned_frac"] > 0.5, s1
    assert s1["anchors_per_gt"] <= 2.0, f"one-to-one seharusnya ~1 anchor/GT: {s1}"
    assert stability(a1, a2, keys) == 1.0, "bobot identik harus 100% stabil"
    print(f"U4 assignment one-to-one: assigned={s1['assigned_frac']:.0%}, "
          f"{s1['anchors_per_gt']:.2f} anchor/GT, deterministik S=1.0 ... {OK}")


def u5_pipeline():
    root = Path(tempfile.mkdtemp()) / "mini"
    try:
        import cv2

        for split in ("valid", "test"):
            (root / split / "images").mkdir(parents=True)
            (root / split / "labels").mkdir(parents=True)
            for i in range(4):
                img = (np.random.rand(320, 416, 3) * 255).astype(np.uint8)
                cv2.imwrite(str(root / split / "images" / f"{i}.jpg"), img)
                (root / split / "labels" / f"{i}.txt").write_text(
                    "0 0.30 0.40 0.20 0.25\n1 0.70 0.60 0.18 0.22\n")
        (root / "data.yaml").write_text(
            f"path: {root}\ntrain: valid/images\nval: valid/images\ntest: test/images\n"
            "nc: 4\nnames: [two-wheeler, car, big-vehicle, pedestrian]\n")

        from ultralytics import YOLO

        model = YOLO("yolo26s.yaml")  # bobot acak: cukup untuk uji jalur pipeline
        acc = evaluate_dr_cm(model, str(root / "data.yaml"), split="test", tau_main=0.25, batch=2)
        s = acc.summary()
        assert s["images"] == 4 and s["M"] == 8 and 0 <= s["miss_frac"] <= 1, s
        assert len(acc.per_image) == 4 and np.isfinite(s["DR"]), s

        # probe loader: koordinat letterbox konsisten
        b, gt_px, _ = load_probe(str(root / "data.yaml"), split="val", n=4)
        assert b["img"].shape == (4, 3, 640, 640) and b["bboxes"].shape == (8, 4)
        assert all(len(g) == 2 for g, _ in gt_px)
        print(f"U5 pipeline penuh (dataset mini): DR={s['DR']:.3f}, miss={s['miss_frac']:.2f} ... {OK}")
    finally:
        shutil.rmtree(root.parent, ignore_errors=True)


if __name__ == "__main__":
    u1_matcher()
    u2_stability()
    u3_internal_forward()
    u4_assignment()
    u5_pipeline()
    print("\nSemua uji Tahap 2 lulus — instrumentasi NMS-free siap dipakai.")
