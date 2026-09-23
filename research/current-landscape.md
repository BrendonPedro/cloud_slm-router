# Deliverable 2 — Current landscape (chronological, through September 2026)

*Prepared 2026-09-23 (gnhf iteration 8). Subject: "Tiny-LM with Jacobi-Forced
Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs"
(`source/main-original.tex`, unchanged; SHA-256 06f5f9d7…07cf6).*

This review is chronological. It pulls together the sources verified in deliverables
3–8 and adds foundation and anchor sources checked this iteration: speculative,
multi-token and diffusion decoding, calibration and selective prediction, split
learning and partitioning origins, and industry routers. Raw copies of the new
sources are in `research/raw/landscape/`: arXiv abstract pages `abs_*.html`, the
extracted metadata in `abstracts.txt`, the PMLR v235 index, Crossref/OpenAlex JSON,
GitHub API records, vendor pages, and `fetch-log.txt` with UTC timestamps. Earlier
evidence stays in `research/raw/{prior-art,novelty,gap,jev}/`.

**Nothing listed here was reproduced or run by us.** Any number quoted is the
authors' or vendor's own claim.

---

## 0. Scope, tags and rules

**Areas** (objective §A–F): **A** LLM routing · **B** edge–cloud inference ·
**C** split LLMs · **D** fast/decision models, calibration, selective prediction ·
**E** Jacobi, speculative, multi-token and diffusion decoding · **F** systems and code.

**Evidence depth:**

| Tag | Meaning |
|---|---|
| **B** | Paper body read (in this project) |
| **A** | Abstract / arXiv metadata only |
| **T** | Title and bibliographic metadata only; no abstract was available to us |
| **V** | Vendor or official project documentation |
| **R** | Repository metadata (GitHub/HF API) |

**Venue verification.** The venue comes from the arXiv "Comments" field, the ACL
Anthology, the PMLR v235 index, Crossref, or OpenAlex, and the table cell names which
one. "pp" means preprint (no venue found). A venue that appears only in a repo README
is marked *(repo claim)*.

**Date convention.** Each row is dated by **first public appearance**: arXiv v1 date
if one exists, otherwise the publication date in Crossref. Peer-reviewed rows also
give the venue year, which can be later.

**Scope limitation.** This is a bounded review, not a systematic one. The searches
were arXiv/web-centric plus one Crossref sweep of IEEE/ACM venues (deliverable 8 §2).
IEEE Xplore and the ACM DL could not be queried directly. DBLP and the Semantic
Scholar search API refused requests from this environment (HTTP 429 / connection
closed) this iteration.

---

## 1. Peer-reviewed work (chronological)

