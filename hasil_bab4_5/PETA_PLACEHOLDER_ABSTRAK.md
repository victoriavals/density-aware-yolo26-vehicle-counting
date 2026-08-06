# Peta 18 Placeholder Abstrak → Data Nyata (FASE 5)

> Disusun 5 Agustus 2026 dari `hasil_bab4_5/` (sumber: `eval_out/`, `eval_out_fase2/`,
> `nmsfree_out/`, `counting_out/`). **Belum ada placeholder yang diisi ke naskah** — dokumen
> ini hanya memetakan. Pengisian menunggu keputusan **A-01/K4** (redaksi) dan **A-02/K5**
> (ambang RQ5).

Ke-18 placeholder numerik seluruhnya berada di **abstrak** (9 di ABSTRAK Indonesia hal. 2–3,
9 kembarannya di ABSTRACT Inggris hal. 4–5). BAB 4–5 belum ditulis sehingga belum
mengandung placeholder.

---

## 🚨 TEMUAN UTAMA: Kalimat abstrak TIDAK BISA sekadar diisi — harus DITULIS ULANG

Kalimat hasil pada abstrak v7 berbunyi:

> "…konfigurasi terbaik mencapai mAP@0,5 sebesar **[XX,X]** persen dan mAP@0,5:0,95 sebesar
> **[XX,X]** persen, **meningkat [X,X] poin persentase dibandingkan baseline YOLO26 standar
> dengan perbedaan yang signifikan secara statistik (p = [0,0XX])**."

Kalimat ini **memprasyaratkan tiga hal yang tidak didukung data**:

| Prasyarat kalimat | Kenyataan data | Status |
|---|---|---|
| mAP@0,5 model penuh > baseline | V8 = **77,97 %** vs V1 = **78,61 %** → **turun 0,64 poin** | ❌ tidak didukung |
| mAP@0,5:0,95 meningkat berarti | V8 = 53,75 % vs V1 = 53,56 % → naik **hanya 0,19 poin** | ⚠️ nyaris nol |
| Perbedaan signifikan secara statistik | Wilcoxon H1 **p = 0,565** (tidak signifikan) | ❌ tidak didukung |

Bahkan **V1 (baseline) memiliki mAP@0,5 tertinggi dari SELURUH varian** (78,61 %), dan V8
juga lebih rendah pada P (−1,38), R (−0,49), dan F1 (−0,87 poin).

**Konsekuensi:** mengisi placeholder apa adanya akan menghasilkan pernyataan yang **salah**.
Kalimat harus disusun ulang lebih dulu — inilah inti keputusan **A-01/K4**.

---

## Tabel pemetaan placeholder

Nomor baris merujuk teks abstrak Indonesia; kembarannya di ABSTRACT Inggris memakai angka
yang sama dengan format desimal titik.

| # | Placeholder | Yang diminta kalimat | Angka nyata | Sumber | Bisa diisi? |
|---|---|---|---|---|---|
| 1 | `[XX,X]` | mAP@0,5 konfigurasi terbaik | **78,6** (V1 baseline) atau **78,0** (V8 model penuh) | `04_ablasi_deteksi/global_metrics.csv` | ⚠️ tergantung definisi "terbaik" — lihat catatan A |
| 2 | `[XX,X]` | mAP@0,5:0,95 konfigurasi terbaik | **53,8** (V8) atau **55,0** (V4_a2.0) | idem + `06_sensitivitas_alpha/` | ⚠️ lihat catatan A |
| 3 | `[X,X]` | kenaikan poin persentase vs baseline | **+0,19** (mAP50-95) / **−0,64** (mAP50) | hitung dari global_metrics | ❌ kalimat perlu diubah |
| 4 | `[0,0XX]` | nilai p perbedaan vs baseline | **0,565** (H1, tidak signifikan) | `04_ablasi_deteksi/wilcoxon_ap5095.csv` | ❌ format `[0,0XX]` mengandaikan p<0,05 |
| 5 | `[X,X]` | kenaikan AP objek kecil & kepadatan tinggi | **oklusi parsial +5,4** pp & **objek kecil +3,0** pp (V8−V5, sel n_gt≥30); **kepadatan tinggi TIDAK dapat dinilai** | `04_ablasi_deteksi/delta_strata.csv` | ⚠️ **DIKOREKSI** — lihat catatan B |
| 6 | `[X,XX]` | MAE penghitungan | **1,97** | `09_counting_end_to_end/metrik_GABUNGAN.csv` | ✅ |
| 7 | `[X,XX]` | RMSE penghitungan | **4,95** | idem | ✅ |
| 8 | `[X,X]` | MAPE penghitungan (persen) | **37,2** | idem | ✅ (+ wajib sebut 68/180 y=0 dikecualikan) |
| 9 | `[XX]` | kecepatan inferensi (FPS) | **20** (pipeline end-to-end) | idem, kolom `fps_pipeline_rata2` = 20,47 | ✅ — **JANGAN** pakai 23,3 (FPS model murni) |

