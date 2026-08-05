# Hasil Eksperimen untuk BAB 4 & BAB 5

> **Status per 5 Agustus 2026.** Folder ini merangkum SEMUA data, tabel, dan visualisasi
> yang menjadi bahan penulisan BAB 4 (Hasil dan Pembahasan) dan BAB 5 (Kesimpulan dan
> Saran), diambil langsung dari sumber kebenaran (`eval_out/`, `nmsfree_out/`, `runs_tesis/`,
> `anotasi_oklusi/`, `dataset/`) — tidak ada angka yang diketik ulang secara manual.
> **Belum ada placeholder di naskah tesis yang diisi dan BAB 4–5 belum ditulis** — folder
> ini adalah *bahan mentah terorganisasi*, bukan draf bab.

## Cara memakai folder ini

Tiap subfolder `0N_<topik>/` punya `README.md` sendiri yang menjelaskan **setiap file**:
apa isinya, bagaimana dibaca, dan kalimat interpretasi yang bisa langsung diadaptasi untuk
naskah. Grafik disimpan sebagai `.png` siap tempel; tabel sebagai `.csv` siap diolah lebih
lanjut atau disalin ke Word/Excel.

| # | Folder | Menjawab | Status |
|---|---|---|---|
| 01 | [dataset](01_dataset/) | Subbab 3.3 — karakteristik & pembagian data | ✅ lengkap |
| 02 | [grid_search_dalw](02_grid_search_dalw/) | Subbab 3.9 — pencarian α, σ | ✅ lengkap |
| 03 | [kompleksitas_model](03_kompleksitas_model/) | Subbab 3.11.4 — Tabel 3.7 | ✅ lengkap |
| 04 | [ablasi_deteksi](04_ablasi_deteksi/) | RQ2, RQ4 — ablasi + Wilcoxon + bootstrap | ✅ lengkap |
| 05 | [analisis_nmsfree](05_analisis_nmsfree/) | RQ1, RQ3 — interaksi NMS-free | ✅ lengkap |
| 06 | [sensitivitas_alpha](06_sensitivitas_alpha/) | Subbab 3.9 — mitigasi keterbatasan grid satu-titik | ✅ lengkap |
| 07 | [ketegaran_normalisasi](07_ketegaran_normalisasi/) | Subbab 3.6.3 — pemeriksaan ketegaran | ✅ lengkap |
| 08 | [validasi_oklusi](08_validasi_oklusi/) | Subbab 3.3.3 — validasi proksi oklusi | ✅ lengkap |
| 09 | [counting_end_to_end](09_counting_end_to_end/) | RQ5 — penghitungan ByteTrack | ✅ hasil 3 klip (GT 1 penghitung — K7) |
| 10 | [multi_seed](10_multi_seed/) | Tabel 3.9 — validitas internal | ⏸️ menunggu keputusan K6 |

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
   penghitung independen + pelaporan tingkat kesesuaian awal (keputusan **K7** terbuka).
5. **Multi-seed (K6) belum dijalankan** — lihat folder 10.
6. **Grid search DALW dilakukan pada pelatihan dipersingkat (60 epoch)** pada satu varian
   (V8) — bukan pada kedelapan varian penuh (keterbatasan biaya komputasi, diakui naskah
   Subbab 3.9).

## Referensi cepat: sumber data mentah (jangan dihapus)

Folder ini adalah **turunan**. Sumber kebenaran tetap di lokasi asli:
`eval_out/`, `nmsfree_out/`, `runs_tesis/`, `anotasi_oklusi/`, `dataset/`, `video_uji/`,
`dalw_best.json`, `bukti_split_*.csv`. Bila sumber berubah (mis. setelah counting
selesai), jalankan ulang generator (lihat `hasil_bab4_5/CARA_REGENERASI.md`) untuk
menyegarkan folder ini.
