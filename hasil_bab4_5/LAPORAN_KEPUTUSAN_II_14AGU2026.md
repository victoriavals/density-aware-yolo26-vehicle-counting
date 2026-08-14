# Laporan — pelaksanaan Keputusan Pembimbing Teknis (II), 14 Agustus 2026

> Dokumen ini melaporkan apa saja yang saya kerjakan setelah menerima dokumen keputusan
> kedua. Kelanjutan dari [`LAPORAN_SESI_13AGU2026.md`](LAPORAN_SESI_13AGU2026.md).
>
> **Keluaran utama:** `JUTIF_Paper_DA-YOLO26_Firdaus_REVISI2.docx`

---

## 1. Ringkas — apa yang berubah

| Gerbang akhir | Status |
|---|---|
| 1. K1 selesai, angka render & tanda air penjual masuk naskah | 🔄 **sebagian** — split test tuntas, train/valid 3/21 lembar |
| 2. K2 selesai, tak ada "1.000 resample" tertinggal | ✅ **SELESAI** |
| 3. K3 selesai atau dinyatakan tidak perlu | ✅ **TIDAK PERLU** — terbukti |
| 4. Koreksi Bagian 1 diterapkan pada DISCUSSIONS | ✅ **SELESAI** |
| 5. D-F sampai D-I diterapkan | ✅ **SELESAI** |
| 6. Visibilitas Roboflow dibatasi | ⬜ **Naufal** |
| 7. K6 manifes diperbarui | ✅ **SELESAI** |
| 8. Dua pertanyaan dijawab Dr. Sandfreni | ⬜ **di luar kendali** |

---

## 2. Koreksi premis pada D-F

Dokumen keputusan menyebut *"empat citra itu ditemukan dari sampel 60 citra, yaitu 6,7 persen.
Ekstrapolasinya sekitar 107 citra"*.

**Itu keliru membaca laporan saya, dan koreksinya penting karena mengubah skala masalah.**
Angka 4 adalah **hitungan populasi penuh** lewat regex nama berkas atas seluruh 1.597 citra,
bukan hasil sampel. Hanya **1 dari 4** yang kebetulan jatuh di sampel 60 — laju sampelnya
**1,7 %**, bukan 6,7 %, sehingga ekstrapolasi ~107 tidak berlaku.

**Keputusan mengaudit tetap benar**, tetapi alasannya berbeda: regex hanya menangkap render
yang namanya **menyebut** simulator/game. Render bernama netral tidak tertangkap, dan
jumlahnya itulah yang belum diketahui — bukan "sekitar 107".

Terbukti benar: `hqdefault-1` memuat logo permainan tanpa namanya menyebut apa pun (§5).

---

## 3. Tinjauan skrip `audit_web_katalog.py`

Skrip yang disertakan saya tinjau sebelum dijalankan. **Dua bug nyata, satu dugaan saya
sendiri yang salah.**

### 3.1 🔴 pHash membuang 8 koefisien, bukan 1

```python
med = np.median(d[1:].flatten())   # d berbentuk 8x8 -> d[1:] membuang seluruh BARIS pertama
```

Yang dimaksud adalah membuang koefisien DC saja. `d[1:]` membuang 8 koefisien.
**Terukur: 30 dari 40 citra menghasilkan hash berbeda** dari `uji_phash.py`, sehingga hasilnya
tidak sebanding dengan Fase 2 maupun `audit_watermark_frame.py`.

Diperbaiki menjadi `v = d.flatten(); med = np.median(v[1:])` — konsisten ketiga skrip.

### 3.2 🔴 *Bucketing* melewatkan 55,6 % pasangan

Klasterisasi mem-*bucket* pada potongan 16 bit, sehingga dua citra hanya dibandingkan bila
berbagi 16 bit yang sama persis. Pada ambang Hamming 12 perbedaan tersebar, jadi syarat itu
terlalu ketat. Terukur pada 1.597 citra:

| Ambang | Pasangan sebenarnya | Tertangkap *bucketing* | Terlewat |
|---|---|---|---|
| 5 | 50 | 47 | 3 (6,0 %) |
| **12** (yang dipakai) | **178** | **79** | **99 (55,6 %)** |

