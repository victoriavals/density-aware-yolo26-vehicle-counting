# Prompt Pack v2 — Claude Code (Extension) + Session Zellij `nfl` sebagai Layar Pantau

**Konsep:** Claude Code berjalan di extension VS Code seperti biasa. Setiap pekerjaan
panjang (grid search, training, evaluasi, counting) TIDAK dijalankan di shell Claude,
melainkan **dilempar ke dalam session Zellij bernama `nfl`** sebagai pane bernama
(`tune`, `train`, `eval`, `count`). Dengan begitu:

- **Anda** memantau secara live: buka terminal mana pun → `zellij attach nfl` → lihat
  semua pane berjalan; lepas dengan `Ctrl+o` `d` tanpa mengganggu apa pun.
- **Claude** memantau lewat berkas log (`logs/*.log`) karena ia tidak bisa melihat pane.
- Perintah peluncuran kembali seketika, jadi shell extension tidak pernah menggantung
  berjam-jam menunggu training.

> Prasyarat: root proyek (mis. `~/tesis/`) berisi `CLAUDE.md` + folder `model_tesis/`.

---

## BAGIAN A — Setup sekali saja (sisi Anda, bukan Claude)

Zellij hanya ada di Linux/macOS. Di PC Windows: pakai **WSL2 Ubuntu**, dan — ini
penting untuk extension — **buka folder proyek sebagai VS Code WSL Remote** (ikon
hijau pojok kiri bawah → *Connect to WSL*, atau `code .` dari terminal Ubuntu).
Dengan begitu shell yang dipakai extension Claude Code adalah bash di WSL, tempat
Zellij hidup. CUDA RTX 4060 didukung penuh di WSL2 (driver cukup yang di Windows).

```bash
# di terminal WSL Ubuntu
curl -fsSL https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz | tar xz
sudo mv zellij /usr/local/bin/ && zellij --version   # butuh >= 0.41 utk --create-background
```

Cara Anda menonton kapan pun (dari VS Code terminal WSL atau Windows Terminal→Ubuntu):

```bash
zellij attach nfl        # masuk; pindah pane: Ctrl+p lalu panah; scroll: Ctrl+s
# lepas tanpa menghentikan apa pun: Ctrl+o lalu d
```

Atur *Power & sleep* Windows agar PC tidak tidur selama training (WSL ikut terjeda).

---

## BAGIAN B — Sepuluh Prompt (tempel ke Claude Code satu per satu, berurutan)

### Prompt 1 — Orientasi, lingkungan, session `nfl`, uji kebenaran

```text
Baca CLAUDE.md dan model_tesis/README.md sampai selesai sebelum bertindak.

Konteks operasional sesi ini: semua pekerjaan panjang WAJIB kamu jalankan di dalam
session Zellij bernama 'nfl' (bukan di shell-mu) memakai bentuk:
  zellij --session nfl run --name <nama-pane> --cwd <dir> -- bash -lc '<perintah> 2>&1 | tee <log>'
supaya saya bisa memantaunya via `zellij attach nfl`. Kamu sendiri memantau lewat
berkas log di logs/.

Kerjakan berurutan, laporkan tiap butir:
1. Verifikasi zellij terpasang (zellij --version). Buat session latar belakang:
   zellij attach --create-background nfl
   lalu verifikasi muncul di `zellij list-sessions`. Jika flag --create-background
   tidak dikenali (zellij lama), pakai fallback pty:
   setsid script -qfc "zellij --session nfl" /dev/null >/dev/null 2>&1 & sleep 1; zellij list-sessions
2. Buat virtualenv .venv (Python 3.11.9) di root proyek bila belum ada, aktifkan.
3. Instal dependensi DENGAN URUTAN INI (torch CUDA dulu agar tak tertimpa versi CPU):
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   pip install ultralytics==8.4.92 roboflow supervision scipy pandas
4. Verifikasi GPU: python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
   Harus True dan menyebut RTX 4060; jika False, diagnosis dulu.
5. mkdir -p logs hasil
6. Uji kebenaran (boleh di shell-mu langsung karena cepat):
   cd model_tesis && python test_smoke.py
   Semua uji harus LULUS. Jika ADA yang gagal: BERHENTI total, tampilkan output
   lengkap, jangan mengubah kode apa pun, minta keputusan saya.

Larangan tetap: jangan memodifikasi berkas .py; ultralytics dikunci 8.4.92.
Akhiri dengan tabel status per butir.
```

### Prompt 2 — Dataset + bukti anti-leakage

