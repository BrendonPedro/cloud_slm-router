# 06 — Systems-venue prior-art map (v3)

*Deliverable 06 of `MICROENCODER_HARDENING_BRIEF.md` §27 (the file the brief's
§9 calls `systems-prior-art-map.md`). Prepared 2026-10-04 (gnhf run
`microencoder-hardeni-d272f9`, iterations 5–6). Resolves findings RF-H4 and
supplies the evidence base for RF-I1 (`12-novelty-v3.md`) of
`00-review-findings.md`.*

**Purpose.** v2's novelty search was arXiv/ACL-centric (RF-H4). This file
records a targeted search of ACM, IEEE, USENIX and MLSys systems venues whose
explicit goal was to **invalidate** the proposed novelty (brief §9), not to
collect support. Routing-paper body readings (RouteLLM, HyDRA, ConsRoute, …)
are in `05-full-routing-prior-art.md` and are only summarised here.

---

## 0. Search protocol and limits

* **Date / tools.** 2026-10-04. Three parallel search clusters (below) plus
  two follow-up venue sweeps in iteration 6. Bibliographic identity was
  checked through Crossref, Semantic Scholar, OpenAlex, USENIX program pages
  and arXiv. **dblp, ACM DL full-text and OpenReview were unreachable or
  returned 403** from this machine, so ACM/IEEE proceedings bodies were read
  only when an arXiv / author / tech-report version existed.
* **Clusters and query families** (brief §9 combinations):
  1. *DNN partitioning / split computing* — "dynamic split point selection",
     "adaptive partitioning", "bandwidth-aware split inference",
     "latency-aware DNN partitioning", "activation-transfer-aware inference",
     "split neural network routing".
  2. *Edge–cloud LLM collaboration* — "collaborative LLM inference",
     "edge-cloud LLM inference", "split LLM routing", "SLM–LLM collaboration",
     "query-aware model offloading".
  3. *Model selection + network state* — "model routing with communication
     cost", "model selection plus network state", "semantic routing with
     network cost", "quality-cost routing", "learned edge/cloud routing".
  4. *Iteration-6 venue sweeps* — MLSys proceedings (`proceedings.mlsys.org`,
     `mlsys.org` domain-restricted), SenSys / CoNEXT / ICDCS keyword sweeps.
* **Venues for which at least one relevant hit was identified:** ASPLOS,
  MobiCom, MobiSys (+EdgeFM workshop), SIGCOMM (+MECOMM workshop), EuroSys,
  SoCC, KDD, INFOCOM, IEEE TMC, IEEE TWC, IEEE TSC, IEEE IoT-J, IEEE Network,
  IEEE COMST, ICC / Globecom / ICCC workshops, ICMLCN, ICDCS, ICWS, ICPADS,
  ISLPED, ICASSP, ACM TECS, ACM CSUR, IEEE/ACM UCC, USENIX NSDI, USENIX ATC,
  ICML (PMLR), FITEE.
* **Venues searched with no relevant hit:** IEEE JSAC (no hit across all three
  clusters), MLSys (domain-restricted query returned no MLSys-hosted result),
  SenSys and CoNEXT (keyword sweeps returned only arXiv / other-venue papers),
  IMC (not relevant to the query families; not pursued further).
* **Inspection levels** (brief §29): **BODY** = method/system-model sections
  and cost equations read from an accessible full text → `[VERIFIED-BODY]` for
  what the paper *does*; **ABS** = abstract / publisher landing page only;
  **META** = bibliographic identity only (`[VERIFIED-META]`). Table cells for
  ABS/META rows are our reading of the abstract and must not be used for a
  load-bearing manuscript claim until upgraded.
* **What this search cannot establish.** It is bounded by the query families,
  the venues above, and the reachability limits listed. **Absence of a hit is
  bounded-search evidence, never `[VERIFIED-BODY]`** (brief §29). Not checked:
  VideoStorm, Mainstream, AdaInf, Online Cascade Learning, RouterBench; MCIA,
  TMO, Splitwise-UCC learned-policy details beyond abstract/body noted below;
  LLMCad's MobiCom venue (unconfirmed).

---

## 1. Master table (brief §9)

