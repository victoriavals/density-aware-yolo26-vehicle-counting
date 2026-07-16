# Kode Model Tesis — YOLO26 Termodifikasi (Tahap 1: Training & Ablasi)

Implementasi BAB 3 tesis *"Modifikasi Arsitektur YOLO26 melalui Atensi Hibrida,
Deteksi Multi-Skala P2, dan Pembobotan Loss Berbasis Densitas"*.
Diverifikasi baris-per-baris terhadap **ultralytics 8.4.92** dan lulus uji
`test_smoke.py` (matematika DALW, pembangunan 4 arsitektur, transfer bobot,
loss end-to-end).

## Peta berkas → tesis

| Berkas | Isi | Rujukan tesis |
|---|---|---|
| `y26_modules.py` | Modul HAM (kaskade atensi kanal→spasial) + registrasi | Subbab 3.6.1, Gambar 3.3 |
| `y26_dalw.py` | Bobot densitas w=1+α·ρ̂ + suntikan ke loss dual-head | Subbab 3.6.3, Pers. 3.2–3.5 |
| `y26_variants.py` | Pembangkit YAML varian, transfer bobot COCO, registry V1–V8 | Subbab 3.6, 3.8, Tabel 3.3 |
| `train_ablation.py` | Runner pelatihan 8 varian + grid search α,σ | Subbab 3.8–3.9, Tabel 3.3–3.4 |
| `download_dataset.py` | Unduh traffic-merged dari Roboflow + verifikasi split | Subbab 3.3 |
| `test_smoke.py` | Uji kebenaran implementasi (jalankan pertama kali) | — |
| `y26_nmsfree.py` | Instrumentasi DR, CM, stabilitas assignment + probe callback | Subbab 3.7, Pers. 3.6–3.7, A-10 |
| `analyze_nmsfree.py` | Analisis pasca-latih antarvarian + sensitivitas τ + plot | Subbab 3.7, BAB 4 |
| `test_nmsfree.py` | Uji instrumentasi Tahap 2 | — |
| `y26_strata.py` | Atribut strata + AP terstratifikasi protokol gaya COCO | Subbab 3.3.3, 3.11.1, Tabel 3.5 |
| `y26_stats.py` | Wilcoxon signed-rank + koreksi Holm | Subbab 3.11.4 |
| `y26_counting.py` | ByteTrack + virtual line crossing + MAE/RMSE/MAPE | Subbab 3.10, 3.11.3 |
| `evaluate_all.py` | Orkestrator evaluasi BAB 4 (global + strata + Wilcoxon) | Subbab 3.11 |
| `test_eval.py` | Uji evaluasi Tahap 3 | — |

## Persiapan lingkungan (PC RTX 4060)

```bash
# Python 3.11.9 dalam virtualenv/conda
pip install ultralytics==8.4.92 "supervision>=0.25,<0.30" roboflow
python -c "import torch; print(torch.cuda.is_available())"   # harus True
python test_smoke.py    # semua uji harus LULUS sebelum lanjut
```

Kode dikunci pada ultralytics **8.4.92** karena `DALWDetectionLoss` menyalin satu
metode internal dari versi tersebut. Bila kelak memperbarui ultralytics, jalankan
`test_smoke.py`; jika T4 gagal, jangan lanjut training sebelum disesuaikan.

## Urutan kerja

```bash
# 1) Dataset (split final per grup kamera-adegan-sesi, tidak diubah skrip)
python download_dataset.py --api-key ROBOFLOW_API_KEY --version <N>

# 2) Grid search α,σ SATU KALI pada varian penuh, pelatihan singkat (Subbab 3.9)
python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60
#    -> hasil terbaik tersimpan di dalw_best.json dan dipakai otomatis

# 3) Latih delapan varian (urut, konfigurasi identik, seed 0)
python train_ablation.py --data dataset/data.yaml --variant all

#    Bila terputus (listrik/OOM), lanjutkan varian tertentu:
python train_ablation.py --data dataset/data.yaml --variant V5 --resume
```

