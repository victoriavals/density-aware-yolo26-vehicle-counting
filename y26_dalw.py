"""
y26_dalw.py — Density-Aware Loss Weighting (DALW) untuk YOLO26.

Implementasi Persamaan 3.2–3.5 tesis:
    rho_i     = sum_{j != i} exp( -||c_i - c_j||^2 / (2 sigma^2) )      (3.2)
    rho_hat_i = rho_i / (rho_i + 1)                                     (3.3)
    w_i       = 1 + alpha * rho_hat_i                                   (3.4)
    L         = (1/N) * sum_i w_i * L_i                                 (3.5)

KEPUTUSAN A-11 (diverifikasi terhadap kode sumber ultralytics 8.4.92):
  DetectionModel.init_criterion (nn/tasks.py:596) mengembalikan E2ELoss untuk
  model end2end. E2ELoss (utils/loss.py:1174) membangun DUA cabang loss dari
  loss_fn yang sama: one2many (tal_topk=10) dan one2one (tal_topk=7, topk2=1),
  lalu mencampurnya dengan gain ProgLoss yang meluruh 0.8 -> 0.1 sepanjang epoch.
  Karena itu w_i disuntikkan DI DALAM v8DetectionLoss sehingga otomatis berlaku
  pada KEDUA head, dan ProgLoss tetap utuh di atasnya:
      L = sum_b g_b(t) * sum_i w_i * L_{b,i}  =  sum_i w_i * ( sum_b g_b(t) L_{b,i} )
  yang identik dengan Persamaan 3.5 dengan L_i = total loss bawaan YOLO26.

Detail penempatan bobot (merujuk v8DetectionLoss.get_assigned_targets_and_loss):
  1) Loss klasifikasi: bce_loss berbentuk (bs, A, nc); dikalikan w per-anchor
     (anchor latar belakang berbobot 1 — bobot bersifat per-OBJEK sesuai tesis).
  2) Loss regresi kotak: BboxLoss memakai target_scores sebagai BOBOT internal
     (bukan target BCE), sehingga cukup meneruskan target_scores * w.
  3) Normalizer target_scores_sum TIDAK diubah, sehingga bobot benar-benar
     menguatkan kontribusi objek padat sesuai semantik (1/N) Σ w_i L_i.
  4) Bobot dihitung dari label batch DI DALAM loss => otomatis terhitung ulang
     pasca-augmentasi mosaic (memenuhi Subbab 3.4), dan berada dalam
     torch.no_grad => konstanta per objek, tidak menambah kompleksitas gradien.
"""

from __future__ import annotations

import torch

from ultralytics.utils.loss import v8DetectionLoss, E2ELoss
from ultralytics.utils.tal import make_anchors

# Parameter global DALW (diisi oleh apply_dalw / set_dalw_params)
_ALPHA: float = 1.0
_SIGMA: float = 0.10


def set_dalw_params(alpha: float, sigma: float) -> None:
    global _ALPHA, _SIGMA
    _ALPHA, _SIGMA = float(alpha), float(sigma)


def density_weights(
    centers: torch.Tensor, valid: torch.Tensor, alpha: float, sigma: float
) -> torch.Tensor:
    """Hitung w_i (Pers 3.2–3.4) per citra pada batch ter-padding.

    Args:
        centers: (bs, n_max, 2) pusat kotak GT dalam koordinat TERNORMALISASI [0,1].
        valid:   (bs, n_max) bool, True untuk slot GT yang terisi.
        alpha, sigma: hiperparameter DALW (Tabel 3.3 tesis).

    Returns:
        (bs, n_max) bobot w_i; slot tidak valid bernilai 1.0.
    """
    if centers.numel() == 0:
        return torch.ones(centers.shape[:2], device=centers.device)
    d2 = torch.cdist(centers, centers, p=2).pow(2)  # (bs, n, n) jarak kuadrat
    kern = torch.exp(-d2 / (2.0 * sigma * sigma))
    pair_valid = valid.unsqueeze(1) & valid.unsqueeze(2)  # (bs, n, n)
    kern = kern * pair_valid
    # j != i : kurangi kontribusi diri sendiri (exp(0) = 1) pada slot valid
    rho = kern.sum(-1) - valid.float()
    rho_hat = rho / (rho + 1.0)  # Pers 3.3, rentang [0, 1)
    w = 1.0 + alpha * rho_hat  # Pers 3.4
    return torch.where(valid, w, torch.ones_like(w))


