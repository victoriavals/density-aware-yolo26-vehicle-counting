"""
make_group_split.py — Re-split lokal 70/20/10 BERBASIS GRUP (Subbab 3.3.2).

Latar: ekspor Roboflow manual (dataset/) berproporsi 83,4/12,6/4,0 dan terbukti
bocor antar-split (3 pasang citra byte-identik lintas split; 128 stem nama-file
asli muncul di >1 subset). Skrip ini membangun ulang split per GRUP sehingga
seluruh citra segrup jatuh pada subset yang sama, lalu menyimpan bukti grup.

Definisi grup (proksi kamera x adegan x sesi, diturunkan dari nama file asli
sebelum sufiks Roboflow "_jpg.rf.<hash>"; bila ragu DIGABUNG — over-merge hanya
membuat grup lebih kasar, tidak pernah menimbulkan kebocoran):
  1. frame_NNNNNN        -> grup per RESOLUSI citra asli (frame satu video pasti
                            seresolusi; video berbeda seresolusi ikut tergabung).
  2. 15 digit YYYYMMDD…  -> grup per TANGGAL (8 digit pertama; proksi sesi CCTV).
  3. selain itu          -> grup per stem, dengan satu sufiks salinan akhir
                            (-N / _N / --N-) dilucuti agar seri "001--1-",
                            "001--2-" menyatu.
  4. Union-find: citra byte-identik (md5) dipaksa segrup apa pun namanya.

Penetapan subset: greedy deterministik SADAR-KELAS — grup diurutkan (ukuran
desc, md5 nama), tiap grup masuk ke subset yang meminimalkan deviasi gabungan
(proporsi citra 70/20/10 berbobot 2 + proporsi instans per kelas), lalu
disempurnakan local search (pemindahan grup tunggal, maks 5 putaran) dengan
fungsi biaya yang sama. Tanpa RNG; hasil identik antar-run.

Keluaran:
  <dst>/{train,valid,test}/{images,labels}  + data.yaml (path absolut)
  bukti_split_grup.csv   grup, subset, n_citra, pola, contoh_stem
  bukti_split_citra.csv  citra -> grup -> subset (jejak penuh, lampiran)

Pakai (folder dataset/ aktif SUDAH hasil skrip ini; regenerasi hanya bila perlu):
  1. Ekstrak arsip ekspor asli:  traffic-merged.yolo26.zip -> dataset_raw/
  2. python make_group_split.py --src dataset_raw --dst dataset
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

SPLITS = ("train", "valid", "test")
TARGET = {"train": 0.70, "valid": 0.20, "test": 0.10}
RF_SUFFIX = re.compile(
    r"_(jpe?g|png|bmp|webp)\.rf\.[A-Za-z0-9]+\.(jpg|jpeg|png|bmp|webp)$", re.I
)
COPY_SUFFIX = re.compile(r"[-_]+\d+[-_]*$")


def stem_of(name: str) -> str:
    return RF_SUFFIX.sub("", name)


def group_key(stem: str, img_path: Path) -> tuple[str, str]:
    """Return (pola, kunci_grup)."""
    if re.fullmatch(r"frame_\d+", stem):
        with Image.open(img_path) as im:
            w, h = im.size
        return "frame-video", f"video-{w}x{h}"
    if re.fullmatch(r"20\d{13}", stem):
        return "cctv-timestamp", f"sesi-{stem[:8]}"
    base = COPY_SUFFIX.sub("", stem)
    return "tunggal", base or stem


class DSU:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="dataset_raw",
                    help="hasil ekstrak traffic-merged.yolo26.zip (ekspor Roboflow asli)")
    ap.add_argument("--dst", default="dataset")
    args = ap.parse_args()
    src, dst = Path(args.src), Path(args.dst)

    # ---------------------------------------------------- inventaris + grup
    items = []  # (img_path, lbl_path, stem, pola, kunci)
    dsu = DSU()
    by_md5: dict[str, str] = {}
    for sp in SPLITS:
        for img in sorted((src / sp / "images").glob("*")):
            lbl = src / sp / "labels" / (img.stem + ".txt")
            assert lbl.exists(), f"label hilang: {lbl}"
            stem = stem_of(img.name)
            pola, kunci = group_key(stem, img)
            items.append((img, lbl, stem, pola, kunci))
            dsu.find(kunci)
            h = hashlib.md5(img.read_bytes()).hexdigest()
            if h in by_md5:
                dsu.union(kunci, by_md5[h])  # byte-identik -> segrup
            else:
                by_md5[h] = kunci

    groups: dict[str, list[int]] = defaultdict(list)
    pola_of: dict[str, set] = defaultdict(set)
    for i, (_, _, _, pola, kunci) in enumerate(items):
        root = dsu.find(kunci)
        groups[root].append(i)
        pola_of[root].add(pola)

    total = len(items)
    print(f"{total} citra -> {len(groups)} grup "
          f"(terbesar: {max(len(v) for v in groups.values())} citra)")

    # -------------------------- vektor kelas per grup (dari berkas label)
    n_cls = 4
    cls_of_group: dict[str, list[int]] = {}
    for g, idxs in groups.items():
        vec = [0] * n_cls
        for i in idxs:
            for line in items[i][1].read_text().split("\n"):
                t = line.split()
                if t:
                    vec[int(t[0])] += 1
        cls_of_group[g] = vec
    tot_cls = [sum(cls_of_group[g][c] for g in groups) for c in range(n_cls)]

    # ---------------- greedy sadar-kelas + local search, deterministik
    count = {sp: 0 for sp in SPLITS}
    ccount = {sp: [0] * n_cls for sp in SPLITS}
    gcount = {sp: 0 for sp in SPLITS}
    n_groups = len(groups)
    assign: dict[str, str] = {}

    # lantai keragaman: tiap subset minimal ~30% dari jatah grup proporsionalnya
    gfloor = {s: 0.30 * TARGET[s] * n_groups for s in SPLITS}

    def dev(cnt, ccnt, gcnt) -> float:
        # tiga sasaran: proporsi citra (utama), proporsi instans per kelas,
        # dan LANTAI jumlah grup (keragaman adegan; saturasi — tidak menuntut
        # proporsional penuh agar tidak melawan keseimbangan kelas)
        d = 6.0 * sum(abs(cnt[s] / total - TARGET[s]) for s in SPLITS)
        for c in range(n_cls):
            if tot_cls[c]:
                d += sum(abs(ccnt[s][c] / tot_cls[c] - TARGET[s]) for s in SPLITS)
        d += 3.0 * sum(max(0.0, gfloor[s] - gcnt[s]) / gfloor[s] for s in SPLITS)
        return d

    def dev_if(g: str, sp: str) -> float:
        n, vec = len(groups[g]), cls_of_group[g]
        cnt = dict(count); cnt[sp] += n
        ccnt = {s: list(ccount[s]) for s in SPLITS}
        ccnt[sp] = [a + b for a, b in zip(ccnt[sp], vec)]
        gcnt = dict(gcount); gcnt[sp] += 1
        return dev(cnt, ccnt, gcnt)

    order = sorted(groups.items(),
                   key=lambda kv: (-len(kv[1]),
                                   hashlib.md5(kv[0].encode()).hexdigest()))
    for g, idxs in order:
        sp = min(SPLITS, key=lambda s: (dev_if(g, s), s))
        assign[g] = sp
        count[sp] += len(idxs)
        ccount[sp] = [a + b for a, b in zip(ccount[sp], cls_of_group[g])]
        gcount[sp] += 1

    for it in range(5):  # local search: pindahkan grup tunggal bila memperbaiki
        improved = False
        for g, _ in order:
            cur = assign[g]
            n, vec = len(groups[g]), cls_of_group[g]
            count[cur] -= n
            ccount[cur] = [a - b for a, b in zip(ccount[cur], vec)]
            gcount[cur] -= 1
            best = min(SPLITS, key=lambda s: (dev_if(g, s), s))
            if best != cur:
                improved = True
            assign[g] = best
            count[best] += n
            ccount[best] = [a + b for a, b in zip(ccount[best], vec)]
            gcount[best] += 1
        if not improved:
            break
    print("hasil:", {sp: f"{count[sp]} ({count[sp]/total:.1%})" for sp in SPLITS})
    print("grup :", {sp: gcount[sp] for sp in SPLITS})
    for sp in SPLITS:
        print(f"  {sp:6s} instans/kelas:",
              {c: f"{ccount[sp][c]} ({ccount[sp][c]/max(tot_cls[c],1):.1%})" for c in range(n_cls)})

    # -------------------------------------------------------- salin berkas
    if dst.exists():
        shutil.rmtree(dst)  # hasil generasi sebelumnya; cegah berkas basi
    for sp in SPLITS:
        for sub in ("images", "labels"):
            (dst / sp / sub).mkdir(parents=True, exist_ok=True)
    for i, (img, lbl, _, _, kunci) in enumerate(items):
        sp = assign[dsu.find(kunci)]
        shutil.copy2(img, dst / sp / "images" / img.name)
        shutil.copy2(lbl, dst / sp / "labels" / lbl.name)

    names = ["big-vehicle", "car", "pedestrian", "two-wheeler"]
    (dst / "data.yaml").write_text(
        f"path: {dst.resolve()}\ntrain: train/images\nval: valid/images\n"
        f"test: test/images\nnc: {len(names)}\nnames: {names}\n"
    )

    # ------------------------------------------------------------- bukti
    with open("bukti_split_grup.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["grup", "subset", "n_citra", "pola", "contoh_stem"])
        for g, idxs in sorted(groups.items(), key=lambda kv: (assign[kv[0]], -len(kv[1]))):
            w.writerow([g, assign[g], len(idxs), "+".join(sorted(pola_of[g])),
                        items[idxs[0]][2]])
    with open("bukti_split_citra.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["berkas", "stem_asli", "grup", "subset"])
        for i, (img, _, stem, _, kunci) in enumerate(items):
            g = dsu.find(kunci)
            w.writerow([img.name, stem, g, assign[g]])
    print("bukti: bukti_split_grup.csv, bukti_split_citra.csv")
    print(f"dataset baru: {dst}/data.yaml")


if __name__ == "__main__":
    main()
