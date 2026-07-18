---
name: smoke-test
description: Jalankan uji kebenaran (test_smoke.py T1-T4, test_nmsfree.py U1-U5, test_eval.py E1-E7) sebelum training/evaluasi. Wajib LULUS; kode terkunci ke ultralytics 8.4.92. Pakai sebelum melatih atau mengevaluasi varian.
---

# Smoke Test — Correctness Gate

> **EN — TL;DR:** Run the correctness suites before training/eval. `test_smoke.py` (T1–T4) is mandatory before any training. A T4 failure means ultralytics changed version → **stop** and reconcile `DALWDetectionLoss`.

## Perintah
```bash
python test_smoke.py            # T1-T4 (mengunduh yolo26s.pt ~19MB sekali)
python test_smoke.py --no-net   # lewati uji yang butuh unduhan
python test_nmsfree.py          # U1-U5
python test_eval.py             # E1-E7
```
(Windows: `\.venv\Scripts\python.exe test_smoke.py`.)

## Yang diuji
- **T1** matematika `density_weights` vs manual (Pers 3.2–3.4); **T2** 4 arsitektur terbangun (baseline/HAM/P2/HAM+P2); **T3** transfer bobot COCO (% cocok); **T4** loss end-to-end (DALW aktif di E2ELoss kedua head; batch padat → loss naik; 1-objek → identik).
- **U1** matcher + DR/CM; **U2** stabilitas S(t) (∅==∅); **U3** `train_format_forward` (BN tak berubah); **U4** ekstraksi assignment o2o; **U5** pipeline `evaluate_dr_cm`.
- **E1** atribut strata; **E2** AP 101-titik; **E3** protokol ignore; **E4** Holm + Wilcoxon vs scipy; **E5** metrik counting (aturan y>0); **E6** pipeline counting; **E7** integrasi strata jalur penuh.

## Arti kegagalan
- **T4 gagal** → versi ultralytics kemungkinan berubah dari **8.4.92** (`DALWDetectionLoss` menyalin `get_assigned_targets_and_loss` versi tersebut). **JANGAN lanjut training** sebelum disesuaikan (CLAUDE.md §13).

## Rujukan
`.agents/knowledge/environment.md`, `.agents/knowledge/dalw.md` (relatif ke root repo).
