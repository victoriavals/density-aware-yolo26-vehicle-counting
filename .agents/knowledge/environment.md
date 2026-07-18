# Lingkungan Teknis & Versi — Technical Environment & Versions

> **EN — TL;DR:** Reproducible research stack lives in `.venv` (Python 3.11.9, torch 2.11.0+cu128, ultralytics **8.4.92** — version-LOCKED, supervision 0.29.1 which must stay `<0.30`), on a single RTX 4060 Ti 8GB. Windows-native (no WSL/Zellij), so every long job runs as a background process writing a timestamped `logs/<name>.log`. Invoke the interpreter directly as `.venv\Scripts\python.exe` — never a global `python`. `test_smoke.py` must pass before any training.

Dokumen ini merangkum lingkungan teknis proyek sesuai `CLAUDE.md` §8 dan §13 serta `README.md`. Angka dan nama paket di sini adalah kondisi *reproducible* yang sudah terverifikasi pada P1 (13 Jul 2026); jangan mengubahnya tanpa alasan kuat karena beberapa versi dikunci demi kebenaran metodologis.

## Ringkasan versi

Lingkungan sudah terpasang penuh di direktori `.venv` pada akar repositori. Isi utama terverifikasi sebagai berikut.

| Komponen | Versi terpasang | Catatan penting |
|---|---|---|
| Python | 3.11.9 | Interpreter di dalam `.venv`; jangan pakai `python` global |
| PyTorch | 2.11.0+cu128 | Roda *build* CUDA 12.8; `torch.cuda.is_available()` harus `True` |
| Ultralytics | **8.4.92** (TERKUNCI) | Basis YOLO26; lihat "Mengapa 8.4.92 dikunci" di bawah |
| supervision | 0.29.1 | WAJIB `<0.30` — `sv.ByteTrack` dihapus di 0.30 |
| roboflow | terpasang | Unduh dataset `traffic-merged` (`download_dataset.py`, subbab 3.3) |
| scipy | terpasang | Uji Wilcoxon *signed-rank* + Holm (`y26_stats.py`) |
| pandas | terpasang | Baca/tulis `results.csv`, CSV strata & Wilcoxon |
| matplotlib | terpasang | Plot `dr_vs_tau.png`, `cm_hist.png` (`analyze_nmsfree.py`) |

## Perangkat keras (GPU)

Eksperimen berjalan pada satu **GPU RTX 4060 Ti 8GB**, terverifikasi lewat `nvidia-smi` pada 13 Jul 2026 (CLAUDE.md §8). VRAM 8 GB adalah batas nyata yang membentuk strategi memori: konfigurasi *default* (batch 16, AMP FP16, `cache=False`, `workers 4`) dirancang muat, dan pada P5 batch 16 memang bertahan penuh untuk kedelapan varian tanpa satu pun *out-of-memory*. Varian ber-P2 (V3/V5/V7/V8) paling boros karena *feature map* 160×160 (VRAM tercatat 8,52–8,64 GB); bila kelak OOM, aturan A-12 menurunkan `--batch` untuk **SEMUA** varian sekaligus (bukan mencampur), demi keadilan ablasi. Detail strategi memori dan keputusan A-12 ada di [Menjalankan eksperimen](../playbooks/run-experiment.md) dan [Keputusan pending](../status/pending-decisions.md).

### Diskrepansi dokumen — "RTX 3060" vs "RTX 4060 Ti"

Ada ketidakcocokan terbuka antara perangkat nyata dan naskah tesis yang **HARUS dikonfirmasi/diperbaiki**, bukan diputuskan sendiri. Perangkat aktual adalah RTX 4060 Ti 8GB, tetapi CLAUDE.md §8 mencatat naskah masih menulis "RTX 3060 8GB" di **5 lokasi** yang wajib diperbarui: Batasan 1.5, Tabel 3.6, subbab 2.5.2, 2.7.3, dan 3.6.2. Perlu dicatat pula bahwa dokumen REVISI_PEMBIMBING sudah memakai "RTX 4060 8GB" di sebagian tempat, sementara `README.md` menuliskannya singkat sebagai "RTX 4060"; sisa lokasi yang belum tersunting harus diverifikasi langsung ke naskah, jangan diasumsikan sudah tuntas. Argumen "perangkat kelas menengah" tetap berlaku karena VRAM sama-sama 8 GB. Item ini ada di daftar TODO naskah (CLAUDE.md §10.4) — surface saja di KB, penyelesaian menunggu Naufal.

