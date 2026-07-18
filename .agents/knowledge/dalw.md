# Pembobotan Loss Berbasis Densitas (DALW) — Density-Aware Loss Weighting

> **EN — TL;DR:** DALW is the thesis' sole *methodological* novelty: a per-object loss weight `w_i = 1 + α·ρ̂_i` derived from local ground-truth density, injected inside `v8DetectionLoss` so it applies to **both** NMS-free heads via `E2ELoss` while ProgLoss + STAL stay intact. Weights come from GT under `torch.no_grad` (recomputed post-mosaic), the loss normalizer is untouched, grid winner is `α=1.0, σ=0.10`. P7: DALW alone (V4−V1) is **not** significant but the full model over HAM+P2 (V8−V5) **is** → DALW is complementary, not standalone.

Berkas sumber: `y26_dalw.py` (subbab tesis 3.6.3, Pers. 3.2–3.5). Uji kebenaran: `test_smoke.py::t1_math` (T1) dan `test_smoke.py::t4_loss` (T4). DALW adalah **satu-satunya kebaruan metodologis** tesis ini (Pilar 1 dari framing dua-pilar — lihat [Framing kebaruan](thesis-framing.md)); HAM dan Lapisan P2 tetap *instrumen*, bukan klaim kebaruan.

## 1. Definisi matematis (Persamaan 3.2–3.5)

Densitas lokal setiap objek `i` dihitung dari pusat kotak *ground truth* `c_i` (koordinat ternormalisasi [0,1]) memakai *kernel* Gaussian atas seluruh objek lain `j` pada citra yang sama:

```
ρ_i     = Σ_{j≠i} exp( −‖c_i − c_j‖² / (2σ²) )        (3.2)
ρ̂_i     = ρ_i / (ρ_i + 1)                              (3.3)   → rentang [0, 1)
w_i     = 1 + α · ρ̂_i                                  (3.4)
L       = (1/N) Σ_i w_i · L_i                          (3.5)
```

Semantiknya: objek di area padat memperoleh `ρ_i` besar → `ρ̂_i` mendekati 1 → bobot `w_i` mendekati `1 + α`, sehingga kontribusi *loss*-nya diperkuat. Objek terisolasi memperoleh `ρ_i = 0` → `w_i = 1` (netral). Normalisasi Pers. 3.3 (`ρ/(ρ+1)`) membatasi bobot ke rentang tertutup `[1, 1+α)` agar tidak meledak pada frame ekstrem (>25 objek/frame, ciri lalu lintas heterogen padat — lihat [Dataset](dataset.md)).

Dalam kode (`density_weights`, `y26_dalw.py`): jarak kuadrat via `torch.cdist(...).pow(2)`, *kernel* `exp(−d²/2σ²)`, koreksi diagonal `ρ = kern.sum(-1) − valid` untuk mewujudkan syarat `j≠i` (karena `exp(0)=1` pada `i=i`), dan slot *padding* (GT tak valid) dipaksa berbobot 1,0.

**Melengkapi STAL, bukan menggantikannya.** STAL bawaan YOLO26 bekerja di **penetapan label** berbasis *ukuran*; DALW bekerja di **penghitungan loss** berbasis *densitas*. Keduanya ortogonal dan aktif bersamaan (Tabel 3.2 tesis).

## 2. Titik injeksi & keputusan A-11 (kedua head)

**A-11 diputus: `w_i` berlaku pada KEDUA cabang head** *(one-to-many* dan *one-to-one)*. Mekanismenya (diverifikasi terhadap ultralytics 8.4.92):

- `DetectionModel.init_criterion` di-*monkey-patch* oleh `apply_dalw(α, σ)` agar untuk model *end2end* mengembalikan `E2ELoss(self, loss_fn=DALWDetectionLoss)`.
- `E2ELoss` membangun **dua** cabang dari `loss_fn` yang sama: `one2many` (`tal_topk=10`) dan `one2one` (`tal_topk=7, topk2=1`), lalu mencampur keduanya dengan *gain* **ProgLoss** yang meluruh 0,8 → 0,1 sepanjang epoch.
- Karena `w_i` disuntik **di dalam** `v8DetectionLoss` (kelas induk), ia otomatis ikut ke kedua cabang tanpa menyentuh ProgLoss:

