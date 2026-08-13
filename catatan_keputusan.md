# Catatan keputusan — perbaikan provenans dataset & naskah

> Templat Lampiran A rencana perbaikan provenans. Satu entri per keputusan.
> Penguji atau penyunting berhak menanyakan alasan setiap keputusan kemudian.
>
> Status: **DIPUTUSKAN** (sudah dijalankan) · **TERBUKA** (menunggu Naufal / pembimbing).

---

## Keputusan 1 — Cakupan manifest integritas: jpg + png
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Perintah Fase 0.2 rencana (`find … -name "*.jpg"`) menghasilkan 2.347 baris,
sedangkan kriteria lolosnya "3.389 baris" dan tindak lanjut bila gagal adalah "Berhenti".
**Pilihan:** (a) jalankan apa adanya lalu berhenti; (b) perbaiki pola menjadi jpg+png.
**Keputusan:** (b).
**Alasan:** dataset memuat 1.042 berkas `.png` (train 763 · valid 252 · test 27) yang sah
dan ikut dipakai pelatihan; ketidakcocokan 2.347 vs 3.389 adalah **alarm palsu**, bukan
tanda dataset berbeda. Berhenti karenanya akan membatalkan seluruh rencana tanpa sebab.
**Siapa yang memutuskan:** Claude (keputusan teknis, tidak menyentuh metodologi).
**Bukti:** `beku_20260813/md5_dataset.txt` = 3.389 baris; hitungan per split di
`VERIFIKASI_PROVENANS_FASE0-4.md` §5.1.
**Dampak pada naskah:** tidak ada.

---

## Keputusan 2 — Uji pHash mencakup png, dan tanpa memasang `imagehash`
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Sketsa Fase 2 memakai `rglob('*.jpg')`, dan `imagehash` belum terpasang.
**Pilihan:** (a) jalankan sketsa apa adanya; (b) jpg+png dan implementasi pHash sendiri.
**Keputusan:** (b) — pHash 64-bit via PIL + `scipy.fft.dct`.
**Alasan:** pola hanya-jpg melewatkan 30,7 % dataset dan sebarannya **tidak acak** —
963 dari 1.477 citra `frame_*` adalah `.png`, yaitu bingkai video berurutan, populasi
paling rawan near-duplicate `train`↔`valid`. Uji itu akan tampak bersih tanpa memeriksa
subjek berisiko tertingginya. Implementasi sendiri menghindari menambah dependensi pada
lingkungan yang sengaja dikunci (ultralytics 8.4.92).
**Siapa yang memutuskan:** Claude (keputusan teknis).
**Bukti:** `uji_phash.py`; `logs/fase2_phash.log`; tabel ekstensi per kategori di §5.2.
**Dampak pada naskah:** menaikkan kredibilitas kalimat hasil pHash.

---

## Keputusan 3 — Hasil uji pHash: 1 citra uji dikecualikan, `train` tidak disentuh
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN (pelaporan naskah: TERBUKA)
**Persoalan:** Uji pHash menemukan 3 pasangan berjarak Hamming 0 lintas split (md5 berbeda),
satu di antaranya `train`↔`test`.
**Pilihan:** (a) diamkan; (b) keluarkan citra sisi `test` dari evaluasi dan laporkan;
(c) hapus juga dari `train`.
**Keputusan:** (b).
**Alasan:** rencana Fase 2 menetapkan hasil **wajib dilaporkan apa pun hasilnya**, dan
menghapus dari `train` tidak sahih karena bobot sudah terlatih dengannya — menghapusnya
hanya menyembunyikan jejak tanpa mengubah bobot.
**Siapa yang memutuskan:** Claude, mengikuti aturan rencana Fase 2.
**Bukti:** `phash_pasangan.csv`; `phash_eksklusi_test.txt`; verifikasi visual pasangan
`Bus-Damri-1` (768×480 di `train` vs 800×500 di `test`, citra identik).
**Dampak pada naskah:** satu kalimat hasil pHash di Method/keterbatasan; jumlah citra uji
subset bersih menjadi 304 (bukan 305).

---

