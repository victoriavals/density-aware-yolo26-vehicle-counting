# Framing Kebaruan Dua Pilar — Two-Pillar Novelty Framing

> **EN — TL;DR:** This thesis makes exactly two novelty claims: (1) a *method* — Density-Aware Loss Weighting (DALW), a per-object loss re-weighting driven by local ground-truth density; and (2) an *analysis* — the first empirical study of how such modifications interact with YOLO26's one-to-one *NMS-free* head (Duplicate Rate, Confidence Margin, assignment stability). HAM and the P2 layer are **instruments, never novelty** — this is the single most-violated rule in the project. Keep YOLO26's *preprint* hedging, and record the two conflicting thesis titles as an open item for the supervisor.

Dokumen ini menjelaskan tulang punggung argumentatif tesis: apa yang boleh diklaim sebagai kebaruan, apa yang tidak, dan bagaimana klaim itu diposisikan terhadap mekanisme bawaan YOLO26. Semua penulisan BAB 1–5 serta seluruh basis pengetahuan ini harus tunduk pada framing di sini. Sumber kebenaran adalah `CLAUDE.md` §1–§3; bila terjadi konflik, `CLAUDE.md` menang.

## Dua pilar kebaruan

Penelitian ini sengaja membatasi diri pada **dua** klaim kebaruan, tidak lebih. Membatasi klaim adalah keputusan strategis: YOLO26 sudah merupakan *baseline* yang kuat (memiliki *dual-head NMS-free*, ProgLoss, STAL, dan MuSGD), sehingga setiap peningkatan harus diframe sebagai perbaikan atas *baseline* yang sudah kuat, bukan sebagai penemuan komponen dari nol.

### Pilar 1 — Kebaruan metodologis: Pembobotan *Loss* Berbasis Densitas (DALW)

Kebaruan metode adalah **Pembobotan *Loss* Berbasis Densitas** (istilah utama dalam narasi; singkatan *DALW* dipakai hanya di tabel dan nama varian). Idenya: setiap objek diberi bobot *loss* yang meningkat seiring kepadatan lokal di sekitarnya, sehingga model menaruh perhatian lebih pada objek yang berdesakan — kondisi khas lalu lintas heterogen padat. Rumusannya (Pers. 3.2–3.5) sebagai berikut:

- densitas lokal ρᵢ = Σⱼ≠ᵢ exp(−‖cᵢ−cⱼ‖²/2σ²) (Pers. 3.2), dihitung dari jarak antar-pusat kotak *ground truth*;
- normalisasi ρ̂ᵢ = ρᵢ/(ρᵢ+1) (Pers. 3.3), memetakan densitas ke rentang [0, 1);
- bobot wᵢ = 1 + α·ρ̂ᵢ (Pers. 3.4), dengan α mengatur kekuatan pembobotan;
- *loss* total L = (1/N) Σ wᵢ·Lᵢ (Pers. 3.5), dengan Lᵢ *loss* bawaan YOLO26 per objek.

Sifat penting yang menjaga klaim tetap konservatif: bobot wᵢ **dihitung dari *ground truth*, bersifat konstanta per iterasi** (termasuk dihitung ulang pasca-augmentasi mosaic/flip/scale), dan berada dalam `torch.no_grad` sehingga **tidak menambah gradien** — kompleksitas gradien identik dengan *baseline*. Detail matematis, implementasi *monkey-patch* `apply_dalw`, dan bukti bahwa wᵢ berlaku pada kedua cabang head ada di [DALW](dalw.md). Hiperparameter α dan σ dipilih via *grid search* sekali pada V8 (pemenang α=1,0 σ=0,1 pada koordinat ternormalisasi); lihat [statistik & grid search](statistics.md) dan [status progres](../status/progress.md).

### Pilar 2 — Kebaruan analitis: interaksi dengan mekanisme *one-to-one NMS-free*

Kebaruan kedua bersifat empiris-analitis: **penyelidikan pertama** tentang bagaimana modifikasi arsitektur/​*loss* memengaruhi mekanisme pencocokan *one-to-one* yang membuat YOLO26 dapat bekerja tanpa NMS. Instrumen ukurnya tiga:

- **Duplicate Rate** DR(τ) (Pers. 3.6, ambang τ = 0,25) — seberapa sering satu objek dipetakan oleh lebih dari satu prediksi; DR≈1 sehat, kenaikan fraksi duplikat berarti mekanisme *one-to-one* terganggu;
- **Confidence Margin** CM (Pers. 3.7) — selisih kepercayaan prediksi pemenang dan runner-up; margin menipis berarti pemenang tidak lagi tunggal-jelas;
- **stabilitas *assignment* antar-epoch** — awalnya belum diformalkan (pending A-10), kini dirumuskan sebagai S(t) atas himpunan probe validasi tetap.

