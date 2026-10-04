# 13 — Experiments v3: E0–E8 with pre-registered falsification rules

*Deliverable 13 of `MICROENCODER_HARDENING_BRIEF.md` §27 (brief §25). Prepared
2026-10-04 (gnhf run `microencoder-hardeni-d272f9`, iteration 16). Replaces
`methods-v2/12-conference-experiment-plan.md`, which is left unchanged. Resolves
the experiment hand-offs from `01` §8, `02` §5–6, `03` §10, `07` §7, `08` §9,
`09` §6, `10` §5.2/§6/§11, `11` §4/§6 and `12` §4.2/§5.2/§8, and stop item 3
(E0 exists).*

Evidence tags follow brief §29 and `00` §0. Everything in this file is a
**protocol**: `[PROPOSED]` for the design, `[OPEN]` for anything that depends on
Henry, the advisor, the pool or a pilot. **No experiment has been run. No number
in this file is a result.** Numbers that do appear are sample-size arithmetic,
proposed thresholds that must be frozen before data are seen, or facts already
verified in earlier files (cited by file and section).

Baseline IDs (B-…) are those of `11` §3. Supervision-condition IDs (S1, C\*,
S3-SD, …) are those of `03` §3.2/§9 and `04` §5. The decision rule C-1, `L̂`
and λ are those of `09` §0/§2/§4. Pool, actions and regimes are those of `10`
§6–7. Claim gates C-a … C-g are those of `12` §5.2.

---

## 0. Bottom line

1. **E0 runs first and decides the utility granularity.** Before any `SPLIT`
   label is collected, E0 (`02` §5) compares split against unsplit execution
   per (configuration, depth). PASS means split depths share the model-level
   utility `Û_θ(M_S|q)` (Branch X, `01` §2). FAIL leads, after a bug check,
   to `Δ̂(d)` (L1), `Δ̂_φ(d,q)` (L2) or per-depth heads (L3). No later
   experiment may assume the outcome of E0.
2. **A headroom pilot gates the label campaign.** E-PILOT (`10` §5.2, H1–H4)
   runs on about 500 queries per candidate dataset before the pool and dataset
   list are frozen. A dataset on which the edge model is near 0 cannot be the
   only dataset (`08` §6.2(3)).
3. **Every claim has a pre-registered negative outcome.** E1 can conclude "KD
   did not improve the router over a tuned, calibrated non-distilled student"
   (`03` §10). E2 can conclude that the encoder is unjustified at this data
   scale. E3 can conclude that self-routing dominates after its prefill is
   charged. E7 can conclude that Split is never chosen in the open regime.
   Each of these is a reportable result, not a failure of the plan.
4. **v2's experiments change in five ways.** (a) E0 is new. (b) E1's control is
   C\* plus S3-SD, not α = 1 at fixed hyperparameters. (c) E4 compares KD
   against non-KD + post-hoc calibration, so calibration is no longer a
   novelty lane. (d) E5 evaluates C-1 (utility minus λ·latency inside SLA,
   memory and data-policy constraints) as a frontier, not v2's normalised
   multi-metric scalar. (e) E6 includes the integrated state-input router
   B-INT as a fair challenger, and E7 must report the Split-vs-Remote outcome
   and the chosen split-depth distribution (`12` §4.2).
5. **Three support experiments are added:** E-BB (backbone ladder and export
   fidelity, `07` §6–7), E-COST (accuracy of the latency model `L̂`, `09` §6)
   and the optional A-TIE (untied per-depth heads, `01` §8).
6. **Staging.** The router-side experiments (E1–E4, E8, E-BB) need only the
   label campaign and an edge-class device. E0, E-COST, E6 and E7 need Henry's
   Split code and testbed (`14`). E5 runs twice: first with profiles from the
   available hardware, then on the testbed. Nothing in the router-side stage
   depends on Henry, except that Split labels must wait for E0.

---

## 1. Dependency order and stages

