#!/usr/bin/env python
"""Manifest integritas artefak — bukti bahwa dataset/bobot TIDAK berubah selama
pekerjaan perbaikan provenans (Fase 0 membuat, Fase 7 memeriksa).

Dipakai dua arah:
    python integritas_artefak.py --buat   --keluar beku_20260813
    python integritas_artefak.py --periksa --keluar beku_20260813

⚠️ Sengaja mencakup **.jpg DAN .png**. Dataset memuat 1.042 berkas .png
(763 train / 252 valid / 27 test); pola hanya-"*.jpg" menghasilkan 2.347 baris,
bukan 3.389, sehingga kriteria lolos "3.389 baris" akan gagal palsu.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

EKSTENSI_CITRA = (".jpg", ".jpeg", ".png")
JUMLAH_CITRA_HARAPAN = 3389
VARIAN = [f"V{i}" for i in range(1, 9)]


def md5(path: Path, blok: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        while chunk := fh.read(blok):
            h.update(chunk)
    return h.hexdigest()


def daftar_citra(akar: Path) -> list[Path]:
    """Seluruh citra dataset, urut stabil, jpg+png."""
    out = [p for p in akar.rglob("*")
           if p.is_file() and p.suffix.lower() in EKSTENSI_CITRA]
    return sorted(out, key=lambda p: p.as_posix())


def daftar_bobot(runs: Path) -> list[Path]:
    return [w for v in VARIAN if (w := runs / v / "weights" / "best.pt").exists()]


def tulis_manifest(berkas: list[Path], akar: Path, tujuan: Path, label: str) -> int:
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as fh:
        for p in berkas:
            fh.write(f"{md5(p)}  {p.relative_to(akar).as_posix()}\n")
    print(f"  {label}: {len(berkas)} berkas -> {tujuan}")
    return len(berkas)


def baca_manifest(path: Path) -> dict[str, str]:
    out = {}
    for baris in path.read_text(encoding="utf-8").splitlines():
        if not baris.strip():
            continue
        h, _, nama = baris.partition("  ")
        out[nama] = h
    return out


def periksa(berkas: list[Path], akar: Path, manifest: Path, label: str) -> bool:
    if not manifest.exists():
        print(f"  [LEWAT] {label}: {manifest} belum ada")
        return True
    lama = baca_manifest(manifest)
    baru = {p.relative_to(akar).as_posix(): md5(p) for p in berkas}
    hilang = sorted(set(lama) - set(baru))
    tambah = sorted(set(baru) - set(lama))
    ubah = sorted(k for k in set(lama) & set(baru) if lama[k] != baru[k])
    ok = not (hilang or tambah or ubah)
    tanda = "OK" if ok else "BERUBAH"
    print(f"  [{tanda}] {label}: {len(baru)} berkas | hilang={len(hilang)} "
          f"tambah={len(tambah)} berubah={len(ubah)}")
    for judul, daftar in (("hilang", hilang), ("tambah", tambah), ("berubah", ubah)):
        for nama in daftar[:10]:
            print(f"      {judul}: {nama}")
        if len(daftar) > 10:
            print(f"      ... +{len(daftar) - 10} lagi")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--buat", action="store_true", help="tulis manifest md5 baru")
    g.add_argument("--periksa", action="store_true", help="bandingkan dengan manifest yang ada")
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--runs", default="runs_tesis")
    ap.add_argument("--keluar", default="beku_20260813", help="folder manifest")
    args = ap.parse_args()

    ds, runs, keluar = Path(args.dataset), Path(args.runs), Path(args.keluar)
    citra, bobot = daftar_citra(ds), daftar_bobot(runs)
    m_ds, m_bt = keluar / "md5_dataset.txt", keluar / "md5_bobot.txt"

    if args.buat:
        print(f"== membuat manifest di {keluar}/ ==")
        n = tulis_manifest(citra, ds, m_ds, "dataset (jpg+png)")
        tulis_manifest(bobot, runs, m_bt, "bobot best.pt")
        lolos = n == JUMLAH_CITRA_HARAPAN and len(bobot) == 8
        print(f"\nKriteria lolos: {n} citra (harap {JUMLAH_CITRA_HARAPAN}), "
              f"{len(bobot)} bobot (harap 8) -> {'LOLOS' if lolos else 'GAGAL'}")
        return 0 if lolos else 1

    print(f"== memeriksa terhadap manifest di {keluar}/ ==")
    ok = periksa(citra, ds, m_ds, "dataset (jpg+png)")
    ok &= periksa(bobot, runs, m_bt, "bobot best.pt")
    print(f"\n{'INTEGRITAS UTUH' if ok else 'ADA PERUBAHAN — periksa di atas'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
