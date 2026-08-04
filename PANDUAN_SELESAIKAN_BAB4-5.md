# Panduan End-to-End: Menyelesaikan BAB 4 & BAB 5

> Peta jalan lengkap dari kondisi **sekarang** (P7 selesai) hingga **BAB 4 (Hasil & Pembahasan)
> dan BAB 5 (Kesimpulan) selesai ditulis**. Dokumen ini adalah kontrak kerja: setiap langkah
> menyebut **siapa** yang mengerjakan, **perintah/aksi** konkret, **keluaran**, dan **cara verifikasi**.

**Legenda:** 👤 = tugas Naufal (manusia; tak bisa didelegasikan) · 🤖 = tugas Claude Code · 🎓 = butuh keputusan bersama pembimbing (Bu Sandfreni)

**Aturan main (dari CLAUDE.md):** jangan isi placeholder tanpa data nyata; jangan tulis BAB 4–5 sebelum semua angka lengkap; jaga framing dua-pilar (DALW = kebaruan; HAM/P2 = instrumen); setiap sesi perbarui §15 + `logs/sesi.log`.

---

## Ringkasan status sekarang (per 18 Jul 2026)

| Sudah selesai | Artefak |
|---|---|
| P1 Lingkungan, P2 Dataset (split grup 2.372/679/338), P3 Grid search (α=1,0 σ=0,1) | `dataset/`, `hasil/grid_search.md`, `dalw_best.json` |
| P5 Latih V1–V8 (batch 16, 0 crash) | `runs_tesis/V1..V8/` + backup `backups/` |
| P7 Evaluasi + Wilcoxon + NMS-free | `eval_out/`, `nmsfree_out/`, `hasil/ringkasan_evaluasi.md` |
| Tabel kompleksitas (Tabel 3.7) | `eval_out/complexity.csv` |
| Kit P8 (anotasi oklusi) siap | `anotasi_oklusi/` (HTML + jalur Roboflow) |
| Kit P9 (counting) siap | `siapkan_counting.py`, `video_uji/README.md` |

**Hasil kunci P7 (angka nyata):** DALW **tidak** signifikan berdiri sendiri (V4–V1 p=0,469) tetapi **signifikan komplementer** di atas HAM+P2 (V8–V5 p=0,012; r=+0,486). FPS: V1=32,4 s.d. V8=23,3.

---

## Peta fase (urutan & dependensi)

```
FASE 0 (keputusan) ──► FASE 1 (perbaikan+re-run P7) ──┐
                                                       ├─► FASE 5 (konsolidasi) ─► FASE 6 (BAB 4) ─► FASE 7 (BAB 5) ─► FASE 8 (housekeeping)
FASE 2 (eksperimen sisa) ──────────────────────────────┤
FASE 3 (P8 oklusi) ────────────────────────────────────┤
FASE 4 (P9 counting) ──────────────────────────────────┘
```
FASE 2, 3, 4 boleh **paralel** setelah FASE 0. FASE 5 menunggu 1–4 selesai.

---

## FASE 0 — Keputusan yang mengunci angka & narasi 🎓👤
**Kenapa dulu:** empat keputusan ini mengubah angka/redaksi yang masuk BAB 4. Menulis sebelum ini = menulis ulang nanti.

- [ ] **K1 — Judul final.** Dokumen pembimbing v4 **dan** v7 memakai judul lama *"MODIFIKASI DETEKTOR NMS-FREE YOLO26 … DAN PELACAKAN BYTETRACK…"*, sedangkan CLAUDE.md §1 mencatat judul *"MODIFIKASI ARSITEKTUR … ATENSI HIBRIDA, P2…"*. **Tegaskan mana yang dipakai** (abstrak-body & BAB 3 tetap framing dua-pilar, jadi apa pun judulnya, isi aman).
- [ ] **K2 — Ambang oklusi.** Naskah v4/v7 Tabel 3.6: heavy > **0,40**; kode: **0,35**. Setujui satu nilai. *(Catatan: untuk data val tidak mengubah angka apa pun — objek maks o=0,286; hanya soal konsistensi naskah↔kode.)*
- [ ] **K3 — Aturan sel-minimum Wilcoxon.** Naskah v4/v7 (3.11.x): sel < 30 objek GT dikeluarkan dari uji signifikansi. Kode belum menerapkannya. Setujui untuk **mengikuti naskah** (disarankan — menyingkirkan sel tak-reliabel spt oklusi-heavy n=8).
- [ ] **K4 (A-01) — Framing hasil.** DALW signifikan hanya sebagai komponen komplementer (V8–V5), bukan berdiri sendiri (V4–V1). Sepakati redaksi klaim (selaras framing dua-pilar: "melengkapi baseline yang sudah kuat").
- [ ] **K5 (A-02) — Ambang lulus RQ5.** Tentukan target MAPE (mis. ≤ X%) & FPS (mis. ≥ Y). Dibutuhkan untuk menilai counting di BAB 4. *(Konteks: V8 penuh ~23 FPS.)*

