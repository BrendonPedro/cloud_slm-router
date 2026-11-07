# E1 results: query-level routing vs task lookup (20-model pool and DS/Qwen pair)

Run 2026-11-07 with no changes to `PREREG.md`. The only change to the code was
the embedding source: `run_e1.py` now loads `../cache/gte_pool.npy`. That file was
dumped by `../dump_gte.py` from the same GTE sqlite cache, opened read-only, in
the same seed-42 row order and L2-normalised, and a SHA-256 of the query list is
checked. The cache is gitignored, so regenerate it with
`~/research/LLMRouterBench/.venv/bin/python -B decision/dump_gte.py` (about 1
minute). After that, `run_e1.py` takes about 9.5 minutes on 4 CPUs.

Raw outputs: `results/e1_results.json`, `results/e1_per_query_choices.csv.gz` and
`results/e1_run.log`.

## Pre-registered verdict

**NO HEADROOM on both the 20-model pool and the pair.**

### 20-model pool (11,467 queries, 15 benchmarks, 5 frozen folds)

| Router | Acc | Macro | Δ vs R2 [95% CI] | Folds Δ>0 | Gap closed | Mean tok | H (bits) |
|---|---|---|---|---|---|---|---|
| R0 best single (Qwen3-8B) | 0.6734 | 0.6923 | −3.33 [−4.08, −2.60] | 0 | — | 4,099 | 0 |
| R1 task lookup, oracle task | 0.7065 | 0.7190 | −0.02 | 0 | — | 3,729 | 2.80 |
| **R2 task lookup, predicted task** | **0.7067** | 0.7192 | 0 | — | 0 | 3,730 | 2.80 |
| R3 direct per-model utility (RidgeCV) | 0.7007 | 0.7184 | −0.60 [−1.28, +0.07] | 0 | −3.0% | 3,597 | 3.64 |
| R4 factored prior + residual | **0.7109** | **0.7312** | **+0.42 [−0.18, +1.01]** | 4 | 2.1% | 3,602 | 3.41 |
| R5 kNN-50 | 0.7067 | 0.7232 | 0.00 [−0.62, +0.62] | 2 | 0.0% | 3,571 | 3.15 |
| OR oracle (hindsight) | 0.9043 | 0.9186 | +19.76 | 5 | 100% | — | — |

R* = R4, with Δ = +0.42 pt. That is below the +0.5 pt floor and the CI
includes 0, so the verdict is **NO HEADROOM**.

### DS/Qwen pair restriction (descriptive)

| Router | Acc | Δ vs R2 [95% CI] | Folds Δ>0 |
|---|---|---|---|
| R0 best single | 0.6734 | −1.10 [−1.60, −0.60] | 0 |
| R2 task lookup, predicted | 0.6844 | 0 | — |
| R3 direct utility | 0.6860 | +0.16 [−0.25, +0.58] | 2 |
| R4 factored | 0.6854 | +0.10 [−0.25, +0.46] | 3 |
| R5 kNN-50 | 0.6856 | +0.12 [−0.27, +0.51] | 4 |
| OR oracle | 0.7597 | +7.53 | 5 |

R* = R3 with Δ = +0.16 pt, so this is also **NO HEADROOM**. That reproduces the
earlier pair finding with an independent implementation.

### Post-hoc paired contrasts

These used the same bootstrap (seed 0, 2,000 resamples) and were not
pre-registered as decision criteria.

| Contrast | Pool20 | Pair |
|---|---|---|
| R4 − R3 (factored vs direct) | **+1.02 [+0.56, +1.44], 5/5 folds** | −0.05 [−0.33, +0.21] |
| R4 − R5 (factored vs kNN) | +0.42 [−0.13, +0.99], 4/5 | −0.02 [−0.38, +0.37] |
| R2 − R0 (lookup vs best single) | **+3.33 [+2.60, +4.08], 5/5** | +1.10 [+0.60, +1.60] |

## What this means (by the interpretation fixed in advance)

1. **The pair result is not a quirk of the pair.** On a pool where the 20 models
   are genuinely different (the oracle is 0.904, against 0.760 for the pair), every
   query-level router that learns from GTE embeddings captures **at most about 2%
   of the gap between lookup and oracle**. All the routing gain that can be
   recovered (+3.3 pt over the best single model) comes from *benchmark
   recognition plus a per-benchmark table*. Task prediction is 99.4–99.8%
   accurate, so R2 ≈ R1.
2. **Within its own design space the factored formulation is the right one.**
   R4 beats direct per-model utility regression by +1.0 pt, CI-separated and in 5
   of 5 folds. Direct regression actually *loses* to the lookup, because it has to
   re-learn the task prior from embeddings and gets it wrong on the large
   benchmarks (medqa −5.1 pt, mbpp −3.7 pt). But R4 still does not beat the
   lookup table that it factors around. So the residual term is too small to
   detect at this sample size, not an established contribution.
3. **Where the residual does help, it looks like a sub-task.** In the per-benchmark
   breakdown, the query-level gains concentrate in benchmarks that are internally
   heterogeneous: korbench +3.8 pt (nominally 5 sub-categories), mmlupro +2.9
   (14 subjects), bbh +1.4 (27 tasks), humaneval +3.1 and gpqa +4.0 (small n).
   They are offset by losses on homogeneous ones: finqa −3.0 and medqa −2.0. This
   suggests that the recoverable query-level signal is a *finer task taxonomy*,
   not per-query difficulty. A sub-category lookup would test that directly (the
   E1b candidate below).
4. **The oracle gap is mostly irreducible noise or unpredictable.** The pair
   stability study found only 27% of winners stable on re-run. A one-shot pool
   oracle of 0.904 against a best router of 0.711 says that ~19 pt of "headroom"
   is not reachable from the query text with these representations.
5. **Cost is the only axis with large slack.** Query-level routers already pick
   cheaper models (about 3.6k vs 3.7k tokens) at equal accuracy, without being
   asked to. With mean completion tokens spanning 232–8.2k across the pool,
   cost-aware routing (E2) has far more structure to exploit than accuracy-only
   routing.

## Consequence for GO / PIVOT (provisional; the literature review and E2 are still open)

E1 is the first decisive cached-data result and it points to **PIVOT**. On the
best available heterogeneous pool, accuracy-only semantic routing reduces to task
recognition plus a lookup, and neither direct winner prediction nor the factored
residual adds a detectable query-level gain. The routing component of the paper
should be the (cheap, about 99.7% accurate) task recognizer plus a table. Any
headline contribution has to come from the cost/latency/deployment side, unless
E2 shows that query-level signal matters for *cost-aware* routing (for example,
predicting when a short-answer model suffices).

## Open follow-ups this result motivates

- **E1b (sub-category / cluster lookup):** replace the benchmark table with a
  finer table. The pool rows carry only `dataset` and an integer `index`, with
  no sub-category field (checked), so the sub-labels must either be joined from
  the source benchmark files or replaced by train-only k-means clusters inside
  each benchmark (a "cluster lookup", as in UniRoute/Avengers-style routers). If
  that matches R4, the "residual" is just a finer task taxonomy, which closes the
  accuracy side of the semantic-routing question.
- **E2 (cost-aware):** utility = correctness − λ·tokens over a λ grid. Compare the
  lookup with R4/R5 on the accuracy-vs-tokens Pareto front (area under the
  curve, and accuracy at matched cost).
