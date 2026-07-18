# video_uji/ — Video Uji Counting (P9 / RQ5)

Folder ini menampung klip CCTV uji untuk evaluasi penghitungan end-to-end
(Subbab 3.10–3.11, Pers. 3.12–3.14). **Isi folder ini dikecualikan dari git**
kecuali README ini.

## Yang perlu Anda (Naufal) siapkan

1. **Beberapa klip video CCTV** (mis. `uji_ruas1.mp4`, `uji_ruas2.mp4`).
   - Adegan lalu lintas heterogen padat (sesuai domain tesis).
   - Durasi cukup untuk beberapa interval pengamatan (mis. ≥5 menit bila interval 60 s).
   - Format terbaca OpenCV (mp4/H.264 aman). Idealnya beda ruas/sudut untuk variasi.
2. **Hitung manual per interval** → `gt_<nama>.csv` (kerangka dibuat otomatis, lihat di bawah).
3. **Ambang lulus RQ5** (keputusan pending **A-02**) — angka MAPE & FPS target. Ini
   keputusan naskah bersama pembimbing; skrip hanya melaporkan angkanya.

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
