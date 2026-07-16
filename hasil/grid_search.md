# P3–P4: Grid Search DALW (α × σ) — Hasil Final

**Status:** ✅ selesai 15 Jul 2026 19:15 (mulai 13 Jul 15:58; ±51 jam; 9 kombinasi × 60 epoch = 540 epoch; 0 crash).
**Protokol (Subbab 3.9):** grid 3×3 α ∈ {0,5; 1,0; 2,0} × σ ∈ {0,05; 0,10; 0,20} (koordinat ternormalisasi), sekali pada varian penuh V8, pelatihan dipersingkat 60 epoch, seed 0, kriteria mAP@0,5:0,95 validasi; nilai terpilih dibekukan untuk seluruh 8 varian.

> **Revisi 16 Jul 2026:** versi pertama dokumen ini memuat urutan ranking yang salah
> (rank 2–3 tertukar) dan klaim pola yang tidak sesuai data final. Seluruh tabel di
> bawah dihitung ulang langsung dari `runs_tesis/tune_a*_s*/results.csv`.

## Pemenang (dalw_best.json)

**α\* = 1,0, σ\* = 0,1 → mAP@0,5:0,95 (val) = 0,6670** (epoch terbaik: 41/60)

## Tabel 9 kombinasi (diurut mAP@0,5:0,95 validasi, terbaik dari 60 epoch)

| Rank | α | σ | mAP@0,5:0,95 (val) | Epoch terbaik | Selisih vs pemenang |
|---|---|---|---|---|---|
| 1 | **1,0** | **0,10** | **0,6670** | 41 | — |
| 2 | 2,0 | 0,20 | 0,6581 | 48 | −0,0089 |
| 3 | 2,0 | 0,10 | 0,6569 | 36 | −0,0100 |
| 4 | 1,0 | 0,20 | 0,6563 | 37 | −0,0107 |
| 5 | 1,0 | 0,05 | 0,6559 | 36 | −0,0111 |
| 6 | 0,5 | 0,05 | 0,6469 | 50 | −0,0200 |
| 7 | 2,0 | 0,05 | 0,6457 | 41 | −0,0213 |
| 8 | 0,5 | 0,10 | 0,6439 | 47 | −0,0231 |
| 9 | 0,5 | 0,20 | 0,6368 | 40 | −0,0302 |

## Matriks mAP@0,5:0,95 + rata-rata marginal

| | σ=0,05 | σ=0,10 | σ=0,20 | **rata-rata α** |
|---|---|---|---|---|
| **α=0,5** | 0,6469 | 0,6439 | 0,6368 | 0,6425 |
| **α=1,0** | 0,6559 | **0,6670** | 0,6563 | **0,6597** |
| **α=2,0** | 0,6457 | 0,6569 | 0,6581 | 0,6536 |
| **rata-rata σ** | 0,6495 | **0,6559** | 0,6504 | |

## Analisis pola (bahan sensitivitas α & narasi BAB 4)

1. **Pemenang adalah titik interior grid** pada kedua sumbu (α tengah, σ tengah) dan unggul pada rata-rata marginal keduanya — pemilihan konsisten, grid tidak perlu diperluas.
2. **α=0,5 terlemah secara seragam** (rank 6, 8, 9; rata-rata 0,6425): pembobotan densitas terlalu lemah, sinyal DALW nyaris tak terasa.
3. **α=2,0 menuntut kernel lebar** (rank 2–3 pada σ≥0,10 tetapi rank 7 pada σ=0,05): pembobotan agresif pada kernel sempit membuat bobot terlalu terkonsentrasi.
4. **Interaksi diagonal**: σ optimal bergeser naik seiring α — α=0,5→σ\*=0,05; α=1,0→σ\*=0,10; α=2,0→σ\*=0,20. Kekuatan pembobotan dan lebar kernel saling mengompensasi; kombinasi moderat–moderat (1,0; 0,10) menjadi puncak global.
5. **Rentang total 0,0302 mAP** (0,6368–0,6670) — pilihan α,σ berdampak nyata; grid search bukan formalitas.
6. **Konvergensi sehat**: seluruh kombinasi mencapai epoch-terbaik pada epoch 36–50 dari 60 (tidak ada yang mentok di epoch akhir → 60 epoch cukup untuk pemeringkatan; tidak ada divergensi/NaN/crash).

## Sanity check (spesifikasi Prompt 4)

- α\* = 1,0 ∈ {0,5; 1,0; 2,0} ✅
- σ\* = 0,10 ∈ {0,05; 0,10; 0,20} ✅
- `dalw_best.json` konsisten dengan perhitungan ulang dari `results.csv` (0,66697) ✅
- 9/9 folder run lengkap, masing-masing 60 epoch tercatat ✅

## Prasyarat P5 terpenuhi

- `dalw_best.json` siap — `train_ablation.py` membacanya otomatis
- Probe NMS-free sudah diperbaiki (`unwrap_model`) → `nmsfree_probe.csv` akan tertulis per epoch di V1–V8
- `ComplexityCallback` terpasang → `complexity_train.json` per varian (Tabel 3.7)
- Sumber angka: `runs_tesis/tune_a*_s*/results.csv` + `dalw_best.json` (jangan dihapus — bahan BAB 4)
