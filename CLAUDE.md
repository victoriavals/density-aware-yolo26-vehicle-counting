# CLAUDE.md — Konteks Proyek Tesis S2 Naufal Firdaus

> Dokumen ini adalah sumber kebenaran (single source of truth) proyek. Baca seluruhnya sebelum mengerjakan apa pun.

## 1. Identitas Tesis
- **Judul (final terbaru):** MODIFIKASI DETEKTOR *NMS-FREE* YOLO26 DENGAN PEMBOBOTAN *LOSS* BERBASIS DENSITAS DAN PELACAKAN BYTETRACK UNTUK PENGHITUNGAN KENDARAAN *REAL-TIME* PADA LALU LINTAS HETEROGEN PADAT
- **Penulis:** Naufal Firdaus — NIM 20240804017
- **Program:** Magister Ilmu Komputer, Fakultas Ilmu Komputer, Universitas Esa Unggul
- **Pembimbing:** Ibu Sandfreni — sandfreni@esaunggul.ac.id (bimbingan offline Sabtu di kampus)
- ⚠️ Verifikasi judul konsisten di halaman judul, ABSTRAK/ABSTRACT, dan seluruh bab; jangan pernah memakai frasa lama "berbasis ukuran objek".

## 2. Ringkasan Penelitian
Lalu lintas heterogen padat (CCTV Jakarta) menyulitkan detektor standar karena tiga hal: dominasi objek kecil (roda dua 8–16 piksel pada citra 640), oklusi tinggi antarobjek, dan kepadatan ekstrem (>25 objek/frame). Tujuan umum: mengembangkan dan mengevaluasi modifikasi YOLO26 untuk sistem penghitungan kendaraan *real-time*.

**Rumusan masalah:** (RQ1) merancang modifikasi YOLO26 (HAM + P2 + DALW) yang kompatibel dengan paradigma *NMS-free*; (RQ2) kontribusi tiap komponen via *ablation study*; (RQ3) pengaruh P2 & HAM terhadap kestabilan pencocokan *one-to-one*; (RQ4) performa terstratifikasi (ukuran × oklusi × densitas); (RQ5) akurasi *end-to-end* dengan ByteTrack terhadap standar penerapan praktis (ambang konkret masih pending).

## 3. Framing Kebaruan — DUA PILAR (jangan diubah)
1. **Kebaruan metodologis — Density-Aware Loss Weighting (DALW):** densitas lokal ρᵢ = Σⱼ≠ᵢ exp(−‖cᵢ−cⱼ‖²/2σ²) (Pers. 3.2) → normalisasi ρ̂ᵢ = ρᵢ/(ρᵢ+1) (3.3) → bobot wᵢ = 1 + α·ρ̂ᵢ (3.4) → L = (1/N)Σ wᵢ·Lᵢ (3.5). Melengkapi STAL bawaan YOLO26: STAL bekerja di penetapan label berbasis **ukuran**; DALW di penghitungan *loss* berbasis **densitas** (lihat Tabel 3.2). Bobot dihitung dari *ground truth* (konstanta per iterasi, termasuk pasca-augmentasi), tanpa gradien tambahan.
2. **Kebaruan analitis:** penyelidikan empiris pertama interaksi modifikasi dengan mekanisme *one-to-one NMS-free* via **Duplicate Rate** (Pers. 3.6, ambang τ = 0,25), **Confidence Margin** (Pers. 3.7), dan stabilitas *assignment* antar-epoch (belum diformalkan — pending A-10).

**HAM dan Lapisan P2 adalah INSTRUMEN, bukan klaim kebaruan.** YOLO26 sudah punya ProgLoss + STAL, jadi semua klaim peningkatan diframe sebagai perbaikan atas *baseline* yang sudah kuat.

