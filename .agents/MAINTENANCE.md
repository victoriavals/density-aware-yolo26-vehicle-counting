# Menjaga KB Tetap Mutakhir — Keeping the KB Current

> **EN — TL;DR:** When code or methodology changes, update the matching `.agents/` doc **and** `CLAUDE.md` §15 (rule §12.7). This KB has **no** auto-sync hook by default (unlike the sibling Traffic Pulse repo) — maintenance is manual and disciplined. An opt-in Python drift-checker + Stop hook could be added later, but **do not enable it without being asked**. The KB is documentation, not build input.

Berkas sumber: `CLAUDE.md` §12.7.

## Prinsip

`CLAUDE.md` = SSOT (khususnya §15 sebagai log kanonik). `.agents/` = ekspansi navigable. Ketika keduanya berbeda, kode + `CLAUDE.md` menang. Setiap sesi yang mengubah kode/metodologi wajib menyinkronkan doc terkait (aturan §12.7).

## Pemetaan sumber → doc

| Kalau kamu mengubah… | Perbarui |
|---|---|
| `y26_dalw.py` (loss densitas) | [knowledge/dalw.md](knowledge/dalw.md) + [architecture/code-injection.md](architecture/code-injection.md) |
| `y26_modules.py` (HAM) | [knowledge/ham.md](knowledge/ham.md) + [architecture/code-injection.md](architecture/code-injection.md) |
| `y26_variants.py` / tambah varian | [architecture/variants.md](architecture/variants.md) + [architecture/code-injection.md](architecture/code-injection.md) |
| `y26_nmsfree.py` / `analyze_nmsfree.py` | [knowledge/nmsfree-analysis.md](knowledge/nmsfree-analysis.md) |
| `y26_strata.py` / `y26_complexity.py` / `evaluate_all.py` | [knowledge/evaluation.md](knowledge/evaluation.md) |
| `y26_stats.py` | [knowledge/statistics.md](knowledge/statistics.md) |
| `y26_counting.py` / `siapkan_counting.py` | [knowledge/counting.md](knowledge/counting.md) |
| `make_group_split.py` / `download_dataset.py` | [knowledge/dataset.md](knowledge/dataset.md) |
| `train_ablation.py` | [playbooks/run-experiment.md](playbooks/run-experiment.md) + [architecture/variants.md](architecture/variants.md) |
| Keputusan/hasil baru | [status/pending-decisions.md](status/pending-decisions.md) + [status/progress.md](status/progress.md) + `CLAUDE.md` §15 |
| Versi/lingkungan | [knowledge/environment.md](knowledge/environment.md) |
| Aturan/konvensi baru | [rules/](rules/) |

## Auto-sync (opsional, belum aktif)

Proyek sibling (Traffic Pulse) memakai Stop-hook + skrip drift-check Node yang mengingatkan saat kode lebih baru dari KB. Repo tesis ini **Python-only** dan **belum** mengaktifkan hook apa pun. Bila diinginkan, opsi opt-in: skrip drift-check Python (bandingkan mtime `*.py` vs `.agents/*.md`) + hook `Stop` di `.claude/settings.json` yang memunculkan pengingat non-blocking. **Jangan diaktifkan tanpa diminta** — hook berjalan tiap giliran dan menghabiskan token/latensi. Untuk saat ini, sinkronisasi manual sesuai daftar di atas.

## Catatan

- KB ini bilingual (Indonesia + TL;DR Inggris) — pertahankan format saat menyunting.
- Tidak ada yang meng-*import* dari `.agents/`; aman untuk direstrukturisasi selama tautan diperbarui.

## Tautan terkait

- [README.md](README.md) · [AGENTS.md](AGENTS.md) · [rules/working-rules.md](rules/working-rules.md) · [rules/logging-and-status.md](rules/logging-and-status.md).