Keluaran tiap run: `runs_tesis/<V>/results.csv` (kurva per-epoch),
`weights/best.pt` & `last.pt`, plot PR/confusion. Simpan folder `runs_tesis`
utuh — ini bahan mentah BAB 4.

## Strategi memori 8GB (keputusan A-12)

Konfigurasi default (batch 16, AMP FP16, `cache=False`, `workers 4`) dirancang
muat di VRAM 8GB, tetapi varian ber-P2 (V3/V5/V7/V8) paling boros karena feature
map 160×160. Bila OOM:

1. Turunkan `--batch` (mis. 8) — **lalu pakai nilai yang sama untuk KEDELAPAN
   varian** dan catat di BAB 4; konfigurasi identik antarvarian adalah syarat
   keadilan ablasi (Subbab 3.2), jadi jangan mencampur batch antar-run.
2. `--batch -1` (AutoBatch) hanya untuk eksplorasi awal, bukan run final,
   karena tiap varian bisa mendapat batch berbeda.
3. Tutup aplikasi lain pemakai VRAM; `--workers 2` bila RAM sistem terbatas.
4. `--resume` aman dipakai kapan pun; checkpoint `last.pt` ditulis tiap epoch.

Estimasi kasar di RTX 4060: ±6–10 mnt/epoch untuk 2.372 citra latih tergantung
varian; dengan early stopping (patience 50) biasanya berhenti jauh sebelum 300.
Total 8 varian: rencanakan beberapa hari; jalankan berurutan, bukan paralel.

## Keputusan teknis yang kini terdokumentasi

**A-11 — head penerima w_i (terjawab, dengan bukti kode).** Pada ultralytics
8.4.92, model end2end memakai `E2ELoss` yang membangun dua cabang dari kelas
loss yang sama: one-to-many (topk 10) dan one-to-one (topk 7/1, mengemban STAL),
lalu mencampurnya dengan gain ProgLoss yang meluruh 0,8→0,1 sepanjang epoch.
DALW disuntikkan di dalam kelas loss bersama tersebut sehingga berlaku pada
**kedua head**, dan secara aljabar L = Σ_b g_b Σ_i w_i L_{b,i} = Σ_i w_i L_i
dengan L_i loss bawaan YOLO26 — persis Persamaan 3.5. ProgLoss dan STAL tetap
utuh (diverifikasi T4). Tuliskan paragraf ini di BAB 4 bagian implementasi.

**Keadilan inisialisasi ablasi.** Semua varian diinisialisasi dari bobot COCO
`yolo26s.pt` pada lapisan yang bersesuaian; HAM dan cabang P2 init segar
(praktik sama dengan CRL-YOLOv5/MST-YOLO/HIC-YOLOv5). Pergeseran indeks akibat
sisipan HAM ditangani pemetaan ulang nama parameter. Persentase transfer
dilaporkan otomatis tiap run — catat untuk BAB 4 (tipikal: HAM ±97% kunci,
P2 ±40% kunci/±62% parameter karena head 4-skala baru).

**Bobot pasca-augmentasi (Subbab 3.4).** w_i dihitung DI DALAM fungsi loss dari
label batch, sehingga otomatis terhitung ulang setelah mosaic/flip/scale, dan
berada dalam `torch.no_grad` (konstanta per objek; tidak menambah kompleksitas
gradien — klaim Pers. 3.5 terpenuhi secara literal).

## Catatan konsistensi naskah (penting sebelum sidang)

1. **GPU**: naskah menulis RTX 3060 8GB (Batasan 1.5, Tabel 3.6, subbab 2.5.2,
   2.7.3, 3.6.2). Karena eksperimen akan berjalan di **RTX 4060**, perbarui
   kelima titik tersebut (VRAM tetap 8GB, argumen "perangkat kelas menengah"
   tetap berlaku).
