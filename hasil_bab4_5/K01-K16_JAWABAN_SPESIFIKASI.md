# Jawaban K-01 … K-16 — pertanyaan spesifikasi naskah artikel

Dijawab 13 Agu 2026. **Setiap angka di bawah ditarik dari kode/artefak, bukan ingatan**;
lokasi sumbernya dicantumkan agar dapat diperiksa ulang. Butir yang merupakan
**keputusan** (bukan fakta) ditandai 🔸 dan menunggu Naufal/pembimbing (aturan §12.6).

---

## Ringkasan status

| Butir | Status | Inti |
|---|---|---|
| K-01 | ✅ terjawab | `max_memory_allocated` (**tanpa** cache alokator); spek 8 GB benar; >8 GB karena limpahan memori bersama Windows |
| K-02 | ✅ terjawab | Definisi ADA — beda ambang: cakupan bebas-τ vs τ=0,25. **Jalan B tidak perlu** |
| K-03 | ✅ terjawab | P5 **tidak** dihapus. Lebar kepala terikat `ch[0]`; P2 menurunkannya 128→64 |
| K-04 | 🔸 keputusan | Setuju secara prinsip; saya bisa mengerjakan pencarian+verifikasi |
| K-05 | 🔸 keputusan | Rename **benar secara teknis**; DR<1 di semua varian → nama lama menyesatkan |
| K-06 | ✅ terjawab | IoU = **0,50**, class-aware. Bukan dugaan |
| K-07 | ✅ **kini tersedia** | V2/V4/V6 baru dihitung → `nmsfree_out_8varian/` |
| K-08 | ✅ tersedia | 12 sel + n_gt lengkap di kolom `sel_dibuang` |
| K-09 | ✅ tersedia | epoch & detik/epoch kedelapan varian |
| K-10 | ✅ terjawab | Keduanya benar — beda konvensi, bukan kontradiksi |
| K-11 | ✅ tersedia | Fraksi berprediksi-tunggal = 1 − miss − dup |
| K-12 | ✅ **selesai** | 10.000×3 seed: V8vsV5 tegar; V8vsV1 batas bawah +0,003…+0,02 pp = praktis nol |
| K-13 | 🔸 keputusan | Rekomendasi tegas: **kosongkan** |
| K-15 | 🔸 keputusan | Rekomendasi **(a)** — prasyarat K-07 & K-08 terpenuhi |
| K-16 | ❌ tidak diketahui | Tidak ada di repo; hanya alamat pembimbing yang tercatat |

---

## K-01 — Memori latih 8,52–8,64 GB pada kartu 8 GB

**Itu memori TERALOKASI, tidak termasuk cache alokator.** Spesifikasi GPU tidak perlu dikoreksi.

Rantai kodenya: `y26_complexity.py:39` merekam `peak_gpu_alloc_gb = torch.cuda.max_memory_allocated()`,
`:40` merekam `peak_gpu_reserved_gb = torch.cuda.max_memory_reserved()` (inilah yang memuat cache),
dan kolom `peak_gpu_train_gb` pada `eval_out/complexity.csv` membaca **`peak_gpu_alloc_gb`** (`:138`).
Jadi angka tabel adalah tensor yang benar-benar teralokasi.

| Varian | teralokasi (GB) | tercadangkan/termasuk cache (GB) | detik/epoch |
|---|---|---|---|
| V1 | 5,045 | 6,395 | 59,2 |
| V2 | 5,170 | 6,371 | 61,4 |
| V3 | 8,516 | **11,668** | 316,8 |
| V4 | 5,049 | 6,383 | 60,1 |
| V5 | 8,640 | **11,793** | 376,2 |
| V6 | 5,146 | 6,371 | 63,8 |
| V7 | 8,517 | **11,666** | 341,9 |
| V8 | 8,643 | **11,799** | 417,2 |

