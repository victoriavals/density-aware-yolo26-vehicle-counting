# Tiga Mekanisme Injeksi Kode — Code Injection Mechanisms

> **EN — TL;DR:** All thesis code is a patch/injection layer on top of the installed `ultralytics` (no fork). Three mechanisms must be understood together: (1) **HAM namespace injection** via `register_ham()`, (2) **DALW loss monkey-patch** via `apply_dalw(α,σ)` which swaps `init_criterion` so `E2ELoss` wraps `DALWDetectionLoss` on **both** heads, (3) **programmatic variant YAML** with head-index remap saved to `inits/{V}_init.pt`. Golden rule: `register_ham()` and `apply_dalw()` MUST run **before** `model.train()`. Everything is pinned to **ultralytics 8.4.92** — test T4 in `test_smoke.py` is the guard. HAM and the P2 layer are **instruments, never the novelty claim**.

Seluruh kode tesis ini adalah **lapisan patch/injeksi di atas ultralytics terpasang** — tidak ada *fork*, tidak ada berkas ultralytics yang diedit. Konsekuensinya, tiap *entry point* yang membangun atau memuat model wajib memasang injeksi yang relevan lebih dulu; bila lupa, model gagal dibangun atau *loss* yang terpasang bukan yang dimaksud. Dokumen ini merangkum tiga mekanisme injeksi beserta urutan wajibnya, lalu menjelaskan jalur akses kepala *one-to-one* mentah dan alasan penguncian versi.

Sebelum lebih jauh: **HAM dan Lapisan P2 adalah instrumen arsitektural, bukan klaim kebaruan.** YOLO26 sudah membawa ProgLoss + STAL; kebaruan tesis ada pada Pembobotan *Loss* Berbasis Densitas (metode) dan analisis interaksi *NMS-free* (analitis). Jangan pernah membingkai HAM atau P2 sebagai temuan baru saat menulis apa pun yang bersumber dari dokumen ini.

## Peta singkat

| Mekanisme | File | Fungsi kunci | Menyentuh subbab |
|---|---|---|---|
| HAM via *namespace injection* | `y26_modules.py` | `register_ham()` | 3.6.1 (arsitektur HAM) |
| DALW via *monkey-patch loss* | `y26_dalw.py` | `apply_dalw(alpha, sigma)`, `DALWDetectionLoss` | 3.6.3, Pers. 3.2–3.5 |
| Varian via YAML programatis | `y26_variants.py` | `generate_ham_yaml()`, `transfer_pretrained()`, `build_model()` | 3.6, 3.8, Tabel 3.4 |
| Akses kepala *one-to-one* mentah | `y26_nmsfree.py` | `evaluate_dr_cm()`, `train_format_forward()`, `_letterbox()` | 3.7, A-10 |

## 1. HAM via *namespace injection*

`parse_model` di `ultralytics/nn/tasks.py` (sekitar baris 1942 pada 8.4.92) meresolusi nama modul yang tertulis di YAML lewat `globals()` modul `tasks`. Karena itu, agar YAML varian yang memuat baris `HAM` bisa dibangun, kelas `HAM` cukup di-*setattr* ke namespace tersebut. `register_ham()` di `y26_modules.py` melakukan tiga hal:

1. `setattr(tasks, "HAM", HAM)` — agar `parse_model` menemukan nama `HAM` saat membangun model dari YAML.
2. `setattr(ultralytics.nn.modules, "HAM", HAM)` — agar deserialisasi *checkpoint* (`torch.load`) menemukan kelasnya.
3. `sys.modules.setdefault("y26_modules", sys.modules[__name__])` — karena `torch.load` pada *checkpoint* menyimpan jalur kelas asli `y26_modules.HAM`; alias ini menjamin proses lain (evaluasi, *counting*) dapat memuat ulang bobot ber-HAM.

`register_ham()` **idempoten** (aman dipanggil berulang) dan mencetak peringatan bila versi ultralytics bukan `8.4.92`. **Aturan wajib:** setiap *entry point* yang membangun atau memuat model ber-HAM harus memanggil `register_ham()` lebih dulu — semua skrip evaluasi (`evaluate_all.py`, `analyze_nmsfree.py`, `y26_counting.py`) dan pembangun varian (`y26_variants.build_model`) sudah melakukannya.

HAM sendiri adalah kaskade atensi kanal → atensi spasial (prinsip CBAM + SE) yang **tidak mengubah bentuk tensor** (c2 = ch masukan), sehingga cocok dengan aturan ultralytics bahwa modul di luar `base_modules` mewarisi kanal masukannya. Rincian arsitektur ada di [ham.md](../knowledge/ham.md).