Column semantics:
**Routing?** chooses among different models/executors per request.
**Query-aware?** decision uses request content (Y), token-level confidence
(tok), task type / deadline only (partial), or nothing about content (N).
**Model selection?** chooses which network/LLM runs. **Split depth?** chooses a
layer/partition point. **Measured act. bytes?** cost uses per-split activation
size. **Live net?** decision uses current bandwidth/RTT/channel. **Learned
utility?** a learned predictor of quality/utility (not just a learned latency
model or a learned scheduling policy). **Edge?** targets edge/device
deployment.

### 1.1 DNN partitioning and split computing (non-LLM unless noted)

| Work | Venue / ID | Insp. | Routing? | Query-aware? | Model selection? | Split depth? | Measured act. bytes? | Live net? | Learned utility? | Edge? | Closest overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Neurosurgeon (Kang et al.) | ASPLOS 2017, 10.1145/3037697.3037698 | META | N | N | N | Y | Y | Y (bw, server load) | N (learned *latency* regressors only) | Y | Runtime split-point choice under live bandwidth — pre-empts "bandwidth-aware split" outright |
| Edge Intelligence co-inference (Li, Zhou, Chen) | MECOMM@SIGCOMM 2018, 10.1145/3229556.3229562 | META | partial | N | partial | Y | Y | static | N | Y | Precursor of Edgent |
| Edgent (Li, Zeng, Zhou, Chen) | IEEE TWC 2020, 10.1109/twc.2019.2946140; arXiv 1910.05316 | **BODY** (§III–IV) | partial (exit branches of one DNN) | N (latency deadline) | partial (model right-sizing by early exit) | Y | Y (§IV-B data size D / bandwidth B) | Y (BOCPD bandwidth states; offline config map §IV-C, §V-C) | N | Y | **Top threat (non-LLM):** joint model-size × split choice under live bandwidth. Not content-aware; "models" are exit branches of one network; accuracy is a static per-branch constant |
| Boomerang (Zeng et al.) | IEEE Network 2019, 10.1109/MNET.001.1800506 | ABS | partial | N | partial | Y | Y | Y | N (DRL policy per abstract) | Y | Edgent + DRL |
| DADS (Hu et al.) | INFOCOM 2019, 10.1109/infocom.2019.8737614 | ABS | N | N | N | Y (min-cut) | Y | Y | N | Y | Split under network dynamics |
| JALAD (Li et al.) | ICPADS 2018, 10.1109/padsw.2018.8645013 | ABS | N | N | N | Y | Y (quantized) | partial | N (ILP) | Y | Accuracy-aware lossy split (quantized activations) |
| IONN (Jeong et al.) | SoCC 2018, 10.1145/3267809.3267828 | ABS | N | N | N | Y | Y | partial | N | Y | Partition offloading |
| BottleNet (Eshratifar et al.) | ISLPED 2019, 10.1109/islped.2019.8824955 | META | N | N | N | partial | Y (learned bottleneck) | N | N | Y | Lossy compressed activations |
| BottleNet++ (Shao, Zhang) | ICC Wksp 2020, 10.1109/iccworkshops49005.2020.9145068 | ABS | N | N | N | partial | Y | partial | N | Y | Lossy compressed activations over channel |
| SPINN (Laskaridis et al.) | MobiCom 2020, 10.1145/3372224.3419194; arXiv 2008.06402 | **BODY** (§3.2–3.6) | N | partial (per-sample early exit; split re-chosen on profiler drift §3.5) | N | Y | Y (8-bit + LZ4 compressed, §3.6) | Y (bw + RTT moving averages, §3.4) | N (analytic) | Y | **Top threat for the cost model:** prices compressed activation bytes with live bw/RTT. Single model; quantization makes the split **lossy** (relevant to `02`) |
| CLIO (Huang et al.) | MobiCom 2020, 10.1145/3372224.3419215 | ABS | N | N | partial | Y | Y | Y (wireless) | N | Y | Split vs wireless bandwidth |
| Auto-Split (Banitalebi-Dehkordi et al.) | KDD 2021, 10.1145/3447548.3467078 | ABS | N | N | N | Y (+ mixed precision) | Y | partial | N | Y | Split + activation precision |
| JointDNN (Eshratifar et al.) | IEEE TMC 2021, 10.1109/tmc.2019.2947893 | META | N | N | N | Y | Y | partial | N | Y | Split latency/energy |
| DynO (Almeida et al.) | ACM TECS 2022, 10.1145/3510831 | ABS | N | N | N | Y | Y | Y | N | Y | Runtime split + bytes |
| Dynamic Split Computing (Bakhtiarnia et al.) | ICASSP 2023, 10.1109/icassp49357.2023.10096914; arXiv 2205.11269 | ABS | N | N | N | Y | Y | Y (rate + load) | N | Y | Split from channel state |
| SplitEE (Bajpai et al.) | AIMLSystems 2023; arXiv 2309.09195 (DOI unconfirmed) | ABS | N | Y (per-sample exit) | N | Y | partial | N | partial (bandit) | Y | Learned per-sample split/exit |
| MCIA (Qi et al.) | ACM TECS 2024, 10.1145/3634704 | ABS | Y (compressed model versions) | partial (task type) | Y | Y | Y | Y (bw allocation) | unverified (DRL per snippet) | Y | Model version × partition × bandwidth; body unread |
| Split Computing & Early Exiting survey (Matsubara et al.) | ACM CSUR 2022, 10.1145/3527155 | META | survey | — | — | — | — | — | — | — | Taxonomy reference for `02` |

