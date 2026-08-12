"""
webtest/app.py — Website pengujian model YOLO26 (V1-V8 + varian tambahan).

Alat bantu DI LUAR scope tesis (lihat CLAUDE.md §8: "Kode website DI LUAR scope
tesis — scope hanya model s.d. evaluasi"). Tujuannya murni demo/QA visual: pilih
varian, unggah gambar atau video, lihat hasil deteksi/penghitungan. Tidak
menyentuh eval_out/, runs_tesis/, atau naskah — hanya MEMBACA bobot terlatih.

Jalankan:
    .venv/Scripts/python.exe webtest/app.py
    -> buka http://localhost:8420
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import threading
import time
import uuid
import warnings
from pathlib import Path

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from y26_modules import register_ham  # noqa: E402
from y26_counting import run_counting  # noqa: E402

TEMP_DIR = Path(__file__).resolve().parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)
RUNS_DIR = REPO_ROOT / "runs_tesis"
IMGSZ = 640
CLASS_COLORS_BGR = {
    "big-vehicle": (255, 100, 0),
    "car": (255, 0, 0),
    "pedestrian": (0, 255, 0),
    "two-wheeler": (0, 165, 255),
}
DEFAULT_COLOR_BGR = (200, 200, 200)
COUNT_EXCLUDE = ("pedestrian", "pejalan-kaki", "person")

VARIANT_META = {
    "V1": {"label": "V1 — Baseline", "ham": False, "p2": False, "dalw": False},
    "V2": {"label": "V2 — HAM", "ham": True, "p2": False, "dalw": False},
    "V3": {"label": "V3 — P2", "ham": False, "p2": True, "dalw": False},
    "V4": {"label": "V4 — DALW (α=1,0 σ=0,1)", "ham": False, "p2": False, "dalw": True},
    "V5": {"label": "V5 — HAM+P2", "ham": True, "p2": True, "dalw": False},
    "V6": {"label": "V6 — HAM+DALW", "ham": True, "p2": False, "dalw": True},
    "V7": {"label": "V7 — P2+DALW", "ham": False, "p2": True, "dalw": True},
    "V8": {"label": "V8 — Model Penuh (HAM+P2+DALW)", "ham": True, "p2": True, "dalw": True},
    "V4_a0.5": {"label": "V4 — DALW (α=0,5, sensitivitas)", "ham": False, "p2": False, "dalw": True},
    "V4_a2.0": {"label": "V4 — DALW (α=2,0, sensitivitas)", "ham": False, "p2": False, "dalw": True},
    "V8_normw": {"label": "V8 — Model Penuh (normalisasi-per-bobot)", "ham": True, "p2": True, "dalw": True},
}

app = FastAPI(title="Traffic Pulse — Model Tester (Tesis YOLO26)")

_register_lock = threading.Lock()
_ham_registered = False


def ensure_ham():
    global _ham_registered
    with _register_lock:
        if not _ham_registered:
            register_ham()
            _ham_registered = True


# --------------------------------------------------------------- varian
def list_variants():
    out = []
    if not RUNS_DIR.exists():
        return out
    for d in sorted(RUNS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("tune_"):
            continue
        weights = d / "weights" / "best.pt"
        if not weights.exists():
            continue
        meta = VARIANT_META.get(d.name, {"label": d.name, "ham": None, "p2": None, "dalw": None})
        out.append({"id": d.name, "weights": str(weights), **meta})
    return out


def variant_weights_path(variant_id: str) -> Path:
    for v in list_variants():
        if v["id"] == variant_id:
            return Path(v["weights"])
    raise HTTPException(404, f"Varian '{variant_id}' tidak ditemukan di runs_tesis/")


# --------------------------------------------------------- pemuat model (satu slot)
_model_lock = threading.Lock()
_loaded = {"variant": None, "nn_model": None, "names": None, "device": None}


def get_model(variant_id: str):
    """Muat model varian ke GPU/CPU; hanya satu varian aktif sekaligus (hemat VRAM 8GB)."""
    with _model_lock:
        if _loaded["variant"] == variant_id and _loaded["nn_model"] is not None:
            return _loaded["nn_model"], _loaded["names"], _loaded["device"]

        ensure_ham()
        weights = variant_weights_path(variant_id)
        if _loaded["nn_model"] is not None:
            del _loaded["nn_model"]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        from ultralytics import YOLO

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        model = YOLO(str(weights))
        nn_model = model.model.to(device).eval()
        names = model.names if isinstance(model.names, dict) else dict(enumerate(model.names))

        _loaded.update(variant=variant_id, nn_model=nn_model, names=names, device=device)
        return nn_model, names, device


def raw_detect(nn_model, device, frame_bgr: np.ndarray, imgsz: int = IMGSZ):
    """Forward mentah kepala one-to-one -> (xyxy piksel frame, conf, cls). Lihat y26_counting.make_detector."""
    h0, w0 = frame_bgr.shape[:2]
    r = min(imgsz / h0, imgsz / w0)
    nw, nh = round(w0 * r), round(h0 * r)
    left, top = (imgsz - nw) // 2, (imgsz - nh) // 2
    canvas = np.full((imgsz, imgsz, 3), 114, np.uint8)
    canvas[top : top + nh, left : left + nw] = cv2.resize(frame_bgr, (nw, nh))
    t = torch.from_numpy(canvas[:, :, ::-1].copy()).permute(2, 0, 1).float().div_(255)[None].to(device)
    with torch.no_grad():
        out = nn_model(t)
    p = (out[0] if isinstance(out, tuple) else out)[0].float().cpu().numpy()
    xyxy = p[:, :4].copy()
    xyxy[:, [0, 2]] = (xyxy[:, [0, 2]] - left) / r
    xyxy[:, [1, 3]] = (xyxy[:, [1, 3]] - top) / r
    xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, w0 - 1)
    xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, h0 - 1)
    return xyxy, p[:, 4], p[:, 5].astype(int)


def draw_detections(frame_bgr, xyxy, conf, cls, names):
    out = frame_bgr.copy()
    for (x1, y1, x2, y2), c, cl in zip(xyxy, conf, cls):
        name = names.get(int(cl), str(cl))
        color = CLASS_COLORS_BGR.get(name, DEFAULT_COLOR_BGR)
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(out, p1, p2, color, 2)
        label = f"{name} {c:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (p1[0], max(0, p1[1] - th - 6)), (p1[0] + tw + 4, p1[1]), color, -1)
        cv2.putText(out, label, (p1[0] + 2, max(12, p1[1] - 4)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return out


# ------------------------------------------------------------------ API
@app.get("/api/variants")
def api_variants():
    return {"variants": list_variants(), "gpu": torch.cuda.is_available(),
             "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"}


@app.post("/api/detect/image")
async def api_detect_image(file: UploadFile = File(...), variant: str = Form(...),
                            confidence: float = Form(0.25)):
    data = await file.read()
    arr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Berkas gambar tidak dapat dibaca")

    nn_model, names, device = get_model(variant)
    t0 = time.time()
    xyxy, conf, cls = raw_detect(nn_model, device, frame)
    infer_ms = (time.time() - t0) * 1000
    keep = conf >= confidence
    xyxy, conf, cls = xyxy[keep], conf[keep], cls[keep]

    annotated = draw_detections(frame, xyxy, conf, cls, names)
    ok, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise HTTPException(500, "Gagal mengkodekan gambar hasil")

    counts = {}
    for cl in cls:
        name = names.get(int(cl), str(cl))
        counts[name] = counts.get(name, 0) + 1
    detections = [
        {"class": names.get(int(cl), str(cl)), "confidence": round(float(c), 4),
         "bbox": [round(float(v), 1) for v in box]}
        for box, c, cl in zip(xyxy.tolist(), conf.tolist(), cls.tolist())
    ]

    import base64
    return JSONResponse({
        "variant": variant,
        "inference_ms": round(infer_ms, 1),
        "total_detections": int(len(cls)),
        "counts_by_class": counts,
        "detections": detections,
        "image_base64": "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode(),
    })


@app.post("/api/video/prepare")
async def api_video_prepare(file: UploadFile = File(...)):
    token = uuid.uuid4().hex[:12]
    job_dir = TEMP_DIR / token
    job_dir.mkdir(parents=True, exist_ok=True)
    src_path = job_dir / f"source_{file.filename}"
    with open(src_path, "wb") as fh:
        shutil.copyfileobj(file.file, fh)

    cap = cv2.VideoCapture(str(src_path))
    if not cap.isOpened():
        raise HTTPException(400, "Video tidak dapat dibuka (format tidak didukung)")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise HTTPException(400, "Tidak dapat membaca frame pertama video")

    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    import base64
    return JSONResponse({
        "token": token, "width": w, "height": h, "fps": round(fps, 2),
        "duration_s": round(n_frames / fps, 1) if fps else None, "frames": n_frames,
        "first_frame_base64": "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode(),
        "source_filename": src_path.name,
    })


JOBS: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _reencode_h264(src: Path, dst: Path):
    """mp4v (OpenCV) tak dapat diputar sebagian besar browser -> transkode H.264 via ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        shutil.copy(src, dst)
        return
    subprocess.run([ffmpeg, "-y", "-i", str(src), "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)],
                   check=True, capture_output=True)


def _run_video_job(job_id: str, video_path: Path, job_dir: Path, variant: str,
                    confidence: float, line: tuple[int, int, int, int]):
    try:
        JOBS[job_id]["status"] = "processing"
        warnings.filterwarnings("ignore", category=FutureWarning)
        nn_model, names, device = get_model(variant)

        def detector(frame_bgr):
            xyxy, conf, cls = raw_detect(nn_model, device, frame_bgr)
            keep = conf >= confidence
            return xyxy[keep], conf[keep], cls[keep]

        out_dir = job_dir / "out"
        summary = run_counting(
            video_path, detector=detector, names=names, line=line, conf=confidence,
            exclude=COUNT_EXCLUDE, interval_s=3600, out_dir=str(out_dir),
            save_video=True, device=device,
        )
        raw_video = next(out_dir.glob("*_annotated.mp4"))
        final_video = job_dir / "annotated_h264.mp4"
        _reencode_h264(raw_video, final_video)

        with _jobs_lock:
            JOBS[job_id].update(status="completed", summary=summary,
                                 video_path=str(final_video))
    except Exception as exc:  # noqa: BLE001
        with _jobs_lock:
            JOBS[job_id].update(status="error", error=str(exc))


@app.post("/api/video/process")
async def api_video_process(token: str = Form(...), variant: str = Form(...),
                             confidence: float = Form(0.25),
                             line: str = Form(...)):
    job_dir = TEMP_DIR / token
    sources = list(job_dir.glob("source_*"))
    if not job_dir.exists() or not sources:
        raise HTTPException(404, "Token video tidak ditemukan; unggah ulang video")
    video_path = sources[0]
    x1, y1, x2, y2 = (int(v) for v in line.split(","))

    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {"status": "pending", "variant": variant}
    th = threading.Thread(target=_run_video_job, args=(job_id, video_path, job_dir, variant,
                                                        confidence, (x1, y1, x2, y2)), daemon=True)
    th.start()
    return {"job_id": job_id}


@app.get("/api/video/job/{job_id}")
def api_video_job(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "Job tidak ditemukan")
    resp = {"status": job["status"]}
    if job["status"] == "completed":
        resp["summary"] = job["summary"]
        resp["video_url"] = f"/api/video/job/{job_id}/video"
    elif job["status"] == "error":
        resp["error"] = job["error"]
    return resp


@app.get("/api/video/job/{job_id}/video")
def api_video_job_video(job_id: str):
    job = JOBS.get(job_id)
    if job is None or job.get("status") != "completed":
        raise HTTPException(404, "Video belum siap")
    return FileResponse(job["video_path"], media_type="video/mp4")


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8420)
