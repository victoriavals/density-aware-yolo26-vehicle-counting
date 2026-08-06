# K5 / A-02 — Ambang "Standar Penerapan Praktis" untuk RQ5

> Disusun 5 Agustus 2026. **Status: USULAN — ambang final adalah keputusan pembimbing.**
> Angka sistem dibaca dari `09_counting_end_to_end/metrik_GABUNGAN.csv`,
> `perbandingan_sistem_vs_manual.csv`, dan `counting_out/fps_probe/`.

RQ5 berbunyi: *akurasi end-to-end dengan ByteTrack terhadap **standar penerapan praktis***.
Frasa terakhir belum pernah didefinisikan, dan itulah yang menghalangi RQ5 disimpulkan.

---

## 1. Masalah metodologis yang harus diakui lebih dulu

Hasil penghitungan **sudah diketahui** sebelum ambang ditetapkan: MAE 1,972 · RMSE 4,947 ·
MAPE 37,17 % · selisih agregat −23,9 % · FPS pipeline 20,47.

Karena itu setiap ambang yang dikarang sekarang adalah ***post-hoc***, dan penguji berhak
bertanya: "kalau MAPE-nya 45 persen, apakah ambangnya juga akan 50 persen?" Pertanyaan itu
tidak punya jawaban yang baik. Hanya ada dua jalan keluar yang jujur:

- **Jalan A — ambang berasal dari luar penelitian ini** (literatur/standar teknis yang bisa
  disitasi). Ambangnya tidak dikarang, jadi tuduhan *post-hoc* tidak berlaku.
- **Jalan B — RQ5 dilaporkan deskriptif**, tanpa verdikt lulus/tidak lulus.

Keduanya sah. Yang tidak sah adalah menetapkan angka sendiri sekarang lalu menyebutnya
"standar penerapan praktis".

---

## 2. Jalan A — tiga ambang literatur nyata (sudah diverifikasi ke sumber)

### A1. Skala interpretasi MAPE Lewis (1982) — **paling langsung terpakai**

| MAPE | Interpretasi |
|---|---|
| ≤ 10 % | sangat akurat (*highly accurate*) |
| 10–20 % | baik (*good*) |
| 20–50 % | **wajar / layak (*reasonable*)** |
| > 50 % | tidak akurat (*inaccurate*) |

**MAPE sistem 37,17 % → masuk kategori "wajar".** Skala ini sangat luas dipakai sebagai
rujukan penilaian akurasi dan tersedia di banyak publikasi turunan.

⚠️ Dua catatan kehati-hatian yang wajib ditulis bila skala ini dipakai: (a) skala Lewis
disusun untuk **peramalan** (*forecasting*), sehingga penerapannya pada galat penghitungan
adalah **analogi**, bukan standar bidang lalu lintas — nyatakan itu terbuka; (b) sumber
primernya adalah buku (Lewis, *Industrial and Business Forecasting Methods*, 1982) yang tidak
tersedia bebas, jadi banyak tesis menyitasi lewat publikasi sekunder. Verifikasi ke sumber
sekunder yang kredibel diperlukan — ini pekerjaan yang sejenis dengan **A-03**.

### A2. Toleransi FHWA *Traffic Monitoring Guide* — standar bidang lalu lintas

Dua angka yang relevan:

1. **±10 % pada taraf kepercayaan 95 %** untuk estimasi AADT tingkat perencanaan.
2. Standar pengujian peralatan turunan TMG (contoh implementasi: NYSDOT): *bin* kelas
   berisi **≥ 30 kendaraan** wajib mencapai akurasi **≥ 90 %**; *bin* < 30 kendaraan cukup
   **75–80 %**; *bin* volume keseluruhan **≥ 95 %**.

Menariknya, aturan "*bin* < 30 kendaraan diberi ambang lebih rendah" adalah **logika yang
sama** dengan aturan sel minimum `MIN_CELL_GT = 30` yang sudah dipakai tesis ini di
Subbab 3.11.5 — konvergensi yang layak disebut sebagai pembenaran independen.

**Hasil sistem terhadap standar ini** (agregat 3 klip, `perbandingan_sistem_vs_manual.csv`):

