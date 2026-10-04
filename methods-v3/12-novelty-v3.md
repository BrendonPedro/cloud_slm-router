# 12 — Novelty v3: claim register, surviving contribution, three contribution statements

*Deliverable 12 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 15). Resolves findings RF-I1
("the first router to …") and RF-I3 (novelty lanes declared defensible before
any experiment) of `00-review-findings.md`. Covers brief §10 (ban on "first"
claims), §24 (three contribution statements) and stop items 10 and 18.*

Inputs: `06-systems-prior-art-map.md` (systems-venue search), `05-full-routing-prior-art.md`
(routing paper bodies), `01` (model-level utility), `02` (split equivalence, E0),
`03` (KD hardening, C\*), `04` (RouteLLM terminology), `07` (backbone), `09`
(C-1 cost rule and the two systems facts of §2.3), `11` (baselines Q1–Q7).
This iteration also ran a **supplementary invalidation search** (§1.2). It found
one paper, **CR²** (arXiv 2605.12001), that pre-empts more of the method than
anything in `05`/`06`. Its body was read (§2.1).

Evidence tags follow brief §29 and `00` §0: `[VERIFIED-BODY]`, `[VERIFIED-META]`,
`[AUTHOR-CLAIM]`, `[PROPOSED]`, `[OPEN]`, `[REJECT]`. In addition, **ABS**
marks a source whose abstract was read but not its body; ABS rows may inform
the search but may not carry a load-bearing manuscript claim.

---

## 0. Bottom line

1. **No "first" claim survives.** v2's sentence "the first router to (i) … and
   (ii) treat Split(d) as a first-class routable action …" is `[REJECT]`.
   Clause (i) (KD of a calibrated utility head) is now directly pre-empted in
   kind by CR², which distils a full-information teacher router into an
   on-device router (§2.1). Clause (ii) is pre-empted in action-space shape
   by EdgeRL, Edgent and MCDNN (`06` §2). The banned-phrase list is in §6.
2. **Every individual component is published.** These are: an encoder with
   per-model sigmoid heads (HyDRA, BEST-Route, CR²); utility minus λ·cost with
   channel-dependent latency (Bao et al., NetGPT routing, CR²); split-point
   selection under live bandwidth (Neurosurgeon, SPINN, Edgent); learned LLM
   splitting (Chen FITEE, Splitwise-UCC); and distilling a router into a
   cheaper deployable router (CR²). Pre-empted components are
   design choices that we must cite, not contributions (§3).
3. **One integration candidate survives the bounded search** (§4): a single
   per-query decision over **{edge SLM, split execution of a larger LLM at
   depth d, remote execution}**. In this decision, a learned query-conditioned
   *model*-level utility (shared across exact split depths, with sharing gated
   by an equivalence test) is combined with a **measured, depth-aware latency
   model**. Within the scope of §1, no paper was found that puts split-depth
   actions of one LLM next to a separate edge SLM inside a learned semantic
   router. This is **absence in a bounded search**, not `[VERIFIED-BODY]`.
   It is an *integration* contribution of weak-to-moderate strength.