## 2. DALW via *monkey-patch* `init_criterion`

`apply_dalw(alpha, sigma)` di `y26_dalw.py` mengganti `DetectionModel.init_criterion` secara **global** pada proses:

```python
def init_criterion(self):
    if getattr(self, "end2end", False):
        return E2ELoss(self, loss_fn=DALWDetectionLoss)
    return DALWDetectionLoss(self)
tasks.DetectionModel.init_criterion = init_criterion
```

Karena model YOLO26 bersifat `end2end`, kriteria yang dibangun adalah `E2ELoss` yang di dalamnya membangun **dua** cabang *loss* dari `loss_fn` yang sama: `one2many` (`tal_topk=10`) dan `one2one` (`tal_topk=7, topk2=1`), lalu mencampurnya dengan *gain* ProgLoss yang meluruh 0,8 → 0,1 sepanjang epoch. Dengan menyuntikkan `DALWDetectionLoss` sebagai `loss_fn`, bobot densitas berlaku pada **KEDUA cabang head** (keputusan **A-11**), sementara ProgLoss dan STAL tetap utuh:

`L = Σ_b g_b(t) · Σ_i w_i · L_{b,i} = Σ_i w_i · (Σ_b g_b(t) L_{b,i})` — identik dengan Persamaan 3.5 dengan `L_i` = *total loss* bawaan YOLO26.

**Urutan wajib:** `apply_dalw()` harus dipanggil **SEBELUM** `model.train()`. Trainer ultralytics membangun ulang model (dan kriterianya) dari awal; bila *patch* belum terpasang saat rebuild, *loss* yang aktif adalah `v8DetectionLoss` biasa — bobot densitas tak akan pernah masuk. Untuk varian tanpa DALW (V1, V2, V3, V5) `apply_dalw()` **tidak** dipanggil sama sekali.

`DALWDetectionLoss.get_assigned_targets_and_loss` **menyalin** metode internal versi 8.4.92 (`utils/loss.py:400–463`) dengan tiga sisipan bertanda `# === DALW`: bobot `w_i` dihitung dari label batch di dalam `torch.no_grad` (otomatis pasca-augmentasi mosaic, tanpa gradien tambahan), dipetakan ke tiap anchor *foreground* via `target_gt_idx`, lalu mengalikan `L_cls` (per-anchor) dan bobot internal `BboxLoss` (`target_scores`). `target_scores_sum` sebagai normalizer **tidak** diubah, sehingga semantik `(1/N) Σ w_i L_i` terjaga. Rincian penurunan Pers. 3.2–3.5 dan penempatan bobot ada di [dalw.md](../knowledge/dalw.md).

## 3. Varian via YAML programatis + *remap* indeks

`y26_variants.py` membangun kedelapan varian faktorial (HAM × P2 × DALW) tanpa menulis YAML tangan:

- **Varian P2 murni** (V3, V7) memakai YAML **resmi** ultralytics (`yolo26-p2.yaml`) — lebih kuat dipertahankan di sidang.
- **Varian ber-HAM** (V2, V5, V6, V8) dibangkitkan `generate_ham_yaml()` dari YAML resmi (`yolo26.yaml` atau `yolo26-p2.yaml`): baris `HAM` disisipkan **setelah blok C3k2 indeks 4 (P3/8) dan indeks 6 (P4/16)**, lalu **seluruh rujukan indeks absolut pada head dipetakan ulang** lewat `_new_index()`/`_map_ref()` agar penomoran layer yang bergeser tidak merusak aliran fitur ke neck. Sebuah *guard* asersi (`bb[conv_i][2] == "Conv"`, `bb[c3_i][2] == "C3k2"`) memastikan titik sisip masih valid — bila struktur YAML resmi berubah antar versi, pembangkitan gagal keras alih-alih diam-diam salah.
- **Transfer bobot COCO** (`transfer_pretrained`): untuk arsitektur ber-HAM (`shifted=True`), nama parameter `model.{i}.` dipetakan ke `model.{_new_index(i)}.` supaya bobot pralatih tetap termuat meski indeks bergeser; lapisan baru (HAM, cabang head P2) terinisialisasi segar. Fungsi mengembalikan ringkasan `{matched, total_target, fraction, param_fraction}` — bahan paragraf inisialisasi BAB 4.

**Mengapa disimpan ke `inits/{V}_{scale}_init.pt`:** trainer ultralytics **membangun ulang** model dari konfigurasi, sehingga transfer bobot *in-memory* akan hilang. `build_model()` menyimpan hasil transfer sebagai *checkpoint* init agar trainer benar-benar memakai bobot tersebut. Folder `inits/` adalah bahan mentah BAB 4 — **jangan dihapus/ditimpa**. Rincian pemetaan indeks, tabel varian, dan keadilan ablasi ada di [variants.md](variants.md).

