# Deliverable 8 — Gap assessment

*Status: audit document, iteration 7, 2026-09-23. Evaluates, sentence by sentence,
the research-gap claim in `source/main-original.tex` (SHA-256 06f5f9d7…07cf6,
unchanged) against the evidence in deliverables 3–7 plus a new IEEE/ACM coverage
sweep (§2). This document gives evidence and options. It does **not** decide
whether the project should continue; that is the advisor's call.*

---

## 0. Method and labels

**Which sentences were assessed.** Every sentence in the manuscript that asserts
one of three things: (i) that a problem exists, (ii) that prior work fails to
solve it, or (iii) that this paper solves it. These are the title (L22), the
abstract (L40), Introduction ¶2–5 and C1–C4 (L48–L67), Table I's "Ours" row
(L104), and the formulation's design requirements (L179–L191). Purely
descriptive related-work sentences (L76–L85) belong to the claim audit
(deliverable 13) and are only used here when they bear on the gap.

**Labels** (as the objective requires):

| Label | Meaning |
|---|---|
| **S — supported** | Primary sources we have read support the sentence as written |
| **P — partially supported** | True in part, or true only after narrowing or qualifying |
| **X — superseded by prior work** | Prior work (listed) already does what the sentence says is missing or new |
| **U — unresolved / needs evidence** | No evidence either way yet, or evidence would have to come from the authors' own (not yet run) experiments |

**Evidence tags** follow deliverables 3–4: [B] body read, [A] abstract only,
[T] title/metadata only, [V] vendor docs, [O] our analysis. Peer-review status
is taken from Crossref/ACL Anthology/arXiv comments; proceedings pages were not
opened for every item (see §7).

---

## 1. Sentence-by-sentence assessment

### 1.1 Title and abstract (L22, L40)

| # | Sentence (abridged) | Loc. | Label | Evidence and reasoning |
|---|---|---|---|---|
| G1 | "Tiny-LM with **Jacobi-Forced Micro-Encoder** for Collaborative Inference between Edge SLMs and Split-LLMs" | L22 | **U** (mechanism undefined); **X** for the "micro-encoder router" part | No method with this name exists (deliverable 7, as of 2026-09-23). The body never defines it; §IV (L195) is ".". Jacobi Forcing needs a causal multi-token generator, and Eq. 3 is a one-pass argmax (deliverable 6). ConsRoute's Table III shows a generated tier choice is **not more accurate** than a hidden-state probe (deliverable 3 §2.1) [B]. Lightweight encoder routers are occupied (RouteLLM-BERT, RouterDC, HyDRA, PRISM's linear gate) |
| G2 | "As large language models (LLMs) evolve, deploying them solely in the cloud or compressing them for edge devices has become inadequate due to concerns about latency, privacy, cost, and personalization." | L40 s1 | **S** as motivation, **but see §5** | Content supported by the edge–cloud surveys. **This sentence is word-for-word identical to the first sentence of the abstract of Li et al., *Collaborative Inference and Learning between Edge SLMs and Cloud LLMs* (arXiv 2507.16731; ACM Computing Surveys 2026, doi 10.1145/3838593, Crossref-verified).** 23 overlapping 8-word sequences; the survey is not in the manuscript's bibliography (checked programmatically, `raw/gap/abstracts.txt`) |
| G3 | "Hybrid inference paradigms that combine cloud-based LLMs with edge-deployed SLMs have emerged as a promising solution, enabling efficient and privacy-aware processing." | L40 s2 | **S** | Hybrid LLM (ICLR 2024), PRISM (AAAI 2026), TMO (MobiHoc 2025), Lyra (INFOCOM 2026, §2). "Privacy-aware" is supported only for systems that model privacy (PRISM), not for hybrid inference in general |
| G4 | "a key challenge … lies in designing lightweight and adaptive routing mechanisms that can accurately select the appropriate model for each query under resource constraints." | L40 s3 | **P** | It is a recognised challenge (surveys), but "lightweight and adaptive" routing is an **occupied** design space (G7, G13). What is still open is narrower: see §3 |
| G5 | "we propose an intelligent routing framework based on a TLM … to guide inference selection between SLMs and **Split-LLMs** in edge–cloud collaborative environments." | L40 s4 | **U** | This is the only part of the abstract that touches a gap we could not close (U1, §3). But the manuscript never models a split (no partition point, activation size or leakage term in Eq. 1–3; deliverable 4 fn. 1), and the method section is empty |
| G6 | "enables low-latency decision-making while accounting for … communication overhead, computational cost, and response time." | L40 s5 | **X** as a category; **U** for this paper | Communication- and latency-aware SLM/LLM routers exist: Bao et al. (ICCC 2025 workshop, explicit wireless comm + compute latency model) [B]; ConsRoute (device–edge–cloud, network conditions) [B]; TMO (MobiHoc 2025) [A]; Lyra (INFOCOM 2026, quality–latency via Lyapunov) [A]; LSCI (IEEE TMC 2026, offloading + model caching) [A]. The manuscript's own formulation does not feed link state to the router (Eq. 3 takes only (q, M_k)), so it cannot account for communication overhead as written |
| G7 | "Unlike existing routing methods that rely on heavy models or complex scoring mechanisms, our framework is lightweight, scalable, and adaptable to heterogeneous model deployments without requiring costly retraining." | L40 s6 | **X** | Lightweight: RouteLLM-BERT/mf (ICLR 2025), RouterDC (NeurIPS 2024), PRISM linear gate (AAAI 2026), HyDRA (149M CPU encoder, production), ComplianceGate (7 ms). No retraining: ICL-Router (AAAI 2026), Arch-Router, CSCR, HyDRA; RecServe adapts thresholds online. The manuscript's own related work (L85) says RouteLMT needs no external predictor and Arch-Router integrates new models "without retraining", which contradicts this sentence |
| G8 | "Extensive experiments demonstrate that the proposed method significantly reduces inference cost and latency while maintaining competitive response quality …" and "The results indicate …" | L40 s7–s8 | **U** — **no evidence exists** | §V Results is empty and the testbed description ends at "…" (L202). These sentences report results that do not exist and must be removed or rewritten as hypotheses (deliverables 1, 13) |