4. **The surviving candidate has a systems weakness that must be stated, not
   hidden.** In a standard dense decoder, prefill bytes do not depend on depth.
   With server-side sampling, a pipeline split also pays one round trip per
   output token (`09` §2.3). If `REMOTE(M_S)` is available, a latency-only rule
   then rarely or never picks `SPLIT_d(M_S)`. The Split action has value
   mainly in a **private regime**, where raw text may not leave the edge
   (the manuscript's own motivation, L76), or under a server-compute budget
   (§4.2). The contribution must be framed around that regime, or it has no
   evaluation in which Split matters.
5. **What can make the paper strong is evidence, not priority.** The candidate
   empirical contributions are: E0 (split equivalence under real numerics),
   E7 (real split execution with network emulation, where CR², Bao et al. and
   the FITEE work rely on simulated channels and profiled costs), E1 (an honest
   KD-versus-C\* test, including a possible negative result) and Q6 (multi-action
   rule versus published binary network-aware rules). Each is gated (§5).
6. **Recommendation:** put the **Conservative** statement (§5.1) into the paper
   now. Move to the Conditional statement only clause by clause, as each gating
   experiment passes. Do not use the Strong statement before submission unless the
   dblp/ACM/IEEE table-of-contents scan in §7 is done (§5.4).

---

## 1. Search scope behind every absence statement

### 1.1 Inherited search (`06` §0, `05` §0)

* **Routing papers, full bodies read** (`05`): RouteLLM, RouterDC, HyDRA,
  LLMRouterBench, ConsRoute, Hybrid LLM, BEST-Route, prefill-activation router,
  Arch-Router, IRT-Router. `11` added section-level reads of RouteLMT and
  ICL-Router.
* **Systems venues** (`06` §0): at least one relevant hit came from ASPLOS,
  MobiCom, MobiSys (+EdgeFM), SIGCOMM (+MECOMM), EuroSys, SoCC, KDD, INFOCOM,
  IEEE TMC/TWC/TSC/IoT-J/Network/COMST, ICC/Globecom/ICCC workshops, ICMLCN,
  ICDCS, ICWS, ICPADS, ISLPED, ICASSP, ACM TECS/CSUR, IEEE/ACM UCC, USENIX NSDI
  and ATC, ICML (PMLR) and FITEE. Searches of IEEE JSAC, MLSys, SenSys and CoNEXT
  returned **no relevant hit**. That is bounded evidence, limited by
  search-engine coverage.
* **Reachability limits:** dblp, ACM DL full text and OpenReview were
  unreachable or returned 403. ACM and IEEE proceedings bodies were read only
  where an arXiv, author or tech-report copy existed.

### 1.2 Supplementary invalidation search (this iteration, 2026-10-04)

The goal was to find work that would sink the §4 candidate or the KD lane.

| # | Query (web search) | Relevant new hits |
|---|---|---|
| S1 | knowledge distillation LLM router small student router teacher soft labels | none (generic KD material) |
| S2 | distilled query router LLM selection "distillation" routing encoder arXiv 2025 | RadialRouter (2506.03880), DiSRouter (2510.19208), Route-Before-Retrieve (2605.10235): none distils a router into a smaller *router* for model selection under system cost |
| S3 | split LLM inference router edge SLM cloud LLM per-query selection split point layer partition 2026 | Koch et al. (2504.03668), Sung et al. (2511.04002), FourierCompress (2510.16418) |
| S4 | LLM routing "knowledge distillation" router compact student calibrated routing scores (extended) | RouteNLP (2604.23577), Calibrate-Then-Route (2609.16206) |
| S5 | joint model selection and split point LLM edge cloud query-aware routing small language model split inference (extended) | **CR² (2605.12001)**, RAC (2608.04991), Cunningham (2602.16760) |

Identity for each hit was taken from its arXiv abstract page (`citation_*`
meta tags). CR² was read in full from the arXiv HTML (v1). The others are ABS.

### 1.3 What the search cannot establish

It is bounded by the query families above, by web-search coverage, and by the
fact that ACM DL and IEEE Xplore full text could not be read. No per-venue
table-of-contents scan was possible. **Therefore no statement in this file
supports "first", "only" or "no prior work".** The strongest permitted form is
"to our knowledge, based on a search of [scope]" (brief §10, §29).

---

## 2. New prior art found this iteration

### 2.1 CR² — the most threatening single paper found so far `[VERIFIED-BODY]`

**Identity.** N. Xue, S. Chen, Z. Chen, J. Yao, Y. Sun, Z. Hu, M. Tao,
"CR²: Cost-Aware Risk-Controlled Routing for Wireless Device-Edge LLM
Inference", arXiv 2605.12001 (v1, 2026-05-12). The arXiv comment says
"submitted to IEEE Journal", so the venue is unconfirmed: cite it as an arXiv
preprint. Body read: §IV (system and cost model), §VI-A–G (the scheme),
§VII-A, §VII-F (setup, complexity).

**What it does (body facts).**
* **Actions.** Whole-model selection among Qwen3-1.7B on the UE (Jetson AGX Orin
  profile) and Qwen3-4B/8B/14B at the edge (RTX 4070 Ti, RTX 4090, A40
  profiles), Eq. (4)–(5). **No split or partition execution.** §II mentions
  split inference only as related work that "require[s] repeated coordination".
* **Utility.** `u_m(x, ξ; λ) = y_m(x) − λ·c_m(x, ξ)` (Eq. 26). This is the same
  shape as our C-1 rule.
* **Cost.** `c̄_m = ω_t·t_m/T₀ + ω_e·e_m/E₀` (Eq. 17), a **normalised
  latency + energy scalar**, then made relative to the largest model (Eq. 18).
  Latency `t_m = τ^ul + τ^rtt + τ^inf_m + τ^dl_m` (Eq. 14). The wireless
  channel state `ξ` enters through uplink and downlink rates (Eq. 8–9). RTT
  is a fixed 18 ms (Table I).
* **Channel.** Simulated quasi-static fading (distance ~U(30,150) m,
  path-loss exponent 4.0, Table I). Inference latency and power are profiled.
  There is **no live network measurement**.
* **Learned components.** (a) A **teacher selector**: frozen all-MiniLM-L6-v2
  embedding plus one binary MLP head per model, giving
  `p_m(x) = σ(ℓ_m(x))` (Eq. 36). It is trained on lm-evaluation-harness
  correctness labels with BCE plus an intra-query pairwise ranking term
  (Eq. 43–45). (b) An **on-device margin gate** (frozen MiniLM, a 2-layer MLP
  with FiLM conditioning on log λ). It "distills full-information utility
  margins into a deployable on-device score" (contributions; §VI-E,
  Eq. 47–59: sign BCE + Huber margin regression to the stop-gradient teacher
  margin + a monotonicity loss in λ). The teacher's margin depends on `ξ`; the
  gate sees only `(e(x), λ)`.
