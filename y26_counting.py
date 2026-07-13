"""
y26_counting.py — Penghitungan kendaraan end-to-end (Subbab 3.10, Gambar 3.6;
metrik Pers. 3.12–3.14).

Pipeline: frame video -> deteksi (keluaran mentah kepala one-to-one, ambang
confidence 0,25) -> ByteTrack (pustaka supervision) -> virtual line crossing
dua arah dengan akumulasi per kelas per interval pengamatan -> MAE/RMSE/MAPE
terhadap hitung manual. Pejalan kaki dikecualikan dari hitungan (kelas konteks,
Tabel 3.1). MAPE hanya pada pengamatan y_t > 0 dan proporsi pengecualian
dilaporkan (Subbab 3.11.3).

Format CSV ground truth (hitung manual):
    interval,class,direction,count
    0,car,in,12
    0,two-wheeler,in,31
    1,car,out,9
interval = indeks jendela waktu ke-i berdurasi --interval-s detik (mulai 0).
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import warnings
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch


# ------------------------------------------------------------- detektor
def make_detector(weights, imgsz=640, device=None, conf=0.25):
    """Detektor frame->(:xyxy piksel frame, conf, cls) via forward mentah o2o."""
    from ultralytics import YOLO
    from y26_modules import register_ham

    register_ham()
    model = YOLO(weights)
    dev = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    nn_model = model.model.to(dev).eval()
    names = model.names if isinstance(model.names, dict) else dict(enumerate(model.names))

    def detect(frame_bgr: np.ndarray):
        h0, w0 = frame_bgr.shape[:2]
        r = min(imgsz / h0, imgsz / w0)
        nw, nh = round(w0 * r), round(h0 * r)
        left, top = (imgsz - nw) // 2, (imgsz - nh) // 2
        canvas = np.full((imgsz, imgsz, 3), 114, np.uint8)
        canvas[top : top + nh, left : left + nw] = cv2.resize(frame_bgr, (nw, nh))
        t = torch.from_numpy(canvas[:, :, ::-1].copy()).permute(2, 0, 1).float().div_(255)[None].to(dev)
        with torch.no_grad():
            out = nn_model(t)
        p = (out[0] if isinstance(out, tuple) else out)[0].float().cpu().numpy()
        p = p[p[:, 4] > conf]
        xyxy = p[:, :4].copy()
        xyxy[:, [0, 2]] = (xyxy[:, [0, 2]] - left) / r
        xyxy[:, [1, 3]] = (xyxy[:, [1, 3]] - top) / r
        xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, w0 - 1)
        xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, h0 - 1)
        return xyxy, p[:, 4], p[:, 5].astype(int)

    return detect, names


# ------------------------------------------------------------ metrik hitung
def counting_metrics(pred: dict, gt: dict) -> dict:
    """MAE/RMSE (Pers. 3.12–3.13) atas seluruh pengamatan; MAPE (3.14) hanya y>0.

    pred/gt: dict {(interval, class, direction): count}. Kunci = gabungan keduanya
    (hilang dianggap 0) sehingga objek terlewat ataupun hitungan hantu terhukum.
    """
    keys = sorted(set(pred) | set(gt))
    y = np.array([gt.get(k, 0) for k in keys], float)
    yh = np.array([pred.get(k, 0) for k in keys], float)
    err = y - yh
    pos = y > 0
    rows = [dict(interval=k[0], **{"class": k[1]}, direction=k[2], y=int(y[i]), yhat=int(yh[i]),
                 abs_err=float(abs(err[i]))) for i, k in enumerate(keys)]
    return dict(
        T=len(keys),
        MAE=float(np.mean(np.abs(err))) if len(keys) else float("nan"),
        RMSE=float(np.sqrt(np.mean(err**2))) if len(keys) else float("nan"),
        MAPE=float(100 * np.mean(np.abs(err[pos]) / y[pos])) if pos.any() else float("nan"),
        mape_excluded=int((~pos).sum()),
        mape_excluded_frac=float((~pos).mean()) if len(keys) else 0.0,
        rows=rows,
    )


# --------------------------------------------------------------- pipeline
def run_counting(video, weights=None, detector=None, names=None, line=None, conf=0.25,
                 exclude=("pedestrian", "pejalan-kaki", "person"), interval_s=60,
                 gt_csv=None, out_dir="counting_out", save_video=False, device=None,
                 imgsz=640, max_frames=0):
    """Jalankan penghitungan pada satu video. Return dict ringkasan (+metrik bila ada GT)."""
    import supervision as sv

    warnings.filterwarnings("ignore", category=FutureWarning)  # deprecation sv.ByteTrack (<0.30)
    if detector is None:
        detector, names = make_detector(weights, imgsz=imgsz, device=device, conf=conf)
    assert names is not None, "names (peta id->nama kelas) wajib bila detector kustom"

    cap = cv2.VideoCapture(str(video))
    assert cap.isOpened(), f"video tidak terbuka: {video}"
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if line is None:
        line = (0, H // 2, W - 1, H // 2)
        print(f"[peringatan] --line tidak diberikan; memakai garis tengah {line}")
    x1, y1, x2, y2 = line
    lz = sv.LineZone(start=sv.Point(x1, y1), end=sv.Point(x2, y2))
    tracker = sv.ByteTrack(track_activation_threshold=conf, lost_track_buffer=int(fps),
                           minimum_matching_threshold=0.8, frame_rate=int(round(fps)))

    excl = {e.lower() for e in exclude}
    counts = defaultdict(int)
    events = []
    writer = None
    if save_video:
        out_v = Path(out_dir) / f"{Path(video).stem}_annotated.mp4"
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(str(out_v), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
        box_ann, lab_ann = sv.BoxAnnotator(), sv.LabelAnnotator()
        line_ann = sv.LineZoneAnnotator()

    f_idx, t_model = 0, 0.0
    t_all0 = time.time()
    while True:
        ok, frame = cap.read()
        if not ok or (max_frames and f_idx >= max_frames):
            break
        t0 = time.time()
        xyxy, cf, cl = detector(frame)
        t_model += time.time() - t0
        keep = np.array([names.get(int(c), str(c)).lower() not in excl for c in cl], bool) \
            if len(cl) else np.zeros(0, bool)
        det = sv.Detections(xyxy=xyxy[keep].reshape(-1, 4), confidence=cf[keep],
                            class_id=cl[keep].astype(int))
        det = tracker.update_with_detections(det)
        ci, co = lz.trigger(det)
        interval = int(f_idx / (fps * interval_s))
        for flag, dr in ((ci, "in"), (co, "out")):
            for j in np.where(flag)[0]:
                cname = names.get(int(det.class_id[j]), str(det.class_id[j]))
                counts[(interval, cname, dr)] += 1
                events.append(dict(time_s=round(f_idx / fps, 2), interval=interval,
                                   tracker_id=int(det.tracker_id[j]), **{"class": cname},
                                   direction=dr))
        if writer is not None:
            fr = box_ann.annotate(frame.copy(), det)
            labels = [f"#{tid} {names.get(int(c), c)}" for tid, c in zip(det.tracker_id, det.class_id)]
            fr = lab_ann.annotate(fr, det, labels)
            fr = line_ann.annotate(fr, lz)
            writer.write(fr)
        f_idx += 1
    cap.release()
    if writer is not None:
        writer.release()

    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    with open(out / "counts_per_interval.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["interval", "class", "direction", "count"])
        for (i, c, d), n in sorted(counts.items()):
            w.writerow([i, c, d, n])
    with open(out / "events.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["time_s", "interval", "tracker_id", "class", "direction"])
        w.writeheader(); w.writerows(events)

    summary = dict(video=str(video), frames=f_idx, fps_video=fps,
                   fps_model=f_idx / max(t_model, 1e-9),
                   fps_pipeline=f_idx / max(time.time() - t_all0, 1e-9),
                   line=list(line), interval_s=interval_s,
                   totals={f"{c}_{d}": n for (_, c, d), n in sorted(counts.items())
                           for n in [sum(v for (i2, c2, d2), v in counts.items()
                                         if c2 == c and d2 == d)]})
    if gt_csv:
        gtd = {}
        for r in csv.DictReader(open(gt_csv)):
            gtd[(int(r["interval"]), r["class"], r["direction"])] = int(r["count"])
        met = counting_metrics(dict(counts), gtd)
        rows = met.pop("rows")
        with open(out / "counting_errors.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["interval", "class", "direction", "y", "yhat", "abs_err"])
            w.writeheader(); w.writerows(rows)
        summary["metrics"] = met
        print(f"MAE={met['MAE']:.3f}  RMSE={met['RMSE']:.3f}  MAPE={met['MAPE']:.2f}% "
              f"(dikecualikan y=0: {met['mape_excluded']}/{met['T']})")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser(description="Penghitungan kendaraan ByteTrack + virtual line")
    ap.add_argument("--video", required=True)
    ap.add_argument("--weights", required=True, help="mis. runs_tesis/V8/weights/best.pt")
    ap.add_argument("--line", default=None, help="x1,y1,x2,y2 pada koordinat piksel video")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--interval-s", type=int, default=60)
    ap.add_argument("--gt", default=None, help="CSV hitung manual (lihat docstring)")
    ap.add_argument("--exclude", default="pedestrian,pejalan-kaki,person")
    ap.add_argument("--out", default="counting_out")
    ap.add_argument("--save-video", action="store_true")
    ap.add_argument("--device", default=None)
    ap.add_argument("--max-frames", type=int, default=0)
    a = ap.parse_args()
    line = tuple(int(v) for v in a.line.split(",")) if a.line else None
    run_counting(a.video, weights=a.weights, line=line, conf=a.conf, interval_s=a.interval_s,
                 gt_csv=a.gt, exclude=tuple(a.exclude.split(",")), out_dir=a.out,
                 save_video=a.save_video, device=a.device, max_frames=a.max_frames)


if __name__ == "__main__":
    main()
