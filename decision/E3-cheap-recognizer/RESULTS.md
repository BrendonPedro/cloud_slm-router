# E3 results: tiny lexical recognizer vs GTE-7B in the cost-aware lookup

Run 2026-11-07 with no changes to `PREREG.md`. Raw outputs are in
`results/e3_results.json` and `results/e3_run.log`. The GTE recognizer (G) reproduces
E2's R2 utility exactly at every λ (for example 0.7067 at λ=0 and 0.6069 at
λ=0.03), which confirms that the lookup pipeline is the same.

## Pre-registered verdict: **SUFFICIENT**

| Recognizer | Task accuracy (5-fold pooled) |
|---|---|
| G: GTE-Qwen2-7B + RidgeClassifier | 0.9967 |
| **L: word+char TF-IDF + LinearSVC** | **0.9958** |
| O: oracle task label | 1.0000 |

U_L − U_G is between −0.14 and +0.04 pt at all 13 λ values, so |Δ| ≤ 0.3 everywhere.
The largest gap is at λ = 0.3: −0.14 [−0.28, −0.01]. The lexical recognizer is
within 0.11 pt of the *oracle-task* lookup at every λ. L's errors are almost all
aime→math500 (33) and mmlupro→medqa (12), which are near-duplicate task families
whose tables are similar.

Measured cost: featurising and predicting with L takes **about 5.1 ms per query**
on a shared 4-core CPU, single-process sklearn, timed over the test fold. The
prereg's motivation said "< 1 ms", and that guess was wrong. Even so, L is orders of
magnitude cheaper than a 7B embedding forward pass, and it needs no GPU.

## What this means (by the interpretation fixed in advance)

- On this pool, the 7B embedder is unnecessary for the routing decision. All of
  the routing value measured in E1 and E2 that counts toward a decision, namely the
  task lookup's +3.3 pt over the best single model at λ=0 and +11 pt at a 1k-token
  budget, is available from a CPU lexical recognizer plus a cost-aware table.
- The old micro-encoder / KD work survives only in a narrow role: a **compact
  task/sub-task recognizer**, needed **only if** robustness to paraphrased or
  non-benchmark traffic requires more than lexical features. E3 does not test that
  robustness, because LLMRouterBench queries carry strong format cues. It is the
  first thing to test on real or held-out-domain traffic.
