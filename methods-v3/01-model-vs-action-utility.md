# 01 — Model utility versus execution-action utility (Issue A, Issue B)

*Deliverable 01 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 9). Resolves findings RF-A1,
RF-A2, RF-A3 and RF-B from `00-review-findings.md`, and stop items 1 and 12
(model-vs-action resolved; corrected architecture specified at the formulation
level).*

Inputs: `02-split-equivalence-analysis.md` (branches X / L1–L3 / E, the model
specification `M`, E0), `05-full-routing-prior-art.md` (RouterDC, BEST-Route,
IRT-Router, HyDRA, prefill-activation router), `06-systems-prior-art-map.md`
(MCDNN, Edgent, EdgeRL, NetGPT-routing). No new literature was read for this
file; every citation below points to a body reading already recorded in `05`/`06`.
Evidence tags follow `00` §0.

---

## 0. Bottom line

1. **Recommendation `[PROPOSED]`.** Utility attaches to the **model
   specification** `M(a)` that an action executes, not to the action:

   ```
   R(q, s) = argmax_{a ∈ 𝒜} [ Û_θ(M(a) | q) − Δ̂(a, q) − λ · C(a | s) ]        (A1)
   ```

   with `Δ̂ ≡ 0` in the default Branch X of `02`. The student outputs **K
   model utilities**, one per distinct model specification, not `N = |𝒜|`
   action utilities.
2. **Why.** v2's per-action heads (RF-A1) are the *untied* version of (A1). Under
   an exact split they estimate the same target `m` times over. This adds no
   information, multiplies label cost if per-depth labels are actually collected,
   and lets independent head noise decide the split depth, which should be a pure
   cost decision (§3).
3. **Model-level utility is a constraint, not an assumption.** It is the
   parameter-tying constraint "every action that runs the same model gets the
   same utility". The constraint is true exactly when E0 passes (`02` §5.6). If
   E0 fails, the tie is relaxed in the cheapest way the data allows (`Δ̂(d)`,
   then `Δ̂(d,q)`, then per-depth heads). Per-action heads are therefore *one
   branch of the same formulation*, justified only by measured depth-dependent
   quality, which is the condition under which BEST-Route uses action-level heads
   (`05` §1.7).
4. **Faithfulness.** (A1) with `Δ̂ ≡ 0` reduces to the manuscript's Eq. (3)
   `R(q) = argmax_{M_k} f_θ(q, M_k)` with `f_θ(q, M_k) := Û_θ(M_k | q)` literally,
   with no relabelling of `M_k` as an action (§6).
5. **Pool-change claim, rewritten (Issue B).** A new **split depth** of an
   existing model needs E0 at that depth plus cost profiling, and *no* utility
   labels or router training if E0 passes. A new **model** needs labelled
   outcomes, at least a new head trained on the (possibly frozen) encoder, and
   recalibration. Zero/few-shot model addition is **not** a property of our
   architecture; it would require model-profile inputs as in IRT-Router or HyDRA
   (§5). v2's "add an action = add a head" and the manuscript's "without requiring
   costly retraining" (`source/main-original.tex` L40, L65) must not be repeated
   unqualified.

---

## 1. The two formulations, stated precisely

### 1.1 Shared notation

* `𝒜 = {EDGE, SPLIT(d₁), …, SPLIT(d_m), STRONG}` — execution actions.
* `M` — a **model specification**: checkpoint + revision, weight quantization,
  compute dtype, tokenizer and template, decoding config (`02` §1.1). Two runs of
  the same checkpoint at different numerics are different `M`.
* `M(a)` — the specification action `a` executes. `𝓜 = {M(a) : a ∈ 𝒜}`,
  `K = |𝓜|`.
* `𝒜(M) = {a : M(a) = M}` — the **realizations** of model `M`. For the split
  model `M_S`: `𝒜(M_S) = {SPLIT(d) : d ∈ D}`. If `STRONG` runs the same
  specification as the split model, full remote execution is simply the depth
  `d = 0` member of `𝒜(M_S)` (all layers on the server).
* `S(y, q) ∈ [0,1]` — the task score of output `y` (defined in `08`).
* `U(a, q) = E[S(y_a(q), q)]` — true expected score when action `a` answers `q`;
  the expectation is over decoding randomness and the run-to-run noise floor
  (`02` §2.3).

