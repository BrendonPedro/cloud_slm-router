# Deliverable 12: Stage-0 prototype (pipeline validation + simple baselines)

*Run 2026-09-23 (iteration 12) on the audit host. This directory implements the
**zero-inference** part of `architecture/recommended-experiment.md` (§4–§5) with the
Python standard library alone. It does **not** implement the paper's router: no
Tiny-LM, no encoder (B-s/B-m), no generative router (A/A-zs), no prefill probe (C-pre),
no Jacobi component, no Split-LLM. No model was run. Every number below was computed by
`stage0.py` from LLMRouterBench's **released** per-query scores. Anything not produced
that way is labelled as an estimate or an interpretation.*

## 1. What was run

| Step | Command (cwd = this directory) | Output |
|---|---|---|
| main run | `python3 stage0.py config/stage0.json` | `logs/stage0_run.log`, `splits/*.json`, `preds/*.jsonl`, `results/stage0_raw.json` |
| summary | `python3 summarize.py` | `results/stage0_summary.md` (formatting plus mean/std only) |
| determinism check | same main command re-run in a copy at `/tmp/proto_rerun`, then `diff -r` of `preds/` and `splits/` | `logs/determinism.txt` |
| environment | see `logs/environment.txt` | Python 3.12.3, WSL2 6.6.87.2, AMD Ryzen 5 8500G (4 vCPU visible), ~9 GiB RAM, no GPU |

- **Input:** `/tmp/llmrb/bench-release`, extracted from `bench-release.tar.gz`, sha256
  `b79f8cde…48c8f1`. The hash was re-checked this iteration and matches the HF LFS oid
  recorded in `research/raw/experiment/hf_dataset_tree.json`. The bundle is **not**
  committed (1.28 GB). The download command is in `research/raw/experiment/fetch-log.txt`.
- **Committed artefacts contain no benchmark text.** Split files and prediction files
  identify queries only by `sha256(origin_query)[:16]`. They can be rejoined to the
  bundle with `stage0.py`'s `qhash`.
- **Wall time:** 4 min 44 s for the full run (all fits, 10,000-resample bootstraps).
  The time for each TF-IDF+LR fit is in `results/stage0_raw.json` → `tfidf_fit`.

## 2. Configuration (frozen in `config/stage0.json`)

- **Pairs:** P-L = Llama-3.1-8B-Instruct → qwen3-235b-a22b-2507; P-Q = Qwen3-8B →
  qwen3-235b-a22b-2507 (recommended-experiment §4).
- **Pool:** mmlupro/test_1000, gpqa/test, livecodebench/test, livemathbench/test and
  aime/hybrid. That gives 2,432 unique queries for each pair, the same count as the
  inventory run in iteration 11. All scores were asserted to be binary {0, 1}.
- **Label:** y = 1 if score_weak ≥ score_strong ("safe to keep on edge").
  P(y=1) = 0.559 (P-L) and 0.886 (P-Q).
- **Router input:** the `origin_query` field only. For MMLU-Pro this means the question
  **without** its answer options.
- **Splits:** 60/20/20, stratified by (dataset group, weak score, strong score),
  seeds 0–4. LODO holds out one of {MMLU-Pro, GPQA, LiveCodeBench, math =
  LiveMathBench ∪ AIME} and splits the remainder 80/20 into train/dev with seed 0.
  The split sha256s are in `results/stage0_raw.json` → `split_sha256`.
- **TF-IDF+LR:** word 1–2-grams, min_df 2, sublinear tf, L2-normalised. Logistic
  regression uses full-batch AdaGrad for 60 epochs, with the L2 penalty chosen from
  {1e-4, 1e-3, 1e-2} by dev log-loss (1e-3 was chosen in 17 of 18 fits).
- **Metrics:** CCR@−1 is the smallest *dev* call rate whose dev quality is ≥ dev
  strong accuracy − 1 pt. It is converted to a threshold on p̂ and applied to test,
  which reports the test call rate, the test quality and whether the test target was
  met. The deferral AUC is the area under the quality vs cloud-call-rate curve, with
  the least-safe queries escalated first. ECE uses 15 equal-width bins; Brier is also
  reported. The paired bootstrap resamples test queries 10,000 times, stratified by
  group, and gives a 95% percentile CI for AUC(TF-IDF+LR) − AUC(baseline).

### Deviations from `recommended-experiment.md` (to be accepted or fixed by the advisor)

1. The **neural routers (B-s, B-m, A, A-zs, C-pre) and the RouteLLM BERT baseline
   were not run**, because torch is not installed and there is no GPU. Only the stdlib
   baselines exist.
2. **"Random at matched call rate"** is implemented in two ways: (a) as a router that
   gives each query a uniform random score and is scored like any other router, and
   (b) as the analytic expectation (1−r)·weak + r·strong at the TF-IDF router's own
   test call rate r (column `random_same_rate_quality`).
3. **Ties in p̂ are broken with a seeded random order.** For the dataset-prior router,
   whose scores are constant within a group, this means random order within each group.
   The threshold transfer cannot split a tie block, which is why the oracle's CCR equals
   the test share of y = 0 instead of the minimum achievable rate.
4. **McNemar and Holm corrections were not computed yet.** The only test implemented
   is the per-seed bootstrap on deferral AUC.
5. In MMLU-Pro, 3 duplicated query strings are resolved by keeping the last record.
   For Qwen3-8B, one of these duplicates has **disagreeing** scores; this is logged in
   `logs/stage0_run.log`.

## 3. Measured results (copied from `results/stage0_summary.md`)

**In-domain, mean ± std over 5 seeds** (n_test = 487 for P-L, 485 for P-Q):

