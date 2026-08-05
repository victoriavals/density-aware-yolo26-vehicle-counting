"""
y26_bangun_hasil_bab45.py — Bangun/segarkan ulang folder hasil_bab4_5/ (visualisasi + data ringkas).

Merakit seluruh artefak BAB 4-5 dari sumber yang sudah ada (eval_out/, nmsfree_out/,
runs_tesis/, anotasi_oklusi/, dataset/) menjadi satu folder terdokumentasi
(hasil_bab4_5/). Membaca data mentah langsung -- tidak mengetik ulang angka secara
manual -- agar selalu konsisten dengan eval_out/*.csv yang menjadi sumber kebenaran.

DIJALANKAN ULANG kapan pun sumber berubah, terutama setelah:
  - V8_normw (uji ketegaran) selesai training -> bab_07_ketegaran()
  - GT counting terisi + y26_counting.py dijalankan -> lengkapi folder 09 manual
  - Keputusan K6 (multi-seed) diambil -> lengkapi folder 10 manual

Pakai:
  python y26_bangun_hasil_bab45.py              # jalankan semua bagian
  python -c "from y26_bangun_hasil_bab45 import bab_07_ketegaran; bab_07_ketegaran()"
"""
from __future__ import annotations

import csv
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(".")
OUT = ROOT / "hasil_bab4_5"
plt.rcParams.update({"figure.dpi": 140, "savefig.dpi": 140, "font.size": 10,
                     "axes.grid": True, "grid.alpha": 0.3})

VARIAN_LABEL = {
    "V1": "V1 Baseline", "V2": "V2 HAM", "V3": "V3 P2", "V4": "V4 DALW",
    "V5": "V5 HAM+P2", "V6": "V6 HAM+DALW", "V7": "V7 P2+DALW", "V8": "V8 Penuh",
}
WARNA = {"V1": "#888888", "V2": "#4C72B0", "V3": "#55A868", "V4": "#C44E52",
        "V5": "#8172B2", "V6": "#CCB974", "V7": "#64B5CD", "V8": "#DD8452"}


def simpan(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path}")


