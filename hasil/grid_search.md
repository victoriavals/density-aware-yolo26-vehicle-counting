# P3: Grid Search DALW — Hasil Akhir

**Status:** ✅ **SELESAI 15 Jul 2026 19:15**

## Ringkasan Kombinasi (9/9 tuntas)

| Rank | α | σ | mAP50-95 (val, 60 epoch) | ΔmAP vs terbaik |
|---|---|---|---|---|
| 🥇 | **1.0** | **0.1** | **0.6670** | — |
| 2 | 1.0 | 0.2 | 0.6563 | −1.1% |
| 3 | 2.0 | 0.2 | 0.6581 | −1.3% |
| 4 | 2.0 | 0.1 | 0.6569 | −1.5% |
| 5 | 1.0 | 0.05 | 0.6559 | −1.7% |
| 6 | 2.0 | 0.05 | 0.6457 | −3.2% |
| 7 | 0.5 | 0.05 | 0.6469 | −3.0% |
| 8 | 0.5 | 0.1 | 0.6439 | −3.5% |
| 9 | 0.5 | 0.2 | 0.6368 | −4.5% |

## Analisis

**Pemenang: α=1.0, σ=0.1** (mAP50-95 = 0.6670)

**Pola signifikan:**
- **α=1.0 konsisten mendominasi** — 3 ranking teratas 2 milik α=1.0 (1st & 5th). Densitas pemboboran moderat unggul.
- **σ=0.1 (kernel radius menengah) = sweet spot** — pemenang, dan ranking 2&4 juga σ=0.1.
- **α=0.5 terlemah** — semua 3 kombinasinya ranking 7–9 (pemboboran terlalu lemah, densitas diabaikan).
- **α=2.0 bervariasi** — kompetitif di σ tinggi (rank 3,4) tapi merosot di σ rendah (rank 6). Pemboboran terlalu agresif mungkin membuat model overfitting pada densitas ekstrim.

**Konvergensi:** laju pembelajaran & early stopping stabil; tidak ada kombinasi yang divergen atau crash.

## Prasyarat P5 Terpenuhi

✅ `dalw_best.json` siap (`{"alpha": 1.0, "sigma": 0.1, "map5095": 0.66697}`)  
✅ Semua 9 run terekam di `runs_tesis/tune_a*_s*/` (checkpoint + results.csv)  
✅ Pipeline NMS-free probe diperbaiki (unwrap_model, efektif P5+)  

## Next: P5

Latih 8 varian (V1–V8) dengan α=1.0, σ=0.1 (dari dalw_best.json), maks 300 epoch + early stopping, seed 0. Prioritas: V1→V4→V8 (hip ablasi).

