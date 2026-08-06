# TODO Naskah & Placeholder BAB 4 — Manuscript TODOs and BAB 4 Placeholders

> **EN — TL;DR (updated 6 Aug 2026):** **All 18 numeric + 2 narrative placeholders are DONE** — the abstract's result sentence was *rewritten* (not filled) and pasted into **`TESIS_BAB1-3_REVISI_SIDANG_v8.docx`**, since it had presupposed a significant gain the data does not support (V8 mAP@0,5 = 77,97 % < V1 78,61 %; H1 p = 0,565). v8 also fixes the GPU label, split figures, split wording, library versions, and §3.10.1 (two counters → one, with the limitation stated). BAB IV & V exist as `TESIS_BAB4-5.docx`. **Still open:** citations [31]–[33] must be entered via Mendeley, the two documents must be merged with TOC/lists regenerated, figure revisions, A-03 literature verification, sidang items 5/23/27, and the appendix/administrative pages.

Berkas sumber: `CLAUDE.md` §9–§10; **`TESIS_BAB1-3_REVISI_SIDANG_v8`** (hasil revisi 6 Agu 2026; v7 disimpan sebagai cadangan). ⚠️ Naskah = **di luar scope kode**, tetapi dilacak agar KB konsisten.

## 1. Placeholder → ✅ SELESAI (6 Agustus 2026)

Ke-18 placeholder numerik dan 2 naratif **sudah tidak ada lagi** di `…v8.docx`. Kalimat hasil
abstrak **ditulis ulang**, bukan diisi, karena bentuk aslinya memprasyaratkan kenaikan
signifikan atas *baseline* yang tidak didukung data. Panjang akhir: ABSTRAK **336 kata**
(v7 337), ABSTRACT **385** (v7 380) — B-01 terpenuhi. Skrip: `y26_revisi_bab13.py`.

Peta lengkap 18 placeholder numerik + 2 naratif → angka nyata (riwayat) ada di
**`hasil_bab4_5/PETA_PLACEHOLDER_ABSTRAK.md`** (disusun 5 Agu 2026, dibaca langsung dari
`eval_out/`, `eval_out_fase2/`, `nmsfree_out/`, `counting_out/`). Ringkasnya:

| Placeholder (ABSTRAK) | Angka nyata | Bisa diisi? |
|---|---|---|
| mAP@0,5 & mAP@0,5:0,95 "konfigurasi terbaik" | V1 78,61/53,56 · V8 77,97/53,75 · V4_a2.0 77,18/**54,96** | ⚠️ definisikan "terbaik" dulu (rekomendasi: mAP@0,5:0,95 tertinggi → V4_a2.0) |
| Peningkatan `[X,X]` poin vs baseline + p `[0,0XX]` | mAP50-95 **+0,19** pp · mAP50 **−0,64** pp · H1 p=**0,565** | ❌ **kalimat harus ditulis ulang** (A-01/K4) |
| Kenaikan AP objek kecil / densitas tinggi | **+5,1** pp (small) · **+3,3** pp (dense) | ✅ didukung |
| MAE / RMSE / MAPE | **1,97** / **4,95** / **37,17 %** (68/180 y=0 dikecualikan) | ✅ (wajib sebut proporsi eksklusi) |
| FPS | **20** (`fps_pipeline` 20,47) | ✅ — **JANGAN** pakai 23,3 (`fps_model`) |
| 2× naratif DR & CM | HAM menstabilkan one-to-one yang diganggu kerapatan P2 (V5 +0,047, V8 +0,055; V3 −0,058, V7 −0,017) | ✅ tersedia lengkap |

> ⚠️ Tabel di atas adalah **riwayat** (kondisi sebelum 6 Agu 2026). Dua barisnya sempat keliru
> dan sudah dikoreksi: "konfigurasi terbaik" bukan V4_a2.0 melainkan **V8** (memilih V4_a2.0
> berdasarkan skor uji = seleksi pada data uji), dan klaim strata bukan "+5,1 pp small /
> +3,3 pp dense" melainkan **oklusi parsial +5,4 pp & objek kecil +3,0 pp** (V8−V5, sel
> n_gt≥30); strata *dense* tidak dapat dinilai. Rincian: `hasil_bab4_5/K4_REDAKSI_HASIL.md`.

## 2. TODO naskah lain

- ✅ **Label GPU:** SELESAI di v8 — "RTX 4060 Ti 8GB" di 6 lokasi.
- **Judul & abstrak:** judul final = versi **NMS-free + ByteTrack** (naskah v4 & v7); judul transisi "ARSITEKTUR … ATENSI HIBRIDA, P2 …" **ditolak**. Sisir seluruh berkas agar tak ada sisa frasa transisi tersebut.
- ✅ **Diksi split:** SELESAI di v8 — "secara acak" → "secara deterministik, yaitu kelompok diurutkan menurut penanda yang stabil lalu dipotong pada ambang kumulatif".
- **Nomor persamaan bergeser (+1 sejak Pers. 3.8):** naskah v7 memformalkan S(t) sebagai Pers. 3.8 sehingga persamaan setelahnya bergeser; rank-biserial menjadi Pers. 3.16. Periksa seluruh rujukan silang "Pers. 3.x".
- ✅ **Tabel lingkungan versi pustaka:** SELESAI di v8 — PyTorch 2.11.0+cu128 dengan Ultralytics 8.4.92, supervision 0.29.1, Python 3.11.9.
- **Revisi sidang yang belum tergarap:** poin 5, butir 23 (referensi internasional — verifikasi ke web lalu **masukkan via Mendeley**, menyunting langsung di Word akan tertimpa), butir 27 (DOI).
- **Sitasi:** dokumen REVISI [1]–[30]; verifikasi `Daftar_Pustaka_Gabungan_BAB1-3.bib` benar 30 entri (catatan lama 27) dan urutan = kemunculan pertama.
- **Revisi manual gambar:** pangkas kotak G1.3/2.1/2.2/2.3/3.4; teks G2.3 ("8–16 piksel", hapus "+5–7% mAP"); margin G3.1; label G3.5.
- **Rakit akhir:** tempel Daftar Pustaka, Lampiran 1 (bukti split, sampel oklusi), halaman administratif.
- ✅ **Konsistensi angka split:** SELESAI di v8 — 2.372/679/338 di §3.3.2 dan §3.11.5.

## 3. Diskrepansi terbuka (catat, jangan resolve)

Ringkas (detail di [Keputusan pending](pending-decisions.md)):

1. ✅ **Judul** — RESOLVED (18 Jul 2026): versi revisi pembimbing dipakai; HAM/P2 deskriptif, framing tak berubah.
2. **Jumlah sitasi** — [1]–[30] otoritatif; rekonsiliasi `.bib`.
3. **Sumber dataset Roboflow** — workspace `sahabats-workspace/...-nkdvt` vs sitasi [17] `naufalfirdaus/...`.
4. ✅ **Label GPU** — SELESAI di v8 ("RTX 4060 Ti 8GB", 6 lokasi).

## Tautan terkait

- [Keputusan pending](pending-decisions.md) · [Progres](progress.md) · [Playbook BAB 4–5](../playbooks/write-bab4-5.md) · [Standar penulisan](../rules/writing-standards.md) · [Statistik](../knowledge/statistics.md).