## 4. Ringkasan BAB 1–3
- **BAB 1:** latar (>168 juta kendaraan, >80% roda dua [1]); dua celah YOLO26: validasi hanya di MS COCO, dan informasi densitas lokal belum dimanfaatkan. Tabel 1.1 Evolusi YOLO (v1→26); Gambar 1.1 montase 3 foto CCTV (a objek kecil, b oklusi, c kepadatan); G1.2 tiga komponen; G1.3 konsep DALW. Tujuan mengacu "*baseline* YOLO26 standar" (bukan v8/v11/v12).
- **BAB 2:** SLR. 2.3.5 YOLO26 (*dual-head NMS-free*, ProgLoss, STAL, MuSGD) dengan bahasa kehati-hatian *preprint* [7][8]. 2.5 modifikasi objek kecil — Tabel 2.1: HIC-YOLOv5, CRL-YOLOv5, MST-YOLO semuanya *NMS-based* (celah). 2.6 preseden Focal Loss [21]. 2.7 tracker — Tabel 2.2: ByteTrack MOTA 80,3 / IDF1 77,3 di MOT17 [16]. 2.9 posisi SOTA (Tabel 2.3–2.4, Gambar 2.4 kuadran).
- **BAB 3:** alur (G3.1); dataset & *group-based split* (3.3.2); proksi oklusi oᵢ = maxⱼ IoU(bᵢ,bⱼ) (Pers. 3.1) + pengakuan limitasi + rencana validasi manual (3.3.3); augmentasi mosaic (off 10 epoch terakhir; densitas dihitung ulang pasca-augmentasi); modifikasi 3.6 (Tabel 3.2 STAL vs DALW); analisis NMS-free 3.7; ablasi 3.8; hiperparameter 3.9 + limitasi *grid search* satu titik + mitigasi sensitivitas α di V4; integrasi 3.10; evaluasi 3.11 (Pers. 3.8–3.14); Wilcoxon + Holm (3.11.4); lingkungan 3.12 (Tabel 3.6).

## 5. Dataset
**traffic-merged** — 3.389 citra CCTV lalu lintas Jakarta (data primer, mayoritas kamera dipasang peneliti) [17: universe.roboflow.com/naufalfirdaus/traffic-merged-qke0k-3yyyo]. Empat kelas: kendaraan roda dua (*two-wheeler*, dominan), mobil (*car*), kendaraan besar (*big-vehicle* = bus+truk), pejalan kaki (*pedestrian*, objek konteks — TIDAK dihitung). Split 70/20/10 **berbasis kelompok kamera×adegan×sesi** (bukan per-frame) untuk mencegah *data leakage* → ≈2.372/678/339 citra. Atribut stratifikasi diturunkan komputasional: ukuran (konvensi COCO), oklusi (proksi Pers. 3.1), densitas (jumlah & kerapatan kotak per frame).

## 6. Desain Eksperimen
| Varian | HAM | P2 | DALW | Keterangan |
|---|---|---|---|---|
| V1 | – | – | – | Baseline YOLO26 |
| V2 | ✓ | – | – | HAM saja |
| V3 | – | ✓ | – | P2 saja |
| V4 | – | – | ✓ | DALW saja |
| V5 | ✓ | ✓ | – | HAM+P2 |
| V6 | ✓ | – | ✓ | HAM+DALW |
| V7 | – | ✓ | ✓ | P2+DALW |
| V8 | ✓ | ✓ | ✓ | Model penuh |

*Grid search* α ∈ {0,5; 1,0; 2,0} × σ ∈ {0,05; 0,10; 0,20} (koordinat ternormalisasi), sekali pada V8 dengan pelatihan dipersingkat, kriteria mAP@0,5:0,95 validasi, lalu dibekukan; limitasinya diakui + sensitivitas α pada V4 dilaporkan di BAB 4. Hiperparameter (Tabel 3.4): 640×640, MuSGD, maks 300 epoch + *early stopping*, batch 16 FP16, lr 0,01 *cosine*, τ = 0,25. Statistik: Wilcoxon signed-rank 5%; *pairing* AP per kelas×strata (deteksi) dan galat per interval (penghitungan); **tiga hipotesis utama: V8–V1, V4–V1, V8–V5**; sisanya sekunder dengan koreksi Holm. Analisis NMS-free fokus varian ber-P2 (V3, V5, V7, V8).

## 7. Integrasi & Evaluasi
ByteTrack via pustaka `supervision` [26] + *virtual line crossing* (per arah, per kelas; pejalan kaki dikecualikan). Metrik deteksi: P, R, F1, mAP@0,5, mAP@0,5:0,95 (Pers. 3.8–3.11). Metrik penghitungan: MAE, RMSE, MAPE (Pers. 3.12–3.14) — **MAPE hanya pada y_t > 0**, proporsi pengecualian dilaporkan. Evaluasi terstratifikasi tiga dimensi: ukuran (small/medium/large), oklusi (no/partial/heavy), densitas (sparse/medium/dense).