| First public | Work | Venue (verification) | Area | Depth | What it establishes | Relevance to the manuscript [our analysis] |
|---|---|---|---|---|---|---|
| 2017-04 | **Neurosurgeon** (Kang et al.) | ASPLOS 2017, published in ACM SIGPLAN Notices (Crossref 10.1145/3093336.3037698) | C | T | DNN partitioning between mobile and cloud (from the title; body not read here) | The historical root of "split inference". Cite it for the concept, not for LLM claims |
| 2017-05 | **Selective Classification for Deep Neural Networks** (Geifman, El-Yaniv) | NeurIPS 2017 (OpenAlex) | D | A | A reject option for DNN classifiers at a target risk | Gives risk–coverage evaluation for an "answer locally or escalate" router |
| 2017-06 | **On Calibration of Modern Neural Networks** (Guo et al.) | ICML 2017 (arXiv comment) | D | A | Modern networks are miscalibrated; temperature scaling fixes much of it | The standard reference for ECE and temperature scaling (DABO uses the latter) |
| 2022-11 | **Speculative decoding** (Leviathan, Kalman, Matias) | ICML 2023 Oral (arXiv comment) | E | A | Draft-then-verify decoding that preserves the output distribution | Baseline family for edge–cloud decoding collaboration (DiP-SD, 2603.19133) |
| 2023-05 | **Parallel (Jacobi) decoding for MT** (Santilli et al.) | ACL 2023 (arXiv comment) | E | A | Jacobi / Gauss–Seidel decoding without retraining | Jacobi lineage (deliverable 6) |
| 2023-10 | **AutoMix** | NeurIPS 2024 (arXiv comment) | A | A | The small LM answers, verifies itself, and a POMDP decides whether to escalate | Post-generation cascade, the confidence/self-routing family (architecture option C) |
| 2024-01 | **Medusa** | ICML 2024 (PMLR v235 index) | E | A | Multiple decoding heads for parallel drafts | Parallel-decoding alternatives to Jacobi Forcing |
| 2024-01 | **EAGLE** | ICML 2024 (PMLR v235 index) | E | A | Feature-level drafting for speculative sampling | As above |
| 2024-02 | **Lookahead decoding** | ICML 2024 (PMLR v235 index) | E | A | Exact, training-free Jacobi-based parallel decoding | Used over a Split-LLM WAN link by Cunningham (2026, §2) |
| 2024-02 | **CLLMs** | ICML 2024 (arXiv comment; PMLR v235 index) | E | A | Consistency distillation on Jacobi trajectories | Direct predecessor of Jacobi Forcing |
| 2024-04 | **Hybrid LLM** (Ding et al.) | ICLR 2024 (arXiv comment) | A, B | A | Router sends each query to a small or large model by predicted difficulty; the quality threshold is tunable at test time | **The peer-reviewed origin of the edge-small vs cloud-large query router. The manuscript does not cite it** |
| 2024-04 | **Multi-token prediction** (Gloeckle et al.) | ICML 2024 (PMLR v235 index) | E | A | Training to predict several future tokens; faster inference | Area E context only |
| 2024-06 | **RouteLLM** | ICLR 2025 (proceedings page, deliverable 3) | A | A | Strong/weak routers trained on preference data (BERT, matrix factorisation, SW ranking, causal LLM) | Standard cloud-pool baseline; Apache-2.0 code |
| 2024-09 | **RouterDC** | NeurIPS 2024 (arXiv comment) | A | A | Contrastive encoder router (mDeBERTa) | A lightweight encoder router already exists |
| 2025-02 | **TMO** | ACM MobiHoc 2025, Best Paper Runner-Up; extended in IEEE/ACM ToN (arXiv comment) | B | A | RL policy chooses device vs cloud per task over quality, latency and cost | A peer-reviewed device–cloud offloading policy the manuscript does not cite |
| 2025-02 | **LLaDA** (large language diffusion models) | NeurIPS 2025 (Crossref, DOI 10.52202/085713-1689) | E | A | A diffusion LM trained from scratch | Area E context; the typesafe-ai org has a fork (deliverable 5, circumstantial only) |
| 2025-06 | **IRT-Router** | ACL 2025 main, pp. 15629–15644 (ACL Anthology) | A | A | Item-response-theory multi-LLM router | Cost–performance routing; the manuscript cites it |
| 2025-06 | **BEST-Route** | ICML 2025 (arXiv comment) | A | A | Picks a model **and** a number of samples | Structured decision output (SD column) |
| 2025-08 | **Dynamic Quality-Latency Aware Routing** (Bao et al.) | IEEE/CIC ICCC 2025 workshop (arXiv comment) | A, B | B | BERT router with an explicit wireless communication plus compute latency model for mobile SLM vs edge LLM (simulated) | Occupies the communication-aware router claim (C2), at workshop level |
| 2025-08 | **LLM Gatekeeper** | ICSC 2025 (arXiv comment) | B | A | Local PII filtering before cloud calls | Privacy-side adjacent work |
| 2025 | **LLMSwitchBench / LLMSwitch-router** | IEEE Access 2025 (Crossref) | A, B | A | 6,000-query smart-home local-vs-cloud benchmark with 1B–8B local models | Candidate dataset for the experiment |
| 2025 | **DIO-LLMs** | IEEE ICC 2025 (Crossref) | C | A | Inter- and intra-layer partitioning of one LLM across edge and cloud | Split-point selector for a single model (no query routing) |
| 2025 | **Poster: split-LLM transmission** (Zhou et al.) | IEEE ICNP 2025 poster (Crossref) | C | A | Transport layer for split-LLM intermediate vectors | Communication engineering for split LLMs |
| 2025-07 | **Li et al. survey**, edge SLMs × cloud LLMs | ACM CSUR 2026, doi 10.1145/3838593 (arXiv comment + Crossref) | B | A | Taxonomy of edge SLM–cloud LLM collaboration | **main-original L40, first sentence, is copied verbatim from this survey's abstract** (deliverable 8 §5) |
| 2025-10 | **ICL-Router** | AAAI 2026 (arXiv comment) | A | A | In-context model representations; new models added without retraining | Occupies C3 "without retraining" |
| 2025-11 | **PRISM** | AAAI 2026 (arXiv comment) | A, B | B | An edge linear gate routes each prompt to cloud-only, collaborative (LDP prompt + sketch) or edge-only | **The closest peer-reviewed three-way edge/collab/cloud router**; MIT code |
| 2025-12 | **Splitwise (edge–cloud)** | ACM UCC '25 (arXiv comment) | C | A | Lyapunov-DRL fine-grained LLM partitioning over edge devices | Split placement, not model routing; the name collides with Microsoft's Splitwise |
| 2025-12 | **Jacobi Forcing** | ICML 2026 poster (OpenReview id ORy2hyPd4G, deliverable 6) | E | B | Progressive consistency-style training that makes an AR model a fast causal parallel decoder; 7B code/math | Does not apply directly to a routing encoder (deliverable 6) |
| 2026-01 | **LLMRouterBench** | Findings of ACL 2026, pp. 37733–37754 (ACL Anthology) | A | A | Large routing benchmark; many recent routers do not reliably beat a simple baseline | Sets the bar for any routing claim (U3) |
| 2026-02 | **Routing and cascading survey** (2603.04445) | TMLR 2026 (arXiv comment) | A | A | Taxonomy of dynamic routing and cascading | The citation for the routing taxonomy |
| 2026-04 | **DiP-SD** | IEEE VTC2026-Spring (arXiv comment) | B, E | A | Distributed pipelined speculative decoding, device–edge | The manuscript's 17.89× figure (L83) matches the abstract |
| 2026-04 | **RouteLMT** | ACL 2026 Industry, pp. 1886–1897 (ACL Anthology) | A | A | Probe on the small model's own prompt representation for a hybrid MT deployment | In-model routing on the small model's prefill state |
| 2026-04 | **Network Edge Inference for LLMs** (survey) | ACM CSUR 58(12), 2026 (arXiv comment + Crossref) | B | A | Taxonomy of edge inference | The citation for the edge-inference framing |
| 2026 | **Lyra** | IEEE INFOCOM 2026 (Crossref) | A, B | A | Online preference-aware routing between edge SLMs and cloud LLMs (Lyapunov) | Top networking venue; supersedes C1/C2 for the non-split case |
| 2026 | **LSCI** | IEEE TMC 2026 (Crossref) | B | A | Joint SLM caching and inference offloading in MEC | Occupies the resource-aware offloading space |
| 2026 | **DABO** | IEEE Access 2026 (Crossref) | B, D | A | Calibrated (temperature-scaled) edge/cloud binary offloading; reports lower ECE | Partly occupies U2 (on-device calibrated routing) |
| 2026 | **In-Browser Split Inference** | IEEE Access 2026 (Crossref) | C | A | Per-token RTT does not depend on split point | Weakens the case that choosing between split and full cloud needs a *learned* router |
| 2026 | **AdaptRoute** | SoutheastCon 2026 (Crossref) | B | A | Token-level edge/cloud GPU routing that uses measured network latency | Link-state-aware, but token-level |
| 2026 | **BiCSRouter** | Findings of ACL 2026 (Crossref) | A | A | Routes across *execution regimes* (single- vs multi-agent) | Structural analogue for routing across execution modes (U1) |
| 2026 | **EC-LLM** | IEEE IoT-J 2026 (Crossref) | B | T | Abstract not available | Unread |
| 2026-11 (issue) | **Mix-or-Split** | IEEE TPDS 2026 (Crossref) | B, C | T | Abstract not available; **closed access** | **Highest-priority unread paper. Could pre-empt U1** |

