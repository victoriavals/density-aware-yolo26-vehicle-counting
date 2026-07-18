# Rantai Modul & Alur Data Eksperimen — Module Chain & Experiment Data Flow

> **EN — TL;DR:** Four entry points form a linear pipeline: `train_ablation.py` writes `runs_tesis/<V>/` (results.csv, weights, nmsfree_probe.csv, complexity_train.json), then `evaluate_all.py` → `eval_out/`, `analyze_nmsfree.py` → `nmsfree_out/`, and `y26_counting.py` → `counting_out/`. Module import chain: `y26_modules` ← `y26_variants` ← `train_ablation`; `y26_nmsfree` supplies `_letterbox`/`split_image_paths` to `y26_strata`; `y26_stats` consumes the `stratified_ap` rows. The `runs_tesis/`, `eval_out/`, `nmsfree_out/`, `counting_out/` folders are BAB 4 raw material — never overwrite or delete them.

Dokumen ini menjelaskan bagaimana data mengalir antar-skrip selama eksperimen (dari pelatihan sampai counting) sekaligus rantai *import* modul yang menghubungkannya. Fokusnya "apa membaca apa, apa menulis apa" — bukan mekanisme injeksi kode (lihat [Injeksi kode](./code-injection.md)) atau pembangunan varian (lihat [Varian & transfer bobot](./variants.md)). Semua klaim di sini di-*grounding* pada `train_ablation.py`, `evaluate_all.py`, dan CLAUDE.md §14.

## 1. Peta empat entry point

Ada empat skrip yang dijalankan langsung dari CLI; sisanya (`y26_*.py`) adalah modul pustaka yang diimpor. Urutannya wajib: hasil pelatihan menjadi masukan bagi ketiga skrip evaluasi.

| Entry point | Membaca | Menulis | Rujukan |
|---|---|---|---|
| `train_ablation.py` | `dataset/data.yaml`, `dalw_best.json`, `inits/{V}_init.pt` | `runs_tesis/<V>/` | Subbab 3.8–3.9 |
| `evaluate_all.py` | `runs_tesis/<V>/weights/best.pt`, `dataset/data.yaml` | `eval_out/` | Subbab 3.11 |
| `analyze_nmsfree.py` | `runs_tesis/<V>/weights/best.pt`, `runs_tesis/<V>/nmsfree_probe.csv` | `nmsfree_out/` | Subbab 3.7 |
| `y26_counting.py` | video uji, `runs_tesis/V8/weights/best.pt`, `gt_<nama>.csv` | `counting_out/` | Subbab 3.10, 3.11.3 |

## 2. Diagram alur data

```
                         dalw_best.json ──(α=1,0 σ=0,1)──┐
                                                         ▼
   dataset/data.yaml ───────────────────────────► train_ablation.py
   inits/{V}_init.pt ──(transfer bobot COCO)─────►      │
                                                        │ per varian V1..V8
                                                        ▼
                                     runs_tesis/<V>/
                                       ├─ results.csv          (kurva per-epoch)
                                       ├─ weights/{best,last}.pt
                                       ├─ nmsfree_probe.csv     (probe A-10, per epoch)
                                       └─ complexity_train.json (Tabel 3.7, revisi pembimbing)
                                                        │
              ┌─────────────────────────────┬──────────┴───────────────┐
              ▼                              ▼                          ▼
      evaluate_all.py               analyze_nmsfree.py           y26_counting.py
              │                              │                          │
              ▼                              ▼                          ▼
         eval_out/                     nmsfree_out/                counting_out/
         ├ global_metrics.csv          ├ summary.csv               ├ counts_per_interval.csv
         ├ strata_ap.csv               ├ tau_sweep.csv             ├ events.csv
         ├ wilcoxon_ap5095.csv         ├ dr_vs_tau.png             ├ counting_errors.csv
         ├ wilcoxon_ap50.csv           ├ cm_hist.png               └ summary.json
         ├ wilcoxon_info.json          └ <V>_per_image.csv           (MAE/RMSE/MAPE/FPS)
         ├ complexity.csv
         └ cache_<V>.npz (dipakai ulang)
```

### 2.1 `train_ablation.py` → `runs_tesis/<V>/`

