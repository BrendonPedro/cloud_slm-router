# 02 — Candidate Methods

*Method-selection sprint, iteration 2. This is a planning document. Nothing here
has been implemented, trained, or measured by us. Every latency or accuracy
figure is quoted from a source already primary-checked in the earlier sprint
(`research/`, `architecture/options.md`) with a pointer, or is explicitly marked
as an untested expectation.*

Evidence tags (same convention as `architecture/options.md`):

- **[S: …]** sourced; the record is in the cited earlier deliverable.
- **[O]** our analysis.
- **[P]** our design proposal, not established practice.
- **[E]** an untested expectation; needs measurement before it can be claimed.

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-checked
this iteration). `paper/main-revised.tex` is unchanged.

---

## 0. How to read this document

The fixed problem (from `methods/00-scope-lock.md`) is:

- Eq. (1) `R : Q → M`
- Eq. (2) `max_R E_q[ U(R(q),q) − λ·C(R(q),q) ]`
- Eq. (3) `R(q) = argmax_{M_k ∈ M} f_θ(q, M_k)`

The Proposed Solution section of the manuscript is empty. **The only open
question is what `f_θ` is and how it is implemented.** Every candidate below is
therefore an implementation of `f_θ`, and each candidate's *Definition of f_θ*
section shows its explicit mapping back to Eq. (3) and Eq. (2). Candidates that
cannot be mapped are not listed.

We carry four serious candidates plus two variants:

| ID | Candidate | Template below | Role |
|---|---|---|---|
| A | Tiny generative LM router | §1 | faithful to the literal "Tiny Language Model" wording |
| B | Lightweight discriminative micro-encoder | §2 | the plain reading of "micro-encoder"; cheapest |
| C | Self-routing edge SLM (hidden-state probe) | §3 | reuses edge computation; only structural link to Split |
| D | Structured multi-head utility/cost model | §4 | model-conditioned utility + explicit system-cost & privacy |
| A-J | Jacobi-forced generative router (variant of A) | §5 | ablation only — the one reading where the *router* is Jacobi-forced |
| E-J | Jacobi Forcing on the edge generator | §6 | **not a router**; orthogonal cost-table change, listed for completeness |

The action set used throughout (from `00-scope-lock.md` / `options.md §0`):
`𝒜 = {EDGE_SLM, SPLIT(d) for d ∈ D, CLOUD_LLM, ABSTAIN/ESCALATE}`.

Two admissible forms of `f_θ` recur, both consistent with Eq. (2)–(3)
[S: options §0 item 5]:

- **Utility-then-cost** — learn a per-action predicted utility `Û(a | q)`, combine
  with a **measured, non-learned** cost table `C(a | s)`, and select
  `argmax_a Û(a|q) − λ·C(a|s)` at inference. λ is a run-time knob; changing it
  needs no retraining.
- **Binary sufficiency** — learn `p̂(edge suffices | q)` and threshold at τ(λ). A
  monotone reduction of the argmax when the pool is effectively {EDGE, ESCALATE}.

A shared warning governs all candidates: LLMRouterBench found most routers tie a
simple baseline, and tinyrouter tied random routing when the pool had little
oracle headroom [S: research d3 §4 item 8; d7 §2]. **Every candidate must beat
TF-IDF + logistic regression and an "always the best single model at budget"
rule**, or it is not worth its overhead. This is a falsification bar, not a
formality.

---

## §1. Candidate A — Tiny generative LM router

### One-sentence idea
Prompt a sub-2B causal language model with the query (and optionally textual
route/model descriptions) and have it **generate** the routing decision as text.

### Why it solves the original paper's problem
This is the manuscript as literally written: "Tiny Language Model (TLM)"
(L40, L56, L61, L129). It produces `R(q)` directly and keeps the exact wording of
the proposal, so it is the fidelity anchor against which cheaper candidates must
justify themselves [S: research d1; options §1].

### Architecture
```
        query q  ─┐
                  ├─► prompt template ─► sub-2B causal LM ─► decode ─► "EDGE" | "SPLIT@d" | "CLOUD"
route descriptions ┘        (optional)         (edge)         (label tokens → probs)
```