| pair | router | test call rate at CCR@−1 τ | test quality | strong acc | target met | deferral AUC | ECE | Brier |
|---|---|---|---|---|---|---|---|---|
| P-L | random | 0.972 ± 0.013 | 0.709 ± 0.004 | 0.719 | 2/5 | 0.509 ± 0.007 | 0.258 | 0.330 |
| P-L | dataset-prior | 1.000 ± 0.000 | 0.719 | 0.719 | 5/5 | 0.529 ± 0.001 | 0.002 | 0.242 |
| P-L | **TF-IDF+LR** | **0.949 ± 0.014** | 0.709 ± 0.006 | 0.719 | 3/5 | **0.542 ± 0.003** | 0.052 | 0.236 |
| P-L | oracle | 0.441 | 0.739 | 0.719 | 5/5 | 0.636 | 0 | 0 |
| P-Q | random | 0.580 ± 0.207 | 0.700 ± 0.014 | 0.718 | 1/5 | 0.698 ± 0.008 | 0.396 | 0.327 |
| P-Q | dataset-prior | 0.410 ± 0.000 | 0.732 | 0.718 | 5/5 | 0.716 ± 0.001 | 0.002 | 0.099 |
| P-Q | **TF-IDF+LR** | **0.299 ± 0.086** | 0.722 ± 0.009 | 0.718 | 5/5 | **0.723 ± 0.005** | 0.017 | 0.099 |
| P-Q | oracle | 0.113 | 0.794 | 0.718 | 5/5 | 0.750 | 0 | 0 |

**Bootstrap CIs for AUC(TF-IDF+LR) − AUC(baseline), in-domain.** The CI excludes 0
against *random* in 5/5 seeds for P-L and 4/5 for P-Q. It excludes 0 against the
*dataset-prior* router in only 2/5 seeds for each pair (point differences
+0.003 to +0.018).

**LODO, seed 0.** Deferral AUC of TF-IDF+LR minus random, with 95% CI:

| held-out group | P-L | P-Q |
|---|---|---|
| MMLU-Pro | −0.001 [−0.014, +0.013] | **−0.014 [−0.023, −0.005]** |
| GPQA | +0.003 [−0.031, +0.036] | −0.009 [−0.039, +0.021] |
| LiveCodeBench | **−0.017 [−0.030, −0.005]** | +0.008 [−0.002, +0.018] |
| math | −0.023 [−0.053, +0.006] | **−0.023 [−0.045, −0.002]** |

## 4. What these numbers mean (interpretation, not additional measurement)

1. **The pipeline works end to end.** Sanity checks hold: the random router's AUC
   equals (weak + strong)/2 up to seed noise (P-L: 0.509 vs 0.5085); the oracle's
   call rate equals the test share of y = 0; and the committed `preds/` and `splits/`
   are byte-identical on re-run, and `stage0_raw.json` differs only in wall-clock fit times (`logs/determinism.txt`).
2. **The simple-baseline bar for H1 is now a number.** In-domain, TF-IDF+LR's dev-tuned
   operating point calls the cloud on 94.9% (P-L) and 29.9% (P-Q) of test queries, and
   it meets the "strong − 1 pt" test target in only 3/5 (P-L) and 5/5 (P-Q) seeds, against oracle rates of 44.1% and 11.3%. Criterion 1 of
   recommended-experiment §9 therefore requires a learned router to reach ≤ 89.9%
   (P-L) or ≤ 24.9% (P-Q) call rate. Both are inside the oracle headroom, so H1 is
   **testable, not yet tested.**
3. **Lexical features do not transfer across datasets.** In LODO, TF-IDF+LR is never
   significantly better than a random router, and it is significantly *worse* in 3 of
   8 folds. On the in-domain data, much of its advantage over random is shared with the
   dataset-prior leak control. This matches, on our pool, the "ties simple baselines"
   warning cited in deliverable 3 (§4 item 8). Criterion 2 (beat random and
   dataset-prior in ≥ 3 of 4 OOD folds) is the demanding one, and it is where any
   neural router has to be evaluated.
4. **ECE alone is not informative here.** The dataset-prior router is almost perfectly
   calibrated in-domain (ECE 0.002) while having almost no ranking ability. Calibration
   claims in the revised paper must therefore be paired with a ranking metric (deferral
   AUC or AURC) and reported OOD.
5. **Dev-tuned thresholds break under dataset shift.** In P-Q LODO:MMLU-Pro, even the
   *oracle* ends up with call rate 0 and misses the target. The reason is that on the
   dev groups (GPQA, LiveCodeBench, math) always-edge already meets "strong − 1 pt",
   so the dev threshold escalates nothing. Any "no retraining" or "adaptive threshold"
   claim (manuscript L40 "without requiring costly retraining", L65 C2, L182 "remain effective as the model pool evolves") has to address how
   τ is set on a new distribution.

None of this says anything yet about Tiny-LM vs encoder (H2) or about Split-LLM (H3).

## 5. What remains (not done, not claimed)

- B-s/B-m encoder fine-tuning and the A/A-zs generative routers (need torch; A-0.5B
  LoRA on this CPU is expected to take hours [E, unmeasured]); C-pre (needs a GPU for
  8B forward passes); the RouteLLM BERT transfer baseline.
- McNemar tests at the dev-selected operating point; Holm correction across the family;
  AURC; the label-definition, truncation and train-size ablations.
- Stage 1 (own labels for the manuscript's edge models) and Stage 2 (Split-LLM
  testbed): not started.
- Router latency: not measured. TF-IDF+LR's fit times are recorded only as pipeline
  bookkeeping and say nothing about edge latency.
