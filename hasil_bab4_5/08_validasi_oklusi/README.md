# 08 — Validasi Proksi Oklusi terhadap Anotasi Manual

Menjawab Subbab 3.3.3 — janji naskah untuk memvalidasi proksi oklusi otomatis
(Pers. 3.1) terhadap penilaian manusia pada subset kecil.

## Berkas

| Berkas | Isi |
|---|---|
| `manual_oklusi.csv` | 200 penilaian manual (no/partial/heavy) oleh peneliti, *blind* terhadap tier proksi |
| `hasil_kesesuaian.json` | Angka kesesuaian + matriks konfusi lengkap (keluaran `occlusion_agreement`) |
| `matriks_konfusi_oklusi.png` | Visualisasi matriks konfusi: baris = manual, kolom = proksi |
| `kesesuaian_per_kelas.png` | Persentase kesesuaian per kelas objek |

## Hasil Utama

**Kesesuaian keseluruhan: 68,0%** (136/200 objek), dari 150 citra validasi, 200 objek.

### Cara membaca matriks konfusi

Baris = penilaian manusia, kolom = tebakan proksi otomatis. **Sel kolom "heavy" kosong
total (0 di ketiga baris)** — proksi **tidak pernah** memberi tier heavy pada 200 objek
yang diuji, padahal manusia menemukan **17 objek heavy** (baris ketiga: 3+14=17).
Ke-17 objek itu dinilai proksi sebagai "partial" (14) atau bahkan "no" (3).

### Bias sistematis

- **Meremehkan** (proksi lebih ringan dari manual): 20,0% objek (40/200)
- **Melebihkan** (proksi lebih berat dari manual): 12,0% objek (24/200)
- Bias **asimetris ke arah meremehkan** — mengonfirmasi keterbatasan yang sudah diakui
  terbuka di Subbab 3.3.3: ketika objek kecil tertutup objek besar, luas gabungan
  (union) yang besar menekan nilai IoU sehingga oklusi tampak kecil secara matematis.

### Per kelas (`kesesuaian_per_kelas.png`)

| Kelas | Kesesuaian |
|---|---|
| big-vehicle | 79,4% |
| pedestrian | 76,4% |
| car | 66,1% |
| **two-wheeler** | **54,5%** (terlemah) |

Kelas terkecil dan mayoritas dataset (`two-wheeler`) paling sering salah dinilai proksi
— konsisten dengan mekanisme bias (objek kecil paling terpengaruh efek union-besar).

## Konsekuensi untuk Folder 04 (Ablasi Deteksi)

Karena proksi nyaris tidak pernah membentuk tier heavy pada data nyata (val: 0/4.094,
test: hanya 4/2.600 pada ambang 0,40), **seluruh sel occlusion/heavy dikeluarkan** dari
uji Wilcoxon di `04_ablasi_deteksi/wilcoxon_ap5095.csv` (aturan sel-minimum 30 objek).
Kedua temuan ini **saling menguatkan secara independen** — bukan kebetulan.

## Kalimat siap-adaptasi

> "Validasi terhadap 200 objek pada 150 citra validasi yang dianotasi manual
> menghasilkan tingkat kesesuaian 68,0 persen, dan memperlihatkan bahwa proksi oklusi
> berbasis IoU maksimum cenderung meremehkan tingkat oklusi perseptual — 20,0 persen
> objek dinilai lebih ringan daripada penilaian manusia, dan seluruh 17 objek yang
> dinilai teroklusi berat oleh penilai manusia tidak pernah mencapai tier heavy menurut
> proksi. Kekeliruan terbesar terjadi pada kelas kendaraan roda dua sebesar 45,5 persen,
> sehingga hasil evaluasi terstratifikasi pada dimensi oklusi, khususnya pada tier
> heavy yang hampir tidak terisi, perlu dibaca sebagai batas bawah performa pada
> kondisi teroklusi berat, bukan estimasi yang teruji secara memadai."

## Reproduksi

```bash
python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('anotasi_oklusi/manual_oklusi.csv','dataset/data.yaml',split='val'))"
```
