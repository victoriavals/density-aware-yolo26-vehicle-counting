# Evaluasi: Metrik, Strata, Kompleksitas — Evaluation: Metrics, Strata, Complexity

> **EN — TL;DR:** How the thesis evaluates the eight variants (Subbab 3.11). Detection metrics P/R/F1/mAP (Eq. 3.8–3.11) come from the Ultralytics validator; the *unit of every Wilcoxon test* is **AP per (class × stratum)** computed with a COCO-style protocol over three strata dimensions — size (COCO 32²/96²), occlusion (proxy Eq. 3.1, tiers 0.10/0.35), density (10/26) — with the `global` row deliberately excluded. Complexity Table 3.7 (params/GFLOPs/size/VRAM/time/FPS) is assembled by `y26_complexity` plus the training `ComplexityCallback`. Counting metrics MAE/RMSE/MAPE (Eq. 3.12–3.14) report **MAPE only where y_t > 0**. All artefacts land in `eval_out/`. NOTE: the occlusion `heavy` tier is nearly empty on val (0/4094) — a real finding, not a bug.

Dokumen ini menjelaskan lapisan evaluasi tesis: apa yang diukur, bagaimana dihitung di kode, dan di mana hasilnya disimpan. Orkestratornya adalah `evaluate_all.py`; mesin strata di `y26_strata.py`; tabel kompleksitas di `y26_complexity.py`. Untuk uji statistik atas hasil ini lihat [Statistik: Wilcoxon, Holm, effect size](../knowledge/statistics.md); untuk penghitungan *end-to-end* lihat [Penghitungan ByteTrack](../knowledge/counting.md).

## Orkestrator: `evaluate_all.py`

Satu perintah menjalankan seluruh rantai evaluasi BAB 4:

```bash
python evaluate_all.py --data dataset/data.yaml --split test --variants all   # → eval_out/
```

Untuk tiap varian, secara berurutan: (1) metrik global via validator Ultralytics (kecuali `--skip-global`); (2) *cache* prediksi mentah kepala *one-to-one* (`cache_<V>.npz`, dipakai ulang bila sudah ada, kecuali `--refresh-cache`); (3) AP terstratifikasi per (kelas × dimensi × strata). Setelah semua varian terkumpul, dijalankan uji Wilcoxon (`run_wilcoxon_suite`) untuk metrik `ap5095` dan `ap50`. `register_ham()` dipanggil di awal `main()` agar bobot ber-HAM dapat dimuat (lihat [Injeksi kode](../architecture/code-injection.md)).

| Tahap | Fungsi | Sumber |
|---|---|---|
| Metrik global P/R/F1/mAP | `global_val()` | `evaluate_all.py` |
| Cache prediksi mentah | `collect_cache()` / `load_cache()` | `y26_strata.py` |
| AP per (kelas × strata) | `stratified_ap()` | `y26_strata.py` |
| Uji Wilcoxon + Holm | `run_wilcoxon_suite()` | `y26_stats.py` |
| Tabel kompleksitas 3.7 | `static_complexity()` + `inference_cost()` + `training_stats()` | `y26_complexity.py` |

## 1. Metrik deteksi global (P, R, F1, mAP — Pers. 3.8–3.11)

`global_val()` memanggil `YOLO.val(...)` (validator Ultralytics standar, jalur *predictor* + NMS-free bawaan) pada `--split test`, imgsz 640, lalu membaca `results_dict`: presisi `metrics/precision(B)`, *recall* `metrics/recall(B)`, `metrics/mAP50(B)`, `metrics/mAP50-95(B)`. F1 dihitung eksplisit sebagai `2·P·R/(P+R)` (Pers. 3.10) dengan penjaga pembagi. Keluaran: `eval_out/global_metrics.csv` (satu baris per varian).

Angka global ini dipakai untuk gambaran menyeluruh dan *sanity check*, **bukan** sebagai unit uji statistik. Pada P7 (status §15) mAP50-95 test kedelapan varian berhimpit 0,522–0,538, sehingga sinyal perbedaan justru muncul saat dipecah per strata (Bagian 3).

## 2. Atribut strata (diturunkan komputasional)

Ketiga dimensi diturunkan dari *bounding box ground truth* di ruang *letterbox* 640 yang sama dengan ruang deteksi — tanpa anotasi manual tambahan (Subbab 3.3.3). Fungsi `gt_attributes()` menghasilkan tier per-GT (ukuran, oklusi) dan per-citra (densitas). Ambang tier adalah **invarian metodologis terkunci** (lihat [Invarian metodologi](../rules/methodology-invariants.md)):

