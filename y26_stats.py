"""
y26_stats.py — Uji Wilcoxon signed-rank + koreksi Holm (Subbab 3.11.4).

Rancangan tesis: tiga hipotesis UTAMA pada taraf 5% — V8 vs V1, V4 vs V1,
V8 vs V5 — sedangkan perbandingan lain berstatus SEKUNDER dengan koreksi Holm.
Unit pasangan deteksi: AP per (kelas × strata evaluasi) pada potongan data uji
yang identik; unit penghitungan: galat per interval pengamatan; unit NMS-free:
DR/CM per citra (keluaran Tahap 2).
"""

from __future__ import annotations

import numpy as np

PRIMARY_PAIRS = (("V8", "V1"), ("V4", "V1"), ("V8", "V5"))

# Naskah Subbab 3.11.5: sel dengan jumlah objek GT kurang dari tiga puluh TIDAK
# diikutkan uji signifikansi dan dilaporkan terpisah sebagai temuan deskriptif
# dengan penanda keterbatasan sampel.
MIN_CELL_GT = 30


def rank_biserial(d: np.ndarray) -> tuple[float, float, float]:
    """Korelasi rank-biserial (Persamaan 3.15): r = (W+ - W-) / (W+ + W-).

    Ukuran efek untuk Wilcoxon signed-rank; rentang -1..+1, positif berarti
    x konsisten lebih unggul dari y. Selisih nol dibuang (metode 'wilcox'),
    peringkat memakai rata-rata untuk nilai kembar (ties).
    """
    from scipy.stats import rankdata

    d = d[d != 0]
    if len(d) == 0:
        return float("nan"), 0.0, 0.0
    r = rankdata(np.abs(d))
    wp, wm = float(r[d > 0].sum()), float(r[d < 0].sum())
    return (wp - wm) / (wp + wm), wp, wm


def wilcoxon_pair(x, y, alternative: str = "two-sided") -> dict:
    """Wilcoxon berpasangan x vs y + ukuran efek (drop pasangan NaN; selisih nol dibuang)."""
    from scipy.stats import wilcoxon

    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    d = x - y
    n_eff = int((d != 0).sum())
    r_rb, wp, wm = rank_biserial(d)
    out = dict(n=int(m.sum()), n_eff=n_eff,
               median_diff=float(np.median(d)) if len(d) else float("nan"),
               mean_diff=float(np.mean(d)) if len(d) else float("nan"),
               rank_biserial=r_rb, W_plus=wp, W_minus=wm)
    if n_eff < 1:
        out.update(W=0.0, p=1.0)
        return out
    res = wilcoxon(x, y, zero_method="wilcox", alternative=alternative, method="auto")
    out.update(W=float(res.statistic), p=float(res.pvalue))
    return out


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Koreksi Holm step-down; mengembalikan p terkoreksi (monoton, terpotong di 1)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, (m - i) * p)
        adj[k] = min(run, 1.0)
    return adj


def paired_vectors(rows_a: list[dict], rows_b: list[dict], metric: str = "ap5095",
                   include_global: bool = False, min_n_gt: int = MIN_CELL_GT):
    """Sejajarkan sel (kelas × dim × strata) dua varian -> (keys, x, y, dibuang).

    Default mengecualikan baris 'global' agar unit pasangan murni strata
    (sesuai frasa 'per kombinasi kelas dan strata evaluasi'), dan membuang sel
    ber-n_gt < min_n_gt sesuai aturan ukuran sel minimum Subbab 3.11.5. Sel yang
    dibuang dikembalikan terpisah (bukan dihilangkan diam-diam) agar dapat
    dilaporkan sebagai temuan deskriptif bertanda keterbatasan sampel.
    """
    def key(r):
        return (r["cls"], r["dim"], r["stratum"])

    da = {key(r): r for r in rows_a if include_global or r["dim"] != "global"}
    db = {key(r): r for r in rows_b if include_global or r["dim"] != "global"}
    keys, dibuang = [], []
    for k in sorted(set(da) & set(db)):
        n_gt = min(int(da[k].get("n_gt", 0) or 0), int(db[k].get("n_gt", 0) or 0))
        (keys if n_gt >= min_n_gt else dibuang).append((k, n_gt))
    x = np.array([da[k][metric] for k, _ in keys], float)
    y = np.array([db[k][metric] for k, _ in keys], float)
    return [k for k, _ in keys], x, y, dibuang


