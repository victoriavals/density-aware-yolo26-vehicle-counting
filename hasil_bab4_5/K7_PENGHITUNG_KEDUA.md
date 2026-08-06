# K7b — Protokol Penghitung Kedua (janji Subbab 3.10.1)

> Disusun 5 Agustus 2026. **Kit sudah siap pakai** di `video_uji/penghitung_kedua/`.
> Yang dibutuhkan hanyalah satu orang selain Naufal, sekitar 30–45 menit.

Subbab 3.10.1 menjanjikan hitung manual oleh **dua penghitung** beserta **pelaporan tingkat
kesesuaian awal**. Saat ini GT berasal dari **satu** penghitung. Selama ini belum dipenuhi,
BAB 3 menjanjikan sesuatu yang tidak dilakukan BAB 4 — inkonsistensi internal yang langsung
terlihat penguji.

---

## 1. Kenapa cukup satu klip, dan kenapa harus klip 4

Menghitung ulang ketiga klip memakan sekitar dua jam orang dan tidak sepadan. Satu klip sudah
cukup untuk melaporkan kesesuaian antar-penilai secara sah, asalkan klip yang dipilih adalah
yang **paling sulit**.

Klip 4 adalah pilihan yang benar karena kepadatannya paling tinggi (17,1 objek/frame
rata-rata, p90 26, maksimum 30) dan jumlah perlintasannya terbesar (931 dari total 1.343).
Di sanalah dua manusia paling mungkin berbeda. Kalau kesesuaian tinggi di klip terpadat, ia
juga tinggi di klip 2 dan 3 yang hanya 1,0–2,8 objek/frame.

Menghitung klip *sparse* lebih dulu justru menghasilkan angka kesesuaian yang
**menyesatkan-optimistis** — mudah sepakat pada arus sepi, lalu diklaim berlaku untuk seluruh
data.

Bila ada waktu lebih, tambahkan klip 2 (hanya 116 perlintasan, sekitar 10 menit kerja).

---

## 2. Berkas yang sudah disiapkan

| Berkas | Isi |
|---|---|
| `video_uji/penghitung_kedua/gt_4_vidiouji_B.csv` | **template kosong** (60 baris, semua `count=0`) untuk penghitung B |
| `video_uji/penghitung_kedua/gt_4_vidiouji_A.csv` | salinan hitungan penghitung A — **JANGAN dibuka penghitung B** |
| `video_uji/penghitung_kedua/4_vidiouji_garis.jpg` | pratinjau garis virtual + panah arah, supaya definisi "melintas" sama |

Struktur baris: `interval,class,direction,count` — 10 interval (0–9, masing-masing 60 detik)
× 3 kelas (`big-vehicle`, `car`, `two-wheeler`) × 2 arah (`in`, `out`).

---

## 3. Instruksi untuk penghitung B (berikan apa adanya)

Tonton `video_uji/4_vidiouji.mp4` dan hitung kendaraan yang **melintasi garis** pada gambar
`4_vidiouji_garis.jpg`. Isi kolom `count` pada `gt_4_vidiouji_B.csv`.

Aturan yang harus sama persis dengan penghitung pertama:

1. **Garis:** dari titik (348, 739) ke (1919, 784). Kendaraan dihitung saat **titik tengah
   badannya melewati garis**, bukan saat mulai menyentuh.
2. **Arah "in" = kendaraan menuju kiri-bawah bingkai**; "out" = menuju kanan-atas. (Klip 4
   pada praktiknya satu arah, sehingga hampir semua masuk ke satu kolom saja — itu normal.)
3. **Tiga kelas:** `big-vehicle` (bus dan truk), `car` (mobil penumpang, termasuk pikap
   kecil), `two-wheeler` (sepeda motor). **Pejalan kaki TIDAK dihitung.**
4. **Interval 60 detik:** interval 0 = detik 0–60, interval 1 = 60–120, dan seterusnya hingga
   interval 9 = detik 540–600.
5. **Jangan melihat hasil penghitung pertama** sebelum selesai. Ini syarat mutlak — kalau
   dilihat, angkanya tidak lagi independen dan tidak bisa dilaporkan sebagai kesesuaian
   antar-penilai.

Bila ragu pada satu kendaraan, ambil keputusan dan lanjutkan; jangan mengulang-ulang
menonton bagian yang sama, karena penghitung pertama pun tidak melakukannya.

---

## 4. Setelah selesai — satu perintah

```bash
./.venv/Scripts/python.exe bandingkan_gt.py \
  --a video_uji/penghitung_kedua/gt_4_vidiouji_A.csv \
  --b video_uji/penghitung_kedua/gt_4_vidiouji_B.csv
```

Keluarannya: persentase kesesuaian awal, kesesuaian per kelas, per arah, dan daftar baris
yang berbeda (`gt_4_vidiouji_perbedaan.csv`). Jalur ini **sudah diuji** berjalan.

Angka "KESESUAIAN AWAL" itulah yang dilaporkan di BAB 4 sebagai pemenuhan janji Subbab 3.10.1.

### ⚠️ Rencanakan konsekuensinya sebelum menghitung

