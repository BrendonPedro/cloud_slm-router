# 12 — Conference Experiment Plan

*Deliverable 12 of the methods-v2 micro-encoder+KD sprint (brief §17). This is a
**plan**, not a result. No router has been trained, no teacher distilled, and no
systems measurement has been taken. **Zero numbers below are measured** — brief
§26 forbids presenting estimated latency as measured and §25.Q12 forbids
inventing results. Everything here is a pre-registered design to be executed
**after** advisor approval and **after** Henry's Split-LLM code arrives.*

Evidence tags: **[VERIFIED]** primary source; **[RELATED]** adjacent prior work;
**[PROPOSED]** our design; **[OPEN]** requires experiment/advisor/Henry;
**[M]** measured only from the already-released LLMRouterBench bundle (sha256
`b79f8cde…48c8f1`) — the *only* real numbers this sprint may cite.

> **Scope-lock check.** Every experiment below evaluates the *same* router
> `R(q,s)=argmax_a[Û_θ(a|q) − λ·C(a|s)]` (methods-v2/06 Eq.(4), the approved
> reduction of the manuscript's Eq.(3) `R(q)=argmax_{M_k} f_θ(q,M_k)`). No
> experiment changes the research question; they differ only in *which term* of
> `U − λC` they stress and *which component* (KD, teacher, cost, Split) they
> isolate. λ and the live state `s` stay run-time knobs throughout.

---

## 0. What this plan must do, and its two hard dependencies

The brief (§17) demands the **minimum** experiment set that can (a) confirm or
**falsify** the distilled micro-encoder, and (b) support *only* the two novelty
axes that survived the stress test (methods-v2/11):

- **N2** — calibration preserved through distillation (gated on **E1/E4**).
- **N4** — measured Split activation bytes (gated on **E7**).

Two dependencies gate the whole plan and must be stated up front so no reviewer
reads a promise as a result:

1. **KD must earn its place.** brief stop-condition #4 explicitly permits
   concluding KD adds no value. **E1 is the falsification test**: if the distilled
   student does not beat the α=1 non-distilled control at matched size, KD is
   reported as a *negative result* and dropped from the conference core
   [PROPOSED, gated on E1; methods-v2/03 §recommendation, 11 §N1].
2. **Split numbers depend on Henry + losslessness.** E6/E7 cannot run until
   Henry's code arrives (methods-v2/09 checklist, all [OPEN]) **and** the F5
   losslessness assumption `y(SPLIT(d),q)=y(full,q)` is empirically confirmed
   (methods-v2/07 §3, 09 §F5). If F5 fails, 06/07 need a per-depth quality head
   and this plan's Split rows change [OPEN].

### Staging (inherited from v1 methods/08 §0, retargeted to the KD method)

| Stage | Experiments | Needs | Gate |
|---|---|---|---|
| **Stage 0** (CPU, ~zero inference) | E1, E2, E3*, E4*, E5*, E8 on **released quality labels** | LLMRouterBench bundle [M] | if E1 falsifies KD → drop KD before any GPU spend |
| **Stage 1** (bounded GPU) | E1–E5, E8 on the **manuscript's real edge pool** | GPU to run real models + build labels | if E2/E3 falsify the learned router → reframe (N2 only) |
| **Stage 2** (edge↔server testbed) | E6, E7 (+ E5 re-run with measured C) | Henry's Split-LLM + testbed + F5 check | the only stage that makes this a *systems* paper |

\*E3/E4/E5 run partially at Stage 0 (released-label proxies) and fully at Stage 1.
Stages gate each other: a Stage-0 falsification of E1 changes the paper before any
expensive Split work is worth doing.

---

## 1. Experiment-to-claim map (why each experiment exists)

| Exp | Question it answers | Isolates | Gates novelty |
|---|---|---|---|
| **E1** | Does distillation help at all? | KD vs no-KD at matched student size | N1 (negative→drop), **N2** |
| **E2** | Does the learned router beat trivial/simple baselines? | learned vs TF-IDF/always-X/random | precondition for *any* claim |
| **E3** | Does it beat the demoted Candidate-C hidden-state router? | pre-gen encoder vs prefill-probe | positions C as baseline (brief §14) |
| **E4** | What does the student keep/lose vs its teacher? | student vs teacher: quality/**calibration**/params/latency | **N2** |
| **E5** | Does the decoupled cost term behave? | route quality across λ | N3 (cost separation) |
| **E6** | Does the router react to the network? | route distribution across BW/RTT | N3/N5 (adaptivity) |
| **E7** | Real Edge vs Split cost | measured TTFT/TPOT/bytes/e2e | **N4** (strongest systems axis) |
| **E8** | Does it generalize off-domain? | in-domain vs leave-one-dataset-out | guards against "learned the benchmark" |

The two **boldface** novelty axes (N2 calibration, N4 Split bytes) are the paper's
defensible contribution (methods-v2/11 §contribution sentence); every other row is
either a precondition, a baseline-positioning, or a negative-result guard.

---

## 2. Shared experimental substrate (one campaign, many experiments)

Reused verbatim from v1 methods/08 §2–3 — the economy is that **one** per-(action,
query) quality table feeds every target and every experiment [S: v1 06, 08]:

- **Datasets (Stage 0, released binary-scored splits):** `mmlupro/test_1000`
  (998), `gpqa/test` (198), `livecodebench/test` (1055), `livemathbench/test`
  (121), `aime/hybrid` (60) = **2,432 unique queries** [M]. `arenahard*` excluded
  from the primary pool (judge win/tie/loss, not accuracy); optional soft-label
  secondary [M].
- **Datasets (Stage 1, real pool):** SimpleQA (n≈4,326) + the Stage-0 sets,
  re-run on the manuscript's real edge models — **required** because none of the
  manuscript pool has SimpleQA records in the bundle (methods-v2/10 §label-source;
  Route P-A, our own inference campaign) [M, OPEN pool].
- **Two headroom regimes (keep both):** **P-L (nested)** weak→strong where oracle
  barely exceeds always-cloud ⇒ primary metric is *cloud-call rate at matched
  quality*; **P-Q (complementary)** where the weak model wins some queries ⇒ a
  router can *raise* quality [M; methods-v2/10 §oracle-headroom MP2].
- **Action set:** 𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD} (methods-v2/06 §2).
  Because `y(SPLIT(d),q)=y(full,q)` (07 §3), the **learned** utility axis is
  essentially binary (edge-class vs strong-class); Split is differentiated
  *entirely* by the measured cost term (08 §3). ⇒ **Stage 0/1 experiments on
  quality labels treat SPLIT≡STRONG for Û**; SPLIT only becomes a distinct action
  in Stage 2 (E6/E7) where `c_comm` separates it.
