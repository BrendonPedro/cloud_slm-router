# PriorBench — Jev

*Measured, pre-registered evaluation of AI systems.*

**An independent, pre-registered evaluation of TypeSafe AI's Jev — 5,721 calls,
21 experiments, $0.176.**

Model `typesafe/jev-1.13-20260917`, accessed through OpenRouter, measured from
Western Europe on 20 September 2026.

📄 **[Read the full report →](paper/REPORT.md)**
📊 **[All 50 predictions and their outcomes →](paper/tables/predictions.md)**

![Zero-shot against a reading scale](paper/figures/fig4_benchmark.png)

---

## Headline findings

- **Latency is a fixed cost, not a workload cost.** ~430 ms floor. **800 typed
  judgements in one call: 985 ms, $0.00075.** Chaining two Jev calls wastes
  430 ms for nothing.
- **95.9 % zero-shot** on our 400-item benchmark, versus 77.2 % for hand-written
  keywords and 66.0 % for supervised TF-IDF + logistic regression that saw every
  label.
- **TypeSafe's own documentation understates the model.** Its "jaggedness" page
  says Jev cannot compare numbers and that date ordering is unreliable. We
  measure **99.6 % across 13 designs**. Negation, another listed failure mode,
  scores **100 %**.
- **It always answers.** A cake recipe is classified as a technical issue at
  **0.94 confidence**; random letters at **0.97**. Without an explicit "none of
  these" option, **0 of 30** out-of-scope messages were flagged — at 0.99
  confidence.
![Intermediate thresholds do nothing](paper/figures/fig3_confidence.png)

- **Gate at 0.99 or not at all.** Accuracy above threshold is flat from 0.50 to
  0.95, then jumps to **100 % at 0.99, covering 60.2 % of traffic**.
- **Eight concurrent requests is the operating point.** Throughput saturates near
  11 req/s.
- **Wrong criteria descriptions are catastrophic:** 16.7 %, below the 25 % random
  floor. Missing descriptions cost only 0.8 points.

## This is the surface

Everything here was produced in a single evening. It is a **wide, shallow
pass**: 21 experiments across the whole model, none of them taken as far as it
could go. Every number below is a first measurement, not a final one.

**This repository is updated daily.** The plan, in order:

- **Separate the model from the gateway.** The ~430 ms floor is the single
  biggest open question in this report, and native API access settles it.
- **Go deeper on every axis.** Counting and cardinality are mapped coarsely;
  the calibration curve deserves ten times the items; the `score` primitive has
  had one experiment and needs five.
- **Automate the whole suite.** The harness is already parameterised. The goal
  is a single command that re-runs all 21 experiments against any model version
  and diffs the results — so a silent model update shows up as a diff, not as a
  surprise.
- **More languages, more adversarial surface, more failure modes.** Ten of the
  vendor's documented weaknesses have been tested. There are more, and there are
  failure modes nobody has written down yet.
- **Other models.** The method in [`METHOD.md`](METHOD.md) is not
  Jev-specific. Jev is the first subject, not the only one.

Corrections and replications are the fastest way to make this better. If a
number here is wrong, the harness is built so you can prove it.

## Ten practical recommendations

1. One call, many questions — never chain Jev calls.
2. Eight concurrent requests; beyond that you buy latency, not throughput.
3. Gate at 0.99, or do not gate.
4. Always offer an explicit "none of these" option.
5. Use `noul` when you need a number — twice as well calibrated as a `choice`'s
   confidence. But do not threshold it at 0.5; it is not reproducible there.
6. Keep criteria short or omit them — but never let them be wrong.
7. Fix your option order for ambiguous tasks (up to 13 points of movement).
8. Do not put it in a sub-300 ms hot loop from Europe.
9. Do not use it to count beyond a handful of items.
10. Test the documentation's warnings yourself — several did not reproduce.

## Method

Twelve rules, stated in full in the report. The three that matter most:

- **Every hypothesis written before collection.** 50 predictions, timestamped in
  [`PREREGISTRATION.md`](PREREGISTRATION.md). **26 confirmed, 21 falsified.**
- **Falsified predictions are published**, including the systematic bias they
  reveal: 18 of our 21 misses were in the same direction — we kept predicting
  failure and kept being wrong.
- **Every surprising result replicated with a different design** before
  publication. The "documentation understates the model" claim was re-tested
  across 13 independent designs before we wrote it down.

An independent recount script (`analysis/recount.py`) recomputes every headline
figure from raw JSONL without importing any analysis code.

## Reproducing

```bash
git clone https://github.com/priorbench/jev
cd jev
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python setkey.py            # paste an OpenRouter key; never echoed
./.venv/bin/python latency/bench.py     # 491 calls, ~4 min
./.venv/bin/python probes/t6_banc.py    # 800 calls, ~1 min
./.venv/bin/python analysis/recount.py  # verify the totals
```

Full suite: 5,721 calls, $0.176, ~25 minutes at 8-way concurrency. Seeds fixed
at 20260920. Every raw response is in `*/raw/*.jsonl`.

## Layout

```
paper/REPORT.md              the report
paper/tables/predictions.md  all 50 predictions and outcomes
PREREGISTRATION.md           hypotheses, timestamped before each wave
bench/reference_set.py       the 400-item benchmark
baselines/no_ai.py           keyword, TF-IDF+LR and random baselines
probes/                      the experiments
latency/                     latency harness
analysis/                    cross-cutting analysis and independent recount
*/raw/*.jsonl              every raw response (published)
```

## Known limits

1. **Everything goes through OpenRouter.** We cannot separate model latency from
   gateway latency. The ~430 ms fixed cost is measured; its cause is hypothesis.
   **Anyone with native API access can settle this in twenty minutes.**
2. **Our benchmarks are ours** — reproducible, but not recognised standards.
3. **One location, one day, one model version.**
4. **Some classification ground truth is disputable** — flagged, reported
   separately, never folded into headline figures.

Corrections welcome. The harness is built to be re-run against them.

## Method

The twelve rules are documented once, separately, in
[`METHOD.md`](METHOD.md) — they apply to every PriorBench evaluation, not just
this one.

## Citing this

```
1j6c (2026). PriorBench — Jev: an independent, pre-registered evaluation
of TypeSafe AI's System One model. https://github.com/priorbench/jev
```

A machine-readable [`CITATION.cff`](CITATION.cff) is included.

## Contact

`1j6c@proton.me` — corrections, replications and disagreements all welcome.

## License

MIT
