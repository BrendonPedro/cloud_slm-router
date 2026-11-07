# E1 — Does query-level semantic routing beat a task lookup on a heterogeneous pool?

Pre-registered 2026-11-07, before any E1 number was computed.

## Why this experiment, and why now

Everything so far is about one pair: DeepSeek-R1-0528-Qwen3-8B vs Qwen3-8B. Both
are Qwen3-8B derivatives and 80% of queries are ties
(`~/research/LLMRouterBench/diagnostics/evaluation_audit.md`). The pair work found
that most routing signal is benchmark recognition plus a per-benchmark prior
(synthesis E4/E8, branch `gnhf/semantic-router-over-e1ca6b`). A sceptic can say
this pair is simply a bad routing problem. Before deciding GO/PIVOT on semantic
routing we have to check whether the same holds on a pool where models really
differ.

The same LLMRouterBench bundle that the pair work used already contains binary
correctness **and** completion-token usage for **20** 7–9B models on all 11,467
queries (`baselines/AvengersPro/data/small_models_seed_42/seed42_split0.7/{train,test}.jsonl`,
`records` and `usages`). The GTE-Qwen2-7B embedding cache covers every query. So
the question can be answered on CPU with no new inference.

## Exact question

On held-out queries, how much accuracy does a **query-level** router add over a
**task-level lookup** (pick the best model for the query's predicted benchmark),
and what fraction of the lookup-to-oracle gap does that gain close?

## Frozen setup

- Pool: 11,467 queries, 15 benchmarks, 20 models, all scores ∈ {0, 1}.
- Folds: `diagnostics/stratified_cv/fold_assignments.csv`, 5 folds, joined on
  (dataset, index). These folds were stratified on the DS/Qwen pair label. They are
  still valid, leakage-free outer splits for the pool, and nothing is refit.
- Representation: cached `Alibaba-NLP/gte-Qwen2-7B-instruct` embeddings,
  L2-normalised (same loader as `run_cv_eval.py`).
- Everything (task classifier, lookups, regressions, centroids, kNN index) is fit
  on outer-train rows only.

## Routers (one changed thing per row; no sweeps)

| ID | Router | Learning target |
|---|---|---|
| R0 | Best single model (highest outer-train mean) | none |
| R1 | Task lookup, oracle benchmark: per-benchmark argmax of train mean | task × model table |
| R2 | **Task lookup, predicted benchmark** (RidgeClassifier α=1, balanced, as in the pair scripts) | task × model table |
| R3 | Direct per-model utility regression: multi-output RidgeCV on GTE, argmax of predicted scores | ŝ_m(q) for all 20 models |
| R4 | Factored prior + residual: predicted-task mean of each model + RidgeCV on task-centred GTE predicting the residual s_m − mean_task(m) | task prior + residual |
| R5 | kNN: mean score of each model over the k = 50 nearest outer-train queries (cosine), argmax | local average |
| OR | Oracle: 1 if any model is correct | hindsight only, not deployable |

RidgeCV alpha grid is fixed at (0.1, 1, 10, 100) and chosen by efficient LOO on
outer-train only. It is model fitting inside train, not a sweep over test
results. k = 50 is fixed in advance and not tuned. Argmax ties are broken by
overall train mean, then by model name.

Pair restriction: the same routers are also run with the pool restricted to
{DS, Qwen}, which links E1 to the earlier pair evidence. This is descriptive.

## Metrics

- **Primary**: held-out accuracy of the chosen model, query-weighted, pooled over
  the 5 folds.
- Secondary: benchmark-macro accuracy (mean over the 15 benchmarks).
- **Within-task gain** Δ = acc(R) − acc(R2), with a paired bootstrap over queries
  (2,000 resamples, seed 0) for a 95% CI, plus the number of folds with Δ > 0.
- **Gap closed** = Δ / (acc(OR) − acc(R2)).
- Descriptive: mean completion tokens of the chosen model, and the model-choice
  entropy.

## Frozen decision rule (applies to the full 20-model pool)

Let R* be whichever of R3, R4, R5 has the highest pooled accuracy. Picking the
best of three adds selection optimism, so the bar is set with that in mind.

- **HEADROOM** (semantic routing has a query-level contribution worth building):
  Δ(R*) ≥ **+1.0 accuracy point**, the bootstrap 95% CI lower bound > 0, **and**
  Δ > 0 in ≥ 4 of 5 folds.
- **NO HEADROOM**: Δ(R*) < +0.5 point, **or** the CI includes 0.
- Anything in between is **MARGINAL**.

## Interpretation fixed in advance

- NO HEADROOM on the 20-pool as well as on the pair → the pair result is not a
  quirk of the pair. Query-level semantic routing on this benchmark reduces to
  task recognition plus a lookup table. That is strong evidence for **PIVOT**
  (semantic routing becomes a task-recognition component inside a
  deployment-optimisation contribution).
- HEADROOM on the 20-pool but not the pair → per-query routing value exists
  where models are heterogeneous. The pair is the wrong testbed, and a GO
  formulation must be built on a heterogeneous pool.
- R4 > R3 by a CI-separated margin → the factored formulation helps on the pool.
  R4 ≤ R3 → the factorisation adds nothing over direct per-model utility
  regression.

## Known limitations, stated in advance

- One-shot labels are noisy (the pair stability study found 27% winner-stable).
  The oracle is therefore inflated by noise, so "gap closed" understates what is
  achievable. Δ itself is unbiased by this, because R and R2 face the same noise.
- The benchmark mix is LLMRouterBench's, not real traffic.
- This is accuracy only. Cost-aware routing is a separate experiment (E2).