**Not peer-reviewed despite appearances.** CITER (2502.01976) is listed as COLM'25 only
in its repo description (*repo claim*, not verified). Arch-Router (2506.16655) is an
arXiv preprint.

## 2. Preprints (chronological)

| First public | Work | Area | Depth | What it establishes | Relevance [our analysis] |
|---|---|---|---|---|---|
| 2018-12 | **Split learning for health** (Vepakomma et al., 1812.00564) | C | A | Split *learning* (training) without sharing raw data | Split *learning* ≠ split *inference*; the manuscript's three split citations are learning papers (deliverable 1) |
| 2023-02 | **Speculative sampling** (Chen et al., DeepMind, 2302.01318) | E | A | Independent concurrent speculative decoding | Area E context |
| 2023-05 | **FrugalGPT** (2305.05176) | A | A | Learned LLM cascade across cloud APIs | Historical cascade baseline |
| 2024-01 | **Edge–cloud GenAI framework** (Tian et al., 2401.01666) | B | A | Big cloud model with small edge models, a collaboration framework | Early edge–cloud framing |
| 2024-06 | **Adaptive layer splitting, MBRL** (2406.02616) | C | A | RL selects the split point from network conditions (simulation) | Split point conditioned on the network, not the query |
| 2024-07 | **Apple Intelligence Foundation LMs** (2407.21075) | B | A | ~3B on-device model plus a server model on Private Cloud Compute | Industry precedent for device/cloud model pairs (see §4) |
| 2024-10 | **SplitLLM** (2410.10759) | C | A | Split placement for throughput | Split substrate |
| 2025-02 | **CITER** (2502.01976) | A | A | Token-level SLM/LLM routing trained with RL | Token-level, not query-level |
| 2025-05 | **RecServe** (2505.16502) | B | A | Recursive device→edge→cloud confidence offloading; thresholds adapt online | Option C design space |
| 2025-05 | **Fast-dLLM** (2505.22618) | E | A | Training-free KV cache and parallel decoding for diffusion LLMs | Fast-dLLM **v2** is in the manuscript's model pool; Jacobi Forcing Table 6 reports it far below AR on HumanEval |
| 2025-05 | **LLM partitioning at the edge** (2505.02533) | C | A | Head-level partitioning | Split substrate |
| 2025-06 | **Arch-Router** (2506.16655) | A | A | Generative 1.5B preference-aligned router | A generative "tiny LM" router already exists; there is no separate routing head (HF API) |
| 2025-07 | **ECO-LLM** (2507.09003) | B | A | Chooses an edge–cloud pipeline configuration under SLOs | Structured decision output |
| 2025-08 | **CSCR** (2508.12491) | A | A | Cost-banded contrastive routing over a dynamic pool | No-retraining pool change |
| 2025-10 | ~~CoSense-LLM~~ (2510.19670) | — | A | **Withdrawn by arXiv (unverifiable authorship)** | Must not be cited |
| 2025-11 | **Adaptive split computing** (2511.04002) | C | A | Jointly picks split point, quantisation and sequence length | Per-deployment configuration |
| 2025-11 | **Joint partitioning and placement** (2512.01039) | C | A | Runtime re-partitioning | Split substrate |
| 2026-01 | **Federate the Router** (2601.22318) | A | A | Federated training of MLP/k-means routers | Privacy of router *training* |
| 2026-02 | **Cunningham**, privacy-aware split inference + lookahead (2602.16760) | C, E | B | Lookahead decoding over a Split-LLM WAN link; inversion recovers ~59% of tokens (2-layer split) and ~35% (8-layer) | Contradicts the L76 privacy argument; occupies the most sensible Jacobi-family role in a split setting |
| 2026-03 | **vLLM Semantic Router** paper (2603.12646) | A, F | A | ModernBERT-class classifiers without a dedicated GPU | Production-grade lightweight router |
| 2026-03 | **PipeSD-style edge–cloud speculative decoding** (2603.19133) | B, E | A | Pipelined collaborative speculative decoding | Decoding-level collaboration |
| 2026-03 | **Prefill-activation router** (2603.20895) | A | A | Routes on an open LLM's prefill activations ("Encoder–Target Decoupling") | The nearest use of the word "encoder" |
| 2026-03 | **ConsRoute** (2603.21237) | A, B | B | MLP on the device SLM's prefill state; three tiers; per-cluster BO thresholds | **Closest prior art overall** (deliverable 3). Table III: generated tier choice is not more accurate than a probe |
| 2026-03 | **Privacy Guard** (2603.28972) | B | A | A local SLM rewrites or re-routes risky prompts | Privacy routing |
| 2026-04 | **Micro language models** (2604.19642) | B | A | 8–30M decoder models on device with cloud handoff | Defines what "micro" means in current usage; not a router |
| 2026-04 | **SWARM-LLM** (2606.14711) | B | A | Edge SLM swarm plus 70B cloud, uncertainty-gated | Edge–cloud router (Apache code) |
| 2026-05 | **HyDRA** (2605.17106) | A | B | 149M CPU encoder with capability heads; deployed in GitHub Copilot | Lightweight, structured, no-retraining router in production |
| 2026-06 | **ComplianceGate** (2606.31163) | A | A | Classifier-gated multi-tier routing (7 ms) for regulated industries | Lightweight and privacy/compliance-aware |
| 2026-07 | **Privacy-aware edge–cloud split inference** (2607.13093) | C | A | Encrypted split transfer, authenticated KV cache | Split privacy engineering |
| 2026-08 | **Pro-Router** (2608.28726) | A, B | B | Pre-scorer plus token-confidence verifier escalating edge→cloud (edge = A10G nodes) | Two-stage, selective-prediction-style |

