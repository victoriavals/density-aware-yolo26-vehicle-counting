# Aturan Kerja untuk Claude Code — Working Rules

> **EN — TL;DR:** The non-negotiables from `CLAUDE.md` §12. Never claim HAM/P2 as novelty; never fill/alter thesis placeholders without real data; never shift citation numbers; never draft BAB 4–5 before results exist. Follow the final methodology (group split, Wilcoxon 3-primary + Holm, MAPE `y>0`, density recomputed post-augmentation). Keep the preprint-cautious language. **Confirm with Naufal before any big decision** (the 7 pending items, the title, chapter structure). At end of session, update `CLAUDE.md` §15 + `logs/sesi.log` and clean temporary artifacts — but never delete results/evidence. Observed commit workflow: on request ("lakukan lagi"), emit **per-file** `git add`/`commit`/`push` commands, newline-separated, **no `&&`**, specific messages.

Berkas sumber: `CLAUDE.md` §12.

## 1. Larangan keras (NEVER)

1. **Jangan pernah** mengklaim HAM atau Lapisan P2 sebagai kebaruan — keduanya instrumen ([Framing kebaruan](../knowledge/thesis-framing.md)).
2. **Jangan** mengisi/mengubah placeholder tesis tanpa data eksperimen nyata ([TODO dokumen](../status/document-todos.md)).
3. **Jangan** menambah/menghapus/menggeser nomor sitasi [1]–[30].
4. **Jangan** menulis draf BAB 4–5 sebelum hasil lengkap tersedia (P8 & P10 belum) — termasuk di dalam KB ini.
5. **Jangan** melonggarkan invarian metodologi ([Invarian metodologi](methodology-invariants.md)).
6. **Jangan** menghapus artefak hasil/bukti (`runs_tesis/`, `eval_out/`, `nmsfree_out/`, `counting_out/`, `inits/`, `dataset/`, `bukti_split_*.csv`).

## 2. Keharusan (ALWAYS)

- Jaga konsistensi istilah, angka, dan framing dua pilar lintas bab.
- Ikuti metodologi final: *group split* sebelum training, protokol Wilcoxon (3 hipotesis utama + Holm), aturan MAPE `y_t > 0`, densitas dihitung ulang pasca-augmentasi.
- Pertahankan bahasa kehati-hatian *preprint* (subbab 2.3.5, 2.9, 3.5).
- Implementasi kode terkunci ke **ultralytics 8.4.92** (`test_smoke.py` T4 = penjaga).

## 3. Konfirmasi sebelum keputusan besar

Selalu konfirmasi ke **Naufal** (dan bila perlu pembimbing Ibu Sandfreni) sebelum: perubahan desain, judul, struktur bab, atau apa pun yang menyentuh **7 keputusan pending** ([Keputusan pending](../status/pending-decisions.md)). Diskrepansi terbuka (judul, jumlah sitasi, sumber Roboflow, label GPU) **dicatat, bukan diselesaikan sendiri**.

## 4. Working agreement teramati (alur commit)

Ketika Naufal meminta commit — mis. lewat frasa **"lakukan lagi"** setelah menambah/mengubah berkas — hasilkan **perintah Git per-file** dengan pola:

```
git add <satu-file>
git commit -m "<pesan spesifik sesuai perubahan file itu>"
git push

git add <file-berikutnya>
...
```

Ketentuan: satu blok bash; setiap perintah baris baru; **TANPA `&&`**; pesan commit spesifik (mis. `feat: ...`, `fix: ...`, `docs: ...`), bukan "update file". **Jangan commit tanpa diminta.**

## 5. Akhir setiap sesi (§12.7–§12.8)

- Perbarui `CLAUDE.md` **§15** (Status & Log Progres) dengan hasil/keputusan baru.
- *Append* setiap tindakan/keputusan/temuan/insiden signifikan ke `logs/sesi.log` (`[YYYY-MM-DD HH:MM] KATEGORI | isi`).
- Bersihkan kode/artefak temporer yang tak dipakai lagi — **tetapi jangan** hapus hasil eksperimen/bukti metodologis.

Detail logging & status: [Logging & status](logging-and-status.md).

## Tautan terkait

- [Invarian metodologi](methodology-invariants.md) · [Standar penulisan](writing-standards.md) · [Logging & status](logging-and-status.md) · [Keputusan pending](../status/pending-decisions.md) · [AGENTS.md](../AGENTS.md).