Akibatnya klaster terpecah, dan — ini yang berbahaya — **klaster tercemar dapat memiliki
perwakilan yang tampak bersih**. Diganti perbandingan penuh tervektor: untuk 1.597 citra hanya
1,27 juta operasi, selesai dalam hitungan detik.

### 3.3 Dugaan saya yang salah

Saya menduga `rglob()` per citra adalah masalah kinerja. **Diukur: 5 ms per panggilan, total
±8 detik.** Bukan masalah. Saya tetap menggantinya dengan indeks sekali jalan karena lebih
rapi, bukan karena lambat — dan saya catat supaya klaim itu tidak beredar sebagai temuan.

Antarmuka, nama berkas keluaran, dan kosakata status dipertahankan persis seperti aslinya.

---

## 4. Heuristik yang saya buat dan GAGAL

Untuk menghindari memeriksa 1.452 klaster secara buta, saya membangun pemeringkat kandidat
render (`skor_render.py`): foto kamera membawa derau sensor, render tidak, jadi sisa frekuensi
tinggi pada wilayah datar seharusnya memisahkan keduanya.

**Divalidasi pada 4 render yang sudah diketahui — dan gagal:**

| Render diketahui | Peringkat | Persentil |
|---|---|---|
| `download-game-simulasi…` (2 berkas) | 802, 803 dari 1.597 | 50 % |
| `UKTS_Bus_Simulator…` | 1.368 | 86 % |
| `bus-simulator-fi-1` | 1.395 | 87 % |

Sebaran skornya degenerat: min 0,0000, **median 0,0000**. Sebabnya kuantisasi JPEG sudah
meratakan wilayah datar, sehingga `|I − median3x3(I)|` menjadi nol persis pada foto maupun
render. Premisnya runtuh setelah kompresi *lossy*.

**Tidak saya pakai.** Skripnya disimpan dengan banner kegagalan supaya tidak ditemukan ulang.
Validasi itulah gunanya — kalau saya tidak mengujinya pada positif yang diketahui, saya akan
menyerahkan daftar kerja yang menyesatkan.

---

## 5. K1 — audit `web_katalog`

### 5.1 Split TEST: tuntas, dan K3 terjawab

145 citra `web_katalog` di split test diperiksa **satu per satu** (6 lembar, 25 per lembar,
390 px).

- **Nol render permainan**
- **Nol citra bukan-lalu-lintas**
- → **K3 (jalankan ulang tiga subset) TIDAK diperlukan.** Angka hasil tidak terpengaruh.

### 5.2 Kategori provenans yang belum pernah teridentifikasi

**14 thumbnail YouTube** (`hqdefault-*`, `maxresdefault-*`) — **seluruhnya di split test**,
memuat branding kanal, bilah *letterbox*, atau teks judul. Kanal yang terbaca: CCTV Kuamang
OFFICIAL, #CCTV Kalirungga, VERDIANSYAH, Mr Zyyy, Sugiono totti.

Satu di antaranya (`hqdefault-1`) memuat logo **"Grand Theft Auto San Andreas"**. Saya periksa
pada resolusi asli: **pikselnya foto nyata** bus Damri dengan logo permainan ditempelkan —
thumbnail video mod, bukan render. Persoalannya **atribusi**, bukan keabsahan konstruk.

Ini persis yang koreksi premis §2 prediksi: nama berkasnya `hqdefault-1`, tidak menyebut
apa pun tentang permainan.

### 5.3 Tanda air situs jauh lebih umum dari perkiraan

Perkiraan dari sampel 60 adalah 5 %. Pada pemeriksaan menyeluruh split test, tanda air situs
penjual/kanal/fotografer **umum dijumpai**. Yang terbaca: TJAP BOEMEL · AUTO VIT · OTO BLITZ ·
ercal trucks · KABAR JOMBANG.COM · CaribbeanEquipmentTraders.com · Dot Sticker · Autonetmagz.com ·
JIBI Photo · @FernwoodCommercials · autokid · Pickles · KEL-BERG · SURYAMALANG · KOMPAS.com ·
BUS TV INDO · rumah lelang armada · satu promo pemasok Tiongkok ber-WhatsApp.

### 5.4 Train/valid: 3 dari 21 lembar

