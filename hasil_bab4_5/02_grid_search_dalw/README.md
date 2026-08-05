# 02 — Grid Search Hiperparameter DALW (α, σ)

Menjawab Subbab 3.9 (Konfigurasi dan Hiperparameter Pelatihan) — pencarian α dan σ untuk
Pembobotan *Loss* Berbasis Densitas, dilakukan sekali pada varian penuh (V8) dengan
pelatihan dipersingkat (60 epoch), sebelum dibekukan untuk kedelapan varian.

## Berkas

| Berkas | Isi |
|---|---|
| `tabel_grid_search.csv` | 9 kombinasi α×σ diurutkan dari mAP50-95 tertinggi |
| `heatmap_grid_search.png` | Peta panas mAP50-95 val untuk kombinasi α∈{0,5;1,0;2,0} × σ∈{0,05;0,10;0,20}; kombinasi terpilih ditandai bintang (*) dan huruf tebal |

## Cara membaca heatmap

Sumbu X = σ (lebar kernel densitas), sumbu Y = α (kekuatan penekanan densitas). Warna
lebih terang = mAP lebih tinggi. Kombinasi **α=1,0, σ=0,1** (mAP50-95=0,6670) adalah
titik **interior grid** (bukan di tepi) — ini penting karena berarti grid tidak perlu
diperluas untuk mencari titik lebih baik.

## Pola untuk narasi BAB 4

- **α=0,5 secara konsisten terlemah** di ketiga nilai σ — pembobotan densitas terlalu
  lemah untuk berpengaruh.
- **σ optimal bergeser naik seiring α membesar** (α=0,5→σ*=0,05; α=1,0→σ*=0,10;
  α=2,0→σ*=0,20) — interaksi diagonal: kekuatan pembobotan dan lebar kernel saling
  mengompensasi.
- Rentang total kombinasi: 0,6368–0,6670 (selisih 0,0302) — pilihan α,σ berdampak nyata,
  bukan formalitas.

## Keterbatasan yang wajib disebutkan (naskah Subbab 3.9 sendiri mengakuinya)

Pencarian dilakukan **satu kali** pada V8 dengan pelatihan **dipersingkat** (60 dari
maksimum 300 epoch). Nilai optimal untuk V8 belum tentu optimal untuk varian lain
(V4, V6, V7) — ini **dikonfirmasi empiris** oleh hasil sensitivitas α pada V4
(lihat folder `06_sensitivitas_alpha/`, di mana α=2,0 justru lebih baik untuk V4 saja).

## Kalimat siap-adaptasi

> "Pencarian hiperparameter α dan σ dilakukan satu kali pada varian penuh (V8) dengan
> pelatihan dipersingkat 60 epoch, menghasilkan konfigurasi terpilih α=1,0 dan σ=0,10
> (mAP50-95 validasi 0,6670), sebuah titik interior pada grid pencarian sehingga tidak
> diperlukan perluasan grid. Kombinasi α=0,5 secara konsisten menghasilkan performa
> terlemah pada seluruh nilai σ yang diuji."
