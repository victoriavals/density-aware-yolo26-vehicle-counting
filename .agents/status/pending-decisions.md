# 7 Keputusan Pending + Diskrepansi Terbuka — Pending Decisions and Open Discrepancies

> **EN — TL;DR:** Seven tracked decisions (A-01, A-02, A-03, A-10, A-11, A-12, B-01). **A-11 and A-12 are resolved** (both heads receive `w_i`; batch 16 held). **A-01 is triggered** by P7 (V8−V1 and V4−V1 not significant). A-02, A-03, A-10, B-01 remain open. Plus four **open discrepancies** that agents must record, never resolve alone: the **title** (SSOT vs the actual document), the **citation count** (27 vs [1]–[30]), the **Roboflow source**, and the **GPU label**. All big decisions require Naufal + supervisor sign-off.

Berkas sumber: `CLAUDE.md` §10.5 + §15.

## 1. Tujuh keputusan pending

| Kode | Isi | Status |
|---|---|---|
| **A-01** | Redaksi/alternatif abstrak bila hasil tidak signifikan | **TERPICU** oleh P7 (V8−V1 p=0,478 & V4−V1 p=0,469 tidak signifikan). Keputusan Naufal + pembimbing sebelum meredaksi abstrak/klaim. |
| **A-02** | Target konkret RQ5 (ambang MAPE & FPS "standar penerapan praktis") | **PENDING** — dari pembimbing. Diperlukan sebelum menjalankan/menyimpulkan counting P9. |
| **A-03** | Verifikasi angka literatur: MST-YOLO (+8,42% mAP@0,5; AP kecil 70,97%) & HIC-YOLOv5 (+6,42%) ke sumber [12][13] | **PENDING** — dokumen REVISI sudah mencantumkan angka; verifikasi ke sumber asli. |
| **A-10** | Formalisasi metrik stabilitas *assignment* + sensitivitas τ ∈ {0,10; 0,25; 0,50} | **PENDING** (sebagian terkumpul via `nmsfree_probe.csv` & `tau_sweep`). Lihat [Analisis NMS-free](../knowledge/nmsfree-analysis.md). |
| **A-11** | *Head* YOLO26 penerima `w_i` (o2m / o2o / keduanya) | **SELESAI** — **KEDUA** cabang via `E2ELoss`/`DALWDetectionLoss`. Lihat [DALW](../knowledge/dalw.md). |
| **A-12** | Strategi komputasi 8 varian di GPU 8GB (early-stopping + checkpoint-resume + fallback batch) | **SELESAI** — batch 16 bertahan penuh (0 OOM); fallback batch-8 tak terpicu; *early stopping* patience 50; resume via `--variant Vx --resume`. |
| **B-01** | Cek batas kata abstrak (±360) | **PENDING** — verifikasi panjang ABSTRAK/ABSTRACT. |

## 2. Diskrepansi terbuka (CATAT, jangan resolve sendiri)

Wajib dikonfirmasi ke **Naufal + pembimbing (Ibu Sandfreni)**. Agen **tidak boleh** memutuskan.

| Diskrepansi | Versi A | Versi B | Catatan |
|---|---|---|---|
| **Judul tesis** | `CLAUDE.md` §1: "MODIFIKASI **DETEKTOR NMS-FREE** YOLO26 … **DAN PELACAKAN BYTETRACK** …" (tanpa HAM/P2) | Dokumen `TESIS_BAB1-3_REVISI_PEMBIMBING`: "MODIFIKASI **ARSITEKTUR** YOLO26 **MELALUI ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2**, DAN PEMBOBOTAN LOSS BERBASIS DENSITAS …" | Versi B menaruh instrumen (HAM/P2) di judul — bertegangan dengan §12.2. **Perlu keputusan mana yang final** dan konsistensikan di halaman judul, ABSTRAK/ABSTRACT, seluruh bab. |
| **Jumlah sitasi** | `CLAUDE.md` §9: 27 referensi | Dokumen REVISI: DAFTAR PUSTAKA [1]–[30] | Naskah bertambah (RT-DETR, YOLO-World, YOLOE, Ultralytics, supervision, Wilcoxon, dst.). Perbarui angka acuan. |
| **Sumber dataset Roboflow** | `CLAUDE.md` §15 P2: `sahabats-workspace/…-nkdvt` | Sitasi [17]: `naufalfirdaus/traffic-merged-qke0k-3yyyo` | Konsistensikan di naskah. |
| **Label GPU** | `CLAUDE.md` §8: masih ada lokasi "RTX 3060" | Dokumen REVISI: sudah "RTX 4060/4060 Ti 8GB" di beberapa tempat (Batasan 1.5, 2.5.2, Tabel 3.8) | Verifikasi lokasi tersisa; target seragam **"RTX 4060 Ti 8GB"**. |

Rincian tindak lanjut naskah: [TODO dokumen](document-todos.md). Ringkasan progres: [Progres](progress.md).

## Tautan terkait

- [Framing kebaruan](../knowledge/thesis-framing.md) · [Statistik (hasil P7)](../knowledge/statistics.md) · [Analisis NMS-free (A-10)](../knowledge/nmsfree-analysis.md) · [Penghitungan (A-02)](../knowledge/counting.md) · [TODO dokumen](document-todos.md).