`train_once()` membangun model varian (via `build_model` dari `y26_variants`), menerapkan `apply_dalw(α, σ)` bila `cfg["dalw"]` benar, lalu memasang dua callback sebelum `model.train()`:

- `ComplexityCallback` (dari `y26_complexity`) pada `on_train_start`/`on_train_end` → menulis `complexity_train.json` di `save_dir` (parameter, GFLOPs, VRAM latih, waktu latih; bahan Tabel 3.7 revisi pembimbing).
- `NMSFreeProbe` (dari `y26_nmsfree`) pada `on_fit_epoch_end` bila `--probe > 0` (default 64) → menulis `nmsfree_probe.csv` per epoch (epoch, S(t) stabilitas *assignment*, assigned_frac, anchors/GT, DR, miss, dup, CM). Ini bahan mentah A-10; lihat [Analisis NMS-free](../knowledge/nmsfree-analysis.md).

Nilai α dan σ tidak di-*hardcode*: `main()` membaca `dalw_best.json` (hasil grid search P3, pemenang α=1,0 σ=0,1 / JSON `alpha:1.0 sigma:0.1`) kecuali di-*override* CLI. Grid search sendiri (`--tune-dalw`) menulis `dalw_best.json` via `tune_dalw()` yang melatih V8 sembilan kali (60 epoch) lalu membaca mAP50-95 terbaik dari tiap `results.csv` melalui `read_best_map()`.

⚠️ `--project` WAJIB path ABSOLUT (gotcha `runs_dir` di CLAUDE.md §15 P3), jika tidak Ultralytics menulis ke direktori yang salah menurut `settings.json`.

### 2.2 `evaluate_all.py` → `eval_out/`

Untuk tiap varian, `main()` melakukan tiga hal berurutan:

1. `global_val()` — memanggil validator Ultralytics (`m.val`) untuk P, R, F1, mAP50, mAP50-95 → `global_metrics.csv` (Pers. 3.8–3.11).
2. `collect_cache()` (dari `y26_strata`) — men-*cache* prediksi mentah kepala one-to-one ke `cache_<V>.npz`, lalu memakainya ulang jika ada (`load_cache`) kecuali `--refresh-cache`. Ini menghemat inferensi ulang antar-*run*.
3. `stratified_ap()` (dari `y26_strata`) — AP50 & AP50-95 per (kelas × ukuran/oklusi/densitas) → dikumpulkan ke `rows_by_variant`, ditulis via `save_strata_csv` ke `strata_ap.csv`.

Setelah semua varian, bila ≥2 varian tersedia, `run_wilcoxon_suite()` (dari `y26_stats`) mengonsumsi `rows_by_variant` untuk metrik `ap5095` dan `ap50` → `wilcoxon_ap5095.csv` + `wilcoxon_ap50.csv` (kolom termasuk `rank_biserial` Pers. 3.15, `W_plus`, `W_minus`, `p_holm`) dan metadata `wilcoxon_info.json`. `register_ham()` dipanggil di awal `main()` agar `torch.load` menemukan kelas HAM (lihat [Injeksi kode](./code-injection.md)). Protokol statistik — 3 hipotesis utama tanpa koreksi + sekunder Holm — dijabarkan di [Statistik](../knowledge/statistics.md) dan [Invarian metodologi](../rules/methodology-invariants.md).

### 2.3 `analyze_nmsfree.py` → `nmsfree_out/`

Menganalisis Duplicate Rate (DR, Pers. 3.6, τ=0,25) dan Confidence Margin (CM, Pers. 3.7) pasca-latih pada varian ber-P2 (fokus V3/V5/V7/V8, ditambah V1 sebagai pembanding). Keluaran: `summary.csv` (+Δ terhadap V1), `tau_sweep.csv` + `dr_vs_tau.png` (sensitivitas τ), `cm_hist.png`, dan `<V>_per_image.csv` (DR/CM per citra, bahan Wilcoxon berpasangan). Detail metrik di [Analisis NMS-free](../knowledge/nmsfree-analysis.md).

### 2.4 `y26_counting.py` → `counting_out/`

