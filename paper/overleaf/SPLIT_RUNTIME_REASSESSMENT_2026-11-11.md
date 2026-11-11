# Split runtime reassessment (2026-11-11)

Scope: CPU-only reanalysis of the archived E0 profiles, a runtime and framework audit from current documentation and source, a corrected hardware audit, and a GO/NO-GO decision for an optimised-runtime follow-up. No GPU was used, no inference was run, no paid instance was started, E0 and its tag `e0-prereg-v1` are untouched, nothing is committed or pushed.

Inputs: `~/research/LLMRouterBench/e0_stage1_VALID_UB1_CONTINUE.tgz` (sha256 `3984d73a…b84f`), `e0_stage2_VALID_UB2_STOP.tgz` (sha256 `f0df5369c30e70013fa8b3c5dbb54b2df78b06ee5fedaeffbe9b9945839fdae9`, verified), harness commit `81461b6`, S1 per-query scores `q3_scores.jsonl`. Scripts and outputs: `~/research/LLMRouterBench/diagnostics/deployment_e1opt/reanalysis/` (`server_speedup_curve.py`, `breakdown.py`, `bw_threshold.py`, `out/*.json`).

## 1. Why the frozen E0 runtime was eager Hugging Face

The frozen layout (E0 PREREG §2) gives the edge the embedding, layers [0, k), layers [64−k, 64), the final norm, the LM head and sampling, and gives the server layers [k, 64−k). Each side keeps its own KV cache. Per forward step one bf16 residual-stream tensor crosses each way. This is not two-stage pipeline parallelism: the same physical device executes both ends of the network and samples.

E0 was pre-registered on 2026-11-08 with one implementation freedom: "a two-process Hugging Face runtime … reuses the transformers 4.51.3 Qwen3 modules unchanged … No other optimisation is permitted before R: no CUDA graphs, batching, speculation, compression or compilation" (PREREG §2). The reasons, in order:
1. No serving engine expresses the layout (§2 below), so a custom runtime was needed in any case.
2. Reusing the stock Qwen3 decoder layers made the split provably the same computation: bitwise equality with the unsplit model on CPU (LOCAL_VALIDATION, 41 checks) was the Q gate's foundation.
3. Freezing the runtime before data prevented post-hoc tuning. The cost was pre-stated as threat 1 (PREREG §11): "SPLIT runs in an eager HF runtime while EDGE and REMOTE run in vLLM. This penalises SPLIT's latency … It is never used to overturn a FAIL." The Stage-3 REMOTE-HF cell that would have separated "this runtime" from "split itself" was never reached, because G-UB2 stopped first.

What the measurement then showed (Stage 2, one H200, `server_compute_ns` of single-token steps, 36 usable requests per profile): fitted decode-step intercept 70.7 / 66.9 / 61.3 / 50.2 ms at k = 1 / 3 / 5 / 9 (62 / 58 / 56 / 46 layers). The H200 datasheet roofline for the same segments (weights 56.6 GB at k = 3 over 4.8 TB/s) is 11.8 ms at k = 3. Ratio 5.7. Per layer: about 1.2 to 1.4 ms measured against 0.2 ms roofline. The edge segment on the RTX 3090 (6 layers + LM head at k = 3) measured 11.7 ms against a 7.9 ms roofline (68 %). A fixed cost of roughly 1 ms per layer that does not scale with the GPU's bandwidth is the signature of per-kernel launch latency and Python dispatch in an eager loop (about 15 to 20 kernels per Qwen3 layer plus the cache bookkeeping), which CUDA-graph replay removes. Prefill was also slow (146 ms for 256 tokens at k = 3 against a 14.6 ms roofline) but prefill is under 1 % of a typical request's time in this workload (median 524 generated tokens).

## 2. What vLLM supports (checked 2026-11-10 against the main branch)

