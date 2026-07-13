"""
analyze_nmsfree.py — Analisis interaksi NMS-free antarvarian (Subbab 3.7, BAB 4).

Dijalankan SETELAH pelatihan selesai, pada bobot best.pt tiap varian:

  python analyze_nmsfree.py --data dataset/data.yaml --split test \
      --runs runs_tesis --variants V1,V3,V5,V7,V8

Keluaran (folder --out, default nmsfree_out/):
  summary.csv            DR(τ=0,25), miss, dup, CM per varian + Δ terhadap V1
  tau_sweep.csv          DR untuk rentang τ (analisis sensitivitas τ, A-10)
  <V>.json               ringkasan lengkap per varian
  <V>_per_image.csv      DR/CM per citra (bahan uji Wilcoxon berpasangan Tahap 3)
  dr_vs_tau.png          kurva sensitivitas τ semua varian
  cm_hist.png            distribusi Confidence Margin semua varian
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from y26_nmsfree import evaluate_dr_cm, save_summary

DEFAULT_VARIANTS = "V1,V3,V5,V7,V8"  # fokus Subbab 3.8: baseline + varian ber-P2


def main():
    ap = argparse.ArgumentParser(description="Analisis DR/CM/sensitivitas tau kepala one-to-one")
    ap.add_argument("--data", required=True)
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--runs", default="runs_tesis", help="folder induk hasil pelatihan")
    ap.add_argument("--variants", default=DEFAULT_VARIANTS, help="'all' | daftar dipisah koma")
    ap.add_argument("--weights", nargs="*", default=None, help="alternatif: path bobot eksplisit")
    ap.add_argument("--tau", type=float, default=0.25, help="ambang utama (Tabel 3.4)")
    ap.add_argument("--iou", type=float, default=0.5, help="ambang IoU pencocokan prediksi-GT")
    ap.add_argument("--class-agnostic", action="store_true", help="pencocokan tanpa syarat kelas")
    ap.add_argument("--max-images", type=int, default=0, help="0 = seluruh subset")
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default=None)
    ap.add_argument("--out", default="nmsfree_out")
    args = ap.parse_args()

    if args.weights:
        items = [(Path(w).stem, w) for w in args.weights]
    else:
        names = [f"V{i}" for i in range(1, 9)] if args.variants == "all" else args.variants.split(",")
        items = [(v, str(Path(args.runs) / v / "weights" / "best.pt")) for v in names]

    rows, sweeps, cm_all = [], {}, {}
    for name, w in items:
        if not Path(w).exists():
            print(f"[lewati] {name}: {w} tidak ditemukan")
            continue
        print(f"== {name}: {w} ==")
        acc = evaluate_dr_cm(w, args.data, split=args.split, tau_main=args.tau, iou_thr=args.iou,
                             class_aware=not args.class_agnostic, batch=args.batch,
                             device=args.device, max_images=args.max_images)
        s = save_summary(acc, args.out, name)
        rows.append(dict(variant=name, images=s["images"], M=s["M"], DR=s["DR"], miss=s["miss_frac"],
                         dup=s["dup_frac"], coverage=s["coverage"], cm_mean=s["cm_mean"],
                         cm_median=s["cm_median"], cm_p10=s["cm_p10"]))
        sweeps[name] = {t: v["DR"] for t, v in s["taus"].items()}
        cm_all[name] = acc.cms
        print(f"   DR(τ={args.tau:g})={s['DR']:.3f}  miss={s['miss_frac']:.3f}  dup={s['dup_frac']:.3f}"
              f"  CM mean/med={s['cm_mean']:.3f}/{s['cm_median']:.3f}")

    if not rows:
        raise SystemExit("tidak ada varian yang dievaluasi")
    out = Path(args.out); out.mkdir(exist_ok=True)

    ref = next((r for r in rows if r["variant"] == "V1"), rows[0])
    with open(out / "summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) + ["dDR_vs_V1", "dCM_vs_V1"])
        w.writeheader()
        for r in rows:
            r["dDR_vs_V1"] = r["DR"] - ref["DR"]
            r["dCM_vs_V1"] = r["cm_mean"] - ref["cm_mean"]
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})

    taus = sorted(next(iter(sweeps.values())).keys(), key=float)
    with open(out / "tau_sweep.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["tau"] + [n for n, _ in items if n in sweeps])
        for t in taus:
            w.writerow([t] + [f"{sweeps[n][t]:.4f}" for n in sweeps])

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        for n, sw in sweeps.items():
            ax.plot([float(t) for t in taus], [sw[t] for t in taus], marker="o", ms=3, label=n)
        ax.axhline(1.0, ls="--", c="gray", lw=1); ax.axvline(args.tau, ls=":", c="gray", lw=1)
        ax.set_xlabel("ambang confidence τ"); ax.set_ylabel("Duplicate Rate")
        ax.set_title("Sensitivitas τ — Duplicate Rate kepala one-to-one"); ax.legend()
        fig.tight_layout(); fig.savefig(out / "dr_vs_tau.png", dpi=200); plt.close(fig)

        fig, ax = plt.subplots(figsize=(6, 4))
        for n, cms in cm_all.items():
            if cms:
                ax.hist(cms, bins=40, range=(0, 1), histtype="step", density=True, label=n)
        ax.set_xlabel("Confidence Margin"); ax.set_ylabel("kepadatan")
        ax.set_title("Distribusi Confidence Margin per varian"); ax.legend()
        fig.tight_layout(); fig.savefig(out / "cm_hist.png", dpi=200); plt.close(fig)
        print(f"Plot tersimpan: {out/'dr_vs_tau.png'}, {out/'cm_hist.png'}")
    except Exception as e:
        print(f"[plot dilewati] {e}")

    print(f"\nRingkasan: {out/'summary.csv'} | sweep τ: {out/'tau_sweep.csv'}")


if __name__ == "__main__":
    main()
