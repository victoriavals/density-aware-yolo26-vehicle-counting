"""
roboflow_ke_oklusi.py — Konversi ekspor Roboflow Classification -> manual_oklusi.csv.

Jalur Roboflow untuk validasi oklusi (P8): 200 crop di anotasi_oklusi/imgs/ diunggah
sebagai proyek Roboflow **Single-Label Classification** (3 kelas: no/partial/heavy),
dianotasi, lalu diekspor. Skrip ini memetakan hasil ekspor kembali ke kunci
(image, gt_index) via anotasi_oklusi/sample_manifest.csv sehingga integritas
pencocokan manual-vs-proksi tetap terjaga (nama crop 000.jpg.. = sample_id).

Mendukung dua bentuk ekspor Roboflow:
  (a) Folder Structure  : <root>/{train,valid,test}/<kelas>/<file>.jpg
  (b) Multiclass CSV    : <root>/**/_classes.csv (kolom filename + satu kolom per kelas one-hot)

Pakai:
  python roboflow_ke_oklusi.py --export <folder_ekspor_roboflow>
  # -> menulis manual_oklusi.csv di root repo (format image,gt_index,tier)

Lalu jalankan Prompt 8:
  python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('manual_oklusi.csv','dataset/data.yaml',split='val'))"
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

TIER_VALID = {"no", "partial", "heavy"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sample_id_dari(nama: str) -> int | None:
    """Ambil sample_id (angka awal) dari nama crop, toleran sufiks Roboflow .rf.<hash>."""
    m = re.match(r"0*(\d+)", Path(nama).stem)
    return int(m.group(1)) if m else None


def baca_manifest(path: Path) -> dict[int, tuple[str, int]]:
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    return {int(r["sample_id"]): (r["image"], int(r["gt_index"])) for r in rows}


def kumpulkan_label(export: Path) -> dict[int, str]:
    """Kembalikan {sample_id: tier} dari ekspor Roboflow (folder-structure atau CSV)."""
    hasil: dict[int, str] = {}

    # (b) Multiclass CSV
    for csvf in export.rglob("_classes.csv"):
        rows = list(csv.DictReader(open(csvf, encoding="utf-8")))
        if not rows:
            continue
        fcol = next((c for c in rows[0] if c.strip().lower() in ("filename", "file", "image")), None)
        kelas_cols = [c for c in rows[0] if c.strip().lower() in TIER_VALID]
        if fcol and kelas_cols:
            for r in rows:
                sid = sample_id_dari(r[fcol])
                aktif = [c.strip().lower() for c in kelas_cols if str(r[c]).strip() in ("1", "1.0", "True", "true")]
                if sid is not None and len(aktif) == 1:
                    hasil[sid] = aktif[0]

    # (a) Folder Structure: <split>/<kelas>/<file>
    if not hasil:
        for img in export.rglob("*"):
            if img.suffix.lower() in IMG_EXT and img.parent.name.lower() in TIER_VALID:
                sid = sample_id_dari(img.name)
                if sid is not None:
                    hasil[sid] = img.parent.name.lower()
    return hasil


def main() -> None:
    ap = argparse.ArgumentParser(description="Ekspor Roboflow Classification -> manual_oklusi.csv")
    ap.add_argument("--export", required=True, help="folder hasil ekstrak ekspor Roboflow")
    ap.add_argument("--manifest", default="anotasi_oklusi/sample_manifest.csv")
    ap.add_argument("--out", default="manual_oklusi.csv")
    a = ap.parse_args()

    manifest = baca_manifest(Path(a.manifest))
    label = kumpulkan_label(Path(a.export))
    if not label:
        raise SystemExit("[gagal] tak menemukan label kelas (no/partial/heavy) di folder ekspor. "
                         "Pastikan ekspor format 'Folder Structure' atau 'Multiclass CSV'.")

    baris, tak_valid, tak_dikenal = [], [], []
    for sid, tier in sorted(label.items()):
        if tier not in TIER_VALID:
            tak_valid.append(sid); continue
        if sid not in manifest:
            tak_dikenal.append(sid); continue
        img, gi = manifest[sid]
        baris.append((img, gi, tier))

    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["image", "gt_index", "tier"])
        w.writerows(baris)

    dist = Counter(t for _, _, t in baris)
    print(f"[OK] {a.out}: {len(baris)}/{len(manifest)} objek terpetakan")
    print(f"     distribusi tier manual: {dict(dist)}")
    if len(baris) < len(manifest):
        print(f"     [info] {len(manifest)-len(baris)} crop belum dianotasi (boleh — occlusion_agreement pakai yang ada)")
    if tak_dikenal:
        print(f"     [peringatan] {len(tak_dikenal)} sample_id di luar manifest (diabaikan): {tak_dikenal[:10]}")
    if tak_valid:
        print(f"     [peringatan] {len(tak_valid)} label non-{{no,partial,heavy}} (diabaikan)")


if __name__ == "__main__":
    main()