```
L = Σ_b g_b(t) · Σ_i w_i · L_{b,i}  =  Σ_i w_i · ( Σ_b g_b(t) L_{b,i} )
```

yang identik dengan Pers. 3.5 bila `L_i` diambil sebagai total *loss* bawaan YOLO26. **ProgLoss dan STAL tetap utuh** di atas DALW. Detail mekanisme *monkey-patch* dan alasan `apply_dalw` harus dipanggil SEBELUM `model.train()` ada di [Mekanisme injeksi kode](../architecture/code-injection.md).

`DALWDetectionLoss` menyalin metode `get_assigned_targets_and_loss` dari `ultralytics/utils/loss.py:400–463` versi **8.4.92** dengan tiga sisipan bertanda `# === DALW`. Versi ini **TERKUNCI**: bila ultralytics berganti versi dan T4 gagal, jangan lanjut sebelum metode disesuaikan (lihat CLAUDE.md §13).

## 3. Detail penempatan bobot (tiga sisipan)

| Sisipan | Lokasi di loss | Perlakuan | Alasan |
|---|---|---|---|
| DALW (1/3) | setelah `preprocess` GT | hitung `w_gt` per objek dari `centers` ternormalisasi, di dalam `torch.no_grad` | bobot = konstanta per iterasi, tanpa gradien tambahan |
| DALW (2/3) — cls | `bce_loss` berbentuk `(bs, A, nc)` | kalikan `w_anc.unsqueeze(-1)` **per-anchor**; anchor latar belakang berbobot 1,0 | bobot bersifat per-OBJEK; hanya *foreground* yang diperkuat |
| DALW (3/3) — box | `bbox_loss(...)` | teruskan `target_scores * w_anc` (BboxLoss memakai `target_scores` sebagai bobot internal) | menghasilkan `w_i · L_box,i` tanpa memodifikasi target |

Pemetaan bobot GT → anchor: `w_anc = w_gt.gather(1, target_gt_idx.clamp(min=0))` lalu `torch.where(fg_mask, w_anc, 1)`. Artinya tiap anchor *foreground* mewarisi bobot objek GT yang di-*assign* padanya oleh STAL.

**Normalizer `target_scores_sum` TIDAK diubah.** Ini krusial: dengan pembilang terbobot (`Σ w_i L_i`) tetapi penyebut tak terbobot, DALW benar-benar **menguatkan** kontribusi objek padat sesuai semantik `(1/N) Σ w_i L_i`, bukan sekadar merata-ratakan ulang.

## 4. Sumber bobot: ground truth, no_grad, pasca-augmentasi

- **Dari ground truth**, bukan prediksi — `w_i` dihitung dari `batch["bboxes"]` (label), sehingga stabil dan bebas *feedback loop* prediksi.
- **`torch.no_grad`** — bobot adalah konstanta per objek per iterasi; tidak menambah jalur gradien maupun kompleksitas *backward*.
- **Dihitung ulang pasca-augmentasi mosaic** — karena bobot diturunkan dari label batch DI DALAM *loss*, ia otomatis mencerminkan geometri hasil augmentasi (mosaic mengubah kepadatan efektif). Ini memenuhi invarian Subbab 3.4 tesis: *densitas dihitung ulang pasca-augmentasi*. Mosaic dimatikan 10 epoch terakhir (invarian metodologi — lihat [Invarian metodologi](../rules/methodology-invariants.md)).

## 5. Hiperparameter & grid search

*Grid search* `α ∈ {0,5; 1,0; 2,0} × σ ∈ {0,05; 0,10; 0,20}` (koordinat ternormalisasi) dijalankan sekali pada V8 dengan pelatihan dipersingkat (60 epoch), kriteria mAP@0,5:0,95 validasi, lalu **dibekukan** ke `dalw_best.json`.

