"""
test_smoke.py — Uji cepat kebenaran implementasi (jalankan sebelum training).

  python test_smoke.py            # semua uji (mengunduh yolo26s.pt ~19MB sekali)
  python test_smoke.py --no-net   # lewati uji yang butuh unduhan bobot

Yang diverifikasi:
  T1  Matematika density_weights vs perhitungan manual (Pers 3.2-3.4).
  T2  Empat arsitektur terbangun: baseline, HAM, P2 resmi, HAM+P2 (register HAM,
      remap indeks head, kanal HAM cocok dengan runtime).
  T3  Transfer bobot COCO ke varian HAM (remap indeks) & P2 — laporan % cocok.
  T4  Loss end-to-end: patch DALW aktif pada E2ELoss; batch padat -> loss naik
      dibanding tanpa DALW; citra 1-objek -> identik (w=1).
"""

from __future__ import annotations

import argparse
import math
import sys

import torch

from y26_modules import register_ham
from y26_dalw import DALWDetectionLoss, apply_dalw, density_weights, set_dalw_params
from y26_variants import VARIANTS, build_model, generate_ham_yaml, transfer_pretrained

OK = "\033[92mLULUS\033[0m"


def t1_math():
    # dua objek berimpit: rho=1 -> rho_hat=0.5 -> w=1+0.5a
    c = torch.tensor([[[0.5, 0.5], [0.5, 0.5]]])
    v = torch.ones(1, 2, dtype=torch.bool)
    w = density_weights(c, v, alpha=2.0, sigma=0.1)
    assert torch.allclose(w, torch.tensor([[2.0, 2.0]]), atol=1e-5), w
    # objek tunggal: rho=0 -> w=1
    w1 = density_weights(torch.tensor([[[0.3, 0.7]]]), torch.ones(1, 1, dtype=torch.bool), 2.0, 0.1)
    assert torch.allclose(w1, torch.ones(1, 1)), w1
    # dua objek berjarak d: rho = exp(-d^2/2s^2)
    d, s = 0.1, 0.1
    c2 = torch.tensor([[[0.2, 0.5], [0.2 + d, 0.5]]])
    rho = math.exp(-(d**2) / (2 * s * s))
    w2 = density_weights(c2, torch.ones(1, 2, dtype=torch.bool), 1.0, s)
    assert torch.allclose(w2, torch.full((1, 2), 1 + rho / (rho + 1)), atol=1e-5), w2
    # slot padding tidak memengaruhi & berbobot 1
    c3 = torch.tensor([[[0.5, 0.5], [0.5, 0.5], [0.0, 0.0]]])
    v3 = torch.tensor([[True, True, False]])
    w3 = density_weights(c3, v3, 2.0, 0.1)
    assert torch.allclose(w3, torch.tensor([[2.0, 2.0, 1.0]]), atol=1e-5), w3
    print(f"T1 matematika DALW (Pers 3.2-3.4) ... {OK}")


def t2_build():
    import ultralytics.nn.tasks as tasks
    from ultralytics import YOLO

    register_ham()
    m_base = tasks.DetectionModel(cfg="yolo26s.yaml", ch=3, nc=4, verbose=False)
    p_base = sum(p.numel() for p in m_base.parameters())

    ham_cfg = generate_ham_yaml(p2=False, scale="s", nc=4, out_dir="cfg")
    m_ham = tasks.DetectionModel(cfg=ham_cfg, ch=3, nc=4, verbose=False)
    p_ham = sum(p.numel() for p in m_ham.parameters())
    n_ham = sum(1 for m in m_ham.modules() if type(m).__name__ == "HAM")
    assert n_ham == 2, f"HAM terpasang {n_ham} kali (harus 2: tahap-3 & tahap-4)"
    assert p_ham > p_base, "parameter varian HAM harus > baseline"

    y_p2 = YOLO("yolo26s-p2.yaml")
    hamp2_cfg = generate_ham_yaml(p2=True, scale="s", nc=4, out_dir="cfg")
    y_hp = YOLO(hamp2_cfg)
    assert sum(1 for m in y_hp.model.modules() if type(m).__name__ == "HAM") == 2
    # jumlah skala deteksi
    det_b = m_base.model[-1]
    det_p2 = y_p2.model.model[-1]
    assert len(det_b.stride) == 3 and len(det_p2.stride) == 4, (det_b.stride, det_p2.stride)
    assert int(det_p2.stride.min()) == 4, f"stride minimum P2 harus 4, dapat {det_p2.stride}"
    print(
        f"T2 arsitektur: base {p_base/1e6:.2f}M | HAM {p_ham/1e6:.2f}M (+{(p_ham-p_base)/1e3:.1f}K) | "
        f"P2 stride {det_p2.stride.int().tolist()} | HAM+P2 ok ... {OK}"
    )
    return m_ham, y_hp


def _fake_official(path: str = "_fake_yolo26s.pt") -> str:
    """Checkpoint tiruan berbentuk IDENTIK dengan yolo26s.pt (nc=80) untuk menguji
    mekanisme remap/transfer saat unduhan resmi tidak tersedia (mis. sandbox)."""
    import os

    import ultralytics.nn.tasks as tasks

    if not os.path.exists(path):
        m = tasks.DetectionModel(cfg="yolo26s.yaml", ch=3, nc=80, verbose=False)
        torch.save({"model": m, "train_args": {}}, path)
    return path


