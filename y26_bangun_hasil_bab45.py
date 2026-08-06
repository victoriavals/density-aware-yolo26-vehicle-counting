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

    # Selisih AP per strata untuk narasi BAB 4. Dihitung DUA cara supaya perbedaannya
    # terlihat: (a) seluruh sel non-kosong, (b) hanya sel n_gt >= MIN_CELL_GT, konsisten
    # dengan aturan sel minimum Subbab 3.11.5 yang dipakai uji Wilcoxon. Angka narasi
    # WAJIB memakai kolom (b) — kolom (a) memuat sel bervolume 1-27 objek yang membalik
    # tanda pada beberapa strata (mis. density/dense).
    from y26_stats import MIN_CELL_GT
    per_cell = defaultdict(dict)
    for r in strata:
        if r["dim"] == "global":
            continue
        per_cell[(r["dim"], r["stratum"], r["class"])][r["variant"]] = (
            int(r["n_gt"] or 0), float(r["AP50_95"]))
    with open(d / "delta_strata.csv", "w", newline="", encoding="utf-8") as fh:
        w_ = csv.writer(fh)
        w_.writerow(["pasangan", "dim", "stratum", "n_kelas_semua", "delta_pp_semua_sel",
                     "n_kelas_selmin", "delta_pp_selmin", "kelas_dipakai", "kelas_dibuang",
                     "layak_dinarasikan"])
        for a, b in (("V8", "V1"), ("V4", "V1"), ("V8", "V5")):
            for dim, tiers in (("size", ("small", "medium", "large")),
                               ("occlusion", ("no", "partial", "heavy")),
                               ("density", ("sparse", "medium", "dense"))):
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
                    # Kendaraan = kelas yang benar-benar dihitung; pedestrian hanya konteks
                    # (dikecualikan dari penghitungan, CLAUDE.md §5). Strata yang hanya
                    # bersisa pedestrian TIDAK boleh dinarasikan sebagai hasil kendaraan.
                    kendaraan = [c for c in dipakai if c != "pedestrian"]
                    if not selmin:
                        layak = "TIDAK - semua sel < 30 GT"
                    elif not kendaraan:
                        layak = "TIDAK - hanya pedestrian (kelas konteks) yang lolos"
                    elif len(dipakai) == 1:
                        layak = f"HATI-HATI - hanya 1 kelas ({dipakai[0]})"
                    else:
                        layak = "ya"
                    w_.writerow([
                        f"{a}-{b}", dim, t, len(semua), f"{100 * np.mean(semua):+.2f}",
                        len(selmin),
                        f"{100 * np.mean(selmin):+.2f}" if selmin else "",
                        "; ".join(sorted(dipakai)), "; ".join(dibuang), layak])

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


# ======================================================================
# 11 — ANALISIS GALAT (Subbab 4.11)
# ======================================================================
# Matriks kekeliruan pada SPLIT UJI (bukan val bawaan training), dekomposisi FP/FN per
# strata, dan kasus kegagalan terburuk. Seluruhnya dihitung dari cache_V*.npz — objek
# yang sama yang dipakai stratified_ap, sehingga angkanya konsisten dengan Subbab 4.5.
GALAT_IOU = 0.50      # ambang pencocokan (konvensi COCO untuk matriks kekeliruan)
GALAT_CONF = 0.25     # ambang keyakinan; sama dengan default y26_counting.py --conf