- **Label leakage discipline:** query-string dedup before splitting; frozen
  query-hash→split files hashed before any router trains; test split opened once
  per final config [S: v1 08 §3].

---

## 3. The experiments (brief §17 structure: hypothesis / IV / DV / baseline /
## success / falsification / hardware / data)

Every hypothesis is stated in **pre-registered, falsifiable** form; the null is
always "paired-bootstrap 95% CI on the primary-metric difference includes 0"
(brief §23; v1 08 §1). Thresholds marked [PROPOSED] are advisor-confirmable
(§5 open questions).

---

### E1 — Standard micro-encoder vs **distilled** micro-encoder *(the KD falsification test)*

- **Hypothesis [PROPOSED].** At matched student backbone (ModernBERT-base ~149M,
  05) and matched inference latency, the **distilled** student (KD-5 hybrid,
  α<1, teacher=ModernBERT-large ~395M) achieves a strictly better routing
  quality/cost frontier **and/or** strictly better calibration than the
  **non-distilled control** (KD-5 with **α=1**, i.e. hard labels only). [03 §KD-5;
  11 §N1]
- **IV.** Distillation on/off, operationalised as the KD weight α ∈ {1.0 (control),
  0.75, 0.5, 0.25} (an **α-sweep**, 03 §recommendation). Teacher fixed.