## Keputusan 4 — Audit tanda air diperluas ke seluruh `frame_*` lewat klaster pHash
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Kontrol acak Langkah 1.2 menemukan 2 dari 30 citra ber-tanda-air yang
**tidak** terdeteksi pola nama. Angka 67 karena itu tidak dapat dipertahankan, tetapi
memeriksa 1.477 citra `frame_*` satu per satu tidak praktis.
**Pilihan:** (a) laporkan 67 dengan catatan "mungkin lebih"; (b) sampel lebih besar;
(c) kelompokkan dengan pHash lalu periksa satu perwakilan per klaster.
**Keputusan:** (c) — 139 klaster, seluruhnya diperiksa mata.
**Alasan:** `frame_*` berisi bingkai video, sehingga citra satu klip nyaris identik dan
sifat perwakilan berlaku bagi seluruh anggota klaster; 1.477 citra terliput oleh 139
pemeriksaan. Melaporkan 67 sambil mengetahui angka itu salah tidak dapat dipertanggungjawabkan.
**Siapa yang memutuskan:** Claude (keputusan teknis pengukuran).
**Bukti:** `audit_watermark_frame.py`; `anotasi_provenans/klaster_frame.csv`;
`anotasi_provenans/watermark_frame_tambahan.csv` (233+15 citra); lembar kontak.
**Dampak pada naskah:** angka lisensi 67 → **315**; komposisi dataset diperbarui.

---

## Keputusan 5 — Verifikasi ulang memakai potongan resolusi asli, bukan miniatur
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Klip Seoul dinyatakan bersih pada lembar miniatur, tetapi ber-tanda-air
jelas pada resolusi asli — pemeriksaan miniatur punya **negatif palsu** pada adegan
terang dan sibuk (kontras tanda air rendah).
**Pilihan:** (a) pertahankan hasil miniatur; (b) periksa ulang dengan potongan tengah
resolusi asli.
**Keputusan:** (b), dan **seluruh klaster split evaluasi** diperiksa ulang dengan cara itu.
**Alasan:** kekeliruan ini ditemukan pada diri sendiri, bukan pada orang lain; membiarkannya
berarti melaporkan angka yang diketahui bias ke bawah. Prioritas diberikan pada `valid`/`test`
karena itulah yang menentukan angka BAB 4.
**Siapa yang memutuskan:** Claude.
**Bukti:** `audit_watermark_frame.lembar_crop`; `anotasi_provenans/crop_klaster_*.jpg`;
`crop_898x506_sisa.jpg` (3 citra K27 Seoul ber-tanda-air).
**Dampak pada naskah:** 15 citra Seoul masuk hitungan; **split evaluasi terkonfirmasi bersih**.

---

## Keputusan 6 — Fase 3 & 4 dijalankan dengan menyaring cache, bukan inferensi ulang
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Rencana Fase 3.1 meminta menyalin `test` ke `test_bersih/` lalu menjalankan
ulang evaluasi (taksiran 1–2 jam + 2–3 jam).
**Pilihan:** (a) salin folder + inferensi ulang; (b) saring `cache_V*.npz` menurut nama berkas.
**Keputusan:** (b).
**Alasan:** cache menyimpan prediksi mentah **per citra beserta nama berkasnya**, dan
hasilnya identik dengan inferensi ulang karena `collect_cache` me-*letterbox* tiap citra
sendiri-sendiri (deterministik, tanpa efek batch), proksi oklusi Pers. 3.1 hanya bergantung
pada GT dalam citra yang sama, dan tier densitas dihitung per citra. Lebih murah **dan**
lebih dapat dipertahankan: tidak ada sumber ragam baru. Dataset pun tidak perlu disentuh.
**Pengaman:** subset `penuh` dijadikan **kontrol reproduksi** — wajib mereproduksi
p = 0,5646 / 0,2076 / 0,0366; bila tidak, subset lain tidak boleh ditafsirkan. **Kontrol LOLOS.**
**Siapa yang memutuskan:** Claude (keputusan implementasi; metodologi tidak berubah —
`MIN_CELL_GT=30`, 3 hipotesis utama, bootstrap tataran citra tetap).
**Bukti:** `eval_subset.py`; `hasil_penuh/wilcoxon_ap5095.csv`; `logs/fase34_subset.log`.
**Dampak pada naskah:** tidak ada perubahan metodologi untuk dinyatakan.

---

