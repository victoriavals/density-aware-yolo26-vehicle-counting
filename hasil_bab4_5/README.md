# Hasil Eksperimen untuk BAB 4 & BAB 5

> **Status per 6 Agustus 2026.** Folder ini memuat SELURUH data, tabel, dan visualisasi
> hasil penelitian, diambil langsung dari sumber kebenaran (`eval_out/`, `nmsfree_out/`,
> `counting_out/`, `runs_tesis/`, `video_uji/`, `anotasi_oklusi/`, `dataset/`) — tidak ada
> angka yang diketik ulang secara manual.
>
> **BAB IV dan BAB V sudah ditulis** dan naskahnya ada di [`14_naskah/`](14_naskah/)
> (`TESIS_BAB4-5.docx`, 15 tabel, 24 gambar, 13 lampiran). Naskah tersebut dibangkitkan
> program dari data di folder ini, sehingga dapat dibangun ulang bila ada data yang berubah.
> Placeholder pada abstrak BAB 1–3 **belum diisi** karena menunggu penempelan manual ke
> naskah utama — redaksi siap tempelnya ada di [`K4_REDAKSI_HASIL.md`](K4_REDAKSI_HASIL.md).

## Cara memakai folder ini

> **Folder ini adalah satu-satunya tempat yang perlu dibuka.** Seluruh data dan
> visualisasi hasil penelitian sudah dikonsolidasikan ke sini (165 berkas, ±12 MB),
> termasuk data mentah yang tak dapat dibangkitkan ulang (folder `00_data_sumber/`)
> dan naskah jadinya (`14_naskah/`). Sumber aslinya di `eval_out/`, `nmsfree_out/`,
> `counting_out/`, `runs_tesis/`, dan `video_uji/` tetap ada dan tidak dihapus —
> folder ini turunan, bukan pengganti. Konsolidasi diulang otomatis lewat
> `konsolidasi_arsip()` pada `y26_bangun_hasil_bab45.py`.

Tiap subfolder `0N_<topik>/` punya `README.md` sendiri yang menjelaskan **setiap file**:
apa isinya, bagaimana dibaca, dan kalimat interpretasi yang bisa langsung diadaptasi untuk
naskah. Grafik disimpan sebagai `.png` siap tempel; tabel sebagai `.csv` siap diolah lebih
lanjut atau disalin ke Word/Excel.

| # | Folder | Menjawab | Status |
|---|---|---|---|
| 00 | [data_sumber](00_data_sumber/) | **Data mentah yang TIDAK dapat dibangkitkan ulang kode**: hitung manual 4 klip, konfigurasi garis maya, kit penghitung kedua, anotasi oklusi manual, bukti split, `dalw_best.json` | ✅ lengkap |
| 01 | [dataset](01_dataset/) | Subbab 3.3 — karakteristik & pembagian data | ✅ lengkap |
| 02 | [grid_search_dalw](02_grid_search_dalw/) | Subbab 3.9 — pencarian α, σ | ✅ lengkap |
| 03 | [kompleksitas_model](03_kompleksitas_model/) | Subbab 3.11.4 — Tabel 3.7 | ✅ lengkap |
| 04 | [ablasi_deteksi](04_ablasi_deteksi/) | RQ2, RQ4 — ablasi + Wilcoxon + bootstrap | ✅ lengkap |
| 05 | [analisis_nmsfree](05_analisis_nmsfree/) | RQ1, RQ3 — interaksi NMS-free | ✅ lengkap |
| 06 | [sensitivitas_alpha](06_sensitivitas_alpha/) | Subbab 3.9 — mitigasi keterbatasan grid satu-titik | ✅ lengkap |
| 07 | [ketegaran_normalisasi](07_ketegaran_normalisasi/) | Subbab 3.6.3 — pemeriksaan ketegaran | ✅ lengkap |
| 08 | [validasi_oklusi](08_validasi_oklusi/) | Subbab 3.3.3 — validasi proksi oklusi | ✅ lengkap |
| 09 | [counting_end_to_end](09_counting_end_to_end/) | RQ5 — penghitungan ByteTrack | ✅ hasil 3 klip (GT 1 penghitung — K7) |
| 10 | [multi_seed](10_multi_seed/) | Tabel 3.9 — validitas internal | ✅ **K6: tidak dijalankan** — kalimat keterbatasan siap pakai |
| 11 | [analisis_galat](11_analisis_galat/) | Subbab 4.11 — matriks kekeliruan uji, FP/FN per strata, kasus gagal | ✅ **baru 5 Agu 2026** |
| 12 | [kurva_pelatihan](12_kurva_pelatihan/) | Kurva pelatihan, `results.csv`, probe NMS-free per epoch, dan catatan kompleksitas untuk **11 run** (V1–V8, V4_a0.5, V4_a2.0, V8_normw) | ✅ lengkap |
| 13 | [ringkasan_naratif](13_ringkasan_naratif/) | Ringkasan naratif per tahap: grid search, catatan run, evaluasi, validasi oklusi | ✅ lengkap |
| 14 | [naskah](14_naskah/) | **`TESIS_BAB4-5.docx`** — naskah BAB IV & V beserta 13 lampiran | ✅ lengkap |