## 3. Released open-source systems, code and checkpoints

The GitHub/HF metadata is from the API (R). Licences are SPDX identifiers as the API
reports them. Most rows were checked in deliverables 3–7; rows marked † were checked
again this iteration (`raw/landscape/gh_*.json`).

| Released | System | License | What is released | Use for us [our analysis] |
|---|---|---|---|---|
| 2024-06 | `lm-sys/RouteLLM` † | Apache-2.0 | Routers, training and evaluation framework (last push 2024-08-10) | Baseline routers; the repo has been quiet since 2024 |
| 2025-06 | `hao-ai-lab/JacobiForcing` † | Apache-2.0 | Training/inference code (last push 2026-02-20); 2 HF checkpoints, both 7B (Coder, Math), no card license | Only relevant to U4 (JF edge generator); no small checkpoints |
| 2025 | `katanemo/Arch-Router-1.5B` (HF) | "other" | Generative 1.5B router (text-generation) | Generative router baseline |
| 2025 | `microsoft/best-route-llm` | MIT | BEST-Route code | Structured-output baseline |
| 2025-08 | `vllm-project/semantic-router` † | Apache-2.0 | Production semantic router (created 2025-08-26; active on 2026-09-23; ~5.9k stars) | The most active open lightweight-classifier router; a practical baseline and serving substrate |
| 2026 | `ynulihao/LLMRouterBench` | no SPDX | Benchmark and pre-computed model outputs | Evaluation. Licence must be checked by hand |
| 2026 | `lalalamdbf/ICL-Router`, `Mercidaiha/IRT-Router` | no SPDX | Router code | Baselines, licence to be checked |
| 2026 | `Junfei-Z/PRISM` | MIT | Edge/collab/cloud gate code | The closest peer-reviewed system with code |
| 2026 | `xinyuangui2/pro-router`, `mdahshan/swarm_llm` | Apache-2.0 | Edge–cloud router code | Baselines |
| 2026 | `typesafe-ai/system-one-adapter-python` | MIT | System One interface on any OpenAI-compatible endpoint | An open structured-decision baseline over a local SLM (untested) |
| 2026-06 | `harrrshall/tinyrouter`, `a2o-labs/gemma4-edge-cloud-router` | none / MIT | Hobby-scale routers | tinyrouter's README shows a router tying random routing, which is a warning about headroom |