**Pemenang grid: `α = 1,0`, `σ = 0,10`** (nilai JSON/CLI: `alpha=1.0`, `sigma=0.10`) → mAP50-95(val) = 0,6670 (titik interior grid, unggul juga di rata-rata marginal kedua sumbu; P3 di CLAUDE.md §15). `set_dalw_params` menaruh default global `_ALPHA=1.0`, `_SIGMA=0.10` yang selaras dengan pemenang. Detail sensitivitas dan protokol grid ada di [Playbook eksperimen](../playbooks/run-experiment.md).

## 6. Verifikasi kebenaran (T1 & T4)

**T1 — `test_smoke.py::t1_math`** memeriksa Pers. 3.2–3.4 terhadap perhitungan manual. Kasus kunci: dua objek **berimpit** (`c_i = c_j`) → `ρ = 1` (karena `exp(0)=1`) → `ρ̂ = 0,5` → `w = 1 + 0,5·α`. Pada `α = 2,0` hasilnya `w = 2,0`. Juga diuji: objek tunggal → `w = 1`; dua objek berjarak `d` → `ρ = exp(−d²/2σ²)`; slot *padding* → tak memengaruhi tetangga & berbobot 1,0.

**T4 — `test_smoke.py::t4_loss`** memverifikasi rakitan *end-to-end*: setelah `apply_dalw`, kriteria tetap `E2ELoss` (ProgLoss utuh) dan **kedua** cabang (`one2one`, `one2many`) adalah `DALWDetectionLoss`; batch padat (12 objek bergerombol) → komponen box naik >15% dibanding tanpa DALW; citra 1-objek → *loss* **identik** (karena `w=1`).

`test_smoke.py` (T1–T4) **WAJIB LULUS sebelum training apa pun** (CLAUDE.md §13). Lihat [Smoke test](../playbooks/run-experiment.md) dan skill `smoke-test`.

## 7. Kaitan dengan hasil P7 — komplementer, bukan berdiri sendiri

Evaluasi terstratifikasi P7 (AP50-95 per kelas × strata, unit uji Wilcoxon; lihat [Statistik](statistics.md)) menempatkan DALW sebagai kontribusi **komplementer/kondisional**, bukan efek mandiri:

| Hipotesis utama | Makna | Hasil | Interpretasi |
|---|---|---|---|
| **V4 − V1** | DALW saja vs baseline | p = 0,469 (median −0,013) | **tidak signifikan** — DALW sendirian tidak cukup |
| **V8 − V5** | model penuh vs HAM+P2 | p = 0,0125; r = +0,486 | **SIGNIFIKAN** — DALW menambah nilai *di atas* HAM+P2 |
| V8 − V1 | model penuh vs baseline | p = 0,478 | tidak signifikan (efek gabungan belum lolos) |

Kesimpulan yang diframe untuk BAB 4: DALW memberi manfaat **saat digabung** dengan tulang punggung yang lebih kuat (HAM+P2) — strata yang terbantu pada V8−V5: objek *small* +0,062, oklusi *partial* +0,053, densitas *sparse* +0,066. Ini **memicu keputusan A-01** (redaksi/alternatif abstrak bila hasil tak signifikan — lihat [Keputusan pending](../status/pending-decisions.md)). ⚠️ Placeholder BAB 4 BELUM diisi; jangan menulis draf BAB 4–5 di KB (aturan NEVER — CLAUDE.md §12).

## Tautan terkait

- [Framing kebaruan (dua pilar)](thesis-framing.md) — posisi DALW sebagai kebaruan metode; HAM/P2 = instrumen.
- [Mekanisme injeksi kode](../architecture/code-injection.md) — `apply_dalw` monkey-patch, register_ham, YAML varian.
- [Statistik (Wilcoxon + Holm + rank-biserial)](statistics.md) — unit uji, 3 hipotesis utama, hasil P7.
- [Invarian metodologi](../rules/methodology-invariants.md) — densitas pasca-augmentasi, kedua head, normalizer.
- [HAM](ham.md) · [Lapisan P2](p2-layer.md) — instrumen pendamping (bukan kebaruan).