| Question | Evidence | Verdict |
|---|---|---|
| Layer-to-stage assignment | `vllm/distributed/utils.py get_pp_indices`: one `[start, end)` per rank; `VLLM_PP_LAYER_PARTITION` sets the sizes of consecutive chunks; docstring: "The first and last partitions are excluded because they contain the input and output embeddings respectively" | contiguous ranges only |
| Where embedding / norm / LM head live | `models/qwen2.py` (Qwen3Model inherits): `embed_tokens` only if `is_first_rank`, else `PPMissingLayer`; `norm` only if `is_last_rank`; `models/qwen3.py`: `lm_head` only if `is_last_rank`; non-last ranks return `IntermediateTensors(hidden_states, residual)` | first rank / last rank, hard-coded |
| Two stages on one GPU | `config/parallel.py`: world size above the node's GPU count is an error; `v1/executor/multiproc_executor.py` and `v1/worker/gpu_worker.py`: one worker per `local_rank`, device `cuda:{local_rank}` | not supported |
| Multi-node transport | `distributed/parallel_state.py`: PP group over NCCL (GPU tensors) + gloo (metadata); docs: "Ensure that every node provides an identical execution environment"; NCCL over raw TCP "is not efficient" | works over Ethernet; mixed aarch64 / x86 and mixed GPU generations not documented as supported |
| Drive a middle segment from outside | `IntermediateTensors` is internal to the PP group (`send_tensor_dict` / `recv_tensor_dict`); no engine or HTTP API accepts hidden states; Qwen layers carry two tensors (hidden, residual), not one | no public interface |
| Built-in split / edge-cloud mode with client-held embedding and head | none found in docs or issues | not supported |

SGLang (`srt/models/qwen2.py`, `make_pp_layers`, `SGLANG_PP_LAYER_PARTITION`) and TensorRT-LLM (`pp_partition`, PR 9003: per-rank layer counts) have the same structure: contiguous ranges, embedding on the first rank, norm and head on the last.

## 3. Why standard vLLM pipeline parallelism does not implement our topology

Three properties of the frozen design each fail separately:
- the edge owns a non-contiguous layer set, [0, k) ∪ [64−k, 64); vLLM ranks own one contiguous range;
- the edge owns the embedding **and** the LM head; vLLM places them on different ranks (first and last);
- sampling happens on the edge; vLLM samples on the last rank, which would be the server, so logits and sampled tokens would cross the link and the no-raw-text accounting would change.

A three-stage pipeline (edge-first, server-middle, edge-last) would fix the first property only if stages 0 and 2 could share one GPU; the executor maps one worker to one device and the stage order is linear, so it cannot. Even then the LM head would sit on stage 2 and sampling would need to be moved. None of this is a configuration matter; it is model and executor code.

## 4. Candidate optimised implementations

| Candidate | Same model computation | First+last on edge | No raw text | Sampling on edge | Changes the architecture | Difficulty | Runs on DGX Spark | Runs on the Asus machine | Changes the question |
|---|---|---|---|---|---|---|---|---|---|
| A. vLLM PP with custom placement | yes | no | yes | no | yes | n/a | n/a | n/a | yes |
| B. vLLM 3 stages, 0 and 2 on one GPU | yes | would | yes | no | yes | blocked by the executor | n/a | n/a | yes |
| C. Custom vLLM worker / transport | yes | possible | yes | possible | no | very high: internal APIs, two-tensor residual, KV manager | unclear (official Spark support is a CUDA-13 nightly "compatibility track") | unknown GPU | no |
| D. vLLM kernels / model executor without the engine | yes (kernels differ; Q-tested) | yes | yes | yes | no | high | unclear | unknown | no |
| **E. Custom PyTorch: E0 modules + fixed-shape KV + CUDA graphs + `flash_attn_with_kvcache`** | yes (prefix mode bitwise; static mode Q-tested) | yes | yes | yes | no | moderate | CUDA graphs and SDPA fallback yes; FlashAttention-2 on sm_121 by source build or community wheel only | needs an NVIDIA GPU ≥ Ampere, bf16 | no |
| F. Other frameworks: Petals (client holds embed + head, no blocks; unmaintained since 2024-09, no Qwen3); llama.cpp RPC (`-ot` places weights by regex, but per-layer device, KV cache and output layer follow the contiguous `--tensor-split`; GGUF kernels and quantised weights); exo (Linux CPU only); PiPPy (one rank may hold two stages; no KV-cache generation documented) | no / partial | partial | partial | partial | yes | n/a | llama.cpp yes | unknown | yes |

