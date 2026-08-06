# 7 Keputusan Pending + Diskrepansi Terbuka — Pending Decisions and Open Discrepancies

> **EN — TL;DR (updated 5 Aug 2026):** A-11, A-12, A-10 are **resolved**; **K2/K3/K6/K7 decided**. Still open: **A-01** (result framing — triggered and now urgent: the abstract sentence presupposes a significant gain over baseline that the data does not support), **A-02/K5** (RQ5 threshold), **A-03** (literature figures), **B-01** (abstract word count), and the **second counter** part of K7. Post-FASE-1 numbers supersede P7: H1 p=0,565 · H2 p=0,208 · **H3 p=0,037 (significant)**. The **title discrepancy is RESOLVED (18 Jul 2026)**: Naufal chose the supervisor-revised document's title (HAM+P2+DALW), while the two-pillar novelty framing is retained (HAM/P2 stay instruments; §12.2 unchanged). Three discrepancies remain to record, never resolve alone: the **citation count** (now [1]–[30] authoritative — reconcile the .bib), the **Roboflow source**, and the **GPU label** (doc says "RTX 4060" — add "Ti"). Big decisions require Naufal + supervisor sign-off.

Berkas sumber: `CLAUDE.md` §10.5 + §15.

## 1. Tujuh keputusan pending

| Kode | Isi | Status |
|---|---|---|
| **A-01** (=K4) | Redaksi/alternatif abstrak bila hasil tidak signifikan | **TERPICU & MENDESAK — usulan lengkap SIAP di `hasil_bab4_5/K4_REDAKSI_HASIL.md`** (definisi "konfigurasi terbaik", aturan pelaporan 3 hipotesis, abstrak ditulis ulang ID+EN siap tempel, daftar frasa terlarang). Tinggal ACC pembimbing. Angka final pasca-FASE 1: H1 (V8−V1) p=**0,565**, H2 (V4−V1) p=**0,208** r=−0,300, H3 (V8−V5) p=**0,037** r=+0,487 SIGNIFIKAN. ⚠️ Kalimat hasil abstrak v7 **memprasyaratkan** kenaikan signifikan atas baseline yang TIDAK didukung: mAP@0,5 V8 77,97 % < V1 **78,61 %** (turun 0,64 poin); mAP@0,5:0,95 hanya +0,19 poin. Abstrak harus **DITULIS ULANG**, bukan diisi. Rincian: `hasil_bab4_5/PETA_PLACEHOLDER_ABSTRAK.md`. Keputusan Naufal + pembimbing. |
| **A-02** (=K5) | Target konkret RQ5 (ambang MAPE & FPS "standar penerapan praktis") | **PENDING** — dari pembimbing. Counting SUDAH dijalankan; angkanya: MAE **1,97** · RMSE **4,95** · MAPE **37,17 %** (68/180 y=0 dikecualikan) · **FPS pipeline 20,47**. Ambang dibutuhkan hanya untuk *menyimpulkan* lulus/tidak. ⚠️ Menetapkan ambang SETELAH melihat hasil berisiko *post-hoc*. **Usulan lengkap SIAP di `hasil_bab4_5/K5_AMBANG_RQ5.md`**: tiga ambang literatur nyata (skala MAPE Lewis 1982 → 37,17 % = "wajar"; FHWA TMG ≥90 % *bin* ≥30 & ≥95 % volume → gagal; literatur CV 90–98 % dengan catatan satuan), + kriteria FPS **a-priori** ≥ laju sumber 30 FPS → **tak satu pun varian memenuhi** (V8 19,29; V4_a2.0 23,20; V1 23,28 FPS pipeline pada klip terpadat, terukur `counting_out/fps_probe/`). |
| **A-03** | Verifikasi angka literatur: MST-YOLO (+8,42% mAP@0,5; AP kecil 70,97%) & HIC-YOLOv5 (+6,42%) ke sumber [12][13] | **PENDING** — dokumen REVISI sudah mencantumkan angka; verifikasi ke sumber asli. |
| **A-10** | Formalisasi metrik stabilitas *assignment* + sensitivitas τ | **SELESAI** — naskah v7 memformalkan S(t) sebagai **Pers. 3.8**; data terkumpul penuh (`runs_tesis/<V>/nmsfree_probe.csv` per epoch + `nmsfree_out/tau_sweep.csv` 12 nilai τ 0,05–0,90). Grafik: `hasil_bab4_5/05_analisis_nmsfree/`. |
| **A-11** | *Head* YOLO26 penerima `w_i` (o2m / o2o / keduanya) | **SELESAI** — **KEDUA** cabang via `E2ELoss`/`DALWDetectionLoss`. Lihat [DALW](../knowledge/dalw.md). |
| **A-12** | Strategi komputasi 8 varian di GPU 8GB (early-stopping + checkpoint-resume + fallback batch) | **SELESAI** — batch 16 bertahan penuh (0 OOM); fallback batch-8 tak terpicu; *early stopping* patience 50; resume via `--variant Vx --resume`. |
| **B-01** | Cek batas kata abstrak (±360) | **PENDING** — verifikasi panjang ABSTRAK/ABSTRACT **setelah** abstrak ditulis ulang (A-01), karena penulisan ulang mengubah panjangnya. |

