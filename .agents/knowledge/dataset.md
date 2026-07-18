# Dataset traffic-merged & Group Split — traffic-merged Dataset & Group Split

> **EN — TL;DR:** `traffic-merged` = 3,389 primary Jakarta CCTV images, 4 classes (two-wheeler dominant; **pedestrian is context only — never counted**). The original Roboflow export leaked (3 byte-identical pairs across splits), so we discard it and re-split **by group** (camera × scene × session) with `make_group_split.py` → deterministic 2.372/679/338 images, 672/53/33 groups, 0 md5/group violations. The live `dataset/` folder IS that re-split; `bukti_split_*.csv` are the thesis appendix. Two open discrepancies to surface (never resolve): Roboflow source workspace vs citation [17], and split counts.

Dokumen ini merangkum sumber data, alasan *group-based split*, mekanika `make_group_split.py`, dan artefak bukti yang dipakai BAB 3/4. Referensi silang: atribut stratifikasi & AP dijelaskan di [Evaluasi & Stratifikasi](evaluation.md); unit uji statistik di [Statistik](statistics.md); invarian metodologis yang mengunci angka split di [Invarian Metodologi](../rules/methodology-invariants.md).

## 1. Identitas dataset

- **Nama:** `traffic-merged` — 3.389 citra CCTV lalu lintas Jakarta, **data primer** (mayoritas kamera dipasang peneliti sendiri).
- **Sitasi tesis [17]:** `universe.roboflow.com/naufalfirdaus/traffic-merged-qke0k-3yyyo`.
- **Empat kelas** (urutan indeks di `data.yaml`, lihat `make_group_split.py` baris `names = [...]`):

| Idx | Kelas | Peran | Catatan |
|---|---|---|---|
| 0 | `big-vehicle` | dihitung | gabungan bus + truk |
| 1 | `car` | dihitung | mobil |
| 2 | `pedestrian` | **objek konteks — TIDAK dihitung** | hadir untuk konteks/deteksi, dikecualikan dari *counting* ByteTrack |
| 3 | `two-wheeler` | dihitung | roda dua, **kelas dominan** (objek kecil 8–16 piksel pada citra 640) |

> ⚠️ **Aturan NEVER:** *pedestrian* muncul di deteksi tetapi **dikecualikan dari penghitungan kendaraan** (lihat [Counting](counting.md)). Jangan pernah memasukkannya ke MAE/RMSE/MAPE.

## 2. Kenapa Group-Based Split (bukan per-frame)

Split acak per-citra membocorkan informasi: frame-frame dari video/sesi CCTV yang sama sangat mirip, sehingga citra "tetangga" bisa jatuh di *train* dan *test* sekaligus → estimasi performa terlalu optimistis (*data leakage*).

Ekspor Roboflow manual yang semula dipakai (folder `dataset/` versi awal) **terbukti bocor** saat verifikasi P2:

- Proporsi ekspor **83,4 / 12,6 / 4,0** (jauh dari target 70/20/10).
- **3 pasang citra byte-identik** (md5 sama) tersebar lintas split.
- **128 stem** nama-file asli muncul di lebih dari satu subset.

Karena itu, ekspor asli dibuang dan split dibangun ulang **per grup** (proksi kamera × adegan × sesi) sehingga seluruh citra segrup dijamin berada di subset yang sama. Keputusan re-split ini **disetujui Naufal** (lihat [Progres](../status/progress.md) P2).

> Catatan integritas kode: `download_dataset.py` masih berasumsi split Roboflow "sudah final per grup" dan hanya memverifikasi jumlah — asumsi itu **tidak berlaku** untuk ekspor manual yang dipakai; kebenaran operasional adalah re-split lokal via `make_group_split.py`. Jangan andalkan komentar di `download_dataset.py` sebagai deskripsi split final.

## 3. Mekanika `make_group_split.py`

Deterministik penuh (**tanpa RNG**; hasil identik antar-run). Alur: inventarisasi → penentuan grup → penetapan subset greedy sadar-kelas → local search → salin berkas + tulis bukti.

### 3.1 Definisi grup

Kunci grup diturunkan dari **nama file asli** (setelah sufiks Roboflow `_jpg.rf.<hash>` dilucuti via `stem_of`). Prinsip: bila ragu **DIGABUNG** — *over-merge* hanya membuat grup lebih kasar, tak pernah menimbulkan kebocoran.

| Pola | Pemicu (regex) | Kunci grup | Proksi |
|---|---|---|---|
| `frame-video` | `frame_\d+` | `video-{w}x{h}` (per **resolusi** citra) | frame satu video pasti seresolusi |
| `cctv-timestamp` | `20\d{13}` (15 digit) | `sesi-{stem[:8]}` (8 digit pertama = tanggal) | proksi sesi CCTV per tanggal |
| `tunggal` | selain di atas | stem tanpa satu sufiks salinan akhir (`[-_]+\d+[-_]*$`) | seri `001--1-`, `001--2-` menyatu |

