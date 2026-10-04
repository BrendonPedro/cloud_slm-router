# 08 — Precise definition of utility (brief §14)

*Deliverable 08 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 10). Resolves finding RF-F
("probability of success" undefined) from `00-review-findings.md` and supplies
the `S` and `U` that `01` §1.1 and `02` §5 (E0 metric) defer to this file.*

Inputs: `01` (model specification `M`, formulation A1), `02` (noise floor,
E-L2/E-L3 equivalence), `04` (supervision conditions S1/S1-MS/S2/S2-J/S3/S4),
`05` (target choices of RouteLLM, BEST-Route, Hybrid LLM, prefill router,
IRT-Router, HyDRA). New primary-source checks made for this file (2026-10-04):

* SimpleQA paper (Wei et al., arXiv 2411.04368, HTML body §2.4 and Table 3).
* LLMRouterBench repository `ynulihao/LLMRouterBench@main`: `README.md`
  (dataset and model-pool tables), `evaluation/SimpleQA/simpleqa.py`,
  `evaluation/SimpleQA/prompts.py`, `config/baseline_config_performance_cost.yaml`,
  `config/baseline_config.yaml`, `config/data_collector_small_model_config.yaml`.

Evidence tags follow `00` §0. `[CODE]` means "read in the official repository
source at `main` on 2026-10-04". It is code evidence, not paper evidence.

---

## 0. Bottom line

1. **General definition `[PROPOSED]`.** Utility is the **expected normalised
   task score of a model specification on a query**:

   ```
   U(M | q) := E_ξ [ S_D(y_M(q; ξ), q) ] ∈ [0, 1]                      (U1)
   ```

   `S_D` is the score function of dataset `D`, pinned in advance and mapped to
   [0,1]. `ξ` collects every source of randomness in a run: decoding samples,
   run-to-run numeric noise (`02` §2.3) and grader stochasticity.
   The student estimates `Û_θ(M | q) ≈ U(M | q)`.
2. **Binary and graded tasks become one object.** If `S_D ∈ {0,1}`, then
   (U1) is `P(pass | q, M)`, which is option A. If `S_D` is graded, (U1) is
   `E[S | q, M]`, which is option B. One sigmoid head per model, trained with
   binary cross-entropy against targets in [0,1], estimates both, because BCE
   is a proper scoring rule for a mean in [0,1] (§2.3). "Probability of success"
   is used **only** for datasets whose native metric is binary.
3. **Pairwise preference (C) and "beats the edge" (D) are not the primary
   target.** The objective `max E[U − λC]` is linear in expected scores. Its
   argmax therefore needs only per-model expectations, never a joint
   probability `P(S_M > S_M')` (§3.2). C and D remain baselines (RouteLLM-style)
   and diagnostics.
4. **A heterogeneous benchmark has no single binary success.** Each dataset
   keeps its own `S_D`. Raw scores are not mixed across metric types without
   the normalisation rules in §5, and results are reported per dataset and
   macro-averaged.
5. **Data reality check (new, important).** In LLMRouterBench, SimpleQA is
   scored **only for the 13 flagship API models** of the performance–cost
   setting, and stored as `is_correct = (grade == "A")`. INCORRECT and
   NOT_ATTEMPTED both become 0 `[CODE]`. The manuscript's statement that
   SimpleQA routing labels "can be automatically constructed" from pre-computed
   LLMRouterBench results (main-original.tex L205) is therefore **not true for
   any edge SLM or Split-LLM in the manuscript's pool**. The labels need new
   inference runs. SimpleQA is also a near-floor task for small models (§6).
   Handed to `10`/`13` as a blocking data issue.

---

## 1. What was wrong with v2's "probability of success"

v2 `07` §2 defined `Û_θ(a|q) := P̂(y*(a,q) = success | q)`. Section 3 of the
same file then let `y*` be "binary correctness, benchmark score or judge score in
[0,1]". Three defects (RF-F):