### 1.2 Introduction (L48–L56)

| # | Sentence (abridged) | Loc. | Label | Evidence and reasoning |
|---|---|---|---|---|
| G9 | Split-LLM architectures "partition model execution … such that sensitive data remains local" | L48 | **P** | Split inference keeps *raw tokens* local, but transmitted activations leak: Cunningham (2602.16760) reports inversion attacks recovering ~59% of tokens at a 2-layer split and ~35% at 8 layers [B]. The three cited works (Pham, Hukkeri, Alhindi) are split-*learning* papers by title (deliverable 1). "Sensitive data remains local" needs qualifying |
| G10 | Hybrid paradigms "dynamically allocate inference workloads based on query complexity … routine queries … locally by SLMs, while complex … escalated to … cloud or Split-LLM environments" | L50 | **P** | Supported for SLM↔cloud (Hybrid LLM, RouteLLM, ConsRoute, Lyra, DABO). **No cited or found work escalates to a Split-LLM** as a routing option: that part is U1 |
| G11 | "Early heuristic-based methods have been largely superseded by learning-based approaches" | L52 | **P** | Learned routers dominate the literature, but LLMRouterBench (Findings of ACL 2026) reports that several recent routers "fail to reliably outperform a simple baseline" and that backbone embedding models have "limited impact" [A]. "Superseded" is stronger than the evidence |
| G12 | "existing routing methods still face important practical limitations, particularly in real-time and resource-constrained environments." | L54 s1 | **P** | Too general to test. True of cloud-pool routers (RouteLLM, IRT-Router, ICL-Router assume datacenter serving); false of the edge–cloud routers the manuscript does not cite (ConsRoute, PRISM, TMO, Bao, Lyra, DABO, LLMSwitch-router) |
| G13 | "Current approaches often struggle to jointly optimize accuracy and system-level efficiency, while remaining adaptable to evolving model pools and deployment conditions." | L54 s2 | **X** | Joint accuracy–efficiency: Hybrid LLM, IRT-Router, BEST-Route, ConsRoute, Lyra, TMO. Adaptable to evolving pools: ICL-Router, HyDRA, CSCR, Arch-Router. Adaptable to deployment conditions: Lyra (online, no future-traffic knowledge) [A], RecServe (online thresholds) [A], ConsRoute (per-cluster thresholds) [B] |
| G14 | "routing decisions must account not only for prediction quality but also for communication overhead, memory constraints, and response latency—especially in edge–cloud and Split-LLM collaborative settings." | L54 s3 | **S** as a requirement; **P** as a gap | The requirement is reasonable and shared by prior work (G6). The only uncovered sub-case is Split-LLM (U1). Memory constraints appear in split-point selectors (2511.04002, DIO-LLMs ICC 2025), not in query routers |
| G15 | "Designing routing mechanisms that are both adaptive and lightweight therefore remains an open challenge." | L54 s4 | **X** | See G7 and G13. As a *general* statement this is contradicted by peer-reviewed work. A narrower version may survive (§3) |
| G16 | "To address this gap, we propose … a TLM, which performs fast and lightweight query understanding …" | L56 | **U** | No architecture, parameter count, training objective or measurement is given. Whether a TLM (generative) is even the right router class is contested: ConsRoute Table III [B] and LLMRouterBench [A] both point away from router-architecture novelty |

