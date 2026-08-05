# 09 — Penghitungan End-to-End dengan ByteTrack (RQ5)

## ⏳ STATUS: BELUM BISA DIISI — menunggu hitung manual (sedang dikerjakan Naufal per 5 Agustus 2026)

Bagian ini **sengaja kosong dari hasil**, sesuai aturan proyek: jangan mengisi
placeholder tanpa data eksperimen nyata (§12.3). Berikut apa yang **sudah siap** dan
apa yang **masih dibutuhkan**.

## ✅ Yang Sudah Siap

| Berkas | Isi |
|---|---|
| `konfigurasi_garis.json` | Garis virtual final, resolusi, FPS, jumlah frame, durasi untuk keempat klip — **bahan pelaporan wajib Subbab 3.10.1** |

### Ringkasan konfigurasi 4 klip

| Klip | Garis (piksel) | Resolusi | Interval | Sumber |
|---|---|---|---|---|
| 1_vidiouji | 504,1,1919,839 | 1920×1080 | 10×60dtk | CCTV ruas jalan |
| 2_vidiouji | 119,1,1919,926 | 1920×1080 | 10×60dtk | CCTV ruas jalan |
| 3_vidiouji | 0,317,1280,668 | 1280×720 | 10×60dtk | CCTV Puncak (arteri) |
| 4_vidiouji | 348,739,1919,784 | 1920×1080 | 10×60dtk | CCTV Padjajaran (persimpangan padat) |

Keempat klip **dipotong tepat 600,0 detik** (18.000 frame, `ffmpeg -c copy` tanpa encode
ulang) agar seluruh jendela pengamatan berdurasi sama — total **40 interval, 240
pasangan pengamatan** (10 interval × 3 kelas × 2 arah × 4 klip).

**Kepadatan lalu lintas terukur** (deteksi V8, batas bawah — lihat catatan keterbatasan):
klip 1–3 rata-rata 1,0–2,8 objek/frame (**tier sparse**); klip 4 rata-rata 17,1
objek/frame, puncak 30 (**tier medium**, 11,1% frame menyentuh ≥26). **Tier dense per
interval tidak terwakili** — keputusan sadar (K7) karena keterbatasan lokasi CCTV yang
terjangkau; harus dinyatakan eksplisit di BAB 4/5.

## ⏳ Yang Masih Dibutuhkan

1. **Hitung manual dua penghitung independen** untuk keempat klip (`video_uji/gt_*.csv`
   → salin jadi `_A.csv`/`_B.csv`, isi terpisah).
2. **Bandingkan & sepakati**: `python bandingkan_gt.py --dir video_uji` → tingkat
   kesesuaian awal antarpenghitung (wajib dilaporkan, Subbab 3.10.1) + tinjau baris
   berselisih → simpan sebagai `gt_<klip>.csv` final.
3. **Jalankan counting** (bobot V8): untuk tiap klip,
   ```bash
   python y26_counting.py --video video_uji/1_vidiouji.mp4 \
       --weights runs_tesis/V8/weights/best.pt --line 504,1,1919,839 \
       --interval-s 60 --gt video_uji/gt_1_vidiouji.csv --save-video
   ```
4. **Ambang lulus RQ5** (target MAPE & FPS — keputusan **A-02/K5**, belum diputuskan
   bersama pembimbing).

## Setelah counting selesai, folder ini akan diisi dengan:

- `ringkasan_counting.csv` — MAE, RMSE, MAPE, %eksklusi y=0, FPS pipeline, per klip + gabungan
- `kesesuaian_penghitung.csv` — tingkat kesesuaian awal dua penghitung per klip
- `grafik_prediksi_vs_manual.png` — sebar y (manual) vs ŷ (sistem) per interval
- `grafik_galat_per_kelas.png` — MAE per kelas kendaraan
- Analisis galat 2 lapis (Subbab 3.11.6): kegagalan deteksi vs pergantian identitas

**Jangan lupa regenerasi:** setelah data di atas tersedia, perbarui folder ini dan
`README.md` utama (ubah status folder 09 dari ⏳ ke ✅).
