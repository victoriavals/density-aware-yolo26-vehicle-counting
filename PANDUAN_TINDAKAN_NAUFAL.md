# Panduan langkah demi langkah — dua tindakan yang hanya dapat Anda lakukan

> Dari seluruh sisa pekerjaan, **hanya dua** yang benar-benar menuntut Anda. Sisanya
> (audit 1.319 klaster `web_katalog` dan audit EZVIZ) dapat saya kerjakan, dan saya keliru
> ketika sempat menyerahkannya kepada Anda.
>
> Butir A memblokir pengiriman artikel (gerbang akhir butir 6). Kerjakan lebih dulu.

---

## A. Batasi visibilitas dataset di Roboflow

**Mengapa mendesak.** Naskah merujuk dataset ini. Penyunting atau penelaah dapat mengekliknya
kapan saja, dan bila dibuka sekarang mereka melihat **315 citra bertanda air pihak ketiga**
sebelum sempat membaca pernyataan lisensi Anda di bagian keterbatasan. Ini tindakan
pengamanan, bukan keputusan yang perlu didiskusikan.

### A.0 Ketahui dulu: ada dua kemungkinan lokasi

Catatan proyek (CLAUDE.md §15) mencatat **diskrepansi yang belum pernah diselesaikan**:

| Sumber | Alamat |
|---|---|
| Sitasi naskah [17]/[38] | `universe.roboflow.com/naufalfirdaus/traffic-merged-qke0k-3yyyo` |
| Tempat ekspor sebenarnya diambil | `sahabats-workspace/traffic-merged-qke0k-3yyyo-nkdvt` |

**Periksa keduanya.** Bisa jadi satu proyek dengan dua tautan, bisa jadi dua salinan. Bila
ternyata dua, keduanya harus ditangani, dan sitasi naskah perlu diarahkan ke yang benar.

### A.1 Masuk dan temukan proyeknya

1. Buka `https://app.roboflow.com` lalu masuk dengan akun Anda.
2. Periksa **pemilih workspace** di kiri atas — akun Anda mungkin punya lebih dari satu
   (`naufalfirdaus` dan `sahabats-workspace`). Buka satu per satu.
3. Cari proyek bernama `traffic-merged` (varian nama: `traffic-merged-qke0k-3yyyo`).
4. Catat: berapa **versi** yang ada, dan mana yang **terpublikasi ke Universe**.

### A.2 Pilih tindakan

Tiga pilihan, dengan konsekuensi berbeda. **Rekomendasi saya: opsi 2.**

| Opsi | Tindakan | Untung | Rugi |
|---|---|---|---|
| 1 | Jadikan **private** seluruhnya | Paling cepat, paparan langsung berhenti | Sitasi [17]/[38] menjadi tautan mati; penelaah tidak dapat memeriksa data |
| **2** | **Private sekarang**, lalu terbitkan ulang versi bersih tanpa 315 citra | Paparan berhenti seketika; reproduktibilitas tetap terjaga | Butuh satu langkah lagi menyusul |
| 3 | Biarkan publik, ganti langsung dengan versi bersih | Tautan tak pernah mati | Selama proses unggah, citra bermasalah masih terlihat |

Opsi 2 menghentikan paparan hari ini tanpa mengorbankan reproduktibilitas, dan versi
bersihnya dapat menyusul setelah Dr. Sandfreni menjawab.

### A.3 Menjadikan private

1. Buka proyeknya → tab **Settings** (ikon gerigi).
2. Cari bagian **Project Visibility** atau **Publish to Universe**.
3. Ubah dari **Public** menjadi **Private**.
4. Bila ada tombol **Unpublish from Universe** yang terpisah, tekan juga.
5. Ulangi untuk workspace kedua bila proyeknya memang ada dua.

### A.4 Verifikasi — jangan lewati langkah ini

Pengaturan visibilitas kadang tidak langsung berlaku pada halaman Universe.

1. Buka **jendela penyamaran/incognito** (Ctrl+Shift+N), atau peramban lain tempat Anda
   tidak masuk akun.
2. Buka `https://universe.roboflow.com/naufalfirdaus/traffic-merged-qke0k-3yyyo`.
3. **Kriteria lolos:** halaman menampilkan 404 atau "not found", **bukan** galeri citra.
4. Ulangi untuk alamat `sahabats-workspace/...` bila ada.
5. Simpan tangkapan layarnya. Itu bukti tanggal Anda bertindak, dan berguna bila kelak
   ditanya penyunting.

### A.5 Daftar 315 citra untuk versi bersih (bila memilih opsi 2)

Daftarnya sudah tersedia, tidak perlu Anda susun ulang:

```
anotasi_provenans/citra_berwatermark_HIPOTESIS.txt   67 citra night-traffic-12/13
anotasi_provenans/watermark_frame_tambahan.csv      248 citra frame_* (Mekkah, Seoul, NL Cycling)
```

Bila nanti versi bersih dibuat, katakan kepada saya — saya dapat membangkitkan berkas
gabungan berisi 315 nama berkas itu dalam format apa pun yang diminta Roboflow.

⚠️ **Jangan menghapus citra dari `dataset/` lokal.** Bobot model sudah terlatih dengannya;
menghapusnya hanya menghilangkan jejak tanpa mengubah bobot, dan akan merusak manifes
integritas yang membuktikan tidak ada pelatihan ulang.

