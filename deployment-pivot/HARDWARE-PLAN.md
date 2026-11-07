# Hardware plan for E0 and the F3 evaluation (2026-11-07)

This plan covers the hardware for E0 (`E0-SPLIT-VIABILITY.md`) and for the trace-driven
F3/baseline evaluation (`BASELINES.md` §7). **No hardware beyond this WSL box was
accessed.** The "Asus" edge machine and the "DGX" server are **not documented anywhere
in the repo**. This plan therefore:
- states requirements;
- gives a 30-minute inventory (§3) that pins down what each machine actually is;
- pre-declares what to do for each answer (§2), so that the answer cannot be used to
  re-scope the experiment after the fact.

**Bottom line.**
- **Minimum hardware:**
  - one NVIDIA edge GPU (Ampere or later, bf16) with **≥ 24 GB**; the 12/16 GB classes
    are emulated by capping memory;
  - one server with **≥ 80 GB** GPU memory per model replica (A100/H100 class), plus a
    second GPU for the in-host pipeline floor;
  - a wired LAN between them where the edge has root for `tc netem`.
- **The identity of "DGX" is the single biggest hardware risk.**
  - If it is an A100/H100 DGX, E0 runs as designed.
  - If it is a **DGX Spark / GB10** (the same chip as an ASUS Ascent GX10), it has
    273 GB/s of unified memory. REMOTE Qwen3-32B bf16 is then bounded at about
    **3 tok/s**, so a 4k-token thinking trace takes about 24 min. That machine is not a
    server: E0 and every REMOTE profile would measure a server slower than the edge.
  - If it is a **V100 DGX-1/2**, it has no native bf16, and E0 forbids an fp16 cast.
- **SPLIT is slower than REMOTE in every realistic pair, even at the roofline.** With
  zero serialisation cost, a U-max(16) split of 32B runs at **0.31–0.83×** REMOTE's
  per-token bound on the same server (§2.3). This holds before Mix-or-Split's measured
  serialisation overhead is added. It matches LIT-REVIEW §4 and E0's "privacy tier, not
  latency" framing.
- **Only 3 of the E0/F3 measurement blocks need both machines at once:** Q1/Q2 for SPLIT,
  the E0-L latency matrix, and the 50-query live replay validation. Everything else
  runs on one machine, unattended (§4).
- **Total budget:**
  - about 10–14 server GPU-hours;
  - about 6 edge GPU-hours;
  - about 6 hours with both endpoints reserved at once.
  - Nothing is rented (§5).

---

## 1. What is known

| Machine | Status | Source | Usable for |
|---|---|---|---|
| This WSL box: Ryzen 5 8500G, 9 GB RAM visible to WSL, no CUDA (`nvidia-smi` absent) | **verified 2026-11-07** | `free -g`, `nproc` = 4 | evidence scripts, replay/scoring, table fitting. **Not** any E0 role |
| Manuscript edge: Xeon W-2123, 64 GB, 2× RTX 3090 (24 GB each) | stated in the manuscript (L202), **not verified** to still exist or be accessible | `research/problem-as-written.md` L163; `research/claim-audit.md` E1 | ideal E0 edge (1 GPU capped to 12/16/24 GB). The second GPU must stay idle during E0-L |
| Manuscript cloud server | **unstated** in the manuscript ("a dedicated server, which is equipped with ..." is cut off) | claim-audit E1 | unknown |
| "Asus / edge machine" | **undocumented** | task brief only | branch table §2.1 |
| "DGX / server-class" | **undocumented**. `ssh dgx` has no config entry on this box | task brief only | branch table §2.2 |

The repo's earlier notes put a Jetson-class board or laptop GPU forward as the edge
(`decision/GO-PIVOT-REPORT.md` §4.4). E0's desk check overrides that for E0: SPLIT has a
quality regime only at 12–24 GB, and that range must be **emulated on one ≥ 24 GB GPU**
so that all three classes are measured on the same silicon. A real small device can
be added later as a single validation point. It is not a precondition.

## 2. Hardware branches, decided in advance

