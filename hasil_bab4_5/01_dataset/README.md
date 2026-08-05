# 01 — Karakteristik & Pembagian Dataset

Menjawab Subbab 3.3 (Dataset Penelitian) dan bahan paragraf pembuka BAB 4.

## Berkas

| Berkas | Isi |
|---|---|
| `distribusi_kelas.csv` | Jumlah citra dan jumlah instans per kelas, untuk tiap subset (train/valid/test) |
| `distribusi_kelas.png` | Visualisasi dua panel: (kiri) jumlah citra per subset, (kanan) jumlah instans per kelas per subset |
| `bukti_split_grup.csv` | 758 grup (kamera×adegan×sesi) beserta subset tujuannya — bukti *group-based split* mencegah *data leakage* (salinan dari root repo) |
| `bukti_split_citra.csv` | Jejak penuh per citra → grup → subset (lampiran tesis) |

## Cara membaca `distribusi_kelas.png`

- **Panel kiri**: jumlah citra 2.372 (train) / 679 (valid) / 338 (test) — proporsi
  70,0/20,0/10,0%, sesuai target Subbab 3.3.2 sampai pembulatan.
- **Panel kanan**: perhatikan **ketimpangan kelas** — `two-wheeler` dan `pedestrian`
  mendominasi di semua subset (mencerminkan komposisi lalu lintas nyata Jakarta),
  sedangkan `big-vehicle` paling jarang. Ini alasan mengapa penafsiran AP per kelas
  minoritas harus hati-hati (lihat folder `04_ablasi_deteksi/`).

## Angka kunci (dari `distribusi_kelas.csv`)

| Subset | Citra | big-vehicle | car | pedestrian | two-wheeler |
|---|---|---|---|---|---|
| train | 2.372 | 1.916 | 3.971 | 5.207 | 5.692 |
| valid | 679 | 397 | 839 | 1.640 | 1.218 |
| test | 338 | 332 | 765 | 638 | 865 |

**Catatan penting untuk konsistensi naskah:** naskah v7 menulis "sekitar 2.372 citra
latih, 678 citra validasi, dan 339 citra uji" — angka aktual adalah **679/338** (bukan
678/339). Selisih 1 citra, akibat pembulatan saat menulis naskah sebelum split final
dijalankan ulang. Perbaiki di BAB 3/4 (lihat `PANDUAN_SELESAIKAN_BAB4-5.md` FASE 8).

## Kalimat siap-adaptasi

> "Dataset traffic-merged terbagi menjadi 2.372 citra latih (70,0%), 679 citra validasi
> (20,0%), dan 338 citra uji (10,0%), dengan pembagian dilakukan pada tataran kelompok
> kamera×adegan×sesi (758 kelompok) untuk mencegah kebocoran data. Distribusi kelas
> bersifat timpang, dengan kendaraan roda dua dan pejalan kaki sebagai kelas mayoritas
> yang mencerminkan komposisi lalu lintas nyata, dan kendaraan besar sebagai kelas
> paling jarang (332 instans pada data uji)."