* **Calibration.** Per-λ conformal risk control of the acceptance threshold
  (§VI-F).
* **Data.** MMLU, BBH, GPQA, MBPP, built following EmbedLLM (§VII-A).
* Results such as "up to 16.9% lower normalized deployment cost at matched
  accuracy" are `[AUTHOR-CLAIM]`.

**What CR² invalidates as novelty for us.**
1. "Per-model sigmoid utility heads on a small encoder, combined with
   utility − λ·(network-dependent latency)" for edge LLM routing. This joins
   HyDRA, BEST-Route and Bao et al. as prior art for the *form* of our decision
   rule.
2. "Distilling a teacher router into a cheaper on-device router". CR² does
   this, with a regression-to-teacher-margin loss. **Any claim that KD for LLM
   routers is new is `[REJECT]`.** CR²'s distillation is a form of *privileged-
   information* distillation (the teacher sees `ξ` and the edge-side scores, the
   student does not). It is therefore the closest published analogue of our
   T-PI teacher (`03` §2.4), and must be cited when T-PI is described.
3. "Edge routing that accounts for wireless communication latency/energy".

**What CR² does NOT invalidate.**
1. Split execution of a larger LLM as a routable action. CR² has none.
2. **Model-level** utility shared across execution realizations, with sharing
   decided by an equivalence test. CR² has one model per action, so the
   question does not arise.
3. A cost built from **measured** quantities (live RTT/bandwidth, real
   transport). CR² simulates the channel.
4. Our KD question, in its specific form: whether a larger *text-only*
   teacher's calibrated per-model soft utilities help a smaller text-only
   student beyond a tuned non-KD control C\* (`03` §9). CR²'s gate solves a
   different problem (information asymmetry across a deferral boundary). CR²
   does not compare against a C\*-style control.
5. Also note that CR² uses a normalised latency+energy scalar online, which `09`
   rejects for us (Option 1). This is a design difference, not a novelty.

**Consequences.** CR² must be (i) cited in the related work and in the KD
paragraph of the blue tex; (ii) added to `06` (done in this iteration, §1.3
row and addendum); (iii) considered as a baseline. Its teacher-selector
architecture (frozen MiniLM + per-model heads + BCE/ranking) is already
covered by the `07` backbone ladder plus `11` B-S1/B-C\*, so a separate run is
optional. Its margin gate addresses a two-stage information constraint that
our single-stage router does not have. Recommended status for `11`: **"B-CR2-
style (optional, N ≥ 3 edge models)"**. No public code was checked; that is an
open item.

### 2.2 Other hits (ABS only)

| Work | Identity | What the abstract says | Threat to us |
|---|---|---|---|
| Koch, Djuhera, Binotto, "Intelligent Orchestration of Distributed Large Foundation Model Inference at the Edge" | arXiv 2504.03668; DOI 10.37256/cnc.3220256807 (journal per DOI prefix; venue not checked) | Runtime-adaptive placement and **re-splitting of LFM layers** across MEC nodes under bandwidth, load and privacy. A reference architecture and formalisation | Pre-empts "adaptive LLM split under dynamic bandwidth/privacy" (as Splitwise-UCC and FITEE already do). Not query-aware, no model selection |
| Sung et al., "Memory- and Latency-Constrained Inference of LLMs via Adaptive Split Computing" | arXiv 2511.04002 | Jointly selects **split point, quantization setting and sequence length** under memory/latency constraints; mixed precision and token-wise adaptive bit quantization | A lossy split with a depth-dependent configuration, which supports `02` Branch L. Claims "first autoregressive-aware split computing framework" `[AUTHOR-CLAIM]`. Not a router |
| Ma et al., "FourierCompress" | arXiv 2510.16418 | **Layer-aware** activation compression: first-layer activations are low-frequency and compress about 7.6× with <0.3% accuracy loss `[AUTHOR-CLAIM]` | Shows **compressed** bytes and the resulting quality loss *can* depend on depth. This happens only in a lossy branch, which is consistent with `09` §2.3(a) (raw bytes are depth-independent) |
| Yang et al., "RAC: Reference-Aware Activation Compression for Communication-Efficient Split LLM Inference" | arXiv 2608.04991 | Head/tail local, middle layers in the cloud; codec for boundary hidden states; reports TTFT/TPOT ratios and task-score changes of −0.40 to +2.50 points `[AUTHOR-CLAIM]` | Another lossy split; reinforces that E0 must log compression configuration |
| Cunningham, "Privacy-Aware Split Inference with Speculative Decoding for LLMs over WANs" | arXiv 2602.16760 | Embedding and unembedding stay local; **lookahead decoding amortises the per-token round trip**; claims formal token-identity with greedy sequential decoding; split depth trades privacy against inversion risk `[AUTHOR-CLAIM]` | Directly relevant to `09` §2.3(b): the per-token round-trip penalty can be reduced by speculative/lookahead schemes. Also supports the private-regime motivation. Not a router. Question for Henry (`14`) |
| Guo, Wu, Yiu, "RouteNLP" | arXiv 2604.23577 (arXiv comment: ACL 2026 Industry Track; unverified) | Router plus conformal cascading plus targeted KD **of cheaper models** (not of the router) | Does not pre-empt router KD. Do not cite it as router KD |
| Tumkur et al., "Calibrate, Then Route" | arXiv 2609.16206 | Request routing across disaggregated serving instances using a calibrated completion-time estimate | Out of scope (instance routing, not model routing). It is useful only as evidence that calibrated system costs matter |

