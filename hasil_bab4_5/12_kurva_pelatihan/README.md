# 12 — Kurva Pelatihan per Run

Riwayat pelatihan **11 run**: delapan varian ablasi (V1–V8), dua run sensitivitas kekuatan
pembobotan (V4_a0.5, V4_a2.0), dan satu run pemeriksaan ketegaran (V8_normw).

| Pola berkas | Isi |
|---|---|
| `<run>_results.csv` | Metrik per epoch: *loss* (box, cls, dfl), presisi, *recall*, mAP@0,5, mAP@0,5:0,95, laju pembelajaran |
| `<run>_kurva.png` | Grafik bawaan pustaka pelatihan: seluruh kurva *loss* dan metrik dalam satu panel |
| `<run>_nmsfree_probe.csv` | Probe interaksi *NMS-free* per epoch: *Duplicate Rate*, *Confidence Margin*, stabilitas penetapan S(t) (Persamaan 3.8) |
| `<run>_complexity.json` | Puncak pemakaian VRAM saat pelatihan dan durasi latih (bahan Tabel 3.8) |

## Cara membaca

Kolom `metrics/mAP50-95(B)` pada `results.csv` adalah mAP **validasi selama pelatihan** —
bukan angka uji yang dipakai pengujian hipotesis. Angka uji ada di
[`../04_ablasi_deteksi/global_metrics.csv`](../04_ablasi_deteksi/global_metrics.csv).
Kedua angka berbeda dan tidak boleh tertukar: peringkat validasi terbukti tidak stabil
terhadap peringkat uji (V2 teratas di validasi tetapi peringkat empat di uji).

Berkas `nmsfree_probe.csv` adalah satu-satunya sumber data stabilitas penetapan antar-epoch,
yang menjadi bahan Gambar S(t) pada Subbab 4.8.
