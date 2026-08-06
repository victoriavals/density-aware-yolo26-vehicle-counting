# 00 — Data Sumber (TIDAK dapat dibangkitkan ulang oleh kode)

⚠️ **Folder paling berharga di repositori ini.** Seluruh berkas lain dapat dibangkitkan ulang
dengan menjalankan program, tetapi isi folder ini tidak — ia berasal dari kerja manusia atau
keputusan manual. Kehilangannya berarti mengulang pekerjaan berjam-jam.

| Berkas | Isi | Kenapa tak dapat dibangkitkan ulang |
|---|---|---|
| `hitung_manual/gt_*.csv` | Hitung manual perlintasan kendaraan 4 klip (399, 116, 296, 931 perlintasan) | Hasil menonton dan mencacah video oleh manusia |
| `konfigurasi_garis.json` | Koordinat garis maya per klip, resolusi, laju bingkai, catatan konvensi arah | Hasil pemilihan manual + verifikasi empiris arah |
| `kit_penghitung_kedua/` | Template buta klip 4, salinan penghitung A, pratinjau garis (kit K7b) | Disiapkan untuk verifikasi antarpenilai |
| `anotasi_oklusi_manual.csv` | 200 penilaian oklusi manual (buta) untuk validasi proksi | Hasil anotasi manusia |
| `bukti_split_grup.csv`, `bukti_split_citra.csv` | Bukti pembagian data berbasis kelompok (lampiran tesis) | Dapat dibangkitkan ulang, tetapi menjadi bukti metodologis yang harus stabil |
| `dalw_best.json` | Hiperparameter α dan σ terpilih dari pencarian grid | Dapat dibangkitkan ulang, tetapi butuh 540 epoch pelatihan |

## Insiden yang pernah terjadi

Pada 5 Agustus 2026 berkas `gt_4_vidiouji.csv` (931 perlintasan) **tertimpa** template kosong
oleh `siapkan_counting.py --make-gt-template`. Data pulih utuh dari kolom `y` pada
`counting_out/4_vidiouji/counting_errors.csv`. Dua perbaikan permanen sudah dipasang:
penjaga timpa dan opsi `--gt-out`. Sejak itu `video_uji/gt_*.csv` juga dikeluarkan dari
`.gitignore` agar ikut ter-*track*. Rincian: [`../K7_PENGHITUNG_KEDUA.md`](../K7_PENGHITUNG_KEDUA.md) §6.