Perangkat: **RTX 4060 Ti 8 GB** (benar). Angka teralokasi varian ber-P2 (8,52–8,64 GB) **melampaui**
VRAM fisik, dan angka tercadangkan bahkan 11,7–11,8 GB. Itu mungkin karena **Windows WDDM
mengizinkan CUDA melimpah ke memori sistem bersama** (RAM host lewat PCIe); tidak ada OOM,
dan `batch` tetap 16 untuk kedelapan varian (invarian keadilan ablasi terjaga).

**Konsekuensi yang justru menguntungkan naskah:** limpahan itu **menjelaskan** ledakan waktu latih.
Varian ber-P2 hanya +17 % GFLOPs (22,51→26,42) tetapi **5,4–7,0× lebih lambat per epoch**
(59–64 dtk → 317–417 dtk). Selisih itu bukan komputasi, melainkan lalu lintas PCIe akibat limpahan.

**Saran pelaporan:** cantumkan **dua kolom** (teralokasi dan tercadangkan), sebut batas fisik 8 GB
secara eksplisit, dan nyatakan limpahan memori bersama sebagai temuan — bukan disembunyikan.
Kalimatnya menjadi klaim yang kuat: kepala *stride*-4 pada 640² dengan batch 16 **melewati kapasitas
kartu 8 GB**, sehingga penerapan praktisnya menuntut kartu lebih besar atau batch lebih kecil.

---

## K-02 — Cakupan 95,5–97,2 % vs komplemen 67,9–77,8 %

**Definisi operasionalnya ADA dan keduanya benar. Tidak perlu Jalan B.** Keduanya mengukur hal
berbeda karena **ambang confidence-nya berbeda**:

- **`coverage`** (`y26_nmsfree.py:128`) = `matched_gt / M`. `matched_gt` dinaikkan pada perulangan
  baris **111–118**, yang memakai `conf[match == k]` **tanpa penyaring τ apa pun**. Jadi: fraksi objek GT
  yang memperoleh ≥1 prediksi tercocokkan (IoU ≥ 0,50, kelas sama) **pada confidence berapa pun**,
  di antara seluruh 300 slot mentah kepala one-to-one.
- **`1 − miss_frac`** = fraksi objek GT yang memperoleh ≥1 prediksi tercocokkan **dengan conf > τ = 0,25**
  (baris 104: `sel = (match >= 0) & (conf > t)`).

Terverifikasi pada kedelapan varian: `coverage` **95,54–97,81 %**; `1 − miss_frac` **67,12–77,85 %**.

⚠️ **Dua koreksi angka** bila kedelapan varian dilaporkan (rentang lama berasal dari 5 varian):
95,5–**97,8** % (bukan 97,2) dan **67,1**–77,9 % (bukan 67,9).

⚠️ **Jangan sebut ini recall.** Ia batas atas: "kepala one-to-one menaruh setidaknya satu kotak
sekelas ber-IoU ≥ 0,5 di salah satu dari 300 slotnya, pada confidence berapa pun". Nama yang saya
sarankan: **cakupan bebas-ambang** (*τ-free matched coverage*).

**Nilai analitisnya besar** — justru inilah pilar kedua. Jarak 96,9 % → 74,4 % (V1) berarti **≈22 poin
persen objek SUDAH terlokalisasi** oleh kepala one-to-one tetapi jatuh di bawah ambang operasi.
Itu **defisit kalibrasi/pemeringkatan confidence, bukan kegagalan lokalisasi** — temuan yang tepat
sasaran untuk analisis NMS-free.

---

## K-03 — Mengapa varian ber-P2 justru berparameter LEBIH SEDIKIT 🔑

**P5 TIDAK dihapus, dan tidak ada restrukturisasi yang kami lakukan.** Diverifikasi empiris pada
*checkpoint* terlatih (nc=4):

