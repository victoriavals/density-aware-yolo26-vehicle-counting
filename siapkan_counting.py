"""
siapkan_counting.py — Penyiap kit counting P9 (RQ5), TANPA GPU/model.

Membantu Naufal menyiapkan tiga prasyarat y26_counting.py yang hanya bisa
disediakan manusia: (1) memilih koordinat GARIS VIRTUAL, (2) memahami arah
in/out, (3) mengisi CSV hitung manual berformat interval,class,direction,count.

Fungsi:
  1. Inspeksi video: cetak resolusi, FPS, durasi, jumlah frame, jumlah interval.
  2. Preview garis: simpan frame pertama + garis kandidat + grid koordinat
     (px) sebagai gambar -> Naufal membaca koordinat garis dari situ.
  3. Template GT: buat CSV kerangka (interval × kelas-nonpejalan × arah) berisi
     count=0 siap diedit — jumlah interval dihitung dari durasi ÷ --interval-s.

Pakai (CPU saja, tak menyentuh training/GPU):
  # inspeksi + preview garis tengah default + grid
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4
  # preview garis kandidat tertentu (untuk verifikasi sebelum counting)
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --line 0,540,1919,540
  # buat kerangka GT (interval dihitung dari durasi video)
  python siapkan_counting.py --video video_uji/uji_ruas1.mp4 --interval-s 60 --make-gt-template

Setelah garis dipilih & GT diisi, jalankan counting sesuai README Tahap 3(c):
  python y26_counting.py --video video_uji/uji_ruas1.mp4 \
      --weights runs_tesis/V8/weights/best.pt \
      --line <x1,y1,x2,y2> --interval-s 60 --gt <gt.csv> --save-video
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np
import yaml

WARNA_GARIS = (0, 0, 255)
WARNA_GRID = (80, 80, 80)
WARNA_TEKS = (0, 255, 255)


def kelas_counting(data_yaml: str, exclude=("pedestrian", "pejalan-kaki", "person")) -> list[str]:
    names = yaml.safe_load(Path(data_yaml).read_text())["names"]
    names = list(names.values()) if isinstance(names, dict) else list(names)
    excl = {e.lower() for e in exclude}
    return [n for n in names if n.lower() not in excl]


def inspeksi(video: Path) -> dict:
    cap = cv2.VideoCapture(str(video))
    assert cap.isOpened(), f"video tidak terbuka: {video}"
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, frame0 = cap.read()
    cap.release()
    dur = n / fps if fps else float("nan")
    return dict(fps=fps, W=W, H=H, n_frames=n, durasi_s=dur,
                frame0=frame0 if ok else None)


def gambar_preview(frame: np.ndarray, line, out: Path, grid_step=None) -> None:
    im = frame.copy()
    H, W = im.shape[:2]
    step = grid_step or max(round(min(W, H) / 8 / 10) * 10, 50)
    for x in range(0, W, step):
        cv2.line(im, (x, 0), (x, H), WARNA_GRID, 1)
        cv2.putText(im, str(x), (x + 2, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WARNA_TEKS, 1)
    for y in range(0, H, step):
        cv2.line(im, (0, y), (W, y), WARNA_GRID, 1)
        cv2.putText(im, str(y), (2, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WARNA_TEKS, 1)
    x1, y1, x2, y2 = line
    cv2.line(im, (x1, y1), (x2, y2), WARNA_GARIS, 3)
    # panah normal garis: sisi "in"/"out" mengikuti orientasi start->end supervision
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    dx, dy = x2 - x1, y2 - y1
    L = max((dx**2 + dy**2) ** 0.5, 1)
    nx, ny = -dy / L, dx / L  # normal
    cv2.arrowedLine(im, (mx, my), (int(mx + 40 * nx), int(my + 40 * ny)), WARNA_GARIS, 2, tipLength=0.3)
    cv2.putText(im, f"garis {tuple(line)}", (10, H - 15), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, WARNA_GARIS, 2)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), im)


def ekstrak_frame(video: Path, fracs, out_dir: Path) -> list[dict]:
    """Simpan beberapa frame contoh (pada posisi relatif) sebagai bahan pemilih garis."""
    cap = cv2.VideoCapture(str(video))
    assert cap.isOpened(), f"video tidak terbuka: {video}"
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    out_dir.mkdir(parents=True, exist_ok=True)
    hasil = []
    for frac in fracs:
        idx = min(int(n * frac), max(n - 1, 0))
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, fr = cap.read()
        if not ok or fr is None:
            continue
        f = out_dir / f"{video.stem}_t{int(frac * 100):02d}.jpg"
        cv2.imwrite(str(f), fr, [cv2.IMWRITE_JPEG_QUALITY, 90])
        hasil.append(dict(file=f.name, label=f"{int(frac*100)}% (menit {idx/fps/60:.1f})"))
    cap.release()
    return hasil


def buat_line_picker(videos: list[Path], out_dir: Path, data_yaml: str, interval_s: int) -> Path:
    """Alat HTML interaktif: klik dua titik pada frame -> koordinat garis virtual.

    Menjawab kebutuhan Subbab 3.10.1 (koordinat kedua ujung garis dicatat dan
    dilaporkan). Menampilkan grid koordinat piksel, panah arah in/out, dan
    perintah y26_counting.py siap salin untuk tiap klip.
    """
    saran_file = out_dir / "saran_garis.json"
    saran = json.loads(saran_file.read_text()) if saran_file.exists() else {}
    klip = []
    for v in videos:
        info = inspeksi(v)
        frames = ekstrak_frame(v, (0.10, 0.50, 0.90), out_dir)
        gerak = out_dir / f"GERAK_{v.stem}.jpg"
        if gerak.exists():  # peta gerakan: memperlihatkan jalur yang benar-benar dilalui
            frames.append(dict(file=gerak.name, label="peta gerakan (seluruh klip)"))
        n_iv = max(int(np.ceil(info["durasi_s"] / interval_s)), 1)
        klip.append(dict(nama=v.name, stem=v.stem, W=info["W"], H=info["H"],
                         fps=round(info["fps"], 2), durasi=round(info["durasi_s"], 1),
                         n_interval=n_iv, frames=frames, saran=saran.get(v.stem)))
    data = json.dumps(klip, ensure_ascii=False)
    html = _LINE_PICKER_HTML.replace("__DATA__", data).replace("__INTERVAL__", str(interval_s))
    out = out_dir / "pilih_garis.html"
    out.write_text(html, encoding="utf-8")
    return out


_LINE_PICKER_HTML = """<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"><title>Pemilih Garis Virtual</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;background:#111;color:#eee}
 #bar{padding:10px 14px;background:#1d1d1d;position:sticky;top:0;z-index:5;border-bottom:1px solid #333}
 select,button{font-size:14px;padding:7px 12px;margin:3px;border-radius:7px;border:0;cursor:pointer}
 button{background:#37474f;color:#fff} button.pri{background:#1565c0} button.warn{background:#c62828}
 #wrap{padding:12px;text-align:center} canvas{border:1px solid #444;cursor:crosshair;max-width:100%}
 #info{font-family:ui-monospace,monospace;font-size:14px;background:#1a1a1a;padding:10px 14px;
       margin:10px auto;max-width:1100px;text-align:left;border-radius:8px;line-height:1.7}
 .cmd{background:#0d1b0d;color:#9f9;padding:8px 10px;border-radius:6px;word-break:break-all;font-size:13px}
 .hint{color:#aaa;font-size:13px;max-width:1100px;margin:6px auto;text-align:left}
 b.ok{color:#7fdc7f} b.no{color:#ff8a80}
</style></head><body>
<div id="bar">
  <b>Pemilih Garis Virtual</b>
  klip: <select id="klip"></select>
  frame: <select id="frame"></select>
  <button onclick="reset()">Ulangi titik</button>
  <button onclick="toggleGrid()">Grid on/off</button>
  <button onclick="pakaiSaran()">Pakai usulan</button>
  <button class="pri" onclick="salin()">Salin perintah</button>
  <span id="stat"></span>
</div>
<div class="hint">
  <b>Cara:</b> klik <b>titik A</b> lalu <b>titik B</b> pada gambar untuk menarik garis (klik ketiga mengulang).
  Gunakan <b>tombol panah</b> untuk menggeser titik terakhir 1 piksel (tahan Shift = 10 piksel).
  Garis sebaiknya <b>memotong seluruh lebar lajur</b>, <b>tegak lurus arah kendaraan</b>, dan di area
  <b>bebas terhalang</b> tiang/reklame. Panah merah menunjukkan sisi <b>in</b> (arah sebaliknya = out).
  Periksa garis pada ketiga frame (10%, 50%, 90%) agar tetap cocok sepanjang klip.
</div>
<div id="wrap"><canvas id="cv"></canvas></div>
<div id="info"></div>
<script>
const KLIP = __DATA__, INTERVAL = __INTERVAL__;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
let ki = 0, fi = 0, A = null, B = null, grid = true, img = new Image(), skala = 1;
const selK = document.getElementById('klip'), selF = document.getElementById('frame');
KLIP.forEach((k, i) => selK.add(new Option(`${k.nama} (${k.W}x${k.H}, ${k.durasi}s)`, i)));
selK.onchange = () => { ki = +selK.value; fi = 0; A = B = null; isiFrame(); muat(); };
selF.onchange = () => { fi = +selF.value; muat(); };

function isiFrame(){ selF.innerHTML=''; KLIP[ki].frames.forEach((f,i)=>selF.add(new Option(f.label,i))); }
function muat(){ img = new Image(); img.onload = gambar; img.src = KLIP[ki].frames[fi].file; }
function gambar(){
  const k = KLIP[ki], maxW = Math.min(window.innerWidth - 40, 1280);
  skala = Math.min(maxW / k.W, 1);
  cv.width = Math.round(k.W * skala); cv.height = Math.round(k.H * skala);
  ctx.drawImage(img, 0, 0, cv.width, cv.height);
  if (grid) {
    const step = 100 * skala;
    ctx.strokeStyle = 'rgba(255,255,255,.22)'; ctx.lineWidth = 1;
    ctx.fillStyle = '#ffe600'; ctx.font = '11px monospace';
    for (let x = 0; x < k.W; x += 100) { const cx = x*skala;
      ctx.beginPath(); ctx.moveTo(cx,0); ctx.lineTo(cx,cv.height); ctx.stroke();
      if (x % 200 === 0) ctx.fillText(x, cx+2, 12); }
    for (let y = 0; y < k.H; y += 100) { const cy = y*skala;
      ctx.beginPath(); ctx.moveTo(0,cy); ctx.lineTo(cv.width,cy); ctx.stroke();
      if (y % 200 === 0) ctx.fillText(y, 2, cy+12); }
  }
  const sr = KLIP[ki].saran;
  if (sr) {  // garis usulan (putus-putus) sebagai acuan; tekan "Pakai usulan" untuk memakainya
    ctx.save(); ctx.setLineDash([12, 10]); ctx.strokeStyle = '#00e676'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(sr[0]*skala, sr[1]*skala); ctx.lineTo(sr[2]*skala, sr[3]*skala);
    ctx.stroke(); ctx.restore();
  }
  if (A) titik(A, '#00e5ff', 'A');
  if (B) titik(B, '#00e5ff', 'B');
  if (A && B) {
    const a = [A[0]*skala, A[1]*skala], b = [B[0]*skala, B[1]*skala];
    ctx.strokeStyle = '#ff2b2b'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke();
    const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2, dx=b[0]-a[0], dy=b[1]-a[1];
    const L=Math.hypot(dx,dy)||1, nx=-dy/L, ny=dx/L, p=45;
    ctx.beginPath(); ctx.moveTo(mx,my); ctx.lineTo(mx+nx*p, my+ny*p); ctx.stroke();
    const ang=Math.atan2(ny,nx);
    ctx.beginPath(); ctx.moveTo(mx+nx*p, my+ny*p);
    ctx.lineTo(mx+nx*p-12*Math.cos(ang-.4), my+ny*p-12*Math.sin(ang-.4));
    ctx.lineTo(mx+nx*p-12*Math.cos(ang+.4), my+ny*p-12*Math.sin(ang+.4));
    ctx.closePath(); ctx.fillStyle='#ff2b2b'; ctx.fill();
    ctx.fillText('in', mx+nx*(p+14), my+ny*(p+14));
  }
  info();
}
function titik(P, warna, label){ const x=P[0]*skala, y=P[1]*skala;
  ctx.fillStyle=warna; ctx.beginPath(); ctx.arc(x,y,5,0,7); ctx.fill();
  ctx.font='13px monospace'; ctx.fillText(`${label} (${P[0]},${P[1]})`, x+8, y-8); }
cv.onclick = e => { const r = cv.getBoundingClientRect();
  const x = Math.round((e.clientX-r.left) * (cv.width/r.width) / skala);
  const y = Math.round((e.clientY-r.top) * (cv.height/r.height) / skala);
  if (!A || (A && B)) { A = [x,y]; B = null; } else { B = [x,y]; }
  gambar(); };
document.addEventListener('keydown', e => {
  const P = B || A; if (!P) return;
  const d = e.shiftKey ? 10 : 1; let u = true;
  if (e.key==='ArrowLeft') P[0]-=d; else if (e.key==='ArrowRight') P[0]+=d;
  else if (e.key==='ArrowUp') P[1]-=d; else if (e.key==='ArrowDown') P[1]+=d; else u=false;
  if (u) { e.preventDefault(); gambar(); } });
function reset(){ A=B=null; gambar(); }
function toggleGrid(){ grid=!grid; gambar(); }
function pakaiSaran(){ const sr = KLIP[ki].saran;
  if (!sr) { alert('Belum ada usulan untuk klip ini.'); return; }
  A = [sr[0], sr[1]]; B = [sr[2], sr[3]]; gambar(); }
function perintah(){ const k=KLIP[ki];
  return A&&B ? `python y26_counting.py --video video_uji/${k.nama} --weights runs_tesis/V8/weights/best.pt --line ${A[0]},${A[1]},${B[0]},${B[1]} --interval-s ${INTERVAL} --gt video_uji/gt_${k.stem}.csv --save-video` : ''; }
function info(){ const k=KLIP[ki];
  document.getElementById('info').innerHTML =
    `<b>${k.nama}</b> — ${k.W}x${k.H} px, ${k.fps} fps, ${k.durasi} dtk, <b>${k.n_interval} interval</b> @ ${INTERVAL} dtk<br>` +
    (A&&B ? `garis: <b class=ok>--line ${A[0]},${A[1]},${B[0]},${B[1]}</b> (panjang ${Math.round(Math.hypot(B[0]-A[0],B[1]-A[1]))} px)<br>
             <div class=cmd>${perintah()}</div>`
          : `<b class=no>belum ada garis</b> — klik titik A lalu titik B`);
  document.getElementById('stat').textContent = A&&B ? ' | garis siap' : ' | klik 2 titik'; }
function salin(){ const c = perintah();
  if (!c) { alert('Tarik garisnya dulu (klik dua titik).'); return; }
  navigator.clipboard.writeText(c).then(()=>alert('Perintah disalin:\\n\\n'+c),
    ()=>prompt('Salin manual:', c)); }
window.onresize = gambar;
isiFrame(); muat();
</script></body></html>"""


def peta_gerakan(video: Path, out_dir: Path, line=None, n_sample: int = 240,
                 n_bg: int = 40, skala: float = 0.5, thr: int = 28) -> Path:
    """Peta frekuensi gerakan sepanjang klip — bukti objektif jalur lalu lintas.

    Latar dibangun dari median beberapa frame (objek bergerak tersaring), lalu tiap
    frame contoh dibandingkan terhadap latar; piksel yang cukup berbeda dihitung.
    Hasilnya menunjukkan LAJUR yang benar-benar dilewati kendaraan, sehingga garis
    virtual dapat ditempatkan agar memotong seluruh jalur (Subbab 3.10.1) — bukan
    ditebak dari satu frame diam.
    """
    cap = cv2.VideoCapture(str(video))
    assert cap.isOpened(), f"video tidak terbuka: {video}"
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def ambil(idx):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, fr = cap.read()
        if not ok or fr is None:
            return None
        return cv2.resize(fr, None, fx=skala, fy=skala, interpolation=cv2.INTER_AREA)

    bg_stack = [f for f in (ambil(i) for i in np.linspace(0, n - 1, n_bg)) if f is not None]
    bg = np.median(np.stack(bg_stack), axis=0).astype(np.uint8)
    bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)

    akum = np.zeros(bg_gray.shape, np.float32)
    dipakai = 0
    for i in np.linspace(0, n - 1, n_sample):
        fr = ambil(i)
        if fr is None:
            continue
        d = cv2.absdiff(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), bg_gray)
        akum += (d > thr).astype(np.float32)
        dipakai += 1
    cap.release()

    frek = akum / max(dipakai, 1)
    frek = cv2.GaussianBlur(frek, (0, 0), 3)
    norm = np.clip(frek / max(frek.max(), 1e-6), 0, 1)
    heat = cv2.applyColorMap((norm * 255).astype(np.uint8), cv2.COLORMAP_JET)
    vis = cv2.addWeighted(bg, 0.55, heat, 0.45, 0)
    vis = cv2.resize(vis, None, fx=1 / skala, fy=1 / skala, interpolation=cv2.INTER_LINEAR)
    if line is not None:
        x1, y1, x2, y2 = line
        cv2.line(vis, (x1, y1), (x2, y2), (255, 255, 255), 5)
        cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 0), 2)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"GERAK_{video.stem}.jpg"
    cv2.imwrite(str(out), vis, [cv2.IMWRITE_JPEG_QUALITY, 88])

    # cakupan garis: berapa persen gerakan berada di sisi masing-masing garis
    if line is not None:
        H, W = frek.shape
        ys, xs = np.mgrid[0:H, 0:W]
        x1s, y1s, x2s, y2s = (v * skala for v in line)
        sisi = (x2s - x1s) * (ys - y1s) - (y2s - y1s) * (xs - x1s)
        tot = frek.sum()
        pos = frek[sisi > 0].sum() / max(tot, 1e-9)
        print(f"   sebaran gerakan: {pos*100:.1f}% di satu sisi, {(1-pos)*100:.1f}% di sisi lain")
    return out


def buat_template_gt(video: Path, info: dict, interval_s: int, kelas: list[str], out: Path) -> int:
    n_interval = max(int(np.ceil(info["durasi_s"] / interval_s)), 1)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["interval", "class", "direction", "count"])
        for i in range(n_interval):
            for c in kelas:
                for d in ("in", "out"):
                    w.writerow([i, c, d, 0])
    return n_interval


def main() -> None:
    ap = argparse.ArgumentParser(description="Penyiap kit counting P9 (tanpa GPU)")
    ap.add_argument("--video", help="satu berkas video (wajib kecuali --make-line-picker)")
    ap.add_argument("--data", default="dataset/data.yaml")
    ap.add_argument("--make-line-picker", action="store_true",
                    help="bangun alat HTML interaktif pemilih garis untuk SEMUA video di --video-dir")
    ap.add_argument("--video-dir", default="video_uji")
    ap.add_argument("--line", default=None, help="x1,y1,x2,y2 piksel; default garis tengah")
    ap.add_argument("--interval-s", type=int, default=60)
    ap.add_argument("--make-gt-template", action="store_true")
    ap.add_argument("--out-dir", default="video_uji/preview")
    a = ap.parse_args()

    if a.make_line_picker:
        vids = sorted(p for p in Path(a.video_dir).glob("*")
                      if p.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv"))
        if not vids:
            raise SystemExit(f"[gagal] tak ada video di {a.video_dir}/")
        out_dir = Path(a.out_dir)
        html = buat_line_picker(vids, out_dir, a.data, a.interval_s)
        for v in vids:
            info = inspeksi(v)
            n_iv = max(int(np.ceil(info["durasi_s"] / a.interval_s)), 1)
            print(f"  {v.name}: {info['W']}x{info['H']} @ {info['fps']:.2f} fps, "
                  f"{info['durasi_s']/60:.2f} mnt -> {n_iv} interval")
        print(f"\nAlat pemilih garis: {html}")
        print("Buka di browser, klik dua titik per klip, lalu salin perintahnya.")
        return

    if not a.video:
        raise SystemExit("[gagal] --video wajib diisi (atau pakai --make-line-picker)")
    video = Path(a.video)
    info = inspeksi(video)
    print(f"== {video.name} ==")
    print(f"  resolusi   : {info['W']}x{info['H']} px")
    print(f"  FPS        : {info['fps']:.2f}")
    print(f"  frame      : {info['n_frames']}")
    print(f"  durasi     : {info['durasi_s']:.1f} s ({info['durasi_s']/60:.1f} mnt)")
    n_iv = max(int(np.ceil(info['durasi_s'] / a.interval_s)), 1)
    print(f"  interval   : {n_iv} jendela @ {a.interval_s} s")

    line = ([int(v) for v in a.line.split(",")] if a.line
            else (0, info["H"] // 2, info["W"] - 1, info["H"] // 2))
    print(f"  garis      : {tuple(line)}" + ("" if a.line else "  (tengah default — sesuaikan!)"))

    if info["frame0"] is not None:
        prev = Path(a.out_dir) / f"{video.stem}_garis.jpg"
        gambar_preview(info["frame0"], line, prev)
        print(f"  preview    : {prev}  (buka untuk baca koordinat & cek arah panah in/out)")
    else:
        print("  [peringatan] frame pertama gagal dibaca — cek codec video")

    if a.make_gt_template:
        kelas = kelas_counting(a.data)
        gt = video.with_name(f"gt_{video.stem}.csv")
        n = buat_template_gt(video, info, a.interval_s, kelas, gt)
        print(f"  template GT: {gt}  ({n} interval × {len(kelas)} kelas × 2 arah "
              f"= {n*len(kelas)*2} baris, count=0 — isi manual)")
        print(f"  kelas dihitung (pejalan kaki dikecualikan): {kelas}")


if __name__ == "__main__":
    main()