```text
Unduh dataset sesuai Subbab 3.3 (CLAUDE.md §5). Dari folder model_tesis:

python download_dataset.py --api-key <ISI_API_KEY_ROBOFLOW_SAYA> --version <N>

(Jika placeholder belum kuisi, tanya saya dulu — jangan menebak.)

Setelah selesai:
1. Konfirmasi skrip lolos verifikasi split; JANGAN pernah re-split lokal.
2. Buat bukti anti-leakage: bukti_split_grup.csv berisi daftar grup
   kamera-adegan-sesi per subset (train/valid/test) + jumlah citranya, diturunkan
   dari struktur dataset hasil unduhan.
3. Laporkan tabel ringkas: jumlah citra per subset (harus mendekati 2.372/678/339)
   dan jumlah instance per kelas per subset.
```

### Prompt 3 — Grid search α,σ → pane `tune` di session `nfl`

```text
Luncurkan grid search DALW (Subbab 3.9) ke session 'nfl' sebagai pane 'tune':

zellij --session nfl run --name tune --cwd "$PWD/model_tesis" -- bash -lc 'source ../.venv/bin/activate && python train_ablation.py --data dataset/data.yaml --tune-dalw --tune-epochs 60 2>&1 | tee ../logs/tune.log'

(Ganti "$PWD" dengan path absolut root proyek bila perlu. Jika zellij run gagal,
fallback: nohup ... > logs/tune.log 2>&1 & — laporkan PID — tapi coba zellij dulu
karena saya ingin memantau dari pane.)

Setelah meluncurkan:
1. Tunggu ±3 menit, baca ekor logs/tune.log; konfirmasi kombinasi pertama berjalan
   dan catat durasi epoch pertama.
2. Estimasikan total waktu 9 kombinasi × 60 epoch dari durasi itu.
3. Beri saya perintah cek progres siap-tempel: tail -n 30 logs/tune.log
Jangan menunggu selesai; akhiri giliran setelah tiga butir dilaporkan.
```

### Prompt 4 — Rangkum hasil grid search

```text
Cek logs/tune.log dan keberadaan model_tesis/dalw_best.json. Jika belum selesai:
laporkan progres (kombinasi ke-berapa, ETA) lalu berhenti.

Jika selesai:
1. Baca dalw_best.json — laporkan α* dan σ* terpilih.
2. Susun tabel 9 kombinasi (α × σ) + mAP@0.5:0.95 validasinya dari log/artefak run,
   simpan ke hasil/grid_search.md (bahan Tabel 3.4 + sensitivitas α BAB 4).
3. Sanity check: α* ∈ {0,5; 1,0; 2,0}, σ* ∈ {0,05; 0,10; 0,20}.
```

### Prompt 5 — Latih 8 varian → pane `train` di session `nfl`

```text
Luncurkan pelatihan delapan varian (Subbab 3.8, konfigurasi identik, seed 0) ke
session 'nfl' sebagai pane 'train':

zellij --session nfl run --name train --cwd "$PWD/model_tesis" -- bash -lc 'source ../.venv/bin/activate && python train_ablation.py --data dataset/data.yaml --variant all 2>&1 | tee ../logs/train_all.log'

Aturan WAJIB sepanjang fase ini (keputusan A-12, CLAUDE.md §10):
- OOM pada varian ber-P2 (V3/V5/V7/V8) → hentikan, ulangi dengan --batch 8 untuk
  KEDELAPAN varian yang terdampak; batch harus identik antar-varian, dilarang
  mencampur. Catat batch final di hasil/catatan_run.md.
- --batch -1 (AutoBatch) dilarang untuk run final.
- Terputus → --variant <Vx> --resume (checkpoint last.pt tertulis tiap epoch).

Setelah meluncurkan: verifikasi V1 mulai dari log, catat waktu/epoch, estimasikan
total 8 varian, akhiri giliran. Jangan menunggu.
```

### Prompt 6 — Pantau / lanjutkan pelatihan (pakai berulang kapan pun)

```text
Periksa status pelatihan ablasi:
1. Baca ekor logs/train_all.log + struktur model_tesis/runs_tesis/ — untuk V1–V8
   laporkan: status, epoch terakhir, best mAP@0.5:0.95 dari results.csv, early
   stopping terpicu atau tidak. Satu tabel.
2. Jika ada yang crash: tampilkan 20 baris error terakhir, lalu lanjutkan di pane baru:
   zellij --session nfl run --name resume --cwd "$PWD/model_tesis" -- bash -lc 'source ../.venv/bin/activate && python train_ablation.py --data dataset/data.yaml --variant <Vx> --resume 2>&1 | tee -a ../logs/train_all.log'
3. Jika semua selesai: pastikan 8 berkas runs_tesis/V*/weights/best.pt ada, lalu
   backup: tar -czf backup_runs_tesis_$(date +%Y%m%d).tar.gz model_tesis/runs_tesis/
```

### Prompt 7 — Evaluasi lengkap (Subbab 3.11) → pane `eval`

