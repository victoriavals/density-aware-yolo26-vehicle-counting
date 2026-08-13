# Verifikasi provenans dataset — hasil FASE 0–4 (13 Agu 2026)

> Pelaksanaan "RENCANA PERBAIKAN PROVENANS DATASET DAN NASKAH" Fase 0 sampai 4.
> Dokumen ini **mengoreksi** beberapa angka pada [`AUDIT_PROVENANS_DATASET.md`](AUDIT_PROVENANS_DATASET.md)
> (audit awal berbasis pola nama berkas). Audit awal dipakai sebagai **hipotesis**;
> di sini hipotesis itu diuji dan sebagian **gugur**.
>
> **Tidak ada dataset, bobot, split, atau naskah yang diubah.** Seluruh angka evaluasi
> baru berada di folder terpisah dan tidak menimpa `eval_out/`, `runs_tesis/`, `nmsfree_out/`.

---

## 0. Ringkasan untuk yang tidak punya waktu

| Temuan | Audit awal | Terverifikasi | Dampak |
|---|---|---|---|
| Citra ber-tanda-air | 67 | **315** | 4,7× lebih banyak; **248 tambahan semuanya di `train`** |
| Split evaluasi terdampak tanda air | 67 (valid 34 + test 33) | **67 (tidak berubah)** | ✅ angka BAB 4 **tidak** terpengaruh kurang-hitung |
| Kebocoran near-duplicate | dugaan | **terbukti: 3 pasangan jarak 0** | 1 pasangan `train`↔`test` → 1 citra uji dikecualikan |
| Lokasi CCTV | Yogyakarta + Demak | **+ Banjarmasin** | kota ketiga, belum pernah disebut |
| Rekaman asing di dataset | tidak diketahui | **Seoul, Mekkah, New York, Belanda** | klaim "CCTV Indonesia" perlu dibatasi |
| CCTV Indonesia asli | 1.792 (52,9 %) | **1.427 (42,1 %)** | kurang dari separuh dataset |
| Kesimpulan statistik | — | **H3 tetap signifikan di ketiga subset** | ✅ cabang terbaik gerbang Fase 3 |

**Dua bug pada rencana** ditemukan sebelum dieksekusi (lihat §5) — satu di antaranya akan
menghentikan seluruh rencana di menit ke-15 atas alarm palsu.

---

## 1. FASE 0 — Pembekuan (LOLOS)

`beku_20260813/` memuat: `dataset/` (3,0 GB, 3.389 citra terverifikasi), `dokumen/`
(naskah jurnal + tesis v8 + BAB4-5 + `TESIS_LENGKAP…v3.docx` + `data.yaml`),
`hasil_bab4_5_snapshot/`, `md5_dataset.txt` (**3.389 baris**), `md5_bobot.txt` (8 `best.pt`).

Alat permanen: **`integritas_artefak.py`** (`--buat` / `--periksa`) — dipakai kembali pada
Fase 7 untuk membuktikan tidak ada pelatihan ulang.

⚠️ Dua berkas yang disebut rencana **tidak ada** di repositori ini: `HASIL_BAB_4.zip`
(padanannya `hasil_bab4_5/`, sudah dibekukan) dan `TESIS_LENGKAP_BAB1-5_SIDANG_HASIL_v4.docx`
(versi tertinggi lokal `v3`, 6 Agu 16:04). Bila v4 ada di komputer lain, bekukan di sana.

---

## 2. FASE 1 — Inventarisasi provenans

### 2.1 Klasifikasi pola nama (LOLOS — cocok penuh dengan audit)

`provenans_audit.py` → **`provenans.csv`** (3.389 baris). Kelima kategori cocok **tepat**
dengan tabel audit: web_katalog 1.597 · frame_* 1.477 · ATCS 161 · Demak 87 · stok 67.
Enumerasi prefiks membuktikan hanya ada lima kelompok `night-traffic` (5, 8, 9, 12, 13) —
tidak ada nomor tak dikenal yang perlu ditebak.

**Bukti sampingan yang menguntungkan:** setiap kelompok `night-traffic` hanya muncul di
**satu** split (5→test, 8→valid, 9→test, 12→valid, 13→test) — *group split* bekerja
sebagaimana dirancang untuk kelompok kamera ini.

### 2.2 Pemeriksaan mata (Langkah 1.2) — menemukan kurang-hitung