| | V1 | V3 / V7 | V5 / V8 |
|---|---|---|---|
| total | 9.950.960 | 9.665.024 | 9.681.604 |
| backbone+neck | 9.016.000 | 9.182.528 | 9.199.108 |
| **kepala Detect** | **934.960** | **482.496** | **482.496** |
| level deteksi | 3 — *stride* 8/16/32 | 4 — *stride* **4**/8/16/32 | idem |
| `ch` masuk Detect | [128, 256, 512] | [**64**, 128, 256, 512] | idem |

*Stride* 32 tetap ada pada varian P2 → **kepala P5 dipertahankan**; `Detect(P3,P4,P5)` hanya berubah
menjadi `Detect(P2,P3,P4,P5)`.

**Penyebab sebenarnya:** Ultralytics menurunkan lebar internal kepala dari `ch[0]` — kanal level
**paling halus** yang masuk Detect (`ultralytics/nn/modules/head.py`, `Detect.__init__`):

```python
c2, c3 = max((16, ch[0] // 4, self.reg_max * 4)), max(ch[0], min(self.nc, 100))
```

Menambah P2 membuat `ch[0]` = **64** (P2/4, 128×lebar 0,5) alih-alih **128** (P3/8, 256×0,5), sehingga
`c2`: 32→**16** dan `c3`: 128→**64** — **lebar internal kepala terbagi dua, pada keempat level**.
Karena YOLO26 ber-`end2end: True`, `cv2`/`cv3` diduplikasi menjadi `one2one_cv2`/`one2one_cv3`,
sehingga penyusutan itu **terhitung dua kali**.

Neraca akhirnya: kepala **−452.464**, neck **+166.528** (cabang P2 baru: Upsample + Concat +
C3k2(128) + Conv(128, s2) + C3k2(256)) → **total −285.936 (−2,9 %)**.

**Ini sifat bawaan Ultralytics resmi, bukan suntingan kami.** Ringkasan resmi skala *s* pada nc=80:
`yolo26.yaml` 10.009.784 → `yolo26-p2.yaml` 9.765.856 — bertanda sama. Dibangun ulang pada nc=80,
kode kami mereproduksi **persis** kedua angka itu. Varian P2 kami memakai **YAML resmi**
(`y26_variants.py:177`), tanpa modifikasi kepala.

Biaya HAM sendiri **tepat +16.580 parameter** (V2−V1 = V5−V3 = V8−V3 = +16.580).

**Kalimat yang benar untuk naskah:** penambahan level P2 **menurunkan** parameter 0,29 M (−2,9 %)
karena lebar kepala deteksi terikat pada level terhalus, sementara **menaikkan** GFLOPs
22,51→26,42 (**+17 %**), VRAM latih teralokasi 5,04→8,64 GB (**+71 %**), dan detik/epoch 59→417 (**7×**).
→ **Parameter adalah proksi yang salah untuk biaya P2; komputasi dan memori adalah proksi yang benar.**

⚠️ **Hapus setiap kalimat yang menyatakan "P2 menambah parameter".**

---

## K-04 🔸 — Menambah 9–10 rujukan terbitan ≥2021

**Setuju secara prinsip**, dengan dua syarat agar tidak menjadi bumerang:

1. **Harus benar-benar disitasi di tempat yang relevan**, bukan ditumpuk di pendahuluan. Penelaah
   mengenali rujukan tempelan, dan itu merugikan lebih besar daripada rasio yang kurang.
2. **Setiap rujukan diverifikasi benar-benar ada** (DOI/penulis/tahun cocok). Ingat §12.3: nomor
   [1]–[30] naskah tesis **tidak boleh bergeser**; artikel memakai penomoran sendiri.

**Saya bisa mengerjakan pencarian + verifikasinya sekarang** (WebSearch/WebFetch tersedia untuk saya).
Catatan: konektor claude.ai (Exa, Scite, Google Drive, dll.) **belum terotorisasi** di sesi ini — kalau
Anda ingin memakainya, otorisasi lewat pengaturan konektor claude.ai atau `/mcp` di sesi interaktif.
Tanpa itu saya tetap bisa memakai pencarian web biasa.

