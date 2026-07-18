# Ikhtisar Proyek — Project Overview

> **EN — TL;DR:** Research codebase for a Master's thesis modifying YOLO26 for real-time vehicle counting on dense heterogeneous Jakarta traffic. Two novelty pillars only: (1) the *method* — Density-Aware Loss Weighting (DALW); (2) the *analysis* — first empirical study of how the modifications interact with the NMS-free one-to-one head. HAM and the P2 layer are **instruments, never novelty claims**. This file is documentation, not a build input — read [`AGENTS.md`](AGENTS.md) for the map and [`../status/progress.md`](status/progress.md) for live status.

Dokumen ini adalah pintu masuk ringkas ke basis pengetahuan `.agents/`. Sumber kebenaran tetap `CLAUDE.md` di root; halaman ini hanya merangkum dan menautkan. Bukan berkas yang dibangun/di-*compile* apa pun — murni dokumentasi bagi agen.

## Ikhtisar penelitian

Objek penelitian adalah lalu lintas heterogen padat pada CCTV Jakarta, yang menyulitkan detektor standar karena tiga hal saling menguatkan: dominasi objek kecil (kendaraan roda dua sekitar 8–16 piksel pada citra 640), oklusi tinggi antarobjek, dan kepadatan ekstrem (lebih dari 25 objek per frame). Tujuan umum tesis adalah mengembangkan dan mengevaluasi modifikasi YOLO26 untuk sistem penghitungan kendaraan *real-time*. Lima rumusan masalah membingkai pekerjaan: perancangan modifikasi yang kompatibel dengan paradigma *NMS-free* (RQ1), kontribusi tiap komponen lewat *ablation study* (RQ2), pengaruh P2 dan HAM terhadap kestabilan pencocokan *one-to-one* (RQ3), performa terstratifikasi menurut ukuran × oklusi × densitas (RQ4), dan akurasi *end-to-end* dengan ByteTrack terhadap standar penerapan praktis (RQ5, ambang konkret masih menunggu keputusan A-02).

Perlu dicatat bahwa rujukan YOLO26 (Sapkota et al.) masih berstatus *preprint* arXiv dan belum melalui *peer-review*; bahasa kehati-hatian ini wajib dipertahankan di seluruh naskah.

## Dua pilar kebaruan (ringkas)

Framing kebaruan terdiri atas tepat dua pilar dan tidak boleh diubah. Pilar metodologis adalah **Pembobotan *Loss* Berbasis Densitas** (DALW): densitas lokal ρᵢ → normalisasi ρ̂ᵢ = ρᵢ/(ρᵢ+1) → bobot wᵢ = 1 + α·ρ̂ᵢ → L = (1/N)Σ wᵢ·Lᵢ (Pers. 3.2–3.5). DALW melengkapi STAL bawaan YOLO26 — STAL bekerja saat penetapan label berbasis **ukuran**, DALW saat penghitungan *loss* berbasis **densitas**. Pilar analitis adalah penyelidikan empiris pertama atas interaksi modifikasi dengan mekanisme *one-to-one NMS-free*, diukur lewat *Duplicate Rate* (Pers. 3.6), *Confidence Margin* (Pers. 3.7), dan stabilitas *assignment* antar-epoch.

> **Aturan mutlak:** HAM dan Lapisan P2 adalah **instrumen**, bukan klaim kebaruan. YOLO26 sudah memiliki ProgLoss + STAL, sehingga setiap peningkatan diframe sebagai perbaikan atas *baseline* yang sudah kuat. Detail lengkap: [Framing kebaruan](knowledge/thesis-framing.md).

## Stack teknis singkat

| Komponen | Versi / Nilai | Catatan |
|---|---|---|
| Python | 3.11.9 (`.venv`) | Windows native; `\.venv\Scripts\python.exe` |
| PyTorch | 2.11.0+cu128 | CUDA 12.8, GPU aktif |
| Ultralytics | **8.4.92 (TERKUNCI)** | `DALWDetectionLoss` menyalin metode internal versi ini |
| supervision | 0.29.1 (WAJIB <0.30) | `sv.ByteTrack` dihapus di 0.30 |
| GPU | RTX 4060 Ti 8GB | terverifikasi `nvidia-smi` 13 Jul 2026 |