67/67 kandidat `night-traffic-12/13` **terkonfirmasi ber-tanda-air "shutterstock"**
(6 lembar kontak, seluruhnya diperiksa, bukan sampel).

**Kontrol acak 30 citra menemukan 2 yang TERLEWAT** — keduanya `frame_*` di `train`
(`frame_000102`, `frame_000256`). Inilah gunanya langkah kontrol: pola nama **tidak dapat
dipercaya** untuk menentukan status hak cipta.

### 2.3 Audit penuh kelompok `frame_*` (1.477 citra)

Karena memeriksa 1.477 citra satu per satu tidak praktis, `audit_watermark_frame.py`
mengelompokkan `frame_*` dengan pHash (union-find, Hamming ≤ 12) → **139 klaster**
(35 klaster >1 anggota meliput 1.373 citra + 104 tunggal), lalu **satu perwakilan per
klaster** diperiksa mata. Seluruh 139 klaster diperiksa.

⚠️ **Pelajaran metodologis:** pemeriksaan pada **miniatur** punya **negatif palsu**.
Klip Seoul tampak bersih di miniatur tetapi ber-tanda-air jelas pada resolusi asli
(kontras tanda air rendah di adegan terang & sibuk). Karena itu ditambahkan lembar
**potongan tengah resolusi asli** (`lembar_crop`), dan seluruh klaster split evaluasi
diperiksa ulang dengan cara itu.

**Hasil — 248 citra ber-tanda-air tambahan, SELURUHNYA di `train`:**

| Sumber | Klaster | Citra | Split |
|---|---|---|---|
| Shutterstock — Mekkah (Masjid al-Haram, jemaah ihram), *car-free day*, masjid | 31 klaster | 229 | train |
| Shutterstock — **Seoul, Korea Selatan** (bus 202/507, marka Hangul) | K27, K39, K41, K45, K47, K55, K60, K62, K63, K64, K67, K70, K72 | 15 | train |
| **Kanal "NL Cycling"** (Belanda) — logo kanal, bukan Shutterstock | K100, K105, K108, K112 | 4 | train |

**Pemegang hak berbeda:** mayoritas Shutterstock, tetapi 4 citra membawa logo kanal
"NL Cycling" — pihak ketiga yang lain lagi.

**Terkonfirmasi bersih pada split evaluasi** (potongan resolusi asli): K2 (valid 104),
K5 (valid 92), K17 (**test 27**), K18/K19/K26/K135 (valid 50), K134/K136/K137/K138
(valid 4). → **tidak ada tanda air tambahan di `valid` maupun `test`.**

### 2.4 Rekaman bukan-CCTV dan bukan-Indonesia di kelompok `frame_*`

Label kategori "CCTV rekam layar" ternyata **tidak homogen**. Isinya:

- CCTV lalu lintas Indonesia asli (Yogyakarta, Demak, **Banjarmasin**);
- **kamera konsumen EZVIZ** (logo "ezviz" di sudut) — gang sempit, depan toko, bukan CCTV lalu lintas;
- rekaman stok ber-tanda-air (§2.3);
- **rekaman stok TANPA tanda air**: 50 citra `valid` adalah **Oculus / WTC Transportation Hub, New York** — pelataran marmer putih, pejalan kaki saja, **nol kendaraan**, monokrom, ber-*letterbox*. Kemungkinan besar ditambahkan untuk menambal kelas *pedestrian*.

### 2.5 Lokasi (Langkah 1.3) — kota ketiga

Audit menyebut Yogyakarta + Demak. Overlay yang terbaca menambah **satu kota lagi**:

| Overlay terbaca | Lokasi | Klaster |
|---|---|---|
| "Dishub Kota Banjarmasin — U turn RSUD Ulin" | **Banjarmasin, Kalimantan Selatan** | K17 (**27 citra, seluruh porsi `frame_*` di split test**) |
| "SIMPANG TERBAN", "PINGIT", "Nol Km – Timur", "S3 Pasar Telo", "S4 WIROSABAN", "Simpang Jogokariyan", "Simpang DeBritto", "JL. WARDANI", "JL. JUADI", "KOMINFO PEDATI SURKEN" + CSR Citranet/Gmedia/Lifemedia | **Yogyakarta** | banyak |
| "DISHUB DEMAK / ARAH SEMARANG", "TL TRENGGULI FIXED ARAH KUDUS" | **Demak, Jawa Tengah** | K5, K34, K136–K138 |

