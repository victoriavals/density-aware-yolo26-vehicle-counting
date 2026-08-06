# K4 / A-01 — Redaksi Hasil & Abstrak yang Ditulis Ulang

> Disusun 5 Agustus 2026. **Status: USULAN — menunggu persetujuan Naufal + Ibu Sandfreni.**
> Naskah `.docx` TIDAK disunting oleh berkas ini. Seluruh angka dibaca dari
> `eval_out/global_metrics.csv`, `eval_out/wilcoxon_ap5095.csv`, `eval_out/bootstrap_ci.csv`,
> `eval_out_fase2/global_metrics.csv`, `counting_out/`, dan `runs_tesis/*/results.csv`.

---

## 1. Keputusan pertama: definisi "konfigurasi terbaik"

Frasa "konfigurasi terbaik" pada abstrak v7 tidak terdefinisi, dan itulah sumber
kekacauannya. Ada tiga kandidat, dan pilihan di antara mereka menentukan seluruh isi kalimat.

| Kandidat | Dasar klaim | mAP@0,5 | mAP@0,5:0,95 | Masalah metodologis |
|---|---|---|---|---|
| **V8** (model penuh) | konfigurasi yang **diusulkan** tesis; **tertinggi** mAP@0,5:0,95 di antara 8 varian ablasi | 77,97 % | **53,75 %** | tidak ada |
| V1 (baseline) | mAP@0,5 tertinggi dari seluruh varian | **78,61 %** | 53,56 % | ini *baseline*, bukan usulan |
| V4_a2.0 (DALW, α=2,0) | mAP@0,5:0,95 tertinggi dari semua *run* | 77,18 % | **54,96 %** | α ≠ 1,0 → di luar desain ablasi; memilihnya berdasar skor **test** = seleksi pada data uji |

**Keputusan yang disarankan: hapus kata "terbaik", ganti menjadi "konfigurasi penuh yang
diusulkan (V8)".**

Alasannya tiga lapis:

1. **Menghindari seleksi pada data uji.** V4_a2.0 memang mencatat mAP@0,5:0,95 tertinggi
   (54,96 %), tetapi ia berasal dari eksperimen *sensitivitas* α, bukan dari delapan varian
   yang telah diregistrasi di Tabel 3.3. Menobatkannya "terbaik" berarti memilih konfigurasi
   berdasarkan performa *test-split* — persis yang dihindari seluruh rancangan BAB 3.
2. **Peringkat validasi tidak stabil, jadi tidak ada dasar menobatkan pemenang.** Pada
   *split* validasi, urutan teratas adalah V2 (0,6528), V4_a2.0 (0,6523), V5 (0,6516),
   V3 (0,6505), baru V8 (0,6457) — selisih empat teratas hanya 0,0025. Sementara pada *test*,
   V2 justru turun ke peringkat empat (53,04 %). Tanpa pengulangan multi-*seed* (keputusan
   **K6**: tidak dijalankan), selisih sekecil itu **tidak dapat dibedakan dari fluktuasi
   inisialisasi**. Menobatkan "terbaik" atas selisih < 0,5 poin persen adalah klaim yang tidak
   dapat dipertahankan di sidang.
3. **Kebetulan menguntungkan: V8 tetap unggul pada metrik utama.** Di antara delapan varian
   ablasi (α dibekukan 1,0), V8 **memang** tertinggi pada mAP@0,5:0,95 test (53,75 %). Jadi
   menyebut V8 sebagai konfigurasi yang dilaporkan bukan kompromi — ia sekaligus pemenang
   metrik utama dalam desain yang telah diregistrasi.

**Efek samping yang penting:** dengan definisi ini, konfigurasi yang dilaporkan di abstrak
sama dengan konfigurasi yang dipakai pada penghitungan *end-to-end* (bobot V8). Konsistensi
internal abstrak terjaga tanpa perlu menjalankan ulang eksperimen penghitungan.

---

## 2. Tiga aturan pelaporan hipotesis

### Aturan 1 — Laporkan H1, H2, dan H3 dengan bobot setara

