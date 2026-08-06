# 11 — Analisis Galat (Subbab 4.11)

> Dibangkitkan `y26_bangun_hasil_bab45.py` → `bab_11_analisis_galat()`. Seluruh angka
> dihitung dari `eval_out/cache_V*.npz` — objek yang sama dengan yang dipakai AP
> terstratifikasi (Subbab 4.5), sehingga konsisten dengan hasil ablasi.
> Ambang: IoU 0,50, keyakinan 0,25 (sama dengan default `y26_counting.py`).

Subbab ini adalah satu-satunya bagian BAB 4 yang sebelumnya **tidak memiliki data sama
sekali**. Matriks kekeliruan bawaan Ultralytics di `runs_tesis/<V>/confusion_matrix.png`
dihitung pada *split* **validasi** saat pelatihan, bukan pada *split* uji — karena itu tidak
dapat dipakai untuk BAB 4.

## Berkas

| Berkas | Isi |
|---|---|
| `matriks_kekeliruan_<V>.csv` + `grafik_matriks_kekeliruan_<V>.png` | matriks 5×5 (4 kelas + latar) pada data uji, V1/V5/V8 |
| `dekomposisi_fp_fn.csv` + `grafik_fn_per_strata_<dim>.png` | objek terlewat, salah kelas, dan prediksi palsu per strata |
| `galat_per_kelas.csv` + `grafik_fn_per_kelas.png` | laju objek terlewat per kelas |
| `galat_siang_malam.csv` | dekomposisi siang/malam |
| `kasus_kegagalan.csv` + `grafik_kasus_kegagalan.png` | 10 citra terburuk; montase 3 teratas (hijau: GT, merah putus-putus: prediksi) |

## Temuan 1 — Model penuh menurunkan objek terlewat di **seluruh** strata

| Strata | V1 terlewat | V8 terlewat |
|---|---|---|
| ukuran kecil | 32,63 % | **29,53 %** |
| ukuran sedang | 17,47 % | **15,33 %** |
| ukuran besar | 8,75 % | **4,17 %** |
| oklusi tanpa | 22,34 % | **19,75 %** |
| oklusi parsial | 32,70 % | **28,30 %** |
| densitas *sparse* | 15,46 % | **14,68 %** |
| densitas *medium* | 26,21 % | **22,63 %** |
| densitas *dense* | 28,18 % | **26,36 %** |

Total objek terlewat turun dari **614 menjadi 541** dari 2.600 objek uji (23,6 % → 20,8 %).
Perbaikan ini **konsisten arah di semua strata** — berbeda dari AP terstratifikasi yang
campuran, dan itu bukan kontradiksi: AP menggabungkan presisi dan *recall*, sedangkan tabel
ini hanya sisi *recall*.

## Temuan 2 — Perbaikan itu **dibayar dengan prediksi palsu**

| Strata | V1 prediksi palsu | V8 prediksi palsu |
|---|---|---|
| ukuran kecil | 553 | **638** (+15,4 %) |
| densitas *medium* | 624 | **696** (+11,5 %) |
| ukuran sedang | 325 | 309 |

Inilah penjelasan mekanistik mengapa **presisi V8 justru lebih rendah** dari V1 (78,06 % vs
79,44 %) meski mAP@0,5:0,95-nya sedikit lebih tinggi: model penuh **mendeteksi lebih banyak**,
termasuk lebih banyak yang salah, terutama pada objek kecil di adegan padat.

Ini konsisten dengan mekanisme DALW: memberi bobot lebih besar pada objek di wilayah padat
menaikkan sensitivitas di wilayah itu, dan sensitivitas yang naik membawa serta prediksi
palsu. Layak dinyatakan terbuka sebagai *trade-off* yang terukur, bukan disembunyikan.

⚠️ Prediksi palsu **tidak dapat distratifikasi menurut oklusi** — proksi Pers. 3.1 memerlukan
pasangan *ground truth* yang menurut definisi tidak dimiliki prediksi palsu. Kolom
`n_fp_prediksi` sengaja dikosongkan untuk dimensi oklusi, bukan bernilai nol.

## Temuan 3 — Roda dua adalah kelas terlemah, sesuai premis BAB 1

| Kelas | n objek uji | V8 terlewat |
|---|---|---|
| **roda dua** | 865 | **270 (31,2 %)** |
| mobil | 765 | 133 (17,4 %) |
| kendaraan besar | 332 | 53 (16,0 %) |
| pejalan kaki | 638 | 85 (13,3 %) |

Roda dua adalah kelas **mayoritas sekaligus paling sering terlewat**. Ini mendukung premis
BAB 1 (dominasi objek kecil 8–16 piksel) secara langsung, dan menjelaskan mengapa galat
penghitungan pada RQ5 juga paling besar secara absolut pada kelas ini meski persentasenya
paling baik (kelas dengan volume terbesar).

## Temuan 4 — Galat terkonsentrasi pada adegan **malam**

| Kelompok | Citra | Objek GT | V1 terlewat | V8 terlewat |
|---|---|---|---|---|
| malam | 129 (38,2 %) | 1.880 (72,3 %) | 26,76 % | **24,73 %** |
| siang | 209 (61,8 %) | 720 (27,7 %) | 15,42 % | **10,56 %** |

Laju objek terlewat pada adegan malam **2,3 kali** adegan siang. Menariknya, perbaikan V8 atas
V1 jauh lebih besar pada siang (−4,86 poin) daripada malam (−2,03 poin) — modifikasi membantu,
tetapi **tidak menutup celah pencahayaan**.

Ketiga kasus kegagalan terburuk (`kasus_kegagalan.csv`) seluruhnya citra malam dari rangkaian
`night-traffic-9`. Penanda malam diambil dari nama berkas Roboflow, bukan analisis citra —
sederhana dan dapat diperiksa ulang.

⚠️ Adegan malam menyumbang **72,3 % objek uji** meski hanya 38,2 % citra, karena adegan malam
pada dataset ini lebih padat. Artinya metrik global tesis ini **didominasi kondisi malam** —
fakta yang perlu disebut saat menafsirkan seluruh angka BAB 4, dan yang tidak terlihat dari
metrik agregat mana pun.

## Bahan BAB 5 (saran)

Tiga arah yang muncul langsung dari data ini: penanganan kondisi cahaya rendah (augmentasi
khusus malam atau kanal inframerah), penekanan prediksi palsu pada objek kecil di adegan
padat, dan penguatan kelas roda dua yang paling sering terlewat meski paling banyak jumlahnya.

## Catatan reproduksi

```bash
./.venv/Scripts/python.exe -c "import y26_bangun_hasil_bab45 as g; g.bab_11_analisis_galat()"
```

Varian default V1/V5/V8 (baseline, HAM+P2, model penuh) — cukup untuk menjelaskan H1 dan H3.
Tambahkan varian lain lewat argumen `variants=(...)` bila diperlukan.
