# Playbook: Validasi Oklusi Manual (P8) — Manual Occlusion Validation

> **EN — TL;DR:** Validate the IoU occlusion proxy (Eq. 3.1) against human judgement (subbab 3.3.3). `make_oklusi_sample.py` builds `anotasi_oklusi/` — blind, tier-balanced, deterministic crops + `anotasi.html`. Naufal annotates → exports `manual_oklusi.csv` (`image,gt_index,tier`) → an agreement pass compares proxy vs manual. **Key finding:** the `heavy` tier (o≥0.35) is nearly empty in val, so it drops out of the Wilcoxon cells; the 0.10/0.35 edges are **locked**, and any change waits on the agreement number + supervisor discussion.

Berkas sumber: `make_oklusi_sample.py`; `CLAUDE.md` §15 (prep P8). Subbab tesis 3.3.3.

## Tujuan

Proksi oklusi Pers. 3.1 (`oᵢ = maxⱼ≠ᵢ IoU`) diturunkan otomatis, tetapi validitasnya perlu diuji terhadap penilaian **manusia** yang independen. `make_oklusi_sample.py` hanya **menyiapkan** bahan (tidak menganotasi).

## Langkah

```bash
# 1) Bangun sampel crop terstratifikasi (blind, deterministik via md5)
python make_oklusi_sample.py --data dataset/data.yaml --n 300
```

Menghasilkan `anotasi_oklusi/`: crop per objek (kotak target merah tebal, tetangga kuning tipis, margin konteks), `sample_manifest.csv` (kolom proksi hanya untuk lampiran — **jangan dilihat saat menganotasi**), dan `anotasi.html`.

2. Buka `anotasi_oklusi/anotasi.html` di browser → nilai tiap crop (klik/keyboard; tier proksi **tidak** ditampilkan — *blind*) → **Ekspor CSV** `manual_oklusi.csv` (format persis `image,gt_index,tier`, tier ∈ {no, partial, heavy}).
3. Pindahkan `manual_oklusi.csv` ke root repo, lalu jalankan agregasi *agreement* (`occlusion_agreement` di `y26_strata`).

Kit siap (prep P8, 16 Jul): ~200 crop val, seimbang tier (100 no + 100 partial) & kelas, deterministik. Waktu anotasi ±20–30 menit.

## ⚠️ Temuan penting (bahan diskusi BAB 4)

Tier `heavy` (o≥0,35) **nyaris kosong**: val 0/4.094 (maks 0,286), test 8/2.600, train 62/16.786. Indikasi proksi box-IoU **meremehkan** oklusi perseptual → strata heavy gugur dari sel Wilcoxon di val. Ambang **0,10/0,35 TERKUNCI**; keputusan (bila perlu) menunggu angka *agreement* + diskusi pembimbing. Lihat [Evaluasi](../knowledge/evaluation.md) & [Keputusan pending](../status/pending-decisions.md).

## Tautan terkait

- [Evaluasi (strata & AP)](../knowledge/evaluation.md) · [Dataset](../knowledge/dataset.md) · [Keputusan pending](../status/pending-decisions.md) · [Progres](../status/progress.md).