### Catatan B — koreksi angka strata (5 Agu 2026, setelah aturan sel-min diterapkan konsisten)

Versi pertama dokumen ini menulis **+5,1 pp (objek kecil)** dan **+3,3 pp (kepadatan tinggi)**.
Kedua angka itu **dihitung dari seluruh sel**, termasuk sel bervolume 1–27 objek — padahal sel
seperti itu justru dikeluarkan aturan `MIN_CELL_GT = 30` (Subbab 3.11.5) dari uji signifikansi.
Memakai aturan berbeda untuk uji dan untuk narasi adalah inkonsistensi yang mudah dibongkar.

Setelah aturan yang sama diterapkan (`04_ablasi_deteksi/delta_strata.csv`):

| Klaim lama | Kenyataan (sel n_gt≥30) |
|---|---|
| objek kecil +5,1 pp | **V8−V1 hanya +0,87 pp**; V8−V5 +3,02 pp. Angka +5,06 berasal dari sel *big-vehicle* n=17 (+17,64 pp) |
| kepadatan tinggi +3,3 pp | **GUGUR** — di strata *dense* hanya **pejalan kaki** (n=77) yang lolos ambang; kelas kendaraan n=1/11/21. Rata-rata sel yang lolos justru −1,31 pp |

Klaim yang **sah**: perbaikan terkuat pada **oklusi parsial** (V8−V5 +5,37 pp; V8−V1 +3,72 pp)
dan **objek kecil** (V8−V5 +3,02 pp) — dua dari tiga tantangan yang disebut BAB 1. Tantangan
ketiga (kepadatan ekstrem) **tidak dapat dinilai** dan wajib dinyatakan sebagai keterbatasan.
Rincian penuh: [K4_REDAKSI_HASIL.md §3b](K4_REDAKSI_HASIL.md).

### Catatan A — "konfigurasi terbaik" perlu didefinisikan lebih dulu

Tiga kandidat, tergantung kriteria:

| Kandidat | mAP@0,5 | mAP@0,5:0,95 | FPS | Catatan |
|---|---|---|---|---|
| **V1** (baseline) | **78,61 %** ⬆ | 53,56 % | **32,4** | mAP@0,5 & FPS tertinggi — tetapi ini *baseline*, bukan usulan |
| **V8** (model penuh) | 77,97 % | 53,75 % | 23,3 | konfigurasi yang diusulkan tesis |
| **V4_a2.0** (DALW saja, α=2,0) | 77,18 % | **54,96 %** ⬆ | **30,5** | mAP@0,5:0,95 tertinggi **dan** masih ≥30 FPS |

**Rekomendasi (DIKOREKSI 5 Agu 2026):** hapus kata "terbaik", ganti menjadi **"konfigurasi
penuh yang diusulkan (V8)"**. Rekomendasi sebelumnya — menobatkan **V4_a2.0** karena
mAP@0,5:0,95-nya tertinggi — **dibatalkan**: V4_a2.0 berasal dari eksperimen *sensitivitas* α
di luar delapan varian yang diregistrasi Tabel 3.3, sehingga memilihnya berdasarkan skor
*test-split* sama dengan seleksi pada data uji. Di antara delapan varian ablasi (α dibekukan
1,0), **V8 justru sudah tertinggi** pada mAP@0,5:0,95 (53,75 %) — jadi tidak ada yang perlu
dikorbankan. Bonus: konfigurasi yang dilaporkan abstrak menjadi sama dengan yang dipakai
penghitungan *end-to-end*, sehingga abstrak konsisten secara internal.