Catatan penting untuk Fase 4: **seluruh 27 citra `frame_*` pada split test adalah CCTV
Banjarmasin yang bersih** — jadi subset CCTV murni split uji (160 citra) = 96 ATCS
Yogyakarta + 37 Dishub Demak + 27 Dishub Banjarmasin, semuanya CCTV lalu lintas asli,
tanpa tanda air dan tanpa rekaman stok.

### 2.6 Klaim "kamera dipasang peneliti" (Langkah 1.4)

Bukti yang menguatkan temuan audit: artefak **"Activate Windows"** dan **bilah pemutar
video serta taskbar Windows** terlihat pada beberapa citra `frame_*` (mis. K8, K9) →
diperoleh dengan **merekam layar** penampil CCTV. Overlay lembaga pihak ketiga
(ATCS/CSR Citranet, Gmedia, Lifemedia, Dishub Demak, Dishub Banjarmasin) muncul konsisten.
Ditambah logo **EZVIZ** pada kamera konsumen. Tidak ada bukti kamera milik sendiri.

---

## 3. FASE 2 — Uji kebocoran near-duplicate (**ADA TEMUAN**)

`uji_phash.py` — pHash 64-bit (PIL + `scipy.fft`, **tanpa** memasang `imagehash`),
**jpg + png**, 3.389 citra, 2,64 juta pasangan lintas split dibandingkan.

| Pasangan split | Pasangan diuji | Jarak minimum | Jarak ≤ 5 |
|---|---|---|---|
| train × test | 801.736 | **0** | **1** |
| train × valid | 1.610.588 | **0** | **2** |
| valid × test | 229.502 | 10 | 0 |

**Ketiga pasangan berjarak Hamming 0 (pHash identik) tetapi md5 BERBEDA** — persis
mekanisme yang diduga audit §2.4: citra web beredar dalam beberapa ukuran/kompresi.
Semuanya `web_katalog` ↔ `web_katalog`:

| train | test / valid | Bukti |
|---|---|---|
| `Bus-Damri-1-768x480…` (768×480) | **test** `Bus-Damri-1…` (800×500) | nama berkas memuat ukuran; **diverifikasi visual: citra identik** |
| `DAMRI-1-1…` (604×453) | valid `DAMRI-1…` (604×453) | nama dasar sama, md5 beda (kompresi ulang) |
| `202101188092986…` (756×567) | valid `202102038642374…` (756×567) | id numerik beda (di-*scrape* dari dua URL) |

**Tindakan:** `Bus-Damri-1_jpg.rf.gm5kTdkPqNvN3EkT6AuO.jpg` (sisi **test**) dikecualikan
dari evaluasi Fase 3. `train` **tidak disentuh** — bobot sudah terlatih dengannya.

**Wajib dinyatakan di naskah apa pun hasilnya.** Skalanya kecil (1 dari 338 citra uji)
tetapi verifikasi split lama (md5 + grup) **tidak dapat** menemukannya.

---

## 3b. Audit `web_katalog` (1.597 citra) — sampel acak 60

Celah yang semula saya nyatakan sebagai keterbatasan, kini ditutup sebagian dengan sampel
acak deterministik (seed 7, `anotasi_provenans/sampel_web.txt`).

**Tanda air / merek pihak ketiga: 3 dari 60 (5,0 %)** — bukan Shutterstock melainkan
**tanda air situs penjual**: logo "OK TRUCKS — CERTIFIED BY IVECO", "BIG VAN WORLD", dan
satu URL situs. Ekstrapolasi kasar: ± 80 citra dari 1.597. Ditambah kredit fotografer
("James Panaligan") yang terlihat pada kontrol acak sebelumnya. Karakter hukumnya berbeda
dari rekaman stok — ini foto iklan dealer yang di-*scrape* — tetapi tetap hak cipta pihak ketiga.

**🔴 Empat citra adalah RENDER PERMAINAN VIDEO, bukan foto** (terverifikasi mata):
`UKTS_Bus_Simulator_Indonesia_PC`, `bus-simulator-fi-1` (memuat **logo permainan
"Bus Simulator"**), dan dua bingkai `download-game-simulasi-mengemudikan-` yang nyaris
kembar. **Dua di antaranya di split `valid`** — jadi citra sintetis ikut menentukan
*early stopping*. Jumlahnya kecil (0,1 %) tetapi secara kualitatif menonjol: citra buatan
mesin di dalam dataset yang dinyatakan sebagai rekaman CCTV lalu lintas.

