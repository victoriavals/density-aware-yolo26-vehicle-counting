"""y26_gambar_jurnal.py — Gambar banding kualitatif siap-jurnal (300 dpi).

Membangun gambar banding prediksi antarvarian pada satu bingkai uji, dengan
mutu cetak: lebar fisik terukur (cm), 300 dpi, kotak digambar sebagai patch
VEKTOR matplotlib (tajam pada PDF/EPS), pembeda ganda warna + gaya garis
sehingga tetap terbaca pada cetak abu-abu maupun bagi pembaca buta warna.

Keluaran (PNG 300 dpi + PDF vektor + TIFF bila diminta):
  gambar_banding[_en].png/.pdf   panel penuh per varian
  gambar_zoom[_en].png/.pdf      baris kedua: perbesaran wilayah terpadat
  ringkasan.csv / .json          TP/FP/FN per kelas per varian

Konvensi penandaan (IoU >= 0,50, class-aware, conf > 0,25):
  TP  garis utuh    prediksi tercocokkan ke objek GT
  FP  garis putus    prediksi tanpa pasangan GT
  FN  garis titik    objek GT tanpa prediksi (terlewat)

Metodologi identik pipeline evaluasi: forward MENTAH kepala one-to-one
(pola y26_counting.make_detector) dan pencocokan y26_nmsfree.match_predictions.

Pakai:
  python y26_gambar_jurnal.py --densest-night --variants V1,V8
  python y26_gambar_jurnal.py --image <path> --variants V1,V8 --lang en --width-cm 17
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from y26_modules import register_ham  # noqa: E402
from y26_nmsfree import match_predictions, read_labels, split_image_paths  # noqa: E402

# Warna dipilih agar (a) kontras pada adegan malam, (b) berbeda terang sehingga
# tetap terpisah pada cetak abu-abu, (c) hijau/magenta/kuning aman bagi deuteranopia.
WARNA = {"TP": "#00E396", "FP": "#FF2D95", "FN": "#FFD60A"}
GAYA = {"TP": "solid", "FP": (0, (4, 2)), "FN": (0, (1, 1.6))}

TEKS = {
    "id": dict(tp="Benar (TP)", fp="Prediksi palsu (FP)", fn="Objek terlewat (FN)",
               gt="Ground truth", pred="prediksi", benar="benar", palsu="palsu",
               lewat="terlewat", objek="objek", zoom="perbesaran wilayah terpadat"),
    "en": dict(tp="True positive (TP)", fp="False positive (FP)", fn="Missed object (FN)",
               gt="Ground truth", pred="predictions", benar="correct", palsu="false",
               lewat="missed", objek="objects", zoom="magnified densest region"),
}
CM = 1 / 2.54


# ------------------------------------------------------------------ inferensi
def muat(weights, device=None):
    from ultralytics import YOLO

    register_ham()
    dev = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    m = YOLO(str(weights))
    net = m.model.to(dev).eval()
    names = m.names if isinstance(m.names, dict) else dict(enumerate(m.names))
    return net, names, dev


def deteksi(net, dev, frame_bgr, conf=0.25, imgsz=640):
    h0, w0 = frame_bgr.shape[:2]
    r = min(imgsz / h0, imgsz / w0)
    nw, nh = round(w0 * r), round(h0 * r)
    left, top = (imgsz - nw) // 2, (imgsz - nh) // 2
    kanvas = np.full((imgsz, imgsz, 3), 114, np.uint8)
    kanvas[top : top + nh, left : left + nw] = cv2.resize(frame_bgr, (nw, nh))
    t = torch.from_numpy(kanvas[:, :, ::-1].copy()).permute(2, 0, 1).float().div_(255)[None].to(dev)
    with torch.no_grad():
        out = net(t)
    p = (out[0] if isinstance(out, tuple) else out)[0].float().cpu().numpy()
    p = p[p[:, 4] > conf]
    xyxy = p[:, :4].copy()
    xyxy[:, [0, 2]] = ((xyxy[:, [0, 2]] - left) / r).clip(0, w0 - 1)
    xyxy[:, [1, 3]] = ((xyxy[:, [1, 3]] - top) / r).clip(0, h0 - 1)
    return xyxy, p[:, 4], p[:, 5].astype(int)


def gt_piksel(img_path: Path, w0: int, h0: int):
    lab = read_labels(img_path)
    if not len(lab):
        return np.zeros((0, 4), np.float32), np.zeros(0, int)
    cx, cy, w, h = lab[:, 1] * w0, lab[:, 2] * h0, lab[:, 3] * w0, lab[:, 4] * h0
    return (np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 1).astype(np.float32),
            lab[:, 0].astype(int))


def wilayah_terpadat(gbox, w0, h0, frac=0.5):
    """Jendela (frac*w0 x frac*h0) yang memuat objek GT terbanyak (grid search kasar)."""
    if not len(gbox):
        return (0, 0, w0, h0)
    cx = (gbox[:, 0] + gbox[:, 2]) / 2
    cy = (gbox[:, 1] + gbox[:, 3]) / 2
    ww, hh = w0 * frac, h0 * frac
    terbaik, skor = (0, 0), -1
    for x in np.linspace(0, w0 - ww, 24):
        for y in np.linspace(0, h0 - hh, 24):
            n = int(((cx >= x) & (cx <= x + ww) & (cy >= y) & (cy <= y + hh)).sum())
            if n > skor:
                skor, terbaik = n, (x, y)
    return (terbaik[0], terbaik[1], terbaik[0] + ww, terbaik[1] + hh)


# ------------------------------------------------------------------- panel
def gambar_panel(ax, rgb, hasil, crop=None, lw=1.1):
    """Tempel citra + kotak vektor. hasil = list (box, status)."""
    ax.imshow(rgb)
    for box, status in hasil:
        x1, y1, x2, y2 = box
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                               edgecolor=WARNA[status], linewidth=lw,
                               linestyle=GAYA[status], joinstyle="miter"))
    if crop:
        ax.set_xlim(crop[0], crop[2])
        ax.set_ylim(crop[3], crop[1])
    else:
        ax.set_xlim(0, rgb.shape[1])
        ax.set_ylim(rgb.shape[0], 0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#333"); s.set_linewidth(0.6)


def label_panel(ax, huruf, judul, sub):
    ax.text(0.012, 0.975, huruf, transform=ax.transAxes, ha="left", va="top",
            fontsize=9, fontweight="bold", color="white",
            bbox=dict(boxstyle="square,pad=0.28", fc="#000000", ec="none", alpha=0.72))
    ax.set_title(judul, fontsize=8, fontweight="bold", pad=3.5, loc="left")
    # subjudul dipusatkan & boleh dua baris agar tidak bertabrakan antarpanel
    ax.set_xlabel(sub, fontsize=6.4, labelpad=2.5, color="#333", ha="center")


def simpan(fig, dasar: Path, tiff=False):
    """Simpan TANPA bbox_inches='tight' agar lebar fisik = figsize tepat (syarat jurnal)."""
    keluar = []
    for ext in ("png", "pdf"):
        p = dasar.with_suffix("." + ext)
        fig.savefig(p, dpi=300, facecolor="white")
        keluar.append(p)
    if tiff:
        p = dasar.with_suffix(".tif")
        fig.savefig(p, dpi=300, facecolor="white", pil_kwargs={"compression": "tiff_lzw"})
        keluar.append(p)
    return keluar


def main():
    ap = argparse.ArgumentParser(description="Gambar banding kualitatif siap-jurnal (300 dpi)")
    ap.add_argument("--image", default=None)
    ap.add_argument("--densest-night", action="store_true",
                    help="pilih citra malam dgn KENDARAAN terbanyak (pejalan kaki tak dihitung)")
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--split", default="test")
    ap.add_argument("--variants", default="V1,V8")
    ap.add_argument("--runs", default="runs_tesis")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.5)
    ap.add_argument("--lang", default="id", choices=["id", "en"])
    ap.add_argument("--width-cm", type=float, default=17.0, help="lebar cetak; 8.5 = satu kolom")
    ap.add_argument("--with-gt", action="store_true", help="sisipkan panel ground truth")
    ap.add_argument("--tiff", action="store_true")
    ap.add_argument("--out", default="hasil_bab4_5/15_gambar_jurnal")
    ap.add_argument("--device", default=None)
    a = ap.parse_args()
    T = TEKS[a.lang]

    if a.densest_night:
        kand = [p for p in split_image_paths(a.data, a.split) if "night" in p.stem.lower()]
        assert kand, "tidak ada citra malam"

        def n_kendaraan(p):
            lab = read_labels(p)
            return sum(1 for c in lab[:, 0] if int(c) != 2)  # 2 = pedestrian

        img_path = max(kand, key=n_kendaraan)
    else:
        assert a.image, "beri --image atau --densest-night"
        img_path = Path(a.image)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    frame = cv2.imread(str(img_path))
    assert frame is not None, f"gagal membaca {img_path}"
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h0, w0 = frame.shape[:2]
    gbox, gcls = gt_piksel(img_path, w0, h0)
    crop = wilayah_terpadat(gbox, w0, h0)
    print(f"Citra : {img_path.name}  ({w0}x{h0}, {len(gbox)} objek GT)")

    varian = a.variants.split(",")
    panel_data, baris, names = {}, [], None
    for v in varian:
        w = Path(a.runs) / v / "weights" / "best.pt"
        assert w.exists(), f"bobot tidak ada: {w}"
        net, names, dev = muat(w, a.device)
        xyxy, conf, cls = deteksi(net, dev, frame, a.conf)
        m = match_predictions(xyxy, cls, gbox, gcls, a.iou, True)
        tercocok = {int(i) for i in m.tolist() if i >= 0}

        hasil = [(gbox[k], "FN") for k in range(len(gbox)) if k not in tercocok]
        hasil += [(xyxy[i], "TP" if m[i] >= 0 else "FP") for i in range(len(xyxy))]
        panel_data[v] = hasil

        tp, fp = int((m >= 0).sum()), int((m < 0).sum())
        fn = len(gbox) - len(tercocok)
        per_kelas: dict[str, dict] = {}
        for k, c in enumerate(gcls):
            d = per_kelas.setdefault(names.get(int(c), str(c)), dict(gt=0, tp=0, fn=0, fp=0))
            d["gt"] += 1; d["tp" if k in tercocok else "fn"] += 1
        for i, c in enumerate(cls):
            d = per_kelas.setdefault(names.get(int(c), str(c)), dict(gt=0, tp=0, fn=0, fp=0))
            if m[i] < 0:
                d["fp"] += 1
        baris.append(dict(varian=v, n_gt=len(gbox), n_pred=len(cls), TP=tp, FP=fp, FN=fn,
                          recall=round(tp / max(len(gbox), 1), 4),
                          presisi=round(tp / max(len(cls), 1), 4), per_kelas=per_kelas))
        print(f"  {v}: {len(cls)} prediksi | TP {tp} | FP {fp} | FN {fn}")
        del net
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    JUDUL = {"V1": "V1 — baseline YOLO26",
             "V8": "V8 — HAM + P2 + DALW",
             "V5": "V5 — HAM + P2", "V4": "V4 — DALW", "V3": "V3 — P2", "V2": "V2 — HAM",
             "V6": "V6 — HAM + DALW", "V7": "V7 — P2 + DALW"}
    huruf = "abcdefgh"

    def bangun(crop_mode: bool, dasar: str):
        kolom = (1 if a.with_gt else 0) + len(varian)
        agg = (w0 if not crop_mode else crop[2] - crop[0])
        tinggi_rel = (h0 if not crop_mode else crop[3] - crop[1]) / agg
        lebar_in = a.width_cm * CM
        lebar_panel = lebar_in / kolom
        fig, axes = plt.subplots(1, kolom, figsize=(lebar_in, lebar_panel * tinggi_rel + 0.78),
                                 layout="constrained")
        fig.get_layout_engine().set(w_pad=0.012, h_pad=0.012, wspace=0.012, hspace=0)
        axes = np.atleast_1d(axes)
        i = 0
        if a.with_gt:
            gt_hasil = [(b, "TP") for b in gbox]
            gambar_panel(axes[i], rgb, gt_hasil, crop if crop_mode else None)
            label_panel(axes[i], f"({huruf[i]})", T["gt"], f"{len(gbox)} {T['objek']}")
            i += 1
        for v in varian:
            r = next(x for x in baris if x["varian"] == v)
            gambar_panel(axes[i], rgb, panel_data[v], crop if crop_mode else None)
            label_panel(axes[i], f"({huruf[i]})", JUDUL.get(v, v),
                        f"{r['n_pred']} {T['pred']}\n{r['TP']} {T['benar']} · "
                        f"{r['FP']} {T['palsu']} · {r['FN']} {T['lewat']}")
            i += 1
        pegangan = [Line2D([0], [0], color=WARNA[s], lw=1.5, ls=GAYA[s],
                           label=T[s.lower()]) for s in ("TP", "FP", "FN")]
        fig.legend(handles=pegangan, loc="outside lower center", ncol=3, frameon=False,
                   fontsize=7.5, handlelength=2.6, columnspacing=2.2)
        p = simpan(fig, out / dasar, a.tiff)
        plt.close(fig)
        return p

    akhiran = "" if a.lang == "id" else "_en"
    dibuat = bangun(False, f"gambar_banding{akhiran}")
    dibuat += bangun(True, f"gambar_zoom{akhiran}")

    with open(out / "ringkasan.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["varian", "n_gt", "n_pred", "TP", "FP", "FN", "recall", "presisi"])
        w.writeheader()
        for r in baris:
            w.writerow({k: v for k, v in r.items() if k != "per_kelas"})
    (out / "ringkasan.json").write_text(json.dumps(
        dict(citra=img_path.name, ukuran=[w0, h0], conf=a.conf, iou=a.iou,
             wilayah_zoom=[round(float(x), 1) for x in crop],
             kelas=names, varian=baris), indent=2, ensure_ascii=False))
    print("\nBerkas:")
    for p in dibuat:
        print(f"  {p}  ({p.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