| Hipotesis | p (Wilcoxon) | r (rank-biserial) | Selang bootstrap 95 % | Kesimpulan yang sah |
|---|---|---|---|---|
| H1: V8 − V1 | 0,565 | +0,140 | [+0,05; +2,08] pp | Wilcoxon **tidak signifikan**; bootstrap tak memuat nol |
| H2: V4 − V1 | 0,208 | **−0,300** | [−1,21; +1,00] pp | **tidak didukung** |
| **H3: V8 − V5** | **0,0367** | **+0,487** | **[+1,26; +3,53] pp** | **signifikan** |

Menyembunyikan H1/H2 dan hanya menonjolkan H3 adalah *cherry-picking* yang mudah dibongkar:
ketiganya sudah dideklarasikan sebagai hipotesis utama di Subbab 3.11.4, sehingga penguji
berhak menanyakan ketiganya.

### Aturan 2 — H2 dilarang disebut "kecenderungan positif"

Nilai p = 0,208 disertai ukuran efek **negatif** (r = −0,300) dan median selisih −0,0133.
Menarasikannya sebagai "belum signifikan tetapi menunjukkan kecenderungan positif" adalah
kesalahan interpretasi yang dapat dibantah hanya dengan menunjuk tanda median. Rumusan yang
benar: DALW **tanpa dukungan arsitektur tidak memberi perbaikan** pada AP terstratifikasi.

### Aturan 3 — Pada H1, laporkan Wilcoxon **dan** bootstrap sekaligus

Keduanya menjawab pertanyaan berbeda dan kebetulan berbeda arah:

- **Wilcoxon** menguji *konsistensi tanda* selisih antar-sel (kelas × strata). p = 0,565
  berarti perbaikan tidak konsisten arah — sebagian sel naik, sebagian turun.
- **Bootstrap tataran citra** menguji *besar efek agregat*. Selang [+0,05; +2,08] pp tidak
  memuat nol, tetapi batas bawahnya **+0,05 pp** — praktis menyentuh nol.

Rumusan jujur: perbaikan agregat V8 atas V1 kecil dan tidak konsisten antar-strata. Memilih
salah satu uji yang menguntungkan = melanggar janji Subbab 3.11.5 yang menjanjikan keduanya.

---

## 3. Klaim tesis yang bertahan — dan dasar teoretisnya

Klaim yang didukung data adalah **H3**: Pembobotan *Loss* Berbasis Densitas memberi
kontribusi inkremental yang signifikan **di atas** fondasi HAM + P2 (p = 0,0367, r = +0,487,
selang [+1,26; +3,53] pp), namun **tidak berdiri sendiri** (H2 tidak didukung).

Ini bukan penyelamatan *post-hoc* — ini persis framing dua pilar yang sudah ditulis di
BAB 1 dan BAB 3: DALW **melengkapi** mekanisme bawaan YOLO26, bukan menggantikannya.

**BAB 2 sudah menyediakan penjelasan teoretis hasil null — pakai, jangan minta maaf.**
Subbab 2.3.5 mencatat YOLO26 sudah memuat ProgLoss dan STAL, artinya *baseline* yang
dilawan sudah menangani ketidakseimbangan berbasis ukuran. Ruang perbaikan yang tersisa
karena itu sempit secara struktural. Bandingkan dengan Tabel 2.1: HIC-YOLOv5 (+6,42 %) dan
MST-YOLO (+8,42 %) melaporkan kenaikan besar, tetapi keduanya diukur atas *baseline*
**NMS-based** tanpa mekanisme penetapan label adaptif. Selisih magnitudo itu adalah temuan,
bukan kelemahan.

Dua hasil ketegaran memperkuat bahwa H3 bukan artefak:

- **Ketegaran normalisasi** (`07_ketegaran_normalisasi/`): V8_normw 53,62 % vs V8 53,75 %,
  p = 0,944 → perolehan DALW **bukan** efek skala *loss*.
