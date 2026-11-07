# Week execution plan: 2026-11-09 (Mon) to 2026-11-13 (Fri)

This plan executes the **MODIFY** decision in `GO-NOGO-REPORT.md`. Work is ordered by
**information gain per hour**: the probability that a block changes the paper decision,
divided by what it costs in Brendon-hours and booked machine time. It is not ordered by
how easy a block is to run. The first two days are spent on the assumptions that can
kill the systems paper for almost no cost. **No runtime code is written and no joint
machine time is used until those assumptions have survived.**

All decision rules below already exist in E0 §8, BASELINES §4 and GO-NOGO §7–§8. This
plan only puts them in order. **It adds no new pass/fail criteria.** The one new item is
a harness-parity check (Day 1), which validates the measurement pipeline and decides
nothing about SPLIT.

---

## 1. Open assumptions, ranked by information gain

The probabilities are subjective priors, stated before any hardware access and based on
the evidence files. They exist to justify the order, not to be reported as results.

| Rank | Assumption still open | P(it changes the decision) | Cost | What it decides | When |
|---|---|---|---|---|---|
| 1 | Film accepts MODIFY **and** the §8.3 measurement-paper fallback | ≈ 0.3 | 1 email / 30 min meeting | Whether this week's plan is the right plan at all | Sat–Mon AM |
| 2 | The "DGX" is A100/H100-class, and an edge with a ≥ 24 GB NVIDIA GPU exists | ≈ 0.3–0.5 that E0 is **blocked** (a "DGX" today is often a DGX Spark/GB10; HARDWARE-PLAN §2.2) | 30 min | Whether E0 can run (GO-NOGO §7 item 5) | Mon AM |
| 3 | The **measured** 32B-bf16 vs EDGE-best(M) accuracy gap is ≥ 3 pt on some task in some mode (S1) | ≈ 0.5 that the gap is < 3 pt everywhere at 16/24 GB; ≈ 0.3 that it is < 3 pt at 12 GB as well | ≈ 6–7 server GPU-h, unattended, **no new code** | E0 early stop. It can end SPLIT before any runtime code is written | Mon–Tue AM |
| 4 | Measured EDGE/REMOTE profiles leave the pre-hardware conclusions intact (H-joint fails, RTT irrelevant, load matters) | ≈ 0.2 | ≈ 3.5 h edge + ≈ 1 h server + a 2 h adapter | Whether anything except SPLIT is alive; whether the assumed throughputs were on the right hardware branch (HARDWARE-PLAN §2.3) | Mon–Tue |
| 5 | U-max(12) and U-max(16) edge slices fit and run at 16k context (F, edge half, S6) | ≈ 0.15 | 0.5 h | F, before joint time is booked | Mon |
| 6 | The lexical task recogniser survives out-of-benchmark traffic (GO-PIVOT §5) | ≈ 0.15 that it re-opens a semantic GO | CPU only, ≈ 0.5 day, runs while GPUs are busy | Whether the router can remain "a component" | Tue–Wed |
| 7 | Q: the split output is equivalent to the unsplit model (J1) | ≈ 0.1 (Cunningham: token-identical at fp16) | ≈ 1 day code + 2 h joint | Q | Wed–Thu, **only if 3 leaves SPLIT alive** |
| 8 | R: SPLIT opens a ≥ 3 pt on-time quality tier in some cell (J2 + replay) | Decisive, but expensive | 1.5–4 h exclusive joint time | E0 PASS/FAIL | Thu–Fri, only if 3 and 7 pass |
| 9 | Trace-driven replay matches live runs within ±10% (J3) | ≈ 0.1 | 2–3 h joint | Whether replayed numbers can be trusted | Following week |
| 10 | No new duplicate paper (model choice + layer split vs quantised edge) | ≈ 0.05 | 1 h search | Novelty (GO-NOGO §8.1) | Fri |

Q (rank 7) has a lower prior risk than S1 (rank 3) but costs about ten times more
Brendon-time. That is why S1 runs first even though Q is "the first thing E0 checks"
on paper.

---

## 2. Decision gates