```
E-PILOT (headroom H1–H4)  ──►  freeze pool M0 + datasets + S_D + splits
        │
        ▼
L-GEN (label campaign on our model specifications; unsplit runs only)
        │
        ├──► E-BB / E-BB-Q (backbone ladder, export fidelity)  ──► deployment backbone
        │            │
        │            ▼
        ├──► E1 (KD vs C*)  ──►  E4 (calibration)  ──►  E8 (domain shift)
        ├──► E2 (learned routing value)      E3 (self-routing; shares the M_E prefill pass with T-PI)
        │
Henry's code (14) ──► E0 (split equivalence, per config × depth) ──► Branch X / L1 / L2 / L3
                         │
                         ├──► (only if L1/L2/L3) Split-specific labels or Δ̂ estimation
                         ▼
                      profiling ──► E-COST ──► E5 (testbed) ──► E6 ──► E7
```

| Stage | Experiments | Needs | Gate before the next stage |
|---|---|---|---|
| **P** pilot | E-PILOT; optional pre-pilot on LLMRouterBench released outcomes (`08` §6.1) | GPU time for ~500 queries × candidate specs × datasets | Pool and dataset list frozen (advisor, `10` O-P1/O-P6); MDE estimate from C\* seed variance (§3.4) |
| **R** router-side | L-GEN, E-BB, E-BB-Q, E1, E2, E3, E4, E8; E5 with pre-testbed profiles | Labels on our specifications; one GPU for encoder fine-tunes; an edge-class device for router latency | If E2 shows no gain over B-TFIDF and B-CB (Q1, Q2), the semantic-routing claim is dropped for that pool before testbed work (`12` C-a) |
| **S** systems | E0, E-COST, E5 (testbed), E6, E7, A-TIE (optional) | Henry's repository, hardware and `tc/netem` permission (`14`) | E0 verdict before any Split result is interpreted; E-COST before E6's trace-driven cells are trusted |

Released LLMRouterBench outcomes are **auxiliary only**. They come from other
model specifications (`08` §6.2(2)), they lack SimpleQA for the small-model
pool (`08` §6.1), and no edge SLM or Split model of `10` has outcomes there.
They may be used for the pre-pilot, for code debugging and for an optional
auxiliary pre-training ablation. They are never the labels of a reported
result.

---

## 2. Shared substrate (one campaign, many experiments)

### 2.1 Pool, actions, regimes

* **M0** (N = 2): `M_E` (edge SLM) and `M_S` (Split-capable model), candidate
  pairs P-A, P-B and P-H from `10` §7.2. `[OPEN]` until Henry and the advisor
  decide (O-P1).
* Actions `EDGE(M_E)`, `SPLIT_d(M_S)` for `d ∈ D` (depths exposed by Henry's
  API), `REMOTE(M_S)`. `M(·)` as in `10` §6.
* Two regimes in every systems experiment: **open** (all actions allowed) and
  **private** (`REMOTE` masked by the data policy). The headline regime is an
  advisor decision (`10` O-P3).
* **M1** (N = 3) repeats E1, E2, E5 and E8 once M0 is complete. Multi-model
  baselines (B-RDC, B-IRT, B-ICL) are compared only at M1 (`11` §7).

### 2.2 Datasets, scores and splits

* Datasets: SimpleQA (manuscript) plus at least one dataset on which `M_E` has
  substantial success, chosen from the pilot (`08` §6.2(3), `10` O-P6).
  `[OPEN]`
* Score `S_D` per dataset is fixed by `08` §4 **before** L-GEN and is reused
  unchanged by E0's metric level (`02` §5.3).
* Per dataset, a fixed partition into **train / validation / calibration /
  test** (proposed 60/10/10/20, stratified by dataset and, where available,
  topic). The calibration split is used only for post-hoc maps; the test split
  is touched once per frozen configuration. Teacher folds (`03` §4, F = 5) live
  inside train only.
* The partition, seeds and all thresholds in this file are written to a
  pre-registration file committed before any test-split evaluation.

### 2.3 Label campaign L-GEN

* Run every model specification `M` (weights, numerics, template, thinking
  mode, decoding; `10` §2) on all queries through the pinned evaluator. Store
  the raw grade (letter grade, per-test result), the output, prompt and output
  token counts, and wall-clock on the generating hardware.
* Labels for `SPLIT_d(M_S)` and `REMOTE(M_S)` come from **unsplit** runs of
  `M_S`, valid only for depths that pass E0 (`01` §3.1, `02` §4.1). If E0 fails at a depth,
  Branch L1 uses E0's own outputs to estimate `Δ̂(d)`; L2/L3 need split runs
  on the training queries at that depth. `[OPEN]` on E0.
