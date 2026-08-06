# 10 — Pengulangan Multi-Seed (Validitas Internal, Tabel 3.9)

## ✅ KEPUTUSAN K6 DIAMBIL (5 Agustus 2026): **TIDAK dijalankan — keterbatasan dinyatakan eksplisit**

Naufal memutuskan tidak menjalankan pengulangan multi-seed karena **anggaran waktu komputasi
tidak memungkinkan** (estimasi ~49 jam GPU tambahan). Naskah v7 Tabel 3.9 secara eksplisit
menyediakan jalan keluar ini:

> "...pengulangan sekurang-kurangnya tiga seed pada empat varian kunci [V1, V4, V5, V8],
> **sepanjang anggaran komputasi memungkinkan**; apabila pengulangan tidak dapat
> dituntaskan, keterbatasan tersebut **dinyatakan secara eksplisit pada BAB IV**."

Jadi keputusan ini **sah menurut protokol naskah sendiri** — bukan penyimpangan. Yang wajib
dipenuhi hanyalah kewajiban menyatakannya terbuka di BAB IV dan BAB V.

## Dasar estimasi biaya yang menjadi alasan penolakan

Dihitung dari waktu latih aktual P5 (`../03_kompleksitas_model/tabel_kompleksitas.csv`):

| Varian | Jam/seed | 2 seed tambahan |
|---|---|---|
| V1 | 1,58 | 3,2 jam |
| V4 | 1,40 | 2,8 jam |
| V5 | 10,24 | 20,5 jam |
| V8 | 11,47 | 22,9 jam |
| **Total** | | **≈49 jam GPU** |

Varian ber-P2 (V5, V8) mendominasi biaya karena *head* deteksi beresolusi tinggi
(stride 4) menghasilkan sekitar empat kali jumlah titik *anchor*.

## Kalimat siap-pakai untuk BAB IV (keterbatasan)

> "Pengulangan pelatihan pada beberapa nilai *seed* acak sebagaimana direncanakan pada
> Tabel 3.9 tidak dapat dituntaskan mengingat keterbatasan anggaran komputasi pada
> perangkat tunggal berkapasitas memori 8 gigabyte. Estimasi kebutuhan tambahan mencapai
> sekitar empat puluh sembilan jam komputasi GPU, terutama disebabkan oleh varian yang
> memuat Lapisan Deteksi P2 yang masing-masing memerlukan sepuluh hingga sebelas jam
> pelatihan per pengulangan. Dengan demikian, seluruh hasil yang dilaporkan pada bab ini
> merepresentasikan satu realisasi pelatihan dengan *seed* tetap bernilai nol untuk setiap
> varian, sebagaimana dicantumkan pada Tabel 3.4."

## Kalimat siap-pakai untuk BAB V (implikasi & saran)

> "Keterbatasan berupa tidak tersedianya pengulangan multi-*seed* perlu diperhatikan dalam
> menafsirkan perbandingan antarvarian yang selisihnya kecil, khususnya hipotesis pertama
> dan kedua yang tidak menunjukkan perbedaan signifikan. Variabilitas akibat inisialisasi
> acak dan urutan pengacakan data tidak terkuantifikasi pada penelitian ini, sehingga tidak
> dapat dipastikan apakah selisih kecil yang teramati berada di dalam atau di luar rentang
> fluktuasi antar-*seed*. Penelitian lanjutan disarankan menjalankan sekurang-kurangnya tiga
> pengulangan pada varian kunci dan melaporkan simpangan bakunya, sehingga kesimpulan
> mengenai kontribusi masing-masing komponen dapat diperkuat secara statistik."

## ⚠️ Kaitan dengan penafsiran hasil BAB 4

Keterbatasan ini **paling relevan untuk H1 dan H2** (`../04_ablasi_deteksi/`), yang
selisihnya kecil dan tidak signifikan:

- **H1 (V8 vs V1)**: selisih mAP hanya +1,02 poin persen, dengan batas bawah selang
  bootstrap +0,05 — sangat tipis. Tanpa data multi-seed, tidak dapat dipastikan apakah
  selisih sekecil ini melampaui fluktuasi antar-*seed*.
- **H2 (V4 vs V1)**: selisih −0,17 poin persen, praktis nol.
- **H3 (V8 vs V5)** relatif lebih aman: selisih +2,29 poin persen dengan selang bootstrap
  [+1,26; +3,53] yang jelas menjauhi nol, sehingga kesimpulannya lebih tahan terhadap
  ketidakpastian antar-*seed* — meski tetap tidak sepenuhnya bebas dari keterbatasan ini.

Rumusan yang disarankan: sebut keterbatasan ini **berdampingan** dengan pembahasan H1/H2,
bukan disembunyikan di akhir bab, agar pembaca dapat menilai kekuatan bukti secara adil.

## Tidak ada artefak data di folder ini

Karena pengulangan tidak dijalankan, folder ini hanya memuat dokumentasi keputusan dan
kalimat siap-pakai. Bila di masa depan multi-seed dijalankan, tambahkan `tabel_multiseed.csv`
(mAP per seed per varian) dan `grafik_multiseed_errorbar.png` (mAP ± simpangan baku), lalu
perbarui status di `../README.md`.