- **DV.** Primary: CCR@−1 (cloud-call rate at quality ≥ strong−1pt). Secondary
  (the N2 quantity): **ECE (15-bin), Brier score** of the per-action P̂(success).
- **Baseline.** The α=1 non-distilled student — *the* control; this is literally
  "the same architecture without KD".
- **Success [PROPOSED].** Some α<1 beats α=1 on CCR@−1 by ≥ advisor-set margin
  (Holm-adjusted 95% CI excludes 0, pooled in-domain) **or** lowers ECE by ≥ 0.02
  at non-inferior CCR@−1.
- **Falsification [PROPOSED].** No α<1 beats α=1 on either quality or calibration
  (CI includes 0 everywhere) ⇒ **KD adds no value; drop KD from the conference
  core and report as a negative result** (brief stop-cond #4). N1 becomes negative;
  N2 cannot be claimed.
- **Hardware.** Stage 0: CPU (released labels). Stage 1: GPU to build real labels
  + train both students + the teacher.
- **Data.** Stage 0: released quality table [M]. Stage 1: Route P-A labels [OPEN].

---

### E2 — Distilled micro-encoder vs **simple baselines** *(does a learned router earn its keep?)*

- **Hypothesis [PROPOSED].** The distilled student reaches a strictly better
  quality/cost frontier than *every* simple baseline: always-edge, always-strong,
  always-split (fixed d), random@matched-rate, dataset-prior, and
  **TF-IDF(1–2gram)+logistic regression** (the bar). [brief §14; v1 08 §5]
- **IV.** Router identity (distilled student vs each baseline).
- **DV.** CCR@−1; deferral AUC (quality vs cloud-call-rate curve); RouteLLM APGR /
  CPT(50%) for cross-paper comparability [RELATED: RouteLLM metrics].
- **Baseline.** TF-IDF+LR is the primary bar (LLMRouterBench's "routers often tie
  simple baselines" warning makes this the decisive test) [RELATED: LLMRouterBench;
  methods-v2/01 §LLMRouterBench]; oracle (per-query max) is the upper bound.
- **Success [PROPOSED].** CCR@−1 lower than TF-IDF+LR by ≥ 5 pts, Holm-adjusted
  95% CI excluding 0, pooled in-domain; beats random@rate **and** dataset-prior on
  deferral AUC.
- **Falsification [PROPOSED].** TF-IDF+LR (or dataset-prior) is within the CI of
  the distilled student in-domain ⇒ repeats the "ties a simple baseline" finding;
  the contribution must rest on N2 calibration / N4 systems, not on routing
  accuracy.
- **Hardware.** Stage 0: CPU (v1 already ran the stdlib Stage-0 baselines, 08 §13).
  Stage 1: GPU for the real-pool labels.
- **Data.** Stage 0 released table [M]; Stage 1 Route P-A [OPEN].

---

### E3 — Distilled micro-encoder vs **hidden-state baseline** *(Candidate C, demoted)*

- **Hypothesis [PROPOSED].** The **pre-generation** distilled encoder is
  non-inferior (on CCR@−1) to a **hidden-state self-router** — a logistic probe on
  the edge SLM's own prefill hidden state (Candidate C, now a baseline per brief
  §14 and advisor decision #6) — while avoiding C's cost of an 8B-class forward
  pass before routing. [methods-v2/00 §decision-6; v1 02 §C]
- **IV.** Routing signal source (external micro-encoder embedding vs internal
  prefill hidden state).
- **DV.** CCR@−1; **and router-side latency/FLOPs** (the whole point — C needs a
  partial forward pass of the edge model *before* it can route).
- **Baseline.** C-pre: logistic probe on the weak model's prefill hidden state
  (needs GPU 8B forward passes) [v1 08 §4].
- **Success [PROPOSED].** Distilled encoder within 2 pts CCR@−1 of C-pre
  (one-sided non-inferiority) at **≥ 10× lower routing-side latency**.
- **Falsification [PROPOSED].** C-pre beats the encoder on CCR@−1 beyond CI *and*
  its extra latency is tolerable ⇒ the hidden-state route is the better method and
  the micro-encoder framing weakens.
- **Hardware.** Stage 1 (GPU): C-pre needs 8B forward passes over 2,432 queries
  (not runnable on the v1 CPU host, 08 §12).
- **Data.** Route P-A labels [OPEN].

---

### E4 — **Teacher vs student** *(quality / calibration / parameter count / latency — the N2 axis)*

- **Hypothesis [PROPOSED].** The distilled student recovers most of the teacher's
  routing quality **and preserves its calibration** at a large parameter/latency
  reduction (ModernBERT-large ~395M → base ~149M, 05). Calibration preservation is
  the **N2 claim** and must be stated as the measurable quantity. [11 §N2]
- **IV.** Model (teacher T1 vs distilled student vs non-distilled student +
  post-hoc temperature scaling).
- **DV.** CCR@−1; **ECE / Brier / reliability curves**; parameter count [M-cardable];
  router p50/p95 latency (CPU **and** GPU; ONNX-INT8 path, 05 §R6).
- **Baseline.** The obvious alternative to KD-for-calibration: **non-distilled
  student + temperature scaling** (the baseline N2 must beat; 11 §N2).
- **Success [PROPOSED].** Distilled student is **better calibrated** (lower ECE)
  than the non-distilled+temperature student at matched CCR−1 and matched latency;
  AND recovers ≥ (teacher − small margin) on CCR−1 at < ½ the teacher's params.
- **Falsification [PROPOSED].** Non-distilled+temperature matches the distilled
  student's ECE ⇒ **N2 collapses** (calibration was free via temperature scaling,
  not from KD); N2 is dropped.
