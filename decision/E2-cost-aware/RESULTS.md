# E2 results: cost-aware routing (correctness − λ·k-tokens), 20-model pool

Run 2026-11-07 with no changes to `PREREG.md`. The script was run twice. The
second run added only an output-only dump of per-query choices
(`results/e2_choices.npz`) for the post-hoc contrasts. The two runs'
`e2_results.json` are identical apart from `fold_meta`, checked with a sorted JSON
`cmp`. Runtime is about 10–17 minutes on 4 shared CPUs.

Raw outputs: `results/e2_results.json`, `results/e2_run.log`,
`results/e2_choices.npz`, and post-hoc `results/e2_posthoc.json` /
`results/e2_posthoc.log`, produced by `posthoc_contrasts.py`.

## Pre-registered verdict: **MARGINAL** (does not support a GO headline)

- Operating band (computed from R2 alone): λ ∈ {0.002 … 0.3}, 11 values. Over
  that range R2's mean tokens fall from 3.68k to 0.26k, between the cheapest model
  (0.23k) and the best single model (4.10k).
- Mean band ΔU: R3 −1.39 pt, R4 +0.15 pt, **R5 +0.58 pt**, so **R\* = R5 (kNN-50)**.
- R5 passes the COST HEADROOM test (ΔU ≥ +1.0, CI > 0, ≥ 4/5 folds) only at
  λ = 0.03 and 0.05, which is **2 of 11** band λ values and well short of half. It is
  not < +0.5 / CI∋0 at every λ either, so the verdict is **MARGINAL**.
- Taxonomy check: R6 (train-only cluster lookup) is within 0.3 pt of R\*, or above
  it, at most band λ values (flag = True). By the prereg, whatever query-level gain
  exists counts as **finer task taxonomy**.

### ΔU vs the cost-aware task lookup R2 (pt, 95% paired bootstrap CI, folds > 0)

| λ | R2 acc / k-tok | R3 direct | R4 factored | R5 kNN-50 (R\*) | R6 cluster lookup |
|---|---|---|---|---|---|
| 0 | .707 / 3.73 | −0.60 [−1.28,+0.07] 0 | +0.42 [−0.18,+1.01] 4 | 0.00 [−0.62,+0.62] 2 | +0.34 [−0.16,+0.84] 4 |
| 0.01 | .703 / 3.45 | −0.04 [−0.77,+0.61] 2 | +0.93 [+0.25,+1.55] 5 | +0.20 [−0.44,+0.85] 3 | +0.61 [+0.08,+1.14] 5 |
| 0.02 | .698 / 3.03 | +0.23 [−0.50,+0.95] 2 | +1.34 [+0.65,+2.06] 5 | +0.68 [+0.01,+1.38] 4 | +0.63 [+0.07,+1.17] 5 |
| 0.03 | .686 / 2.63 | +1.04 [+0.26,+1.81] 3 | **+1.98 [+1.26,+2.68] 5** | +1.36 [+0.64,+2.10] 5 | +1.12 [+0.52,+1.71] 5 |
| 0.05 | .647 / 1.47 | +1.04 [+0.24,+1.88] 4 | **+2.18 [+1.43,+2.97] 5** | +1.76 [+1.01,+2.51] 5 | +2.01 [+1.41,+2.65] 5 |
| 0.075 | .617 / 0.83 | −0.20 | +0.77 [+0.01,+1.51] 5 | +0.68 | +0.72 |
| 0.1 | .597 / 0.60 | −1.00 | −0.14 | +0.45 | +0.32 |
| 0.2 | .576 / 0.46 | −4.67 | −1.67 [−2.63,−0.75] 1 | +0.71 | +0.27 |
| 0.3 | .532 / 0.26 | −7.59 | −3.72 | +0.25 | +0.13 |

The full 13-λ table is in `e2_run.log`. The oracle's utility gap over R2 is 20–31
pt, and every router closes **≤ 7.4%** of it.

### Secondary metrics

- **Tokens at R2's accuracy** (interpolated along each router's λ-curve, band λ ≤
  0.05): R4 saves **20–25%**, R6 9.5–23.5% (9.5–13.6% for λ ≤ 0.03), R5 3–23% and R3
  ≤ 13%. For λ ≥ 0.1, R4 needs *more* tokens than R2, by 10–52%.
