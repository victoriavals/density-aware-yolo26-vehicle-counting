#!/usr/bin/env python
"""FASE 2 — Uji kebocoran near-duplicate lintas split memakai pHash.

Verifikasi split (P2) memeriksa duplikat **md5 identik** + grup kamera x adegan x sesi.
Citra web hasil unduhan beredar dalam beberapa ukuran/kompresi sehingga md5-nya berbeda
meski citranya sama; bingkai video berurutan pun nyaris identik. Kebocoran semacam itu
tidak terdeteksi pemeriksaan yang ada. Skrip ini menutup celah tersebut.

    python uji_phash.py                  # seluruh dataset, ambang Hamming <= 5
    python uji_phash.py --ambang 8       # lebih longgar

⚠️ Mencakup **jpg DAN png**. Sketsa rencana memakai `rglob('*.jpg')` yang melewatkan
1.042 citra (30,7 %) — 963 di antaranya `frame_*`, yaitu bingkai video berurutan, justru
populasi paling rawan near-duplicate antara train (1.198) dan valid (252). Menjalankan
uji ini hanya atas .jpg akan tampak bersih tanpa pernah memeriksa subjek berisiko
tertingginya.

pHash 64-bit tanpa dependensi baru: PIL + scipy.fft (keduanya sudah terpasang), jadi
`imagehash` tidak perlu dipasang.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.fft import dct

EKSTENSI = (".jpg", ".jpeg", ".png")
SPLITS = ("train", "valid", "test")
SISI = 32           # citra diperkecil ke 32x32
SUDUT = 8           # ambil blok DCT 8x8 kiri-atas
LUT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def phash(path: Path) -> np.uint64 | None:
    """pHash 64-bit: grayscale 32x32 -> DCT-II 2D -> blok 8x8 (tanpa DC) -> banding median."""
    try:
        with Image.open(path) as im:
            g = im.convert("L").resize((SISI, SISI), Image.Resampling.LANCZOS)
            a = np.asarray(g, dtype=np.float64)
    except Exception:
        return None
    d = dct(dct(a, axis=0, norm="ortho"), axis=1, norm="ortho")[:SUDUT, :SUDUT]
    v = d.flatten()
    med = np.median(v[1:])                      # buang koefisien DC agar tahan beda kecerahan
    bits = (v > med).astype(np.uint64)
    out = np.uint64(0)
    for b in bits:
        out = np.uint64(out << np.uint64(1)) | np.uint64(b)
    return out


def hamming(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Jarak Hamming tervektor antara dua larik uint64 (broadcast)."""
    x = np.bitwise_xor(a, b)
    return LUT[x.view(np.uint8).reshape(*x.shape, 8)].sum(-1).astype(np.int16)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--keluar", default=".")
    ap.add_argument("--ambang", type=int, default=5, help="jarak Hamming maksimum dilaporkan")
    ap.add_argument("--provenans", default="provenans.csv",
                    help="untuk melabeli kategori sumber pasangan (opsional)")
    args = ap.parse_args()

    akar, keluar = Path(args.dataset), Path(args.keluar)
    keluar.mkdir(parents=True, exist_ok=True)

    kat = {}
    if (pp := Path(args.provenans)).exists():
        with open(pp, encoding="utf-8") as fh:
            kat = {r["nama_berkas"]: r["kelompok_sumber"] for r in csv.DictReader(fh)}

    # ------------------------------------------------------------ hitung pHash
    print("== FASE 2: uji kebocoran near-duplicate (pHash 64-bit) ==\n")
    data: dict[str, list] = {s: [] for s in SPLITS}
    gagal = []
    for s in SPLITS:
        d = akar / s / "images"
        berkas = sorted((p for p in d.iterdir() if p.suffix.lower() in EKSTENSI),
                        key=lambda p: p.name)
        for p in berkas:
            h = phash(p)
            if h is None:
                gagal.append(f"{s}/{p.name}")
                continue
            data[s].append((p.name, h))
        n_png = sum(1 for p in berkas if p.suffix.lower() == ".png")
        print(f"  {s:<6s}: {len(data[s]):5d} pHash  "
              f"({len(berkas) - n_png} jpg + {n_png} png)")
    total = sum(len(v) for v in data.values())
    print(f"  {'JUMLAH':<6s}: {total:5d}" + (f"  ({len(gagal)} gagal dibaca)" if gagal else ""))
    if total != 3389:
        print(f"  ⚠️ total {total} != 3.389 — periksa pola berkas")

    with open(keluar / "phash_semua.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["berkas", "split", "kelompok_sumber", "phash_hex"])
        for s in SPLITS:
            for nama, h in data[s]:
                w.writerow([nama, s, kat.get(nama, "?"), f"{int(h):016x}"])

    # ------------------------------------------- banding pasangan lintas split
    arr = {s: np.array([h for _, h in data[s]], dtype=np.uint64) for s in SPLITS}
    nama = {s: [n for n, _ in data[s]] for s in SPLITS}
    pasangan_uji = [("train", "test"), ("train", "valid"), ("valid", "test")]

    print(f"\n{'-'*76}\nPasangan lintas split, jarak Hamming <= {args.ambang}:\n")
    hasil, ringkas = [], {}
    for a, b in pasangan_uji:
        A, B = arr[a], arr[b]
        if not len(A) or not len(B):
            continue
        temuan, min_global = [], 64
        # potong per blok agar matriks (2372 x 679) tetap ringan
        for i0 in range(0, len(A), 512):
            blok = A[i0:i0 + 512]
            D = hamming(blok[:, None], B[None, :])
            min_global = min(min_global, int(D.min()))
            ii, jj = np.where(D <= args.ambang)
            for i, j in zip(ii, jj):
                temuan.append((i0 + int(i), int(j), int(D[i, j])))
        ringkas[(a, b)] = (len(temuan), min_global, len(A) * len(B))
        print(f"  {a:>5s} x {b:<5s}: {len(A)*len(B):>9,d} pasangan | "
              f"jarak minimum {min_global:2d} | {len(temuan):4d} pasangan <= {args.ambang}")
        for i, j, d in sorted(temuan, key=lambda t: t[2]):
            na, nb = nama[a][i], nama[b][j]
            hasil.append(dict(split_a=a, berkas_a=na, kategori_a=kat.get(na, "?"),
                              split_b=b, berkas_b=nb, kategori_b=kat.get(nb, "?"),
                              jarak_hamming=d))

    with open(keluar / "phash_pasangan.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["split_a", "berkas_a", "kategori_a",
                                           "split_b", "berkas_b", "kategori_b",
                                           "jarak_hamming"])
        w.writeheader()
        for r in hasil:
            w.writerow(r)

    # ------------------------------------------------------------- kesimpulan
    n_tt = ringkas.get(("train", "test"), (0, 64, 0))[0]
    n_tv = ringkas.get(("train", "valid"), (0, 64, 0))[0]
    print(f"\n{'-'*76}\nKriteria lolos Langkah 2.2: nol pasangan <= {args.ambang} "
          f"antara train dan test")
    print(f"  train x test : {n_tt} pasangan -> {'LOLOS' if n_tt == 0 else 'TEMUAN — WAJIB DILAPORKAN'}")
    print(f"  train x valid: {n_tv} pasangan -> "
          f"{'bersih' if n_tv == 0 else 'TEMUAN (memengaruhi early stopping)'}")

    if hasil:
        print(f"\n  {len(hasil)} pasangan tersimpan di phash_pasangan.csv. Rincian per kategori:")
        per_kat = {}
        for r in hasil:
            k = (r["split_a"], r["split_b"], r["kategori_a"], r["kategori_b"])
            per_kat[k] = per_kat.get(k, 0) + 1
        for (sa, sb, ka, kb), n in sorted(per_kat.items(), key=lambda kv: -kv[1]):
            print(f"    {n:4d}  {sa}({ka}) <-> {sb}({kb})")
        print("\n  Tindakan (sesuai rencana Fase 2): citra sisi TEST masuk daftar eksklusi")
        print("  Fase 3. `train` TIDAK disentuh — bobot sudah terlatih dengannya.")
        if n_tt:
            sisi_test = sorted({r["berkas_b"] for r in hasil
                                if r["split_a"] == "train" and r["split_b"] == "test"})
            (keluar / "phash_eksklusi_test.txt").write_text(
                "".join(f"{n}\n" for n in sisi_test), encoding="utf-8")
            print(f"  -> phash_eksklusi_test.txt ({len(sisi_test)} citra unik)")
    else:
        print("\n  Tidak ada pasangan near-duplicate lintas split pada ambang ini.")

    print(f"\n{'='*76}\nSTATUS FASE 2: {'LOLOS (bersih)' if n_tt == 0 else 'ADA TEMUAN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
