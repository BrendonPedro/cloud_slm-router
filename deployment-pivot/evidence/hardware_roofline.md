# Hardware-branch roofline (spec sheets + assumed eff = 0.7; NOT measured)

Memory need at 16k ctx (weights + bf16 KV + 1.5 GB): Qwen3-8B-AWQ 10.0 GB, Qwen3-8B 20.3 GB, Qwen3-14B-AWQ 14.2 GB, Qwen3-32B-AWQ 25.1 GB, Qwen3-32B 71.3 GB 

## 1. Fit (F = fits at 16k ctx) and batch-1 decode bound (tok/s) per machine

| machine | mem GB | BW GB/s | bf16 | role | Qwen3-8B-AWQ | Qwen3-8B | Qwen3-14B-AWQ | Qwen3-32B-AWQ | Qwen3-32B |
|---|---|---|---|---|---|---|---|---|---|
| RTX 3090 (manuscript edge, 1 of 2) | 24 | 936 | yes | edge | F 98 | F 39 | F 61 | — (32) | — (10) |
| RTX 4090 desktop | 24 | 1008 | yes | edge | F 105 | F 41 | F 66 | — (35) | — (11) |
| RTX 4090 Laptop | 16 | 576 | yes | edge | F 60 | — (24) | F 38 | — (20) | — (6) |
| RTX 4070 Laptop | 8 | 256 | yes | edge | — (27) | — (11) | — (17) | — (9) | — (3) |
| GB10 (ASUS Ascent GX10 / DGX Spark) | 128 | 273 | yes | edge or server | F 29 | F 11 | F 18 | F 9 | F 3 |
| Jetson AGX Orin 64GB | 64 | 204.8 | yes | edge | F 21 | F 8 | F 13 | F 7 | — (2) |
| Ryzen 5 8500G CPU (this WSL box) | 9 | 83 | NO | none | — (9) | — (3) | — (5) | — (3) | — (1) |
| A100 80GB SXM (DGX A100 / Station) | 80 | 2039 | yes | server | F 213 | F 84 | F 134 | F 70 | F 21 |
| H100 80GB SXM (DGX H100) | 80 | 3350 | yes | server | F 350 | F 138 | F 220 | F 115 | F 35 |
| V100 32GB (DGX-1 / DGX-2) | 32 | 900 | NO | server | F 94 | F 37 | F 59 | F 31 | — (9) |

Parenthesised = bound if it fitted (it does not on one device).

## 2. Server branches for REMOTE Qwen3-32B bf16 (the SPLIT reference)

| server branch | GPUs used | fits | 32B bf16 bound tok/s | 4k-token trace (s) | 16k-token trace (s) |
|---|---|---|---|---|---|
| A100 80GB SXM (DGX A100 / Station) | 1 | yes | 21.4 | 191 | 764 |
| A100 80GB SXM (DGX A100 / Station) | 2 | yes | 42.9 | 96 | 382 |
| H100 80GB SXM (DGX H100) | 1 | yes | 35.2 | 116 | 465 |
| H100 80GB SXM (DGX H100) | 2 | yes | 70.4 | 58 | 233 |
| GB10 (ASUS Ascent GX10 / DGX Spark) | 1 | yes | 2.9 | 1427 | 5708 |
| V100 32GB (DGX-1 / DGX-2) (no native bf16) | 4 | yes | 37.9 | 108 | 433 |

## 3. Assumed sim throughputs vs bound

| assumption (joint_vs_sequential_sim.py) | value | bound on plausible hardware | verdict |
|---|---|---|---|
| edge 8B fast | 40 tok/s | 3090 bf16 39, 3090 AWQ 98, 4090L AWQ 60, GB10 AWQ 29 | plausible on a discrete GPU |
| edge 8B slow | 15 tok/s | Orin AWQ 21, CPU 8500G AWQ 9 | plausible for board/CPU class |
| server 8B | 90 tok/s | A100 bf16 84, H100 bf16 138, GB10 bf16 11 | plausible only on A100/H100 |

## 4. SPLIT per-token bound, Qwen3-32B bf16, U-max(16) = 10 edge layers

| edge | server | RTT ms | SPLIT tok/s bound | REMOTE tok/s bound (same server) | SPLIT/REMOTE |
|---|---|---|---|---|---|
| RTX 3090 (manuscript edge, 1 of 2) | A100 80GB SXM (DGX A100 / Station) | 1 | 17.8 | 21.4 | 0.83 |
| RTX 3090 (manuscript edge, 1 of 2) | A100 80GB SXM (DGX A100 / Station) | 20 | 13.3 | 21.4 | 0.62 |
| RTX 3090 (manuscript edge, 1 of 2) | A100 80GB SXM (DGX A100 / Station) | 50 | 9.5 | 21.4 | 0.44 |
| RTX 3090 (manuscript edge, 1 of 2) | H100 80GB SXM (DGX H100) | 1 | 24.2 | 35.2 | 0.69 |
| RTX 3090 (manuscript edge, 1 of 2) | H100 80GB SXM (DGX H100) | 20 | 16.6 | 35.2 | 0.47 |
| RTX 3090 (manuscript edge, 1 of 2) | H100 80GB SXM (DGX H100) | 50 | 11.1 | 35.2 | 0.31 |
| RTX 4090 Laptop | A100 80GB SXM (DGX A100 / Station) | 1 | 14.9 | 21.4 | 0.70 |
| RTX 4090 Laptop | A100 80GB SXM (DGX A100 / Station) | 20 | 11.6 | 21.4 | 0.54 |
| RTX 4090 Laptop | A100 80GB SXM (DGX A100 / Station) | 50 | 8.6 | 21.4 | 0.40 |
| GB10 (ASUS Ascent GX10 / DGX Spark) | A100 80GB SXM (DGX A100 / Station) | 1 | 10.1 | 21.4 | 0.47 |
| GB10 (ASUS Ascent GX10 / DGX Spark) | A100 80GB SXM (DGX A100 / Station) | 20 | 8.5 | 21.4 | 0.40 |
| GB10 (ASUS Ascent GX10 / DGX Spark) | A100 80GB SXM (DGX A100 / Station) | 50 | 6.8 | 21.4 | 0.32 |
| RTX 3090 (manuscript edge, 1 of 2) | GB10 (ASUS Ascent GX10 / DGX Spark) | 1 | 3.3 | 2.9 | 1.17 |
| RTX 3090 (manuscript edge, 1 of 2) | GB10 (ASUS Ascent GX10 / DGX Spark) | 20 | 3.1 | 2.9 | 1.10 |
| RTX 3090 (manuscript edge, 1 of 2) | GB10 (ASUS Ascent GX10 / DGX Spark) | 50 | 2.9 | 2.9 | 1.00 |