## 4. Proprietary and industry systems

| Date | System | Depth | What is disclosed | What is **not** disclosed | Relevance [our analysis] |
|---|---|---|---|---|---|
| 2024-06-10 | **Apple Intelligence / Private Cloud Compute** (Apple security blog; AFM report 2407.21075) | V, A | An on-device ~3B model and a larger server model on PCC; "to process more sophisticated requests, Apple Intelligence needs to be able to enlist help from larger, more complex models in the cloud"; stateless, verifiable cloud processing | How requests are sent to device or cloud (by feature or per query), and any learned router | The main industry device↔cloud pair. Its privacy answer is **attested cloud hardware**, not split inference. That is a competing design for the manuscript's privacy motivation |
| 2026 (doc update 2026-05-15) | **Not Diamond** | V | Pre-trained router and custom routers trained on user data; API/SDK | Architecture, evaluation | Commercial cloud-pool router |
| 2026 (docs fetched 2026-09-23) | **OpenRouter Auto Router** | V | "A fast, lightweight classifier assigns each prompt one of ~30 fine-grained task types"; models are ranked by trailing-7-day community spend share; "no retraining or manual curation"; cost tiers | Classifier architecture and accuracy | Production evidence that **lightweight classification plus a non-learned ranking** is how routing is actually deployed. Its navigation also lists a Jev (TypeSafe) integration |
| 2026 (paper 2605.17106) | **HyDRA in GitHub Copilot** | B | 149M CPU encoder, capability heads, 86 ms | Production traffic results beyond the paper | Production lightweight router |
| 2025-12-23 | **Qualcomm US 12,505,362 B2**, "Model selection for split inference" | P | Selects server-side parameters of a split task network from channel and distortion | — | The only "model selection × split inference" item found; not a per-query choice between SLM, split and cloud |
| 2026-09-15 | **Jev / System One (TypeSafe)** | V + independent repos | Typed Choice/Score decisions, calibrated probabilities, API-only, US-hosted; docs market confidence-gated escalation | Architecture; no weights; the terms forbid distillation | Weakens the "fast router" motivation; points to an on-device, pool-specific router (deliverable 5) |