### 1.3 Contributions (L61–L67) and Table I (L104)

| # | Claim | Loc. | Label | Evidence and reasoning |
|---|---|---|---|---|
| C1 | "novel routing architecture that leverages a TLM … Unlike existing routing approaches that rely on heavy models or complex scoring pipelines …" | L61 | **X** | Pre-generation SLM-vs-LLM edge–cloud routing: Hybrid LLM, TMO, PRISM, Lyra (peer-reviewed); ConsRoute, Pro-Router, SWARM-LLM (preprints). Lightweight routers: see G7. A *generative* 1.5B router already exists (Arch-Router) |
| C2 | "explicitly consider … communication overhead, inference latency, and computational cost … suitable for … privacy-sensitive settings, such as Split-LLM architectures" | L63 | **X** for the comm/latency/cost part; **U** for the Split-LLM part | See G6. Privacy-aware edge/collaborative/cloud three-way routing is occupied by PRISM (AAAI 2026) [B]; its collaborative path is LDP prompt + sketch, **not** a layer split (deliverable 4 fn. 7) |
| C3 | "supports flexible integration of heterogeneous models … without requiring expensive retraining or large-scale supervision" | L65 | **X** | ICL-Router (AAAI 2026), Arch-Router, CSCR, HyDRA. Also, Eq. 3 is a *learned* scoring function f_θ(q, M_k) over a fixed pool; no mechanism for adding M_{K+1} without retraining is described, so the claim is also internally unsupported |
| C4 | "We conduct extensive experiments … showing that the proposed method significantly reduces inference overhead …" | L67 | **U** — **no evidence exists** | As G8 |
| T1 | Table I "Ours" row: System-Aware (Full) ✓, Learning-Based ✓, Lightweight ✓, Adaptive ✓, **only row with Split-LLM Support ✓** | L104 | **P** | Among the 7 rows the manuscript chose, only "Ours" claims Split-LLM support, which is true of the manuscript's comparison set. But the set omits the closest prior art (ConsRoute, PRISM, Bao, TMO, Lyra, Hybrid LLM, DABO), several of which would score ✓ on System-Aware, Lightweight and Adaptive. The "Ours" ticks are claims about an unbuilt system. Individual competitor cells (e.g. RouteLLM "Lightweight ✗" despite its BERT and matrix-factorisation routers) go to the claim audit |

### 1.4 Formulation requirements (L179–L191)

| # | Sentence (abridged) | Loc. | Label | Evidence and reasoning |
|---|---|---|---|---|
| F1 | "Lightweight requirement: the router must operate with minimal latency …" | L179 | **S** (as a design requirement) | Uncontroversial. Not a gap |
| F2 | "Query understanding: accurate routing requires capturing query complexity, intent, and uncertainty." | L180 | **P** | "Uncertainty" is the part that matters: calibrated SLM-confidence offloading exists (DABO, IEEE Access 2026, reports a 31% ECE reduction [A]; AutoMix NeurIPS 2024; Pro-Router). The manuscript has no uncertainty term in Eq. 2–3 |
| F3 | "System constraints: decisions must account for communication overhead, memory limitations, and response latency." | L181 | **P**, and **internally inconsistent** | Correct as a requirement, but Eq. 3's router input is (q, M_k) only. System state cannot enter the decision unless it is folded into C(M_k, q), which is itself undefined beyond L165 |
| F4 | "Adaptability: … remain effective as the model pool evolves." | L182 | **X** as a gap | See C3 |
| F5 | "f_θ is a lightweight scoring function learned by the TLM … enabling fast routing with minimal overhead while maintaining high-quality inference" | L191 | **U** | A design intention, not yet evidenced. Must be measured against LLMRouterBench's simple baseline (U3) |

