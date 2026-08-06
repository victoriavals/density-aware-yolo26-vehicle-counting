# TODO Naskah & Placeholder BAB 4 — Manuscript TODOs and BAB 4 Placeholders

> **EN — TL;DR (updated 5 Aug 2026):** All **18 numeric placeholders sit in the abstract** (9 Indonesian + 9 mirrored English); BAB 4–5 are not written yet so they contain none. **Every number is now available** — but the abstract's result sentence **cannot be filled, it must be REWRITTEN**: it presupposes a statistically significant gain over the baseline, whereas V8 mAP@0,5 = 77,97 % is *below* V1 = 78,61 % and H1 p = 0,565. Full mapping with the exact numbers: `hasil_bab4_5/PETA_PLACEHOLDER_ABSTRAK.md`. A-01/K4 and A-02/K5 must be settled with the supervisor first. The **title is RESOLVED** (NMS-free + ByteTrack, v4 & v7). Three discrepancies remain recorded, not resolved: citation count ([1]–[30] authoritative), Roboflow source, GPU label ("RTX 4060" → add "Ti").

Berkas sumber: `CLAUDE.md` §9–§10; `TESIS_BAB1-3_REVISI_SIDANG_v7` (ABSTRAK/ABSTRACT). ⚠️ Naskah = **di luar scope kode**, tetapi dilacak agar KB konsisten.

## 1. Placeholder → sumber angka (JANGAN isi tanpa data)

Peta lengkap 18 placeholder numerik + 2 naratif → angka nyata ada di
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

> **A-01/K4 aktif & MENDESAK:** bukan sekadar "hasil tidak signifikan" — kalimat hasil abstrak
> memprasyaratkan tiga hal yang tidak didukung data sekaligus. Mengisi apa adanya menghasilkan
> **pernyataan salah**. Redaksi menunggu keputusan Naufal + pembimbing. Lihat
> [Keputusan pending](pending-decisions.md) & [Playbook BAB 4–5](../playbooks/write-bab4-5.md).
>
> **B-01 menunggu A-01:** panjang ABSTRAK/ABSTRACT (±360 kata) hanya bisa diverifikasi setelah
> abstrak ditulis ulang.

## 2. TODO naskah lain

- **Label GPU:** dokumen REVISI sudah "RTX 4060 8GB" di **semua** lokasi (Batasan 1.6, subbab 2.5.2, 2.7.3, 3.6.2, Tabel 3.8) — "3060" TUNTAS. Sisa: **tambahkan "Ti"** → "RTX 4060 Ti 8GB" (perangkat asli ber-Ti).
- **Judul & abstrak:** judul final = versi **NMS-free + ByteTrack** (naskah v4 & v7); judul transisi "ARSITEKTUR … ATENSI HIBRIDA, P2 …" **ditolak**. Sisir seluruh berkas agar tak ada sisa frasa transisi tersebut.
- **Diksi split:** naskah menyebut pemilihan split "acak"; implementasi `make_group_split.py` **deterministik** (grup diurutkan lalu dipotong pada ambang kumulatif) — samakan diksi agar tak ada klaim yang tak cocok kode.
- **Nomor persamaan bergeser (+1 sejak Pers. 3.8):** naskah v7 memformalkan S(t) sebagai Pers. 3.8 sehingga persamaan setelahnya bergeser; rank-biserial menjadi Pers. 3.16. Periksa seluruh rujukan silang "Pers. 3.x".
- **Tabel 3.8 versi pustaka:** samakan ke versi terpasang aktual — ultralytics **8.4.92**, torch **2.11.0+cu128**, supervision **0.29.1**, Python **3.11.9**.
- **Revisi sidang yang belum tergarap:** poin 5, butir 23 (referensi internasional — verifikasi ke web lalu **masukkan via Mendeley**, menyunting langsung di Word akan tertimpa), butir 27 (DOI).
- **Sitasi:** dokumen REVISI [1]–[30]; verifikasi `Daftar_Pustaka_Gabungan_BAB1-3.bib` benar 30 entri (catatan lama 27) dan urutan = kemunculan pertama.
- **Revisi manual gambar:** pangkas kotak G1.3/2.1/2.2/2.3/3.4; teks G2.3 ("8–16 piksel", hapus "+5–7% mAP"); margin G3.1; label G3.5.
- **Rakit akhir:** tempel Daftar Pustaka, Lampiran 1 (bukti split, sampel oklusi), halaman administratif.
- **Konsistensi angka split:** naskah gunakan **2.372/679/338** (dokumen revisi menulis approx 2.372/678/339 di §3.3.2 — samakan ke angka final aktual).

## 3. Diskrepansi terbuka (catat, jangan resolve)

Ringkas (detail di [Keputusan pending](pending-decisions.md)):

1. ✅ **Judul** — RESOLVED (18 Jul 2026): versi revisi pembimbing dipakai; HAM/P2 deskriptif, framing tak berubah.
2. **Jumlah sitasi** — [1]–[30] otoritatif; rekonsiliasi `.bib`.
3. **Sumber dataset Roboflow** — workspace `sahabats-workspace/...-nkdvt` vs sitasi [17] `naufalfirdaus/...`.
4. **Label GPU** — dokumen "RTX 4060 8GB" → tambahkan "Ti".

## Tautan terkait

- [Keputusan pending](pending-decisions.md) · [Progres](progress.md) · [Playbook BAB 4–5](../playbooks/write-bab4-5.md) · [Standar penulisan](../rules/writing-standards.md) · [Statistik](../knowledge/statistics.md).