* Optional **S1-MS**: k sampled runs per (q, M) (`03` O-F3; `11` O-B4). If
  affordable for a dataset, the same k-sample labels are made available to
  every condition (C\* rule, `03` §9).
* One `M_E` prefill pass over all queries stores the activations needed by
  B-PFA, B-EOS and T-PI (`11` §3.E).

### 2.4 Network cells

A grid of emulated `(RTT, BW_up, server load)` cells set with `tc/netem` and a
load generator. Values are fixed after profiling and before test data are used
(`09` §9). The grid is split into **in-range** cells (used to train B-INT and
B-NGPT's α, β) and **held-out** cells (outside the training range in at least
one coordinate) (`11` O-B5). `[OPEN]` on Henry's permissions.

---

## 3. Global statistical protocol `[PROPOSED]`

### 3.1 Primary metrics

* **Decision metric:** realised normalised utility (mean `S` of the chosen
  model, per dataset, then macro-averaged) at pre-registered SLA operating
  points; plus area under the utility–latency frontier over a latency range
  fixed in advance (`09` §4.3).
* **Estimation metric:** per-model Brier score of `Û` on test.
* Secondary: AUROC per model (binary `S`), ECE (15 equal-mass bins), NLL, regret
  against B-OR, teacher–student agreement where relevant.

### 3.2 Inference

* Paired bootstrap over test queries (10,000 resamples, stratified by dataset),
  crossed with seeds where a condition has seeds; 95% percentile CIs of
  differences.
* **Confirmatory family:** Q1–Q7 of `11` §4, adjusted with Holm–Bonferroni.
  Everything else is reported as exploratory and labelled so.
* **Equivalence claims** (E0; "no loss" claims in E6 and E8) use TOST with a
  pre-registered margin. A non-significant difference is never reported as
  equivalence.
* **No fixed "≥ X points" success margin** (v2's margins had no source and are
  withdrawn, `11` §4). A difference counts when its CI excludes 0 and it is at
  least the minimum detectable effect (§3.4).

### 3.3 Seeds and budgets

* ≥ 5 seeds for every E1/E4 condition, the same seed set across conditions.
  ≥ 3 seeds for the E-BB ladder (`07` §6).
* Equal HPO trials and search algorithm for every learned router, KD
  hyperparameters counted inside the KD budget (`03` §9, `11` F3).

### 3.4 Minimum detectable effect

From the pilot, estimate the seed-and-bootstrap standard deviation of C\* on
the primary metrics. Report the minimum detectable effect at 80% power before
the main runs. Results smaller than that are written as "no detectable
difference" in either direction (`03` §10).

### 3.5 Reporting

Per dataset first, then macro average. The mix of metric types is stated in
every caption (`08` §5). All candidates are reported, not only winners
(`07` §6). Oracles (B-OR, B-OU, B-OC) are labelled as unattainable (`11` §3.G).

---

## 4. Support experiments

### E-PILOT — routing headroom `[PROPOSED]`

* **Question.** Does the candidate pool have headroom that a router could
  capture, per dataset?
* **Design.** `10` §5.2: ~500 stratified queries per dataset; H1 mean score
  per model, H2 oracle gain over the best single model, H3 edge-only wins, H4
  fraction the edge answers as well as `M_S`.
* **Decision.** No numeric threshold is pre-set (`10` §5.2). The pool and
  dataset decision is recorded with the pilot numbers and signed off by the
  advisor. A dataset with H1(`M_E`) ≈ 0 may stay only alongside a dataset
  with edge headroom.
* **Also produces:** C\* seed variance for §3.4, and the query-length
  distribution for E-BB-ctx.

### E-BB — backbone ladder and export fidelity `[PROPOSED]` (`07` §6–7)

* **Candidates:** ModernBERT-base, Ettin-68m, Ettin-32m, DeBERTa-v3-small,
  MiniLM-L12-H384; B-TFIDF as the floor.
* **Protocol:** same non-KD protocol (C\*), same heads, equal HPO, ≥ 3 seeds.
* **Rule:** the deployment backbone is the lowest-latency candidate within δ of
  the best validation utility and within the router-overhead budget on the
  edge device (`07` §6). δ is `[OPEN]` (advisor).