| # | Defect | Consequence |
|---|---|---|
| F1 | "Success" is binary language applied to graded scores (F1, judge Likert). | A sigmoid trained on 0.6-valued targets does not estimate any probability of success. It estimates a mean score, and v2 never said so. |
| F2 | Randomness is not specified. `y*(a,q)` is one run. | The target is a noisy single draw. The same query can pass or fail across runs under sampling or BF16 numerics (`02` §2.3). Calibration has no well-defined reference. |
| F3 | Abstention, partial credit and judge-based grading are not distinguished. | On SimpleQA, "not attempted" is a legitimate third outcome with its own metric (§4.1). v2 folded it silently into failure. |

v2's structural decisions were sound and are kept: one sigmoid per scalar,
calibrated afterwards, with `λ` and `s` kept out of the weights. What changes
is the semantics of the scalar and the head index, which is now model rather
than action (`01`).

---

## 2. General definition

### 2.1 Objects

| Symbol | Meaning |
|---|---|
| `D` | dataset or task family, with a pinned scorer |
| `q` | query, including any dataset-mandated prompt template, but **not** the answer |
| `M` | model specification (`01` §1.1, `02` §1.1): checkpoint, revision, weight quantization, compute dtype, template, decoding configuration |
| `ξ` | run randomness: decoding seed, numeric non-determinism, grader sampling |
| `y_M(q; ξ)` | the output text |
| `G_D` | grader: exact match, regex, unit tests or a pinned LLM judge with a fixed prompt and version |
| `S_D(y, q) ∈ [0,1]` | normalised score computed by `G_D` against the reference `r(q)` |
| `U(M|q)` | `E_ξ[S_D(y_M(q;ξ), q)]`, the quantity the router estimates |

`U` is a property of the pair (query, model specification). It does **not**
depend on network state, cost or `λ`. This is what makes the separation
`Û_θ(M|q)` vs `C(a|s)` in `01`/`09` well-posed.

### 2.2 Why an expectation, not a single outcome

The router chooses before the run, so the decision-relevant quantity is the
score it should expect. A single observed `S` is one Bernoulli draw (binary
tasks) or one noisy draw (graded tasks) from the distribution whose mean is
`U`. Consequences:

* **Labels.** A single-run label `s_i ∈ {0,1}` is an unbiased but noisy
  estimate of `U(M|q_i)`. A `k`-sample empirical rate `s̄_i = (1/k) Σ_j s_ij`
  (S1-MS in `04` §5) is unbiased with variance reduced by `1/k`. Hybrid LLM's
  `r_prob` (Eq. 2, 10 samples) is the published precedent for multi-sample
  soft labels `[VERIFIED-BODY]` (`05` §1.6).
* **Greedy decoding does not remove `ξ`.** BF16 batch-dependent numerics give
  run-to-run differences even at temperature 0 (`02` §2.3, He 2025; Yuan et al.
  2025). With greedy decoding `U` is close to a point mass, not exactly one.
  The E0 noise floor `R_A` vs `R_B` (`02` §5.3) measures how far from a point
  mass it is.
* **Calibration has a defined reference.** A calibrated router satisfies
  `E[S | Û_θ(M|q) = u] = u` for every `u` and every `M`. For binary `S` this is
  the usual probability calibration (Guo et al. 2017). For graded `S` it is
  calibration in the mean, checked with a binned reliability curve of observed
  mean score against predicted score (§7).

### 2.3 Training loss

For a target `t ∈ [0,1]` (hard 0/1, multi-sample rate, normalised graded
score or soft teacher output) and a prediction `p = σ(z)`:

```
ℓ_BCE(p, t) = −[ t log p + (1 − t) log(1 − p) ]
```

`E_t[ℓ_BCE(p,t)]` is minimised at `p = E[t]`. BCE with fractional targets is
therefore a consistent estimator of the conditional mean, the same property
the squared error (Brier) loss has. This justifies one head type for binary and
graded datasets. It also means S1, S1-MS and S3 (soft KD) in `04` all share the
**same** loss and differ **only** in the target, which is the clean comparison
E1 needs (`03`). Brier/MSE is kept as an ablation loss.

Proposed-method facts (`[PROPOSED]`): K heads, one per model specification;
per-dataset scorers as in §4; post-hoc per-model calibration on a held-out
calibration split (§7).

