# 09 — Penghitungan End-to-End dengan ByteTrack (RQ5)

**Status: ✅ hasil tersedia** untuk 3 klip (2, 3, 4). Satu hal masih terbuka: GT berasal dari
**satu penghitung**, sedangkan protokol Subbab 3.10.1 menuntut dua (keputusan **K7**), dan
ambang lulus RQ5 (**A-02/K5**) belum ditetapkan bersama pembimbing.

## Hasil Utama

### Metrik gabungan (180 pengamatan berpasangan, 3 klip)

| Besaran | Nilai |
|---|---|
| **MAE** | **1,972** kendaraan per interval |
| **RMSE** | **4,947** |
| **MAPE** | **37,17 %** (68/180 pengamatan y=0 dikecualikan, Subbab 3.11.3) |
| Total manual vs sistem | 1.343 vs 1.022 → **−23,9 %** (sistem kurang hitung) |
| **FPS pipeline end-to-end** | **20,47** rata-rata (rentang 19,2–21,4) |

⚠️ **Untuk placeholder abstrak "[XX] frame per detik" pakai ≈20 FPS** (pipeline lengkap
dengan ByteTrack + line crossing), **BUKAN** 23,3 FPS model murni di `03_kompleksitas_model/`.

### Per klip

| Klip | Karakter | MAE | RMSE | MAPE | y=0 | Manual | Sistem | Selisih |
|---|---|---|---|---|---|---|---|---|
| 2_vidiouji | lengang (1,0 obj/frame) | **0,717** | 1,478 | 39,28 % | 33/60 | 116 | 79 | −31,9 % |
| 3_vidiouji | arteri (2,1 obj/frame) | 1,050 | 1,522 | **26,78 %** | 5/60 | 296 | 259 | **−12,5 %** |
| 4_vidiouji | ramai (17,1 obj/frame) | 4,150 | 8,302 | 54,33 % | 30/60 | 931 | 684 | −26,5 % |

**Pola yang jelas dan layak dibahas:** galat absolut (MAE) **naik seiring kepadatan**
(0,72 → 1,05 → 4,15) — konsisten dengan hipotesis bahwa lalu lintas padat lebih sulit
dihitung karena oklusi dan perpindahan identitas. Sementara **MAPE terbaik justru pada
klip 3** (26,78 %) karena selnya paling padat isi (hanya 5/60 bernilai nol), sehingga
galat relatifnya paling stabil.

### Pola per kelas (bahan analisis galat Subbab 3.11.6)

| Klip | Kelas | Sistem | Manual | Selisih | Catatan |
|---|---|---|---|---|---|
| 2 | big-vehicle | 2 | 2 | **0 %** | tepat |
| 2 | car | 8 | 9 | −11 % | sangat baik |
| 2 | two-wheeler | 69 | 105 | −34 % | arah "out" terlemah (17 vs 43) |
| 3 | big-vehicle | 18 | 41 | −56 % | arah "out" 7 vs 26 |
| 3 | car | 110 | 110 | **0 %** | tepat (53/57 vs 60/50) |
| 3 | two-wheeler | 130 | 145 | −10 % | sangat baik |
| 4 | big-vehicle | **0** | 21 | **−100 %** ⚠️ | lihat catatan di bawah |
| 4 | car | 133 | 303 | −56 % | separuh terlewat |
| 4 | two-wheeler | 551 | 607 | **−9 %** | sangat baik meski padat |

**Tiga simpulan yang layak dibahas di BAB 4:**

1. **Roda dua paling andal** — galat −9 % sampai −10 % pada klip 3 dan 4, bahkan pada klip
   terpadat. Ini kelas mayoritas dataset (5.692 instans latih), sehingga konsisten dengan
   dugaan bahwa performa mengikuti kecukupan data latih.
2. **Kendaraan besar paling lemah** — tepat pada klip 2 (n kecil), tetapi −56 % pada klip 3
   dan **nol** pada klip 4. Ini kelas paling jarang di dataset (1.916 instans latih, kelas
   minoritas). Dugaan tambahan untuk klip 4: garis berada di **latar depan** sedangkan
   kendaraan besar cenderung berada di lajur utama yang lebih jauh, sehingga tak melintasi
   garis — pola yang serupa (meski lebih ringan) dengan alasan pengecualian klip 1.
3. **Mobil bergantung geometri** — tepat pada klip 2 dan 3, tetapi −56 % pada klip 4.
   Memperkuat dugaan bahwa penempatan garis di latar depan klip 4 hanya menangkap sebagian
   arus. **Layak dinyatakan sebagai keterbatasan penempatan garis**, bukan semata kelemahan
   model.

## Berkas

| Berkas | Isi |
|---|---|
| `metrik_GABUNGAN.csv` | **Angka utama untuk BAB 4** — MAE/RMSE/MAPE gabungan 180 pengamatan + FPS + klip yang dipakai/dikecualikan |
| `ringkasan_counting_per_klip.csv` | Metrik per klip (MAE/RMSE/MAPE/FPS, sistem vs manual) |
| `perbandingan_sistem_vs_manual.csv` | Rincian per klip × kelas × arah |
| `konfigurasi_garis.json` | Garis, resolusi, FPS, **konvensi arah**, dan **alasan pengecualian klip 1** — sumber pelaporan Subbab 3.10.1 |
| `grafik_sistem_vs_manual.png` | Batang berpasangan manual vs sistem, tiga klip |
| `grafik_sebar_per_interval.png` | Sebar y vs ŷ per interval — titik di bawah diagonal = sistem kurang hitung |
| `<klip>_counting_errors.csv` | Galat per (interval × kelas × arah) — bahan analisis galat Subbab 3.11.6 |
| `<klip>_counts_per_interval.csv`, `<klip>_summary.json` | Keluaran mentah `y26_counting.py` |