```text
Semua varian terlatih. Fase evaluasi:
1. cd model_tesis && python test_eval.py — semua uji harus lulus; gagal → berhenti +
   tampilkan output.
2. Jalankan evaluate_all.py PERSIS mengikuti blok "Tahap 3 — Evaluasi" di
   model_tesis/README.md (kutip perintah dari README, jangan mengarang flag).
   Luncurkan ke session 'nfl' pane 'eval' dengan log logs/eval.log memakai pola
   zellij --session nfl run yang sama.
3. Setelah selesai (pantau log), verifikasi keluaran: global_metrics.csv,
   strata_ap.csv, wilcoxon_ap5095.csv, folder nmsfree_out/.
4. Ringkas ke hasil/ringkasan_evaluasi.md dan laporkan: (a) metrik global per varian;
   (b) TIGA p-value hipotesis utama V8–V1, V4–V1, V8–V5 + hasil Holm sekunder;
   (c) strata mana yang paling terbantu DALW (small / heavy-occlusion / dense);
   (d) DR, CM, sensitivitas τ dari nmsfree_out/.
```

### Prompt 8 — Validasi proksi oklusi (setelah saya menganotasi manual)

```text
manual_oklusi.csv (format image,gt_index,tier) sudah kusiapkan di model_tesis/.
Jalankan sesuai README:

python -c "from y26_strata import occlusion_agreement; print(occlusion_agreement('manual_oklusi.csv','dataset/data.yaml',split='val'))"

Laporkan angka kesesuaian + jumlah citra subset, simpan ke hasil/validasi_oklusi.md
dengan satu kalimat interpretasi untuk BAB 4 (menunaikan janji Subbab 3.3.3).
```

### Prompt 9 — Counting end-to-end ByteTrack (RQ5) → pane `count`

```text
Video uji ada di video_uji/ dan ground truth manual per interval per kelas per arah
ada di gt_counting.csv.

1. Jalankan y26_counting.py PERSIS mengikuti bagian counting di model_tesis/README.md,
   bobot runs_tesis/V8/weights/best.pt, ke session 'nfl' pane 'count' dengan log
   logs/count.log (pola zellij --session nfl run yang sama).
2. Setelah selesai, baca summary.json: laporkan MAE, RMSE, MAPE + proporsi pengamatan
   y_t = 0 yang dikecualikan (aturan Subbab 3.11.3), dan FPS rata-rata.
3. Simpan ringkasan + konfigurasi garis virtual ke hasil/ringkasan_counting.md.
Ambang lulus RQ5 adalah keputusan naskah — cukup laporkan angkanya.
```

### Prompt 10 — Konsolidasi hasil → peta placeholder (BELUM menulis BAB 4)

```text
Buat SATU dokumen hasil/hasil_eksperimen.md memetakan setiap angka ke placeholder
naskah, mengikuti "Peta keluaran → placeholder" di model_tesis/README.md:
dalw_best.json → Tabel 3.4; global_metrics.csv → tabel metrik utama;
strata_ap.csv → stratifikasi (RQ4); wilcoxon_ap5095.csv → tiga p-value (RQ2);
nmsfree_out/ → DR/CM/sensitivitas τ (RQ3); summary.json → MAE/RMSE/MAPE/FPS (RQ5).
Sertakan daftar 18 placeholder numerik + nilai penggantinya yang sudah tersedia.

Tambahan — keputusan A-11 (CLAUDE.md §10): baca y26_dalw.py, tentukan faktual head
mana yang menerima bobot w_i (one-to-many / one-to-one / keduanya), kutip barisnya,
lalu draftkan SATU kalimat Bahasa Indonesia akademik untuk Subbab 3.6.3 (standar §11).

LARANGAN: jangan menulis BAB 4/5 dan jangan menyentuh .docx — sesi terpisah setelah
kureview dokumen ini.
```

---

## BAGIAN C — Contekan pemantauan (sisi Anda)

| Kebutuhan | Perintah / tombol |
|---|---|
| Menonton semua pekerjaan Claude | `zellij attach nfl` |
| Pindah antar-pane (tune/train/eval/count) | `Ctrl+p` lalu panah |
| Scroll riwayat pane | `Ctrl+s` (keluar: `Esc`) |
| Lepas tanpa menghentikan apa pun | `Ctrl+o` lalu `d` |
| Daftar session | `zellij list-sessions` |
| Cek progres dari mana saja (tanpa attach) | `tail -f logs/train_all.log` |
| Bereskan setelah semua tuntas | `zellij kill-session nfl` |

Pane hasil `zellij run` **tetap terbuka setelah proses selesai** dan menampilkan exit
code — jadi Anda bisa attach belakangan dan tetap melihat riwayatnya. Urutan eksekusi:
P1 → P2 → P3 → (tunggu) → P4 → P5 → (P6 berulang) → P7 → P8 → P9 → P10, lalu bawa
`hasil/hasil_eksperimen.md` ke sesi penulisan BAB 4–5.
