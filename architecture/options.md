# Deliverable 9 — Candidate router architectures

*Written 2026-09-23 (iteration 9). This is a design document. No part of it has
been implemented or measured by us. Every latency or accuracy figure below is
either quoted from a source already verified in deliverables 3–8 (with a pointer)
or is marked as an untested expectation.*

Tags used:

- **[S: dN §x]** means the fact is sourced, and the source record is in deliverable N, section x.
- **[O]** means our analysis.
- **[P]** means a design proposal of ours, not established practice.
- **[E]** means an untested expectation. It needs measurement before it can be claimed.

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-checked this iteration).

---

## 0. Design constraints inherited from earlier deliverables

These constraints come from earlier findings. They are not preferences.

1. **The decision is a scoring/classification problem.** Eq. (3) (L187–189) is
   `argmax_k f_θ(q, M_k)` over a finite pool, so no sequential decoding is required
   [S: d1 §3.2; d6 §9]. A router therefore needs a specific justification before it
   *generates* its decision.
2. **The labels are pool-specific capability labels.** For each training query we need
   whether (or how well) each candidate model answered it. These labels are not
   recoverable from the query text alone. That is why general zero-shot decision models
   (Jev) are over-confident on this label type [S: d5 §5].
3. **The router must run on the edge before any data leaves the device.** This follows from
   the manuscript's own privacy motivation (L40, L76) and its "lightweight requirement"
   (L179) [S: d1; d5 §6].
4. **The action space must be explicit.** The manuscript never defines the
   Split-LLM partition point as a decision variable [S: d1 §3.4 item 4]. Here we use the
   action set
   `𝒜 = {EDGE_SLM, SPLIT(d) for d ∈ D, CLOUD_LLM, ABSTAIN/ESCALATE}`.
   `ABSTAIN` is kept because a typed decision without an "uncertain" option is always
   forced to answer [S: d5 §6, J7].
5. **The objective has to be computable.** Eq. (2) `U − λC` needs `U` to be a defined
   quality metric and `C` to be a single scalar with units [S: d1 §3.4 items 1–3]. All
   options below use one of two forms:
   - a **per-action predicted utility** `Û(a | q)`, combined with a **measured, non-learned
     cost table** `C(a | system state)`, and selected by `argmax_a Û(a|q) − λ C(a)` at
     inference time. λ can then be changed without retraining.
   - a **binary "will the edge be good enough"** probability `p̂(q)`, thresholded at τ(λ).
6. **The evaluation bar** is LLMRouterBench's finding that most routers tie a simple
   baseline [S: d3 §4 item 8]. A second warning is tinyrouter's tie with random routing when
   the pool has little oracle headroom [S: d7 §2]. Every option has to beat TF-IDF +
   logistic regression and a "always the best single model at budget" rule.

---

## 1. Option A — Tiny generative LM router (the manuscript as literally written)

The "Tiny Language Model (TLM)" of L40, L56, L61, L129.