The action→model map was never stated in v2 (RF-A2). It is now part of the
method and has three possible shapes, depending on Henry's model `[OPEN]` → `14`:

| Case | `𝓜` | `K` | Comment |
|---|---|---|---|
| C1: split model ≡ STRONG (same checkpoint, same numerics) | `{M_E, M_S}` | 2 | `STRONG` = `SPLIT(0)` |
| C2: split model ≠ STRONG | `{M_E, M_S, M_L}` | 3 | e.g. 4-bit split model vs FP16 cloud model (`02` §1.1) |
| C3: full paper pool | several edge SLMs, split models, strong models | ≥ 3 | `10` |

### 1.2 v2 formulation (action-level, untied)

```
Û_θ(a | q) = σ(w_aᵀ h_θ(q) + b_a),           a ∈ 𝒜, N = |𝒜| heads
R(q, s)    = argmax_a [ Û_θ(a | q) − λ C(a | s) ]                              (V2)
```

### 1.3 Proposed formulation (model-level, tied, with an optional depth term)

```
Û_θ(M | q) = σ(w_Mᵀ h_θ(q) + b_M),           M ∈ 𝓜, K heads
Δ̂(a, q)    = 0                               Branch X (E0 passes)
           = Δ̂(d)                            Branch L1 (uniform loss, E0 table)
           = Δ̂_φ(d, q)                       Branch L2 (small extra head)
R(q, s)    = argmax_a [ Û_θ(M(a) | q) − Δ̂(a, q) − λ C(a | s) ]                (A1)
```

Branch L3 (one head per `(M, d)`) and Branch E (a semantics-changing split is a
new model `M'`) are also expressible in (A1): L3 sets
`Û_θ(M(a)|q) − Δ̂(a,q) := Û_θ(a|q)`, which is (V2); E adds `M'` to `𝓜`.

**So (V2) is not a competing design. It is (A1) with the tie between realizations
of one model removed.** The question in Issue A is therefore: *is the tie true?*
That is an empirical question with a pre-registered test (E0), not a modelling
taste.

### 1.4 The two-stage reading (exact identity)

For any cost function and any `λ ≥ 0`, in Branch X:

```
max_a [ U(M(a)) − λ C(a|s) ]  =  max_{M ∈ 𝓜} [ U(M) − λ · min_{a ∈ 𝒜(M)} C(a|s) ]
```

because `U(M(a))` is constant on each `𝒜(M)`, so the inner maximization over
realizations only touches the cost. The router therefore factors exactly into

* **a semantic decision** — which model, from `Û_θ(M|q)` and the best achievable
  cost of each model; and
* **a systems decision** — which realization (depth) of the chosen model, from
  `C(a|s)` alone.

The same factorization holds for the constrained form that `09` will recommend
(maximize utility subject to a latency SLA): the feasible realizations of `M` are
`{a ∈ 𝒜(M) : Ĉ_lat(a|s) ≤ SLA}`, and the depth choice is any feasible minimizer of
the secondary cost. `[PROPOSED]` This is the formal content of "split depth is a
system-cost property" in brief §2, and it holds **only** under Branch X.

---

## 2. When the tie holds (Branch X) and when it does not

| Condition | Tie `U(SPLIT(d), q) = U(M_S, q)` for every `q`? | Formulation | Source |
|---|---|---|---|
| Raw same-dtype activation transfer, no early exit, E0 passes against the unsplit noise floor | **Yes** (within the floor) | (A1), `Δ̂ ≡ 0` | `02` §4.1 |
| Cross-device kernels or GPUs differ, E0 still passes | Yes (within the floor) | (A1), `Δ̂ ≡ 0` | `02` §2.3, §4.4 |
| Activation quantization / compression / noise, E0 passes | Yes for that config; config becomes part of `M` | (A1), `Δ̂ ≡ 0` | `02` §4.4 |
| Lossy transform, E0 fails uniformly | No, but the gap is query-independent | (A1) + `Δ̂(d)` (L1) | `02` §4.2 |
| Lossy transform, E0 fails heterogeneously | No, gap depends on `q` | (A1) + `Δ̂_φ(d,q)` (L2) or per-depth heads (L3) | `02` §4.2 |
| Early exit, partition-specific adapters | No — different function | `M'` added to `𝓜` (E) | `02` §4.3; CALM §4 Defs 1–2 |
| Sampling decoding | Tie is in distribution (E-L3), not per run | (A1); `U` is an expectation | `02` §2.1 |

