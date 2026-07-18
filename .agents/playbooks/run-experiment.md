# Playbook: Menjalankan Eksperimen — Running the Experiments

> **EN — TL;DR:** Mandatory order: `test_smoke.py` must **pass** → grid search (`--tune-dalw`) → train `V1..V8` (`--variant all`, priority V1→V4→V8) → resume interrupted runs (`--variant Vx --resume`). Everything runs as a **background** job with a timestamped `awk` log and an **absolute** `--project`. Batch 16 (fallback = batch 8 for **all** variants if OOM — proven unnecessary). Monitor with `Get-Content`. Never loosen the shared config (seed 0, identical batch).

Berkas sumber: `CLAUDE.md` §13 + §15; `train_ablation.py`, `test_smoke.py`.

## 0. Prasyarat

- `.venv` aktif (Python 3.11.9, torch cu128, ultralytics 8.4.92). Lihat [Lingkungan](../knowledge/environment.md).
- **`python test_smoke.py` T1–T4 LULUS** (wajib sebelum training apa pun). Lihat skill `smoke-test`.
- GPU bebas; `dataset/` = hasil *group split* aktif ([Dataset](../knowledge/dataset.md)).

## 1. Urutan wajib

```bash
# (a) Grid search α,σ sekali pada V8 (pelatihan dipersingkat) → dalw_best.json
python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60

# (b) Latih 8 varian berurutan (dalw_best.json dibaca otomatis)
python train_ablation.py --data dataset/data.yaml --variant all      # prioritas V1→V4→V8

# (c) Lanjutkan bila terputus
python train_ablation.py --data dataset/data.yaml --variant V5 --resume
```

Bungkus setiap perintah panjang sebagai **background process** + pipe ke konvensi awk log berstempel-waktu, dan **WAJIB `--project` ABSOLUT** menunjuk `<repo>/runs_tesis` (gotcha P3). Detail konvensi: [Logging & status](../rules/logging-and-status.md).

## 2. Konfigurasi terkunci (jangan diubah)

seed 0 deterministik; imgsz 640; MuSGD; lr0 0,01 cosine; maks 300 epoch + *early stopping* patience 50; batch **16** FP16 identik untuk **kedelapan** varian; α=1,0 σ=0,1 (dari `dalw_best.json`). Aturan A-12: bila OOM pada varian ber-P2 → turunkan batch untuk **SEMUA** varian (AutoBatch dilarang). Terbukti tak terpicu. Invarian lengkap: [Invarian metodologi](../rules/methodology-invariants.md).

## 3. Memantau & interpretasi

```
Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8
```

Notifikasi harness **"stopped" umumnya selesai-normal**, bukan crash (job selamat tutup VS Code). Keluaran per varian: `runs_tesis/<V>/` berisi `results.csv`, `weights/{best,last}.pt`, `nmsfree_probe.csv` (A-10), `complexity_train.json` (Tabel 3.7). **Backup `runs_tesis/` sebelum evaluasi.**

## Langkah berikutnya

Setelah semua varian selesai → [Playbook evaluasi](evaluate.md).

## Tautan terkait

- [Invarian metodologi](../rules/methodology-invariants.md) · [Logging & status](../rules/logging-and-status.md) · [Varian V1–V8](../architecture/variants.md) · [DALW](../knowledge/dalw.md) · [Alur data](../architecture/data-flow.md).