Fokus analisis adalah varian ber-P2 (V3, V5, V7, V8), karena penambahan lapisan P2 adalah intervensi arsitektural terbesar terhadap kepala deteksi. Rincian metrik, konvensi forward mentah kepala *one-to-one*, dan hasil sensitivitas τ ada di [analisis NMS-free](nmsfree-analysis.md).

## HAM dan Lapisan P2 adalah INSTRUMEN — bukan kebaruan

Ini aturan **paling sering dilanggar** dan pelanggarannya adalah cacat fatal yang akan ditandai penguji. Tegas:

- **HAM** (*Hybrid Attention Module*, kaskade atensi kanal→spasial) dan **Lapisan P2** (kepala deteksi resolusi tinggi stride-4 untuk objek kecil) adalah **komponen instrumental** yang dipinjam/diadaptasi dari literatur yang sudah ada. Keduanya dipakai untuk *memungkinkan* dan *menstres-uji* dua pilar kebaruan, bukan untuk diklaim sebagai temuan.
- Alasannya: YOLO26 **sudah** memiliki ProgLoss dan STAL, jadi mengklaim "kami menambahkan atensi" atau "kami menambahkan lapisan multi-skala" sebagai kebaruan akan langsung dipatahkan — atensi dan P2 sudah lazim di keluarga YOLO dan literatur objek kecil (HIC-YOLOv5, CRL-YOLOv5, MST-YOLO; semuanya *NMS-based*, lihat Tabel 2.1).
- **Framing yang benar:** HAM dan P2 diposisikan sebagai *instrumen* dalam desain faktorial 8 varian (HAM × P2 × DALW). Perannya adalah menyediakan konteks arsitektural agar kontribusi DALW (Pilar 1) dan interaksinya dengan mekanisme *NMS-free* (Pilar 2) dapat diisolasi lewat *ablation study*.

Konsekuensi praktis untuk penulisan: setiap kalimat yang menyebut HAM/P2 harus memakai bahasa instrumental ("digunakan", "diintegrasikan", "diadaptasi"), **tidak pernah** bahasa kebaruan ("kami mengusulkan", "kontribusi utama", "novel"). Detail masing-masing komponen (tetap dalam bingkai instrumen) ada di [HAM](ham.md) dan [Lapisan P2](p2-layer.md); aturan ini juga dikodekan di [invarian metodologi](../rules/methodology-invariants.md) dan [standar penulisan](../rules/writing-standards.md).

## STAL vs DALW — melengkapi, bukan menduplikasi

Pertanyaan yang pasti muncul di sidang: "Bukankah YOLO26 sudah punya STAL yang juga membobot objek? Apa bedanya dengan DALW?" Jawabannya harus jelas dan konsisten (mengacu Tabel 3.2 tesis): keduanya bekerja di **tahap yang berbeda** dan atas **dasar yang berbeda**, sehingga saling melengkapi alih-alih menduplikasi.

| Aspek | STAL (bawaan YOLO26) | DALW (kebaruan Pilar 1) |
|---|---|---|
| Tahap kerja | Penetapan label (*label assignment*) | Penghitungan *loss* (*loss aggregation*) |
| Dasar pembobotan | **Ukuran** objek | **Densitas** lokal antarobjek |
| Sumber sinyal | Statistik selama pencocokan anchor–GT | Jarak antar-pusat kotak *ground truth* |
| Status | Komponen bawaan (dipertahankan utuh) | Modifikasi baru yang diklaim |

Karena STAL menyeimbangkan berdasarkan **ukuran saat memilih anchor**, sedangkan DALW menyeimbangkan berdasarkan **densitas saat menjumlahkan *loss***, keduanya beroperasi pada dimensi ortogonal dan dapat aktif bersamaan tanpa saling meniadakan. Framing "melengkapi STAL" ini wajib dijaga; jangan pernah menyiratkan DALW menggantikan atau bertentangan dengan STAL. Verifikasi kode menunjukkan STAL (dan ProgLoss) tetap utuh saat DALW aktif — lihat uji T4 di [smoke test](../playbooks/run-experiment.md) dan pembahasan head penerima wᵢ (keputusan A-11) di [DALW](dalw.md).

> ⚠️ **Jangan pernah** memakai frasa lama "berbasis ukuran objek" untuk mendeskripsikan DALW. DALW **berbasis densitas**; "berbasis ukuran" justru menggambarkan STAL. Kekeliruan ini pernah ada di draf lama dan wajib dihindari di semua bab.

## Bahasa kehati-hatian *preprint* YOLO26