---

## 3. Options A–E compared (brief §14)

### 3.1 Comparison table

| Option | Object | Strengths | Weaknesses | Published precedent (body-read, `05`) | Verdict |
|---|---|---|---|---|---|
| **A** `P(S ≥ τ | q, M)` | threshold success | Matches binary metrics exactly; easy to calibrate (ECE). | For graded metrics, `τ` is arbitrary and discards information. The result depends on `τ`. | Prefill router P(correct) (§3.1, Eq. 1); IRT-Router P̂ (Eq. 4–5); BEST-Route Pr[reward ≥ reference] (Eq. 3–4) | **Primary for binary datasets**, where it equals (U1). For graded datasets only as a sensitivity analysis. |
| **B** `E[S | q, M]` | expected score | Unifies binary and graded metrics; it is what `max E[U − λC]` needs; one loss (§2.3). | Mean calibration is less familiar than ECE. Means hide variance, so risk-sensitive SLAs need more. | RouterDC uses correctness scores (§3); ConsRoute regresses a soft score with MSE (Eq. 8) | **Primary (general definition U1)**. |
| **C** pairwise `P(S_M > S_M' | q)` | preference | Natural for judge comparisons with no reference answer; RouteLLM's formulation. | Defined per pair, so K models need O(K²) outputs. Not a model-level utility. Needs the **joint** distribution of outcomes. Ties need a rule (RouteLLM Eq. 1 has a tie class). | RouteLLM (Eq. 1, Eq. 13) | **Baseline only** (`11`). Usable for open-ended data in the journal version. |
| **D** `P(S_M > S_EDGE | q)` | beats the edge baseline | Directly answers "is escalation worth it". | A special case of C. With a deterministic binary S, `P(S_M=1, S_E=0)` needs the joint, not the marginals. Escalation-only, so it does not rank several remote models. | Hybrid LLM r_det/r_prob/r_trans (Eq. 1–4) | **Diagnostic + N=2 baseline**. Also reported as the "regret" view in E5. |
| **E1** `U − λC` regressed directly | net value | One number. | Puts `λ` and cost into the weights (v2 `07` §2, kept). Contradicts the separation in `09`. | — | **Reject.** |
| **E2** IRT ability–difficulty | latent `σ(aᵀθ_M − b)` | Shares statistical strength across models; enables profile-based extension to new models. | Extra modelling assumptions; matters mainly for pool growth. | IRT-Router (Eq. 4–5) | **Journal extension** (`15`), not the conference core. |

### 3.2 Why expectations suffice for the routing decision

With model-level utility (A1, `01`):

```
R(q, s) = argmax_a [ U(M(a)|q) − Δ(a,q) − λ C(a|s) ]
```