### Inputs
Query text `q` in a prompt template listing the candidate routes, optionally with
short natural-language model/route descriptions (the Arch-Router pattern)
[S: research d7 §2].

### Outputs
Generated tokens naming a route (e.g. `EDGE`), or a short structured string such
as `{route, split_depth, confidence}`. Probabilities come only from the
label-token logits.

### Definition of f_θ
`f_θ(q, M_k) = log P_LM(token(M_k) | prompt(q, 𝒜))`, i.e. the model's
label-token log-probability for the route naming `M_k`. Then
`R(q) = argmax_{M_k} f_θ(q, M_k)` is exactly Eq. (3), realised by comparing
label-token logits rather than by free generation. Cost enters via the
utility-then-cost form: treat the normalised label-token probability as `Û` and
subtract `λ·C(a|s)` from the measured cost table before the argmax.

### Parameter / model-size target
0.5–1.5B causal LM. Arch-Router-1.5B is the concrete reference point [P; S: d7 §2].
Not invented: this is an existing released size class.

### Training target
Multiclass route (or a short structured record). See `06-label-and-training-design.md`
formulation B/E.

### Training objective / loss
Next-token cross-entropy on the label string (SFT), optionally LoRA. Optional
preference optimisation on route policies (Arch-Router style).

### Label construction
Route names derived from pool outcome labels ("best model under budget for `q`"),
or from natural-language routing policies (Arch-Router). Requires per-query,
per-model pool outcomes [S: d1 §6; d3 §2.17].

### Inference procedure
1. Build the prompt from `q` and the route list.
2. Prefill on the edge device.
3. Read label-token logits (no free decode needed for a single-token label) →
   normalise to `Û`.
4. Subtract `λ·C(a|s)` from the measured cost table.
5. `argmax_a` → route. For multi-field output, one or more decode steps.

### How U is estimated
From normalised label-token probability, calibrated post-hoc (weakly defined for
multi-token outputs — see risks).

### How C is incorporated
Externally, via the measured cost table (communication bytes, RTT, decode-time ∝
length). Not learned into the LM.

### How network/system state is incorporated
Only through the external cost table at selection time. The LM sees query text,
not live system state, unless system features are injected into the prompt (not
recommended — pollutes the semantic signal) [O].

### How Split-LLM fits
Nominal only: a split depth can be emitted as a token. Nothing in the
architecture relates to the split computation [O; S: options §1].

### How a new model is added
Semantic pool change: describe the new route in the prompt → no retraining
(Arch-Router/ICL-Router). Capability change: a new model's per-query competence
is *not* in its description, so quality is unverified without relabelling [O].

### Whether retraining is required
No, for semantic route additions. Yes (or at least relabelling) for genuine
capability changes in the pool.

### Calibration method
Temperature scaling on label-token logits, held-out calibration split. Poorly
defined for multi-token labels — an open weakness [O].

### Expected router overhead
Prefill + ≥1 decode step on the edge. The only published head-to-head we have:
ConsRoute Table III — generating the tier choice took 36.2 ms (1,868 ms with CoT)
vs 20.9 ms for a hidden-state probe, and was *less* accurate (85.79% vs 87.92% on
GSM8K) [S: d3 §2.1]. One paper, one dataset, not our hardware. **[E]** for us.

### Hardware needed for training
One GPU for LoRA SFT of a 0.5–1.5B model. Feasible in a university lab.

### Hardware needed for inference
Edge device able to hold a 0.5–1.5B model in memory (see `10-lab-requirements.md`).

### Software dependencies
HF Transformers / PEFT (LoRA) for training; a small-model edge runtime
(llama.cpp / vLLM / HF) for inference.

### Existing open-source components
Arch-Router-1.5B (released generative small router) [S: d7 §2]; RouteLLM,
ICL-Router code for prompt patterns [S: d3].

### Closest primary research
Arch-Router (small generative router), ICL-Router (in-context routing)
[S: d3, d7].

### What we borrow from prior work
Prompt-described route policies; label-token-probability scoring.

### What is our proposed implementation choice
Use A **as a released baseline / fidelity anchor**, not as the headline method.

