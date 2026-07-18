# Analisis Interaksi NMS-free (DR/CM/Stabilitas) — NMS-free Interaction Analysis

> **EN — TL;DR:** The thesis' second (analytical) novelty pillar: an empirical probe of how HAM/P2/DALW interact with YOLO26's one-to-one NMS-free head. Three instruments — Duplicate Rate (Eq. 3.6, τ=0.25; ~1 healthy, >1 duplicates, <1 misses), Confidence Margin (Eq. 3.7), and cross-epoch assignment stability S(t) (A-10). All measured from the **raw one-to-one head** (direct `DetectionModel` eval forward → `(B,300,6)` in letterbox-640 space), never the standard predictor. Matching is IoU≥0.5 + class-aware. Outputs land in `nmsfree_out/`; correctness is guarded by tests U1–U5. HAM and P2 remain **instruments**, never claimed as novelty.

## Peran dalam framing dua pilar

Subbab ini adalah **pilar kebaruan analitis** (lihat [Framing kebaruan](./thesis-framing.md)): *penyelidikan empiris pertama* atas interaksi modifikasi (HAM, P2, Pembobotan *Loss* Berbasis Densitas/DALW) dengan mekanisme *one-to-one NMS-free* bawaan YOLO26. Ia tidak mengeklaim komponen baru — ia **mengukur** apakah dan bagaimana modifikasi memengaruhi kesehatan penetapan *one-to-one* (satu prediksi per objek tanpa NMS). Analisis difokuskan pada varian ber-P2 (**V3, V5, V7, V8**) plus *baseline* **V1**, karena P2 yang paling berpotensi mengganggu jumlah *anchor* dan pencocokan.

Kode inti: `y26_nmsfree.py` (instrumentasi + `NMSFreeProbe` callback), `analyze_nmsfree.py` (analisis pasca-latih antarvarian + *sweep* τ + plot), `test_nmsfree.py` (uji U1–U5). Peta ke tesis: **Subbab 3.7** (definisi metrik) dan **A-10** (formalisasi stabilitas + sensitivitas τ).

| File | Covers |
|---|---|
| `y26_nmsfree.py` | Definisi & pengukuran DR/CM/S(t); matcher; akses kepala *one-to-one* mentah; `NMSFreeProbe` callback per-epoch |
| `analyze_nmsfree.py` | Orkestrasi antarvarian pasca-latih → `nmsfree_out/` (summary, tau_sweep, per-image, plot) |
| `test_nmsfree.py` | U1–U5: kebenaran matcher/DR/CM, rumus S(t), forward internal tanpa merusak BN, determinisme, pipeline penuh |

## Tiga metrik

### 1. Duplicate Rate — DR(τ) (Pers. 3.6)

Rumus: **DR(τ) = (1/M) Σ_k N_k(τ)**, dengan M = jumlah objek *ground truth* (GT) ber-label, dan N_k(τ) = banyaknya prediksi ber-*confidence* > τ yang **tercocokkan** ke objek k. Ambang utama **τ = 0,25** (Tabel 3.4; `tau_main=0.25`).

Interpretasi (didokumentasikan di `y26_nmsfree.py` docstring):
- **DR ≈ 1** → sehat: satu prediksi kuat per objek, sesuai janji *one-to-one*.
- **DR > 1** → duplikasi: NMS-free gagal menekan prediksi ganda pada objek yang sama.
- **DR < 1** → ada objek terlewat (*miss*) pada ambang τ.

Selain DR, akumulator melaporkan `miss_frac` (fraksi objek tanpa prediksi tercocok) dan `dup_frac` (fraksi objek dengan ≥2 prediksi tercocok). Sumber: `DRCMAccumulator.update()`/`.summary()`.

### 2. Confidence Margin — CM_k (Pers. 3.7)