---

## 3. Claim register

One row per candidate contribution from v2 `11`, from the manuscript (L40,
L61–L65) or from v3 design changes. "Strongest prior work" lists only sources
read at BODY level in `05`, `06` or §2.1, unless marked ABS.

| ID | Candidate claim | Origin | Strongest prior work | Verdict | Tag | Gate |
|---|---|---|---|---|---|---|
| **K1** | Lightweight encoder router (ModernBERT-class) with independent sigmoid heads | v2 N-baseline; manuscript L61 "novel routing architecture … unlike approaches that rely on heavy models" | HyDRA (ModernBERT-base + sigmoid heads, INT8 CPU), BEST-Route (DeBERTa-v3-small + K×N sigmoid heads), CR² (MiniLM + per-model heads) | **Not a contribution.** Engineering choice (`07`) | `[REJECT]` as novelty | — |
| **K2** | KD of a larger teacher router into a micro-encoder student | v2 N1 | CR² (router-to-router distillation, §2.1); Hinton et al.; generic KD (`03`) | **Not new in kind.** What remains is an *empirical question*: does a larger text teacher's calibrated soft per-model utility beat C\*? A negative answer is reportable | `[OPEN]` (finding, not novelty) | E1 |
| **K3** | KD preserves calibrated utility | v2 N2 | Guo et al. (temperature scaling), Müller et al. (label smoothing) | Withdrawn as a contribution (`03` §0.8). It is measured in E4 against C\* + post-hoc calibration | `[REJECT]` as novelty | E4 |
| **K4** | Keep learned semantic utility separate from measured runtime cost | v2 N3 | Bao et al. (Eq. 11–12), NetGPT routing (Eq. 28–29), Hybrid LLM, ConsRoute, CR² (Eq. 26) | **Not a contribution.** It is a design choice whose justification is `09` §7. Q7 (vs B-INT) tests whether it loses anything | `[REJECT]` as novelty; `[PROPOSED]` as design | E6, Q7 |
| **K5** | Network-adaptive decision without router retraining | v2 N5; manuscript L65 "without requiring costly retraining" | NetGPT routing (threshold monotone in BW/RTT), CR² (λ-conditioned gate + per-λ CRC), ConsRoute (threshold re-tuning) | **Not a contribution.** E6 can show it holds for *our* router over a measured range. The manuscript's general "without costly retraining" must be removed (`01` §5) | `[REJECT]` as novelty | E6 |
| **K6** | "Depth-dependent measured activation bytes" in the router cost | v2 N4; `06` §2 row | `09` §2.3(a): raw bytes are depth-independent for dense decoders. Depth-dependent bytes appear only with layer-aware compression (FourierCompress, Sung et al.; ABS) or non-uniform architectures (Gemma-4 E-series, `10`) | **Rejected as stated.** Reworded as K7 | `[REJECT]` | — |
| **K7** | Measured, depth-aware latency model for split actions: edge-vs-server compute by depth, transfer time from measured bytes and live bandwidth, the per-token round trip | `09` §2 | SPINN, Neurosurgeon, Edgent (CNN analogues); Chen FITEE (learned LLM split, constant tensor size); Splitwise-UCC | An **application** of known cost modelling to LLM split actions inside a router. It supports the integration claim, but is not a standalone contribution | `[PROPOSED]` (design); not a novelty claim | E7, E-COST |
| **K8** | Model-level utility shared across split depths, with sharing gated by an equivalence test (E0); lossy fallback `Û − Δ̂(d)` | `01`, `02` | BEST-Route (action-level heads when the action changes the output distribution); CR², HyDRA (one model per action); nondeterminism literature (`02`) | A **formulation choice** with a stated falsification test. It sharpens the method and is not a priority claim. May be described as "we formulate … and test" | `[PROPOSED]` | E0 |
| **K9** | One per-query decision over {edge SLM, SPLIT_d(M_S), REMOTE} using learned model utility and measured costs | v2 N4/N6 conjunction; `06` §3 | No single paper found (§1). Closest: CR² (multi-model, wireless cost, no split); Bao et al. and NetGPT (binary, no split); EdgeRL and MCDNN (model × split, CNN, not content-aware); CE-CoLLM (edge vs split of *one* LLM, token-level exits) | **The only surviving integration candidate.** Bounded-search absence only. Weak-to-moderate | `[OPEN]` | E0, E5, E7, Q6 |
| **K10** | Real split execution measured on hardware with network emulation (TTFT, TPOT, tails, bytes, throughput, resources, per depth) inside a router evaluation | v2 N6 | Splitwise-UCC, SPINN, Cunningham (ABS) measure split systems but do not evaluate a semantic router. Routing papers that model wireless cost (CR², Bao et al.) simulate the channel | **Empirical contribution**, conditional on E7 actually running on Henry's system | `[OPEN]` | E7 |
| **K11** | The private regime: routing when `REMOTE(M_S)` is masked by data policy, so that Split is the only way to reach the stronger model | `09` §2.3(b), `10` | Cunningham (ABS: privacy-aware split with raw tokens kept local); SnD (cited by the manuscript L78); CE-CoLLM | Not novel as a motivation. It is the **evaluation regime in which K9 is meaningful**. It must be described honestly: split activations are not private by themselves (`09` §2.3(b)) | `[PROPOSED]` (regime); not a novelty claim | E5, E7 |
| **K12** | Hidden-state/self-routing as a baseline, and as a privileged-information teacher (T-PI) | `03` §2.4, `11` B-PFA | Prefill-activation router (`05` §1.8); Lopez-Paz et al.; CR² (privileged margin distillation) | Not novel. T-PI is a combination of known techniques (`03` §10) | `[REJECT]` as novelty | E3, E1 |
| **K13** | "Extensive experiments demonstrate that the proposed method significantly reduces inference cost and latency" | manuscript L40 (abstract) | — | **No experiments exist.** This must not remain in any text that is submitted before results (brief §30) | `[REJECT]` until results | all |