- **Hardware.** Stage 0 proxy on released labels (train both + a large-encoder
  teacher on CPU if feasible); Stage 1 full on GPU.
- **Data.** released table [M] / Route P-A [OPEN].

---

### E5 — Route quality **under changing λ** *(the decoupled cost term behaves)*

- **Hypothesis [PROPOSED].** Sweeping λ in `argmax_a[Û_θ(a|q) − λ·C(a|s)]`
  (06 Eq.(4); SC1 scalar = Lagrangian dual of the SC3 budget, 08 §scalarization)
  traces a **monotone, well-behaved quality↔cost frontier** *without retraining* —
  the structural payoff of keeping cost outside θ (N3). [08 §SC1; 11 §N3]
- **IV.** λ swept over a grid (e.g. 0 → large), at **fixed** trained θ.
- **DV.** Quality (routed-system accuracy) vs cost (cloud-call-rate at Stage 0/1;
  measured bytes/latency at Stage 2); the resulting Pareto curve (SC4).
- **Baseline.** A **λ-in-weights** design (cost folded into the net) that would
  need retraining per operating point — shows structurally why the decoupled form
  wins (v1 08 §7 finding) [RELATED].
- **Success [PROPOSED].** A single trained θ produces the full frontier; endpoints
  recover always-edge (λ→∞) and always-best-quality (λ=0); curve is monotone
  non-increasing in cost.
- **Falsification [PROPOSED].** The frontier is non-monotone or no λ beats
  always-edge/always-strong ⇒ the cost term is not informative / Û is miscalibrated
  across actions.
- **Hardware.** Stage 0/1 CPU/GPU on quality labels (cost = cloud-call-rate proxy);
  Stage 2 re-run with **measured** C.
- **Data.** released/Route P-A [M/OPEN]; Stage-2 measured C [OPEN, Henry].

---

### E6 — Route changes **under changing bandwidth / RTT** *(network adaptivity — Stage 2)*

- **Hypothesis [PROPOSED].** With `C(a|s)` carrying **measured** BW/RTT (08 §s
  vector), sweeping the network at **fixed θ** shifts the route distribution
  toward EDGE as BW drops / RTT rises, and the learned router beats a
  **fixed-threshold** systems policy. [11 §N3/N5; v1 08 §7 BW/RTT row]