## 8. Lingkungan Teknis & Kode
- PyTorch + **Ultralytics 8.4.92**, Python, Roboflow, Mendeley (.bib).
- **GPU: RTX 4060 Ti 8GB** (terverifikasi `nvidia-smi` 13 Jul 2026). ⚠️ Dokumen tesis masih menulis "RTX 3060 8GB" di **5 lokasi** yang WAJIB diperbarui ke "RTX 4060 Ti 8GB": Batasan 1.5, Tabel 3.6, subbab 2.5.2, 2.7.3, 3.6.2.
- Paket kode `model_tesis_lengkap.zip` (15 file, ±2.645 baris), terverifikasi terhadap Ultralytics 8.4.92, mencakup fase model hingga evaluasi.
- Deployment: API *real-time* dari PC → website Traffic Detection PSM di `cam.geprekinaja.my.id` (React SPA). **Kode website DI LUAR scope tesis** — scope hanya model s.d. evaluasi.

## 9. Status Pekerjaan
- BAB 1–3 **final** (`TESIS_BAB1-3_FINAL_v2.docx`); audit sitasi selesai: 27 referensi IEEE bracket urut kemunculan pertama, semua ber-URL/DOI (satu pengecualian *paywalled*: Wilcoxon 1945 di JSTOR).
- BAB 4–5 **belum ditulis**; **18 placeholder numerik** ([XX,X], [0,0XX], dll.) + 2 placeholder naratif menunggu hasil eksperimen.
- Bibliografi siap: `Daftar_Pustaka_Gabungan_BAB1-3.bib` (urutan entri = [1]–[27]).

## 10. TODO
1. Implementasi *group-based split* SEBELUM pelatihan apa pun; simpan daftar grup per subset sebagai bukti.
2. Jalankan eksperimen: grid search → V1–V8 (prioritas V1→V4→V8; *fallback* batch 8 + *gradient accumulation* untuk varian ber-P2) → instrumentasi NMS-free → sensitivitas α (V4) dan τ → stratifikasi → Wilcoxon+Holm → penghitungan ByteTrack.
3. Isi 18 placeholder; tulis BAB 4–5.
4. Update RTX 3060 → RTX 4060 di 5 lokasi (§8).
5. **7 keputusan pending:** (A-10) formalisasi metrik stabilitas *assignment* + sensitivitas τ {0,10; 0,25; 0,50}; (A-11) tentukan *head* YOLO26 penerima wᵢ setelah verifikasi kode (o2m/o2o/keduanya); (A-12) strategi komputasi 8 varian pada GPU 8GB VRAM: *patience early-stopping* eksplisit + *checkpoint-resume*; (A-02) target konkret RQ5 (mis. ambang MAPE & FPS); (A-03) verifikasi angka MST-YOLO (+8,42%; 70,97%) dan HIC-YOLOv5 (+6,42%) ke sumber [12][13]; (A-01) redaksi alternatif abstrak bila hasil tidak signifikan; (B-01) cek batas kata abstrak (±360).
6. Naskah: revisi manual gambar tersisa (pangkas kotak G1.3/2.1/2.2/2.3/3.4; teks G2.3 "8–16 piksel" & hapus "+5–7% mAP"; margin G3.1; label G3.5), tempel Daftar Pustaka, Lampiran 1, halaman administratif.

## 11. Standar Penulisan (WAJIB)
Bahasa Indonesia akademik formal; Times New Roman 12pt, spasi 1,5; margin 3-3-3-4 cm (kiri 4 cm); indentasi baris pertama 1 cm; sitasi IEEE bracket urut kemunculan pertama; **body text prosa murni TANPA bullet/numbering**; istilah asing/teknis dicetak *miring* (kecuali nama produk: YOLO26, ByteTrack, Roboflow); desimal memakai koma; gaya bahasa natural anti-deteksi-AI (variasikan struktur kalimat, hindari pola repetitif).

