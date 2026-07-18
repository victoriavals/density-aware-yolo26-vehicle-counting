# Uji Statistik: Wilcoxon + Holm + Rank-Biserial — Statistical testing protocol

> **EN — TL;DR:** Paired Wilcoxon signed-rank test on AP-per-(class × stratum) cells (never the global row); three PRIMARY hypotheses (V8−V1, V4−V1, V8−V5) at α = 5% with no correction, all other pairs SECONDARY under Holm step-down. Effect size is rank-biserial r = (W⁺ − W⁻)/(W⁺ + W⁻) (Eq. 3.15), `zero_method="wilcox"`. Actual P7 result: V8−V1 and V4−V1 not significant, **V8−V5 p = 0,0125, r = +0,486 significant** → DALW is complementary/conditional, not standalone; this triggers decision A-01.

Modul: `y26_stats.py` (Subbab 3.11.4–3.11.5). Diuji oleh `test_eval.py` E4. Semua angka hasil di halaman ini berasal dari eksekusi P7 (`eval_out/wilcoxon_ap5095.csv`); ringkasan naratifnya di `hasil/ringkasan_evaluasi.md`.

## 1. Unit uji — AP per (kelas × strata), TANPA baris global

Unit pasangan Wilcoxon untuk perbandingan deteksi adalah **nilai AP per kombinasi (kelas × dimensi strata × tier strata)**, bukan angka mAP global agregat. Alasannya metodologis: mAP global antarvarian berhimpit rapat (test mAP50-95 hanya berkisar 0,522–0,538), sehingga rata-rata agregat menutupi kantong-kantong sulit; uji per-sel jauh lebih sensitif terhadap ukuran kecil, oklusi, dan densitas tinggi yang justru menjadi target penelitian.

Penyejajaran sel dilakukan `paired_vectors(rows_a, rows_b, metric, include_global=False)`. Kunci sel adalah `(r["cls"], r["dim"], r["stratum"])`; hanya sel yang **ada di kedua varian** yang dipasangkan. Parameter `include_global=False` (default) **membuang baris `dim == "global"`** agar unit murni strata — ini invarian metodologis yang tidak boleh dilonggarkan (lihat [Invarian metodologi](../rules/methodology-invariants.md)). Pada P7 ini menghasilkan **n = 34 sel** per pasangan.

Metrik default `metric="ap5095"` (AP@0,5:0,95); tersedia pula `metric="ap50"` untuk keluaran `wilcoxon_ap50.csv`. Dimensi strata: ukuran (small/medium/large), oklusi (no/partial/heavy), densitas (sparse/medium/dense) — lihat [Evaluasi](evaluation.md) dan [Dataset](dataset.md).

## 2. Uji Wilcoxon berpasangan — `wilcoxon_pair`

`wilcoxon_pair(x, y, alternative="two-sided")` menjalankan `scipy.stats.wilcoxon` dengan ketentuan:

- **Pasangan NaN dibuang** lebih dulu (masker `~(isnan(x) | isnan(y))`) — sel yang salah satu varian-nya kosong (mis. `n_gt == 0`) tidak ikut.
- **`zero_method="wilcox"`** — selisih dᵢ = xᵢ − yᵢ yang bernilai nol dibuang dari perhitungan peringkat (konvensi Wilcoxon klasik). `method="auto"` membiarkan scipy memilih p-value eksak vs aproksimasi normal.
- Bila jumlah selisih non-nol `n_eff < 1` (semua sama), fungsi mengembalikan `W=0.0, p=1.0` tanpa memanggil scipy (mencegah error).
- Keluaran dict memuat: `n` (pasangan valid), `n_eff` (selisih non-nol), `median_diff`, `mean_diff`, `rank_biserial`, `W_plus`, `W_minus`, `W`, `p`.

