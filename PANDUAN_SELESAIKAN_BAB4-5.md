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

**Hasil kunci P7 — tiga hipotesis utama (angka nyata, unit AP50-95 per kelas×strata):**

| Hipotesis | Makna | p | r (rank-biserial) | Simpulan |
|---|---|---|---|---|
| **H1 · V8 vs V1** | model penuh vs baseline | 0,478 | +0,143 | tidak signifikan |
| **H2 · V4 vs V1** | DALW saja vs baseline | 0,469 | −0,144 | **tidak** didukung (p besar, bukan nyaris) |
| **H3 · V8 vs V5** | +DALW di atas HAM+P2 | 0,012 | +0,486 | **SIGNIFIKAN** (efek sedang) |

FPS: V1=32,4 … V8=23,3. **Catatan revisi:** angka final akan berubah setelah FASE 1 (filter sel-min-30 + bootstrap CI); H2 yang tidak didukung adalah **temuan jujur yang konsisten dengan ramalan tinjauan pustaka** (baseline YOLO26 sudah punya STAL sadar-ukuran → ruang perbaikan lebih sempit), bukan kegagalan — lihat aturan redaksi K4.

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
**Kenapa dulu:** keputusan ini mengubah angka/redaksi yang masuk BAB 4. Menulis sebelum ini = menulis ulang nanti.

> ~~K1 — Judul~~ **SUDAH SELESAI, bukan keputusan.** Judul final = naskah v7 *"MODIFIKASI DETEKTOR NMS-FREE YOLO26 DENGAN PEMBOBOTAN LOSS BERBASIS DENSITAS DAN PELACAKAN BYTETRACK…"*. Judul transisi "ARSITEKTUR … ATENSI HIBRIDA, P2 …" **sudah ditolak**. `CLAUDE.md` §1 + KB sudah dikoreksi (18 Jul). **Jangan** dibawa ke pembimbing (berisiko membuka ulang keputusan yang sudah tutup). 👤 Sisir naskah Word untuk sisa judul lama, terutama frasa "Ukuran Objek" / "Perkotaan Indonesia".

- [ ] **K2 — Ambang oklusi.** Naskah v4/v7 Tabel 3.6: heavy > **0,40**; kode: **0,35**. Setujui satu nilai. **Dampak nyata (data terverifikasi):** pada **val** tak berpengaruh (maks o=0,286 → heavy=0 di 0,35 maupun 0,40); pada **data uji** (yang dipakai P7) **berpengaruh** → heavy 8→4, partial 314→318. Jadi K2 bukan sekadar kosmetik.
- [ ] **K3 — Aturan sel-minimum Wilcoxon.** Naskah v4/v7 (3.11.5): sel < 30 objek GT dikeluarkan dari uji signifikansi, dilaporkan terpisah sebagai deskriptif. Kode belum menerapkannya (P7 pakai n=34, termasuk oklusi-heavy n=8 di test). Setujui **mengikuti naskah** (disarankan — sel <30 memang tak reliabel).
- [ ] **K4 (A-01) — Framing hasil DALW.** H2 (V4 vs V1) **tidak didukung**, p=0,469 (p besar, **bukan** nyaris signifikan — dilarang dihaluskan). H3 (V8 vs V5) **didukung**, p=0,012 r=+0,486. Aturan redaksi: (a) nyatakan eksplisit **H2 tidak didukung** di BAB 4 & keterbatasan BAB 5; (b) rumuskan kebaruan sebagai **kontribusi komplementer** (DALW menambah signifikan di atas HAM+P2), **bukan** peningkatan mandiri; (c) sisir BAB 1–2 untuk kalimat yang menyiratkan DALW cukup berdiri sendiri; (d) dua-pilar tetap (DALW=kebaruan, HAM/P2=instrumen); (e) laporkan semua apa adanya termasuk strata kosong. Penjelasan teoretis sudah ada di BAB 2 (baseline YOLO26 ber-STAL → ruang perbaikan lebih sempit dari CRL/MST/HIC-YOLOv5).
- [ ] **K5 (A-02) — Ambang lulus RQ5.** Tentukan target MAPE (mis. ≤ X%) & FPS (mis. ≥ Y). *(Konteks: V8 penuh ~23 FPS — di bawah 30 FPS.)*
- [ ] **K6 — Pengulangan multi-seed** (naskah Tabel 3.9, validitas internal): naskah menjanjikan **≥3 seed pada V1, V4, V5, V8** *"sepanjang anggaran memungkinkan; bila tidak, keterbatasan dinyatakan eksplisit di BAB IV"*. **Pilih:** jalankan (prioritas V4 & V8 penyangga kebaruan) **atau** nyatakan keterbatasan. Lihat FASE 2.
- [ ] **K7 — Cakupan data uji counting** (naskah 3.10.1): naskah menjanjikan **≥3 klip titik berbeda, ≥10 mnt/klip (lengang+padat), dua penghitung terpisah + tinjau selisih**. Tentukan yang realistis. **Bila dikurangi, ubah Subbab 3.10.1 DULU** sebelum BAB 4 — dilarang BAB 3 janji 3 klip/2 penghitung tapi BAB 4 lapor 1 klip/1 penghitung. Lihat FASE 4.

