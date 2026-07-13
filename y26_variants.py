"""
y26_variants.py — Pembangkit arsitektur varian ablasi & transfer bobot pralatih.

Delapan varian sesuai Tabel 3.3 tesis (full factorial HAM x P2 x DALW):
    V1 baseline | V2 HAM | V3 P2 | V4 DALW | V5 HAM+P2 | V6 HAM+DALW
    V7 P2+DALW  | V8 model penuh

Desain:
- Varian P2 memakai arsitektur RESMI ultralytics (yolo26-p2.yaml) — lebih kuat
  dipertahankan di sidang daripada YAML buatan sendiri.
- Varian HAM dibangkitkan PROGRAMATIS dari YAML resmi terpasang: HAM disisipkan
  setelah blok C3k2 tahap-3 (indeks 4, fitur P3/8) dan tahap-4 (indeks 6, fitur
  P4/16) sesuai Subbab 3.6.1, lalu seluruh rujukan indeks absolut pada head
  dipetakan ulang; rujukan ke keluaran tahap 3/4 dialihkan ke keluaran HAM agar
  fitur yang termodulasi atensi-lah yang mengalir ke neck (Gambar 3.2 tesis).
- Keadilan ablasi: semua varian diinisialisasi dari bobot COCO yolo26{scale}.pt
  pada lapisan yang bersesuaian; lapisan baru (HAM, cabang head P2) terinisialisasi
  segar — praktik yang sama dengan CRL-YOLOv5/MST-YOLO/HIC-YOLOv5 [11]-[13].
  Pergeseran indeks akibat sisipan HAM ditangani pemetaan ulang nama parameter
  sehingga transfer tidak gugur karena perubahan penomoran layer.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path

import torch
import yaml

from y26_modules import register_ham

# ---------------------------------------------------------------- registry
VARIANTS: dict[str, dict] = {
    "V1": dict(ham=False, p2=False, dalw=False, desc="Baseline YOLO26"),
    "V2": dict(ham=True, p2=False, dalw=False, desc="Hanya HAM"),
    "V3": dict(ham=False, p2=True, dalw=False, desc="Hanya P2"),
    "V4": dict(ham=False, p2=False, dalw=True, desc="Hanya Density-Aware"),
    "V5": dict(ham=True, p2=True, dalw=False, desc="HAM + P2"),
    "V6": dict(ham=True, p2=False, dalw=True, desc="HAM + Density-Aware"),
    "V7": dict(ham=False, p2=True, dalw=True, desc="P2 + Density-Aware"),
    "V8": dict(ham=True, p2=True, dalw=True, desc="Model penuh yang diusulkan"),
}

_INSERT_AFTER = (4, 6)  # blok C3k2 tahap-3 (P3/8) dan tahap-4 (P4/16)


def _official_cfg_dir() -> Path:
    import ultralytics

    return Path(ultralytics.__file__).parent / "cfg" / "models" / "26"


def _make_divisible(x: float, divisor: int = 8) -> int:
    import math

    return max(divisor, int(math.ceil(x / divisor) * divisor))


def _new_index(i: int, insert_after=_INSERT_AFTER) -> int:
    return i + sum(1 for p in insert_after if i > p)


def _ham_positions(insert_after=_INSERT_AFTER) -> dict[int, int]:
    return {p: _new_index(p, insert_after) + 1 for p in insert_after}


def _map_ref(v, redirect: dict[int, int]):
    if isinstance(v, int) and v >= 0:
        return redirect.get(v, _new_index(v))
    return v


def generate_ham_yaml(p2: bool, scale: str = "s", nc: int = 4, out_dir: str = "cfg") -> str:
    """Bangkitkan YAML varian ber-HAM dari YAML resmi terpasang. Return path keluaran."""
    src = _official_cfg_dir() / ("yolo26-p2.yaml" if p2 else "yolo26.yaml")
    d = yaml.safe_load(src.read_text())

    bb = d["backbone"]
    # Penjaga struktur: pastikan titik sisip masih sesuai (antisipasi drift versi)
    for conv_i, c3_i in ((3, 4), (5, 6)):
        assert bb[conv_i][2] == "Conv" and bb[conv_i][3][2] == 2, f"layer {conv_i} bukan Conv stride-2"
        assert bb[c3_i][2] == "C3k2", f"layer {c3_i} bukan C3k2 — struktur yolo26.yaml berubah"

    depth, width, max_ch = d["scales"][scale]
    redirect = _ham_positions()

    # Sisipkan HAM (dari belakang agar indeks sumber tidak bergeser saat insert)
    new_bb = copy.deepcopy(bb)
    for p in sorted(_INSERT_AFTER, reverse=True):
        c_out_yaml = bb[p][3][0]  # kanal keluaran blok yang dibungkus (skala YAML)
        c1 = _make_divisible(min(c_out_yaml, max_ch) * width)  # kanal aktual pasca-scaling
        new_bb.insert(p + 1, [-1, 1, "HAM", [c1, 16, 7]])

    # Petakan ulang seluruh rujukan 'from' pada head (backbone hanya memakai -1)
    new_head = []
    for f, n, m, args in copy.deepcopy(d["head"]):
        f = [_map_ref(v, redirect) for v in f] if isinstance(f, list) else _map_ref(f, redirect)
        new_head.append([f, n, m, args])

    d["backbone"], d["head"] = new_bb, new_head
    d["nc"] = nc
    d["scales"] = {scale: d["scales"][scale]}  # kunci ke satu skala agar kanal HAM konsisten

    os.makedirs(out_dir, exist_ok=True)
    name = f"yolo26{scale}-ham{'-p2' if p2 else ''}.yaml"
    out = Path(out_dir) / name
    out.write_text(yaml.dump(d, sort_keys=False))
    return str(out)


def _official_state_dict(weights: str) -> dict:
    """Muat state_dict bobot resmi via loader YOLO (mengunduh otomatis bila perlu)."""
    from ultralytics import YOLO

    return YOLO(weights).model.float().state_dict()


# ---------------------------------------------------------- transfer bobot
def transfer_pretrained(nn_model: torch.nn.Module, weights: str, shifted: bool) -> dict:
    """Muat bobot COCO ke model varian; tangani pergeseran indeks bila ber-HAM.

    Returns ringkasan {matched, total_target, fraction} untuk dilaporkan di BAB 4.
    """
    src = _official_state_dict(weights)

    if shifted:  # 'model.{i}.' -> 'model.{_new_index(i)}.'
        remapped = {}
        for k, v in src.items():
            parts = k.split(".")
            if parts[0] == "model" and parts[1].isdigit():
                parts[1] = str(_new_index(int(parts[1])))
                k = ".".join(parts)
            remapped[k] = v
        src = remapped

    dst = nn_model.state_dict()
    csd = {k: v for k, v in src.items() if k in dst and dst[k].shape == v.shape}
    nn_model.load_state_dict(csd, strict=False)
    n_par = sum(v.numel() for v in dst.values())
    n_par_ok = sum(v.numel() for v in csd.values())
    return dict(
        matched=len(csd),
        total_target=len(dst),
        fraction=len(csd) / max(len(dst), 1),
        param_fraction=n_par_ok / max(n_par, 1),
    )


# ------------------------------------------------------------- build model
def build_model(variant: str, scale: str = "s", nc: int = 4, workdir: str = ".", pretrained: bool = True,
                weights: str | None = None):
    """Siapkan model awal sebuah varian. Return (path_atau_nama_model, laporan_transfer).

    Untuk varian berarsitektur kustom, bobot hasil transfer disimpan sebagai
    checkpoint init ('inits/{V}_init.pt') agar trainer ultralytics memakai bobot
    tersebut (trainer membangun ulang model, sehingga transfer in-memory saja
    akan hilang tanpa checkpoint).
    """
    from ultralytics import YOLO

    register_ham()
    cfg = VARIANTS[variant]
    base_pt = weights or f"yolo26{scale}.pt"

    if not cfg["ham"] and not cfg["p2"]:
        # V1 / V4: arsitektur standar, langsung bobot resmi penuh
        return (base_pt if pretrained else str(_official_cfg_dir() / "yolo26.yaml")), dict(
            matched=None, total_target=None, fraction=1.0 if pretrained else 0.0
        )

    if cfg["ham"]:
        cfg_path = generate_ham_yaml(p2=cfg["p2"], scale=scale, nc=nc, out_dir=os.path.join(workdir, "cfg"))
        shifted = True
    else:  # P2 murni: YAML resmi
        cfg_path = f"yolo26{scale}-p2.yaml"
        shifted = False

    model = YOLO(cfg_path)
    report = dict(matched=0, total_target=len(model.model.state_dict()), fraction=0.0)
    if pretrained:
        report = transfer_pretrained(model.model, base_pt, shifted=shifted)

    init_dir = Path(workdir) / "inits"
    init_dir.mkdir(parents=True, exist_ok=True)
    init_path = init_dir / f"{variant}_{scale}_init.pt"
    model.save(str(init_path))
    return str(init_path), report