* **E-BB-Q:** FP32 vs ONNX-FP32 vs ONNX-INT8 decision agreement, ΔECE and
  Δutility. INT8 latency is quoted only if E-BB-Q passes.
* **E-BB-ctx:** share of queries above 128 and 512 tokens per tokenizer.
* **Claim it supports:** "a compact encoder suffices" (an engineering
  statement), never "ModernBERT is best".

### E-COST — accuracy of the latency model `[PROPOSED]` (`09` §6)

* **Question.** Is `L̂(a | q, s)` accurate enough to route on?
* **Design.** For each action and network cell, predicted vs measured latency:
  MAPE, action-rank agreement, and **decision regret** (utility lost by routing
  on `L̂` instead of measured latency, same `Û`), using B-OC.
* **Negative outcome.** High regret means the cost model, not the semantic
  router, limits the system. A learned queue/tail predictor is then justified
  (`09` §9), and E6's trace-driven cells cannot be used.

### A-TIE — untied per-depth heads (optional) `[PROPOSED]` (`01` §8)

Runs only if E0 passes at ≥ 2 depths. On the E0 query subset, train (A1)
model-level heads and (V2) per-depth heads with equal budgets. Report the
agreement of the depth choice with `argmin_d L̂`, model-choice accuracy and
calibration. A real gain for (V2) means E0's margins were too loose.

---

## 5. Core experiments

Each card gives: question, conditions, measurements, baselines, pre-registered
decision rule, honest negative outcome, gate, and what is `[OPEN]`.

### E0 — Split equivalence test (runs first on the testbed)

* **Question.** For each (configuration, depth), does `SPLIT_d(M_S)` reproduce
  the per-query scores of unsplit `M_S` within its own run-to-run variation?
* **Protocol.** Exactly `02` §5. Query set Q_E0 of n = 500 stratified queries
  plus a long-prompt subset. Reference runs `R_A` (unsplit, batch 1), `R_B`
  (unsplit, deployment batch), `R_C` (unsplit, edge GPU type, if feasible);
  split runs `S_d` per depth. Greedy decoding primary; the deployment sampler
  with k = 8 secondary.
* **Measurements.** Transport level (sha256 before and after serialization,
  shape, dtype, raw and on-wire bytes, check `bytes = shape × dtype size`);
  numerical level (max abs diff, relative L2, cosine of the cut hidden state,
  step-1 logit KL, top-1/top-5 agreement); token level (exact-sequence match,
  first-divergence position, length difference); **metric level** (2×2
  agreement table, flip rate `f_d`, McNemar, TOST on the mean paired score
  difference); sampling level (per-query success-rate difference vs a second
  reference batch); and the configuration log of `02` §5.4 (dtype,
  quantization/compression, serialization, KV placement, versions, decoding,
  seed, link settings).
* **Decision rule** (`02` §5.6, thresholds frozen before E0, advisor confirms
  δ and ε `[OPEN]`): PASS at depth d iff `f_d ≤ f_floor + ε` (proposed ε = 1
  percentage point) **and** TOST shows `|E[S^d − S^ref]| < δ` (proposed δ = 1
  point). Otherwise FAIL → bug check if the transport hashes match → heterogeneity
  regression of the flip indicator on task type, prompt length and output
  length → L1 (uniform) or L2 (predictable). The verdict is per (configuration,
  depth) and is never extrapolated.
* **Negative outcome.** FAIL at a depth is a result: that depth becomes a lossy
  action with a reported quality term, and the Branch L wording of `02` §7 is
  used. "Bit-exact" is written only if hashes and logits match bitwise.
* **Gate.** C-d (`12` §5.2). Also decides which depths may reuse unsplit labels
  in L-GEN.
* **Reuse.** E7 reuses E0's transport logs for byte accounting.
* **`[OPEN]`.** Valid depths, activation dtype, compression, serialization,
  KV handling, sampling location: all from Henry (`14`).

### E1 — Does KD beat direct student training?

* **Question.** Does distilling a larger (or privileged) teacher improve the
  micro-encoder over the strongest non-KD control at identical inference cost?