## Dua Koreksi Metodologis yang Sudah Diterapkan

### 1. Konvensi arah in/out diselaraskan (berdampak besar)

`sv.LineZone` menentukan in/out dari **orientasi garis** (titik A→B), sedangkan penghitung
manual mendefinisikan **"in" = kendaraan menuju kiri-bawah bingkai**. Diagnosis pelacakan
bingkai-per-bingkai membuktikan konvensi sistem **terbalik seragam** di keempat klip
(sistem "in" = menuju kanan-atas). Perbaikan: urutan titik garis dibalik — geometri garis
**identik**, hanya arah pembacaan yang berubah. Diverifikasi empiris pada klip 4:
`car_out=15` menjadi `car_in=15` (tertukar tepat, jumlah sama).

**Dampaknya besar** — tanpa koreksi ini, galat terinflasi oleh pertukaran arah sistematis:

| Klip | MAPE sebelum koreksi | MAPE sesudah |
|---|---|---|
| 2 | 77,26 % | **39,28 %** |
| 3 | 54,79 % | **26,78 %** |

### 2. Klip 1 dikecualikan (cacat validitas pengukuran)

Segmen garis klip 1 (`504,1,1919,839`) berakhir pada y=839 sehingga **tidak menjangkau
lajur bawah yang dipakai mobil**. Akibatnya hitung manual (mencakup lebar jalan penuh:
20 mobil per 10 menit) dan keluaran sistem (**0 mobil**) mengukur **populasi kendaraan
yang berbeda**.

Bukti: diagnosis 80 detik menemukan 24 *track* mobil terbentuk tetapi hanya 2 berpindah
sisi garis, dan **nol** event LineZone untuk kelas mobil. Uji pembanding dengan garis tegak
lurus (`1007,0,1528,1079`) menangkap **tepat 2 mobil** — sama dengan hitung manual menit 1.

**Ini cacat penyiapan pengukuran, BUKAN performa model yang buruk.** Berkas mentahnya tetap
disimpan sebagai bukti (`counting_out/1_vidiouji/`, `video_uji/preview/DIAG_klip1_mobil.jpg`).

> ⚠️ **WAJIB dinyatakan eksplisit di BAB 4 dan BAB 5.** Pengecualian data setelah hasil
> terlihat berpotensi dianggap *cherry-picking* bila alasannya tidak dijelaskan. Rumuskan
> sebagai keterbatasan penyiapan data, bukan sebagai penyaringan hasil.

## Kalimat siap-adaptasi

> "Evaluasi penghitungan end-to-end dilakukan pada tiga klip video berdurasi sepuluh menit
> dari titik pengamatan berbeda, menghasilkan 180 pasangan pengamatan antara hitungan
> sistem dan hitungan manual pada interval satu menit per kelas per arah. Sistem mencapai
> MAE sebesar 1,972 kendaraan per interval, RMSE sebesar 4,947, dan MAPE sebesar 37,17
> persen dengan 68 dari 180 pengamatan dikecualikan dari perhitungan MAPE karena bernilai
> nol sesuai ketentuan Subbab 3.11.3. Secara agregat sistem mencatat 1.022 perlintasan
> dibandingkan 1.343 hasil hitung manual, yaitu kekurangan 23,9 persen. Kecepatan pemrosesan
> pipeline lengkap yang mencakup deteksi, pelacakan ByteTrack, dan penghitungan perlintasan
> garis virtual mencapai rata-rata 20,47 bingkai per detik. Galat absolut meningkat seiring
> kepadatan lalu lintas, dari 0,717 pada klip berkepadatan rendah menjadi 4,150 pada klip
> paling ramai, sejalan dengan dugaan bahwa oklusi dan pergantian identitas pada kondisi
> padat menyulitkan pelacakan."

## Yang masih terbuka

1. **Penghitung kedua** (protokol 3.10.1) — GT saat ini dari satu penghitung. Alat siap:
   `python bandingkan_gt.py --dir video_uji` bila salinan `_A`/`_B` tersedia. Keputusan **K7**.
2. **Ambang lulus RQ5** (**A-02/K5**) — target MAPE & FPS belum ditetapkan pembimbing.
3. **Klip 4 satu arah** — GT klip 4 hanya memuat arah "in" (30 baris "out" bernilai nol)
   karena lalu lintasnya terbukti satu arah; asumsi ini perlu konfirmasi akhir.
4. **Analisis galat dua lapis** (Subbab 3.11.6) — kegagalan deteksi vs pergantian identitas;
   bahan tersedia di `<klip>_counting_errors.csv` dan `events.csv`.

Regenerasi: `python -c "from y26_bangun_hasil_bab45 import bab_09_counting; bab_09_counting()"`