## Keputusan 7 — Subset `cctv` berstatus uji ketegaran, BUKAN hasil utama
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIKUATKAN PEMBIMBING TEKNIS** (Bagian 3, 13 Agu 2026) — dan diperluas:
pola p monoton **boleh dinarasikan deskriptif** di DISCUSSIONS tanpa klaim signifikansi.
Sudah dijalankan; narasinya juga memuat peringatan bahwa selang bootstrap pada subset
terkecil melebar memuat nol, sehingga tren p tidak dapat dibaca sebagai bukti yang menguat.
**Persoalan:** Pada subset CCTV murni, bukti H1 paling kuat (p 0,0787 vs 0,5646 pada
subset penuh) dan H3 paling kuat (p 0,0229). Menggodanya adalah menjadikannya hasil utama.
**Pilihan:** (a) jadikan hasil utama; (b) laporkan ketiga subset berdampingan sebagai uji ketegaran.
**Keputusan:** (b).
**Alasan:** memilih subset yang memberi p terkecil **setelah** melihat hasilnya adalah
seleksi pada data uji — kekeliruan yang sama dengan yang sudah ditolak pada K4 saat
V4_a2.0 dibatalkan sebagai "konfigurasi terbaik". Subset penuh tetap hasil utama sampai
pembimbing memutuskan lain.
**Siapa yang memutuskan:** Claude; **layak ditinjau pembimbing**.
**Bukti:** `hasil_banding_subset.json`; §6.3 `VERIFIKASI_PROVENANS_FASE0-4.md`.
**Dampak pada naskah:** RESULT memuat tabel tiga subset; DISCUSSIONS boleh menyebut pola
monoton sebagai dukungan tafsir, tanpa klaim signifikansi baru.

---

## Keputusan 8 — Status 315 citra ber-tanda-air
**Tanggal:** 13 Agu 2026
**Status:** ⚖️ **TERBELAH.** Pembimbing teknis (Bagian 4) memutuskan **final** bahwa
*pertanyaan ilmiahnya sudah terjawab*: mempertahankan bobot + melaporkan uji ketegaran
adalah keputusan yang benar secara metodologis, dan pelatihan ulang 49 jam GPU tidak
diminta. Yang **tetap TERBUKA** hanyalah apakah posisi itu memadai menurut **kebijakan
integritas publikasi institusi** — kewenangan Dr. Sandfreni, bukan penelaah mana pun.
**Persoalan:** 315 citra (train 248 · valid 34 · test 33) memuat tanda air pihak ketiga
(Shutterstock; 4 di antaranya kanal "NL Cycling"). 248 di `train` berarti bobot sudah
terlatih dengannya; pembersihan menyeluruh menuntut pelatihan ulang 8 varian ≈ 49 jam GPU.
**Pilihan:** (a) keluarkan dari evaluasi lalu jadikan hasil bersih sebagai hasil utama;
(b) pertahankan dengan pernyataan lisensi terbuka + uji ketegaran (sudah tersedia);
(c) latih ulang seluruhnya.
**Rekomendasi Claude:** (b) — uji ketegaran sudah menunjukkan kesimpulan bertahan, dan
biaya (c) tidak sebanding. Keterikatan bobot pada data pelatihan dinyatakan terbuka.
**Yang harus diputuskan pembimbing:** apakah (b) memadai untuk integritas publikasi.
**Dampak pada naskah:** pernyataan lisensi di keterbatasan; kemungkinan penarikan/penggantian
versi dataset Roboflow [17]/[38].

---

## Keputusan 9 — Penulisan lokasi dataset
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN PEMBIMBING TEKNIS — opsi (a), sudah dijalankan pada naskah
jurnal** (`JUTIF_Paper_DA-YOLO26_Firdaus_REVISI_PROVENANS.docx`). Naskah **tesis ditahan**
sampai ada arahan prosedur Dr. Sandfreni. Alasan kewenangan: menuliskan sesuatu yang
diketahui keliru bukan pilihan yang tersedia, sehingga tidak ada kewenangan yang dilampaui.
**Persoalan:** Naskah menulis "Jakarta". Bukti overlay menunjukkan **Yogyakarta, Demak,
dan Banjarmasin**; ditambah rekaman stok dari **Seoul, Mekkah, New York, Belanda**.
**Pilihan:** (a) sebut tiga kota Indonesia apa adanya + nyatakan rekaman stok asing;
(b) generalisasi "lalu lintas heterogen Indonesia".
**Rekomendasi Claude:** (a) — tiga kota dengan karakter lalu lintas berbeda **memperkuat**
validitas eksternal, dan satu kalimat keterbatasan "satu kota" dapat dihapus.
**Dampak pada naskah:** Abstract (¶6), Introduction (¶10), Method 2.1 (¶21) naskah jurnal;
padanannya di tesis. ¶485 (sitasi [34] "Jakarta-Cikampek") **jangan diubah** — itu nama sumber.

