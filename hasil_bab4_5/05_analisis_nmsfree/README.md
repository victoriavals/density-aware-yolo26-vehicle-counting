# 05 — Analisis Interaksi dengan Paradigma NMS-free

Menjawab RQ1 & RQ3 dan Subbab 3.7 — kebaruan analitis tesis: penyelidikan empiris
bagaimana Lapisan P2 dan Modul Atensi Hibrida berinteraksi dengan mekanisme
pencocokan *one-to-one*.

## Berkas

| Berkas | Isi |
|---|---|
| `summary.csv` | DR, CM, coverage per varian ber-P2 (V3/V5/V7/V8) vs V1, pada τ=0,25 |
| `tau_sweep.csv` | Duplicate Rate pada 12 nilai τ (0,05–0,90), kelima varian |
| `grafik_dr_cm_ringkasan.png` | Duplicate Rate & Confidence Margin, ringkas per varian |
| `grafik_tau_sweep_ulang.png`, `dr_vs_tau.png` | Kurva sensitivitas DR terhadap ambang τ (dua versi: dibuat ulang & asli dari `analyze_nmsfree.py`) |
| `cm_hist.png` | Histogram distribusi Confidence Margin (dari `analyze_nmsfree.py`) |
| `grafik_stabilitas_assignment.png` | **Baru** — S(t) (Pers. 3.8) per epoch selama pelatihan, kelima varian |

## Cara membaca

**DR (Duplicate Rate)**: idealnya mendekati 1,0 (satu prediksi dominan per objek).
V5 dan V8 (ber-HAM) di atas V1 baseline (+0,047 dan +0,055); V3 dan V7 (P2 tanpa HAM)
di bawah baseline (−0,058 dan −0,017). **Pola konsisten: HAM menstabilkan, P2 sendiri
sedikit mengganggu.**

**CM (Confidence Margin)**: margin lebih besar = pemenang lebih jelas. Pola sama —
naik pada varian ber-HAM (V5 +0,045, V8 +0,031), turun pada P2-tanpa-HAM (V3 −0,043,
V7 −0,024).

**Stabilitas S(t)**: mendekati 1,0 di akhir pelatihan untuk semua varian → mekanisme
penetapan anchor **konvergen dan stabil**, tidak ada tanda kegagalan pencocokan
kronis meski P2 menambah ~4× titik anchor.

## Angka kunci (τ=0,25, dari `summary.csv`)

| Varian | DR | ΔDR vs V1 | CM mean | ΔCM vs V1 |
|---|---|---|---|---|
| V1 | 0,778 | — | 0,548 | — |
| V3 (P2) | 0,720 | −0,058 | 0,506 | −0,043 |
| V5 (HAM+P2) | 0,825 | +0,047 | 0,593 | +0,045 |
| V7 (P2+DALW) | 0,761 | −0,017 | 0,524 | −0,024 |
| **V8 (penuh)** | **0,833** | **+0,055** | 0,579 | +0,031 |

## Kalimat siap-adaptasi

> "Analisis interaksi dengan mekanisme pencocokan one-to-one menunjukkan bahwa
> penambahan Lapisan Deteksi P2 tanpa disertai Modul Atensi Hibrida cenderung
> menurunkan Duplicate Rate dan Confidence Margin dibandingkan baseline (V3: ΔDR=−0,058,
> ΔCM=−0,043), sedangkan kombinasi dengan Modul Atensi Hibrida secara konsisten
> membalikkan tren tersebut (V5: ΔDR=+0,047, ΔCM=+0,045; V8: ΔDR=+0,055, ΔCM=+0,031),
> mengindikasikan bahwa modul atensi berperan menstabilkan mekanisme pencocokan yang
> berpotensi terganggu oleh peningkatan kepadatan prediksi dari lapisan deteksi
> tambahan. Stabilitas assignment antar-epoch konvergen menuju nilai mendekati satu
> pada seluruh varian, menunjukkan tidak terjadi kegagalan pencocokan yang kronis."

## Catatan reproduksi

`grafik_stabilitas_assignment.png` dibaca dari `runs_tesis/<V>/nmsfree_probe.csv` —
probe tetap 64 citra validasi, direkam tiap akhir epoch selama pelatihan V1–V8
(P5). Nilai epoch 1 kosong (S(t) tidak terdefinisi tanpa pembanding epoch
sebelumnya, sesuai definisi Pers. 3.8).
