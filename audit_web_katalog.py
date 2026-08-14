#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_web_katalog.py — audit menyeluruh 1.597 citra kategori `web_katalog`.

Latar. Sampel acak 60 citra menemukan 3 citra bertanda air penjual (5,0 %). Terpisah dari
itu, pencarian pola nama berkas atas SELURUH 1.597 citra menemukan 4 render permainan video.
Keduanya menyentuh keabsahan data, bukan sekadar komposisi, sehingga tidak dapat dilaporkan
sebagai hasil sampel maupun sebagai hasil pencarian nama.

⚠️ KOREKSI PREMIS (13 Agu 2026). Dokumen keputusan menyebut "4 dari 60 citra, yaitu 6,7 %,
ekstrapolasi sekitar 107". Itu keliru membaca laporan: angka 4 adalah hitungan **populasi
penuh** lewat regex nama berkas, bukan hasil sampel; hanya 1 dari 4 yang kebetulan jatuh di
sampel 60 (laju sampel 1,7 %). Auditnya tetap wajib, tetapi alasannya berbeda: pencarian nama
hanya menangkap render yang namanya MENYEBUT simulator/game. Render bernama netral tidak
tertangkap, dan jumlahnya itulah yang belum diketahui.

Metode. Sama dengan `audit_watermark_frame.py`: pengelompokan pHash lalu pemeriksaan satu
perwakilan per klaster, ditambah potongan resolusi asli untuk tanda air berkontras rendah
(pelajaran Keputusan 5 — miniatur punya negatif palsu pada adegan terang). Ditambah penyaring
nama berkas untuk pola yang sudah teridentifikasi, karena murah dan menangkap klaster tunggal.

TIGA PERBAIKAN atas naskah skrip yang disertakan pembimbing, seluruhnya terverifikasi:

  1. pHash — `d[1:].flatten()` membuang seluruh BARIS pertama (8 koefisien), bukan hanya
     koefisien DC. Terukur: 30 dari 40 citra menghasilkan hash berbeda dari `uji_phash.py`,
     sehingga hasilnya tidak sebanding dengan Fase 2 dan `audit_watermark_frame.py`.
     Diperbaiki menjadi `v = d.flatten(); med = np.median(v[1:])`, konsisten ketiga skrip.

  2. Klasterisasi — *bucketing* pada potongan 16 bit mensyaratkan dua citra berbagi 16 bit
     yang sama persis, padahal pada ambang Hamming 12 perbedaan tersebar. Terukur pada 1.597
     citra: ambang 12 → **178 pasangan sebenarnya, hanya 79 tertangkap, 99 TERLEWAT (55,6 %)**.
     Akibatnya klaster terpecah dan sebuah klaster tercemar dapat memiliki perwakilan yang
     tampak bersih. Diganti perbandingan penuh tervektor (1,27 juta pasangan, hitungan detik).

  3. Pencarian berkas — `rglob()` per citra diganti indeks nama sekali jalan. (Catatan jujur:
     dugaan awal bahwa ini masalah kinerja TIDAK terbukti — satu `rglob` hanya 5 ms, total
     ±8 dtk. Diperbaiki karena lebih rapi, bukan karena lambat.)

Antarmuka, nama berkas keluaran, dan kosakata status DIPERTAHANKAN persis seperti aslinya.

Keluaran.
  anotasi_web/klaster_web.csv          daftar klaster beserta anggotanya
  anotasi_web/lembar_kontak_*.jpg      lembar kontak perwakilan klaster, untuk diperiksa mata
  anotasi_web/crop/W###.jpg            potongan resolusi asli, untuk tanda air berkontras rendah
  anotasi_web/kandidat_render.csv      hasil penyaring nama berkas
  anotasi_web/TEMPLAT_ANOTASI.csv      diisi tangan setelah pemeriksaan mata

Cara pakai.
  python audit_web_katalog.py --dataset dataset --provenans provenans.csv
  # periksa lembar kontak dan potongan, isi TEMPLAT_ANOTASI.csv, lalu:
  python audit_web_katalog.py --rekap anotasi_web/TEMPLAT_ANOTASI.csv
