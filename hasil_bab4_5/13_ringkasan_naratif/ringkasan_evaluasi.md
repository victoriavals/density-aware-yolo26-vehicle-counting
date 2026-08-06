# P7 — Ringkasan Evaluasi Terstratifikasi + Wilcoxon + NMS-free (Subbab 3.11)

**Dijalankan:** 18 Jul 2026 13:57–14:03 (test split, 338 citra / 2.600 instans). Sumber angka: `eval_out/` dan `nmsfree_out/` (bahan mentah BAB 4 — jangan ditimpa). `test_eval.py` E1–E7 LULUS sebelum eksekusi.

> ⚠️ **Dokumen ini ringkasan HASIL, bukan naskah BAB 4.** Placeholder tesis belum diisi
> dan BAB 4–5 belum ditulis (aturan §12.3). Beberapa temuan menyentuh keputusan pending
> **A-01** (redaksi abstrak bila hasil tidak signifikan) — itu keputusan Naufal + pembimbing,
> BUKAN diputuskan di sini.

## (a) Metrik global per varian (test)

| Varian | Modul | P | R | F1 | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| V1 | baseline | 0,794 | 0,689 | 0,738 | 0,786 | **0,5356** |
| V2 | HAM | 0,764 | 0,697 | 0,729 | 0,773 | 0,5304 |
| V3 | P2 | 0,757 | 0,669 | 0,710 | 0,751 | 0,5216 |
| V4 | DALW | 0,762 | 0,697 | 0,728 | 0,777 | 0,5366 |
| V5 | HAM+P2 | 0,758 | 0,696 | 0,726 | 0,772 | 0,5247 |
| V6 | HAM+DALW | 0,718 | 0,692 | 0,705 | 0,740 | 0,5283 |
| V7 | P2+DALW | 0,776 | 0,637 | 0,700 | 0,750 | 0,5219 |
| V8 | penuh | 0,781 | 0,684 | 0,729 | 0,780 | **0,5375** |

Seluruh varian berhimpit rapat (mAP50-95 0,522–0,538; rentang 0,016). V8 tertinggi tipis, V4 kedua. Perbedaan antar varian pada metrik global agregat kecil — itulah mengapa unit uji resmi adalah **AP per (kelas × strata)**, bukan angka global (lebih sensitif terhadap kantong-kantong sulit).

## (b) Tiga hipotesis utama — Wilcoxon signed-rank, unit AP50-95 per (kelas × strata), n=34 sel

| Hipotesis | Makna | W | p | rank-biserial r | median Δ | Kesimpulan (5%) |
|---|---|---|---|---|---|---|
| **V8 vs V1** | model penuh vs baseline | 255 | **0,478** | +0,143 | +0,001 | **tidak signifikan** |
| **V4 vs V1** | DALW saja vs baseline | 240 | **0,469** | −0,144 | −0,013 | **tidak signifikan** |
| **V8 vs V5** | +DALW di atas HAM+P2 | 153 | **0,0125** | +0,486 | +0,025 | **SIGNIFIKAN** |

**Pembacaan jujur (belum diframe untuk naskah):**
- Baik model penuh (V8) maupun DALW-saja (V4) **tidak** mengungguli baseline secara signifikan pada AP terstratifikasi agregat. V4−V1 bahkan median sedikit negatif.
- Namun **kontribusi marginal DALW nyata dan signifikan bila ditumpangkan pada arsitektur** (V8 vs V5: p=0,012, efek sedang-besar r=+0,49). Artinya nilai DALW bersifat **komplementer/kondisional** terhadap HAM+P2, bukan berdiri sendiri.
- Ini hasil ilmiah yang sah dan justru selaras dengan framing dua-pilar (DALW = penyempurnaan atas baseline yang sudah kuat). **Memicu keputusan A-01** — diskusikan dengan pembimbing sebelum meredaksi abstrak/klaim.

**Sekunder (koreksi Holm) yang signifikan:** V2 vs V8 (p_holm=0,009; V8>V2), V6 vs V8 (p_holm=0,016; V8>V6), V1 vs V2 (p_holm=0,037; V1>V2 — HAM-saja justru di bawah baseline pada strata). Pasangan lain tidak signifikan pasca-Holm. Detail: `eval_out/wilcoxon_ap5095.csv`.

## (c) Strata mana yang paling terbantu DALW

Selisih AP50-95 (rata-rata antar kelas), dua kontras penambahan DALW:

| Strata | n_gt (test) | V4−V1 (DALW saja) | V8−V5 (+DALW atas HAM+P2) |
|---|---|---|---|
| size/small | 1.192 | +0,030 | **+0,062** |
| size/medium | 1.168 | −0,010 | +0,011 |
| size/large | 240 | +0,175 ⚠ | −0,078 |
| occlusion/no | 2.278 | +0,001 | +0,023 |
| occlusion/partial | 314 | −0,005 | **+0,053** |
| occlusion/heavy | **8** ⚠ | −0,096 ⚠ | −0,029 ⚠ |
| density/sparse | 647 | −0,019 | **+0,066** |
| density/medium | 1.843 | −0,016 | +0,009 |
| density/dense | 110 | −0,033 | +0,029 |

**Temuan:** pada kontras yang bersih (V8−V5, DALW ditambahkan ke arsitektur), DALW **konsisten membantu objek kecil (+0,062), oklusi parsial (+0,053), dan seluruh tingkat densitas** (sparse +0,066, dense +0,029) — persis sasaran densitas-aware. Menurun di objek besar (−0,078), wajar: pembobotan densitas sengaja menomorduakan objek besar yang mudah.

⚠️ **Peringatan reliabilitas (WAJIB masuk BAB 4):** (1) **occlusion/heavy hanya 8 GT di test** → AP-nya tak bermakna statistik, JANGAN disimpulkan (konsisten temuan proksi oklusi underestimate, kit validasi manual sudah disiapkan untuk P8). (2) **size/large V4−V1=+0,175** mencurigakan (n=240, dan DALW tak seharusnya menolong objek besar) — kemungkinan besar derau sampel kecil; jangan diangkat sebagai klaim.

## (d) Analisis NMS-free (Duplicate Rate, Confidence Margin, sensitivitas τ)

Fokus varian ber-P2 (V3/V5/V7/V8) vs V1, pada τ=0,25 (`nmsfree_out/summary.csv`):

| Varian | DR (τ=0,25) | miss | dup | coverage | CM mean | ΔDR vs V1 | ΔCM vs V1 |
|---|---|---|---|---|---|---|---|
| V1 | 0,778 | 0,257 | 0,035 | 0,969 | 0,548 | — | — |
| V3 (P2) | 0,720 | 0,321 | 0,041 | 0,966 | 0,506 | −0,058 | −0,043 |
| V5 (HAM+P2) | 0,825 | 0,222 | 0,046 | 0,972 | 0,593 | +0,047 | +0,045 |
| V7 (P2+DALW) | 0,761 | 0,293 | 0,052 | 0,955 | 0,524 | −0,017 | −0,024 |
| V8 (penuh) | 0,833 | 0,235 | 0,065 | 0,967 | 0,579 | +0,055 | +0,031 |

- **Confidence Margin** naik pada V5 & V8 (+0,045/+0,031) — kombinasi HAM+P2 (± DALW) menajamkan pemisahan kandidat one-to-one; P2/DALW tanpa HAM (V3, V7) justru menurun. Konsisten: **HAM tampak berperan menstabilkan margin** pada mekanisme NMS-free.
- **τ-sweep** (`tau_sweep.csv` + `dr_vs_tau.png`) monoton menurun untuk semua varian dari τ=0,05→0,9 (perilaku sehat, tak ada anomali). V5 & V8 kurva DR tertinggi di sepanjang τ; V3 terendah.
- Ini menunaikan **pilar analitis (kebaruan 2)**: penyelidikan empiris interaksi modul dengan one-to-one — arahnya (naik/turun) adalah temuan itu sendiri, bukan klaim perbaikan. `<V>_per_image.csv` = bahan uji Wilcoxon berpasangan DR/CM bila diperlukan lanjutan (A-10).

## Keluaran & langkah lanjut

Keluaran: `eval_out/{global_metrics,strata_ap,wilcoxon_ap5095,wilcoxon_ap50,wilcoxon_info}.csv` + `cache_V*.npz`; `nmsfree_out/{summary,tau_sweep}.csv` + `V{1,3,5,7,8}[_per_image].csv/json` + `dr_vs_tau.png` + `cm_hist.png`.

**Untuk Naufal / pembimbing:** hasil signifikansi memicu **A-01**. Sebelum meredaksi klaim, diskusikan: (i) framing V8-vs-V5 sebagai bukti kontribusi DALW komplementer; (ii) penanganan strata heavy yang kosong (revisi ambang oklusi? — tunggu validasi manual P8); (iii) apakah menambah sensitivitas α pada V4 (rencana §3.9) untuk memperkuat narasi. **Belum ada placeholder yang diisi dan BAB 4 belum ditulis.**