- **Sensitivitas α** (`06_sensitivitas_alpha/`): mekanisme responsif terhadap α secara
  monoton pada V4 (0,5400 → 0,5366 → 0,5496 test; pada val 0,6313 → 0,6356 → 0,6523),
  menunjukkan bobot densitas benar-benar bekerja, sekaligus mengonfirmasi keterbatasan
  *grid search* satu titik yang sudah diakui Subbab 3.9.

### Temuan tambahan yang layak ditonjolkan: DALW gratis saat inferensi

Dari `03_kompleksitas_model/tabel_kompleksitas.csv`: V4 dan V1 memiliki parameter
(9,951 M), GFLOPs (22,51), dan ukuran model (19,38 MB) yang **identik**. DALW hanya menyentuh
penghitungan *loss* saat pelatihan sehingga **biaya inferensinya nol secara struktural** —
bukan sekadar kecil, tetapi nol, karena grafik komputasi inferensinya sama persis dengan
*baseline*. Sebaliknya varian ber-P2 membayar *head* beresolusi stride-4.

⚠️ **Jangan campur dua konteks pengukuran kecepatan.** Tabel 3.7 melaporkan FPS **model
murni pada tolok ukur standar** (V1 32,39; V4 30,51; V8 23,31). Angka itu **bukan** kecepatan
sistem. Pengukuran menyeluruh pada video terpadat (`counting_out/fps_probe/`, 1.800 bingkai
klip 4, ByteTrack + *line crossing* aktif) memberi angka yang jauh lebih rendah:

| Varian | FPS model (tolok ukur) | FPS model (klip padat) | **FPS pipeline (klip padat)** | Rasio thd sumber 30 FPS |
|---|---|---|---|---|
| V1 | 32,39 | 28,35 | 23,28 | 0,78× |
| V4_a2.0 | 30,51 | 28,53 | **23,20** | 0,77× |
| V8 | 23,31 | 22,79 | **19,29** | 0,64× |

Jadi klaim "konfigurasi DALW-saja mencapai ≥30 FPS" **tidak didukung** begitu pelacakan dan
kepadatan nyata diperhitungkan. Yang **didukung**: konfigurasi DALW-saja berjalan sekitar
**20 persen lebih cepat** daripada model penuh (23,20 vs 19,29 FPS pipeline) tanpa mengorbankan
mAP@0,5:0,95. Itu tetap temuan praktis yang layak masuk BAB 5 — tetapi sebagai *trade-off*
kecepatan–akurasi, bukan sebagai klaim *real-time* 30 FPS. Rincian: [K5](K5_AMBANG_RQ5.md).

---

## 3b. 🚨 Temuan kedua: klaim strata "+5,1 pp objek kecil, +3,3 pp kepadatan tinggi" TIDAK SAH

Angka ini sempat tercatat di [peta placeholder](PETA_PLACEHOLDER_ABSTRAK.md) versi pertama.
Angka tersebut dihitung dengan **merata-ratakan seluruh sel**, termasuk sel bervolume 1–27
objek — padahal sel semacam itu justru yang dikeluarkan aturan sel minimum
`MIN_CELL_GT = 30` (Subbab 3.11.5) dari uji signifikansi. Memakai satu aturan untuk uji
statistik dan aturan berbeda untuk narasi adalah inkonsistensi yang fatal bila ditanyakan
penguji.

Setelah aturan yang sama diterapkan (sumber baru: `04_ablasi_deteksi/delta_strata.csv`,
dibangkitkan `y26_bangun_hasil_bab45.py` agar tak diketik manual):

| Strata | V8−V1 semua sel | V8−V1 sel n_gt≥30 | V8−V5 sel n_gt≥30 | Layak dinarasikan? |
|---|---|---|---|---|
| oklusi parsial | +0,56 pp | **+3,72 pp** | **+5,37 pp** | ✅ 3 kelas |
| ukuran kecil | +5,06 pp | **+0,87 pp** | **+3,02 pp** | ✅ 3 kelas |
| oklusi tanpa | +1,11 pp | +1,11 pp | +2,32 pp | ✅ 4 kelas |
| densitas *dense* | +3,28 pp | −1,31 pp | −6,61 pp | ❌ hanya pejalan kaki |
| oklusi *heavy* | −8,79 pp | — | — | ❌ semua sel < 30 GT |