## Mengapa Ultralytics 8.4.92 dikunci

Versi ini **tidak boleh dinaikkan tanpa penyesuaian**. Alasannya: `DALWDetectionLoss` menyalin persis satu metode internal Ultralytics, yaitu `get_assigned_targets_and_loss` (di `utils/loss.py` baris 400–463) versi 8.4.92. Jika versi Ultralytics berubah dan tanda tangan/perilaku metode itu bergeser, penyuntikan bobot densitas bisa salah tanpa terlihat.

Penjaga (*guard*) atas risiko ini adalah uji **T4** di `test_smoke.py` (*loss end-to-end*). Aturan operasionalnya: setiap kali Ultralytics diperbarui, jalankan `test_smoke.py`; **bila T4 gagal, JANGAN lanjut training** sebelum salinan metode disesuaikan dengan versi baru. Karena itu `test_smoke.py` WAJIB lulus sebelum pelatihan apa pun. Konteks arsitektur injeksi (HAM *namespace injection*, DALW *monkey-patch*, varian YAML programatis) ada di [Injeksi kode](../architecture/code-injection.md).

Catatan supervision: `sv.ByteTrack` sudah *deprecated* sejak supervision 0.28 dan **dihapus** di 0.30, sehingga rentang `>=0.25,<0.30` (terpasang 0.29.1) wajib dipertahankan agar pipeline *counting* (`y26_counting.py`, subbab 3.10) tetap berfungsi. Versi pustaka ini perlu dicatat di BAB 3/4.

## Cara memakai `.venv`

Panggil interpreter di dalam `.venv` **secara langsung** — jangan mengandalkan aktivasi *shell* atau `python` global (keliru interpreter berarti keliru versi paket, dan bisa memicu kegagalan T4 palsu).

```powershell
# Windows / PowerShell (shell utama proyek)
.\.venv\Scripts\python.exe test_smoke.py
.\.venv\Scripts\python.exe test_smoke.py --no-net   # lewati uji yang butuh unduhan
```

```bash
# Bash (untuk skrip POSIX / pipa logging)
./.venv/Scripts/python.exe test_smoke.py
```

Verifikasi cepat GPU sebelum training: `.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"` harus mencetak `True`.

## Windows-native: job panjang = background + log ber-stempel-waktu

PC ini **tidak memakai WSL maupun Zellij** (WSL tak berdistribusi di mesin ini), sehingga skenario multiplexer terminal pada prompt asli diadaptasi menjadi **Opsi A Windows-native**: setiap job panjang (grid search, pelatihan 8 varian, evaluasi) dijalankan sebagai *background process* yang menulis `logs/<nama>.log` dengan **stempel waktu per baris**. Job terbukti selamat meski VS Code ditutup (proses OS tetap hidup, teramati pada P3 dan P5). Pemantauan dari PowerShell:

```powershell
Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8
```

Konvensi pipa `awk` (pecah `\r` per baris, buang ANSI + glyph *bar*, stempel per baris, `--project` ABSOLUT), format `logs/sesi.log`, dan aturan pembaruan §15 CLAUDE.md dirinci di [Logging & status](../rules/logging-and-status.md) — jangan diduplikasi di sini. Nilai desimal dalam narasi tesis memakai koma (mis. mAP50-95 val 0,6670), sedangkan nilai di JSON/CLI apa adanya (`0.6670`); keduanya merujuk angka yang sama.

## Tautan terkait

- [Logging & status](../rules/logging-and-status.md) — konvensi log ber-stempel-waktu, `logs/sesi.log`, pembaruan §15
- [Injeksi kode](../architecture/code-injection.md) — tiga mekanisme patch di atas Ultralytics 8.4.92
- [Menjalankan eksperimen](../playbooks/run-experiment.md) — strategi memori 8 GB (A-12), urutan job
- [Keputusan pending](../status/pending-decisions.md) — A-12 dan diskrepansi dokumen