**Sekalian:** **A-03 masih terbuka** (angka MST-YOLO +8,42 %/70,97 % dan HIC-YOLOv5 +6,42 % belum
diverifikasi ke sumber [12][13]). Verifikasi itu sebaiknya digabung ke sapuan yang sama.

---

## K-05 🔸 — Rename *duplicate rate* → MMP

**Secara teknis rename itu BENAR**, dan alasannya kuat:

- Definisinya memang **rata-rata prediksi tercocokkan per objek GT**: DR(τ) = (1/M) Σₖ Nₖ(τ),
  dengan Nₖ = jumlah prediksi ber-conf > τ yang tercocokkan ke objek k (`y26_nmsfree.py:7-13`).
- **Empirisnya DR < 1 pada SEMUA varian** (0,6938–0,8746). Menyebut 0,69 sebagai "*duplicate rate*"
  menyesatkan: nilainya rendah karena objek **terlewat** pada τ, bukan karena duplikasi rendah.
- Ukuran duplikasi yang sebenarnya adalah **`dup_frac`** (fraksi objek dengan ≥2 prediksi) = **0,0227–0,1146**.

**Rekomendasi:** pakai **MMP** di artikel **dan** laporkan `dup_frac` berdampingan sebagai ukuran
duplikasi sesungguhnya, dengan catatan kaki yang memetakan MMP ke "*Duplicate Rate*, Pers. 3.6" tesis
supaya kedua dokumen rekonsiliasi. **Perlu ACC pembimbing** karena menyimpang dari istilah tesis
yang sudah disetujui.

---

## K-06 — Ambang IoU pada Persamaan 5

**0,50 — bukan dugaan.** Tiga lokasi konsisten:
`match_predictions(..., iou_thr=0.5)` (`y26_nmsfree.py:69`), CLI `--iou` *default* `0.5`
(`analyze_nmsfree.py:37`), dan `NMSFreeProbe(..., iou=0.5)` (`y26_nmsfree.py:297`).

Detail yang wajib ikut dilaporkan:
- **Class-aware** (`class_aware=True`): IoU dinolkan bila kelas berbeda (baris 76–78) — prediksi hanya
  boleh cocok ke GT **sekelas**.
- Setiap prediksi dipetakan ke **satu** GT ber-IoU tertinggi; **beberapa prediksi boleh menunjuk GT yang
  sama** — itulah duplikasi yang diukur (baris 79–80).
- Docstring baris 9–12 sudah menandainya sebagai keputusan implementasi yang harus didokumentasikan.

---

## K-07 — Instrumentasi V2, V4, V6 ✅ KINI TERSEDIA

Sebelumnya `nmsfree_out/` hanya memuat V1/V3/V5/V7/V8 — **memang sesuai desain** (Subbab 3.8
memfokuskan analisis NMS-free pada *baseline* + varian ber-P2; `DEFAULT_VARIANTS` di
`analyze_nmsfree.py:26`). Saya jalankan sapuan penuh kedelapan varian → **`nmsfree_out_8varian/`**.

**Kelima varian lama bereproduksi bit-per-bit** (DR identik 4 desimal) → pipeline deterministik.

| Varian | MMP/DR | miss | dup | coverage | CM rata | CM median |
|---|---|---|---|---|---|---|
| V1 | 0,7781 | 0,2565 | 0,0346 | 0,9685 | 0,5484 | 0,6659 |
| **V2** | **0,6938** | **0,3288** | **0,0227** | **0,9619** | **0,5243** | **0,6282** |
| V3 | 0,7204 | 0,3208 | 0,0408 | 0,9658 | 0,5057 | 0,5869 |
| **V4** | **0,8054** | **0,2435** | **0,0465** | **0,9781** | **0,5561** | **0,6821** |
| V5 | 0,8246 | 0,2215 | 0,0458 | 0,9723 | 0,5933 | 0,7360 |
| **V6** | **0,8746** | **0,2488** | **0,1146** | **0,9750** | **0,4578** | **0,4665** |
| V7 | 0,7612 | 0,2927 | 0,0523 | 0,9554 | 0,5241 | 0,6166 |
| V8 | 0,8327 | 0,2350 | 0,0654 | 0,9665 | 0,5794 | 0,7156 |