| Kelas | Sistem | Manual | Akurasi | Verdikt vs ambang |
|---|---|---|---|---|
| roda dua | 751 | 857 | **87,6 %** | *bin* ≥30 → gagal 90 %, tetapi **tipis** |
| mobil | 251 | 422 | 59,5 % | gagal |
| kendaraan besar | 20 | 64 | 31,2 % | gagal |
| **volume keseluruhan** | 1.022 | 1.343 | **76,1 %** | gagal ambang 95 % |

Jujur: **sistem tidak memenuhi standar peralatan pemantauan terkalibrasi.** Itu bukan
kegagalan yang memalukan — standar itu ditujukan bagi sensor terkalibrasi pada geometri
terkendali, sedangkan penelitian ini prototipe akademik pada lalu lintas heterogen padat
dengan kamera *existing*. Yang penting: **jangan mengklaim memenuhinya.**

### A3. Literatur *computer vision* penghitungan kendaraan — pembanding sebidang

Publikasi sejenis melaporkan akurasi penghitungan **90–98 %** (galat 1–5 %) untuk
YOLO+ByteTrack pada arus bebas, dan sekitar **90 %** untuk YOLO dibandingkan hitung manual.

⚠️ **Perbandingan ini WAJIB disesuaikan satuannya, kalau tidak menyesatkan.** Angka
90–98 % itu umumnya dihitung pada **total agregat** dalam kondisi **arus bebas**. Metrik utama
tesis ini adalah MAPE **per interval 60 detik × kelas × arah** — satuan yang jauh lebih keras
karena penyebutnya sering kecil (68 dari 180 pengamatan bahkan bernilai nol dan dikecualikan).

Satuan yang **sebanding** adalah selisih agregat: **−23,9 % (akurasi 76,1 %)**, jadi sistem
ini memang di bawah literatur — tetapi lihat §3 sebelum menyimpulkan penyebabnya.

---

## 3. Dekomposisi defisit — penyebabnya bukan terutama deteksi

Total defisit 321 kendaraan. Kontributor terbesar:

| Defisit | Sumber | Sistem vs manual | Sifat |
|---|---|---|---|
| **170** (53,0 %) | klip 4, mobil, arah *in* | 133 vs 303 | geometri garis |
| 56 (17,4 %) | klip 4, roda dua, *in* | 551 vs 607 | performa (−9,2 %) |
| 26 (8,1 %) | klip 2, roda dua, *out* | 17 vs 43 | perlu diperiksa |
| **21** (6,5 %) | klip 4, kendaraan besar, *in* | **0 vs 21** | geometri garis |
| 15 (4,7 %) | klip 3, kendaraan besar, *out* | 11 vs 26 | kelas minoritas |

**Sekitar 59,5 % defisit total berasal dari dua sel klip 4 (mobil + kendaraan besar)** yang
memperlihatkan pola yang **sama jenisnya** dengan cacat yang membuat klip 1 dikecualikan:
sistem mencatat nol atau sangat sedikit untuk kelas yang manual mencatat banyak, indikasi
garis virtual tidak memotong lajur yang dipakai kelas tersebut. Klip 4 tetap dipakai (keputusan
**K7a**) karena kelas mayoritas roda dua — 93,5 % arus pada pengukuran klip 1 — bekerja pada
−9,2 %.

**Implikasi redaksi:** angka agregat −23,9 % **tidak boleh** dinarasikan sebagai "akurasi
deteksi dan pelacakan sistem". Ia adalah akurasi **sistem beserta penempatan garisnya**.
Pelaporan per kelas wajib, dan keterbatasan geometri klip 4 wajib disebut berdampingan dengan
angkanya — persis seperti klip 1.

---

## 4. Kriteria FPS yang ditetapkan **secara a-priori** (tidak bergantung hasil)

Ini satu-satunya bagian RQ5 yang bisa punya ambang tanpa risiko *post-hoc*, karena
definisinya teknis dan tidak dikarang dari data:

> **Kriteria:** sistem disebut *real-time* bila laju pemrosesan menyeluruh ≥ laju bingkai
> sumber. Seluruh klip uji direkam pada **30,0 FPS** (`video_uji/konfigurasi_garis.json`).
> Ambang karena itu **30 FPS**.