- **IV.** Network condition `s` swept with `tc/netem` (bandwidth, RTT).
- **DV.** Route distribution over 𝒜; e2e p50/p95 latency; cloud/split-call rate.
- **Baseline.** Fixed BW-threshold policy; fixed RTT-threshold policy; the
  **system-state-only scheduler** (ignores query content — isolates the value of
  *query awareness*, the S4 baseline) [v1 08 §5].
- **Success [PROPOSED].** Route distribution shifts significantly with `s` (not
  invariant) **and** the learned router achieves lower e2e latency at matched
  quality than the best system-only rule, across ≥ 2 network conditions,
  CI excluding 0.
- **Falsification [PROPOSED].** Route distribution invariant to `s` (router ignores
  the network) **or** the fixed-threshold policy is within CI everywhere ⇒
  adaptivity claim (N3/N5) reduces to a systems policy.
- **Hardware.** **Stage 2 testbed** (edge server + cloud server + `tc/netem`
  link) — cloud HW undefined in manuscript L200 → advisor question (16) [OPEN].
- **Data.** trained θ from Stage 1 + live `s` sweep [OPEN, testbed].

---

### E7 — **Measured Edge vs Split execution** *(the N4 systems core — strongest, most at risk)*

- **Hypothesis [PROPOSED].** On a **real** Split-LLM (Henry's code, 09), the
  SPLIT(d) action, selected via measured `c_comm` (activation bytes) + `c_lat`,
  gives a better quality-vs-{latency,bytes} frontier than always-edge /
  always-strong / always-split at fixed d. **This is the only lane genuinely
  unoccupied among routers (N4) and is entirely gated on Henry + F5.** [11 §N4;
  09; 07 §F5]
- **IV.** Execution path (EDGE / SPLIT(d) for each available depth d / STRONG) and
  router on/off.
- **DV (all measured, none estimated — brief §26):** TTFT; TPOT; e2e
  p50/p95/p99; **transmitted activation bytes per query** (the N4 quantity);
  throughput (req/s, tok/s at fixed quality); GPU utilisation (edge + server);
  memory; operational cost if defensibly modelled (08 §operational).
- **Baseline.** always-split at fixed d; always-edge-then-escalate; the system-only
  scheduler (v1 08 §5/§7).
- **Success [PROPOSED].** The learned router with a SPLIT action beats the best
  fixed policy on e2e latency **or** activation bytes at matched quality, CI
  excluding 0, across ≥ 2 network conditions.
- **Falsification [PROPOSED].** The fixed "sensitive→SPLIT else cost-optimal" rule
  is within CI everywhere ⇒ Split reduces to a systems policy; **or** the **F5
  losslessness check fails** (`y(SPLIT(d),q)≠y(full,q)`) ⇒ the quality model needs
  a per-depth head and 06/07 must change before E7 is valid [09 §F5].
- **Hardware.** **Stage 2 testbed + Henry's Split-LLM**; both [OPEN] (09 checklist,
  every row unresolved). Edge server L200 (2×RTX 3090, inferred [M-ish]); cloud
  server undefined [OPEN].
- **Data.** Henry's activation tensor shape/dtype at the cut (the single most
  load-bearing [OPEN] quantity, 09 §activation) + live `s` [OPEN].
- **Discipline.** Until E7 is actually run, the paper writes "we **will** measure",
  never "we measured" (brief §26; 11 §N4).

---

### E8 — **Domain-shift / generalization** *(guards against "learned the benchmark")*

- **Hypothesis [PROPOSED].** The distilled router generalises off-domain:
  leave-one-dataset-out (LODO) quality degrades gracefully and still beats
  random@rate + dataset-prior — i.e. it did not merely learn "which benchmark is
  this". [v1 08 §9; LLMRouterBench OOD warning, 01]
