# Deployment-pivot literature review (2026-11-07)

Scope: does any 2025–2026 work already do **model/task selection jointly with
EDGE / SPLIT / REMOTE execution** under measured latency, energy, memory and network
constraints? Inputs:
- `lit-raw/*.md`: three research passes, full text read via arXiv HTML or the author PDF on 2026-11-07.
- Re-verification by the main agent the same day:
  - Mix-or-Split: re-read from the author PDF text.
  - RouterWise, BOute, ECO-LLM, EdgeShard: arXiv metadata and abstracts.
  - A fresh extended search for "model selection + split + routing". It found nothing new.

Earlier routing-side literature (RouteLLM, Avengers-Pro, UniRoute, R2-Router,
"routing gap is task type") is in `decision/LIT-REVIEW.md` and is not repeated here.

Read depth: **F** = full text read. **F+V** = full text read, and the key numbers were
re-checked against the primary source by the main agent. **A** = abstract or
metadata only. Do not make A-level claims central.

---

## 1. Bottom line

1. **Joint routing + resource allocation is solved in the datacenter.**
   RouterWise, BOute, Cascadia and arXiv 2604.07472 all optimise model choice (or
   routing fractions) together with GPU allocation and parallelism under latency
   SLOs. A "joint routing + placement" claim **without an edge/network dimension
   is not novel**.
2. **Model selection with EDGE vs REMOTE is crowded.**
   ECO-LLM, ConsRoute, CR², Yu et al. 2507.15553, TMO, PRISM and HybridInfer all
   pick a model or site per query, several on real hardware.
   2507.15553 already compiles its optimisation into a **runtime lookup table**, and
   ECO-LLM already uses offline query clustering with online nearest-prototype lookup.
   A task-table EDGE/REMOTE router is therefore **incremental at best**.
3. **SPLIT exists only for one fixed model.** Splitwise-UCC'25, EdgeShard, HAT,
   Hyperion, Cunningham, In-Browser Split and the drone VLM study all split a single
   model. None chooses *which* model to run as well as how to split it.
   Mix-or-Split's "Split" is **prefill/decode disaggregation of one model**, not a
   layer split, and it has no quality term.
4. **No paper found combines (a) quality-based model choice, (b) a layer-split
   option and (c) measured EDGE/REMOTE profiles plus live link state.** The nearest
   formulation, the Unified AI Gateway (2609.06940), is analytical only and uses
   prefill/decode disaggregation, not a layer split, as its "split".
5. **Every measured head-to-head comparison finds SPLIT slower than an
   uncontended REMOTE** (§4): drone VLM, Cunningham, HAT, In-Browser Split and
   Mix-or-Split. SPLIT wins only on device energy, edge memory, privacy, or when the
   remote path is degraded or capacity-limited. The open gap is therefore real but
   **narrow and conditional on SPLIT having a regime**, which is exactly what E0
   must test.

---

## 2. Central paper records

All dates read: 2026-11-07. "Joint" means routing/model choice and placement are
optimised together. "Act." means the paper models the cost of transferring
activations or the KV cache.

