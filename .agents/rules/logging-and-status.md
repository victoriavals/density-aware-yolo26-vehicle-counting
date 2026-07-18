# Logging Proses & Update Status — Process Logging and Status Updates

> **EN — TL;DR:** Long jobs run as **background processes** writing `logs/<name>.log` with a per-line timestamp (an `awk` filter strips `\r`, ANSI, and bar glyphs, then stamps each line). Always pass an **absolute** `--project` (the `runs_dir` gotcha from P3). Monitor with `Get-Content logs\<name>.log -Wait -Tail 30 -Encoding UTF8`. A harness "stopped" notification is usually **normal completion**, not a crash (jobs survive closing VS Code). At session end: append a `CLAUDE.md` §15 entry **and** a `logs/sesi.log` line `[YYYY-MM-DD HH:MM] CATEGORY | text`.

Berkas sumber: `CLAUDE.md` §12.7–§12.8, §13, §15.

## 1. Job panjang = background + log ber-stempel waktu

Adaptasi Windows-native (tanpa WSL/Zellij): eksperimen panjang dijalankan sebagai **background process**, bukan foreground. Setiap job punya log keluaran sendiri `logs/<nama>.log` dengan **stempel waktu per baris** dan **per-batch**.

**Konvensi awk (bash)** — pecah `\r` per baris, buang ANSI + glyph bar (ASCII murni), stempel per baris:

```
<perintah> 2>&1 | awk 'BEGIN{RS="\r|\n"} { gsub(/\x1b\[[0-9;]*[a-zA-Z]/,""); gsub(/[\xe2][\x94-\x95][\x80-\xbf]/,""); if ($0 != "") print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush() }' > logs/<nama>.log
```

## 2. Gotcha: `--project` WAJIB absolut

Insiden P3: percobaan pertama grid search gagal karena path `--project` relatif salah tempat (`settings.json` Ultralytics). **Selalu** pakai `--project` **ABSOLUT** menunjuk `<repo>/runs_tesis`. Folder mentah (`runs_tesis/`, `eval_out/`, `nmsfree_out/`) jangan ditimpa.

## 3. Memantau job

Dari PowerShell:

```
Get-Content logs\<nama>.log -Wait -Tail 30 -Encoding UTF8
```

**Notifikasi harness "stopped" ≠ crash.** Terbukti berkali-kali (P3, P5): job OS tetap hidup lintas sesi (~41–45 jam), selamat dari penutupan VS Code; "stopped" biasanya penanda **selesai-normal** (varian terakhir tuntas). Verifikasi via isi log, bukan asumsi.

## 4. Akhir sesi — dua tempat wajib

1. **`CLAUDE.md` §15** — tambah entri bullet berisi hasil/keputusan/insiden baru (aturan §12.7).
2. **`logs/sesi.log`** — *append* baris per tindakan/keputusan/temuan/insiden signifikan (aturan §12.8):

```
[YYYY-MM-DD HH:MM] KATEGORI | isi ringkas
```

Proses harus terdokumentasi, bukan hanya hasil. Job panjang tetap punya log keluarannya sendiri.

## Tautan terkait

- [Playbook eksperimen](../playbooks/run-experiment.md) · [Playbook evaluasi](../playbooks/evaluate.md) · [Lingkungan](../knowledge/environment.md) · [Aturan kerja](working-rules.md) · skill `perbarui-status-log`.
