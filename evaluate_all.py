"""
evaluate_all.py — Orkestrator evaluasi BAB 4 (Subbab 3.11).

  python evaluate_all.py --data dataset/data.yaml --split test --variants all

Untuk tiap varian: (1) metrik global P/R/F1/mAP via validator ultralytics,
(2) cache prediksi mentah kepala one-to-one, (3) AP terstratifikasi per
(kelas × ukuran/oklusi/densitas). Setelah semua varian: uji Wilcoxon —
tiga hipotesis utama (V8vsV1, V4vsV1, V8vsV5, taraf 5%) dan seluruh pasangan
sekunder dengan koreksi Holm — pada unit AP per (kelas × strata).

Keluaran (--out, default eval_out/):
  global_metrics.csv   P, R, F1, mAP50, mAP50-95 per varian (Pers. 3.8–3.11)
  strata_ap.csv        AP50 & AP50-95 per varian × kelas × dimensi × strata
  wilcoxon_ap5095.csv  hasil uji (family, W, p, p_holm, signifikan)
  cache_<V>.npz        prediksi mentah (dipakai ulang, hemat inferensi)
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

from y26_modules import register_ham
from y26_strata import collect_cache, load_cache, save_strata_csv, stratified_ap
from y26_stats import run_wilcoxon_suite


def global_val(weights, data, split, batch, device):
    from ultralytics import YOLO

    m = YOLO(weights)
    r = m.val(data=data, split=split, imgsz=640, batch=batch, device=device,
              plots=False, verbose=False)
    d = r.results_dict
    p = float(d.get("metrics/precision(B)", float("nan")))
    rc = float(d.get("metrics/recall(B)", float("nan")))
    return dict(P=p, R=rc, F1=2 * p * rc / max(p + rc, 1e-9),
                mAP50=float(d.get("metrics/mAP50(B)", float("nan"))),
                mAP50_95=float(d.get("metrics/mAP50-95(B)", float("nan"))))


def main():
    ap = argparse.ArgumentParser(description="Evaluasi terstratifikasi + Wilcoxon (BAB 4)")
    ap.add_argument("--data", required=True)
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--runs", default="runs_tesis")
    ap.add_argument("--variants", default="all")
    ap.add_argument("--out", default="eval_out")
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default=None)
    ap.add_argument("--skip-global", action="store_true", help="lewati val ultralytics")
    ap.add_argument("--refresh-cache", action="store_true")
    args = ap.parse_args()

    register_ham()
    names = yaml.safe_load(Path(args.data).read_text())["names"]
    names = list(names.values()) if isinstance(names, dict) else list(names)
    variants = [f"V{i}" for i in range(1, 9)] if args.variants == "all" else args.variants.split(",")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    rows_by_variant, glob = {}, []
    for v in variants:
        w = Path(args.runs) / v / "weights" / "best.pt"
        if not w.exists():
            print(f"[lewati] {v}: {w} tidak ada"); continue
        print(f"===== {v} =====")
        if not args.skip_global:
            g = global_val(str(w), args.data, args.split, args.batch, args.device)
            glob.append(dict(variant=v, **g))
            print("  global:", {k: round(x, 4) for k, x in g.items()})
        cpath = out / f"cache_{v}.npz"
        cache = (load_cache(cpath) if cpath.exists() and not args.refresh_cache
                 else collect_cache(str(w), args.data, split=args.split,
                                    batch=args.batch, device=args.device, out_path=cpath))
        rows = stratified_ap(cache, names)
        rows_by_variant[v] = rows
        agg = {}
        for r in rows:
            if r["dim"] != "global" and r["n_gt"]:
                agg.setdefault((r["dim"], r["stratum"]), []).append(r["ap5095"])
        print("  mAP50-95 per strata:",
              {f"{d}/{s}": round(sum(a) / len(a), 3) for (d, s), a in sorted(agg.items())})

    if glob:
        with open(out / "global_metrics.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(glob[0]))
            w.writeheader()
            for r in glob:
                w.writerow({k: (f"{x:.4f}" if isinstance(x, float) else x) for k, x in r.items()})
    save_strata_csv(rows_by_variant, out / "strata_ap.csv")

    if len(rows_by_variant) >= 2:
        for metric in ("ap5095", "ap50"):
            res = run_wilcoxon_suite(rows_by_variant, metric=metric)
            f = out / f"wilcoxon_{metric}.csv"
            with open(f, "w", newline="") as fh:
                cols = ["pair", "family", "metric", "n", "n_eff", "W", "p", "p_holm",
                        "median_diff", "mean_diff", "signif_5pct"]
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for r in res:
                    w.writerow({c: (f"{r[c]:.6g}" if isinstance(r.get(c), float) else r.get(c, ""))
                                for c in cols})
            if metric == "ap5095":
                print("\n=== Wilcoxon (AP50-95, unit kelas×strata) ===")
                for r in res:
                    if r["family"] == "primary":
                        print(f"  [UTAMA] {r['pair']:>9}: W={r['W']:.1f} p={r['p']:.4g} "
                              f"median Δ={r['median_diff']:+.4f} -> "
                              f"{'SIGNIFIKAN' if r['signif_5pct'] else 'tidak signifikan'} (5%)")
        (out / "wilcoxon_info.json").write_text(json.dumps(dict(
            unit="AP per (kelas x strata ukuran/oklusi/densitas), global dikecualikan",
            primary=["V8 vs V1", "V4 vs V1", "V8 vs V5"],
            secondary="seluruh pasangan lain, koreksi Holm", alpha=0.05), indent=2))
    print(f"\nSelesai. Hasil di {out}/")


if __name__ == "__main__":
    main()
