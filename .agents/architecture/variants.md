# Delapan Varian Ablasi (V1–V8) — Eight Ablation Variants

> **EN — TL;DR:** The ablation is a full-factorial 2×2×2 over three switches — HAM, P2, DALW — giving eight variants V1..V8, all defined in `y26_variants.py::VARIANTS`. `build_model()` transfers COCO weights per variant (HAM ~97% keys/100% params, P2 ~40%/62%, HAM+P2 ~40%/63% from `test_smoke.py::t3_transfer`) and freezes the result to `inits/{V}_{scale}_init.pt` because the trainer rebuilds the model and would otherwise discard in-memory transfer. HAM and P2 are **instruments, never the novelty** — only DALW (density-aware loss weighting) is the methodological contribution. Fairness across variants (seed 0, identical config) is a hard methodology invariant.

Halaman ini menjelaskan bagaimana kedelapan varian ablasi dibentuk secara programatis, bagaimana bobot pralatih dipindahkan, dan perbandingan mana yang mengisolasi efek tiap komponen. Sumber kode: `y26_variants.py` (registry + pembangkit YAML + transfer), diverifikasi oleh `test_smoke.py` (T2 arsitektur, T3 transfer). Peta ke tesis: Subbab 3.6, 3.8, dan Tabel 3.3.

> Pengingat framing (lihat [Framing kebaruan](../knowledge/thesis-framing.md)): **HAM dan Lapisan P2 adalah INSTRUMEN, bukan klaim kebaruan.** YOLO26 sudah membawa ProgLoss + STAL, sehingga setiap peningkatan diframe sebagai perbaikan atas *baseline* yang sudah kuat. Satu-satunya kebaruan metode adalah [Pembobotan *Loss* Berbasis Densitas (DALW)](../knowledge/dalw.md).

## Matriks 2×2×2

Desain adalah *full factorial* atas tiga sakelar (HAM × P2 × DALW). Registry `VARIANTS` di `y26_variants.py` mengunci definisi ini — jangan diubah tanpa persetujuan Naufal (menyentuh desain eksperimen, Aturan Kerja §12.6).

| Varian | HAM | P2 | DALW | Keterangan (`desc`) | Arsitektur |
|---|---|---|---|---|---|
| **V1** | – | – | – | Baseline YOLO26 | Standar (`yolo26{s}.pt` langsung) |
| **V2** | ✓ | – | – | Hanya HAM | HAM (YAML dibangkitkan) |
| **V3** | – | ✓ | – | Hanya P2 | P2 resmi (`yolo26{s}-p2.yaml`) |
| **V4** | – | – | ✓ | Hanya Density-Aware | Standar + patch *loss* DALW |
| **V5** | ✓ | ✓ | – | HAM + P2 | HAM+P2 (YAML dibangkitkan) |
| **V6** | ✓ | – | ✓ | HAM + Density-Aware | HAM + patch *loss* DALW |
| **V7** | – | ✓ | ✓ | P2 + Density-Aware | P2 resmi + patch *loss* DALW |
| **V8** | ✓ | ✓ | ✓ | Model penuh yang diusulkan | HAM+P2 + patch *loss* DALW |

Perhatikan bahwa DALW **tidak mengubah arsitektur** — ia adalah *monkey-patch* pada penghitungan *loss* (lihat [Aliran injeksi kode](code-injection.md) dan [DALW](../knowledge/dalw.md)). Oleh sebab itu V4 memakai arsitektur identik dengan V1, hanya berbeda pada bobot per-objek wᵢ = 1 + α·ρ̂ᵢ yang aktif selama *training*. Sebaliknya HAM dan P2 mengubah grafik model, sehingga butuh YAML + transfer bobot khusus.

## `build_model()` — siapkan titik awal tiap varian

`build_model(variant, scale, nc, workdir, pretrained, weights)` mengembalikan `(path_atau_nama, laporan_transfer)`. Alurnya bercabang berdasar dua *flag* arsitektur:

