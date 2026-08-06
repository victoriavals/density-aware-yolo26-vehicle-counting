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

## Hasil utama FINAL (unit AP50-95 per kelas × strata, n=24 sel pasca-FASE 1)

| Hipotesis utama | p | effect size | Bootstrap CI 95% (poin persen) | Kesimpulan |
|---|---|---|---|---|
| H1: V8 − V1 (penuh vs baseline) | 0,565 | r=+0,140 | [+0,05; +2,08] *tak memuat nol* | Wilcoxon **tidak signifikan** (dua uji berbeda arah — laporkan keduanya) |
| H2: V4 − V1 (DALW saja) | 0,208 | r=−0,300 | [−1,21; +1,00] memuat nol | **tidak didukung** (p besar, bukan nyaris) |
| **H3: V8 − V5** (DALW inkremental) | **0,0367** | **r=+0,487** | **[+1,26; +3,53]** *tak memuat nol* | **SIGNIFIKAN — temuan terkokoh** |

> ⚠️ **Angka di atas adalah hasil pasca-FASE 1** (ambang oklusi 0,40 + aturan sel-min-30 +
> bootstrap CI, 24 sel). Angka P7 lama (p=0,478/0,469/0,0125 pada 34 sel) **sudah tidak
> dipakai** — arah kesimpulan sama, tetapi selalu kutip angka pasca-FASE 1.

Kesimpulan awal: **DALW komplementer/kondisional** atas HAM+P2, tidak berdiri sendiri. Global mAP50-95 test berhimpit 0,522–0,538. Detail & sekunder Holm: [Statistik](../knowledge/statistics.md). Memicu **A-01** ([Keputusan pending](pending-decisions.md)).


## FASE 1, FASE 2, dan P9 (5 Agustus 2026)

**FASE 1 — perbaikan metodologi + re-run.** `OCC_EDGES` 0,35→**0,40** (Tabel 3.6); aturan
**sel minimum 30** objek GT (Subbab 3.11.5) → unit uji 34→**24 sel**, 12 dibuang & dilaporkan
terpisah; **bootstrap CI 95 %** (1.000 resample tataran citra berpasangan, Subbab 3.11.5)
ditambahkan. `test_eval.py` diperluas → **E1–E8 LULUS**. Arah kesimpulan tidak berubah.

**FASE 2 — dua eksperimen sisa naskah, keduanya tuntas.**
- *Sensitivitas α pada V4*: α=0,5 → 54,00 % test; α=1,0 → 53,66 %; **α=2,0 → 54,96 % test
  (tertinggi dari 7 varian yang diuji, di atas V8 53,75 %)** sekaligus tetap **30,5 FPS**.
  Mengonfirmasi empiris keterbatasan grid satu-titik (Subbab 3.9); α=1,0 tetap dipakai untuk
  ablasi utama demi keadilan perbandingan.
- *Ketegaran normalisasi-per-bobot*: V8_normw 53,62 % vs V8 53,75 % (selisih 0,13 poin,
  Wilcoxon p=0,944) → **gain DALW bukan efek skala loss** (hasil yang menguntungkan klaim).

**P9 — counting end-to-end (RQ5) SELESAI.** 3 klip × 10 interval × 3 kelas × 2 arah =
**180 pengamatan**. **MAE 1,972 · RMSE 4,947 · MAPE 37,17 %** (68/180 y=0 dikecualikan) ·
agregat **−23,9 %** · **FPS pipeline 20,47** (pakai angka ini untuk klaim *real-time*, bukan
23,3 FPS model murni). Dua koreksi metodologis: (1) konvensi arah in/out diselaraskan
("in" = menuju kiri-bawah) → MAPE klip 3 turun 54,79 %→**26,78 %**; (2) **klip 1 dikecualikan**
karena segmen garisnya tak menjangkau lajur mobil (cacat validitas pengukuran, wajib
dinyatakan eksplisit di BAB 4/5). Pola: MAE naik seiring kepadatan (0,72→1,05→4,15); roda dua
paling andal (−9 %), kendaraan besar terlemah (0/21 pada klip terpadat).

**Konsolidasi.** Seluruh bahan BAB 4–5 dirakit di **`hasil_bab4_5/`** (10 subfolder, generator
idempoten `y26_bangun_hasil_bab45.py`) + peta placeholder abstrak di
**`hasil_bab4_5/PETA_PLACEHOLDER_ABSTRAK.md`**. ⚠️ Temuan penting: kalimat hasil abstrak v7
memprasyaratkan kenaikan signifikan atas baseline yang **tidak didukung** (mAP@0,5 V8 77,97 %
< V1 78,61 %) → abstrak harus **ditulis ulang**, bukan diisi (keputusan A-01).

## Tautan terkait

- [Keputusan pending](pending-decisions.md) · [TODO dokumen](document-todos.md) · [Statistik](../knowledge/statistics.md) · [Playbook oklusi](../playbooks/occlusion-validation.md) · [Playbook BAB 4–5](../playbooks/write-bab4-5.md).