## 1b. Keputusan K yang SUDAH diambil (5 Agu 2026)

| Kode | Keputusan | Hasil |
|---|---|---|
| **K1** | Judul final | ✅ **DITUTUP** — judul NMS-free+ByteTrack (naskah v4 & v7); judul transisi "ARSITEKTUR/ATENSI HIBRIDA" ditolak. Bukan lagi bahan diskusi. |
| **K2** | Ambang oklusi 0,35 vs 0,40 | ✅ **0,40** (ikut naskah Tabel 3.6). Tak berpengaruh pada validasi val (maks o=0,286); di split uji heavy 8→4 objek. |
| **K3** | Aturan sel minimum Wilcoxon | ✅ **diterapkan** `MIN_CELL_GT=30` (Subbab 3.11.5) → unit uji 34→**24 sel**, 12 dibuang & dilaporkan terpisah. Arah kesimpulan TIDAK berubah. |
| **K6** | Pengulangan multi-seed | ✅ **TIDAK dijalankan** — anggaran ~49 jam GPU tak tersedia; naskah Tabel 3.9 mengizinkan dengan syarat keterbatasan dinyatakan eksplisit. Kalimat siap pakai: `hasil_bab4_5/10_multi_seed/README.md`. |
| **K7a** | Cakupan klip counting | ✅ **3 klip** (2, 3, 4). Klip 1 **dikecualikan** — segmen garisnya tak menjangkau lajur mobil sehingga GT & sistem mengukur populasi berbeda (cacat validitas pengukuran, BUKAN performa). Wajib dinyatakan eksplisit di BAB 4/5. |
| **K7b** | Penghitung kedua | ⏳ **TERBUKA — kit SIAP PAKAI.** `video_uji/penghitung_kedua/` berisi template buta klip 4 (`gt_4_vidiouji_B.csv`), salinan A, dan pratinjau garis; jalur `bandingkan_gt.py` sudah diuji. Protokol + cadangan *test-retest* + redaksi revisi 3.10.1: `hasil_bab4_5/K7_PENGHITUNG_KEDUA.md`. ⚠️ Bila A≠B, GT hasil kesepakatan menjadi final dan **MAE/RMSE/MAPE harus dihitung ulang**. |
| — | Konvensi arah in/out | ✅ diselaraskan: "in" = menuju **kiri-bawah** (definisi penghitung); diwujudkan dengan membalik urutan titik `--line`. Dampak besar: MAPE klip 3 turun 54,79 %→**26,78 %**. |

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