`test_smoke.py` (T1–T4) WAJIB lulus sebelum training apa pun. Rincian lingkungan dan gotcha ada di [Lingkungan](knowledge/environment.md).

## Peta berkas → subbab tesis

Diverifikasi dari `README.md` (bagian "Peta berkas → tesis") dan `CLAUDE.md` §13–§14.

| File | Covers | Rujukan tesis |
|---|---|---|
| `y26_modules.py` | Modul HAM (kaskade atensi kanal→spasial) + registrasi | Subbab 3.6.1, Gambar 3.3 |
| `y26_dalw.py` | Bobot densitas w=1+α·ρ̂ + suntikan ke *loss* dual-head | Subbab 3.6.3, Pers. 3.2–3.5 |
| `y26_variants.py` | Pembangkit YAML varian, transfer bobot COCO, registry V1–V8 | Subbab 3.6, 3.8, Tabel 3.3 |
| `train_ablation.py` | Runner pelatihan 8 varian + grid search α,σ + `ComplexityCallback` | Subbab 3.8–3.9, Tabel 3.3–3.4 |
| `download_dataset.py` | Unduh traffic-merged dari Roboflow + verifikasi split | Subbab 3.3 |
| `make_group_split.py` | Re-split grup deterministik (kamera×adegan×sesi) + `bukti_split_*.csv` | Subbab 3.3.2 |
| `test_smoke.py` | Uji kebenaran implementasi (T1–T4; jalankan pertama kali) | — |
| `y26_nmsfree.py` | Instrumentasi DR, CM, stabilitas *assignment* + probe callback | Subbab 3.7, Pers. 3.6–3.7, A-10 |
| `analyze_nmsfree.py` | Analisis pasca-latih antarvarian + sensitivitas τ + plot | Subbab 3.7, BAB 4 |
| `test_nmsfree.py` | Uji instrumentasi Tahap 2 (U1–U5) | — |
| `y26_strata.py` | Atribut strata + AP terstratifikasi protokol gaya COCO | Subbab 3.3.3, 3.11.1, Tabel 3.5 |
| `y26_stats.py` | Wilcoxon signed-rank + koreksi Holm + `rank_biserial` (Pers. 3.15) | Subbab 3.11.4 |
| `y26_counting.py` | ByteTrack + *virtual line crossing* + MAE/RMSE/MAPE | Subbab 3.10, 3.11.3 |
| `y26_complexity.py` | Tabel kompleksitas (parameter/GFLOPs/VRAM/FPS) | Tabel 3.7 (revisi pembimbing) |
| `evaluate_all.py` | Orkestrator evaluasi BAB 4 (global + strata + Wilcoxon) | Subbab 3.11 |
| `test_eval.py` | Uji evaluasi Tahap 3 (E1–E7) | — |
| `siapkan_counting.py` | Kit inspeksi video + template GT (persiapan P9) | Subbab 3.10 |
| `make_oklusi_sample.py` | Kit anotasi manual oklusi (persiapan P8) | Subbab 3.3.3 |

Rantai injeksi dan dependensi modul dijelaskan di [Injeksi kode](architecture/code-injection.md), [Alur data](architecture/data-flow.md), dan [Varian](architecture/variants.md).

## Layout repo

Struktur folder utama. Folder bertanda **[MENTAH BAB 4]** adalah bahan mentah hasil eksperimen — jangan disarankan hapus/timpa (aturan `CLAUDE.md` §14).