### Main technical risk
Superseded as a contribution — a released generative small router already exists
(Arch-Router-1.5B), and it is slower and (in the one comparison we have) less
accurate than a probe for the same decision [S: d3 §2.1; d7 §2]. The manuscript's
Arch-Router description at L317 ("fine-tune its routing head") does not match a
causal-LM checkpoint — an inconsistency to raise with the advisor [S: d7 §6].

### What would falsify this approach
If A does not beat B and C-pre on **quality at equal-or-better latency**, the
"tiny generative router" premise fails. Current published evidence points the
other way [S: d3 §2.1].

### SIGCOMM relevance
Indirect. Generative routing is an ML mechanism; its systems value shows only
through the cost table it feeds. Weakest SIGCOMM story of the four on its own [O].

### Implementation difficulty
LOW–MEDIUM (LoRA SFT of a released model).

### Implementation sequence
1. Fix the pool and produce per-query route labels (see `06`, `11`).
2. Choose the 0.5–1.5B base; build the prompt template with route list.
3. LoRA SFT on route labels; hold out a calibration split.
4. Temperature-scale label-token logits.
5. Wire the measured cost table and λ knob for the utility-then-cost argmax.
6. Measure edge prefill/decode latency on the target device (not before).
7. Compare against TF-IDF+LR, Arch-Router-as-released, B, and C-pre.

---

## §2. Candidate B — Lightweight discriminative micro-encoder

### One-sentence idea
A small bidirectional encoder with a scoring head maps the query to per-action
utilities in a single forward pass — the plain meaning of "micro-encoder"
[S: d7 §2].

### Why it solves the original paper's problem
It produces `Û(M_k | q)` for the pool directly; combined with the measured cost
table it realises `argmax_a Û − λC` (Eq. 2–3). It is the cheapest and most
reproducible realisation of `f_θ` [O; S: options §2].

### Architecture
```
query q ─► small encoder ─► pooled representation ─┬─► head₁ Û(M₁|q)
          (20–150M)                                ├─► head₂ Û(M₂|q)
                                                    └─► ...  Û(M_K|q)
                                            argmax_a [Û(a|q) − λ·C(a|s)]  (outside net)
```

### Inputs
Query text `q` only. Optionally cheap metadata (length, language, detected PII)
appended as features [P].

### Outputs
One of: **(B1)** binary `p̂(edge suffices | q)`; **(B2)** a vector `Û(M_k | q)`
per pool member (multi-label sigmoid, HyDRA-style capability heads); **(B3)** a
query embedding scored against learned per-model embeddings (RouterDC/CSCR style).

### Definition of f_θ
`f_θ(q, M_k) = Û(M_k | q)` from head `k` (B2), or `sim(e_q, e_{M_k})` (B3). The
selected action is `argmax_a Û(a|q) − λ·C(a|s)` = Eq. (2) with the measured cost
table; for B1, `f_θ` collapses to the sufficiency probability thresholded at τ(λ).

### Parameter / model-size target
20–150M (MiniLM → DeBERTa-v3-small → ModernBERT-base). A μLM-scale 8–30M variant
is a possible lower-bound ablation [P; S: d7 §3.1]. **We do not auto-select
DeBERTa or ModernBERT** — the choice is an ablation (brief §6 B).

### Training target
B1 binary; B2 per-model utility regression / multi-label; B3 contrastive. See `06`.

### Training objective / loss
B1/B2: binary cross-entropy per model + post-hoc temperature scaling on a
held-out split. B3: contrastive loss (RouterDC).

### Label construction
Per-query, per-model correctness/quality from the pool. LLMRouterBench
pre-computed outputs where the pool overlaps, otherwise our own runs
[S: d1 §6; d3 §2.17].

### Inference procedure
1. Encode `q` (one forward pass).
2. Read head outputs → `Û(a|q)`.
3. Subtract `λ·C(a|s)` (measured cost table).
4. `argmax_a` → route.

### How U is estimated
Directly by the heads, calibrated by temperature scaling.

### How C is incorporated
Externally, via the measured cost table (utility-then-cost form). λ is a runtime
knob.

### How network/system state is incorporated
Only through the external cost table. The encoder sees text, not live system
state — a deliberate separation (brief §9 S2/S3) [O].

