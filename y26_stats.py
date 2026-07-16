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
                   include_global: bool = False):
    """Sejajarkan sel (kelas × dim × strata) dua varian -> (keys, x, y).

    Default mengecualikan baris 'global' agar unit pasangan murni strata
    (sesuai frasa 'per kombinasi kelas dan strata evaluasi').
    """
    def key(r):
        return (r["cls"], r["dim"], r["stratum"])

    da = {key(r): r[metric] for r in rows_a if include_global or r["dim"] != "global"}
    db = {key(r): r[metric] for r in rows_b if include_global or r["dim"] != "global"}
    keys = sorted(set(da) & set(db))
    x = np.array([da[k] for k in keys], float)
    y = np.array([db[k] for k in keys], float)
    return keys, x, y


def run_wilcoxon_suite(rows_by_variant: dict[str, list[dict]], metric: str = "ap5095",
                       primary=PRIMARY_PAIRS) -> list[dict]:
    """Tiga hipotesis utama (taraf 5% tanpa koreksi) + seluruh pasangan lain (Holm)."""
    variants = list(rows_by_variant)
    primary = [p for p in primary if p[0] in variants and p[1] in variants]
    all_pairs = [(a, b) for i, a in enumerate(variants) for b in variants[i + 1 :]]
    secondary = [p for p in all_pairs if p not in primary and tuple(reversed(p)) not in primary]

    results = []
    for fam, pairs in (("primary", primary), ("secondary", secondary)):
        raw = {}
        for a, b in pairs:
            _, x, y = paired_vectors(rows_by_variant[a], rows_by_variant[b], metric)
            r = wilcoxon_pair(x, y)
            r.update(pair=f"{a} vs {b}", family=fam, metric=metric)
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