Transformers 4.51.3 facts that shape E: Qwen3 declares `_supports_static_cache = True`; `StaticCache.update` uses `index_copy_` at `cache_position`; the stock SDPA path (`integrations/sdpa_attention.py`) runs `repeat_kv` over the **full** key length every step, an 8x copy for Qwen3-32B's 64/8 GQA, which with a static 17,920-token cache would move about 4 GB per step on the server. The static GPU path therefore needs `flash_attn_with_kvcache` (in-place cache, `cache_seqlens`, native GQA, fixed shapes) or an equivalent kernel. Hugging Face reports "up to a 4x speed up" for static cache + `torch.compile` on whole-model generation, smaller for larger models.

Chosen: **E**, built as `~/research/LLMRouterBench/diagnostics/deployment_e1opt/` (§9).

## 5. Exact required-speedup analysis (CPU, archived data, E0 gate code unchanged)

Method. `e0_r.py` (commit 81461b6) is imported unmodified. The only change is a factor f on the Stage-2 measured server-segment profile before the gate's own 0.90 discount: server time = 0.90 · f · measured. Edge-segment profiles, competitor profiles, eligibility, S1 scores, the 200 × 2 queries, the bootstrap (10,000, seed 20261107) and the exclusions are the archived ones. At f = 1 every evaluated cell's Δ and CI equal the archived `gate_ub2.json` to floating-point precision (checked by the script).

### 5.1 What G-UB2 falsified, and what it did not

1. Falsified: that this frozen runtime, on these cells, keeps Δ ≥ 3.0 in any cell with zero network time. The bound is monotone (PREREG §9.2), so the real E0-R could not have passed. The decision and its archive are final.
2. Not falsified: that the split design opens a quality tier. The server term entered as "measured compute of the frozen eager runtime × 0.9". No measurement of an optimised runtime exists, and the Stage-3 REMOTE-HF comparison never ran.
3. How much of the failure is the measured eager server compute: all of the change between G-UB1 and G-UB2 (+12.25 → +0.5) is the server term; the two gates share every other input. The datasheet term in G-UB1 (11.8 ms at k = 3) corresponds to f ≈ 0.18.
4. Is the server term the dominant difference: yes, it is the only difference.
5. Any other measured term preventing a pass: at the best cell no. The edge segment (11.7 ms + 0.7 ms per 1,000 context tokens at k = 3, cap 12 GB, × 0.9) and the competitor profile are also in the bound; with a perfectly fast server (f = 0) the best cell reaches +15.25 and 9 of 10 no-raw-text cells pass, so the edge term alone does not stop a pass. The S1 quality gap caps what any runtime can recover (+15.25). At D ≥ 300 s the 8B-AWQ thinking competitor (U = 0.63) beats non-thinking SPLIT (0.58) at any speed; thinking SPLIT needs a server step below about 27 ms (f ≈ 0.4) to win at D = 600 s.

### 5.2 Required server compute at the best cells

| Target | any cell | 12 GB, D = 60 s | 16 GB, D = 60 s | 12 GB, D = 600 s | 16 GB, D = 600 s |
|---|---|---|---|---|---|
| Δ ≥ 0 (reach the competitor) | already (f = 1, +0.5) | f = 1 | f = 1 | f = 0.874 | f = 0.834 |
| Δ ≥ +3.0 (the E0 gate) | **f = 0.830 (1.20×)** | 0.830 | 0.814 | 0.734 | 0.679 |
| CI lower bound > 0 | f = 0.689 | 0.689 | 0.660 | 0.661 | 0.596 |
| Full pass (Δ ≥ 3.0 and CI > 0) | **f = 0.705 (1.42×)** | 0.705 | 0.675 | 0.672 | 0.609 |

In milliseconds at k = 3: the raw measured step is 66.9 ms (60.2 ms after the 0.9 discount). Δ ≥ 3.0 needs a discounted server intercept ≤ 50.0 ms (raw ≤ 55.5 ms). A full pass needs ≤ 42.4 ms discounted (raw ≤ 47.2 ms). These are small improvements: a 1.2× and a 1.42× faster server step, against a measured-to-roofline ratio of 5.7×.

### 5.3 The curve: server scaling factor → best bounded advantage (no-raw-text cells, 12 and 16 GB)

