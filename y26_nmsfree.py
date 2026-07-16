"""
y26_nmsfree.py — Instrumentasi interaksi paradigma NMS-free (Subbab 3.7 tesis).

Tiga metrik Persamaan 3.6-3.7 + formalisasi A-10, diukur dari keluaran kepala
one-to-one (model end2end: keluaran inferensi = kepala one-to-one, tanpa NMS):

1) Duplicate Rate (Pers. 3.6):  DR(τ) = (1/M) Σ_k N_k(τ)
   N_k(τ) = jumlah prediksi ber-confidence > τ yang TERCOCOKKAN ke objek k.
   Aturan pencocokan (keputusan implementasi, dokumentasikan di BAB 4):
   setiap prediksi dipetakan ke SATU objek GT dengan IoU tertinggi, syarat
   IoU >= iou_thr (default 0,5) dan kelas sama (class_aware=True). Beberapa
   prediksi boleh menunjuk objek yang sama — itulah duplikasi yang diukur.
   DR sehat ~1; DR>1 duplikasi; DR<1 ada objek terlewat pada ambang τ.

2) Confidence Margin (Pers. 3.7): CM_k = conf(p_k^(1)) - conf(p_k^(2))
   dihitung atas SEMUA prediksi yang tercocokkan ke objek k (tanpa filter τ;
   τ hanya menyaring DR). Bila prediksi kedua tidak ada, conf(p^(2)) = 0
   sehingga CM_k = conf(p^(1)) — pemenang tunggal yang maksimal jelas.

3) Stabilitas assignment antar-epoch (formalisasi A-10):
       S(t) = (1/M_probe) Σ_k 1[ a_k(t) = a_k(t-1) ]
   a_k(t) = indeks anchor (rata seluruh skala) yang dipilih assigner kepala
   one-to-one (STAL, topk akhir 1) untuk objek k pada akhir epoch t, dihitung
   pada HIMPUNAN PROBE TETAP dari data validasi (letterbox 640, tanpa
   augmentasi). a_k dapat bernilai ∅ (tak ter-assign); kesamaan ∅==∅ dihitung
   stabil, dan fraksi ter-assign dilaporkan terpisah. Diukur dengan menggali
   assigner internal (get_assigned_targets_and_loss), bukan antarmuka standar.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2
import numpy as np
import torch
import yaml

from y26_modules import register_ham

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# ------------------------------------------------------------ util dataset
def split_image_paths(data_yaml: str, split: str = "val") -> list[Path]:
    d = yaml.safe_load(Path(data_yaml).read_text())
    root = Path(d.get("path") or Path(data_yaml).parent)
    entry = d.get(split) or ("valid/images" if split == "val" else f"{split}/images")
    p = Path(entry)
    p = p if p.is_absolute() else root / p
    return sorted(q for q in p.glob("*") if q.suffix.lower() in IMG_EXT)


def label_path(img: Path) -> Path:
    return Path(str(img.parent).replace("images", "labels")) / (img.stem + ".txt")


def read_labels(img: Path) -> np.ndarray:
    """Return (G,5) [cls, cx, cy, w, h] ternormalisasi; kosong -> (0,5)."""
    lp = label_path(img)
    if not lp.exists() or not lp.read_text().strip():
        return np.zeros((0, 5), dtype=np.float32)
    return np.array([l.split()[:5] for l in lp.read_text().strip().splitlines()], dtype=np.float32)


# --------------------------------------------------- pencocokan & akumulasi
def match_predictions(pred_xyxy, pred_cls, gt_xyxy, gt_cls, iou_thr=0.5, class_aware=True):
    """Petakan tiap prediksi ke GT ber-IoU tertinggi (>= iou_thr). Return (P,) idx GT / -1."""
    from ultralytics.utils.metrics import box_iou

    if len(pred_xyxy) == 0 or len(gt_xyxy) == 0:
        return torch.full((len(pred_xyxy),), -1, dtype=torch.long)
    iou = box_iou(torch.as_tensor(gt_xyxy, dtype=torch.float32), torch.as_tensor(pred_xyxy, dtype=torch.float32)).T
    if class_aware:
        neq = torch.as_tensor(pred_cls).view(-1, 1).long() != torch.as_tensor(gt_cls).view(1, -1).long()
        iou = iou.masked_fill(neq, 0.0)
    best, idx = iou.max(dim=1)
    return torch.where(best >= iou_thr, idx, torch.full_like(idx, -1))


class DRCMAccumulator:
    """Akumulasi DR(τ), CM, miss/duplicate fraction lintas citra + rekaman per-citra."""

    def __init__(self, taus=(0.25,), tau_main: float = 0.25):
        self.taus = sorted(set(float(t) for t in taus) | {float(tau_main)})
        self.tau_main = float(tau_main)
        self.M = 0
        self.images = 0
        self.tal = {t: dict(n=0, miss=0, dup=0) for t in self.taus}
        self.cms: list[float] = []
        self.matched_gt = 0
        self.per_image: list[dict] = []

    def update(self, match: torch.Tensor, conf: torch.Tensor, n_gt: int, name: str = ""):
        self.images += 1
        if n_gt == 0:
            return
        self.M += n_gt
        conf = torch.as_tensor(conf, dtype=torch.float32)
        row_cm, n_main = [], None
        for t in self.taus:
            sel = (match >= 0) & (conf > t)
            N = torch.bincount(match[sel], minlength=n_gt).float()
            self.tal[t]["n"] += int(N.sum())
            self.tal[t]["miss"] += int((N == 0).sum())
            self.tal[t]["dup"] += int((N >= 2).sum())
            if t == self.tau_main:
                n_main = N
        for k in range(n_gt):
            c = conf[match == k]
            if len(c):
                c, _ = torch.sort(c, descending=True)
                cm = float(c[0] - (c[1] if len(c) > 1 else 0.0))
                self.cms.append(cm)
                row_cm.append(cm)
                self.matched_gt += 1
        self.per_image.append(
            dict(image=name, n_gt=n_gt, dr=float(n_main.mean()), miss=int((n_main == 0).sum()),
                 dup=int((n_main >= 2).sum()), cm_mean=float(np.mean(row_cm)) if row_cm else float("nan"))
        )

    def summary(self) -> dict:
        cm = torch.tensor(self.cms) if self.cms else torch.zeros(0)
        out = dict(
            images=self.images, M=self.M, tau_main=self.tau_main,
            coverage=self.matched_gt / max(self.M, 1),
            cm_mean=float(cm.mean()) if len(cm) else float("nan"),
            cm_median=float(cm.median()) if len(cm) else float("nan"),
            cm_p10=float(torch.quantile(cm, 0.10)) if len(cm) else float("nan"),
            taus={},
        )
        for t in self.taus:
            d = self.tal[t]
            out["taus"][f"{t:g}"] = dict(
                DR=d["n"] / max(self.M, 1), miss_frac=d["miss"] / max(self.M, 1), dup_frac=d["dup"] / max(self.M, 1)
            )
        m = out["taus"][f"{self.tau_main:g}"]
        out.update(DR=m["DR"], miss_frac=m["miss_frac"], dup_frac=m["dup_frac"])
        return out


# ------------------------------------------------------------- letterbox
def _letterbox(path, imgsz: int = 640):
    """Muat 1 citra letterbox 640 + label pada DUA representasi konsisten:
    GT xyxy piksel-letterbox (untuk pencocokan) dan baris [cls,cx,cy,w,h]
    ternormalisasi-letterbox (untuk batch format loss)."""
    im = cv2.imread(str(path))
    h0, w0 = im.shape[:2]
    r = min(imgsz / h0, imgsz / w0)
    nw, nh = round(w0 * r), round(h0 * r)
    left, top = (imgsz - nw) // 2, (imgsz - nh) // 2
    canvas = np.full((imgsz, imgsz, 3), 114, np.uint8)
    canvas[top : top + nh, left : left + nw] = cv2.resize(im, (nw, nh))
    t = torch.from_numpy(canvas[:, :, ::-1].copy()).permute(2, 0, 1).float() / 255.0
    lab = read_labels(Path(path))
    if len(lab):
        cx, cy = lab[:, 1] * w0 * r + left, lab[:, 2] * h0 * r + top
        w, h = lab[:, 3] * w0 * r, lab[:, 4] * h0 * r
        gt = np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 1).astype(np.float32)
        rows = np.stack([lab[:, 0], cx / imgsz, cy / imgsz, w / imgsz, h / imgsz], 1).astype(np.float32)
        gcls = lab[:, 0]
    else:
        gt, rows, gcls = np.zeros((0, 4), np.float32), np.zeros((0, 5), np.float32), np.zeros(0, np.float32)
    return t, gt, gcls, rows


# ------------------------------------------------- evaluasi penuh (post-hoc)
def evaluate_dr_cm(weights, data_yaml, split="test", tau_main=0.25, taus=None, iou_thr=0.5,
                   class_aware=True, imgsz=640, batch=16, device=None, max_images=0, conf_floor=0.0):
    """DR/CM pada seluruh subset, dari keluaran MENTAH kepala one-to-one.

    Sengaja melewati predictor standar: forward langsung DetectionModel dalam
    mode eval mengembalikan (B, 300, 6) [xyxy, conf, cls] pada ruang letterbox,
    dan GT ditransformasikan ke ruang yang sama — 'menggali keluaran kepala
    one-to-one', bukan memanggil antarmuka standar (Subbab 3.7).
    """
    from ultralytics import YOLO

    register_ham()
    model = YOLO(weights) if isinstance(weights, (str, Path)) else weights
    dev = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    nn_model = model.model.to(dev).eval()
    paths = split_image_paths(data_yaml, split)
    if max_images:
        paths = paths[:: max(len(paths) // max_images, 1)][:max_images]
    acc = DRCMAccumulator(taus or [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], tau_main)
    for i0 in range(0, len(paths), batch):
        chunk = paths[i0 : i0 + batch]
        ims, gts, gcs = [], [], []
        for p in chunk:
            t, g, gc, _ = _letterbox(p, imgsz)
            ims.append(t); gts.append(g); gcs.append(gc)
        with torch.no_grad():
            out = nn_model(torch.stack(ims).to(dev))
        preds = (out[0] if isinstance(out, tuple) else out).float().cpu()  # (B, 300, 6)
        for j, p in enumerate(chunk):
            pr = preds[j]
            if conf_floor > 0:
                pr = pr[pr[:, 4] > conf_floor]
            m = match_predictions(pr[:, :4], pr[:, 5], gts[j], gcs[j], iou_thr, class_aware)
            acc.update(m, pr[:, 4], len(gts[j]), name=Path(p).name)
    return acc


# ------------------------------------------ akses internal kepala one-to-one
def train_format_forward(nn_model: torch.nn.Module, imgs: torch.Tensor):
    """Forward yang mengembalikan dict {'one2many','one2one'} TANPA merusak statistik BN.

    Trik: hanya flag `training` milik modul Detect yang dinaikkan (menentukan
    cabang forward); seluruh anak modul (Conv+BN) tetap mode eval sehingga
    running statistics BN tidak berubah — inilah 'menggali kode internal'
    yang dijanjikan Subbab 3.7.
    """
    det = nn_model.model[-1]
    prev_model, prev_det = nn_model.training, det.training
    nn_model.eval()
    det.training = True  # HANYA atribut flag; JANGAN det.train() (akan menular ke BN)
    try:
        with torch.no_grad():
            out = nn_model(imgs)
    finally:
        det.training = prev_det
        nn_model.train(prev_model)
    return out


def extract_o2o_assignments(nn_model: torch.nn.Module, batch: dict):
    """Assignment kepala one-to-one per objek GT: {(img_i, gt_k): anchor_id}.

    Menggunakan assigner internal loss (STAL) persis seperti saat pelatihan.
    """
    crit = getattr(nn_model, "criterion", None)
    if crit is None:
        crit = nn_model.criterion = nn_model.init_criterion()
    out = train_format_forward(nn_model, batch["img"])
    preds = crit.one2many.parse_output(out)
    with torch.no_grad():
        (fg, tgi, *_), _, _ = crit.one2one.get_assigned_targets_and_loss(preds["one2one"], batch)
    assigns: dict[tuple[int, int], int] = {}
    per_gt_count: dict[tuple[int, int], int] = {}
    for b in range(fg.shape[0]):
        anchors = torch.nonzero(fg[b], as_tuple=False).flatten()
        for a in anchors.tolist():
            key = (b, int(tgi[b, a]))
            per_gt_count[key] = per_gt_count.get(key, 0) + 1
            assigns[key] = min(assigns.get(key, a), a)  # deterministik: anchor terkecil
    n_gt_total = int(batch["batch_idx"].numel())
    stats = dict(
        assigned=len(assigns), total_gt=n_gt_total,
        assigned_frac=len(assigns) / max(n_gt_total, 1),
        anchors_per_gt=float(np.mean(list(per_gt_count.values()))) if per_gt_count else 0.0,
    )
    return assigns, stats


def stability(prev: dict | None, cur: dict, total_keys: set) -> float:
    """S(t): fraksi objek probe dengan a_k(t) == a_k(t-1); ∅==∅ dihitung stabil."""
    if prev is None:
        return float("nan")
    same = sum(1 for k in total_keys if prev.get(k) == cur.get(k))
    return same / max(len(total_keys), 1)


# ------------------------------------------------------------- probe loader
def load_probe(data_yaml: str, split="val", n=64, imgsz=640):
    """Muat n citra probe (letterbox 640) + label terkoreksi + GT piksel letterbox."""
    paths = split_image_paths(data_yaml, split)
    assert paths, f"tidak ada citra pada split '{split}' dari {data_yaml}"
    idx = np.linspace(0, len(paths) - 1, min(n, len(paths))).round().astype(int)
    paths = [paths[i] for i in sorted(set(idx.tolist()))]
    imgs, bidx, cls, bb, gt_px = [], [], [], [], []
    for i, p in enumerate(paths):
        t, g, gcls, rows = _letterbox(p, imgsz)
        imgs.append(t)
        gt_px.append((g, gcls))
        for row in rows:
            bidx.append(i); cls.append([row[0]]); bb.append(row[1:5].tolist())
    batch = dict(
        img=torch.stack(imgs),
        batch_idx=torch.tensor(bidx, dtype=torch.float32),
        cls=torch.tensor(cls, dtype=torch.float32) if cls else torch.zeros(0, 1),
        bboxes=torch.tensor(bb, dtype=torch.float32) if bb else torch.zeros(0, 4),
    )
    return batch, gt_px, [str(p) for p in paths]


# --------------------------------------------------------- callback training
class NMSFreeProbe:
    """Callback on_fit_epoch_end: stabilitas assignment + DR/CM probe per epoch.

    Menulis <save_dir>/nmsfree_probe.csv; tidak pernah menghentikan training
    (seluruh isi dibungkus try/except).
    """

    def __init__(self, data_yaml: str, n: int = 64, split: str = "val", tau: float = 0.25, iou: float = 0.5):
        self.data_yaml, self.n, self.split, self.tau, self.iou = data_yaml, n, split, tau, iou
        self.batch = None
        self.prev = None
        self.keys: set = set()

    def _ensure(self, device):
        if self.batch is None:
            b, self.gt_px, _ = load_probe(self.data_yaml, self.split, self.n)
            self.batch = {k: v.to(device) for k, v in b.items()}
            counts = torch.bincount(self.batch["batch_idx"].long(), minlength=self.batch["img"].shape[0])
            self.keys = {(i, k) for i in range(len(counts)) for k in range(int(counts[i]))}

    def __call__(self, trainer):
        try:
            # ultralytics 8.4.92: de_parallel telah berganti nama menjadi unwrap_model
            from ultralytics.utils.torch_utils import unwrap_model

            m = unwrap_model(trainer.model)
            self._ensure(next(m.parameters()).device)

            assigns, astats = extract_o2o_assignments(m, self.batch)
            s = stability(self.prev, assigns, self.keys)
            self.prev = assigns

            # DR/CM probe dari keluaran inferensi one-to-one (letterbox px)
            was = m.training
            m.eval()
            with torch.no_grad():
                out = m(self.batch["img"])
            m.train(was)
            preds = out[0] if isinstance(out, tuple) else out  # (B, 300, 6)
            acc = DRCMAccumulator(taus=[self.tau], tau_main=self.tau)
            for i, (g, gcls) in enumerate(self.gt_px):
                p = preds[i].cpu()
                mt = match_predictions(p[:, :4], p[:, 5], g, gcls, self.iou, True)
                acc.update(mt, p[:, 4], len(g))
            summ = acc.summary()

            f = Path(trainer.save_dir) / "nmsfree_probe.csv"
            new = not f.exists()
            with open(f, "a", newline="") as fh:
                w = csv.writer(fh)
                if new:
                    w.writerow(["epoch", "stability", "assigned_frac", "anchors_per_gt",
                                "DR", "miss_frac", "dup_frac", "cm_mean", "cm_median"])
                w.writerow([trainer.epoch + 1, f"{s:.4f}", f"{astats['assigned_frac']:.4f}",
                            f"{astats['anchors_per_gt']:.3f}", f"{summ['DR']:.4f}", f"{summ['miss_frac']:.4f}",
                            f"{summ['dup_frac']:.4f}", f"{summ['cm_mean']:.4f}", f"{summ['cm_median']:.4f}"])
        except Exception as e:  # jangan pernah mematikan training
            print(f"[NMSFreeProbe] dilewati epoch ini: {type(e).__name__}: {e}")


def save_summary(acc: DRCMAccumulator, out_dir: str, name: str) -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    summ = acc.summary()
    (out / f"{name}.json").write_text(json.dumps(summ, indent=2))
    with open(out / f"{name}_per_image.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["image", "n_gt", "dr", "miss", "dup", "cm_mean"])
        w.writeheader()
        w.writerows(acc.per_image)
    return summ