---

## Peta Rumusan Masalah (RQ1–RQ5) → Bukti

Ini jawaban langsung atas permintaan "semua yang di BAB 1–3 terjawab dengan jelas" —
setiap rumusan masalah (CLAUDE.md §2 / BAB 1 Subbab 1.2) dipetakan ke file pembuktiannya.

### RQ1 — Merancang modifikasi YOLO26 (HAM+P2+DALW) yang kompatibel dengan paradigma NMS-free

**Terjawab.** Kompatibilitas dibuktikan karena kedelapan varian **berhasil dilatih dan
menghasilkan prediksi one-to-one yang valid** (tak ada satupun varian gagal/divergen).
Buktinya tersebar di:
- `03_kompleksitas_model/tabel_kompleksitas.csv` — kedelapan varian punya jumlah parameter,
  GFLOPs, dan kebutuhan VRAM yang tercatat wajar (8,5–8,6 GB pada varian ber-P2, sesuai
  budget GPU 8GB Batasan 1.6).
- `05_analisis_nmsfree/summary.csv` + `grafik_dr_cm_ringkasan.png` — Duplicate Rate dan
  Confidence Margin varian ber-P2 (V3/V5/V7/V8) tetap terukur dan masuk akal (DR 0,72–0,83,
  bukan longsor ke nol atau meledak) → mekanisme one-to-one tetap berfungsi walau P2
  menambah kepadatan prediksi 4×.

### RQ2 — Kontribusi setiap komponen via *ablation study*

**Terjawab lengkap dengan nuansa penting.** Lihat `04_ablasi_deteksi/`:
- `global_metrics.csv` + `grafik_map_per_varian.png` — metrik global kedelapan varian.
- `wilcoxon_ap5095.csv` (kolom `family=primary`) + `grafik_wilcoxon_hipotesis_utama.png` —
  **tiga hipotesis utama**:
  - **H1 (V8 vs V1)**: p=0,565, **tidak signifikan** menurut Wilcoxon per-sel, TAPI
    `bootstrap_ci.csv` menunjukkan selang selisih mAP agregat **tidak memuat nol**
    (+0,05 hingga +2,08 poin persen) — dua uji mengukur hal berbeda (median lintas sel
    heterogen vs selisih agregat antar-citra); **laporkan keduanya**, jangan pilih yang
    menguntungkan.
  - **H2 (V4 vs V1, DALW berdiri sendiri)**: p=0,208, **tidak didukung** (p besar, bukan
    nyaris signifikan). Ini **konsisten dengan ramalan BAB 2** (baseline YOLO26 sudah
    ber-STAL sadar-ukuran → ruang perbaikan lebih sempit dari CRL/MST/HIC-YOLOv5).
  - **H3 (V8 vs V5, DALW komplementer di atas HAM+P2)**: p=0,037, **SIGNIFIKAN**,
    r=+0,487 (efek sedang), dan bootstrap CI [+1,26; +3,53] poin persen — **temuan
    paling kokoh**, dikonfirmasi dua metode independen.