* **Conditions** (`03` §5, §10). Minimal: B-S1, **B-C\***, B-SD (S3-SD), S3
  with T1-OOF (calibrated, cross-fitted teacher). Secondary if prerequisites
  hold: S3-PI (T-PI from the `M_E` prefill pass), S3-U vs self-training ST,
  B-MS (S1-MS), S3 with in-sample teacher targets (the `03` §4 contrast),
  teacher size ×2, S3-T, S3-RANK, S3-LOGIT. B-T (teacher itself) is reported
  for the student–teacher gap.
* **Interaction with E-BB.** KD gain is measured for at least two student sizes
  from the ladder (`07` §7), so that the conclusion is not an artefact of one
  size.
* **Measurements.** §3.1 primary metrics; secondary AUROC, ECE before and after
  post-hoc calibration, regret vs B-OR, teacher–student agreement.
* **Pre-registered decision rule** (`03` §10, unchanged):
  * "KD adds value" iff an S3 variant beats C\* on the decision metric with a
    paired CI excluding 0, is at least the MDE, and is not worse on Brier.
  * S3 > S1 but S3 ≈ C\* → "the gain is attributable to regularisation or
    smoothing, not to distillation". Ship C\*.
  * S3 ≈ S3-SD > C\* → "self-distillation effect; teacher capacity not needed".
  * S3-PI > S3 > C\* → "privileged-information distillation helps" (still a
    combination of known techniques, `12` K2).
  * No KD condition beats C\* → **"KD did not improve the router over a tuned,
    calibrated non-distilled student in our setting."** C\* is deployed and
    nothing else in the method changes.
* **Data caveat.** Per-dataset reporting is mandatory. On near-floor datasets
  every rung converges (`03` §10).
* **Gate.** C-b. Confirmatory question Q3.

### E2 — Does the learned router beat simple and published routers?

* **Question.** Q1 (does query content matter?), Q2 (is a neural encoder
  needed?), Q5 (does per-model calibrated utility beat pairwise escalation?).
* **Conditions.** The E1 winner (C\* or KD student) vs B-AE, B-AS, B-CB, B-RND
  (matched action rates per λ), B-DP (privileged dataset ID), B-TFIDF, B-FRZ,
  B-RLLM (adapter P, N = 2). At M1 also B-RDC, and optionally B-IRT and B-ICL
  (cost-charged).
* **Protocol.** Every baseline enters the same C-1 rule through the adapters of
  `11` §1.2, under fairness rules F1–F8. Pre-testbed: `L̂` from profiles
  measured on available hardware for `EDGE` and `REMOTE`, labelled as such;
  repeated in E5 on the testbed.
* **Decision rule.** Q1 is supported iff the method's frontier dominates B-CB
  and B-RND at the SLA points with a Holm-adjusted CI excluding 0. Q2 likewise
  against B-TFIDF. Q5 against B-RLLM.
* **Negative outcomes.** Method inside B-CB's frontier → no semantic-routing
  contribution in this pool. No gain over B-TFIDF → the encoder is unjustified
  at this data scale, and the paper says so. No gain over B-RLLM at N = 2 → any
  advantage must come from N ≥ 3 or from the cost integration (`11` §4).
* **Gate.** C-a.

### E3 — Does the micro-encoder beat or complement hidden-state self-routing?

* **Question.** Q4. Is a separate text encoder justified when the edge SLM's
  own prefill activations are available?
* **Conditions.** E1 winner vs B-PFA (prefill-activation router, `05` §1.8),
  B-EOS (ConsRoute-style probe), optional B-LMT. **Complementarity** is tested
  with (i) T-PI distillation (E1 secondary) and (ii) a late-fusion router that
  averages the logits of the micro-encoder and B-PFA, charged the cost of both.
* **Cost accounting** (F6, `11` §3.E). The `M_E` prefill is charged as measured.
  It is not charged for `EDGE` decisions only if the serving stack actually
  reuses the KV cache (`11` O-B3, Henry). Router latency of each family is
  reported p50/p95 on the edge device.
* **Decision rule.** "The micro-encoder is justified against self-routing" iff
  it is not dominated by B-PFA on the cost-charged utility–latency frontier.
  "Complementary" iff fusion or T-PI beats both single sources with a CI
  excluding 0.
* **Negative outcome.** B-PFA dominates after charging its prefill → the
  separate encoder is unjustified for this pool; report it (`11` Q4).

### E4 — Does KD improve or preserve calibration versus non-KD + post-hoc calibration?