## Akses kepala *one-to-one* mentah `(B, 300, 6)`

Seluruh instrumentasi *NMS-free* (Duplicate Rate/Confidence Margin, cache strata, *counting*) **sengaja melewati predictor standar**. *Forward* langsung `DetectionModel` dalam mode eval mengembalikan tensor `(B, 300, 6)` = `[xyxy, conf, cls]` pada **ruang letterbox 640** — inilah keluaran kepala *one-to-one* tanpa NMS. GT ditransformasikan ke ruang yang sama lewat `_letterbox()` bersama di `y26_nmsfree.py`, sehingga pencocokan prediksi↔GT konsisten (letterbox faktor `r`, *padding* `left`/`top`).

Dua fungsi pendukung yang harus dipahami bersama:

- **`_letterbox(path, imgsz=640)`** — memuat satu citra letterbox 640 sekaligus dua representasi GT: `xyxy` piksel-letterbox (untuk `match_predictions`) dan baris `[cls, cx, cy, w, h]` ternormalisasi-letterbox (untuk format batch *loss*). Dipakai juga oleh `y26_strata` (rantai `split_image_paths`/`_letterbox` bersama).
- **`train_format_forward(nn_model, imgs)`** — hanya menaikkan **flag** `training` milik modul `Detect` (menentukan cabang forward `one2many`/`one2one`), **BUKAN** `det.train()` atau `.train()` penuh. Semua anak modul (Conv+BN) tetap mode eval sehingga *running statistics* BN tidak berubah. Inilah "menggali kode internal" yang dijanjikan Subbab 3.7: dict dual-head keluar tanpa merusak statistik BN.

Callback `NMSFreeProbe` (probe A-10 per epoch) memakai jalur ini dan **selalu dibungkus try/except** agar tidak pernah menghentikan training. Formalisasi metrik DR/CM/stabilitas ada di [nmsfree-analysis.md](../knowledge/nmsfree-analysis.md).

## Penguncian versi ultralytics 8.4.92 — mengapa T4 penjaga

Kode **dikunci** pada ultralytics `8.4.92`. `DALWDetectionLoss.get_assigned_targets_and_loss` **menyalin baris demi baris** metode internal `v8DetectionLoss.get_assigned_targets_and_loss` (`utils/loss.py:400–463`) versi tersebut, lalu menyisipkan tiga blok DALW. Bila versi ultralytics berubah, metode internal itu bisa bergeser (nama, argumen, struktur `preds`), sehingga salinan menjadi usang secara diam-diam.

Penjaga praktisnya adalah **test T4 di `test_smoke.py`** (uji *loss* E2E). `test_smoke.py` **WAJIB LULUS sebelum training apa pun**. Bila versi berubah dan **T4 gagal, JANGAN lanjut** sebelum salinan disesuaikan ke versi baru. `register_ham()` juga mencetak peringatan versi, dan `y26_modules.VERIFIED_ULTRALYTICS` mengikat nilai `"8.4.92"` sebagai referensi. Catatan versi pustaka lain (torch 2.11.0+cu128, supervision <0,30) ada di [environment.md](../knowledge/environment.md).

## Rantai dependensi & pemanggilan aman

```
register_ham()  ──►  build_model / generate_ham_yaml   (WAJIB sebelum bangun/muat model ber-HAM)
apply_dalw(α,σ) ──►  model.train()                      (WAJIB sebelum train; hanya varian ber-DALW)
```

Ringkasnya, sebelum menyentuh model: panggil `register_ham()` untuk setiap varian ber-HAM, lalu `apply_dalw(alpha, sigma)` untuk setiap varian ber-DALW — keduanya sebelum trainer merebuild model. Untuk evaluasi/inferensi, cukup `register_ham()`; DALW tidak relevan saat *forward* (bobot hanya memengaruhi *loss* pelatihan). Peta alur data eksperimen antar-skrip ada di [data-flow.md](data-flow.md).

## Lihat juga

- [DALW — Pembobotan *Loss* Berbasis Densitas](../knowledge/dalw.md)
- [HAM — Modul Atensi Hibrida (instrumen)](../knowledge/ham.md)
- [Varian & transfer bobot](variants.md)
- [Analisis *NMS-free* (DR/CM/stabilitas)](../knowledge/nmsfree-analysis.md)
- [Lapisan P2 (instrumen)](../knowledge/p2-layer.md)
- [Invarian metodologis](../rules/methodology-invariants.md)
