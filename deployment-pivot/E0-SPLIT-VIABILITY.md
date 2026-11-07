# E0: Split viability (frozen design, 2026-11-07)

E0 is the first hardware experiment. It decides whether SPLIT enters the action set
`A` of the selected formulation F3 (`PROBLEM-FORMULATION.md` §3). **Nothing in this
document has been run.** The local machine (Ryzen 5 8500G under WSL, 9 GB RAM, no CUDA
GPU) cannot run it. Its hardware needs are stated in §5 and in `HARDWARE-PLAN.md`.

**Bottom line.**
- **Candidate:** Qwen3-32B in bf16, split U-shaped. Embedding, the first k layers, the
  last j layers and the LM head run on the edge; the middle runs on the server.
  Activations cross as raw bf16, about 10 KB per token in each direction.
- **Main competitor:** not REMOTE but **the best model that fits fully on the edge
  after weight quantisation**. According to vendor numbers, Qwen3-32B-AWQ-int4 loses at
  most 2.0 pt against bf16.
  - So SPLIT can add quality only on edges that **cannot** hold 32B-AWQ, i.e. about
    12–24 GB of accelerator memory.
  - It is useful only for traffic that may **not** go to REMOTE.
- **Pre-registered expectation** (revised 2026-11-07, before any hardware access, after the upper bound
  in `evidence/e0_r_prior.md`):
  - **thinking mode: likely fail at every class for D ≤ 600 s.** Even the SPLIT-favouring upper bound
    clears +3.0 pt in only 6/40 rows, all at D = 600 s, and in 0/10 rows at realistic runtime
    efficiency. A thinking-mode quality tier exists only at D ≥ 1200 s (asynchronous traffic);
  - **non-thinking mode: the one plausible pass**, at 12 GB and D = 30–60 s. This is not bounded by
    cached data;
  - fail at ≥ 32 GB;
  - fail for the `open` class at any memory size.
- **Pass** requires all three of **Q** (output equivalence), **F** (feasibility) and
  **R** (a regime ≥ 3.0 pt over the best admissible non-SPLIT action) (§8).
- **Failure of any one removes SPLIT from F3.** It must not be kept because the original
  paper proposed it.

---

## 1. Desk check that shaped E0 (done, no hardware)

`evidence/split_vs_quant_desk_check.{py,md}` uses:
- checkpoint sizes and configs from the Hugging Face API;
- **vendor-reported** thinking-mode scores for bf16 vs AWQ-int4, from the Qwen3-{8B,14B,32B}-AWQ
  model cards (fetched 2026-11-07).

The memory model is the checkpoint plus a bf16 KV cache for 16k tokens plus 1.5 GB of overhead.

| Edge memory | Best fully edge-resident | 32B-bf16 gain (LiveBench / GPQA / MMLU-Redux / AIME24) | Mean | 32B layers the edge can hold in a U-split |
|---|---|---|---|---|
| 8 GB | none fits at 16k ctx | — | — | 3/64 |
| 12 GB | Qwen3-8B-AWQ | +9.4 / +9.4 / +4.5 / +10.1 | +8.4 | 7/64 |
| 16 GB | Qwen3-14B-AWQ | +4.9 / +6.3 / +2.4 / +4.4 | +4.5 | 10/64 |
| 24 GB | Qwen3-14B-AWQ (32B-AWQ needs 25.1 GB; fits with an FP8 KV cache) | +4.9 / +6.3 / +2.4 / +4.4 (≤ +2.0 if 32B-AWQ fits) | +4.5 / +0.8 | 18/64 |
| ≥ 32 GB | Qwen3-32B-AWQ | +1.8 / −0.6 / +0.1 / +2.0 | +0.8 | 26–41/64 |

Consequences, which are folded into the design below:

1. **Weight quantisation is the strongest competitor to SPLIT.** On a 2×RTX 3090
   (48 GB) edge, which is the workstation the manuscript names at L202, SPLIT has no
   quality regime: the gain over 32B-AWQ is within vendor noise. A split paper on that
   edge would be refuted by the `EDGE: 32B-AWQ` baseline.
   - **The edge class must therefore be ≤ 24 GB of accelerator memory.**
   - **The quantised edge baseline is mandatory** (BASELINES.md).
2. **Qwen3-14B is not a useful split candidate.** Its AWQ version fits on a 16 GB edge,
   and a lossless bf16 split of 14B would gain at most +2.3 over 14B-AWQ on the vendor
   benchmarks (+1.3 / +1.9 / +0.1 / +2.3).