## 12. Aturan Kerja untuk Claude Code
1. Jaga konsistensi istilah, angka, dan framing dua-pilar lintas bab; istilah utama "Pembobotan *Loss* Berbasis Densitas" (DALW hanya di tabel/nama varian).
2. **JANGAN PERNAH** mengklaim HAM atau P2 sebagai kebaruan.
3. **JANGAN** mengisi/mengubah placeholder tanpa data eksperimen nyata; **JANGAN** menambah/menghapus/menggeser nomor sitasi [1]–[27]; **JANGAN** menulis BAB 4–5 sebelum ada hasil.
4. Implementasi kode WAJIB mengikuti metodologi final: group split, protokol Wilcoxon (3 hipotesis utama + Holm), aturan MAPE y_t > 0, densitas dihitung ulang pasca-augmentasi.
5. Pertahankan bahasa kehati-hatian *preprint* (2.3.5, 2.9, 3.5).
6. Konfirmasi ke Naufal sebelum keputusan besar (perubahan desain, judul, struktur bab, atau apa pun yang menyentuh 7 keputusan pending).
7. **Setiap akhir prompt/sesi:** perbarui §15 (Status & Log Progres) dengan hasil dan keputusan baru, lalu bersihkan kode/artefak temporer yang tidak dipakai lagi (artefak hasil eksperimen dan bukti metodologis JANGAN dihapus).
8. **Log proses sesi:** setiap tindakan/keputusan/temuan/insiden signifikan di-append ke `logs/sesi.log` (format `[YYYY-MM-DD HH:MM] KATEGORI | isi`) — proses harus terdokumentasi, bukan hanya hasil. Job panjang tetap punya log keluaran sendiri (`logs/<nama>.log`, stempel waktu per baris, per-batch).

## 13. Perintah Pengembangan

Repositori ini berisi skrip Python murni (tanpa pyproject/requirements — instal manual). Peta lengkap berkas → subbab tesis ada di `README.md`.

```bash
# Lingkungan SUDAH TERPASANG di .venv (Python 3.11.9) — pakai:
#   Windows: .\.venv\Scripts\python.exe   (bash: ./.venv/Scripts/python.exe)
# Isi: torch 2.11.0+cu128, ultralytics==8.4.92, supervision 0.29.1 (WAJIB <0.30,
# sv.ByteTrack dihapus di 0.30), roboflow, scipy, pandas, matplotlib

# Uji — skrip biasa, BUKAN pytest; tiap file menjalankan seluruh kasusnya berurutan.
# Jalankan satu kasus dengan mengimpor fungsinya: python -c "from test_smoke import t1_math; t1_math()"
python test_smoke.py            # T1-T4: matematika DALW, arsitektur, transfer bobot, loss E2E (unduh yolo26s.pt sekali)
python test_smoke.py --no-net   # lewati uji yang butuh unduhan
python test_nmsfree.py          # U1-U5: matcher, DR/CM, stabilitas, forward internal
python test_eval.py             # E1-E7: strata, AP, Wilcoxon/Holm, counting

# Dataset: dataset/ AKTIF = hasil re-split lokal berbasis grup 70/20/10 (§15 P2).
# Ekspor Roboflow ASLI (split bocor) hanya tersisa sebagai arsip traffic-merged.yolo26.zip;
# regenerasi bila perlu: ekstrak zip -> dataset_raw/ lalu python make_group_split.py
# (deterministik; bukti_split_*.csv ikut ditulis ulang)

# Eksperimen (urutan wajib; jalankan sebagai BACKGROUND process + log ber-stempel-waktu)
# Konvensi log (bash) — pecah \r per baris, buang ANSI + glyph bar (ASCII murni), stempel per baris;
# WAJIB --project ABSOLUT (runs_dir gotcha, lihat §15 P3):
#   <perintah> 2>&1 | awk 'BEGIN{RS="\r|\n"} { gsub(/\x1b\[[0-9;]*[a-zA-Z]/,""); gsub(/[\xe2][\x94-\x95][\x80-\xbf]/,""); if ($0 != "") print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush() }' > logs/<nama>.log
# Pantau dari PowerShell: Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8
python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60  # grid α,σ → dalw_best.json
python train_ablation.py --data dataset/data.yaml --variant all                 # V1..V8, seed 0
python train_ablation.py --data dataset/data.yaml --variant V5 --resume         # lanjut bila terputus

# Evaluasi (setelah semua varian selesai)
python evaluate_all.py --data dataset/data.yaml --split test --variants all     # → eval_out/
python analyze_nmsfree.py --data dataset/data.yaml --split test --runs runs_tesis # → nmsfree_out/
python y26_counting.py --video klip.mp4 --weights runs_tesis/V8/weights/best.pt \
    --line x1,y1,x2,y2 --interval-s 60 --gt gt.csv                              # → counting_out/
```

