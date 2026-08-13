#!/usr/bin/env python
"""FASE 1 — Inventarisasi provenans mandiri (rencana perbaikan provenans, Langkah 1.1-1.2).

Mengklasifikasi seluruh 3.389 citra menurut sumbernya, menulis `provenans.csv`, lalu
merakit lembar-kontak untuk pemeriksaan mata: 67 kandidat ber-tanda-air + 30 kontrol
acak dari kategori lain (Langkah 1.2 — "jangan percaya pola nama untuk hal sepenting ini").

    python provenans_audit.py                    # klasifikasi + lembar kontak
    python provenans_audit.py --tanpa-montase    # hanya CSV

⚠️ Dua jebakan yang sudah pernah mengecoh dan sengaja dihindari di sini:
  1. Regex `night-traffic-(12|13)\\b` GAGAL — `_` termasuk karakter kata, jadi `\\b`
     tidak cocok di `night-traffic-12_mp4`. Dipakai `(\\d+)_` lalu bandingkan grup.
  2. Pola hanya-"*.jpg" melewatkan 1.042 berkas .png (30,7 % dataset), 963 di antaranya
     `frame_*`. Di sini jpg+png keduanya diikutsertakan.
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

EKSTENSI = (".jpg", ".jpeg", ".png")
SPLITS = ("train", "valid", "test")

# night-traffic yang benar-benar ada di dataset: 5, 8, 9, 12, 13 (terverifikasi enumerasi).
NT_STOK = {"12", "13"}          # rekaman stok Shutterstock — tanda air
NT_ATCS = {"5", "8", "9"}       # ATCS Yogyakarta — overlay lambang DIY terbaca di audit

KATEGORI_CCTV = ("cctv_atcs_diy", "cctv_dishub_demak", "cctv_rekam_layar")

# Harapan dari AUDIT_PROVENANS_DATASET.md — dipakai sebagai HIPOTESIS, diverifikasi ulang.
HARAPAN = {
    "web_katalog": 1597,
    "cctv_rekam_layar": 1477,
    "cctv_atcs_diy": 161,
    "cctv_dishub_demak": 87,
    "stok_berwatermark": 67,
}
HARAPAN_STOK_SPLIT = {"valid": 34, "test": 33, "train": 0}


def klasifikasi(nama: str) -> tuple[str, str]:
    """Return (kelompok_sumber, dasar_klasifikasi)."""
    m = re.match(r"night-traffic-(\d+)_", nama)
    if m:
        n = m.group(1)
        if n in NT_STOK:
            return "stok_berwatermark", f"prefiks night-traffic-{n} (rekaman stok, tanda air)"
        if n in NT_ATCS:
            return "cctv_atcs_diy", f"prefiks night-traffic-{n} (overlay lambang DIY)"
        return "cctv_belum_terverifikasi", f"prefiks night-traffic-{n} TIDAK dikenali"
    if nama.startswith("Recording"):
        return "cctv_dishub_demak", "prefiks Recording* (overlay DISHUB DEMAK)"
    if nama.startswith("frame_"):
        return "cctv_rekam_layar", "prefiks frame_* (rekam layar penampil CCTV)"
    return "web_katalog", "tidak cocok pola CCTV mana pun (citra web/katalog)"


def kumpulkan(akar: Path) -> list[dict]:
    baris = []
    for sp in SPLITS:
        d = akar / sp / "images"
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir(), key=lambda x: x.name):
            if p.suffix.lower() not in EKSTENSI:
                continue
            kel, dasar = klasifikasi(p.name)
            baris.append(dict(nama_berkas=p.name, split=sp, kelompok_sumber=kel,
                              dasar_klasifikasi=dasar, ekstensi=p.suffix.lower(),
                              _path=p))
    return baris


def lembar_kontak(items: list[dict], tujuan: Path, judul: str,
                  kolom: int = 4, lebar_sel: int = 460) -> None:
    """Montase berlabel agar tanda air (besar & di tengah) terbaca sekali pandang."""
    if not items:
        return
    baris_n = (len(items) + kolom - 1) // kolom
    tinggi_sel = int(lebar_sel * 0.62)
    pad, bar = 6, 22
    W = kolom * (lebar_sel + pad) + pad
    H = baris_n * (tinggi_sel + bar + pad) + pad + 26
    kanvas = Image.new("RGB", (W, H), (18, 20, 24))
    d = ImageDraw.Draw(kanvas)
    d.text((pad, 7), judul, fill=(255, 255, 255))
    for i, it in enumerate(items):
        r, c = divmod(i, kolom)
        x = pad + c * (lebar_sel + pad)
        y = 26 + pad + r * (tinggi_sel + bar + pad)
        try:
            with Image.open(it["_path"]) as im:
                im = im.convert("RGB")
                im.thumbnail((lebar_sel, tinggi_sel))
                kanvas.paste(im, (x + (lebar_sel - im.width) // 2,
                                  y + (tinggi_sel - im.height) // 2))
        except Exception as e:  # citra rusak jangan menggagalkan seluruh montase
            d.text((x + 4, y + 4), f"GAGAL: {e}", fill=(255, 80, 80))
        label = f"[{it['_no']:>3}] {it['split']:<5} {it['nama_berkas'][:44]}"
        d.text((x + 2, y + tinggi_sel + 4), label, fill=(200, 205, 215))
    kanvas.save(tujuan, quality=88)
    print(f"    {tujuan.name}  ({len(items)} citra)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--keluar", default=".", help="folder provenans.csv")
    ap.add_argument("--montase-dir", default="anotasi_provenans")
    ap.add_argument("--n-kontrol", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tanpa-montase", action="store_true")
    args = ap.parse_args()

    baris = kumpulkan(Path(args.dataset))
    print(f"== FASE 1: inventarisasi provenans ({len(baris)} citra) ==\n")

    # ---------------------------------------------------------------- CSV
    keluar = Path(args.keluar); keluar.mkdir(parents=True, exist_ok=True)
    csv_path = keluar / "provenans.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["nama_berkas", "split", "kelompok_sumber",
                                           "dasar_klasifikasi", "ekstensi"])
        w.writeheader()
        for b in baris:
            w.writerow({k: b[k] for k in w.fieldnames})
    print(f"Tersimpan: {csv_path}  ({len(baris)} baris)\n")

    # -------------------------------------------------- tabel komposisi
    tot = Counter(b["kelompok_sumber"] for b in baris)
    per = defaultdict(Counter)
    ext = defaultdict(Counter)
    for b in baris:
        per[b["kelompok_sumber"]][b["split"]] += 1
        ext[b["kelompok_sumber"]][b["ekstensi"]] += 1
    print(f"{'kategori sumber':28s} {'train':>6s} {'valid':>6s} {'test':>6s} "
          f"{'TOTAL':>6s} {'%':>6s} {'harap':>6s} {'cocok':>6s}")
    lolos = True
    for k in sorted(tot, key=lambda x: -tot[x]):
        p, h = per[k], HARAPAN.get(k)
        cocok = "-" if h is None else ("ya" if h == tot[k] else "TIDAK")
        if h is not None and h != tot[k]:
            lolos = False
        print(f"{k:28s} {p['train']:6d} {p['valid']:6d} {p['test']:6d} "
              f"{tot[k]:6d} {100*tot[k]/len(baris):5.1f}% {str(h or '-'):>6s} {cocok:>6s}")
    n_cctv = sum(tot[k] for k in KATEGORI_CCTV)
    print(f"\n  CCTV asli (3 kategori)      : {n_cctv:5d} ({100*n_cctv/len(baris):.1f} %)")
    print(f"  BUKAN CCTV (web/katalog)    : {tot['web_katalog']:5d} "
          f"({100*tot['web_katalog']/len(baris):.1f} %)")
    print(f"  stok ber-tanda-air          : {tot['stok_berwatermark']:5d} "
          f"({100*tot['stok_berwatermark']/len(baris):.1f} %)")

    if tot.get("cctv_belum_terverifikasi"):
        lolos = False
        print(f"\n  ⚠️ {tot['cctv_belum_terverifikasi']} citra night-traffic-* dengan nomor "
              f"TIDAK dikenali — perlu verifikasi visual sebelum dikategorikan.")

    # ------------------------------------------- kriteria lolos Langkah 1.1
    stok = [b for b in baris if b["kelompok_sumber"] == "stok_berwatermark"]
    stok_split = Counter(b["split"] for b in stok)
    print(f"\n{'-'*76}\nKriteria lolos Langkah 1.1:")
    print(f"  total 3.389                : {len(baris)}  "
          f"{'LOLOS' if len(baris) == 3389 else 'GAGAL'}")
    ok_stok = all(stok_split.get(s, 0) == n for s, n in HARAPAN_STOK_SPLIT.items())
    print(f"  stok 67 (valid 34/test 33) : {len(stok)} "
          f"(valid {stok_split.get('valid',0)}/test {stok_split.get('test',0)}/"
          f"train {stok_split.get('train',0)})  {'LOLOS' if ok_stok else 'GAGAL'}")
    print(f"  web_katalog ~1.597         : {tot['web_katalog']}  "
          f"{'LOLOS' if tot['web_katalog'] == 1597 else 'GAGAL'}")
    print(f"  seluruh kategori cocok audit: {'LOLOS' if lolos else 'GAGAL'}")

    # kebocoran kelompok kamera antar-split (bonus: bukti group split bekerja)
    print(f"\nSebaran kelompok night-traffic antar-split (bukti group split):")
    for n in sorted(NT_STOK | NT_ATCS, key=int):
        s = Counter(b["split"] for b in baris
                    if re.match(rf"night-traffic-{n}_", b["nama_berkas"]))
        huni = [f"{k}={v}" for k, v in s.items()]
        print(f"  night-traffic-{n:<3s}: {', '.join(huni)}"
              f"{'  <- satu split saja, tidak bocor' if len(s) == 1 else '  <- LINTAS SPLIT!'}")

    # ------------------------------------------------ Langkah 1.2 montase
    if not args.tanpa_montase:
        md = Path(args.montase_dir); md.mkdir(parents=True, exist_ok=True)
        print(f"\n{'-'*76}\nLangkah 1.2 — lembar kontak untuk pemeriksaan mata -> {md}/")
        for i, b in enumerate(stok, 1):
            b["_no"] = i
        for j in range(0, len(stok), 12):
            potong = stok[j:j + 12]
            lembar_kontak(potong, md / f"montase_watermark_{j//12 + 1:02d}.jpg",
                          f"KANDIDAT TANDA AIR  [{j+1}-{j+len(potong)} dari {len(stok)}]"
                          f"  — tandai yang TIDAK ber-tanda-air")
        lain = [b for b in baris if b["kelompok_sumber"] != "stok_berwatermark"]
        rng = random.Random(args.seed)
        kontrol = rng.sample(lain, min(args.n_kontrol, len(lain)))
        kontrol.sort(key=lambda b: (b["kelompok_sumber"], b["nama_berkas"]))
        for i, b in enumerate(kontrol, 1):
            b["_no"] = i
        for j in range(0, len(kontrol), 12):
            potong = kontrol[j:j + 12]
            lembar_kontak(potong, md / f"montase_kontrol_{j//12 + 1:02d}.jpg",
                          f"KONTROL ACAK (seed {args.seed})  [{j+1}-{j+len(potong)} dari "
                          f"{len(kontrol)}]  — tandai bila ADA tanda air terlewat")
        # daftar hipotesis, dikonfirmasi mata lalu jadi citra_berwatermark.txt
        cal = md / "citra_berwatermark_HIPOTESIS.txt"
        cal.write_text("".join(f"{b['split']}/{b['nama_berkas']}\n" for b in stok),
                       encoding="utf-8")
        (md / "kontrol_acak.txt").write_text(
            "".join(f"{b['split']}/{b['kelompok_sumber']}/{b['nama_berkas']}\n"
                    for b in kontrol), encoding="utf-8")
        print(f"\n  {cal.name}  <- setelah diperiksa mata, salin/sunting menjadi "
              f"citra_berwatermark.txt")

    print(f"\n{'='*76}\nSTATUS FASE 1 (mesin): {'LOLOS' if lolos else 'PERLU TINJAUAN'}")
    print("Sisa Langkah 1.2/1.3/1.4 menuntut mata manusia — lihat montase di atas.")
    return 0 if lolos else 1


if __name__ == "__main__":
    sys.exit(main())
