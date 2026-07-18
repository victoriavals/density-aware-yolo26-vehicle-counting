---
name: jalankan-eksperimen
description: Panduan menjalankan pelatihan tesis (smoke -> grid search alpha/sigma -> V1-V8 -> resume) sebagai background job dengan log berstempel-waktu dan --project absolut. Pakai saat akan melatih varian ablasi YOLO26.
---

# Jalankan Eksperimen — Run Experiment

> **EN — TL;DR:** Gate on `test_smoke.py` passing, then grid → `--variant all` → resume, always as a background job with a timestamped log and an **absolute** `--project`. Keep seed 0 and identical batch across all 8 variants.

## Prasyarat
- `.venv` aktif (Python 3.11.9, torch cu128, **ultralytics 8.4.92**, supervision <0.30).
- `python test_smoke.py` **T1–T4 LULUS** (skill `smoke-test`). GPU bebas.

## Urutan wajib
```bash
python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60   # grid -> dalw_best.json
python train_ablation.py --data dataset/data.yaml --variant all                  # V1..V8 (prioritas V1->V4->V8)
python train_ablation.py --data dataset/data.yaml --variant V5 --resume           # lanjut bila terputus
```

## Aturan
- **Background process** + pipe konvensi awk (stempel waktu per baris) → `logs/<nama>.log`. **`--project` WAJIB ABSOLUT** (`<repo>/runs_tesis`; gotcha P3).
- Konfigurasi terkunci: seed 0, imgsz 640, MuSGD, batch **16** FP16 identik untuk 8 varian, patience 50, alpha=1,0 sigma=0,1. A-12: OOM → turunkan batch **SEMUA** varian.
- Pantau: `Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8`. "stopped" biasanya selesai-normal.
- Jangan timpa `runs_tesis/`. Backup sebelum evaluasi.

## Rujukan
Detail: `.agents/playbooks/run-experiment.md`, `.agents/rules/methodology-invariants.md`, `.agents/rules/logging-and-status.md` (relatif ke root repo).