### 1.2 Model / variant selection under network or resource state

| Work | Venue / ID | Insp. | Routing? | Query-aware? | Model selection? | Split depth? | Measured act. bytes? | Live net? | Learned utility? | Edge? | Closest overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MCDNN (Han et al.) | MobiSys 2016, 10.1145/2906388.2906396 | **BODY** (UW tech-report version: Alg. 1, scheduler) | Y (model variants) | N (request type / frequency) | Y | partial (location ∈ {device, split, cloud}) | partial | partial (network/cloud budgets) | N (heuristic, profiled accuracy) | Y | **Pre-empts "model selection + placement under network cost"** for CNNs |
| DeepDecision (Ran et al.) | INFOCOM 2018, 10.1109/infocom.2018.8485905 | ABS | Y (local small vs remote large) | N | Y | N | N | Y (measured) | N | Y | Local-vs-remote model choice under measured network |
| Chameleon (Jiang et al.) | SIGCOMM 2018, 10.1145/3230543.3230574 | ABS | partial (configs) | partial (content dynamics) | partial | N | N | N | N | N | Content-adaptive configuration |
| AWStream (Zhang et al.) | SIGCOMM 2018, 10.1145/3230543.3230554 | ABS | N | N | N | N | N | Y (bw estimation) | partial | partial | Bandwidth-adaptive accuracy degradation |
| JCAB (Wang et al.) | INFOCOM 2020, 10.1109/infocom41043.2020.9155524 | ABS | partial | N | partial | N | N | Y | N | Y | Config + bandwidth allocation |
| Clipper (Crankshaw et al.) | USENIX NSDI 2017 | ABS | Y | partial | Y | N | N | N | partial (bandit selection) | N | Serving-side model selection |
| INFaaS (Romero et al.) | USENIX ATC 2021 | ABS | Y | partial (requirements) | Y | N | N | N | N | N | Variant selection from requirements |
| Cocktail (Gunasekaran et al.) | USENIX NSDI 2022 | ABS | Y | N | Y (ensembles) | N | N | N | partial | N | Cost-aware model ensembling |
| EdgeRL (Mounesan et al.) | arXiv 2410.12221 (venue unverified) | **BODY** (§II-B,C, Eq. 8) | Y (DNN versions) | N | Y | **Y — joint action a = (version, cut layer)** | Y (per-layer output size D) | N (battery, tx power, motion; no bw/RTT input) | partial (A2C policy, not a utility predictor) | Y | **Same model × split action shape as ours**, for CNNs; not content-aware |
| Infer-EDGE | arXiv 2501.18842 | META | Y | N | Y | Y | Y | partial | partial | Y | Overlaps EdgeRL |

### 1.3 Edge–cloud LLM / SLM collaboration and LLM routing with network cost

