#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Peringkat kandidat RENDER (citra buatan mesin) di dalam `web_katalog`.

🔴 HASIL VALIDASI: HEURISTIK INI GAGAL. JANGAN DIPAKAI. Disimpan sebagai catatan negatif
agar tidak ditemukan ulang.

Diuji pada 4 render yang sudah diketahui (13 Agu 2026): peringkatnya 802, 803, 1368, dan
1395 dari 1.597 — yaitu persentil 50, 50, 86, dan 87, bukan terkumpul di atas. Sebaran
skornya degenerat: min 0,0000 dan **median 0,0000**, artinya separuh korpus berskor nol.

Sebabnya: kuantisasi JPEG sudah meratakan wilayah datar, sehingga `|I − median3x3(I)|`
menjadi nol persis pada foto maupun render. Premis "foto membawa derau sensor, render
tidak" runtuh setelah kompresi lossy. Dua render `.png` justru berskor 0 (mulus, sesuai
dugaan) tetapi dua render `.jpg` berskor 1,0 — lebih tinggi daripada median foto.

Pelajaran: bila hendak memisahkan citra sintetis dari foto pada korpus ter-JPEG, ukuran
berbasis derau tidak memadai. Pemeriksaan mata pada lembar kontak tetap diperlukan, dan
untungnya render terlihat jelas bahkan pada miniatur — berbeda dari tanda air berkontras
rendah yang menuntut resolusi asli (Keputusan 5).

--- rancangan asli, disimpan apa adanya ---

Masalah. Audit `web_katalog` menghasilkan 1.452 klaster; memeriksa seluruh perwakilan
dengan mata adalah pekerjaan berjam-jam, dan pencarian pola nama hanya menangkap render
yang namanya menyebut "simulator"/"game". Render bernama netral tidak tertangkap.

Gagasan. Foto kamera membawa **derau sensor**; render permainan tidak. Pada wilayah datar
(gradien rendah), foto tetap menyisakan riak halus sedangkan render nyaris mulus. Skor di
bawah mengukur sisa frekuensi tinggi pada wilayah datar saja, sehingga tepi objek tidak
mencemari ukuran.

    skor = median |I − median3x3(I)| pada piksel bergradien rendah

Semakin RENDAH skor, semakin besar dugaan render. Ini **alat pemeringkat**, bukan vonis;
keputusan tetap dari mata. Nilainya: mengubah 1.452 pemeriksaan buta menjadi daftar kerja
terurut yang laju temuannya dapat diukur.

    python skor_render.py                  # peringkat + validasi pada 4 render diketahui
    python skor_render.py --teratas 120    # tulis daftar kerja n teratas
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import median_filter, sobel

POLA_RENDER_DIKENAL = r"(?i)(ukts|bus.simulator|game-simulasi|simulasi-mengemudi)"


def skor(path: pathlib.Path, sisi: int = 512) -> tuple[float, float]:
    """Return (skor_derau, frac_datar). Skor rendah = dugaan render."""
    im = Image.open(path).convert("L")
    im.thumbnail((sisi, sisi), Image.Resampling.LANCZOS)
    a = np.asarray(im, dtype=np.float32)
    if a.size < 4096:
        return float("nan"), 0.0
    # wilayah datar: magnitudo gradien di bawah persentil 40
    gx, gy = sobel(a, axis=1), sobel(a, axis=0)
    g = np.hypot(gx, gy)
    amb = np.percentile(g, 40)
    datar = g <= amb
    if datar.sum() < 500:
        return float("nan"), float(datar.mean())
    sisa = np.abs(a - median_filter(a, size=3))
    return float(np.median(sisa[datar])), float(datar.mean())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--provenans", default="provenans.csv")
    ap.add_argument("--keluar", default="anotasi_web")
    ap.add_argument("--teratas", type=int, default=120)
    args = ap.parse_args()

    with open(args.provenans, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["kelompok_sumber"] == "web_katalog"]
    akar = pathlib.Path(args.dataset)
    indeks = {p.name: p for sp in ("train", "valid", "test")
              for p in (akar / sp / "images").iterdir()}

    hasil = []
    for i, r in enumerate(rows):
        p = indeks.get(r["nama_berkas"])
        if p is None:
            continue
        s, fd = skor(p)
        if np.isnan(s):
            continue
        hasil.append(dict(nama=r["nama_berkas"], split=r["split"], skor=s, frac_datar=fd,
                          dikenal=bool(re.search(POLA_RENDER_DIKENAL, r["nama_berkas"]))))
        if (i + 1) % 400 == 0:
            print(f"  {i+1}/{len(rows)}")

    hasil.sort(key=lambda d: d["skor"])
    n = len(hasil)
    keluar = pathlib.Path(args.keluar); keluar.mkdir(exist_ok=True)
    with open(keluar / "skor_render.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["peringkat", "nama", "split", "skor",
                                          "frac_datar", "dikenal"])
        w.writeheader()
        for k, d in enumerate(hasil, 1):
            w.writerow(dict(peringkat=k, nama=d["nama"], split=d["split"],
                            skor=f"{d['skor']:.4f}", frac_datar=f"{d['frac_datar']:.3f}",
                            dikenal="ya" if d["dikenal"] else ""))

    # ---------------------------------------------------------- validasi
    dikenal = [(k, d) for k, d in enumerate(hasil, 1) if d["dikenal"]]
    print(f"\n{'='*72}\nVALIDASI pada render yang SUDAH diketahui (dari pola nama)\n{'='*72}")
    print(f"citra terskor: {n}")
    for k, d in dikenal:
        print(f"  peringkat {k:5d}/{n}  (persentil {100*k/n:5.2f} %)  skor {d['skor']:.4f}"
              f"  {d['split']:5s} {d['nama'][:48]}")
    if dikenal:
        terburuk = max(k for k, _ in dikenal)
        print(f"\n  seluruh {len(dikenal)} render dikenal berada di {100*terburuk/n:.1f} % "
              f"teratas (peringkat terburuk {terburuk})")
        cukup = terburuk <= args.teratas
        print(f"  daftar kerja {args.teratas} teratas "
              f"{'MENCAKUP' if cukup else 'TIDAK mencakup'} seluruhnya"
              f" -> heuristik {'layak dipakai' if cukup else 'JANGAN diandalkan sendiri'}")
    print(f"\n  skor: min {hasil[0]['skor']:.4f} | median "
          f"{hasil[n//2]['skor']:.4f} | maks {hasil[-1]['skor']:.4f}")

    kerja = hasil[:args.teratas]
    with open(keluar / "daftar_kerja_render.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["peringkat", "nama_berkas", "split", "skor"])
        for k, d in enumerate(kerja, 1):
            w.writerow([k, d["nama"], d["split"], f"{d['skor']:.4f}"])
    print(f"\nDaftar kerja {len(kerja)} teratas -> {keluar/'daftar_kerja_render.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
