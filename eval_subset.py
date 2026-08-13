#!/usr/bin/env python
"""FASE 3 + 4 — Evaluasi ulang pada subset split uji (uji ketegaran komposisi data).

Menjawab dua pertanyaan rencana perbaikan provenans:
  FASE 3  apakah kesimpulan bertahan bila 33 citra ber-tanda-air (+ citra bocor pHash)
          dikeluarkan dari split uji?
  FASE 4  apakah keunggulan V8 pada oklusi parsial & objek kecil bertahan bila HANYA
          citra CCTV yang dinilai (citra web/katalog dikeluarkan)?

TIDAK ADA INFERENSI ULANG DAN TIDAK ADA PELATIHAN ULANG. `eval_out/cache_V*.npz`
sudah menyimpan prediksi mentah kepala one-to-one **per citra beserta nama berkasnya**,
sehingga subset apa pun dibentuk dengan menyaring cache lalu memanggil pipeline yang
sama (`stratified_ap`, `run_wilcoxon_suite`, `bootstrap_map_ci`). Hasilnya identik
dengan menjalankan ulang inferensi karena `collect_cache` me-*letterbox* tiap citra
sendiri-sendiri (deterministik, tanpa efek batch), proksi oklusi Pers. 3.1 hanya
bergantung pada GT dalam citra yang sama, dan tier densitas dihitung per citra —
menghapus citra lain tidak mengubah atribut citra yang tersisa.

    python eval_subset.py                       # penuh + bersih + cctv, n_boot 1000
    python eval_subset.py --subset cctv          # satu subset saja
    python eval_subset.py --n-boot 0             # lewati bootstrap (cepat, ~2 menit)

Subset `penuh` adalah **kontrol reproduksi**: ia HARUS mereproduksi p = 0,5646 /
0,2076 / 0,0366. Bila tidak, penyaringan cache cacat dan subset lain tidak boleh
ditafsirkan.

Keluaran per subset ke folder sendiri (`hasil_penuh/`, `hasil_bersih/`, `hasil_cctv/`);
`eval_out/`, `runs_tesis/`, `nmsfree_out/` TIDAK ditimpa (CLAUDE.md §14).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import yaml

from y26_stats import PRIMARY_PAIRS, MIN_CELL_GT, bootstrap_map_ci, run_wilcoxon_suite
from y26_strata import (global_match_cache, load_cache, save_strata_csv, stratified_ap)

# p tiga hipotesis utama pada split uji PENUH (FASE 1, 4 Agu 2026) — kontrol reproduksi.
KONTROL_P = {"V8vsV1": 0.5646, "V4vsV1": 0.2076, "V8vsV5": 0.0366}
KATEGORI_CCTV = ("cctv_atcs_diy", "cctv_dishub_demak", "cctv_rekam_layar")


def baca_provenans(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        return {r["nama_berkas"]: r["kelompok_sumber"] for r in csv.DictReader(fh)}


def baca_daftar(path: Path) -> set[str]:
    """Daftar berkas; menerima 'split/nama' maupun 'nama'."""
    if not path.exists():
        return set()
    out = set()
    for baris in path.read_text(encoding="utf-8").splitlines():
        b = baris.strip()
        if b:
            out.add(b.split("/")[-1])
    return out


def saring_cache(cache: dict, simpan: np.ndarray) -> dict:
    """Bentuk cache baru hanya dari citra ber-`simpan` True, dengan indeks diremap.

    `pred[:,0]` dan `gt[:,0]` adalah indeks citra ke dalam `names`; keduanya harus
    dipetakan ulang ke penomoran 0..n_baru-1 agar `stratified_ap` tetap konsisten.
    """
    peta = -np.ones(cache["n_images"], dtype=np.int64)
    peta[np.where(simpan)[0]] = np.arange(int(simpan.sum()))

    def remap(A: np.ndarray) -> np.ndarray:
        if len(A) == 0:
            return A.copy()
        idx = A[:, 0].astype(int)
        m = peta[idx] >= 0
        B = A[m].copy()
        B[:, 0] = peta[idx[m]].astype(B.dtype)
        return B

    return dict(pred=remap(cache["pred"]), gt=remap(cache["gt"]),
                names=np.array([n for n, k in zip(cache["names"], simpan) if k],
                               dtype=object),
                n_images=int(simpan.sum()), imgsz=cache["imgsz"])


def bangun_topeng(names: list[str], prov: dict[str, str], subset: str,
                  watermark: set[str], bocor: set[str]) -> tuple[np.ndarray, str]:
    n = len(names)
    if subset == "penuh":
        return np.ones(n, bool), "seluruh citra uji (kontrol reproduksi)"
    if subset == "bersih":
        keep = np.array([nm not in watermark and nm not in bocor for nm in names])
        return keep, "tanpa citra ber-tanda-air dan tanpa citra bocor pHash"
    if subset == "cctv":
        keep = np.array([prov.get(nm) in KATEGORI_CCTV for nm in names])
        return keep, "hanya citra CCTV (web/katalog, stok ber-tanda-air dikeluarkan)"
    raise SystemExit(f"subset tidak dikenal: {subset}")


def jalankan(subset: str, args, kelas: list[str], prov: dict[str, str],
             watermark: set[str], bocor: set[str]) -> dict:
    varian = ([f"V{i}" for i in range(1, 9)] if args.variants == "all"
              else args.variants.split(","))
    eval_dir = Path(args.eval_out)
    out = Path(f"hasil_{subset}" if not args.prefix else f"{args.prefix}_{subset}")
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*78}\n=== SUBSET '{subset}' -> {out}/ ===")
    rows_by_variant, match_caches = {}, {}
    perlu_boot = {x for p in PRIMARY_PAIRS for x in p} if args.n_boot > 0 else set()
    info = {}

    for v in varian:
        cp = eval_dir / f"cache_{v}.npz"
        if not cp.exists():
            print(f"  [lewati] {v}: {cp} tidak ada")
            continue
        cache = load_cache(cp)
        names = [str(x) for x in cache["names"]]
        keep, alasan = bangun_topeng(names, prov, subset, watermark, bocor)
        sub = saring_cache(cache, keep)
        if not info:
            info = dict(alasan=alasan, n_citra_asal=len(names),
                        n_citra=int(sub["n_images"]), n_gt=int(len(sub["gt"])),
                        dibuang=sorted(n for n, k in zip(names, keep) if not k))
            print(f"  {alasan}")
            print(f"  citra {len(names)} -> {sub['n_images']}   "
                  f"objek GT {len(cache['gt'])} -> {len(sub['gt'])}")
        rows = stratified_ap(sub, kelas)
        rows_by_variant[v] = rows
        if v in perlu_boot:
            match_caches[v] = global_match_cache(sub, kelas)
        lolos = sum(1 for r in rows if r["dim"] != "global" and r["n_gt"] >= MIN_CELL_GT)
        glob = next((r for r in rows if r["dim"] == "global"), None)
        print(f"  {v}: sel lolos>={MIN_CELL_GT} {lolos}/36"
              + (f"   mAP50-95(semua kelas, global)"
                 f" {np.nanmean([r['ap5095'] for r in rows if r['dim']=='global']):.4f}"
                 if glob else ""))

    if len(rows_by_variant) < 2:
        print("  [gagal] butuh >=2 varian")
        return {}

    save_strata_csv(rows_by_variant, out / "strata_ap.csv")

    hasil = {}
    for metric in ("ap5095", "ap50"):
        res = run_wilcoxon_suite(rows_by_variant, metric=metric)
        with open(out / f"wilcoxon_{metric}.csv", "w", newline="", encoding="utf-8") as fh:
            cols = ["pair", "family", "metric", "n", "n_eff", "W", "p", "p_holm",
                    "median_diff", "mean_diff", "rank_biserial", "W_plus", "W_minus",
                    "signif_5pct", "min_n_gt", "n_sel_dibuang", "sel_dibuang"]
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in res:
                w.writerow({c: (f"{r[c]:.6g}" if isinstance(r.get(c), float)
                                else r.get(c, "")) for c in cols})
        if metric == "ap5095":
            print(f"\n  --- Wilcoxon (AP50-95, unit kelas x strata) ---")
            for r in res:
                if r["family"] == "primary":
                    nama = r["pair"].replace(" vs ", "vs").replace(" ", "")
                    hasil[nama] = dict(n=r["n"], p=r["p"], r=r["rank_biserial"],
                                       median=r["median_diff"],
                                       signif=bool(r["signif_5pct"]),
                                       n_dibuang=r["n_sel_dibuang"])
                    print(f"    [UTAMA] {r['pair']:>9}: n={r['n']} "
                          f"(buang {r['n_sel_dibuang']} sel) p={r['p']:.4g} "
                          f"median D={r['median_diff']:+.4f} r={r['rank_biserial']:+.3f}"
                          f" -> {'SIGNIFIKAN' if r['signif_5pct'] else 'tidak signifikan'}")

    if args.n_boot > 0 and len(match_caches) >= 2:
        print(f"\n  --- Bootstrap CI 95% ({args.n_boot} resample, tataran citra) ---")
        boot = bootstrap_map_ci(match_caches, pairs=PRIMARY_PAIRS,
                                n_boot=args.n_boot, seed=args.boot_seed)
        if boot:
            with open(out / "bootstrap_ci.csv", "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(boot[0]))
                w.writeheader()
                for r in boot:
                    w.writerow({k: (f"{x:.6g}" if isinstance(x, float) else x)
                                for k, x in r.items()})
            for r in boot:
                nama = r["pair"].replace(" vs ", "vs").replace(" ", "")
                hasil.setdefault(nama, {}).update(
                    ci_lo=r.get("ci_lo"), ci_hi=r.get("ci_hi"),
                    diff=r.get("diff_point"))
                print(f"    {r['pair']:>9}: D={r['diff_point']:+.4f} "
                      f"CI95=[{r['ci_lo']:+.4f}; {r['ci_hi']:+.4f}]")

    (out / "info_subset.json").write_text(json.dumps(
        dict(subset=subset, **info, n_boot=args.n_boot, boot_seed=args.boot_seed,
             min_cell_gt=MIN_CELL_GT, hipotesis=hasil,
             catatan="Dibentuk dengan menyaring cache_V*.npz menurut nama berkas; "
                     "tanpa inferensi ulang, tanpa pelatihan ulang."),
        indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------------------------- kontrol reproduksi
    if subset == "penuh":
        print(f"\n  --- KONTROL REPRODUKSI ---")
        ok = True
        for nama, p_harap in KONTROL_P.items():
            p = hasil.get(nama, {}).get("p")
            cocok = p is not None and abs(p - p_harap) < 5e-4
            ok &= cocok
            print(f"    {nama}: p={p if p is None else f'{p:.4f}'} "
                  f"(harap {p_harap})  {'COCOK' if cocok else 'TIDAK COCOK'}")
        print(f"    -> {'LOLOS — penyaringan cache sahih' if ok else 'GAGAL — JANGAN tafsirkan subset lain'}")
        hasil["_kontrol_lolos"] = ok
    return hasil


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--eval-out", default="eval_out", help="folder cache_V*.npz")
    ap.add_argument("--variants", default="all")
    ap.add_argument("--subset", default="penuh,bersih,cctv")
    ap.add_argument("--prefix", default="", help="awalan folder keluaran")
    ap.add_argument("--provenans", default="provenans.csv")
    ap.add_argument("--watermark", default="anotasi_provenans/citra_berwatermark_HIPOTESIS.txt")
    ap.add_argument("--bocor", default="phash_eksklusi_test.txt")
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--boot-seed", type=int, default=0)
    args = ap.parse_args()

    kelas = yaml.safe_load(Path(args.data).read_text())["names"]
    kelas = list(kelas.values()) if isinstance(kelas, dict) else list(kelas)
    prov = baca_provenans(Path(args.provenans))
    watermark = baca_daftar(Path(args.watermark))
    bocor = baca_daftar(Path(args.bocor))

    print(f"== FASE 3+4: evaluasi subset (tanpa inferensi ulang) ==")
    print(f"  provenans      : {len(prov)} citra terklasifikasi")
    print(f"  ber-tanda-air  : {len(watermark)} citra (daftar eksklusi)")
    print(f"  bocor pHash    : {len(bocor)} citra sisi uji")
    print(f"  MIN_CELL_GT    : {MIN_CELL_GT}   n_boot: {args.n_boot}")

    ringkas = {}
    for subset in args.subset.split(","):
        ringkas[subset.strip()] = jalankan(subset.strip(), args, kelas, prov,
                                          watermark, bocor)

    # ------------------------------------------------- tabel banding Fase 3.3
    print(f"\n{'='*78}\n=== TABEL BANDING (Fase 3.3 / 4.3) ===\n")
    sub_ada = [s for s in ringkas if ringkas[s]]
    head = f"{'Besaran':<26s}" + "".join(f"{s:>16s}" for s in sub_ada)
    print(head); print("-" * len(head))
    for nama in ("V8vsV1", "V4vsV1", "V8vsV5"):
        for kunci, label, fmt in (("p", f"{nama} p", "{:.4f}"),
                                  ("r", f"{nama} r", "{:+.3f}"),
                                  ("n", f"{nama} n sel", "{:d}")):
            baris = f"{label:<26s}"
            for s in sub_ada:
                v = ringkas[s].get(nama, {}).get(kunci)
                baris += f"{'-' if v is None else fmt.format(v):>16s}"
            print(baris)
    baris = f"{'signifikan 5% (V8vsV5)':<26s}"
    for s in sub_ada:
        v = ringkas[s].get("V8vsV5", {}).get("signif")
        baris += f"{'-' if v is None else ('YA' if v else 'tidak'):>16s}"
    print(baris)

    with open("hasil_banding_subset.json", "w", encoding="utf-8") as fh:
        json.dump(ringkas, fh, indent=2, ensure_ascii=False, default=str)
    print(f"\nRingkasan -> hasil_banding_subset.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