3. In the regime that matters, the edge holds only **3–18 of 64 layers**. SPLIT is
   then "REMOTE plus one RTT per token, with raw text kept on the device". It is a
   **privacy/admissibility** action, not a latency action, which matches the literature
   (LIT-REVIEW §4).
4. **Mix-or-Split-style prefill/decode splitting is out of scope for E0.** Decoding at
   the edge needs the full weights there. Wherever the weights fit, an edge-resident
   model already exists. Mix-or-Split remains a baseline family in BASELINES.md.

Vendor numbers come from one harness and are not our measurements. They place the
regime; E0-Q3 (§4.3) measures the actual gap.

## 2. Questions E0 answers

| ID | Question | Decides |
|---|---|---|
| **Q** | Does the split path compute the same function as the unsplit model, to within the numerical noise between pieces of hardware? | whether SPLIT's quality can be taken as Qwen3-32B-bf16's quality |
| **F** | Does a U-shaped split of Qwen3-32B run reliably within an edge memory cap of 12/16/24 GB at 16k context? | technical feasibility |
| **R** | Is there a pre-declared (memory class, privacy class, live state, deadline) cell where SPLIT beats the best *admissible* non-SPLIT action by ≥ 3.0 pt of on-time utility? | whether SPLIT has any useful regime |

## 3. Configurations

### 3.1 Models

| Role | Model | Where | Notes |
|---|---|---|---|
| Split candidate | **Qwen3-32B** (bf16; 64 layers; hidden 5120; 8 KV heads × 128) | edge + server | the only split model |
| REMOTE reference | Qwen3-32B bf16 | server | same weights as SPLIT |
| EDGE competitors | Qwen3-8B-AWQ, Qwen3-14B-AWQ, Qwen3-32B-AWQ (+FP8 KV at 24 GB), Qwen3-8B bf16 where it fits | edge | best per memory class is chosen *after* measurement |
| Noise-floor pair | Qwen3-8B bf16 | edge **and** server | fits on both, so it measures the edge-vs-server numerical floor |

**Mode variants (amendment 2026-11-07, before any hardware access; `evidence/e0_r_prior.md`).**
Every model above enters Q3 and R in **both** thinking and non-thinking mode. Each
(model, mode) pair is a separate action. Reason: the desk-check upper bound shows that
thinking-mode SPLIT almost never clears R at D ≤ 600 s, because thinking traces are thousands
of tokens long. Non-thinking 32B, however, is +12.1 pt (vendor mean) over non-thinking
8B-AWQ and produces short outputs. So the one plausible short-deadline SPLIT regime
(12 GB class, D = 30–60 s) involves non-thinking mode. Leaving mode out would make E0
fail SPLIT for a reason the paper did not test. Adding it also gives the edge more
competitors, so the amendment is not one-sided.

Qwen3-30B-A3B is a strong edge candidate too: an MoE with 3B active parameters and vendor
GPQA of 65.8 (thinking mode). It is **not** in E0 to keep the matrix small. If E0-R
passes at a memory class where a 4-bit 30B-A3B would fit (about 16–17 GB of weights, to be checked), it
must be added as an EDGE competitor before R is declared, and the cell re-evaluated.
This pre-empts the obvious reviewer objection.

### 3.2 Legal split points

U-shaped split (edge → server → edge each step):
- **edge:** embedding, layers `[0, k)`, layers `[64−j, 64)`, final norm, LM head;
- **server:** layers `[k, 64−j)`.

A configuration is legal iff:
- `k ≥ 1` and `j ≥ 1`, so raw text and output tokens never leave the device;
- edge peak memory ≤ the class cap.

Frozen configurations:

| Config | (k, j) | Purpose |
|---|---|---|
| `U-min` | (1, 1) | minimum edge compute share (closest to REMOTE + RTT) |
| `U-max(M)` | the largest symmetric (k, j) fitting cap M ∈ {12, 16, 24} GB; desk estimate (3,3), (5,5), (9,9) | maximum edge share per class |

The split depth is **not** swept further. Per-token network time does not depend on the
cut (In-Browser Split, LIT-REVIEW). One check cell (§6) verifies this on our runtime.
If the check fails, a third depth is added.

### 3.3 Runtime

- A minimal two-process PyTorch runtime: Hugging Face `transformers` layer slices on
  each side, with a KV cache for its own layers on each side.
- Transport: a TCP socket carrying raw bf16 bytes from pinned memory.
- No batching, lookahead, speculation or activation compression. The cut tensor is
  `[n_tokens, 5120]` bf16, so 10 KB per decoded token per direction and `n_in × 10 KB`
  at prefill.
