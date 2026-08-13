# Audit provenans dataset `traffic-merged` — temuan 13 Agu 2026

> ## ⚠️ SEBAGIAN ANGKA DI BAWAH SUDAH DIKOREKSI
>
> Dokumen ini adalah **audit awal berbasis pola nama berkas**, ditulis sebagai *hipotesis*.
> Verifikasi mandiri (FASE 0–4, 13 Agu 2026) menguji hipotesis itu dan sebagian **gugur**.
> **Angka yang berlaku ada di [`VERIFIKASI_PROVENANS_FASE0-4.md`](VERIFIKASI_PROVENANS_FASE0-4.md).**
>
> | Yang dikoreksi | Dokumen ini | Terverifikasi |
> |---|---|---|
> | Citra ber-tanda-air | 67 | **315** (248 tambahan, **semuanya di `train`**) |
> | CCTV asli | 1.792 (52,9 %) | **1.427 (42,1 %)** |
> | Lokasi CCTV | Yogyakarta + Demak | **+ Banjarmasin** (kota ketiga) |
> | Rekaman asing | tidak diketahui | **Seoul · Mekkah · New York · Belanda** |
> | Kebocoran near-duplicate | dugaan (§2.4 butir 3) | **terbukti: 3 pasangan pHash jarak 0, 1 di `train`↔`test`** |
> | Pemegang hak | Shutterstock | Shutterstock **+ kanal "NL Cycling"** |
>
> Yang **tetap berlaku**: keberadaan tanda air Shutterstock, klaim "Jakarta" tidak
> didukung bukti, klaim "kamera dipasang peneliti" tidak didukung bukti, dan 1.597 citra
> (47,1 %) bukan CCTV. Kabar baiknya — **split evaluasi tidak berubah**: 248 citra
> ber-tanda-air tambahan seluruhnya di `train`, sehingga `valid`/`test` tetap 34/33 dan
> angka BAB 4 tidak terpengaruh kurang-hitung ini.
>
> Dokumen ini **sengaja tidak dihapus**: ia merekam bagaimana temuan muncul (aturan §12.8).

> Ditemukan **tidak sengaja** saat memilih bingkai untuk gambar jurnal: bingkai uji terpadat
> (`night-traffic-9_mp4-0055`) ternyata memuat **tanda air "shutterstock"** di tengah citra.
> Penelusuran lanjutan atas seluruh 3.389 citra memunculkan tiga persoalan yang **harus
> diputuskan sebelum artikel dikirim**. Dokumen ini menyajikan bukti, bukan tuduhan —
> beberapa temuan mungkin punya penjelasan yang saya tidak ketahui.

---

## 1. Komposisi sumber sebenarnya (3.389 citra, seluruh split)

Diklasifikasikan dari pola nama berkas + pembacaan overlay pada citra:

| Kategori sumber | train | valid | test | TOTAL | % |
|---|---|---|---|---|---|
| **Citra web/katalog — BUKAN CCTV** | 1.124 | 328 | 145 | **1.597** | **47,1 %** |
| CCTV: rekam-layar `frame_*` | 1.198 | 252 | 27 | 1.477 | 43,6 % |
| CCTV: ATCS Yogyakarta (`night-traffic-5/8/9`) | 0 | 65 | 96 | 161 | 4,8 % |
| CCTV: Dishub Demak (`Recording 2025-08-25 *`) | 50 | 0 | 37 | 87 | 2,6 % |
| **CCTV: rekaman stok ber-tanda-air Shutterstock** (`night-traffic-12/13`) | 0 | 34 | 33 | **67** | **2,0 %** |
| **Jumlah** | | | | **3.389** | 100 % |

→ Hanya **1.792 citra (52,9 %)** benar-benar citra CCTV. **1.597 citra (47,1 %) bukan CCTV.**

---

## 2. Tiga persoalan

### 2.1 🔴 Tanda air Shutterstock pada 67 citra (hak cipta)

`night-traffic-12` (34 citra, split **valid**) dan `night-traffic-13` (33 citra, split **test**)
berasal dari rekaman stok berbayar dan **masih memuat tanda air "shutterstock"** yang terlihat
jelas di tengah bingkai.

