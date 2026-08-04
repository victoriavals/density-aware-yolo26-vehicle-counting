# TODO Naskah & Placeholder BAB 4 — Manuscript TODOs and BAB 4 Placeholders

> **EN — TL;DR:** The manuscript (`.docx`, out of code scope but tracked here) still has **18 numeric placeholders + 2 narrative placeholders**, plus figure revisions, GPU-label fixes, and appendix pasting. This file maps each placeholder to the artifact that will fill it — but **do not fill any placeholder without real data** (rule NEVER). A-01 and A-02 must be settled with the supervisor first. The **title is RESOLVED** (supervisor-revised version chosen). Three discrepancies remain recorded, not resolved: citation count ([1]–[30] authoritative), Roboflow source, GPU label ("RTX 4060" → add "Ti").

Berkas sumber: `CLAUDE.md` §9–§10; `TESIS_BAB1-3_REVISI_PEMBIMBING` (ABSTRAK/ABSTRACT). ⚠️ Naskah = **di luar scope kode**, tetapi dilacak agar KB konsisten.

## 1. Placeholder → sumber angka (JANGAN isi tanpa data)

18 placeholder numerik + 2 naratif menunggu hasil. Pemetaan ke artefak:

| Placeholder (ABSTRAK/BAB 4) | Sumber angka | Prasyarat |
|---|---|---|
| mAP@0,5 `[XX,X]` %, mAP@0,5:0,95 `[XX,X]` % konfigurasi terbaik | `eval_out/global_metrics.csv` | P7 ✅ |
| Peningkatan `[X,X]` poin vs baseline + p `[0,0XX]` | `eval_out/wilcoxon_*.csv` | P7 ✅ (⚠️ A-01: hasil tidak signifikan) |
| Kenaikan AP objek kecil/densitas tinggi `[X,X]` poin | `eval_out/strata_ap.csv` | P7 ✅ |
| MAE `[X,XX]`, RMSE `[X,XX]`, MAPE `[X,X]` % | `counting_out/summary.json` | **P9 belum** |
| FPS `[XX]` | `counting_out/summary.json` / `y26_complexity` | P9 / kompleksitas |
| 2× naratif: "ringkasan temuan *Duplicate Rate* & *Confidence Margin*" | `nmsfree_out/summary.csv` | P7 ✅ (rangkai naratif) |

> **A-01 aktif:** hasil utama P7 tidak signifikan (V8−V1, V4−V1). Redaksi abstrak/klaim menunggu keputusan Naufal + pembimbing sebelum placeholder diisi. Lihat [Keputusan pending](pending-decisions.md) & [Playbook BAB 4–5](../playbooks/write-bab4-5.md).

## 2. TODO naskah lain

- **Label GPU:** dokumen REVISI sudah "RTX 4060 8GB" di **semua** lokasi (Batasan 1.6, subbab 2.5.2, 2.7.3, 3.6.2, Tabel 3.8) — "3060" TUNTAS. Sisa: **tambahkan "Ti"** → "RTX 4060 Ti 8GB" (perangkat asli ber-Ti).
- **Judul & abstrak:** samakan halaman judul + ABSTRAK + ABSTRACT + seluruh bab ke judul final (versi revisi pembimbing, sudah otoritatif) — HAM/P2 deskriptif, framing dua-pilar tetap.
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
