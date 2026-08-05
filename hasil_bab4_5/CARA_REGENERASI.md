# Cara Menyegarkan Ulang Folder Ini

Folder `hasil_bab4_5/` adalah **turunan otomatis** dari sumber kebenaran
(`eval_out/`, `nmsfree_out/`, `runs_tesis/`, `anotasi_oklusi/`, `dataset/`, `video_uji/`).
Bila sumber berubah, jalankan ulang generator agar folder ini tetap konsisten —
**jangan mengedit CSV/PNG di sini secara manual.**

## Regenerasi penuh (folder 01–06, 08)

```bash
cd d:\computer-vision\density-aware-yolo26-vehicle-counting
.\.venv\Scripts\python.exe y26_bangun_hasil_bab45.py
```

Aman dijalankan berulang kali — menimpa berkas lama dengan angka terbaru dari sumber.

## Regenerasi sebagian (setelah satu peristiwa tertentu)

```bash
# Setelah V8_normw (uji ketegaran) selesai training:
.\.venv\Scripts\python.exe -c "from y26_bangun_hasil_bab45 import bab_07_ketegaran; bab_07_ketegaran()"

# Setelah evaluate_all.py di-refresh-cache ulang (mis. ambang/aturan berubah lagi):
.\.venv\Scripts\python.exe -c "from y26_bangun_hasil_bab45 import bab_04_ablasi; bab_04_ablasi()"
```

## Yang TIDAK otomatis (perlu kerja manual)

| Folder | Kapan diisi | Caranya |
|---|---|---|
| `09_counting_end_to_end/` | Setelah GT terisi + `y26_counting.py` dijalankan tiap klip | Rangkum `counting_out/summary.json` per klip → tulis `ringkasan_counting.csv` + grafik baru; update status di README 09 dan README utama |
| `10_multi_seed/` | Setelah keputusan K6 diambil | Bila dijalankan: rangkum hasil multi-seed → tabel + grafik baru. Bila tidak: cukup pastikan kalimat keterbatasan masuk BAB 4/5 |

## Checklist sebelum menulis BAB 4/5 dari folder ini

- [ ] Folder 07 tidak lagi berstatus "MASIH BERJALAN"
- [ ] Folder 09 terisi hasil counting nyata (bukan placeholder)
- [ ] Folder 10 punya keputusan final (dijalankan ATAU kalimat keterbatasan disiapkan)
- [ ] README utama (`README.md`) kolom "Status" sudah diperbarui semua jadi ✅
- [ ] Jalankan sekali lagi `y26_bangun_hasil_bab45.py` penuh untuk memastikan tak ada
     angka basi dari sumber yang mungkin berubah di antara waktu
