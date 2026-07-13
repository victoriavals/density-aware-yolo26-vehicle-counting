"""
test_eval.py — Uji kebenaran evaluasi Tahap 3.

  python test_eval.py

  E1  Atribut strata (ukuran/oklusi/densitas) bernilai pasti.
  E2  Mesin AP 101-titik pada kasus hitung-tangan.
  E3  Protokol ignore strata: cocok-ke-GT-luar-strata tidak dihukum FP.
  E4  Holm step-down pada contoh baku + Wilcoxon konsisten dgn scipy.
  E5  Metrik counting (MAE/RMSE/MAPE + aturan y>0) bernilai pasti.
  E6  Pipeline counting: video sintetis + detektor palsu -> jumlah lintasan pasti.
  E7  Integrasi strata pada dataset mini + model acak (jalur penuh).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np
import torch

from y26_stats import holm, run_wilcoxon_suite, wilcoxon_pair
from y26_strata import (DEN_EDGES, OCC_EDGES, _ap101, collect_cache, gt_attributes,
                        stratified_ap)
from y26_counting import counting_metrics, run_counting

OK = "\033[92mLULUS\033[0m"


def e1_attrs():
    # img0: kotak 20x20 (small) & 100x100 (large) tumpang tindih 50%-an; img1: 40x40 (medium)
    gt = np.array([
        [0, 0, 0, 20, 20, 0],
        [0, 10, 10, 110, 110, 1],
        [1, 0, 0, 40, 40, 0],
    ], np.float32)
    A = gt_attributes(gt, n_images=2)
    assert A["size_t"].tolist() == [0, 2, 1], A["size_t"]
    inter, uni = 10 * 10, 20 * 20 + 100 * 100 - 100
    assert abs(A["occ"][0] - inter / uni) < 1e-6 and A["occ"][2] == 0.0
    assert A["occ_t"].tolist() == [0, 0, 0]  # IoU ~0.0097 < 0.10 -> 'no'
    assert A["count"].tolist() == [2, 1] and A["den_t"].tolist() == [0, 0]
    # densitas: 12 objek -> medium; 30 -> dense
    gt2 = np.concatenate([np.array([[0, i, 0, i + 5, 5, 0] for i in range(12)], np.float32),
                          np.array([[1, i, 0, i + 5, 5, 0] for i in range(30)], np.float32)])
    A2 = gt_attributes(gt2, 2)
    assert A2["den_t"].tolist() == [1, 2]  # 12 objek -> medium; 30 -> dense (per-citra)
    print(f"E1 atribut strata (Pers. 3.1, COCO, tier densitas) ... {OK}")


def e2_ap():
    # 2 GT; deteksi: FP(0.9), TP(0.8), TP(0.7) -> AP101 = 2/3
    conf = np.array([0.9, 0.8, 0.7]); tp = np.array([0.0, 1.0, 1.0]); ig = np.zeros(3, bool)
    ap = _ap101(conf, tp, ig, n_pos=2)
    assert abs(ap - 2 / 3) < 0.01, ap
    assert _ap101(conf, np.array([1.0, 1.0, 0.0]), ig, 2) > 0.99  # sempurna
    assert np.isnan(_ap101(conf, tp, ig, 0))
    print(f"E2 mesin AP 101-titik (kasus hitung-tangan) ... {OK}")


def _mk_cache(pred_rows, gt_rows, n_images):
    return dict(pred=np.array(pred_rows, np.float32).reshape(-1, 7),
                gt=np.array(gt_rows, np.float32).reshape(-1, 6),
                names=np.array([f"{i}.jpg" for i in range(n_images)], object),
                n_images=n_images, imgsz=640)


def e3_ignore():
    # img0: GT large (100x100) + GT small (20x20). Deteksi sempurna keduanya.
    gt = [[0, 200, 200, 300, 300, 0], [0, 10, 10, 30, 30, 0]]
    pred = [[0, 200, 200, 300, 300, 0.9, 0], [0, 10, 10, 30, 30, 0.8, 0]]
    rows = stratified_ap(_mk_cache(pred, gt, 1), ["car"])
    r = {(x["dim"], x["stratum"]): x for x in rows}
    assert r[("global", "all")]["ap50"] > 0.99
    # strata LARGE: GT small ignore; deteksi small tercocok ke GT ignore -> di-ignore, AP=1
    assert r[("size", "large")]["n_gt"] == 1 and r[("size", "large")]["ap50"] > 0.99
    assert r[("size", "small")]["n_gt"] == 1 and r[("size", "small")]["ap50"] > 0.99
    # deteksi hantu kecil TAK tercocok: di-ignore pada strata large (filter area), FP pada global
    pred2 = pred + [[0, 50, 50, 68, 68, 0.95, 0]]
    rows2 = stratified_ap(_mk_cache(pred2, gt, 1), ["car"])
    r2 = {(x["dim"], x["stratum"]): x for x in rows2}
    assert r2[("size", "large")]["ap50"] > 0.99, "unmatched det kecil harus di-ignore di strata large"
    assert r2[("global", "all")]["ap50"] < 0.99, "pada global, det hantu = FP"
    print(f"E3 protokol ignore strata (gaya COCO) ... {OK}")


def e4_stats():
    adj = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert abs(adj["a"] - 0.03) < 1e-9 and abs(adj["c"] - 0.06) < 1e-9 and abs(adj["b"] - 0.06) < 1e-9
    rng = np.random.default_rng(0)
    x = rng.normal(0.6, 0.1, 30); y = x - rng.normal(0.03, 0.02, 30)
    from scipy.stats import wilcoxon as sw

    r = wilcoxon_pair(x, y)
    ref = sw(x, y, zero_method="wilcox")
    assert abs(r["p"] - ref.pvalue) < 1e-12 and r["n_eff"] == 30
    x2 = x.copy(); x2[:3] = np.nan
    assert wilcoxon_pair(x2, y)["n"] == 27  # pasangan NaN dibuang
    assert wilcoxon_pair(y, y)["p"] == 1.0  # semua selisih nol
    # suite: V8 unggul konsisten -> primer signifikan
    rows_v1 = [dict(cls="c", dim="size", stratum=s, n_gt=10, ap50=0.5, ap5095=0.40 + 0.01 * i)
               for i, s in enumerate(["small", "medium", "large"])]
    for extra_dim in ("occlusion", "density"):
        rows_v1 += [dict(cls="c", dim=extra_dim, stratum=s, n_gt=10, ap50=0.5, ap5095=0.42)
                    for s in ("a", "b", "c")]
    rows_v8 = [dict(r, ap5095=r["ap5095"] + 0.05) for r in rows_v1]
    res = run_wilcoxon_suite({"V1": rows_v1, "V8": rows_v8})
    pri = [r for r in res if r["family"] == "primary"]
    assert len(pri) == 1 and pri[0]["signif_5pct"] and pri[0]["median_diff"] > 0
    print(f"E4 Wilcoxon + Holm (konsisten scipy, suite utama/sekunder) ... {OK}")


def e5_count_metrics():
    pred = {(0, "car", "in"): 4, (1, "car", "in"): 2}
    gt = {(0, "car", "in"): 5, (1, "car", "in"): 0}
    m = counting_metrics(pred, gt)
    assert m["T"] == 2 and abs(m["MAE"] - 1.5) < 1e-9
    assert abs(m["RMSE"] - np.sqrt((1 + 4) / 2)) < 1e-9
    assert abs(m["MAPE"] - 20.0) < 1e-9 and m["mape_excluded"] == 1 and m["mape_excluded_frac"] == 0.5
    print(f"E5 metrik counting (MAE/RMSE/MAPE, aturan y>0) ... {OK}")


def e6_count_pipeline():
    tmp = Path(tempfile.mkdtemp())
    try:
        vid = tmp / "syn.mp4"
        W, H, fps, N = 320, 240, 10.0, 40
        vw = cv2.VideoWriter(str(vid), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
        if not vw.isOpened():
            vid = tmp / "syn.avi"
            vw = cv2.VideoWriter(str(vid), cv2.VideoWriter_fourcc(*"MJPG"), fps, (W, H))
        for _ in range(N):
            vw.write(np.zeros((H, W, 3), np.uint8))
        vw.release()

        def fake_detector(frame, _s=[0]):
            f = _s[0]; _s[0] += 1
            y = 20 + f * 5  # dua objek bergerak turun melintasi garis y=120
            return (np.array([[40, y, 90, y + 40], [180, y, 230, y + 40]], np.float32),
                    np.array([0.9, 0.85], np.float32), np.array([0, 1]))

        s = run_counting(vid, detector=fake_detector, names={0: "car", 1: "two-wheeler", 2: "pedestrian"},
                         line=(0, 120, W - 1, 120), interval_s=2, out_dir=str(tmp / "out"))
        tot = sum(v for k, v in s["totals"].items())
        assert tot == 2, s["totals"]  # tiap objek melintas tepat sekali
        assert (tmp / "out" / "counts_per_interval.csv").exists()
        # pejalan kaki dikecualikan
        def ped_det(frame, _s=[0]):
            f = _s[0]; _s[0] += 1
            y = 20 + f * 5
            return (np.array([[40, y, 90, y + 40]], np.float32),
                    np.array([0.9], np.float32), np.array([2]))
        s2 = run_counting(vid, detector=ped_det, names={0: "car", 2: "pedestrian"},
                          line=(0, 120, W - 1, 120), out_dir=str(tmp / "out2"))
        assert sum(s2["totals"].values()) == 0, s2["totals"]
        print(f"E6 pipeline counting (video sintetis, lintasan pasti, eksklusi pedestrian) ... {OK}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def e7_integration():
    root = Path(tempfile.mkdtemp()) / "mini"
    try:
        for split in ("test",):
            (root / split / "images").mkdir(parents=True)
            (root / split / "labels").mkdir(parents=True)
            rng = np.random.default_rng(0)
            for i in range(6):
                cv2.imwrite(str(root / split / "images" / f"{i}.jpg"),
                            (rng.random((320, 416, 3)) * 255).astype(np.uint8))
                n = [2, 5, 12, 27, 3, 30][i]
                lines = [f"{k % 4} {0.1 + 0.8 * rng.random():.3f} {0.1 + 0.8 * rng.random():.3f} 0.08 0.10"
                         for k in range(n)]
                (root / split / "labels" / f"{i}.txt").write_text("\n".join(lines))
        (root / "data.yaml").write_text(
            f"path: {root}\ntest: test/images\nnc: 4\nnames: [two-wheeler, car, big-vehicle, pedestrian]\n")
        from ultralytics import YOLO

        cache = collect_cache(YOLO("yolo26s.yaml"), str(root / "data.yaml"), split="test", batch=3)
        assert cache["n_images"] == 6 and len(cache["gt"]) == 79
        rows = stratified_ap(cache, ["two-wheeler", "car", "big-vehicle", "pedestrian"])
        dims = {r["dim"] for r in rows}
        assert dims == {"global", "size", "occlusion", "density"}
        dens = {r["stratum"]: r["n_gt"] for r in rows if r["dim"] == "density" and r["cls"] == "two-wheeler"}
        assert set(dens) == {"sparse", "medium", "dense"}
        assert all(np.isfinite(r["ap50"]) or r["n_gt"] == 0 for r in rows)
        print(f"E7 integrasi strata (dataset mini, {len(rows)} sel) ... {OK}")
    finally:
        shutil.rmtree(root.parent, ignore_errors=True)


if __name__ == "__main__":
    e1_attrs(); e2_ap(); e3_ignore(); e4_stats(); e5_count_metrics(); e6_count_pipeline(); e7_integration()
    print("\nSemua uji Tahap 3 lulus — evaluasi terstratifikasi, Wilcoxon, dan counting siap.")
