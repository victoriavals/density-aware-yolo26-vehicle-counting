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

## Hasil akhir — SELESAI 18 Jul 2026 09:43

**Kedelapan varian tuntas, batch 16 bertahan, 0 OOM, 0 crash.** Wall-clock total 45,5 jam (16 Jul 12:07 → 18 Jul 09:43). Semua berhenti via early stopping (patience 50); tidak ada yang mencapai 300 epoch. Aturan A-12 (fallback batch 8) TIDAK terpicu.

| Varian | Epoch (early stop) | mAP50-95 (val, training)* | Jam latih | VRAM puncak (GB) |
|---|---|---|---|---|
| V1 | 96 | 0,6407 | 1,58 | 5,04 |
| V2 | 112 | 0,6528 | 1,91 | 5,17 |
| V3 | 100 | 0,6505 | 8,80 | 8,52 |
| V4 | 84 | 0,6356 | 1,40 | 5,05 |
| V5 | 98 | 0,6516 | 10,24 | 8,64 |
| V6 | 52 | 0,6381 | 0,92 | 5,15 |
| V7 | 97 | 0,6337 | 9,21 | 8,52 |
| V8 | 99 | 0,6457 | 11,47 | 8,64 |

\* **PERINGATAN:** kolom ini adalah mAP validasi selama training (seluruh kelas & data), **bukan** AP terstratifikasi test-split yang menjadi unit hipotesis. Ranking ablasi & uji Wilcoxon baru sah setelah P7 (`evaluate_all.py`, split test). Jangan menyimpulkan kontribusi DALW dari angka ini.

**Observasi untuk BAB 4 (Tabel 3.7):** varian ber-P2 (V3/V5/V7/V8) memakan 8,5–11,5 jam & VRAM 8,52–8,64 GB (spill shared memory, tanpa crash) — konsekuensi head resolusi tinggi stride-4 (~4× titik anchor); varian non-P2 hanya 0,9–1,9 jam & ~5 GB. Artefak per varian lengkap: `results.csv`, `nmsfree_probe.csv` (S(t) per epoch), `complexity_train.json`, `weights/{best,last}.pt`.

## Log insiden & keputusan batch

- (16 Jul 12:07) Run dimulai dengan **batch 16** untuk semua varian.
- (18 Jul 09:43) Selesai tanpa satu pun OOM/error — batch 16 dipertahankan penuh; fallback batch 8 tidak diperlukan.
- Notifikasi harness "stopped" (18 Jul) BUKAN crash: itu penanda selesai-normal (V8 = varian terakhir). Job kembali terbukti selamat dari penutupan VS Code (berjalan ~45 jam lintas sesi).