`test_smoke.py` WAJIB lulus sebelum training apa pun. Kode dikunci pada ultralytics **8.4.92** karena `DALWDetectionLoss` menyalin metode internal `get_assigned_targets_and_loss` (utils/loss.py:400-463) versi tersebut; bila versi berubah dan T4 gagal, jangan lanjut sebelum disesuaikan.

## 14. Arsitektur Kode

Seluruh kode adalah **lapisan patch/injeksi di atas ultralytics terpasang** — tidak ada fork. Tiga mekanisme injeksi yang harus dipahami bersama:

1. **HAM via namespace injection** (`y26_modules.register_ham()`): kelas `HAM` di-setattr ke `ultralytics.nn.tasks` (parse_model meresolusi nama YAML via globals()) + `ultralytics.nn.modules` + alias `sys.modules["y26_modules"]` agar `torch.load` checkpoint menemukan kelasnya. **Setiap entry point yang membangun/memuat model ber-HAM wajib memanggil `register_ham()` lebih dulu** — semua skrip evaluasi sudah melakukannya.
2. **DALW via monkey-patch loss** (`y26_dalw.apply_dalw(α,σ)`): mengganti `DetectionModel.init_criterion` secara global agar `E2ELoss` dibangun dengan `DALWDetectionLoss` pada KEDUA cabang head (keputusan A-11). Harus dipanggil SEBELUM `model.train()` (trainer membangun ulang model). Bobot w_i dihitung DI DALAM loss dari label batch (otomatis pasca-augmentasi, `torch.no_grad`).
3. **Varian via YAML programatis** (`y26_variants`): YAML HAM dibangkitkan dari YAML resmi terpasang (`yolo26.yaml`/`yolo26-p2.yaml`) dengan sisipan setelah blok C3k2 indeks 4 & 6 dan pemetaan ulang seluruh indeks head (`_new_index`); transfer bobot COCO memetakan ulang nama parameter untuk mengatasi pergeseran indeks. Hasil transfer disimpan ke `inits/{V}_init.pt` karena transfer in-memory hilang saat trainer membangun ulang model.

**Konvensi akses kepala one-to-one mentah:** seluruh evaluasi (DR/CM, cache strata, counting) SENGAJA melewati predictor standar — forward langsung `DetectionModel` mode eval mengembalikan `(B, 300, 6)` `[xyxy, conf, cls]` pada ruang letterbox 640, dan GT ditransformasikan ke ruang yang sama via `_letterbox` bersama di `y26_nmsfree.py`. `train_format_forward` hanya menaikkan flag `training` milik modul Detect (bukan `.train()`) agar dict dual-head keluar tanpa merusak statistik BN.

**Alur data eksperimen:**
```
train_ablation.py ──→ runs_tesis/<V>/ (results.csv, weights/{best,last}.pt, nmsfree_probe.csv)
     │  (dalw_best.json dibaca otomatis; probe NMSFreeProbe per epoch via callback)
     ├─ evaluate_all.py ──→ eval_out/ (global_metrics.csv, strata_ap.csv, wilcoxon_*.csv, cache_<V>.npz dipakai ulang)
     ├─ analyze_nmsfree.py ──→ nmsfree_out/ (summary.csv, tau_sweep.csv, per-image CSV, plot)
     └─ y26_counting.py ──→ counting_out/ (counts, events, errors, summary.json berisi MAE/RMSE/MAPE/FPS)
```
Rantai dependensi modul: `y26_modules` ← `y26_variants` ← `train_ablation`; `y26_nmsfree` menyediakan `_letterbox`/`split_image_paths` yang dipakai `y26_strata`; `y26_stats` mengonsumsi baris `stratified_ap`. Folder `runs_tesis/`, `eval_out/`, `nmsfree_out/` adalah bahan mentah BAB 4 — jangan dihapus/ditimpa.

