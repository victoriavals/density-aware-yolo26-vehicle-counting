"""
bandingkan_gt.py — Bandingkan hitung manual DUA penghitung (protokol Subbab 3.10.1).

Naskah mensyaratkan: "Penghitungan dilakukan oleh dua penghitung secara terpisah pada
seluruh klip, kemudian hasil keduanya dibandingkan per interval. Interval yang selisih
hitungnya tidak nol ditinjau ulang bersama hingga diperoleh kesepakatan, dan tingkat
kesesuaian [awal] dilaporkan."

Skrip ini menghitung TINGKAT KESESUAIAN AWAL (sebelum peninjauan) — angka yang wajib
dilaporkan di BAB 4 — dan menuliskan daftar baris yang perlu ditinjau bersama.

Pakai:
  # setelah kedua penghitung selesai mengisi salinan masing-masing
  python bandingkan_gt.py --a video_uji/gt_1_vidiouji_A.csv --b video_uji/gt_1_vidiouji_B.csv

  # sekaligus banyak klip (pasangan dicari otomatis: *_A.csv <-> *_B.csv)
  python bandingkan_gt.py --dir video_uji

Keluaran:
  <stem>_perbedaan.csv   baris yang berbeda (bahan peninjauan bersama)
  ringkasan di layar     kesesuaian keseluruhan, per kelas, per arah + statistik selisih

Setelah ditinjau bersama, sepakati angkanya, simpan sebagai gt_<klip>.csv (tanpa akhiran
_A/_B), lalu jalankan y26_counting.py memakai berkas kesepakatan itu.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

KOLOM = ("interval", "class", "direction", "count")


def baca(path: Path) -> dict[tuple, int]:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    if not rows:
        raise SystemExit(f"[gagal] {path} kosong")
    kurang = [c for c in KOLOM if c not in rows[0]]
    if kurang:
        raise SystemExit(f"[gagal] {path} tidak punya kolom {kurang}; ditemukan {list(rows[0])}")
    out = {}
    for i, r in enumerate(rows, start=2):
        try:
            k = (int(r["interval"]), r["class"].strip(), r["direction"].strip().lower())
            out[k] = int(float(r["count"] or 0))
        except ValueError as e:
            raise SystemExit(f"[gagal] {path} baris {i}: nilai tidak sah ({e})")
    return out


def bandingkan(pa: Path, pb: Path) -> dict:
    A, B = baca(pa), baca(pb)
    hanya_a, hanya_b = sorted(set(A) - set(B)), sorted(set(B) - set(A))
    kunci = sorted(set(A) & set(B))
    if not kunci:
        raise SystemExit(f"[gagal] tak ada baris yang bersesuaian antara {pa.name} dan {pb.name}")

    beda, cocok = [], 0
    per_kelas: dict[str, list[int]] = defaultdict(list)
    per_arah: dict[str, list[int]] = defaultdict(list)
    tot_a = tot_b = 0
    jumlah_selisih = 0
    for k in kunci:
        a, b = A[k], B[k]
        tot_a += a; tot_b += b
        sama = a == b
        cocok += sama
        per_kelas[k[1]].append(sama)
        per_arah[k[2]].append(sama)
        if not sama:
            jumlah_selisih += abs(a - b)
            beda.append(dict(interval=k[0], **{"class": k[1]}, direction=k[2],
                             count_A=a, count_B=b, selisih=a - b))

    n = len(kunci)
    stem = pa.stem.replace("_A", "").replace("_a", "")
    out_beda = pa.with_name(f"{stem}_perbedaan.csv")
    if beda:
        with open(out_beda, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(beda[0]))
            w.writeheader(); w.writerows(beda)

    return dict(nama=stem, n=n, cocok=cocok, kesesuaian=cocok / n,
                n_beda=len(beda), jumlah_selisih=jumlah_selisih,
                total_a=tot_a, total_b=tot_b,
                per_kelas={c: sum(v) / len(v) for c, v in sorted(per_kelas.items())},
                per_arah={d: sum(v) / len(v) for d, v in sorted(per_arah.items())},
                hanya_a=hanya_a, hanya_b=hanya_b,
                berkas_beda=str(out_beda) if beda else None)


def lapor(r: dict) -> None:
    print(f"\n=== {r['nama']} ===")
    print(f"  baris dibandingkan      : {r['n']}")
    print(f"  KESESUAIAN AWAL         : {r['kesesuaian']*100:.1f}%  ({r['cocok']}/{r['n']} baris identik)")
    print(f"  baris perlu ditinjau    : {r['n_beda']}  (total selisih {r['jumlah_selisih']} kendaraan)")
    print(f"  total hitungan A vs B   : {r['total_a']} vs {r['total_b']} "
          f"(beda {abs(r['total_a']-r['total_b'])}, {abs(r['total_a']-r['total_b'])/max(r['total_a'],1)*100:.1f}%)")
    print("  kesesuaian per kelas    : " + ", ".join(f"{c} {v*100:.0f}%" for c, v in r["per_kelas"].items()))
    print("  kesesuaian per arah     : " + ", ".join(f"{d} {v*100:.0f}%" for d, v in r["per_arah"].items()))
    if r["hanya_a"] or r["hanya_b"]:
        print(f"  [peringatan] baris hanya di A: {len(r['hanya_a'])}, hanya di B: {len(r['hanya_b'])} "
              f"-> pastikan kedua penghitung memakai template yang sama")
    if r["berkas_beda"]:
        print(f"  daftar perbedaan        : {r['berkas_beda']}  <- tinjau bersama, sepakati angkanya")
    else:
        print("  kedua penghitung SEPAKAT penuh — tidak perlu peninjauan")


def main() -> None:
    ap = argparse.ArgumentParser(description="Bandingkan hitung manual dua penghitung (3.10.1)")
    ap.add_argument("--a", help="CSV penghitung A")
    ap.add_argument("--b", help="CSV penghitung B")
    ap.add_argument("--dir", help="folder berisi pasangan *_A.csv dan *_B.csv")
    a = ap.parse_args()

    pasangan = []
    if a.dir:
        d = Path(a.dir)
        for pa in sorted(d.glob("*_A.csv")):
            pb = pa.with_name(pa.name.replace("_A.csv", "_B.csv"))
            if pb.exists():
                pasangan.append((pa, pb))
            else:
                print(f"[lewati] {pa.name}: pasangannya ({pb.name}) tidak ada")
        if not pasangan:
            raise SystemExit(f"[gagal] tak ada pasangan *_A.csv/*_B.csv di {d}/")
    elif a.a and a.b:
        pasangan = [(Path(a.a), Path(a.b))]
    else:
        raise SystemExit("[gagal] beri --a dan --b, atau --dir")

    hasil = [bandingkan(pa, pb) for pa, pb in pasangan]
    for r in hasil:
        lapor(r)

    if len(hasil) > 1:
        n = sum(r["n"] for r in hasil); c = sum(r["cocok"] for r in hasil)
        print(f"\n=== GABUNGAN {len(hasil)} klip ===")
        print(f"  KESESUAIAN AWAL ANTARPENGHITUNG: {c/n*100:.1f}%  ({c}/{n} baris)")
        print(f"  total baris perlu ditinjau     : {sum(r['n_beda'] for r in hasil)}")
        print("  (angka kesesuaian ini yang dilaporkan di BAB 4 sesuai Subbab 3.10.1)")


if __name__ == "__main__":
    main()