Every term is a **per-action expectation**. Linearity of expectation means the
expected objective of any policy depends on the outcome distribution only
through the marginals `U(M|q)`. The correlation between `S_M` and `S_M'` on the
same query does not enter. Options C/D estimate a joint-distribution quantity
the objective never uses. They are informative (they describe "how often
escalation changes the answer") but they are not the decision variable.

Two qualifications `[PROPOSED]`:

* If the systems policy is **risk-constrained**, for example "probability of a
  wrong answer ≤ ε" or a quantile SLA on quality, then a marginal mean is
  sufficient only for binary `S`, where the mean *is* the probability. For
  graded `S` a quantile target would be needed. No such quality SLA is
  proposed for the conference version. Latency SLAs in `09` constrain cost,
  not utility.
* **N=2 milestone.** With `𝓜 = {M_E, M_S}`, comparing `Û(M_S|q) − Û(M_E|q)`
  against `λ ΔC` is equivalent to thresholding an estimate of the expected
  gain `E[S_S − S_E | q]`. Hybrid LLM and RouteLLM threshold the same
  quantity (in expectation). This is why the N=2 milestone can be compared
  fairly with them (`11`).

---

## 4. Task-specific instantiations

Each row fixes `S_D`. "Native metric" is the metric the source benchmark
reports. "Router target" is what enters (U1).

| Task family | Example datasets | Native metric | `S_D` (router target) | Notes |
|---|---|---|---|---|
| **Factual short-answer QA with abstention** | SimpleQA | 3-way grade CORRECT / INCORRECT / NOT_ATTEMPTED; reported as overall correct, correct-given-attempted, F-score | **Primary:** `S = 1[CORRECT]` ⇒ `U = P(correct)` | §4.1. Abstention handled as a secondary analysis. |
| **Multiple choice** | MMLU-Pro, GPQA, BBH | accuracy | `1[option = key]` | Chance floor `1/#options`. Report chance-corrected score as a secondary metric only. |
| **Math / reasoning with final answer** | MATH500, AIME, GSM8K | accuracy (final-answer match) | `1[normalised answer = reference]` | Reasoning models have long, sampled outputs, so `ξ` matters. Use S1-MS labels (k samples) if budget allows. |
| **Code** | HumanEval, MBPP, LiveCodeBench | pass@1 | `1[all tests pass]` | Fraction of tests passed is a partial-credit ablation only. Pass@1 is the native metric. |
| **Partial-credit extraction** | F1/ROUGE-scored QA | token F1 etc. | the metric itself, already in [0,1] | Here (U1) is `E[S]`, not a probability. Do not say "success". |
| **Open-ended generation, reference-based judge** | ArenaHard-style, HLE (judge) | judge grade / win rate | `(g − g_min)/(g_max − g_min)` for a Likert judge, or `1[judge: correct]` for a binary judge | Judge model, prompt and version are part of `G_D`. Report judge–human agreement where the benchmark provides it. |
| **Pairwise preference with no reference** | Chatbot-Arena-style | win/tie/loss | No model-level `S` exists without a reference. Use win rate against a **fixed anchor model** as `S`, or exclude. | Converting to a per-model score needs a fixed anchor or a Bradley–Terry model. Out of conference scope. |
| **Tool use / agents** | τ²-Bench | task success rate | `1[task success]` | Multi-turn. Not compatible with single-query routing in the conference version. Exclude. |

### 4.1 SimpleQA in detail (the manuscript's dataset)

Facts:

* The SimpleQA grader assigns CORRECT, INCORRECT or NOT_ATTEMPTED. The paper
  reports overall correct, correct-given-attempted and an F-score, defined as
  the harmonic mean of the two (= `2c/(2c+2i+n)`) (Wei et al., §2.4)
  `[VERIFIED-BODY]` (HTML body read for §2.4 and Table 3 only).
* The paper's grader is a prompted ChatGPT classifier. The authors report 2
  disagreements in 300 manually read completions (§2.4) `[AUTHOR-CLAIM]`.
* LLMRouterBench re-grades with its own copy of the SimpleQA grader template
  (`evaluation/SimpleQA/prompts.py`). It sets `is_correct = (grade == "A")`,
  that is, CORRECT only. If the grader output cannot be parsed, it defaults to
  `"C"` = NOT_ATTEMPTED, which scores 0 (`simpleqa.py`, `_get_grader_result`,
  `evaluate`) `[CODE]`. The paper states the grader is o3-mini (`05` §1.4)
  `[VERIFIED-BODY]`. The pinned grader configuration in code was not checked
  `[OPEN]`.
* The default evaluation split in code is `subset_500`. The full `test` split
  (4,326) is also valid `[CODE]`. Which split produced the released numbers
  must be checked when the data tarball is downloaded `[OPEN]`.

Decision `[PROPOSED]`:

* **Primary `S = 1[CORRECT]`.** This matches LLMRouterBench's stored field and
  SimpleQA's "overall correct". With it, `U = P(correct | q, M)` is a genuine
  probability and can be ECE-calibrated.
* **Secondary analysis: abstention-aware utility.** On SimpleQA an abstaining
  model is safer than a confidently wrong one. The paper's F-score and its
  observed "not attempted" rates (Claude-3-haiku 75.3%, GPT-4o-mini 0.9%;
  Table 3) `[AUTHOR-CLAIM]` show that models with similar overall-correct
  scores can behave very differently. A penalised score `S_pen = 1[C] − κ·1[I]`
  (with `κ` pre-registered, for example κ=1, then rescaled to [0,1]) is a
  sensitivity analysis only. It needs the 3-way grade, which LLMRouterBench's
  `prediction` field stores as the letter A/B/C (`evaluate` returns
  `"prediction": grader_result`) `[CODE]`. The 3-way grade is therefore
  recoverable from released records without re-grading, pending a check of the
  data tarball `[OPEN]`.

---

## 5. Heterogeneous benchmarks

Brief §14 warns against pretending that a heterogeneous benchmark has one
natural binary definition. Rules `[PROPOSED]`:

1. **Per-dataset scorers are fixed.** `S_D` is chosen per dataset from §4
   before any router training and recorded in the run config.
2. **One head per model, not per (model, dataset).** The query encoder is
   expected to recognise the task from the text. Dataset identity is **not**
   an input, because at deployment it is unknown. A dataset-conditioned oracle
   ("dataset prior", `11`) is a baseline that shows how much of the router's
   gain is coarse domain structure. LLMRouterBench reports that leading routers
   come close to a per-dataset oracle in its performance setting
   `[AUTHOR-CLAIM]` (repo README "Key Findings"; paper body `05` §1.4).
3. **Do not average across metric types without stratifying.** Training
   mixes binary and graded targets in one BCE loss (§2.3), which is valid. For
   **reporting**, utility is aggregated per dataset first and then
   macro-averaged. The mix of metric types is stated in the table caption.
4. **Base rates differ by dataset.** Calibration is checked per model and per
   dataset (§7). A router that looks calibrated in aggregate can be
   miscalibrated within every dataset.
5. **λ is interpreted per unit of normalised score.** Because `U ∈ [0,1]`
   everywhere, `λ` (or the SLA in `09`) has the same unit, "score points per
   unit cost", across datasets. That unit is only meaningful where
   `S_D` is comparable, so the E5 sweep is reported per dataset as well as
   pooled.

---

## 6. Data reality check: what LLMRouterBench can and cannot supply

### 6.1 Facts `[CODE]` (README and configs, 2026-10-04)

* **Performance setting:** 20 "lightweight" ~7–9B open models on 15 datasets
  (AIME, MATH500, MATHBench, HumanEval, MBPP, LiveCodeBench, BBH, KORBench,
  Knights & Knaves, MMLU-Pro, GPQA, FinQA, MedQA, EmoryNLP, MELD). The pool
  includes `Qwen3-8B`, `Llama-3.1-8B-Instruct`, `Gemma-2-9b-it`,
  `NVIDIA-Nemotron-Nano-9B-v2` and others. **SimpleQA is not in this
  setting**: it does not appear in `config/baseline_config.yaml` or in
  `config/data_collector_small_model_config.yaml`.
* **Performance–cost setting:** 13 flagship API models (Claude-sonnet-4,
  Gemini-2.5-flash/pro, GPT-5-chat, GPT-5-medium, Qwen3-235B-A22B-2507 and its
  thinking variant, DeepSeek-V3-0324, DeepSeek-V3.1-Terminus, DeepSeek-R1-0528,
  GLM-4.6, Kimi-K2-0905, Intern-S1) on 10 datasets, **including SimpleQA**
  (listed in `config/baseline_config_performance_cost.yaml`, line 29).
* Every record stores `origin_query`, `prompt`, `prediction`, `ground_truth`,
  `score`, `prompt_tokens`, `completion_tokens` and `cost`. The released data is
  a single 1.28 GB archive (`bench-release.tar.gz` on HF `NPULH/LLMRouterBench`),
  which was not downloaded in this iteration.

### 6.2 Consequences `[PROPOSED]` / `[OPEN]`

1. **The manuscript's SimpleQA plan needs new inference.** None of the
   manuscript's edge SLMs or Split-LLMs (the pool to be fixed in `10`) has
   SimpleQA outcomes in LLMRouterBench. Pre-computed labels exist only for the
   13 API models, which are not edge-deployable and not split-executable.
   main-original.tex L205 ("routing labels can be automatically constructed
   without repeatedly executing ... SLMs and Split-LLMs") must not be carried
   into the v3 text. The blue tex will say that labels are produced by running
   each model specification through the pinned LLMRouterBench evaluator.
2. **Specification matching.** Even for models that do appear in the 7B
   performance pool (for example Qwen3-8B), LLMRouterBench's serving numerics,
   templates and decoding are not our 4-bit edge specification. By the
   definition of `M` (`01` §1.1), these are different specifications unless an
   E0-style agreement check on a sample shows otherwise. Released outcomes are
   usable as **pre-training or auxiliary labels** and for the TF-IDF / dataset
   prior pilot. Final labels are regenerated on our specifications `[OPEN]`.
3. **SimpleQA is close to the floor for small models.** In the SimpleQA
   paper, GPT-4o-mini scores 8.6% overall correct and Claude-3-haiku 5.1%
   (Table 3) `[AUTHOR-CLAIM]`. These are API models, not our SLMs, so they are
   only an indication. If the edge SLM is near 0%, then `U(M_E|q) ≈ 0` for
   almost every query, the routing problem degenerates to "always escalate",
   and calibration is dominated by the negative class. Headroom must be
   measured before SimpleQA is the sole dataset. This is handed to `10` as a
   pool-selection criterion ("overlapping competencies"). It is also a reason
   to add at least one dataset where the edge SLM succeeds on a substantial
   fraction, for example MMLU-Pro, BBH or MATH500 from the performance setting
   `[OPEN]`, advisor decision.
4. **One labelling campaign still serves every target.** Storing the raw
   grade (letter A/B/C, or the per-test results for code) lets A, B, the
   penalised SimpleQA score, D and S1-MS all be derived from the same runs
   (kept from v2 `07` §3). E0 reuses the same `S_D` (`02` §5).

---

## 7. Calibration targets and metrics

| Quantity | Binary `S` | Graded `S` |
|---|---|---|
| Calibration condition | `P(S=1 | Û=u) = u` | `E[S | Û=u] = u` |
| Primary metric | ECE (15 equal-mass bins), per model and per dataset | binned mean-calibration error (same bins) |
| Proper score | Brier, NLL | Brier (squared error), BCE with fractional targets |
| Post-hoc map | temperature scaling per head (Guo et al. 2017); isotonic as an ablation | isotonic or affine-logit per head |
| Decision-level check | routing regret at fixed λ / SLA: realised utility vs the oracle | same |

Calibration is fitted on a dedicated calibration split, disjoint from the
training split and from the test split, per model specification. If KD is used,
the order (teacher calibrated before distillation? student calibrated after?) is
an experimental factor handled in `03`. This file only fixes what "calibrated"
means.

---

## 8. Manuscript wording

**Allowed** `[PROPOSED]`:

* "For each candidate model $M$ we define its utility on query $q$ as the
  expected task score $U(M\mid q)=\mathbb{E}[S_D(y_M(q),q)]\in[0,1]$, where
  $S_D$ is the benchmark's own scoring function; for binary metrics this is
  the probability that $M$ answers $q$ correctly."
* "On SimpleQA we use the benchmark's grader and score a response as 1 only if
  it is graded CORRECT~\cite{wei2024simpleqa}; abstentions and incorrect
  answers score 0."
* "Routing labels are obtained by running each model configuration through the
  LLMRouterBench evaluation pipeline~\cite{li2026llmrouterbench}." (Do not
  claim that pre-computed results cover our models.)

**Rejected** `[REJECT]`:

* "The router predicts the probability of success" without defining success
  per dataset.
* "Routing labels are constructed from pre-computed LLMRouterBench results
  without executing the SLMs and Split-LLMs" (false for SimpleQA and our pool,
  §6).