The brief lists this inside E3. It is a separate experiment here because it
uses E1's conditions, not E3's.

* **Conditions.** 2 × 2 × 2 factorial over the E1 conditions C\* and S3:
  teacher calibrated before distillation (yes/no, S3 only), student post-hoc
  calibration after training (none / temperature per head; isotonic as an
  ablation), plus the raw and calibrated teacher B-T.
* **Measurements.** ECE (15 equal-mass bins) and binned mean-calibration error
  per model and per dataset, Brier, NLL, reliability diagrams, and the
  decision-level check: regret at fixed λ/SLA (`08` §7).
* **Decision rule.** The only comparison that may support a calibration
  sentence is **S3 + post-hoc** vs **C\* + post-hoc** on the same calibration
  split. Raw (uncalibrated) comparisons are reported but labelled as such.
  "Preserves calibration" requires TOST equivalence on ECE within a
  pre-registered margin `[OPEN]`; "improves" requires a CI excluding 0.
* **Negative outcome.** No difference after post-hoc calibration → no
  calibration claim (C-c is omitted), consistent with `03` §7.3.
* **Gate.** C-c.

### E5 — Utility–latency trade-off sweep

* **Question.** Does C-1 trace a better utility–latency frontier than the
  baselines, and what does it choose?
* **Design.** λ on a log grid including 0 and a value giving always-fastest
  (`09` §4.3). For each λ: realised utility, mean and p95 latency, bytes,
  server GPU-seconds and USD from the same runs (reported, not priced, `09`
  §5). Headline operating point: λ chosen on validation to meet a pre-stated
  mean-latency or remote-call budget, then frozen for test.
* **Baselines.** All adapter-U/P baselines, B-CB, B-RND, B-LO, B-AE, B-AS, and
  oracles B-OR, B-OU, B-OC (`11` §6).
* **Mandatory reports.** (i) Action shares per λ, including the **distribution
  of chosen split depths** (`12` §4.2.3); a single dominant depth is reported
  as such. (ii) Both regimes, open and private. (iii) The deterministic-policy
  caveat: a λ sweep reaches only supported points of the frontier (`09`
  §4.2). (iv) Per dataset and pooled (`08` §5).
* **Negative outcome.** The method's frontier lies inside a content-blind
  baseline's frontier → no routing contribution at that pool and regime.
* **Gate.** C-a (with E2), input to C-f.

### E6 — Bandwidth/RTT variation without retraining the semantic router

* **Question.** With θ and λ fixed, do decisions stay near the oracle-cost
  frontier across network and load conditions, and does a router that takes
  the state as input do better?
* **Clarification.** "Without retraining" holds **by construction** in the
  separated design, because `Û_θ` never sees `s` (`09` §7). The experiment
  therefore tests decision quality across states, not the absence of
  retraining.
* **Design.** Sweep the §2.4 grid with `tc/netem` and the load generator.
  Record decisions, outcomes, latency and regret vs B-OU/B-OC per cell. Cells
  run live on the testbed; extra cells may be **trace-driven** (latency
  recomputed from measured profiles) only if E-COST regret is low, and are
  labelled as trace-driven. Optional variant: online dual ascent on λ for a
  running latency budget (`09` §4.3, not core).
* **Baselines.** B-CB, B-AS, B-LO, B-BAO, B-NGPT and **B-INT** (integrated
  `(q, s)` router trained on in-range cells), evaluated on in-range and
  held-out cells separately.
* **Decision rule.** Q6: C-1 vs B-BAO/B-NGPT at matched latency. Q7: method vs
  B-INT, in-range and held-out, with TOST for "no loss in range".
* **Negative outcomes.** B-INT wins in range → the case for separation rests
  on reuse and out-of-range behaviour only, and Issue C is worded that way
  (`09` §7). B-NGPT matches C-1 → the contribution reduces to the Split action
  set and its measured costs (`11` Q6).
* **Gate.** C-e.

### E7 — Real Split execution

* **Question.** On Henry's system, what do Split actions actually cost, and
  does choosing among `EDGE`, `SPLIT_d` and `REMOTE` improve the frontier?
* **Conditions.** B-ASd for every valid depth, B-AE, B-AS (both realizations),
  the method; each in a subset of E6's cells; open and private regimes;
  at least two concurrency levels for throughput.