| Aspect | Specification |
|---|---|
| Inputs | Query text `q` in a prompt template that lists the candidate routes (optionally with textual model descriptions, as Arch-Router does) |
| Outputs | Generated tokens naming a route (e.g. `"EDGE"`), or a short structured string such as `{route, split_depth, confidence}`. Probabilities come only from label-token logits |
| Training labels | Route names derived from pool outcome labels (best-under-budget model per query), or preference/policy descriptions (Arch-Router style) |
| Objective | Next-token cross-entropy on the label string (SFT). Optional preference optimisation |
| Latency | Prefill plus one or more decode steps on the edge. Only published comparison we have: ConsRoute's Table III, where asking the device LM to *generate* its tier choice took 36.2 ms (1,868 ms with CoT), against 20.9 ms for a hidden-state probe, and was *less* accurate (85.79% vs 87.92% on GSM8K) [S: d3 §2.1]. One paper, one dataset |
| Parameter target [P] | 0.5–1.5B causal LM (Arch-Router-1.5B is the reference point [S: d7 §2]) |
| Adaptability | Good for *semantic* pool changes: routes can be described in the prompt, so no retraining is needed (Arch-Router, ICL-Router). Poor for *capability* changes: a new model's per-query competence is not in its description [O] |
| Deployment | Edge device, as a separate model or as the edge SLM itself (which then becomes Option C) |
| Split-LLM compatibility | Nominal. A split depth can be emitted as a token. Nothing in the architecture relates to the split computation [O] |
| Expected advantages | Natural-language route policies. Can emit multi-field structured decisions. Matches the manuscript's wording |
| Risks | (i) Slower than a head for the same decision [S: d3 §2.1]. (ii) Calibration from label-token logits is weakly defined, especially for multi-token outputs [O]. (iii) Superseded as a contribution: a released generative small router exists (Arch-Router-1.5B), and small in-model routers already exist in other forms (e.g. RouteLMT's probe) [S: d7 §2; d3 §2.6; d8 §4]. (iv) The Arch-Router baseline description at L317 ("fine-tune its routing head") does not match a causal-LM checkpoint [S: d7 §6] |
| Implementation difficulty | Low–medium. LoRA SFT of a released 0.5–1.5B model |

**Jacobi variant (A-J, = J2/P3).** Decode the structured multi-token decision with a
Jacobi-Forcing-trained router. This is the **only** reading in which the *router itself*
is "Jacobi-forced" [S: d6 §9; d7 §5 P3]. It is technically possible, but it is weakly
justified. The decision is at most tens of tokens, and Jacobi Forcing's reported gains
(2.57–3.86× on A100) were measured on long code/math generations with 7B models
[S: d6 §6]. The same fields can come from a multi-head classifier in one pass (Option D).
A single-token decision gives n = 1 and exactly 1× speed-up [S: d6 §9].
**We recommend A-J only as an ablation** that tests whether generative routing brings
anything, not as the proposed method [O].

---

## 2. Option B — Lightweight discriminative encoder router

A small bidirectional encoder with a scoring head. This is the plain meaning of
"micro-encoder" [S: d7 §2].

| Aspect | Specification |
|---|---|
| Inputs | Query text `q` only. Optionally cheap metadata (length, language, detected PII) appended as features [P] |
| Outputs | One of: (B1) a binary probability `p̂(edge suffices | q)`; (B2) a vector `Û(M_k | q)` for every pool member (multi-label sigmoid, as in HyDRA's capability heads); (B3) an embedding scored against learned per-model embeddings (RouterDC/CSCR style) |
| Training labels | Per-query, per-model correctness/quality from the pool: LLMRouterBench pre-computed outputs where the pool overlaps, otherwise from our own runs [S: d1 §6; d3 §2.17] |
| Objective | B1/B2: binary cross-entropy per model, then post-hoc temperature scaling on a held-out calibration split. B3: contrastive loss (RouterDC). Selection at inference by `argmax Û − λC` with the measured cost table (§0 item 5) |
| Latency | One encoder forward pass. Reported for comparable production encoders: HyDRA, ModernBERT with 4 heads, 86 ms median on **CPU**; ComplianceGate reports 7 ms overhead (small evaluation) [S: d7 §2]. Neither was measured on our hardware |
| Parameter target [P] | 20–150M (MiniLM → DeBERTa-v3-small → ModernBERT-base). "Micro" at the μLM scale (8–30M) is a possible lower-bound ablation [S: d7 §3.1] |
| Adaptability | B3 and a B2 variant with per-model profile vectors can add a model by embedding a few labelled probes, without retraining the encoder (CSCR, HyDRA "zero retraining") [S: d7 §2]. B1 needs relabelling when the edge SLM changes |
| Deployment | Edge device, CPU or NPU. Independent of the SLM runtime |
| Split-LLM compatibility | Treats `SPLIT(d)` as just another action with its own utility head and cost row. It cannot exploit the split computation. If the split path runs the same model as the cloud path, its quality equals the cloud's, and the split-vs-cloud choice collapses to a cost/leakage rule [S: d8 §3, U1 caveat] |
| Expected advantages | Cheapest and most reproducible option. Well-understood calibration tooling. Strong published baselines exist (RouteLLM-BERT, RouterDC, BEST-Route) |
| Risks | **This is not a contribution on its own**: lightweight encoder routers are standard [S: d7 §2; d8 §4 "not defensible"]. Needs a second model resident on the edge device. Does not see the edge SLM's internal state, so it may predict SLM failure less well than Option C [E] |
| Implementation difficulty | Low. Standard fine-tuning, with public code for the baselines |

---

## 3. Option C — Confidence / self-routing edge SLM (probe on the SLM's own state)

The edge SLM routes for itself. A tiny head reads its prefill hidden state (pre-generation),
and optionally its token-level confidence after a short generation (post-generation).

| Aspect | Specification |
|---|---|
| Inputs | C-pre: the edge SLM's hidden state after prefill of `q` (last token, final or intermediate layer). C-post: additionally the first *k* generated tokens' entropies/log-probs |
| Outputs | `p̂(edge answer acceptable | q)`, optionally per-action utilities for the remote options |
| Training labels | Whether the edge SLM's answer to `q` was acceptable (correctness, or judge/reranker agreement with the cloud answer as in ConsRoute) [S: d3 §2.1] |
| Objective | BCE on the probe, then temperature scaling. The threshold τ(λ) is chosen on a dev split, or per query cluster (ConsRoute uses Bayesian-optimised cluster thresholds) [S: d3 §2.1] |
| Latency | C-pre: essentially free if the query stays local, because the prefill is reused for generation; if the query leaves, the prefill is wasted. ConsRoute reports 20.9 ms router latency with Qwen3-1.7B on an RTX 3050 laptop GPU [S: d3 §2.1]. C-post adds *k* decode steps before any offload decision |
| Parameter target [P] | Head of 10K–1M parameters on a 0.5–4B edge SLM. No separate router model |
| Adaptability | The head must be retrained whenever the edge SLM changes, because the labels are that SLM's capability. Adding cloud models only changes the cost table if the head predicts edge sufficiency only [O] |
| Deployment | Inside the edge SLM runtime. Needs access to hidden states (llama.cpp and HF transformers expose them; closed runtimes may not) [E] |
| Split-LLM compatibility | **The only option with a structural link to split inference [O].** In a Split-LLM, the edge already runs the first layers of the large model. A probe on *those* early-layer activations (instead of the SLM's) would decide between `SPLIT(d)` and the other actions using computation that the split path needs anyway. That is deliverable 7's P2, and it is only partly pre-empted: ConsRoute probes the SLM, not the split head [S: d3 §4 item 2; d7 §5 P2] |
| Expected advantages | Sees the SLM's own uncertainty. No second model. Best cost when most queries stay local |
| Risks | **Prefill-state routing is occupied** (ConsRoute, RouteLMT, the prefill-activation router) [S: d3 §4 item 2]. Post-generation confidence is occupied (SWARM-LLM, Pro-Router's verifier, DABO) [S: d3; d8 §3]. Probe calibration under domain shift is unreported for the edge setting (open part of U2) [S: d8 §3]. When the query must leave, the edge has paid the SLM prefill for nothing [O] |
| Implementation difficulty | Medium. Hidden-state extraction on the edge runtime, plus labelling runs of the edge SLM |

---

## 4. Option D — Structured decision model inspired by System One / Jev

A discriminative model with **several typed, independent heads evaluated in one pass**, a full
probability vector per head, and an explicit abstain option. This is our generation-free
reading of Jev's "parallel questions" [S: d5 §8, proposed takeaways]. Jev's own architecture
is undisclosed, so this option borrows only the **interface** [S: d5 §3].

| Aspect | Specification |
|---|---|
| Inputs | Query text (the Option B backbone) **or** the edge SLM prefill state (the Option C backbone). The choice is an ablation [P] |
| Outputs | A typed record from parallel heads [P]: `route ∈ 𝒜` (Choice, softmax over actions including ABSTAIN); `edge_ok` (Noul-like, sigmoid); `sensitivity ∈ {none, PII, confidential}` (Choice); `expected_output_length` bucket (Score, ordinal); an optional `domain` (Choice). Every head returns probabilities, and none generates text |
| Training labels | `route`/`edge_ok`: pool outcome labels as in B/C. `sensitivity`: public PII/privacy datasets or synthetic labels (**not yet identified; an open dependency**). `length`: measured output lengths of the pool models. Jev outputs **cannot** be used as teacher labels (TypeSafe terms forbid distillation) [S: d5 §6] |
| Objective | Sum of per-head losses (CE / BCE / ordinal), then per-head temperature scaling. The routing rule combines heads explicitly [P]: e.g. forbid `CLOUD_LLM` when `P(sensitivity≠none) > ρ`, fall back to the best allowed split depth, and put expected length into the cost term (decode time ∝ length, Eq. 4) |
| Latency | Same as B or C: one forward pass, with extra heads that are linear layers [E: negligible, unmeasured]. Jev's own latency (≥~430 ms per call through a gateway) is **not** relevant, because D runs on-device [S: d5 §6] |
| Parameter target [P] | The B or C backbone plus <1M parameters of heads |
| Adaptability | Separating the heads keeps the policy (thresholds ρ, λ, the allowed-action rules) outside the weights, so policy can change without retraining. Capability heads still need relabelling when the pool changes [O] |
| Deployment | Edge device, as for B or C |
| Split-LLM compatibility | Good in the policy sense [O]. The sensitivity head gives the Split-LLM path a query-content-dependent reason to exist: it is the action for queries too hard for the edge but too sensitive for full cloud. That is precisely the "why must split-vs-cloud be *learned*?" precondition of N1 [S: d8 §4 N1]. Whether splitting actually protects such queries depends on split depth and must be measured (inversion attacks), not assumed |
| Expected advantages | Makes privacy an explicit variable, which fixes formulation gap 5 [S: d1 §3.4]. Gives interpretable, auditable decisions and per-head calibration reporting. Answers RQ10 constructively (Jev-like decision interface, on-device, pool-specific, open) [S: d5 §8] |
| Risks | (i) PRISM (AAAI 2026) already does privacy-aware three-way edge/collaborative/cloud routing, so D differs only if its "collaborative" path is a genuine layer-split path with measured leakage [S: d4 row I-1; d8 §4]. (ii) Sensitivity labels are a new data dependency. (iii) More heads mean more calibration to report. (iv) The multi-head encoder itself is not new (HyDRA's capability heads, BEST-Route's model × samples output) [S: d7 §2] |
| Implementation difficulty | Medium. B or C plus a data effort for the sensitivity head and a policy layer |

---

## 5. Not a router: Jacobi Forcing on the edge generator (E-J, = J1/P1/N3)

Listed for completeness, because it is the only technically natural place for "Jacobi" in the
title [S: d6 §9 J1; d7 §5 P1; d8 §4 N3]. It is **orthogonal** to A–D. It changes the cost
table (the local decode time `TPOT_edge` in Eq. 4), and through the cost table it moves the
routing threshold. It does not change the router.

- Needs Jacobi-Forcing post-training of a sub-2B edge SLM ourselves. Public checkpoints
  are 7B code/math only [S: d6 §1, §7].
- The speed-up relies on spare compute during memory-bound decoding. It is unmeasured on
  edge NPUs or small models [S: d6 §5, §7], so any benefit here is **[E]**.
- It is a separate systems contribution that could be combined with any of A–D. It is not
  evidence for a "Jacobi-forced router".

---

## 6. Side-by-side comparison

`●` = strong, `◐` = partial/conditional, `○` = weak/absent. These are our judgements [O],
with sources in §§1–4.

| Criterion | A Generative TLM | B Encoder | C Self-routing SLM | D Structured multi-head |
|---|---|---|---|---|
| Needs generation for the decision | ● yes | ○ no | ○ no (C-pre) / ◐ (C-post) | ○ no |
| Router latency (relative, sourced where possible) | slowest [d3 §2.1] | low [d7 §2] | lowest if the query stays local [d3 §2.1] | as B or C |
| Separate model resident on the edge | ● | ● | ○ | depends on backbone |
| Sees edge-SLM internal state | ○ (unless it *is* the SLM) | ○ | ● | ◐ (C backbone) |
| Calibrated probabilities are well defined | ◐ | ● | ● | ● (per head) |
| Privacy represented explicitly | ○ | ○ | ○ | ● |
| Structural link to the split computation | ○ | ○ | ◐ (probe on split-head activations, P2) | ◐ (policy reason for SPLIT) |
| Pool-change adaptation without retraining | ◐ (semantic only) | ◐ (B3) | ○ | ◐ (policy only) |
| Novelty as an architecture on its own | ○ | ○ | ○ | ○ |
| Novelty as part of N1/N2 | ○ | ◐ (N2 baseline) | ◐ (N1 via P2, N2) | ◐ (N1) |
| Implementation difficulty | low–med | low | med | med |

**No option is novel as an architecture.** The novelty map (d4, d8) shows that encoders,
prefill probes, generative small routers and multi-head capability heads all exist. What may
remain is **what the router decides and how it is evaluated**: the Split-LLM action with
measured leakage (N1), and calibration under shift on device hardware (N2) [S: d8 §4].

---

## 7. How the options map to the advisor's choices (options, not a decision)

| If the advisor chooses… | The architecture that fits | The minimum comparison set |
|---|---|---|
| **N1** split-aware routing (only if Mix-or-Split and EC-LLM do not pre-empt it) | D with a C backbone, with a probe on the split-head activations (P2) | B, C-pre, a rule-based split/cloud policy, PRISM's gate, ConsRoute-style probe |
| **N2** calibrated pre-generation capability routing | C-pre and B side by side (the comparison between them is itself a finding) | TF-IDF+LR, B, C-pre, C-post, A (Arch-Router as released), optionally Jev as an API baseline under its terms |
| **N3** Jacobi Forcing for the edge generator | Any router (B is simplest) plus E-J | AR edge SLM vs a JF edge SLM under the same router |
| **Keep the manuscript's framing** | A | Must then show A beats B and C on quality at equal or better latency; the only published evidence we found points the other way [S: d3 §2.1] |

**Our read [O], for discussion.** B and C-pre are the cheapest pair to build and give the
comparison N2 needs. D is a thin layer on top of either and is the only option that
represents privacy explicitly, which the manuscript's motivation requires. A should remain as
a baseline, and A-J as an ablation at most. `architecture/recommended-experiment.md`
(deliverable 10) should therefore test B vs C-pre (and A as released) before any D- or
split-specific work, because that comparison is cheap and falsifies the "tiny generative
router" premise directly.

---

## 8. Open questions / uncertainty

1. **Which hardware is "edge"?** The manuscript names a 2×RTX 3090 workstation (L202). The
   latency comparisons between A, B and C depend on whether the device is that workstation,
   a laptop GPU (ConsRoute) or a phone/Jetson-class device. Question for the authors
   [S: d1 open question 4].
2. **Is the split head's activation predictive?** Option C/D-on-split-activations (P2) assumes
   early-layer activations of the *large* model predict whether the *edge SLM* would fail.
   No source tests this. It is an empirical question [E].
3. **Can the split-vs-cloud choice be learned at all?** If `SPLIT(d)` and `CLOUD_LLM` run the
   same model, their quality is equal. The decision is then cost plus leakage only and
   could be a rule [S: d8 §3]. Option D's sensitivity head is our proposed answer. It is
   untested.
4. **Sensitivity labels.** No labelled dataset for "query too sensitive for full cloud" has
   been identified yet. Deliverable 11 must look for one or state that synthetic labels are
   needed.
5. **Mix-or-Split (IEEE TPDS 2026) is still unread** [S: d8 §3]. It could pre-empt the N1
   column of §7.
6. None of the latency figures in §§1–4 were measured by us. They come from other papers'
   hardware and should not be carried into main-revised.tex as properties of our design.