* "The router predicts which model is better" as a description of the primary
  target (that is option C/D).
* Mixing raw accuracy, F1 and judge Likert scores into one average without
  normalisation and stratification.

---

## 9. Consequences for other deliverables

| File | What it takes from 08 |
|---|---|
| `03-kd-hardening.md` | All supervision conditions use BCE with targets in [0,1] (§2.3). The teacher predicts `E[S]` per model. KD targets are the teacher's calibrated or uncalibrated expectations (to be decided in 03). S1-MS is a multi-sample estimate of the same `U`. |
| `09-cost-policy.md` | `U ∈ [0,1]` per dataset gives `λ` the unit "normalised score per unit cost". No quality SLA in the conference version (§3.2). |
| `10-model-pool.md` | Blocking data issue §6.2(1); specification matching §6.2(2); SimpleQA headroom §6.2(3). The edge SLM must have non-trivial success on at least one evaluation dataset. |
| `11-baselines-v3.md` | RouteLLM-style (option C) and Hybrid-LLM-style (option D) as N=2 baselines; dataset prior as a baseline (§5.2). |
| `13-experiments-v3.md` | E0 metric = `S_D` from §4. E4 calibration as in §7. E5 reported per dataset. Pre-register the penalised SimpleQA analysis. Label-generation step before E1. |
| `14-henry-checklist.md` | Nothing new (utility is model-level; Henry's answers matter through `M` and E0). |
| `proposed-solution-blue-v3.tex` | Use the wording in §8. Cite SimpleQA and LLMRouterBench. |
| `17-verified-references-v3.md` / `.bib` | Add `wei2024simpleqa` (arXiv 2411.04368; title "Measuring short-form factuality in large language models"; authors Jason Wei, Nguyen Karina, Hyung Won Chung, Yunxin Joy Jiao, Spencer Papay, Amelia Glaese, John Schulman, William Fedus) as `[VERIFIED-META]` + `[VERIFIED-BODY]` for §2.4/Table 3. Its peer-review venue was not checked, so cite as arXiv. |

---

## 10. Sources

| Source | Locator | Used for | Tag |
|---|---|---|---|
| Wei et al., "Measuring short-form factuality in large language models", arXiv 2411.04368 | §2.4 (grades, metrics, F-score, grader agreement); Table 3 | SimpleQA grading, abstention, small-model floor | `[VERIFIED-BODY]` (those parts only); numbers `[AUTHOR-CLAIM]` |
| LLMRouterBench repo `ynulihao/LLMRouterBench@main` | `README.md` dataset and pool tables; `evaluation/SimpleQA/simpleqa.py`; `evaluation/SimpleQA/prompts.py`; `config/baseline_config_performance_cost.yaml` L29; `config/baseline_config.yaml`; `config/data_collector_small_model_config.yaml` | SimpleQA only in performance–cost pool; `is_correct` rule; record fields | `[CODE]` |
| LLMRouterBench paper (Findings ACL 2026) | `05` §1.4 | 21 datasets / 33 models; o3-mini judge; scope | `[VERIFIED-BODY]` (via `05`) |
| Hybrid LLM (ICLR 2024) | Eq. 1–4 | Option D, multi-sample soft labels | `[VERIFIED-BODY]` (via `05` §1.6) |
| BEST-Route (ICML 2025) | Eq. 3–5 | Threshold-type action-level target | `[VERIFIED-BODY]` (via `05` §1.7) |
| Prefill-activation router (arXiv 2603.20895) | §3.1, Eq. 1–2 | Per-model P(correct) + additive cost | `[VERIFIED-BODY]` (via `05` §1.8) |
| IRT-Router (ACL 2025) | Eq. 1, 4–5 | Option E2 | `[VERIFIED-BODY]` (via `05` §1.10) |
| RouteLLM (ICLR 2025) | Eq. 1, Eq. 13 | Option C | `[VERIFIED-BODY]` (via `05` §1.1, `04`) |
| RouterDC (NeurIPS 2024), ConsRoute (preprint) | `05` §1.2, §1.5 | Score-based targets | `[VERIFIED-BODY]` (via `05`) |
| Guo et al. 2017, "On calibration of modern neural networks" (ICML) | temperature scaling | §7 | `[VERIFIED-META]`; body check pending in `17` |
| Properness of BCE/Brier for a [0,1] mean | standard result; derivation in §2.3 | §2.3 | our derivation; no citation needed |