---

## 4. The surviving contribution, stated precisely

### 4.1 Statement `[OPEN]`

> A per-query router for edge–cloud LLM serving whose learned component, a
> compact text encoder, predicts the expected task score of each **model**
> from the query. A runtime controller maps each candidate **execution
> action** (edge SLM, split execution of a larger LLM at depth `d`, or remote
> execution) to its model and selects the action that maximises predicted
> utility minus λ times **measured, predicted end-to-end latency**, subject
> to SLA, memory and data-policy constraints. Split depths of a model share
> that model's utility only where an equivalence test shows split execution
> is score-equivalent to unsplit execution.

### 4.2 Why it is weak-to-moderate, from a reviewer's viewpoint

1. **It is a conjunction of published parts.** A reviewer who knows CR² and
   Edgent/EdgeRL can call it "CR² with an EdgeRL-style split action added".
   The answer must be evidence: E0, E7, and the Split-vs-Remote analysis
   below.
2. **Split has to earn its place.** With an open regime and a server faster
   than the edge, `09` §2.3(b) predicts `L̂(SPLIT_d) > L̂(REMOTE)` at equal
   utility, so C-1 rarely or never picks Split. The paper therefore has to show
   one of the following: (a) a private regime in which `REMOTE(M_S)` is
   infeasible; (b) a server-compute budget under which Split's edge-side
   prefill offload is priced; or (c) a message pattern (batched, speculative
   or lookahead decoding; cf. Cunningham, ABS) that removes the per-token
   round trip. If none of these holds in Henry's system, **K9 collapses**, and
   the contribution becomes the KD/encoder study plus a binary
   edge-vs-remote router. That would be a weaker paper, and it must be said.
3. **Depth selection may be trivial.** In Branch X, with constant bytes, the
   best depth depends only on edge/server compute speed and memory. It may be
   the same `d` for almost all queries and states. E5 and E7 must report the
   depth distribution chosen by the controller. A degenerate distribution
   means the "split-depth action" adds little beyond one fixed split, which
   would be an honest negative result.
