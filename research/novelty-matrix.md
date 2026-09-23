# Deliverable 4 — Novelty matrix

*Prepared 2026-09-23 (gnhf iteration 6). Subject: "Tiny-LM with Jacobi-Forced
Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs"
(`source/main-original.tex`, unchanged; SHA-256 06f5f9d7…07cf6).*

Builds on `research/closest-prior-art.md` (deliverable 3),
`research/micro-encoder-investigation.md` (7), `research/jacobi-forcing.md` (6) and
`research/jev-system-one.md` (5). This iteration ran a **targeted search for the
candidate residual gap** named in deliverable 3 §4 item 6: a query-level router
whose options include a Split-LLM path. That search turned up **seven sources not
previously recorded**, most importantly **PRISM (AAAI 2026)**, which narrows the gap
considerably (§2, §5). Raw copies are in `research/raw/novelty/`: arXiv abstract
pages `abs_*.html`, the extracted metadata in `abstracts.txt`, PRISM's full HTML and
text, the Google Patents page for US12505362B2, the GitHub API record, and
`fetch-log.txt` with UTC timestamps.

**Nothing in this document was reproduced or run by us.** Cells record what the
source *says it does*. They do not say whether it works.

---

## 0. Legend and rules

| Symbol | Meaning |
|---|---|
| ● | Present, as an explicit design element, in the source text we read |
| ◐ | Partial or weaker form; the footnote in §3 explains |
| ○ | Absent from the text we read (abstract, and body where the tag says so). **Not proof of absence** |
| ? | Not checked |
| — | Does not apply (e.g. router properties of a benchmark) |
| c | *Claimed only.* Used for the manuscript row: stated in the text, but not defined, implemented or evaluated |

**Evidence depth per row:** **B** = full paper body read (this or an earlier
iteration), **A** = abstract/arXiv metadata only, **V** = vendor documentation,
**P** = patent text (Google Patents).

**Column definitions** (fixed in advance so that wording cannot create novelty):

| Col | Name | Counted as ● when… |
|---|---|---|
| E | Edge SLM | a small LM runs on a user device or an edge node *and answers queries* |
| Cl | Cloud LLM | a larger remote LLM is one of the options |
| Sp | Split-LLM | one LLM's layers are partitioned across device/edge and remote, with **activations** crossing the link |
| Q | Query-level routing | a decision is taken per query (or per task/turn) *before* the answer is generated |
| Ln | Learned router | the decision function has trained parameters |
| Lw | Lightweight router | router cost is small relative to the models it routes: ≤~150M parameters, an MLP/linear probe, or k-NN |
| Cf | Confidence / calibration | the router outputs, or thresholds on, a probability or uncertainty that is used for the decision (◐ if calibration itself is not evaluated) |
| La | Latency-aware | latency enters the objective, the constraint, or the evaluation of the routing decision |
| Co | Cost-aware | monetary or compute cost enters the objective, or large-model-call fraction is optimised |
| Cm | Communication-aware | link bandwidth, RTT or payload size enters the model or the routing input |
| Pr | Privacy-aware | privacy is a routing criterion, a mechanism, or is evaluated (◐ = motivation only) |
| H | Heterogeneous pool | >2 candidate models, or models of different families |
| NR | No-retraining adaptation | the pool or operating point can change without retraining the router |
| J | Parallel/Jacobi mechanism | Jacobi, lookahead, consistency, or speculative/parallel decoding is part of the system (◐ = speculative decoding, not Jacobi-family) |
| SD | Structured decision output | the router emits more than one scalar or argmax, e.g. multi-head capabilities, a model × budget pair, or a typed schema |
| OS | Open source | code or weights are public (◐ = public but no SPDX license detected, or a non-standard license) |

---

## 1. The matrix

Rows are grouped: **(0)** the manuscript as written; **(I)** edge–cloud routers;
**(II)** cloud-pool routers; **(III)** Split-LLM / split-computing systems (not
routers); **(IV)** decoding and other adjacent work. Venue is in brackets; "pp" means
preprint.

