# Lapisan Deteksi Multi-Skala P2 — P2 Multi-Scale Detection Layer

> **EN — TL;DR:** P2 adds a stride-4 detection head (160×160 feature map) so tiny objects (8–16 px two-wheelers at 640) get their own high-resolution scale. It is built from the OFFICIAL `yolo26-p2.yaml` (easier to defend than a hand-rolled YAML), not a novelty claim — it is an INSTRUMENT alongside HAM. The stride-4 head roughly quadruples anchor points, so P2 variants (V3/V5/V7/V8) cost ~8,5–8,6 GB VRAM and 8,8–11,5 h to train vs ~5 GB and 0,9–1,9 h for non-P2, with FLOPs up ~30–40%. The one-to-one NMS-free analysis (Duplicate Rate / Confidence Margin) focuses on the P2 variants.

Lapisan P2 adalah kepala deteksi tambahan pada *stride*-4 yang menghasilkan *feature map* beresolusi 160×160 (untuk citra masukan 640×640). Motivasinya langsung pada karakteristik dataset traffic-merged: objek roda dua di CCTV Jakarta kerap hanya berukuran 8–16 piksel, sehingga terlalu halus untuk dikenali secara stabil oleh kepala standar YOLO26 yang paling rapat pun berada pada *stride*-8 (P3, 80×80). Dengan menambahkan cabang *stride*-4, jaringan memperoleh satu skala yang jauh lebih rapat untuk objek kecil, melengkapi P3/P4/P5 yang sudah ada. Ini menjawab celah "dominasi objek kecil" yang diuraikan pada CLAUDE.md §2 dan menjadi salah satu dari tiga komponen modifikasi (§3.6 naskah).

## Instrumen, BUKAN kebaruan (WAJIB dipatuhi)

Lapisan P2 dan HAM adalah *instrumen* rekayasa, bukan klaim kebaruan. YOLO26 sudah kuat sejak awal (dilengkapi *ProgLoss* dan STAL), sehingga setiap peningkatan yang melibatkan P2 selalu diframe sebagai perbaikan atas *baseline* yang sudah kuat, bukan sebagai temuan orisinal. Kebaruan tesis hanya dua pilar: (1) metodologis — Pembobotan *Loss* Berbasis Densitas (DALW), dan (2) analitis — penyelidikan interaksi *NMS-free*. Lihat [Framing kebaruan dua-pilar](thesis-framing.md); jangan pernah menempatkan P2 sebagai kontribusi orisinal di teks manapun. Detail komponen instrumen pendamping ada di [HAM](ham.md), sedangkan pilar metode ada di [DALW](dalw.md).

⚠️ Diskrepansi judul terbuka (jangan diselesaikan sendiri): judul SSOT (CLAUDE.md §1) menonjolkan "DETEKTOR *NMS-FREE*" dan "PELACAKAN BYTETRACK" tanpa menyebut P2, sedangkan judul dokumen fisik pasca-revisi pembimbing memuat frasa "DETEKSI MULTI-SKALA P2" di judul. Ini harus dikonfirmasi ke Naufal + pembimbing — catat, jangan memilih. Ringkasan diskrepansi ada di [Keputusan pending & isu terbuka](../status/pending-decisions.md).

## Sumber arsitektur: YAML resmi

Varian ber-P2 dibangun dari file konfigurasi RESMI ultralytics, bukan YAML buatan sendiri. Keputusan ini eksplisit di `y26_variants.py` (komentar modul: "Varian P2 memakai arsitektur RESMI ultralytics (yolo26-p2.yaml) — lebih kuat dipertahankan di sidang daripada YAML buatan sendiri"). Alasan pertahanan sidang: memakai definisi resmi menghindari tudingan bahwa peningkatan berasal dari desain kepala P2 yang di-*tune* sendiri, sehingga fokus tetap pada kebaruan DALW.

Dua jalur pembangkitan di `build_model()` (`y26_variants.py`):

| Varian | HAM | P2 | Sumber cfg | `shifted` | Catatan |
|---|---|---|---|---|---|
| V3, V7 | – | ✓ | `yolo26{scale}-p2.yaml` (resmi, apa adanya) | `False` | P2 murni; tanpa pergeseran indeks |
| V5, V8 | ✓ | ✓ | `generate_ham_yaml(p2=True)` dari `yolo26-p2.yaml` | `True` | HAM disisipkan → seluruh indeks head dipetakan ulang |

Untuk V3/V7 (P2 tanpa HAM), kode langsung memakai `cfg_path = f"yolo26{scale}-p2.yaml"` dan transfer bobot COCO **tanpa** remap nama parameter (`shifted=False`). Untuk V5/V8, `generate_ham_yaml(p2=True)` membaca `yolo26-p2.yaml` resmi lalu menyisipkan blok `HAM` setelah C3k2 indeks 4 & 6; karena penyisipan menggeser penomoran layer, seluruh rujukan `from` pada head dipetakan ulang lewat `_new_index`/`_map_ref`, dan transfer bobot memakai `shifted=True` agar bobot COCO tetap menempel meski indeks bergeser. Mekanika penuh injeksi YAML programatis ada di [Arsitektur varian](../architecture/variants.md) dan [Mekanisme injeksi kode](../architecture/code-injection.md).