- `grafik_strata_size.png`, `_occlusion.png`, `_density.png` — strata mana yang paling
  terbantu (lihat kontras V8−V5): objek kecil, oklusi parsial, dan densitas sparse.
- 12 sel dikeluarkan dari uji (aturan `min_n_gt=30`, Subbab 3.11.5) — lihat kolom
  `sel_dibuang` di `wilcoxon_ap5095.csv`.

### RQ3 — Pengaruh P2 & HAM terhadap kestabilan pencocokan *one-to-one*

**Terjawab.** Lihat `05_analisis_nmsfree/`:
- `grafik_stabilitas_assignment.png` — S(t) (Pers. 3.8) per epoch, kelima varian ber-P2
  vs baseline. Konvergen ke ~1,0 di akhir pelatihan untuk semua varian.
- `grafik_dr_cm_ringkasan.png` — **HAM tampak menstabilkan margin**: V5 & V8 (ber-HAM)
  naik CM dibanding V1, sedangkan V3 & V7 (P2 tanpa HAM) justru turun.
- `grafik_tau_sweep_ulang.png` + `dr_vs_tau.png` — sensitivitas ambang τ, perilaku
  monoton sehat di seluruh varian (bukti tak ada anomali pencocokan).

### RQ4 — Performa terstratifikasi (ukuran × oklusi × densitas)

**Terjawab**, lihat `04_ablasi_deteksi/strata_ap.csv` (sumber lengkap) dan tiga grafik
`grafik_strata_*.png`. Catatan penting: strata **oklusi-heavy nyaris tak berisi objek**
(dikonfirmasi independen oleh `08_validasi_oklusi/` — proksi tak pernah membentuk tier
heavy) sehingga performa pada oklusi berat **tidak dapat disimpulkan** dari data ini;
harus dinyatakan sebagai keterbatasan, bukan disembunyikan.

### RQ5 — Akurasi *end-to-end* dengan ByteTrack terhadap standar penerapan praktis

**✅ Terjawab.** Counting penuh 10 menit dijalankan pada **3 klip** (2, 3, 4) dengan konvensi
arah yang sudah diselaraskan — lihat `09_counting_end_to_end/`.

| Klip | Karakter | MAE | MAPE | Selisih agregat |
|---|---|---|---|---|
| 2_vidiouji | lengang | 0,717 | 39,28 % | −31,9 % |
| 3_vidiouji | arteri | 1,050 | **26,78 %** | **−12,5 %** |
| 4_vidiouji | ramai | 4,150 | 54,33 % | −26,5 % |
| **GABUNGAN** | 180 pengamatan | **1,972** | **37,17 %** | **−23,9 %** |

**FPS pipeline end-to-end = 20,47 rata-rata** (19,2–21,4) — inilah angka untuk placeholder
abstrak *"[XX] frame per detik"*, **BUKAN** 23,3 FPS model murni di `03_kompleksitas_model/`.

**Temuan layak dibahas:** MAE naik seiring kepadatan (0,72 → 1,05 → 4,15), sejalan dugaan
bahwa oklusi & pergantian identitas menyulitkan pelacakan pada kondisi padat.

**Dua koreksi metodologis yang diterapkan** (rincian di README folder 09):
1. **Konvensi arah in/out diselaraskan** — sistem awalnya terbalik dari definisi penghitung
   manual; setelah dikoreksi MAPE klip 3 turun 54,79 % → 26,78 %.
2. **Klip 1 dikecualikan** — segmen garisnya tak menjangkau lajur mobil sehingga GT dan
   sistem mengukur populasi berbeda (cacat validitas pengukuran, bukan performa model).
   ⚠️ **Wajib dinyatakan eksplisit di BAB 4/5.**

**Masih terbuka:** GT dari satu penghitung (protokol 3.10.1 menuntut dua — **K7**) dan
ambang lulus RQ5 (**A-02/K5**) belum ditetapkan pembimbing.

---