---

## Keputusan 10 — Penulisan sumber data ("kamera dipasang peneliti")
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN PEMBIMBING TEKNIS — opsi (a), sudah dijalankan pada naskah
jurnal** (`JUTIF_Paper_DA-YOLO26_Firdaus_REVISI_PROVENANS.docx`). Naskah **tesis ditahan**
sampai ada arahan prosedur Dr. Sandfreni. Alasan kewenangan: menuliskan sesuatu yang
diketahui keliru bukan pilihan yang tersedia, sehingga tidak ada kewenangan yang dilampaui.
**Persoalan:** Klaim "data primer, mayoritas kamera dipasang peneliti" tidak didukung bukti:
overlay lembaga pihak ketiga, artefak "Activate Windows" + taskbar (rekam layar), logo EZVIZ.
**Pilihan:** (a) ganti menjadi umpan ATCS/Dishub publik + rekaman stok berlisensi + kamera
konsumen, sebutkan izin bila ada; (b) pertahankan.
**Rekomendasi Claude:** (a). Bila ada izin resmi (indikasi "CSR DEMAK CENTRAL DATA"),
menyebutnya eksplisit **memperkuat** naskah.
**Dampak pada naskah:** Method 2.1 + BAB 3 tesis; hapus frasa "self-collected" (1 kemunculan).

---

## Keputusan 11 — Perlakuan 1.597 citra bukan-CCTV + 365 rekaman stok
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN PEMBIMBING TEKNIS — opsi (a), sudah dijalankan pada naskah
jurnal** (`JUTIF_Paper_DA-YOLO26_Firdaus_REVISI_PROVENANS.docx`). Naskah **tesis ditahan**
sampai ada arahan prosedur Dr. Sandfreni. Alasan kewenangan: menuliskan sesuatu yang
diketahui keliru bukan pilihan yang tersedia, sehingga tidak ada kewenangan yang dilampaui.
**Persoalan:** 47,1 % dataset adalah citra web/katalog (kendaraan tunggal dari dekat) dan
10,8 % rekaman stok; CCTV Indonesia hanya 42,1 %. Ini membiaskan stratifikasi RQ4 —
terukur: 82 % objek sel `size/large/big-vehicle` split uji berasal dari citra web/katalog.
**Pilihan:** (a) nyatakan komposisi terbuka + laporkan uji ketegaran subset CCTV;
(b) sebut sebagai catatan kaki.
**Rekomendasi Claude:** (a) — uji ketegaran sudah tersedia dan hasilnya menguntungkan.
**Dampak pada naskah:** paragraf komposisi baru di Method 2.1; keterbatasan; RESULT subbab
pendamping.

---

## Keputusan 12 — Urutan: hitung dulu, baru kirim surel pembimbing
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN
**Persoalan:** Rencana menempatkan surel pembimbing di Fase 0.3, sebelum Fase 3–4 dijalankan.
**Keputusan:** jalankan Fase 3 + 4 lebih dulu (± 50 menit), lalu kirim surel berisi dampak terukur.
**Alasan:** hasilnya dibutuhkan pada **setiap** cabang keputusan pembimbing, dan surel yang
menyatakan "inilah dampak terukurnya — H3 tetap signifikan di ketiga subset" dijawab lebih
cepat dan lebih baik daripada "mohon arahan". Ini tidak mendahului keputusan siapa pun:
statusnya tetap uji ketegaran sampai pembimbing memutuskan.
**Siapa yang memutuskan:** Claude (usulan urutan; isi keputusan tetap pada pembimbing).
**Dampak pada naskah:** tidak ada.

---

