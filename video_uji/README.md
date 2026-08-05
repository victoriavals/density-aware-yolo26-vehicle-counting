# video_uji/ — Video Uji Counting (P9 / RQ5)

## ✅ Status: counting SELESAI untuk 3 klip (hasil di `hasil_bab4_5/09_counting_end_to_end/`)

Berkas kerja sudah **dipotong tepat 600,0 detik (18.000 frame)** dengan `ffmpeg -frames:v 18000 -c copy`
(tanpa encode ulang) agar setiap jendela pengamatan berdurasi sama. Rekaman penuh diarsipkan di `asli/`.

**Konvensi arah:** `in` = kendaraan menuju **kiri-bawah** bingkai (definisi penghitung manual).
Diwujudkan dengan **membalik urutan titik** garis pada `--line` — geometri garis identik,
hanya arah pembacaan `sv.LineZone` yang berubah. Rincian & bukti: `konfigurasi_garis.json`.

| Klip | Garis dipakai (`--line`) | Resolusi | Interval | Status |
|---|---|---|---|---|
| `2_vidiouji.mp4` | `1919,926,119,1` | 1920×1080 | 10 | ✅ dipakai |
| `3_vidiouji.mp4` | `1280,668,0,317` | 1280×720 | 10 | ✅ dipakai |
| `4_vidiouji.mp4` | `1919,784,348,739` | 1920×1080 | 10 | ✅ dipakai |
| `1_vidiouji.mp4` | ~~`504,1,1919,839`~~ | 1920×1080 | 10 | ⛔ **DIKECUALIKAN** |

> **Kenapa klip 1 dikecualikan (keputusan peneliti, 5 Agu 2026):** segmen garisnya berakhir
> pada y=839 sehingga tidak menjangkau lajur bawah yang dipakai mobil — hitung manual
> (lebar jalan penuh, 20 mobil/10 mnt) dan keluaran sistem (0 mobil) mengukur populasi
> kendaraan yang berbeda. Ini **cacat validitas pengukuran**, bukan performa model. Berkas
> mentahnya **tetap disimpan** sebagai bukti; alasan pengecualian wajib ditulis di BAB 4/5.
> Bukti diagnosis: `preview/DIAG_klip1_mobil.jpg`, `counting_out/1_vidiouji/`.

Rincian lengkap (untuk dilaporkan di BAB 4 sesuai §3.10.1): `konfigurasi_garis.json`.
Pratinjau garis: `preview/FINAL_*.jpg` · alat pemilih garis: `preview/pilih_garis.html`.

**Hasil counting** (3 klip, 180 pengamatan): MAE 1,972 · RMSE 4,947 · MAPE 37,17 % ·
FPS pipeline 20,47. Rincian: `../hasil_bab4_5/09_counting_end_to_end/`.

Perintah yang dipakai (contoh klip 3):
```bash
python y26_counting.py --video video_uji/3_vidiouji.mp4 --weights runs_tesis/V8/weights/best.pt \
    --line 1280,668,0,317 --interval-s 60 --gt video_uji/gt_3_vidiouji.csv
```

### ⏳ Yang masih terbuka

1. **Penghitung kedua** (protokol 3.10.1 menuntut dua penghitung independen + pelaporan
   tingkat kesesuaian awal — keputusan **K7**). GT saat ini dari satu penghitung.
   Bila penghitung kedua tersedia: salin `gt_<klip>.csv` → `gt_<klip>_A.csv` dan `_B.csv`,
   isi terpisah, lalu jalankan `python bandingkan_gt.py --dir video_uji`.
2. **Ambang lulus RQ5** (**A-02/K5**) — target MAPE & FPS dari pembimbing.

---

## Referensi: cara menyiapkan klip baru (bila diperlukan)


Folder ini menampung klip CCTV uji untuk evaluasi penghitungan end-to-end
(Subbab 3.10–3.11, Pers. 3.12–3.14). **Isi folder ini dikecualikan dari git**
kecuali README ini.

## Yang perlu Anda (Naufal) siapkan — sesuai protokol naskah Subbab 3.10.1

