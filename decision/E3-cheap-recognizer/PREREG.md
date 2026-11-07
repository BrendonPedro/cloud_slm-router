# E3: Can a tiny task recognizer replace the 7B embedder in the cost-aware lookup?

Pre-registered 2026-11-07, after E1 and E2 finished and before any E3 number was
computed.

## Why

E1 and E2 say the routing value on this pool comes almost entirely from
*recognising the benchmark/task* and then looking up a cost-aware table (R2). If
that holds, the semantic-routing *component* of a deployment paper only has to be
an accurate, very cheap task recognizer. The GTE-Qwen2-7B embedder used so far
costs about as much as a 7–9B forward pass, which would defeat the purpose on an
edge device. E3 tests whether a recognizer with almost no compute (character and
word TF-IDF plus a linear classifier, under 1 ms on a CPU) loses anything. This
is also the narrowest defensible revival of the old micro-encoder work: the
encoder's job becomes task recognition, not winner prediction.

## Setup (frozen)

- Same pool, same 5 frozen folds, same 13-value λ grid, the same
  `choose()` tie-breaking and the same per-task train-mean tables as E2's R2.
  Everything is fit on outer-train only.
- Recognizers:
  - **G**: GTE-7B + RidgeClassifier (α=1, balanced). This is E2's R2,
    recomputed in this script.
  - **L**: TF-IDF (word 1–2-grams, `sublinear_tf`, `min_df`=2) ⊕ TF-IDF (char_wb
    3–5-grams, `sublinear_tf`, `min_df`=2), fed to LinearSVC (C=1, balanced).
  - **O**: oracle task label (upper bound, = E1's R1).
- Metrics: task accuracy, and realised utility U(λ) of the lookup with each
  recognizer, with a paired bootstrap of L − G (2,000 resamples, seed 0).

## Frozen decision rule

- **SUFFICIENT**: L task accuracy ≥ 98% **and** |U_L − U_G| ≤ 0.3 pt at every λ
  (or L ≥ G).
- **INSUFFICIENT**: otherwise. Report where it fails.

## Interpretation fixed in advance

- **SUFFICIENT** → the routing component of the deployment paper can be a lexical
  recognizer plus a table, or a tiny distilled encoder if robustness to paraphrase
  or out-of-benchmark queries is needed later. That robustness is *not* tested
  here. The 7B embedder is unnecessary for the routing decision on this pool.
- **INSUFFICIENT** → a learned compact encoder (micro-encoder / KD from GTE) is
  justified as the recognizer, and its accuracy target is G's task accuracy.

## Limitation stated in advance

Benchmark recognition on LLMRouterBench is easy because the benchmarks have
distinctive formats. Real traffic will not be labelled by benchmark. E3 measures
the *cost* of the recognizer on this pool, not how it generalises to unlabelled
production traffic.