2. Nilai α, σ terpilih dari `dalw_best.json` → isi placeholder Tabel 3.3/BAB 4.
3. `runs_tesis/*/results.csv` → sumber angka mAP placeholder BAB 4.

## Lisensi

Ultralytics berlisensi AGPL-3.0 — bebas untuk riset/tesis. Bila kelak dijadikan
layanan komersial tertutup, perlu lisensi enterprise Ultralytics.

## Tahap 2 — Instrumentasi NMS-free (Subbab 3.7, menjawab A-10)

**Apa yang diukur.** Duplicate Rate DR(τ) = (1/M) Σ N_k(τ) (Pers. 3.6) dan
Confidence Margin CM_k = conf(p¹)−conf(p²) (Pers. 3.7) dari keluaran MENTAH
kepala one-to-one (forward langsung, melewati predictor standar — sesuai janji
"menggali kode internal"), plus stabilitas assignment antar-epoch yang kini
diformalkan (A-10):

    S(t) = (1/M_probe) Σ_k 1[ a_k(t) = a_k(t−1) ]

dengan a_k(t) indeks anchor pilihan assigner one-to-one (STAL, top-k akhir 1 —
terverifikasi empiris 1,00 anchor/GT) pada himpunan probe validasi tetap
(default 64 citra, letterbox 640, tanpa augmentasi); a_k boleh ∅ (tak
ter-assign), ∅==∅ dihitung stabil, dan fraksi ter-assign dilaporkan terpisah.

**Keputusan implementasi yang perlu ditulis di BAB 3/4.** Pencocokan prediksi→
objek: tiap prediksi dipetakan ke SATU GT ber-IoU tertinggi dengan syarat
IoU ≥ 0,5 dan kelas sama; beberapa prediksi boleh menunjuk objek yang sama
(itulah duplikasi yang diukur). CM dihitung atas semua prediksi tercocok tanpa
filter τ (τ hanya menyaring DR), dan bila prediksi kedua tidak ada maka
conf(p²)=0. Interpretasi: DR≈1 sehat; dup_frac naik = mekanisme one-to-one
terganggu (kekhawatiran P2); CM menipis = pemenang tidak lagi tunggal-jelas.

**Pemakaian.** Saat training, probe berjalan otomatis tiap epoch (atur
`--probe`, 0 = mati) dan menulis `runs_tesis/<V>/nmsfree_probe.csv`
(epoch, S(t), assigned_frac, anchors/GT, DR, miss, dup, CM). Setelah kedelapan
varian selesai:

```bash
python analyze_nmsfree.py --data dataset/data.yaml --split test \
    --runs runs_tesis --variants V1,V3,V5,V7,V8
```

Keluaran `nmsfree_out/`: `summary.csv` (+Δ terhadap V1), `tau_sweep.csv` dan
`dr_vs_tau.png` (analisis sensitivitas τ, bagian A-10), `cm_hist.png`, serta
`<V>_per_image.csv` — DR/CM per citra sebagai bahan uji Wilcoxon berpasangan
pada Tahap 3. Fokus pembahasan BAB 4: V1 versus varian ber-P2 (V3/V5/V7/V8)
sesuai Subbab 3.8.

## Tahap 3 — Evaluasi terstratifikasi, Wilcoxon, dan counting (Subbab 3.11)

**Alur setelah kedelapan varian selesai dilatih:**

```bash
# (a) metrik global + AP terstratifikasi + Wilcoxon, sekali untuk semua varian
python evaluate_all.py --data dataset/data.yaml --split test --variants all

# (b) analisis NMS-free (Tahap 2)
python analyze_nmsfree.py --data dataset/data.yaml --split test --runs runs_tesis

# (c) counting end-to-end pada video uji + hitung manual
python y26_counting.py --video uji_ruas1.mp4 --weights runs_tesis/V8/weights/best.pt \
    --line 0,540,1919,540 --interval-s 60 --gt gt_ruas1.csv --save-video
```