Evaluasi *end-to-end* RQ5: ByteTrack (`supervision` 0.29.1, WAJIB <0.30) + *virtual line crossing* per arah/kelas (pejalan kaki dikecualikan). Keluaran `summary.json` memuat MAE/RMSE/MAPE + FPS; **MAPE hanya pada y_t > 0** dengan proporsi eksklusi dilaporkan. Butuh video uji + `gt_<nama>.csv`; ambang target (A-02) masih menunggu pembimbing. Detail di [Counting](../knowledge/counting.md) dan playbook belum-siap di [Validasi & counting](../playbooks/occlusion-validation.md).

## 3. Rantai dependensi modul (import)

Ini bukan alur data melainkan *urutan import* — penting saat mengubah satu modul agar tidak memutus modul di hilirnya.

```
y26_modules ◄── y26_variants ◄── train_ablation
     ▲                                  
     ├── y26_nmsfree ── (_letterbox, split_image_paths) ──► y26_strata
     ├── y26_counting                                          │
     └── y26_complexity                          (baris stratified_ap)
                                                                ▼
                                                            y26_stats
```

- **`y26_modules` ← `y26_variants` ← `train_ablation`** — `y26_variants` mengimpor `register_ham` dari `y26_modules` (baris 32); `train_ablation.train_once` mengimpor `build_model`/`VARIANTS` dari `y26_variants`. HAM harus teregistrasi sebelum YAML varian di-*parse*.
- **`y26_nmsfree` → `y26_strata`** — `y26_strata` mengimpor `_letterbox` dan `split_image_paths` dari `y26_nmsfree` (baris 34). Keduanya menyediakan transformasi ke ruang letterbox 640 dan daftar citra per-split yang dipakai `collect_cache`/`stratified_ap`. Konvensi akses kepala one-to-one mentah (`(B, 300, 6)` `[xyxy, conf, cls]`) dijelaskan di [Injeksi kode §akses one-to-one](./code-injection.md).
- **`y26_stats` mengonsumsi `stratified_ap`** — `evaluate_all.py` meneruskan `rows_by_variant` (keluaran `stratified_ap`) ke `run_wilcoxon_suite`. Unit uji = AP per (kelas × strata), baris `dim == "global"` dikecualikan.
- **`register_ham()` tersebar** — dipanggil juga oleh `y26_nmsfree`, `y26_counting`, `y26_complexity`, dan `evaluate_all.py`. Setiap entry point yang membangun/memuat model ber-HAM WAJIB memanggilnya lebih dulu (invarian di [Injeksi kode](./code-injection.md)).

## 4. Aturan artefak: folder mentah BAB 4 JANGAN ditimpa

`runs_tesis/`, `eval_out/`, `nmsfree_out/`, `counting_out/`, `inits/`, `dataset/`, dan `bukti_split_*.csv` adalah bahan mentah BAB 4 — sumber angka yang akan mengisi 18 placeholder numerik. Jangan menghapus, menimpa, atau me-*regenerate* tanpa persetujuan Naufal. `evaluate_all.py` sengaja memakai ulang `cache_<V>.npz` (kecuali `--refresh-cache`) agar prediksi mentah stabil antar-*run*. Backup sebelum langkah destruktif dicontohkan di §15 P7 (`backups/runs_tesis_20260718_1356.tar.gz`). Aturan lengkap ada di [Invarian metodologi](../rules/methodology-invariants.md) dan [Logging & status](../rules/logging-and-status.md).

## 5. Pranala terkait

- Menjalankan pipeline langkah demi langkah: [Playbook jalankan eksperimen](../playbooks/run-experiment.md) dan [Playbook evaluasi](../playbooks/evaluate.md).
- Konsumsi keluaran ke naskah: [Playbook tulis BAB 4–5](../playbooks/write-bab4-5.md) dan [Status progres](../status/progress.md).
- Konsep di balik tiap keluaran: [DALW](../knowledge/dalw.md), [Analisis NMS-free](../knowledge/nmsfree-analysis.md), [Evaluasi](../knowledge/evaluation.md), [Statistik](../knowledge/statistics.md), [Counting](../knowledge/counting.md), [Dataset](../knowledge/dataset.md).
- Mekanisme di balik pembangunan model: [Injeksi kode](./code-injection.md), [Varian & transfer bobot](./variants.md).
- Keputusan terbuka yang menyentuh keluaran (A-01, A-02, A-10): [Keputusan pending](../status/pending-decisions.md).
