"""
y26_strata.py — Evaluasi terstratifikasi (Subbab 3.3.3, 3.11.1; Tabel 3.5).

Atribut diturunkan KOMPUTASIONAL dari anotasi bounding box, tanpa anotasi
manual tambahan (Subbab 3.3.3), pada ruang letterbox 640 yang sama dengan
ruang deteksi:

  Ukuran   : luas kotak, konvensi MS COCO — small < 32², medium < 96², large.
  Oklusi   : proksi Pers. 3.1, o_i = max_{j≠i} IoU(b_i, b_j);
             tier default no < 0,10 ≤ partial < 0,35 ≤ heavy (keputusan
             implementasi — laporkan ambangnya di BAB 3/4).
  Densitas : jumlah objek per citra; default sparse < 10 ≤ medium < 26 ≤ dense
             (selaras narasi BAB 1 "lebih dari 25 objek per frame").

AP per (kelas × strata) dihitung dengan protokol bergaya COCO:
  - GT di luar strata ditandai IGNORE (bukan target, bukan penalti);
  - prediksi yang tercocok ke GT ignore ikut di-ignore;
  - khusus dimensi UKURAN, prediksi tak tercocok yang luasnya di luar strata
    juga di-ignore (padanan filter area COCOeval);
  - dimensi DENSITAS bersifat per-citra sehingga dievaluasi sebagai subset citra.
AP memakai interpolasi 101 titik; mAP50-95 = rerata IoU 0,50–0,95 langkah 0,05.
Sel (kelas × strata) inilah unit pasangan uji Wilcoxon (Subbab 3.11.4).
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import torch

from y26_modules import register_ham
from y26_nmsfree import _letterbox, split_image_paths

SIZE_EDGES = (32.0**2, 96.0**2)
OCC_EDGES = (0.10, 0.35)
DEN_EDGES = (10, 26)
SIZE_NAMES = ("small", "medium", "large")
OCC_NAMES = ("no", "partial", "heavy")
DEN_NAMES = ("sparse", "medium", "dense")
IOU_THRS = np.arange(0.50, 0.96, 0.05)


# ------------------------------------------------------------ cache prediksi
def collect_cache(weights, data_yaml, split="test", imgsz=640, batch=16, device=None,
                  out_path=None, max_images=0):
    """Inferensi mentah kepala one-to-one sekali, simpan untuk semua analisis.

    Format npz: pred (P,7)=[img,x1,y1,x2,y2,conf,cls], gt (G,6)=[img,x1..y2,cls],
    names (daftar nama file), imgsz.
    """
    from ultralytics import YOLO

    register_ham()
    model = YOLO(weights) if isinstance(weights, (str, Path)) else weights
    dev = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    nn_model = model.model.to(dev).eval()
    paths = split_image_paths(data_yaml, split)
    if max_images:
        paths = paths[:: max(len(paths) // max_images, 1)][:max_images]
    P, G, names = [], [], []
    for i0 in range(0, len(paths), batch):
        chunk = paths[i0 : i0 + batch]
        ims, metas = [], []
        for p in chunk:
            t, g, gcls, _ = _letterbox(p, imgsz)
            ims.append(t); metas.append((g, gcls)); names.append(p.name)
        with torch.no_grad():
            out = nn_model(torch.stack(ims).to(dev))
        preds = (out[0] if isinstance(out, tuple) else out).float().cpu().numpy()
        for j, (g, gcls) in enumerate(metas):
            gi = i0 + j
            pr = preds[j]
            P.append(np.concatenate([np.full((len(pr), 1), gi, np.float32), pr], 1))
            if len(g):
                G.append(np.concatenate([np.full((len(g), 1), gi, np.float32), g,
                                         gcls.reshape(-1, 1)], 1))
    cache = dict(pred=np.concatenate(P) if P else np.zeros((0, 7), np.float32),
                 gt=np.concatenate(G) if G else np.zeros((0, 6), np.float32),
                 names=np.array(names, dtype=object), n_images=len(paths), imgsz=imgsz)
    if out_path:
        np.savez_compressed(out_path, **{k: v for k, v in cache.items() if k != "names"},
                            names=cache["names"])
    return cache


def load_cache(path):
    z = np.load(path, allow_pickle=True)
    return dict(pred=z["pred"], gt=z["gt"], names=z["names"], n_images=int(z["n_images"]),
                imgsz=int(z["imgsz"]))


# ---------------------------------------------------------------- atribut GT
def _tier(x, edges):
    return np.digitize(x, edges)  # 0,1,2


def gt_attributes(gt: np.ndarray, n_images: int,
                  occ_edges=OCC_EDGES, den_edges=DEN_EDGES, size_edges=SIZE_EDGES):
    """Return dict: size_t, occ, occ_t (per-GT), count, den_t (per-citra)."""
    from ultralytics.utils.metrics import box_iou

    G = len(gt)
    area = (gt[:, 3] - gt[:, 1]) * (gt[:, 4] - gt[:, 2])
    size_t = _tier(area, size_edges)
    occ = np.zeros(G, np.float32)
    count = np.zeros(n_images, np.int64)
    img_ids = gt[:, 0].astype(int)
    for i in np.unique(img_ids):
        m = img_ids == i
        count[i] = int(m.sum())
        if count[i] > 1:
            b = torch.from_numpy(gt[m, 1:5])
            iou = box_iou(b, b).numpy()
            np.fill_diagonal(iou, 0.0)
            occ[m] = iou.max(1)  # Persamaan 3.1
    occ_t = _tier(occ, occ_edges)
    den_t = _tier(count.astype(float), den_edges)
    return dict(size_t=size_t, occ=occ, occ_t=occ_t, count=count, den_t=den_t, area=area)


# --------------------------------------------------------- mesin AP strata
def _ap101(conf, tp, ig, n_pos):
    if n_pos == 0:
        return float("nan")
    keep = ~ig
    conf, tp = conf[keep], tp[keep]
    o = np.argsort(-conf)
    tp = tp[o]
    tps, fps = np.cumsum(tp), np.cumsum(1 - tp)
    rec = tps / n_pos
    prec = tps / np.maximum(tps + fps, 1e-9)
    mrec = np.concatenate(([0.0], rec, [1.0]))
    mpre = np.concatenate(([1.0], prec, [0.0]))
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    return float(np.mean(np.interp(np.linspace(0, 1, 101), mrec, mpre)))


def _match_image(iou, conf_order, gt_ig, thr, det_ig_extra=None):
    """Greedy bergaya COCO: prioritas GT non-ignore; GT ignore boleh dicocok berulang."""
    D, Gn = iou.shape
    tp = np.zeros(D, np.float32)
    ig = np.zeros(D, bool)
    taken = np.zeros(Gn, bool)
    for d in conf_order:
        best, best_iou = -1, thr
        big, big_iou = -1, thr
        for g in range(Gn):
            v = iou[d, g]
            if v < thr:
                continue
            if gt_ig[g]:
                if v >= big_iou:
                    big, big_iou = g, v
            elif not taken[g] and v >= best_iou:
                best, best_iou = g, v
        if best >= 0:
            tp[d] = 1.0
            taken[best] = True
        elif big >= 0 or (det_ig_extra is not None and det_ig_extra[d]):
            ig[d] = True
    return tp, ig


def stratified_ap(cache, class_names, iou_thrs=IOU_THRS,
                  occ_edges=OCC_EDGES, den_edges=DEN_EDGES, size_edges=SIZE_EDGES):
    """Hitung AP50 & AP50-95 per (kelas × dimensi × strata) + global. Return list dict."""
    pred, gt, n_img = cache["pred"], cache["gt"], cache["n_images"]
    A = gt_attributes(gt, n_img, occ_edges, den_edges, size_edges)
    p_img, p_cls = pred[:, 0].astype(int), pred[:, 6].astype(int)
    g_img, g_cls = gt[:, 0].astype(int), gt[:, 5].astype(int)
    p_area = (pred[:, 3] - pred[:, 1]) * (pred[:, 4] - pred[:, 2])
    from ultralytics.utils.metrics import box_iou

    # pra-hitung per (citra, kelas): iou, urutan conf, indeks global
    per = {}
    for i in range(n_img):
        for c in range(len(class_names)):
            dm = (p_img == i) & (p_cls == c)
            gm = (g_img == i) & (g_cls == c)
            if not dm.any() and not gm.any():
                continue
            di, gi = np.where(dm)[0], np.where(gm)[0]
            iou = (box_iou(torch.from_numpy(gt[gi, 1:5]), torch.from_numpy(pred[di, 1:5])).T.numpy()
                   if len(di) and len(gi) else np.zeros((len(di), len(gi)), np.float32))
            per[(i, c)] = (di, gi, iou, np.argsort(-pred[di, 5]))

    def strata_list():
        yield ("global", "all", None, np.zeros(len(gt), bool), None)
        for t, nm in enumerate(SIZE_NAMES):
            lo = ([0.0] + list(size_edges))[t]
            hi = (list(size_edges) + [np.inf])[t]
            yield ("size", nm, None, A["size_t"] != t, (lo, hi))
        for t, nm in enumerate(OCC_NAMES):
            yield ("occlusion", nm, None, A["occ_t"] != t, None)
        for t, nm in enumerate(DEN_NAMES):
            yield ("density", nm, A["den_t"] == t, np.zeros(len(gt), bool), None)

    rows = []
    for dim, nm, img_keep, gt_ig_all, size_rng in strata_list():
        for c, cname in enumerate(class_names):
            confs, tps, igs = [], [], []
            n_pos = 0
            for (i, cc), (di, gi, iou, order) in per.items():
                if cc != c or (img_keep is not None and not img_keep[i]):
                    continue
                gt_ig = gt_ig_all[gi]
                n_pos += int((~gt_ig).sum())
                if len(di) == 0:
                    continue
                det_extra = None
                if size_rng is not None:
                    a = p_area[di]
                    det_extra = (a < size_rng[0]) | (a >= size_rng[1])
                ap50_cache = {}
                for thr in iou_thrs:
                    tp, ig = _match_image(iou, order, gt_ig, float(thr), det_extra)
                    ap50_cache[round(float(thr), 2)] = (tp, ig)
                confs.append(pred[di, 5])
                tps.append(ap50_cache)
            # rakit per threshold
            aps = []
            for thr in iou_thrs:
                key = round(float(thr), 2)
                if confs:
                    cc_ = np.concatenate(confs)
                    tp_ = np.concatenate([t[key][0] for t in tps])
                    ig_ = np.concatenate([t[key][1] for t in tps])
                else:
                    cc_ = tp_ = np.zeros(0, np.float32); ig_ = np.zeros(0, bool)
                aps.append(_ap101(cc_, tp_, ig_, n_pos))
            aps = np.array(aps, dtype=float)
            rows.append(dict(cls=cname, dim=dim, stratum=nm, n_gt=n_pos,
                             ap50=float(aps[0]), ap5095=float(np.nanmean(aps)) if n_pos else float("nan")))
    return rows


def save_strata_csv(rows_by_variant: dict[str, list[dict]], out_csv: str):
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "class", "dim", "stratum", "n_gt", "AP50", "AP50_95"])
        for v, rows in rows_by_variant.items():
            for r in rows:
                w.writerow([v, r["cls"], r["dim"], r["stratum"], r["n_gt"],
                            f"{r['ap50']:.4f}", f"{r['ap5095']:.4f}"])


# ------------------------------------------- validasi proksi oklusi (3.3.3)
def occlusion_agreement(manual_csv: str, data_yaml: str, split="val", occ_edges=OCC_EDGES):
    """Bandingkan tier proksi vs anotasi manual.

    Format manual_csv: kolom image,gt_index,tier  (tier ∈ {no,partial,heavy};
    gt_index = urutan baris pada file label). Return akurasi + matriks konfusi.
    """
    rows = list(csv.DictReader(open(manual_csv)))
    paths = {p.name: p for p in split_image_paths(data_yaml, split)}
    conf = {a: {b: 0 for b in OCC_NAMES} for a in OCC_NAMES}
    ok = tot = 0
    for r in rows:
        p = paths.get(r["image"])
        if p is None:
            continue
        _, g, _, _ = _letterbox(p)
        if len(g) < 2:
            proxy_t = 0
        else:
            from ultralytics.utils.metrics import box_iou

            b = torch.from_numpy(g)
            iou = box_iou(b, b).numpy(); np.fill_diagonal(iou, 0)
            proxy_t = int(_tier(np.array([iou[int(r["gt_index"])].max()]), occ_edges)[0])
        manual = r["tier"].strip()
        conf[manual][OCC_NAMES[proxy_t]] += 1
        ok += manual == OCC_NAMES[proxy_t]; tot += 1
    return dict(agreement=ok / max(tot, 1), n=tot, confusion=conf)
