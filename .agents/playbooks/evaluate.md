# Playbook: Evaluasi & Analisis — Evaluation and Analysis

> **EN — TL;DR:** After all variants train: (1) `test_eval.py` E1–E7 must pass; (2) back up `runs_tesis/`; (3) `evaluate_all.py --split test --variants all` → `eval_out/` (global, strata AP, Wilcoxon, `cache_V*.npz`); (4) `analyze_nmsfree.py` → `nmsfree_out/`; (5) `y26_counting.py` → `counting_out/`. Never overwrite the raw BAB-4 output folders. The `.npz` caches are reused to save inference.

Berkas sumber: `CLAUDE.md` §13–§14; `evaluate_all.py`, `analyze_nmsfree.py`, `y26_counting.py`, `test_eval.py`.

## 0. Prasyarat

- Semua varian terlatih di `runs_tesis/V*/` ([Playbook eksperimen](run-experiment.md)).
- **`python test_eval.py` E1–E7 LULUS** (skill `smoke-test`).
- **Backup** `runs_tesis/` (mis. `backups/runs_tesis_<stamp>.tar.gz`) — bahan mentah BAB 4.

## 1. Evaluasi deteksi (global + strata + Wilcoxon)

```bash
python evaluate_all.py --data dataset/data.yaml --split test --variants all
```

Keluaran `eval_out/`: `global_metrics.csv` (P/R/F1/mAP), `strata_ap.csv` (AP50 & AP50-95 per varian×kelas×dimensi×strata — **unit uji Wilcoxon**), `wilcoxon_ap5095.csv` + `wilcoxon_ap50.csv` (family, W, p, p_holm, rank_biserial, W_plus/minus, signif), `cache_V*.npz` (prediksi mentah kepala one-to-one, **dipakai ulang** untuk hemat inferensi). Konsep metrik: [Evaluasi](../knowledge/evaluation.md); protokol uji: [Statistik](../knowledge/statistics.md).

## 2. Analisis NMS-free (DR/CM/τ)

```bash
python analyze_nmsfree.py --data dataset/data.yaml --split test --runs runs_tesis --variants V1,V3,V5,V7,V8
```

Keluaran `nmsfree_out/`: `summary.csv` (DR τ=0,25, miss, dup, CM + Δ vs V1), `tau_sweep.csv`, `<V>.json`, `<V>_per_image.csv` (bahan Wilcoxon berpasangan), `dr_vs_tau.png`, `cm_hist.png`. Fokus varian ber-P2. Detail: [Analisis NMS-free](../knowledge/nmsfree-analysis.md).

## 3. Penghitungan end-to-end (RQ5)

```bash
python y26_counting.py --video video_uji/<klip>.mp4 --weights runs_tesis/V8/weights/best.pt \
    --line x1,y1,x2,y2 --interval-s 60 --gt gt_<nama>.csv
```

Keluaran `counting_out/`: counts, events, errors, `summary.json` (MAE/RMSE/MAPE/FPS). **MAPE hanya y>0.** Butuh video uji + `gt_<nama>.csv` + ambang **A-02**. Persiapan garis/GT: `siapkan_counting.py`. Detail: [Penghitungan](../knowledge/counting.md).

## Aturan

Jangan menimpa/menghapus `runs_tesis/`, `eval_out/`, `nmsfree_out/`, `counting_out/` — bahan mentah BAB 4. Cache `.npz` konsisten dengan bobot; regenerasi bila bobot berubah.

## Tautan terkait

- [Evaluasi](../knowledge/evaluation.md) · [Statistik](../knowledge/statistics.md) · [Analisis NMS-free](../knowledge/nmsfree-analysis.md) · [Penghitungan](../knowledge/counting.md) · [Alur data](../architecture/data-flow.md) · [Playbook BAB 4–5](write-bab4-5.md).
