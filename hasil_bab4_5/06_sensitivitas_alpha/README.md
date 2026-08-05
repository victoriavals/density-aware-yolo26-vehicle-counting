# 06 — Sensitivitas Hiperparameter α pada Varian V4

Menjawab mitigasi keterbatasan yang diakui naskah Subbab 3.9: karena grid search
dilakukan satu kali pada V8, dilakukan pemeriksaan tambahan apakah α optimal untuk V8
juga optimal untuk varian lain (diwakili V4, varian DALW-saja).

## Berkas

| Berkas | Isi |
|---|---|
| `tabel_sensitivitas_alpha.csv` | mAP50-95 val terbaik pada α∈{0,5; 1,0; 2,0} (σ=0,1 tetap), untuk V4 |
| `grafik_sensitivitas_alpha.png` | Kurva mAP terbaik vs α, dengan anotasi epoch konvergensi |

## Temuan Utama — Penting untuk BAB 4

| α | mAP50-95 val terbaik | Epoch checkpoint terbaik | Total epoch (berhenti early-stop) | Waktu latih |
|---|---|---|---|---|
| 0,5 | 0,6313 | 21 | 71 | 1,21 jam |
| 1,0 (dipilih grid search pada V8) | 0,6356 | 34 | 84 | 1,40 jam |
| **2,0** | **0,6523** ⬆ | 72 | 122 | 2,00 jam |

**α=2,0 justru terbaik untuk V4**, bukan α=1,0 yang dipilih grid search (yang dicari
pada V8). Ini **mengonfirmasi secara empiris** keterbatasan yang sudah diakui naskah
sendiri: *"nilai α dan σ yang optimal bagi varian lengkap belum tentu optimal bagi
varian lain seperti V4, V6, dan V7."* Perhatikan juga α=2,0 baru mencapai performa
terbaiknya pada epoch yang **lebih lambat** (epoch 72 vs 21 dan 34) — kemungkinan
pembobotan kuat memerlukan waktu adaptasi lebih panjang sebelum manfaatnya terlihat.
(Kolom "total epoch" adalah titik *early stopping* berhenti — patience 50 epoch
setelah checkpoint terbaik — bukan epoch performa terbaik itu sendiri; jangan tertukar
saat mengutip di naskah.)

## Implikasi penulisan

Ini **bukan berarti hasil ablasi utama (folder 04) tidak valid** — kedelapan varian
dibandingkan dengan konfigurasi (α,σ) yang **sama demi keadilan perbandingan** (syarat
Subbab 3.9). Temuan ini murni melaporkan **keterbatasan metodologi pencarian
satu-titik**, sesuai janji naskah untuk dilaporkan di BAB 4.

## Kalimat siap-adaptasi

> "Untuk memeriksa kepekaan hasil terhadap nilai α yang dibekukan dari pencarian pada
> varian penuh, dilakukan pelatihan ulang varian V4 (DALW saja) pada α=0,5 dan α=2,0
> dengan σ=0,10 tetap. Hasil menunjukkan bahwa α=2,0 mencapai mAP@0,5:0,95 validasi
> terbaik sebesar 0,6523, lebih tinggi dari α=1,0 yang dibekukan dari pencarian pada
> V8 (0,6356), mengonfirmasi keterbatasan yang telah diakui pada Subbab 3.9 bahwa
> nilai hiperparameter optimal tidak bersifat seragam antarvarian. Nilai α=1,0 tetap
> dipertahankan untuk kedelapan varian pada eksperimen ablasi utama demi menjamin
> keadilan perbandingan antarvarian."