| f | server step k = 3 (ms, discounted) | best Δ | CI low | cells Δ ≥ 3 | cells pass | 12/30 | 12/60 | 12/120 | 12/300 | 12/600 | 16/30 | 16/60 | 16/120 | 16/300 | 16/600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.00 (measured, G-UB2) | 60.2 | +0.50 | −4.75 | 0 | 0 | −17.00 | +0.50 | −2.00 | −5.00 | −1.75 | −17.00 | +0.50 | −2.25 | −5.00 | −2.75 |
| 0.90 | 54.2 | +2.25 | −3.25 | 0 | 0 | −14.75 | +2.25 | −1.75 | −5.00 | −0.25 | −15.25 | +2.25 | −1.75 | −5.00 | −0.75 |
| 0.83 (gate) | 50.0 | +3.0 | −2.4 | 1 | 0 | | | | | | | | | | |
| 0.80 | 48.2 | +3.50 | −2.00 | 2 | 0 | −11.25 | +3.50 | −1.25 | −5.00 | +1.00 | −13.00 | +3.50 | −1.25 | −5.00 | +0.50 |
| 0.705 (full pass) | 42.4 | +5.2 | +0.0 | 3 | 1 | | | | | | | | | | |
| 0.70 | 42.1 | +5.25 | +0.00 | 3 | 0 | −6.75 | +5.25 | −0.50 | −5.00 | +4.00 | −7.75 | +4.50 | −0.50 | −5.00 | +2.50 |
| 0.60 | 36.1 | +7.75 | +2.25 | 4 | 3 | −1.25 | +7.75 | −0.25 | −5.00 | +6.25 | −3.25 | +6.50 | −0.25 | −5.00 | +4.50 |
| 0.50 | 30.1 | +9.50 | +4.00 | 4 | 4 | +1.00 | +9.50 | +0.25 | −5.00 | +7.25 | +0.75 | +8.75 | +0.00 | −5.00 | +6.50 |
| 0.40 | 24.1 | +10.25 | +5.50 | 6 | 4 | +4.00 | +10.25 | +0.25 | −2.25 | +10.25 | +3.00 | +9.50 | +0.25 | −4.75 | +8.00 |
| 0.30 | 18.1 | +11.75 | +7.25 | 6 | 5 | +6.75 | +11.25 | +0.25 | +0.75 | +11.75 | +5.25 | +10.50 | +0.25 | −1.50 | +10.00 |
| 0.20 | 12.0 | +12.00 | +6.49 | 7 | 7 | +11.00 | +12.00 | +0.25 | +6.00 | +11.75 | +7.75 | +11.75 | +0.25 | +1.00 | +11.75 |
| 0.18 (≈ H200 roofline, G-UB1 territory) | 10.6 | +12.25 | | | | | | | | | | | | | |
| 0.10 | 6.0 | +13.50 | +8.25 | 8 | 8 | +13.50 | +12.50 | +0.25 | +8.75 | +11.75 | +11.75 | +12.25 | +0.25 | +5.75 | +11.75 |
| 0.00 | 0.0 | +15.25 | +10.00 | 9 | 9 | +15.25 | +12.50 | +5.75 | +11.75 | +11.75 | +13.50 | +12.50 | +0.25 | +8.25 | +11.75 |

(The f = 0.83 and 0.705 rows are the bisection results; the other rows are the grid in `out/curve.json`.) Figure: `main.tex` Fig. 5.

Mechanism of the discontinuity (12 GB, D = 60 s, non-thinking SPLIT; 200 queries × 2 seeds; its total correct rate is 0.580):

| f | U_SPLIT | share on time | T median / p75 / p90 (s) |
|---|---|---|---|
| 1.00 | 0.460 | 0.730 | 37.4 / 63.7 / 111.8 |
| 0.83 | 0.485 | 0.762 | 32.0 / 54.6 / 95.7 |
| 0.705 | 0.5075 | 0.805 | 28.0 / 47.8 / 83.9 |
| 0.50 | 0.550 | 0.890 | 21.5 / 36.7 / 64.5 |
| 0.00 | 0.580 | 0.983 | 5.7 / 9.8 / 17.5 |