Two consequences that v2 missed:

* **"Same checkpoint" is not enough.** A 4-bit split model and an FP16 cloud model
  of the same checkpoint are different `M` (case C2) and get separate model
  utilities. The tie is between realizations of **one specification**, never
  between "split" and "the strong model" in general.
* **The tie is per depth.** E0 can pass at some depths and fail at others (`02`
  §4.2: monotonicity in `d` is not assumed). Depths that pass share `Û_θ(M_S|q)`;
  depths that fail carry `Δ̂`.

---

## 3. What the untied (v2) design costs under Branch X

### 3.1 Supervision

Under the tie, the Bayes-optimal predictor for every `SPLIT(d)` head is the same
function `q ↦ U(M_S, q)`. v2 must obtain its `m` head targets in one of two ways:

* **Collect labels at every depth** (run the full split pipeline `m` times per
  training query). This is an `m`-fold label campaign through the network for
  targets that are, by assumption, identical up to noise. Model-level labels can
  instead come from **unsplit** runs of `M_S`, or from any single E0-validated
  depth (`02` §4.1).
* **Copy the unsplit label to every depth head.** Then the `m` heads are trained
  on identical targets and differ only through initialization and SGD noise. They
  are `m` noisy copies of one estimator.

There is a further data-source consequence specific to this paper. The manuscript
builds labels from **pre-computed inference results in LLMRouterBench** (L205).
Those are, by construction, unsplit model outputs. They can supply model-level
targets for a matching specification (whether LLMRouterBench's serving numerics
match our 4-bit deployment is `[OPEN]` → `08`/`10`), but they can **never** supply
per-depth targets. Under (V2) every split head would need new split-pipeline runs.

### 3.2 Decision quality: noise picks the depth

Let the depth heads be unbiased estimates `Û(SPLIT(d)|q) = U(M_S,q) + ε_d` with
independent errors of variance `σ²`. For two depths, the depth choice under (V2)
is driven by

```
(ε_{d1} − ε_{d2})  −  λ [C(SPLIT(d1)|s) − C(SPLIT(d2)|s)]
```

The first term has variance `2σ²` and carries **no** quality information. Whenever
the cost gap between depths is small relative to `√2 σ / λ`, (V2) chooses depth
by estimator noise. (A1) chooses the cheapest depth exactly (§1.4). This is a
property of the estimator, not a measured result; it is checked in the optional
ablation of §8.

### 3.3 Calibration

Each sigmoid head needs its own post-hoc calibration (`08`, `03`). (V2) fits
`K + m − 1` calibrators where `K` suffice, each on the same held-out data, and the
calibrated depth heads can still disagree.

### 3.4 Changing the depth set

Under (V2), adding a depth adds a head that needs labels, training and
calibration; removing one leaves a dead head. Under (A1)/Branch X, the depth set
is a runtime configuration of the cost side (§5).

**Conclusion for Issue A, questions 6 and 7:** yes, per-depth heads waste
supervision and force unnecessary retraining when depths change — *under Branch
X*. Under Branch L3 they are the correct design, and the cost is the price of a
real depth-dependent quality effect.

---

## 4. The ten Issue-A questions (brief §2)