Rujukan primer YOLO26 (Sapkota et al., [7][8]) masih berupa **preprint arXiv yang belum melalui peninjauan sejawat** (*peer review*). Karena itu semua pernyataan tentang mekanisme internal YOLO26 — *dual-head NMS-free*, ProgLoss, STAL, MuSGD — harus ditulis dengan bahasa berhati-hati (Subbab 2.3.5, 2.9, dan 3.5): gunakan "dilaporkan", "menurut *preprint*", "diklaim penulis", bukan kalimat yang menganggapnya fakta mapan. Sikap ini juga melindungi klaim tesis: karena *baseline*-nya belum terverifikasi sejawat, verifikasi empiris terhadap kode nyata (yang justru dilakukan penelitian ini via instrumentasi *NMS-free*) menjadi kontribusi tersendiri.

## Diskrepansi judul — WAJIB dikonfirmasi ke pembimbing

Terdapat **dua versi judul yang berbeda** dan diskrepansi ini **belum boleh diselesaikan sendiri**. Catat keduanya apa adanya:

| Sumber | Judul | Penekanan |
|---|---|---|
| `CLAUDE.md` §1 (SSOT) | "MODIFIKASI DETEKTOR *NMS-FREE* YOLO26 DENGAN PEMBOBOTAN *LOSS* BERBASIS DENSITAS DAN PELACAKAN BYTETRACK UNTUK PENGHITUNGAN KENDARAAN *REAL-TIME* PADA LALU LINTAS HETEROGEN PADAT" | Menonjolkan "DETEKTOR *NMS-FREE*" + "PELACAKAN BYTETRACK"; **tidak** menaruh HAM/P2 di judul |
| Dokumen fisik `TESIS_BAB1-3_REVISI_PEMBIMBING` | "MODIFIKASI ARSITEKTUR YOLO26 MELALUI ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2, DAN PEMBOBOTAN *LOSS* BERBASIS DENSITAS UNTUK PENGHITUNGAN KENDARAAN *REAL-TIME* PADA LALU LINTAS HETEROGEN PADAT" | Menaruh "ATENSI HIBRIDA, DETEKSI MULTI-SKALA P2" di judul |

Perbedaan ini bukan sekadar gaya: versi dokumen fisik menempatkan HAM dan P2 di judul, yang berpotensi menegangkan aturan "HAM/P2 = instrumen, bukan kebaruan" (judul biasanya mengangkat kontribusi utama). Versi SSOT justru menonjolkan *NMS-free* dan ByteTrack yang selaras dengan dua pilar. **JANGAN memilih, menggabungkan, atau menyelaraskan sendiri.** Tandai sebagai item konfirmasi ke Naufal dan Ibu Sandfreni, dan lacak di [keputusan pending](../status/pending-decisions.md). Diskrepansi terkait lain (jumlah sitasi 27 vs [1]–[30], sumber dataset Roboflow, lokasi "RTX 3060" tersisa) juga dicatat di sana — jangan menetapkan angka final tanpa persetujuan.

## Rangkuman istilah wajib

- Istilah utama Indonesia: **"Pembobotan *Loss* Berbasis Densitas"** (narasi); **DALW** hanya di tabel dan nama varian.
- HAM = *Hybrid Attention Module*; P2 = lapisan/kepala deteksi resolusi tinggi. Keduanya **instrumen**.
- STAL = mekanisme *label assignment* berbasis ukuran bawaan YOLO26 (dipertahankan).
- Desimal dalam narasi memakai koma (mis. α=1,0; σ=0,1); nilai JSON/CLI apa adanya (`alpha=1.0`, `sigma=0.1`).

## Tautan terkait

| File | Isi |
|---|---|
| [00-overview.md](../00-overview.md) | Peta ringkas seluruh basis pengetahuan |
| [DALW](dalw.md) | Matematika Pilar 1, *monkey-patch* loss, head penerima wᵢ (A-11) |
| [Analisis NMS-free](nmsfree-analysis.md) | Pilar 2: DR, CM, stabilitas *assignment*, sensitivitas τ |
| [HAM](ham.md) | Modul atensi hibrida (instrumen) |
| [Lapisan P2](p2-layer.md) | Kepala deteksi objek kecil (instrumen) |
| [Dataset](dataset.md) | traffic-merged, *group split*, kelas & stratifikasi |
| [Evaluasi](evaluation.md) | Metrik deteksi & penghitungan, protokol strata |
| [Statistik](statistics.md) | Wilcoxon, Holm, *effect size*, grid search |
| [Invarian metodologi](../rules/methodology-invariants.md) | Aturan yang dikodekan (tak boleh dilonggarkan) |
| [Standar penulisan](../rules/writing-standards.md) | Gaya bahasa, aturan NEVER, format bab |
| [Keputusan pending](../status/pending-decisions.md) | Diskrepansi judul + 7 keputusan A-01…B-01 |
| [Progres eksperimen](../status/progress.md) | Status P1–P10 dan hasil utama |