Numbers are from `evidence/hardware_roofline.{py,md}`. They are spec-sheet memory
bandwidth × an **assumed** 0.7 batch-1 efficiency, with a 16k-token bf16 KV cache for
the memory check. **They are upper bounds, not measurements.**

### 2.1 Edge ("Asus", or the 2×3090 workstation)

| If the edge turns out to be | 8B-AWQ / 14B-AWQ / 32B-AWQ fit at 16k? | 8B-AWQ decode bound | Role in E0 | Action |
|---|---|---|---|---|
| **RTX 3090 / 4090 desktop, 24 GB** | yes / yes / **no** (32B-AWQ needs 25.1 GB; fits with FP8 KV) | ≈ 100 tok/s | **primary E0 edge**: cap to 12/16/24 GB | use as designed |
| RTX 4090 **Laptop**, 16 GB | yes / yes / no | ≈ 60 tok/s | a *real* 16 GB class point; the 24 GB class cannot be run | use as the edge for classes 12/16 only; borrow a 24 GB card for the 24 GB class, or drop that class and say so |
| ≤ 8 GB laptop GPU | no / no / no at 16k | — | no E0 role (cannot hold U-max(12) plus KV for 16k context) | do not use; edge = 2×3090 workstation |
| **GB10 (ASUS Ascent GX10)**, 128 GB unified, 273 GB/s | all fit, **32B bf16 fits too** | ≈ 29 tok/s | **not a memory-starved edge**. Capping memory does not cap bandwidth, but any cap is a declared emulation | usable as a capped edge **only if** no ≥ 24 GB discrete GPU is available; flag that 32B runs EDGE-resident at about 3 tok/s in bf16 and about 9 tok/s in AWQ, so SPLIT's competitor set grows |
| Jetson AGX Orin 64 GB | all fit | ≈ 21 tok/s | as GB10, and no `tc`-friendly root may be available | validation point only |

Selection rule (fixed now): **the edge is the first available machine down this list:**
1. 2×3090 workstation (use 1 GPU);
2. a 24 GB desktop GPU;
3. a 16 GB laptop GPU, with the 24 GB class dropped;
4. GB10, flagged as an emulation.

### 2.2 Server ("DGX")

| If the DGX turns out to be | 32B bf16 fits? | REMOTE 32B bf16 bound | 4k-token trace | Action |
|---|---|---|---|---|
| DGX A100 / DGX Station A100 (80 GB A100s) | yes, on 1 GPU | 21 tok/s (1 GPU), 43 (TP=2) | 191 s / 96 s | **use as designed**. TP=1 is the REMOTE reference. GPU 2 provides the Q1(c) in-host pipeline; GPUs 3+ run the κ load generator |
| DGX H100 / H200 | yes | 35 (1 GPU), 70 (TP=2) | 116 s / 58 s | use as designed |
| DGX A100 **40 GB** | no on 1 GPU; TP=2 | ≈ 43 (TP=2) | 96 s | REMOTE reference = TP=2. Q1(c) uses a 4-GPU pipeline. Record that SPLIT's server segment is TP=2 too |
| **DGX Spark / GB10** | yes (unified 128 GB) | **≈ 3 tok/s** | **≈ 24 min** | **not a server.** Do **not** run E0 against it. Options in order: (1) obtain lab A100/H100 time; (2) treat the GB10 as an *edge* (row in §2.1) and find a server; (3) if neither exists, E0 cannot run, and GO-NOGO falls to its no-hardware branch |
| DGX-1 / DGX-2 (V100) | 32 GB/GPU, so TP ≥ 4 | ≈ 38 (TP=4) | ≈ 108 s | **no native bf16**, and E0 §7 forbids an fp16 cast (overflow risk in Qwen3 hidden states). Usable only for Q3 accuracy in fp32/emulated bf16; not usable for E0-L latency. Treat as "no server" for E0-L |
| shared cluster under SLURM (any GPU) | — | — | — | E0-L needs an **exclusive** node reservation for about 6 h. Without it, κ = 1 cannot be guaranteed and the contention block is uncontrolled. Q3 and server profiling can run as normal batch jobs |

