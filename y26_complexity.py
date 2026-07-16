"""
y26_complexity.py — Metrik kompleksitas dan efisiensi model (Subbab 3.11.4, Tabel 3.7).

Menjawab masukan pembimbing poin 4: selain mAP dan FPS, laporkan jumlah parameter,
FLOPs, ukuran model, kebutuhan memori GPU, dan waktu pelatihan untuk kedelapan varian.

Pakai:
  # (a) saat pelatihan: callback merekam memori GPU puncak + waktu latih
  #     (sudah otomatis terpasang di train_ablation.py)
  # (b) setelah pelatihan: rakit tabel kompleksitas seluruh varian
  python y26_complexity.py --runs runs_tesis --data dataset/data.yaml --variants all
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import torch


# ------------------------------------------------------- callback pelatihan
class ComplexityCallback:
    """Rekam memori GPU puncak dan waktu pelatihan ke <save_dir>/complexity_train.json."""

    def __init__(self):
        self.t0 = None

    def on_train_start(self, trainer):
        self.t0 = time.time()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

    def on_train_end(self, trainer):
        try:
            peak = torch.cuda.max_memory_allocated() / 1024**3 if torch.cuda.is_available() else float("nan")
            reserved = torch.cuda.max_memory_reserved() / 1024**3 if torch.cuda.is_available() else float("nan")
            out = dict(
                train_hours=(time.time() - self.t0) / 3600.0 if self.t0 else float("nan"),
                peak_gpu_alloc_gb=peak,
                peak_gpu_reserved_gb=reserved,
                epochs_ran=int(getattr(trainer, "epoch", -1)) + 1,
                batch=int(getattr(trainer.args, "batch", -1)),
            )
            Path(trainer.save_dir, "complexity_train.json").write_text(json.dumps(out, indent=2))
            print(f"[kompleksitas] {out}")
        except Exception as e:
            print(f"[kompleksitas] gagal mencatat: {e}")


# ------------------------------------------------------- pengukuran statis
def static_complexity(weights: str, imgsz: int = 640) -> dict:
    """Jumlah parameter, GFLOPs, dan ukuran berkas bobot."""
    from ultralytics import YOLO
    from ultralytics.utils.torch_utils import get_flops, get_num_params

    from y26_modules import register_ham

    register_ham()
    m = YOLO(weights)
    return dict(
        params_M=get_num_params(m.model) / 1e6,
        gflops=get_flops(m.model, imgsz),
        size_MB=Path(weights).stat().st_size / 1024**2,
    )


def inference_cost(weights: str, imgsz: int = 640, device=None, n_warmup: int = 10,
                   n_iter: int = 50) -> dict:
    """FPS dan memori GPU puncak saat inferensi (batch 1, FP16 bila CUDA)."""
    from ultralytics import YOLO

    from y26_modules import register_ham

    register_ham()
    dev = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    m = YOLO(weights).model.to(dev).eval()
    half = "cuda" in str(dev)
    if half:
        m = m.half()
        torch.cuda.reset_peak_memory_stats()
    x = torch.rand(1, 3, imgsz, imgsz, device=dev, dtype=torch.half if half else torch.float)
    with torch.no_grad():
        for _ in range(n_warmup):
            m(x)
        if half:
            torch.cuda.synchronize()
        t0 = time.time()
        for _ in range(n_iter):
            m(x)
        if half:
            torch.cuda.synchronize()
        dt = time.time() - t0
    return dict(
        fps=n_iter / dt,
        latency_ms=1000 * dt / n_iter,
        peak_gpu_infer_gb=(torch.cuda.max_memory_allocated() / 1024**3) if half else float("nan"),
    )


def training_stats(run_dir: Path) -> dict:
    """Ambil waktu latih & memori puncak dari callback; fallback ke results.csv."""
    j = run_dir / "complexity_train.json"
    if j.exists():
        return json.loads(j.read_text())
    csvf = run_dir / "results.csv"
    if csvf.exists():
        rows = list(csv.DictReader(open(csvf)))
        tkey = next((k for k in rows[0] if "time" in k.lower()), None)
        return dict(train_hours=float(rows[-1][tkey]) / 3600 if tkey else float("nan"),
                    epochs_ran=len(rows), peak_gpu_alloc_gb=float("nan"))
    return dict(train_hours=float("nan"), epochs_ran=-1, peak_gpu_alloc_gb=float("nan"))


def main():
    ap = argparse.ArgumentParser(description="Tabel kompleksitas & efisiensi model (Tabel 3.7)")
    ap.add_argument("--runs", default="runs_tesis")
    ap.add_argument("--variants", default="all")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default=None)
    ap.add_argument("--out", default="eval_out/complexity.csv")
    a = ap.parse_args()

    names = [f"V{i}" for i in range(1, 9)] if a.variants == "all" else a.variants.split(",")
    rows = []
    for v in names:
        w = Path(a.runs) / v / "weights" / "best.pt"
        if not w.exists():
            print(f"[lewati] {v}: {w} tidak ada")
            continue
        s = static_complexity(str(w), a.imgsz)
        inf = inference_cost(str(w), a.imgsz, a.device)
        tr = training_stats(Path(a.runs) / v)
        rows.append(dict(variant=v, params_M=s["params_M"], gflops=s["gflops"], size_MB=s["size_MB"],
                         peak_gpu_train_gb=tr.get("peak_gpu_alloc_gb", float("nan")),
                         peak_gpu_infer_gb=inf["peak_gpu_infer_gb"], train_hours=tr.get("train_hours"),
                         epochs=tr.get("epochs_ran"), fps=inf["fps"], latency_ms=inf["latency_ms"]))
        print(f"  {v}: {s['params_M']:.2f}M par | {s['gflops']:.1f} GFLOPs | {s['size_MB']:.1f} MB | "
              f"VRAM latih {tr.get('peak_gpu_alloc_gb', float('nan')):.2f} GB | {inf['fps']:.1f} FPS")

    if rows:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            for r in rows:
                w.writerow({k: (f"{x:.4g}" if isinstance(x, float) else x) for k, x in r.items()})
        print(f"\nTersimpan: {a.out}  (isi langsung ke Tabel 3.7 / BAB 4)")


if __name__ == "__main__":
    main()
