# 7 Keputusan Pending + Diskrepansi Terbuka — Pending Decisions and Open Discrepancies

> **EN — TL;DR:** Seven tracked decisions (A-01, A-02, A-03, A-10, A-11, A-12, B-01). **A-11 and A-12 are resolved** (both heads receive `w_i`; batch 16 held). **A-01 is triggered** by P7 (V8−V1 and V4−V1 not significant). A-02, A-03, A-10, B-01 remain open. The **title discrepancy is RESOLVED (18 Jul 2026)**: Naufal chose the supervisor-revised document's title (HAM+P2+DALW), while the two-pillar novelty framing is retained (HAM/P2 stay instruments; §12.2 unchanged). Three discrepancies remain to record, never resolve alone: the **citation count** (now [1]–[30] authoritative — reconcile the .bib), the **Roboflow source**, and the **GPU label** (doc says "RTX 4060" — add "Ti"). Big decisions require Naufal + supervisor sign-off.

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

## 2. Diskrepansi (status)

### ✅ Judul tesis — FINAL (dikoreksi 18 Jul 2026)

Naskah otoritatif `TESIS_BAB1-3_REVISI_SIDANG_v7` (dan v4) memakai:

> **MODIFIKASI DETEKTOR *NMS-FREE* YOLO26 DENGAN PEMBOBOTAN *LOSS* BERBASIS DENSITAS DAN PELACAKAN BYTETRACK UNTUK PENGHITUNGAN KENDARAAN *REAL-TIME* PADA LALU LINTAS HETEROGEN PADAT**

Judul transisi ("MODIFIKASI ARSITEKTUR … ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2 …") yang sempat dicatat 18 Jul **SUDAH DITOLAK** (mendaftar ketiga komponen → mengaburkan instrumen vs kebaruan). **Bukan** keputusan pembimbing lagi — sudah final; jangan dibuka ulang. Framing kebaruan tetap: DALW (metode) + analisis NMS-free (analitis); HAM/P2 = instrumen (§12.2 utuh). `CLAUDE.md` §1 sudah disamakan.

### Diskrepansi terbuka tersisa (CATAT, jangan resolve sendiri)

Wajib dikonfirmasi ke **Naufal + pembimbing (Ibu Sandfreni)**. Agen **tidak boleh** memutuskan.

| Diskrepansi | Status | Catatan |
|---|---|---|
| **Jumlah sitasi** | Dokumen REVISI **[1]–[30] = otoritatif** | `CLAUDE.md` §9 sudah diperbarui ke 30. Sisa: verifikasi `Daftar_Pustaka_Gabungan_BAB1-3.bib` benar berisi 30 entri (catatan lama 27) dan rekonsiliasikan bila perlu. |
| **Sumber dataset Roboflow** | Terbuka | `CLAUDE.md` §15 P2: `sahabats-workspace/…-nkdvt` (ekspor aktual) vs sitasi [17]: `naufalfirdaus/traffic-merged-qke0k-3yyyo`. Konsistensikan di naskah. |
| **Label GPU** | Terbuka (menyempit) | Dokumen REVISI sudah "RTX 4060 8GB" di **semua** lokasi (3060 sudah diperbaiki) tetapi **tanpa "Ti"**. Perangkat asli "RTX 4060 **Ti** 8GB". Sisa: tambahkan "Ti" seragam. |

Rincian tindak lanjut naskah: [TODO dokumen](document-todos.md). Ringkasan progres: [Progres](progress.md).

## Tautan terkait

- [Framing kebaruan](../knowledge/thesis-framing.md) · [Statistik (hasil P7)](../knowledge/statistics.md) · [Analisis NMS-free (A-10)](../knowledge/nmsfree-analysis.md) · [Penghitungan (A-02)](../knowledge/counting.md) · [TODO dokumen](document-todos.md).
