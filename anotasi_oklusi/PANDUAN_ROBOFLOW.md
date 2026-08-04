# Panduan P8 via Roboflow — Validasi Proksi Oklusi (Subbab 3.3.3)

Jalur Roboflow untuk menganotasi 200 crop → `manual_oklusi.csv`. Integritas
pemasangan `(image, gt_index)` dijaga oleh `sample_manifest.csv` (nama crop =
sample_id), lalu `roboflow_ke_oklusi.py` mengonversi ekspornya. Alat sudah diuji.

**Yang dinilai:** pada tiap crop, objek di **KOTAK MERAH** — seberapa besar bagiannya
tertutup objek lain (kotak kuning = tetangga)?
- `no` = terlihat utuh / nyaris utuh
- `partial` = sebagian tertutup, mayoritas masih terlihat
- `heavy` = sebagian besar tertutup

Crop sudah menggambar kotak merah/kuning ke dalam gambar, jadi penilaian tetap **blind**
(tier proksi tidak ditampilkan).

---

## Langkah

### 1. Akun & workspace
- Daftar/masuk di https://roboflow.com (paket gratis "Public" cukup; 200 gambar jauh di bawah kuota).
- Buat Workspace bila belum ada.

### 2. Buat proyek Classification
- **Create New Project** → **Project Type: Classification** → **Single-Label**.
- Annotation Group: `occlusion` (bebas).
- Buat **tepat 3 kelas** dengan nama persis (huruf kecil): **`no`**, **`partial`**, **`heavy`**.

### 3. Upload crop
- **Upload Data** → seret seluruh isi folder **`anotasi_oklusi/imgs/`** (200 berkas `000.jpg`–`199.jpg`).
- **Save and Continue**. (Jangan pakai Label Assist / auto-label.)

### 4. Anotasi (±20–30 menit)
- Buka antrean **Annotate**. Untuk tiap crop, tetapkan satu kelas `no`/`partial`/`heavy`
  berdasar objek di kotak merah (lihat definisi di atas). Tombol angka/klik mempercepat.
- Selesaikan **semua 200** (boleh sebagian; converter memakai yang ada, tapi lengkap lebih baik).
- **Add Images to Dataset** (approve semua).

### 5. Generate version + export
- **Generate** versi baru: **tanpa augmentasi**; preprocessing/resize bebas (kita hanya butuh labelnya).
- Split tidak penting (boleh 100% train atau default; converter membaca semua split).
- **Export Dataset** → format **"Folder Structure"** (paling aman) → **Download zip** (bukan kode).

### 6. Konversi ke manual_oklusi.csv
Ekstrak zip ekspor ke sebuah folder, lalu di root repo:
```bash
python roboflow_ke_oklusi.py --export <folder_hasil_ekstrak>
```
Menulis `manual_oklusi.csv` (format `image,gt_index,tier`) + melaporkan berapa dari 200
terpetakan dan distribusi tier.

### 7. Hitung kesesuaian (Prompt 8)
```bash
python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('manual_oklusi.csv','dataset/data.yaml',split='val'))"
```
Atau cukup tempel **Prompt 8** ke Claude — akan dirangkum ke `hasil/validasi_oklusi.md`
dengan satu kalimat interpretasi untuk BAB 4.

---

## Catatan
- **Nama kelas** harus `no`/`partial`/`heavy` (converter meng-huruf-kecilkan, tapi harus tiga kata itu).
- Ekspor **Multiclass CSV** juga didukung converter (auto-deteksi); "Folder Structure" paling tahan banting.
- Alternatif tanpa Roboflow: buka `anotasi_oklusi/anotasi.html` (offline, langsung ekspor CSV) —
  lebih cepat untuk satu anotator; Roboflow unggul bila dibagi ke beberapa orang / dari ponsel.
- ⚠️ Ekspektasi hasil: proksi box-IoU cenderung *underestimate* oklusi perseptual, dan tier
  heavy nyaris kosong di val — matriks konfusi manual-vs-proksi justru mengukur kesenjangan ini
  (bahan diskusi BAB 4; ambang 0,10/0,35 tetap terkunci sampai ada angka + keputusan pembimbing).
