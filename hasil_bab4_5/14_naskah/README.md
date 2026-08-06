# 14 — Naskah BAB IV dan BAB V

`TESIS_BAB4-5.docx` — naskah jadi, terpisah dari BAB 1–3.

| Aspek | Nilai |
|---|---|
| Isi | BAB IV (13 subbab) + BAB V (4 subbab) + 13 lampiran |
| Ukuran | 15 tabel, 24 gambar, ±6.700 kata badan bab |
| Penomoran | Tabel 4.1–4.15, Gambar 4.1–4.24 (melanjutkan Tabel 3.10 / Gambar 3.7 pada BAB 1–3) |
| Sitasi baru | [31]–[33], tidak menggeser [1]–[30] |
| Format | A4, margin 3-3-4-3 cm, Times New Roman 12 pt, spasi 1,15, indentasi baris pertama 1 cm — diverifikasi terhadap `TESIS_BAB1-3_REVISI_SIDANG_v7.docx` |

## Dibangkitkan program, bukan diketik

```bash
./.venv/Scripts/python.exe y26_tulis_bab45.py
```

Modul: `y26_tulis_bab45.py` (gaya dan pembantu), `y26_bab4_isi.py` (Subbab 4.1–4.9),
`y26_bab45_lanjutan.py` (Subbab 4.10–4.13 dan BAB V), `y26_lampiran.py` (13 lampiran).
Seluruh angka diinjeksi dari berkas hasil di folder induk, sehingga naskah dapat dibangun
ulang setiap kali ada data yang berubah.

## Yang masih harus dikerjakan manual

Rujukan **[31]–[33] wajib dimasukkan melalui Mendeley**, bukan diketik langsung di Word,
karena daftar pustaka naskah dikelola sebagai *field* dan akan tertimpa saat disegarkan.
Entri lengkapnya ada pada Lampiran 12 di dalam dokumen. Selain itu perlu pemeriksaan
penempatan gambar setelah dibuka di Word dan penyesuaian nomor halaman lanjutan.