**Isi `web_katalog` sebagian besar iklan dealer komersial**, mayoritas Inggris/Eropa,
ditambah Hong Kong, Israel, Seattle, London, Belanda, Amerika, Argentina, Pyongyang,
Thailand, Selandia Baru.

**Keluarga potongan satu-kendaraan** — relevan langsung dengan bias RQ4:

| Pola nama | Jumlah | Sifat |
|---|---|---|
| `Image_0<angka>` | 161 | tangkapan kamera timbang/tol, satu kendaraan |
| `gol<angka>_` | 141 | klasifikasi golongan tol, satu kendaraan |
| `T<angka>_png` | 79 | **foto nyata** truk *dump* dari kamera tinggi tepi jalan, pelat Indonesia terbaca — dipotong satu kendaraan |
| `Cutting-Sticker` / `wallpaper` / *mockup* | 19 | gambar promosi/desain |

⚠️ Dugaan awal saya bahwa `T<angka>_png` adalah render **salah** — setelah diperiksa pada
ukuran memadai, itu foto nyata. Dicatat agar tidak beredar sebagai temuan.

Ketiga keluarga pertama (**381 citra**) adalah potongan **satu kendaraan besar, tanpa
oklusi, densitas nol** — persis populasi yang menggelembungkan sel `size/large/big-vehicle`
(terukur 82 % pada split uji, §6.4).

⚠️ **Masih terbuka:** audit tanda air `web_katalog` baru berbasis sampel 60 citra (dari
1.597). Bila 3/60 mewakili, ± 80 citra bertanda air situs penjual belum terdaftar
satu per satu.

---

## 4. Komposisi dataset TERKOREKSI (3.389 citra)

| Kategori | train | valid | test | TOTAL | % |
|---|---|---|---|---|---|
| **web/katalog — BUKAN CCTV** | 1.124 | 328 | 145 | **1.597** | **47,1 %** |
| CCTV Indonesia rekam-layar (bersih) | 950 | 202 | 27 | 1.179 | 34,8 % |
| **stok Shutterstock — Mekkah/CFD/masjid** | 229 | 0 | 0 | **229** | 6,8 % |
| CCTV ATCS Yogyakarta | 0 | 65 | 96 | 161 | 4,8 % |
| CCTV Dishub Demak | 50 | 0 | 37 | 87 | 2,6 % |
| **stok Shutterstock — `night-traffic-12/13`** | 0 | 34 | 33 | **67** | 2,0 % |
| **stok tanpa tanda air — Oculus New York** | 0 | 50 | 0 | **50** | 1,5 % |
| **stok Shutterstock — Seoul** | 15 | 0 | 0 | **15** | 0,4 % |
| **stok kanal NL Cycling — Belanda** | 4 | 0 | 0 | **4** | 0,1 % |
| **Jumlah** | 2.372 | 679 | 338 | **3.389** | 100 % |

Turunan:

- **ber-tanda-air: 315** (train 248 · valid 34 · test 33) — audit awal 67
- **rekaman stok (semua, ber- maupun tanpa tanda air): 365 (10,8 %)**
- **CCTV Indonesia: 1.427 (42,1 %)** — audit awal 1.792 (52,9 %)
- **bukan CCTV: 1.597 (47,1 %)**

⚠️ Angka 1.427 masih **batas atas** untuk "CCTV lalu lintas": di dalamnya ada kamera
konsumen EZVIZ (gang, depan toko) yang bukan kamera lalu lintas. Menghitungnya menuntut
audit visual 1.179 citra dan belum dikerjakan.

Rincian di dalam `web_katalog` (§3b): **381 citra** potongan satu-kendaraan
(`Image_0*` 161 · `gol*` 141 · `T*` 79), **19** gambar promosi/desain, **4 render
permainan video** (2 di `train`, **2 di `valid`**), dan **± 80** citra (ekstrapolasi
sampel 3/60) bertanda air situs penjual.

---

## 5. Dua bug pada rencana (ditemukan sebelum dieksekusi)

### 5.1 🔴 Fase 0.2 akan memicu "BERHENTI" palsu