### 1.5 Tally

| Label | Count | Items |
|---|---|---|
| S | 3 (+1 requirement) | G2 (content only; §5), G3, G14 (as requirement), F1 |
| P | 8 (+ G14 read as a gap) | G4, G9, G10 (non-split part), G11, G12, T1, F2, F3 |
| X | 8 | G6 (category), G7, G13, G15, C1, C2 (non-split part), C3, F4 |
| U | 8 | G1, G5, G8, G16, C2 (Split-LLM part), C4, F5, and the Split-LLM part of G10 |

Every sentence that asserts the *gap itself* (G7, G13, G15, C1, C3) is
superseded. Every sentence that asserts *results* (G8, C4) has no evidence
behind it. The only gap-adjacent material still labelled U is the **Split-LLM**
option (G5, G10, C2), plus the undefined title mechanism (G1).

---

## 2. New evidence this iteration: IEEE/ACM coverage sweep

Deliverable 4 §6 flagged that IEEE Xplore and the ACM DL had not been searched,
and that one INFOCOM/TMC/JSAC paper could close U1. Xplore and ACM DL both block
scripted access here (Xplore returns a JS shell; ACM returns 403), so the sweep
used **Crossref** (`query.bibliographic`, 8 queries × 20 rows, 2024–2026,
`raw/gap/crossref_sweep.txt`), then abstracts from Crossref/OpenAlex/Semantic
Scholar (`raw/gap/ieee_acm_abstracts.txt`, `raw/gap/s2_lyra.json`), plus 5 web
searches. Everything below is at depth [A] or [T]; no bodies were read.

