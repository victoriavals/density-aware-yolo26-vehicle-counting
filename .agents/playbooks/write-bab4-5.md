# Playbook: Menulis BAB 4–5 — Writing Chapters 4–5

> **EN — TL;DR:** **Do not start** until the results exist (P7 done; counting P9 and occlusion P8 still pending) **and** A-01/A-02 are settled with the supervisor. Rules: never fabricate placeholder numbers; **prose only, no bullets/numbering** in body text; keep the two-pillar framing and preprint caution; report effect size alongside p. The honest narrative is that V4−V1 and V8−V1 are **not** significant while V8−V5 **is** → DALW is complementary. This playbook maps the narrative flow; it does **not** authorize drafting BAB 4–5 inside the KB.

Berkas sumber: `CLAUDE.md` §9–§12; `hasil/ringkasan_evaluasi.md`. ⚠️ Menulis BAB 4–5 = **di luar** pekerjaan KB; playbook ini hanya memetakan alur.

## 0. Prasyarat mutlak

1. Hasil eksperimen tersedia: P7 ✅; **counting P9 & oklusi P8 belum** → sebagian metrik belum ada.
2. **A-01** (redaksi bila tak signifikan) & **A-02** (ambang RQ5) **diselesaikan dengan pembimbing** dulu ([Keputusan pending](../status/pending-decisions.md)).
3. Diskrepansi judul & sitasi diklarifikasi ([TODO dokumen](../status/document-todos.md)).

## 1. Aturan penulisan yang mengikat

- **Jangan** isi placeholder tanpa data nyata; jangan mengarang angka.
- **Body text prosa murni** — tanpa bullet/numbering (aturan §11). Lihat [Standar penulisan](../rules/writing-standards.md).
- Framing dua pilar dijaga; **HAM/P2 = instrumen** ([Framing kebaruan](../knowledge/thesis-framing.md)).
- Bahasa kehati-hatian *preprint* untuk klaim YOLO26.
- Laporkan **effect size** (rank-biserial) + median selisih bersama nilai p.

## 2. Alur narasi BAB 4 (peta)

1. Metrik global per varian (test mAP50-95 berhimpit 0,522–0,538) → argumen kenapa unit resmi = AP per (kelas × strata).
2. Ablasi — 3 hipotesis utama: **V8−V1 (p=0,478, ns)**, **V4−V1 (p=0,469, ns, median −0,013)**, **V8−V5 (p=0,0125, r=+0,486, signifikan)**. Sekunder + Holm.
3. **Interpretasi jujur:** DALW **komplementer** — bermanfaat saat digabung HAM+P2, tidak berdiri sendiri (memicu A-01).
4. Stratifikasi: strata terbantu (V8−V5) small +0,062, oklusi-parsial +0,053, densitas-sparse +0,066; catat tier heavy nyaris kosong.
5. Analisis NMS-free (DR/CM/τ, varian ber-P2).
6. Penghitungan end-to-end (MAE/RMSE/MAPE/FPS) — setelah P9.
7. Analisis galat (confusion matrix, dekomposisi FP/FN per strata, kasus kegagalan).

## 3. BAB 5 (Penutup)

Simpulan temuan utama (termasuk hasil jujur DALW komplementer), kontribusi (dua pilar), keterbatasan (proksi oklusi, grid satu titik, satu GPU), rekomendasi lanjutan.

## Tautan terkait

- [Statistik](../knowledge/statistics.md) · [Evaluasi](../knowledge/evaluation.md) · [Framing kebaruan](../knowledge/thesis-framing.md) · [Standar penulisan](../rules/writing-standards.md) · [TODO dokumen](../status/document-todos.md) · [Keputusan pending](../status/pending-decisions.md).