- **One optimisation pass is allowed before R is judged:** pinned buffers and
  non-blocking copies. Mix-or-Split found that serialisation, not bandwidth, dominates
  its transfer cost.
- The **component floor** `τ_e + τ_c + ρ` (zero serialisation) is reported beside the
  measured value, to show what an optimised runtime could reach.
- **R is judged on the measured value**, not on the floor.

REMOTE and EDGE use their natural engines: vLLM on the server, vLLM or llama.cpp on the
edge, recorded. Q is judged in HF on both sides, so that Q isolates the split
effect from differences between engines.

## 4. Quality equivalence (Q)

### 4.1 Q1: teacher-forced agreement (cheap; prefill only)

1. Take the 200-query sample (§4.4).
2. Generate REMOTE greedy reference continuations, capped at 4,096 new tokens.
3. Run **one teacher-forced forward pass** over prompt + continuation on each of:
   - (a) **SPLIT** (U-min and U-max(16), real edge and server hosts);
   - (b) **single-host** Qwen3-32B in HF on the server (the reference);
   - (c) the server with a **2-GPU in-host pipeline cut at the same layer**. This is a
     split with no network or hardware heterogeneity, so it is the implementation floor.
4. Also run the noise-floor pair: **Qwen3-8B** single-host on the edge vs on the server.
   This is the hardware floor.

Metrics, per position, against (b):
- top-1 disagreement rate `D`;
- mean KL(b‖x).

### 4.2 Q2: free-running greedy smoke test (catches KV-cache and position bugs)

- Run 30 prompts × 1,024 new tokens, greedy, SPLIT vs single-host HF.
- At the **first divergence** of each sequence, record the reference's top-1 vs top-2
  log-probability margin.
- A divergence caused by numerical noise occurs only at near-ties. A bug causes
  divergences at confident positions, or degenerate output afterwards.

### 4.3 Q3: the quality gap that R needs (independent of SPLIT)