| # | Question | Answer | Tag |
|---|---|---|---|
| 1 | When should utility attach to **model identity**? | Whenever all actions that run one model specification produce score-equivalent outputs (E0 passes against the noise floor). This is the default, because brief §5 forbids choosing the lossy branch unless Henry's code requires it. | `[PROPOSED]` |
| 2 | When should utility attach to the **execution action**? | When the action changes the output distribution: a lossy split whose degradation is query-dependent and not captured by `Δ̂(d,q)` (L3), or any procedure whose output is defined by a different function. BEST-Route attaches utility to `(model, best-of-n)` for exactly this reason (`05` §1.7). Early exit is handled as a *new model* (E), which is action-level utility under another name. | `[PROPOSED]`, precedent `[VERIFIED-BODY]` |
| 3 | When can split depths **safely share** one prediction? | Per depth, when E0 passes at that depth for that model specification, including the activation dtype, quantization and compression config (`02` §5.6). Sharing is never assumed for a depth that was not tested. | `[PROPOSED]`/`[OPEN]` (E0) |
| 4 | What if activation quantization/compression makes Split(d) **lossy**? | Keep the model term and add a depth correction: `Δ̂(d)` if the loss is uniform (L1, estimated from E0, reported as a quality term, not converted to milliseconds), `Δ̂_φ(d,q)` if query-dependent (L2), per-depth heads only if L2 fails (L3). Each `(d, bits)` pair is its own action. | `[PROPOSED]` |
| 5 | What if early exit / split execution **modifies inference semantics**? | Then it is a different model `M'` (Branch E) with its own label and head; every exit threshold is a distinct `M'`. It is out of conference scope unless Henry's code does it (`02` §4.3). | `[PROPOSED]`/`[OPEN]` |
| 6 | Does a head per depth **waste supervision**? | Yes under Branch X: `m` targets that are equal up to noise, an `m`-fold label campaign or copied labels, `m − 1` extra calibrators, and LLMRouterBench pre-computed results cannot be used for them (§3.1). | `[PROPOSED]` (argument) |
| 7 | Does it create **unnecessary retraining** when depths change? | Yes under Branch X: adding a depth adds a head that must be labelled, trained and calibrated, while (A1) needs only E0 + cost profiling (§5.1). | `[PROPOSED]` |
| 8 | Which maps most faithfully to `f_θ(q, M_k)`? | (A1): `f_θ(q, M_k) = Û_θ(M_k|q)` is literal, `M_k` stays a model, and the action set enters only through `C` (§6). (V2) has to redefine `M_k` as an action. | `[PROPOSED]` |
| 9 | Which gives the cleanest **systems/ML decomposition**? | (A1): the ML component answers "which model can answer this query", the systems component answers "what does each realization cost now", and §1.4 shows the argmax factorizes exactly. | `[PROPOSED]` |
| 10 | Which is easiest to **implement and falsify**? | (A1): K heads, labels from unsplit runs, and a single binary falsifier (E0) for the tie, with pre-registered fallbacks L1→L2→L3. (V2) has no falsifier for its extra heads: when they agree, they were redundant; when they disagree under an exact split, the disagreement is noise. | `[PROPOSED]` |

---

## 5. Issue B — "add a head without retraining", stress-tested

### 5.1 What each kind of pool change actually requires

| Change | Labelled outcomes for the new item? | Head training? | Backbone fine-tuning? | Recalibration? | Teacher update (if KD is kept, `03`)? |
|---|---|---|---|---|---|
| New split depth, Branch X | **No** (E0 run at `d_new` only) | **No** | No | No (utility unchanged) | No |
| New split depth, Branch L1 | E0 run gives `Δ̂(d_new)` | No | No | `Δ̂` is a new estimate with a CI | No |
| New split depth, Branch L2/L3 | **Yes**, at `d_new` on a training subset | Yes (`φ` or a new head) | Possibly not | Yes | Yes for L3 |
| New network/hardware state | No | No | No | No | No (cost side only; `09`) |
| New model `M_new` | **Yes**: run `M_new` on (a subset of) the training queries and score with `S` | **Yes**: at minimum a new linear head on frozen features | **Unknown** `[OPEN]` — needed if `M_new`'s competence is not linearly decodable from `h_θ(q)` | **Yes**, for the new head; and the decision threshold / `λ` operating points move because the argmax set changed | Yes if the new head is distilled; a hard-label-only head is the cheap option |
| Remove a model | No | No (drop head) | No | Operating points move | No |
| New model, *zero* outcomes | Not supported by a per-model-head router | — | — | — | — |

So the honest claim is narrower than v2's:

> **Rejected `[REJECT]`:** "Adding an action = adding a head (no retraining)"
> (v2 `06` §3.1, §6 table); "adaptable to heterogeneous model deployments without
> requiring costly retraining" (manuscript L40, L65) as an unqualified property.
>
> **Allowed `[PROPOSED]`:** "Because utility is attached to models, a new split
> depth of an already-profiled model changes only the cost side, provided it
> passes the split-equivalence test. Adding a model requires outcome labels for
> that model and training of its utility head; we evaluate the frozen-encoder
> variant of this update in [journal extension / if run]."

### 5.2 Could frozen-backbone + new-head training work?

Plausibly, but it is **not demonstrated** for this router. What is known:

* Linear heads on frozen query embeddings are a standard and often competitive
  router family; LLMRouterBench's embedding routers run on frozen encoders
  (`05` §4). That supports *feasibility*, not *sufficiency* for a new model whose
  failure pattern differs from the existing pool. `[VERIFIED-BODY]` for the fact,
  `[OPEN]` for our case.
* The encoder `h_θ` was fine-tuned to separate the **existing** models' successes;
  features that matter only for `M_new` may have been discarded. Whether a frozen
  head recovers most of the full-retrain utility is an experiment, not a claim.

This belongs to the **journal** extension (changing model pool; `15`). The
conference code keeps the interface (per-model heads addressable by model ID,
per-head calibrators, logged per-model outcomes) so the experiment can run later.
`[PROPOSED]`

### 5.3 What true zero/few-shot pool expansion would need

A per-model head is a learned parameter vector `w_M`; with no outcomes for
`M_new` there is nothing to fit it to. Every routing paper in `05` that claims
cheap model addition makes the **model an input** rather than a head:

* **IRT-Router** embeds a textual model profile and predicts
  `P̂ = σ(aᵀθ_M − b)` (`05` §1.10) — the model enters as a vector computed from its
  description. `[VERIFIED-BODY]`
* **HyDRA** matches predicted capability requirements against static
  benchmark-derived YAML profiles and claims zero retraining on model addition
  (`05` §1.3) `[AUTHOR-CLAIM]`; the profile still needs benchmark scores, and the
  profile-to-routing-quality mapping is not validated in the paper.
* **RouterDC** learns a fixed table of model embeddings, so adding a model needs
  scores for it plus retraining (`05` §1.2) — model embeddings alone do not give
  zero-shot expansion. `[VERIFIED-BODY]` (paper), our reading of Eq. 3–4.

Hence: zero/few-shot expansion requires a **model-profile or model-embedding
input computed without routing labels**. Our conference router does not have
one and must not claim the property. A profile-conditioned head
`Û_θ(M|q) = σ(g(h_θ(q), p_M))` is a candidate journal direction (`15`), not
conference scope. `[PROPOSED]`

---

## 6. Faithfulness to the manuscript (Eq. 1–3)

