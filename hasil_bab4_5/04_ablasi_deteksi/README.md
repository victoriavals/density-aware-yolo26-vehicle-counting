# 04 — Ablasi Deteksi: Metrik Global, Strata, Wilcoxon, Bootstrap CI

**Bagian paling penting folder ini.** Menjawab RQ2 (kontribusi komponen) dan RQ4
(performa terstratifikasi), serta memuat hasil pengujian tiga hipotesis utama tesis.

## Berkas

| Berkas | Isi |
|---|---|
| `global_metrics.csv` | P, R, F1, mAP50, mAP50-95 per varian (data uji, Pers. 3.8–3.11) |
| `strata_ap.csv` | **Sumber lengkap** — AP50 & AP50-95 per (varian × kelas × dimensi × strata), termasuk n_gt tiap sel |
| `wilcoxon_ap5095.csv`, `wilcoxon_ap50.csv` | Hasil uji Wilcoxon signed-rank: 3 hipotesis utama + seluruh pasangan sekunder (koreksi Holm), + rank-biserial + info sel yang dibuang |
| `bootstrap_ci.csv` | Selang kepercayaan bootstrap 95% (1.000 resample tataran citra) untuk selisih mAP50-95 ketiga hipotesis utama |
| `wilcoxon_info.json` | Metadata protokol uji (unit, ambang, aturan sel minimum) |
| `grafik_map_per_varian.png` | mAP@0,5 dan mAP@0,5:0,95 kedelapan varian (data uji) |
| `grafik_strata_size.png` / `_occlusion.png` / `_density.png` | AP50-95 rata-rata kelas per tier, untuk V1/V4/V5/V8 |
| `grafik_wilcoxon_hipotesis_utama.png` | Ukuran efek (rank-biserial) tiga hipotesis utama + nilai p |
| `grafik_bootstrap_ci.png` | Selang kepercayaan bootstrap tiga hipotesis utama |

## Tiga Hipotesis Utama — Baca Ini Dulu

| Hipotesis | Makna | Wilcoxon p | rank-biserial r | Bootstrap CI (mAP, poin %) | Simpulan |
|---|---|---|---|---|---|
| **H1: V8 vs V1** | model penuh vs baseline | 0,565 | +0,140 | **[+0,05; +2,08]** *tak memuat nol* | **Bertentangan** — lihat catatan di bawah |
| **H2: V4 vs V1** | DALW saja vs baseline | 0,208 | −0,300 | [−1,21; +1,00] memuat nol | **Tidak didukung** |
| **H3: V8 vs V5** | +DALW di atas HAM+P2 | **0,037** | **+0,487** | **[+1,26; +3,53]** *tak memuat nol* | **Signifikan (kedua uji sepakat)** |

### ⚠️ Kenapa H1 "bertentangan" antara dua uji — WAJIB dijelaskan di BAB 4, jangan disembunyikan

- **Wilcoxon** menguji median selisih AP pada **24 sel (kelas × strata)** — unit yang
  heterogen dan sedikit, sehingga daya ujinya rendah untuk mendeteksi efek kecil.
- **Bootstrap** menguji selisih **mAP agregat antar-citra** (338 citra, 1.000 resample)
  — unit yang jauh lebih banyak dan homogen, lebih sensitif terhadap efek kecil tapi
  konsisten.
- Kedua uji **valid**, mengukur pertanyaan yang sedikit berbeda: Wilcoxon menjawab
  "apakah keunggulan konsisten di seluruh strata?" (tidak), bootstrap menjawab "apakah
  ada keunggulan agregat yang bisa diandalkan?" (ya, tapi tipis — batas bawah CI
  hanya +0,0005).
- **Rekomendasi penulisan**: laporkan keduanya, jelaskan perbedaan unit analisis, dan
  simpulkan bahwa V8 punya **keunggulan global kecil namun tidak merata**, bukan
  keunggulan yang tegas di semua strata.

### H2 dan H3 — konsisten dan mendukung framing dua-pilar

- **H2 tidak didukung** (p=0,208, BUKAN nyaris signifikan — dilarang dihaluskan
  menjadi "cenderung positif": rank-biserial malah **negatif** −0,300). Ini **sejalan
  dengan ramalan BAB 2**: baseline YOLO26 sudah punya STAL (sadar ukuran objek),
  sehingga ruang perbaikan dari penambahan mekanisme densitas semata lebih sempit
  dibanding studi terdahulu yang memodifikasi baseline tanpa mekanisme serupa
  (CRL-YOLOv5, MST-YOLOv5, HIC-YOLOv5).