## Keputusan 13 — Figure 9 memakai bingkai PENUH, bukan versi ter-*crop*
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN PEMBIMBING TEKNIS (D-A1), sudah dijalankan**
**Persoalan:** Tersedia dua keluaran: `gambar_banding_en.png` (bingkai utuh, overlay lokasi
terlihat) dan `gambar_zoom_en.png` (diperbesar pada wilayah terpadat).
**Keputusan:** versi **penuh**; versi *zoom* tidak dipakai.
**Alasan (pembimbing):** setelah lokasi dikoreksi, overlay "SIMPANG TERBAN U. BARAT" berubah
dari kontradiksi menjadi **bukti provenans**; efek pemotongan pada versi *zoom* kebetulan
menghilangkan penanda lokasi dari pandangan, dan menerbitkannya sesudah audit integritas
menciptakan kesan yang tidak perlu ditanggung; bingkai penuh juga memperlihatkan kepadatan
heterogen yang memotivasi penelitian.
**Bukti:** `word/media/image9.png` = 1.191 KB (identik `gambar_banding_en.png`; versi *zoom*
1.084 KB, jadi dapat dibedakan dari ukuran berkas).
**Dampak pada naskah:** Figure 9 + keterangan lima unsur; bingkai TIDAK diganti walau
memperlihatkan V8 dengan prediksi palsu **lebih banyak** daripada V1 — justru konsistensi
contoh tunggal dengan temuan agregat itulah nilainya.

---

## Keputusan 14 — Label panel digeser turun agar tera waktu tidak tertutup
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN (D-A4), sudah dijalankan**
**Persoalan:** Telaah pembimbing menemukan kotak label (a)/(b)/(c) menutupi sebagian tera
waktu CCTV, dan mempertanyakan keterbacaan angka di bawah panel pada lebar cetak sebenarnya.
**Keputusan:** label digeser turun (`0,975` → `0,905` koordinat sumbu), ukuran subjudul
dinaikkan 6,4 → 7,4 pt dan judul panel 8 → 8,5 pt, lalu dibangkitkan ulang pada 300 dpi.
**Alasan:** tera waktu dan overlay lokasi adalah **bukti provenans**, sehingga tidak boleh
tertutup elemen anotasi kita sendiri.
**Bukti:** tera waktu "02-09-2025 19:24:19" kini terbaca penuh pada ketiga panel; lebar
fisik tetap **16,99 × 5,14 cm @ 300 dpi** (2007 × 607 piksel) — syarat jurnal tidak berubah.
**Dampak pada naskah:** hanya gambar; tidak ada angka yang berubah.

---

## Keputusan 15 — Kedudukan hukum 4 citra kanal "NL Cycling" dipisahkan
**Tanggal:** 13 Agu 2026
**Status:** ✅ **DIPUTUSKAN PEMBIMBING TEKNIS (Bagian 5 butir 2), sudah dijalankan**
**Persoalan:** Pernyataan lisensi semula menyatukan seluruh 315 citra sebagai "rekaman stok".
**Keputusan:** dipisahkan — 311 citra stok berbayar, **4 citra materi kanal video**.
**Alasan (pembimbing):** rekaman stok setidaknya diperoleh melalui mekanisme lisensi,
sedangkan materi kanal video umumnya tidak; menyatukan keduanya menyamarkan perbedaan yang
justru relevan secara hukum.
**Bukti:** paragraf lisensi naskah revisi; klaster K100/K105/K108/K112.
**Dampak pada naskah:** satu kalimat terpisah di keterbatasan.

---

## Keputusan 16 — Angka wilayah pengganti TIDAK dikarang
**Tanggal:** 13 Agu 2026
**Status:** DIPUTUSKAN (perlu tinjauan Naufal bila ia punya sumber)
**Persoalan:** D-B menawarkan "ganti ke angka nasional saja, atau angka DIY dan Jawa Tengah
bila tersedia". Angka registrasi kendaraan untuk DIY, Jawa Tengah, dan Kalimantan Selatan
tidak tersedia terverifikasi di repositori ini.
**Pilihan:** (a) karang/estimasi angka wilayah; (b) hapus kalimat khusus Jakarta dan biarkan
angka nasional membawa motivasinya.
**Keputusan:** (b) — kalimat "24,5 juta … Jakarta Metropolitan Police … 19,5 juta" dihapus,
tidak diganti.
**Alasan:** CLAUDE.md §12.3 melarang mengisi angka tanpa data nyata. Paragraf tetap utuh
karena angka nasional (168.275.423 kendaraan, 83,7 % roda dua) sudah cukup memotivasi.
**Dampak pada naskah:** INTRODUCTION kehilangan satu kalimat; **bila Naufal punya sumber
BPS/Korlantas untuk DIY + Jawa Tengah + Kalimantan Selatan, kalimat itu dapat dikembalikan
dengan angka yang benar.**
