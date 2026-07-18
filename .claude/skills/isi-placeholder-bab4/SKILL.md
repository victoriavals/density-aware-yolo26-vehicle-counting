---
name: isi-placeholder-bab4
description: Peta 18 placeholder numerik + 2 naratif BAB 4/ABSTRAK ke artefak eval_out/nmsfree_out/counting_out. JANGAN isi tanpa data nyata; hormati keputusan A-01/A-02 dan bahasa preprint. Pakai saat menyiapkan penulisan BAB 4.
---

# Peta Placeholder BAB 4 — BAB 4 Placeholder Map

> **EN — TL;DR:** Maps each placeholder to the artifact that fills it. **Never fabricate numbers.** A-01 (rewording if not significant) and A-02 (RQ5 thresholds) must be settled with the supervisor first; counting metrics need P9. This skill does **not** authorize drafting BAB 4–5.

## Peta placeholder → sumber
| Placeholder | Sumber angka | Status |
|---|---|---|
| mAP@0,5 / mAP@0,5:0,95 `[XX,X]` | `eval_out/global_metrics.csv` | P7 ✅ |
| Peningkatan `[X,X]` poin + p `[0,0XX]` | `eval_out/wilcoxon_*.csv` | P7 ✅ (⚠️ tidak signifikan → A-01) |
| AP kecil/densitas `[X,X]` poin | `eval_out/strata_ap.csv` | P7 ✅ |
| MAE/RMSE/MAPE `[X,XX]/[X,XX]/[X,X]` | `counting_out/summary.json` | **P9 belum** |
| FPS `[XX]` | `counting_out/summary.json` | P9 belum |
| 2× naratif DR & CM | `nmsfree_out/summary.csv` | P7 ✅ |

## Aturan mutlak
- **JANGAN** isi placeholder tanpa data nyata; **JANGAN** menggeser sitasi; **JANGAN** menulis draf BAB 4–5 di KB.
- Hasil utama P7 **tidak signifikan** (V8-V1, V4-V1) → A-01 aktif; tunggu keputusan Naufal + pembimbing.
- RQ5 butuh ambang **A-02** dari pembimbing.
- Pertahankan bahasa kehati-hatian *preprint*; laporkan effect size bersama p.

## Rujukan
`.agents/playbooks/write-bab4-5.md`, `.agents/status/document-todos.md`, `.agents/status/pending-decisions.md` (relatif ke root repo).
