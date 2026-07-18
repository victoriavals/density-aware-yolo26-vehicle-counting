# Modul Atensi Hibrida (HAM) — Hybrid Attention Module

> **EN — TL;DR:** HAM is a cascade of channel attention (SE principle) followed by spatial attention (CBAM principle), injected into backbone stages 3 & 4 (layer indices 4 & 6). It keeps tensor shape unchanged (`c2 = ch[f]`) and is registered via `register_ham()` (three `setattr` injection points), verified against ultralytics 8.4.92 whose `parse_model` resolves YAML module names through `globals()`. **HAM is an instrument, NOT a novelty claim** — YOLO26 already ships ProgLoss + STAL, so any gain is framed as improvement over an already-strong baseline.

## Ringkasan

HAM (*Hybrid Attention Module*) adalah blok atensi ringan yang disisipkan ke *backbone* YOLO26 untuk memperkuat representasi objek kecil pada lalu lintas heterogen padat. Implementasinya ada di `y26_modules.py` (Subbab 3.6.1, Gambar 3.3). Modul ini merangkai dua tahap secara kaskade: **atensi kanal** (mengikuti prinsip *Squeeze-and-Excitation*/SE, Hu et al. [20]) lalu **atensi spasial** (mengikuti prinsip CBAM, Woo et al. [10]).

**PENTING (aturan NEVER).** HAM adalah *instrumen*, **bukan** klaim kebaruan tesis. YOLO26 sudah memiliki ProgLoss + STAL, sehingga setiap peningkatan yang teramati diframe sebagai perbaikan atas *baseline* yang sudah kuat — bukan sebagai temuan orisinal. Kebaruan tesis hanya dua: metode (Pembobotan *Loss* Berbasis Densitas / DALW) dan analisis (interaksi *one-to-one NMS-free*). Lihat [Framing kebaruan dua pilar](thesis-framing.md).

## Mekanisme (kaskade dua tahap)

Kelas `HAM(nn.Module)` di `y26_modules.py` memproses tensor masukan `x` berbentuk `(B, C, H, W)`:

| Tahap | Prinsip | Operasi (dari kode) |
|---|---|---|
| 1. Atensi kanal | SE [20] | *Shared* MLP `Conv2d(c1→cm→c1)` (`cm = max(c1//reduction, 8)`, `reduction=16`) diterapkan pada jalur `adaptive_avg_pool2d` **dan** `adaptive_max_pool2d`, dijumlahkan, lalu `sigmoid` → dikalikan ke `x` per-kanal. |
| 2. Atensi spasial | CBAM [10] | `concat(mean_kanal, amax_kanal)` → `Conv2d(2→1, kernel=spatial_k=7, padding=3, bias=False)` → `sigmoid` → dikalikan ke `x` per-piksel. |

Aktivasi tersembunyi memakai `SiLU`. Bobot atensi berada di rentang (0, 1) karena `sigmoid`, sehingga HAM hanya menyeleksi ulang penekanan fitur tanpa mengubah skala tensor secara struktural.

**Invarian bentuk.** HAM tidak mengubah dimensi tensor: kanal keluaran = kanal masukan. Ini konsisten dengan konvensi `parse_model` ultralytics untuk modul di luar `base_modules` — channel keluaran dianggap `c2 = ch[f]` (lihat docstring `y26_modules.py`). Karena itu penyisipan HAM aman tanpa perlu menyesuaikan channel lapisan berikutnya.

## Penempatan di arsitektur

HAM disisipkan pada **backbone tahap 3 dan tahap 4**, yakni **setelah blok C3k2 indeks 4 & 6** pada YAML resmi (`yolo26.yaml` / `yolo26-p2.yaml`). Penyisipan ini menggeser seluruh indeks *head*, sehingga `y26_variants.py` melakukan *remap* indeks (`_new_index`) dan pemetaan ulang nama parameter saat transfer bobot COCO. Detail pembangkitan YAML programatis dan transfer bobot ada di [Varian & pembangkitan YAML](../architecture/variants.md).

HAM muncul di varian **V2** (HAM saja), **V5** (HAM+P2), **V6** (HAM+DALW), dan **V8** (model penuh) pada desain faktorial 8 varian.

## Registrasi: `register_ham()` (namespace injection)

YOLO26 dibangun dari YAML yang menyebut nama modul sebagai *string*; `parse_model` (ultralytics 8.4.92, `ultralytics/nn/tasks.py` ~baris 1942) meresolusinya via `globals()`. Agar nama `HAM` dikenali, `register_ham()` menyuntikkan kelas ke **tiga titik `setattr`**:

1. `setattr(ultralytics.nn.tasks, "HAM", HAM)` — agar `parse_model` menemukan kelas saat membangun model dari YAML.
2. `setattr(ultralytics.nn.modules, "HAM", HAM)` — agar deserialisasi *checkpoint* (`torch.load`) menemukan kelasnya.
3. `sys.modules.setdefault("y26_modules", sys.modules[__name__])` — agar path kelas asli (`y26_modules.HAM`) yang tersimpan di *checkpoint* dapat diimpor dengan nama sama di proses lain.

Fungsi ini **idempoten** (aman dipanggil berulang) dan mencetak peringatan bila versi ultralytics ≠ `8.4.92` (`VERIFIED_ULTRALYTICS`). **Setiap entry point yang membangun atau memuat model ber-HAM WAJIB memanggil `register_ham()` lebih dahulu** — seluruh skrip evaluasi sudah melakukannya. Pola injeksi ini adalah satu dari tiga mekanisme injeksi kode proyek; lihat [Mekanisme injeksi kode](../architecture/code-injection.md).

## Verifikasi versi

Kode diverifikasi baris-per-baris terhadap **ultralytics 8.4.92**. Ketergantungan spesifik-versi bertumpu pada dua fakta yang dikunci: (a) `parse_model` meresolusi nama modul via `globals()`, dan (b) modul di luar `base_modules` menerima args YAML apa adanya dengan `c2 = ch[f]`. Bila versi ultralytics berubah, jalankan `test_smoke.py` (uji T2 membangun keempat arsitektur, termasuk yang ber-HAM) sebelum melanjutkan. Detail lingkungan ada di [Lingkungan teknis](environment.md).

## Tautan terkait

- [Mekanisme injeksi kode](../architecture/code-injection.md) — tiga mekanisme injeksi (HAM namespace, DALW monkey-patch, YAML varian).
- [Varian & pembangkitan YAML](../architecture/variants.md) — penyisipan indeks 4 & 6, *remap* head, transfer bobot COCO.
- [Lapisan P2](p2-layer.md) — instrumen kedua (deteksi multi-skala), juga bukan klaim kebaruan.
- [Pembobotan Loss Berbasis Densitas (DALW)](dalw.md) — kebaruan metode.
- [Framing kebaruan dua pilar](thesis-framing.md) — mengapa HAM/P2 = instrumen, bukan kebaruan.

## Peta ke tesis

| Aspek | Rujukan tesis |
|---|---|
| Modul HAM (kaskade kanal→spasial) | Subbab 3.6.1, Gambar 3.3 |
| Prinsip CBAM | Woo et al. (ECCV 2018) [10] |
| Prinsip Squeeze-and-Excitation | Hu et al. (CVPR 2018) [20] |
| Varian ber-HAM (V2, V5, V6, V8) | Subbab 3.8, Tabel desain varian |
