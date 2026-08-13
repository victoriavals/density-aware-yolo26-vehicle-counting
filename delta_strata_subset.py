#!/usr/bin/env python
"""Selisih AP per strata untuk subset uji — aturan identik `delta_strata.csv`.

Menerapkan aturan yang sama dengan fungsi pembangun `delta_strata.csv` di
`y26_bangun_hasil_bab45.py` (keputusan K4), pada `strata_ap.csv` subset mana pun:

  (a) kolom "semua sel"  : rata-rata selisih atas seluruh sel non-kosong;
  (b) kolom "sel-min"    : hanya sel dengan min(n_gt) >= MIN_CELL_GT (Subbab 3.11.5).

**Angka narasi WAJIB memakai kolom (b).** Kolom (a) memuat sel bervolume 1-27 objek yang
membalik tanda pada beberapa strata — inilah sebabnya klaim lama "+5,1 pp objek kecil,
+3,3 pp kepadatan tinggi" tidak sah (temuan K4).

Penjaga tambahan (sama seperti K4): strata yang hanya menyisakan kelas *pedestrian*
TIDAK boleh dinarasikan sebagai hasil kendaraan — pejalan kaki adalah kelas konteks
dan dikecualikan dari penghitungan (CLAUDE.md §5).

    python delta_strata_subset.py hasil_penuh hasil_bersih hasil_cctv
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from y26_stats import MIN_CELL_GT

PASANGAN = (("V8", "V1"), ("V4", "V1"), ("V8", "V5"))
DIMENSI = (("size", ("small", "medium", "large")),
           ("occlusion", ("no", "partial", "heavy")),
           ("density", ("sparse", "medium", "dense")))


def hitung(strata_csv: Path) -> list[dict]:
    with open(strata_csv, encoding="utf-8") as fh:
        strata = list(csv.DictReader(fh))
    per_cell = defaultdict(dict)
    for r in strata:
        if r["dim"] == "global":
            continue
        per_cell[(r["dim"], r["stratum"], r["class"])][r["variant"]] = (
            int(r["n_gt"] or 0), float(r["AP50_95"]))

    keluar = []
    for a, b in PASANGAN:
        for dim, tiers in DIMENSI:
            for t in tiers:
                semua, selmin, dipakai, dibuang = [], [], [], []
                for (dd, ss, cls), v in per_cell.items():
                    if (dd, ss) != (dim, t) or a not in v or b not in v:
                        continue
                    (na, apa), (nb, apb) = v[a], v[b]
                    if na == 0 or nb == 0:
                        continue
                    semua.append(apa - apb)
                    if min(na, nb) >= MIN_CELL_GT:
                        selmin.append(apa - apb)
                        dipakai.append(cls)
                    else:
                        dibuang.append(f"{cls}(n={min(na, nb)})")
                if not semua:
                    continue
                kendaraan = [c for c in dipakai if c != "pedestrian"]
                if not selmin:
                    layak = "TIDAK - semua sel < 30 GT"
                elif not kendaraan:
                    layak = "TIDAK - hanya pedestrian (kelas konteks) yang lolos"
                elif len(dipakai) == 1:
                    layak = f"HATI-HATI - hanya 1 kelas ({dipakai[0]})"
                else:
                    layak = "ya"
                keluar.append(dict(
                    pasangan=f"{a}-{b}", dim=dim, stratum=t,
                    n_kelas_semua=len(semua),
                    delta_pp_semua=100 * float(np.mean(semua)),
                    n_kelas_selmin=len(selmin),
                    delta_pp_selmin=(100 * float(np.mean(selmin))) if selmin else None,
                    kelas_dipakai="; ".join(sorted(dipakai)),
                    kelas_dibuang="; ".join(dibuang),
                    layak_dinarasikan=layak))
    return keluar


def main() -> int:
    folder = [Path(x) for x in sys.argv[1:]] or [Path("hasil_penuh"),
                                                 Path("hasil_bersih"),
                                                 Path("hasil_cctv")]
    tabel = {}
    for d in folder:
        sp = d / "strata_ap.csv"
        if not sp.exists():
            print(f"[lewati] {sp} tidak ada")
            continue
        rows = hitung(sp)
        tabel[d.name] = {(r["pasangan"], r["dim"], r["stratum"]): r for r in rows}
        with open(d / "delta_strata.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            for r in rows:
                w.writerow({k: (f"{v:+.2f}" if isinstance(v, float) else
                                ("" if v is None else v)) for k, v in r.items()})
        print(f"  {d/'delta_strata.csv'} ({len(rows)} baris)")

    if not tabel:
        return 1
    nama = list(tabel)
    print(f"\n{'='*100}")
    print("SELISIH AP50-95 per strata, kolom SEL-MIN (>=30 GT) — satuan poin persen")
    print("hanya baris layak_dinarasikan = 'ya' yang boleh dikutip di naskah")
    print("=" * 100)
    kunci = [k for k in tabel[nama[0]]]
    head = f"{'pasangan / strata':<34s}" + "".join(f"{n:>14s}" for n in nama) + "   layak"
    for pas in ("V8-V5", "V8-V1", "V4-V1"):
        print(f"\n--- {pas} ---")
        print(head); print("-" * len(head))
        for (p, dim, t) in kunci:
            if p != pas:
                continue
            baris = f"{dim+'/'+t:<34s}"
            layak = ""
            for n in nama:
                r = tabel[n].get((p, dim, t))
                v = r and r["delta_pp_selmin"]
                baris += f"{'-' if v is None else f'{v:+.2f}':>14s}"
                if n == nama[-1] and r:
                    layak = r["layak_dinarasikan"]
            print(baris + f"   {layak}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