### 2.3 What the roofline already says about SPLIT (no hardware needed)

Per-token SPLIT bound for Qwen3-32B bf16 at U-max(16) (10 of 64 layers on the edge, plus
the LM head), with zero serialisation:

| Edge | Server | RTT 1 ms | RTT 20 ms | RTT 50 ms | REMOTE bound |
|---|---|---|---|---|---|
| RTX 3090 | A100 | 17.8 tok/s (0.83×) | 13.3 (0.62×) | 9.5 (0.44×) | 21.4 |
| RTX 3090 | H100 | 24.2 (0.69×) | 16.6 (0.47×) | 11.1 (0.31×) | 35.2 |
| RTX 4090 Laptop | A100 | 14.9 (0.70×) | 11.6 (0.54×) | 8.6 (0.40×) | 21.4 |
| GB10 | A100 | 10.1 (0.47×) | 8.5 (0.40×) | 6.8 (0.32×) | 21.4 |

Consequences:
1. On an uncontended server, SPLIT is **never** faster than REMOTE, even before
   serialisation, which Mix-or-Split found dominant. E0-R's `open`-class cells are
   therefore expected to fail, and E0 already pre-registers that.
2. The faster the server, the worse SPLIT looks relative to REMOTE. The edge share is a
   fixed cost per token: 10 slow layers plus the LM head plus one RTT.
3. **Server contention is the only state in which SPLIT's ratio rises.** SPLIT's server
   segment sees κ just as REMOTE does, but only on 54 of 64 layers. This is the
   mechanism E0-L's contention block must measure: the realised κ for each path
   separately (E0 §6).
4. The sim's assumed throughputs (edge 8B at 15/40 tok/s, server 8B at 90 tok/s) lie
   inside the bounds for a 3090/laptop edge and an A100 server. **The pre-hardware
   numbers in PROBLEM-FORMULATION and BASELINES remain valid only on that hardware
   branch.** On a GB10 "server" they are off by 8× and must be re-run before any
   conclusion is drawn.

## 3. Day-0 inventory (≈ 30 min, before anything else)

Run on each machine and save the output to `e0/env/<host>.txt`. Each line answers one
branch question in §2.

```bash
# identity and accelerator
hostnamectl; uname -a; cat /etc/os-release | head -3
nvidia-smi --query-gpu=index,name,memory.total,power.limit,clocks.max.sm --format=csv
nvidia-smi topo -m                          # NVLink vs PCIe between server GPUs
nvidia-smi -q | grep -iE "persistence|compute mode|MIG"   # MIG slices change everything
free -g; nproc
# software
python -c "import torch,sys;print(torch.__version__,torch.version.cuda,torch.cuda.is_bf16_supported())"
pip show vllm transformers 2>/dev/null | grep -E "Name|Version"
# scheduling / exclusivity
which sbatch squeue 2>/dev/null && squeue -u $USER
# privileges needed by E0
sudo -n true && echo "sudo OK" ; tc -V; modprobe -n ifb && echo "ifb OK"
sudo -n nvidia-smi -lgc 1395,1395 && sudo nvidia-smi -rgc   # clock locking allowed? (edge; resets after)
```

Between the two machines (from the edge):
```bash
ping -c 100 <server> | tail -1               # base RTT; must be < 1 ms p50 for E0's "native"
iperf3 -c <server> -t 20 ; iperf3 -c <server> -t 20 -R   # ≥ 1 Gbps both directions
nc -vz <server> 29500                        # an open TCP port for the split socket
```

**Go/no-go for E0 hardware (fixed now).** All six must hold:
1. The edge has an NVIDIA GPU with ≥ 24 GB, or 16 GB with the 24 GB class dropped
   (`is_bf16_supported` = True).
2. The server has an A100/H100-class GPU with ≥ 80 GB for one replica, or 2 × 40 GB, and
   at least one more GPU for Q1(c) and load generation.
3. RTT p50 < 1 ms and ≥ 1 Gbps between them. If they are on different networks, an SSH
   tunnel is allowed, but its overhead is measured as part of "native".
