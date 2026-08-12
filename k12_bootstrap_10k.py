"""k12_bootstrap_10k.py — Ulangi selang kepercayaan bootstrap dengan n_boot lebih besar.

Latar (K-12): pada n_boot = 1.000 batas bawah selang V8 vs V1 hanya +0,000506
(+0,05 poin persen), sehingga rawan berubah tanda karena galat Monte Carlo
bootstrap itu sendiri. Skrip ini memakai ULANG cache pencocokan yang sudah ada
(`eval_out/cache_V*.npz`) sehingga TIDAK ada inferensi ulang — hanya penyusunan
ulang potongan per citra, persis mekanisme Subbab 3.11.5.

Bersifat NON-DESTRUKTIF: menulis ke berkas terpisah (`bootstrap_ci_<n>.csv`),
`bootstrap_ci.csv` hasil 1.000 resample TIDAK ditimpa agar dapat dibandingkan.

Pakai:
  python k12_bootstrap_10k.py --n-boot 10000
  python k12_bootstrap_10k.py --n-boot 10000 --seeds 0,1,2   # cek kestabilan antar-seed
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import yaml

from y26_stats import PRIMARY_PAIRS, bootstrap_map_ci
from y26_strata import global_match_cache, load_cache


def main():
    ap = argparse.ArgumentParser(description="Bootstrap CI ulang dengan n_boot lebih besar (K-12)")
    ap.add_argument("--eval-out", default="eval_out")
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seeds", default="0", help="daftar seed dipisah koma; tiap seed satu baris")
    ap.add_argument("--variants", default="V1,V4,V5,V8", help="varian yang dibutuhkan pasangan utama")
    a = ap.parse_args()

    out_dir = Path(a.eval_out)
    names = yaml.safe_load(Path(a.data).read_text())["names"]

    match_caches = {}
    for v in a.variants.split(","):
        cpath = out_dir / f"cache_{v}.npz"
        if not cpath.exists():
            print(f"[lewati] {v}: {cpath} tidak ada")
            continue
        t0 = time.time()
        match_caches[v] = global_match_cache(load_cache(cpath), names)
        print(f"  cache {v} dimuat & dicocokkan ({time.time() - t0:.1f} dtk)")

    rows = []
    for seed in (int(s) for s in a.seeds.split(",")):
        t0 = time.time()
        res = bootstrap_map_ci(match_caches, pairs=PRIMARY_PAIRS, n_boot=a.n_boot, seed=seed)
        print(f"  bootstrap n={a.n_boot} seed={seed} selesai ({time.time() - t0:.1f} dtk)")
        for r in res:
            print(f"    {r['pair']:<12} selisih {r['diff_point']:+.6f}  "
                  f"CI95 [{r['ci_lo']:+.6f}; {r['ci_hi']:+.6f}]  "
                  f"pos {r['frac_positif']:.4f}  tanpa-nol {r['selang_tanpa_nol']}")
        rows.extend(res)

    dst = out_dir / f"bootstrap_ci_{a.n_boot}.csv"
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nTersimpan: {dst}  (bootstrap_ci.csv 1.000 resample TIDAK ditimpa)")


if __name__ == "__main__":
    main()
