# Catatan Run P5 — Pelatihan 8 Varian (V1–V8)

**Diluncurkan:** 16 Jul 2026 ~12:07 WIB, background process, log `logs/train_all.log` (stempel waktu per baris, ASCII murni).
**Perintah:** `train_ablation.py --data dataset/data.yaml --variant all --project <ABSOLUT>/runs_tesis`

## Konfigurasi (identik antarvarian — Subbab 3.9 / keputusan A-12)

| Parameter | Nilai | Keterangan |
|---|---|---|
| **batch** | **16** | FP16/AMP; bila OOM pada varian ber-P2 (V3/V5/V7/V8) → ulang **batch 8 untuk kedelapan varian**; AutoBatch (-1) DILARANG untuk run final |
| epochs | maks 300 | early stopping patience 50 |
| imgsz | 640 | |
| optimizer | MuSGD | lr0=0,01, cos_lr |
| seed | 0 | deterministic=True |
| α, σ (DALW) | 1,0 / 0,1 | otomatis dari `dalw_best.json` (V4, V6, V7, V8) |
| probe NMS-free | 64 citra val/epoch | `nmsfree_probe.csv` per varian (A-10) |
| kompleksitas | callback aktif | `complexity_train.json` per varian (Tabel 3.7) |

Pra-syarat terpenuhi sebelum peluncuran: `test_smoke.py` T1–T4 LULUS pasca-revisi pembimbing (log `logs/smoke_pre_p5.log`); GPU bebas (737 MiB/8 GB).

## Log insiden & keputusan batch

- (16 Jul) Run dimulai dengan **batch 16** untuk semua varian. Belum ada OOM. *(Perbarui bagian ini bila ada perubahan.)*