Dua konsekuensi:

1. **"+5,1 pp objek kecil" turun menjadi +0,87 pp** untuk V8−V1 (angka besar itu berasal dari
   sel *big-vehicle* n=17 yang naik +17,64 pp). Untuk V8−V5 angkanya +3,02 pp — masih layak.
2. **Klaim kepadatan tinggi GUGUR seluruhnya.** Pada strata *dense* di data uji, satu-satunya
   kelas yang melewati ambang 30 objek adalah **pejalan kaki** (n = 77) — kelas konteks yang
   justru **dikecualikan dari penghitungan**. Kelas kendaraan hanya bervolume 1 (*big-vehicle*),
   11 (*car*), dan 21 (*two-wheeler*). Tanda positif +3,28 pp sepenuhnya berasal dari sel-sel
   itu.

Ini adalah manifestasi **kedua** dari keterbatasan yang sama yang sudah dicatat pada
penghitungan (tier *dense* per interval tak terwakili di klip uji): **data uji tesis ini tidak
memuat cukup objek kendaraan pada kondisi kepadatan ekstrem untuk mendukung klaim apa pun di
strata tersebut.** Karena BAB 1 menjadikan kepadatan >25 objek/frame sebagai salah satu dari
tiga tantangan utama, keterbatasan ini **wajib dinyatakan eksplisit**, bukan didiamkan.

Yang masih bisa diklaim dan justru cocok dengan premis BAB 1: perbaikan terkuat berada pada
**oklusi parsial** dan **objek berukuran kecil** — dua dari tiga tantangan yang disebut BAB 1.

---

## 4. Usulan redaksi abstrak (Indonesia) — bagian hasil

> Naskah lama (TIDAK BISA DIISI):
> *"…konfigurasi terbaik mencapai mAP@0,5 sebesar [XX,X] persen dan mAP@0,5:0,95 sebesar
> [XX,X] persen, meningkat [X,X] poin persentase dibandingkan baseline YOLO26 standar dengan
> perbedaan yang signifikan secara statistik (p = [0,0XX])."*

**Usulan pengganti** (prosa murni, tanpa *bullet*, desimal koma, istilah asing miring —
sesuai Standar Penulisan §11):

> Konfigurasi penuh yang diusulkan mencapai mAP@0,5 sebesar 77,97 persen dan mAP@0,5:0,95
> sebesar 53,75 persen pada *split* uji, dengan selisih terhadap *baseline* YOLO26 standar
> sebesar 0,19 poin persentase pada mAP@0,5:0,95 yang tidak terbukti signifikan secara
> statistik (p = 0,565). Sebaliknya, kontribusi inkremental pembobotan *loss* berbasis
> densitas di atas kombinasi atensi hibrida dan lapisan P2 terbukti signifikan dengan
> p = 0,037 dan ukuran efek *rank-biserial* sebesar 0,487, disertai selang kepercayaan
> *bootstrap* 95 persen antara 1,26 dan 3,53 poin persentase. Kontribusi tersebut
> terkonsentrasi pada strata oklusi parsial sebesar 5,4 poin persentase dan strata objek
> berukuran kecil sebesar 3,0 poin persentase, sedangkan strata kepadatan ekstrem tidak dapat
> dinilai karena jumlah objek kendaraan pada strata tersebut di data uji berada di bawah
> ambang minimum tiga puluh objek. Temuan ini menunjukkan bahwa pembobotan *loss* berbasis
> densitas bersifat komplementer terhadap modifikasi arsitektural dan tidak memberi
> perbaikan ketika diterapkan tanpa dukungan tersebut.

Kalimat penghitungan (placeholder 6–9) tetap dapat diisi apa adanya:

> Integrasi dengan pelacak ByteTrack menghasilkan *mean absolute error* sebesar 1,97,
> *root mean square error* sebesar 4,95, dan *mean absolute percentage error* sebesar
> 37,17 persen pada interval yang bernilai positif, yaitu 112 dari 180 pengamatan, dengan
> kecepatan pemrosesan menyeluruh sebesar 20 bingkai per detik.

