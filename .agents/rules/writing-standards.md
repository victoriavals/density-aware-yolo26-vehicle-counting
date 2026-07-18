# Standar Penulisan Naskah — Thesis Manuscript Writing Standards

> **EN — TL;DR:** Formatting and prose rules for the thesis manuscript (`.docx`), not for this KB file. Indonesian formal-academic prose, Times New Roman 12pt / 1,5 spacing, left margin 4 cm (others 3 cm), 1 cm first-line indent, IEEE bracket citations in first-appearance order, **pure prose body — no bullets/numbering**, foreign terms italicized (except product names YOLO26/ByteTrack/Roboflow), comma decimals, and human-varied sentences to avoid AI-detection patterns. Never claim HAM or the P2 layer as novelty; keep the two-pillar framing and *preprint* caution intact.

Berkas ini merangkum standar penulisan **naskah tesis** (dokumen `.docx`: halaman judul, ABSTRAK/ABSTRACT, BAB 1–5, Daftar Pustaka, Lampiran) sebagaimana ditetapkan pada `CLAUDE.md` §11. Aturan di sini **tidak** berlaku untuk berkas basis pengetahuan `.agents/` — KB justru wajib memakai format bilingual (H1 dua bahasa, blockquote *TL;DR*, tabel, dan tautan) yang dilarang di badan naskah. Bila keduanya tampak bertentangan, ingat konteksnya: prosa murni untuk naskah, format terstruktur untuk KB.

## Spesifikasi tata letak

Parameter berikut mengikat untuk seluruh dokumen naskah dan harus konsisten dari halaman judul hingga lampiran.

| Aspek | Ketentuan |
|---|---|
| Bahasa | Indonesia akademik formal (baku, lugas, impersonal) |
| Fon | Times New Roman, 12pt |
| Spasi baris | 1,5 |
| Margin | Kiri 4 cm; atas, kanan, dan bawah masing-masing 3 cm |
| Indentasi | Baris pertama tiap paragraf menjorok 1 cm |
| Desimal | Memakai koma (mis. 0,6670; α = 1,0; σ = 0,1) |
| Sitasi | IEEE *bracket* `[n]`, dinomori urut kemunculan pertama |

Catatan margin: `CLAUDE.md` §11 menuliskan notasi "3-3-3-4 cm (kiri 4 cm)". Notasi urutan sisi dapat berbeda antar sumber, tetapi maknanya tetap satu — sisi kiri 4 cm, tiga sisi lain 3 cm. Pakai disambiguasi "(kiri 4 cm)" itu sebagai acuan bila ada keraguan urutan.

## Gaya prosa (aturan paling sering dilanggar)

Badan naskah adalah **prosa murni tanpa *bullet* maupun penomoran**. Daftar berpoin, penomoran langkah, dan potongan tabel-dalam-kalimat tidak boleh muncul di teks berjalan; ubah menjadi kalimat yang mengalir. Tabel dan gambar resmi tetap diizinkan sebagai elemen bernomor (Tabel 3.x, Gambar 3.x) dengan narasi pengantar dan penutup, bukan sebagai pengganti paragraf.

Istilah asing dan teknis dicetak *miring* pada kemunculan yang relevan (*loss*, *one-to-one*, *NMS-free*, *baseline*, *grid search*, *early stopping*, *two-wheeler*, dan sejenisnya). Pengecualian adalah nama produk yang ditulis tegak apa adanya: YOLO26, ByteTrack, Roboflow. Singkatan komponen mengikuti aturan istilah: sebutan naratif utama adalah "Pembobotan *Loss* Berbasis Densitas", sedangkan akronim DALW hanya dipakai di tabel dan nama varian (V4, V6, V7, V8). HAM dan Lapisan P2 boleh disebut namanya, tetapi selalu sebagai *instrumen*, bukan klaim kebaruan.