4. **Utility headroom.** Q1 (`11`) must show that query content matters in the
   pool. If B-CB (content-blind model choice + best realization) matches the
   method, there is no semantic-routing contribution in that pool (`10` §5.2
   headroom pilot).

### 4.3 What would strengthen it (all `[OPEN]`)

* E0 passes for at least two depths, so model-level sharing is demonstrated
  empirically rather than assumed (K8).
* E7 shows a regime (private, or budgeted) in which choosing among
  `EDGE / SPLIT_d / (REMOTE)` with live measurements beats both fixed policies
  and B-BAO/B-NGPT-style binary rules on the utility–latency frontier (Q6).
* E6 shows that the same trained `Û_θ` stays on or near the frontier across
  the emulated bandwidth/RTT grid, and that B-INT does not dominate outside
  its training range (Q7).

---

## 5. Three contribution statements (brief §24)

Wording rules for all three: present tense for design ("we propose"); future
or conditional tense for evaluation until results exist; no "first", "only",
"novel paradigm", "without retraining" or "lossless"; every comparative clause
names its experiment. Citation keys are placeholders, finalised in `17` /
`method-references-v3.bib`.

### 5.1 Conservative — safe before any experiment (**recommended now**)

> We study query routing for edge–cloud LLM serving in which a query can be
> answered by an on-device small language model, by split execution of a larger
> model across the edge and a server, or by remote execution. We propose a
> router that separates *what* a model is likely to answer well from *how
> much* it costs to run it: a compact text encoder estimates, for each candidate
> model, the expected task score on the query, and a runtime controller combines
> these estimates with predicted end-to-end latency from live network and
> load measurements to choose an execution action under latency, memory and
> data-policy constraints. Split depths of the same model share one utility
> estimate only if a split-equivalence test shows that split execution
> preserves task scores. We also investigate whether distilling a larger
> teacher router into the compact encoder improves routing over a tuned,
> calibrated non-distilled student. The design builds on prior work on
> query-aware routing [RouteLLM, Hybrid LLM, BEST-Route, HyDRA], network-aware
> LLM routing [Bao et al., NetGPT routing, CR²], and split computing
> [Neurosurgeon, SPINN, Edgent].

Contribution bullets (Conservative):

1. A formulation of edge–cloud routing in which learned utility is attached to
   **models** and runtime cost to **execution actions**, including split
   execution at several depths, with an explicit test that decides when split
   depths may share a model's utility. `[PROPOSED]`
2. A runtime controller that prices actions by predicted end-to-end latency,
   built from TTFT/TPOT profiles and live RTT/bandwidth, under hard SLA,
   memory and data-policy constraints, and that reports bytes, energy and
   memory separately. `[PROPOSED]`
3. An evaluation protocol that tests, against strong controls, whether the
   learned router, its distillation and its split actions each add value:
   split equivalence (E0), distillation versus a tuned non-distilled student
   (E1), a lexical baseline (E2), self-routing (E3), calibration (E4),
   utility–latency frontiers (E5), network variation without retraining the
   semantic router (E6) and real split execution (E7). `[PROPOSED]`

### 5.2 Conditional — allowed clause by clause, if the named experiments succeed

Each clause may be used **only** after its gate passes, and the wording must
report the measured effect with its CI, not an adjective.

| Clause | Allowed wording (template) | Gate (success criterion as pre-registered in `03`/`11`/`13`) | If the gate fails |
|---|---|---|---|
| C-a | "On [pool, datasets], the router's utility–latency frontier dominates the content-blind and lexical baselines, with [Δ, 95% CI] at the pre-registered SLA points." | Q1, Q2 (E2, E5) | Drop the semantic-routing claim for that pool; report it |
| C-b | "Distilling a [teacher] into the compact encoder improves [primary metric] over a tuned, calibrated non-distilled student by [Δ, CI]" | E1, with S3 > C\* by the rule in `03` §10 | "KD did not improve the router over a tuned, calibrated non-distilled student in our setting" (ship C\*) |
| C-c | "Calibration of the distilled router [matches/exceeds] post-hoc-calibrated non-distilled students ([ECE/Brier, CI])" | E4 | Omit. No calibration claim |
| C-d | "Split execution at depths [D] is score-equivalent to unsplit execution within the run-to-run noise floor, so the depths share one utility estimate" | E0 PASS (`02` §5.6) | Use the Branch L/E wording of `02` §7 and the `Û − Δ̂(d)` formulation |
| C-e | "Across [bandwidth × RTT grid], the same trained semantic router, combined with live latency predictions, stays within [x, CI] of the oracle-cost frontier without retraining the semantic router" | E6, Q7 | Report the range over which it fails. If B-INT dominates in-range, reword per `09` §7 |
| C-f | "On real edge/server hardware with emulated network conditions, choosing among edge, split and remote actions improves the utility–latency frontier over [fixed policies, Bao-style and NetGPT-style binary rules] by [Δ, CI] in the [private/budgeted] regime" | E7, Q6, plus the depth distribution reported | Contribution reduces to the measured study; report that Split was rarely chosen and why (`09` §2.3(b)) |
| C-g | "The router adds [ms, p50/p95] and [MB] on [device], measured" | E7 / E-BB | Report measured numbers whatever they are |