Akibat langsung:
- **Tidak satu pun dari 67 citra ini boleh muncul pada gambar artikel/tesis.** Menerbitkan
  citra ber-tanda-air adalah pelanggaran hak cipta yang akan langsung terlihat penyunting.
- Keberadaannya di dataset yang **dipublikasikan di Roboflow** ([17]) adalah persoalan lisensi
  tersendiri, terlepas dari artikel.
- Keduanya ada di split **evaluasi** (valid & test), jadi ikut menyumbang angka metrik yang
  dilaporkan. Bila 67 citra ini dikeluarkan, seluruh angka BAB 4 berubah — perlu dipertimbangkan
  apakah itu langkah yang diambil, atau cukup dinyatakan sebagai keterbatasan lisensi.

⚠️ Bingkai uji **terpadat** (`night-traffic-9_mp4-0055`, 30 objek) semula saya pilih untuk gambar
jurnal justru berasal dari kelompok ini — inilah cara temuan ini muncul. Gambar sudah diganti
ke bingkai bersih.

### 2.2 🔴 Lokasi bukan Jakarta

Naskah (§5 SSOT, dan BAB 1/3) menyatakan dataset adalah **"citra CCTV lalu lintas Jakarta"**.
Overlay yang terbaca pada citra menunjukkan lain — teks berikut saya baca setelah perbesaran 3×:

| Sumber | Teks overlay terbaca | Lokasi sebenarnya |
|---|---|---|
| `night-traffic-5` | "SIMPANG TERBAN U. BARAT / Koneksi Didukung CSR Citranet" + lambang DIY | **Yogyakarta** |
| `night-traffic-8` | "PINGIT" + "Koneksi Didukung CSR" + lambang DIY | **Yogyakarta** |
| `night-traffic-9` | "Nol Km – Timur" + lambang DIY | **Yogyakarta** (Titik Nol Km) |
| `frame_*` | "S3 Pasar Telo U. Selatan" | **Yogyakarta** |
| `Recording …113001` | "DISHUB DEMAK / ARAH SEMARANG" | **Demak, Jawa Tengah** |
| `Recording …114243` | "TL TRENGGULI FIXED ARAH KUDUS / DISHUB DEMAK" | **Demak → Kudus, Jawa Tengah** |

Jadi **seluruh sumber CCTV yang dapat diidentifikasi berada di Yogyakarta dan Demak**, bukan
Jakarta. Satu-satunya rekaman yang *secara visual* menyerupai Jakarta (ruas mirip Sudirman/
Semanggi pada `night-traffic-13`) justru adalah **rekaman stok Shutterstock** — bukan rekaman
sendiri.

Ini menyentuh klaim inti: judul/latar tesis membangun urgensi pada lalu lintas heterogen padat
**Jakarta**. Klaim itu perlu dikoreksi menjadi lokasi yang sebenarnya, atau dibatasi menjadi
"lalu lintas heterogen padat di Indonesia" dengan penyebutan kota yang tepat.

### 2.3 🔴 "Data primer, kamera dipasang peneliti" tidak didukung bukti

§5 SSOT menyatakan "data primer, **mayoritas kamera dipasang peneliti**". Yang saya temukan:

- Setiap sumber CCTV membawa **overlay lembaga pihak ketiga** (ATCS/CSR Citranet + lambang
  Pemda DIY; DISHUB DEMAK; "CSR DEMAK CENTRAL DATA") — penanda umpan CCTV publik/pemerintah,
  bukan kamera milik sendiri.
- Kelompok `frame_*` (1.477 citra, terbesar di antara sumber CCTV) memuat artefak
  **"Activate Windows"** di sudut kanan bawah → citra diperoleh dengan **merekam layar** dari
  penampil CCTV, bukan mengambil dari kamera sendiri.
- Berkas `Recording 2025-08-25 HHMMSS.mp4` juga khas nama keluaran perekam layar.

Memakai umpan ATCS publik itu **sah** — asalkan disebut apa adanya dan disitasi/diizinkan.
Yang tidak dapat dipertahankan adalah kalimat "kamera dipasang peneliti". Bila memang ada
kerja sama resmi dengan Dishub Demak (indikasi "CSR DEMAK CENTRAL DATA"), itu justru layak
disebut eksplisit sebagai izin akses — lebih kuat dan jujur.