Between f = 1 and f = 0.705, 30 of the 400 query-seed pairs cross the 60-s deadline, 19 of them correct: +4.75 points. The competitor is fixed at U = 0.455 (8B-AWQ thinking, 61 % on time at 60 s, 0.63 correct). Per token at 800 tokens of context, the bound's SPLIT step is 71.7 ms (edge 11.0 + server 60.7, both discounted) against 8.9 ms for the 8B-AWQ competitor; 32B non-thinking answers have a median of 524 tokens (p90 1,553), 8B thinking answers a median of 4,851.

### 5.4 Link what-if (not part of the gate; the gate is zero-network by design)

Adding one synchronous round trip per forward step (decode step and prefill chunk):

| RTT per step (ms) | f = 1.0 | f = 0.5 | f = 0.25 | f = 0.1 | f = 0 |
|---|---|---|---|---|---|
| 0 | +0.50 | +9.50 | +12.00 | +13.50 | +15.25 |
| 1 | +0.50 | +9.00 | +11.75 | +13.00 | +15.00 |
| 5 | +0.00 | +8.00 | +11.25 | +12.25 | +13.50 |
| 20 | −3.75 | +3.25 | +8.00 | +10.00 | +11.75 |

A local-network link (≤ 1 ms) costs at most 0.5 points. A 20-ms wide-area link removes most of the advantage. The E0 G-link rule (p50 ≤ 5 ms) stays appropriate.

## 6. Hardware criterion and hardware audit

### 6.1 Server bandwidth criterion (gate-ub1 with the server at its bandwidth roofline, prefill at H200 FLOPs to stay optimistic, measured RTX 3090 edge × 0.9, zero link)

| Server (public datasheet bandwidth) | GB/s | at 100 % | at 70 % | at 50 % |
|---|---|---|---|---|
| GB10 / DGX Spark | 273 | step 207 ms, best −5.00 | −6.00 | −8.00 |
| RTX 3090 | 936 | 60.4 ms, +0.50 | −5.00 | −5.00 |
| RTX 4090 | 1,008 | 56.1 ms, +2.25 | −3.50 | −5.00 |
| RTX PRO 6000 Blackwell | 1,792 | 31.6 ms, +9.00 pass | +4.50 no | +0.25 |
| H100 PCIe | 2,000 | 28.3 ms, +9.50 pass | +6.00 pass | +2.25 |
| A100 80 GB SXM | 2,039 | 27.7 ms, +9.50 pass | +6.50 pass | +2.25 |
| H100 SXM | 3,350 | 16.9 ms, +11.75 pass | +10.25 pass | +8.75 pass |
| H200 | 4,800 | 11.8 ms, +12.25 pass | +11.75 pass | +10.50 pass |

Minimum **effective** server decode bandwidth: 1,127 GB/s for Δ ≥ 3.0 in some cell (server step 50.2 ms at k = 3); 1,322 GB/s for a full pass (42.8 ms). A GB10 is 4 to 5 times short at its roofline. Independent public measurements agree with the roofline: Qwen3-32B bf16 decodes at 3.7 tok/s on a DGX Spark (NVIDIA cuTile tutorial), q4 at 9 to 14 tok/s (Ollama blog, NVIDIA forum).

### 6.2 Correction of the previous pass

`FINAL_REVIEW_NOTES_2026-11-10.md` §4 and `REFRAME_AUDIT_2026-11-10.md` §12.2 stated that no advisor instruction naming hardware exists. That was wrong: it was missing from the repositories, not from the record. The advisor's instruction (quoted by the user on 2026-11-10): "the SLMs and Split-LLMs mentioned in the paper are all that you will use. The computational resources will be the Asus server and DGX Spark", and later "after we get the right router with good performance, we will test it with our server resources". The Asus server and DGX Spark are the intended final system-level resources. Roles were not assigned.

### 6.3 Hardware audit table