# ======================================================================
# 01 — DATASET
# ======================================================================
def bab_01_dataset():
    d = OUT / "01_dataset"
    names = ["big-vehicle", "car", "pedestrian", "two-wheeler"]
    rows = []
    for split in ("train", "valid", "test"):
        c = Counter()
        for lbl in (ROOT / f"dataset/{split}/labels").glob("*.txt"):
            for line in lbl.read_text().split("\n"):
                t = line.split()
                if t:
                    c[names[int(t[0])]] += 1
        n_img = len(list((ROOT / f"dataset/{split}/images").glob("*")))
        rows.append(dict(split=split, n_citra=n_img, **{k: c.get(k, 0) for k in names}))

    with open(d / "distribusi_kelas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["split", "n_citra", *names])
        w.writeheader(); w.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    splits = [r["split"] for r in rows]
    n_img = [r["n_citra"] for r in rows]
    axes[0].bar(splits, n_img, color=["#4C72B0", "#55A868", "#C44E52"])
    for i, v in enumerate(n_img):
        axes[0].text(i, v + 20, str(v), ha="center", fontsize=10)
    axes[0].set_title("Jumlah citra per subset (split berbasis grup)")
    axes[0].set_ylabel("jumlah citra")

    x = np.arange(len(names)); w = 0.25
    for i, r in enumerate(rows):
        axes[1].bar(x + i * w, [r[k] for k in names], w, label=r["split"])
    axes[1].set_xticks(x + w, names, rotation=20)
    axes[1].set_title("Jumlah instans per kelas per subset")
    axes[1].set_ylabel("jumlah instans")
    axes[1].legend()
    fig.tight_layout()
    simpan(fig, d / "distribusi_kelas.png")

    for f in ("bukti_split_grup.csv", "bukti_split_citra.csv"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
            print(f"  copy -> {d/f}")


# ======================================================================
# 02 — GRID SEARCH DALW
# ======================================================================
def bab_02_grid():
    d = OUT / "02_grid_search_dalw"
    best = json.loads((ROOT / "dalw_best.json").read_text())
    rows = best["all"]
    alphas = sorted({r["alpha"] for r in rows})
    sigmas = sorted({r["sigma"] for r in rows})
    M = np.full((len(alphas), len(sigmas)), np.nan)
    for r in rows:
        M[alphas.index(r["alpha"]), sigmas.index(r["sigma"])] = r["map5095"]

    with open(d / "tabel_grid_search.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["alpha", "sigma", "mAP50_95"])
        for r in sorted(rows, key=lambda r: -r["map5095"]):
            w.writerow([r["alpha"], r["sigma"], f"{r['map5095']:.5f}"])

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(M, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(sigmas)), sigmas); ax.set_yticks(range(len(alphas)), alphas)
    ax.set_xlabel("sigma (sigma)"); ax.set_ylabel("alpha")
    ax.set_title(f"Grid search DALW — mAP50-95 val (V8, 60 epoch)\nterpilih: alpha={best['best']['alpha']}, sigma={best['best']['sigma']}")
    for i in range(len(alphas)):
        for j in range(len(sigmas)):
            v = M[i, j]
            if not np.isnan(v):
                bi = (alphas[i] == best["best"]["alpha"] and sigmas[j] == best["best"]["sigma"])
                ax.text(j, i, f"{v:.4f}" + (" *" if bi else ""), ha="center", va="center",
                        color="white" if v < np.nanmean(M) else "black",
                        fontweight="bold" if bi else "normal")
    fig.colorbar(im, ax=ax, label="mAP50-95")
    fig.tight_layout()
    simpan(fig, d / "heatmap_grid_search.png")


# ======================================================================
# 03 — KOMPLEKSITAS MODEL (Tabel 3.7)
# ======================================================================
def bab_03_kompleksitas():
    d = OUT / "03_kompleksitas_model"
    shutil.copy(ROOT / "eval_out/complexity.csv", d / "tabel_kompleksitas.csv")
    rows = list(csv.DictReader(open(ROOT / "eval_out/complexity.csv")))
    variants = [r["variant"] for r in rows]
    cols = {k: [float(r[k]) for r in rows] for k in
           ("params_M", "gflops", "peak_gpu_train_gb", "train_hours", "fps")}
    colors = [WARNA[v] for v in variants]

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    specs = [("params_M", "Jumlah parameter (juta)"), ("gflops", "GFLOPs (640x640)"),
            ("peak_gpu_train_gb", "VRAM puncak latih (GB)"), ("fps", "FPS inferensi (batch 1, FP16)")]
    for ax, (key, title) in zip(axes.flat, specs):
        ax.bar(variants, cols[key], color=colors)
        ax.set_title(title); ax.set_ylabel(title.split("(")[-1].rstrip(")") if "(" in title else "")
        for i, v in enumerate(cols[key]):
            ax.text(i, v, f"{v:.1f}" if v > 5 else f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    fig.suptitle("Tabel 3.7 — Kompleksitas & Efisiensi Model (8 Varian)")
    fig.tight_layout()
    simpan(fig, d / "grafik_kompleksitas_4panel.png")

    fig, ax = plt.subplots(figsize=(6, 5))
    gm = {r["variant"]: float(r["mAP50_95"]) for r in csv.DictReader(open(ROOT / "eval_out/global_metrics.csv"))}
    for v in variants:
        ax.scatter(cols["fps"][variants.index(v)], gm[v] * 100, s=120, color=WARNA[v], label=VARIAN_LABEL[v])
        ax.annotate(v, (cols["fps"][variants.index(v)], gm[v] * 100), textcoords="offset points", xytext=(6, 4))
    ax.set_xlabel("FPS inferensi"); ax.set_ylabel("mAP50-95 test (%)")
    ax.set_title("Trade-off akurasi vs kecepatan inferensi")
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    simpan(fig, d / "grafik_tradeoff_akurasi_fps.png")


# ======================================================================
# 04 — ABLASI DETEKSI (metrik global + strata + Wilcoxon + bootstrap)
# ======================================================================
def bab_04_ablasi():
    d = OUT / "04_ablasi_deteksi"
    for f in ("global_metrics.csv", "strata_ap.csv", "wilcoxon_ap5095.csv", "wilcoxon_ap50.csv",
             "bootstrap_ci.csv", "wilcoxon_info.json"):
        shutil.copy(ROOT / f"eval_out/{f}", d / f)

    gm = list(csv.DictReader(open(ROOT / "eval_out/global_metrics.csv")))
    variants = [r["variant"] for r in gm]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    vals50 = [float(r["mAP50"]) * 100 for r in gm]
    vals5095 = [float(r["mAP50_95"]) * 100 for r in gm]
    x = np.arange(len(variants)); w = 0.35
    ax.bar(x - w / 2, vals50, w, label="mAP@0.5", color="#4C72B0")
    ax.bar(x + w / 2, vals5095, w, label="mAP@0.5:0.95", color="#C44E52")
    ax.set_xticks(x, [VARIAN_LABEL[v] for v in variants], rotation=30, ha="right")
    ax.set_ylabel("mAP (%)"); ax.set_title("Metrik global per varian (data uji)")
    ax.legend(); fig.tight_layout()
    simpan(fig, d / "grafik_map_per_varian.png")

    strata = list(csv.DictReader(open(ROOT / "eval_out/strata_ap.csv")))
    for dim, tiers in (("size", ("small", "medium", "large")),
                      ("occlusion", ("no", "partial", "heavy")),
                      ("density", ("sparse", "medium", "dense"))):
        agg = defaultdict(list)
        for r in strata:
            if r["dim"] == dim and int(r["n_gt"] or 0) > 0:
                agg[(r["variant"], r["stratum"])].append(float(r["AP50_95"]))
        fig, ax = plt.subplots(figsize=(8, 4.5))
        x = np.arange(len(tiers)); w = 0.10
        for i, v in enumerate(["V1", "V4", "V5", "V8"]):
            ys = [np.mean(agg.get((v, t), [np.nan])) * 100 for t in tiers]
            ax.bar(x + (i - 1.5) * w, ys, w, label=VARIAN_LABEL[v], color=WARNA[v])
        ax.set_xticks(x, tiers); ax.set_ylabel("mAP50-95 rata-rata kelas (%)")
        ax.set_title(f"AP terstratifikasi — dimensi {dim} (V1, V4, V5, V8)")
        ax.legend(fontsize=8); fig.tight_layout()
        simpan(fig, d / f"grafik_strata_{dim}.png")

    wil = list(csv.DictReader(open(ROOT / "eval_out/wilcoxon_ap5095.csv")))
    boot = list(csv.DictReader(open(ROOT / "eval_out/bootstrap_ci.csv")))
    boot_by_pair = {r["pair"]: r for r in boot}
    primer = [r for r in wil if r["family"] == "primary"]
    fig, ax = plt.subplots(figsize=(8.5, 4))
    ypos = np.arange(len(primer))
    rbs = [float(r["rank_biserial"]) for r in primer]
    xmin, xmax = min(rbs + [0]), max(rbs + [0])
    pad = max(xmax - xmin, 0.1) * 0.28
    for i, r in enumerate(primer):
        rb = float(r["rank_biserial"])
        ax.barh(i, rb, color="#DD8452" if r["signif_5pct"] == "True" else "#888888", height=0.5)
        label = f"p={float(r['p']):.3f}" + (" *" if r["signif_5pct"] == "True" else "")
        # taruh label SELALU di sisi kanan ujung batang (searah, tak pernah menabrak tick label kiri)
        ax.text(rb + pad * 0.15 if rb >= 0 else pad * 0.05, i, label, va="center", ha="left", fontsize=9)
    ax.set_yticks(ypos, [r["pair"] for r in primer])
    ax.set_xlim(xmin - pad, xmax + pad * 2.2)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Korelasi rank-biserial r (Wilcoxon, AP per kelas x strata)")
    ax.set_title("Tiga hipotesis utama — ukuran efek Wilcoxon\n(* = signifikan taraf 5%)")
    fig.tight_layout()
    simpan(fig, d / "grafik_wilcoxon_hipotesis_utama.png")

    fig, ax = plt.subplots(figsize=(7.5, 4))
    for i, r in enumerate(boot):
        lo, hi, pt = float(r["ci_lo"]) * 100, float(r["ci_hi"]) * 100, float(r["diff_point"]) * 100
        no_zero = r["selang_tanpa_nol"] == "True"
        ax.plot([lo, hi], [i, i], color="#DD8452" if no_zero else "#888888", lw=3)
        ax.plot(pt, i, "o", color="black", ms=6)
        ax.text(hi + 0.1, i, f"[{lo:+.2f}, {hi:+.2f}]" + (" *" if no_zero else ""), va="center", fontsize=9)
    ax.axvline(0, color="black", lw=0.8, linestyle="--")
    ax.set_yticks(range(len(boot)), [r["pair"] for r in boot])
    ax.set_xlabel("Selisih mAP50-95 (poin persen)")
    ax.set_title("Selang kepercayaan bootstrap 95% (1.000 resample tataran citra)\n(* = selang tidak memuat nol)")
    fig.tight_layout()
    simpan(fig, d / "grafik_bootstrap_ci.png")


# ======================================================================
# 05 — ANALISIS NMS-FREE
# ======================================================================
def bab_05_nmsfree():
    d = OUT / "05_analisis_nmsfree"
    for f in ("summary.csv", "tau_sweep.csv"):
        shutil.copy(ROOT / f"nmsfree_out/{f}", d / f)
    for f in ("dr_vs_tau.png", "cm_hist.png"):
        src = ROOT / f"nmsfree_out/{f}"
        if src.exists():
            shutil.copy(src, d / f)

    summ = list(csv.DictReader(open(ROOT / "nmsfree_out/summary.csv")))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    vs = [r["variant"] for r in summ]
    axes[0].bar(vs, [float(r["DR"]) for r in summ], color=[WARNA[v] for v in vs])
    axes[0].axhline(1.0, color="black", ls="--", lw=0.8, label="ideal (DR=1)")
    axes[0].set_title("Duplicate Rate (tau=0.25)"); axes[0].set_ylabel("DR"); axes[0].legend()
    axes[1].bar(vs, [float(r["cm_mean"]) for r in summ], color=[WARNA[v] for v in vs])
    axes[1].set_title("Confidence Margin rata-rata"); axes[1].set_ylabel("CM")
    fig.suptitle("Analisis interaksi NMS-free — varian ber-P2 vs baseline")
    fig.tight_layout()
    simpan(fig, d / "grafik_dr_cm_ringkasan.png")

    tau_rows = list(csv.DictReader(open(ROOT / "nmsfree_out/tau_sweep.csv")))
    taus = [float(r["tau"]) for r in tau_rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for v in ("V1", "V3", "V5", "V7", "V8"):
        ax.plot(taus, [float(r[v]) for r in tau_rows], marker="o", ms=3, label=VARIAN_LABEL[v], color=WARNA[v])
    ax.axhline(1.0, color="black", ls="--", lw=0.7)
    ax.set_xlabel("ambang tau"); ax.set_ylabel("Duplicate Rate")
    ax.set_title("Sensitivitas Duplicate Rate terhadap ambang tau"); ax.legend(fontsize=8)
    fig.tight_layout()
    simpan(fig, d / "grafik_tau_sweep_ulang.png")

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for v in ("V1", "V3", "V5", "V7", "V8"):
        p = ROOT / f"runs_tesis/{v}/nmsfree_probe.csv"
        if not p.exists():
            continue
        rows = list(csv.DictReader(open(p)))
        ep = [int(r["epoch"]) for r in rows]
        st = [float(r["stability"]) if r["stability"] not in ("", "nan") else np.nan for r in rows]
        ax.plot(ep, st, label=VARIAN_LABEL[v], color=WARNA[v], alpha=0.85, lw=1.3)
    ax.set_xlabel("epoch"); ax.set_ylabel("S(t) stabilitas assignment")
    ax.set_title("Stabilitas assignment antar-epoch S(t) (Pers. 3.8)\nprobe tetap, data validasi")
    ax.legend(fontsize=8); ax.set_ylim(0, 1.05)
    fig.tight_layout()
    simpan(fig, d / "grafik_stabilitas_assignment.png")


# ======================================================================
# 06 — SENSITIVITAS ALPHA (V4)
# ======================================================================
def bab_06_sensitivitas_alpha():
    d = OUT / "06_sensitivitas_alpha"
    rows = []
    for name, a in (("V4_a0.5", 0.5), ("V4", 1.0), ("V4_a2.0", 2.0)):
        f = ROOT / f"runs_tesis/{name}/results.csv"
        r = list(csv.DictReader(open(f)))
        k = next(x for x in r[0] if "mAP50-95" in x)
        best = max(float(x[k]) for x in r)
        best_ep = max(range(len(r)), key=lambda i: float(r[i][k])) + 1
        cj = ROOT / f"runs_tesis/{name}/complexity_train.json"
        hours = json.loads(cj.read_text())["train_hours"] if cj.exists() else float("nan")
        rows.append(dict(run=name, alpha=a, epoch_total=len(r), epoch_terbaik=best_ep,
                         mAP50_95_val_terbaik=round(best, 5), jam_latih=round(hours, 2)))
    with open(d / "tabel_sensitivitas_alpha.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    alphas = [r["alpha"] for r in rows]
    vals = [r["mAP50_95_val_terbaik"] * 100 for r in rows]
    ax.plot(alphas, vals, "o-", color="#C44E52", ms=9, lw=2)
    for a, v, r in zip(alphas, vals, rows):
        ax.annotate(f"{v:.2f}%\n(ep {r['epoch_terbaik']})", (a, v), textcoords="offset points",
                   xytext=(0, 10), ha="center", fontsize=9)
    ax.axvline(1.0, color="gray", ls=":", lw=1, label="alpha terpilih grid search")
    ax.set_xlabel("alpha (V4, sigma=0.1 tetap)"); ax.set_ylabel("mAP50-95 val terbaik (%)")
    ax.set_title("Sensitivitas alpha pada varian V4 (DALW saja)")
    ax.legend(); fig.tight_layout()
    simpan(fig, d / "grafik_sensitivitas_alpha.png")


# ======================================================================
# 07 — PEMERIKSAAN KETEGARAN NORMALISASI-PER-BOBOT
# ======================================================================
def bab_07_ketegaran():
    d = OUT / "07_ketegaran_normalisasi"
    f8 = ROOT / "runs_tesis/V8/results.csv"
    fn = ROOT / "runs_tesis/V8_normw/results.csv"
    log = ROOT / "logs/fase2_ketegaran.log"
    log_txt = log.read_text(errors="ignore") if log.exists() else ""
    rows = []
    for name, f, cek_log in (("V8 (default, bagi N objek)", f8, False),
                             ("V8_normw (bagi Sigma w_i)", fn, True)):
        if not f.exists():
            continue
        r = list(csv.DictReader(open(f)))
        k = next(x for x in r[0] if "mAP50-95" in x)
        best = max(float(x[k]) for x in r)
        best_ep = max(range(len(r)), key=lambda i: float(r[i][k])) + 1
        if cek_log:
            if "TUNTAS" in log_txt:
                status = "selesai (early-stop)"
            elif "GAGAL" in log_txt:
                status = "GAGAL/error"
            else:
                status = f"MASIH BERJALAN (epoch {len(r)} tercatat, belum berhenti)"
        else:
            status = "selesai (early-stop)" if len(r) < 300 else "selesai (300 epoch)"
        rows.append(dict(run=name, epoch_tercatat=len(r), epoch_terbaik=best_ep,
                         mAP50_95_val_terbaik=round(best, 5), status=status))
    if rows:
        with open(d / "tabel_perbandingan_normalisasi.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


# ======================================================================
# 08 — VALIDASI OKLUSI (P8)
# ======================================================================
def bab_08_oklusi():
    d = OUT / "08_validasi_oklusi"
    shutil.copy(ROOT / "anotasi_oklusi/manual_oklusi.csv", d / "manual_oklusi.csv")

    import sys
    sys.path.insert(0, str(ROOT))
    from y26_strata import occlusion_agreement, OCC_NAMES
    r = occlusion_agreement("anotasi_oklusi/manual_oklusi.csv", "dataset/data.yaml", split="val")
    with open(d / "hasil_kesesuaian.json", "w") as fh:
        json.dump(dict(agreement=r["agreement"], n=r["n"], confusion=r["confusion"]), fh, indent=2)

    C = r["confusion"]
    M = np.array([[C[a][b] for b in OCC_NAMES] for a in OCC_NAMES])
    fig, ax = plt.subplots(figsize=(5.5, 4.8))
    im = ax.imshow(M, cmap="Blues")
    ax.set_xticks(range(3), OCC_NAMES); ax.set_yticks(range(3), OCC_NAMES)
    ax.set_xlabel("tier menurut proksi (otomatis)"); ax.set_ylabel("tier menurut anotasi manual")
    ax.set_title(f"Matriks konfusi proksi vs manual (n={r['n']})\nkesesuaian = {r['agreement']*100:.1f}%")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(int(M[i, j])), ha="center", va="center",
                    color="white" if M[i, j] > M.max() / 2 else "black", fontsize=13)
    fig.colorbar(im, ax=ax, label="jumlah objek")
    fig.tight_layout()
    simpan(fig, d / "matriks_konfusi_oklusi.png")

    import csv as csv_mod
    mf = {(row["image"], int(row["gt_index"])): row
         for row in csv_mod.DictReader(open(ROOT / "anotasi_oklusi/sample_manifest.csv", encoding="utf-8"))}
    man = list(csv_mod.DictReader(open(ROOT / "anotasi_oklusi/manual_oklusi.csv", encoding="utf-8")))
    per_kelas = defaultdict(lambda: [0, 0])
    for row in man:
        k = (row["image"], int(row["gt_index"]))
        m = mf.get(k)
        if not m:
            continue
        per_kelas[m["kelas"]][0] += 1
        per_kelas[m["kelas"]][1] += (m["proxy_tier"] == row["tier"])
    fig, ax = plt.subplots(figsize=(6, 4.2))
    kelas = sorted(per_kelas, key=lambda k: -per_kelas[k][1] / per_kelas[k][0])
    pct = [per_kelas[k][1] / per_kelas[k][0] * 100 for k in kelas]
    ax.bar(kelas, pct, color="#4C72B0")
    ax.axhline(r["agreement"] * 100, color="red", ls="--", label=f"rata-rata {r['agreement']*100:.1f}%")
    for i, v in enumerate(pct):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_ylabel("kesesuaian (%)"); ax.set_title("Kesesuaian proksi vs manual per kelas")
    ax.legend(); fig.tight_layout()
    simpan(fig, d / "kesesuaian_per_kelas.png")
    return r


# ======================================================================
# 09 — COUNTING END-TO-END (RQ5)
# ======================================================================
KLIP_COUNTING = ("2_vidiouji", "3_vidiouji", "4_vidiouji")
# 1_vidiouji DIKECUALIKAN (keputusan Naufal 5 Agu 2026): segmen garis virtualnya tidak
# menjangkau lajur yang dipakai mobil, sehingga hitung manual (lebar jalan penuh) dan
# keluaran sistem mengukur populasi kendaraan yang berbeda -> cacat validitas pengukuran,
# BUKAN performa buruk. Berkas mentahnya tetap disimpan sebagai bukti; alasan pengecualian
# wajib dinyatakan eksplisit di BAB 4/5.


def bab_09_counting(klip=KLIP_COUNTING):
    """Rangkum hasil counting yang TERSEDIA; klip tanpa hasil dilewati (jujur)."""
    d = OUT / "09_counting_end_to_end"
    KELAS = ("big-vehicle", "car", "two-wheeler")
    ringkas, banding = [], []
    for stem in klip:
        sj = ROOT / f"counting_out/{stem}/summary.json"
        gtf = ROOT / f"video_uji/gt_{stem}.csv"
        if not sj.exists():
            print(f"  [lewati] {stem}: belum ada hasil counting")
            continue
        s = json.loads(sj.read_text())
        m = s.get("metrics", {})
        sys_tot = {}
        for k, v in s.get("totals", {}).items():
            kls, arah = k.rsplit("_", 1)
            sys_tot[(kls, arah)] = v
        gt_tot = {}
        if gtf.exists():
            for r in csv.DictReader(open(gtf, encoding="utf-8")):
                key = (r["class"], r["direction"])
                gt_tot[key] = gt_tot.get(key, 0) + int(r["count"])
        ringkas.append(dict(
            klip=stem, garis=",".join(map(str, s["line"])), frame=s["frames"],
            MAE=round(m.get("MAE", float("nan")), 4), RMSE=round(m.get("RMSE", float("nan")), 4),
            MAPE_persen=round(m.get("MAPE", float("nan")), 2),
            n_pengamatan=m.get("T", 0), n_dikecualikan_y0=m.get("mape_excluded", 0),
            total_sistem=sum(sys_tot.values()), total_manual=sum(gt_tot.values()),
            selisih_agregat_persen=round((sum(sys_tot.values()) - sum(gt_tot.values()))
                                         / max(sum(gt_tot.values()), 1) * 100, 1),
            fps_pipeline=round(s["fps_pipeline"], 2), fps_model=round(s["fps_model"], 2)))
        for kls in KELAS:
            for arah in ("in", "out"):
                banding.append(dict(klip=stem, kelas=kls, arah=arah,
                                    sistem=sys_tot.get((kls, arah), 0),
                                    manual=gt_tot.get((kls, arah), 0)))
    if not ringkas:
        print("  [09] belum ada hasil counting sama sekali")
        return []

    with open(d / "ringkasan_counting_per_klip.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ringkas[0])); w.writeheader(); w.writerows(ringkas)
    with open(d / "perbandingan_sistem_vs_manual.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(banding[0])); w.writeheader(); w.writerows(banding)

    # grafik 1: sistem vs manual per kelas/arah, per klip
    n = len(ringkas)
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 4.4), squeeze=False)
    for ax, r in zip(axes[0], ringkas):
        sub = [b for b in banding if b["klip"] == r["klip"]]
        lbl = [f"{b['kelas'].split('-')[0]}\n{b['arah']}" for b in sub]
        x = np.arange(len(sub)); w = 0.38
        ax.bar(x - w / 2, [b["manual"] for b in sub], w, label="manual (GT)", color="#4C72B0")
        ax.bar(x + w / 2, [b["sistem"] for b in sub], w, label="sistem", color="#DD8452")
        ax.set_xticks(x, lbl, fontsize=7)
        ax.set_title(f"{r['klip']}\nMAE={r['MAE']:.2f} MAPE={r['MAPE_persen']:.1f}%", fontsize=10)
        ax.set_ylabel("jumlah perlintasan (10 menit)")
        ax.legend(fontsize=8)
    fig.suptitle("Penghitungan end-to-end: sistem vs hitung manual "
                 "(arah diselaraskan; klip 1 dikecualikan)")
    fig.tight_layout()
    simpan(fig, d / "grafik_sistem_vs_manual.png")

    # grafik 2: galat per interval (sebar)
    fig, ax = plt.subplots(figsize=(6.2, 5.6))
    warna_klip = {"1_vidiouji": "#4C72B0", "2_vidiouji": "#55A868",
                  "3_vidiouji": "#C44E52", "4_vidiouji": "#8172B2"}
    maks = 1
    for r in ringkas:
        f = ROOT / f"counting_out/{r['klip']}/counting_errors.csv"
        if not f.exists():
            continue
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        ys = [int(x["y"]) for x in rows]; yh = [int(x["yhat"]) for x in rows]
        maks = max(maks, max(ys + yh + [1]))
        ax.scatter(ys, yh, s=32, alpha=.65, label=r["klip"], color=warna_klip.get(r["klip"], "#888"))
    ax.plot([0, maks], [0, maks], "k--", lw=1, label="ideal (sistem = manual)")
    ax.set_xlabel("hitung manual per interval (y)"); ax.set_ylabel("hitung sistem per interval (yhat)")
    ax.set_title("Sebar hitungan per interval x kelas x arah\ntitik di bawah garis = sistem kurang hitung")
    ax.legend(fontsize=8); fig.tight_layout()
    simpan(fig, d / "grafik_sebar_per_interval.png")

    for r in ringkas:
        for f in ("counts_per_interval.csv", "counting_errors.csv", "summary.json"):
            src = ROOT / f"counting_out/{r['klip']}/{f}"
            if src.exists():
                shutil.copy(src, d / f"{r['klip']}_{f}")

    # ---- metrik GABUNGAN: dihitung dari kumpulan pengamatan, bukan rata-rata dari rata-rata
    y, yh = [], []
    for r in ringkas:
        f = ROOT / f"counting_out/{r['klip']}/counting_errors.csv"
        if not f.exists():
            continue
        for row in csv.DictReader(open(f, encoding="utf-8")):
            y.append(int(row["y"])); yh.append(int(row["yhat"]))
    if y:
        y = np.array(y, float); yh = np.array(yh, float)
        err = y - yh
        pos = y > 0
        gab = dict(
            n_klip=len(ringkas), n_pengamatan=len(y),
            MAE=round(float(np.mean(np.abs(err))), 4),
            RMSE=round(float(np.sqrt(np.mean(err ** 2))), 4),
            MAPE_persen=round(float(100 * np.mean(np.abs(err[pos]) / y[pos])), 2),
            n_dikecualikan_y0=int((~pos).sum()),
            frac_dikecualikan=round(float((~pos).mean()), 4),
            total_manual=int(y.sum()), total_sistem=int(yh.sum()),
            selisih_agregat_persen=round(float((yh.sum() - y.sum()) / max(y.sum(), 1) * 100), 1),
            fps_pipeline_rata2=round(float(np.mean([r["fps_pipeline"] for r in ringkas])), 2),
            fps_pipeline_min=min(r["fps_pipeline"] for r in ringkas),
            fps_pipeline_maks=max(r["fps_pipeline"] for r in ringkas),
            klip_dipakai="; ".join(r["klip"] for r in ringkas),
            klip_dikecualikan="1_vidiouji (segmen garis tak menjangkau lajur mobil)")
        with open(d / "metrik_GABUNGAN.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(gab)); w.writeheader(); w.writerow(gab)
        print(f"  GABUNGAN {gab['n_klip']} klip, {gab['n_pengamatan']} pengamatan: "
              f"MAE={gab['MAE']} RMSE={gab['RMSE']} MAPE={gab['MAPE_persen']}% "
              f"(y=0 dikecualikan {gab['n_dikecualikan_y0']}), "
              f"agregat {gab['selisih_agregat_persen']:+}%, FPS {gab['fps_pipeline_rata2']}")
        ringkas.append({"klip": "GABUNGAN", **{k: v for k, v in gab.items() if k in
                        ("MAE", "RMSE", "MAPE_persen", "n_pengamatan", "n_dikecualikan_y0",
                         "total_sistem", "total_manual", "selisih_agregat_persen")}})
    return ringkas


if __name__ == "__main__":
    print("01 dataset..."); bab_01_dataset()
    print("02 grid search..."); bab_02_grid()
    print("03 kompleksitas..."); bab_03_kompleksitas()
    print("04 ablasi deteksi..."); bab_04_ablasi()
    print("05 nmsfree..."); bab_05_nmsfree()
    print("06 sensitivitas alpha..."); bab_06_sensitivitas_alpha()
    print("07 ketegaran..."); rows7 = bab_07_ketegaran()
    print("  ", rows7)
    print("08 validasi oklusi..."); r8 = bab_08_oklusi()
    print("  agreement:", r8["agreement"])
    print("SELESAI")