## Keterbatasan yang WAJIB dinyatakan eksplisit di BAB 4/5

Daftar ini bukan kegagalan — ini kejujuran ilmiah yang justru memperkuat kredibilitas hasil:

1. **Strata oklusi-heavy nyaris kosong** (val 0/4.094 objek, test 4/2.600 pada ambang
   0,40) — proksi box-IoU terbukti meremehkan oklusi perseptual (kesesuaian manual hanya
   68,0%, lihat folder 08). Kesimpulan pada oklusi berat tidak dapat ditarik.
2. **H2 (DALW berdiri sendiri) tidak didukung secara statistik** — DALW baru signifikan
   sebagai kontribusi komplementer di atas HAM+P2 (H3), bukan mandiri.
3. **Sensitivitas α** (folder 06) menunjukkan nilai optimal untuk V4 (α=2,0) berbeda dari
   nilai yang dipilih grid search pada V8 (α=1,0) — mengonfirmasi keterbatasan yang sudah
   diakui naskah (Subbab 3.9): pencarian satu-titik pada varian lengkap tidak menjamin
   optimal untuk varian lain.
4. **Data uji counting hanya mencakup tier sparse & medium** (tidak ada interval tier
   dense >25 objek/frame) — keterbatasan lokasi CCTV yang terjangkau (keputusan K7).
4b. **Satu klip (1_vidiouji) dikecualikan dari evaluasi RQ5** karena segmen garis virtualnya
   tidak menjangkau lajur yang dipakai mobil, sehingga hitung manual dan keluaran sistem
   mengukur populasi kendaraan yang berbeda (0 mobil sistem vs 20 manual). **Alasan ini
   wajib ditulis apa adanya** — pengecualian data setelah hasil terlihat berpotensi dianggap
   penyaringan hasil bila tidak dijelaskan sebagai cacat penyiapan pengukuran. Evaluasi
   akhir memakai 3 klip / 180 pengamatan (protokol 3.10.1 tetap terpenuhi: ≥3 klip,
   masing-masing ≥10 menit, titik pengamatan berbeda).
4c. **GT counting berasal dari satu penghitung**, sedangkan Subbab 3.10.1 menjanjikan dua
   penghitung independen + pelaporan tingkat kesesuaian awal (keputusan **K7b** terbuka).
   Kit penghitung kedua **sudah siap pakai** di `video_uji/penghitung_kedua/` — protokol,
   cadangan, dan redaksi revisi 3.10.1 ada di [K7_PENGHITUNG_KEDUA.md](K7_PENGHITUNG_KEDUA.md).
5. **Multi-seed (K6) TIDAK dijalankan** — keputusan sadar 5 Agu 2026 karena anggaran waktu
   (≈49 jam GPU tambahan); naskah Tabel 3.9 mengizinkan dengan syarat dinyatakan eksplisit.
   Kalimat siap-pakai untuk BAB IV & V ada di `10_multi_seed/README.md`. **Paling relevan
   untuk H1 & H2** yang selisihnya kecil — sebutkan berdampingan dengan pembahasan keduanya,
   jangan disembunyikan di akhir bab.
6. **Grid search DALW dilakukan pada pelatihan dipersingkat (60 epoch)** pada satu varian
   (V8) — bukan pada kedelapan varian penuh (keterbatasan biaya komputasi, diakui naskah
   Subbab 3.9).
7. **Strata kepadatan ekstrem (*dense*) tidak dapat dinilai pada data uji deteksi.** Setelah
   aturan sel minimum `MIN_CELL_GT=30` diterapkan, satu-satunya kelas yang lolos pada strata
   ini adalah **pejalan kaki** (n=77) — kelas konteks yang justru dikecualikan dari
   penghitungan; kelas kendaraan hanya bervolume 1, 11, dan 21 objek. Ini **manifestasi kedua**
   dari keterbatasan yang sama dengan butir 4 (tier *dense* juga tak terwakili di klip
   counting). Karena BAB 1 menjadikan kepadatan >25 objek/frame sebagai salah satu dari tiga
   tantangan utama, keterbatasan ini wajib disebut terbuka. Bukti:
   `04_ablasi_deteksi/delta_strata.csv`.
