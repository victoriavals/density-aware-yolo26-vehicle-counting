"""
siapkan_counting.py — Penyiap kit counting P9 (RQ5), TANPA GPU/model.

Membantu Naufal menyiapkan tiga prasyarat y26_counting.py yang hanya bisa
disediakan manusia: (1) memilih koordinat GARIS VIRTUAL, (2) memahami arah
in/out, (3) mengisi CSV hitung manual berformat interval,class,direction,count.

Fungsi:
  1. Inspeksi video: cetak resolusi, FPS, durasi, jumlah frame, jumlah interval.
  2. Preview garis: simpan frame pertama + garis kandidat + grid koordinat
     (px) sebagai gambar -> Naufal membaca koordinat garis dari situ.
  3. Template GT: buat CSV kerangka (interval × kelas-nonpejalan × arah) berisi
     count=0 siap diedit — jumlah interval dihitung dari durasi ÷ --interval-s.

Pakai (CPU saja, tak menyentuh training/GPU):
  # inspeksi + preview garis tengah default + grid
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4
  # preview garis kandidat tertentu (untuk verifikasi sebelum counting)
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line 0,540,1919,540
  # buat kerangka GT (interval dihitung dari durasi video)
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template

Setelah garis dipilih & GT diisi, jalankan counting sesuai README Tahap 3(c):
  python y26_counting.py --video video_uji/uji_ruas1.mp4 \
      --weights runs_tesis/V8/weights/best.pt \
      --line <x1,y1,x2,y2> --interval-s 60 --gt <gt.csv> --save-video
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np
import yaml

WARNA_GARIS = (0, 0, 255)
WARNA_GRID = (80, 80, 80)
WARNA_TEKS = (0, 255, 255)


def kelas_counting(data_yaml: str, exclude=("pedestrian", "pejalan-kaki", "person")) -> list[str]:
    names = yaml.safe_load(Path(data_yaml).read_text())["names"]
    names = list(names.values()) if isinstance(names, dict) else list(names)
    excl = {e.lower() for e in exclude}
    return [n for n in names if n.lower() not in excl]


def inspeksi(video: Path) -> dict:
    cap = cv2.VideoCapture(str(video))
    assert cap.isOpened(), f"video tidak terbuka: {video}"
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, frame0 = cap.read()
    cap.release()
    dur = n / fps if fps else float("nan")
    return dict(fps=fps, W=W, H=H, n_frames=n, durasi_s=dur,
                frame0=frame0 if ok else None)


def gambar_preview(frame: np.ndarray, line, out: Path, grid_step=None) -> None:
    im = frame.copy()
    H, W = im.shape[:2]
    step = grid_step or max(round(min(W, H) / 8 / 10) * 10, 50)
    for x in range(0, W, step):
        cv2.line(im, (x, 0), (x, H), WARNA_GRID, 1)
        cv2.putText(im, str(x), (x + 2, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WARNA_TEKS, 1)
    for y in range(0, H, step):
        cv2.line(im, (0, y), (W, y), WARNA_GRID, 1)
        cv2.putText(im, str(y), (2, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WARNA_TEKS, 1)
    x1, y1, x2, y2 = line
    cv2.line(im, (x1, y1), (x2, y2), WARNA_GARIS, 3)
    # panah normal garis: sisi "in"/"out" mengikuti orientasi start->end supervision
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    dx, dy = x2 - x1, y2 - y1
    L = max((dx**2 + dy**2) ** 0.5, 1)
    nx, ny = -dy / L, dx / L  # normal
    cv2.arrowedLine(im, (mx, my), (int(mx + 40 * nx), int(my + 40 * ny)), WARNA_GARIS, 2, tipLength=0.3)
    cv2.putText(im, f"garis {tuple(line)}", (10, H - 15), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, WARNA_GARIS, 2)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), im)


def buat_template_gt(video: Path, info: dict, interval_s: int, kelas: list[str], out: Path) -> int:
    n_interval = max(int(np.ceil(info["durasi_s"] / interval_s)), 1)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["interval", "class", "direction", "count"])
        for i in range(n_interval):
            for c in kelas:
                for d in ("in", "out"):
                    w.writerow([i, c, d, 0])
    return n_interval


def main() -> None:
    ap = argparse.ArgumentParser(description="Penyiap kit counting P9 (tanpa GPU)")
    ap.add_argument("--video", required=True)
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--line", default=None, help="x1,y1,x2,y2 piksel; default garis tengah")
    ap.add_argument("--interval-s", type=int, default=60)
    ap.add_argument("--make-gt-template", action="store_true")
    ap.add_argument("--out-dir", default="video_uji/preview")
    a = ap.parse_args()

    video = Path(a.video)
    info = inspeksi(video)
    print(f"== {video.name} ==")
    print(f"  resolusi   : {info['W']}x{info['H']} px")
    print(f"  FPS        : {info['fps']:.2f}")
    print(f"  frame      : {info['n_frames']}")
    print(f"  durasi     : {info['durasi_s']:.1f} s ({info['durasi_s']/60:.1f} mnt)")
    n_iv = max(int(np.ceil(info['durasi_s'] / a.interval_s)), 1)
    print(f"  interval   : {n_iv} jendela @ {a.interval_s} s")

    line = ([int(v) for v in a.line.split(",")] if a.line
            else (0, info["H"] // 2, info["W"] - 1, info["H"] // 2))
    print(f"  garis      : {tuple(line)}" + ("" if a.line else "  (tengah default — sesuaikan!)"))

    if info["frame0"] is not None:
        prev = Path(a.out_dir) / f"{video.stem}_garis.jpg"
        gambar_preview(info["frame0"], line, prev)
        print(f"  preview    : {prev}  (buka untuk baca koordinat & cek arah panah in/out)")
    else:
        print("  [peringatan] frame pertama gagal dibaca — cek codec video")

    if a.make_gt_template:
        kelas = kelas_counting(a.data)
        gt = video.with_name(f"gt_{video.stem}.csv")
        n = buat_template_gt(video, info, a.interval_s, kelas, gt)
        print(f"  template GT: {gt}  ({n} interval × {len(kelas)} kelas × 2 arah "
              f"= {n*len(kelas)*2} baris, count=0 — isi manual)")
        print(f"  kelas dihitung (pejalan kaki dikecualikan): {kelas}")


if __name__ == "__main__":
    main()
