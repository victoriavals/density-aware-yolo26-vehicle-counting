# Kemajuan audit `web_katalog` — status per 14 Agu 2026

> Pelacak supaya pekerjaan ini dapat dilanjutkan lintas sesi tanpa mengulang.
> Perbarui setiap kali satu lembar selesai diperiksa.

## Ringkas

| Bagian | Klaster | Status |
|---|---|---|
| Klaster memuat citra **test** | 133 (145 citra) | ✅ **SELESAI** — diperiksa satu per satu, 6 lembar @390 px |
| Klaster **train/valid** | 1.319 | 🔄 **3 dari 21 lembar** (`sisa_00`–`sisa_02`, 192 klaster) |
| **Total** | 1.452 | — |

## Hasil yang sudah pasti

**Split test — pemeriksaan menyeluruh 145 citra:**

- **Nol render permainan.** Empat render yang diketahui ada di `train` (2) dan `valid` (2).
- **Nol citra bukan-lalu-lintas.**
- → **K3 (jalankan ulang tiga subset) TIDAK diperlukan.** Angka hasil tidak terpengaruh.
- **14 thumbnail YouTube** (`hqdefault-*`, `maxresdefault-*`), **seluruhnya di test**, memuat
  branding kanal, bilah letterbox, atau teks judul. Satu (`hqdefault-1`) memuat logo
  **"Grand Theft Auto San Andreas"** — diperiksa pada resolusi asli: **pikselnya foto nyata**
  bus Damri, bukan render. Persoalannya atribusi, bukan keabsahan konstruk.
- **Tanda air situs banyak dijumpai**, jauh di atas perkiraan sampel 5 %. Yang terbaca:
  TJAP BOEMEL · AUTO VIT · OTO BLITZ · ercal trucks · KABAR JOMBANG.COM ·
  CaribbeanEquipmentTraders.com · Dot Sticker · Autonetmagz.com · JIBI Photo ·
  @FernwoodCommercials · rumah lelang armada · satu promo pemasok Tiongkok ber-WhatsApp.

**Lembar `sisa_00` (W000–W072, 64 klaster train/valid):** seluruhnya foto nyata, tanpa render.
Dua tanda air terbaca: satu "OK TRUCKS", satu berlogo pustaka stok (Dreamstime).

## Cara melanjutkan

Lembar: `anotasi_web/sisa/sisa_00.jpg` … `sisa_20.jpg` (64 perwakilan per lembar, 210 px).
Label merah = id klaster + jumlah anggota.

⚠️ **Untuk klaster yang mencurigakan, WAJIB buka potongan resolusi asli** di
`anotasi_web/crop/W###.jpg`. Miniatur punya negatif palsu untuk tanda air berkontras rendah —
itu kekeliruan yang sudah terjadi sekali pada klip Seoul (Keputusan 5).

Catat hasilnya di `anotasi_web/TEMPLAT_ANOTASI.csv`, lalu:

```bash
python audit_web_katalog.py --rekap anotasi_web/TEMPLAT_ANOTASI.csv
```

Rekap akan menolak selesai bila masih ada klaster berstatus kosong, dan menyatakan sendiri
apakah K3 diperlukan.

## Catatan kejujuran

Pada pemeriksaan split test saya mencatat **temuan agregat** (nol render, nol bukan-lalu-lintas,
daftar tanda air yang terbaca) tetapi **tidak mencatat status per klaster satu per satu**.
Untuk keperluan naskah itu memadai — yang menentukan adalah ada/tidaknya render dan citra
bukan-lalu-lintas di split test, dan jawabannya nol. Untuk **angka lisensi yang pasti**,
status per klaster masih perlu diisi.

## Log lembar

| Lembar | Klaster | Diperiksa | Temuan |
|---|---|---|---|
| test_00–05 | 133 klaster / 145 citra | ✅ 13 Agu 2026 | 0 render · 0 bukan-lalu-lintas · 14 thumbnail YouTube · banyak tanda air situs |
| sisa_00 | W000–W072 | ✅ 14 Agu | 0 render · 2 tanda air (OK TRUCKS, pustaka stok) |
| sisa_01 | W073–W145 | ✅ 14 Agu | 1 render **yang sudah diketahui** (Bandung Express simulator) · tanda air SURYAMALANG, KOMPAS.com, BUS TV INDO, Pickles, dealer Jepang-Eropa |
| sisa_02 | W146–W209 | ✅ 14 Agu | 0 render · tanda air autokid, Pickles, KEL-BERG |
| sisa_03 … sisa_20 | sisanya (18 lembar) | ⬜ belum | — |

**Pola sejauh ini (192 klaster train/valid diperiksa):** nol render BARU di luar 4 yang sudah
diketahui dari pola nama; tanda air situs penjual/kanal **umum dijumpai** dan jelas melebihi
perkiraan sampel 5 %. Angka pastinya baru dapat dinyatakan setelah 18 lembar sisa selesai.
