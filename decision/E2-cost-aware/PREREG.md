# E2 — Does query-level semantic signal matter for *cost-aware* routing?

Pre-registered 2026-11-07, before any E2 number was computed. E1 had already
finished (NO HEADROOM for accuracy-only routing; see
`../E1-pool-headroom/RESULTS.md`).

## Why this experiment

E1 showed that on the 20-model LLMRouterBench pool, accuracy-only query-level
routing does no better than predicting the benchmark and looking up a table. The
pool has far more spread in **cost** than in accuracy: mean completion tokens run
from 232 (gemma-2-9b) to about 8.2k (OpenThinker3, Intern-S1-mini). If a
query-level router is worth anything, it most plausibly shows up as *knowing when a
cheap or short-answer model is enough for this particular query*. E2 tests exactly
that. If E2 also finds no headroom, the semantic-routing contribution is closed on
both axes for this data. E2 also folds in E1b (a finer, cluster-level lookup) so
we can tell whether any query-level gain is really just a finer task taxonomy.

## Frozen setup (same as E1)

- 11,467 queries, 15 benchmarks, 20 models; correctness s_m(q) ∈ {0,1} and
  completion tokens t_m(q) from the same bundle (`records`, `usages`).
- Same 5 frozen folds, GTE-Qwen2-7B embeddings (`../cache/gte_pool.npy`, with the
  query hash checked) and the same task classifier (RidgeClassifier α=1,
  balanced). Everything is fit on outer-train only.
- Cost is measured in **thousands of completion tokens** (all models are 7–9B, so
  tokens are the dominant cost/latency driver; prices are not modelled).

## Utility and λ grid

u_m(q; λ) = s_m(q) − λ · t_m(q)/1000, so λ is in "accuracy points per 1k tokens ÷ 100".

λ ∈ {0, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5}
(13 values, fixed).

**Operating band** (fixed rule, computed from R2 itself so it cannot favour R*):
the λ values with λ > 0 at which R2's mean chosen tokens lie strictly between
the cheapest model's mean tokens and the best-single model's mean tokens (on the
full pool, pooled over folds). Outside the band the problem degenerates to "pick
the cheapest" or to accuracy-only routing (already covered by E1).

## Routers

Every predictor estimates ŝ_m(q) and t̂_m(q) separately and routes by
argmax_m ŝ_m − λ·t̂_m/1000. Because the predictors are linear in the target, this
is the same as fitting the utility directly, and it lets one fit serve all λ.

| ID | Router | ŝ and t̂ |
|---|---|---|
| R0 | Best single model under λ (highest train mean utility) | global means |
| R2 | **Task lookup, predicted benchmark** | per-benchmark train means |
| R3 | Direct per-model regression (RidgeCV on GTE, separately for s and t) | query-level |
| R4 | Factored prior + residual (task mean + RidgeCV on task-centred GTE, for s and t) | query-level |
| R5 | kNN-50 (cosine) mean of s and t | query-level |
| R6 | **Cluster lookup (E1b)**: inside each predicted benchmark, nearest of k_t train-only k-means centroids (k_t = clip(round(n_train_t/200), 1, 16), seed 0), with cluster means shrunk to the benchmark mean as (n_c·x̄_c + 20·x̄_t)/(n_c + 20) | sub-task table |
| OR | Oracle per λ: max_m u_m(q; λ) | hindsight only |

RidgeCV alpha grid (0.1, 1, 10, 100) via LOO on train, exactly as in E1. Ties
are broken by global train mean utility, as in E1.

## Metrics

- **Primary**: realised mean utility U(R; λ) on held-out queries, using the true
  s and t of the chosen model. ΔU(λ) = U(R; λ) − U(R2; λ) is in accuracy points
  net of the token charge, with a paired bootstrap over queries (2,000
  resamples, seed 0) and the count of folds with ΔU > 0.
- Secondary: (a) the accuracy-vs-mean-tokens curve of each router traced over λ;
  (b) **tokens at matched accuracy**: for each band λ, R*'s mean tokens at R2's
  accuracy, interpolated along R*'s λ-curve (a percentage saving); (c) accuracy
  at fixed mean-token budgets of 1k, 2k and 3k tokens, interpolated along each
  curve; (d) gap closed = ΔU / (U(OR) − U(R2)).
- Descriptive: how much of the per-query token variance the predictors explain
  beyond the benchmark mean (held-out R² of t̂ for R4 vs R2), and the same for s.

## Frozen decision rule

R* = whichever of R3, R4, R5 has the highest ΔU averaged over the band λ values.

- **COST HEADROOM**: at **≥ half of the band λ values**, ΔU(R*) ≥ +1.0 pt, the
  bootstrap CI lower bound > 0, and ΔU > 0 in ≥ 4 of 5 folds.
- **NO COST HEADROOM**: at every band λ, ΔU(R*) < +0.5 pt **or** the CI
  includes 0.
- Anything else is **MARGINAL**.

**Taxonomy check (E1b)**: separately, compare R* with R6 at each band λ (and at
λ = 0). If R6 is within 0.3 pt of R* or above it at most band λ values, any
query-level gain counts as "finer task taxonomy", not per-query semantics.

## Interpretation fixed in advance

- **NO COST HEADROOM** (together with E1's NO HEADROOM) → on this data, semantic
  routing adds nothing beyond task recognition plus a cost-aware lookup table,
  on accuracy or on cost. That supports **PIVOT**: the main contribution becomes
  deployment optimisation (cost/latency/placement), and semantic routing becomes
  a task-recognition component. The cost-aware lookup (R2 over λ) is then the
  routing baseline to carry forward.
- **COST HEADROOM with R* ≫ R6** → there is real per-query value, and it lives in
  *cost*, not correctness. A GO formulation would be cost-aware query-level
  routing. The post-hoc decomposition (does the gain come from t̂ or from ŝ?)
  then decides whether the learning target should be per-query output length
  rather than per-query winner.
- **COST HEADROOM but R6 ≈ R*** → the gain is a finer taxonomy. The publishable
  piece is then sub-task discovery plus a cost-aware table, which is closer to
  existing cluster routers (weak novelty), so this leans PIVOT with a stronger
  routing component.
- **MARGINAL** → report it as such. It does not support a GO headline.

## Known limitations, stated in advance

- One-shot labels: t_m(q) varies on re-generation too, so per-query token
  prediction is upper-bounded by sampling noise that we cannot measure here.
- Tokens are a proxy for cost. Real deployment cost also depends on prompt
  length, batching and hardware; none of that is modelled.
- Choosing R* as the best of three over the band adds selection optimism, so the
  threshold is kept at +1.0 pt as in E1.