| Work | Venue / ID | Insp. | Routing? | Query-aware? | Model selection? | Split depth? | Measured act. bytes? | Live net? | Learned utility? | Edge? | Closest overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bao et al., "Dynamic Quality-Latency Aware Routing for LLM Inference in Wireless Edge-Device Networks" | IEEE/CIC ICCC Workshops 2025, 10.1109/icccworkshops67136.2025.11147210; arXiv 2508.11291 | **BODY** (§III, Eq. 6–12) | Y (Qwen2.5-3B device vs QwQ-32B edge) | Y | Y | N | N (token counts only) | partial (fixed B = 2·10⁷ tok/s + δ) | Y (BERT router adopted from RouteLLM) | Y | **Most threatening LLM work:** p̃ = p − α(T_edge − T_local), thresholded — our "utility minus cost" shape, binary actions only, no split |
| Chen et al., "Optimizing NetGPT via Routing-Based Synergy and Reinforcement Learning" | arXiv 2511.22217 (venue unverified) | **BODY** (§IV, Eq. 2, 5, 8, 28–29) | Y (7B edge / DeepSeek-V3.2 cloud) | Y (reward-model score) | Y | N | N (payload via transmit time) | **Y** (τ = τ₀ − α·RTT + β·BW, Eq. 28; emulated regimes + Gauss–Markov) | Y (+ ~2.9k-param PolicyNet MLP) | Y | **High threat:** learned edge score + network-adaptive threshold; proves the optimal threshold is monotone in BW/RTT. Two models, no split |
| Splitwise (Younesi et al.), "Collaborative Edge–Cloud Inference for LLMs via Lyapunov-Assisted DRL" | IEEE/ACM UCC 2025, 10.1145/3773274.3774267; arXiv 2512.23310 | **BODY** (state/action, Δacc) | N | N | N | Y (attention head / FFN sub-layer) | Y (modelled D_k(π)) | Y (B(t), moving average, variance) | partial (DRL policy; accuracy loss = fixed quantization proxy) | Y | Learned LLM partitioning under live bandwidth; single model, not query-aware |
| Chen et al., adaptive layer splitting for wireless LLM inference (MBRL) | FITEE 2025, 10.1631/fitee.2400468; arXiv 2406.02616 | **BODY** (§II–V) | N | N (state = channel noise/fading + split) | N | Y (±1/0 moves) | **N — tensor size assumed constant across splits (§II-B)** | Y (simulated, §III-A) | partial (reward −(PPL + λ·FLOPs)) | Y | Learned LLM split under channel state; explicitly does not model depth-dependent bytes |
| R. Zhang et al., "Compact LLM Deployment and World Model Assisted Offloading in MEC" | arXiv 2602.13628 (venue unverified) | **BODY** (system model, state, reward) | Y (local compact vs edge full) | N | partial (offload ratio) | N | N | Y (channel gains) | partial (WM-PPO) | Y | Multi-user per-slot offloading |
| Hao et al., "Hybrid SLM and LLM for Edge-Cloud Collaborative Inference" | EdgeFM@MobiSys 2024, 10.1145/3662006.3662067 | ABS | Y | tok | Y | N (argues partitioning unsuitable) | N | N | partial | Y | SLM↔LLM token-level collaboration |
| CE-CoLLM (Jin, Wu) | IEEE ICWS 2025, 10.1109/icws67624.2025.00046; arXiv 2411.02829 | ABS | N | tok (per-token exit confidence) | N | partial (fixed split + early exit) | Y | partial (standalone mode on unstable network) | N | Y | **Nearest to "EDGE vs SPLIT of one LLM"**; no separate SLM, no learned query utility |
| EdgeShard (Zhang et al.) | IEEE IoT-J 12(10) 2025, 10.1109/jiot.2024.3524255 | ABS | N | N | N (device selection) | Y (DP) | Y | partial (profiled) | N | Y | Joint device selection + LLM partition |
| Galaxy (Ye et al.) | INFOCOM 2024, 10.1109/infocom52122.2024.10621342 | ABS | N | N | N | partial (hybrid parallelism) | Y | partial | N | Y | Transformer across edge devices |
| Jupiter (Ye et al.) | INFOCOM 2025, 10.1109/infocom55648.2025.11044734 | ABS | N | N | N | Y (pipeline) | Y | partial | N | Y | Collaborative generative-LLM inference across edge devices |
| Partitioned collaborative inference via evolutionary RL | IEEE ICDCS 2025 (identity from search snippet only) | META-unconfirmed | — | — | — | Y (per title) | — | — | — | Y | ICDCS hit; do not cite until identity is confirmed |
| Lyu et al., "The Larger the Merrier? …" | arXiv 2505.09214 | ABS | N | N | partial (pruning ratio) | Y | Y (rate–distortion) | partial | N | Y | Model size × split, offline |
| Tabi (Wang et al.) | EuroSys 2023, 10.1145/3552326.3587438 | ABS | Y | Y (calibrated confidence) | Y | N | N | N | partial | N (datacenter) | Confidence-based small→large escalation |
| Oh et al., U-HLM | IEEE ICMLCN 2025, 10.1109/icmlcn64995.2025.11140540; arXiv 2412.12687 | ABS | Y | tok (uncertainty) | partial | N | N | partial (uplink-aware) | N | Y | Uncertainty-gated SLM→LLM offloading |
| Kim et al., "Accuracy-Delay Trade-Off in LLM Offloading via Token-Level Uncertainty" | Globecom Wksp 2025, 10.1109/gcwkshps68340.2025.11591100 | ABS | Y | tok | Y | N | N | partial | N (greedy) | Y | Accuracy–delay offloading |
| Yang et al., "QoS-Aware LLM Routing for Edge Computing With Multiple Experts" | IEEE TMC 2025, 10.1109/tmc.2025.3590969; arXiv 2508.00234 | ABS | Y | partial | Y | N | N | partial | partial (DRL) | Y | DRL routing among edge LLM experts |
| Xu et al., "Joint Inference Offloading and Model Caching for SLM and LLM Collaboration" | IEEE TMC 2025, 10.1109/tmc.2025.3608303 | ABS | Y | unverified | Y | N | N | partial | partial | Y | SLM/LLM offloading + caching |
| Zhou et al., delay–accuracy trade-off for LLM–SLM in vehicular edge | IEEE IoT-J 2026, 10.1109/jiot.2026.3695122 | ABS | Y | unverified | Y | N | N | partial | N (PSO) | Y | Delay–accuracy LLM/SLM allocation |
| Li, Guo et al., cloud-edge scheduling of unpredictable LLM requests (combinatorial bandit) | IEEE TSC 2025, 10.1109/TSC.2025.3611379 | ABS | partial | Y (prompt → job time) | partial | N | N | N | partial (neural UCB on job time) | Y | Prompt-aware scheduling |
| EdgeLLM (Xu et al.) | IEEE TMC 2025, 10.1109/tmc.2024.3513457 | META | N | tok | partial | N | N | N | N | Y | On-device LLM with verification; LLMCad MobiCom venue unconfirmed |
| Fang et al., "Bridging On-Device and Cloud LLMs for Collaborative Reasoning" | ICML 2026, PMLR v306 (proceedings.mlr.press/v306/fang26d); arXiv 2509.24050 | ABS (search snippet + PMLR landing listing) | Y (on-device vs cloud) | Y (self-routing learned in RL post-training) | Y | N | N | N | Y (routing learned inside the on-device LLM) | Y | Self-routing baseline candidate for `11` (hidden-state family) |
| PerLLM | arXiv 2405.14636 (venue unverified) | ABS | Y | partial | Y | N | N | partial (bw constraint) | partial (CMAB-UCB) | Y (edge servers) | Bandit scheduling with bandwidth |
| TMO (Yuan et al.) | arXiv 2502.11007 (MobiHoc 2025 per arXiv comment only) | ABS | Y | Y | Y | N | N | unverified | partial (RL) | Y | Per-query local/cloud learned offloading |
| HybridFlow | arXiv 2512.22137 (ICML 2026 per arXiv comment only) | ABS | Y | Y (subtask) | Y | N | N | N (budgets) | Y (benefit–cost) | Y | Learned benefit–cost edge/cloud reasoning |
| ConsRoute | arXiv 2603.21237 | **BODY** (see `05` §1.5) | Y | Y | Y (device/edge/cloud tiers) | N | N | N | Y | Y | Tiered LLM routing; re-tunes thresholds, no network input |
| Hybrid LLM (Ding et al.) | ICLR 2024; arXiv 2404.14618 | **BODY** (see `05` §1.6) | Y | Y | Y | N | N | N | Y | partial | Query-aware small/large routing with a quality-gap threshold |
| FrugalGPT | arXiv 2305.05176 (TMLR 2024 unverified) | ABS | Y (cascade) | Y | Y | N | N | N (API price) | Y | N | Learned cascade under price |