- **Accuracy at a fixed mean budget** of 1k / 2k / 3k tokens: R2 .625/.665/.697,
  R4 .638/.687/.708, R6 .637/.678/.703, R5 .637/.681/.701, best single
  .511/.559/.613. The lookup alone is +11 pt over the best single model at a 1k
  budget. Query-level routers add a further +1.2 to +2.2 pt.
- **Held-out R² beyond the benchmark mean**: tokens 0.38 (R2) → 0.49 (R4); correctness
  0.15 → 0.26. The per-query signal is real but small. In particular, about half of
  the per-query token variance remains unexplained by any predictor.

## Post-hoc analysis (not pre-registered; selection-optimistic)

From `posthoc_contrasts.py`, using the same bootstrap (seed 0, 2,000 resamples).

1. **R4 vs the cluster table R6.** R4 is significantly better only at λ = 0.02
   (+0.71 [+0.09, +1.36], 5/5) and λ = 0.03 (+0.87 [+0.19, +1.56], 5/5). It is
   indistinguishable from R6 at λ ≤ 0.01 and at λ = 0.05–0.1, and significantly
   **worse** for λ ≥ 0.15 (−1.2 to −7.1 pt). So the factored router beats a
   sub-task table in a single two-λ window, chosen post hoc from three candidates.
2. **Where R4's gain comes from.** At λ = 0.03, R4 − R2 = +1.98 pt pooled. Of this,
   **korbench contributes +1.30 pt and livecodebench +0.76 pt**, and the other 13
   benchmarks net −0.08 pt (medqa −0.31, finqa −0.25, math500 −0.11, mbpp −0.11).
   The same pattern holds at λ = 0.01, 0.02 and 0.05. Both winning benchmarks have
   explicit internal sub-structure: KOR-Bench has rule categories, and LiveCodeBench
   has easy/medium/hard difficulty tiers. The homogeneous benchmarks lose
   consistently. This is the E1 pattern again: **the residual is acting as a finer
   task taxonomy, not as per-query semantics.** The pool rows have no sub-category
   field, so we could not join the true sub-labels to confirm this directly. That
   check is recorded as an open item.
3. **Correctness residual vs token residual.** R4s (correctness residual + task-mean
   tokens) matches R4 at λ ≤ 0.02. It loses about 0.7 pt at λ = 0.03–0.05 and is far
   more robust at high λ (+1.3 to +6.5 pt over R4 for λ ≥ 0.15). The ridge token
   residual on heavy-tailed raw token counts is what makes R4 collapse at high λ:
   it mis-ranks the cheap models. A deployable cost-aware router should therefore
   keep the token term at task (or sub-task) level and should not regress per-query
   tokens linearly from GTE.
4. **Direct regression (R3) is again the worst query-level formulation.** It is
   negative at 10 of 13 λ values, which repeats E1's rejection of direct
   winner/utility prediction.

## What this means (by the interpretation fixed in advance)

- **MARGINAL → "report it as such; it does not support a GO headline."** Cost-aware
  routing has more per-query structure than accuracy-only routing (E1: none). The
  best query-level router buys about 20% fewer tokens at matched accuracy, or about
  +2 pt utility, in a mid-λ window. However, (a) most of that is matched by a
  train-only cluster table (R6), (b) what R6 does not match is concentrated in two
  benchmarks with known sub-categories, (c) it reverses at high λ, and (d) it closes
  < 8% of the oracle gap.
- The **cost-aware task (or sub-task) lookup is the routing baseline to carry
  forward**, as the prereg specified for the non-GO outcomes. Per-query semantic
  residuals are an optional, λ-dependent ablation, not a contribution.
- Relation to prior work (see `../LIT-REVIEW.md`): a cost-aware cluster table is what
  Avengers-Pro and UniRoute already publish, and output-length control as a routing
  variable is R2-Router (ICML 2026). The cost axis therefore offers no free novelty
  for a semantic router either.

## Limitations

The labels are one-shot, so both correctness and tokens are single draws (see
Chen, arXiv 2607.03436, on single-draw noise). Tokens are only a proxy for cost.
The post-hoc contrasts were selected after seeing the pre-registered results. R6's
k-means k is small (1–5 clusters per benchmark), so it is a *coarse* lower bound on
what a true sub-category table could do.
