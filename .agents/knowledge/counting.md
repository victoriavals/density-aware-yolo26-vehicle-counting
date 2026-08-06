# Penghitungan End-to-End (ByteTrack + Virtual Line) — End-to-End Vehicle Counting

> **EN — TL;DR:** RQ5 evaluates end-to-end counting: raw one-to-one detections (conf 0,25) → ByteTrack (`supervision` <0.30) → virtual-line crossing counted per direction and per class, pedestrians always excluded. Errors are MAE/RMSE/MAPE (Pers. 3.12–3.14); MAPE is computed only over intervals with `y_t > 0` and the excluded fraction is reported. Ground truth is a manual CSV `interval,class,direction,count`. `siapkan_counting.py` is the CPU-only prep kit (video inspection, line/grid preview, `--make-gt-template`). Concrete MAPE/FPS pass thresholds are **A-02** (pending from pembimbing). Outputs land in `counting_out/`.

Subbab ini mendokumentasikan tahap akhir pipeline tesis, yaitu penghitungan
kendaraan *real-time* yang menjawab RQ5. Berkas inti `y26_counting.py`
(Subbab 3.10, Gambar 3.6; metrik Pers. 3.12–3.14) dan kit persiapan
`siapkan_counting.py` (P9). Untuk cara menjalankannya langkah demi langkah lihat
[playbook evaluate](../playbooks/evaluate.md); invarian metodologis yang mengikat
tahap ini ada di [methodology-invariants](../rules/methodology-invariants.md).

| File | Covers | Rujukan tesis |
|---|---|---|
| `y26_counting.py` | Detektor o2o mentah → ByteTrack → *virtual line crossing* → MAE/RMSE/MAPE | Subbab 3.10, 3.11.3, Pers. 3.12–3.14 |
| `siapkan_counting.py` | Kit P9 (inspeksi video, preview garis/grid, `--make-gt-template`) — CPU saja | — (bantu RQ5) |

## Posisi dalam pipeline

Alur end-to-end memproses satu video menjadi hitungan per interval, lalu
membandingkannya dengan hitung manual:

```
frame video → deteksi (kepala one-to-one MENTAH, conf 0,25)
            → ByteTrack (supervision) → virtual line crossing (in/out per kelas)
            → akumulasi per interval → MAE/RMSE/MAPE terhadap hitung manual
```

Penghitungan memakai satu bobot terlatih (praktik: `runs_tesis/V8/weights/best.pt`,
model penuh) — ia bukan bagian *ablation study* deteksi, melainkan uji akurasi
*end-to-end* pada standar penerapan praktis.

## Detektor: forward mentah kepala one-to-one

`make_detector()` TIDAK memakai predictor standar Ultralytics. Ia melakukan
*forward* langsung `DetectionModel` mode eval yang mengembalikan keluaran mentah
kepala *one-to-one* `(B, 300, 6)` `[xyxy, conf, cls]` pada ruang letterbox 640
(padding 114), lalu:

- menyaring dengan ambang `conf = 0,25` (CLI/JSON: `0.25`);
- mentransformasi ulang kotak dari ruang letterbox 640 kembali ke koordinat
  piksel frame asli (buang padding, bagi rasio skala, klip ke tepi frame);
- mengembalikan `(xyxy_piksel_frame, conf, cls)`.

Konvensi *NMS-free* ini konsisten dengan seluruh evaluasi tesis (DR/CM, cache
strata) yang sengaja melewati predictor standar — lihat
[code-injection](../architecture/code-injection.md) dan
[nmsfree-analysis](nmsfree-analysis.md). `register_ham()` dipanggil sebelum
memuat bobot agar `torch.load` menemukan kelas HAM (varian ber-HAM).

## ByteTrack + virtual line crossing

Pelacakan memakai `sv.ByteTrack` dari pustaka `supervision` [26]. Parameter yang
dikodekan:

| Parameter ByteTrack | Nilai | Catatan |
|---|---|---|
| `track_activation_threshold` | `conf` (0,25) | ambang aktivasi = ambang deteksi |
| `lost_track_buffer` | `int(fps)` | toleransi ±1 detik track hilang |
| `minimum_matching_threshold` | `0.8` | ambang pencocokan IoU antar-frame |
| `frame_rate` | `round(fps)` | dari FPS video |

Garis virtual adalah `sv.LineZone(start, end)` dengan koordinat piksel video.
`lz.trigger(det)` mengembalikan dua *boolean mask* `(ci, co)` — kendaraan yang
melintas ke arah **in** dan **out**. Orientasi in/out mengikuti arah
`start → end` supervision (normal garis); preview di `siapkan_counting.py`
menggambar panah normal agar arah bisa diverifikasi sebelum penghitungan.