### Mix-or-Split: Latency-Aware Scheduling for Edge–Cloud LLM Inference — F+V
- **Venue / year:** IEEE TPDS 37(11):2423–2439, Nov 2026.
  [DOI 10.1109/TPDS.2026.3729256](https://doi.org/10.1109/TPDS.2026.3729256),
  [author PDF](https://fangmingliu.github.io/files/tpds26-moe.pdf).
  Authors: Wang, Zhong, Yang, F. Liu, Zhang.
- **Setting:** mobile devices → edge server (OFDMA wireless) → cloud over backhaul.
- **Decision variables:** per-request route, chosen from
  1. **Cloud**: prefill and decode both in the cloud.
  2. **Split**: *cloud prefill → KV cache over the backhaul → edge decode*.
  3. **Mix**: edge prefill and decode co-located, admitted only if SM-feasible.

  Also edge server choice, admission window, δ-similar prompt bucketing, kernel tile,
  and the prefill/decode SM allocation.
- **Objective:** minimum predicted end-to-end latency per request, under
  TTFT/TPOT/deadline SLOs and register, shared-memory and warp feasibility. Reports
  goodput and SLO attainment.
- **Hardware:** cloud A800-80GB PCIe; edge RTX A6000-48GB. Llama-3 and Qwen3-8B.
  Wireless emulated at 20/50 Mbps with 10 ms delay; backhaul 1/10/40 Gbps via
  tc/netem.
- **Coverage:** Edge ✔ (edge *server*, not a device). Split ✔ (prefill/decode
  disaggregation, **not a layer split**). Remote ✔. Joint ✘: the same model
  everywhere, no model selection and **no quality term**. Act. ✔: KV bits
  = 2·N_layers·L_in·H_kv·d_h·bytes, plus measured serialisation, copy and RPC.
- **Key measured results** (Qwen3-8B heterogeneous replay, Table II):

  | Policy | Mean latency | P95 | SLO attainment |
  |---|---|---|---|
  | Auto | 1179.2 ms (−6.4% vs best fixed) | 1769.4 ms | 100% |
  | Edge-local | 1259.5 ms | 1753.4 ms | 95.6% |
  | Cloud | 1316.4 ms | 1751.3 ms | 93.3% |
  | Mix | 1362.1 ms | — | 100% |
  | **Split** | 1467.8 ms | **2013.2 ms (worst)** | **66.7% (worst)** |

  - Auto does **not** improve P95: its P95 is 1.0% above Cloud's, with overlapping CIs.
  - Raising the backhaul from 1 to 40 Gbps lowers Split's P95 only from 1758.7 to 1593.0 ms,
    so KV **serialisation, not bandwidth,** dominates.
  - Split becomes necessary only when the cloud's per-token return path degrades:
    at +40 ms/token, Cloud's SLO falls to 0% while Auto keeps 97.6%.
  - A "multi-model sensitivity matrix" (Qwen3-1.7B, Qwen2.5-3B, Qwen3-8B,
    Qwen2.5-14B) sweeps profiles **one model at a time**. It is not model selection.
- **Future work it names:** multi-model, multi-tenant deployments.
- **Different from ours:** no model selection, no task utility, no layer split of a
  model too large for the edge, and no energy term. It is the closest prior art for
  **per-request mode choice from measured profiles and live network state**, and its
  "Auto" policy is the natural systems baseline (BASELINES.md).

### RouterWise: Joint Resource Allocation and Routing for Latency-Aware Multi-Model LLM Serving — F+V
- **Venue / year:** arXiv 2604.10907 (v1 13 Apr 2026, v2 22 Jun 2026), no venue.
  https://arxiv.org/abs/2604.10907
- **Setting:** a single GPU cluster.
- **Decision variables:** per-model setup (GPU count, TP degree, MPS share) plus
  routing fractions, with a per-prompt DeBERTa quality regressor and dual prices.
- **Objective:** maximise predicted average quality s.t. mean latency (TTFT) ≤ τ and
  GPU memory limits.
- **Hardware:** 4–8× A100-80GB.
- **Coverage:** Edge ✘, Split ✘, Remote: n/a (everything is in the datacenter).
  **Joint ✔.** Act. ✘ (no network).
- **Different from ours:** no edge, no network, no split, and provisionable
  resources (ours are fixed edge hardware). It shows quality varies by up to 87% across setups at a
  fixed SLO. This is the canonical "deployment decides outcomes" citation.

### BOute: Cost-Efficient LLM Serving with Heterogeneous LLMs and GPUs via Multi-Objective Bayesian Optimization — F+V
- **Venue / year:** arXiv 2602.10729 (Feb 2026). The comment field says "MLSys 2026"; acceptance is not confirmed on the page.
  https://arxiv.org/abs/2602.10729
- **Setting:** heterogeneous datacenter GPUs.
- **Decision variables:** RouteLLM threshold (8B vs 70B), GPU allocation matrix, and
  DP/TP/PP per model.
- **Objective:** multi-objective Bayesian optimisation (qNEHVI) under p95 ≤ L_max,
  quality ≥ Q_min and a $ budget.
- **Coverage:** Edge ✘, Split: PP inside the cluster only. **Joint ✔.** Act.:
  intra-cluster PP communication is profiled.
- **Different from ours:** datacenter only and two models. Reports up to 157% better
  at the same budget, or 15–61% cheaper.

### ECO-LLM: Orchestration for Domain-specific Edge-Cloud Language Models — F+V
- **Venue / year:** arXiv 2507.09003 (v1 Jul 2025, v2 21 Jun 2026), no venue.
  Patidar et al., CMU and Microsoft Research. https://arxiv.org/abs/2507.09003
- **Setting:** edge devices plus cloud APIs, in smart-home and smart-car assistant scenarios.
- **Decision variables:** per-query **resolution path** (preprocessing, retrieval,
  context, model), over 200–300 candidate paths.
- **Objective:** maximise accuracy s.t. TTFT ≤ L_max and $ ≤ C_max.
- **Method:** offline query clustering plus Pareto path selection (the "Emulator");
  online prototype-encoder nearest-neighbour lookup (the "Runtime").
- **Hardware:** SmolLM2, Llama-3.2-3B and Phi-4 on Jetson Orin Nano, M1/M4 and
  A4500; GPT-4.1 family in the cloud.
- **Coverage:** Edge ✔, Split ✘, Remote ✔. Joint: model + pipeline, not placement.
  Act. ✘. No network or energy model.
- **Different from ours:** **closest edge-cloud routing prior art, and it already
  uses a cluster/prototype table.** It has no SPLIT and no network state. If our
  system drops SPLIT, the remaining contribution is close to ECO-LLM plus an
  energy term.

### Cascadia — F
- **Venue / year:** ICLR 2026 poster. https://arxiv.org/abs/2506.04203
- **Decision variables:** bi-level. An MILP chooses the GPU and parallelism
  allocation; an outer search chooses cascade thresholds.
- **Objective:** quality/throughput under a p95 SLO.
- **Hardware:** 4×8 H100.
- **Coverage:** Edge ✘, Split ✘. Joint ✔ (cascade + allocation).
- **Different from ours:** datacenter only. It is the cascade-serving reference.

### Fast Heterogeneous Serving (arXiv 2604.07472, Apr 2026) — F
- **URL:** https://arxiv.org/abs/2604.07472. Simulation only.
- **Decision variables:** an MILP over GPU tiers, TP/PP, placement, and **routing
  fractions per query type**.
- **Objective:** cost under per-type error and latency SLOs.
- **Coverage:** Edge ✘, Split ✘. **Joint ✔.**
- **Different from ours:** this is structurally our "task → model table +
  allocation", in the datacenter and simulated. **It pre-empts any claim that a
  task-typed table jointly optimised with placement is new in itself.**

### HW-Router (arXiv 2608.14575, Jun 2026) — F
- **URL:** https://arxiv.org/abs/2608.14575
- **Decision variables:** per-query (model, GPU) choice from live queue and KV-cache
  signals. Placement is fixed.
- **Hardware:** 2×H100.
- **Coverage:** Edge ✘, Split ✘. Joint: routing with live state, no placement.
- **Different from ours:** datacenter, no network. It is the "live-state-aware router" baseline idea.

### Splitwise: Collaborative Edge–Cloud Inference for LLMs via Lyapunov-Assisted DRL — F
- **Venue / year:** IEEE/ACM UCC 2025.
  [DOI 10.1145/3773274.3774267](https://dl.acm.org/doi/10.1145/3773274.3774267),
  https://arxiv.org/abs/2512.23310
- **Decision variables:** placement of attention heads and FFN blocks on edge or
  cloud, for **one** model, chosen by Lyapunov + DRL under time-varying bandwidth B(t).
- **Hardware:** Jetson Orin NX, Galaxy S23 and RPi5 at the edge; AWS p4d (8×A100) in
  the cloud; tc links from 10 to 100 Mbps.
- **Coverage:** Edge ✔, **Split ✔ (sub-layer)**, Remote ✔. Joint ✘ (no model
  choice). **Act. ✔.**
- **Results:** claims 1.4–2.8× lower latency than cloud-only; up to about 4% accuracy
  loss from quantising activations at the boundary.
- **Caveat:** the reported 87 ms full-system latency looks implausible, and there is
  no explicit decode or KV model. It is the **only** paper claiming split beats
  cloud, so treat it with caution. E0 adjudicates this conflict.
- **Different from ours:** single model, no quality or utility trade-off, no task layer.

### Cloud, Edge, or Split? (drone VLM; arXiv 2609.25415, iEdge 2026) — F
- **URL:** https://arxiv.org/abs/2609.25415
- **Setting:** SmolVLM-256M; Jetson vs A6000; replayed LTE trace. The **cleanest measured
  three-way comparison.**
- **Results:**

  | Bandwidth | Edge | Cloud | Split |
  |---|---|---|---|
  | 2.1 Mbps | **2.77 s** | 3.87 s | 3.59 s |
  | 43.5 Mbps | 2.73 s | **0.83 s** | 2.19 s |

  Split never wins on latency. It wins only on onboard energy (15 J vs 26 J) and memory.
- **Coverage:** Edge ✔, Split ✔, Remote ✔. Joint ✘ (one model). Act. ✔.
- **Different from ours:** one tiny model; no model choice. **It is direct evidence for
  "Split is a constraint fallback".**

### In-Browser Split Inference (IEEE Access 14, 2026) — F
- **URL:** [DOI 10.1109/ACCESS.2026.3720562](https://doi.org/10.1109/ACCESS.2026.3720562)
- **Setting:** a WebGPU client runs layers 0..k−1; the server is an RTX 3060.
  Models: SmolLM2-1.7B and Phi-3.5-mini; 4G/5G/WiFi links.
- **Results:**
  - **Per-token network time is independent of k** (5G: 315 / 326 / 314 ms at k = 0 / 16 / 32).
  - For a weak client the best k is about 0, i.e. effectively remote.
  - Local-vs-offload crossover at RTT ≈ 60 ms (SmolLM2) and ≈ 150 ms (Phi-3.5).
  - Per-channel INT8 at the cut costs 0–7% perplexity; per-tensor INT8 is catastrophic.
- **Coverage:** Edge ✔, Split ✔ (layer), Remote ✔. Joint ✘. Act. ✔.
- **Different from ours:** single model per run. **Its rule "offload iff profiled
  RTT-term > local throughput" is a strong, cheap baseline.**

### Cunningham (arXiv 2602.16760) — F
- **URL:** https://arxiv.org/abs/2602.16760
- **Setting:** U-split. Embedding, first/last layers and head on a local RTX 3090;
  middle layers on a cloud A100 or 4090. Mistral-7B and NeMo-12B; RTT ≈ 80 ms.
- **Results:**

  | Setup | tok/s |
  |---|---|
  | Local only | 39 |
  | Split, sequential | 11 |
  | Split, with lookahead | 13–17 |
  | Cloud API | 30–60 |

  - 64% of per-token time is network RTT.
  - **Output is token-identical with fp16 activations under greedy decoding.**
  - An inversion attack recovers about 59% of tokens at a 2-layer cut and about 35% at 8 layers.
- **Coverage:** Edge ✔, Split ✔, Remote ✔. Joint ✘. Act. ✔.
- **Different from ours:** it justifies split only by privacy. **It supplies E0's
  quality-equivalence protocol.**

### EdgeShard — F (venue per subagent)
- **URL:** https://arxiv.org/abs/2405.14371. The arXiv listing says "under review";
  the subagent reports IEEE IoT-J 2025, which is unverified.
- **Decision variables:** device selection plus layer partition, by dynamic programming.
- **Hardware:** 12 AGX Orin + 2 Orin NX, with an RTX 3090 as the "cloud". Llama-2 7B/13B/70B.
- **Results:** at 1 Mbps the optimum for 7B is edge-solo. For 13B/70B, edge-only runs
  out of memory, so splitting is the **only** option. Cloud-only was excluded "for privacy".
- **Coverage:** Edge ✔, Split ✔, Remote: partial. Joint ✘. Act. ✔.

### HAT (arXiv 2503.18989) — F
- **URL:** https://arxiv.org/abs/2503.18989
- **Setting:** U-shaped split plus a device-side SLM drafter (speculative decoding).
  30 Jetsons + 8×A6000.
- **Result:** a **plain U-split is slower than cloud on TTFT and on
  time-between-tokens.** At a 2k-token prompt, TTFT is 3.57 s, 89.6% of it communication.
- **Coverage:** Edge ✔, Split ✔, Remote ✔. Joint ✘ (fixed architecture). Act. ✔.

### Edge model choice with EDGE/REMOTE on real hardware (one record each)

| Paper | URL | Decision variables / objective | Hardware | E/S/R | Joint | Act. | Gap vs ours |
|---|---|---|---|---|---|---|---|
| ConsRoute (2603.21237) — F | arxiv.org/abs/2603.21237 | Device 1.7B / edge 14B / cloud 32B tier from the prefill hidden state; per-cluster thresholds tuned by BO. Goal: ≥95% of cloud quality | RTX 3050 / A6000 / 2×A6000 | ✔/✘/✔ | routing only | ✘ (network profiles are test conditions, not inputs) | no split; network not a decision input |
| CR² (2605.12001) — F | arxiv.org/abs/2605.12001 | On-device gate, then edge selection over Qwen3-4B/8B/14B; cost = 0.5·latency + 0.5·energy | Orin AGX, 4070Ti/4090/A40; analytical wireless | ✔/✘/✔ | routing only | ✘ | no split; Shannon-model link |
| Yu, Goudarzi, Toosi (2507.15553) — F | arxiv.org/abs/2507.15553 | NSGA-II offline → **runtime lookup table**; placement fixed | CPU edge Qwen2.5-1.5B; A40 cloud gemma3-27B | ✔/✘/✔ | ✘ | ✘ | no split; already an offline-table design |
| TMO (2502.11007) — F | arxiv.org/abs/2502.11007 | RL per turn, Phi-3-mini vs GPT-4o, under latency and $ budgets | Edge latency *modelled* from TX2 FLOPs | ✔/✘/✔ | ✘ | ✘ | modelled, not measured |
| PRISM (2511.22788) — F | arxiv.org/abs/2511.22788 | Privacy-gated edge / cloud / "collaboration" (perturbed text) | RTX 3070 laptop, llama.cpp | ✔/~/✔ | ✘ | ✘ | the "split" is text exchange, not activations |
| HybridInfer (2609.30270) — F | arxiv.org/abs/2609.30270 | Tabular Q-learning over device / edge / cloud (GPT-4o), 15 thermal×complexity states | Galaxy S25+ | ✔/✘/✔ | ✘ | ✘ | no split |
| Unified AI Gateway (2609.06940, Huawei) — F | arxiv.org/abs/2609.06940 | Per-request (model, site ∈ end/edge/cloud, KV action) | **analytical** (DistServe A100 coefficients) | ✔/~(PD)/✔ | ✔ (model + site) | ✔ (KV) | **nearest formulation**, but analytical and PD-split, not layer split, no measurements |
| To Offload or Not (2504.15162) — F | arxiv.org/abs/2504.15162 | Local vs offload by bandwidth and load | Jetson clients; A2/4070 servers; tc 2–50 Mbps | ✔/✘/✔ | ✘ | ✘ | offloading pays off above ~5–15 Mbps; load also flips the decision |
| Edge-cloud speculative decoding (2505.21594, TMLR 2025) — F | arxiv.org/abs/2505.21594 | Jetson draft, A100 verify | Jetson + A100 | ✔/~/✔ | ✘ | ✔ | 1.35× vs cloud autoregressive decoding, but some pairs are 0.42–0.69× slower |
| RAC (2608.04991) — F | arxiv.org/abs/2608.04991 | Activation compression on a head/middle/tail split | 2×3090 local; A800 cloud | ✔/✔/✘ | ✘ | ✔ | no cloud-only baseline; INT4 is catastrophic, RAC stays within ±2.5 points |
| Adaptive Split Computing (2511.04002) — F | arxiv.org/abs/2511.04002 | Split layer, bit-widths, sequence length, KV vs hidden-state transfer | Xavier NX + A6000; simulated channel | ✔/✔/✘ | ✘ | ✔ | naive quantisation: HellaSwag 77.3 → 45.3; outlier-aware: 77.1 |

### Abstract / metadata only (do not make central)
- Lyra, INFOCOM 2026 ([DOI](https://doi.org/10.1109/INFOCOM59046.2026.11571307)): Lyapunov online SLM/LLM routing.
- LSCI, IEEE TMC 25(2), DOI 10.1109/TMC.2025.3608303: SLM caching plus offloading, numerical results only.
- EC-LLM, IEEE IoT-J 2026: an edge→cloud cascade, *not* split.
- Others: DIO-LLMs (ICC'25, simulated), HybridFlow (ICML 2026, sub-task DAG edge/cloud),
  QLMIO 2606.15210, GAR 2605.11603 (CO₂ routing), DynamoLLM (HPCA'25), Hyperion
  2511.14450, T2DRL 2501.14205, Speculation at a Distance 2606.25091 (analytical: an
  edge draft pays off only below ~50–60 ms RTT).
- Not found: "DABO (IEEE Access 2026)". Do not cite.
- 2512.01039 (joint partitioning/placement of foundation models) is a vision paper with
  "expected KPIs", not measurements.

---

## 3. Coverage matrix (the novelty test)

| Capability | Datacenter joint (RouterWise, BOute, Cascadia, 2604.07472) | Edge routing (ECO-LLM, ConsRoute, CR², 2507.15553) | Single-model split (Splitwise, EdgeShard, HAT, Cunningham, In-Browser) | Mix-or-Split | Unified AI Gateway | **Ours (target)** |
|---|---|---|---|---|---|---|
| Quality-based model choice | ✔ | ✔ | ✘ | ✘ | ✔ | ✔ (task table) |
| EDGE device | ✘ | ✔ | ✔ | edge *server* | ✔ | ✔ |
| Layer SPLIT | ✘ | ✘ | ✔ | ✘ (PD) | ✘ (PD) | ✔ *if E0 passes* |
| REMOTE | n/a | ✔ | ✔ / partial | ✔ | ✔ | ✔ |
| Activation/KV transfer cost | ✘ | ✘ | ✔ | ✔ | ✔ | ✔ |
| Live link state as a decision input | ✘ | mostly ✘ | Splitwise only | ✔ | ✔ | ✔ |
| Energy | ✘ | CR² | Splitwise, drone | ✘ | partial | ✔ |
| Measured on real hardware | ✔ | ✔ | ✔ | ✔ | ✘ | ✔ |
| Evidence that a task table suffices for the semantic layer | ✘ | ECO-LLM assumes it | n/a | n/a | n/a | ✔ (E1–E3) |

**Exact gap:** no measured system jointly chooses the **model** (by task
utility) and the **execution path**, where the path includes a **layer split of a model
that exceeds edge memory**, using measured profiles and live link state. Each
ingredient exists separately. The gap holds **only as the combination**, and only if
SPLIT is ever chosen.

---

## 4. What measured split studies say about SPLIT's regime

| Study | Split vs Remote (latency) | Split vs Edge | When Split is chosen |
|---|---|---|---|
| Drone VLM 2609.25415 | slower at 43–65 Mbps | slower at 2.1 Mbps | never on latency; only on energy and memory |
| Cunningham 2602.16760 | 11–17 vs 30–60 tok/s | slower (39 tok/s local) | privacy |
| HAT 2503.18989 | slower on TTFT and TBT | — | only with speculative-decoding add-ons |
| In-Browser 2026 | per-token net time independent of k; best k ≈ 0 | — | weak client + low RTT, which is effectively remote |
| EdgeShard | (cloud excluded) | edge-solo wins at 1 Mbps for 7B | model does not fit on the edge (13B/70B) |
| Mix-or-Split (PD split) | worst SLO (66.7%) | worse | cloud return path degraded (+40 ms/token) |
| Splitwise UCC'25 | **claims 1.4–2.8× faster** | — | low bandwidth; methodological concerns noted |

Mechanism (consistent with `evidence/split_bound.md`): decode is autoregressive,
so a layer split pays **one network round trip per generated token**. A REMOTE
stream pays RTT once and then streams. Bandwidth barely matters because activations
are about 2·d_model bytes per token, around 8–16 KB at fp16. **RTT × output length
is the killer.** With our cached output lengths (median 400–13,000 tokens,
`evidence/size_class_table.md`), a 20 ms RTT adds 8–260 s to a split generation.

Therefore SPLIT can only be *selected* when REMOTE is infeasible or degraded
(privacy, server capacity or queueing, a lossy downlink) **and** EDGE-only is infeasible
or too low in quality (memory, accuracy). This is a **constraint-driven fallback**,
not a latency optimisation. E0 must confirm or refute this on our hardware.

---

## 5. Threats to novelty, ranked

1. **Unified AI Gateway (2609.06940)** already writes down "model + site +
   KV/split action". Our difference is measurement on real hardware plus a layer
   split. If SPLIT drops out, the difference shrinks to "measured, not analytical".
2. **ECO-LLM** (cluster table + edge/cloud path selection under TTFT and $). If we drop
   SPLIT and the network dimension, we are ECO-LLM with an energy term.
3. **2604.07472 / RouterWise** (task-typed routing fractions + allocation). A
   "joint task table + placement" claim must state that the resources are a fixed
   edge plus a variable link, not provisionable GPUs.
4. **Mix-or-Split** (per-request mode from live state). A "dynamic network-aware
   mode selection" claim must add model choice and a quality term, or it duplicates
   Mix-or-Split.

## 6. Implications carried into PROBLEM-FORMULATION.md

- The **semantic layer is not a contribution** (E1–E3 plus the literature). It is a
  lookup whose sufficiency we *evidence*. That evidence is a differentiator against
  ECO-LLM, which assumes clustering suffices.
- Because utility is a task-level lookup and the action set is small (a few models × 3
  paths × a few split depths), **the online "optimizer" is an enumerable argmin**. Any
  contribution must come from the *measured coupling* (which model is feasible on
  which path at what cost under which link state), not from optimisation-algorithm
  novelty.
- Whether the formulation is novel at all hinges on **SPLIT being selected in some
  measured regime**. If E0 fails, the honest fallback is a measurement/analysis
  paper ("task lookup + EDGE/REMOTE is sufficient; split never pays"), and its
  novelty must be argued against ECO-LLM and 2507.15553.
