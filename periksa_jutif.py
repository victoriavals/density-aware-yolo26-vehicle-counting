#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daftar periksa JUTIF berangka untuk naskah artikel.

Mengukur, bukan menebak: jumlah kata judul & abstrak, proporsi keempat bagian utama,
monotonisitas sitasi, rasio jurnal/prosiding, rujukan mutakhir, buku, sitasi diri,
serta kelengkapan rujukan silang tabel dan gambar.

    python periksa_jutif.py JUTIF_Paper_..._REVISI2.docx
"""
from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

BAGIAN = ("INTRODUCTION", "METHOD", "RESULT", "DISCUSSIONS", "CONCLUSION")
BATAS = dict(judul_kata=(0, 20), abstrak_kata=(150, 250))
TAHUN_MUTAKHIR = 2021          # "mutakhir" = terbit >= tahun ini


def paragraf(docx: Path) -> list[str]:
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml").decode("utf8", errors="ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    t = re.sub(r"<[^>]+>", "", xml)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&apos;", "'")):
        t = t.replace(a, b)
    return [x.strip() for x in t.split("\n") if x.strip()]


def main() -> int:
    src = Path(sys.argv[1] if len(sys.argv) > 1
               else "JUTIF_Paper_DA-YOLO26_Firdaus_REVISI2.docx")
    if not src.exists():
        print(f"[gagal] {src} tidak ada")
        return 1
    P = paragraf(src)
    print(f"== Daftar periksa JUTIF — {src.name} ==")
    print(f"   {len(P)} paragraf\n")

    # ── batas bagian ─────────────────────────────────────────────────────────
    idx = {}
    for i, p in enumerate(P):
        if p.strip().upper() in BAGIAN and len(p) < 40:
            idx.setdefault(p.strip().upper(), i)
    # akhir badan = REFERENCES / CONFLICT
    akhir = next((i for i, p in enumerate(P)
                  if p.strip().upper().startswith(("CONFLICT", "REFERENCES"))), len(P))

    urut = sorted(idx.items(), key=lambda kv: kv[1])
    batas = []
    for k, (nama, i) in enumerate(urut):
        j = urut[k + 1][1] if k + 1 < len(urut) else akhir
        batas.append((nama, i, j))

    # ── judul & abstrak ──────────────────────────────────────────────────────
    judul = P[0]
    abstrak = next((p for p in P if p.startswith("Automatic vehicle counting")), "")
    print("-- Judul & abstrak --")
    nj = len(judul.split())
    print(f"  judul   : {nj} kata   {'OK' if nj <= 20 else 'PERIKSA (>20)'}")
    print(f"            {judul[:96]}")
    na = len(abstrak.split())
    lo, hi = BATAS["abstrak_kata"]
    sisa = hi - na
    print(f"  abstrak : {na} kata   batas {lo}-{hi}   "
          f"{'OK' if lo <= na <= hi else 'LANGGAR'}   sisa ruang {sisa} kata"
          + ("  <-- MEPET" if 0 <= sisa <= 15 else ""))

    # ── proporsi bagian ──────────────────────────────────────────────────────
    print("\n-- Proporsi bagian (kata badan, tanpa daftar pustaka) --")
    kata = {}
    for nama, i, j in batas:
        kata[nama] = sum(len(p.split()) for p in P[i + 1:j])
    total = sum(kata.values())
    for nama, i, j in batas:
        pct = 100 * kata[nama] / total if total else 0
        tanda = ""
        if nama == "RESULT":
            tanda = "  <-- di bawah 45 %" if pct < 45 else "  (>=45 %)"
        print(f"  {nama:<13} {kata[nama]:6d} kata   {pct:5.1f} %{tanda}")
    print(f"  {'TOTAL':<13} {total:6d} kata")

    # ── sitasi ───────────────────────────────────────────────────────────────
    print("\n-- Sitasi --")
    badan = " ".join(P[:akhir])
    nomor = [int(n) for m in re.finditer(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", badan)
             for n in re.findall(r"\d+", m.group(1))]
    pertama, urut_ok, sebelumnya = {}, True, 0
    for n in nomor:
        if n not in pertama:
            pertama[n] = len(pertama) + 1
            if n != sebelumnya + 1:
                urut_ok = False
            sebelumnya = max(sebelumnya, n)
    print(f"  rujukan dipakai di badan : {len(pertama)} nomor unik, maks [{max(nomor) if nomor else 0}]")
    print(f"  monotonisitas kemunculan : {'OK' if urut_ok else 'TIDAK monoton'}")
    if not urut_ok:
        salah = [n for k, n in enumerate(dict.fromkeys(nomor), 1) if n != k][:8]
        print(f"     nomor pertama yang menyimpang: {salah}")

    # daftar pustaka
    ref = [p for p in P[akhir:] if re.match(r"^\[\d+\]", p.strip())]
    print(f"  entri daftar pustaka     : {len(ref)}")
    if ref:
        thn = [int(m.group()) for p in ref
               if (m := re.search(r"\b(19|20)\d{2}\b", p))]
        mutakhir = sum(1 for t in thn if t >= TAHUN_MUTAKHIR)
        print(f"  tahun terbaca            : {len(thn)} dari {len(ref)}")
        print(f"  mutakhir (>= {TAHUN_MUTAKHIR})       : {mutakhir}"
              f"  ({100*mutakhir/len(ref):.1f} %)")
        jur = sum(1 for p in ref if re.search(r"(?i)\b(journal|jurnal|trans\.|letters|"
                                              r"review|vol\.)", p))
        pros = sum(1 for p in ref if re.search(r"(?i)(proceedings|conference|symposium|"
                                               r"workshop|\bconf\.|CVPR|ICCV|ECCV|NeurIPS)", p))
        buku = sum(1 for p in ref if re.search(r"(?i)(press|publisher|\bed\.\b|edition|"
                                               r"springer|wiley|elsevier book)", p))
        arxiv = sum(1 for p in ref if re.search(r"(?i)(arxiv|preprint)", p))
        diri = sum(1 for p in ref if re.search(r"(?i)(firdaus|sandfreni)", p))
        print(f"  jurnal (heuristik)       : {jur} ({100*jur/len(ref):.1f} %)")
        print(f"  prosiding                : {pros} ({100*pros/len(ref):.1f} %)")
        print(f"  jurnal+prosiding         : {jur+pros} ({100*(jur+pros)/len(ref):.1f} %)")
        print(f"  buku                     : {buku}")
        print(f"  praterbit/arXiv          : {arxiv}")
        print(f"  sitasi diri              : {diri}")

    # ── tabel & gambar ───────────────────────────────────────────────────────
    print("\n-- Tabel & gambar --")
    with zipfile.ZipFile(src) as z:
        x = z.read("word/document.xml").decode("utf8", errors="ignore")
        n_draw = len(re.findall(r"<w:drawing", x))
        n_tbl = len(re.findall(r"<w:tbl>", x))
        n_media = len([m for m in z.namelist()
                       if m.startswith("word/media/") and not m.endswith("/")])
    cap_t = sorted({int(m.group(1)) for m in re.finditer(r"^Table (\d+)\.", "\n".join(P), re.M)})
    cap_f = sorted({int(m.group(1)) for m in re.finditer(r"^Figure (\d+)\.", "\n".join(P), re.M)})
    print(f"  keterangan Table  : {cap_t}")
    print(f"  keterangan Figure : {cap_f}")
    print(f"  objek w:tbl={n_tbl}  w:drawing={n_draw}  media={n_media}")
    for n in cap_t:
        dirujuk = len(re.findall(rf"Table {n}\b", badan)) > 0
        if not dirujuk:
            print(f"  ! Table {n} TIDAK dirujuk di badan")
    for n in cap_f:
        dirujuk = len(re.findall(rf"Figure {n}\b", badan)) > 0
        if not dirujuk:
            print(f"  ! Figure {n} TIDAK dirujuk di badan")
    # duplikat / lompatan nomor
    for nama, lst in (("Table", cap_t), ("Figure", cap_f)):
        if lst and lst != list(range(1, len(lst) + 1)):
            print(f"  ! penomoran {nama} tidak berurutan 1..n: {lst}")
    # URUTAN FISIK — jurnal menomori menurut urutan kemunculan. Pemeriksaan himpunan
    # saja tidak cukup: pernah lolos padahal urutannya 1,2,3,4,5,9,6,7,8 (14 Agu 2026).
    teks_semua = "\n".join(P)
    for nama in ("Table", "Figure"):
        urut = [int(m.group(1)) for m in re.finditer(rf"^{nama} (\d+)\.", teks_semua, re.M)]
        # buang pengulangan berturut-turut (keterangan bisa terpecah antar-paragraf)
        rapi = [n for k, n in enumerate(urut) if k == 0 or n != urut[k - 1]]
        ok = rapi == sorted(set(rapi)) and rapi == list(range(1, len(rapi) + 1))
        print(f"  urutan fisik {nama:<7}: {rapi}  {'OK' if ok else '! TIDAK URUT KEMUNCULAN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
