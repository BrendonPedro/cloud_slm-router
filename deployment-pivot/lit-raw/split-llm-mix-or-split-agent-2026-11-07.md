# Raw lit notes: Mix-or-Split + split LLM inference (subagent, 2026-11-07)

Produced by a research subagent on 2026-11-07. Mix-or-Split was read in FULL TEXT from the
author-hosted PDF. This is RAW input for LIT-REVIEW.md; re-check numbers before citing.

## Mix-or-Split (READ, full text)
- **Paper:** "Mix-or-Split: Latency-Aware Scheduling for Edge–Cloud LLM Inference".
  - Authors: Xinghan Wang, Xiaoxiong Zhong (corresponding author), Weihong Yang, Fangming Liu, Weizhe Zhang (Peng Cheng Lab).
  - IEEE TPDS 37(11):2423–2439, Nov 2026. DOI 10.1109/TPDS.2026.3729256.
  - PDF: https://fangmingliu.github.io/files/tpds26-moe.pdf (17 pages, matching the Crossref page range).
- **Modes:** three per request.
  - CLOUD: prefill and decode in the cloud.
  - SPLIT: **cloud prefill → KV cache crosses the backhaul → edge decode**. This is prefill/decode (PD) disaggregation, NOT a layer split.
  - MIX: prefill and decode co-located on the edge GPU, with an SM-feasibility check.
- **Model:** the SAME model at every site. No model selection, no quality term. Multi-model deployment is listed as future work.
- **Decision variables:** edge server and mode per request (minimum predicted latency). Also OFDMA bandwidth fractions, admission windows, prompt bucketing, and kernel tile and prefill/decode allocation.
- **Objective / constraints:** TTFT, TPOT, deadline and GPU-resource constraints; goodput and SLO attainment.
- **Hardware:** cloud A800 80GB; edge RTX A6000 48GB. Models: Llama-3 and Qwen3-8B.
  - Wireless emulated at 20/50 Mbps with 10 ms delay; backhaul 1/10/40 Gbps via tc netem.
- **Transfer cost:** KV-cache bits = 8·2·N_layers·L_in·H_kv·d_h·bytes, plus measured copy, serialisation, deserialisation and RPC overheads.
- **Results:**

  | Policy (Qwen3-8B) | Mean latency | SLO attainment |
  |---|---|---|
  | Auto | 1179 ms (6.4% better than the best fixed policy) | — |
  | Edge | 1259.5 ms (best fixed policy) | 95.6% |
  | Split | 1467.8 ms | **66.7% (worst)** |
  | Cloud | — | 93.3% |
  | Mix | — | 100% |

  - Auto's P95 is not better than Cloud's or Edge's.
  - On the Llama-3 trace, Auto chose Cloud/Mix/Split for 18/21/6 requests.
  - KV transfer P95 grows from 745 ms (15 MiB) to 2606 ms (236 MiB), measured on loopback.
  - Raising backhaul from 1 to 40 Gbps lowers Split P95 only from 1759 to 1593 ms, so serialisation, not bandwidth, is the bottleneck.
  - Split wins only when the cloud's per-token return path is slow: with a 40 ms/token penalty, Cloud SLO drops to 0% while Split stays at 97.6%.
- **Gap vs ours:** no task recognizer, no utility table, no quality objective, and no layer split of a stronger model.
  It is the closest paper on "per-request mode choice from live network state and measured profiles".