- **H3 signifikan pada kedua metode** — inilah **bukti kebaruan metodologis paling
  kokoh**: DALW memberi kontribusi nyata **sebagai pelengkap**, bukan berdiri sendiri.
  Rumuskan sebagai **kontribusi komplementer**, JANGAN sebagai peningkatan mandiri.

## Strata Mana yang Paling Terbantu DALW (kontras V8−V5, dari `strata_ap.csv`)

| Strata | AP50-95 V5 | AP50-95 V8 | Δ (V8−V5) |
|---|---|---|---|
| size/small | 0,340 | 0,402 | **+0,062** |
| size/medium | 0,528 | 0,539 | +0,011 |
| size/large | 0,795 | 0,717 | −0,078 |
| occlusion/no | 0,521 | 0,544 | +0,023 |
| occlusion/partial | 0,192 | 0,244 | **+0,053** |
| occlusion/heavy | 0,073 | 0,039 | −0,034 ⚠️ n kecil, tak bermakna (hanya big-vehicle & pedestrian punya GT) |
| density/sparse | 0,528 | 0,594 | **+0,066** |
| density/medium | 0,425 | 0,434 | +0,009 |
| density/dense | 0,338 | 0,367 | +0,029 |

**Pola jelas**: DALW paling membantu pada **objek kecil, oklusi parsial, dan densitas
rendah** — tepat sasaran perancangannya. Turun pada objek besar (wajar — pembobotan
densitas menomorduakan objek besar yang mudah). Heavy-occlusion **tidak bisa
disimpulkan** (lihat peringatan sel kecil di bawah).

## 12 Sel Dikeluarkan dari Uji (aturan `min_n_gt=30`, Subbab 3.11.5)

Terekam di kolom `sel_dibuang` pada `wilcoxon_ap5095.csv` baris manapun. Termasuk
**seluruh sel occlusion/heavy** (big-vehicle n=2, car n=0, pedestrian n=2,
two-wheeler n=0) dan beberapa sel size/large & density/dense kelas minoritas.
Sel ini dilaporkan **deskriptif saja** di `strata_ap.csv`, ditandai keterbatasan
sampel — jangan ditarik simpulan statistik darinya.

## Kalimat siap-adaptasi

> "Pengujian tiga hipotesis utama pada taraf signifikansi 5 persen terhadap unit AP
> per kombinasi kelas dan strata (24 sel setelah pengecualian sel berukuran kurang
> dari 30 objek) menunjukkan bahwa model penuh tidak berbeda signifikan dari baseline
> (p=0,565) maupun Pembobotan Loss Berbasis Densitas yang berdiri sendiri tidak
> berbeda signifikan dari baseline (p=0,208; ukuran efek rank-biserial −0,300).
> Sebaliknya, penambahan Pembobotan Loss Berbasis Densitas di atas kombinasi Modul
> Atensi Hibrida dan Lapisan Deteksi P2 menghasilkan perbedaan signifikan (p=0,037;
> rank-biserial +0,487), dikonfirmasi oleh selang kepercayaan bootstrap 95 persen atas
> selisih mAP@0,5:0,95 yang tidak memuat nol (+1,26 hingga +3,53 poin persen). Temuan
> ini mengindikasikan bahwa kebaruan metodologis penelitian ini bersifat komplementer
> terhadap arsitektur yang telah dimodifikasi, bukan kontribusi yang berdiri sendiri —
> sebuah hasil yang konsisten dengan analisis literatur pada Subbab 2.9 mengenai
> ruang perbaikan yang lebih sempit pada baseline yang telah memiliki mekanisme
> sadar-ukuran."

## Peringatan konsistensi angka

Angka di folder ini adalah **hasil FASE 1** (ambang oklusi 0,40 + aturan sel-minimum +
bootstrap CI) — **BUKAN** angka P7 asli (34 sel, ambang 0,35, tanpa bootstrap) yang
tercatat di `hasil/ringkasan_evaluasi.md` versi lama. Arah kesimpulan **sama** pada
kedua versi (H3 signifikan, H1/H2 tidak) — perbedaan metodologi tidak mengubah temuan.
Selalu kutip dari folder ini, bukan dokumen P7 lama.