4. Root (or `CAP_NET_ADMIN`) on the edge for `tc netem` + `ifb`.
5. An exclusive 6 h window on both machines for E0-L.
6. torch/transformers versions can be pinned to the same values on both hosts.

If 1–2 fail, record that E0 is blocked and why. GO-NOGO uses its no-hardware branch.
If only 3–5 fail, Q3 and the single-host profiling still run (§4.1), because they
carry most of the information (E0 §8 early stop).

## 4. What is measured where

### 4.1 Single-machine blocks (independent, can run unattended and in parallel)

| Block | Machine | What | Settings | Budget | Feeds |
|---|---|---|---|---|---|
| **S1 Q3 accuracy** | server | per-query (score, completion tokens) for Qwen3-32B bf16 and each EDGE competitor (8B-AWQ, 14B-AWQ, 32B-AWQ; 8B bf16) on the 200-query E0 sample | vLLM batched; thinking mode; T = 0.6, top-p 0.95, top-k 20; 2 seeds; max 16,384 tokens | ≈ 5 models × ≈ 1 h ≈ **5–6 GPU-h** | E0-R, E0 early stop, F3's `Q`, `N` for new models |
| **S2 Q1 reference + in-host floor** | server | teacher-forced logits of 32B single-host (b) and 2-GPU pipeline cut (c); Qwen3-8B single-host server logits (hardware floor, half) | HF, greedy reference continuations ≤ 4,096 tokens, TF32 off | ≈ **2 GPU-h** | Q1 thresholds |
| **S3 Q1 hardware floor, edge half** | edge | Qwen3-8B single-host teacher-forced logits on the same continuations | as S2 | ≈ **1 GPU-h** | Q1 thresholds (compared offline with S2) |
| **S4 REMOTE profile vs load** | server (client on the server) | TTFT, TPOT p50/p95 for each REMOTE model at load-generator concurrency {0, 8, 32}; server power (NVML/DCGM) | 10 fixed-length prompts (n_in ≈ 256 / 2,048) × 256 tokens, 3 reps, 2 warm-ups | ≈ **1 GPU-h** | κ(load), τdec_c, τpre_c |
| **S5 EDGE profile per memory class** | edge | TTFT, TPOT, peak memory, GPU power (NVML, 100 ms) for each EDGE competitor at caps 12/16/24 GB; idle and "waiting on network" power | same fixed-length workload; clocks locked | ≈ **2 GPU-h** | τdec_e, P_active, P_wait, mem(m, EDGE) |
| **S6 F feasibility, edge half** | edge | U-max(12/16/24) edge slices load and run a synthetic 16k-token prefill within the cap; peak memory | HF slices with dummy server stub | ≈ **0.5 h** | F (before any joint time is booked) |

S1 runs first because of the early-stop rule: if the 32B-bf16 vs EDGE-best(16) gap is
< 3 pt on every task, E0-L shrinks to the 6 core cells.

### 4.2 Joint blocks (both endpoints reserved at once)

| Block | What | Cells × reps | Budget |
|---|---|---|---|
| **J1 Q1 split + Q2** | SPLIT U-min and U-max(16) teacher-forced logits (200 queries); 30 × 1,024-token greedy free-runs | 2 configs + 30 runs | ≈ **2 h** |
| **J2 E0-L** | 22 cells (core 6, RTT 6, cut-invariance 1, bandwidth 1, contention 4, held-out 4) | 22 × 3 reps + 2 warm-ups, randomised order within each block | ≈ **3–4 h** |
| **J3 replay validation** (after E0, only if F3/baselines go ahead) | F3, B*'s winning policy and B-fixed live end-to-end | 50 queries × 2 states | ≈ **2–3 h** (long thinking traces dominate) |

