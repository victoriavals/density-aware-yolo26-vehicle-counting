#!/usr/bin/env python
"""Butir 5.3 keputusan pembimbing — sisir MENYELURUH klaim provenans di semua dokumen.

Pembimbing meminta pencarian menyeluruh, bukan koreksi per lokasi yang sudah
teridentifikasi: frasa semacam "dikumpulkan sendiri" berpotensi muncul juga di Abstrak
tesis, Subbab 1.5 (manfaat penelitian), dan Tabel 3.10 (ancaman validitas).

    python sisir_klaim_provenans.py                 # semua .docx di root
    python sisir_klaim_provenans.py --konteks 240

Hanya MEMBACA — tidak mengubah dokumen apa pun.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

# Pola dikelompokkan menurut keputusan pembimbing yang menanganinya.
POLA = {
    "D-B lokasi (Jakarta)": [
        r"(?i)\bjakarta\b", r"(?i)\bdki\b", r"(?i)metropolitan police",
        r"(?i)polda metro", r"(?i)jabodetabek",
    ],
    "D-C sumber data (klaim primer/sendiri)": [
        r"(?i)self[- ]collect", r"(?i)data primer", r"(?i)primary data",
        r"(?i)dikumpulkan sendiri", r"(?i)dipasang (oleh )?peneliti",
        r"(?i)kamera (milik )?sendiri", r"(?i)own camera", r"(?i)installed by the (author|researcher)",
        r"(?i)pengumpulan data primer", r"(?i)direkam sendiri",
    ],
    # Menyebut jumlah 3.389 saja BUKAN klaim; yang bermasalah adalah menyatakan
    # seluruhnya CCTV. Pola dipersempit agar tidak menghasilkan positif palsu.
    "D-D komposisi (klaim CCTV menyeluruh)": [
        r"(?i)\b3[.,]?389\s+(citra|images?|gambar)\s+(cctv|surveillance)",
        r"(?i)seluruhnya (dari )?cctv", r"(?i)all .{0,20}cctv",
        r"(?i)citra cctv lalu lintas", r"(?i)dataset (primer|cctv)\b",
    ],
}
# Kemunculan yang SAH dan tidak boleh dikoreksi (nama sumber pada daftar pustaka dsb).
KECUALIAN = [
    r"(?i)jakarta[- ]cikampek",     # judul sumber sitasi [34]
    r"(?i)astonjadro",              # nama jurnal pada sitasi yang sama
    r"(?i)jakarta,\s*\[?tanggal",   # kota penandatanganan halaman administratif (SAH:
                                    # Universitas Esa Unggul memang di Jakarta)
]
# Frasa yang MENYANGKAL klaim — bila pola cocok di dalam konteks ini, itu kalimat
# koreksi, bukan klaim. Tanpa penjaga ini detektor menandai kalimat perbaikannya sendiri
# (terjadi 13 Agu 2026 pada "none of the material is primary data collected by...").
PENYANGKALAN = [
    r"(?i)\bno(ne|t)?\b[^.]{0,80}$", r"(?i)\bbukan\b[^.]{0,80}$",
    r"(?i)\btidak\b[^.]{0,80}$", r"(?i)rather than[^.]{0,80}$",
]


def teks_paragraf(docx: Path) -> list[str]:
    """Paragraf dokumen sebagai teks polos (termasuk isi tabel)."""
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml").decode("utf8", errors="ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    t = re.sub(r"<[^>]+>", "", xml)
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&apos;", "'"))
    return [b.strip() for b in t.split("\n") if b.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--akar", default=".")
    ap.add_argument("--konteks", type=int, default=170)
    args = ap.parse_args()

    docs = sorted(p for p in Path(args.akar).glob("*.docx") if not p.name.startswith("~$"))
    if not docs:
        print("tidak ada .docx di akar")
        return 1

    total = 0
    ringkas: dict[str, dict[str, int]] = {}
    for d in docs:
        paras = teks_paragraf(d)
        temuan: list[tuple[str, int, str]] = []
        for i, p in enumerate(paras):
            for kel, pols in POLA.items():
                for pol in pols:
                    for m in re.finditer(pol, p):
                        # lewati bila kemunculan berada di dalam frasa kecualian
                        sekitar = p[max(0, m.start() - 30):m.end() + 30]
                        if any(re.search(k, sekitar) for k in KECUALIAN):
                            continue
                        # lewati bila berada dalam kalimat yang MENYANGKAL klaim
                        awal_kal = p.rfind(".", 0, m.start()) + 1
                        depan = p[awal_kal:m.start()]
                        if any(re.search(k, depan) for k in PENYANGKALAN):
                            continue
                        a = max(0, m.start() - args.konteks // 2)
                        cuplik = p[a:a + args.konteks].replace("\n", " ")
                        temuan.append((kel, i, cuplik))
                        break   # satu pola per kelompok per paragraf cukup
        # dedup (kelompok, paragraf)
        unik, seen = [], set()
        for kel, i, c in temuan:
            if (kel, i) in seen:
                continue
            seen.add((kel, i))
            unik.append((kel, i, c))

        print(f"\n{'='*94}\n{d.name}  ({len(paras)} paragraf)")
        print("=" * 94)
        if not unik:
            print("  (bersih — tidak ada klaim yang perlu dikoreksi)")
        per_kel: dict[str, int] = {}
        for kel, i, c in sorted(unik, key=lambda x: (x[0], x[1])):
            per_kel[kel] = per_kel.get(kel, 0) + 1
            print(f"  [{kel}] ¶{i}")
            print(f"      …{c}…")
        ringkas[d.name] = per_kel
        total += len(unik)

    print(f"\n{'='*94}\nRINGKASAN — {total} paragraf perlu ditinjau\n{'='*94}")
    kelompok = list(POLA)
    print(f"{'dokumen':<52s}" + "".join(f"{k.split()[0]:>10s}" for k in kelompok))
    print("-" * (52 + 10 * len(kelompok)))
    for nama, per in ringkas.items():
        print(f"{nama[:51]:<52s}" + "".join(f"{per.get(k,0):>10d}" for k in kelompok))
    print("\nCatatan: kemunculan 'Jakarta-Cikampek' (judul sumber sitasi [34]) sengaja "
          "DIKECUALIKAN\ndan tidak dihitung — sesuai keputusan pembimbing D-B.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