def _cocokkan(pred, gt, n_cls, iou_thr=GALAT_IOU, conf_thr=GALAT_CONF):
    """Cocokkan prediksi<->GT per citra (serakah, skor menurun, tanpa syarat kelas).

    Mengembalikan (cm, gt_match, pred_keep, pred_match) dengan cm berukuran
    (n_cls+1, n_cls+1); indeks n_cls = latar (FN pada baris, FP pada kolom).
    """
    from ultralytics.utils.metrics import box_iou
    import torch

    cm = np.zeros((n_cls + 1, n_cls + 1), np.int64)
    pred = pred[pred[:, 5] >= conf_thr]
    gt_match = np.full(len(gt), -1, np.int64)      # indeks prediksi pasangan, -1 = FN
    pred_match = np.full(len(pred), -1, np.int64)  # indeks GT pasangan, -1 = FP
    for img in np.unique(np.concatenate([gt[:, 0], pred[:, 0]]) if len(pred) else gt[:, 0]):
        gi = np.flatnonzero(gt[:, 0] == img)
        pi = np.flatnonzero(pred[:, 0] == img)
        if len(gi) and len(pi):
            iou = box_iou(torch.as_tensor(gt[gi, 1:5]), torch.as_tensor(pred[pi, 1:5])).numpy()
            for j in np.argsort(-pred[pi, 5]):          # prediksi paling yakin lebih dulu
                k = int(np.argmax(iou[:, j]))
                if iou[k, j] >= iou_thr:
                    gt_match[gi[k]] = pi[j]
                    pred_match[pi[j]] = gi[k]
                    iou[k, :] = -1                      # GT terpakai
        for k in gi:
            c_gt = int(gt[k, 5])
            cm[c_gt, int(pred[gt_match[k], 6]) if gt_match[k] >= 0 else n_cls] += 1
        for j in pi:
            if pred_match[j] < 0:
                cm[n_cls, int(pred[j, 6])] += 1
    return cm, gt_match, pred, pred_match