Bila A dan B berbeda cukup jauh, praktik yang benar adalah **meninjau bersama baris yang
berbeda, menyepakati satu angka, lalu menjadikan hasil kesepakatan itu sebagai GT final** —
dan **metrik penghitungan harus dihitung ulang** dengan GT tersebut. Artinya MAE 1,972,
RMSE 4,947, dan MAPE 37,17 % **berpotensi berubah**.

Yang dilaporkan di BAB 4 tetap dua-duanya: kesesuaian **awal** (sebelum rekonsiliasi, ini
ukuran keandalan penghitungan manual) dan metrik final (dihitung dari GT hasil kesepakatan).
Menyembunyikan salah satunya menghilangkan makna prosedurnya.

Perintah untuk menghitung ulang setelah GT final disepakati:

```bash
./.venv/Scripts/python.exe y26_counting.py \
  --video video_uji/4_vidiouji.mp4 \
  --weights runs_tesis/V8/weights/best.pt \
  --line 1919,784,348,739 --interval-s 60 \
  --gt video_uji/gt_4_vidiouji.csv --out counting_out
./.venv/Scripts/python.exe y26_bangun_hasil_bab45.py     # regenerasi hasil_bab4_5/
```

(Perhatikan urutan titik `--line` yang **terbalik** dari koordinat pemilihan — itu koreksi
konvensi arah yang sudah diverifikasi empiris; jangan diubah.)

---

## 5. Jalan cadangan bila benar-benar tidak ada orang kedua

### Cadangan 1 — uji ulang intra-penilai (*test-retest*)

Naufal menghitung ulang klip 4 setelah jeda **minimal tiga hari**, tanpa membuka hasil
pertama, memakai template `gt_4_vidiouji_B.csv` yang sama. Lalu bandingkan dengan perintah
yang sama.

⚠️ Ini **bukan pengganti setara**. Uji ulang intra-penilai mengukur konsistensi satu orang,
bukan bias sistematisnya — kalau seseorang konsisten salah menilai pikap sebagai mobil, uji
ini tidak akan menangkapnya. Karena itu **wajib dilabeli jujur**: *"keandalan intra-penilai
(test-retest)"*, tidak boleh ditulis sebagai kesesuaian antar-penilai.

### Cadangan 2 — revisi Subbab 3.10.1

Bila cadangan 1 pun tidak memungkinkan, **ubah janji di BAB 3** agar sesuai yang benar-benar
dilakukan. Mengubah janji lebih baik daripada melanggarnya. Usulan redaksi pengganti:

> Hitung manual pada penelitian ini dilakukan oleh satu penghitung dengan protokol yang
> ditetapkan sebelumnya, meliputi definisi titik lintas, konvensi arah, dan pengelompokan
> kelas kendaraan. Verifikasi silang oleh penghitung kedua sebagaimana lazim dilakukan pada
> pengumpulan data pengamatan tidak dapat dilaksanakan karena keterbatasan sumber daya
> pengamat, sehingga keandalan antar-penilai tidak terkuantifikasi. Keterbatasan ini
> dinyatakan secara eksplisit dan perlu diperhatikan dalam menafsirkan galat penghitungan,
> khususnya pada klip berkepadatan tinggi yang paling rentan terhadap perbedaan penilaian
> antarpengamat.

Kalimat pendampingnya untuk BAB 5:

> Penelitian lanjutan disarankan melibatkan sekurang-kurangnya dua penghitung independen
> beserta pelaporan tingkat kesesuaian awal, sehingga galat sistem dapat dipisahkan dari
> ketidakpastian acuan kebenaran itu sendiri.

---

## 6. Catatan keselamatan data (insiden 5 Agustus 2026)

Saat menyiapkan kit ini, perintah `siapkan_counting.py --make-gt-template` **menimpa**
`video_uji/gt_4_vidiouji.csv` — hitung manual 931 perlintasan — dengan template nol. Berkas
itu tidak ter-*track* git (`video_uji/*` masuk `.gitignore`).

Data **pulih utuh dan terverifikasi identik** dari kolom `y` pada
`counting_out/4_vidiouji/counting_errors.csv` (60 baris, total 931, MAE klip 4 tetap 4,15).

Dua perbaikan permanen sudah dipasang di `siapkan_counting.py`:

1. **Penjaga timpa** — menulis template ke berkas GT yang sudah berisi hitungan akan
   dibatalkan dengan pesan eksplisit, kecuali diberi `--timpa-gt`.
2. **Opsi `--gt-out`** — tujuan template dapat diarahkan ke folder lain, sehingga template
   penghitung kedua tidak pernah mendarat di jalur penghitung pertama.

Keduanya sudah diuji: perintah default kini menolak menimpa, dan GT tetap 931.

⚠️ **Hitung manual adalah satu-satunya data pada proyek ini yang tidak dapat dibangkitkan
ulang oleh kode.** Sebelum menjalankan apa pun yang menyentuh `video_uji/gt_*.csv`, salin
dulu. Pertimbangkan mengeluarkan `video_uji/gt_*.csv` dari `.gitignore` agar ikut ter-*track*
— ukurannya hanya beberapa kilobita dan nilainya paling tinggi di antara seluruh artefak.

---

Tautan: [redaksi hasil (K4)](K4_REDAKSI_HASIL.md) · [ambang RQ5 (K5)](K5_AMBANG_RQ5.md) ·
[hasil counting](09_counting_end_to_end/) · alat: `bandingkan_gt.py`, `siapkan_counting.py`