`find dataset/ -type f -name "*.jpg"` menghasilkan **2.347** baris, bukan 3.389, karena
dataset memuat **1.042 berkas `.png`** (train 763 · valid 252 · test 27). Kriteria lolos
rencana berbunyi "3.389 baris" dan tindak lanjutnya "Berhenti" → rencana menghentikan
dirinya sendiri di menit ke-15. Perbaikan: `\( -name '*.jpg' -o -name '*.png' \)`.

### 5.2 🔴 Fase 2 akan melewatkan populasi paling berisiko

Sketsa pHash memakai `rglob('*.jpg')` → melewatkan 30,7 % dataset, dan sebarannya tidak
acak: **963 dari 1.477** citra `frame_*` adalah `.png` (65,2 %). `frame_*` adalah bingkai
video berurutan — populasi yang paling mungkin near-duplicate antara `train` (1.198) dan
`valid` (252). Uji itu akan **tampak bersih tanpa pernah memeriksa subjek berisiko
tertingginya**. Sudah diperbaiki (jpg+png).

---

## 6. FASE 3 + 4 — Evaluasi ulang subset

**Tanpa inferensi ulang dan tanpa pelatihan ulang.** `eval_out/cache_V*.npz` menyimpan
prediksi mentah kepala one-to-one **per citra beserta nama berkasnya**, sehingga subset
dibentuk dengan menyaring cache lalu memanggil pipeline yang sama (`stratified_ap`,
`run_wilcoxon_suite`, `bootstrap_map_ci`). Sahih karena `collect_cache` me-*letterbox*
tiap citra sendiri-sendiri (deterministik, tanpa efek batch), proksi oklusi Pers. 3.1
hanya bergantung pada GT dalam citra yang sama, dan tier densitas dihitung per citra.

Alat: **`eval_subset.py`** (+ `delta_strata_subset.py` untuk selisih strata).

### 6.1 Kontrol reproduksi — LOLOS

Subset `penuh` (338 citra) mereproduksi ketiga p **tepat**: **0,5646 / 0,2076 / 0,0366**
(FASE 1, 4 Agu 2026). Penyaringan cache karena itu sahih, dan subset lain boleh ditafsirkan.

### 6.2 Ukuran subset

| Subset | Citra | Objek GT | Sel lolos `MIN_CELL_GT=30` |
|---|---|---|---|
| `penuh` (kontrol) | 338 | 2.600 | 24 / 36 |
| `bersih` (−33 tanda air, −1 bocor pHash) | **304** | 2.082 | 24 / 36 |
| `cctv` (hanya CCTV Yogyakarta+Demak+Banjarmasin) | **160** | 1.868 | 24 / 36 |

**Struktur 24 sel identik di ketiga subset** → n Wilcoxon tetap 24, ketiga subset
langsung sebanding, dan gerbang kelayakan Fase 4.2 ("berhenti bila sel lolos < 10")
terlampaui jauh.

### 6.3 Hasil uji hipotesis (AP50-95, unit kelas × strata, n = 24)

| Besaran | `penuh` (338) | `bersih` (304) | `cctv` (160) |
|---|---|---|---|
| **H1** V8−V1 p | 0,5646 | **0,3029** | **0,0787** |
| H1 r | +0,140 | +0,247 | **+0,413** |
| **H2** V4−V1 p | 0,2076 | 0,2522 | 0,5457 |
| H2 r | −0,300 | −0,273 | −0,147 |
| **H3** V8−V5 p | **0,0366** | **0,0395** | **0,0229** |
| H3 r | +0,487 | +0,480 | **+0,527** |
| H3 signifikan 5 % | **YA** | **YA** | **YA** |

**Gerbang keputusan Fase 3 → cabang "kesimpulan bertahan" (hasil terbaik).**
H3 tetap signifikan, arah H1 dan H2 tidak berbalik.

**Pola tambahan pada H1:** nilai p dan ukuran efek Wilcoxon membaik monoton seiring data
dibersihkan — p 0,565 → 0,303 → 0,0787 dan r +0,140 → +0,247 → +0,413. Mekanismenya
terukur (§6.4): citra katalog adalah kendaraan tunggal dari dekat (besar, tanpa oklusi,
densitas nol) sehingga V1 sama baiknya dengan V8 di sana dan selisihnya **mengencerkan**
rata-rata.

