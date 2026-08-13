# Laporan sesi kerja — 13 Agustus 2026

> Satu dokumen berisi seluruh yang dikerjakan pada sesi ini, beserta angka, bukti, dan
> keputusan. Disusun atas permintaan Naufal.
>
> **Ringkas satu kalimat:** sesi ini dimulai dengan membuat alat demo dan menjawab
> pertanyaan spesifikasi artikel, lalu satu gambar jurnal yang sebenarnya opsional
> membongkar persoalan provenans dataset; persoalan itu ditelusuri sampai selesai, dampaknya
> diukur, dan naskah jurnal dikoreksi sesuai keputusan pembimbing teknis — **kesimpulan tesis
> bertahan**.

---

## Daftar isi

1. [Urutan pekerjaan](#1-urutan-pekerjaan)
2. [Website pengujian model](#2-website-pengujian-model-di-luar-scope-tesis)
3. [Jawaban K-01…K-16](#3-jawaban-k-01k-16-spesifikasi-artikel)
4. [Gambar jurnal V1 vs V8](#4-gambar-jurnal-v1-vs-v8--dan-bagaimana-temuan-muncul)
5. [Estimasi durasi rencana 7 fase](#5-estimasi-durasi-rencana-7-fase)
6. [FASE 0 — Pembekuan](#6-fase-0--pembekuan)
7. [FASE 1 — Inventarisasi provenans](#7-fase-1--inventarisasi-provenans)
8. [FASE 2 — Uji kebocoran pHash](#8-fase-2--uji-kebocoran-phash)
9. [Audit tanda air menyeluruh](#9-audit-tanda-air-menyeluruh--67--315)
10. [Komposisi dataset terkoreksi](#10-komposisi-dataset-terkoreksi)
11. [FASE 3 + 4 — Uji ketegaran](#11-fase-3--4--uji-ketegaran-tiga-subset)
12. [Keputusan pembimbing teknis dijalankan](#12-keputusan-pembimbing-teknis-dijalankan)
13. [Kekeliruan saya sendiri](#13-kekeliruan-saya-sendiri-dan-koreksinya)
14. [Verifikasi](#14-verifikasi)
15. [Artefak yang dihasilkan](#15-artefak-yang-dihasilkan)
16. [Yang masih terbuka](#16-yang-masih-terbuka)

---

## 1. Urutan pekerjaan

| # | Permintaan | Hasil |
|---|---|---|
| A | Website pengujian model V1–V8 | `webtest/` — FastAPI + satu halaman, diuji langsung |
| B | "Apakah sudah QA dan dijalankan?" | Server dinyalakan ulang; diakui QA hanya lewat curl, bukan peramban |
| C | Jawab K-01…K-16, terutama K-03 | `K01-K16_JAWABAN_SPESIFIKASI.md` |
| D | Inferensi V1 & V8 pada satu bingkai malam padat, untuk gambar jurnal | `y26_gambar_jurnal.py` + `15_gambar_jurnal/` → **memicu temuan provenans** |
| E | "Berapa lama rencana 7 fase ini?" | Estimasi dari angka terukur; premis rencana terbantah |
| F | Jalankan Fase 0–4 | Dokumen ini, §6–§11 |
| G | Jalankan keputusan pembimbing teknis | `JUTIF_Paper_..._REVISI_PROVENANS.docx`, §12 |

---

## 2. Website pengujian model (di luar scope tesis)

`webtest/` — alat demo/QA visual bergaya UI/UX repositori Traffic Pulse (dashboard gelap,
label Indonesia). FastAPI + satu halaman HTML/JS tanpa Node atau langkah *build*.

- **Dropdown 11 varian** (8 ablasi + `V4_a0.5`, `V4_a2.0`, `V8_normw`) dibaca otomatis dari
  `runs_tesis/*/weights/best.pt`, ber-badge HAM/P2/DALW. **Hanya satu model di VRAM
  sekaligus** (*evict-on-switch*) agar aman pada GPU 8 GB.
- **Uji gambar** — *forward* mentah kepala one-to-one, kotak berwarna memakai konvensi BGR
  yang sama dengan `traffic-detection-api`.
- **Uji video** — pilih garis virtual dengan klik dua titik pada bingkai pertama, proses
  ByteTrack + `LineZone` lewat `run_counting()` (impor langsung dari `y26_counting.py`, tanpa
  duplikasi logika), keluaran ditranskode H.264 via ffmpeg.

Diverifikasi *end-to-end* pada GPU: gambar V1 & V8 (249–605 ms), video 30 dtk V5 dengan garis
nyata klip 2 (`two-wheeler_in=5`, keluaran h264 1920×1080 terverifikasi ffprobe).

⚠️ **Jujur soal batasnya:** QA dilakukan lewat `curl`, **bukan** peramban. Pemilih garis pada
*canvas* belum pernah diuji secara visual. Ini sudah saya sampaikan saat ditanya.

---

## 3. Jawaban K-01…K-16 (spesifikasi artikel)

Enam belas pertanyaan dijawab dari kode/artefak dengan rujukan lokasi sumber →
[`K01-K16_JAWABAN_SPESIFIKASI.md`](K01-K16_JAWABAN_SPESIFIKASI.md).

**K-03 (inti pertanyaan).** Varian ber-P2 berparameter lebih sedikit **bukan** karena P5
dihapus — P5 dipertahankan (`Detect(P3,P4,P5)` → `Detect(P2,P3,P4,P5)`, *stride* 32 tetap).
Penyebabnya `Detect.__init__` Ultralytics mengikat lebar internal kepala pada `ch[0]` level
terhalus:

```python
c2 = max(16, ch[0] // 4, reg_max * 4)
c3 = max(ch[0], min(nc, 100))
```

P2 menurunkan `ch[0]` 128 → 64, sehingga `c2` 32 → 16 dan `c3` 128 → 64; `end2end: True`
menduplikasinya ke cabang `one2one_*` sehingga penyusutan terhitung dua kali. Neto: kepala
**−452.464**, neck **+166.528**, total **−285.936 (−2,9 %)**. Sifat bawaan Ultralytics resmi
(nc=80: 10.009.784 → 9.765.856, bereproduksi persis), bukan suntingan kami. Biaya HAM tepat
**+16.580** parameter.

→ **Hapus klaim "P2 menambah parameter".** Yang benar: parameter **turun 2,9 %** tetapi
GFLOPs **+17 %**, VRAM **+71 %**, detik/epoch **7×**.

**Ringkas jawaban lain:**

| Kode | Hasil |
|---|---|
| K-01 | `peak_gpu_train_gb` = `max_memory_allocated` (**tanpa** cache alokator); `reserved` terekam terpisah 6,37–11,80 GB; melampaui 8 GB fisik karena **limpahan memori bersama WDDM** — sekaligus menjelaskan varian P2 5,4–7,0× lebih lambat per epoch meski hanya +17 % GFLOPs |
| K-02 | Definisi **ada**, klaim tak perlu ditarik: `coverage` bebas-τ **95,5–97,8 %** vs `1 − miss_frac` pada τ=0,25 **67,1–77,9 %** (koreksi dari 97,2/67,9 yang berbasis 5 varian). **Jangan disebut *recall***; jarak ≈22 pp = defisit kalibrasi *confidence*, bukan kegagalan lokalisasi |
| K-06 | IoU **0,50** *class-aware*, bukan dugaan |
| K-07 | Diubah menjadi **TERSEDIA** → `nmsfree_out_8varian/`; V1/V3/V5/V7/V8 bereproduksi bit-per-bit. Baru: **V2** DR 0,6938; **V4** cakupan tertinggi 0,9781; **V6** duplikasi tertinggi 0,1146 (~3,3× V1) dengan CM terendah 0,4578 |
| K-12 | **Selesai** — bootstrap 10.000 × 3 seed berjalan **13,7 jam**; V8vsV1 batas bawah hanya +0,0035…+0,022 pp → tafsir sah tetap "tidak ada peningkatan andal"; V8vsV5 tegar (frac 1,000 ketiga seed) |
| K-13 | Rekomendasi tegas: **kosongkan** header ber-DOI milik artikel lain (misatribusi faktual) |
| K-15 | Pilih **(a)** karena prasyarat K-07 & K-08 terpenuhi |
| K-16 | Tak diketahui dari repositori |

---

## 4. Gambar jurnal V1 vs V8 — dan bagaimana temuan muncul

`y26_gambar_jurnal.py` (skrip permanen, idempoten) → `15_gambar_jurnal/`: **300 dpi**, lebar
fisik **tepat 16,99 × 5,14 cm**, kotak sebagai *patch* vektor matplotlib, pembeda **ganda**
warna + gaya garis (aman cetak abu-abu & deuteranopia), label ID dan EN, PNG+PDF+TIFF.

Pencocokan identik pipeline BAB 4: IoU ≥ 0,50 *class-aware*, conf > 0,25, *forward* mentah
kepala one-to-one.

**Rantai kejadian yang memunculkan seluruh temuan sesi ini:**

1. Dipilih bingkai uji **terpadat** (`night-traffic-9_mp4-0055`, 30 objek).
2. Ditolak sendiri: 18 dari 30 objeknya pejalan kaki, hanya 1 objek kecil — buruk untuk
   premis BAB 1. Bingkai di-*ranking* ulang menurut jumlah kendaraan/roda dua/objek kecil.
3. Kandidat berikutnya (`night-traffic-13_mp4-0015`) diperbesar → **terlihat tanda air
   "shutterstock"**.
4. Seluruh 3.389 citra diaudit → §7–§10 dokumen ini.
5. Bingkai final: `night-traffic-5_mp4-0028` (1144×638, 18 objek, **15 roda dua**, malam),
   bersih tanda air. Overlay lokasi **sengaja tidak dipotong**.

**Angka pada bingkai itu:** V1 → 17 prediksi, 13 TP / 4 FP / 5 FN (presisi 0,765);
V8 → 19 prediksi, 14 TP / 5 FP / 4 FN (presisi 0,737). Memperagakan mekanisme global
Subbab 4.11: objek terlewat **turun**, prediksi palsu **naik**.

---

## 5. Estimasi durasi rencana 7 fase

Ditanyakan sebelum eksekusi. Dijawab dari angka **terukur di repositori**, bukan taksiran.

| Fase | Taksiran rencana | Terukur/realistis |
|---|---|---|
| 0 Pembekuan | 15 mnt | 10–15 mnt ✓ |
| 1 Inventarisasi | 1–2 jam | 2 mnt mesin + 60–90 mnt mata ✓ |
| 2 pHash | 15 mnt | 5–10 mnt ✓ |
| 3 Evaluasi bersih | 1–2 jam | **± 30 mnt** |
| 4 Stratifikasi CCTV | 2–3 jam | **± 20 mnt** |
| 5 Koreksi naskah | ½ hari | 1–2 jam mesin + persetujuan |
| 6 Figure 9 | 30 mnt | 5–10 mnt |
| 7 Verifikasi | 1 jam | 30–60 mnt ✓ |

**Premis rencana terbantah.** Catatan penutup rencana menyebut "Fase 3 dan 4 sebagai penyita
waktu terbesar dan keduanya berupa inferensi". Keduanya **tidak butuh inferensi sama sekali**:
`eval_out/cache_V*.npz` menyimpan prediksi mentah **per citra beserta nama berkasnya**, jadi
subset dibentuk dengan **menyaring cache**.

**Biaya terukur:** `stratified_ap` ± 11 dtk/varian · Wilcoxon beberapa detik · **bootstrap
1.000 resample ± 28 mnt/subset** (tuas dominan `--n-boot`; 10.000 × 3 seed = 13,7 jam
terukur) · `global_val` + bangun cache 8 varian ± 6 mnt.

**Jalur kritis sebenarnya bukan komputasi**, melainkan balasan pembimbing. Karena itu
diusulkan satu perbaikan urutan: **jalankan Fase 3 + 4 lebih dulu (± 50 mnt), baru kirim
surel** — hasilnya dibutuhkan di setiap cabang keputusan, dan surel berisi dampak terukur
dijawab lebih cepat daripada surel berisi permintaan arahan.

---

## 6. FASE 0 — Pembekuan

`beku_20260813/`: `dataset/` (3,0 GB, 3.389 citra), `dokumen/` (naskah jurnal + tesis v8 +
BAB4-5 + LENGKAP v3 + `data.yaml`), `hasil_bab4_5_snapshot/`, `md5_dataset.txt`
(**3.389 baris**), `md5_bobot.txt` (8 `best.pt`).

Alat permanen **`integritas_artefak.py`** (`--buat` / `--periksa`) — dipakai lagi di §14.

### 🔴 Bug rencana #1 — akan memicu "BERHENTI" palsu

Perintah rencana:

```bash
find dataset/ -type f -name "*.jpg" | sort | xargs md5sum > beku_20260813/md5_dataset.txt
```

Kriteria lolosnya "3.389 baris", tindak lanjut bila gagal "Berhenti". **Terukur: perintah itu
menghasilkan 2.347 baris**, karena dataset memuat **1.042 berkas `.png`**:

| split | .jpg | .png | total |
|---|---|---|---|
| train | 1.609 | 763 | 2.372 |
| valid | 427 | 252 | 679 |
| test | 311 | 27 | 338 |
| **jumlah** | **2.347** | **1.042** | **3.389** |

Rencana akan menghentikan dirinya sendiri di menit ke-15 atas alarm palsu.
Perbaikan: `\( -name '*.jpg' -o -name '*.png' \)`.

⚠️ Dua berkas yang disebut rencana **tidak ada** di repositori: `HASIL_BAB_4.zip` (padanan
`hasil_bab4_5/`, sudah dibekukan) dan `TESIS_LENGKAP_..._v4.docx` (versi tertinggi lokal `v3`).

---

## 7. FASE 1 — Inventarisasi provenans

`provenans_audit.py` → **`provenans.csv`** (3.389 baris). Kelima kategori cocok **tepat**
dengan tabel audit awal: web_katalog 1.597 · `frame_*` 1.477 · ATCS 161 · Demak 87 · stok 67.

**Bukti sampingan yang menguntungkan:** setiap kelompok `night-traffic` hanya muncul di
**satu** split (5→test, 8→valid, 9→test, 12→valid, 13→test) — *group split* bekerja
sebagaimana dirancang.

### Pemeriksaan mata (Langkah 1.2)

- **67/67** kandidat `night-traffic-12/13` **terkonfirmasi ber-tanda-air**, seluruhnya
  diperiksa (6 lembar kontak), bukan sampel.
- **Kontrol acak 30 citra menemukan 2 yang TERLEWAT** — keduanya `frame_*` di `train`
  (`frame_000102`, `frame_000256`). Inilah gunanya langkah kontrol: **pola nama tidak dapat
  dipercaya** untuk menentukan status hak cipta.

### Lokasi (Langkah 1.3) — kota ketiga

| Overlay terbaca | Lokasi | Catatan |
|---|---|---|
| "Dishub Kota Banjarmasin — U turn RSUD Ulin" | **Banjarmasin, Kalsel** | **kota ketiga, belum pernah disebut**; K17 = seluruh 27 citra `frame_*` split **test** |
| "SIMPANG TERBAN", "PINGIT", "Nol Km – Timur", "S3 Pasar Telo", "S4 WIROSABAN", "Simpang Jogokariyan", "Simpang DeBritto", "JL. WARDANI", "JL. JUADI", "KOMINFO PEDATI SURKEN" + CSR Citranet/Gmedia/Lifemedia | **Yogyakarta** | banyak klaster |
| "DISHUB DEMAK / ARAH SEMARANG", "TL TRENGGULI FIXED ARAH KUDUS" | **Demak, Jateng** | K5, K34, K136–K138 |

→ Subset CCTV murni split uji (160 citra) = 96 ATCS Yogyakarta + 37 Demak + **27 Banjarmasin**,
semuanya CCTV lalu lintas asli tanpa tanda air.

### Klaim "kamera dipasang peneliti" (Langkah 1.4)

Artefak **"Activate Windows"**, bilah pemutar video, dan **taskbar Windows** terlihat pada
beberapa citra `frame_*` → diperoleh dengan **merekam layar**. Overlay lembaga pihak ketiga
konsisten, ditambah logo **EZVIZ** (kamera konsumen). Tidak ada bukti kamera milik sendiri.

---

## 8. FASE 2 — Uji kebocoran pHash

### 🔴 Bug rencana #2 — akan melewatkan populasi paling berisiko

Sketsa rencana memakai `rglob('*.jpg')` → melewatkan 1.042 citra (30,7 %), dan sebarannya
**tidak acak**:

| kategori | .jpg | .png | % terlewat |
|---|---|---|---|
| web_katalog | 1.518 | 79 | 4,9 % |
| **`frame_*` (bingkai video berurutan)** | 514 | **963** | **65,2 %** |

`frame_*` adalah populasi paling mungkin *near-duplicate* antara `train` (1.198) dan `valid`
(252). Uji itu akan **tampak bersih tanpa pernah memeriksa subjek berisiko tertingginya**.

`uji_phash.py`: pHash 64-bit via **PIL + `scipy.fft`** (tanpa memasang `imagehash`),
**jpg + png**, 2,64 juta pasangan lintas split.

### Hasil: ADA TEMUAN

| Pasangan | Diuji | Jarak min | ≤ 5 |
|---|---|---|---|
| train × test | 801.736 | **0** | **1** |
| train × valid | 1.610.588 | **0** | **2** |
| valid × test | 229.502 | 10 | 0 |

Ketiganya berjarak **Hamming 0 (pHash identik) tetapi md5 BERBEDA** — persis mekanisme yang
diduga audit. Semuanya `web_katalog`:

| train | test / valid | Bukti |
|---|---|---|
| `Bus-Damri-1-768x480…` (768×480) | **test** `Bus-Damri-1…` (800×500) | nama berkas memuat ukuran; **diverifikasi visual: citra identik** |
| `DAMRI-1-1…` (604×453) | valid `DAMRI-1…` (604×453) | nama dasar sama, md5 beda (kompresi ulang) |
| `202101188092986…` (756×567) | valid `202102038642374…` (756×567) | id numerik beda (di-*scrape* dua URL) |

**Tindakan:** citra sisi **test** dikecualikan dari evaluasi; `train` **tidak disentuh**
karena bobot sudah terlatih dengannya. Skalanya kecil (1 dari 338) tetapi verifikasi md5 lama
**tidak dapat** menemukannya — dan itulah yang wajib dilaporkan.

---

## 9. Audit tanda air menyeluruh — 67 → 315

Karena kontrol acak membuktikan pola nama tidak memadai, seluruh 1.477 citra `frame_*` diaudit
lewat **klaster pHash** (`audit_watermark_frame.py`, union-find Hamming ≤ 12) → **139 klaster**
(35 klaster >1 anggota meliput 1.373 citra + 104 tunggal). **Seluruh 139 perwakilan diperiksa
mata.**

**Hasil: 248 citra tambahan, SELURUHNYA di `train`.**

| Sumber | Citra | Split |
|---|---|---|
| Shutterstock — Mekkah (Masjid al-Haram), *car-free day*, masjid | 229 | train |
| Shutterstock — **Seoul, Korea Selatan** (bus 202/507, marka Hangul) | 15 | train |
| **Kanal "NL Cycling"** (Belanda) — logo kanal, **bukan** Shutterstock | 4 | train |

**Total ber-tanda-air: 315** (train 248 · valid 34 · test 33) — **4,7× angka audit awal**.

✅ **Kabar baiknya:** karena 248 tambahan seluruhnya di `train`, `valid`/`test` tetap 34/33 →
**angka BAB 4 tidak terpengaruh kurang-hitung ini.** Klaster split evaluasi (K2, K5, K17, K18,
K19, K26, K134–K138) diverifikasi bersih pada potongan resolusi asli.

### Audit `web_katalog` (sampel acak 60, seed 7)

- **3/60 (5,0 %)** bertanda air **situs penjual**: "OK TRUCKS — CERTIFIED BY IVECO",
  "BIG VAN WORLD", satu URL → ekstrapolasi ± 80 citra. Karakter hukumnya berbeda dari stok
  (foto iklan dealer yang di-*scrape*).
- 🔴 **4 citra adalah RENDER PERMAINAN VIDEO**, terverifikasi mata: `UKTS_Bus_Simulator_
  Indonesia_PC`, `bus-simulator-fi-1` (memuat **logo permainan "Bus Simulator"**), dan dua
  bingkai `download-game-simulasi-mengemudikan-` yang nyaris kembar. **Dua di split `valid`**
  → citra sintetis ikut menentukan *early stopping*.
- Isinya mayoritas iklan dealer komersial dari Inggris/Eropa, ditambah Hong Kong, Israel,
  Seattle, London, Belanda, Amerika, Argentina, Pyongyang, Thailand, Selandia Baru.

**Keluarga potongan satu-kendaraan** — relevan langsung dengan bias RQ4:

| Pola | Jumlah | Sifat |
|---|---|---|
| `Image_0<angka>` | 161 | kamera timbang/tol, satu kendaraan |
| `gol<angka>_` | 141 | klasifikasi golongan tol, satu kendaraan |
| `T<angka>_png` | 79 | **foto nyata** truk *dump* dari kamera tinggi tepi jalan, pelat Indonesia terbaca |
| `Cutting-Sticker` / wallpaper / mockup | 19 | gambar promosi/desain |

Tiga keluarga pertama (**381 citra**) semuanya jatuh ke strata "besar / tanpa oklusi /
renggang".

---

## 10. Komposisi dataset terkoreksi

| Kategori | train | valid | test | TOTAL | % |
|---|---|---|---|---|---|
| **web/katalog — BUKAN CCTV** | 1.124 | 328 | 145 | **1.597** | **47,1 %** |
| CCTV Indonesia rekam-layar (bersih) | 950 | 202 | 27 | 1.179 | 34,8 % |
| **stok Shutterstock — Mekkah/CFD/masjid** | 229 | 0 | 0 | **229** | 6,8 % |
| CCTV ATCS Yogyakarta | 0 | 65 | 96 | 161 | 4,8 % |
| CCTV Dishub Demak | 50 | 0 | 37 | 87 | 2,6 % |
| **stok Shutterstock — `nt-12/13`** | 0 | 34 | 33 | **67** | 2,0 % |
| **stok tanpa tanda air — Oculus New York** | 0 | 50 | 0 | **50** | 1,5 % |
| **stok Shutterstock — Seoul** | 15 | 0 | 0 | **15** | 0,4 % |
| **stok kanal NL Cycling — Belanda** | 4 | 0 | 0 | **4** | 0,1 % |
| **Jumlah** | 2.372 | 679 | 338 | **3.389** | 100 % |

Turunan:

- **CCTV Indonesia: 1.427 (42,1 %)** — audit awal menyebut 1.792 (52,9 %)
- **bukan CCTV: 1.597 (47,1 %)**
- **rekaman stok: 365 (10,8 %)**
- **ber-tanda-air: 315**

⚠️ Angka 1.427 masih **batas atas** untuk "CCTV lalu lintas": di dalamnya ada kamera konsumen
EZVIZ (gang, depan toko). Menghitungnya menuntut audit visual 1.179 citra — belum dikerjakan.

**Catatan khusus:** 50 citra `valid` adalah **Oculus / WTC Transportation Hub, New York** —
pelataran marmer putih, pejalan kaki saja, **nol kendaraan**, monokrom, ber-*letterbox*.
Kemungkinan besar ditambahkan untuk menambal kelas *pedestrian*.

---

## 11. FASE 3 + 4 — Uji ketegaran tiga subset

**Tanpa inferensi ulang dan tanpa pelatihan ulang.** `eval_subset.py` menyaring
`cache_V*.npz` menurut nama berkas lalu memanggil pipeline yang sama (`stratified_ap`,
`run_wilcoxon_suite`, `bootstrap_map_ci`).

**Mengapa sahih:** `collect_cache` me-*letterbox* tiap citra sendiri-sendiri (deterministik,
tanpa efek batch); proksi oklusi Pers. 3.1 hanya bergantung pada GT dalam citra yang sama;
tier densitas dihitung per citra. Menghapus citra lain tidak mengubah atribut citra tersisa.

### Kontrol reproduksi — LOLOS dua kali

Subset `penuh` mereproduksi ketiga nilai p **tepat** (0,5646 / 0,2076 / 0,0366) **dan**
`eval_out/bootstrap_ci.csv` **bit-per-bit**. Karena bootstrap mengambil ulang *indeks citra*,
yang kedua adalah konfirmasi independen bahwa penyaringan eksak.

### Ukuran subset

| Subset | Citra | Objek GT | Sel lolos `MIN_CELL_GT=30` |
|---|---|---|---|
| `penuh` (kontrol) | 338 | 2.600 | **24 / 36** |
| `bersih` (−33 tanda air, −1 bocor pHash) | **304** | 2.082 | **24 / 36** |
| `cctv` (Yogyakarta+Demak+Banjarmasin) | **160** | 1.868 | **24 / 36** |

Struktur **24 sel identik di ketiganya** → n Wilcoxon tetap 24, ketiga kolom langsung
sebanding, dan gerbang kelayakan Fase 4.2 ("berhenti bila sel lolos < 10") terlampaui jauh.

### Hasil uji hipotesis (AP50-95, unit kelas × strata, n = 24)

| Besaran | `penuh` (338) | `bersih` (304) | `cctv` (160) |
|---|---|---|---|
| **H1** V8−V1 p | 0,5646 | 0,3029 | 0,0787 |
| H1 r | +0,140 | +0,247 | +0,413 |
| **H2** V4−V1 p | 0,2076 | 0,2522 | 0,5457 |
| H2 r | −0,300 | −0,273 | −0,147 |
| **H3** V8−V5 p | **0,0366** | **0,0395** | **0,0229** |
| H3 r | +0,487 | +0,480 | **+0,527** |
| H3 signifikan 5 % | **YA** | **YA** | **YA** |

### Selang bootstrap 95 % (1.000 resample, tataran citra)

| Pasangan | `penuh` | `bersih` | `cctv` |
|---|---|---|---|
| V8 vs V1 | +0,0102 [+0,0005; +0,0208] **tanpa nol** | +0,0121 [+0,0009; +0,0222] **tanpa nol** | +0,0149 [**−0,0005**; +0,0305] **MEMUAT NOL** |
| V4 vs V1 | −0,0017 memuat nol | −0,0025 memuat nol | −0,0018 memuat nol |
| **V8 vs V5** | **+0,0229 [+0,0126; +0,0353]** | **+0,0211 [+0,0094; +0,0328]** | **+0,0226 [+0,0075; +0,0371]** |

✅ **V8 vs V5 tegar pada KEDUA analisis di ketiga subset** — inilah temuan yang boleh
dinyatakan paling kuat.

🔴 **Peringatan penting.** Kedua analisis **berbeda arah keyakinan** untuk V8 vs V1 pada
subset `cctv`: p Wilcoxon **membaik** (0,565 → 0,303 → 0,0787) tetapi selang bootstrap justru
**melebar dan mulai memuat nol**, karena subset itu hanya 160 citra. Jadi tren p yang monoton
**tidak boleh** dibaca sebagai "hampir signifikan pada data bersih". Kedua analisis tetap
sepakat: **belum ada peningkatan yang andal atas *baseline* V1** — konsisten dengan K-12.

### Selisih AP per strata — klaim K4 TEGAR

**V8 − V5** (hipotesis yang signifikan), kolom sel-min ≥30 GT, satuan poin persen:

| Strata | `penuh` | `bersih` | `cctv` | layak |
|---|---|---|---|---|
| **occlusion/partial** | **+5,37** | **+6,57** | **+6,10** | ya |
| **size/small** | **+3,02** | **+3,08** | **+3,22** | ya |
| density/sparse | +2,18 | +2,17 | +3,07 | ya |
| occlusion/heavy | — | — | — | TIDAK (semua sel < 30 GT) |
| density/dense | −6,61 | −6,61 | −6,61 | TIDAK (hanya *pedestrian*) |

→ **Kedua klaim sah K4 bertahan dan sedikit menguat.** Penjaga jujur tetap berlaku.

**V8 − V1**, dari mana penguatan H1 berasal:

| Strata | `penuh` | `bersih` | `cctv` |
|---|---|---|---|
| **size/large** | +0,52 | +2,72 | **+5,02** |
| size/medium | −0,19 | +0,90 | +1,87 |

**Mekanismenya terukur:** sel `size/large/big-vehicle` split uji **82 %** diisi citra
web/katalog (192 objek → 35 saat dibatasi CCTV). Pada foto dealer satu kendaraan besar dari
dekat, V1 sama baiknya dengan V8, sehingga selisihnya **mengencerkan** rata-rata. Ditambah
381 citra potongan satu-kendaraan (§9), inilah **penjelasan kuantitatif keganjilan sel
`big-vehicle`** yang selama ini tidak dimiliki naskah — termasuk mengapa sel
`big-vehicle/size/small` hanya berisi 17 objek padahal kelasnya menyumbang 2.645 instans.

⚠️ Subset `cctv` **bukan hasil utama**: memilih subset ber-p terkecil **setelah** melihat
hasilnya adalah seleksi pada data uji — kekeliruan yang sama sudah ditolak di K4.

---

## 12. Keputusan pembimbing teknis dijalankan

Keluaran: **`JUTIF_Paper_DA-YOLO26_Firdaus_REVISI_PROVENANS.docx`** (naskah asli tidak
diubah). Skrip: `revisi_jurnal_provenans.py` — 8 penggantian + 5 blok baru.

| Keputusan | Tindakan |
|---|---|
| **D-A1** | Figure 9 memakai bingkai **PENUH** (`image9.png` 1.191 KB; versi *zoom* 1.084 KB) |
| **D-A2** | Menjadi **Figure 9**, sesudah analisis galat, dirujuk di teks sebelum keterangannya |
| **D-A3** | Keterangan lima unsur, termasuk atribusi ATCS Pemkot Yogyakarta dan kalimat **"an illustration and not evidence"** yang tidak boleh dihapus |
| **D-A4** | Label (a)(b)(c) digeser (0,975 → 0,905); subjudul 6,4 → 7,4 pt; judul 8 → 8,5 pt. **Tera waktu "02-09-2025 19:24:19" kini terbaca penuh**; lebar fisik tetap 16,99 × 5,14 cm @ 300 dpi |
| **D-B** | Lokasi → Yogyakarta, Demak, Banjarmasin + pernyataan rekaman stok asing. ¶485 (sitasi [34] "Jakarta-Cikampek") **tidak disentuh**. Kalimat keterbatasan "one city" dihapus |
| **D-C** | "self-collected"/"data primer"/"kamera dipasang peneliti" **dihapus seluruhnya**; diganti deskripsi benar + **atribusi lembaga** di Method 2.1, keterangan Figure 9, dan ACKNOWLEDGEMENT |
| **D-D** | Paragraf komposisi di Method 2.1 memuat **angka 82 %** dan proporsi ketiga kategori |
| **Bagian 3** | Subbab **"Robustness to Dataset Composition" + Table 8** (tiga subset berdampingan); narasi pola p monoton **deskriptif** di DISCUSSIONS |
| **Bagian 5.2** | **NL Cycling dipisahkan**: 311 stok berbayar vs **4 materi kanal video** (kedudukan hukum berbeda) |
| **Bagian 5.3** | Sisiran **menyeluruh** 7 docx (`sisir_klaim_provenans.py`) |

**Satu tambahan yang tidak ada di keputusan:** pada narasi monoton saya sertakan **peringatan
bahwa selang bootstrap subset terkecil memuat nol**. Bootstrap `cctv` selesai setelah laporan
sebelumnya, dan hasilnya membuat tren p tidak dapat dibaca sebagai bukti menguat. Tanpa
kalimat itu, narasi deskriptif yang diizinkan berisiko dibaca sebagai klaim terselubung.

**Temuan sisiran Bagian 5.3 yang mengubah gambaran:** "15 Jakarta" di `TESIS_BAB4-5.docx`
ternyata **hampir semuanya nama berkas di Lampiran** (`jadwal-damri-…jakarta`) — itu data,
bukan klaim, dan tidak boleh diubah. Hanya ¶682 klaim prosa. Kekecualian juga ditambahkan
untuk `"Jakarta, [tanggal]"` (kota penandatanganan halaman administratif — Universitas Esa
Unggul memang di Jakarta). Cakupan nyata tesis: **2/1/4 per dokumen**, jauh lebih kecil.

**Keputusan 16 — angka wilayah tidak dikarang.** D-B menawarkan mengganti angka Jakarta
dengan angka DIY/Jawa Tengah "bila tersedia". Tidak tersedia terverifikasi, dan CLAUDE.md
§12.3 melarang mengisi angka tanpa data nyata → kalimat khusus Jakarta **dihapus tanpa
pengganti**. Angka nasional (168.275.423 kendaraan, 83,7 % roda dua) sudah memotivasi
paragrafnya. Bila Naufal punya sumber BPS/Korlantas untuk ketiga wilayah, kalimat itu dapat
dikembalikan dengan angka yang benar.

**Surel Dr. Sandfreni ditulis ulang** (butir 2): dua pertanyaan kewenangan institusional
**dinaikkan ke bagian atas**, cakupan dipersempit dari sepuluh hal menjadi dua. Kalimat
"Roboflow sudah dibatasi" dijadikan blok peringatan bersyarat karena saya tidak dapat
memverifikasinya.

---

## 13. Kekeliruan saya sendiri dan koreksinya

Dicatat karena proses harus terdokumentasi, bukan hanya hasil (§12.8).

| # | Kekeliruan | Koreksi |
|---|---|---|
| 1 | Server `webtest` saya matikan saat bersih-bersih, lalu Naufal tidak bisa mengaksesnya | Dinyalakan ulang terlepas; diakui QA hanya lewat curl, bukan peramban |
| 2 | Bingkai jurnal pertama dipilih hanya karena terpadat — 18/30 objeknya pejalan kaki | Bingkai di-*ranking* ulang menurut kendaraan/roda dua/objek kecil |
| 3 | Regex `night-traffic-(12\|13)\b` gagal karena `_` termasuk karakter kata | Diganti `(\d+)_` lalu bandingkan grup |
| 4 | Saya laporkan job bootstrap 10.000 "mati"; **sebenarnya selesai** 13,7 jam | Dikoreksi terbuka; §15 CLAUDE.md diperbaiki |
| 5 | Pemeriksaan **miniatur** punya **negatif palsu** — klip Seoul bersih di miniatur, ber-tanda-air pada resolusi asli | Ditambah lembar **potongan tengah resolusi asli**; seluruh klaster split evaluasi diperiksa ulang |
| 6 | Saya duga keluarga `T<angka>_png` (79 citra) adalah render | **Salah** — foto nyata truk *dump*, pelat Indonesia terbaca. Dicatat agar tidak beredar sebagai temuan |
| 7 | Saya sebut tren p monoton "menguntungkan naskah" | **Ditarik** setelah bootstrap `cctv` selesai: selangnya melebar memuat nol, jadi bukan bukti yang menguat |
| 8 | Detektor sisiran menandai **kalimat koreksinya sendiri** ("none of the material is primary data…") sebagai klaim | Ditambah penjaga PENYANGKALAN + pola D-D dipersempit |
| 9 | Draf surel memuat klaim "Roboflow sudah dibatasi" yang belum tentu benar | Dijadikan blok bersyarat |

Dua alarm verifikasi juga terbukti **palsu**: `media` tetap 9 karena FINAL memuat entri
direktori `word/media/` 0 KB (sebenarnya 8 → 9 gambar); dan "Table 9 tidak dirujuk" benar
karena tabel ke-9 adalah daftar periksa JUTIF yang tak bernomor.

---

## 14. Verifikasi

| Butir | Hasil |
|---|---|
| `test_eval.py` E1–E8 | **LULUS** (kode bersama tidak berubah perilaku) |
| Kontrol reproduksi p | 0,5646 / 0,2076 / 0,0366 **tepat** |
| Kontrol reproduksi bootstrap | **bit-per-bit** identik `eval_out/bootstrap_ci.csv` |
| `delta_strata_subset.py` vs K4 | mereproduksi tepat (+3,02 / +5,37 pp; penjaga *dense* aktif) |
| Integritas dataset | **3.389 berkas, 0 hilang / 0 tambah / 0 berubah** |
| Integritas bobot | **8 `best.pt`, 0 berubah** → bukti tidak ada pelatihan ulang |
| md5 naskah tesis & jurnal asli | **identik** dengan `beku_20260813/dokumen/` → tidak tersentuh |
| Abstrak jurnal revisi | **249 kata** (batas JUTIF 150–250) |
| Frasa terlarang | *self-collected* 0 · *data primer* 0 · *dipasang peneliti* 0 · *one city* 0 |
| Paragraf ber-"Jakarta" selain sitasi [34] | **0** |
| Sisiran klaim naskah jurnal revisi | **0 / 0 / 0 bersih** |
| Tabel & gambar | 8 → **9** keduanya; Figure 1–9 & Table 1–8 semua dirujuk |
| *Field* Mendeley | 0 di kedua versi jurnal (naskah jurnal memang tidak memakai Mendeley; tesis 121 instrText — karena itu tesis butuh pendekatan substring bila kelak diizinkan) |
| Tautan dokumen | 0 rusak |

---

## 15. Artefak yang dihasilkan

### Alat permanen (baru)

| Berkas | Fungsi |
|---|---|
| `integritas_artefak.py` | Manifest md5 dataset+bobot (`--buat`/`--periksa`) |
| `provenans_audit.py` | Klasifikasi sumber 3.389 citra + lembar kontak |
| `uji_phash.py` | pHash 64-bit tanpa dependensi baru, jpg+png |
| `audit_watermark_frame.py` | Klaster pHash `frame_*` + lembar miniatur & potongan asli |
| `eval_subset.py` | Evaluasi subset dari cache + kontrol reproduksi |
| `delta_strata_subset.py` | Selisih strata aturan K4 untuk subset mana pun |
| `sisir_klaim_provenans.py` | Sisiran klaim provenans menyeluruh di semua `.docx` |
| `revisi_jurnal_provenans.py` | Revisi naskah jurnal menurut keputusan pembimbing |
| `y26_gambar_jurnal.py` | Gambar banding siap-jurnal 300 dpi (**disunting** untuk D-A4) |
| `k12_bootstrap_10k.py` | Bootstrap 10.000 × 3 seed non-destruktif |
| `webtest/` | Alat demo/QA visual (di luar scope tesis) |

### Data & hasil

`provenans.csv` · `phash_semua.csv` · `phash_pasangan.csv` · `phash_eksklusi_test.txt` ·
`anotasi_provenans/` (lembar kontak + `klaster_frame.csv` + `watermark_frame_tambahan.csv`) ·
`hasil_penuh/` `hasil_bersih/` `hasil_cctv/` (strata_ap, wilcoxon, bootstrap, delta_strata) ·
`hasil_banding_subset.json` · `beku_20260813/` · `logs/fase2_phash.log` ·
`logs/fase34_subset.log`

### Dokumen

| Berkas | Isi |
|---|---|
| [`VERIFIKASI_PROVENANS_FASE0-4.md`](VERIFIKASI_PROVENANS_FASE0-4.md) | Hasil lengkap Fase 0–4 |
| [`AUDIT_PROVENANS_DATASET.md`](AUDIT_PROVENANS_DATASET.md) | Audit awal + **banner koreksi** |
| [`../catatan_keputusan.md`](../catatan_keputusan.md) | **16 entri** keputusan beserta alasan |
| [`SUREL_PEMBIMBING_PROVENANS.md`](SUREL_PEMBIMBING_PROVENANS.md) | Draf surel, dua pertanyaan di atas |
| [`K01-K16_JAWABAN_SPESIFIKASI.md`](K01-K16_JAWABAN_SPESIFIKASI.md) | Jawaban 16 pertanyaan |
| [`15_gambar_jurnal/`](15_gambar_jurnal/) | Figure 9 + README |
| `JUTIF_Paper_..._REVISI_PROVENANS.docx` | **Naskah jurnal terkoreksi** |

Diperbarui: `CLAUDE.md` §15 (2 entri baru + koreksi K-12) · `logs/sesi.log` (+30 entri) ·
`.agents/knowledge/dataset.md` (banner peringatan provenans) · `README.md` (bagian alat audit) ·
`.gitignore` (`beku_20260813/` 3,1 GB dan `anotasi_provenans/*.jpg` 18 MB dikecualikan;
136 KB bukti keputusan tetap ter-*track*)

---

## 16. Yang masih terbuka

### Menunggu Naufal

1. 🔴 **Batasi visibilitas dataset Roboflow** — **mendesak, mendahului segalanya** menurut
   keputusan pembimbing. **Tidak dapat saya kerjakan** (butuh akses akun). Rujukan dataset
   pada naskah menunjuk ke sana dan penelaah dapat mengekliknya kapan saja.
2. Kirim surel Dr. Sandfreni (dua pertanyaan sudah di atas).
3. Buka naskah revisi di Word: cetak satu halaman uji Figure 9, segarkan tata letak —
   penempatan gambar bisa bergeser saat Word merender ulang.
4. Bila punya sumber BPS/Korlantas untuk DIY + Jawa Tengah + Kalimantan Selatan, kalimat
   angka wilayah di Introduction dapat dikembalikan (Keputusan 16).

### Menunggu Dr. Sandfreni

5. Apakah mempertahankan bobot + pernyataan lisensi terbuka memadai menurut kebijakan
   integritas publikasi program studi.
6. Apakah tesis yang telah disidangkan perlu koreksi formal, dan melalui prosedur apa.
   **Naskah tesis belum disentuh** (md5 membuktikannya). Cakupan nyata bila diizinkan:
   2/1/4 paragraf per dokumen; `y26_revisi_bab13.py` adalah pola yang sudah terbukti
   mempertahankan 121 *field* Mendeley.

### Belum dikerjakan

7. Audit tanda air `web_katalog` menyeluruh — baru sampel 60 (± 80 dari 1.597 diperkirakan
   belum terdaftar satu per satu).
8. Hitung kamera konsumen EZVIZ di dalam 1.179 citra "CCTV bersih".
9. Status **4 render permainan video** (2 di `valid`) pada dataset yang didistribusikan.
10. **K6 multi-seed** (≥3 seed pada V1/V4/V5/V8) — belum diputuskan, ± 49 jam GPU.
11. Daftar periksa JUTIF penuh (butir 6 urutan pembimbing) — proporsi bagian, monotonisitas
    sitasi, rasio jurnal/prosiding 81,2 %, rujukan mutakhir 28.

---

## Catatan penutup

Yang paling perlu dipegang dari sesi ini: **kesimpulan tesis bertahan**. Hipotesis utama yang
signifikan (V8 vs V5) tetap signifikan pada ketiga subset, pada **kedua** analisis, dan kedua
klaim strata yang disahkan K4 juga bertahan bahkan sedikit menguat. Yang berubah adalah
kejujuran deskripsi datanya — dan itu membuat naskahnya lebih baik, bukan lebih lemah: tiga
kota alih-alih satu, uji ketegaran terhadap tiga komposisi, komposisi dataset yang dinyatakan
terbuka beserta angka 82 % yang akhirnya menjelaskan keganjilan stratifikasi, dan uji
kebocoran perseptual yang dilaporkan apa adanya termasuk temuan negatifnya.