1. **Panggil `register_ham()` lebih dulu** (selalu, apa pun variannya) agar kelas `HAM` terdaftar di *namespace* `ultralytics.nn.tasks`/`nn.modules` sebelum YAML mana pun di-*parse* atau *checkpoint* dimuat. Ini invarian injeksi — lihat [code-injection.md](code-injection.md) mekanisme 1.
2. **V1 & V4 (tanpa HAM, tanpa P2):** arsitektur standar. Fungsi langsung mengembalikan nama bobot resmi `yolo26{scale}.pt` dengan `fraction=1.0` — seluruh bobot COCO terpakai penuh, tidak ada *file* init yang ditulis. DALW pada V4 disuntikkan terpisah lewat `apply_dalw()` saat *training* (bukan urusan `build_model`).
3. **Varian ber-HAM (V2, V5, V6, V8):** panggil `generate_ham_yaml(p2, scale, nc)` → `shifted=True` (indeks bergeser karena sisipan HAM).
4. **P2 murni (V3, V7):** pakai YAML resmi `yolo26{scale}-p2.yaml` → `shifted=False`.
5. Untuk kasus 3–4: bangun `YOLO(cfg_path)`, jalankan `transfer_pretrained(...)`, lalu **simpan hasil ke `inits/{variant}_{scale}_init.pt`** via `model.save(...)`.

> ⚠️ Catatan nama *file*: kode menulis `inits/{variant}_{scale}_init.pt` (mis. `inits/V2_s_init.pt`), sedikit berbeda dari penyebutan ringkas `inits/{V}_init.pt` di CLAUDE.md §14 — patokan adalah kode.

### `generate_ham_yaml()` — YAML varian ber-HAM secara programatis

Dibangkitkan dari YAML **resmi terpasang** (`yolo26-p2.yaml` bila P2, selain itu `yolo26.yaml`), bukan YAML buatan sendiri — lebih kokoh dipertahankan di sidang. Langkah kunci:

- **Penjaga struktur:** meng-*assert* bahwa lapisan indeks 3/5 adalah `Conv` *stride*-2 dan indeks 4/6 adalah `C3k2` — bila `yolo26.yaml` bawaan Ultralytics berubah struktur (drift versi 8.4.92), *assert* gagal sebelum menghasilkan arsitektur salah.
- **Sisipan HAM** `[-1, 1, "HAM", [c1, 16, 7]]` setelah blok C3k2 tahap-3 (indeks 4, fitur P3/8) dan tahap-4 (indeks 6, fitur P4/16), sesuai Subbab 3.6.1. Disisipkan **dari belakang** (`sorted(..., reverse=True)`) agar indeks sumber tidak bergeser saat *insert*. Kanal `c1` dihitung dari kanal keluaran blok yang dibungkus setelah *scaling* lebar (`_make_divisible(min(c_out, max_ch) * width)`).
- **Remap seluruh rujukan `from` pada head** lewat `_new_index()` + tabel `redirect` (`_ham_positions()`): rujukan ke keluaran tahap 3/4 dialihkan ke keluaran HAM, sehingga fitur yang **sudah termodulasi atensi** yang mengalir ke *neck* (Gambar 3.2 tesis). Backbone hanya memakai `-1`, jadi hanya *head* yang perlu dipetakan ulang.

Verifikasi arsitektur ada di `test_smoke.py::t2_build`: memastikan tepat **2 modul HAM** terpasang (tahap-3 & tahap-4), parameter varian HAM > baseline, dan varian P2 punya 4 skala deteksi dengan *stride* minimum 4 (P2 = *stride*-4, ~4× jumlah *anchor* dibanding P3 — sumber beban VRAM V3/V5/V7/V8; lihat [P2](../knowledge/p2-layer.md)).

### `transfer_pretrained()` — transfer bobot COCO + laporan % cocok

Memuat *state_dict* COCO ke model varian dan menangani pergeseran indeks:

- Bila `shifted=True` (ber-HAM), kunci `model.{i}.` dipetakan ke `model.{_new_index(i)}.` agar cocok dengan penomoran lapisan pasca-sisipan HAM.
- Hanya kunci yang **ada di target dan berbentuk sama** (`dst[k].shape == v.shape`) yang dipindahkan (`load_state_dict(strict=False)`). Lapisan baru — modul HAM dan seluruh cabang *head* P2 — sengaja dibiarkan **terinisialisasi segar**, praktik sama dengan CRL-YOLOv5/MST-YOLO/HIC-YOLOv5 [11]–[13].
- Mengembalikan `{matched, total_target, fraction, param_fraction}`: `fraction` = proporsi **kunci** yang cocok; `param_fraction` = proporsi **jumlah parameter** yang cocok.

**Angka transfer hasil `test_smoke.py::t3_transfer` (P1, 13 Jul 2026) — bahan paragraf inisialisasi BAB 4:**

| Varian | Lapisan baru | Kunci cocok (`fraction`) | Parameter cocok (`param_fraction`) |
|---|---|---|---|
| HAM (V2) | 2× modul HAM | ~97% (0,97) | ~100% (1,00) |
| P2 (V3) | head 4-skala + cabang P2 | ~40% (0,40) | ~62% (0,62) |
| HAM+P2 (V8) | HAM + head/ cabang P2 | ~40% (0,40) | ~63% (0,63) |