| Machine | Role if documented | GPU / accelerator | Memory | Software constraints | Network | Source | Known / unknown |
|---|---|---|---|---|---|---|---|
| "Asus server" | final system-level resource (advisor statement, B); edge or server role **not stated** | unknown (D) | unknown (D) | unknown (D) | unknown; physical link to the DGX Spark unknown (D) | advisor statement (B); `deployment-pivot/HARDWARE-PLAN.md` §1 "not documented anywhere" (A) | **unknown** |
| "DGX Spark" | final system-level resource (B); role not stated (D) | GB10, Blackwell, compute capability 12.1 (public spec, C) | 128 GB LPDDR5X unified, 273 GB/s (public spec, C) | aarch64, DGX OS 7.6 / CUDA 13.0.3 (Oct 2026 release notes, C); FlashAttention-2 wheels for sm_121 not official (C); vLLM on a CUDA-13 nightly track (C) | 10 GbE RJ-45 + 2 × ConnectX-7 QSFP (public spec, C) | advisor statement (B); NVIDIA product and docs pages (C) | identity known as a product; the lab unit, its OS version and its link are **unverified** |
| "Edge server" of the 2026-10-08 manuscript (`source/main-original.tex` l.202) | edge testbed, client side of Split-LLM (A) | 2 × RTX 3090 24 GB (A) | 64 GB system RAM (A) | Ubuntu 20.04.6, Xeon W-2123 (A) | not stated (D) | manuscript (A) | documented; whether it is the "Asus server" is **unknown** (D) |
| "Cloud server" of the same manuscript | cloud side (A) | sentence unfinished ("equipped with …") (A) | — | — | — | manuscript (A) | documented as unspecified |
| Rented RTX 3090 pod (E0 Stage 1) | screening edge, capped to 12/16/24 GB (A) | RTX 3090 24,126 MiB (A) | — | torch 2.6.0+cu124, transformers 4.51.3, vLLM 0.8.5.post1 (A) | loopback echo only (A) | Stage-1 archive (A) | known, not the final hardware |
| Rented H200 pod (E0 Stage 2, S1) | screening server (A) | H200 143,771 MiB, driver 595.91.07 (A) | 2 TB host (A) | torch 2.6.0+cu124, CUDA 12.4 (A) | 12 × ConnectX NICs, not used (A) | Stage-2 `env/7eb83243ffc7.json` (A) | known, not the final hardware |
| This WSL box | analysis only (A) | none (A) | 9 GB visible (A) | no CUDA (A) | — | HARDWARE-PLAN §1 (A) | known |
| SSH / access information for the lab machines | — | — | — | — | — | HARDWARE-PLAN §1: "`ssh dgx` has no config entry on this box" (A) | **none documented** |

What must be inspected physically or asked before the final experiment (RUNBOOK §1 of E1-OPT): for each lab machine, hostname, OS and kernel, CPU architecture, `nvidia-smi` (GPU name, memory, driver, compute capability), CUDA toolkit and PyTorch versions, free memory; the NIC speeds and the measured RTT and throughput between the two machines; who assigns roles; whether `tc netem` (CAP_NET_ADMIN) is allowed; whether the 2 × RTX 3090 edge server of the October manuscript still exists and whether it is the Asus machine.

### 6.4 What the criterion implies for the lab pair, by role (derived, C)

- DGX Spark as **server**: fails the desk gate at its roofline in every cell. No runtime can change this. If it is the only server, E1-OPT ends at Stage 0 with a hardware result.
- DGX Spark as **edge**: its 128 GB holds Qwen3-32B whole, so the "edge too small" premise exists only as an emulated budget; its 273 GB/s makes both the split's edge segment and the 8B-AWQ competitor about 3.4 times slower than on the RTX 3090 (roofline ratio), which changes every profile. The gate must be re-run with measured profiles on that device (E1-OPT Stage 3).
- Asus server as **server**: admissible only if its GPU's effective decode bandwidth is ≥ 1,127 GB/s (≥ 1,322 GB/s for a pass with CI > 0): A100 / H100 / H200 class or an RTX PRO 6000 Blackwell at ≥ 70 % efficiency; an RTX 3090 / 4090 / 6000 Ada class GPU fails even at 100 % efficiency.
- Nothing above assigns roles. The inventory does.

## 7. GO / NO-GO for an optimised Split follow-up