**Perubahan struktural yang dituntut:** kalimat hasil yang semula satu klaim tunggal menjadi
tiga kalimat (hasil global, hasil hipotesis inkremental, hasil strata). Ini menambah panjang
abstrak sekitar 55 kata, sehingga **B-01 (batas ±360 kata) wajib diperiksa ulang setelah
penulisan ulang**, bukan sebelum.

## 5. Usulan redaksi ABSTRACT (Inggris) — bagian hasil

> The proposed full configuration attained a mAP@0.5 of 77.97 percent and a mAP@0.5:0.95 of
> 53.75 percent on the test split, differing from the standard YOLO26 baseline by 0.19
> percentage points on mAP@0.5:0.95, a difference that was not statistically significant
> (p = 0.565). In contrast, the incremental contribution of density-aware loss weighting on
> top of the hybrid attention module and the P2 layer was significant, with p = 0.037, a
> rank-biserial effect size of 0.487, and a 95 percent bootstrap confidence interval ranging
> from 1.26 to 3.53 percentage points. This contribution was concentrated in the
> partial-occlusion stratum at 5.4 percentage points and the small-object stratum at 3.0
> percentage points, whereas the extreme-density stratum could not be assessed because the
> number of vehicle objects it contains in the test split falls below the minimum threshold of
> thirty objects. These findings indicate that density-aware loss weighting is complementary to
> the architectural modifications and yields no improvement when applied without them.

> Integration with the ByteTrack tracker yielded a mean absolute error of 1.97, a root mean
> square error of 4.95, and a mean absolute percentage error of 37.17 percent over
> positive-valued intervals, namely 112 of 180 observations, at an end-to-end processing
> speed of 20 frames per second.

---

## 6. Daftar frasa yang DILARANG muncul di BAB 4/5

| Frasa terlarang | Kenapa | Ganti dengan |
|---|---|---|
| "meningkat signifikan dibandingkan *baseline*" | H1 p = 0,565 | "selisih 0,19 poin persentase yang tidak signifikan" |
| "menunjukkan kecenderungan positif" (untuk H2) | r = −0,300, median −0,0133 | "tidak memberi perbaikan" |
| "konfigurasi terbaik" tanpa definisi | tiga kandidat berbeda | "konfigurasi penuh yang diusulkan (V8)" |
| "mencapai 23,3 bingkai per detik" (klaim sistem) | itu `fps_model`, bukan pipeline | "20,47 bingkai per detik (`fps_pipeline`)" |
| "unggul pada seluruh metrik" | V8 lebih rendah pada P (−1,38), R (−0,49), F1 (−0,87), mAP@0,5 (−0,64) | sebutkan per metrik apa adanya |
| "hampir signifikan" / "marginally significant" | p = 0,208 bukan ambang batas | "tidak didukung" |

---

## 7. Yang masih butuh keputusan manusia

1. **Persetujuan definisi "konfigurasi penuh yang diusulkan (V8)"** — Naufal + pembimbing.
2. **Persetujuan bentuk kalimat** di §4 dan §5 sebelum ditempel ke `.docx`.
3. **B-01** — hitung ulang panjang ABSTRAK/ABSTRACT setelah penempelan.
4. Apakah temuan V4_a2.0 (54,96 %) dinaikkan ke abstrak sebagai kalimat terpisah, atau cukup
   di BAB 4 Subbab sensitivitas. **Saran: cukup di BAB 4** — menaikkannya ke abstrak
   mengundang pertanyaan mengapa α tidak diubah untuk seluruh ablasi, sedangkan jawabannya
   (keadilan perbandingan) butuh ruang penjelasan yang tidak tersedia di abstrak.

Tautan: [peta placeholder](PETA_PLACEHOLDER_ABSTRAK.md) · [ambang RQ5 (K5)](K5_AMBANG_RQ5.md) ·
[penghitung kedua (K7)](K7_PENGHITUNG_KEDUA.md) · [ablasi](04_ablasi_deteksi/) ·
[kompleksitas](03_kompleksitas_model/)
