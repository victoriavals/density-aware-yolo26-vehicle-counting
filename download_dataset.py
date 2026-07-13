"""
download_dataset.py — Unduh dataset traffic-merged dari Roboflow + verifikasi ringan.

Pakai:
  pip install roboflow
  python download_dataset.py --api-key XXXX --version 3

Split train/val/test SUDAH final per grup kamera-adegan-sesi di Roboflow
(Subbab 3.3.2), jadi skrip ini TIDAK menyentuh pembagian — hanya mengunduh
format YOLO lalu memverifikasi jumlah citra per subset dan komposisi kelas
(bahan Tabel 3.1 / sanity-check sebelum pelatihan).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import yaml


def verify(root: Path):
    data_yaml = root / "data.yaml"
    d = yaml.safe_load(data_yaml.read_text())
    names = d["names"]
    print(f"\nKelas ({len(names)}): {names}")

    for split in ("train", "valid", "test"):
        img_dir = root / split / "images"
        lbl_dir = root / split / "labels"
        if not img_dir.exists():
            print(f"[!] subset '{split}' tidak ditemukan")
            continue
        imgs = list(img_dir.glob("*"))
        counts, empty = Counter(), 0
        for lf in lbl_dir.glob("*.txt"):
            lines = lf.read_text().split()
            if not lines:
                empty += 1
            counts.update(int(x) for x in lines[0::5])
        per_kelas = {names[k] if isinstance(names, list) else names[k]: v for k, v in sorted(counts.items())}
        print(f"{split:6s}: {len(imgs):5d} citra | objek/kelas: {per_kelas} | label kosong: {empty}")

    # Pastikan path di data.yaml absolut agar aman dipanggil dari folder mana pun
    d["path"] = str(root.resolve())
    for k in ("train", "val", "test"):
        key = "valid" if k == "val" else k
        if (root / key).exists():
            d[k] = f"{key}/images"
    data_yaml.write_text(yaml.dump(d, sort_keys=False))
    print(f"\ndata.yaml dinormalisasi: {data_yaml}")
    print("Pakai path ini untuk --data pada train_ablation.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True, help="API key Roboflow Anda")
    ap.add_argument("--workspace", default="naufalfirdaus")
    ap.add_argument("--project", default="traffic-merged-qke0k-3yyyo")
    ap.add_argument("--version", type=int, required=True, help="nomor versi dataset di Roboflow")
    ap.add_argument("--out", default="dataset")
    args = ap.parse_args()

    from roboflow import Roboflow

    rf = Roboflow(api_key=args.api_key)
    proj = rf.workspace(args.workspace).project(args.project)
    ds = proj.version(args.version).download("yolov11", location=args.out, overwrite=False)
    verify(Path(ds.location))


if __name__ == "__main__":
    main()