def bab_11_analisis_galat(variants=("V1", "V5", "V8")):
    import y26_strata as ys

    d = OUT / "11_analisis_galat"; d.mkdir(parents=True, exist_ok=True)
    import yaml
    kelas = list(yaml.safe_load(open(ROOT / "dataset/data.yaml"))["names"])
    n_cls = len(kelas)
    label = kelas + ["latar (tak terdeteksi / palsu)"]
    hasil, ringkas = {}, []

    for v in variants:
        z = np.load(ROOT / f"eval_out/cache_{v}.npz", allow_pickle=True)
        pred, gt, n_img = z["pred"], z["gt"], int(z["n_images"])
        cm, gt_match, pk, pred_match = _cocokkan(pred, gt, n_cls)
        hasil[v] = (cm, gt, gt_match, pk, pred_match, n_img)

        with open(d / f"matriks_kekeliruan_{v}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["gt\\pred"] + label)
            for i, nm in enumerate(label):
                w.writerow([nm] + list(cm[i]))

        fig, ax = plt.subplots(figsize=(6.4, 5.4))
        norm = cm / np.maximum(cm.sum(1, keepdims=True), 1)   # dinormalisasi per baris GT
        im = ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
        for i in range(n_cls + 1):
            for j in range(n_cls + 1):
                if cm[i, j]:
                    ax.text(j, i, f"{cm[i, j]}\n{100*norm[i, j]:.0f}%", ha="center",
                            va="center", fontsize=7.5,
                            color="white" if norm[i, j] > 0.55 else "black")
        ax.set_xticks(range(n_cls + 1), label, rotation=35, ha="right", fontsize=8)
        ax.set_yticks(range(n_cls + 1), label, fontsize=8)
        ax.set_xlabel("prediksi"); ax.set_ylabel("kebenaran dasar")
        ax.set_title(f"Matriks kekeliruan {VARIAN_LABEL.get(v, v)} — data uji\n"
                     f"(IoU {GALAT_IOU}, conf {GALAT_CONF}; % dinormalisasi per baris)",
                     fontsize=10)
        fig.colorbar(im, ax=ax, shrink=0.8); fig.tight_layout()
        simpan(fig, d / f"grafik_matriks_kekeliruan_{v}.png")

    # --- dekomposisi FN per strata GT, dan FP menurut atribut kotak prediksi ---
    z0 = np.load(ROOT / f"eval_out/cache_{variants[0]}.npz", allow_pickle=True)
    atr = ys.gt_attributes(z0["gt"], int(z0["n_images"]))
    TIER = {"size": ("small", "medium", "large"), "occlusion": ("no", "partial", "heavy"),
            "density": ("sparse", "medium", "dense")}
    with open(d / "dekomposisi_fp_fn.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["varian", "dim", "stratum", "n_gt", "n_fn", "fn_persen",
                    "n_salah_kelas", "n_fp_prediksi", "catatan"])
        for v in variants:
            cm, gt, gt_match, pk, pred_match, n_img = hasil[v]
            img_ids = gt[:, 0].astype(int)
            for dim, tiers in TIER.items():
                t_gt = (atr["size_t"] if dim == "size" else atr["occ_t"] if dim == "occlusion"
                        else atr["den_t"][img_ids])
                # atribut prediksi: ukuran dari kotaknya sendiri; densitas dari citranya.
                # Oklusi TIDAK dapat diturunkan untuk FP (proksi butuh pasangan GT).
                if dim == "size":
                    a = (pk[:, 3] - pk[:, 1]) * (pk[:, 4] - pk[:, 2])
                    t_pred = ys._tier(a, ys.SIZE_EDGES)
                elif dim == "density":
                    t_pred = atr["den_t"][pk[:, 0].astype(int)]
                else:
                    t_pred = None
                for ti, nama in enumerate(tiers):
                    m = t_gt == ti
                    n_gt = int(m.sum())
                    if not n_gt:
                        continue
                    fn = int((gt_match[m] < 0).sum())
                    cocok = m & (gt_match >= 0)
                    salah = int((gt[cocok, 5] != pk[gt_match[cocok], 6]).sum())
                    if t_pred is None:
                        n_fp, catatan = "", "FP tak dapat distratifikasi (proksi oklusi butuh pasangan GT)"
                    else:
                        n_fp = int(((pred_match < 0) & (t_pred == ti)).sum()); catatan = ""
                    w.writerow([v, dim, nama, n_gt, fn, round(100 * fn / n_gt, 2),
                                salah, n_fp, catatan])

    # --- grafik: laju FN per strata, V1 vs V8 ---
    baris = list(csv.DictReader(open(d / "dekomposisi_fp_fn.csv", encoding="utf-8")))
    for dim, tiers in TIER.items():
        ada = [t for t in tiers if any(r["dim"] == dim and r["stratum"] == t for r in baris)]
        if not ada:
            continue
        fig, ax = plt.subplots(figsize=(7.2, 4))
        x = np.arange(len(ada)); w_ = 0.8 / len(variants)
        for i, v in enumerate(variants):
            ys_ = [next((float(r["fn_persen"]) for r in baris
                         if r["varian"] == v and r["dim"] == dim and r["stratum"] == t), 0)
                   for t in ada]
            ax.bar(x + (i - (len(variants) - 1) / 2) * w_, ys_, w_,
                   label=VARIAN_LABEL.get(v, v), color=WARNA.get(v))
        ax.set_xticks(x, ada); ax.set_ylabel("objek tak terdeteksi (%)")
        ax.set_title(f"Laju objek terlewat per strata — dimensi {dim} (data uji)")
        ax.legend(fontsize=8); fig.tight_layout()
        simpan(fig, d / f"grafik_fn_per_strata_{dim}.png")

    # --- kasus kegagalan terburuk (citra dengan FN terbanyak pada model penuh) ---
    v = variants[-1]
    cm, gt, gt_match, pk, pred_match, n_img = hasil[v]
    nama_citra = list(np.load(ROOT / f"eval_out/cache_{v}.npz", allow_pickle=True)["names"])
    fn_per_img = np.zeros(n_img, int)
    for k in np.flatnonzero(gt_match < 0):
        fn_per_img[int(gt[k, 0])] += 1
    urut = np.argsort(-fn_per_img)[:10]
    with open(d / "kasus_kegagalan.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["peringkat", "citra", "n_gt", "n_terlewat", "n_prediksi_palsu", "kepadatan"])
        for r, i in enumerate(urut, 1):
            w.writerow([r, nama_citra[i], int((gt[:, 0] == i).sum()), int(fn_per_img[i]),
                        int(((pred_match < 0) & (pk[:, 0] == i)).sum()),
                        TIER["density"][int(atr["den_t"][i])]])
        ringkas = [nama_citra[i] for i in urut[:3]]

    # --- montase kualitatif 3 kasus terburuk: hijau = GT, merah = prediksi ---
    import cv2
    img_dir = ROOT / "dataset/test/images"
    ada = [i for i in urut[:3] if (img_dir / nama_citra[i]).exists()]
    if ada:
        fig, axes = plt.subplots(1, len(ada), figsize=(5.0 * len(ada), 4.4))
        for ax, i in zip(np.atleast_1d(axes), ada):
            im = cv2.cvtColor(cv2.imread(str(img_dir / nama_citra[i])), cv2.COLOR_BGR2RGB)
            h, w0 = im.shape[:2]
            # cache berada di ruang letterbox 640 -> kembalikan ke piksel citra asli
            s = min(640 / h, 640 / w0); px, py = (640 - w0 * s) / 2, (640 - h * s) / 2
            for b in gt[gt[:, 0] == i]:
                x1, y1, x2, y2 = (b[1] - px) / s, (b[2] - py) / s, (b[3] - px) / s, (b[4] - py) / s
                ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                           ec="#2ca02c", lw=1.4))
            for b in pk[pk[:, 0] == i]:
                x1, y1, x2, y2 = (b[1] - px) / s, (b[2] - py) / s, (b[3] - px) / s, (b[4] - py) / s
                ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                           ec="#d62728", lw=1.0, ls="--"))
            ax.imshow(im); ax.set_axis_off()
            ax.set_title(f"{int((gt[:, 0] == i).sum())} objek, {fn_per_img[i]} terlewat",
                         fontsize=9)
        fig.suptitle(f"Kasus kegagalan terburuk {VARIAN_LABEL.get(v, v)} — "
                     f"hijau: kebenaran dasar, merah putus-putus: prediksi", fontsize=10)
        fig.tight_layout()
        simpan(fig, d / "grafik_kasus_kegagalan.png")

    # --- dekomposisi siang/malam + per kelas: dua sumbu galat yang paling menjelaskan ---
    # Penanda malam diambil dari nama berkas Roboflow ("night-traffic-*"), bukan analisis
    # citra — sederhana, deterministik, dan dapat diperiksa ulang dari daftar nama.
    malam = np.array(["night" in s.lower() for s in nama_citra])
    with open(d / "galat_siang_malam.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["varian", "kelompok", "n_citra", "n_gt", "n_terlewat", "fn_persen"])
        for vv in variants:
            _, g2, gm2, _, _, _ = hasil[vv]
            ids = g2[:, 0].astype(int)
            for nama_k, msk, n_im in (("malam", malam[ids], int(malam.sum())),
                                      ("siang", ~malam[ids], int((~malam).sum()))):
                tot = int(msk.sum()); fn = int((gm2[msk] < 0).sum())
                w.writerow([vv, nama_k, n_im, tot, fn, round(100 * fn / max(tot, 1), 2)])
    with open(d / "galat_per_kelas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["varian", "kelas", "n_gt", "n_terlewat", "fn_persen", "n_salah_kelas"])
        for vv in variants:
            _, g2, gm2, pk2, _, _ = hasil[vv]
            for c, k in enumerate(kelas):
                m = g2[:, 5] == c
                fn = int((gm2[m] < 0).sum())
                ck = m & (gm2 >= 0)
                w.writerow([vv, k, int(m.sum()), fn, round(100 * fn / max(int(m.sum()), 1), 2),
                            int((g2[ck, 5] != pk2[gm2[ck], 6]).sum())])

    fig, ax = plt.subplots(figsize=(7.6, 4))
    x = np.arange(len(kelas)); w_ = 0.8 / len(variants)
    for i, vv in enumerate(variants):
        _, g2, gm2, _, _, _ = hasil[vv]
        ys_ = [100 * float((gm2[g2[:, 5] == c] < 0).sum()) / max(int((g2[:, 5] == c).sum()), 1)
               for c in range(len(kelas))]
        ax.bar(x + (i - (len(variants) - 1) / 2) * w_, ys_, w_,
               label=VARIAN_LABEL.get(vv, vv), color=WARNA.get(vv))
    ax.set_xticks(x, kelas); ax.set_ylabel("objek tak terdeteksi (%)")
    ax.set_title("Laju objek terlewat per kelas — data uji")
    ax.legend(fontsize=8); fig.tight_layout()
    simpan(fig, d / "grafik_fn_per_kelas.png")

    total_fn = {v: int((hasil[v][2] < 0).sum()) for v in variants}
    print(f"  FN total (dari {len(gt)} objek uji): " +
          ", ".join(f"{v}={n} ({100*n/len(gt):.1f}%)" for v, n in total_fn.items()))
    return {"fn_total": total_fn, "kasus_terburuk": ringkas}


# ======================================================================
# KONSOLIDASI — kumpulkan SELURUH data & visualisasi ke satu tempat
# ======================================================================
# Tujuan: hasil_bab4_5/ menjadi satu-satunya folder yang perlu dibuka/diserahkan.
# Artefak yang tersebar (counting_out, nmsfree_out, runs_tesis, hasil/, video_uji)
# disalin ke sini. Sumber aslinya TIDAK dihapus - folder ini turunan, bukan pengganti.
def _salin(src: Path, dst: Path) -> int:
    if not src.exists():
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return 1


def konsolidasi_arsip():
    n = 0

    # -- 00 data sumber yang tidak dapat dibangkitkan ulang oleh kode --------
    d = OUT / "00_data_sumber"; d.mkdir(parents=True, exist_ok=True)
    for f in sorted((ROOT / "video_uji").glob("gt_*.csv")):
        n += _salin(f, d / "hitung_manual" / f.name)
    n += _salin(ROOT / "video_uji/konfigurasi_garis.json", d / "konfigurasi_garis.json")
    n += _salin(ROOT / "video_uji/README.md", d / "PANDUAN_VIDEO_UJI.md")
    for f in sorted((ROOT / "video_uji/penghitung_kedua").glob("*")):
        if f.is_file():
            n += _salin(f, d / "kit_penghitung_kedua" / f.name)
    n += _salin(ROOT / "anotasi_oklusi/manual_oklusi.csv", d / "anotasi_oklusi_manual.csv")
    n += _salin(ROOT / "bukti_split_grup.csv", d / "bukti_split_grup.csv")
    n += _salin(ROOT / "bukti_split_citra.csv", d / "bukti_split_citra.csv")
    n += _salin(ROOT / "dalw_best.json", d / "dalw_best.json")

    # -- 05 lengkapi keluaran mentah analisis NMS-free -----------------------
    for f in sorted((ROOT / "nmsfree_out").glob("*")):
        if f.is_file() and not (OUT / "05_analisis_nmsfree" / f.name).exists():
            n += _salin(f, OUT / "05_analisis_nmsfree" / f.name)

    # -- 09 lengkapi counting: pengukuran FPS + klip 1 (bukti pengecualian) --
    d9 = OUT / "09_counting_end_to_end"
    for v in ("V1", "V4_a2.0", "V8"):
        n += _salin(ROOT / f"counting_out/fps_probe/{v}/summary.json",
                    d9 / "pengukuran_fps" / f"{v}_summary.json")
    for f in ("counting_errors.csv", "counts_per_interval.csv", "summary.json"):
        n += _salin(ROOT / f"counting_out/1_vidiouji/{f}",
                    d9 / "klip1_DIKECUALIKAN_bukti" / f)

    # -- 12 kurva pelatihan per varian --------------------------------------
    d12 = OUT / "12_kurva_pelatihan"
    for run in sorted((ROOT / "runs_tesis").glob("V*")):
        if not run.is_dir():
            continue
        n += _salin(run / "results.csv", d12 / f"{run.name}_results.csv")
        n += _salin(run / "results.png", d12 / f"{run.name}_kurva.png")
        n += _salin(run / "nmsfree_probe.csv", d12 / f"{run.name}_nmsfree_probe.csv")
        n += _salin(run / "complexity_train.json", d12 / f"{run.name}_complexity.json")

    # -- 13 ringkasan naratif per tahap -------------------------------------
    for f in sorted((ROOT / "hasil").glob("*.md")):
        n += _salin(f, OUT / "13_ringkasan_naratif" / f.name)

    # -- 14 naskah hasil ----------------------------------------------------
    n += _salin(ROOT / "TESIS_BAB4-5.docx", OUT / "14_naskah/TESIS_BAB4-5.docx")

    print(f"  {n} berkas dikonsolidasikan ke {OUT}/")
    return n


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
    print("11 analisis galat..."); r11 = bab_11_analisis_galat()
    print("  ", r11["fn_total"])
    print("konsolidasi arsip..."); konsolidasi_arsip()
    print("SELESAI")