192 dari 1.319 klaster diperiksa. **Nol render baru** di luar 4 yang sudah diketahui.
Pelacak resumable: [`../anotasi_web/KEMAJUAN_AUDIT.md`](../anotasi_web/KEMAJUAN_AUDIT.md).

⚠️ **Kejujuran pencatatan:** pada pass split test saya mencatat temuan **agregat**, bukan
status per klaster. Untuk naskah itu memadai — yang menentukan K3 adalah ada/tidaknya render
di test, dan jawabannya nol. Untuk **angka lisensi yang pasti**, status per klaster masih
harus diisi.

---

## 6. K4 — bias katalog per sel, hasilnya menguntungkan

Diperluas dari 1 sel ke seluruh 24 sel (`eval_out/bias_katalog_sel.csv`).

**Cemaran terkonsentrasi di tepat tiga sel, seluruhnya *big-vehicle*:**

| Sel | n_GT | dari katalog | % |
|---|---|---|---|
| `size/large/big-vehicle` | 192 | 157 | **81,8 %** |
| `density/sparse/big-vehicle` | 261 | 174 | **66,7 %** |
| `occlusion/no/big-vehicle` | 303 | 175 | **57,8 %** |

**Sel yang menopang klaim K4 justru nyaris bersih:**

| Sel | % katalog |
|---|---|
| `occlusion/partial/two-wheeler` | 2,6 % |
| `occlusion/partial/car` | 1,9 % |
| `size/small/car` | 1,3 % |
| `size/small/pedestrian` | 1,2 % |
| `occlusion/partial/pedestrian` | 0,6 % |
| `size/small/two-wheeler` | **0,0 %** |
| **rata-rata** | **1,3 %** |

Rata-rata 24 sel: 11,0 %.

**Artinya klaim RQ4 justru bersandar pada citra CCTV**, sementara sel yang didominasi katalog
adalah sel yang gugur dari pengujian atau paling tidak relevan bagi klaim itu. Ini memperkuat
naskah, persis seperti yang pembimbing perkirakan.

---

## 7. Perubahan naskah

Keluaran: **`JUTIF_Paper_DA-YOLO26_Firdaus_REVISI2.docx`**

| Butir | Yang dikerjakan |
|---|---|
| **Bagian 1** | Narasi tren p **dihapus**, diganti rumusan pembimbing yang melaporkan **ketidaksepakatan dua analisis sebagai temuan** |
| **K2** | Bootstrap 1.000 → **10.000 × 3 seed** di METHOD; catatan di bawah Tabel 4 memuat rentang lintas seed (V8vsV1 batas bawah +0,0035…+0,0216 pp; V8vsV5 frac 1,000 ketiganya; V4vsV1 memuat nol ketiganya) |
| **K2 lanjutan** | **Ambiguitas ditutup:** Table 8 dinyatakan eksplisit memakai 1.000 resample, dibedakan dari Table 4 — tanpa itu pembaca akan menyangka keduanya sama |
| **D-G** | Komposisi validasi **beserta dampaknya pada penalaan**: 50 citra Oculus (7,4 %) tanpa kendaraan + 34 bertanda air + 2 render; validasi inilah yang dipakai *grid search* α/σ **dan** *early stopping* |
| **D-H** | Tanda air situs penjual dipisahkan kategorinya dari stok dan kanal |
| **D-I** | 381 potongan satu-kendaraan dipindah ke **RESULT sebagai penjelasan** sebaran sel, plus rincian per sel §6 |
| **Temuan baru** | Paragraf hasil audit split uji: nol render, nol bukan-lalu-lintas, 14 thumbnail platform video |

### Verifikasi naskah

| Butir | Hasil |
|---|---|
| Penyebutan "1.000 resample" tersisa | **0** |
| Abstrak | **249 kata** (batas JUTIF 250) |
| Narasi monoton lama | **hilang** |
| Rumusan pembimbing hadir | ✅ |
| Angka 82 % · 7,4 % · 1,3 % · 81,8 % | ✅ semuanya |
| Kalimat "no rendered frames and no images…" | ✅ |
| Frasa terlarang (*self-collected*, *data primer*, *one city*) | **0** |

---

## 8. K6 — integritas