| Gate | When | Input | Rule (source) | If it fails |
|---|---|---|---|---|
| **G0** | Mon 10:00 | Film's reply; Day-0 inventory | Film accepts MODIFY + fallback; the six hardware go/no-go conditions (HARDWARE-PLAN §3) | No Film agreement: stop and settle the paper direction first. Conditions 1–2 fail: E0 **blocked**, follow branch C (§4). Only 3–5 fail: run S1–S6 anyway |
| **G1** | Tue 09:00 | S1 `e0/q3_scores.jsonl` | Early stop (E0 §8), applied **per mode**: if 32B-bf16 − EDGE-best(16) < 3.0 pt on every task in both modes, only the 12 GB class and the 6 core cells remain. If 32B-bf16 − EDGE-best(12) is also < 3.0 pt on every task in both modes, the same argument (on-time utility ≤ accuracy; edge actions are faster in the same mode) rules out 12 GB: **R fails by bound** (GO-NOGO §10 step 6) | SPLIT removed. Write `e0/DECISION.md` (R: FAIL by S1 bound). Go to branch B |
| **G2** | Tue 17:00 | S4/S5 profiles + S1 per-query data through the replay adapter | H-joint and H-state without SPLIT, cross-fitted, against `B*` (BASELINES §4; PROBLEM-FORMULATION §4) | Expected outcome: H-joint fails without SPLIT. That is not a gate failure; it confirms that everything rests on SPLIT. If H-joint unexpectedly **passes** without SPLIT, report it, re-check against the hardware branch, and tell Film. Do not change the plan mid-week |
| **G3** | Thu 12:00 | J1 | Q1 + Q2 (E0 §8), with one implementation fix allowed | SPLIT removed; no activation compression as a rescue. Branch B |
| **G4** | Fri 12:00 | J2 + replay | R (E0 §8): some cell ≥ 3.0 pt, CI > 0; the Qwen3-30B-A3B check where it fits (GO-NOGO §7 item 4) | SPLIT removed for lack of a regime. Branch B |

---

## 3. Day by day (main branch: hardware available, SPLIT still alive)

### Sat 7 / Sun 8: no machine time

- Send `GO-NOGO-REPORT.md` to Film with the two questions in GO-NOGO §10 step 1.
- Email the lab admins with the access request: root/`CAP_NET_ADMIN` on the edge,
  permission to lock clocks, and a **tentative** exclusive 6 h window on both machines
  for **Thu 13:00–19:00** (cancellable if G1 or G3 fails).

### Mon 9: resolve ranks 1–2, start rank 3 before lunch

| Time | Brendon | Server | Edge | WSL (CPU) |
|---|---|---|---|---|
| 09:00 | HARDWARE-PLAN §3 inventory on all machines → `e0/env/<host>.txt`; **G0** | — | — | — |
| 09:45 | Download models pinned by commit: Qwen3-32B, Qwen3-8B, Qwen3-{8B,14B,32B}-AWQ (≈ 120 GB) | download | download 8B/14B-AWQ | Draw the 200-query sample (`seed=20261107`, E0 §4.4), **reusing the cached `prompt` strings** from `results/bench/<b>/<split>/Qwen3-8B/*.json` so that the LLMRouterBench scorers apply unchanged |
| 11:00 | **Harness parity** (≈ 20 min): Qwen3-8B bf16 under vLLM, through the LLMRouterBench `data_collector` + evaluators, at the cached run's settings (T = 0.2, top-p 1.0, the template in `config/data_collector_small_model_config.yaml`), on the 200 queries | run | — | Compare with the cached per-query scores |
| 11:30 | Start **S1**: both modes, 5 models, 2 seeds, vendor sampling (E0 §4.3), unattended | S1 (≈ 6–7 h) | — | — |
| 12:00 | Edge blocks, while S1 runs | — | **S6** (F, edge half, 0.5 h) → **S5** (profiles at 12/16/24 GB caps, ≈ 2 h) → **S3** (8B noise floor, ≈ 1 h) | — |
| 14:00 | Write `evidence/measured_replay.py` (§5) | — | — | Adapter + regression test |
| 18:00 | Check S1's truncation rate and failed requests; re-queue only crashed requests, never low-scoring ones | S1 finishing | — | — |

**Harness-parity rule (validation only, not a SPLIT criterion).** Mean accuracy per
benchmark must lie within the 95% CI of the cached run, and per-query agreement must be
≥ 80% on the short-output tasks (MMLU-Pro, GPQA). If it fails, fix the harness (prompt,
chat template, answer extraction) **before** trusting S1. Fixing the harness does not
consume E0's one allowed Q fix. The cached data does not record its sampling settings;
the template value is the best available guess. If parity cannot be reached at that
guess, record the residual gap and carry it into Q3 as a stated limitation.