| Criterion | Finding | Met? |
|---|---|---|
| 1. Technically credible implementation that preserves the research question | Option E keeps E0's modules, weights, cut, ownership, wire content and sampling; CPU tests show prefix mode bitwise equal to E0 and HF, static mode token-identical on greedy decoding | yes |
| 2. Required speedup plausibly reachable | 1.2× (gate) and 1.42× (full pass) needed; measured runtime is 5.7× above the roofline with a launch-bound per-layer signature; CUDA graphs target exactly that | yes |
| 3. Answers something E0 did not | E0 could not separate "this runtime" from "split itself" (threat 1; Stage 3 not reached) | yes |
| 4. Testable on the Asus server and DGX Spark | conditional: the DGX Spark cannot be the server (public bandwidth); the Asus machine's GPU is unknown; E1-OPT Stage 0 is a desk gate on the inventory that stops before any GPU time if the pair cannot host the server segment | conditional |
| 5. Could materially change the deployment conclusion | at f ≤ 0.70 the best cell passes with CI > 0 and 3 to 9 cells reach Δ ≥ 3; the Split conclusion would flip in the 12/16 GB, no-raw-text, D = 60 s regime (and D = 600 s with thinking SPLIT at f ≤ 0.4) | yes |

**Decision: GO, as a pre-registered experiment (E1-OPT) whose first stage is a desk hardware gate.** Not GO for "more time is available"; GO because the gap between the measured step and the required step is 1.2× while the gap between the measured step and the hardware limit is 5.7×, and because the E0 archive cannot answer the design question. NO-GO conditions are inside the pre-registration: the desk gate (server bandwidth), the equivalence gate (Q after one fix), and the bound gates after each measured segment.

What this does not say: that an optimised runtime will pass. The quality headroom caps the advantage at +15.25; the real link, the real edge GPU and server contention all subtract from the bound; and at 16 GB the S1 CIs include zero. The follow-up can end in "removed with a runtime within X % of the roofline", which would close threat 1 for this design.

## 8. Implications for the final Asus / DGX Spark testing

1. The final test is E1-OPT Stage 4 (joint cells over the lab link) and nothing in the current manuscript is that test. The manuscript now says so.
2. Before any code runs on the lab machines: the Stage-0 inventory and desk gate. If the DGX Spark is the only server-class box, the lab pair cannot host this split; the paper then reports the bandwidth criterion as the deployment result and the E0 STOP as a screen.
3. If the Asus server has an A100 / H100 / H200-class GPU: E1-OPT runs end to end on the lab pair, with the DGX Spark as the (emulated-budget) edge and all edge profiles re-measured there.
4. Software risks on the DGX Spark, from public sources: aarch64 wheels, FlashAttention-2 for sm_121 (source build), vLLM on a CUDA-13 nightly track. The E1 runtime's SDPA fallback and CUDA graphs do not need FlashAttention, but the edge competitor needs vLLM; its availability on the Spark must be checked at Stage 0.
5. No rented GPU is needed for the decision; a rented H200 Stage 2 would only screen the runtime on a server class the lab may not have, and is the user's call.

## 9. What was built tonight (CPU only; nothing run on a GPU)

`~/research/LLMRouterBench/diagnostics/deployment_e1opt/`: `PREREG_E1OPT.md` (draft, to freeze by tag), `IMPLEMENTATION_PLAN.md`, `RUNBOOK.md`, `README.md`; `e1_spec.py`, `e1_static_cache.py` (fixed-shape KV, prefix and static modes), `e1_segment.py` (Segment, GraphedStep with CUDA-graph capture and CPU fallback, USplitEdge, LocalMiddle), `e1_attention.py` (registered `e1_static` kernel: `flash_attn_with_kvcache` on CUDA, SDPA fallback), `e1_protocol.py` (E0 message set, version 2, buffers allocated once), `e1_memory.py`, `e1_bench.py` (`profile-segment` in E0's schema, `gate-ub` calling E0's gate), `tests/test_e1_cpu.py` (9 tests, all pass, including Qwen3-0.6B real weights: prefix mode bitwise equal to HF and to E0's runtime; static mode greedy tokens equal to HF; wire byte accounting; refusals; E0 directory unchanged since commit 81461b6; tag `e0-prereg-v1` at `1b277b3`), `reanalysis/` (the three scripts and their outputs).

## 10. One next research question

With the server segment of the U-split executed by a runtime frozen before measurement and running near its bandwidth roofline, does Qwen3-32B keep a ≥ 3.0-point on-time advantage over the best edge-feasible model at an emulated 12 GB budget, D = 60 s, under a no-raw-text policy, on the laboratory's edge and server machines?