Hasil ukur (`counting_out/fps_probe/`, 1.800 bingkai klip terpadat, ByteTrack aktif):

| Varian | FPS model (Tabel 3.7) | FPS pipeline terukur | Rasio thd 30 FPS | Verdikt |
|---|---|---|---|---|
| V1 (baseline) | 32,39 | 23,28 | 0,78× | tidak memenuhi |
| V4_a2.0 (DALW saja) | 30,51 | **23,20** | 0,77× | tidak memenuhi |
| **V8 (diusulkan)** | 23,31 | **19,29** | **0,64×** | **tidak memenuhi** |

Rata-rata pipeline pada tiga klip penuh: **20,47 FPS** (rentang 19,45–21,49).

**Konsekuensi yang harus diterima terbuka:** judul tesis memuat kata "*real-time*", sehingga
klaim kecepatan tidak dapat dihindari. Di bawah kriteria ≥30 FPS, **tidak satu pun varian
memenuhinya** ketika pelacakan diperhitungkan pada video padat.

Rumusan yang jujur sekaligus tidak merusak kontribusi:

> Sistem memproses sekitar 20 bingkai per detik secara menyeluruh, yaitu sekitar dua per tiga
> laju bingkai sumber. Laju tersebut memadai untuk pemantauan lalu lintas dengan penurunan
> laju bingkai (*frame skipping*) atau untuk pemrosesan rekaman, namun belum memenuhi
> pemrosesan setiap bingkai secara serentak pada laju 30 bingkai per detik.

⚠️ Bila pembimbing menghendaki klaim *real-time* yang lebih kuat, jalan yang tersedia
**bukan** menurunkan ambang, melainkan menyebut bahwa **konfigurasi DALW-saja 20 persen lebih
cepat** (23,20 vs 19,29 FPS) pada mAP@0,5:0,95 yang sedikit lebih tinggi — sebuah *trade-off*
kecepatan–akurasi yang terukur, dan biaya inferensi DALW **nol secara struktural** (parameter
dan GFLOPs identik *baseline*).

---

## 5. Jalan B — redaksi RQ5 deskriptif (bila pembimbing menolak menetapkan ambang)

Ubah pertanyaan dari verdikt menjadi pengukuran + pola. Materinya sudah lengkap:

> RQ5 dijawab dengan melaporkan akurasi penghitungan menyeluruh beserta polanya menurut
> kepadatan lalu lintas dan kelas kendaraan, tanpa menetapkan ambang kelulusan tunggal.

Pola yang siap dinarasikan:

1. **MAE meningkat monoton seiring kepadatan:** 0,717 (klip 2) → 1,050 (klip 3) → 4,150
   (klip 4). Ini menjawab RQ5 secara substantif — sistem tetap akurat pada arus sedang dan
   terdegradasi pada kepadatan tinggi.
2. **Keandalan per kelas mengikuti proporsi kelas dalam data latih:** roda dua (kelas
   mayoritas) 87,6 %; mobil 59,5 %; kendaraan besar (minoritas) 31,2 %.
3. **MAPE terbaik pada klip 3 (26,78 %)** yang paling sedikit interval bernilai nol (5 dari
   60) — memperlihatkan bahwa MAPE pada penyebut kecil menghukum berat, sesuai alasan aturan
   y > 0 di Subbab 3.11.3.
4. **Kecepatan 20,47 FPS** dilaporkan apa adanya dengan konteks laju sumber 30 FPS.

---

## 6. Rekomendasi

**Kombinasikan A1 + A2 + kriteria FPS a-priori, dan siapkan Jalan B sebagai cadangan.**

| Komponen | Ambang | Sumber | Hasil |
|---|---|---|---|
| MAPE per interval | 20–50 % = "wajar" | Lewis (1982), sebagai **analogi** | 37,17 % → **wajar** ✅ |
| Akurasi agregat kelas mayoritas | ≥ 90 % (*bin* ≥30) | FHWA TMG / NYSDOT | roda dua 87,6 % → **gagal tipis** ⚠️ |
| Akurasi volume keseluruhan | ≥ 95 % | FHWA TMG / NYSDOT | 76,1 % → **gagal** ❌ |
| Kecepatan | ≥ laju sumber (30 FPS) | teknis, a-priori | 20,47 FPS → **gagal (0,68×)** ❌ |