**Done means:** `e0/env/*.txt`, `e0/sample_200.jsonl`, `e0/parity.md`, S1 running or
finished, S5/S6 logs, and the adapter passing its regression test.

### Tue 10: decide whether SPLIT is worth any code (G1, G2)

| Time | Work |
|---|---|
| 09:00 | **G1.** Compute the per-task, per-mode gaps 32B-bf16 − EDGE-best(M) from `e0/q3_scores.jsonl`, where EDGE-best(M) is taken over (model, mode) for each memory class according to S6's fit results. Write the one-paragraph note to Film (GO-NOGO §10 step 6) |
| 09:30 | Server: **S4** (REMOTE profiles at loads {0, 8, 32}, ≈ 1 h), then **S2** (Q1 reference + in-host pipeline floor, ≈ 2 h) **only if G1 left SPLIT alive** |
| 11:00 | Run the adapter with measured S4/S5 profiles and S1 per-query data. Output: `evidence/measured_replay.md` with H-joint and H-state without SPLIT, and the F4 contention-gradient check (GO-NOGO §8.2) from S4's three loads |
| 14:00 | If SPLIT is alive: start the split runtime (two-process HF + socket, E0 §3.3), written against S6's edge slices. If SPLIT is dead: branch B |
| 17:00 | **G2** |

**Done means:** `e0/G1.md`, `evidence/measured_replay.md`, and S4 (plus S2 if
applicable) profiles on disk.

### Wed 11: split runtime (SPLIT alive) + router robustness on CPU

- **Brendon:** finish the split runtime. Test it **in-host first**, with both halves on
  one server: this reproduces the S2 pipeline floor, and a mismatch is a code bug, not
  a Q failure. Then run a 10-query edge↔server smoke test with netem off.
- **WSL, in parallel:** the out-of-benchmark router robustness test (GO-PIVOT §5), as
  **one pre-declared test, not a sweep**:
  - leave-one-benchmark-out for the existing TF-IDF + LinearSVC recogniser, plus one
    paraphrase set;
  - compare the task-lookup table with the query-level routers already in the repo;
  - no hyperparameter search;
  - GO-PIVOT's rule applies: query-level ≥ 1 pt over the table with CI > 0 re-opens
    robust task recognition as a router item. That changes **the router component**,
    not this week's systems plan.
- **Confirm or cancel** Thursday's exclusive window by 17:00.

**Done means:** a split runtime that passes the in-host check, and
`deployment-pivot/router_ood.md`.

### Thu 12: Q, then E0-L (G3)

| Time | Work |
|---|---|
| 09:00 | **J1:** Q1 teacher-forced logits for U-min and U-max(16), 200 queries; Q2 with 30 × 1,024-token greedy free-runs (≈ 2 h) |
| 11:30 | **G3.** Compute Q1/Q2 against the S2/S3 floors. One implementation fix is allowed (re-run J1 once) |
| 13:00–19:00 | **J2 E0-L** in the exclusive window. Order: the 6 core cells first, then contention (4), RTT (6), held-out (4), bandwidth and cut-invariance. If G1 early-stopped 16/24 GB, run only the 6 core cells at 12 GB and release the window early. Log `tc -s qdisc` before and after every cell |

### Fri 13: decide (G4) and report

| Time | Work |
|---|---|
| 09:00 | Fit the latency model on J2's training cells; check the held-out cells within ±10% |
| 10:00 | Compute R for every cell (E0 §8) → `e0/R_cells.md`. Add Qwen3-30B-A3B as a competitor where it fits (GO-NOGO §7 item 4); if S1 did not include it, run its Q3 on the server today (≈ 1 GPU-h) |
| 12:00 | **G4** → `e0/DECISION.md` |
| 13:00 | If E0 passes: F3 vs all 12 baselines on measured profiles, with SPLIT in the action set (BASELINES §4) → H-joint and H-state with SPLIT. If it fails: the `B*` comparison from Tuesday stands |
| 15:00 | Re-run the LIT-REVIEW §5 duplicate search, 1 h, primary sources only |
| 16:00 | Decision memo to Film: E0 result, H-joint/H-state, which form of the paper (GO-NOGO §3), next week's J3 plan |

**Done means:** `e0/DECISION.md`, `e0/R_cells.md`, and the memo sent.