**Pejalan kaki DIKECUALIKAN.** `exclude = ("pedestrian", "pejalan-kaki",
"person")` menyaring deteksi berdasarkan nama kelas SEBELUM masuk tracker,
sehingga `pedestrian` (objek konteks, Tabel 3.1) tidak pernah dihitung. Ini
invarian metodologis — jangan dilonggarkan.

**Interval pengamatan.** Setiap frame dipetakan ke jendela waktu
`interval = int(f_idx / (fps * interval_s))` (default `--interval-s 60` detik,
mulai indeks 0). Hitungan diakumulasi per kunci `(interval, class, direction)`.

## Metrik penghitungan (Pers. 3.12–3.14)

`counting_metrics()` menyatukan kunci prediksi dan GT (`set(pred) | set(gt)`,
yang hilang dianggap 0) sehingga objek terlewat maupun hitungan hantu
sama-sama terhukum. Dari selisih `err = y − yhat`:

| Metrik | Rumus di kode | Cakupan |
|---|---|---|
| MAE (Pers. 3.12) | `mean(|err|)` | seluruh pengamatan |
| RMSE (Pers. 3.13) | `sqrt(mean(err²))` | seluruh pengamatan |
| MAPE (Pers. 3.14) | `100 · mean(|err[y>0]| / y[y>0])` | **hanya `y_t > 0`** |

**Aturan MAPE.** MAPE dihitung hanya pada pengamatan dengan `y_t > 0` (menghindari
pembagian nol). Proporsi yang dikecualikan WAJIB dilaporkan dan sudah otomatis:
`mape_excluded` (jumlah interval `y = 0`) dan `mape_excluded_frac`. Ini mengikat —
lihat [methodology-invariants](../rules/methodology-invariants.md).

## Format CSV ground truth (hitung manual)

GT diisi manusia berformat empat kolom:

```
interval,class,direction,count
0,car,in,12
0,two-wheeler,in,31
1,car,out,9
```

`interval` = indeks jendela ke-i berdurasi `--interval-s` detik (mulai 0);
`class` = nama kelas (tanpa `pedestrian`); `direction` ∈ {`in`, `out`};
`count` = jumlah lintasan manual pada sel itu.

## Kit persiapan: `siapkan_counting.py` (P9)

Kit CPU-only yang menyiapkan tiga prasyarat yang hanya bisa disediakan manusia:
memilih garis, memahami arah in/out, dan mengisi GT. Tanpa GPU/model.

- **Inspeksi video** — cetak resolusi, FPS, durasi, jumlah frame, jumlah interval.
- **Preview garis** — simpan frame pertama + garis kandidat (merah) + grid
  koordinat piksel + panah normal in/out ke `video_uji/preview/<stem>_garis.jpg`;
  Naufal membaca koordinat garis dari gambar itu.
- **Template GT** — `--make-gt-template` membuat kerangka
  `gt_<stem>.csv` (interval × kelas-nonpejalan × 2 arah, semua `count=0`,
  jumlah interval = `ceil(durasi / interval_s)`) siap diisi manual.

```bash
# inspeksi + preview garis tengah default + grid
python siapkan_counting.py --video video_uji/uji_ruas1.mp4
# preview garis kandidat tertentu (verifikasi arah panah in/out)
python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line 0,540,1919,540
# buat kerangka GT
python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template
```

Panduan langkah demi langkah ada di `video_uji/README.md` (Tahap 3c).

## Menjalankan penghitungan

```bash
python y26_counting.py --video video_uji/uji_ruas1.mp4 \
    --weights runs_tesis/V8/weights/best.pt \
    --line x1,y1,x2,y2 --interval-s 60 --gt gt_uji_ruas1.csv --save-video
```

Argumen utama: `--video`, `--weights`, `--line x1,y1,x2,y2` (piksel video),
`--conf` (default `0.25`), `--interval-s` (default `60`), `--gt` (CSV manual),
`--exclude` (default `pedestrian,pejalan-kaki,person`), `--out` (default
`counting_out`), `--save-video`, `--device`, `--max-frames`.

## Keluaran (`counting_out/`)

| Berkas | Isi |
|---|---|
| `counts_per_interval.csv` | hitungan prediksi per `(interval, class, direction)` |
| `events.csv` | tiap lintasan: `time_s, interval, tracker_id, class, direction` |
| `counting_errors.csv` | per sel: `y, yhat, abs_err` (hanya bila `--gt` diberikan) |
| `summary.json` | `frames, fps_video, fps_model, fps_pipeline, line, interval_s, totals`, dan `metrics` (MAE/RMSE/MAPE + proporsi eksklusi) |

`summary.json` juga membawa **FPS model** (`frames / waktu_forward`) dan
**FPS pipeline** (`frames / waktu_wall-clock`) — pengisi placeholder kecepatan
inferensi "[XX] frame per detik" di abstrak/BAB 4. Folder `counting_out/` adalah
bahan mentah BAB 4 — jangan dihapus/ditimpa.