**Dua temuan baru yang layak dinarasikan:**
1. **V6 (HAM+DALW, tanpa P2)** — duplikasi **tertinggi** (0,1146 ≈ 3,3× V1) sekaligus **CM terendah**
   (0,4578). DALW tanpa P2 **menaikkan duplikasi dan melemahkan pemisahan one-to-one**.
2. **V4 (DALW saja)** — **cakupan bebas-τ tertinggi** (0,9781) di antara kedelapan varian.

Probe per-epoch (`nmsfree_probe.csv`) **sudah ada sejak awal untuk kedelapan varian**
(V2 113 baris data, V4 85, V6 53).

---

## K-08 — Daftar 12 sel yang gugur ✅ TERSEDIA LENGKAP

Ada di kolom **`sel_dibuang`** pada `eval_out/wilcoxon_ap5095.csv`. Daftarnya **identik untuk semua
pasangan** karena aturan sel-minimum bergantung pada jumlah GT, bukan pada varian:

| # | Sel (kelas / dimensi / tier) | n_gt |
|---|---|---|
| 1 | big-vehicle / density / dense | 1 |
| 2 | big-vehicle / occlusion / heavy | 2 |
| 3 | big-vehicle / occlusion / partial | **27** |
| 4 | big-vehicle / size / small | 17 |
| 5 | car / density / dense | 11 |
| 6 | car / occlusion / heavy | 0 |
| 7 | pedestrian / density / sparse | 21 |
| 8 | pedestrian / occlusion / heavy | 2 |
| 9 | pedestrian / size / large | 1 |
| 10 | two-wheeler / density / dense | 21 |
| 11 | two-wheeler / occlusion / heavy | 0 |
| 12 | two-wheeler / size / large | 1 |

Ambang: `MIN_CELL_GT = 30`. Unit uji 36 → **24 sel**.

Dua pola yang wajib disebut: **seluruh 4 sel occlusion/heavy gugur** (strata *heavy* hilang total), dan
**3 dari 4 sel density/dense gugur** (hanya pedestrian n=77 yang lolos). Sel #3 (n=27) adalah **nyaris
lolos** — layak ditampilkan agar pembaca melihat aturannya tidak dipilih demi hasil.

→ **Janji pada METHOD tidak perlu dihapus.** Datanya ada dan bisa ditabelkan apa adanya.

---

## K-09 — Epoch & detik/epoch ✅ TERSEDIA

Sumber: `runs_tesis/<V>/complexity_train.json`. Lihat tabel pada **K-01** (kolom epoch, jam, detik/epoch).
Ringkas: V1 96 ep/59,2 dtk · V2 112/61,4 · V3 100/316,8 · V4 84/60,1 · V5 98/376,2 · V6 52/63,8 ·
V7 97/341,9 · V8 99/417,2. Semuanya `batch = 16`, berhenti via *early stopping* (patience 50).
Tersedia juga untuk V4_a0.5, V4_a2.0, V8_normw.

---

## K-10 — Figure 1 (P3/P4) vs METHOD (tahap backbone ke-3/ke-4)

**Keduanya benar dan merujuk hal yang SAMA** — ini ketidakseragaman konvensi, bukan kontradiksi
faktual.