Transfer bobot untuk varian ber-P2 hanya sebagian karena cabang kepala *stride*-4 adalah lapisan baru yang terinisialisasi segar (praktik sama dengan CRL-YOLOv5/MST-YOLO/HIC-YOLOv5). Pengukuran *smoke test* P1 (CLAUDE.md §15): P2 memperoleh ~40% kunci / ~62% parameter dari COCO; HAM+P2 ~40% kunci / ~63% parameter. Angka-angka ini menjadi bahan paragraf inisialisasi bobot di BAB 4 (jangan diisi ke placeholder tanpa verifikasi ulang dari artefak).

## Biaya komputasi (Tabel 3.7)

Kepala *stride*-4 menambah kurang lebih 4× titik *anchor* dibanding *stride*-8, sehingga biaya memori dan waktu latih naik tajam. Data terukur dari P5 (delapan varian, batch 16, RTX 4060 Ti 8GB — lihat `hasil/catatan_run.md`):

| Kelompok | Varian | VRAM puncak | Jam latih |
|---|---|---|---|
| Ber-P2 | V3, V5, V7, V8 | 8,52–8,64 GB | 8,8–11,5 jam |
| Non-P2 | V1, V2, V4, V6 | ~5,0–5,2 GB | 0,9–1,9 jam |

Peningkatan FLOPs akibat lapisan P2 berada di kisaran +30–40% (konsekuensi resolusi *feature map* stride-4 yang tinggi). VRAM ber-P2 (8,5–8,6 GB) sedikit melampaui batas fisik 8 GB dan *spill* ke *shared memory*, namun terverifikasi TANPA OOM/crash sepanjang 45,5 jam wall-clock P5 — sehingga aturan A-12 (fallback batch 8 untuk kedelapan varian) tidak terpicu. Rincian per-varian (parameter, GFLOPs, ukuran model, VRAM latih+inferensi, waktu latih, FPS) dirakit `y26_complexity.py` ke `eval_out/complexity.csv` untuk Tabel 3.7 revisi pembimbing. Konteks strategi 8-varian di 8 GB ada di [Keputusan pending (A-12)](../status/pending-decisions.md).

Catatan invarian: bila salah satu varian OOM, batch WAJIB diturunkan untuk SEMUA delapan varian (bukan hanya yang ber-P2) demi menjaga konfigurasi identik antarvarian — lihat [Invarian metodologis](../rules/methodology-invariants.md).

## Kaitan dengan analisis NMS-free

P2 memperbanyak kandidat objek kecil pada *stride*-4, yang berpotensi menaikkan tekanan pada mekanisme pencocokan *one-to-one* YOLO26 (rawan duplikat sebelum pemenang tunggal terpilih). Karena itu analisis *NMS-free* — Duplicate Rate (Pers. 3.6, τ = 0,25) dan Confidence Margin (Pers. 3.7) — SENGAJA difokuskan pada varian ber-P2 (V3, V5, V7, V8), sesuai CLAUDE.md §6 dan RQ3. Ini menghubungkan instrumen P2 dengan pilar kebaruan analitis: menyelidiki apakah penambahan skala rapat mengganggu atau justru menstabilkan pencocokan satu-lawan-satu tanpa NMS. Metodologi, ambang, dan hasil sweep τ diuraikan di [Analisis NMS-free](nmsfree-analysis.md).

## Peran dalam desain eksperimen

Dalam faktorial penuh HAM × P2 × DALW (delapan varian, CLAUDE.md §6), P2 adalah satu faktor biner. Varian yang memuatnya: V3 (P2 saja), V5 (HAM+P2), V7 (P2+DALW), V8 (model penuh). Salah satu dari tiga hipotesis utama, **V8–V5**, mengisolasi kontribusi DALW *di atas* fondasi HAM+P2; hasil P7 menunjukkan pasangan ini signifikan (p=0,0125, r=+0,486), sehingga peran P2 di sini adalah menyediakan fondasi kuat tempat DALW terbukti komplementer. Angka evaluasi terstratifikasi dan protokol Wilcoxon ada di [Evaluasi](evaluation.md) dan [Statistik](statistics.md).

## Rujukan kode & artefak

| Berkas / Artefak | Cakupan |
|---|---|
| `y26_variants.py` | Pembangkitan cfg P2 (`build_model`, `generate_ham_yaml(p2=True)`), transfer bobot (`shifted`) |
| `yolo26-p2.yaml` (resmi, dalam paket ultralytics) | Definisi arsitektur kepala *stride*-4 |
| `inits/{V}_init.pt` | Checkpoint init hasil transfer bobot per varian ber-P2 |
| `hasil/catatan_run.md` | VRAM/jam latih terukur P5 (tabel di atas) |
| `y26_complexity.py` → `eval_out/complexity.csv` | Tabel 3.7 (parameter/GFLOPs/VRAM/FPS) |

Lihat juga: [HAM](ham.md) · [DALW](dalw.md) · [Analisis NMS-free](nmsfree-analysis.md) · [Arsitektur varian](../architecture/variants.md) · [Framing kebaruan](thesis-framing.md).
