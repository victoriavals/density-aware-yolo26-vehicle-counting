# Ringkasan Progres Eksperimen — Experiment Progress Summary

> **EN — TL;DR:** Snapshot of the P1–P10 pipeline as of 18 Jul 2026. **P1–P7 + P8/P9 prep are done.** Grid winner `α=1.0, σ=0.10` (val mAP50-95 0.6670); all 8 variants trained (batch 16, 0 OOM); P7 stratified Wilcoxon: **V8−V5 significant (p=0.0125, r=+0.486)** while V8−V1 and V4−V1 are not → DALW is complementary. **Still open: P8** (manual occlusion validation) and **P10** (fill placeholders + write BAB 4–5). The canonical, always-updated log is `CLAUDE.md` §15 — this file summarizes and links, it does not replace it.

Berkas sumber (kanonik): `CLAUDE.md` §15. Ringkasan naratif per fase: `hasil/grid_search.md`, `hasil/catatan_run.md`, `hasil/ringkasan_evaluasi.md`.

## Status per prompt (P1–P10)

| Prompt | Isi | Status | Artefak kunci |
|---|---|---|---|
| P1 | Lingkungan (.venv, CUDA, versi) | ✅ 13 Jul | `logs/smoke.log`; T1–T4 LULUS |
| P2 | Dataset — *group split* 70/20/10 | ✅ 13 Jul | `dataset/`, `bukti_split_*.csv`; 2.372/679/338 |
| P3 | Grid search α,σ (3×3 di V8, 540 epoch) | ✅ 15 Jul | `dalw_best.json` (α=1,0 σ=0,1; 0,6670); `hasil/grid_search.md` |
| P4 | Rangkum grid (ditulis ulang dari `results.csv`) | ✅ 16 Jul | `hasil/grid_search.md` final |
| Revisi pembimbing | `y26_complexity.py` (Tabel 3.7) + rank-biserial | ✅ 16 Jul | efek mulai P5 (complexity) & P7 (effect size) |
| P5 | Latih 8 varian V1–V8 (batch 16, 0 OOM) | ✅ 16–18 Jul | `runs_tesis/V*/`; `hasil/catatan_run.md` |
| P7 | Evaluasi strata + Wilcoxon + NMS-free | ✅ 18 Jul | `eval_out/`, `nmsfree_out/`; `hasil/ringkasan_evaluasi.md` |
| Prep P8 | Kit anotasi oklusi manual | ✅ 16 Jul | `anotasi_oklusi/`, `make_oklusi_sample.py` |
| Prep P9 | Kit counting | ✅ 18 Jul | `siapkan_counting.py`, `video_uji/README.md` |
| **P8** | Validasi oklusi manual → `manual_oklusi.csv` | ⏳ **BELUM** | butuh anotasi Naufal ([playbook](../playbooks/occlusion-validation.md)) |
| **P10** | Konsolidasi placeholder + tulis BAB 4–5 | ⏳ **BELUM** | butuh P7/P8/P9 + A-01/A-02 ([playbook](../playbooks/write-bab4-5.md)) |

*(Penghitungan ByteTrack RQ5 (bagian dari P9) menunggu video uji + `gt_<nama>.csv` + ambang A-02.)*

## Hasil utama P7 (unit AP50-95 per kelas × strata, n=34)

| Hipotesis utama | p | effect size | Kesimpulan |
|---|---|---|---|
| V8 − V1 (penuh vs baseline) | 0,478 | r=+0,143 | tidak signifikan |
| V4 − V1 (DALW saja) | 0,469 | r=−0,144 (median −0,013) | tidak signifikan |
| **V8 − V5** (DALW inkremental) | **0,0125** | **r=+0,486** | **SIGNIFIKAN** |

Kesimpulan awal: **DALW komplementer/kondisional** atas HAM+P2, tidak berdiri sendiri. Global mAP50-95 test berhimpit 0,522–0,538. Detail & sekunder Holm: [Statistik](../knowledge/statistics.md). Memicu **A-01** ([Keputusan pending](pending-decisions.md)).

## Tautan terkait

- [Keputusan pending](pending-decisions.md) · [TODO dokumen](document-todos.md) · [Statistik](../knowledge/statistics.md) · [Playbook oklusi](../playbooks/occlusion-validation.md) · [Playbook BAB 4–5](../playbooks/write-bab4-5.md).