HAM disisipkan setelah blok C3k2 pada indeks backbone **4** dan **6** (`y26_variants.py:46`,
`_INSERT_AFTER = (4, 6)`). Pada `yolo26.yaml`, indeks 4 adalah C3k2 sesudah Conv *stride*-2 berlabel
`# 3-P3/8`, dan indeks 6 adalah C3k2 sesudah `# 5-P4/16`. Jadi blok itu **adalah** tahap backbone ke-3
dan ke-4, dan keluarannya **adalah** peta P3/8 dan P4/16. Docstring kode menyatakannya utuh:
"setelah blok C3k2 tahap-3 (indeks 4, fitur P3/8) dan tahap-4 (indeks 6, fitur P4/16)".

**Saran:** seragamkan ke **"P3/8 dan P4/16"** (tak ambigu, langsung terikat *stride*), sebut
"(tahap backbone ke-3 dan ke-4)" sekali saja sebagai penjelas. Kode punya penjaga struktur
(`y26_variants.py:82-84`) yang meng-*assert* posisi ini, sehingga tidak dapat bergeser diam-diam.

---

## K-11 — Fraksi objek berprediksi tunggal ✅ TERSEDIA

Ketiga fraksi mempartisi tepat 1,000 pada τ=0,25, jadi **tepat-satu = 1 − miss − dup**:

| Varian | miss (0) | **tepat 1** | dup (≥2) | coverage bebas-τ |
|---|---|---|---|---|
| V1 | 0,2565 | **0,7088** | 0,0346 | 0,9685 |
| V2 | 0,3288 | **0,6485** | 0,0227 | 0,9619 |
| V3 | 0,3208 | **0,6385** | 0,0408 | 0,9658 |
| V4 | 0,2435 | **0,7100** | 0,0465 | 0,9781 |
| V5 | 0,2215 | **0,7327** | 0,0458 | 0,9723 |
| V6 | 0,2488 | **0,6365** | 0,1146 | 0,9750 |
| V7 | 0,2927 | **0,6550** | 0,0523 | 0,9554 |
| V8 | 0,2350 | **0,6996** | 0,0654 | 0,9665 |

⚠️ **Kehati-hatian yang wajib masuk naskah:** CM dihitung **tanpa** penyaring τ (docstring baris 15–18),
dan bila prediksi kedua tak ada maka conf(p⁽²⁾) = 0 sehingga **CM = conf prediksi tunggal itu** — bukan
"margin" dalam arti biasa. Karena **64–73 % objek** berada pada golongan ini, sifat itu harus dinyatakan
terbuka, bukan dibiarkan tersirat. Bila Anda ingin angka "tepat-satu" yang **persis** sepadan dengan
definisi CM (yakni bebas-τ), itu belum tersimpan langsung; baris τ=0,05 pada `tau_sweep.csv` adalah
proksi terdekat, atau saya hitung ulang (murah).

---

## K-12 — Bootstrap 10.000 resample ✅ SELESAI

**Ya, dan Anda benar bahwa yang sekarang rawan.** Pada n_boot = 1.000:

| Pasangan | selisih mAP50-95 | CI 95 % | frac positif | tanpa nol |
|---|---|---|---|---|
| V8 vs V1 | +0,010178 | [**+0,000506**; +0,020793] | 0,979 | ya |
| V4 vs V1 | −0,001692 | [−0,012059; +0,009997] | 0,402 | tidak |
| V8 vs V5 | +0,022914 | [+0,012577; +0,035269] | 1,000 | ya |

Batas bawah V8 vs V1 hanya **+0,05 poin persen** → memang rawan berubah tanda karena galat
Monte Carlo bootstrap itu sendiri.

**Sudah dijalankan** (`k12_bootstrap_10k.py`, skrip permanen baru): **10.000 resample × 3 seed
(0, 1, 2)**, memakai ulang cache pencocokan `eval_out/cache_V*.npz` sehingga **tanpa inferensi
ulang**. **Non-destruktif** — hasil di `eval_out/bootstrap_ci_10000.csv`; `bootstrap_ci.csv`
(1.000 resample) tidak ditimpa. Waktu jalan ±13,7 jam (`map_from_sample` berulang di Python).