---

## B. Kirim surel kepada Dr. Sandfreni

**Mengapa perlu.** Pembimbing teknis sudah memutuskan seluruh hal metodologis dan
penyuntingan. Yang tersisa dua, dan keduanya kewenangan program studi, bukan kewenangan
penelaah mana pun.

### B.1 Ambil drafnya

Berkas: [`hasil_bab4_5/SUREL_PEMBIMBING_PROVENANS.md`](hasil_bab4_5/SUREL_PEMBIMBING_PROVENANS.md)

Draf itu sudah disusun ulang sesuai permintaan pembimbing: **dua pertanyaan berada di bagian
atas**, dan cakupannya dipersempit dari sepuluh hal menjadi dua.

### B.2 Sunting tiga hal sebelum mengirim

1. **Blok bersyarat tentang Roboflow.** Di dalam draf ada blok peringatan berisi kalimat
   *"Visibilitas dataset di Roboflow juga sudah saya batasi."* Sertakan kalimat itu **hanya
   bila Anda sudah menyelesaikan Bagian A**; bila belum, hapus. Hapus juga blok
   peringatannya sendiri — itu catatan untuk Anda, bukan bagian surat.
2. **Sapaan dan penutup.** Sesuaikan dengan kebiasaan Anda berkorespondensi dengan beliau.
3. **Lampiran.** Saya sarankan melampirkan dua berkas saja, jangan lebih:
   - `hasil_bab4_5/VERIFIKASI_PROVENANS_FASE0-4.md` — bukti dan angka lengkap
   - `catatan_keputusan.md` — 16 keputusan beserta alasannya

   Bila beliau ingin lebih dalam, `hasil_bab4_5/LAPORAN_SESI_13AGU2026.md` memuat semuanya.

### B.3 Dua pertanyaan yang dijawab beliau

Supaya Anda tahu persis apa yang sedang ditunggu:

1. Apakah **mempertahankan bobot** disertai pernyataan lisensi terbuka dapat diterima menurut
   kebijakan integritas publikasi program studi.
2. Apakah **tesis yang telah disidangkan** perlu diajukan koreksi formal, dan melalui
   prosedur apa.

### B.4 Yang tidak perlu Anda tunggu

Butir 1 sampai 7 gerbang akhir **tidak menunggu jawaban beliau**. Hanya butir 8. Jadi kirim
suratnya, lalu lanjutkan pekerjaan lain sambil menunggu.

---

## C. Bila Anda ingin ikut mengerjakan audit (opsional)

Audit 1.319 klaster sisa **dapat saya kerjakan** dan sedang saya kerjakan. Tetapi Anda lebih
cepat daripada saya untuk pekerjaan mata semacam ini, dan Anda mengenal datanya. Bila ingin
mengerjakannya paralel — **beri tahu saya lebih dulu supaya kita tidak bekerja dua kali.**

Prosedurnya:

1. Buka `anotasi_web/lembar_kontak_*.jpg` berurutan (37 lembar, 36 perwakilan per lembar).
   Label merah di tiap sel adalah **id klaster** dan **jumlah anggotanya**.
2. Untuk klaster yang mencurigakan, buka potongan resolusi aslinya di
   `anotasi_web/crop/W###.jpg`. **Ini penting** — tanda air berkontras rendah tidak terlihat
   pada miniatur. Itu kekeliruan yang saya buat sendiri pada klip Seoul dan harus diulangi
   pemeriksaannya.
3. Isi kolom `status` pada `anotasi_web/TEMPLAT_ANOTASI.csv`. Nilai yang sah:

   | status | artinya |
   |---|---|
   | `bersih` | foto biasa, tanpa tanda air pihak ketiga |
   | `watermark_stok` | tanda air pustaka stok (Shutterstock, Dreamstime, dll.) |
   | `watermark_penjual` | tanda air situs penjual/kanal/fotografer |
   | `render_permainan` | citra buatan mesin, bukan foto |
   | `bukan_lalu_lintas` | bukan kendaraan/jalan sama sekali |

4. Setelah semua terisi:

   ```bash
   python audit_web_katalog.py --rekap anotasi_web/TEMPLAT_ANOTASI.csv
   ```

   Perintah itu merekap per split dan **menyatakan sendiri** apakah K3 (jalankan ulang tiga
   subset) diperlukan. Ia akan menolak selesai bila masih ada klaster berstatus kosong.

**Catatan yang sudah pasti:** untuk split **test** jawabannya sudah diketahui — 145 citra
diperiksa satu per satu, hasilnya **nol render dan nol citra bukan-lalu-lintas**, jadi
**K3 tidak diperlukan**. Sisa audit ini menyangkut angka lisensi dan pernyataan komposisi,
bukan angka hasil.

---

## Ringkasan urutan

| # | Tindakan | Siapa | Memblokir? |
|---|---|---|---|
| 1 | Batasi visibilitas Roboflow + verifikasi incognito | **Anda** | **YA** |
| 2 | Kirim surel Dr. Sandfreni | **Anda** | butir 8 saja |
| 3 | Audit 1.319 klaster sisa | **saya** | ya, sedang dikerjakan |
| 4 | K5 audit EZVIZ | **saya** | tidak |
| 5 | Buka naskah revisi di Word, cetak uji Figure 9, segarkan tata letak | **Anda** | ya, di akhir |