- **IV.** Train/test domain split: in-domain (60/20/20) vs 4 LODO folds over
  {MMLU-Pro, GPQA, LiveCodeBench, math=LiveMathBench∪AIME}.
- **DV.** CCR−1 and deferral AUC per fold; **ECE in-domain vs averaged-OOD** (does
  KD-preserved calibration survive distribution shift — ties N2).
- **Baseline.** dataset-prior router (the information-leak control); random@rate.
- **Success [PROPOSED].** Beats random@rate + dataset-prior on deferral AUC in
  ≥ 3/4 OOD folds; ECE ≤ 0.10 in-domain, ≤ 0.15 averaged OOD.
- **Falsification [PROPOSED].** The dataset-prior router is within CI of the
  distilled router in-domain while OOD folds collapse ⇒ the router learned the
  benchmark, not the query → the "query understanding" requirement fails.
- **Hardware.** Stage 0 (CPU) on released labels + Stage 1 (GPU) on the real pool.
- **Data.** released table [M] / Route P-A [OPEN].

---

## 4. Statistics, splits, and the minimum vs full set

- **Statistics [PROPOSED, S: v1 08 §8]:** paired bootstrap (10,000 resamples,
  stratified by dataset) for CCR−1 / deferral AUC / ECE differences, 95%
  percentile CIs; McNemar's exact test at the dev-selected operating point;
  **Holm–Bonferroni** across {routers} × {P-L, P-Q} × {in-domain, 4 OOD folds};
  **5 seeds {0..4}**, a gap < 2×seed-std is not a win even if the CI excludes 0.
- **Power caveat [E]:** at 20% test (~486 pooled) per-dataset CIs are several
  points wide ⇒ per-dataset numbers are descriptive; only the pooled test is
  confirmatory (v1 08 §8).
- **Minimum conference set.** If resources force a cut, the **irreducible** core is
  **E1 (KD falsification) + E2 (beats simple baselines) + E4 (N2 calibration) +
  E7 (N4 Split bytes)** — one per surviving-or-gating claim. E3/E5/E6/E8 strengthen
  but do not by themselves carry the contribution. Any such cut must be
  `log()`-style disclosed in the paper, not silently dropped.

---

## 5. Open questions (advisor) — carried to deliverable 16

1. Confirm the quantitative thresholds (5-pt CCR margin, 2-pt non-inferiority,
   0.02 ECE margin for N2, 0.10/0.15 ECE bars, ≥2-network-condition bar for E6/E7).
   [brief §17 success/falsification]
2. Confirm the **model pool** that defines P-L/P-Q for the real Stage-1 pool, and
   the **label route** (P-A own-inference vs P-B flagship) — mutually exclusive
   (methods-v2/10 §label-source).
3. Confirm **Split-LLM framework + cloud-server hardware** for Stage 2 (undefined,
   L200/L202) — blocks E6/E7.
4. Is the **F5 losslessness** check (09) a precondition the advisor accepts as
   gating E7, or should 06/07 carry a per-depth quality head from the start?
5. Does `arenahard*` enter as a secondary soft-label pool? [v1 08 §14]

## 6. What this plan does **not** do (constraint check, brief §26)

- Does **not** run any experiment this sprint (brief §17 "Do NOT run these").
- Does **not** present a single estimated latency/byte number as measured.
- Does **not** assume KD helps (E1 is its falsifier).
- Does **not** turn Split into a cloud API (E7 requires Henry's real split; 09).
- Does **not** invent Henry's code, hardware names, or the final model pool.
- Does **not** modify `source/main-original.tex`.

---

*Cross-refs: hypotheses and staging inherited from v1 `methods/08-experiment-design.md`
and `architecture/recommended-experiment.md`; novelty gating from
`methods-v2/11-novelty-stress-test.md`; method/f_θ from `06`; labels from `07`;
cost/scalarization from `08`; Split dependency from `09`; pool/baselines from `10`.
Feeds the journal extension (`13`), publication staging (`14`), and FINAL-SUMMARY
Q12/Q13/Q20. Original manuscript unmodified.*
