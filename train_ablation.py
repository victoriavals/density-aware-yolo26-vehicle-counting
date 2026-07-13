"""
train_ablation.py — Runner pelatihan 8 varian ablasi (Tabel 3.3–3.4 tesis).

Contoh pakai:
  # 1) Grid search alpha & sigma satu kali pada varian penuh, pelatihan singkat (Subbab 3.9)
  python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60

  # 2) Latih satu varian (hasil tuning otomatis terbaca dari dalw_best.json)
  python train_ablation.py --data dataset/data.yaml --variant V4

  # 3) Latih semuanya berurutan (V1..V8), bisa dilanjutkan bila terputus
  python train_ablation.py --data dataset/data.yaml --variant all
  python train_ablation.py --data dataset/data.yaml --variant V5 --resume

Konfigurasi identik antarvarian (keadilan perbandingan, Subbab 3.9):
  imgsz=640, epochs=300 + early stopping (patience), batch=16 FP16 (AMP),
  optimizer=MuSGD, lr0=0.01 cos_lr, seed=0 deterministic.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
from pathlib import Path

ALPHA_GRID = (0.5, 1.0, 2.0)     # Tabel 3.3
SIGMA_GRID = (0.05, 0.10, 0.20)  # Tabel 3.3 (koordinat ternormalisasi)


def train_once(args, variant: str, run_name: str, epochs: int, alpha: float, sigma: float):
    """Satu proses pelatihan penuh untuk satu varian/konfigurasi."""
    from y26_variants import VARIANTS, build_model
    from y26_dalw import apply_dalw
    from ultralytics import YOLO

    cfg = VARIANTS[variant]
    if cfg["dalw"]:
        apply_dalw(alpha, sigma)  # patch loss SEBELUM trainer membangun model

    last = Path(args.project) / run_name / "weights" / "last.pt"
    if args.resume and last.exists():
        model, report = YOLO(str(last)), dict(fraction="resume")
    else:
        src, report = build_model(variant, scale=args.scale, nc=args.nc, workdir=args.workdir,
                                  pretrained=not args.from_scratch)
        model = YOLO(src)
    print(f"[{run_name}] sumber bobot: transfer={report}")

    if getattr(args, "probe", 0) > 0:
        from y26_nmsfree import NMSFreeProbe

        model.add_callback("on_fit_epoch_end",
                           NMSFreeProbe(args.data, n=args.probe, split="val", tau=0.25))

    results = model.train(
        data=args.data,
        epochs=epochs,
        patience=args.patience,          # A-12: early stopping eksplisit
        batch=args.batch,                # 16 default; -1 = AutoBatch bila OOM
        imgsz=640,
        optimizer="MuSGD",               # bawaan YOLO26 (Tabel 3.4)
        lr0=0.01,
        cos_lr=True,
        amp=True,                        # mixed precision FP16 (Tabel 3.4)
        seed=0,
        deterministic=True,
        cache=False,                     # A-12: hemat RAM/VRAM
        workers=args.workers,
        device=args.device,
        project=args.project,
        name=run_name,
        exist_ok=True,
        resume=bool(args.resume and last.exists()),
        val=True,
        plots=True,
    )
    return results


def read_best_map(run_dir: Path) -> float:
    """Ambil mAP50-95 terbaik dari results.csv sebuah run."""
    f = run_dir / "results.csv"
    if not f.exists():
        return float("nan")
    with open(f) as fh:
        rows = list(csv.DictReader(fh))
    key = next((k for k in rows[0] if "mAP50-95" in k), None)
    return max(float(r[key]) for r in rows if r.get(key)) if key else float("nan")


def tune_dalw(args):
    """Grid search 3x3 (alpha, sigma) pada varian penuh V8, pelatihan dipersingkat.

    Sesuai Subbab 3.9: pencarian SATU KALI, lalu nilai terpilih dibekukan untuk
    seluruh delapan varian; nilai terpilih dilaporkan pada BAB 4.
    """
    results = []
    for a, s in itertools.product(ALPHA_GRID, SIGMA_GRID):
        name = f"tune_a{a}_s{s}"
        print(f"\n===== TUNE {name} ({args.tune_epochs} epoch singkat) =====")
        train_once(args, "V8", name, epochs=args.tune_epochs, alpha=a, sigma=s)
        m = read_best_map(Path(args.project) / name)
        results.append(dict(alpha=a, sigma=s, map5095=m))
        print(f"[tune] alpha={a} sigma={s} -> mAP50-95(val)={m:.4f}")

    best = max(results, key=lambda r: (r["map5095"] == r["map5095"]) and r["map5095"] or -1)
    out = dict(best=best, all=results, protocol=f"grid 3x3, {args.tune_epochs} epoch, varian V8, seed 0")
    Path("dalw_best.json").write_text(json.dumps(out, indent=2))
    print(f"\n[tune] TERPILIH alpha={best['alpha']} sigma={best['sigma']} "
          f"(mAP50-95={best['map5095']:.4f}) -> disimpan ke dalw_best.json")


def main():
    ap = argparse.ArgumentParser(description="Pelatihan ablasi YOLO26 termodifikasi (tesis)")
    ap.add_argument("--data", required=True, help="path data.yaml dataset traffic-merged")
    ap.add_argument("--variant", default=None, help="V1..V8 | all")
    ap.add_argument("--tune-dalw", action="store_true", help="grid search alpha,sigma pada V8")
    ap.add_argument("--tune-epochs", type=int, default=60)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--patience", type=int, default=50)
    ap.add_argument("--batch", type=int, default=16, help="16 default; -1 = AutoBatch bila OOM")
    ap.add_argument("--alpha", type=float, default=None, help="override alpha DALW")
    ap.add_argument("--sigma", type=float, default=None, help="override sigma DALW")
    ap.add_argument("--scale", default="s", help="skala model YOLO26 (Batasan 1.5: small)")
    ap.add_argument("--nc", type=int, default=4)
    ap.add_argument("--device", default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--probe", type=int, default=64,
                    help="jumlah citra probe NMS-free per epoch (0 = nonaktif)")
    ap.add_argument("--suffix", default="",
                    help="akhiran nama run, mis. _a0.5 untuk sensitivitas alpha (BAB 4)")
    ap.add_argument("--project", default="runs_tesis")
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--from-scratch", action="store_true", help="tanpa bobot COCO (opsional)")
    args = ap.parse_args()

    if args.tune_dalw:
        return tune_dalw(args)

    # alpha & sigma: override CLI > hasil tuning > default tengah grid
    a, s = args.alpha, args.sigma
    if (a is None or s is None) and os.path.exists("dalw_best.json"):
        best = json.loads(Path("dalw_best.json").read_text())["best"]
        a = best["alpha"] if a is None else a
        s = best["sigma"] if s is None else s
        print(f"[DALW] memakai hasil tuning: alpha={a}, sigma={s}")
    a = 1.0 if a is None else a
    s = 0.10 if s is None else s

    variants = list("V%d" % i for i in range(1, 9)) if args.variant == "all" else [args.variant]
    for v in variants:
        print(f"\n===== PELATIHAN {v}{args.suffix} =====")
        train_once(args, v, v + args.suffix, epochs=args.epochs, alpha=a, sigma=s)


if __name__ == "__main__":
    main()