🔴 **Tetapi pola ini TIDAK boleh dibaca sebagai bukti yang menguat.** Selang bootstrap
pada subset `cctv` justru **melebar dan memuat nol** (§6.5) karena subsetnya hanya 160
citra. Kedua analisis sepakat: **belum ada peningkatan yang andal atas *baseline* V1**.
Pada subset CCTV pun p = 0,0787 belum melewati 5 %. Kutip §6.5 bersama §6.3 — jangan
salah satunya saja.

⚠️ Jangan menyebut subset `cctv` sebagai "hasil utama" tanpa keputusan pembimbing:
memilih subset yang memberi p terkecil **setelah** melihat hasilnya adalah seleksi pada
data uji. Statusnya **uji ketegaran**, dan ketiga subset dilaporkan berdampingan.

### 6.4 Selisih AP per strata — klaim K4 TEGAR terhadap komposisi data

Aturan sel-minimum K4 diterapkan sama (`delta_strata_subset.py`); hanya baris
`layak_dinarasikan = ya` boleh dikutip. Satuan poin persen.

**V8 − V5 (hipotesis yang signifikan):**

| Strata | `penuh` | `bersih` | `cctv` | layak |
|---|---|---|---|---|
| **occlusion/partial** | **+5,37** | **+6,57** | **+6,10** | ya |
| **size/small** | **+3,02** | **+3,08** | **+3,22** | ya |
| density/sparse | +2,18 | +2,17 | +3,07 | ya |
| occlusion/no | +2,32 | +1,98 | +2,21 | ya |
| size/medium | +1,09 | +1,16 | +0,85 | ya |
| density/medium | +0,89 | +0,98 | +1,28 | ya |
| size/large | −0,83 | −0,27 | +0,80 | ya |
| occlusion/heavy | — | — | — | TIDAK — semua sel < 30 GT |
| density/dense | −6,61 | −6,61 | −6,61 | TIDAK — hanya *pedestrian* |

→ **Kedua klaim sah K4 bertahan dan sedikit menguat.** Ini hasil ketegaran yang
menguntungkan naskah: keunggulan V8 atas V5 pada oklusi parsial dan objek kecil **tidak**
bergantung pada citra web/katalog.

**V8 − V1** (untuk melihat dari mana penguatan H1 berasal):

| Strata | `penuh` | `bersih` | `cctv` |
|---|---|---|---|
| **size/large** | +0,52 | +2,72 | **+5,02** |
| size/medium | −0,19 | +0,90 | +1,87 |
| occlusion/partial | +3,72 | +4,36 | +3,93 |
| occlusion/no | +1,11 | +1,21 | +1,65 |
| size/small | +0,87 | +0,28 | +0,53 |

Kenaikan terbesar ada pada `size/large` (+0,52 → +5,02 pp). Ini **mekanisme** di balik
penguatan H1: sel `size/large/big-vehicle` split uji **82 %** diisi citra web/katalog
(192 objek → 35 saat dibatasi CCTV), yaitu foto dealer satu kendaraan besar dari dekat.
Pada citra semacam itu *baseline* V1 sama baiknya dengan V8, sehingga selisihnya mendekati
nol dan **mengencerkan** rata-rata. Ditambah 381 citra potongan satu-kendaraan
(`Image_0*`, `gol*`, `T*`, §3b) yang seluruhnya jatuh ke strata "besar / tanpa oklusi /
renggang", inilah penjelasan kuantitatif untuk keganjilan sel `big-vehicle` yang selama
ini tidak dimiliki naskah.

### 6.5 Selang bootstrap 95 % (1.000 resample, tataran citra)

| Pasangan | `penuh` (338) | `bersih` (304) | `cctv` (160) |
|---|---|---|---|
| V8 vs V1 | +0,0102 [+0,0005; +0,0208] frac 0,979 **tanpa nol** | +0,0121 [+0,0009; +0,0222] frac 0,986 **tanpa nol** | +0,0149 [**−0,0005**; +0,0305] frac 0,972 **MEMUAT NOL** |
| V4 vs V1 | −0,0017 [−0,0121; +0,0100] frac 0,402 memuat nol | −0,0025 [−0,0136; +0,0096] frac 0,386 memuat nol | −0,0018 [−0,0187; +0,0148] frac 0,436 memuat nol |
| **V8 vs V5** | **+0,0229 [+0,0126; +0,0353] frac 1,000** | **+0,0211 [+0,0094; +0,0328] frac 1,000** | **+0,0226 [+0,0075; +0,0371] frac 0,998** |