Low-threat / not tabulated in detail: MoE² (2501.09410), SWARM-LLM
(2606.14711), PICE (2501.09367), CE-LSLM (2505.14085), Pro-Router
(2608.28726), BALANCE (2608.05926), INAR-VL (2605.18853), Yu–Goudarzi–Toosi
(2507.15553), HybridInfer (2609.30270), LIME (2512.21835),
EdgeMoE (TMC 2025, 10.1109/tmc.2025.3546466), LinguaLinked (ACL Demos 2024),
DiSCo (Findings ACL 2025). Splitwise (Patel et al., ISCA 2024) is datacenter
prefill/decode phase splitting and is **out of scope** despite the name clash
with Younesi et al.

Surveys used for taxonomy only: Matsubara et al. ACM CSUR 2022
(10.1145/3527155); Qu et al. IEEE COMST 2025 (10.1109/comst.2025.3527641);
Li et al. arXiv 2507.16731 (BODY of taxonomy: separates *task assignment*
from *task division/partitioning* and lists no work that unifies them);
ACM CSUR 2026 network-edge LLM inference survey (10.1145/3809166, META).

**Do not cite:** CoSense-LLM (arXiv 2510.19670) — withdrawn by arXiv.

---

## 2. Axis-by-axis pre-emption (attempted invalidation)

