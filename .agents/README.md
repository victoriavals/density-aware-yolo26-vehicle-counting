# `.agents/` — Basis Pengetahuan Tesis YOLO26

> **EN — TL;DR:** Agent-facing knowledge base for the YOLO26 density-aware vehicle-counting thesis. It expands the root [`CLAUDE.md`](../CLAUDE.md) (the canonical source of truth) into navigable per-domain docs, rules, status, and playbooks. Start at [`AGENTS.md`](AGENTS.md). When docs and code disagree, **the code (and `CLAUDE.md`) win**. This tree is documentation, not build input — nothing imports from `.agents/`.

Basis pengetahuan bagi agen (atau insinyur baru) untuk mengerjakan repo tesis ini dengan aman: framing kebaruan, arsitektur/injeksi kode, pengetahuan per-domain, aturan keras, status eksperimen, dan playbook.

> **Sumber kebenaran.** Root [`CLAUDE.md`](../CLAUDE.md) tetap SSOT. `.agents/` adalah **ekspansi navigable** darinya; bila berbeda, verifikasi ke kode — kode menang. Skill operasional di [`.claude/skills/`](../.claude/skills/).

## Cara pakai

1. Mulai dari [`AGENTS.md`](AGENTS.md) — pintu masuk: apa proyeknya, aturan yang menggigit, di mana mencari.
2. Baca [`00-overview.md`](00-overview.md) — ikhtisar penelitian, stack, layout, peta berkas→tesis.
3. Lompat ke area relevan di bawah.

## Peta

### Arsitektur (`architecture/`)
| File | Isi |
|---|---|
| [architecture/code-injection.md](architecture/code-injection.md) | Tiga mekanisme injeksi (HAM namespace, DALW monkey-patch, YAML varian); akses kepala one-to-one mentah; kunci ultralytics 8.4.92 |
| [architecture/data-flow.md](architecture/data-flow.md) | Rantai dependensi modul + alur data train→eval→nmsfree→counting; folder mentah BAB 4 |
| [architecture/variants.md](architecture/variants.md) | 8 varian faktorial V1–V8, `build_model`, transfer bobot, `inits/` |

### Pengetahuan domain (`knowledge/`)
| File | Isi |
|---|---|
| [knowledge/thesis-framing.md](knowledge/thesis-framing.md) | Dua pilar kebaruan; HAM/P2 = instrumen; STAL vs DALW; diskrepansi judul |
| [knowledge/dalw.md](knowledge/dalw.md) | Pers. 3.2–3.5, A-11 (kedua head), penempatan bobot, pasca-augmentasi |
| [knowledge/ham.md](knowledge/ham.md) | Modul HAM (kaskade kanal→spasial), registrasi — instrumen |
| [knowledge/p2-layer.md](knowledge/p2-layer.md) | Lapisan P2 stride-4, biaya VRAM/waktu — instrumen |
| [knowledge/nmsfree-analysis.md](knowledge/nmsfree-analysis.md) | Duplicate Rate, Confidence Margin, stabilitas assignment (A-10) |
| [knowledge/evaluation.md](knowledge/evaluation.md) | Metrik, strata AP gaya COCO, tier, kompleksitas Tabel 3.7 |
| [knowledge/statistics.md](knowledge/statistics.md) | Wilcoxon 3 utama + Holm + rank-biserial; hasil P7 |
| [knowledge/counting.md](knowledge/counting.md) | ByteTrack + virtual line + MAE/RMSE/MAPE (RQ5) |
| [knowledge/dataset.md](knowledge/dataset.md) | traffic-merged, group split 70/20/10, bukti lampiran |
| [knowledge/environment.md](knowledge/environment.md) | .venv, versi terkunci, GPU, konvensi Windows-native |

### Aturan (`rules/`) — baca sebelum menulis
| File | Isi |
|---|---|
| [rules/methodology-invariants.md](rules/methodology-invariants.md) | Invarian terkodekan yang tidak boleh dilonggarkan |
| [rules/writing-standards.md](rules/writing-standards.md) | Standar penulisan naskah (Indonesia akademik, prosa murni, IEEE) |
| [rules/working-rules.md](rules/working-rules.md) | Aturan kerja §12: NEVER/ALWAYS, alur commit per-file |
| [rules/logging-and-status.md](rules/logging-and-status.md) | Background job, log berstempel waktu, update §15 + sesi.log |

### Status (`status/`)
| File | Isi |
|---|---|
| [status/progress.md](status/progress.md) | Ringkasan P1–P10 + hasil utama P7 |
| [status/pending-decisions.md](status/pending-decisions.md) | 7 keputusan pending + 4 diskrepansi terbuka |
| [status/document-todos.md](status/document-todos.md) | 18+2 placeholder BAB 4, TODO naskah |

### Playbook (`playbooks/`)
| File | Isi |
|---|---|
| [playbooks/run-experiment.md](playbooks/run-experiment.md) | Smoke → grid → V1–V8 → resume |
| [playbooks/evaluate.md](playbooks/evaluate.md) | evaluate_all / analyze_nmsfree / counting |
| [playbooks/occlusion-validation.md](playbooks/occlusion-validation.md) | Kit anotasi oklusi manual (P8) |
| [playbooks/write-bab4-5.md](playbooks/write-bab4-5.md) | Peta narasi BAB 4–5 (prasyarat & aturan) |

### Skill operasional (`.claude/skills/`)
`jalankan-eksperimen` · `cek-invarian-metodologi` · `perbarui-status-log` · `smoke-test` · `isi-placeholder-bab4`.

## Menjaga tetap mutakhir

Saat kode/metodologi berubah, perbarui file `.agents/` terkait + `CLAUDE.md` §15 (aturan §12.7). Mekanisme & pemetaan sumber→doc: [MAINTENANCE.md](MAINTENANCE.md). Tree ini dihasilkan dari `CLAUDE.md` + `README.md` + sapuan kode; dokumentasi, bukan build input.