Temuan V4_a2.0 tetap dilaporkan, tetapi tempatnya di **BAB 4 subbab sensitivitas** sebagai
bukti empiris keterbatasan *grid search* satu titik (Subbab 3.9). Alasan lengkap:
[K4_REDAKSI_HASIL.md §1](K4_REDAKSI_HASIL.md).

---

## 2 placeholder naratif

| # | Placeholder | Isi yang tersedia |
|---|---|---|
| N1 | `[ringkasan temuan Duplicate Rate dan Confidence Margin setelah eksperimen]` | **Tersedia lengkap** — `05_analisis_nmsfree/`: DR naik pada varian ber-HAM (V5 +0,047, V8 +0,055 vs V1) tetapi turun pada P2-tanpa-HAM (V3 −0,058, V7 −0,017); pola sama pada CM (V5 +0,045, V8 +0,031; V3 −0,043, V7 −0,024). Kesimpulan: **HAM menstabilkan pencocokan one-to-one yang terganggu kerapatan prediksi P2.** |
| N2 | Kalimat penutup abstrak: "…DALW melengkapi mekanisme bawaan YOLO26" | **Didukung data** — H3 (V8 vs V5) p=0,037, r=+0,487, bootstrap CI [+1,26; +3,53] poin persen. Justru inilah temuan terkokoh; kalimat ini boleh dipertahankan. |

---

## Angka pendukung lain yang siap dikutip (bukan placeholder, tetapi dibutuhkan BAB 4)

| Besaran | Nilai | Sumber |
|---|---|---|
| Tiga hipotesis utama | H1 p=0,565 r=+0,140 · H2 p=0,208 r=−0,300 · **H3 p=0,037 r=+0,487** | `04_ablasi_deteksi/wilcoxon_ap5095.csv` |
| Selang bootstrap 95 % | H1 [+0,05; +2,08] · H2 [−1,21; +1,00] · H3 [+1,26; +3,53] poin persen | `04_ablasi_deteksi/bootstrap_ci.csv` |
| Unit uji | 24 sel (12 dibuang, aturan n_gt<30) | idem, kolom `sel_dibuang` |
| Grid search DALW | α\*=1,0 σ\*=0,1 → mAP50-95 val 0,6670 | `02_grid_search_dalw/` |
| Kompleksitas | V8: 9,68 M par · 26,4 GFLOPs · 8,64 GB VRAM · 11,47 jam latih | `03_kompleksitas_model/` |
| Sensitivitas α | α=2,0 test 54,96 % > α=1,0 53,66 % > α=0,5 54,00 % | `06_sensitivitas_alpha/` |
| Ketegaran normalisasi | V8_normw 53,62 % vs V8 53,75 % (p=0,944) → gain bukan efek skala loss | `07_ketegaran_normalisasi/` |
| Validasi oklusi | kesesuaian 68,0 % · kappa 0,410 · proksi tak pernah beri tier heavy | `08_validasi_oklusi/` |
| Dataset | 2.372/679/338 citra · 758 grup | `01_dataset/` |
| Counting | MAE 1,97 · RMSE 4,95 · MAPE 37,17 % · FPS 20,47 · 180 pengamatan | `09_counting_end_to_end/` |

---

## Urutan tindakan yang disarankan

1. **Putuskan A-01/K4** (redaksi hasil) bersama pembimbing — ini menentukan bentuk kalimat
   abstrak, bukan sekadar angkanya.
2. **Putuskan A-02/K5** (ambang RQ5) — menentukan apakah MAPE 37,2 % dan 20 FPS disebut
   "memenuhi standar penerapan praktis" atau dilaporkan deskriptif saja.
3. Definisikan **"konfigurasi terbaik"** secara eksplisit (rekomendasi: mAP@0,5:0,95 tertinggi).
4. Tulis ulang kalimat hasil abstrak, lalu isi placeholder 1–9 + N1/N2 dari tabel di atas.
5. Perbarui ABSTRACT Inggris agar identik (format desimal titik).