Rumus: **CM_k = conf(p_k^(1)) − conf(p_k^(2))**, selisih *confidence* prediksi terbaik dan terbaik-kedua yang tercocok ke objek k. Dihitung atas **semua** prediksi tercocok ke k **tanpa filter τ** (τ hanya menyaring DR). Bila prediksi kedua tidak ada, conf(p^(2)) = 0 sehingga CM_k = conf(p^(1)) — pemenang tunggal yang jelas maksimal. Margin besar menandakan pemisahan pemenang yang tegas (indikator *one-to-one* stabil). Ringkasan melaporkan `cm_mean`, `cm_median`, `cm_p10`.

### 3. Stabilitas assignment antar-epoch — S(t) (formalisasi A-10)

Rumus: **S(t) = (1/M_probe) Σ_k 1[ a_k(t) = a_k(t−1) ]**, dengan a_k(t) = indeks *anchor* (rata seluruh skala) yang dipilih *assigner* kepala *one-to-one* (STAL, topk akhir 1) untuk objek k pada akhir epoch t. Dihitung pada **himpunan probe TETAP** dari data validasi (letterbox 640, **tanpa augmentasi**) agar perbandingan antar-epoch adil.

Konvensi (dikodekan di `stability()`):
- a_k boleh bernilai **∅** (objek tak ter-*assign*); kesamaan **∅ == ∅ dihitung stabil**.
- Fraksi ter-*assign* (`assigned_frac`) dan rata *anchor* per GT (`anchors_per_gt`, harusnya ≈1 untuk *one-to-one*) dilaporkan terpisah.
- Epoch pertama menghasilkan NaN (tak ada pembanding `prev`).

Diukur dengan **menggali assigner internal** `get_assigned_targets_and_loss` (via `extract_o2o_assignments()`), bukan antarmuka standar — konsisten dengan versi ultralytics **8.4.92** yang dikunci (lihat [Environment](./environment.md) dan [Code injection](../architecture/code-injection.md)). Determinisme dijamin dengan memilih *anchor* terkecil (`min(...)`) saat sebuah GT menerima lebih dari satu *anchor*.

> **Status A-10:** formalisasi S(t) di atas sudah diimplementasikan, tetapi **metrik stabilitas belum sepenuhnya diformalkan di naskah** dan **sensitivitas τ ∈ {0,10; 0,25; 0,50}** masih menjadi keputusan tertunda. Lihat [Pending decisions — A-10](../status/pending-decisions.md).

## Aturan pencocokan prediksi ↔ GT

Semua metrik berpijak pada satu `match_predictions()` yang sama:
- Tiap prediksi dipetakan ke **satu** objek GT dengan **IoU tertinggi**, dengan syarat **IoU ≥ 0,5** (`iou_thr`, default 0.5) dan **kelas sama** (`class_aware=True`).
- Beberapa prediksi boleh menunjuk objek GT yang sama — itulah duplikasi yang diukur DR.
- Pencocokan gagal (IoU < ambang atau kelas beda) → indeks −1 (tidak tercocok).

## Diukur dari kepala one-to-one MENTAH

Instrumentasi **sengaja melewati predictor standar** ultralytics. `evaluate_dr_cm()` memanggil *forward* langsung `DetectionModel` dalam mode `eval()`, yang pada model *end2end* mengembalikan **`(B, 300, 6)` = `[xyxy, conf, cls]`** pada **ruang letterbox 640**. GT ditransformasikan ke ruang yang sama lewat `_letterbox()` bersama, sehingga IoU dihitung konsisten. Ini persis frasa "menggali keluaran kepala *one-to-one*" pada Subbab 3.7.

Untuk stabilitas, dict dual-head `{'one2many','one2one'}` diperoleh via `train_format_forward()` — trik penting: **hanya flag `training` milik modul `Detect` yang dinaikkan**, bukan `.train()`, sehingga statistik BatchNorm (running mean/var) **tidak berubah**. Konvensi ini juga dijelaskan di [Code injection](../architecture/code-injection.md) ("Konvensi akses kepala one-to-one mentah").

## Keluaran `nmsfree_out/`

`analyze_nmsfree.py` (default `--variants V1,V3,V5,V7,V8`, `--split test`, `--tau 0.25`, `--iou 0.5`) menulis:

| Berkas | Isi |
|---|---|
| `summary.csv` | DR(τ=0,25), `miss`, `dup`, `coverage`, CM (mean/median/p10) per varian + `dDR_vs_V1`, `dCM_vs_V1` |
| `tau_sweep.csv` | DR untuk rentang τ (0,05…0,90) — analisis sensitivitas τ (A-10) |
| `<V>.json` | Ringkasan lengkap per varian (dari `save_summary`) |
| `<V>_per_image.csv` | DR/CM per citra — **bahan uji Wilcoxon berpasangan** (lihat [Statistics](./statistics.md)) |
| `dr_vs_tau.png` | Kurva sensitivitas τ semua varian (garis acuan DR=1 dan τ=0,25) |
| `cm_hist.png` | Distribusi Confidence Margin semua varian |

Folder `nmsfree_out/` adalah **bahan mentah BAB 4** — jangan dihapus/ditimpa (aturan invarian, lihat [Methodology invariants](../rules/methodology-invariants.md)). Status: sudah terisi pada **P7 (18 Jul 2026)** untuk V{1,3,5,7,8} beserta `dr_vs_tau.png` dan `cm_hist.png`.

### Probe per-epoch selama training

Selain analisis pasca-latih, `NMSFreeProbe` (callback `on_fit_epoch_end`, dipasang `train_ablation.py`) menulis **`runs_tesis/<V>/nmsfree_probe.csv`** tiap epoch dengan kolom: `epoch, stability, assigned_frac, anchors_per_gt, DR, miss_frac, dup_frac, cm_mean, cm_median`. Callback **tidak pernah mematikan training** (seluruh isi dibungkus `try/except`) dan memakai `unwrap_model` (ganti nama `de_parallel` di 8.4.92 — bug ini diperbaiki 13 Jul 2026, lihat [Progress](../status/progress.md)).

## Uji U1–U5 (`test_nmsfree.py`)

Wajib lulus sebelum menaruh kepercayaan pada angka NMS-free apa pun:

| Uji | Memverifikasi |
|---|---|
| U1 | `match_predictions` + DR/CM pada kasus sintetis bernilai pasti (mis. DR=1,5; CM mean=0,55) |
| U2 | Rumus S(t), termasuk konvensi ∅ == ∅ dan NaN pada epoch pertama |
| U3 | `train_format_forward` menghasilkan dict dual-head **tanpa** mengubah statistik BN |
| U4 | Ekstraksi assignment *one-to-one* deterministik (bobot identik → S = 1,0; ~1 anchor/GT) |
| U5 | Pipeline `evaluate_dr_cm` *end-to-end* pada dataset mini sintetis di disk |

Jalankan: `python test_nmsfree.py` (semua kasus berurutan) atau satu kasus via impor, mis. `python -c "from test_nmsfree import u1_matcher; u1_matcher()"`.

## Catatan angka (desimal)

Ambang dan nilai narasi memakai koma (τ = **0,25**; IoU = **0,5**); nilai CLI/JSON apa adanya (`--tau 0.25`, `iou_thr=0.5`). Ambang τ = 0,25 **terkunci** sebagai Pers. 3.6/Tabel 3.4; sensitivitas τ {0,10; 0,25; 0,50} hanyalah *sweep* pelaporan, bukan penggantian nilai utama.

## Tautan terkait

- [Code injection](../architecture/code-injection.md) — HAM namespace injection, akses kepala *one-to-one* mentah, `register_ham()`.
- [Pending decisions — A-10](../status/pending-decisions.md) — formalisasi metrik stabilitas *assignment* + sensitivitas τ.
- [Framing kebaruan](./thesis-framing.md) — dua pilar; pilar analitis dijelaskan di sini.
- [Statistics](./statistics.md) — Wilcoxon berpasangan yang mengonsumsi `<V>_per_image.csv`.
- [Environment](./environment.md) — kunci ultralytics 8.4.92 (alasan menyalin `get_assigned_targets_and_loss`).