## Other split papers
- **Splitwise** (UCC'25, DOI 10.1145/3773274.3774267). Head/FFN-level DRL+Lyapunov partitioning of ONE model.
  - Hardware: Jetson Orin NX / S23 / RPi5, with AWS p4d (8×A100) as the cloud.
  - Up to about 4% accuracy loss from quantising activations at the boundary.
  - The reported "87 ms" full-system latency looks implausible, and there is no explicit decode or KV model.
- **Adaptive Split Computing** (2511.04002). Chooses split layer, bit-widths, sequence length and KV-vs-hidden transmission.
  - Jetson Xavier NX with an A6000; simulated channel.
  - Naive token-wise quantisation of cut activations drops HellaSwag from 77.3 to 45.3; outlier-preserving splitting restores 77.1.
- **Joint partitioning/placement** (2512.01039). Vision paper; its table shows "expected KPIs", not measurements.
- **DIO-LLMs** (ICC'25, DOI 10.1109/ICC52391.2025.11160773). Abstract only; Greedy-PPO intra/inter-layer partitioning, simulated.
- **MBRL layer splitting** (2406.02616). Simulation; perplexity under channel noise. Earlier splits are more fragile.
- **SplitLLM** (2410.10759). Dynamic programming over client layers to cut server load by about one third. BERT/GPT-2 class models; simulated communication.
- **In-Browser Split Inference** (IEEE Access 14, 2026, DOI 10.1109/ACCESS.2026.3720562).
  - WebGPU client running layers 0..k−1; server RTX 3060. SmolLM2-1.7B and Phi-3.5-mini.
  - Per-token network time is INDEPENDENT of k (5G: 315 / 326 / 314 ms at k = 0 / 16 / 32).
  - For the weak client the best k is about 0, i.e. effectively remote. Local-vs-offload crossover at about 60 ms RTT (SmolLM2) and about 150 ms (Phi-3.5).
  - Rule: offload iff profiled O(RTT) > local throughput.
    - Always-offload loses up to 82% of achievable throughput; always-local loses up to 69%.
  - Per-channel INT8 at the cut changes perplexity by 0–7%; per-tensor INT8 is catastrophic.
- **Cunningham** (2602.16760). Embedding, head and first/last layers on a local RTX 3090; middle layers on a cloud A100 or 4090. Mistral-7B and NeMo-12B; about 80 ms RTT.

  | Setup | tok/s |
  |---|---|
  | Local only | 39 |
  | Split, sequential | 11 |
  | Split, with lookahead | 13–17 |
  | Cloud API | 30–60 |

  - Per-token time: 64% network RTT. Output is TOKEN-IDENTICAL with fp16 activations and greedy decoding.
  - Inversion attack recovers about 59% of tokens at a 2-layer split and about 35% at 8 layers.
  - Privacy is the only justification for split here.
- **EC-LLM** (IEEE IoT-J 2026, DOI 10.1109/JIOT.2026.3710272). Abstract only. NOT a split paper: an edge→cloud cascade with foresight/hindsight early stopping.
- **EdgeShard** (IEEE IoT-J 2025). Device selection plus layer partition by dynamic programming. 12 AGX Orin + 2 Orin NX, with an RTX 3090 as the "cloud"; Llama2 7B/13B/70B.
  - At 1 Mbps the optimum for 7B is Edge-Solo. For 13B/70B, edge-only runs out of memory, so splitting is the only option.
  - Cloud-only was excluded "for privacy".
- **HAT** (2503.18989). U-shaped split plus device-side SLM drafter (speculative decoding). 30 Jetsons + 8×A6000.
  - A plain U-shaped split is SLOWER than cloud on both TTFT and time-between-tokens. At a 2k-token prompt, TTFT is 3.57 s, 89.6% of it communication.
- **RAC** (2608.04991). Compresses activations crossing a head/middle/tail split by about 72–75%. 2×3090 local, A800 cloud; GLM-4-9B, Qwen3-30B-A3B, Llama-3.3-70B.
  - Global INT4 on activations is catastrophic; RAC stays within about ±2.5 task points. No cloud-only baseline.
- **Speculation at a Distance** (2606.25091). Analytical: edge-draft/cloud-verify loses to co-located speculative decoding, and beats cloud autoregressive decoding only below roughly 50–60 ms RTT.
- **Brief:** Galaxy, PicoSpec, ICNP'25 split-transport poster, DynaSplit (WcCST'26; garbled abstract).

## Synthesis
- **Split is useful only when:**
  1. the model does not fit on the edge (it then competes only with REMOTE);
  2. privacy or regulation forbids REMOTE;
  3. offloading server load or throughput under multi-tenancy matters;
  4. the client is weak and RTT is low, but then the best k is about 0, i.e. effectively remote.
- **On latency, split loses to remote in every measured study:**
  - Cunningham: 11 tok/s split vs 30–60 tok/s cloud API.
  - HAT: plain U-split slower than cloud.
  - EdgeShard: optimum is local at 1 Mbps.
  - Mix-or-Split: Split has the worst SLO attainment.
  - In-Browser: per-token RTT is independent of k.
  - This matches evidence/split_bound.md.
- **Quality:** splitting is lossless at fp16 (token-identical under greedy decoding). Naive activation quantisation is catastrophic; per-channel or outlier-aware schemes stay within about 0–7% perplexity or about ±2.5 points.
- **Novelty:** "model selection + EDGE/SPLIT/REMOTE" is NOT FOUND in the literature.
  - Closest on mode selection: Mix-or-Split (one model, prefill/decode split, no quality term).
  - Closest on routing: ECO-LLM / EC-LLM / Lyra / PerLLM / ECLD 2602.13628 (no split).
  - Closest hybrid: HAT (fixed architecture).
- **Expectation:** SPLIT is chosen only when REMOTE is ruled out (privacy, cost or capacity) and EDGE lacks memory or quality.
  This implies the optimizer's SPLIT branch is a constraint-driven fallback, not a latency optimization.