Setelah itu, **union-find (DSU)** memaksa setiap citra **byte-identik (md5 sama)** masuk grup yang sama apa pun namanya — ini penjaga terakhir terhadap kebocoran byte-identik yang meloloskan penamaan.

### 3.2 Penetapan subset (greedy sadar-kelas + local search)

- Grup diurutkan **deterministik**: ukuran menurun, lalu `md5(nama grup)` sebagai *tie-break*.
- Tiap grup ditempatkan ke subset yang **meminimalkan deviasi gabungan** (fungsi `dev`):
  - proporsi **citra** terhadap target 70/20/10 (bobot utama `6.0`),
  - proporsi **instans per kelas** (menjaga keseimbangan 4 kelas),
  - **lantai jumlah grup** per subset (bobot `3.0`, menjaga keragaman adegan agar *valid*/*test* tak kehilangan variasi).
- Disempurnakan **local search**: pindah grup tunggal bila memperbaiki `dev`, maksimum 5 putaran.

### 3.3 Hasil final

| Subset | Citra | Proporsi | Grup |
|---|---|---|---|
| train | 2.372 | 70,0% | 672 |
| valid | 679 | 20,0% | 53 |
| test | 338 | 10,0% | 33 |
| **Total** | **3.389** | **100%** | **758** |

- **0 pelanggaran** md5/grup lintas split (kebocoran teratasi).
- Komposisi kelas *test* minimal **332 instans/kelas** (cukup untuk AP terstratifikasi).
- ⚠️ CLAUDE.md §5 menuliskan angka *approx* "≈2.372/678/339"; angka **final aktual** (§15 P2) adalah **2.372/679/338** — pakai yang final.

## 4. Artefak & folder aktif

| Artefak | Isi | Peran |
|---|---|---|
| `dataset/` | hasil re-split (`{train,valid,test}/{images,labels}` + `data.yaml` path absolut) | **dataset AKTIF** untuk semua pelatihan/evaluasi |
| `traffic-merged.yolo26.zip` (root) | arsip ekspor Roboflow **asli yang bocor** | arsip; integritas terverifikasi 3.389 citra+label; regenerasi hanya bila perlu |
| `bukti_split_grup.csv` | 758 grup → subset, `n_citra`, pola, `contoh_stem` | **lampiran tesis** (bukti metodologis) |
| `bukti_split_citra.csv` | jejak per citra → stem asli → grup → subset | **lampiran tesis** (jejak penuh) |

Regenerasi (hanya bila perlu; deterministik): ekstrak `traffic-merged.yolo26.zip` → `dataset_raw/`, lalu `python make_group_split.py --src dataset_raw --dst dataset`. `bukti_split_*.csv` ikut ditulis ulang identik.

> ⚠️ `dataset/`, `traffic-merged.yolo26.zip`, dan `bukti_split_*.csv` adalah **bahan mentah/bukti BAB 4** — jangan sarankan menghapus atau menimpanya (lihat [Invarian Metodologi](../rules/methodology-invariants.md)).

## 5. Atribut stratifikasi (diturunkan komputasional)

Tiga dimensi strata diturunkan otomatis dari label/geometri kotak (bukan anotasi tangan), lalu dipakai untuk AP terstratifikasi dan unit Wilcoxon:

- **Ukuran** — konvensi COCO (small/medium/large berdasar luas kotak).
- **Oklusi** — proksi `o_i = max_j IoU(b_i, b_j)` (Pers. 3.1), tier default 0,10 / 0,35.
- **Densitas** — jumlah & kerapatan kotak per frame, tier default 10 / 26; **dihitung ulang pasca-augmentasi** (mosaic).

Detail komputasi, tier, dan pipeline AP ada di [Evaluasi & Stratifikasi](evaluation.md). Catatan penting P8: tier **oklusi-heavy (o ≥ 0,35) nyaris kosong** di *val* (0/4.094; *test* 8/2.600) → indikasi proksi box-IoU *underestimate* oklusi perseptual; ambang 0,10/0,35 **TERKUNCI** menunggu validasi manual — lihat [Keputusan Pending](../status/pending-decisions.md).

## 6. Diskrepansi terbuka (SURFACE — jangan resolve sendiri)

Dua ketidakcocokan harus **dicatat**, bukan diputuskan sepihak; konfirmasi ke Naufal + pembimbing:

1. **Sumber Roboflow.** Sitasi [17] dan default `download_dataset.py` menunjuk workspace **`naufalfirdaus/traffic-merged-qke0k-3yyyo`**, tetapi ekspor manual yang dipakai P2 berasal dari **`sahabats-workspace/traffic-merged-qke0k-3yyyo-nkdvt`** (berbeda). Perlu dikonsistenkan di naskah.
2. **Angka split.** CLAUDE.md §5 memakai "≈2.372/678/339"; §15 P2 dan `bukti_split_*.csv` memakai final **2.372/679/338**. Naskah harus menyeragamkan ke angka final.

Diskrepansi lain di tingkat naskah (judul, jumlah sitasi, GPU) dilacak di [Keputusan Pending](../status/pending-decisions.md) dan [TODO Dokumen](../status/document-todos.md).