🤖 **Bantuan Claude:** saya bisa menyiapkan draf pertanyaan terstruktur untuk Bu Sandfreni memuat **K2–K7** (bukan K1) + konteks angka. **Minta:** "buatkan draf pertanyaan pembimbing".

**Keluaran fase:** keputusan K2–K7 tercatat → saya perbarui `CLAUDE.md` + `logs/sesi.log`.

---

## FASE 1 — Perbaikan metodologi + re-run P7 🤖
**Prasyarat:** K2 & K3 diputuskan. **Estimasi:** ~15 menit (6 menit re-run).

- [ ] 🤖 Sesuaikan `y26_strata.py` `OCC_EDGES` bila K2 = 0,40.
- [ ] 🤖 Tambah filter **sel < 30 GT** di `y26_stats.py` (`paired_vectors`/`run_wilcoxon_suite`) + laporkan sel yang dikeluarkan terpisah (sesuai naskah).
- [ ] 🤖 Perbarui `test_eval.py` bila perlu, pastikan E1–E7 tetap LULUS.
- [ ] 🤖 **Bootstrap CI 95%** (naskah 3.11.5 — WAJIB, sempat terlewat di roadmap awal): tambahkan ke `y26_stats.py`/`evaluate_all.py` perhitungan **selang kepercayaan bootstrap 95% untuk selisih mAP@0,5:0,95 antarvarian, 1.000 resampling pada tataran CITRA UJI** (bukan tataran objek — jaga keterkaitan antarobjek dalam satu citra). Laporkan selang untuk **ketiga hipotesis utama**. *(Penting: karena H2 tak signifikan, analisis yang tak bergantung asumsi independensi ini justru menopang argumen.)*
- [ ] 🤖 Re-run: `python evaluate_all.py --data dataset/data.yaml --split test --variants all --refresh-cache` lalu `analyze_nmsfree.py`.
- [ ] 🤖 Perbarui `hasil/ringkasan_evaluasi.md` dengan angka final (n sel baru, p-value final, **selang bootstrap**, sebaran oklusi test 0,35 vs 0,40).

**Verifikasi:** `eval_out/wilcoxon_ap5095.csv` memuat kolom sel-dikeluarkan + kolom CI bootstrap; n hipotesis utama berubah dari 34 → (lebih kecil); `test_eval.py` LULUS.
**Keluaran:** angka Wilcoxon **metodologis-benar** + selang bootstrap — inilah yang masuk BAB 4.

---

## FASE 2 — Dua eksperimen sisa yang dijanjikan naskah 🤖
**Prasyarat:** FASE 0 (α ikut grid yang sama). **Estimasi:** ~4–6 jam GPU (background job). Boleh paralel dgn FASE 3/4.

- [ ] 🤖 **Sensitivitas α pada V4** (naskah hal 49 "dilaporkan pada BAB 4"): latih V4 pada α ∈ {0,5; 2,0} (α=1,0 sudah ada), σ=0,1 tetap.
  `python train_ablation.py --data dataset/data.yaml --variant V4 --alpha 0.5 --suffix _a0.5 --project <ABS>/runs_tesis` (ulangi α=2,0). Lalu evaluasi ketiganya → tabel sensitivitas.
