# PEMBARUAN KODE TESIS — Analisis Kompleksitas Model + Effect Size Wilcoxon

## KONTEKS
Ini proyek kode tesis (deteksi YOLO26 termodifikasi, ablasi 8 varian). Folder proyek
berisi antara lain: `train_ablation.py`, `y26_stats.py`, `evaluate_all.py`,
`y26_modules.py`, `y26_dalw.py`, `y26_nmsfree.py`, `y26_strata.py`.
Naskah tesis baru saja direvisi dan kini mensyaratkan dua hal yang belum ada di kode:
(1) metrik kompleksitas model — jumlah parameter, GFLOPs, ukuran model, memori GPU
puncak (latih & inferensi), dan waktu pelatihan (Subbab 3.11.4 / Tabel 3.7 naskah);
(2) ukuran efek korelasi rank-biserial r = (W⁺ − W⁻)/(W⁺ + W⁻) mendampingi nilai p
uji Wilcoxon (Persamaan 3.15 naskah).

## ATURAN KESELAMATAN (WAJIB)
- Proses TRAINING mungkin SEDANG BERJALAN di mesin ini. JANGAN menghentikan,
  me-restart, atau menjalankan proses training apa pun.
- JANGAN menyentuh folder `runs_tesis/`, `dataset/`, `inits/`, `cfg/`, dan file
  `dalw_best.json`.
- Terapkan HANYA empat tugas di bawah, persis seperti tertulis. Jangan merapikan,
  memformat ulang, atau "memperbaiki" kode lain di luar blok yang diminta.
- Jika teks jangkar (blok LAMA) pada Tugas 2–4 tidak ditemukan persis, BERHENTI dan
  laporkan isi aktual bagian tersebut — jangan berimprovisasi.

## TUGAS 1 — Buat file baru `y26_complexity.py` dengan isi PERSIS berikut

```python
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
```

## TUGAS 2 — `y26_stats.py`: ganti fungsi `wilcoxon_pair` LAMA dengan blok BARU

Blok LAMA (hapus persis ini):

```python
def wilcoxon_pair(x, y, alternative: str = "two-sided") -> dict:
    """Wilcoxon berpasangan x vs y (drop pasangan NaN; selisih nol dibuang, metode 'wilcox')."""
    from scipy.stats import wilcoxon

    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    d = x - y
    n_eff = int((d != 0).sum())
    out = dict(n=int(m.sum()), n_eff=n_eff,
               median_diff=float(np.median(d)) if len(d) else float("nan"),
               mean_diff=float(np.mean(d)) if len(d) else float("nan"))
    if n_eff < 1:
        out.update(W=0.0, p=1.0)
        return out
    res = wilcoxon(x, y, zero_method="wilcox", alternative=alternative, method="auto")
    out.update(W=float(res.statistic), p=float(res.pvalue))
    return out
```

Blok BARU (tulis persis ini sebagai gantinya):

```python
def rank_biserial(d: np.ndarray) -> tuple[float, float, float]:
    """Korelasi rank-biserial (Persamaan 3.15): r = (W+ - W-) / (W+ + W-).

    Ukuran efek untuk Wilcoxon signed-rank; rentang -1..+1, positif berarti
    x konsisten lebih unggul dari y. Selisih nol dibuang (metode 'wilcox'),
    peringkat memakai rata-rata untuk nilai kembar (ties).
    """
    from scipy.stats import rankdata

    d = d[d != 0]
    if len(d) == 0:
        return float("nan"), 0.0, 0.0
    r = rankdata(np.abs(d))
    wp, wm = float(r[d > 0].sum()), float(r[d < 0].sum())
    return (wp - wm) / (wp + wm), wp, wm


def wilcoxon_pair(x, y, alternative: str = "two-sided") -> dict:
    """Wilcoxon berpasangan x vs y + ukuran efek (drop pasangan NaN; selisih nol dibuang)."""
    from scipy.stats import wilcoxon

    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    d = x - y
    n_eff = int((d != 0).sum())
    r_rb, wp, wm = rank_biserial(d)
    out = dict(n=int(m.sum()), n_eff=n_eff,
               median_diff=float(np.median(d)) if len(d) else float("nan"),
               mean_diff=float(np.mean(d)) if len(d) else float("nan"),
               rank_biserial=r_rb, W_plus=wp, W_minus=wm)
    if n_eff < 1:
        out.update(W=0.0, p=1.0)
        return out
    res = wilcoxon(x, y, zero_method="wilcox", alternative=alternative, method="auto")
    out.update(W=float(res.statistic), p=float(res.pvalue))
    return out
```