| Work | Record (Crossref-verified) | What the abstract establishes | Effect on the gap [O] |
|---|---|---|---|
| **Lyra**: *Preference-Aware Task Routing for Edge-Cloud Hierarchical LLM Inference* | X. Ma, H. Zhou, T. Wu, X. Fan. **IEEE INFOCOM 2026**, doi 10.1109/INFOCOM59046.2026.11571307 | Online preference-aware routing that "synergizes edge SLMs and cloud LLMs", optimising the quality–latency trade-off with Lyapunov drift-plus-penalty "without requiring future traffic knowledge" [A] | A **peer-reviewed top-networking-venue** edge-SLM/cloud-LLM query router that adapts to dynamic workloads. Further supersedes C1, C2 (non-split) and G13. No split path mentioned |
| **LSCI**: *Joint Inference Offloading and Model Caching for Small and Large Language Model Collaboration* | X. Xu, G. Feng, Y. Liu, S. Qin, J. Wang, Y. Wang. **IEEE TMC 2026**, doi 10.1109/TMC.2025.3608303 | MEC scheme that jointly decides which SLMs to cache at the edge (DRL) and how to offload inference tasks (belief propagation), balancing latency, accuracy and resource cost; numerical results [A] | Peer-reviewed joint SLM/LLM offloading with resource constraints. Supersedes G6/C2 (non-split) further |
| **DABO**: *Difficulty-Aware Binary Offloading for Collaborative Large-Small Model Inference* | C. Zhu, Y. Su, C. Mao, Y. Wu, Y. Gao, C. Yan, R. Tao. **IEEE Access 2026**, doi 10.1109/ACCESS.2026.3724635 | Edge SLM probe inference → temperature-scaled confidence → difficulty score → threshold chosen under an explicit accuracy constraint; 83.72% of requests kept at the edge, ECE reduced 31.08%, mean latency −84.24% vs cloud-only, "in a controlled workstation-based edge simulation" [A] | **Partly occupies U2** (calibrated edge/cloud offloading with ECE reported). Its confidence is over a *label space*, so it targets classification-style tasks; distribution shift and open-ended generation are not mentioned in the abstract |
| **LLMSwitchBench / LLMSwitch-router** | Z. Liu, P. Guo, P. Wang. **IEEE Access 2025**, doi 10.1109/ACCESS.2025.3632276 | 6,000-query smart-home benchmark for local-vs-cloud routing (local 1B–8B) and a privacy-preserving router; 48% API-cost reduction at "cloud-level accuracy" [A] | A public edge/cloud routing benchmark with on-device-scale SLMs: a candidate dataset for the experiment (deliverable 10) |
| **Mix-or-Split**: *Latency-Aware Scheduling for Edge–Cloud LLM Inference* | X. Wang, X. Zhong, W. Yang, F. Liu, W. Zhang. **IEEE TPDS, Nov 2026**, doi 10.1109/TPDS.2026.3729256 | **Abstract not available** from Crossref, OpenAlex or Semantic Scholar (closed access; Xplore not scriptable) [T] | **Highest-priority unread paper for U1.** The title suggests a per-request choice between a *mixture* (SLM–LLM collaboration) and a *split* (partitioned LLM) mode. If so, it would occupy U1 in whole or in part. **U1 must not be presented as a gap until this paper is read** |
| **EC-LLM** | Q. Han, S. Guo, C. Zhao, S. Yang, X. Ren, L. Wang. IEEE IoT-J 2026, doi 10.1109/JIOT.2026.3710272 | Abstract not available [T] | Title: low-cost/low-latency/high-quality edge–cloud LLM inference. Unread |
| **DIO-LLMs** | Z. Feng et al. **IEEE ICC 2025**, doi 10.1109/ICC52391.2025.11160773 | Inter- and intra-layer partitioning of one decoder-only LLM across edge and cloud nodes, chosen by workload and network status (GPPO); simulation [A] | Another split-point selector for **one** model; confirms the group-III pattern (Sp ●, Q ○) |
| **In-Browser Split Inference** (their "SplitLLM") | Y. Lee, Y.-S. Choee, S. Lee, S. Kwon. IEEE Access 2026, doi 10.1109/ACCESS.2026.3720562 | WebGPU client ↔ server split; "the optimal split point depends on the client device, whereas the per-token round trip time is invariant to the split point", so adapting the split to the network "yields no communication benefit"; 8-bit activation compression [A] | Bears on **U1 caveat (a)**: if per-token RTT does not depend on split depth, the split-vs-cloud choice may be driven by device capability and privacy more than by link state. That favours a simple rule over a learned router for that choice |
| **Poster: Optimizing Transmission for Privacy-Preserving Edge-Cloud Split LLM Inference** | Y. Zhou et al. IEEE ICNP 2025 (poster), doi 10.1109/ICNP65844.2025.11192440 | Transport-layer framework (congestion control, adaptive FEC, quantisation) for moving split-LLM intermediate vectors; preliminary results [A] | Split transport is being engineered separately. No routing |
| **AdaptRoute**: *Adaptive Token Routing for Heterogeneous LLM Inference in Edge-Cloud Continuum* | T. P. Patel. SoutheastCon 2026, doi 10.1109/SoutheastCon63549.2026.11476596 | Token-level assignment of inference to edge or cloud GPUs using complexity prediction, measured network latency and GPU queue depth [A] | Link-state-aware routing, but token-level and over GPU nodes, not SLM-vs-LLM query routing |
| **BiCSRouter** | K. Mao, E. Murata, U. Honda. **Findings of ACL 2026**, doi 10.18653/v1/2026.findings-acl.947 | A lightweight inter-regime router that picks an *execution regime* (single-agent vs multi-agent) and then a configuration within it [A] | A structural analogue for U1: routing across **execution regimes**, not just models. Worth citing if U1 is framed as "which execution mode" |
| Surveys | Li et al., ACM CSUR 2026 (doi 10.1145/3838593; = arXiv 2507.16731); Chen et al., *Network Edge Inference for LLMs*, ACM CSUR 58(12), 2026 (doi 10.1145/3809166) | Taxonomies of edge SLM–cloud LLM collaboration and edge inference [A] | The correct citations for the manuscript's framing paragraph (and see §5) |

**What the sweep did *not* find:** no abstract we could read describes a
query-level router whose options include a layer-split LLM next to an edge SLM
and a full cloud LLM. That is the same negative result as deliverables 3–4,
with one important exception: **Mix-or-Split (TPDS 2026) could not be read.**

---

## 3. Status of the candidate gaps after this iteration