Interpretasi untuk naskah: HAM nyaris tidak mengganggu transfer (parameter praktis penuh — HAM hanya menyisipkan modul atensi ringan), sedangkan P2 menurunkan proporsi **kunci** ke ~40% karena *head* Detect 4-skala dan seluruh cabang P2 adalah lapisan baru; namun proporsi **parameter** tetap ~62–63% karena tulang punggung/*neck* awal (bagian dengan parameter terbanyak) tetap tertransfer penuh. *Assert* penjaga di `test_smoke.py`: HAM `fraction > 0.55`, P2 `fraction > 0.35`.

### Mengapa `inits/{V}_{scale}_init.pt` perlu

Trainer Ultralytics **membangun ulang model** dari konfigurasi saat `model.train()` dipanggil. Bila transfer bobot hanya dilakukan *in-memory* (pada objek `YOLO` sementara), hasilnya akan **hilang** ketika trainer merakit ulang model. Menyimpan hasil transfer sebagai *checkpoint* init membuat trainer memuat bobot COCO yang sudah dipetakan ulang alih-alih memulai dari nol. V1/V4 tidak butuh init karena arsitekturnya standar — trainer cukup diberi `yolo26{scale}.pt` langsung. *File* `inits/` termasuk **bahan mentah BAB 4 — jangan dihapus/ditimpa** ([progress](../status/progress.md), [invarian metodologi](../rules/methodology-invariants.md)).

## Perbandingan yang mengisolasi efek

Karena desainnya *full factorial*, tiap pasangan varian yang berbeda pada satu sakelar mengisolasi kontribusi komponen itu. Empat perbandingan utama:

| Pasangan | Mengisolasi | Peran |
|---|---|---|
| **V4 − V1** | DALW **mandiri** (kontribusi *loss* densitas atas baseline murni) | **Hipotesis utama** |
| **V8 − V5** | DALW **inkremental** (nilai tambah DALW di atas HAM+P2) | **Hipotesis utama** |
| **V8 − V1** | Efek **gabungan** model penuh vs baseline | **Hipotesis utama** |
| **V2 − V1** | Efek instrumen **HAM** saja | Sekunder (koreksi Holm) |
| **V3 − V1** | Efek instrumen **P2** saja | Sekunder (koreksi Holm) |

Tiga pasangan utama (V8–V1, V4–V1, V8–V5) diuji tanpa koreksi; sisanya sekunder dengan koreksi Holm. Unit uji Wilcoxon = **AP per (kelas × strata)**, tanpa baris global. Rincian protokol di [statistik](../knowledge/statistics.md).

**Hasil P7 (18 Jul 2026)** untuk konteks — jangan salin sebagai placeholder tesis (belum dituangkan ke naskah): V4−V1 **tidak signifikan** (p=0,469; median −0,013), V8−V1 **tidak signifikan** (p=0,478), V8−V5 **signifikan** (p=0,0125; r=+0,486). Kesimpulan awal: DALW bersifat **komplementer/kondisional** atas HAM+P2, bukan berdiri sendiri. Ini memicu keputusan pending A-01 — lihat [keputusan pending](../status/pending-decisions.md) dan [progress](../status/progress.md).

## Invarian keadilan ablasi (WAJIB)

Agar selisih antar-varian benar-benar mengukur komponen (bukan derau konfigurasi), seluruh varian **wajib** berbagi kondisi identik:

- **Seed 0** untuk kedelapan varian (`train_ablation.py --variant all`).
- **Konfigurasi *training* identik**: 640×640, MuSGD, maks 300 epoch + *early stopping*, batch 16 FP16, lr 0,01 *cosine*, τ = 0,25 (Tabel 3.4). Bila salah satu varian OOM, batch **diturunkan untuk SEMUA** varian — bukan hanya varian bermasalah (P5 membuktikan batch 16 bertahan penuh, 0 OOM; *fallback* batch-8 A-12 tak terpicu).
- **Inisialisasi setara**: semua varian berangkat dari bobot COCO pada lapisan bersesuaian; lapisan baru (HAM, cabang P2) init segar.
- α\*=1,0 dan σ\*=0,1 dari `dalw_best.json` (pemenang *grid search* P3) dipakai seragam pada semua varian ber-DALW (V4, V6, V7, V8).

Detail lengkap dan alasan tiap invarian ada di [invarian metodologi](../rules/methodology-invariants.md). Untuk memahami bagaimana ketiga komponen benar-benar disuntikkan ke Ultralytics tanpa *fork*, lihat [Aliran injeksi kode](code-injection.md).