Keluaran `eval_out/`: `global_metrics.csv` (P/R/F1/mAP — Pers. 3.8–3.11),
`strata_ap.csv` (AP50 & AP50-95 per varian × kelas × ukuran/oklusi/densitas),
`wilcoxon_ap5095.csv` & `wilcoxon_ap50.csv`. Keluaran counting:
`counts_per_interval.csv`, `events.csv`, `counting_errors.csv`, `summary.json`
(memuat MAE/RMSE/MAPE + proporsi eksklusi y=0, serta **FPS model & pipeline**
— pengisi placeholder "[XX] frame per detik" pada abstrak/BAB 4).

**Keputusan implementasi yang perlu ditulis di BAB 3/4.**
(1) Tier oklusi dari proksi Pers. 3.1: no < 0,10 ≤ partial < 0,35 ≤ heavy;
tier densitas per citra: sparse < 10 ≤ medium < 26 ≤ dense (selaras narasi
"lebih dari 25 objek" BAB 1); ukuran memakai luas piksel letterbox-640 konvensi
COCO. Semua ambang dapat diganti via parameter dan wajib dilaporkan.
(2) AP strata memakai protokol ignore gaya COCO: GT luar-strata = ignore,
prediksi tercocok ke GT ignore ikut di-ignore, dan khusus dimensi ukuran
prediksi tak tercocok berluas di luar strata juga di-ignore.
(3) Unit Wilcoxon = AP50-95 per (kelas × strata) — maksimum 36 sel, baris
global dikecualikan; tiga hipotesis utama (V8vsV1, V4vsV1, V8vsV5) taraf 5%,
seluruh pasangan lain sekunder dengan koreksi Holm (`wilcoxon_info.json`).
(4) MAPE hanya pada pengamatan y>0; proporsi pengecualian dilaporkan otomatis.

**Prasyarat counting (tantangan yang sudah lama tercatat).** Evaluasi Pers.
3.12–3.14 membutuhkan VIDEO dengan hitung manual — dataset citra statis tidak
cukup. Rekam beberapa klip CCTV uji, tentukan garis virtual per klip, lalu isi
CSV GT berformat `interval,class,direction,count` (dokumentasi lengkap di
docstring `y26_counting.py`). Pustaka: `sv.ByteTrack` deprecated sejak
supervision 0.28 (dihapus di 0.30) namun tetap berfungsi pada rentang yang
dipin di atas — catat versi pustaka di BAB 3/4.

**Analisis sensitivitas α (rencana BAB 4)** — jalankan V4 pada tiap α dengan
σ terpilih, tanpa saling menimpa:

```bash
for A in 0.5 1.0 2.0; do
  python train_ablation.py --data dataset/data.yaml --variant V4 \
      --alpha $A --sigma 0.10 --suffix _a$A
done
```

**Validasi proksi oklusi (Subbab 3.3.3).** Anotasikan subset kecil secara
manual (CSV `image,gt_index,tier`) lalu:

```python
from y26_strata import occlusion_agreement
print(occlusion_agreement("manual_oklusi.csv", "dataset/data.yaml", split="val"))
```

**RQ5 / A-13.** Tetapkan ambang target counting SEBELUM eksperimen bersama
pembimbing (misalnya MAPE ≤ 10% per interval sebagai "standar penerapan
praktis") — kode melaporkan angkanya, keputusan ambang milik naskah.

## Peta keluaran → placeholder BAB 4

`global_metrics.csv` → tabel metrik utama; `strata_ap.csv` → tabel/figur
terstratifikasi; `wilcoxon_ap5095.csv` → nilai p tiga hipotesis; `nmsfree_out/`
→ DR, CM, sensitivitas τ, kurva S(t); `counting summary.json` → MAE, RMSE,
MAPE, FPS; `dalw_best.json` → α, σ terpilih (Tabel 3.3); laporan transfer
bobot tiap run → paragraf inisialisasi.