✅ **Verifikasi tambahan:** bootstrap subset `penuh` mereproduksi `eval_out/bootstrap_ci.csv`
**bit-per-bit** (setiap digit sama). Karena bootstrap mengambil ulang **indeks citra**,
ini konfirmasi kedua — di luar ketiga nilai p — bahwa penyaringan cache eksak.

✅ **V8 vs V5 tegar pada KEDUA analisis di ketiga subset** — Wilcoxon signifikan dan selang
bootstrap tidak memuat nol. Inilah temuan yang boleh dinyatakan paling kuat.

🔴 **Peringatan penting — kedua analisis BERBEDA arah keyakinan untuk V8 vs V1 pada subset
`cctv`.** Nilai p Wilcoxon **membaik** (0,565 → 0,303 → 0,0787) tetapi selang bootstrap
justru **melebar dan mulai memuat nol** (batas bawah −0,0005), karena subset CCTV hanya
160 citra sehingga ragam pengambilan ulang tataran citra naik. Jadi tren p yang monoton
**tidak boleh** dibaca sebagai "hampir signifikan pada data bersih": begitu ketidakpastian
tataran citra diperhitungkan, buktinya **tidak** lebih kuat. Kedua analisis tetap sepakat
pada kesimpulan yang sama — **belum ada peningkatan yang andal atas *baseline* V1** —
konsisten dengan K-12 (bootstrap 10.000 × 3 seed). Melaporkan hanya nilai p tanpa selang
ini akan menyesatkan.

---

## 7. Yang masih terbuka

1. **Status 315 citra ber-tanda-air** — keputusan Naufal + pembimbing (naik dari 67;
   248 di `train`, jadi bobot terlatih dengannya dan pembersihan menyeluruh menuntut
   pelatihan ulang 8 varian ≈ 49 jam GPU).
2. **Distribusi dataset Roboflow** [17]/[38] — 315 citra ber-tanda-air masih terpublikasi.
3. **Audit tanda air `web_katalog`** — baru sampel 60 citra (3 bertanda air situs penjual);
   ± 80 dari 1.597 diperkirakan belum terdaftar satu per satu.
4. **Hitung kamera konsumen EZVIZ** di dalam 1.179 citra "CCTV bersih".
4b. **Empat render permainan video** (2 di `train`, 2 di `valid`) — perlu diputuskan apakah
   dikeluarkan dari dataset yang didistribusikan; satu memuat logo permainan.
5. **Koreksi naskah** (Fase 5): lokasi → Yogyakarta + Demak + **Banjarmasin**; lepas
   "self-collected"; paragraf komposisi; pernyataan lisensi; kalimat hasil pHash.
6. **Klaim "CCTV Indonesia"** perlu dibatasi: 42,1 % dataset, dan ada rekaman Seoul,
   Mekkah, New York, Belanda di dalamnya.

---

## 8. Artefak yang dihasilkan

| Berkas | Isi |
|---|---|
| `integritas_artefak.py` | manifest md5 `--buat`/`--periksa` (Fase 0 & 7) |
| `provenans_audit.py` | klasifikasi 3.389 citra + lembar kontak |
| `uji_phash.py` | pHash 64-bit tanpa dependensi baru, jpg+png |
| `audit_watermark_frame.py` | klaster pHash `frame_*` + lembar miniatur & potongan asli |
| `eval_subset.py` | evaluasi subset dari cache, + kontrol reproduksi |
| `delta_strata_subset.py` | selisih strata aturan K4 untuk subset |
| `provenans.csv` | 3.389 baris: split, kelompok sumber, dasar klasifikasi |
| `phash_semua.csv` / `phash_pasangan.csv` / `phash_eksklusi_test.txt` | hasil Fase 2 |
| `anotasi_provenans/` | lembar kontak, peta klaster, daftar ber-tanda-air |
| `hasil_penuh/` `hasil_bersih/` `hasil_cctv/` | strata_ap, wilcoxon, bootstrap, delta_strata per subset |
| `hasil_banding_subset.json` | tabel banding Fase 3.3 / 4.3 |
| `beku_20260813/` | pembekuan Fase 0 |
| `logs/fase2_phash.log`, `logs/fase34_subset.log` | log ber-stempel waktu |