- [ ] 🤖 **Pemeriksaan ketegaran normalisasi-per-bobot** (naskah hal 43): implementasikan varian loss yang membagi dengan Σwᵢ (bukan N), latih V8-varian-ini, bandingkan dengan V8 → pastikan gain bukan sekadar efek skala loss. *(Perlu tambahan kecil di `y26_dalw.py` + 1 run.)*
- [ ] 🤖 **Pengulangan multi-seed (K6, naskah Tabel 3.9)**: bila K6 = jalankan → tambah argumen `--seed` di `train_ablation.py`, latih **V1, V4, V5, V8** pada ≥3 seed, laporkan **simpangan baku + rentang**. Bila mepet, prioritaskan **V4 & V8** (penyangga kebaruan). Bila K6 = tidak → siapkan kalimat keterbatasan eksplisit untuk BAB IV (naskah mengizinkan dengan syarat dinyatakan terbuka).

**Verifikasi:** `runs_tesis/V4_a0.5/`, `V4_a2.0/`, run robustness, dan (bila dijalankan) run multi-seed ada + hasil terangkum.
**Keluaran:** tiga subbagian BAB 4 (sensitivitas α; pemeriksaan ketegaran; stabilitas antar-seed / pernyataan keterbatasan).

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
**Prasyarat:** K5 (ambang RQ5) **dan** K7 (cakupan). **Estimasi:** 👤 rekam + hitung manual (bervariasi).

> ⚠️ **Naskah 3.10.1 menetapkan protokol ketat — patuhi atau turunkan janji naskah lebih dulu (K7):**
> **≥3 klip** dari titik pengamatan **berbeda** · masing-masing **≥10 menit** mencakup lengang **dan** padat · resolusi & laju frame asli **dilaporkan** · klip **bukan** dari sesi perekaman data latih · garis virtual tegak lurus arah dominan, di area bebas oklusi tetap, koordinat piksel **dicatat** · interval 1 menit · **dua penghitung terpisah**, interval yang berselisih **ditinjau ulang** sampai sepakat, **tingkat kesesuaian awal antar-penghitung dilaporkan** · tiga aturan kasus khusus (titik acuan = tengah sisi bawah bbox; kendaraan berhenti tak dihitung sampai lintas selesai; berbalik arah dihitung per arah).

- [ ] 👤 Taruh **≥3 klip** CCTV uji (titik berbeda, ≥10 mnt, lengang+padat, bukan sesi data latih) di `video_uji/`.
- [ ] 👤 Pilih garis tiap klip: `python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line x1,y1,x2,y2` → cek preview → catat koordinat + resolusi + FPS.
- [ ] 👤 Buat + isi GT: `python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template` → **dua penghitung** isi terpisah; bandingkan per interval; tinjau selisih; catat **kesesuaian awal**.
- [ ] 🤖 Jalankan counting tiap klip: `python y26_counting.py --video video_uji/<klip>.mp4 --weights runs_tesis/V8/weights/best.pt --line <...> --interval-s 60 --gt video_uji/gt_<klip>.csv --save-video`.
- [ ] 🤖 Rangkum `counting_out/summary.json` (MAE/RMSE/MAPE + %eksklusi y=0 + FPS) → `hasil/ringkasan_counting.md`, plus tabel per klip + koordinat garis + kesesuaian antar-penghitung.
- [ ] 🤖/👤 Perbarui `video_uji/README.md` & `siapkan_counting.py` (sudah diselaraskan ke protokol ini).

**Verifikasi:** ≥3 `counting_out/summary.json`; MAE/RMSE/MAPE/FPS + koordinat garis + kesesuaian penghitung terlaporkan.
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