8. **Tidak ada varian yang memenuhi kriteria *real-time* ≥30 FPS** ketika pelacakan dan
   kepadatan nyata diperhitungkan (V8 19,29 FPS; V4_a2.0 23,20; V1 23,28 pada klip terpadat —
   `counting_out/fps_probe/`). Judul tesis memuat kata *real-time*, sehingga ini wajib dijawab
   terbuka, bukan didiamkan. Rincian & redaksi: [K5_AMBANG_RQ5.md](K5_AMBANG_RQ5.md).
9. **Sekitar 59,5 % defisit penghitungan berasal dari dua sel klip 4** (mobil −170,
   kendaraan besar −21) yang berpola sama dengan cacat geometri garis pada klip 1. Angka
   agregat −23,9 % karena itu **bukan** murni akurasi deteksi/pelacakan, melainkan akurasi
   sistem beserta penempatan garisnya. Pelaporan per kelas wajib.

## Tiga dokumen keputusan (K4, K5, K7) — baca sebelum menulis BAB 4

| Dokumen | Isi | Status |
|---|---|---|
| [K4_REDAKSI_HASIL.md](K4_REDAKSI_HASIL.md) | Definisi "konfigurasi terbaik", aturan pelaporan 3 hipotesis, **abstrak ditulis ulang (ID+EN) siap tempel**, daftar frasa terlarang | usulan — perlu ACC pembimbing |
| [K5_AMBANG_RQ5.md](K5_AMBANG_RQ5.md) | Tiga ambang literatur nyata (Lewis 1982, FHWA TMG, literatur CV), kriteria FPS a-priori, dekomposisi defisit, redaksi RQ5 deskriptif | usulan — perlu ACC pembimbing |
| [K7_PENGHITUNG_KEDUA.md](K7_PENGHITUNG_KEDUA.md) | Protokol penghitung kedua + kit siap pakai, cadangan *test-retest*, redaksi revisi Subbab 3.10.1 | kit siap — tinggal dijalankan |

## Kelengkapan bahan per subbab BAB 4

| Subbab | Bahan | Status |
|---|---|---|
| 4.1 Dataset & distribusi kelas | `01_dataset/` | ✅ |
| 4.2 Inisialisasi & transfer bobot | `logs/smoke.log` | ✅ |
| 4.3 Grid search α,σ | `02_grid_search_dalw/` | ✅ |
| 4.4 Metrik global per varian | `04_ablasi_deteksi/global_metrics.csv` | ✅ |
| 4.5 Ablasi terstratifikasi + Wilcoxon | `04_ablasi_deteksi/` (+ `delta_strata.csv`) | ✅ |
| 4.6 Sensitivitas α + ketegaran | `06_`, `07_` | ✅ |
| 4.7 Kompleksitas & efisiensi | `03_kompleksitas_model/` | ✅ |
| 4.8 Analisis NMS-free (DR/CM/τ/S(t)) | `05_analisis_nmsfree/` | ✅ |
| 4.9 Validasi proksi oklusi | `08_validasi_oklusi/` | ✅ |
| 4.10 Penghitungan end-to-end | `09_counting_end_to_end/` | ✅ |
| **4.11 Analisis galat** | **`11_analisis_galat/`** | ✅ **baru (5 Agu 2026)** |
| Keterbatasan multi-seed | `10_multi_seed/` | ✅ (kalimat siap pakai) |

## Referensi cepat: sumber data mentah (jangan dihapus)

Folder ini adalah **turunan**. Sumber kebenaran tetap di lokasi asli:
`eval_out/`, `nmsfree_out/`, `runs_tesis/`, `anotasi_oklusi/`, `dataset/`, `video_uji/`,
`dalw_best.json`, `bukti_split_*.csv`. Bila sumber berubah (mis. setelah counting
selesai), jalankan ulang generator (lihat `hasil_bab4_5/CARA_REGENERASI.md`) untuk
menyegarkan folder ini.
