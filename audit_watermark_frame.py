#!/usr/bin/env python
"""Audit lanjutan — tanda air pada kelompok `frame_*` (1.477 citra).

LATAR. Audit 13 Agu 2026 menghitung 67 citra ber-tanda-air berdasarkan **pola nama**
(`night-traffic-12/13`). Pemeriksaan kontrol acak Langkah 1.2 menemukan **2 dari 30**
citra kategori lain juga ber-tanda-air Shutterstock — keduanya `frame_*` dan keduanya di
split **train** (`frame_000102`, `frame_000256`). Jadi angka 67 adalah **kurang hitung**:
kelompok `frame_*` mencampur rekaman layar penampil CCTV dengan rekaman stok.

STRATEGI. Memeriksa 1.477 citra satu per satu tidak praktis, dan pola nama sudah terbukti
tidak dapat dipercaya untuk ini. Karena `frame_*` berisi bingkai video, citra dari klip
sumber yang sama nyaris identik → dikelompokkan dengan pHash (union-find, ambang Hamming),
lalu **satu perwakilan per klaster** diperiksa mata. Sifat perwakilan berlaku untuk seluruh
anggota klaster, sehingga 1.477 citra terliput oleh ~139 pemeriksaan.

    # tahap 1 — rakit lembar kontak perwakilan klaster
    python audit_watermark_frame.py --lembar

    # tahap 2 — setelah diperiksa mata, daftarkan id klaster ber-tanda-air
    python audit_watermark_frame.py --klaster-watermark 3,17,42 --tulis-daftar
"""
from __future__ import annotations

import argparse
import collections
import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

LUT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
KATEGORI = "cctv_rekam_layar"


def muat(phash_csv: Path, kategori: str) -> list[dict]:
    with open(phash_csv, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["kelompok_sumber"] == kategori]


def klasterkan(rows: list[dict], ambang: int) -> list[list[int]]:
    """Union-find atas jarak Hamming pHash; return daftar klaster (indeks), terurut besar->kecil."""
    h = np.array([int(r["phash_hex"], 16) for r in rows], dtype=np.uint64)
    par = list(range(len(h)))

    def find(x: int) -> int:
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for i0 in range(0, len(h), 256):
        blok = h[i0:i0 + 256]
        x = np.bitwise_xor(blok[:, None], h[None, :])
        D = LUT[x.view(np.uint8).reshape(*x.shape, 8)].sum(-1)
        for i, j in zip(*np.where(D <= ambang)):
            ra, rb = find(i0 + int(i)), find(int(j))
            if ra != rb:
                par[rb] = ra

    kl = collections.defaultdict(list)
    for i in range(len(h)):
        kl[find(i)].append(i)
    return sorted(kl.values(), key=len, reverse=True)


def lembar_crop(items: list[tuple[str, str, str]], tujuan: Path, judul: str,
                kolom: int = 3, frac_w: float = 0.62, frac_h: float = 0.30,
                maks_w: int = 620) -> None:
    """Lembar potongan TENGAH pada resolusi asli.

    Diperlukan karena pemeriksaan miniatur punya **negatif palsu**: tanda air Shutterstock
    berkontras rendah dan tidak terbaca saat diperkecil pada adegan terang & sibuk (terbukti
    pada klip Seoul — bersih di miniatur, ber-tanda-air pada resolusi asli). Memotong pita
    tengah tanpa penskalaan membuat teks tanda air terbaca.
    """
    potongan = []
    for p, atas, bawah in items:
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                W, H = im.size
                cw, ch = int(W * frac_w), int(H * frac_h)
                x0, y0 = (W - cw) // 2, (H - ch) // 2
                c = im.crop((x0, y0, x0 + cw, y0 + ch))
                if c.width > maks_w:                      # perkecil hanya bila sangat besar
                    c = c.resize((maks_w, int(c.height * maks_w / c.width)),
                                 Image.Resampling.LANCZOS)
                potongan.append((c, atas, bawah))
        except Exception:
            continue
    if not potongan:
        return
    lebar_sel = max(c.width for c, _, _ in potongan)
    tinggi_sel = max(c.height for c, _, _ in potongan)
    baris_n = (len(potongan) + kolom - 1) // kolom
    pad, bar = 6, 20
    W = kolom * (lebar_sel + pad) + pad
    H = baris_n * (tinggi_sel + bar + pad) + pad + 26
    kanvas = Image.new("RGB", (W, H), (18, 20, 24))
    d = ImageDraw.Draw(kanvas)
    d.text((pad, 7), judul, fill=(255, 255, 255))
    for i, (c, atas, bawah) in enumerate(potongan):
        r, cc = divmod(i, kolom)
        x = pad + cc * (lebar_sel + pad)
        y = 26 + pad + r * (tinggi_sel + bar + pad)
        kanvas.paste(c, (x, y))
        d.text((x + 2, y + 2), atas, fill=(255, 235, 120))
        d.text((x + 2, y + c.height + 3), bawah, fill=(200, 205, 215))
    kanvas.save(tujuan, quality=92)
    print(f"    {tujuan.name}  ({len(potongan)} potongan tengah)")