### 2.4 🟠 47,1 % citra bukan CCTV sama sekali

Kelompok terbesar (1.597 citra) adalah gambar web/katalog. Contoh nama berkas apa adanya:

```
chiangmai-thailand-march-mitsubishi-…      ← foto stok THAILAND
Damri-2BPontianak-2BSingkawang             ← Pontianak/Singkawang, Kalimantan Barat
jadwal-bus-damri-bandara-supadio-ke-…      ← gambar artikel jadwal bus
banjir-jakarta-bus-damri-rute-bandar…      ← foto berita banjir
2005-mitsubishi-fuso-fm2 · Cutting-Sticker-Truk-Can · BUS-PATAS-INDONESIA
Image-3-BusDriverJade-Y717-TOH-1024x       ← bus pelat non-Indonesia
gol2_14 · gol3_17 · gol5_42 · 2_117 · T24 · 20130712092311711
```

Dugaan saya: ini ditambahkan untuk menambal kelas **big-vehicle** yang minoritas (1.916 instans).
Konsekuensi yang perlu dipertimbangkan:

1. Framing "dataset CCTV" menjadi tidak tepat untuk hampir separuh data.
2. Citra katalog/marketing adalah **foto tunggal kendaraan dari dekat** — distribusi ukuran,
   sudut, oklusi, dan densitasnya sangat berbeda dari CCTV. Ini kemungkinan besar **membiaskan
   evaluasi terstratifikasi** (dimensi ukuran/oklusi/densitas) yang menjadi jawaban RQ4, dan
   membantu menjelaskan mengapa sel `big-vehicle/size/small` (n=17) dan
   `big-vehicle/occlusion/partial` (n=27) berperilaku ganjil serta gugur oleh `MIN_CELL_GT=30`.
3. **Risiko kebocoran sisa:** verifikasi split (P2) memeriksa duplikat **md5 identik** dan grup
   kamera×adegan×sesi. Gambar web hasil scrape sering beredar dalam **beberapa ukuran/kompresi**
   sehingga md5-nya berbeda meski citranya sama — kebocoran semacam itu **tidak terdeteksi** oleh
   pemeriksaan yang ada. Perlu uji kemiripan perseptual (mis. pHash) bila ingin dipastikan.

---

## 3. Yang sudah saya lakukan

- Gambar jurnal **dialihkan** dari bingkai ber-tanda-air ke bingkai bersih
  (`night-traffic-5_mp4-0028`) → `hasil_bab4_5/15_gambar_jurnal/`.
- ⚠️ Bingkai bersih itu **masih** memuat overlay "SIMPANG TERBAN U. BARAT / CSR Citranet" yang
  menunjukkan Yogyakarta. Overlay **tidak** saya potong: memangkasnya untuk menyembunyikan lokasi
  akan memperburuk masalah §2.2, bukan menyelesaikannya. Keputusan ada pada Anda.

## 4. Keputusan yang saya butuhkan dari Anda

1. **Tanda air Shutterstock (67 citra di valid+test)** — dikeluarkan lalu seluruh evaluasi
   dijalankan ulang, atau dipertahankan dengan pernyataan lisensi eksplisit? Saya sarankan
   dibicarakan dengan pembimbing, karena ini menyangkut integritas publikasi.
2. **Klaim "Jakarta"** — dikoreksi menjadi Yogyakarta + Demak, atau dibuat umum?
3. **Klaim "kamera dipasang peneliti"** — diganti menjadi umpan ATCS/Dishub publik (+ izin bila
   ada)? Bila ada surat izin/kerja sama, itu justru memperkuat naskah.
4. **1.597 citra non-CCTV** — dinyatakan terbuka sebagai bagian komposisi dataset, dan
   implikasinya terhadap stratifikasi RQ4 dibahas sebagai keterbatasan?
5. **Uji pHash** untuk kebocoran near-duplicate — saya jalankan? (murah, ~beberapa menit)

Saya tidak mengubah dataset, split, bobot, hasil evaluasi, atau naskah apa pun sehubungan
temuan ini. Semuanya masih utuh sebagaimana sebelumnya.