Verifikasi kebenaran ada di `test_eval.py` E4: hasil `wilcoxon_pair` cocok dengan `scipy.stats.wilcoxon` hingga 1e-12, pasangan NaN benar-benar terbuang (`n` turun dari 30 → 27), dan `wilcoxon_pair(y, y)["p"] == 1.0`.

## 3. Tiga hipotesis UTAMA vs SEKUNDER

`PRIMARY_PAIRS = (("V8","V1"), ("V4","V1"), ("V8","V5"))` — tiga hipotesis utama diuji pada **taraf 5% tanpa koreksi apa pun**. Ini keputusan desain (CLAUDE.md §6): pertanyaan penelitian inti hanya tiga, sehingga tidak perlu "dihukum" koreksi keluarga.

- **V8 − V1**: kontribusi model penuh (HAM + P2 + DALW) atas baseline YOLO26.
- **V4 − V1**: kontribusi Pembobotan *Loss* Berbasis Densitas berdiri sendiri atas baseline.
- **V8 − V5**: kontribusi marginal DALW ketika ditumpangkan pada arsitektur HAM + P2 (kontras paling bersih untuk isolasi efek DALW).

`run_wilcoxon_suite` membangun **seluruh pasangan** antarvarian (`all_pairs`), menyingkirkan tiga pasangan utama (dan pembalikannya), lalu sisanya menjadi keluarga **SEKUNDER** yang p-value-nya dikoreksi Holm. Kolom `family` menandai `"primary"`/`"secondary"`; `signif_5pct` memakai `p_holm` untuk sekunder dan `p` mentah untuk utama.

> Catatan framing (aturan NEVER): HAM dan Lapisan P2 adalah **instrumen**, bukan klaim kebaruan. Kontras V8−V5 menguji nilai tambah DALW, dan setiap peningkatan diframe sebagai perbaikan atas *baseline* YOLO26 yang sudah kuat (ProgLoss + STAL). Lihat [Framing kebaruan](thesis-framing.md).

## 4. Koreksi Holm step-down — `holm`

`holm(pvals)` mengurutkan p-value menaik lalu menerapkan Holm–Bonferroni step-down: p terkoreksi ke-i = max berjalan dari `(m − i) * p`, dipotong di 1,0 dan dijaga monoton. Berlaku **hanya untuk keluarga sekunder** (tiga hipotesis utama tidak dikoreksi). Uji baku di `test_eval.py` E4: `holm({"a":0.01,"b":0.04,"c":0.03})` → `a≈0,03; c≈0,06; b≈0,06`.

## 5. Ukuran efek rank-biserial (Pers. 3.15) — `rank_biserial`

r = (W⁺ − W⁻) / (W⁺ + W⁻)

di mana W⁺/W⁻ adalah jumlah peringkat selisih positif/negatif (peringkat dihitung dari `|d|` dengan **rata-rata untuk nilai kembar**, selisih nol dibuang lebih dulu — konsisten `zero_method="wilcox"`). Rentang −1..+1; **positif berarti x konsisten lebih unggul dari y**. Fungsi mengembalikan `(r, W_plus, W_minus)` dan menghasilkan `nan` bila seluruh selisih nol. Ukuran efek ini ditambahkan atas permintaan revisi pembimbing (CLAUDE.md §15) dan dicetak di kolom CSV `evaluate_all.py`.

## 6. Peta fungsi

| Fungsi | Peran | Subbab |
|---|---|---|
| `paired_vectors(a,b,metric,include_global=False)` | Sejajarkan sel (kelas × dim × strata); buang baris global | 3.11.4 |
| `wilcoxon_pair(x,y,alternative)` | Wilcoxon berpasangan + statistik ringkas; `zero_method="wilcox"` | 3.11.4 |
| `holm(pvals)` | Koreksi Holm step-down untuk keluarga sekunder | 3.11.4 |
| `rank_biserial(d)` | Ukuran efek r = (W⁺−W⁻)/(W⁺+W⁻) (Pers. 3.15) | 3.11.5 |
| `run_wilcoxon_suite(rows_by_variant,metric)` | Orkestrasi 3 utama (tanpa koreksi) + sekunder (Holm) | 3.11.4 |