def t3_transfer():
    from ultralytics import YOLO

    wsrc, note = None, ""
    try:
        from y26_variants import _official_state_dict

        _official_state_dict("yolo26s.pt")
    except Exception:
        wsrc = _fake_official()
        note = " [sandbox: bobot tiruan berbentuk identik; di PC Anda bobot resmi terunduh otomatis]"

    src, rep = build_model("V2", scale="s", nc=4, workdir=".", weights=wsrc)  # HAM
    assert rep["fraction"] > 0.55, f"transfer HAM terlalu rendah: {rep}"
    y2 = YOLO(src)  # init checkpoint terbaca kembali
    src3, rep3 = build_model("V3", scale="s", nc=4, workdir=".", weights=wsrc)  # P2 resmi
    # Head Detect 4-skala + seluruh cabang P2 adalah lapisan BARU (init segar),
    # sehingga ~35-45% kunci wajar; backbone/neck awal tetap tertransfer penuh.
    assert rep3["fraction"] > 0.35, f"transfer P2 terlalu rendah: {rep3}"
    src8, rep8 = build_model("V8", scale="s", nc=4, workdir=".", weights=wsrc)  # HAM+P2
    pf = lambda r: f"{r['fraction']:.0%} kunci/{r['param_fraction']:.0%} param"
    print(
        f"T3 transfer bobot COCO -> HAM {pf(rep)} | P2 {pf(rep3)} | "
        f"HAM+P2 {pf(rep8)} (lapisan baru init segar){note} ... {OK}"
    )


def _fake_batch(n_dense: int, device):
    """Batch sintetis 1 citra: n_dense objek bergerombol di tengah."""
    g = torch.Generator().manual_seed(0)
    cx = 0.5 + 0.03 * torch.randn(n_dense, generator=g)
    cy = 0.5 + 0.03 * torch.randn(n_dense, generator=g)
    wh = torch.full((n_dense, 2), 0.08)
    bboxes = torch.stack([cx, cy, wh[:, 0], wh[:, 1]], 1).clamp(0.02, 0.98)
    return {
        "img": torch.rand(1, 3, 128, 128, generator=g).to(device),
        "batch_idx": torch.zeros(n_dense).to(device),
        "cls": torch.zeros(n_dense, 1).to(device),
        "bboxes": bboxes.to(device),
    }


def t4_loss():
    import ultralytics.nn.tasks as tasks
    from ultralytics.cfg import get_cfg
    from ultralytics.utils.loss import E2ELoss

    register_ham()
    device = "cpu"

    def build(nc=1):
        m = tasks.DetectionModel(cfg="yolo26s.yaml", ch=3, nc=nc, verbose=False)
        m.args = get_cfg()
        m.train()  # head end2end mengembalikan dict {'one2many','one2one'} saat mode train
        return m

    orig_init = tasks.DetectionModel.init_criterion
    torch.manual_seed(0)
    m_plain = build()
    batch_dense = _fake_batch(12, device)
    batch_single = _fake_batch(1, device)
    with torch.no_grad():
        v_plain_dense = m_plain.loss(batch_dense)[0]  # vektor [box, cls, dfl]
        v_plain_single = m_plain.loss(batch_single)[0]

    apply_dalw(alpha=2.0, sigma=0.10)
    torch.manual_seed(0)
    m_dalw = build()
    crit = m_dalw.init_criterion()
    assert isinstance(crit, E2ELoss), "patch harus tetap E2ELoss (ProgLoss utuh)"
    assert isinstance(crit.one2one, DALWDetectionLoss) and isinstance(crit.one2many, DALWDetectionLoss)
    with torch.no_grad():
        v_dalw_dense = m_dalw.loss(batch_dense)[0]
        v_dalw_single = m_dalw.loss(batch_single)[0]

    tasks.DetectionModel.init_criterion = orig_init  # bersihkan patch
    # Komponen box (indeks 0) sepenuhnya foreground -> harus naik jelas pada batch padat
    assert v_dalw_dense[0] > v_plain_dense[0] * 1.15, (v_plain_dense, v_dalw_dense)
    # Komponen cls juga naik (bagian foreground terbobot)
    assert v_dalw_dense[1] >= v_plain_dense[1], (v_plain_dense, v_dalw_dense)
    # Citra 1 objek: w = 1 -> identik pada semua komponen
    assert torch.allclose(v_dalw_single, v_plain_single, rtol=1e-4), (v_plain_single, v_dalw_single)
    print(
        f"T4 loss E2E: box padat {v_plain_dense[0]:.3f} -> {v_dalw_dense[0]:.3f} (w>1) | "
        f"1-objek identik (w=1) | ProgLoss+STAL utuh ... {OK}"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-net", action="store_true", help="lewati uji yang mengunduh bobot")
    a = ap.parse_args()
    t1_math()
    t2_build()
    if not a.no_net:
        t3_transfer()
    t4_loss()
    print("\nSemua uji lulus — implementasi konsisten dengan Persamaan 3.2-3.5 dan siap training.")