Titik estimasi **cocok persis** dengan berkas 1.000-resample (mAP V8 0,540397429…,
V1 0,530219566…, selisih 0,010177863…) → jalur kode & cache identik, hanya pengambilan ulangnya
yang berbeda.

**Hasil n_boot = 10.000, per seed:**

| Pasangan | seed | CI 95 % bawah | CI 95 % atas | frac positif | tanpa nol |
|---|---|---|---|---|---|
| V8 vs V1 | 0 | **+0,000216** | +0,020438 | 0,9775 | ya |
| V8 vs V1 | 1 | **+0,000035** | +0,020402 | 0,9755 | ya |
| V8 vs V1 | 2 | **+0,000122** | +0,020570 | 0,9763 | ya |
| V4 vs V1 | 0–2 | −0,01280 … −0,01251 | +0,00968 … +0,01012 | 0,408–0,423 | tidak |
| V8 vs V5 | 0–2 | **+0,011257 … +0,011389** | +0,03441 … +0,03485 | **1,000** | ya |

**Tafsiran yang jujur:**
- **V8 vs V1** — selang **masih** tidak memuat nol pada ketiga seed, tetapi batas bawahnya
  **+0,0035 s.d. +0,022 poin persen**, yakni **praktis tak terbedakan dari nol** (pada seed 1
  hanya +0,0035 pp). Digabung Wilcoxon **p = 0,565**, bacaan yang dapat dipertahankan adalah
  **tidak ada perbaikan yang andal** — jangan sekali-kali menyajikan "selang tidak memuat nol"
  sebagai bukti keunggulan; itu akan terbaca sebagai memilih uji yang menguntungkan.
- **V4 vs V1** — memuat nol pada ketiga seed, konsisten p = 0,208. Stabil, tidak signifikan.
- **V8 vs V5** — **tegar**: batas bawah +0,0113 pp dan `frac_positif` **1,000** pada ketiga seed.
  Inilah satu-satunya temuan yang kokoh di ketiga uji (Wilcoxon p = 0,0367, r = +0,487).

**Saran pelaporan:** cantumkan ketiga seed (atau rentang antar-seed) agar pembaca melihat
kestabilannya sendiri, dan naikkan `n_boot` dari 1.000 → 10.000 di METHOD sesuai yang benar-benar
dijalankan.

---

## K-13 🔸 — Metadata produksi artikel lain di header

**Rekomendasi tegas: KOSONGKAN.** Ini bukan persoalan gaya.

Header memuat Vol. 6 No. 6 December 2025, halaman 1530–1537, dan **DOI 10.52436/1.jutif.6.6.3540** —
DOI **hidup milik artikel lain**. Membiarkannya dalam berkas *submission* Anda adalah **misatribusi
faktual**, dan akan dibaca penelaah/penyunting sebagai kelalaian atau — lebih buruk — upaya tampak
sudah terbit. "Templat tidak memuat instruksi" **bukan** izin menyimpan pengenal milik makalah lain.

Kosongkan medan produksi (atau isi *placeholder* netral "Vol. X No. X") dan biarkan penyunting
mengisinya. Menurut saya **ini butir berisiko tertinggi di seluruh daftar** relatif terhadap betapa
sepelenya memperbaikinya.

---

## K-14 — Koordinat garis maya per klip ✅ TERSEDIA (laporkan langsung)

Sumber: `video_uji/konfigurasi_garis.json` (sengaja **di-track git**, §15 — satu-satunya data yang tak
dapat dibangkitkan ulang kode). Klip 1 dikecualikan (cacat validitas pengukuran).

