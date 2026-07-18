---
name: cek-invarian-metodologi
description: Periksa invarian metodologis terkodekan (seed 0, batch parity, tier strata 0,10/0,35 & 10/26, MAPE y>0, pejalan kaki dikecualikan, densitas pasca-augmentasi, unit Wilcoxon AP per kelas x strata tanpa global, 3 hipotesis utama + Holm) sebelum training, commit, atau menulis BAB 4. Pakai untuk mencegah pelanggaran metodologi.
---

# Cek Invarian Metodologi — Methodology Invariant Check

> **EN — TL;DR:** A checklist of coded invariants that must never be loosened, plus where each is enforced. Run before training, committing, or writing BAB 4.

## Checklist (dengan tempat penegakan)
- [ ] **Framing:** HAM/P2 = instrumen, DALW = kebaruan metode. (naskah + KB)
- [ ] **Seed 0 + konfigurasi identik** antar 8 varian; batch sama (OOM → turunkan SEMUA). (`train_ablation.py`)
- [ ] **Tier strata terkunci:** oklusi 0,10/0,35, densitas 10/26, ukuran COCO 32²/96². (`y26_strata.py`: `OCC_EDGES`, `DEN_EDGES`, `SIZE_EDGES`)
- [ ] **Unit Wilcoxon** = AP per (kelas × strata), **tanpa** baris global; 3 hipotesis utama (V8-V1, V4-V1, V8-V5) tanpa koreksi + sekunder Holm. (`y26_stats.py`: `PRIMARY_PAIRS`, `holm`)
- [ ] **MAPE hanya y>0**; proporsi eksklusi dilaporkan. (`y26_counting.py`)
- [ ] **Pejalan kaki dikecualikan** dari counting. (`y26_counting.py`)
- [ ] **Densitas dihitung ulang pasca-augmentasi** (bobot dari label batch di dalam loss, `torch.no_grad`). (`y26_dalw.py`)
- [ ] **DALW pada KEDUA head** via E2ELoss (A-11). (`y26_dalw.py`)
- [ ] **Group split sebelum training**; bukti `bukti_split_*.csv` utuh. (`make_group_split.py`)
- [ ] **ultralytics 8.4.92 terkunci** (T4 penjaga). (`test_smoke.py`)

## Hint grep
```bash
grep -n "OCC_EDGES\|DEN_EDGES\|SIZE_EDGES" y26_strata.py
grep -n "PRIMARY_PAIRS" y26_stats.py
grep -n "no_grad\|centers" y26_dalw.py
```

## Rujukan
`.agents/rules/methodology-invariants.md`, `.agents/knowledge/statistics.md` (relatif ke root repo).
