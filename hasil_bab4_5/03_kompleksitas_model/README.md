# 03 — Kompleksitas & Efisiensi Model (Tabel 3.7)

Menjawab Subbab 3.11.4 — masukan revisi pembimbing poin 4: selain akurasi, laporkan
jumlah parameter, FLOPs, ukuran model, kebutuhan memori GPU, waktu latih, dan FPS.

## Berkas

| Berkas | Isi |
|---|---|
| `tabel_kompleksitas.csv` | **Tabel 3.7 siap-salin.** Kolom: params_M, gflops, size_MB, peak_gpu_train_gb, peak_gpu_infer_gb, train_hours, epochs, fps, latency_ms — untuk kedelapan varian |
| `grafik_kompleksitas_4panel.png` | 4 panel: parameter, GFLOPs, VRAM latih, FPS — perbandingan langsung antarvarian |
| `grafik_tradeoff_akurasi_fps.png` | Sebar mAP50-95 (test) vs FPS inferensi — trade-off akurasi/kecepatan |

## Cara membaca

**4 panel**: perhatikan varian ber-P2 (V3, V5, V7, V8) vs non-P2 (V1, V2, V4, V6) —
perbedaannya tegas di ketiga panel pertama (P2 menambah GFLOPs +17%, VRAM +70%) tetapi
**parameter hampir sama** (P2 menambah lapisan deteksi kecil, bukan lapisan besar).

**Trade-off**: titik di kanan-atas = ideal (akurasi tinggi + cepat). V1 (baseline)
tercepat (32,4 FPS) tapi bukan paling akurat; V8 (penuh) akurasi tertinggi tapi
lebih lambat (23,3 FPS) — konsekuensi wajar dari P2.

## Angka kunci

| Varian | Parameter (M) | GFLOPs | VRAM latih (GB) | Waktu latih (jam) | FPS |
|---|---|---|---|---|---|
| V1 | 9,95 | 22,5 | 5,05 | 1,58 | **32,4** |
| V4 | 9,95 | 22,5 | 5,05 | 1,40 | 30,5 |
| V5 | 9,68 | 26,4 | 8,64 | 10,24 | 22,5 |
| **V8** | 9,68 | 26,4 | **8,64** | **11,47** | **23,3** |

**Catatan VRAM:** varian ber-P2 memakai 8,52–8,64 GB dari 8 GB VRAM RTX 4060 Ti —
sangat dekat batas, mengonfirmasi keputusan desain Batasan 1.6 (GPU 8GB kelas menengah
sengaja dipilih untuk menguji kelayakan praktis).

## Kalimat siap-adaptasi

> "Penambahan Lapisan Deteksi P2 meningkatkan kompleksitas komputasi sebesar 17%
> (22,5→26,4 GFLOPs) dan kebutuhan memori GPU sebesar 70% (5,05→8,64 GB) tanpa
> menambah jumlah parameter secara berarti, konsekuensi dari resolusi spasial head
> deteksi tambahan berstride 4 yang menghasilkan sekitar empat kali jumlah titik
> anchor. Model penuh (V8) mencapai kecepatan inferensi 23,3 bingkai per detik pada
> presisi FP16, masih memenuhi ambang praktis untuk pemantauan lalu lintas non-kritis
> namun di bawah standar real-time konvensional 30 FPS."

⚠️ **FPS di sini adalah FPS model murni (batch 1, forward pass saja)** — BUKAN FPS
pipeline end-to-end dengan ByteTrack + virtual line crossing, yang akan diukur di
`09_counting_end_to_end/` setelah counting selesai. Jangan tertukar saat mengisi
placeholder abstrak "[XX] frame per detik".