- [ ] **GPU:** "RTX 4060 8GB" → **"RTX 4060 Ti 8GB"** di **6 lokasi** (v7; verifikasi hitungan sebelum ganti massal agar tak terlewat/dobel) + Tabel 3.8. Bila perangkat memang ber-Ti, samakan juga di `CLAUDE.md` & log.
- [ ] **Angka split:** naskah "sekitar 2.372/678/339" → aktual **2.372/679/338**.
- [ ] **Nomor persamaan:** pastikan rujukan naskah↔komentar kode selaras (S(t)=3.8 menggeser MAE/RMSE/MAPE→3.13–3.15, rank-biserial→3.16).
- [ ] **Diksi split "acak"** → "prosedur deterministik yang menjaga keterwakilan" (kode tanpa RNG).
- [ ] **Sumber Roboflow [17]:** rekonsiliasi `naufalfirdaus/traffic-merged` vs ekspor `sahabats-workspace/…-nkdvt`.
- [ ] **Tabel 3.8 versi pustaka:** tambah ultralytics 8.4.92, supervision 0.29.1, Python 3.11.9, torch 2.11.0+cu128.

**Revisi sidang yang belum tuntas (dari catatan penguji — konfirmasi ke berita acara):**
- [ ] **Poin 5 sidang HILANG** — catatan penguji melompat butir 4 → 6. Konfirmasi ke penguji / berita acara agar tak terlewat saat verifikasi revisi.
- [ ] **Butir 23** — tambah 1–2 rujukan **internasional bereputasi** counting kendaraan di Subbab 2.7.2 (kini hanya 3 rujukan nasional YOLOv8: [25][26][27]). ⚠️ **verifikasi web dulu**, masuk lewat **Mendeley** (bukan diketik di Word).
- [ ] **Butir 27** — lengkapi entri Mendeley: RT-DETR [19] hal **16965–16974** DOI **10.1109/CVPR52733.2024.01605**; YOLO-World [20] hal **16901–16911** DOI **10.1109/CVPR52733.2024.01599**; YOLOE [21] sudah lengkap (24591–24602).
- [ ] **`.bib` / Mendeley:** verifikasi tepat 30 entri [1]–[30]. ⚠️ **Daftar pustaka Word = content-control Mendeley (77 buah)** — menyunting langsung di Word **akan tertimpa** saat refresh; semua penambahan/perbaikan referensi **wajib lewat Mendeley**.
- [ ] Setelah edit di Word: **Ctrl+A lalu F9** untuk menyegarkan Daftar Isi/Tabel/Gambar/Rumus.

---

## Cara memulai (langkah berikutnya)

1. 👤 **Putuskan FASE 0 (K2–K7)** — atau minta 🤖 "buatkan draf pertanyaan pembimbing" (memuat K2–K7, bukan K1). *K1 judul sudah tutup.*
2. Begitu K2 & K3 diputuskan → 🤖 jalankan **FASE 1** (perbaikan + bootstrap CI + re-run P7).
3. Paralel: 👤 mulai **FASE 3** (anotasi oklusi, tak perlu menunggu apa pun) & siapkan **≥3 video** FASE 4; 🤖 luncurkan **FASE 2** (α-sens + robustness + multi-seed bila K6=jalankan).
4. Setelah 1–4 beres → 🤖 **FASE 5 → 6 → 7**, Anda review; 🤖/👤 **FASE 8**.

**Pemantauan job:** `Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8`. Progres selalu tercatat di `logs/sesi.log` + CLAUDE.md §15.

---

## Lampiran — Riwayat koreksi roadmap (18 Jul 2026)

Roadmap ini direvisi setelah dokumen `KOREKSI_PANDUAN_BAB4-5.md`. Semua klaim yang dapat dicek **diverifikasi benar** terhadap naskah v7 & data: (1) K1 judul bukan keputusan — judul NMS-free final, KB dikoreksi; (2) **bootstrap CI 95%/1.000-resampling-citra** dijanjikan naskah 3.11.5 → masuk FASE 1; (3) **multi-seed ≥3 pada V1/V4/V5/V8** dijanjikan Tabel 3.9 → K6/FASE 2; (4) **protokol counting 3.10.1** (≥3 klip/≥10 mnt/2 penghitung) → K7/FASE 4; (5) **H1 (V8–V1 p=0,478)** kini dilaporkan; (6) kontradiksi oklusi diselesaikan dengan data (val heavy=0 di 0,35≡0,40; test heavy 8→4, partial 314→318); (7) GPU **6 lokasi** (bukan 7); (8) revisi sidang poin 5/butir 23/butir 27 + alur Mendeley → FASE 8.
