# P8 — Validasi Proksi Oklusi terhadap Anotasi Manual (menunaikan janji Subbab 3.3.3)

**Dijalankan:** 18 Jul 2026. **Subset:** 200 objek *ground truth* dari **150 citra** split **validasi**, dianotasi manual oleh peneliti melalui alat klik lokal (penilaian *blind* — tier proksi tidak ditampilkan). Berkas: `anotasi_oklusi/manual_oklusi.csv`, bukti sampel `anotasi_oklusi/sample_manifest.csv`.

## Hasil utama

| Besaran | Nilai |
|---|---|
| Jumlah objek dinilai | **200** (150 citra) |
| **Tingkat kesesuaian (akurasi tier)** | **68,0 %** (136/200) |
| Kappa Cohen | **0,410** (kesesuaian sedang) |
| Kappa berbobot linear (tier ordinal) | 0,427 |
| Proksi **meremehkan** oklusi | **40 objek (20,0 %)** |
| Proksi **melebihkan** oklusi | 24 objek (12,0 %) |

### Matriks konfusi (baris = anotasi manual, kolom = tier proksi)

| manual ↓ / proksi → | no | partial | heavy | total manual |
|---|---|---|---|---|
| **no** | **74** | 24 | 0 | 98 |
| **partial** | 23 | **62** | 0 | 85 |
| **heavy** | 3 | 14 | **0** | 17 |
| **total proksi** | 100 | 100 | **0** | 200 |

## Tiga temuan untuk BAB 4

**1. Tier *heavy* tidak pernah terbentuk oleh proksi, padahal manusia menemukannya.** Penilaian manual mengidentifikasi **17 objek teroklusi berat**, tetapi proksi menempatkan **nol** objek pada tier *heavy* (14 dinilai *partial*, 3 dinilai *no*). Nilai proksi ke-17 objek itu berkisar **o = 0,0025 sampai 0,2609** — seluruhnya jauh di bawah ambang 0,35 maupun 0,40. Kasus paling ekstrem: sebuah mobil dengan o = 0,0025 (praktis "tidak teroklusi" menurut proksi) dinilai **tertutup berat** oleh mata manusia.

**2. Bias bersifat asimetris ke arah meremehkan.** Kekeliruan "proksi lebih ringan daripada manual" (20,0 %) hampir dua kali kekeliruan sebaliknya (12,0 %). Ini **mengonfirmasi secara empiris** keterbatasan yang sudah diakui terbuka pada Subbab 3.3.3: ketika objek kecil tertutup objek yang jauh lebih besar, luas gabungan yang besar menekan nilai IoU sehingga oklusi tampak kecil.

**3. Kesesuaian paling buruk justru pada kelas paling rentan.** Urutan kesesuaian per kelas: **big-vehicle 79,4 %** (n=34) > **pedestrian 76,4 %** (n=55) > **car 66,1 %** (n=56) > **two-wheeler 54,5 %** (n=55). Kendaraan roda dua — objek terkecil dan kelas mayoritas dataset — adalah yang paling sering salah dinilai proksi, persis seperti yang diramalkan mekanisme luas-gabungan pada butir 2.

## Konsekuensi metodologis (penting untuk pelaporan)

- **Strata oklusi *heavy* pada evaluasi terstratifikasi harus dilaporkan sebagai tidak terisi/tak bermakna, bukan disembunyikan.** Pada split validasi tidak ada satu pun objek melewati ambang (maksimum o = 0,286); pada split uji hanya 8 objek pada ambang 0,35 (dan 4 objek pada ambang 0,40) dari 2.600 objek. Sel Wilcoxon yang melibatkan tier ini otomatis gugur oleh aturan sel minimum 30 objek (Subbab 3.11.5).
- **Tier *partial* memuat sebagian objek yang secara perseptual berat.** Interpretasi hasil per strata oklusi harus menyebut bahwa "partial" pada penelitian ini mencakup rentang oklusi perseptual yang lebih lebar daripada namanya.
- **Keputusan ambang (K2: 0,35 versus 0,40) tidak berpengaruh pada validasi ini.** Tingkat kesesuaian **identik 68,0 %** pada kedua ambang, dan matriks konfusinya sama persis — sebab tak ada objek validasi yang melewati 0,35 sekalipun. Perbedaan kedua ambang hanya muncul pada split uji (heavy 8 → 4 objek; partial 314 → 318).

## Kalimat interpretasi untuk BAB 4 (siap dipakai, sesuai spesifikasi Prompt 8)

> Validasi terhadap 200 objek pada 150 citra validasi yang dianotasi manual menghasilkan tingkat kesesuaian 68,0 persen dengan kappa Cohen 0,410, dan memperlihatkan bahwa proksi oklusi berbasis IoU maksimum cenderung meremehkan tingkat oklusi perseptual — 20,0 persen objek dinilai lebih ringan daripada penilaian manusia, seluruh 17 objek yang dinilai teroklusi berat oleh penilai manusia tidak pernah mencapai tier *heavy* menurut proksi, dan kekeliruan terbesar terjadi pada kelas kendaraan roda dua sebesar 45,5 persen, sehingga hasil evaluasi terstratifikasi pada dimensi oklusi perlu dibaca sebagai batas bawah performa pada kondisi teroklusi.

## Reproduksi

```bash
python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('anotasi_oklusi/manual_oklusi.csv','dataset/data.yaml',split='val'))"
```
Kit anotasi dibangkitkan oleh `make_oklusi_sample.py` (deterministik; 200 crop seimbang antar tier proksi dan antar kelas; antrean disusun bergantian antar tier sehingga setiap prefiks tetap seimbang).