A typical Conditional sentence, if C-a, C-b, C-d and C-f all pass:

> "We propose … [Conservative design sentence]. On [pool] and [datasets],
> the router improves the utility–latency frontier over content-blind,
> lexical and network-aware binary baselines by [Δ, CI]; distillation from a
> [teacher] improves over a tuned non-distilled student by [Δ, CI]; and on
> real edge/server hardware, split execution, shown to be score-equivalent
> to unsplit execution at the tested depths, extends the frontier in the
> private regime by [Δ, CI]."

No "first" appears in the Conditional statement.

### 5.3 Strong — only if experiments succeed and the literature supports it

> "… To our knowledge — based on a search of ACM, IEEE, USENIX and ML venues
> and preprints up to [date], documented in the supplementary material — this
> is the first evaluation of a learned query router that jointly selects among
> an on-device model, split execution of a larger model at multiple depths, and
> remote execution using measured network and compute costs."

Preconditions, all required:
1. C-a, C-d (or the Branch L variant) and C-f all pass.
2. The §7 table-of-contents scan has been completed and has found no paper
   with K9's conjunction. It must cover dblp listings of MobiCom, MobiSys,
   SenSys, SIGCOMM, CoNEXT, INFOCOM, ICDCS, MLSys, EuroSys and USENIX ATC/NSDI
   for 2023–2026, and IEEE TMC/JSAC 2024–2026. The search log must be put in
   the supplement.
3. The sentence keeps "to our knowledge", the scope and the word
   "evaluation". It is narrowed to the conjunction and never extends to any
   component (K1–K8, K12).
4. Advisor sign-off (brief §24).

Even then, the recommendation is to **prefer the Conditional statement**.
CR² shows how quickly this area moves: it appeared five months before this
search and pre-empts two of v2's lanes.

### 5.4 Which version goes into the paper now

**Conservative (§5.1).** No experiment has been run, the search is bounded
(§1.3), and CR² was found only in a supplementary search, which shows that
coverage is incomplete. The manuscript's current contribution bullets (L61,
L65) and abstract claims (L40) must be replaced by §5.1 when the blue Proposed
Solution is merged. That merge needs advisor review; `source/main-original.tex`
is not modified by this sprint.

---

## 6. Banned and replacement wording

| Banned `[REJECT]` | Why | Replacement |
|---|---|---|
| "the first router to …" (v2 `11` §9) | Bounded search only; CR², EdgeRL and Edgent pre-empt clauses | "We propose a router that …" |
| "first to treat Split(d) as a routable action" | EdgeRL (joint version × cut layer), Edgent, MCDNN | "We include split execution at several depths among the router's actions" |
| "first application of KD to LLM routing" / "no router uses distillation" | CR² distils a teacher router into an on-device gate; `04` §4 | "We investigate whether distilling a larger teacher router improves a compact router over a tuned non-distilled student" |
| "RouteLLM distils GPT-4" / "KD in all but name" | `04` | "RouteLLM trains on LLM-judge preference labels as data augmentation" |
| "novel network-aware LLM routing" | Bao et al., NetGPT routing, CR² | "Following network-aware routing [Bao, NetGPT, CR²], our controller …" |
| "depth-dependent activation bytes" | `09` §2.3(a) | "depth-dependent edge/server compute, with transfer time from measured bytes and live bandwidth" |
| "first to include activation-transfer cost" | SPINN, Neurosurgeon, Edgent | "As in split computing [SPINN, Neurosurgeon], transfer time enters the cost" |
| "without (costly) retraining" (manuscript L40, L65) | `01` §5, `09` §7 | "Changing network conditions or split depths does not require retraining the semantic router when split execution passes the equivalence test; adding a model requires labelled outcomes for it and training a new head" |
| "split quality is identical" / "lossless split" | `02` | "score-equivalent within the run-to-run noise floor, as tested by E0" |
| "a novel routing architecture" / "unlike existing approaches that rely on heavy models" (manuscript L61) | HyDRA, BEST-Route, CR² are compact | "We use a compact encoder, as in [HyDRA, BEST-Route]" |
| "encoder architecture does not matter" | `05` §4 bound on LLMRouterBench | Use only the bounded sentence of `05` §4 |
| "Extensive experiments demonstrate …" (manuscript L40) | No experiments | Remove until results exist |
| "ModernBERT is the most efficient encoder" | `07` | "We use ModernBERT-base as the first implementation candidate; backbone choice is an engineering decision" |