🤖 **Bantuan Claude:** saya bisa menyiapkan draf pertanyaan terstruktur (1 halaman) untuk dibawa ke Bu Sandfreni yang memuat K1–K5 + konteks angkanya. **Minta:** "buatkan draf pertanyaan pembimbing".

**Keluaran fase:** 5 keputusan tercatat → saya perbarui `CLAUDE.md` (§1, §14, pending-decisions) + `logs/sesi.log`.

---

## FASE 1 — Perbaikan metodologi + re-run P7 🤖
**Prasyarat:** K2 & K3 diputuskan. **Estimasi:** ~15 menit (6 menit re-run).

- [ ] 🤖 Sesuaikan `y26_strata.py` `OCC_EDGES` bila K2 = 0,40.
- [ ] 🤖 Tambah filter **sel < 30 GT** di `y26_stats.py` (`paired_vectors`/`run_wilcoxon_suite`) + laporkan sel yang dikeluarkan terpisah (sesuai naskah).
- [ ] 🤖 Perbarui `test_eval.py` bila perlu, pastikan E1–E7 tetap LULUS.
- [ ] 🤖 Re-run: `python evaluate_all.py --data dataset/data.yaml --split test --variants all --refresh-cache` lalu `analyze_nmsfree.py`.
- [ ] 🤖 Perbarui `hasil/ringkasan_evaluasi.md` dengan angka final (n sel baru, p-value final).

**Verifikasi:** `eval_out/wilcoxon_ap5095.csv` memuat kolom sel-dikeluarkan; n hipotesis utama berubah dari 34 → (lebih kecil); `test_eval.py` LULUS.
**Keluaran:** angka Wilcoxon **metodologis-benar** — inilah yang masuk BAB 4.

---

## FASE 2 — Dua eksperimen sisa yang dijanjikan naskah 🤖
**Prasyarat:** FASE 0 (α ikut grid yang sama). **Estimasi:** ~4–6 jam GPU (background job). Boleh paralel dgn FASE 3/4.

- [ ] 🤖 **Sensitivitas α pada V4** (naskah hal 49 "dilaporkan pada BAB 4"): latih V4 pada α ∈ {0,5; 2,0} (α=1,0 sudah ada), σ=0,1 tetap.
  `python train_ablation.py --data dataset/data.yaml --variant V4 --alpha 0.5 --suffix _a0.5 --project <ABS>/runs_tesis` (ulangi α=2,0). Lalu evaluasi ketiganya → tabel sensitivitas.
- [ ] 🤖 **Pemeriksaan ketegaran normalisasi-per-bobot** (naskah hal 43): implementasikan varian loss yang membagi dengan Σwᵢ (bukan N), latih V8-varian-ini, bandingkan dengan V8 → pastikan gain bukan sekadar efek skala loss. *(Perlu tambahan kecil di `y26_dalw.py` + 1 run.)*

**Verifikasi:** `runs_tesis/V4_a0.5/`, `V4_a2.0/`, dan run robustness ada + hasil terangkum.
**Keluaran:** dua subbagian BAB 4 (sensitivitas α; pemeriksaan ketegaran).

---

## FASE 3 — P8: Validasi proksi oklusi 👤→🤖
**Prasyarat:** tidak ada (kit siap). **Estimasi:** 👤 ±20–30 menit anotasi.