## Catatan pustaka & keputusan pending

- **`supervision` < 0.30 WAJIB.** `sv.ByteTrack` *deprecated* sejak supervision
  0.28 dan **dihapus di 0.30**; kode di-pin `supervision 0.29.1` dan menyembunyikan
  `FutureWarning` deprecation. Catat versi pustaka di BAB 3/4. Lihat
  [environment](environment.md).
- **A-02 (pending — dari pembimbing).** Ambang target RQ5 (mis. MAPE ≤ X% per
  interval sebagai "standar penerapan praktis" dan target FPS) BELUM ditetapkan.
  Kode melaporkan angkanya; keputusan ambang milik naskah dan menunggu pembimbing.
  Jangan menetapkan angka final sendiri — lihat
  [pending-decisions](../status/pending-decisions.md).
- **Status.** Kit P9 (`siapkan_counting.py` + `video_uji/README.md`) sudah siap
  dan terverifikasi pada video sintetis (artefak uji dihapus). P10 counting nyata
  belum dijalankan — butuh video uji CCTV, `gt_<nama>.csv` terisi manual, dan
  ambang A-02. Lihat [progress](../status/progress.md).

## Hasil aktual RQ5 (5 Agustus 2026)

**3 klip × 10 interval × 3 kelas × 2 arah = 180 pengamatan.** MAE **1,972** · RMSE **4,947** ·
MAPE **37,17 %** (68/180 pengamatan y=0 dikecualikan, aturan Subbab 3.11.3) · selisih agregat
**−23,9 %** (sistem 1.022 vs manual 1.343) · **FPS pipeline 20,47** (19,45–21,49).

⚠️ **TIGA konteks pengukuran kecepatan, jangan tertukar.** (1) Tabel 3.7 `eval_out/complexity.csv`
= FPS **model murni pada tolok ukur standar** (V1 32,39; V4 30,51; V8 23,31) — BUKAN kecepatan
sistem. (2) `summary.json` `fps_model` = forward pass pada video nyata. (3) `summary.json`
`fps_pipeline` = **termasuk ByteTrack + line crossing** — inilah satu-satunya angka yang sah
untuk klaim *real-time* dan placeholder abstrak. Terukur pada klip terpadat
(`counting_out/fps_probe/`, 1.800 bingkai): V1 23,28 · V4_a2.0 23,20 · V8 **19,29** FPS.
Rata-rata tiga klip penuh: **20,47**. Sumber direkam 30,0 FPS → **tak satu pun varian
mencapai laju sumber**; jangan mengklaim 30 FPS dari Tabel 3.7.

⚠️ **Konvensi arah in/out harus diselaraskan sebelum menghitung MAE.** `sv.LineZone`
menentukan in/out dari **orientasi garis** (titik A→B pada `--line`), sedangkan penghitung
manusia memakai definisi visualnya sendiri. Pada proyek ini konvensi penghitung adalah
**"in" = kendaraan menuju kiri-bawah bingkai**, sedangkan LineZone menganggap "in" = menuju
kanan-atas → **terbalik seragam** di keempat klip. Perbaikan: **balik urutan titik garis**
(`--line x2,y2,x1,y1`) — geometri identik, hanya arah pembacaan berubah; diverifikasi empiris
(klip 4: `car_out=15` → `car_in=15`). Dampaknya besar: MAPE klip 3 turun 54,79 % → **26,78 %**.

⚠️ **Periksa geometri garis per kelas.** Garis harus benar-benar memotong lajur yang dipakai
SETIAP kelas. Klip 1 dikecualikan dari evaluasi karena segmennya berakhir sebelum lajur mobil:
hitung manual mencatat 20 mobil sementara sistem 0 → GT dan sistem mengukur **populasi
berbeda** (cacat validitas pengukuran, bukan performa model). Cara mendeteksi: lacak per
bingkai lalu hitung berapa *track* per kelas yang benar-benar **berpindah sisi** garis
(klip 1: hanya 2 dari 24 track mobil).

**Pola galat per kelas** (bahan analisis Subbab 3.11.6): roda dua paling andal (−9 % bahkan
pada klip terpadat; kelas mayoritas), mobil bergantung geometri garis (tepat pada 2 klip,
−56 % pada klip 4), kendaraan besar terlemah (0 dari 21 pada klip terpadat; kelas minoritas).
MAE naik seiring kepadatan (0,72 → 1,05 → 4,15).

**Status protokol:** GT masih dari **satu** penghitung; Subbab 3.10.1 menjanjikan dua +
pelaporan tingkat kesesuaian awal (alat: `bandingkan_gt.py`, keputusan **K7b** terbuka).
Hasil & grafik: `hasil_bab4_5/09_counting_end_to_end/`.