1. **Sekurang-kurangnya 3 klip video CCTV** dari **titik pengamatan berbeda**:
   - Masing-masing **≥10 menit**, mencakup periode lalu lintas **lengang dan padat**.
   - **Bukan** dari sesi perekaman yang citranya dipakai sebagai data latih (cegah kebocoran).
   - Rekam pada **resolusi & laju frame asli** kamera (keduanya dilaporkan — FPS memengaruhi pelacakan).
   - Format terbaca OpenCV (mp4/H.264 aman).
2. **Hitung manual oleh DUA penghitung terpisah** → `gt_<nama>.csv` (kerangka otomatis, lihat di bawah).
   Bandingkan hasil per interval; interval yang berselisih ditinjau ulang bersama sampai sepakat;
   **catat tingkat kesesuaian awal antar-penghitung** (dilaporkan di BAB 4).
3. **Garis virtual** per klip: segmen lurus memotong seluruh lebar lajur, di area **bebas oklusi tetap**
   (tiang/reklame), **tegak lurus** arah dominan; koordinat kedua ujung (piksel) **dicatat & dilaporkan**.
4. **Ambang lulus RQ5** (keputusan pending **A-02/K5**) — target MAPE & FPS, bersama pembimbing.

> **Tiga aturan kasus khusus (naskah 3.10.1) — untuk penghitung manual:** (a) titik acuan kendaraan =
> **tengah sisi bawah** kotak pembatas saat melintas utuh; (b) kendaraan **berhenti** di garis tak dihitung
> sampai perlintasan selesai (cegah hitung berulang saat macet); (c) kendaraan **berbalik arah** dihitung
> sekali per arah perlintasan.

## Langkah kerja

### 1. Inspeksi video + pilih garis virtual
```bash
python siapkan_counting.py --video video_uji/uji_ruas1.mp4
```
Cetak resolusi/FPS/durasi/jumlah interval, dan menyimpan
`video_uji/preview/uji_ruas1_garis.jpg` — frame pertama dengan **grid koordinat piksel**,
garis tengah default, dan **panah arah** (sisi tujuan panah = salah satu dari in/out).
Baca koordinat garis yang Anda inginkan dari grid, lalu verifikasi:
```bash
python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line 0,540,1919,540
```
Ulangi sampai garis melintang tepat di lokasi penghitungan (biasanya melintang arah lalu lintas).

### 2. Buat kerangka GT lalu isi hitung manual
```bash
python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template
```
Menghasilkan `video_uji/gt_uji_ruas1.csv` berisi baris `interval,class,direction,count`
untuk tiap (interval × kelas × arah) dengan `count=0`. **Tonton video, hitung manual**
berapa kendaraan tiap kelas melintasi garis per arah per interval, lalu isi kolom `count`.
- Kelas dihitung: **big-vehicle, car, two-wheeler** (pejalan kaki DIKECUALIKAN — kelas konteks).
- `interval` = indeks jendela ke-i (mulai 0), tiap `--interval-s` detik.
- `direction` in/out mengikuti panah pada preview (dua arah dihitung terpisah).
- Baris ber-`count=0` boleh dibiarkan bila memang tidak ada; MAPE hanya dihitung pada y>0.

### 3. Jalankan counting (butuh GPU + bobot V8)
Sesuai README Tahap 3(c):
```bash
python y26_counting.py --video video_uji/uji_ruas1.mp4 \
    --weights runs_tesis/V8/weights/best.pt \
    --line <x1,y1,x2,y2> --interval-s 60 --gt video_uji/gt_uji_ruas1.csv --save-video
```
Keluaran `counting_out/`: `counts_per_interval.csv`, `events.csv`, `counting_errors.csv`,
`summary.json` (MAE/RMSE/MAPE + proporsi eksklusi y=0 + FPS model & pipeline).

Setelah itu tempel **Prompt 9** — saya rangkum ke `hasil/ringkasan_counting.md`.

## Catatan
- `sv.ByteTrack` deprecated sejak supervision 0.28 (dihapus 0.30) tetapi berfungsi pada
  0.29.1 yang dipin — versi pustaka dicatat di BAB 3/4.
- Garis virtual per klip **dilaporkan di naskah** (koordinat + alasan penempatan).
- FPS dari `summary.json` mengisi placeholder "[XX] frame per detik" di abstrak/BAB 4.
