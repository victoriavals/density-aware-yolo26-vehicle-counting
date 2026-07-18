---
name: perbarui-status-log
description: Perbarui CLAUDE.md §15 dan logs/sesi.log di akhir sesi sesuai aturan §12.7-12.8; bersihkan artefak temporer tetapi jangan hapus hasil/bukti eksperimen. Pakai saat menutup sesi kerja.
---

# Perbarui Status & Log — Update Status and Session Log

> **EN — TL;DR:** At session end, append a `CLAUDE.md` §15 bullet (results/decisions/incidents) **and** a `logs/sesi.log` line `[YYYY-MM-DD HH:MM] CATEGORY | text`. Clean temporary artifacts but never delete results/evidence.

## Langkah
1. **`CLAUDE.md` §15** — tambah bullet baru di akhir daftar (§15) berisi: fase/nama, tanggal absolut, hasil/keputusan/insiden, artefak kunci, dan pemicu keputusan pending bila ada. Konversi tanggal relatif → absolut.
2. **`logs/sesi.log`** — *append* satu baris per tindakan/keputusan/temuan/insiden signifikan:
   ```
   [YYYY-MM-DD HH:MM] KATEGORI | isi ringkas
   ```
   (Kategori mis. `EKSPERIMEN`, `KEPUTUSAN`, `TEMUAN`, `INSIDEN`, `DOKUMENTASI`.)
3. **Bersihkan** kode/artefak temporer yang tak dipakai — **JANGAN** hapus `runs_tesis/`, `eval_out/`, `nmsfree_out/`, `counting_out/`, `inits/`, `dataset/`, `bukti_split_*.csv`, atau ringkasan `hasil/`.

## Catatan
- `logs/` di-*gitignore*; commit CLAUDE.md bila diminta (per-file, lihat aturan kerja).
- Job panjang tetap punya log keluaran sendiri (`logs/<nama>.log`).

## Rujukan
`.agents/rules/logging-and-status.md`, `.agents/rules/working-rules.md` (relatif ke root repo).
