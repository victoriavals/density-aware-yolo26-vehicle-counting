"""
make_oklusi_sample.py — Kit anotasi MANUAL oklusi (menunaikan rencana Subbab 3.3.3).

Validasi proksi oklusi (Pers. 3.1) mensyaratkan penilaian MANUSIA yang independen
dari proksi — karena itu skrip ini hanya MENYIAPKAN bahan anotasi, bukan menganotasi:

  1. Mengambil sampel objek GT terstratifikasi dari split val (default 300 objek,
     seimbang antar tier proksi no/partial/heavy agar ketiga kelas keputusan teruji;
     deterministik via md5, tanpa RNG — konsisten dengan make_group_split.py).
  2. Merender crop per objek: kotak TARGET merah tebal, kotak tetangga kuning tipis,
     margin konteks di sekitarnya — cukup untuk menilai seberapa tertutup objeknya.
  3. Menulis anotasi_oklusi/anotasi.html — alat klik lokal (blind: tier proksi TIDAK
     ditampilkan) yang mengekspor manual_oklusi.csv berformat persis kebutuhan
     y26_strata.occlusion_agreement: image,gt_index,tier  (tier ∈ {no,partial,heavy}).

Pakai:
  python make_oklusi_sample.py --data dataset/data.yaml --n 300
  # buka anotasi_oklusi/anotasi.html di browser -> nilai -> Ekspor CSV
  # pindahkan unduhan manual_oklusi.csv ke root repo, lalu jalankan Prompt 8.

Bukti stratifikasi tersimpan di anotasi_oklusi/sample_manifest.csv (kolom proxy_*
hanya untuk lampiran/agregat — JANGAN dilihat saat menganotasi).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw

from y26_strata import OCC_EDGES, OCC_NAMES

WARNA_TARGET = (255, 40, 40)
WARNA_TETANGGA = (255, 220, 0)


def baca_label(p: Path) -> list[tuple[int, float, float, float, float]]:
    """Baris label YOLO -> [(cls, x1, y1, x2, y2)] ternormalisasi, urutan file ASLI."""
    out = []
    for line in p.read_text().splitlines():
        t = line.split()
        if len(t) >= 5:
            c, cx, cy, w, h = int(t[0]), *map(float, t[1:5])
            out.append((c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return out


def iou_maks(boxes: np.ndarray) -> np.ndarray:
    """o_i = max_j IoU (Pers. 3.1) pada koordinat ternormalisasi (IoU invarian skala)."""
    n = len(boxes)
    if n < 2:
        return np.zeros(n)
    x1 = np.maximum(boxes[:, None, 0], boxes[None, :, 0])
    y1 = np.maximum(boxes[:, None, 1], boxes[None, :, 1])
    x2 = np.minimum(boxes[:, None, 2], boxes[None, :, 2])
    y2 = np.minimum(boxes[:, None, 3], boxes[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    iou = inter / np.maximum(area[:, None] + area[None, :] - inter, 1e-9)
    np.fill_diagonal(iou, 0)
    return iou.max(1)


def tier_dari(o: float) -> int:
    return 0 if o < OCC_EDGES[0] else (1 if o < OCC_EDGES[1] else 2)


def render_crop(img: Image.Image, boxes_px: list, idx: int, dst: Path, min_sisi: int) -> None:
    """Crop di sekitar kotak target + gambar target (merah) & tetangga (kuning)."""
    im = img.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    for j, (_, x1, y1, x2, y2) in enumerate(boxes_px):
        if j != idx:
            d.rectangle([x1, y1, x2, y2], outline=WARNA_TETANGGA, width=2)
    _, tx1, ty1, tx2, ty2 = boxes_px[idx]
    d.rectangle([tx1, ty1, tx2, ty2], outline=WARNA_TARGET, width=4)

    m = max(0.9 * max(tx2 - tx1, ty2 - ty1), 48)  # margin konteks
    cx1, cy1 = max(int(tx1 - m), 0), max(int(ty1 - m), 0)
    cx2, cy2 = min(int(tx2 + m), im.width), min(int(ty2 + m), im.height)
    crop = im.crop((cx1, cy1, cx2, cy2))
    skala = min(max(min_sisi / max(min(crop.size), 1), 1.0), 4.0)
    if skala > 1.0:
        crop = crop.resize((round(crop.width * skala), round(crop.height * skala)), Image.LANCZOS)
    crop.save(dst, quality=92)


def buat_html(items: list[dict], out: Path) -> None:
    data = json.dumps(items, ensure_ascii=False)
    html = """<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"><title>Anotasi Manual Oklusi</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;background:#111;color:#eee;text-align:center}
 #bar{padding:10px;background:#1d1d1d;position:sticky;top:0}
 img{max-height:62vh;max-width:96vw;border:1px solid #444;image-rendering:auto}
 button{font-size:16px;padding:10px 18px;margin:6px;border-radius:8px;border:0;cursor:pointer}
 .no{background:#2e7d32;color:#fff}.partial{background:#f9a825;color:#000}.heavy{background:#c62828;color:#fff}
 .nav{background:#37474f;color:#fff}.aktif{outline:3px solid #fff}
 #ket{color:#aaa;font-size:14px;max-width:720px;margin:6px auto}
 #ekspor{background:#1565c0;color:#fff}
</style></head><body>
<div id="bar"><b>Anotasi Manual Oklusi</b> — objek <span id="pos"></span>/<span id="tot"></span>
 · terjawab <span id="done"></span> · kelas: <b id="kls"></b><br>
 <span id="ket">Nilai objek pada KOTAK MERAH: seberapa besar bagian objek tertutup objek/kendaraan lain?
 <b>1 = no</b> (terlihat utuh / nyaris utuh) · <b>2 = partial</b> (sebagian tertutup, mayoritas masih terlihat)
 · <b>3 = heavy</b> (sebagian besar tertutup). Kotak kuning = objek tetangga. Navigasi: ←/→. Jawaban tersimpan otomatis.</span></div>
<p><img id="im" alt="crop"></p>
<div>
 <button class="no" onclick="jwb('no')">1 · no</button>
 <button class="partial" onclick="jwb('partial')">2 · partial</button>
 <button class="heavy" onclick="jwb('heavy')">3 · heavy</button>
 <button class="nav" onclick="pindah(-1)">← sebelumnya</button>
 <button class="nav" onclick="pindah(1)">berikutnya →</button>
 <button id="ekspor" onclick="ekspor()">⬇ Ekspor manual_oklusi.csv</button>
</div>
<script>
const ITEMS=__DATA__;const KEY='oklusi_anot_v1';
let jawab=JSON.parse(localStorage.getItem(KEY)||'{}');let i=0;
while(i<ITEMS.length&&jawab[ITEMS[i].sid]!==undefined)i++;if(i>=ITEMS.length)i=0;
function render(){const it=ITEMS[i];document.getElementById('im').src='imgs/'+it.f;
 document.getElementById('pos').textContent=i+1;document.getElementById('tot').textContent=ITEMS.length;
 document.getElementById('kls').textContent=it.c;
 document.getElementById('done').textContent=Object.keys(jawab).length;
 document.querySelectorAll('button.no,button.partial,button.heavy').forEach(b=>b.classList.remove('aktif'));
 const j=jawab[it.sid];if(j)document.querySelector('button.'+j).classList.add('aktif');}
function jwb(t){jawab[ITEMS[i].sid]=t;localStorage.setItem(KEY,JSON.stringify(jawab));
 if(i<ITEMS.length-1)i++;render();}
function pindah(d){i=Math.min(Math.max(i+d,0),ITEMS.length-1);render();}
function ekspor(){const n=Object.keys(jawab).length;
 if(n<ITEMS.length&&!confirm('Baru '+n+'/'+ITEMS.length+' terjawab. Tetap ekspor?'))return;
 let csv='image,gt_index,tier\\n';
 for(const it of ITEMS){const t=jawab[it.sid];if(t)csv+=it.img+','+it.gi+','+t+'\\n';}
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
 a.download='manual_oklusi.csv';a.click();}
document.addEventListener('keydown',e=>{
 if(e.key==='1')jwb('no');else if(e.key==='2')jwb('partial');else if(e.key==='3')jwb('heavy');
 else if(e.key==='ArrowLeft')pindah(-1);else if(e.key==='ArrowRight')pindah(1);});
render();
</script></body></html>"""
    out.write_text(html.replace("__DATA__", data), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Kit anotasi manual oklusi (Subbab 3.3.3)")
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--split", default="val", choices=["val", "test"])
    ap.add_argument("--n", type=int, default=300, help="target jumlah objek sampel")
    ap.add_argument("--per-image-cap", type=int, default=4, help="maks objek per citra per tier")
    ap.add_argument("--min-sisi", type=int, default=320, help="sisi terpendek minimum crop (px)")
    ap.add_argument("--out", default="anotasi_oklusi")
    a = ap.parse_args()

    cfg = yaml.safe_load(Path(a.data).read_text())
    root = Path(cfg.get("path", Path(a.data).parent))
    img_dir = root / cfg["val" if a.split == "val" else "test"]
    lbl_dir = img_dir.parent / "labels"
    names = cfg["names"]
    names = list(names.values()) if isinstance(names, dict) else list(names)

    # ------------------------------------------------ kandidat per tier proksi
    kandidat: dict[int, list] = {0: [], 1: [], 2: []}
    boxes_cache: dict[str, list] = {}
    for img_p in sorted(img_dir.glob("*")):
        lbl = lbl_dir / (img_p.stem + ".txt")
        if not lbl.exists():
            continue
        rows = baca_label(lbl)
        if not rows:
            continue
        boxes_cache[img_p.name] = rows
        o = iou_maks(np.array([r[1:] for r in rows], float))
        for gi, (c, *_xy) in enumerate(rows):
            kandidat[tier_dari(float(o[gi]))].append((img_p.name, gi, names[c], float(o[gi])))

    # deterministik: urut md5(image|gt_index), lalu cap per citra
    def kunci(t):
        return hashlib.md5(f"{t[0]}|{t[1]}".encode()).hexdigest()

    target = {t: a.n // 3 for t in (0, 1, 2)}
    sisa = a.n - sum(target.values())
    for t in range(sisa):
        target[t] += 1
    pilih: list[tuple] = []
    kekurangan = 0
    for t in (0, 1, 2):
        # round-robin antar kelas di dalam tier agar tidak didominasi satu kelas
        # (pejalan kaki bergerombol -> o tinggi -> menyapu pool bila urutan datar)
        per_kelas: dict[str, list] = {k: [] for k in names}
        for cand in sorted(kandidat[t], key=kunci):
            per_kelas[cand[2]].append(cand)
        per_img, ambil, kursor = {}, [], {k: 0 for k in names}
        while len(ambil) < target[t]:
            maju = False
            for k in names:
                if len(ambil) >= target[t]:
                    break
                pool = per_kelas[k]
                while kursor[k] < len(pool):
                    cand = pool[kursor[k]]
                    kursor[k] += 1
                    if per_img.get(cand[0], 0) < a.per_image_cap:
                        ambil.append((t, *cand))
                        per_img[cand[0]] = per_img.get(cand[0], 0) + 1
                        maju = True
                        break
            if not maju:
                break
        kekurangan += target[t] - len(ambil)
        pilih.extend(ambil)
    if kekurangan:
        print(f"[peringatan] {kekurangan} slot tak terisi (tier kurang kandidat) — total {len(pilih)}")

    # ------------------------------------------------------------- render crop
    out = Path(a.out)
    (out / "imgs").mkdir(parents=True, exist_ok=True)
    pilih.sort(key=lambda s: kunci((s[1], s[2])))  # acak-deterministik urutan anotasi
    manifest, items = [], []
    per_image_groups: dict[str, list] = {}
    for sid, (t, img_name, gi, cls_name, o) in enumerate(pilih):
        per_image_groups.setdefault(img_name, []).append((sid, t, gi, cls_name, o))
    for img_name, grup in per_image_groups.items():
        with Image.open(img_dir / img_name) as im:
            W, H = im.size
            boxes_px = [(c, x1 * W, y1 * H, x2 * W, y2 * H)
                        for (c, x1, y1, x2, y2) in boxes_cache[img_name]]
            for sid, t, gi, cls_name, o in grup:
                f = f"{sid:03d}.jpg"
                render_crop(im, boxes_px, gi, out / "imgs" / f, a.min_sisi)
                manifest.append(dict(sample_id=sid, berkas_crop=f, image=img_name, gt_index=gi,
                                     kelas=cls_name, proxy_o=f"{o:.4f}", proxy_tier=OCC_NAMES[t]))
                items.append(dict(sid=sid, f=f, img=img_name, gi=gi, c=cls_name))
    manifest.sort(key=lambda r: r["sample_id"])
    items.sort(key=lambda r: r["sid"])

    with open(out / "sample_manifest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)
    buat_html(items, out / "anotasi.html")

    dist_tier = {nm: sum(1 for m in manifest if m["proxy_tier"] == nm) for nm in OCC_NAMES}
    dist_kelas = {k: sum(1 for m in manifest if m["kelas"] == k) for k in names}
    n_img = len(per_image_groups)
    print(f"sampel: {len(manifest)} objek dari {n_img} citra ({a.split})")
    print(f"distribusi tier proksi (bukti stratifikasi): {dist_tier}")
    print(f"distribusi kelas: {dist_kelas}")
    print(f"buka: {out / 'anotasi.html'}  ->  Ekspor manual_oklusi.csv  ->  taruh di root repo")


if __name__ == "__main__":
    main()