**Invarian metodologis yang dikodekan (jangan dilonggarkan):** konfigurasi identik antarvarian (seed 0, batch sama untuk kedelapan varian — bila OOM turunkan untuk SEMUA); tier strata default oklusi 0,10/0,35, densitas 10/26, ukuran konvensi COCO; unit Wilcoxon = AP per (kelas × strata) tanpa baris global, 3 hipotesis utama tanpa koreksi + sekunder Holm; MAPE hanya y>0 dengan proporsi eksklusi dilaporkan; pejalan kaki dikecualikan dari counting.

## 15. Status & Log Progres Eksperimen (perbarui tiap prompt — aturan §12.7)

Eksperimen mengikuti 10 prompt berurutan di `prompts_claude_code_nfl_v2.md`, **adaptasi Windows native (Opsi A)**: tanpa Zellij/WSL (WSL tak berdistribusi di PC ini); job panjang = background process + log `logs/<nama>.log`; pantau: `Get-Content logs\<nama>.log -Wait -Tail 30`.

- **P1 ✅ (13 Jul 2026) — Lingkungan.** `.venv` Python 3.11.9; torch 2.11.0+cu128; ultralytics 8.4.92; supervision 0.29.1; CUDA aktif pada **RTX 4060 Ti 8GB**. `test_smoke.py` T1–T4 **LULUS** (transfer bobot: HAM 97% kunci/100% param; P2 40%/62%; HAM+P2 40%/63% — bahan paragraf inisialisasi BAB 4). Log: `logs/smoke.log`.
- **P2 ✅ (13 Jul 2026) — Dataset.** Ekspor Roboflow manual (dari `sahabats-workspace/traffic-merged-qke0k-3yyyo-nkdvt` — ⚠️ beda dengan sitasi [17], konsistenkan di naskah) berproporsi 83,4/12,6/4,0 dan **bocor** (3 pasang citra byte-identik lintas split) → atas persetujuan Naufal, re-split lokal berbasis grup via `make_group_split.py` → **2.372/679/338 citra (70,0/20,0/10,0), grup 672/53/33, 0 pelanggaran md5/grup**; komposisi kelas test min. 332 instans/kelas. Hasil split kini menjadi **`dataset/` aktif** (ekspor asli yang bocor dihapus; arsipnya `traffic-merged.yolo26.zip` di root, integritas terverifikasi 3.389 citra+label). Bukti lampiran: `bukti_split_grup.csv` (758 grup) + `bukti_split_citra.csv`. Catatan naskah: angka split final 2.372/679/338; metode proksi grup (frame_N per resolusi; timestamp per tanggal; union md5) perlu didokumentasikan di BAB 3/4. Log: `logs/group_split.log`, `logs/dataset_group_verify.log`. Log lama ber-header waktu pembuatan; sejak P3 semua log ber-stempel waktu per baris (konvensi awk di §13).
- **P3 ✅ SELESAI (13 Jul 15:58 – 15 Jul 19:15) — Grid search α,σ** 3×3 pada V8, 540 epoch (60×9) tanpa crash. **Pemenang:** α=1,0 σ=0,1 → mAP50-95(val)=0,6670 (titik interior grid, unggul juga di rata-rata marginal kedua sumbu). Pola final (dihitung ulang dari results.csv): ranking 1–3 = a1.0_s0.1 (0,6670) > a2.0_s0.2 (0,6581) > a2.0_s0.1 (0,6569); α=0,5 terlemah seragam (rank 6,8,9); interaksi diagonal σ\*-naik-seiring-α (0,5→0,05; 1,0→0,10; 2,0→0,20); rentang 0,0302. `dalw_best.json` otomatis tertulis. **Resolusi insiden sebelumnya:** (a) percobaan-1 path salah (settings.json) → perbaiki + relaunch `--project` ABSOLUT; (b) ✅ **BUG NMSFreeProbe** (de_parallel) diperbaiki 13 Jul 16:21 (unwrap_model, test_nmsfree.py U1–U5 LULUS); (c) **job terbukti selamat tutup VS Code** (proses OS tetap hidup ~41 jam, laju stabil ~5,7 mnt/epoch). Log: `logs/tune.log` (per-batch), ringkasan `hasil/grid_search.md`. Observasi: GPU_mem 9,3 GB spill shared memory (normal, no OOM).
- **P4 ✅ SELESAI (16 Jul; dikoreksi 16 Jul siang) — Rangkum grid.** α\*=1,0 σ\*=0,1 dilaporkan; sanity check lulus (keduanya di grid, titik interior). ⚠️ Versi pertama `hasil/grid_search.md` salah urutan ranking (rank 2–3 tertukar) & klaim pola keliru → **ditulis ulang penuh dari `results.csv`** (tabel 9 kombinasi + matriks marginal + epoch-terbaik 36–50 + interaksi diagonal). Dokumen final: `hasil/grid_search.md`.
- **Revisi pembimbing ✅ (16 Jul 11:35, sebelum P5)** — `Prompt_Claude_Code_Update.md` diimplementasikan penuh & diverifikasi diff byte-per-byte: (1) file baru `y26_complexity.py` (Tabel 3.7: parameter/GFLOPs/ukuran/VRAM latih+inferensi/waktu latih/FPS; callback + perakit tabel `eval_out/complexity.csv`); (2) `y26_stats.py` + `rank_biserial` (Pers. 3.15) di keluaran `wilcoxon_pair`; (3) `evaluate_all.py` kolom CSV + print r; (4) `train_ablation.py` pasang `ComplexityCallback` di `train_once`. Verifikasi: sintaks OK; r=+1,000 (konsisten) / r=+0,500 (campuran). Catatan: asersi W⁺=8/W⁻=2 di skrip verifikasi prompt keliru secara matematis (|d| kembar semua → peringkat rata-rata 2,5 → W⁺=7,5/W⁻=2,5; nilai r tetap +0,5 sesuai harapan) — kode mengikuti spesifikasi fungsi yang benar. Hasil P1–P4 TIDAK berubah; efek mulai P5 (complexity_train.json per varian) & P7 (kolom effect size).
- **P5 🔄 BERJALAN (mulai 16 Jul 2026 12:07) — Latih 8 varian (V1–V8)** berurutan (`--variant all`), α=1,0 σ=0,1 otomatis dari `dalw_best.json`, batch 16, maks 300 epoch + patience 50, seed 0, `--project` ABSOLUT. Pra-flight: GPU bebas + `test_smoke.py` T1–T4 LULUS pasca-revisi pembimbing (`logs/smoke_pre_p5.log`). V1 mulai 12:07:30, path simpan terverifikasi benar. Log: `logs/train_all.log`; batch & insiden dicatat di `hasil/catatan_run.md` (aturan A-12: OOM varian ber-P2 → ulang batch 8 SEMUA varian; AutoBatch dilarang; terputus → `--variant Vx --resume`). Estimasi total ±7–10 hari. Keluaran per varian: results.csv, nmsfree_probe.csv (probe sudah diperbaiki), complexity_train.json (revisi pembimbing), weights/{best,last}.pt. Observasi: 1 citra val "corrupt JPEG — restored" otomatis oleh ultralytics (benign). Pantau: `Get-Content logs\train_all.log -Wait -Tail 30 -Encoding UTF8` atau tempel Prompt 6.
- **Persiapan P8 ✅ (16 Jul 12:40)** — Kit anotasi manual oklusi siap: `make_oklusi_sample.py` → `anotasi_oklusi/` (200 crop val, blind, seimbang tier 100 no + 100 partial & kelas 34/56/55/55, deterministik; `anotasi.html` klik/keyboard → ekspor `manual_oklusi.csv` format persis `occlusion_agreement`). Naufal tinggal menganotasi (±20–30 mnt). ⚠️ **TEMUAN: tier heavy (o≥0,35) nyaris kosong** — val 0/4.094 (maks 0,286), test 8/2.600, train 62/16.786 → strata heavy akan gugur dari sel Wilcoxon di val; indikasi proksi box-IoU underestimate oklusi perseptual; ambang 0,10/0,35 TERKUNCI — keputusan (bila perlu) menunggu angka agreement + diskusi pembimbing. Bahan diskusi BAB 4.
- P6–P10 belum: monitor V1-V8 → evaluasi strata & Wilcoxon → analisis NMS-free (DR/CM/τ sweep) → validasi oklusi manual (kit siap, tinggal anotasi) → counting ByteTrack (RQ5) → konsolidasi BAB 4 hasil eksperimen.