# video_uji/ — Video Uji Counting (P9 / RQ5)

## ✅ Status: keempat klip siap, tinggal hitung manual

Berkas kerja sudah **dipotong tepat 600,0 detik (18.000 frame)** dengan `ffmpeg -frames:v 18000 -c copy`
(tanpa encode ulang) agar setiap jendela pengamatan berdurasi sama. Rekaman penuh diarsipkan di `asli/`.

| Klip | Garis virtual | Resolusi | FPS | Interval |
|---|---|---|---|---|
| `1_vidiouji.mp4` | `504,1,1919,839` | 1920×1080 | 30 | 10 |
| `2_vidiouji.mp4` | `119,1,1919,926` | 1920×1080 | 30 | 10 |
| `3_vidiouji.mp4` | `0,317,1280,668` | 1280×720 | 30 | 10 |
| `4_vidiouji.mp4` | `348,739,1919,784` | 1920×1080 | 30 | 10 |

Rincian lengkap (untuk dilaporkan di BAB 4 sesuai §3.10.1): `konfigurasi_garis.json`.
Pratinjau garis: `preview/FINAL_*.jpg` · alat pemilih garis: `preview/pilih_garis.html`.

**Yang tersisa:** isi `gt_*.csv` (60 baris tiap klip = 10 interval × 3 kelas × 2 arah) oleh **dua penghitung terpisah**.

Alur hitung manual:
1. Salin template jadi dua: `gt_1_vidiouji_A.csv` (penghitung 1) dan `gt_1_vidiouji_B.csv` (penghitung 2).
   Masing-masing mengisi **tanpa melihat hasil yang lain**.
2. Bandingkan + hitung tingkat kesesuaian awal (wajib dilaporkan di BAB 4):
   ```bash
   python bandingkan_gt.py --dir video_uji
   ```
   Menghasilkan `<klip>_perbedaan.csv` berisi baris yang berselisih.
3. Tinjau baris yang berselisih **bersama-sama**, sepakati angkanya, simpan sebagai
   `gt_<klip>.csv` (tanpa akhiran `_A`/`_B`) — inilah GT final yang dipakai `y26_counting.py`.

Perintah counting (dijalankan Claude setelah GT terisi):
```bash
python y26_counting.py --video video_uji/1_vidiouji.mp4 --weights runs_tesis/V8/weights/best.pt \
    --line 504,1,1919,839 --interval-s 60 --gt video_uji/gt_1_vidiouji.csv --save-video
```

---


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