## 7. Hasil aktual P7 (18 Jul 2026)

Wilcoxon signed-rank, unit AP50-95 per (kelas × strata), **n = 34 sel**. Sumber: `eval_out/wilcoxon_ap5095.csv`; ringkasan penuh di [progres](../status/progress.md) dan `hasil/ringkasan_evaluasi.md`.

| Hipotesis (utama) | W | p | rank-biserial r | median Δ | Kesimpulan 5% |
|---|---|---|---|---|---|
| **V8 vs V1** (penuh vs baseline) | 255 | 0,478 | +0,143 | +0,001 | tidak signifikan |
| **V4 vs V1** (DALW saja vs baseline) | 240 | 0,469 | −0,144 | −0,013 | tidak signifikan |
| **V8 vs V5** (+DALW atas HAM+P2) | 153 | **0,0125** | **+0,486** | +0,025 | **SIGNIFIKAN** |

**Sekunder signifikan pasca-Holm** (`family="secondary"`): V2 vs V8 (p_holm = 0,009; V8 > V2), V6 vs V8 (p_holm = 0,016; V8 > V6), dan V1 vs V2 (p_holm = 0,037; V1 > V2 — HAM-saja justru di bawah baseline pada strata). Pasangan lain tidak signifikan setelah koreksi.

Nilai desimal di narasi memakai koma (p = 0,0125; r = +0,486); nilai apa adanya di CSV/kode memakai titik (`0.0125`, `0.486`, ambang `p_eff < 0.05`).

## 8. Interpretasi jujur — komplementer, memicu A-01

Baik model penuh (V8) maupun DALW-saja (V4) **tidak** mengungguli baseline secara signifikan pada AP terstratifikasi agregat; V4−V1 bahkan bermedian sedikit negatif (−0,013). Namun **kontribusi marginal DALW nyata dan signifikan ketika ditumpangkan pada arsitektur** (V8 vs V5: p = 0,0125, efek sedang-besar r = +0,486). Artinya nilai Pembobotan *Loss* Berbasis Densitas bersifat **komplementer/kondisional** terhadap HAM + P2, bukan berdiri sendiri.

Ini hasil ilmiah yang sah dan selaras dengan framing dua-pilar (DALW = penyempurnaan atas *baseline* yang sudah kuat). Karena tiga hipotesis utama tidak seluruhnya signifikan, temuan ini **memicu keputusan pending A-01** (redaksi/alternatif abstrak bila hasil tidak signifikan) — itu keputusan Naufal bersama pembimbing, **bukan** diputuskan di basis pengetahuan ini. Jangan mengisi placeholder atau menulis draf BAB 4–5 berdasarkan angka di atas.

Peringatan reliabilitas yang wajib menyertai penafsiran: strata **occlusion/heavy hanya 8 GT** di test (AP tak bermakna statistik), dan **size/large V4−V1 = +0,175** diduga derau sampel kecil (n = 240) — keduanya jangan diangkat sebagai klaim. Detail di [Evaluasi](evaluation.md).

## Tautan terkait

- [Keputusan pending](../status/pending-decisions.md) — A-01 (terpicu), A-10 (stabilitas *assignment* + sensitivitas τ)
- [Evaluasi terstratifikasi](evaluation.md) — asal baris `stratified_ap`, tier strata, protokol ignore
- [Analisis NMS-free](nmsfree-analysis.md) — DR/CM per citra sebagai unit Wilcoxon lanjutan (A-10)
- [Framing kebaruan](thesis-framing.md) — dua pilar; HAM/P2 = instrumen
- [Invarian metodologi](../rules/methodology-invariants.md) — unit uji tanpa baris global, 3 hipotesis utama, MAPE y>0