Each row asks: *is this component of our method already published?*

| Our component | Pre-empted? | Strongest prior work | Consequence |
|---|---|---|---|
| Choosing a split point at runtime from live bandwidth/RTT | **Yes, fully** | Neurosurgeon (ASPLOS'17), DADS (INFOCOM'19), SPINN (MobiCom'20), Edgent (TWC'20) | Cannot be claimed. Cite as foundation of the cost side. |
| Pricing activation bytes per split with live bw/RTT | **Yes** (non-LLM) | SPINN §3.4–3.6, Edgent §IV-B, Neurosurgeon | Our cost model is an *application* of this to LLM layers, not a contribution. |
| Learned LLM split under channel state | **Yes** | Chen FITEE 2025; Splitwise UCC 2025 | Cannot claim "learned/adaptive LLM splitting". |
| Joint model-variant × placement/split under network cost | **Yes** (CNN) | MCDNN (MobiSys'16), Edgent, EdgeRL, MCIA | The *action-space shape* (model × split) is not new. |
| Per-query, content-aware LLM routing (edge SLM vs strong) | **Yes** | RouteLLM, Hybrid LLM, ConsRoute (`05`); Tabi, TMO, Fang ICML'26 | Not new on its own. |
| Utility-minus-latency LLM routing with network term | **Yes, binary case** | Bao ICCC-W'25 (Eq. 11–12); NetGPT-routing arXiv 2511.22217 (Eq. 28) | Our decision rule's *form* is pre-empted; we must cite both and present ours as a generalisation to a multi-action set. |
| Split of an LLM as an alternative to an edge-only path | **Partially** | CE-CoLLM (ICWS'25), Edgent-style exits | Exists for *one* LLM with early exit; not alongside a separate edge SLM and a strong model in a learned per-query router. |
| Depth-dependent measured activation bytes in an LLM router's cost | **Not found** | Chen FITEE assumes constant tensor size (§II-B); Bao/NetGPT use transmit time / tokens only | Narrow, bounded-search candidate. |
| Learned per-query semantic utility over {EDGE SLM, SPLIT(d) of another LLM, STRONG} priced with live network state | **Not found (conjunction)** | Closest: Bao, NetGPT-routing, EdgeRL, Edgent, SPINN, CE-CoLLM | Only surviving novelty candidate; see §3. |
| Micro-encoder router + KD | Not a systems-venue question | See `05`, `03`, `04` | Engineering/ML-side; no systems claim. |

---

## 3. What survives, and the allowed wording

**Surviving candidate (bounded-search, `[OPEN]` until experiments).** A
per-query router whose *learned* component predicts query-conditioned model
utility from content, and whose runtime optimiser chooses among an edge SLM,
**split execution of a larger LLM at depth d**, and a strong remote model,
pricing each action with **measured, depth-dependent activation bytes** and
**live bandwidth/RTT**. Every individual axis is pre-empted (§2); only the
conjunction was not found within §0's scope.

**This is an integration contribution, not a component contribution.** The
manuscript must say so and must cite, at minimum: Neurosurgeon, SPINN, Edgent
(split + live network); MCDNN and EdgeRL (model × split action shape); Bao
et al. and NetGPT-routing (utility-minus-network-cost LLM routing); Chen FITEE
and Splitwise-UCC (learned LLM splitting); CE-CoLLM (edge vs split of one
LLM); RouteLLM / Hybrid LLM (query-aware routing, from `05`).

**Allowed wording (feeds `12-novelty-v3.md`):**

> "We propose a router that combines query-conditioned model-utility
> prediction with runtime costs for edge, split and remote execution. Prior
> systems choose split points under live network conditions [Neurosurgeon,
> SPINN, Edgent], select model variants and placements under network budgets
> [MCDNN, EdgeRL], or route queries between an on-device and a remote LLM with
> a latency- or network-aware threshold [Bao et al., NetGPT routing]. To our
> knowledge — based on a search of ACM, IEEE, USENIX and ML venues documented
> in our supplementary material — these have not been combined into a single
> per-query decision over edge, split-depth and remote actions with measured
> activation costs."

**Banned wording:** "the first router to …"; "first to treat Split(d) as a
routable action" (EdgeRL and Edgent already treat split as part of a joint
action); "novel network-aware LLM routing" (Bao, NetGPT); "first to include
activation transfer cost" (SPINN, Neurosurgeon). `[REJECT]`

**Strength of the surviving claim.** Weak-to-moderate. A reviewer who knows
Edgent + Bao/NetGPT can call the conjunction incremental. The paper's value
must therefore rest on **measured evidence** (E0 split equivalence, E6
network sweep without router retraining, E7 real split execution) rather than
on priority. This supports using the **Conservative** contribution statement
before experiments (`12`).

---

## 4. Consequences for other v3 deliverables

* **`01` / `09` (Issue A, C).** NetGPT-routing's monotone-threshold result
  (Eq. 28–29) is published support for keeping semantic utility separate from
  network-dependent decision thresholds: the network enters as a threshold
  shift, not a retrained scorer. Cite it as precedent, not as proof for our
  multi-action case. EdgeRL is the counter-design (state-integrated joint
  policy) and is the natural "integrated" comparison in `09`.
* **`02` (Issue D).** SPINN (8-bit + LZ4), JALAD (quantized), BottleNet/++ and
  Auto-Split (mixed precision) are published examples of **lossy** splits; the
  exact branch of `02` must state that it assumes none of these transforms.
  Chen FITEE's constant-tensor-size assumption shows why bytes must be
  measured per depth (E0/E7).
* **`11` (baselines).** Candidate systems baselines: Bao-style thresholded
  score − α·ΔT (re-implementable from Eq. 11–12, binary); NetGPT-style
  network-adaptive threshold (Eq. 28); Neurosurgeon/SPINN-style
  latency-optimal split ignoring query content ("Always Split at best d");
  Fang ICML'26 as a self-routing reference if code is released.
* **`12` (novelty).** Uses §3 verbatim as its evidence base; no "first".
* **`17` / bib.** Only BODY or Crossref-confirmed META entries above may enter
  `method-references-v3.bib`. arXiv-only entries with "venue unverified" must
  be cited as arXiv preprints. The ICDCS 2025 snippet hit must not be cited
  until identity is confirmed.

---

## 5. Remaining gaps `[OPEN]`

1. Proceedings bodies behind ACM DL/IEEE Xplore (Neurosurgeon, DADS, MCIA,
   CLIO, Galaxy, Jupiter, EdgeShard) were not read; their cells are
   abstract-level. MCIA (model version × partition × bandwidth) is the
   highest-priority upgrade.
2. JSAC, MLSys, SenSys, CoNEXT returned no relevant hit; this is bounded
   evidence only and depends on search-engine coverage of those venues.
3. dblp was unreachable, so systematic per-venue table-of-contents scans were
   not possible; a manual dblp/ACM DL TOC scan of MobiCom/MobiSys/SenSys
   2023–2026 and INFOCOM 2024–2026 is recommended before submission.
4. VideoStorm, Mainstream, AdaInf, Online Cascade Learning, RouterBench not
   checked.
5. Venues stated only in arXiv comments (TMO → MobiHoc 2025; HybridFlow →
   ICML 2026) are unverified; Fang et al. ICML 2026 is confirmed via the PMLR
   v306 page found in the search, at META level.