---

## 4. Branches

**Branch B: SPLIT removed at G1, G3 or G4.** No split-runtime work after the gate.
Release the joint window. Then:
- **Remaining days:** write the measurement-paper skeleton (GO-NOGO §8.3) from E1–E3,
  `evidence/measured_replay.md`, `e0/G1.md` (or Q/R logs), and the network-irrelevance
  result.
- **Next week:** run J3 for `B-route`, F3 (EDGE/REMOTE) and `B-fixed`, 50 queries × 2
  states, because the measurement paper's claims also rest on replay.
- **F4** is tried only if the GO-NOGO §8.2 gradient condition holds on Tuesday's numbers
  **and** Film approves. No other reformulation.

**Branch C: E0 blocked at G0** (no A100/H100-class server, or no ≥ 16 GB NVIDIA edge).
- Record `e0/DECISION.md` as **BLOCKED**, not FAILED.
- Still run whatever single-machine blocks the hardware allows:
  - S1 on any server with bf16 and ≥ 80 GB, even if it is slow. Accuracy does not depend
    on hardware speed, and S1 alone may kill SPLIT, which saves the cost of finding
    better hardware.
  - S5/S6 on whatever edge exists.
- Ask Film or the lab for A100/H100 time. **Do not rent.**
- If the only server is a GB10/DGX Spark, REMOTE is not a meaningful action (GO-NOGO
  §8.1), and the systems version is on hold until real server access exists.

**Branch D: Film rejects the fallback at G0.** Do no hardware work. The disagreement is
about what paper to write. Benchmarking cannot resolve that, and running it first would
only spend the week.

---

## 5. Code written this week (and nothing else)

| Item | Day | Size | Test |
|---|---|---|---|
| `e0/` sample draw + parity script (calls LLMRouterBench `data_collector`/evaluators unchanged; `enable_thinking`, `top_k` **and `max_tokens: 16384`** passed through `extra_body`. `DirectGenerator` never sets `max_tokens`, so without it vLLM's default applies and E0's truncation limit silently changes) | Mon | < 100 lines | Parity rule above |
| `evidence/measured_replay.py`: reads S1 per-query `(score, tokens, n_in)` and S4/S5 profile JSON; reuses the policy and bootstrap code from `baseline_crossfit_check.py` | Mon | ≈ 150 lines, pure Python (no numpy on WSL) | **Regression:** with the assumed profiles and the cached 5-benchmark data it must reproduce `baseline_crossfit_check.md` exactly |
| Split runtime (two-process HF + TCP socket, bf16 activations, U-shaped cut) | Tue PM–Wed, only if G1 passes | ≈ 300 lines | In-host equivalence with the S2 pipeline floor before any edge run |

**Note on the replay's model set.** The pre-hardware simulations used the cached pool
(Qwen3-8B, Nemotron-9B, Llama-8B, qwen3-235b, deepseek-v3). The measured replay uses the
**S1 Qwen3 set** on the 200 E0 queries, because those are the models that can actually be
served and profiled on our hardware. Tuesday's numbers therefore have wider CIs than the
cached-pool numbers. That is accepted: the decision is taken on measured models, not on
models we cannot run (PROBLEM-FORMULATION §3.1).

---

## 6. Resource budget for the week

| Resource | Main branch | Branch B (SPLIT dies at G1) |
|---|---|---|
| Server GPU-h | ≈ 10–14 | ≈ 8 |
| Edge GPU-h | ≈ 6 | ≈ 4 |
| Exclusive joint window | 1 × 6 h (Thu) | released |
| Brendon-days of code | ≈ 1.5 | ≈ 0.5 |
| Rentals, field runs, extra devices | none | none |

---

## 7. Explicitly not this week

- No E0-L cell before G1 and G3 have passed. No "quick look" split timings: the roofline
  already bounds them (HARDWARE-PLAN §2.3).
- No activation compression, no speculative decoding, no prefill/decode disaggregation
  variant.
- No new semantic-router training or classifier sweeps. The robustness test on Wednesday
  is a single pre-declared test.
- No multi-device fleet, energy wall-meter or battery campaign.
- No new formulation, objective or decision variable after a gate fails. Only F4, and
  only under GO-NOGO §8.2.
- No re-running a gate with new thresholds. The only pre-declared extension is
  Q3 200 → 400 queries if R's CI straddles 0 only because of sample size (E0 §4.4).