### How Split-LLM fits
`SPLIT(d)` is just another action with its own utility head and cost row. The
encoder cannot exploit the split computation. If the split path runs the same
model as cloud, its quality equals cloud's and the split-vs-cloud choice collapses
to a cost/leakage rule [S: d8 §3, U1 caveat] — a limitation to state plainly.

### How a new model is added
B3 and a B2 variant with per-model profile vectors can add a model by embedding a
few labelled probes, **without retraining the encoder** (CSCR, HyDRA "zero
retraining") [S: d7 §2]. B1 needs relabelling when the edge SLM changes.

### Whether retraining is required
Not for B3/profile-B2 model additions. Yes for B1 on edge-SLM change.

### Calibration method
Post-hoc temperature scaling per head; standard, well-understood tooling.

### Expected router overhead
One encoder forward pass. Comparable production encoders: HyDRA (ModernBERT, 4
heads) 86 ms median **on CPU**; ComplianceGate reports 7 ms overhead (small
eval) [S: d7 §2]. Not our hardware — **[E]** for us.

### Hardware needed for training
One GPU (or even CPU for the smallest variants); standard fine-tuning.

### Hardware needed for inference
Edge CPU or NPU; independent of the SLM runtime.

### Software dependencies
HF Transformers, standard fine-tuning stack; ONNX/quantisation optional for edge.

### Existing open-source components
RouteLLM-BERT, RouterDC, BEST-Route, HyDRA-style multi-head encoders [S: d7 §2].

### Closest primary research
RouteLLM (encoder router), RouterDC (contrastive model embeddings), BEST-Route
[S: d3, d7].

### What we borrow from prior work
Encoder backbone, per-model heads / model embeddings, temperature calibration.

### What is our proposed implementation choice
Use B (specifically B2/B3) as the **cheap baseline in the head-to-head against
C-pre** that N2 needs, and as the backbone option for D.

### Main technical risk
**Not a contribution on its own** — lightweight encoder routers are standard
[S: d7 §2; d8 §4 "not defensible"]. Needs a second model resident on the edge.
Does not see the edge SLM's internal state, so may predict SLM failure worse than
C [E].

### What would falsify this approach
If B ties TF-IDF+LR (the LLMRouterBench/tinyrouter warning), the learned encoder
adds nothing [S: d3 §4 item 8; d7 §2].

### SIGCOMM relevance
Same as A: value shows only through the cost table and end-to-end effect. Needs
the systems evaluation of `13`/`15` to matter to networking [O].

### Implementation difficulty
LOW (standard fine-tuning, public baseline code).

### Implementation sequence
1. Assemble per-query per-model pool labels (`06`, `11`).
2. Pick the encoder size (ablation: μLM / MiniLM / DeBERTa-small / ModernBERT).
3. Train B2 heads (and B3 embeddings) with BCE / contrastive loss.
4. Temperature-scale each head on a held-out split.
5. Wire the measured cost table + λ argmax.
6. Measure edge forward-pass latency on target hardware (not before).
7. Compare vs TF-IDF+LR, A, C-pre.

---

## §3. Candidate C — Self-routing edge SLM (hidden-state probe)

### One-sentence idea
The edge SLM routes for itself: a tiny head reads its **prefill hidden state**
(pre-generation), optionally its first-`k`-token confidence (post-generation), to
predict whether the edge answer will be acceptable.

### Why it solves the original paper's problem
It produces `p̂(edge suffices | q)` (and optionally per-action utilities), which
thresholds/argmaxes into `R(q)`. It is the only candidate that reuses the edge
SLM's own computation and the only one with a structural link to Split inference
[O; S: options §3].

### Architecture
```
query q ─► edge SLM prefill ─► last-token hidden state (layer ℓ) ─► tiny probe ─► p̂(edge ok | q)
                │                                                                     │
                └──(if EDGE) reuse prefill for generation                    threshold τ(λ) → route
   C-post: + first-k generated tokens' entropies/log-probs
```

### Inputs
**C-pre:** edge SLM hidden state after prefill of `q` (last token, final or an
intermediate layer). **C-post:** additionally the first `k` generated tokens'
entropies / log-probs.

### Outputs
`p̂(edge answer acceptable | q)`; optionally per-action utilities for remote
options.

### Definition of f_θ
`f_θ(q, EDGE) = p̂(edge ok | q) = σ(w·h_ℓ(q))` where `h_ℓ` is the prefill hidden
state; remote actions score `1 − p̂` weighted by the cost table. Selection:
`EDGE` if `p̂ > τ(λ)` else `argmax` over escalation actions by `Û − λC`. This is
the binary-sufficiency reduction of Eq. (3), with τ(λ) the monotone image of λ.

### Parameter / model-size target
Probe of 10K–1M parameters on a 0.5–4B edge SLM. **No separate router model** [P].

### Training target
Binary edge-sufficiency (C-pre); + confidence features (C-post). See `06`.

### Training objective / loss
BCE on the probe → temperature scaling. τ(λ) chosen on a dev split, or per query
cluster (ConsRoute uses Bayesian-optimised cluster thresholds) [S: d3 §2.1].

### Label construction
Whether the edge SLM's answer to `q` was acceptable (correctness, or
judge/reranker agreement with the cloud answer, as in ConsRoute) [S: d3 §2.1].

