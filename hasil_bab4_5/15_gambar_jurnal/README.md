# 15 — Gambar banding kualitatif siap-jurnal (300 dpi)

Banding kualitatif prediksi **V1 (baseline)** vs **V8 (HAM+P2+DALW)** pada satu bingkai uji
malam padat, dengan panel *ground truth* sebagai acuan.

Dibangkitkan oleh **`y26_gambar_jurnal.py`** (skrip permanen, idempoten) — bukan diedit manual,
sehingga dapat dibangun ulang bila bobot atau bingkai berubah.

## Berkas

| Berkas | Isi |
|---|---|
| `gambar_banding.png/.pdf/.tif` | 3 panel bingkai penuh — (a) GT, (b) V1, (c) V8 — label Indonesia |
| `gambar_zoom.png/.pdf/.tif` | Sama, diperbesar pada wilayah terpadat (dipilih otomatis) |
| `gambar_banding_en.*`, `gambar_zoom_en.*` | Kembaran label Inggris |
| `ringkasan.csv` / `.json` | TP/FP/FN + recall/presisi per varian, rincian per kelas |

**Spesifikasi cetak:** 2007 × 607 px @ **300 dpi** = **16,99 × 5,14 cm** (lebar dua kolom).
Untuk satu kolom: `--width-cm 8.5`. PDF bersifat **vektor** untuk teks & kotak (citra tetap raster),
jadi label tetap tajam pada perbesaran berapa pun. TIFF ber-kompresi LZW bila jurnal memintanya.

## Bingkai yang dipakai

`night-traffic-5_mp4-0028` — 1144 × 638, **18 objek**, malam, **15 roda dua** (mendukung premis
BAB 1 soal dominasi roda dua), 2 objek kecil + 14 sedang.

⚠️ **Bingkai terpadat pada split uji TIDAK dipakai** (`night-traffic-9_mp4-0055`, 30 objek) karena
berasal dari kelompok ber-**tanda air Shutterstock**. Lihat
[`../AUDIT_PROVENANS_DATASET.md`](../AUDIT_PROVENANS_DATASET.md) — **wajib dibaca sebelum gambar
apa pun dikirim ke jurnal**. Bingkai yang dipakai sekarang bersih dari tanda air, tetapi **masih
memuat overlay "SIMPANG TERBAN U. BARAT / CSR Citranet"** yang menunjukkan lokasi **Yogyakarta**,
bukan Jakarta.

## Penandaan

Pembeda **ganda** — warna *dan* gaya garis — agar tetap terbaca pada cetak abu-abu maupun bagi
pembaca buta warna (hijau/magenta/kuning aman untuk deuteranopia):

| Penanda | Warna | Gaya | Arti |
|---|---|---|---|
| TP | `#00E396` hijau | utuh | prediksi tercocokkan ke objek GT |
| FP | `#FF2D95` magenta | putus | prediksi tanpa pasangan GT |
| FN | `#FFD60A` kuning | titik | objek GT terlewat |

Pencocokan: **IoU ≥ 0,50, class-aware, conf > 0,25** — identik `y26_nmsfree.match_predictions`
dan pipeline evaluasi BAB 4, sehingga gambar ini konsisten dengan angka Subbab 4.5/4.11.
Deteksi memakai **forward mentah kepala one-to-one** (pola `y26_counting.make_detector`).

## Angka pada bingkai ini

| Varian | prediksi | TP | FP | FN | recall | presisi |
|---|---|---|---|---|---|---|
| V1 | 17 | 13 | 4 | 5 | 0,722 | 0,765 |
| V8 | 19 | 14 | 5 | 4 | 0,778 | 0,737 |

**Nilai naratifnya:** bingkai ini memperagakan mekanisme yang sama dengan temuan global Subbab
4.11 — V8 **menurunkan objek terlewat** (5 → 4) tetapi **membayarnya dengan prediksi palsu**
(4 → 5), sehingga presisi turun (0,765 → 0,737) meski cakupan naik. Persis pola global
FN 614 → 541 dengan FP meningkat, yang menjelaskan presisi V8 78,06 % < V1 79,44 %.

⚠️ Ini **satu bingkai**, ilustratif — **bukan bukti statistik**. Jangan menarik kesimpulan
kuantitatif darinya; rujuk Wilcoxon/bootstrap untuk itu.

## Regenerasi

```bash
# Indonesia + Inggris, lebar dua kolom
python y26_gambar_jurnal.py --image dataset/test/images/night-traffic-5_mp4-0028_jpg.rf.WiS4loX9lB4ekbsgjqZ9.jpg \
    --variants V1,V8 --with-gt --lang id --width-cm 17 --tiff
python y26_gambar_jurnal.py --image <sama> --variants V1,V8 --with-gt --lang en --width-cm 17 --tiff

# varian lain / satu kolom / tanpa panel GT
python y26_gambar_jurnal.py --image <path> --variants V1,V5,V8 --width-cm 8.5
```

## Draf keterangan gambar

**Indonesia** — Gambar N. Banding kualitatif hasil deteksi pada bingkai lalu lintas malam
padat (18 objek, 15 di antaranya kendaraan roda dua): (a) *ground truth*; (b) *baseline*
YOLO26 (V1); (c) konfigurasi penuh yang diusulkan (V8). Kotak utuh menandai deteksi benar,
kotak putus prediksi palsu, dan kotak titik objek yang terlewat (pencocokan IoU ≥ 0,50 sekelas,
ambang keyakinan 0,25). V8 menurunkan jumlah objek terlewat dari lima menjadi empat, namun
menambah satu prediksi palsu — sejalan dengan pola galat pada Subbab [rujuk].

**English** — Figure N. Qualitative detection comparison on a dense night-time traffic frame
(18 objects, 15 of them two-wheelers): (a) ground truth; (b) YOLO26 baseline (V1); (c) the
proposed full configuration (V8). Solid boxes denote true positives, dashed boxes false
positives, and dotted boxes missed objects (class-aware IoU ≥ 0.50, confidence threshold 0.25).
V8 reduces missed objects from five to four at the cost of one additional false positive,
consistent with the error pattern reported in Section [ref].