def lembar(items: list[tuple[str, str, str]], tujuan: Path, judul: str,
           kolom: int = 4, lebar_sel: int = 460) -> None:
    """items = [(path, label_atas, label_bawah)]"""
    baris_n = (len(items) + kolom - 1) // kolom
    tinggi_sel = int(lebar_sel * 0.62)
    pad, bar = 6, 22
    W = kolom * (lebar_sel + pad) + pad
    H = baris_n * (tinggi_sel + bar + pad) + pad + 26
    kanvas = Image.new("RGB", (W, H), (18, 20, 24))
    d = ImageDraw.Draw(kanvas)
    d.text((pad, 7), judul, fill=(255, 255, 255))
    for i, (p, atas, bawah) in enumerate(items):
        r, c = divmod(i, kolom)
        x = pad + c * (lebar_sel + pad)
        y = 26 + pad + r * (tinggi_sel + bar + pad)
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                im.thumbnail((lebar_sel, tinggi_sel))
                kanvas.paste(im, (x + (lebar_sel - im.width) // 2,
                                  y + (tinggi_sel - im.height) // 2))
        except Exception as e:
            d.text((x + 4, y + 4), f"GAGAL: {e}", fill=(255, 80, 80))
        d.text((x + 2, y + 2), atas, fill=(255, 235, 120))
        d.text((x + 2, y + tinggi_sel + 4), bawah, fill=(200, 205, 215))
    kanvas.save(tujuan, quality=88)
    print(f"    {tujuan.name}  ({len(items)} perwakilan)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--phash", default="phash_semua.csv")
    ap.add_argument("--kategori", default=KATEGORI)
    ap.add_argument("--ambang", type=int, default=12)
    ap.add_argument("--keluar", default="anotasi_provenans")
    ap.add_argument("--lembar", action="store_true", help="rakit lembar kontak perwakilan")
    ap.add_argument("--per-lembar", type=int, default=12)
    ap.add_argument("--klaster-watermark", default="",
                    help="id klaster ber-tanda-air, dipisah koma (hasil periksa mata)")
    ap.add_argument("--tulis-daftar", action="store_true",
                    help="tulis daftar citra ber-tanda-air lengkap dari id klaster")
    args = ap.parse_args()

    rows = muat(Path(args.phash), args.kategori)
    if not rows:
        print(f"[gagal] tidak ada baris kategori '{args.kategori}' di {args.phash}")
        return 1
    kl = klasterkan(rows, args.ambang)
    print(f"== audit tanda air '{args.kategori}' ==")
    print(f"  {len(rows)} citra -> {len(kl)} klaster (ambang Hamming <= {args.ambang})")
    print(f"  klaster >1 anggota: {sum(1 for k in kl if len(k) > 1)} "
          f"(meliput {sum(len(k) for k in kl if len(k) > 1)} citra)")
    print(f"  klaster tunggal   : {sum(1 for k in kl if len(k) == 1)}")

    ds = Path(args.dataset)
    keluar = Path(args.keluar)
    keluar.mkdir(parents=True, exist_ok=True)

    # peta klaster -> anggota, ditulis agar keputusan mata dapat diaudit ulang
    with open(keluar / "klaster_frame.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["klaster_id", "ukuran_klaster", "split", "berkas"])
        for kid, anggota in enumerate(kl):
            for i in anggota:
                w.writerow([kid, len(anggota), rows[i]["split"], rows[i]["berkas"]])
    print(f"  peta klaster -> {keluar/'klaster_frame.csv'}")

    if args.lembar:
        print(f"\n  lembar kontak perwakilan (label kuning = id klaster & ukuran):")
        items = []
        for kid, anggota in enumerate(kl):
            r = rows[anggota[0]]
            sp = collections.Counter(rows[i]["split"] for i in anggota)
            items.append((
                str(ds / r["split"] / "images" / r["berkas"]),
                f"K{kid}  n={len(anggota)}  " + "/".join(f"{k}:{v}" for k, v in sp.items()),
                r["berkas"][:46],
            ))
        for j in range(0, len(items), args.per_lembar):
            potong = items[j:j + args.per_lembar]
            lembar(potong, keluar / f"klaster_frame_{j//args.per_lembar + 1:02d}.jpg",
                   f"PERWAKILAN KLASTER frame_*  [K{j}-K{j+len(potong)-1} dari {len(kl)} klaster]"
                   f"  — tandai id klaster yang BER-TANDA-AIR")
        # lembar potongan tengah resolusi asli — menutup negatif palsu miniatur
        print(f"\n  lembar POTONGAN TENGAH resolusi asli (tanda air terbaca):")
        for j in range(0, len(items), 9):
            potong = items[j:j + 9]
            lembar_crop(potong, keluar / f"crop_klaster_{j//9 + 1:02d}.jpg",
                        f"POTONGAN TENGAH  [K{j}-K{j+len(potong)-1} dari {len(kl)}]"
                        f"  — cari teks tanda air")
        print(f"\n  Periksa lembar di atas, catat id klaster ber-tanda-air, lalu jalankan:")
        print(f"    python {Path(__file__).name} --klaster-watermark <id,id,...> --tulis-daftar")

    if args.klaster_watermark:
        ids = {int(x) for x in args.klaster_watermark.split(",") if x.strip()}
        buruk = [(rows[i]["split"], rows[i]["berkas"], kid)
                 for kid in sorted(ids) if kid < len(kl) for i in kl[kid]]
        per_split = collections.Counter(s for s, _, _ in buruk)
        print(f"\n{'-'*76}\nKlaster ditandai ber-tanda-air: {sorted(ids)}")
        print(f"  citra terdampak: {len(buruk)}  ({dict(per_split)})")
        print(f"  + 67 dari night-traffic-12/13 = {len(buruk) + 67} total ber-tanda-air")
        if args.tulis_daftar:
            out = keluar / "watermark_frame_tambahan.txt"
            out.write_text("".join(f"{s}/{b}\n" for s, b, _ in sorted(buruk)), encoding="utf-8")
            print(f"  -> {out}")
            with open(keluar / "watermark_frame_tambahan.csv", "w", newline="",
                      encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["split", "berkas", "klaster_id"])
                for s, b, kid in sorted(buruk):
                    w.writerow([s, b, kid])
    return 0


if __name__ == "__main__":
    sys.exit(main())