The manuscript defines `𝓜 = {M_1, …, M_K}` where "each model may correspond to a
small language model deployed on edge devices or a large language model (or
Split-LLM) hosted in the cloud" (L137), and Eq. (3) `R(q) = argmax_{M_k}
f_θ(q, M_k)`.

* Under (A1), `f_θ(q, M_k) := Û_θ(M_k|q)` **unchanged in meaning**: a learned,
  query-conditioned score per model. The split depth never appears inside
  `f_θ`.
* The extension is confined to the decision rule: the manuscript's `C(R(q), q)` in
  Eq. (2) becomes `min_{a ∈ 𝒜(M_k)} C(a|s)`, the cost of the cheapest realization
  of `M_k` in the current state (§1.4). The manuscript already lists
  "offload `q` (or part of it, in Split-LLM settings)" as a decision option (L158),
  so realizations of one model under different partitions are within its problem
  statement.
* (A1) reduces to Eq. (3) exactly when `λ = 0` (or every model has a single
  realization) and `Δ̂ ≡ 0`. v2's reduction (v2 `06` §2) needed split depths to be
  *disabled*; (A1) does not.

---

## 7. Related questions that this decision settles or hands off

### 7.1 Independent sigmoids versus softmax (RF-A3)

v2 argued that a softmax "would entangle the learned utility with the cost term".
`[REJECT]` — a softmax over models is still query-only and never sees `s`. The
correct reasons to prefer independent sigmoids over a softmax are:

1. **Non-exclusive success.** Several models can all answer a query correctly; a
   softmax forces the probabilities to sum to one and so cannot represent
   "everyone succeeds" or "nobody succeeds". The routing decision needs
   `P(success | q, M)` per model, compared against costs, not a distribution over
   which model is "the" answerer.
2. **Calibration per model.** Each sigmoid output can be calibrated against its
   own model's outcomes (`08`, `03`). RouterDC's softmax score over LLMs is not a
   calibrated per-model success probability (`05` §1.2).
3. **Pool edits.** Removing or adding a model changes every softmax output;
   with sigmoids it touches one head (still subject to §5.1).

The softmax remains a legitimate **baseline** shape (RouterDC). `[PROPOSED]`

### 7.2 System state stays out of `Û_θ` — but for the right reasons

(A1) keeps `s` out of the learned utility. This file does **not** justify that by
"network changes would force retraining" (RF-C, `[REJECT]`). The justification
(direct use of fresh measurements, no synthetic state distribution in training,
one semantic router reused across deployments, separately testable parts, and the
fact that depth choice is pure cost under Branch X) is written in `09`.
NetGPT-routing already shows a learned edge score combined with an analytically
network-adaptive threshold (`06`, Eq. 28), and ConsRoute re-tunes thresholds
rather than retraining its encoder (`05` §5, item 3); both are consistent with the
separation without implying that an integrated router *must* be retrained.

### 7.3 Query-dependent cost

`C(SPLIT(d)|s)` depends on the query through prompt length (activation bytes
`B(d, |q|)` during prefill) and output length (per-step decode transfer) (`02`
§6). That makes it `C(a|s,q)`, which is fine: it is still measured or analytically
modelled, not part of the semantic utility. Whether output length is predicted
(a second learned quantity) or bounded by a cap is decided in `09`. `[OPEN]`

---

## 8. Falsification plan (handed to `13`)

| Test | What it decides | Pre-registered outcome → action |
|---|---|---|
| **E0** (`02` §5) at each candidate depth | Whether the tie holds per depth | Pass → Branch X for that depth. Fail → bug check, then L1 / L2 / L3 per `02` §4.4. |
| **E0-heterogeneity regression** (`02` §5.6) | L1 vs L2 | Uniform → `Δ̂(d)` table. Concentrated → `Δ̂_φ(d,q)`. |
| **Optional ablation A-TIE** (cheap: reuses E0 outputs) | Whether untied per-depth heads behave as §3.2 predicts | On the E0 query subset, train (A1) and (V2) with identical budgets; report (i) agreement of depth choice with `argmin_d C`, (ii) model-choice accuracy vs oracle, (iii) calibration. If E0 passed, (V2) should show no utility gain and noisier depth choices; if it shows a real gain, the tie is wrong and E0's δ/ε were too loose. |
| **Journal: frozen-head model addition** (`15`) | Issue B, §5.2 | Report frozen-head vs full-retrain utility for a held-out model; no conference claim either way. |

No result is claimed here. A-TIE is optional because, if E0 passes, its outcome
is predictable from §3 and its main value is reviewer reassurance.

---

## 9. Implementation consequences

* **Router output:** a vector of `K` calibrated model utilities, indexed by model
  specification ID, plus (only in Branch L) a `Δ̂` table or a small `φ` head.
* **Action registry (runtime config, not weights):** for each action `a`:
  `model_id = M(a)`, depth `d`, transfer config (dtype, compression), E0 status
  per depth, and its cost profile. Adding or removing a depth edits this registry.
* **Label store:** outcomes keyed by `(q, model_id)`, with the full model
  specification recorded (`02` §1.1); split runs used only for E0 and for
  Branch L corrections.
* **Logging (forward-compatible, `15`):** per-query `Û_θ(M|q)` for all `M`, chosen
  action, measured cost, and outcome when available.

---

## 10. Manuscript wording

**Allowed `[PROPOSED]`:**

* "The router estimates, for each candidate model, the expected task score of
  that model on the query, $\hat U_\theta(M\mid q)$. An execution action $a$ (edge,
  a split at depth $d$, or remote) runs a model $M(a)$; the runtime controller
  selects the action that maximizes $\hat U_\theta(M(a)\mid q)$ minus its
  measured cost."
* "When the split execution of a model is score-equivalent to its unsplit
  execution, which we test for every split depth, all split depths of that model
  share one utility estimate, and the depth is selected by cost alone."
* "If activation compression degrades quality, we subtract a depth-specific
  quality correction estimated on a held-out set."

**Rejected `[REJECT]`:**

* "Each action, including each split depth, has its own utility head" — unless
  E0 fails heterogeneously (Branch L3).
* "Adding a model or action only requires adding a head" / "without retraining".
* "Split depths have identical quality" without reference to the equivalence test.
* "A softmax would entangle utility with cost."

---

## 11. Consequences for other deliverables

| File | Consequence |
|---|---|
| `03-kd-hardening.md` | KD targets are per **model** (`K` outputs). Teacher and student share the tie; no per-depth soft targets under Branch X. |
| `08-utility-definition.md` | Define `S` and `U(M,q) = E[S]` per model specification; E0's metric uses the same `S`. Decide whether LLMRouterBench pre-computed outputs match our model specifications. |
| `09-cost-policy.md` | Owns `C(a|s,q)`, the constrained/SLA form, and the corrected Issue-C justification (§7.2). Must implement the inner `min_{a∈𝒜(M)}` / feasible-realization step of §1.4. |
| `10-model-pool.md` | Fix the action→model map case (C1/C2) as far as possible without Henry; `K` for the initial pool. |
| `11-baselines-v3.md` | Add RouterDC as the softmax-over-models shape; "content-blind best split" is now automatically the depth policy of (A1), so the baseline must instead be "content-blind model choice + best split". |
| `13-experiments-v3.md` | E0 first; A-TIE optional; E6 tests that the semantic router is unchanged across network states. |
| `14-henry-checklist.md` | Whether the split model is the STRONG model with identical numerics (C1 vs C2); activation dtype/compression (Branch X vs L); early exit/adapters (Branch E). |
| `15-conference-vs-journal.md` | Frozen-head model addition and profile-conditioned heads are journal items. |
| Architecture figure / blue tex | Draw `K` model-utility outputs feeding a runtime optimizer that also takes `C(a|s)`; actions are downstream of the optimizer, not heads of the encoder. |

---

## 12. Sources used (all read in earlier v3 iterations)

| Source | Used for | Status |
|---|---|---|
| BEST-Route (Ding et al., ICML 2025) §3, Eq. 3–5 | Action-level heads justified by distribution-changing actions | `[VERIFIED-BODY]` (`05` §1.7) |
| RouterDC (Chen et al., NeurIPS 2024) Eq. 3–4 | Model-level softmax shape; model embeddings need retraining | `[VERIFIED-BODY]` (`05` §1.2) |
| IRT-Router (Song et al., ACL 2025) Eq. 4–5 | Model as input via profile embedding | `[VERIFIED-BODY]` (`05` §1.10) |
| HyDRA (arXiv 2605.17106) §3.1, Eq. 5, App. H | Profile-based zero-retraining claim | `[VERIFIED-BODY]` paper, claim `[AUTHOR-CLAIM]` (`05` §1.3) |
| Prefill-activation router (arXiv 2603.20895 v3) §3.1, Eq. 1–2 | Per-model P(correct) with additive cost | `[VERIFIED-BODY]` (`05` §1.8) |
| LLMRouterBench (Findings ACL 2026) §4.2.1, Table 10 | Frozen-encoder routers; pre-computed unsplit outputs | `[VERIFIED-BODY]` (`05` §1.4, §4) |
| ConsRoute (arXiv 2603.21237) Alg. 2 | Threshold re-tuning instead of encoder retraining | `[VERIFIED-BODY]` (`05` §1.5) |
| NetGPT-routing (arXiv 2511.22217) Eq. 28 | Learned score + network-adaptive threshold | `[VERIFIED-BODY]` (`06`) |
| CALM (Schuster et al., NeurIPS 2022) §4 | Early exit changes outputs within δ | `[VERIFIED-BODY]` (`02` §8) |
| `source/main-original.tex` L40, L65, L137, L158, L205 | Manuscript claims and problem statement | read, not modified |