| Path | Isi |
|---|---|
| `*.py` (root) | Skrip patch/injeksi di atas ultralytics terpasang (tanpa fork) |
| `dataset/` | **[MENTAH]** Split aktif hasil re-split grup 70/20/10 (2.372/679/338 citra) |
| `bukti_split_grup.csv`, `bukti_split_citra.csv` | **[MENTAH]** Bukti *group split* untuk lampiran tesis |
| `inits/` | **[MENTAH]** Bobot transfer COCO per varian (`{V}_init.pt`) |
| `runs_tesis/` | **[MENTAH BAB 4]** Hasil latih per varian (`results.csv`, `weights/`, `nmsfree_probe.csv`, `complexity_train.json`) |
| `eval_out/` | **[MENTAH BAB 4]** `global_metrics.csv`, `strata_ap.csv`, `wilcoxon_*.csv`, `cache_V*.npz` |
| `nmsfree_out/` | **[MENTAH BAB 4]** `summary.csv`, `tau_sweep.csv`, per-image CSV, plot |
| `counting_out/` | **[MENTAH BAB 4]** counts/events/errors + `summary.json` (MAE/RMSE/MAPE/FPS) |
| `dalw_best.json` | α, σ terpilih dari grid search |
| `anotasi_oklusi/`, `video_uji/` | Kit persiapan P8/P9 (input anotasi & counting) |
| `hasil/` | Ringkasan naratif per prompt (`grid_search.md`, `catatan_run.md`, `ringkasan_evaluasi.md`) |
| `logs/` | Log job ber-stempel waktu + `sesi.log` |
| `.agents/`, `.claude/` | Basis pengetahuan (dokumen ini) & skill |

## Snapshot status

Eksperimen mengikuti 10 prompt berurutan (adaptasi Windows-native). Ringkas per 18 Jul 2026:

- **P1–P7 + persiapan P8/P9 ✅ SELESAI.** Lingkungan, dataset (*group split*), grid search (pemenang α=1,0 σ=0,1; `0.6670` mAP50-95 val), 8 varian terlatih (batch 16 penuh, 0 OOM, 0 crash), evaluasi terstratifikasi + Wilcoxon + NMS-free.
- **Hasil utama P7** (AP50-95 per kelas×strata, n=34): V8–V1 p=0,478 (tidak signifikan); V4–V1 p=0,469 (tidak signifikan, median −0,013); **V8–V5 p=0,0125 r=+0,486 signifikan**. Kesimpulan awal: DALW komplementer/kondisional atas HAM+P2, tidak berdiri sendiri. Ini **memicu keputusan A-01** (redaksi bila hasil tidak signifikan).
- **P8 & P10 BELUM.** Validasi oklusi manual (kit siap) → penghitungan ByteTrack RQ5 (butuh video uji + `gt_<nama>.csv` + ambang A-02 dari pembimbing) → konsolidasi placeholder + penulisan BAB 4–5.

Status penuh, tabel per-prompt, dan angka detail: [Progres eksperimen](status/progress.md). Keputusan yang menggantung: [Keputusan pending](status/pending-decisions.md).

## Diskrepansi terbuka (jangan diselesaikan sendiri)

Beberapa item wajib dikonfirmasi ke Naufal + pembimbing dan **tidak boleh diputuskan agen**:

- **Judul tesis berbeda** antara `CLAUDE.md` §1 (menekankan "DETEKTOR *NMS-FREE*" + "PELACAKAN BYTETRACK", tanpa HAM/P2 di judul) dan dokumen fisik `TESIS_BAB1-3_REVISI_PEMBIMBING` (menaruh "ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2" di judul).
- **Jumlah sitasi** (§9 menyebut 27; dokumen revisi memuat [1]–[30]).
- **Sumber dataset Roboflow** (workspace `sahabats-workspace/...-nkdvt` vs sitasi [17] `naufalfirdaus/...`).
- **Label GPU** (masih ada lokasi bertuliskan "RTX 3060" yang wajib jadi "RTX 4060 Ti 8GB").

Semua item ini dilacak di [TODO dokumen](status/document-todos.md) dan [Keputusan pending](status/pending-decisions.md).

---

**Lihat juga:** [`AGENTS.md`](AGENTS.md) (peta navigasi KB) · [Invarian metodologi](rules/methodology-invariants.md) · [Standar penulisan](rules/writing-standards.md) · [Playbook eksperimen](playbooks/run-experiment.md) · [Playbook evaluasi](playbooks/evaluate.md).