Link control for J2 and J3, on the **edge** only:
```bash
sudo tc qdisc add dev $IF root netem delay ${RTT_HALF}ms rate ${BW}mbit
sudo ip link add ifb0 type ifb && sudo ip link set ifb0 up
sudo tc qdisc add dev $IF handle ffff: ingress
sudo tc filter add dev $IF parent ffff: matchall action mirred egress redirect dev ifb0
sudo tc qdisc add dev ifb0 root netem delay ${RTT_HALF}ms rate ${BW}mbit
tc -s qdisc show dev $IF; tc -s qdisc show dev ifb0      # log before/after every cell
```
The REMOTE cells of J2 are run **from the edge as the client**, so REMOTE and SPLIT see
the same shaped link.

### 4.3 Energy

- **Edge:** NVML board power at 100 ms; J/token = ∫P dt / tokens. Report P_wait (the GPU
  idle while REMOTE/SPLIT waits on the server) separately. It is the term that made REMOTE
  the device-energy winner in the sim (PROBLEM-FORMULATION §1.1).
  - On a laptop, also log battery discharge (`upower`/`/sys/class/power_supply`) to cover
    CPU/DRAM draw that NVML misses.
  - On a GB10/Jetson, use `tegrastats` or the platform power sensor and record which.
- **Server:** NVML/DCGM power per GPU. **Reported, not optimised** (BASELINES §7).
- **Not measured:** wall power with an external meter. Add one only if a reviewer
  demands system-level energy; it does not change any frozen decision.

## 5. What is deliberately not needed

- **No rented GPUs** (brief). If the server branch fails (§2.2), E0 is blocked; it is not
  moved to the cloud.
- **No real 12/16 GB device for E0.** Emulation on one 24 GB GPU is conservative for
  SPLIT (E0 §5) and keeps all classes on the same silicon. A real 16 GB laptop is a
  welcome *extra* validation point for the 16 GB class (§2.1). It is not a gate.
- **No multi-edge fleet, no Wi-Fi/LTE field runs.** `netem` covers the RTT/BW range
  where any decision could flip. The sim (PROBLEM-FORMULATION §1.1) and §2.3 both say RTT
  does not flip EDGE/REMOTE, and only matters for SPLIT. A field run would add
  realism, not decision information.
- **No large-model REMOTE beyond Qwen3-32B for E0.** The cached LLMRouterBench data
  supply the 235B/DeepSeek-class quality rows for F3. Their latency profile, if
  needed, is the server's measured TPOT for the largest model it can host, recorded
  as such. It is not extrapolated.
- **This WSL box runs nothing on a GPU.** It holds the evidence scripts, the replay
  scorer and the bootstrap only (pure Python; numpy is not installed system-wide).

## 6. Expected matrix and calendar (feeds WEEK-EXECUTION-PLAN)

| Order | Block | Machines | Wall-clock | Blocks on |
|---|---|---|---|---|
| 0 | §3 inventory + go/no-go | both | 0.5 h | — |
| 1 | S1 Q3 accuracy (start first; unattended) | server | 5–6 h | inventory |
| 1 | S5 EDGE profiles, S6 F edge half, S3 edge floor | edge | 3.5 h | inventory |
| 2 | Early-stop decision from S1 | — | minutes | S1 |
| 2 | S2 Q1 reference + pipeline floor, S4 REMOTE profiles | server | 3 h | S1 done (frees GPUs) |
| 3 | Split runtime coding (two-process HF + socket) | WSL/edge | ≈ 1 day | early-stop decision leaves SPLIT alive (GO-NOGO §10 step 8; WEEK-EXECUTION-PLAN G1) |
| 4 | J1 Q1/Q2 | both | 2 h | runtime, S2 |
| 5 | J2 E0-L (full or the 6 core cells only) | both, exclusive | 1.5–4 h | J1 passes Q |
| 6 | R computation (replay with measured profiles) | WSL | 1 h | S1, S4, S5, J2 |
| 7 | J3 live replay validation | both | 2–3 h | E0 decision + baseline code |

- **Critical path:** inventory → S1 → early-stop decision. That is the cheapest
  information (≈ 6 server GPU-h, no runtime code). It can already end the SPLIT branch.
- **Joint time is booked only after S6 and S1:**
  - S6 shows whether F can pass at all;
  - S1 shows whether R can pass at all.