class DALWDetectionLoss(v8DetectionLoss):
    """v8DetectionLoss + pembobotan densitas per objek (kebaruan metode tesis).

    Metode get_assigned_targets_and_loss disalin dari ultralytics 8.4.92
    (utils/loss.py:400-463) dengan tiga modifikasi bertanda '# === DALW'.
    """

    def __init__(self, model, tal_topk: int = 10, tal_topk2=None, alpha=None, sigma=None):
        super().__init__(model, tal_topk=tal_topk, tal_topk2=tal_topk2)
        self.dalw_alpha = _ALPHA if alpha is None else float(alpha)
        self.dalw_sigma = _SIGMA if sigma is None else float(sigma)

    def get_assigned_targets_and_loss(self, preds, batch):
        loss = torch.zeros(3, device=self.device)  # box, cls, dfl
        pred_distri, pred_scores = (
            preds["boxes"].permute(0, 2, 1).contiguous(),
            preds["scores"].permute(0, 2, 1).contiguous(),
        )
        anchor_points, stride_tensor = make_anchors(preds["feats"], self.stride, 0.5)

        dtype = pred_scores.dtype
        batch_size = pred_scores.shape[0]
        imgsz = torch.tensor(preds["feats"][0].shape[2:], device=self.device, dtype=dtype) * self.stride[0]

        # Targets
        targets = torch.cat((batch["batch_idx"].view(-1, 1), batch["cls"].view(-1, 1), batch["bboxes"]), 1)
        targets = self.preprocess(targets.to(self.device), batch_size, scale_tensor=imgsz[[1, 0, 1, 0]])
        gt_labels, gt_bboxes = targets.split((1, 4), 2)  # cls, xyxy (skala piksel)
        mask_gt = gt_bboxes.sum(2, keepdim=True).gt_(0.0)

        # === DALW (1/3): bobot densitas per GT, dari label batch pasca-augmentasi ===
        with torch.no_grad():
            centers_px = (gt_bboxes[..., 0:2] + gt_bboxes[..., 2:4]) * 0.5  # (bs, n, 2)
            centers = centers_px / imgsz[[1, 0]]  # normalisasi ke [0,1] (x/W, y/H)
            w_gt = density_weights(
                centers, mask_gt.squeeze(-1).bool(), self.dalw_alpha, self.dalw_sigma
            ).to(dtype)  # (bs, n)

        # Pboxes
        pred_bboxes = self.bbox_decode(anchor_points, pred_distri)  # xyxy, (b, h*w, 4)

        _, target_bboxes, target_scores, fg_mask, target_gt_idx = self.assigner(
            pred_scores.detach().sigmoid(),
            (pred_bboxes.detach() * stride_tensor).type(gt_bboxes.dtype),
            anchor_points * stride_tensor,
            gt_labels,
            gt_bboxes,
            mask_gt,
        )

        target_scores_sum = max(target_scores.sum(), 1)

        # === DALW (2/3): petakan w_gt ke tiap anchor foreground via target_gt_idx ===
        with torch.no_grad():
            w_anc = w_gt.gather(1, target_gt_idx.clamp(min=0))  # (bs, A)
            w_anc = torch.where(fg_mask.bool(), w_anc, torch.ones_like(w_anc))

        # Cls loss with optional class weighting
        bce_loss = self.bce(pred_scores, target_scores.to(dtype))  # (bs, A, nc)
        if self.class_weights is not None:
            bce_loss *= self.class_weights
        bce_loss = bce_loss * w_anc.unsqueeze(-1)  # === DALW: w_i * L_cls,i
        loss[1] = bce_loss.sum() / target_scores_sum  # BCE

        # Bbox loss
        if fg_mask.sum():
            # === DALW (3/3): target_scores dipakai BboxLoss sebagai bobot internal,
            # sehingga mengalikannya dengan w menghasilkan w_i * L_box,i.
            loss[0], loss[2] = self.bbox_loss(
                pred_distri,
                pred_bboxes,
                anchor_points,
                target_bboxes / stride_tensor,
                target_scores * w_anc.unsqueeze(-1),
                target_scores_sum,
                fg_mask,
                imgsz,
                stride_tensor,
            )

        loss[0] *= self.hyp.box  # box gain
        loss[1] *= self.hyp.cls  # cls gain
        loss[2] *= self.hyp.dfl  # dfl gain
        return (
            (fg_mask, target_gt_idx, target_bboxes, anchor_points, stride_tensor),
            loss,
            loss.detach(),
        )


def apply_dalw(alpha: float, sigma: float) -> None:
    """Aktifkan DALW untuk seluruh model yang dibangun SETELAH pemanggilan ini.

    Mem-patch DetectionModel.init_criterion agar E2ELoss dibangun dengan
    loss_fn=DALWDetectionLoss pada KEDUA cabang head (keputusan A-11).
    ProgLoss (jadwal gain o2m->o2o) dan STAL (assigner bawaan) tetap aktif.
    Panggil sekali per proses, SEBELUM model.train().
    """
    set_dalw_params(alpha, sigma)
    from ultralytics.nn import tasks

    def init_criterion(self):  # menggantikan tasks.DetectionModel.init_criterion
        if getattr(self, "end2end", False):
            return E2ELoss(self, loss_fn=DALWDetectionLoss)
        return DALWDetectionLoss(self)

    tasks.DetectionModel.init_criterion = init_criterion
    print(f"[DALW] aktif: alpha={alpha}, sigma={sigma} (kedua head, ProgLoss & STAL utuh)")