Gaya bahasa harus terbaca alami dan manusiawi untuk menghindari pola khas hasil AI: variasikan panjang dan struktur kalimat, hindari pembuka paragraf yang berulang, jangan menumpuk kalimat berpola identik, dan sebisa mungkin sambungkan gagasan dengan transisi yang beragam. Konsistensi istilah tetap dijaga, tetapi bukan dengan mengulang frasa yang sama secara mekanis.

## Angka desimal: naskah vs kode

Di narasi naskah semua desimal memakai koma: mAP@0,5:0,95 = 0,6670, α = 1,0, σ = 0,1, τ = 0,25, p = 0,0125, r = +0,486. Nilai yang berasal dari berkas JSON, argumen CLI, atau keluaran skrip ditulis apa adanya dengan titik saat merujuk artefak teknis (mis. `dalw_best.json` berisi `0.6670`, flag `--tune-epochs 60`). Bila menyandingkan keduanya, jelaskan bahwa itu nilai yang sama dalam dua konvensi penulisan.

## Konsistensi framing (wajib, lihat aturan NEVER)

Penulisan harus mempertahankan **framing dua pilar** tanpa perubahan: kebaruan metodologis pada Pembobotan *Loss* Berbasis Densitas dan kebaruan analitis pada penyelidikan interaksi modifikasi dengan mekanisme *one-to-one NMS-free*. HAM dan Lapisan P2 **tidak pernah** boleh dibingkai sebagai kebaruan; keduanya adalah instrumen, dan setiap peningkatan diframe sebagai perbaikan atas *baseline* YOLO26 yang sudah kuat (sudah memiliki ProgLoss + STAL). Rujukan YOLO26 (Sapkota et al.) harus dijaga dalam bahasa kehati-hatian karena masih *preprint* arXiv dan belum melewati *peer-review*; pertahankan nada ini terutama di subbab 2.3.5, 2.9, dan 3.5. Latar konsep ini dijelaskan pada [Framing kebaruan tesis](../knowledge/thesis-framing.md).

Larangan editorial yang menyertai penulisan: jangan mengisi atau mengubah placeholder ([XX,X], [0,0XX], dsb.) tanpa data eksperimen nyata; jangan menggeser, menambah, atau menghapus nomor sitasi; dan jangan menulis draf BAB 4–5 di dalam KB. Peta placeholder dan tugas naskah dilacak di [Document TODOs](../status/document-todos.md).

## Item verifikasi terbuka (jangan diputus sendiri)

Terdapat diskrepansi jumlah referensi yang **belum boleh diselesaikan sepihak** dan harus dikonfirmasi ke Naufal serta pembimbing sebelum finalisasi Daftar Pustaka:

| Sumber | Klaim jumlah sitasi |
|---|---|
| `CLAUDE.md` §9 (SSOT) | 27 referensi (`[1]`–`[27]`), urut kemunculan pertama, semua ber-URL/DOI (kecuali Wilcoxon 1945 *paywalled* di JSTOR) |
| Dokumen fisik REVISI_PEMBIMBING | Daftar Pustaka memuat `[1]`–`[30]` |

Selama diskrepansi ini terbuka, jangan menetapkan angka akhir jumlah sitasi maupun menomori ulang entri; tandai sebagai item verifikasi. Ketidaksesuaian serupa (judul tesis SSOT vs dokumen fisik, sumber *workspace* Roboflow, dan lokasi "RTX 3060" yang harus menjadi "RTX 4060 Ti 8GB") juga hanya di-*surface*, bukan diresolusi otomatis — lihat [Keputusan pending](../status/pending-decisions.md) dan [Document TODOs](../status/document-todos.md).

## Aturan terkait

Standar penulisan ini berlaku bersama aturan kerja umum proyek — konfirmasi keputusan besar ke Naufal, jaga konsistensi lintas bab, jangan menyentuh 7 keputusan pending tanpa persetujuan — yang dirinci di [Aturan kerja](../rules/working-rules.md). Invarian metodologis yang tidak boleh dilonggarkan saat menuliskan hasil (unit Wilcoxon, aturan MAPE y>0, dan lainnya) ada di [Invarian metodologi](../rules/methodology-invariants.md).