| Dimensi | Ukuran atribut | Ambang (konstanta kode) | Tier (narasi) |
|---|---|---|---|
| Ukuran | luas kotak, konvensi MS COCO | `SIZE_EDGES = (32², 96²)` = (1024, 9216) px² | small < 32² ≤ medium < 96² ≤ large |
| Oklusi | proksi Pers. 3.1: oᵢ = maxⱼ≠ᵢ IoU(bᵢ, bⱼ) | `OCC_EDGES = (0.10, 0.35)` | no < 0,10 ≤ partial < 0,35 ≤ heavy |
| Densitas | jumlah objek per citra | `DEN_EDGES = (10, 26)` | sparse < 10 ≤ medium < 26 ≤ dense |

Catatan implementasi: tier dihitung via `np.digitize(x, edges)` → {0,1,2}. Oklusi memakai `box_iou` Ultralytics dengan diagonal dinolkan lalu `iou.max(1)` per citra (persis Pers. 3.1). Ambang densitas 26 selaras narasi BAB 1 (">25 objek per frame"); ambang oklusi 0,10/0,35 adalah keputusan implementasi yang wajib dilaporkan di BAB 3/4.

## 3. AP per (kelas × strata) — protokol gaya COCO

Ini bagian terpenting: **sel (kelas × strata) inilah unit pasangan uji Wilcoxon** (Subbab 3.11.4). `stratified_ap()` menghitung AP50 dan AP50-95 untuk setiap kombinasi (kelas × dimensi × strata), plus baris `global` yang **dikecualikan** dari uji.

Aturan pencocokan bergaya COCO (`_match_image`, greedy per urutan *confidence*):

- **Ignore GT di luar strata** — GT yang tidak termasuk strata ditandai *ignore*: bukan target positif, bukan penalti.
- **Prediksi tercocok ke GT ignore ikut di-ignore** — tidak dihitung TP maupun FP.
- **Khusus dimensi ukuran**, prediksi *tak tercocok* yang luasnya di luar rentang strata juga di-ignore (padanan filter area `COCOeval`, argumen `det_ig_extra`).
- **Dimensi densitas bersifat per-citra** → dievaluasi sebagai subset citra (`img_keep`), bukan ignore per-GT.

AP memakai interpolasi **101 titik** (`_ap101`, `np.linspace(0,1,101)`); rentang IoU `IOU_THRS = np.arange(0.50, 0.96, 0.05)` (sepuluh ambang 0,50–0,95 langkah 0,05). AP50 = AP pada IoU 0,50; AP50-95 = `nanmean` seluruh ambang. Sel dengan `n_gt = 0` menghasilkan `NaN` dan gugur dari analisis.

Cache mentah (`collect_cache`) berasal dari *forward* langsung `DetectionModel` mode eval → `(B, 300, 6)` `[xyxy, conf, cls]` di ruang *letterbox* 640; GT ditransformasi via `_letterbox` bersama (lihat [Analisis NMS-free](../knowledge/nmsfree-analysis.md)). Format npz: `pred (P,7)=[img,x1,y1,x2,y2,conf,cls]`, `gt (G,6)=[img,x1..y2,cls]`.

Keluaran: `eval_out/strata_ap.csv` (kolom `variant, class, dim, stratum, n_gt, AP50, AP50_95`). Pada P7, jumlah sel non-kosong pembanding = **n = 34** — itulah panjang vektor pasangan Wilcoxon per hipotesis. Interpretasi statistiknya (tiga hipotesis utama V8–V1, V4–V1, V8–V5; sekunder + Holm; `rank_biserial` Pers. 3.15) dibahas di [Statistik](../knowledge/statistics.md).

## 4. Kompleksitas & efisiensi (Tabel 3.7)

Menjawab masukan pembimbing: selain mAP dan FPS, laporkan biaya model kedelapan varian. Dua sumber angka bersatu di `y26_complexity.py`:

- **Statik & inferensi** (`static_complexity` + `inference_cost`): jumlah parameter (`get_num_params`), GFLOPs (`get_flops`), ukuran berkas bobot (MB), FPS + latensi + VRAM inferensi puncak (batch 1, FP16 di CUDA, 10 *warmup* + 50 iterasi).
- **Pelatihan** (`ComplexityCallback`): merekam VRAM alokasi/*reserved* puncak, jam latih, dan jumlah epoch ke `<save_dir>/complexity_train.json`. Callback dipasang otomatis di `train_ablation.py` (`add_callback("on_train_start"/"on_train_end", ...)`). `training_stats()` membacanya, dengan *fallback* ke `results.csv` bila JSON tidak ada.

Rakit tabel: `python y26_complexity.py --runs runs_tesis --data dataset/data.yaml --variants all` → `eval_out/complexity.csv` (kolom `variant, params_M, gflops, size_MB, peak_gpu_train_gb, peak_gpu_infer_gb, train_hours, epochs, fps, latency_ms`). Nilai VRAM latih P5 tercatat langsung di `complexity_train.json` tiap varian (varian ber-P2 8,52–8,64 GB; non-P2 ~5 GB — lihat [Progres](../status/progress.md)).

## 5. Penghitungan (counting) — MAPE hanya y > 0

Metrik penghitungan MAE, RMSE, MAPE (Pers. 3.12–3.14) dihitung pada tahap integrasi ByteTrack, **bukan** di `evaluate_all.py`. Aturan invarian: **MAPE dihitung hanya pada interval dengan y_t > 0**, dan proporsi interval yang dikecualikan wajib dilaporkan (menghindari pembagian nol). Pejalan kaki dikecualikan dari penghitungan (objek konteks). Detail pipa video, garis virtual per arah/per kelas, dan format keluaran ada di [Penghitungan ByteTrack](../knowledge/counting.md).

## 6. Keluaran `eval_out/` (bahan mentah BAB 4 — jangan dihapus/timpa)

| Berkas | Isi |
|---|---|
| `global_metrics.csv` | P, R, F1, mAP50, mAP50-95 per varian (Pers. 3.8–3.11) |
| `strata_ap.csv` | AP50 & AP50-95 per varian × kelas × dimensi × strata (unit Wilcoxon) |
| `wilcoxon_ap5095.csv` | uji AP50-95: `family, W, p, p_holm, rank_biserial, signif_5pct`, dll. |
| `wilcoxon_ap50.csv` | uji serupa untuk AP50 |
| `wilcoxon_info.json` | metadata unit + daftar tiga hipotesis utama + α |
| `cache_<V>.npz` | prediksi mentah kepala one-to-one (dipakai ulang, hemat inferensi) |
| `complexity.csv` | Tabel 3.7 (dari `y26_complexity.py`) |

## 7. Temuan: tier oklusi *heavy* nyaris kosong

Persiapan P8 mengungkap bahwa strata oklusi *heavy* (o ≥ 0,35) praktis kosong: **val 0/4.094** GT (maks proksi hanya 0,286), **test 8/2.600**, train 62/16.786. Konsekuensinya sel `occlusion/heavy` gugur dari matriks Wilcoxon di val, dan pada P7 sel oklusi/*heavy* di test hanya n = 8 (tak bermakna). Ini indikasi kuat bahwa **proksi box-IoU (Pers. 3.1) meremehkan oklusi perseptual** — objek yang tampak sangat teroklusi bagi manusia belum tentu ber-IoU tinggi antar-kotak.

Ambang 0,10/0,35 **TERKUNCI** (invarian metodologi); keputusan penyesuaian—bila perlu—menunggu angka *agreement* validasi manual (kit `make_oklusi_sample.py` → `manual_oklusi.csv`, fungsi `occlusion_agreement()` di `y26_strata.py`) dan diskusi pembimbing. Ini bahan diskusi BAB 4, bukan alasan mengubah kode secara sepihak. Lihat [Validasi oklusi](../playbooks/occlusion-validation.md) dan [Keputusan pending](../status/pending-decisions.md).

## Tautan terkait

- [Statistik: Wilcoxon, Holm, effect size](../knowledge/statistics.md) — apa yang dilakukan atas `strata_ap.csv`.
- [Penghitungan ByteTrack](../knowledge/counting.md) — MAE/RMSE/MAPE end-to-end.
- [Analisis NMS-free](../knowledge/nmsfree-analysis.md) — sumber cache mentah one-to-one yang sama.
- [Dataset](../knowledge/dataset.md) — komposisi kelas & split yang mengisi sel strata.
- [Invarian metodologi](../rules/methodology-invariants.md) — ambang tier & aturan MAPE yang tak boleh dilonggarkan.
- [Playbook evaluasi](../playbooks/evaluate.md) — langkah menjalankan rantai ini.
