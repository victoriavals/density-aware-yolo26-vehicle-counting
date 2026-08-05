# 10 — Pengulangan Multi-Seed (Validitas Internal, Tabel 3.9)

## ⏸️ STATUS: BELUM DIPUTUSKAN (Keputusan K6, menunggu Naufal + pembimbing)

## Latar Belakang

Naskah v7 Tabel 3.9 (Ancaman terhadap Validitas Internal) menjanjikan:

> "...pengulangan sekurang-kurangnya tiga seed pada empat varian kunci [V1, V4, V5,
> V8], **sepanjang anggaran komputasi memungkinkan**; apabila pengulangan tidak dapat
> dituntaskan, keterbatasan tersebut dinyatakan secara eksplisit pada BAB IV."

Naskah sendiri menyediakan **jalan keluar yang sah** bila tidak dijalankan — ini bukan
kewajiban mutlak, tapi keputusan biaya-manfaat yang harus diambil sadar oleh Naufal
bersama pembimbing.

## Dua Opsi

### Opsi A — Jalankan multi-seed

Latih V1, V4, V5, V8 masing-masing pada ≥3 seed berbeda (`--seed` sudah didukung
`train_ablation.py` melalui parameter `seed=0` di `model.train()` — perlu ditambah
sebagai argumen CLI bila belum ada), laporkan simpangan baku & rentang mAP50-95 per
varian.

**Estimasi biaya** (berdasarkan waktu latih aktual P5, `03_kompleksitas_model/tabel_kompleksitas.csv`):
- V1: ~1,6 jam/seed × 2 seed tambahan = ~3,2 jam
- V4: ~1,4 jam/seed × 2 = ~2,8 jam
- V5: ~10,2 jam/seed × 2 = ~20,4 jam
- V8: ~11,5 jam/seed × 2 = ~23,0 jam
- **Total tambahan: ~49 jam GPU** (varian ber-P2 mendominasi biaya)

Prioritaskan **V4 dan V8** bila anggaran terbatas — keduanya penyangga klaim
kebaruan (H2 dan H3).

### Opsi B — Nyatakan keterbatasan eksplisit

Tulis di BAB 4/5 (kalimat siap-adaptasi, sesuai izin naskah sendiri):

> "Pengulangan pada beberapa nilai seed acak tidak dapat dituntaskan mengingat
> keterbatasan anggaran komputasi pada perangkat tunggal GPU 8GB, sehingga hasil
> yang dilaporkan merepresentasikan satu realisasi pelatihan (seed=0) untuk setiap
> varian. Keterbatasan ini berpotensi memengaruhi generalisasi temuan, khususnya pada
> perbandingan dengan selisih performa kecil seperti hipotesis H1 dan H2."

## Rekomendasi

Mengingat FASE 1 & FASE 2 (sensitivitas α, ketegaran normalisasi) sudah memakan
signifikan waktu GPU, dan masih ada P9 (counting) yang menunggu, **Opsi B lebih
realistis** kecuali Naufal punya kelonggaran waktu >2 hari GPU tambahan sebelum
tenggat. Keputusan akhir tetap milik Naufal + pembimbing.

## Setelah Diputuskan

- **Bila Opsi A**: folder ini akan diisi `tabel_multiseed.csv` (mAP per seed per
  varian) + `grafik_multiseed_errorbar.png` (mAP ± simpangan baku).
- **Bila Opsi B**: tidak ada artefak baru; cukup kalimat keterbatasan di atas dimasukkan
  ke BAB 4/5, dan folder ini bisa dihapus atau dibiarkan sebagai catatan keputusan.