* **Measurements** (all measured, none estimated): TTFT, TPOT, end-to-end
  p50/p95/p99; prefill and decode activation bytes per query, raw and on the
  wire; throughput (requests/s and tokens/s); GPU, CPU and memory on edge and
  server; cold-start count and added latency; router overhead p50/p95; energy
  only if a meter or counter is available `[OPEN]`. Warm and cold runs are
  separated, with repetitions per cell for run-to-run variation.
* **Two pre-registered systems checks** (`09` §2.3):
  * **(a) Bytes vs depth.** Regress measured prefill bytes on prompt length and
    depth. For a dense decoder with a residual-only cut, `09` predicts no depth
    effect. A depth effect must be explained (extra state, depth-specific
    compression, or an architecture such as Gemma-4 E-series, `10` §4.2).
  * **(b) Split vs Remote.** Test whether measured TPOT of `SPLIT_d` is at
    least RTT, and count how often C-1 picks `SPLIT_d` in the open regime.
    If Henry's message pattern avoids the per-token round trip (batched,
    speculative or lookahead decoding), record which one and redo `09` §2.3(b).
* **Decision rule.** C-f is supported iff, in the stated regime, the method's
  frontier beats every fixed policy and B-BAO/B-NGPT at matched latency with a
  Holm-adjusted CI excluding 0, **and** the depth distribution is reported.
* **Negative outcome.** Split is never or almost never chosen in the open
  regime → report this and its cause. The Split contribution then rests on the
  private regime or a priced server-compute budget (C-2), or it collapses as
  described in `12` §4.2.2. This is written up, not hidden.
* **Gates.** C-f, C-g.

### E8 — Generalization and domain shift

* **Question.** Did the router learn query properties or the benchmark?
* **Design.** Leave-one-dataset-out when ≥ 3 datasets are used. With 2
  datasets, train on one and test on the other in both directions. Within a
  dataset, a held-out topic or category split where the dataset provides such
  metadata `[OPEN]`. No adaptation, recalibration or replay on the target
  domain: those belong to the journal extension (`15`). Calibration on shifted
  data is only measured.
* **Conditions.** E1 winner, B-DP, B-TFIDF, B-C\*, B-RLLM, B-PFA (`11` §6).
* **Measurements.** Primary metrics per held-out domain; ECE in-domain vs
  out-of-domain; regret vs B-OR.
* **Decision rule.** Generalization is claimed for a held-out domain only if
  the router beats B-RND and B-CB there with a CI excluding 0. The size of the
  in-domain-to-out-of-domain drop is reported for every router.
* **Negative outcome.** B-DP matches the router in-domain while held-out
  domains collapse → the router learned dataset identity, and the "query
  understanding" wording is dropped.

---

## 6. Gate table (`12` §5.2) and confirmatory questions (`11` §4)

| Gate | Clause topic | Experiments | Confirmatory Q | Fallback if the gate fails |
|---|---|---|---|---|
| C-a | Frontier dominates content-blind and lexical baselines | E2, E5 | Q1, Q2, (Q5) | Drop the semantic-routing claim for that pool |
| C-b | KD improves over C\* | E1 | Q3 | "KD did not improve the router over a tuned, calibrated non-distilled student" |
| C-c | KD calibration matches or exceeds C\* + post-hoc | E4 | — (exploratory) | No calibration claim |
| C-d | Split depths score-equivalent to unsplit | E0 | — (TOST per cell) | Branch L wording, `Û − Δ̂(d)` |
| C-e | Same semantic router stays near the oracle-cost frontier across states | E6 | Q7 | Report the failing range; reword Issue C |
| C-f | EDGE/SPLIT/REMOTE choice improves the frontier on real hardware | E7 (+ E5) | Q6 | Report that Split was rarely chosen and why |
| C-g | Measured router overhead | E7, E-BB | — | Report the measured numbers |
| — | Micro-encoder vs self-routing | E3 | Q4 | Separate encoder unjustified for this pool |

---

## 7. Minimum set and run order

**Irreducible conference set:** E0, E1, E2, E5, E7, plus E-PILOT and E-COST.
E0 because model-level utility depends on it. E1 because KD is the
investigated optimisation. E2 and E5 because they decide whether routing
matters at all. E7 because it is the systems evidence. E3, E4, E6 and E8
strengthen the paper. If any is cut, the cut is stated in the paper.

