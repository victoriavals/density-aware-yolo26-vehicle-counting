# AGENTS.md — Tesis YOLO26 (Naufal Firdaus)

> **EN — TL;DR:** Read this first. This is a **thesis research codebase** (not a web app) implementing modifications to YOLO26 for real-time vehicle counting. `CLAUDE.md` at the repo root is the single source of truth; this `.agents/` tree expands it. The rules that bite most: **HAM/P2 are instruments, never novelty**; never fabricate placeholder numbers; ultralytics is locked at 8.4.92. There is an **open title discrepancy** between the SSOT and the actual document — flagged below, not resolved.

Pintu masuk bagi agen/insinyur. Setelah ini, buka [`README.md`](README.md) untuk peta lengkap dan [`00-overview.md`](00-overview.md) untuk ikhtisar.

## Apa proyek ini

Kode penelitian tesis S2 (Naufal Firdaus, NIM 20240804017, Magister Ilmu Komputer, Universitas Esa Unggul; pembimbing Ibu Sandfreni). Tujuan: modifikasi **YOLO26** untuk **penghitungan kendaraan *real-time*** pada lalu lintas heterogen padat (CCTV Jakarta). Tiga komponen: **HAM** (atensi hibrida), **Lapisan P2** (stride-4), **DALW** (Pembobotan *Loss* Berbasis Densitas). Delapan varian ablasi (V1–V8), evaluasi terstratifikasi + Wilcoxon, penghitungan ByteTrack. Kode = lapisan patch/injeksi di atas ultralytics terpasang (tanpa fork). Peta berkas: [`00-overview.md`](00-overview.md).

## Aturan yang menggigit bila diabaikan

1. **JANGAN PERNAH mengklaim HAM atau P2 sebagai kebaruan** — keduanya instrumen; kebaruan = DALW (metode) + analisis interaksi NMS-free. [Framing kebaruan](knowledge/thesis-framing.md).
2. **Jangan isi/ubah placeholder tesis tanpa data nyata**, dan **jangan geser nomor sitasi** [1]–[30]. [TODO dokumen](status/document-todos.md).
3. **Jangan tulis draf BAB 4–5** sebelum hasil lengkap (P8 & P10 belum). [Playbook BAB 4–5](playbooks/write-bab4-5.md).
4. **ultralytics TERKUNCI 8.4.92** — `test_smoke.py` T4 penjaga; T4 gagal → stop. [Lingkungan](knowledge/environment.md).
5. ***Group split* + seed 0 + batch parity** antar 8 varian; densitas dihitung ulang pasca-augmentasi. [Invarian metodologi](rules/methodology-invariants.md).
6. **Unit Wilcoxon = AP per (kelas × strata)**, 3 hipotesis utama + Holm; **MAPE hanya y>0**; **pejalan kaki dikecualikan** counting. [Statistik](knowledge/statistics.md), [Penghitungan](knowledge/counting.md).
7. **Job panjang = background + log berstempel waktu + `--project` ABSOLUT**. [Logging & status](rules/logging-and-status.md).
8. **Pertahankan bahasa kehati-hatian *preprint*** untuk klaim YOLO26.
9. **Konfirmasi Naufal + pembimbing** sebelum keputusan besar (7 pending + judul). [Keputusan pending](status/pending-decisions.md).

## ⚠️ Diskrepansi judul (belum diselesaikan)

Judul di dokumen fisik ("MODIFIKASI **ARSITEKTUR** YOLO26 **MELALUI ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2**, …") **berbeda** dari judul SSOT `CLAUDE.md` §1 ("MODIFIKASI **DETEKTOR NMS-FREE** YOLO26 … **DAN PELACAKAN BYTETRACK** …"). Dokumen menaruh HAM/P2 di judul — bertegangan dengan aturan #1. **Keputusan Naufal + pembimbing**, bukan agen. Dilacak di [Keputusan pending](status/pending-decisions.md).

## Di mana mencari

| Saya perlu… | Baca |
|---|---|
| Ikhtisar + peta berkas | [00-overview.md](00-overview.md) |
| Posisi kebaruan / framing | [knowledge/thesis-framing.md](knowledge/thesis-framing.md) |
| Menyentuh loss densitas | [knowledge/dalw.md](knowledge/dalw.md) + [architecture/code-injection.md](architecture/code-injection.md) |
| Menyentuh HAM / P2 | [knowledge/ham.md](knowledge/ham.md) · [knowledge/p2-layer.md](knowledge/p2-layer.md) |
| Membangun/memahami varian | [architecture/variants.md](architecture/variants.md) |
| Analisis NMS-free (DR/CM) | [knowledge/nmsfree-analysis.md](knowledge/nmsfree-analysis.md) |
| Evaluasi / strata / kompleksitas | [knowledge/evaluation.md](knowledge/evaluation.md) |
| Uji statistik | [knowledge/statistics.md](knowledge/statistics.md) |
| Penghitungan ByteTrack (RQ5) | [knowledge/counting.md](knowledge/counting.md) |
| Dataset & group split | [knowledge/dataset.md](knowledge/dataset.md) |
| Menjalankan training | [playbooks/run-experiment.md](playbooks/run-experiment.md) |
| Menjalankan evaluasi | [playbooks/evaluate.md](playbooks/evaluate.md) |
| Validasi oklusi (P8) | [playbooks/occlusion-validation.md](playbooks/occlusion-validation.md) |
| Status & keputusan pending | [status/progress.md](status/progress.md) · [status/pending-decisions.md](status/pending-decisions.md) |
| Lingkungan / versi | [knowledge/environment.md](knowledge/environment.md) |

## Working agreements

- **Commit hanya bila diminta.** Ketika Naufal minta commit (mis. "lakukan lagi"), hasilkan perintah Git **per-file** (satu blok bash; `git add`/`commit`/`push` tiap file; **tanpa `&&`**; pesan spesifik). [Aturan kerja](rules/working-rules.md).
- **Akhir sesi:** perbarui `CLAUDE.md` §15 + `logs/sesi.log`; bersihkan artefak temporer, **jangan** hapus hasil/bukti.
- **Bahasa:** UI/istilah utama Indonesia; KB ini bilingual (Indonesia + TL;DR Inggris).

## Referensi perintah cepat

```bash
python test_smoke.py                                                   # T1-T4 (wajib LULUS)
python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60
python train_ablation.py --data dataset/data.yaml --variant all
python evaluate_all.py --data dataset/data.yaml --split test --variants all
python analyze_nmsfree.py --data dataset/data.yaml --split test --runs runs_tesis
# Windows: gunakan .\.venv\Scripts\python.exe; job panjang = background + logs/<nama>.log
```

Skill operasional: [`.claude/skills/`](../.claude/skills/) — `jalankan-eksperimen`, `cek-invarian-metodologi`, `perbarui-status-log`, `smoke-test`, `isi-placeholder-bab4`.