- [ ] 👤 Anotasi 200 crop. **Dua jalur (pilih satu):**
  - **Offline (tercepat):** buka `anotasi_oklusi/anotasi.html` → nilai no/partial/heavy (tombol 1/2/3) → **Ekspor** → taruh `manual_oklusi.csv` di root repo.
  - **Roboflow:** ikuti `anotasi_oklusi/PANDUAN_ROBOFLOW.md` → `python roboflow_ke_oklusi.py --export <folder>`.
- [ ] 🤖 Hitung kesesuaian: `python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('manual_oklusi.csv','dataset/data.yaml',split='val'))"` → `hasil/validasi_oklusi.md`.

**Verifikasi:** `manual_oklusi.csv` ada (format `image,gt_index,tier`); angka agreement + matriks konfusi tercatat.
**Keluaran:** subbagian BAB 4 "validasi proksi oklusi" (menunaikan janji Subbab 3.3.3).

---

## FASE 4 — P9: Counting end-to-end (RQ5) 👤→🤖
**Prasyarat:** K5 (ambang RQ5). **Estimasi:** 👤 rekam + hitung manual (bervariasi).

- [ ] 👤 Taruh 1+ klip CCTV uji di `video_uji/` (mis. `uji_ruas1.mp4`).
- [ ] 👤 Pilih garis: `python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line x1,y1,x2,y2` → cek preview.
- [ ] 👤 Buat + isi GT: `python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template` → isi `count` manual (kelas: big-vehicle/car/two-wheeler; pejalan kaki dikecualikan).
- [ ] 🤖 Jalankan counting: `python y26_counting.py --video video_uji/uji_ruas1.mp4 --weights runs_tesis/V8/weights/best.pt --line <...> --interval-s 60 --gt video_uji/gt_uji_ruas1.csv --save-video`.
- [ ] 🤖 Rangkum `counting_out/summary.json` (MAE/RMSE/MAPE + %eksklusi y=0 + FPS) → `hasil/ringkasan_counting.md`.

**Verifikasi:** `counting_out/summary.json` ada; MAE/RMSE/MAPE/FPS terlaporkan.
**Keluaran:** subbagian BAB 4 "penghitungan end-to-end" + isi placeholder FPS/MAPE abstrak.

---

## FASE 5 — Konsolidasi: peta 18 placeholder + 2 naratif 🤖
**Prasyarat:** FASE 1–4 selesai (semua angka ada). **Estimasi:** ~30 menit.

- [ ] 🤖 Jalankan skill `isi-placeholder-bab4`: petakan tiap placeholder `[XX,X]`/`[0,0XX]`/naratif → sel artefak (`eval_out/`, `nmsfree_out/`, `counting_out/`, `validasi_oklusi.md`).
- [ ] 🤖 Buat `hasil/peta_placeholder_bab4.md`: tabel placeholder → nilai → sumber → status.
- [ ] 🤖 Tandai placeholder yang **masih** menunggu keputusan (mis. redaksi A-01) agar tidak diisi prematur.

**Verifikasi:** setiap placeholder abstrak/BAB 4 punya sumber angka yang jelas atau alasan tertunda.
**Keluaran:** peta lengkap — bahan tulis BAB 4.

---

## FASE 6 — Tulis BAB 4 (Hasil & Pembahasan) 🤖→👤
**Prasyarat:** FASE 5 + keputusan K1/K4. **Estimasi:** 🤖 draf per subbagian; 👤 review tiap subbagian.