| Id (deliverable 4 §4.3) | Previous status | Status now | Why |
|---|---|---|---|
| **U1**: query-level router whose actions include a **Split-LLM** path (with activation-transmission cost and split-depth-dependent leakage) next to edge SLM and full cloud LLM | Unresolved; not found; IEEE/ACM unchecked | **Unresolved, at risk.** Not found in any readable abstract; **one likely-relevant peer-reviewed paper (Mix-or-Split, TPDS 2026) is unread** | Caveat (a) from deliverable 4 still applies and is sharpened by the In-Browser split result: if the split path runs the same model as the cloud path, the split-vs-cloud choice changes cost and leakage, not quality. It may then be a rule, not a learned decision |
| **U2**: calibration of an on-device capability router under distribution shift | Partially occupied in pieces | **Narrower.** DABO (IEEE Access 2026) reports ECE for calibrated edge/cloud offloading in a workstation simulation [A] | What remains: calibration **under domain shift**, for **open-ended generation** (not a label space), **pre-generation** (without running the SLM first), on **device-class hardware** |
| **U3**: does any router beat LLMRouterBench's simple baseline with an on-device SLM and a real link? | Unresolved (evaluation question) | **Unchanged** | No new evidence. LLMSwitchBench (IEEE Access 2025) is a possible second dataset with on-device-scale SLMs |
| **U4**: Jacobi-Forcing-trained small edge (or split-edge) generator | Unresolved; a systems component, not routing | **Unchanged** | No new evidence. JF checkpoints remain 7B code/math only (deliverable 6) |

---

## 4. The narrowest defensible contribution that appears to remain

These are **options for the advisor**, ordered from most to least
novelty-dependent. Each is stated with what would have to be shown. None is
established; all rest on bounded searches (§7).

### N1: split-aware query routing (depends on U1 surviving)

*"A query-level router on the edge device that chooses among {edge SLM, Split-LLM
at depth d, full cloud LLM}, where the split path's cost includes measured
activation transmission and a split-depth-dependent leakage estimate."*

- **Preconditions:** (i) Mix-or-Split and EC-LLM are read and do not already do
  this; (ii) the paper states **why the choice needs to be learned from query
  content**. For example: the split path uses a different model or depth, so
  quality differs, or query sensitivity decides whether any split is acceptable.
  Without (ii), a reviewer can call it "PRISM's gate + an existing split system"
  (deliverable 4 §4.3 caveat a).
- **Minimum evidence:** measured activation payload and per-token latency per
  split depth on real hardware; a leakage measure per depth (e.g. an inversion
  attack as in Cunningham); routing quality vs an oracle and vs a rule-based
  split/cloud policy; comparison with PRISM's gate and ConsRoute's probe.
- **Risk:** highest novelty upside, highest risk of being pre-empted.

### N2: calibrated pre-generation capability routing on device (U2 + U3)

*"An on-device, pre-generation estimator of 'will this edge SLM answer correctly?',
evaluated for calibration under domain shift and for routing gain over
LLMRouterBench's simple baseline on a real device and link."*

- **Preconditions:** position it explicitly against DABO (post-probe,
  label-space confidence), ConsRoute (prefill probe, no ECE found), Pro-Router
  (selective prediction, datacenter "edge") and Jev (cloud, weak OOD calibration
  per one independent repo).
- **Minimum evidence:** ECE and risk–coverage in-domain and out-of-domain;
  routing gain with confidence intervals vs the simple baseline; on-device
  latency of the router itself.
- **Risk:** the contribution is mainly empirical. It can be defended even with a
  negative result (e.g. "calibration collapses under shift"), which suits an
  honest paper, but it is incremental on method.

### N3: Jacobi Forcing for the edge generator (U4), a separate contribution

*"Does Jacobi-Forcing-style training transfer to a sub-2B edge SLM, and does the
decoding speed-up survive on edge hardware or across a split link?"*

- This is the **only** role in which "Jacobi" in the title is technically
  justified (deliverables 6 J1, 7 P1). It is a systems/decoding contribution,
  **orthogonal to routing**, and would need training compute that the 7B
  checkpoints do not provide.
- **Risk:** it changes the paper's topic. Cunningham already applies
  lookahead (Jacobi-family) decoding to split inference over WAN.

### What is **not** defensible as a contribution (from §1)

A tiny or encoder router; a generative/TLM router as such; a Jacobi-decoded
router; no-retraining adaptation; joint accuracy–latency–cost routing between an
edge SLM and a cloud LLM; privacy-aware three-way edge/collaborative/cloud
routing (PRISM); any results claim until experiments are run.