| Klip | garis dipakai (x1,y1,x2,y2) | garis geometris | resolusi | fps | frame | interval |
|---|---|---|---|---|---|---|
| 2_vidiouji | 1919, 926, 119, 1 | 119, 1, 1919, 926 | 1920×1080 | 30,0 | 18.000 | 10 × 60 dtk |
| 3_vidiouji | 1280, 668, 0, 317 | 0, 317, 1280, 668 | 1280×720 | 30,0 | 18.000 | 10 × 60 dtk |
| 4_vidiouji | 1919, 784, 348, 739 | 348, 739, 1919, 784 | 1920×1080 | 30,0 | 18.000 | 10 × 60 dtk |

**Laporkan di badan naskah, jangan "tersedia atas permintaan"** — hanya tiga baris, dan ia membuat
hasil *counting* dapat direproduksi. **Wajib disertai catatan konvensi arah:** "garis dipakai" adalah
titik yang **dibalik** terhadap "garis geometris"; geometri garisnya identik, pembalikan itu menyelaraskan
arah in/out `sv.LineZone` dengan definisi penghitung manual (in = menuju kiri-bawah). Tanpa catatan
ini pembaca tak dapat mereproduksi angkanya.

---

## K-15 🔸 — Panjang RESULT

**Pilih (a).** Prasyarat yang Anda sebut sendiri **terpenuhi**: K-07 dan K-08 keduanya **tersedia**.

Bahkan sekarang datanya **lebih banyak** daripada saat opsi itu ditulis:
- 3 varian baru terinstrumentasi (V2/V4/V6) + **dua temuan baru** (anomali duplikasi/CM V6; cakupan
  tertinggi V4);
- tabel 12 sel gugur lengkap dengan n_gt;
- epoch & detik/epoch kedelapan varian + dua kolom VRAM;
- dekomposisi cakupan bebas-τ vs τ=0,25 (≈22 pp objek terlokalisasi tapi di bawah ambang);
- neraca parameter K-03 (kepala −452.464 vs neck +166.528).

**Syaratnya satu:** jangan mengisi dengan menarasikan ulang tabel. RESULT 50 % yang isinya parafrase
tabel lebih buruk daripada 44 % yang padat. Isi dengan **penjelasan mekanistik** yang sudah punya
dasar data — mengapa presisi turun sementara objek terlewat berkurang, mengapa P2 mahal di
komputasi tetapi murah di parameter, mengapa strata *heavy*/*dense* gugur — itu analisis, bukan
tambalan.

---

## K-16 — Alamat surel kampus

**Tidak diketahui, dan tidak dapat saya tentukan dari repo.** Satu-satunya alamat kampus yang
tercatat adalah **pembimbing**: sandfreni@esaunggul.ac.id (CLAUDE.md §1). Alamat Naufal sendiri
tidak ada di repositori.

Saya **tidak akan menebak** alamat yang akan tercetak pada artikel terbit. Mohon konfirmasi alamat
aktif Anda, **dan pastikan Anda benar-benar dapat menerima surat di sana** — alamat ini menjadi
kanal *corresponding author*, dan surat keputusan penyuntingan akan dikirim ke situ.

---

## Berkas & artefak yang dihasilkan sesi ini

| Berkas | Isi |
|---|---|
| `nmsfree_out_8varian/` | Instrumentasi NMS-free **kedelapan** varian (K-07); 5 varian lama bereproduksi persis |
| `k12_bootstrap_10k.py` | Skrip permanen bootstrap n_boot besar, non-destruktif (K-12) |
| `eval_out/bootstrap_ci_10000.csv` | Hasil 10.000 resample × 3 seed (menyusul saat job selesai) |
| `logs/k07_nmsfree_8varian.log` | Log berstempel waktu job K-07 |
| dokumen ini | Jawaban K-01…K-16 dengan rujukan sumber |

**Tidak ada artefak lama yang ditimpa:** `nmsfree_out/`, `eval_out/bootstrap_ci.csv`, `runs_tesis/`,
dan seluruh naskah tetap utuh.