**First runs, in order:**

1. Pre-register partition, `S_D`, thresholds (δ, ε, MDE method, SLA points).
2. E-PILOT on candidate pairs and datasets; advisor freezes pool and datasets.
3. L-GEN on unsplit specifications; `M_E` prefill pass.
4. E-BB and E-BB-Q → deployment backbone.
5. E1 (minimal set) → E4 → E2 → E3 → E8.
6. On receipt of Henry's code: E0 per configuration and depth.
7. Profiling → E-COST.
8. E5 on the testbed → E6 → E7 (both regimes).
9. A-TIE only if E0 passes at ≥ 2 depths and time allows.
10. M1 repeat of E1, E2, E5, E8 with B-RDC.

---

## 8. Corrections to `methods-v2/12-conference-experiment-plan.md`

| v2 item | v3 ruling |
|---|---|
| Hard dependency 2 assumes F5 (`y(SPLIT(d)) = y(full)`) and tests it inside E7 | Replaced by E0, run **before** any Split label or result, with a noise floor and TOST (`02` §5) |
| E1 control: α = 1 at the KD student's hyperparameters | Replaced by C\* and S3-SD with equal HPO budget (`03` §9) |
| E4 frames calibration preservation as novelty lane N2 | Calibration is measured against C\* + post-hoc. No novelty lane (`03` §7.3, `12` §3) |
| E5 uses v2's normalised scalar cost | C-1 (latency only, SLA/memory/data-policy constraints), evaluated as a frontier (`09`) |
| E6 success = route distribution shifts with `s` | A shifting distribution is expected by construction. Success is defined by regret vs the oracle-cost frontier and by Q6/Q7, with B-INT as challenger |
| E7 hypothesis centres on "measured activation bytes" as the novelty quantity (N4) | For dense decoders bytes do not depend on depth (`09` §2.3(a)). E7 tests this and the Split-vs-Remote question instead of assuming Split is attractive |
| E7 hardware "2×RTX 3090, inferred" | Not used. Hardware comes from Henry (`14`) |
| E8 thresholds "ECE ≤ 0.10 in-domain, ≤ 0.15 OOD", "≥ 3/4 folds" and fold list from LLMRouterBench | Withdrawn: no source. Datasets depend on the pilot. Decisions use CIs and TOST |
| "A gap < 2×seed-std is not a win" | Replaced by the MDE computed from the pilot (§3.4) |
| Stage 0 runs E1–E8 on released LLMRouterBench labels | Released outcomes are auxiliary only; they are other specifications and lack our pool (`08` §6.2) |

---

## 9. Open items

| ID | Item | Owner |
|---|---|---|
| O-E1 | δ and ε for E0; TOST margins for E4 ("preserves calibration") and E6 ("no loss in range") | advisor |
| O-E2 | Datasets beyond SimpleQA and the pool pair (`10` O-P1, O-P6) | advisor, after E-PILOT |
| O-E3 | Headline regime, open or private (`10` O-P3) | advisor |
| O-E4 | SLA points, latency budget and λ grid | us, after profiling and before test |
| O-E5 | Network grid and the in-range/held-out split (`11` O-B5) | us + Henry (`tc/netem`) |
| O-E6 | Whether S1-MS labels are affordable (k, datasets) | us, after pilot cost estimate |
| O-E7 | Energy measurement availability on edge and server | Henry |
| O-E8 | Whether the edge stack reuses the `M_E` prefill after a routing decision (E3 cost accounting) | Henry |
| O-E9 | Topic/category metadata for within-dataset shift in E8 | us (dataset inspection) |

---

## 10. Consequences for other deliverables

| File | Consequence |
|---|---|
| `14-henry-checklist.md` | Every `[OPEN]` marked Henry above: depths, numerics, message pattern (per-token round trip vs batched/speculative), KV reuse, energy counters, `tc/netem`, load generator |
| `15-conference-vs-journal.md` | E8 measures shift only; adaptation, recalibration and replay are journal items |
| `proposed-solution-blue-v3.tex` | Future tense for every evaluation sentence; the shared-utility design stated as conditional on E0 |
| `FINAL-SUMMARY-v3.md` | Q26 (first 10 steps) can draw on §7. No result may be quoted from this file because none exists |