---

## 5. Chronological synthesis: what changed, and when [our analysis]

1. **2017–2019: the foundations.** DNN partitioning between mobile and cloud
   (Neurosurgeon), split learning, calibration (Guo et al.) and selective
   classification (Geifman and El-Yaniv) all existed before LLMs. None of the
   manuscript's "split" or "confidence" ingredients is new as a concept.
2. **2022–2024: decoding acceleration and the first query routers.** Speculative
   decoding (ICML 2023), then Jacobi/lookahead/CLLM, Medusa, EAGLE and multi-token
   prediction (all ICML 2024). In parallel, **Hybrid LLM (ICLR 2024)** framed the
   small-edge vs large-cloud query router, and AutoMix (NeurIPS 2024) the
   self-verifying cascade. RouteLLM and RouterDC made lightweight learned routers
   standard for cloud pools. Apple shipped a device ~3B / server-model pair behind an
   attested-cloud privacy design.
3. **2025: diversification.** Structured and theory-based routers (BEST-Route
   ICML'25, IRT-Router ACL'25); device–cloud RL offloading (TMO, MobiHoc'25);
   communication-aware routing at workshop level (Bao, ICCC'25 wksp); split
   placement for LLMs (UCC'25, ICC'25); diffusion LMs (LLaDA, NeurIPS'25). **A
   generative 1.5B router (Arch-Router) was released**, so "tiny LM as router"
   already existed as an artifact by mid-2025.
4. **Late 2025 to mid 2026: edge–cloud routing becomes crowded and peer-reviewed.**
   PRISM (AAAI'26) established three-way edge/collaborative/cloud routing with
   privacy. ICL-Router (AAAI'26) established no-retraining adaptation. Lyra
   (INFOCOM'26), LSCI (TMC'26) and DABO (Access'26, calibrated) followed. ConsRoute,
   SWARM-LLM, HyDRA (production), vLLM Semantic Router, ComplianceGate and
   Pro-Router appeared as preprints or products. **LLMRouterBench (Findings ACL'26)
   reported that many routers do not reliably beat a simple baseline**, which moves
   the burden of proof onto any new router. Jacobi Forcing (ICML'26) gave strong
   parallel-decoding speedups, but only for 7B code/math generators. Cunningham used
   lookahead decoding over a split-LLM WAN link and reported substantial inversion
   leakage.
5. **September 2026.** Jev (2026-09-15) commoditises fast, calibrated, typed
   decisions as a cloud API. Mix-or-Split (TPDS, Nov 2026 issue) is the one
   identified paper whose title suggests per-request choice between collaborative
   and split execution, and it is unread.

**Net effect on the manuscript.** Between the draft's apparent framing and September
2026, every category claim in C1–C3 acquired peer-reviewed prior art. What remains
open is narrow (U1–U4 in deliverables 4 and 8): Split-LLM as a *routable option*,
calibrated capability routing under shift on device-class hardware, whether any
routing gain survives LLMRouterBench-style baselines with a real on-device SLM and
link, and (separately) a Jacobi-Forcing-trained small edge generator.

---

## 6. Consistency check against earlier deliverables

| Check | Result |
|---|---|
| Venue labels agree with deliverables 3, 4 and 8? | Yes. New venue confirmations this iteration: Medusa, EAGLE, MTP, Lookahead and CLLMs in ICML 2024 (PMLR v235 index), LLaDA NeurIPS 2025 (Crossref), Geifman and El-Yaniv NeurIPS 2017 (OpenAlex), Guo et al. ICML 2017 and Leviathan et al. ICML 2023 (arXiv comments). Lookahead was already ICML 2024 in deliverable 6 |
| Anything here contradict the novelty matrix §4? | No. The industry rows add evidence **for** "lightweight routers are occupied" (OpenRouter's classifier, vLLM-SR). Apple PCC adds a competing privacy design (attested cloud), which the gap assessment did not mention. It does not change U1–U4, but it belongs in the revised paper's privacy discussion |
| Dates | SWARM-LLM carries arXiv id 2606.xxxxx but a citation_date of 2026-04-22 (deliverable 3 metadata). Listed here under its citation_date; the discrepancy is unexplained |

## 7. Uncertainties and open questions

- **Mix-or-Split (TPDS 2026)** and **EC-LLM (IoT-J 2026)** are unread (closed access,
  no abstract in any API). They remain the main risk to U1.
- Neurosurgeon is cited from Crossref metadata only; the ASPLOS proceedings DOI was not
  resolved separately.
- Industry rows are vendor documentation (V). None of the router quality or latency
  claims has been independently checked. How Apple routes between device and PCC is not
  disclosed in the sources read.
- Venue for Arch-Router, ConsRoute, HyDRA, Pro-Router and SWARM-LLM: none found. They
  may since have been accepted somewhere.
- Coverage gaps: no direct IEEE Xplore/ACM DL search. MobiCom/SenSys/MobiSys 2026
  proceedings were not browsed. DBLP was unreachable this iteration.
- Areas **D** (selective prediction for LLM routing specifically, e.g. conformal
  routing) and **E** (diffusion LMs beyond LLaDA/Fast-dLLM, EAGLE-2/3) are covered only
  at anchor level, which is sufficient for positioning but not a full survey.

## Sources added in this iteration (raw copies in `research/raw/landscape/`)

arXiv abstract pages (metadata in `abstracts.txt`): 1705.08500, 1706.04599,
1812.00564, 2211.17192, 2302.01318, 2305.10427, 2401.10774, 2401.15077, 2402.02057,
2403.00835, 2404.19737, 2407.21075, 2502.09992, 2505.22618, 2512.14681, 2603.12646,
2604.19642 · `pmlr_v235_index.html` (ICML 2024 titles) · `crossref_llada.json`,
`crossref_neurosurgeon.json`, `openalex.txt` · `gh_routellm.json`, `gh_jf.json`,
`gh_vllm_sr.json` · `apple_pcc.html/.txt`, `openrouter_auto.html/.txt`,
`notdiamond.html/.txt/.md` · `fetch-log.txt`. The empty `dblp.txt` and the 429
`s2_*.json` files are kept as a record of failed lookups.
