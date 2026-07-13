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
- **GPU: RTX 4060.** ⚠️ Dokumen tesis masih menulis "RTX 3060 8GB" di **5 lokasi** yang WAJIB diperbarui: Batasan 1.5, Tabel 3.6, subbab 2.5.2, 2.7.3, 3.6.2.
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