| # | Work [venue] | Depth | E | Cl | Sp | Q | Ln | Lw | Cf | La | Co | Cm | Pr | H | NR | J | SD | OS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0** | **main-original.tex (as claimed)** | source | c● | c● | c◐¹ | c● | c● | c● | ○ | c◐² | c● | c◐³ | c◐⁴ | c● | c●⁵ | c◐⁶ | ○ | ○ |
| **I-1** | **PRISM** 2511.22788 [**AAAI 2026**] | B | ● | ● | ○⁷ | ● | ●⁸ | ● | ◐ | ● | ◐ | ◐ | ● | ● | ? | ○ | ○ | ● MIT |
| I-2 | ConsRoute 2603.21237 [pp] | B | ● | ● | ○ | ● | ● | ● | ◐ | ● | ● | ◐⁹ | ○ | ◐ | ◐ | ○ | ○ | ○ |
| I-3 | Bao et al. 2508.11291 [ICCC'25 wksp] | B | ● | ◐¹⁰ | ○ | ● | ● | ● | ○ | ● | ◐ | ● | ○ | ○ | ○ | ○ | ○ | ○ |
| I-4 | TMO 2502.11007 [**MobiHoc 2025**] | A | ● | ● | ○ | ● | ●¹¹ | ? | ○ | ● | ● | ◐ | ○ | ◐ | ? | ○ | ◐¹² | ●¹³ |
| I-5 | Pro-Router 2608.28726 [pp] | B | ◐¹⁴ | ● | ○ | ● | ● | ● | ● | ● | ◐ | ◐ | ○ | ● | ? | ○ | ○ | ● Apache |
| I-6 | Hybrid LLM 2404.14618 [**ICLR 2024**] | A | ◐¹⁵ | ● | ○ | ● | ● | ? | ◐ | ○ | ● | ○ | ○ | ○ | ◐ | ○ | ○ | ? |
| I-7 | SWARM-LLM 2606.14711 [pp] | A | ● | ● | ○ | ● | ? | ● | ◐ | ● | ◐ | ○ | ◐ | ● | ? | ○ | ○ | ● Apache |
| I-8 | RecServe 2505.16502 [pp] | A | ● | ● | ○ | ● | ◐¹⁶ | ● | ● | ? | ◐ | ● | ○ | ◐ | ◐ | ○ | ○ | ? |
| I-9 | ECO-LLM 2507.09003 [pp] | A | ● | ● | ○ | ● | ◐ | ? | ○ | ● | ● | ○ | ◐ | ● | ? | ○ | ●¹⁷ | ? |
| I-10 | ComplianceGate 2606.31163 [pp] | A | ◐¹⁸ | ● | ○ | ● | ● | ● | ○ | ● | ● | ○ | ● | ● | ? | ○ | ◐ | ○ |
| I-11 | Privacy Guard 2603.28972 [pp] | A | ● | ● | ○ | ● | ? | ○ | ○ | ○ | ● | ◐ | ● | ◐ | ? | ○ | ○ | ? |
| I-12 | RouteLMT 2604.22520 [**ACL 2026 Ind.**] | A | ◐ | ◐ | ○ | ● | ● | ● | ◐ | ○ | ● | ○ | ○ | ○ | ? | ○ | ○ | ○ |
| I-13 | AutoMix 2310.12963 [**NeurIPS 2024**] | A | ○ | ● | ○ | ◐¹⁹ | ◐ | ◐ | ● | ○ | ● | ○ | ○ | ◐ | ? | ○ | ○ | ? |
| II-1 | HyDRA 2605.17106 [pp; prod.] | B | ○ | ● | ○ | ● | ● | ● | ◐ | ● | ● | ○ | ○ | ● | ● | ○ | ● | ○ |
| II-2 | Prefill-activation router 2603.20895 [pp] | A | ○ | ● | ○ | ● | ● | ◐²⁰ | ◐ | ○ | ● | ○ | ○ | ● | ? | ○ | ◐ | ○ |
| II-3 | RouteLLM 2406.18665 [**ICLR 2025**] | A | ○ | ● | ○ | ● | ● | ● | ◐ | ○ | ● | ○ | ○ | ○ | ◐ | ○ | ○ | ● Apache |
| II-4 | CSCR 2508.12491 [pp] | A | ○ | ● | ○ | ● | ● | ● | ○ | ◐ | ● | ○ | ○ | ● | ● | ○ | ○ | ? |
| II-5 | ICL-Router 2510.09719 [**AAAI 2026**] | A | ○ | ● | ○ | ● | ● | ○ | ◐ | ○ | ? | ○ | ○ | ● | ● | ○ | ○ | ◐ |
| II-6 | IRT-Router 2506.01048 [**ACL 2025**] | A | ○ | ● | ○ | ● | ● | ? | ○ | ○ | ● | ○ | ○ | ● | ? | ○ | ◐ | ◐ |
| II-7 | Arch-Router 2506.16655 [pp] | A | ○ | ● | ○ | ● | ● | ◐ | ○ | ◐ | ○ | ○ | ○ | ● | ● | ○ | ● | ◐ |
| II-8 | BEST-Route 2506.22716 [**ICML 2025**] | A | ○ | ● | ○ | ● | ● | ? | ○ | ○ | ● | ○ | ○ | ● | ○ | ○ | ● | ● MIT |
| II-9 | RouterDC 2409.19886 [**NeurIPS 2024**] | A | ○ | ● | ○ | ● | ● | ● | ○ | ○ | ? | ○ | ○ | ● | ? | ○ | ○ | ? |
| II-10 | LLMRouterBench 2601.07206 [**Findings ACL 2026**] | A | ? | ● | ○ | ● | — | — | — | ◐ | ● | ○ | ○ | ● | — | ○ | — | ◐ |
| II-11 | Jev / System One (TypeSafe) [product] | V | ○ | ● | ○ | ● | ● | ○²¹ | ● | ● | ● | ○ | ○²² | ? | ● | ○ | ● | ○ |
| III-1 | Cunningham 2602.16760 [pp] | A | ◐ | ● | ● | ○ | ○ | — | ○ | ● | ○ | ● | ● | ○ | — | ● | ○ | ○ |
| III-2 | Splitwise (edge–cloud) 2512.23310 [**ACM UCC'25**] | A | ● | ● | ● | ○ | ◐²³ | — | ○ | ● | ? | ● | ○ | ○ | — | ○ | ○ | ? |
| III-3 | Adaptive split computing 2511.04002 [pp] | A | ● | ● | ● | ○ | ○ | — | ○ | ● | ○ | ● | ○ | ◐ | — | ○ | ○ | ? |
| III-4 | Adaptive layer splitting (MBRL) 2406.02616 [pp] | A | ● | ◐ | ● | ○ | ◐²³ | — | ○ | ◐ | ○ | ● | ◐ | ○ | — | ○ | ○ | ? |
| III-5 | Privacy-aware edge–cloud split 2607.13093 [pp] | A | ● | ● | ● | ○ | ○ | — | ○ | ? | ? | ◐ | ● | ○ | — | ○ | ○ | ? |
| III-6 | SplitLLM 2410.10759 [pp] | A | ● | ● | ● | ○ | ○ | — | ○ | ● | ◐ | ● | ○ | ○ | — | ○ | ○ | ? |
| III-7 | US 12,505,362 B2 (Qualcomm) [patent] | P | ● | ◐ | ●²⁴ | ○ | ○ | — | ○ | ◐ | ○ | ● | ○ | ◐ | — | ○ | ○ | — |
| IV-1 | Jacobi Forcing 2512.14681 [**ICML 2026**] | B | ○ | ○ | ○ | ○ | — | — | ○ | ● | ○ | ○ | ○ | ○ | — | ● | ○ | ● Apache |
| IV-2 | DiP-SD 2604.20919 [VTC2026-Spring] | A | ● | ◐ | ○ | ○ | — | — | ○ | ● | ○ | ● | ○ | ○ | — | ◐ | ○ | ? |
| IV-3 | CITER 2502.01976 [COLM'25 per repo] | A | ◐ | ◐ | ○ | ◐²⁵ | ● | ? | ○ | ○ | ● | ○ | ○ | ○ | ? | ○ | ○ | ● |

### Column coverage (counted from the table; rows I–IV only, the manuscript excluded)

| Column | ● rows | Occupied by at least one **peer-reviewed** ● row? |
|---|---|---|
| E, Cl, Q, Ln | many | yes (PRISM, TMO, Hybrid LLM, RouteLLM, …) |
| Lw | ≥10 | yes (PRISM linear gate, RouteLLM-BERT, RouterDC) |
| Cf | ● in 4 rows (Pro-Router, RecServe, AutoMix, Jev); ◐ in 9 more | yes (AutoMix, NeurIPS 2024) |
| La / Co | many | yes |
| Cm | Bao, RecServe, all split systems | yes for split systems (UCC'25); for **routers**, workshop only (Bao, ICCC'25 wksp) |
| Pr | PRISM, ComplianceGate, Privacy Guard, Cunningham, 2607.13093 | **yes: PRISM (AAAI 2026)** |
| Sp | only group III (and the patent) | yes (UCC'25), but **never in a row with Q = ●** |
| NR | HyDRA, CSCR, ICL-Router, Arch-Router, Jev | yes (ICL-Router, AAAI 2026) |
| J | Jacobi Forcing, Cunningham | yes (ICML 2026), but **never in a row with Q = ●** |
| SD | HyDRA, Arch-Router, BEST-Route, ECO-LLM, Jev | yes (BEST-Route, ICML 2025) |

---

## 2. Newly recorded sources (this iteration)

All were opened at the primary location. Numbers are the authors' claims [abs] or
[body] and have **not** been reproduced.

| Work | Record | What it establishes | Relevance to us [O] | Limitations | Code |
|---|---|---|---|---|---|
| **PRISM**: *Privacy-Aware Routing for Adaptive Cloud-Edge LLM Inference via Semantic Sketch Collaboration* | J. Zhan, H. Shen, Z. Lin, T. He (UPenn, HKU, Jinan U.). arXiv 2511.22788, 2025-11-27; "Accepted to AAAI 2026" (arXiv comment; AAAI proceedings not opened) | An **edge-side soft gate routes each prompt to one of three modes: cloud-only, cloud–edge collaboration, or edge-only** [abs]. The gate is a "light-weight linear transformation" plus softmax over sensitivity features (NER, contextual cues, a statistical risk score), trained with an entropy penalty; top-1 at inference [body]. The collaboration mode sends an **LDP-perturbed prompt** to the cloud, which returns a semantic sketch that the edge SLM refines [abs][body]. Edge: RTX 3070 laptop, llama.cpp, SLMs of 1.1–3.5B; cloud: GPT-4o or Qwen3-235B via API [body]. Energy and latency measured; quality by LLM judge [body]. "Energy consumption and latency to 40–50% of baseline methods" [abs] | **The closest match to the manuscript's three-way action space** (edge SLM / collaborative / cloud) with a lightweight edge router and privacy as a criterion, in a **peer-reviewed** venue with **public code**. The manuscript does not cite it | Gating is driven by **privacy sensitivity, not by answer quality or SLM capability**. The collaborative path is **prompt perturbation plus sketch refinement, not a Split-LLM** (no layer partition, no activation transmission). The dataset is semi-synthetic and self-constructed (4 domains). Calibration is not evaluated | `Junfei-Z/PRISM`, **MIT**, last push 2026-07-16 [api] |
| **TMO**: *Device-Cloud Collaborative LLM Inference with Multi-Modal, Multi-Task, Multi-Turn Conversations* | L. Yuan, D.-J. Han, S. Wang, C. G. Brinton. arXiv 2502.11007; "ACM MobiHoc 2025 (Best Paper Runner-Up) → IEEE/ACM ToN (extended)" (arXiv comment) | A resource-constrained RL policy chooses **device vs cloud per task in multi-turn conversations**, plus which modalities to send, maximising quality, latency and usage cost under resource constraints; compared against "LLM-as-Router" baselines; releases the M4A1 dataset [abs] | A **peer-reviewed** device–cloud per-query offloading policy with latency and cost. The manuscript does not cite it | Only two locations; no Split-LLM; RL policy, not a capability classifier; body not read | "code and dataset are available" [abs]; URL and license not checked |
| **RecServe**: *Recursive Offloading for LLM Serving in Multi-tier Networks* | Z. Wu, S. Sun, Y. Wang, M. Liu, B. Gao, J. Lu, Z. Yang, T. Wen. arXiv 2505.16502, preprint | Device→edge→cloud **confidence-based recursive offloading** with sliding-window quantile thresholds that adapt online; communication burden reduced by ">50%" vs centralised cloud serving on 8 datasets [abs] | A confidence cascade across three tiers with **threshold adaptation without retraining**: the option-C design space (architecture options) | Post-generation cascade (each tier answers first); no Split-LLM; body not read | not checked |
| **ECO-LLM**: *Orchestration for Domain-specific Edge-Cloud Language Models* | P. Patidar, A. Crown, K. Hsieh, Y. Xu, T. Chakraborty, R. Chandra, Y. Agarwal. arXiv 2507.09003, preprint | Query-level selection of a whole **edge–cloud pipeline configuration** (context retrieval, preprocessing, model) under user SLOs, using query clustering and Pareto path selection [abs] | A structured, SLO-aware decision output for edge–cloud (column SD) | Smart-home/car domains only; no Split-LLM; body not read | not checked |
| **Privacy Guard** | A. Langiu. arXiv 2603.28972, preprint, single author | An on-premise SLM rewrites and decomposes prompts and re-routes high-risk queries to "Zero-Trust or NDA-covered models" [abs] | Privacy-sensitivity routing with a local SLM (column Pr) | Single author, 1,000-sample self-built benchmark, not a Split-LLM | not checked |
| **Adaptive split computing** | M. Sung et al. arXiv 2511.04002, preprint | Jointly selects **split point**, quantisation and sequence length for autoregressive LLM split computing under memory/latency constraints [abs] | Shows split configuration is optimised *per deployment*, not per query or per model choice | No routing between different models | not checked |
| **Adaptive layer splitting (MBRL)** | Y. Chen, R. Li, X. Yu, Z. Zhao, H. Zhang. arXiv 2406.02616, preprint | Model-based RL selects the **split point** between UE and edge under varying network conditions (simulation) [abs] | Split-point choice conditioned on the network, not on the query | Simulation only | not checked |
| **US 12,505,362 B2**, *Model selection for split inference* | L. Ma, S. Zhang, Y. Qi; assignee Qualcomm Inc. Priority 2024-05-09, granted 2025-12-23 (Google Patents metadata) | A split task network whose **server-side parameter set is selected** from the encoder/compression configuration, distortion, change in task performance, channel capacity and delay (claims 1–8) [P] | The only source found that pairs **"model selection" with split inference**. It selects parameters for the *remote half of one split network*, not a query-level choice between an SLM, a split LLM and a full cloud LLM. It is not LLM-specific | A patent: it establishes a claimed method, not results | — |
| **LLM Gatekeeper** 2508.16765 [ICSC 2025] and **SplitLLM** 2410.10759, **EdgeFM partition** 2505.02533, **joint partitioning** 2512.01039, **survey** 2603.04445 (TMLR 2026), **edge survey** 2604.22906 (ACM CSUR 2026) | abstracts saved in `raw/novelty/abstracts.txt` | Local PII filtering before cloud calls; split placement for throughput; head-level partitioning; runtime re-partitioning; routing/cascading taxonomy; edge-inference taxonomy | Adjacent. The two surveys are the right citations for the routing taxonomy and edge-inference taxonomy | None routes queries to a split path | — |

---

## 3. Footnotes to cells

1. L151 lists "LLMs or Split-LLMs" at the cloud server. The formulation (Eq. 1–3,
   L136–189) never models a partition point, activation size or the edge half of
   the split. Split-LLM is an *option name*, not a modelled mechanism.
2. "may include computation, communication, and latency" (L165). Latency is not
   a separate term, and the router input is (q, M_k) only.
3. Claimed in C2 (L63) and L181. Bandwidth/RTT is not a router input (Eq. 3), so the
   router cannot react to link state as formulated.
4. L40 and L76 give motivation (the S/2-layer argument). There is no mechanism and
   no evaluation. Cunningham 2602.16760 reports ~35% token recovery even at an
   8-layer split, which contradicts the L76 reasoning as stated.
5. C3 (L65) claims "without costly retraining". No mechanism is described.
6. In the title only (L22). The body never defines "Jacobi-Forced" (deliverables
   6 and 7).
7. PRISM's collaboration mode is **prompt-level LDP plus cloud sketch plus edge
   refinement**. No model is partitioned and no activations are transmitted.
   Counted ○ for Sp deliberately: the mechanism differs in kind, not just in
   wording (the privacy threat model and communication payload differ).
8. A linear layer plus softmax over hand-built sensitivity features, trained with
   task loss plus an entropy penalty (Eq. 4–5 of the paper). "Learned", but over
   privacy features, not capability features.
9. Emulated "good"/"bad" network profiles in evaluation. Bandwidth is not a router
   input.
10. The "LLM" is on an edge server, not a cloud.
11. Resource-constrained RL (RCRL) policy.
12. Joint output: location plus the subset of modalities to send.
13. The abstract says code and data are available. The URL and license were not
    checked.
14. The "edge" tier is AWS A10G GPU nodes, not an on-device SLM (deliverable 3 §2.3).
15. "Deployed on lower cost (e.g., edge) devices": framing, not on-device measurement.
16. Confidence thresholds adapted online (quantile interpolation), not a trained router.
17. The output is a full pipeline configuration (retrieval, preprocessing, model).
18. "Local endpoints" in a regulated-jurisdiction sense (data residency), not on-device.
19. Post-generation: the small LM answers first, then self-verifies.
20. Small MLP head, but its features come from a full open-weight LLM's activations.
21. Vendor FAQ: "neither small nor an LLM" (deliverable 5).
22. API-only, US-hosted; routing through it sends every query to the cloud first
    (deliverable 5).
23. RL selects a **split point**, not a model. With the split point at 0 or at S,
    the extremes are "all remote" or "all local" **for the same model**. That is
    not SLM-vs-LLM routing, because quality does not change with the split point.
24. Generic task networks, not specifically LLMs.
25. Token-level routing, not query-level.

---

## 4. Occupied, partially occupied, and unresolved space

All of §4 is our analysis [O]. It uses the rule that **a difference only counts
if it changes what must be built or measured**, not if it only changes wording.

### 4.1 Clearly occupied (peer-reviewed ● and/or several independent preprints)

| Space | Occupied by | Consequence for the manuscript |
|---|---|---|
| Pre-generation SLM-vs-LLM query router between edge and cloud | Hybrid LLM (ICLR'24), TMO (MobiHoc'25), PRISM (AAAI'26); preprints ConsRoute, Bao, SWARM-LLM, Pro-Router | C1 "novel routing architecture" is not defensible as a category claim |
| Lightweight (encoder / MLP / linear) routers | RouteLLM-BERT (ICLR'25), RouterDC (NeurIPS'24), PRISM's linear gate; production HyDRA (149M, CPU); ComplianceGate (7 ms) | "Unlike existing methods that rely on heavy models" (L40/L61) is contradicted |
| Routing on the small model's own prefill state | RouteLMT (ACL'26 Industry); ConsRoute; 2603.20895 | Deliverable 7's interpretation P2 is pre-empted as a *mechanism* |
| No-retraining adaptation to pool changes | ICL-Router (AAAI'26), Arch-Router, CSCR, HyDRA | C3 as written is not a contribution |
| Cost/quality objective of Eq. 2 | Hybrid LLM, RouteLLM, IRT-Router (ACL'25), BEST-Route (ICML'25) | Eq. 2 needs citing, not claiming |
| Three-way edge / collaborative / cloud action space with privacy as a criterion | **PRISM (AAAI'26, MIT code)** | The manuscript's three-way framing (L151, L40) is occupied as a *framing*. Only the *kind* of collaborative path differs (§4.3) |
| Structured decision outputs for routing | BEST-Route (model × samples), HyDRA (capability heads), Arch-Router (policy labels), Jev (typed schema) | Architecture option D is not novel by itself |
| Split-LLM systems with communication and privacy analysis | UCC'25 Splitwise; 2511.04002; 2607.13093; Cunningham (with inversion numbers) | Split-LLM is an established substrate, not a contribution |
| Jacobi-family decoding over a Split-LLM WAN link | Cunningham 2602.16760 (lookahead decoding; preprint) | Partly occupied |

### 4.2 Partially occupied (preprints only, weak evaluation, or occupied in a neighbouring form)

| Space | Status | What remains |
|---|---|---|
| Communication-aware *router* (link state in the routing score) | Bao et al. (workshop, **simulated**); ConsRoute (emulated network, not an input); TMO (RL state) | A measured, on-device router that takes live link state as input, evaluated on real hardware, has no peer-reviewed full-paper instance in our set |
| Calibrated capability routing on device | Pro-Router (selective prediction, datacenter "edge"); ConsRoute (no ECE found); Jev (calibration weak out-of-distribution per an independent repo, deliverable 5) | Reporting **calibration (ECE, risk–coverage)** of an on-device capability router is not standard in the edge–cloud rows |
| Confidence cascades across device/edge/cloud | RecServe, AutoMix, SWARM-LLM | Pre- vs post-generation trade-off on device-class hardware is not directly compared in one study we found; ConsRoute Table III is the closest |
| Jacobi Forcing on an edge or split generator | Jacobi Forcing checkpoints are 7B and code/math only; Cunningham uses lookahead, not JF | A JF-trained *small* generator in an edge or split setting has not been reported (bounded search). It is a **systems component**, not a routing contribution |

### 4.3 Genuinely unresolved (not found in our bounded search)

- **U1: a query-level router whose action space includes a *Split-LLM* path next
  to an edge SLM and a full cloud LLM**, with the split path's cost including
  **activation transmission** and **split-depth-dependent leakage**. The group III
  rows have Sp = ● but Q = ○. The group I rows have Q = ● but Sp = ○. PRISM is the
  nearest: its collaborative path is prompt-LDP-plus-sketch, not layer splitting.
  **Caveats:**
  - (a) *Is this difference meaningful?* If the split path runs the same model as
    the full-cloud path, the split-vs-cloud choice changes **cost and leakage but
    not answer quality**, so it may not need a *learned, query-content* router: a
    rule on link state and sensitivity might do. U1 is a real research question
    **only if** the split path uses a different model or depth, so that quality
    differs, **or** query content predicts which path is acceptable (e.g.
    sensitivity, as in PRISM). A reviewer could otherwise call U1 "PRISM's gate +
    an existing split system", i.e. an incremental composition.
  - (b) *Coverage.* The search was arXiv- and web-search-centric. IEEE Xplore and
    the ACM DL were not searched directly (no API access in this environment). One
    INFOCOM/TMC/JSAC paper could close U1.
- **U2: calibration of an on-device capability router under distribution shift**
  (does "will the SLM answer this correctly?" stay calibrated for new query
  domains?), reported with ECE and risk–coverage next to the routing gain. Occupied
  in pieces (Pro-Router's selective prediction, Jev's weak OOD calibration per one
  non-peer-reviewed repo) but not, in our set, measured for an on-device router.
- **U3: whether a routing gain survives LLMRouterBench's finding** that many
  routers tie a simple baseline, once the pool includes an **on-device SLM** and a
  real link. This is an **evaluation question, not a method**, but it has a
  falsifiable answer.
- **U4: a Jacobi-Forcing-trained small edge (or split-edge) generator.** It is
  unreported, but it is a systems contribution orthogonal to routing, and existing
  JF checkpoints (7B, code/math) do not cover the edge regime. Any "Jacobi" element
  in the title is defensible **only** in this role (deliverable 6 J1), not as a
  property of the router.

**Not unresolved (do not claim):** a tiny or encoder router; a generative router;
a Jacobi-decoded router (no technical reason found: ConsRoute Table III shows
generated tier choices are slower and not more accurate than a probe); no-retraining
adaptation; privacy-sensitivity-aware three-way routing (PRISM).

---

## 5. Self-review (contradiction check)

Checks run on this document before saving:

| Check | Result |
|---|---|
| Does any ● here contradict deliverable 3's detailed entries? | Checked every row that deliverable 3 covers. One difference in wording: deliverable 3 lists Hybrid LLM's edge side as "framing". Here it is ◐ for E with footnote 15, which is consistent |
| Does the new evidence contradict deliverable 3 §4 item 6 ("candidate residual gap")? | **Yes, partly.** Deliverable 3 said no router with a split tier was found; that still holds. It did not know PRISM, which occupies the **three-way edge/collaborative/cloud action space with privacy routing**. U1 is therefore **narrower** than deliverable 3 stated: only the *Split-LLM kind* of collaborative path, and only if caveat (a) is answered. Deliverable 3 should be read together with this note; the gap assessment (deliverable 8) must use U1 as stated here |
| Does the new evidence contradict deliverable 5 (Jev)? | No. Jev stays a cloud decision API; SD and NR ● are vendor claims (depth V) |
| Does it contradict deliverables 6/7 (Jacobi Forcing not applicable to a router)? | No. No row has Q = ● together with J = ● |
| Novelty declared from wording alone? | Checked: (i) "micro-encoder" vs "lightweight encoder": treated as the **same** column (Lw); (ii) "Split-LLM" vs PRISM's "collaboration": treated as **different**, and footnote 7 gives the mechanism-level reason (activations vs perturbed text; different threat model and payload); (iii) "tiny LM" vs "SLM-as-router": same column |
| Is any cell an inference presented as fact? | Depth A rows rely on abstracts only. Their ○ cells mean "not stated in the abstract". The column-coverage table uses only ● cells |
| Is peer-review status stated from the source? | Venue from arXiv comments, the ACL Anthology, or repo descriptions. The AAAI 2026 proceedings entry for PRISM and the MobiHoc 2025 proceedings entry for TMO were **not** opened |

---

## 6. Open questions and uncertainties

- PRISM: does its public code include the gating classifier and the SLM
  deployment? Is the gate retrained per domain? Neither was checked.
- TMO: repository URL and license; whether its "LLM-as-Router" baselines include
  RouteLLM-style routers.
- IEEE Xplore / ACM DL direct search for "split inference" × "model selection" /
  "routing" / "offloading" for LLMs (2024–2026). This is the most important
  remaining check before U1 is presented to the advisor as a gap.
- For U1 caveat (a): the manuscript must say *what differs in quality* between the
  Split-LLM and the cloud-LLM options. If nothing does, the router's split-vs-cloud
  decision is a systems policy, not a learned quality decision.
- Rows with depth A (abstract only) may have ○ cells that the body would turn ●.
  In particular: Hybrid LLM's router backbone, TMO's communication model, RecServe's
  latency evaluation, and the open-source status of ECO-LLM, CSCR, RouterDC, AutoMix.
- The Google Patents metadata for US 12,505,362 B2 was not cross-checked on the
  USPTO page (the USPTO PDF was saved but is image-based and was not parsed).