def run_wilcoxon_suite(rows_by_variant: dict[str, list[dict]], metric: str = "ap5095",
                       primary=PRIMARY_PAIRS, min_n_gt: int = MIN_CELL_GT) -> list[dict]:
    """Tiga hipotesis utama (taraf 5% tanpa koreksi) + seluruh pasangan lain (Holm).

    Sel ber-n_gt < min_n_gt dikeluarkan dari pengujian (Subbab 3.11.5); jumlah dan
    daftarnya dibawa pada kunci n_sel_dibuang / sel_dibuang tiap hasil.
    """
    variants = list(rows_by_variant)
    primary = [p for p in primary if p[0] in variants and p[1] in variants]
    all_pairs = [(a, b) for i, a in enumerate(variants) for b in variants[i + 1 :]]
    secondary = [p for p in all_pairs if p not in primary and tuple(reversed(p)) not in primary]

    results = []
    for fam, pairs in (("primary", primary), ("secondary", secondary)):
        raw = {}
        for a, b in pairs:
            _, x, y, dibuang = paired_vectors(rows_by_variant[a], rows_by_variant[b], metric,
                                              min_n_gt=min_n_gt)
            r = wilcoxon_pair(x, y)
            r.update(pair=f"{a} vs {b}", family=fam, metric=metric,
                     min_n_gt=min_n_gt, n_sel_dibuang=len(dibuang),
                     sel_dibuang="; ".join(f"{c}/{d}/{s}(n={n})" for (c, d, s), n in dibuang))
            raw[r["pair"]] = r["p"]
            results.append(r)
        if fam == "secondary" and raw:
            adj = holm(raw)
            for r in results:
                if r["family"] == "secondary":
                    r["p_holm"] = adj[r["pair"]]
    for r in results:
        p_eff = r.get("p_holm", r["p"])
        r["signif_5pct"] = bool(p_eff < 0.05)
    return results


# ------------------------------- selang kepercayaan bootstrap (Subbab 3.11.5)
def bootstrap_map_ci(match_caches: dict[str, dict], pairs=PRIMARY_PAIRS,
                     n_boot: int = 1000, seed: int = 0, level: float = 0.95) -> list[dict]:
    """Selang kepercayaan bootstrap bagi selisih mAP@0,5:0,95 antarvarian.

    Naskah Subbab 3.11.5 mensyaratkan analisis pendamping yang tidak bergantung
    pada asumsi independensi antarunit: pengambilan ulang dilakukan pada TATARAN
    CITRA UJI dengan pengembalian (bukan tataran objek), sebanyak n_boot kali,
    sehingga keterkaitan antarobjek di dalam satu citra tetap utuh. Seluruh
    varian dinilai pada resample YANG SAMA (bootstrap berpasangan) agar selisih
    per resample sebanding. Deterministik untuk seed tertentu.

    match_caches: {nama_varian: keluaran y26_strata.global_match_cache}
    Return satu dict per pasangan: selisih titik, batas selang, proporsi
    resample bernilai positif, dan simpulan apakah selang memuat nol.
    """
    from y26_strata import map_from_sample

    pairs = [(a, b) for a, b in pairs if a in match_caches and b in match_caches]
    if not pairs:
        return []
    varian = sorted({v for p in pairs for v in p})
    n_img = match_caches[varian[0]]["n_images"]
    penuh = {v: map_from_sample(match_caches[v], np.arange(n_img)) for v in varian}

    rng = np.random.default_rng(seed)
    sampel = {v: np.empty(n_boot, float) for v in varian}
    for b in range(n_boot):
        idx = rng.integers(0, n_img, n_img)
        for v in varian:
            sampel[v][b] = map_from_sample(match_caches[v], idx)

    lo_q, hi_q = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    out = []
    for a, b in pairs:
        d = sampel[a] - sampel[b]
        d = d[~np.isnan(d)]
        lo, hi = (float(np.percentile(d, lo_q)), float(np.percentile(d, hi_q))) if len(d) else (float("nan"),) * 2
        out.append(dict(pair=f"{a} vs {b}", metric="mAP50-95", n_boot=int(len(d)),
                        n_images=int(n_img), level=level, seed=seed,
                        map_a=penuh[a], map_b=penuh[b], diff_point=penuh[a] - penuh[b],
                        diff_mean_boot=float(np.mean(d)) if len(d) else float("nan"),
                        ci_lo=lo, ci_hi=hi,
                        frac_positif=float(np.mean(d > 0)) if len(d) else float("nan"),
                        selang_tanpa_nol=bool(len(d) and (lo > 0 or hi < 0))))
    return out