Alasan kombinasi ini yang terbaik:

1. **Tidak ada angka yang dikarang setelah melihat hasil** — semuanya berasal dari luar.
2. **Hasilnya campuran, dan itu justru kredibel.** Satu lulus, satu gagal tipis, dua gagal.
   Skema ambang yang membuat semuanya lulus akan mencurigakan; skema ini menunjukkan
   penelitian tidak menyetel ambangnya demi hasil.
3. **Memberi arah BAB 5 yang konkret:** yang gagal adalah volume agregat (didominasi geometri
   garis klip 4) dan kecepatan — keduanya masalah **rekayasa penerapan**, bukan cacat metode.
   Saran penelitian lanjutan jadi spesifik: kalibrasi geometri garis per kelas, dan
   optimasi inferensi (TensorRT/kuantisasi) atau penurunan laju bingkai terkendali.

## 7. Yang butuh keputusan pembimbing

1. **Setuju memakai skala Lewis sebagai analogi?** Bila tidak, RQ5 jatuh ke Jalan B.
2. **Setuju memakai FHWA TMG sebagai pembanding** meski hasilnya gagal? (Saran: ya —
   melaporkan kegagalan terhadap standar yang jelas lebih kuat daripada tidak punya
   pembanding.)
3. **Verifikasi sumber** — A1 dan A3 belum diverifikasi ke sumber primer; setara pekerjaan
   **A-03**. Untuk A2, `Traffic Monitoring Guide` FHWA perlu dirujuk ke edisi resminya.
4. ⚠️ **Referensi baru = entri baru [31] dan seterusnya, WAJIB via Mendeley.** Karena sitasi
   IEEE diurut kemunculan pertama dan seluruh rujukan ini muncul pertama kali di BAB 4,
   penambahannya **tidak menggeser** nomor [1]–[30] yang sudah ada — aman terhadap aturan
   `CLAUDE.md` §12.3. Menyunting daftar pustaka langsung di Word akan tertimpa Mendeley.

## Sumber yang dikonsultasikan

- [NYSDOT Traffic Monitoring Standards for Short Count Data Collection (EB 23-032)](https://www.dot.ny.gov/divisions/engineering/technical-services/hds-respository/Tab/NYSDOT_Traffic_Monitoring_Standards_for_Short_Count_Data_Collection_EB_23-032.pdf)
- [FHWA — Highway Performance Monitoring System, Ch. 5 (volume/AADT)](https://www.fhwa.dot.gov/policyinformation/hpms/volumeroutes/ch5.cfm)
- [Traffic Monitoring Fundamentals (National Academies)](https://www.nationalacademies.org/read/27925/chapter/3)
- [Interpretation of MAPE for Forecasting Accuracy (Lewis, 1982) — tabel turunan](https://www.researchgate.net/figure/Interpretation-of-MAPE-for-Forecasting-Accuracy-Lewis-1982_tbl1_398860905)
- [Re-interpretation of MAPE values and comparison with Lewis (1982)](https://figshare.com/articles/dataset/Re-interpretation_of_MAPE_values_and_comparison_with_interpretations_by_Lewis_1982_/29138492)
- [Automated Vehicle Counting from Pre-Recorded Video Using YOLO (MDPI J. Imaging)](https://www.mdpi.com/2313-433X/9/7/131)
- [A Real-Time Vehicle Counting, Speed Estimation, and Classification System Based on Virtual Detection Zone and YOLO](https://www.researchgate.net/publication/355863548_A_Real-Time_Vehicle_Counting_Speed_Estimation_and_Classification_System_Based_on_Virtual_Detection_Zone_and_YOLO)

Tautan internal: [redaksi hasil (K4)](K4_REDAKSI_HASIL.md) ·
[penghitung kedua (K7)](K7_PENGHITUNG_KEDUA.md) · [hasil counting](09_counting_end_to_end/)