### Inference procedure
1. Prefill `q` on the edge SLM.
2. Read `h_ℓ` → probe → `p̂`.
3. If `p̂ > τ(λ)`: **reuse the prefill** and generate locally (probe cost ~free).
4. Else escalate; `argmax` over SPLIT/CLOUD by `Û − λC`. C-post first decodes `k`
   tokens for a confidence read before deciding.

### How U is estimated
The probe *is* the utility estimate for EDGE; remote-action utility is a fixed
prior or a small auxiliary head.

### How C is incorporated
Externally via the cost table on escalation; EDGE cost is the local decode time.

### How network/system state is incorporated
Through the cost table at the escalation argmax; the probe itself is
query-conditioned only.

### How Split-LLM fits
**The only candidate with a structural link** [O]. In a Split-LLM the edge already
runs the first layers of the large model; a probe on *those* early-layer
activations (rather than the SLM's) would choose `SPLIT(d)` using computation the
split path needs anyway (this is research P2, only partly pre-empted — ConsRoute
probes the SLM, not the split head) [S: d3 §4 item 2; d7 §5 P2].

### How a new model is added
The probe must be retrained whenever the **edge SLM** changes (labels are that
SLM's capability). Adding cloud models only changes the cost table if the probe
predicts edge sufficiency only [O].

### Whether retraining is required
Yes on edge-SLM change; no for cloud-side pool changes (cost table only).

### Calibration method
Temperature scaling; per-cluster thresholds (ConsRoute). Calibration under domain
shift on edge hardware is **unreported** — an open research part (research U2)
[S: d8 §3].

### Expected router overhead
C-pre: essentially free if the query stays local (prefill reused for generation);
**wasted prefill if the query must leave** [O]. ConsRoute reports 20.9 ms router
latency (Qwen3-1.7B, RTX 3050 laptop GPU) [S: d3 §2.1]. C-post adds `k` decode
steps before any offload decision.

### Hardware needed for training
One GPU to run labelling generations of the edge SLM + train the probe.

### Hardware needed for inference
The edge SLM runtime itself, with hidden-state access (llama.cpp, HF expose them;
closed runtimes may not) [E].

### Software dependencies
An edge runtime exposing hidden states; a tiny probe trainer.

### Existing open-source components
ConsRoute (probe + cluster thresholds), RouteLMT (in-model probe), prefill-
activation routers [S: d3].

### Closest primary research
ConsRoute, RouteLMT, prefill-activation routing [S: d3 §2.1, §4 item 2].

### What we borrow from prior work
Prefill-state probe; cluster-thresholding; consistency labels.

### What is our proposed implementation choice
Use C-pre as the **other half of the N2 head-to-head against B**; use the
split-head-activation variant (P2) as the route into N1 if the advisor chooses
split-aware routing.

### Main technical risk
Prefill-state routing is **occupied** (ConsRoute, RouteLMT); post-gen confidence
is occupied (SWARM-LLM, Pro-Router, DABO). Novelty must come from N1/N2, not the
mechanism [S: d3 §4 item 2; d8 §3]. Wasted prefill on escalation is a real cost.

### What would falsify this approach
If C-pre does not beat B on quality-at-latency (i.e. internal state adds nothing
over query text), or if probe calibration collapses under domain shift.

### SIGCOMM relevance
Higher than A/B: routing cost is folded into inference the system runs anyway, and
the split-activation variant directly touches activation-transfer volume and
split depth — measurable networking quantities [O].

### Implementation difficulty
MEDIUM (hidden-state extraction on the edge runtime + edge-SLM labelling runs).

### Implementation sequence
1. Run the edge SLM over the query set; label edge-sufficiency (`06`, `11`).
2. Extract prefill hidden states at candidate layers ℓ (ablation over ℓ).
3. Train the BCE probe; temperature-scale; fit τ(λ) (global and per-cluster).
4. Measure "wasted prefill" cost on escalation for the cost table.
5. (N1 branch) build the split-head-activation probe variant (P2) and test
   whether early large-model activations predict edge failure — an open empirical
   question [E].
6. Compare vs B, A, TF-IDF+LR.

---

## §4. Candidate D — Structured multi-head utility/cost model

### One-sentence idea
A discriminative model with **several typed, independent heads evaluated in one
pass** (route, edge-ok, sensitivity, expected-length) with full per-head
probabilities and an explicit ABSTAIN — a generation-free reading of Jev's
"parallel questions" interface [P; S: d5 §8].

### Why it solves the original paper's problem
It produces the per-action utility and an explicit policy over `𝒜`, realising
`argmax_a Û − λC`, **and** it makes privacy an explicit variable — which the
manuscript's own motivation (L40, L76) requires but never formalises (formulation
gap 5) [O; S: d1 §3.4; options §4]. It borrows only Jev's *interface*, not its
(undisclosed) architecture [S: d5 §3].

### Architecture
```
query q  (or edge-SLM prefill state)
        │
        ▼
  B- or C-backbone ─┬─► route head       (softmax over 𝒜 incl. ABSTAIN)
                    ├─► edge_ok head      (sigmoid)
                    ├─► sensitivity head  ({none, PII, confidential})
                    └─► exp_length head   (ordinal bucket)
                    policy layer: forbid CLOUD if P(sensitive)>ρ;
                                  length → cost term; argmax_a Û − λ·C(a|s)
```

### Inputs
Query text (B backbone) **or** edge-SLM prefill state (C backbone). The backbone
choice is itself an ablation [P].

### Outputs
A typed record from parallel heads: `route ∈ 𝒜`, `edge_ok`, `sensitivity`,
`expected_length` bucket, optional `domain`. Every head returns probabilities;
none generates text.

### Definition of f_θ
`f_θ(q, M_k) = Û_route(M_k | q)`, with the policy layer imposing hard constraints
from the other heads before the argmax:
`R(q) = argmax_{a ∈ 𝒜_allowed(q)} Û(a|q) − λ·C(a|s)`, where
`𝒜_allowed(q) = 𝒜 \ {CLOUD_LLM}` when `P(sensitivity≠none|q) > ρ`. Length feeds
`C` (decode time ∝ length, Eq. 4). This keeps the policy (ρ, λ, allowed-action
rules) *outside* the weights.

### Parameter / model-size target
The B or C backbone + <1M parameters of heads [P].

### Training target
Multi-task: route/edge-ok = pool labels; sensitivity = privacy labels; length =
measured pool output lengths. See `06`.

### Training objective / loss
Sum of per-head losses (CE / BCE / ordinal) + per-head temperature scaling.

### Label construction
`route`/`edge_ok`: pool outcome labels (as B/C). `length`: measured pool output
lengths. `sensitivity`: **open dependency** — public PII/privacy datasets or
synthetic labels; not yet identified (`11` must resolve). **Jev outputs cannot be
teacher labels — TypeSafe terms forbid distillation** [S: d5 §6].

### Inference procedure
1. One backbone forward pass → all heads.
2. Policy layer computes `𝒜_allowed(q)` from sensitivity.
3. `argmax_a Û − λC` over allowed actions with the measured cost table.

### How U is estimated
Route/edge_ok heads, calibrated per head.

### How C is incorporated
Cost table + the length head feeding decode-time cost; privacy enters as a hard
constraint on the allowed action set, not as a soft term.

### How network/system state is incorporated
Cost table at selection; sensitivity/length are query-conditioned head outputs.

### How Split-LLM fits
Good in the *policy* sense [O]: the sensitivity head gives the Split path a
query-content reason to exist — the action for queries too hard for the edge but
too sensitive for full cloud. This is exactly the "why must split-vs-cloud be
*learned*?" precondition of research N1 [S: d8 §4 N1]. Whether splitting actually
protects such queries depends on split depth and must be **measured** (inversion
attacks), not assumed.

### How a new model is added
Policy (ρ, λ, rules) changes without retraining. Capability heads still need
relabelling on pool change [O]. A profile-vector head (as B2/B3) can soften this.

### Whether retraining is required
No for policy changes; yes (relabelling) for capability-head pool changes.

### Calibration method
Per-head temperature scaling; report per-head reliability.

### Expected router overhead
Same as B or C — one forward pass; extra heads are linear layers, expected
negligible [E, unmeasured]. Jev's own ≥~430 ms gateway latency is **irrelevant**:
D runs on-device [S: d5 §6].

### Hardware needed for training
As B or C + a data effort for the sensitivity head.

### Hardware needed for inference
Edge device, as B or C.

### Software dependencies
As B/C + a privacy-label dataset or synthetic-label generator.

### Existing open-source components
B/C backbones; HyDRA multi-head capability heads; BEST-Route model×samples output
[S: d7 §2].

### Closest primary research
PRISM (AAAI 2026, privacy-aware three-way edge/collaborative/cloud routing);
HyDRA; Jev (interface inspiration only) [S: d4 row I-1; d5; d7].

### What we borrow from prior work
Multi-head capability heads (HyDRA); typed-decision interface (Jev, interface
only); privacy-aware routing framing (PRISM).

### What is our proposed implementation choice
D as a **thin policy layer on top of B or C** — the only candidate that
represents privacy explicitly and thereby earns the learned split-vs-cloud choice.

### Main technical risk
(i) **PRISM already does privacy-aware three-way routing**, so D differs only if
its "collaborative" path is a genuine layer-split path with *measured* leakage
[S: d4 row I-1; d8 §4]. (ii) Sensitivity labels are a new data dependency. (iii)
More heads → more calibration to report. (iv) Multi-head encoders are not new
[S: d7 §2].

### What would falsify this approach
If the sensitivity head cannot be trained to useful accuracy on available/
synthetic labels, or if measured leakage shows split depth does not protect
"sensitive" queries — then the learned split-vs-cloud choice collapses to a rule
and D reduces to B/C.

### SIGCOMM relevance
Strongest of the four [O]: privacy → split-depth → activation-transfer volume and
end-to-end path selection is a networked-systems trade-off with measurable bytes,
latency, and leakage, not a pure classification result.

### Implementation difficulty
MEDIUM (B or C + sensitivity-label data effort + policy layer).

### Implementation sequence
1. Build B or C first (D is a layer on top).
2. Resolve sensitivity labels (`11`) — find a dataset or define synthetic labels.
3. Add heads; multi-task train; per-head temperature scaling.
4. Implement the policy layer (ρ constraint, length→cost).
5. (N1) Measure split-depth leakage (inversion) to justify the learned
   split-vs-cloud choice — an experiment, not an assumption.
6. Compare vs B, C, PRISM's gate, a rule-based split/cloud policy.

---

## §5. Variant A-J — Jacobi-forced generative router (ablation only)

### One-sentence idea
Decode Candidate A's structured multi-token decision with a
**Jacobi-Forcing-trained** router — the *only* reading in which the router itself
is "Jacobi-forced" [S: d6 §9; d7 §5 P3].

### Why it (partly) touches the original paper
The title says "Jacobi-Forced Micro-Encoder". `04-jacobi-role.md` establishes that
no method by that name exists and the literal phrase is incoherent; A-J is the
single technically *possible* placement of Jacobi on the router. It is weakly
justified and **proposed as an ablation, not the method** [O].

### Definition of f_θ
Identical to Candidate A; only the *decoder* of the multi-token label string is
Jacobi-forced. `f_θ` and the Eq. (2)–(3) mapping are unchanged.

### Why it is only an ablation (key facts, all sourced)
- Jacobi Forcing's reported gains (2.57–3.86× on A100) were measured on **long
  code/math generations with 7B models** [S: d6 §6].
- A routing decision is at most tens of tokens; a **single-token** decision gives
  `n = 1` and exactly **1× speed-up** [S: d6 §9].
- The same structured fields come from a multi-head classifier (Candidate D) in
  one pass, with no decode at all [O].

### What would falsify it
If A itself does not beat B/C-pre (§1), the generative-router premise fails before
Jacobi acceleration is even relevant. A-J's only defensible purpose is to test
whether generative routing brings anything; it is not a contribution.

### SIGCOMM relevance
None on its own; it is a micro-optimisation of a mechanism that is not the
systems contribution.

### Implementation difficulty
MEDIUM–HIGH (Jacobi-Forcing post-training of the router LM) for near-zero expected
routing benefit — hence ablation status.

---

## §6. E-J — Jacobi Forcing on the edge generator (NOT a router)

Listed for completeness because it is the only technically natural place for
"Jacobi" in the title [S: d6 §9 J1; d7 §5 P1; d8 §4 N3]. It is **orthogonal to
A–D**: it changes the **cost table** (local decode time `TPOT_edge` in Eq. 4) and,
through the cost table, moves the routing threshold τ(λ). **It does not change the
router**, so it is not a candidate for `f_θ`.

- Needs Jacobi-Forcing post-training of a sub-2B edge SLM ourselves; public
  checkpoints are 7B code/math only [S: d6 §1, §7].
- The speed-up relies on spare compute during memory-bound decoding; **unmeasured
  on edge NPUs or small models** [S: d6 §5, §7] → any benefit is **[E]**.
- It is a separable systems contribution combinable with any of A–D, and it is
  **not** evidence for a "Jacobi-forced router".

E-J is carried in `04-jacobi-role.md`, `08-experiment-design.md`, and
`09-implementation-roadmaps.md` as an optional systems ablation, not as the
routing method.

---

## §7. What all viable candidates share (Reviewer Pass A pre-check)

For each candidate carried as viable (A, B, C, D) the mapping to the fixed problem
is explicit above:

| Candidate | `f_θ` realisation | Selection rule = Eq. (2)/(3)? | Still the original paper? |
|---|---|---|---|
| A | label-token log-prob | `argmax Û − λC` | Yes — literal TLM |
| B | per-model utility head | `argmax Û − λC` | Yes — micro-encoder |
| C | prefill-state sufficiency probe | τ(λ) / `argmax Û − λC` | Yes — lightweight self-router |
| D | multi-head utility + policy over 𝒜 | `argmax_{allowed} Û − λC` | Yes — adds explicit privacy variable the motivation already implies |

None of A–D changes the research question. None replaces the router with a generic
scheduler. **At least two (B and C, with D as a policy layer on either) remain
technically viable and cheap to build**, satisfying the stop condition's viability
requirement. The full comparison matrix and the "no premature winner" discussion
are deferred to `03-method-comparison.md`; the label/target choice to `06`; the
system-cost integration (S1–S4) to `07`.

## §8. Open dependencies flagged by this document

1. **Which hardware is "edge"?** Latency ordering of A/B/C depends on it (advisor
   question) [S: d1 open q4].
2. **Is the split head's activation predictive of edge-SLM failure?** C/D-on-split
   (P2) assumes it; no source tests it [E].
3. **Can split-vs-cloud be learned at all?** If both run the same model, quality is
   equal and the choice is cost+leakage — possibly a rule (D's sensitivity head is
   the proposed, untested answer) [S: d8 §3].
4. **Sensitivity labels** for D — no dataset identified yet (`11`).
5. **Mix-or-Split (IEEE TPDS 2026) unread** — could pre-empt the N1 split-aware
   angle [S: d8 §3].

None of the latency/accuracy figures above were measured by us; they come from
other papers' hardware and must not be carried into `paper/main-revised.tex` as
properties of our design.