"""
import argparse
import csv
import pathlib
import sys
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw
from scipy.fft import dct

# pola nama berkas render permainan yang sudah teridentifikasi mata
POLA_RENDER = [
    'ukts', 'bus_simulator', 'bus-simulator', 'simulator-indonesia',
    'game-simulasi', 'game_simulasi', 'simulasi-mengemudi', 'ets2', 'euro-truck',
]
# pola nama berkas yang menandakan iklan penjual, kandidat tanda air situs
POLA_PENJUAL = [
    'ok-trucks', 'oktrucks', 'bigvan', 'big-van', 'truckscorner', 'autoline',
    'mascus', 'trucksnl', 'kleyn', 'dealer',
]
STATUS_SAH = ('bersih', 'watermark_stok', 'watermark_penjual',
              'render_permainan', 'bukan_lalu_lintas')

LUT = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)


def phash64(path, ukuran=32, potong=8):
    """pHash 64 bit tanpa dependensi imagehash.

    PERBAIKAN 1: median dihitung atas seluruh koefisien KECUALI DC saja (`v[1:]`),
    sama seperti `uji_phash.py` dan `audit_watermark_frame.py`. Naskah asli memakai
    `d[1:]` yang membuang seluruh baris pertama (8 koefisien) sehingga hash-nya
    tidak sebanding antar-skrip.
    """
    im = Image.open(path).convert('L').resize((ukuran, ukuran), Image.Resampling.LANCZOS)
    a = np.asarray(im, dtype=np.float64)
    d = dct(dct(a, axis=0, norm='ortho'), axis=1, norm='ortho')[:potong, :potong]
    v = d.flatten()
    med = np.median(v[1:])
    out = np.uint64(0)
    for b in (v > med):
        out = np.uint64(out << np.uint64(1)) | np.uint64(bool(b))
    return int(out)


def klasterisasi(item, ambang=12):
    """Union-find atas jarak Hamming <= ambang, perbandingan PENUH tervektor.

    PERBAIKAN 2: naskah asli mem-*bucket* pada potongan 16 bit dan melewatkan 55,6 %
    pasangan pada ambang 12 (terukur, 1.597 citra). Untuk n sebesar ini perbandingan
    penuh hanya 1,27 juta operasi dan selesai dalam hitungan detik.
    """
    n = len(item)
    H = np.array([it['phash'] for it in item], dtype=np.uint64)
    induk = list(range(n))

    def cari(x):
        while induk[x] != x:
            induk[x] = induk[induk[x]]
            x = induk[x]
        return x

    for i0 in range(0, n, 512):
        blok = H[i0:i0 + 512]
        x = np.bitwise_xor(blok[:, None], H[None, :])
        D = LUT[x.view(np.uint8).reshape(*x.shape, 8)].sum(-1)
        for i, j in zip(*np.where(D <= ambang)):
            a, b = cari(i0 + int(i)), cari(int(j))
            if a != b:
                induk[b] = a

    grup = defaultdict(list)
    for i in range(n):
        grup[cari(i)].append(i)
    return list(grup.values())


def lembar_kontak(paths, label, keluar, kolom=6, sel=260):
    baris = (len(paths) + kolom - 1) // kolom
    kanvas = Image.new('RGB', (kolom * sel, baris * (sel + 18)), 'white')
    dr = ImageDraw.Draw(kanvas)
    for k, (p, lb) in enumerate(zip(paths, label)):
        try:
            im = Image.open(p).convert('RGB')
        except Exception:
            continue
        im.thumbnail((sel, sel))
        x, y = (k % kolom) * sel, (k // kolom) * (sel + 18)
        kanvas.paste(im, (x, y))
        dr.text((x + 2, y + 2), lb, fill='red')
        dr.text((x + 2, y + sel + 3), pathlib.Path(p).name[:38], fill='black')
    kanvas.save(keluar, quality=92)


def potong_tengah(path, keluar, frac=0.78, maks=900):
    """Potongan tengah pada resolusi asli; tanda air berkontras rendah sering tidak
    terlihat pada miniatur (Keputusan 5).

    Ukuran potongan mengikuti ukuran citra (naskah asli memakai 898x506 tetap, padahal
    lebar median web_katalog hanya 640 sehingga potongannya menjadi seluruh citra).
    """
    im = Image.open(path).convert('RGB')
    w, h = im.size
    cw, ch = int(w * frac), int(h * frac)
    kiri, atas = (w - cw) // 2, (h - ch) // 2
    c = im.crop((kiri, atas, kiri + cw, atas + ch))
    if c.width > maks:
        c = c.resize((maks, int(c.height * maks / c.width)), Image.Resampling.LANCZOS)
    c.save(keluar, quality=95)


def muat_web(provenans_csv, kategori='web_katalog'):
    with open(provenans_csv, encoding='utf-8') as f:
        return [r for r in csv.DictReader(f) if r.get('kelompok_sumber') == kategori]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default='dataset')
    ap.add_argument('--provenans', default='provenans.csv')
    ap.add_argument('--keluar', default='anotasi_web')
    ap.add_argument('--ambang', type=int, default=12)
    ap.add_argument('--rekap', default=None,
                    help='jalankan tahap rekap dari berkas anotasi terisi')
    args = ap.parse_args()

    keluar = pathlib.Path(args.keluar)
    keluar.mkdir(exist_ok=True)

    # ---------------- tahap rekap ----------------
    if args.rekap:
        klaster_status = {}
        with open(args.rekap, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                klaster_status[r['klaster']] = r['status'].strip().lower()
        anggota = defaultdict(list)
        with open(keluar / 'klaster_web.csv', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                anggota[r['klaster']].append(r)
        rekap = defaultdict(lambda: defaultdict(int))
        belum, tak_sah = [], []
        for kl, rows in anggota.items():
            st = klaster_status.get(kl, '')
            if not st:
                belum.append(kl)
                st = 'BELUM_DIPERIKSA'
            elif st not in STATUS_SAH:
                tak_sah.append((kl, st))
            for r in rows:
                rekap[st][r['split']] += 1
                rekap[st]['TOTAL'] += 1
        print(f'{"status":24} {"train":>7} {"valid":>7} {"test":>7} {"TOTAL":>7}')
        print('-' * 56)
        for st in sorted(rekap):
            d = rekap[st]
            print(f'{st:24} {d["train"]:7} {d["valid"]:7} {d["test"]:7} {d["TOTAL"]:7}')
        cemar_test = sum(rekap[s]['test'] for s in rekap
                         if s in ('render_permainan', 'bukan_lalu_lintas'))
        print(f'\nCemaran di split TEST (render/bukan lalu lintas): {cemar_test}')
        print('  -> K3 (jalankan ulang tiga subset) '
              + ('DIPERLUKAN' if cemar_test else 'TIDAK diperlukan'))
        if tak_sah:
            print(f'\nPERINGATAN: status tidak dikenal: {tak_sah[:10]}')
            sys.exit(1)
        if belum:
            print(f'\nPERINGATAN: {len(belum)} klaster belum diperiksa: {belum[:10]}')
            sys.exit(1)
        print('\nSeluruh klaster telah diperiksa.')
        return

    # ---------------- tahap audit ----------------
    baris = muat_web(args.provenans)
    print(f'citra web_katalog: {len(baris)}')
    if not baris:
        sys.exit('provenans.csv tidak memuat kategori web_katalog')

    # PERBAIKAN 3: indeks nama sekali jalan
    akar = pathlib.Path(args.dataset)
    indeks = {}
    for sp in ('train', 'valid', 'test'):
        d = akar / sp / 'images'
        if d.is_dir():
            for p in d.iterdir():
                indeks[p.name] = p

    item = []
    for i, r in enumerate(baris):
        p = indeks.get(r['nama_berkas'])
        if p is None:
            print(f'  lewati, berkas tak ditemukan: {r["nama_berkas"]}')
            continue
        try:
            item.append({'nama': r['nama_berkas'], 'split': r['split'],
                         'path': str(p), 'phash': phash64(p)})
        except Exception as e:
            print(f'  gagal pHash {p.name}: {e}')
        if (i + 1) % 400 == 0:
            print(f'  {i+1}/{len(baris)}')

    grup = klasterisasi(item, args.ambang)
    grup.sort(key=len, reverse=True)
    print(f'klaster: {len(grup)} (anggota >1: {sum(1 for g in grup if len(g) > 1)}, '
          f'tunggal: {sum(1 for g in grup if len(g) == 1)})')

    with open(keluar / 'klaster_web.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['klaster', 'nama_berkas', 'split', 'anggota_klaster', 'perwakilan'])
        for gi, g in enumerate(grup):
            kl = f'W{gi:03d}'
            for k, idx in enumerate(g):
                w.writerow([kl, item[idx]['nama'], item[idx]['split'], len(g),
                            'ya' if k == 0 else ''])

    wakil = [(f'W{gi:03d}', item[g[0]], len(g)) for gi, g in enumerate(grup)]
    per_lembar = 36
    for i in range(0, len(wakil), per_lembar):
        potongan = wakil[i:i + per_lembar]
        lembar_kontak([w[1]['path'] for w in potongan],
                      [f'{w[0]} n={w[2]} {w[1]["split"]}' for w in potongan],
                      keluar / f'lembar_kontak_{i//per_lembar:02d}.jpg')
    (keluar / 'crop').mkdir(exist_ok=True)
    for kl, it, _ in wakil:
        potong_tengah(it['path'], keluar / 'crop' / f'{kl}.jpg')

    with open(keluar / 'kandidat_render.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['nama_berkas', 'split', 'dugaan'])
        n_r = n_p = 0
        for it in item:
            n = it['nama'].lower()
            if any(p in n for p in POLA_RENDER):
                w.writerow([it['nama'], it['split'], 'render_permainan']); n_r += 1
            elif any(p in n for p in POLA_PENJUAL):
                w.writerow([it['nama'], it['split'], 'iklan_penjual']); n_p += 1
    print(f'penyaring nama: {n_r} kandidat render, {n_p} kandidat iklan penjual')

    with open(keluar / 'TEMPLAT_ANOTASI.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['klaster', 'anggota', 'split_perwakilan', 'status', 'catatan'])
        for kl, it, n in wakil:
            w.writerow([kl, n, it['split'], '', ''])

    print(f'\nSelesai. Periksa {keluar}/lembar_kontak_*.jpg dan {keluar}/crop/, '
          f'lalu isi kolom status pada TEMPLAT_ANOTASI.csv.')
    print('Nilai status: ' + ' | '.join(STATUS_SAH))


if __name__ == '__main__':
    main()