---

## 7. Pre-submission search still required `[OPEN]`

This is needed before the Strong statement, and it is also recommended before
submission even with the Conservative one.

1. dblp TOC scans (2023–2026): MobiCom, MobiSys, SenSys, SIGCOMM, CoNEXT,
   NSDI, ATC, EuroSys, ASPLOS, MLSys, INFOCOM, ICDCS, IEEE EDGE, plus IEEE
   TMC/JSAC/TWC 2024–2026, using the keywords "split", "partition",
   "collaborative inference", "routing", "offloading" combined with "LLM" /
   "language model".
2. A forward-citation check (Semantic Scholar or Google Scholar "cited by") on
   CR², Bao et al., NetGPT routing, CE-CoLLM, EdgeRL and Splitwise-UCC. Any
   paper that combines them is most likely to cite them.
3. Upgrade MCIA (ACM TECS 2024: model version × partition × bandwidth) from
   ABS to BODY (`06` §5.1). It is still the highest-priority unread systems
   body.
4. Check whether CR² has public code and whether a journal version exists.
5. Re-run S1–S5 (§1.2) on the submission date. The area produces relevant
   preprints monthly.

---

## 8. Consequences for other deliverables

| File | Consequence |
|---|---|
| `06-systems-prior-art-map.md` | CR² row added to §1.3; iteration-15 addendum lists the ABS hits of §2.2 (done in this iteration). |
| `11-baselines-v3.md` | Add "B-CR2-style" as optional (N ≥ 3 edge models; the teacher-selector architecture is already covered by the `07` ladder and B-C\*). Cite CR² next to Bao/NetGPT for Q6. |
| `03-kd-hardening.md` | T-PI must cite CR² as the closest routing analogue of privileged distillation. KD remains an investigation (K2). |
| `13-experiments-v3.md` | Must report (i) the split-depth distribution chosen by C-1 (§4.2.3); (ii) Split-vs-Remote in the open and private regimes (§4.2.2); (iii) all gates C-a … C-g with pre-registered criteria. |
| `14-henry-checklist.md` | Ask whether decoding uses speculative/lookahead or batched messages (removes the per-token RTT, §2.2 Cunningham), and whether activations are compressed per depth (FourierCompress/Sung-style). |
| `proposed-solution-blue-v3.tex` | Use only §5.1 wording; contribution bullets = §5.1 bullets; cite CR², Bao et al., NetGPT routing, HyDRA, BEST-Route, SPINN, Neurosurgeon, Edgent at the positions shown in §5.1 and §6. |
| `16-citation-audit.md` / `17` / `.bib` | CR² enters as an arXiv preprint (`@misc`/`@article` with eprint 2605.12001), venue "submitted", not as an IEEE journal. ABS-only hits in §2.2 may be cited only for what their abstracts state, and only if needed. Prefer omission. |
| `FINAL-SUMMARY-v3.md` | Q17–Q19 answered from §4–§5. Q18 = §5.1; Q19 = §5.2 (and §5.3 with its preconditions). |

---

## 9. Sources used in this file

| Source | Identity checked | Inspection | Used for |
|---|---|---|---|
| CR², Xue et al., arXiv 2605.12001 v1 | arXiv abstract meta tags (title, 7 authors, 2026-05-12); arXiv comment "submitted to IEEE Journal" | **BODY** (arXiv HTML: §II, §IV Eq. 4–18, §VI Eq. 24–59, §VII-A, §VII-F, Table I) | §2.1, K1, K2, K4, K5, K9 |
| Koch et al., arXiv 2504.03668 | meta tags incl. DOI 10.37256/cnc.3220256807 | ABS | §2.2 |
| Sung et al., arXiv 2511.04002 | meta tags | ABS | §2.2, K6 |
| Ma et al. (FourierCompress), arXiv 2510.16418 | meta tags | ABS | §2.2, K6 |
| Yang et al. (RAC), arXiv 2608.04991 | meta tags | ABS | §2.2 |
| Cunningham, arXiv 2602.16760 | meta tags | ABS | §2.2, §4.2, K11 |
| Guo et al. (RouteNLP), arXiv 2604.23577 | meta tags; arXiv comment (ACL 2026 Industry) | ABS | §2.2 |
| Tumkur et al., arXiv 2609.16206 | meta tags | ABS | §2.2 |
| All other works | see `05`, `06`, `03`, `04`, `07`, `09`, `11` | as recorded there | §3 |

Protected-file check at the time of writing: `source/main-original.tex`
sha256 prefix `06f5f9d7`, methods-v2 aggregate `562faa69`. Both unchanged
from the `00` baseline.