On the 200-query sample, measure task accuracy for:
- Qwen3-32B bf16 (REMOTE, vLLM, batched; this is SPLIT's quality once Q passes);
- each EDGE competitor (§3.1).

All are run on the **server**. Accuracy does not depend on the hardware, and batching
makes it about an hour per model.

Settings:
- thinking mode;
- the vendor-recommended sampling (T = 0.6, top-p 0.95, top-k 20);
- 2 seeds, `max_new_tokens` = 16,384, with the truncation rate reported.
- **Non-thinking runs as well** (§3.1 amendment): `enable_thinking=False`, with the vendor
  non-thinking sampling (T = 0.7, top-p 0.8, top-k 20) and 2 seeds, for Qwen3-32B bf16 and
  each EDGE competitor. Outputs are short, so this adds well under 1 GPU-h.

Greedy decoding is not used here, because Qwen3 advises against it in thinking mode
(repetition). Store per-query `(score, completion_tokens)`. F3's utility needs the
correlation between length and correctness (PROBLEM-FORMULATION §3.4).

### 4.4 Query sample

| Benchmark | n | Why |
|---|---|---|
| MMLU-Pro (test_1000 subset) | 60 | short-output knowledge task; smallest vendor gap |
| GPQA-Diamond | 60 | largest vendor gap (+6.3 over 14B-AWQ) |
| LiveMathBench | 40 | long reasoning traces |
| LiveCodeBench | 40 | long outputs; sub-task structure (E2) |

- The sample is stratified and drawn with a fixed seed (`seed=20261107`) from benchmarks
  the router already recognises (E3).
- This ties `t̂` to the table rows.
- 200 queries detect a mean accuracy gap of 3 pt only loosely (paired SE ≈ 2 pt). That
  is acceptable because **Q3 locates the regime, and R is tested per cell with a paired
  bootstrap**. If R's CI straddles 0 only through sample size, the sample is extended
  once to 400, using the same seed procedure. This is pre-declared, not a retry.

## 5. Hardware and link

| Endpoint | Requirement | Candidates (verify in HARDWARE-PLAN) |
|---|---|---|
| Edge | 1 NVIDIA GPU with ≥ 24 GB (Ampere or later, bf16); memory classes 12/16 GB **emulated** by capping (`torch.cuda.set_per_process_memory_fraction`, vLLM `gpu_memory_utilization`) | one RTX 3090 of the 2×3090 workstation (manuscript L202); the Asus machine if it has a suitable NVIDIA GPU (undocumented) |
| Server | ≥ 80 GB GPU memory for 32B bf16 + KV (1×A100/H100-80GB or 2 GPUs); a second GPU for the Q1(c) in-host pipeline | DGX, only if it is A100/H100-class: a DGX Spark/GB10 (≈ 3 tok/s for 32B bf16) or a V100 DGX (no bf16) does not qualify (HARDWARE-PLAN §2.2) |
| Link | wired LAN between the two; base RTT < 1 ms; `tc netem` on the edge egress plus an `ifb` ingress for RTT/BW control | — |

**Emulation bias.** A capped RTX 3090 is faster and has more bandwidth than a real
12–16 GB device. It favours EDGE and the edge segment of SPLIT alike. SPLIT's edge share
is only 3–18 layers, so the bias favours EDGE more. This is acceptable because it makes
any SPLIT pass conservative, and it is reported.

## 6. Latency, transfer volume and energy (E0-L)

**Fixed latency workload.** 10 prompts: 5 with n_in ≈ 256 and 5 with n_in ≈ 2,048. Each
generates exactly 256 tokens (`min_tokens = max_tokens`), so latency does not depend on
content. Batch 1.

Measured per request:
- TTFT;
- every inter-token time, from which TPOT p50/p95 are computed;
- per-step split components: edge compute, serialisation, wire, server compute;
- bytes on the wire (prefill and per token, from socket counters, cross-checked
  against `n × 5120 × 2`);
- edge GPU power from NVML at 100 ms intervals. Edge J/token = ∫P dt / tokens. REMOTE is
  charged at edge idle-wait power. Server power from DCGM/NVML is reported, not optimised.

Link and state factors:
- RTT ρ ∈ {native (<1 ms), 5, 20, 50} ms;
- bandwidth B ∈ {100 Mbps, 1 Gbps};
- server contention κ, created by a vLLM load generator on the server GPU(s) at
  concurrency {0, 8, 32}. The *realised* per-token slowdown is measured for REMOTE and
  for the split's server segment separately, not assumed to be equal.

Cells (smallest set that identifies the additive per-token model of PROBLEM-FORMULATION §3.2):

| Block | Paths | Factor levels | Cells |
|---|---|---|---|
| Core | SPLIT U-min, SPLIT U-max(16), REMOTE, EDGE-best(12, 16, 24) | native RTT, 1 Gbps, κ=0 | 6 |
| RTT sweep | SPLIT U-max(16), REMOTE | ρ ∈ {5, 20, 50} | 6 |
| Cut-invariance check | SPLIT U-min | ρ = 20 | 1 |
| Bandwidth | SPLIT U-max(16) | 100 Mbps, ρ = native | 1 |
| Contention | SPLIT U-max(16), REMOTE | load concurrency {8, 32} | 4 |
| Held-out validation | SPLIT U-max(12), SPLIT U-max(24), REMOTE | 4 random (ρ, B, κ) combos drawn with the fixed seed | 4 |

- **Total:** 22 cells × 3 repetitions after 2 warm-up requests.
- **Time:** about 3–4 h of SPLIT wall-clock at roughly 10 tok/s, less for the others.
- **Model validation:** the additive model fitted on the other cells must predict the
  held-out cells' TPOT p50 to within ±10%. Otherwise the model is not used to
  interpolate, and R is evaluated only at measured cells.

## 7. Deterministic controls

- Pinned identical `torch`, `transformers` and CUDA versions on both hosts (recorded);
  model revisions pinned by commit hash.
- Q1/Q2:
  - greedy decoding, batch 1;
  - `torch.use_deterministic_algorithms(True)` where supported;
  - TF32 disabled;
  - the same chat template with `enable_thinking=True`.
- The cut tensor is transmitted as raw bf16, with no dtype change. An fp16 cast is
  forbidden because of overflow risk in Qwen3 hidden states.
- Q3: fixed seeds {0, 1}; the engine and version are recorded.
- E0-L:
  - no other jobs on the edge GPU;
  - GPU clocks locked where permitted (`nvidia-smi -lgc`);
  - the order of cells is randomised within each block;
  - the netem configuration is logged before and after every cell;
  - ping RTT is sampled during the run.

## 8. Frozen pass/fail criteria

**Q: output equivalence.** All must hold for both U-min and U-max(16):
- Q1: `D_split ≤ max(D_pipeline, D_hw) + 0.2 pp`, and mean KL ≤ 2 × max(KL_pipeline, KL_hw).
- Q2: ≥ 27 of 30 first divergences (or no divergence) fall at a reference top-1/top-2
  margin < 0.5 nats, and no SPLIT sequence degenerates into repetition or invalid tokens unless the reference sequence for the same prompt also does. Greedy thinking-mode decoding can loop on its own; the Qwen3 model card warns against it.

If Q fails:
- one implementation fix is allowed;
- if Q still fails, SPLIT is removed;
- **no activation compression may be introduced to rescue it.** Compression only adds
  error.

**F: feasibility.** All must hold:
- U-max(M) runs at 16k context within cap M for M ∈ {12, 16, 24};
- there are zero transport errors or OOMs over every E0-L request;
- edge peak memory is logged.

A class that fails F is dropped from R, and that is not an E0 failure. **F fails if
no class passes.**

**R: a useful regime.**
1. Use the measured profiles together with the Q3 per-query `(score, tokens)`.
2. Compute on-time utility `U` (PROBLEM-FORMULATION §3.4) for each cell in:
   - memory class ∈ {12, 16, 24} GB;
   - privacy class ∈ {`no-raw-text`, `open`};
   - state ∈ {good, contended at load 32};
   - ρ ∈ {native, 20 ms};
   - deadline D ∈ {30, 60, 120, 300, 600} s.
3. The admissible competitors in each cell are the best admissible non-SPLIT action:
   - `no-raw-text`: EDGE-best(M) (including 32B-AWQ+FP8-KV where it fits);
   - `open`: max(EDGE-best(M), REMOTE-32B).

   The best is taken over (model, mode) pairs on both sides (§3.1 amendment). SPLIT may use
   either mode, and so may each competitor.

**R passes iff at least one cell shows `U_SPLIT − U_best-admissible ≥ 3.0 pt` with a
paired-bootstrap 95% CI > 0 (10,000 resamples over queries).**
- Report every cell, not just the winner.
- If the passing cells are all at the 12 GB class, declare that the regime is restricted
  to memory-starved edges.

Two cells are excluded **by construction**:
- the remote-down state, because SPLIT needs the server too;
- deadlines where every action has U < 0.05.

**E0 PASS = Q ∧ F ∧ R.**

| Outcome | Consequence for F3 / the paper |
|---|---|
| PASS, with `no-raw-text` cells only | SPLIT enters `A` as the `no-raw-text` quality tier. The paper's SPLIT claim is "a larger model under a raw-text-stays-local constraint", and **measured leakage must be reported** (Cunningham: about 35% token recovery at 8 layers), never called privacy-preserving |
| PASS, including `open` cells | unexpected given the literature; re-check against the component floor and the netem logs before believing it |
| Q or F fails | SPLIT removed. F3 = EDGE/REMOTE; H-joint must pass on contention alone (PROBLEM-FORMULATION §4) |
| Q ∧ F pass, R fails | SPLIT removed, for lack of a regime. Report it as a negative result: "weight-quantised edge models dominate layer split" is itself a publishable measurement |

**Early stop (pre-declared, saves E0-L).** If Q3 finds the measured gap between
32B-bf16 and EDGE-best(16) to be < 3.0 pt on **every** task, **in each mode separately**
(thinking vs thinking, non-thinking vs non-thinking), R cannot pass at 16 or 24 GB.
On-time utility ≤ accuracy, and in the same mode the edge actions are faster than SPLIT.
Then run only the 12 GB class and the 6 core cells.

## 9. Order and effort

1. **Hardware check:** GPU model and memory on the edge and the server; `nvidia-smi`;
   LAN RTT; whether netem is allowed. Takes 0.5 h. HARDWARE-PLAN.
2. **Q3 accuracy** of 32B-bf16 and the AWQ variants on the server, batched. About 4–6 GPU-h,
   unattended. Apply the early-stop rule.
3. **Split runtime + Q1 + Q2.** About 1 day of coding plus about 2 h of runs.
4. **E0-L, 22 cells.** About 4 h, on both endpoints at the same time.
5. **R computation** offline from the logs, using the sim code in
   `evidence/joint_vs_sequential_sim.py` with measured profiles substituted.

**Total:** about 2.5 days, of which only steps 3 and 4 need both machines.

## 10. Artifacts E0 must leave

- `e0/q1_agreement.csv`: per query and config, D and KL.
- `e0/q2_divergence.csv`
- `e0/q3_scores.jsonl`: per query, model, seed, score and tokens.
- `e0/latency/*.jsonl`: per token, per component.
- `e0/netem_log.txt`, `e0/env.json` (versions, hashes, clocks).
- `e0/R_cells.md`: every cell, U per action, Δ, and CI.
- `e0/DECISION.md`: PASS/FAIL per Q/F/R, and the consequence row from §8.
