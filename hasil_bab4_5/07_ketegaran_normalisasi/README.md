# 07 — Pemeriksaan Ketegaran: Normalisasi-per-Bobot

Menjawab Subbab 3.6.3 — pemeriksaan yang dijanjikan naskah untuk memastikan peningkatan
performa DALW bukan sekadar efek kenaikan skala loss pada citra padat.

## ⏳ STATUS: BELUM LENGKAP — training V8_normw masih berjalan

`tabel_perbandingan_normalisasi.csv` sudah dibuat, namun baris `V8_normw` masih
berstatus **"MASIH BERJALAN"** — **jangan mengutip angkanya sebagai final.** Jalankan
ulang generator (`y26_bangun_hasil_bab45.py`, fungsi `bab_07_ketegaran`) setelah
training selesai untuk mendapat angka final.

## Latar belakang metodologis

Bentuk normalisasi resmi naskah (Pers. 3.5) membagi loss dengan **jumlah objek** (N),
sehingga skala total loss ikut naik pada citra padat — ini **penguatan yang
dikehendaki**. Bentuk alternatif (`V8_normw`) membagi dengan **jumlah bobot** (Σwᵢ),
mempertahankan skala loss tetapi menghapus penguatan absolut tersebut. Bila performa
V8_normw jauh lebih rendah dari V8, itu mengindikasikan sebagian gain DALW berasal dari
efek skala loss (laju pembelajaran efektif), bukan murni sinyal densitas.

## Cara membaca tabel setelah training selesai

Bandingkan `mAP50_95_val_terbaik` V8 vs V8_normw:
- **Selisih kecil** → gain DALW murni dari sinyal densitas, robust terhadap pilihan
  normalisasi.
- **Selisih besar (V8 >> V8_normw)** → sebagian gain berasal dari efek skala loss;
  harus diakui terbuka di BAB 4/5 sebagai nuansa kontribusi metodologis.

## Kalimat siap-adaptasi (ISI ULANG setelah angka final tersedia)

> "Pemeriksaan ketegaran dengan mengganti pembagi loss dari jumlah objek menjadi jumlah
> bobot — yang menghapus penguatan skala pada citra padat namun mempertahankan sinyal
> pembobotan densitas — menghasilkan mAP@0,5:0,95 validasi sebesar [ISI], dibandingkan
> [ISI] pada bentuk baku (Persamaan 3.5), mengindikasikan bahwa [gain berasal murni
> dari sinyal densitas / sebagian gain berasal dari efek skala loss — pilih sesuai hasil]."

⚠️ **JANGAN mengisi placeholder [ISI] di atas sebelum training benar-benar tuntas dan
angka diverifikasi ulang** — sesuai aturan proyek (§12.3): tidak mengisi placeholder
tanpa data eksperimen nyata.