Struktur (mengikuti janji naskah v7, urut):
- [ ] 4.1 Karakteristik dataset & distribusi kelas (dari label + `bukti_split_*.csv`)
- [ ] 4.2 Inisialisasi & transfer bobot (dari `logs/smoke.log`: HAM 97%/100%, P2 40%/62%)
- [ ] 4.3 Hasil grid search α,σ (dari `hasil/grid_search.md`)
- [ ] 4.4 Metrik global per varian (dari `eval_out/global_metrics.csv`)
- [ ] 4.5 Ablasi terstratifikasi + Wilcoxon + effect size (dari `eval_out/`, **pasca FASE 1**)
- [ ] 4.6 Sensitivitas α (V4) + pemeriksaan ketegaran (dari FASE 2)
- [ ] 4.7 Kompleksitas & efisiensi — Tabel 3.7 (dari `eval_out/complexity.csv`)
- [ ] 4.8 Analisis interaksi NMS-free: DR/CM/τ + stabilitas S(t) (dari `nmsfree_out/` + `nmsfree_probe.csv`)
- [ ] 4.9 Validasi proksi oklusi (dari FASE 3)
- [ ] 4.10 Penghitungan end-to-end (dari FASE 4)
- [ ] 4.11 Analisis galat (confusion matrix, dekomposisi FP/FN per strata, kasus gagal)
- [ ] 🤖 Isi 18 placeholder numerik dari peta FASE 5 (hanya yang berdata nyata).
- [ ] 👤 Review tiap subbagian (akurasi angka, framing dua-pilar, bahasa akademik anti-AI).

**Aturan menulis:** prosa murni tanpa bullet; desimal koma; istilah asing miring; sitasi [1]–[30]; bahasa kehati-hatian *preprint* untuk YOLO26; **jangan** klaim HAM/P2 sebagai kebaruan; laporkan hasil apa adanya (termasuk yang tak signifikan).

**Keluaran:** draf BAB 4 lengkap, direview.

---

## FASE 7 — Tulis BAB 5 (Kesimpulan & Saran) 🤖→👤
**Prasyarat:** BAB 4 final. **Estimasi:** 🤖 draf; 👤 review.

- [ ] 5.1 Kesimpulan per rumusan masalah (RQ1–RQ5) — jawab tiap RQ dengan angka BAB 4.
- [ ] 5.2 Kontribusi (metodologis: DALW komplementer; analitis: temuan DR/CM/S(t)).
- [ ] 5.3 Keterbatasan (jujur: DALW tak signifikan sendiri; strata heavy kosong; grid satu titik; 1 perangkat GPU).
- [ ] 5.4 Saran pengembangan.
- [ ] 👤 Review — pastikan konsisten dengan klaim BAB 1 & tak melebihi bukti.

**Keluaran:** draf BAB 5 lengkap, direview.

---

## FASE 8 — Housekeeping naskah (bisa kapan saja) 🤖👤
Perbaikan konsistensi yang sudah tercatat (tak menghalangi penulisan, tapi wajib sebelum final):

- [ ] **GPU:** "RTX 4060 8GB" → **"RTX 4060 Ti 8GB"** di 7 lokasi + Tabel 3.8 (perangkat asli ber-Ti).
- [ ] **Angka split:** naskah "sekitar 2.372/678/339" → aktual **2.372/679/338**.
- [ ] **Nomor persamaan:** pastikan rujukan naskah↔komentar kode selaras (S(t)=3.8 menggeser MAE/RMSE/MAPE→3.13–3.15, rank-biserial→3.16).
- [ ] **Diksi split "acak"** → "prosedur deterministik yang menjaga keterwakilan" (kode tanpa RNG).
- [ ] **Sumber Roboflow [17]:** rekonsiliasi `naufalfirdaus/traffic-merged` vs ekspor `sahabats-workspace/…-nkdvt`.
- [ ] **Tabel 3.8 versi pustaka:** tambah ultralytics 8.4.92, supervision 0.29.1, Python 3.11.9, torch 2.11.0+cu128.
- [ ] **`.bib`:** verifikasi tepat 30 entri sesuai [1]–[30].

---

## Cara memulai (langkah berikutnya)

1. 👤 **Putuskan FASE 0** (atau minta 🤖 "buatkan draf pertanyaan pembimbing").
2. Begitu K2 & K3 diputuskan → 🤖 jalankan **FASE 1** (re-run P7).
3. Paralel: 👤 mulai **FASE 3** (anotasi oklusi, tak perlu menunggu apa pun) & siapkan video **FASE 4**; 🤖 luncurkan **FASE 2** (background).
4. Setelah 1–4 beres → 🤖 **FASE 5 → 6 → 7**, Anda review; 🤖/👤 **FASE 8**.

**Pemantauan job:** `Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8`. Progres selalu tercatat di `logs/sesi.log` + CLAUDE.md §15.