| Butir | Hasil |
|---|---|
| Dataset | **3.389 berkas — 0 hilang / 0 tambah / 0 berubah** |
| Bobot | **8 `best.pt` — 0 berubah** (bukti tidak ada pelatihan ulang) |
| `JUTIF_..._FINAL.docx` (asli) | md5 identik dengan `beku_20260813/` — **tidak tersentuh** |
| `TESIS_BAB1-3_REVISI_SIDANG_v8.docx` | md5 identik — **tidak tersentuh** |
| `TESIS_BAB4-5.docx` | md5 identik — **tidak tersentuh** |

Rantai naskah jurnal: `FINAL` (asli, utuh) → `REVISI_PROVENANS` (keputusan I) →
`REVISI2` (keputusan II).

---

## 9. `.gitignore` — 1K changes

`anotasi_web/` memuat **1.543 citra turunan / 223 MB** (1.452 potongan resolusi asli + lembar
kontak) — itulah penyebabnya. Seluruhnya dibangkitkan ulang oleh satu perintah.

Pola abaikan ditambahkan; bukti keputusan (`.csv`/`.md`, 257 KB) tetap ter-*track*.

**Hasil: 1.556 berkas → 13.**

---

## 10. Kekeliruan saya pada sesi ini

| # | Kekeliruan | Koreksi |
|---|---|---|
| 1 | Menduga `rglob()` masalah kinerja | Diukur: 5 ms, bukan masalah. Klaim ditarik |
| 2 | Heuristik skor render | **Gagal validasinya sendiri**; tidak dipakai, kegagalannya didokumentasikan |
| 3 | Menyerahkan audit 1.319 klaster kepada Naufal | **Keliru** — itu bukan pekerjaan yang menuntut dia. Diambil kembali |
| 4 | Tidak mencatat status per klaster pada pass split test | Diakui di pelacak; agregatnya memadai untuk naskah, tidak untuk angka lisensi |

---

## 11. Sisa pekerjaan

### Hanya Naufal

| # | Tindakan | Memblokir |
|---|---|---|
| 1 | **Batasi visibilitas Roboflow** — butuh akses akun. Panduan langkah demi langkah: [`../PANDUAN_TINDAKAN_NAUFAL.md`](../PANDUAN_TINDAKAN_NAUFAL.md) Bagian A | **YA** |
| 2 | Kirim surel Dr. Sandfreni (dua pertanyaan sudah di atas) | butir 8 |
| 3 | Buka `REVISI2.docx` di Word, cetak uji Figure 9, segarkan tata letak | ya, di akhir |

### Saya

| # | Tindakan | Status |
|---|---|---|
| 4 | Audit 18 lembar sisa (1.127 klaster train/valid) | 🔄 berlanjut, pelacak resumable |
| 5 | K5 audit EZVIZ pada 1.179 citra rekam-layar | ⬜ belum, tidak memblokir |
| 6 | Daftar periksa JUTIF penuh (proporsi bagian, monotonisitas sitasi, rasio 81,2 %) | ⬜ belum |

### Menunggu Dr. Sandfreni

Kebijakan integritas publikasi atas 315 citra, dan prosedur koreksi tesis yang telah
disidangkan. **Naskah tesis belum disentuh** — md5 membuktikannya. Cakupan nyata bila kelak
diizinkan: 2/1/4 paragraf per dokumen, dan `y26_revisi_bab13.py` adalah pola yang sudah
terbukti mempertahankan 121 *field* Mendeley.

---

## 12. Artefak sesi ini

**Skrip baru:** `audit_web_katalog.py` (diperbaiki 3 hal) · `skor_render.py` (gagal,
disimpan sebagai catatan negatif) · `revisi_jurnal_keputusan2.py` ·
`sisir_klaim_provenans.py`

**Data:** `anotasi_web/klaster_web.csv` (1.452 klaster) · `TEMPLAT_ANOTASI.csv` ·
`kandidat_render.csv` · `eval_out/bias_katalog_sel.csv` (24 sel)

**Dokumen:** `JUTIF_Paper_DA-YOLO26_Firdaus_REVISI2.docx` · `PANDUAN_TINDAKAN_NAUFAL.md` ·
`anotasi_web/KEMAJUAN_AUDIT.md` · dokumen ini

**Diperbarui:** `.gitignore` · `logs/sesi.log` · `catatan_keputusan.md`