## TUGAS 3 — `evaluate_all.py`: dua penggantian kecil

(a) Ganti baris daftar kolom LAMA:

```python
                cols = ["pair", "family", "metric", "n", "n_eff", "W", "p", "p_holm",
                        "median_diff", "mean_diff", "signif_5pct"]
```

menjadi:

```python
                cols = ["pair", "family", "metric", "n", "n_eff", "W", "p", "p_holm",
                        "median_diff", "mean_diff", "rank_biserial", "W_plus", "W_minus",
                        "signif_5pct"]
```

(b) Ganti blok cetak hipotesis utama LAMA:

```python
                    if r["family"] == "primary":
                        print(f"  [UTAMA] {r['pair']:>9}: W={r['W']:.1f} p={r['p']:.4g} "
                              f"median Δ={r['median_diff']:+.4f} -> "
                              f"{'SIGNIFIKAN' if r['signif_5pct'] else 'tidak signifikan'} (5%)")
```

menjadi:

```python
                    if r["family"] == "primary":
                        print(f"  [UTAMA] {r['pair']:>9}: W={r['W']:.1f} p={r['p']:.4g} "
                              f"median Δ={r['median_diff']:+.4f} r={r['rank_biserial']:+.3f} -> "
                              f"{'SIGNIFIKAN' if r['signif_5pct'] else 'tidak signifikan'} (5%)")
```

## TUGAS 4 — `train_ablation.py`: pasang ComplexityCallback

Di dalam fungsi `train_once`, cari baris ini:

```python
    if getattr(args, "probe", 0) > 0:
```

dan sisipkan PERSIS blok berikut TEPAT DI ATAS baris tersebut (indentasi 4 spasi, sama):

```python
    from y26_complexity import ComplexityCallback
    cx = ComplexityCallback()
    model.add_callback("on_train_start", cx.on_train_start)
    model.add_callback("on_train_end", cx.on_train_end)

```

## VERIFIKASI (jalankan semua; JANGAN menjalankan training)

```bash
python -c "import ast; [ast.parse(open(f).read()) for f in ['y26_complexity.py','y26_stats.py','evaluate_all.py','train_ablation.py']]; print('sintaks OK')"

python - <<'PY'
import numpy as np
from y26_stats import wilcoxon_pair
x = np.array([0.50, 0.55, 0.60, 0.62]); y = x - 0.03
r = wilcoxon_pair(x, y); assert abs(r['rank_biserial'] - 1.0) < 1e-9, r
x2 = np.array([0.5, 0.6, 0.7, 0.8]); y2 = np.array([0.4, 0.5, 0.6, 0.9])
r2 = wilcoxon_pair(x2, y2)
assert abs(r2['rank_biserial'] - 0.5) < 1e-9 and r2['W_plus'] == 8 and r2['W_minus'] == 2, r2
print(f"OK rank-biserial: konsisten unggul r={r['rank_biserial']:+.3f} | campuran r={r2['rank_biserial']:+.3f}")
PY

grep -n "ComplexityCallback" train_ablation.py
```

Keluaran yang diharapkan: `sintaks OK`, lalu
`OK rank-biserial: konsisten unggul r=+1.000 | campuran r=+0.500`,
lalu grep menemukan pemasangan callback di `train_once`.

## CATATAN AKHIR
Setelah selesai, laporkan ringkas: file yang dibuat/diubah, hasil ketiga verifikasi,
dan konfirmasi bahwa tidak ada file lain yang tersentuh. Perubahan ini baru berlaku
pada invokasi training berikutnya; proses yang sedang berjalan tidak terpengaruh.