---

## 5. Text-reuse finding (must be fixed before any circulation)

The first sentence of the abstract (L40) is **identical, word for word**, to the
first sentence of the abstract of Li et al. (arXiv 2507.16731, now ACM Computing
Surveys 2026, doi 10.1145/3838593):

> "As large language models (LLMs) evolve, deploying them solely in the cloud or
> compressing them for edge devices has become inadequate due to concerns about
> latency, privacy, cost, and personalization."

This was verified by exact string match against the saved arXiv abstract
(`raw/gap/abs_2507.16731.html`), and the survey is not among the manuscript's 20
`\bibitem`s. We draw no conclusion about how this happened. The sentence should
be rewritten in the authors' own words and the survey cited;
`paper/main-revised.tex` must not carry it over. The claim audit (deliverable
13) should run the same n-gram check against the other cited abstracts. That
check was **not** done this iteration.

---

## 6. Consistency check against earlier deliverables

| Check | Result |
|---|---|
| Does §1 contradict the novelty matrix (deliverable 4)? | No. The X labels match §4.1 "clearly occupied"; the U labels match U1/U4 |
| Does new evidence change deliverable 4? | **Yes, in two places:** (i) U2 is narrower because of DABO; (ii) U1 is "at risk" because of the unread Mix-or-Split. Lyra, LSCI, DABO and LLMSwitchBench should be added as rows when deliverable 4 is next revised. Deliverable 4 is not edited here, to keep this iteration to one unit |
| Does it contradict deliverable 3's ranking? | Lyra (INFOCOM 2026) is peer-reviewed and conceptually close to Hybrid LLM/ConsRoute, but it is read at abstract depth only, so it is not re-ranked here |
| Deliverables 6/7 (Jacobi not applicable to the router)? | Consistent: nothing found uses Jacobi decoding for routing |
| Deliverable 5 (Jev)? | Consistent: Jev is still a cloud decision API. N2 is the direction deliverable 5 pointed to |
| Novelty credited for wording alone? | No. "TLM" vs "lightweight router", "Split-LLM" vs "collaboration" and "micro-encoder" vs "encoder" were treated as in deliverable 4 §5 |

---

## 7. Uncertainty and open questions

1. **Mix-or-Split (TPDS 2026) must be read in full** before U1/N1 goes to the
   advisor. It needs institutional IEEE Xplore access, which this environment
   does not have. EC-LLM (IoT-J 2026) and the SmartIoT 2026 model-size/precision
   selection paper (doi 10.1109/SmartIoT70864.2026.00023) are the next two.
2. The Crossref sweep ranks by bibliographic relevance and returned noisy
   results (SSRN, CRAN, unrelated journals). It is **not** a systematic review.
   Titles that do not use "split" or "routing" (e.g. "partitioned",
   "collaborative decoding", "hybrid execution") could still be missed.
3. Lyra, LSCI, DABO and LLMSwitchBench were read at abstract depth only. Their
   bodies may include (or exclude) calibration, link state or split options.
4. For N1 the authors must answer: **what differs in answer quality between the
   Split-LLM option and the full-cloud option?** If nothing does, the split/cloud
   choice is a systems policy, not a learned routing decision.
5. Whether LLMRouterBench's 33 models include any edge-scale model from the
   manuscript's pool is still unverified (carried over from iteration 1). This
   matters for N2 and U3.
6. The n-gram text-reuse check was run against one source only (§5).

---

## Sources added in this iteration (raw copies in `research/raw/gap/`)

All fetches are logged with UTC timestamps in `research/raw/gap/fetch-log.txt`.

- `abs_2507.16731.html`, `abs_2507.00672.html`, `abstracts.txt`: arXiv abstract pages
- `crossref_10.1145_3838593.json`, `crossref_10.1145_3809166.json`, `crossref_dio.json`: Crossref records
- `crossref_sweep.txt`: 8-query Crossref sweep (raw titles/DOIs)
- `ieee_acm_abstracts.txt`: Crossref/OpenAlex metadata + abstracts for 14 DOIs
- `s2_ieee_try.txt`, `s2_lyra.json`: Semantic Scholar records (Mix-or-Split abstract null; Lyra abstract)
- `ieee_11160773.html`: empty response from IEEE Xplore (documents that direct fetching failed)
