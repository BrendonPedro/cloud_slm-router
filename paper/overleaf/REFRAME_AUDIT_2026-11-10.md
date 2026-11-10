# Research and manuscript audit: reframing for Film's Overleaf review (2026-11-10)

Scope: synthesis, verification and manuscript restructuring only. No GPU was used, no inference was run, and no frozen protocol was changed. The only computation was a CPU re-run of `e0_r.py gate-ub1` and `gate-ub2` on the archived Stage-1/Stage-2 profiles, which reproduced both archived gate files exactly.

Manuscript baseline: the Overleaf draft `Week 3/main_revised_2026-10-08.tex` ("Model-Utility Routing for Edge, Split, and Remote LLM Inference"). It was imported verbatim as commit `e1202db` on local branch `paper-reframe-2026-11-10` of `~/dev/cloud_slm-router`. The reframed manuscript is the uncommitted working-tree version of `paper/overleaf/main.tex`, so `git diff` shows the full patch. Nothing has been pushed.

---

## 0. Verification of the evidence in the brief

| Claim in the brief | Artifact checked | Status |
|---|---|---|
| MiniLM MLP-64 0.6003 ± 0.0154, AUC 0.6699 | `diagnostics/stratified_cv/CV_CORRECTION_REPORT.md`, `capability_profile/CAPABILITY_PROFILE_REPORT.md` | ✅ exact |
| Capability+MiniLM 0.6082, AUC 0.6725 | `CAPABILITY_PROFILE_REPORT.md` l.46–49 | ✅ but **0.6082 uses the secondary training-only threshold**. The pre-declared primary (p ≥ 0.5) gave **0.5968**. Fair comparison: 0.6082 vs B-threshold 0.6009 = +0.0072, which fails the pre-declared +0.03 bar. The manuscript reports both. |
| Within-benchmark macro AUC 0.501 / 0.512; benchmark identity 0.613 | `within_task_routing/WITHIN_TASK_ROUTING_REPORT.md` Part 4 | ✅ (0.6132 ± 0.0089). Rank-normalised within-fold sensitivity: 0.505 / 0.507, so it is robust to the pooled-AUC issue raised in the 2026-11-06 audit. |
| BBH / KorBench / MBPP strongest; MELD / MedQA / FinQA ≈ chance | `within_task_routing/benchmark_auc.csv` | ✅ (0.713 / 0.681 / 0.669; 0.456 / 0.505 / 0.480). Also: **K&K is inverted, 0.398, with the CI entirely below 0.5.** |
| 120 queries, 6 × 20, 5 repeats, 1,200 generations; 32/120 = 26.7%; 35.0% / 18.3% | `winner_label_stability/group_comparison.csv`, `benchmark_stability.csv` | ✅. New detail: across the 600 repeated pairs, the original winner wins **44.5%**, tie **48.3%**, opposite model wins **7.2%**. |
| Mean \|m\| 0.46; 65% ≥ 0.4; 17 zero; 87/103 = 84.5% | `utility_margin_groups.csv`, `utility_margin_diagnostic.log` | ✅ |
| Target-only: within F1 0.381→0.421, within AUC 0.573→0.640, 5/6, MedQA worse | `target_only_eval_summary.csv`, `target_only_eval_benchmark.csv` | ✅. Per-benchmark n = 16–19. No significance test exists. |
| S1: 200 queries, 5 configs × 2 modes × 2 seeds = 4,000; CONTINUE | `deployment_s1/results/s1_2026-11-08/S1_SUMMARY.md` | ✅ |
| Stage 1 valid, no defects, U-max (3,3)/(5,5)/(9,9), EDGE 12: 8B-AWQ, 16: 8B-AWQ, 24: none, F_pass_static | `e0_stage1_VALID_UB1_CONTINUE.tgz` → `stage1/f_results.json` | ✅. **"24 GB blocked" means the Qwen3-32B-AWQ *edge competitor* failed for an engine reason** (`edge_engine_failures`), so PREREG §8.4(b) blocks the class (`no_split_pass_classes: [24]`). The (9,9) split itself fits at 24 GB. |
| G-UB1 CONTINUE | `gates/gate_ub1.json` | ✅ max Δ = +12.25 [+6.5, +17.25], 14/20 cells pass, Bonferroni-robust |
| Stage 2 H200 self-test 13/0/1; k = 1, 3, 5, 9; 38 rows, 36 usable | `selftest_server.json`, `stage2/P-server-*.jsonl` | ✅ (38 = 2 warm-ups + 36). Median middle-segment decode step: **70.8 / 66.4 / 61.7 / 49.9 ms** at k = 1/3/5/9. |
| G-UB2 STOP, max Δ +0.5 [−4.75, 5.25], Bonferroni −7.125, 0/20 pass | `gates/gate_ub2.json` | ✅ exact. **CPU recompute from the archived profiles matches byte-for-byte on every field except timestamps (both gates).** |
| "Earlier controlled deployment analysis: RTT did not matter; joint optimisation added nothing" | `~/dev/cloud_slm-router/deployment-pivot/evidence/joint_vs_sequential_sim.md` l.1, `baseline_crossfit_check.md` | ⚠️ These are **pre-hardware simulations on cached LLMRouterBench outputs with ASSUMED throughputs/RTTs/powers** (the file header says so), not controlled measurements. The paper must call them simulations or drop them. |

Additional facts found during verification that affect the paper:
- **Open cells = no-raw-text cells in both UB gates**, because the gates bound REMOTE at U = 0 (PREREG §9.1). So the "open" policy was never really tested against REMOTE; that comparison could only have made SPLIT look worse.
- **The competitor that removes SPLIT is Qwen3-8B-AWQ, often in thinking mode**, not REMOTE. At D ≥ 300 s it reaches U = 0.63, more than either SPLIT mode under UB2. At D = 30 s SPLIT loses by 17 pt.
- **UB1→UB2 is entirely the server term**: datasheet roofline vs measured compute of the frozen eager Hugging Face runtime (no CUDA graphs or compilation, by pre-registration). PREREG §11 threat 1 pre-states that this runtime difference "is never used to overturn a FAIL", and the Stage-3 REMOTE-HF cell that would separate "this runtime" from "split itself" was never reached. This is the main reviewer objection to the Split result, and the paper states it.
- **§8.5 sample extension is not triggered**: it applies only when the best cell has Δ ≥ 3.0 with CI lower bound ≤ 0. Here Δ = 0.5.
- **The 20-model pool supports the task-recognition finding** (`decision/E1-pool-headroom/RESULTS.md`, pre-registered): the best query-level router gains +0.42 pt [−0.18, +1.01] over a predicted-task lookup, on the same 11,467 queries and folds. It was not in the weekly brief. It is now one paragraph in §V-C, labelled as a different protocol.
- **The E0 runtime is bitwise-equal to unsplit HF forward/generate on CPU** (tiny model and Qwen3-0.6B, over TCP). The Oct-8 draft's "split-equivalence" question was answered only at that level; the CUDA Q gate was a Stage-3 item and was never reached.

---

## 1. Evidence ledger (chronological)

| # | Date | Research question | Experiment | Pre-declared criterion | Observed | Decision | What changed scientifically | What did NOT change | Next step implied |
|---|---|---|---|---|---|---|---|---|---|
| 0 | to 10-08 | Can a compact router + runtime optimiser choose Edge/Split/Remote? | None (design-only Overleaf draft) | — | No results | — | — | — | Pilot the router |
| 0′ | Oct | Is ~0.60 Macro-F1 good? | Repeated-holdout ladder | — | ~0.60 is the top of the reproducible ladder on this pair | **Film: 0.60 is only a baseline; use stratified K-fold before any Edge/Split/Remote work** | Evaluation standard raised | — | Stratified CV |
| 1 | 10-29→11-01 | Is the 0.60 plateau a protocol artifact or a capacity limit? | Stratified 5-fold CV (11,467 q; seed 42); MLP-64 student; GTE classifier capacity | Reach ≥ 0.70, or show a material gain | MiniLM MLP-64 0.6003 ± 0.0154 (AUC 0.670); GTE LogReg-thr 0.615; RBF-SVM-thr 0.626 (max); LogReg has the best AUC (0.683) | Plateau persists | The estimate is protocol-robust; capacity is not the bottleneck | Router still ~0.60 | Test a new information source |
| 2 | 11-01 | Do hand-built capability features add signal? | Capability-profile v1 (A/B/C) | C beats B by ≥ +0.03 Macro-F1 | Primary 0.5968 (−0.0035); threshold-matched 0.6082 vs 0.6009 (+0.0072) | FAIL | Another feature family adds ≈ nothing | — | Ask *where* the signal is |
| 3 | 11-01 | Is the signal per-query or per-benchmark? | Within-task diagnostic on held-out scores | Clear within-task: AUC > 0.55 and CI > 0.5 | Overall AUC 0.670 vs within-macro 0.501; 3/15 clear (BBH/KorBench/MBPP); K&K inverted; benchmark identity 0.613 F1 | "Task recognition" | Aggregate signal mostly = benchmark recognition | Per-query signal exists on 3 benchmarks (not zero) | Is the label the problem? |
| 3b | 11-07 | Does query-level routing beat a task lookup on the full pool? | E1 (20 models, pre-registered) | Δ ≥ +0.5 pt with CI > 0 | +0.42 [−0.18, +1.01] | NO HEADROOM | Replicates #3 on 20 models | — | Pivot to deployment question |
| 4 | 11-03→11-05 | Are one-shot winner labels stable? | 120 non-ties × 5 repeats × 2 models (reconstructed serving) | Stable = original winner ≥ 4/5 | 32/120 (26.7%); signal 35.0%, chance 18.3%; repeats: 44.5% orig-win / 48.3% tie / 7.2% reversal | Labels are noisy single draws | Instability is mostly win↔tie, not reversal | No evidence the preference is absent | Measure repeated margin |
| 4b | 11-05 | Is there a repeated preference despite instability? | Utility margin m = DS rate − Qwen rate | Descriptive | mean \|m\| 0.46; 65% ≥ 0.4; 17 zero; 87/103 agree with one-shot | — | One-shot labels are noisy versions of real preferences | — | Re-score against it |
| 5 | 11-05 | Do the same router scores fit repeated preference better? | Target-only re-scoring (no retraining) | Within-F1 gain ≥ +0.03, AUC up, not one benchmark | F1 +0.040, AUC +0.068 (0.573→0.640), 5/6, MedQA worse | Practical criterion PASSED | One-shot labels hid some genuine per-query signal | Router not solved; n = 103; no significance test; not shown that training on repeated utility helps | Bootstrap (open); deployment |
| 5c | 11-07 | Does a deployment layer add value? (desk) | Simulation with assumed profiles | Joint F3 − B* ≥ 3 pt | RTT 20→300 ms flips 0/5 EDGE/REMOTE choices; F3 − B* ≈ −0.8…0 | Drop EDGE/REMOTE-optimiser claim; only SPLIT question survives | The deployment question narrows to E0 | All simulated, not measured | S1 → E0 |
| 6 | 11-08 | Is there a quality tier above edge-feasible models? | S1, H200, 4,000 generations | CONTINUE if gap ≥ 3.0 pt on any benchmark × mode at 16 GB | 12 GB: +2.5…+27.5; 16 GB: up to +7.5 | **CONTINUE** | Headroom exists | Says nothing about Split utility or latency | E0 Stage 1 |
| 7 | 11-09 | Does a U-split of Qwen3-32B fit 12/16/24 GB? | E0 Stage 1, RTX 3090 (runs 1–2 INVALID harness; run 3 valid) | F: symmetric split fits + competitor fits | U-max (3,3)/(5,5)/(9,9); EDGE 8B-AWQ at 12/16; 24 GB blocked (32B-AWQ engine failure, §8.4b) | F_pass_static | Split is physically feasible | Not latency evidence | G-UB1 |
| 8 | 11-09 | Can an optimistic bound rule Split out? | G-UB1: 0.9 × edge measured + H200 datasheet, zero link, REMOTE U = 0 | STOP iff max Δ_bound < 3.0 | +12.25 [+6.5, +17.25]; 14/20 pass | **CONTINUE** | Cannot exclude Split yet | **Not latency evidence** (the gate text says so) | Measure server compute |
| 9 | 11-10 | What is the real server-segment compute? | Stage 2, 1 × H200, k = 1/3/5/9 | Self-test pass; profiles complete | 13/0/1; median decode 66 ms (k=3), 50 ms (k=9) | Valid | Server segment ≈ 15 tok/s in the frozen eager runtime | — | G-UB2 |
| 10 | 11-10 | Does Split survive with measured compute? | G-UB2 (same as UB1 with measured server) | STOP iff max Δ_bound < 3.0 | **+0.5 [−4.75, +5.25]**; 0/20 pass; Bonferroni lo −7.13 | **STOP: SPLIT removed** | The surviving Split hypothesis is falsified for this design | Not all split inference; not optimised runtimes; not physical small devices | **Stage 3 not run**; write up |

---

## 2. Claim audit

Locations: **OV** = Overleaf baseline `paper/overleaf/main.tex` at commit `e1202db` (line numbers); **ORIG** = `source/main-original.tex` (= `TLM Paper/IEEE_Cloud_SLM_Router.pdf`); **SEP** = `paper/main-revised.tex` (Sept-23 draft); **LRB** = `~/research/LLMRouterBench`; **CSR** = `~/dev/cloud_slm-router`.

### Contradicted
| Location | Claim | Why |
|---|---|---|
| ORIG l.40, l.67 (abstract, intro) | "Extensive experiments demonstrate … significantly reduces inference cost and latency" | No such experiment exists. Must never reappear. |
| OV l.118 (§IV-C) | "split execution may become useful or selectable when direct remote execution is disallowed by the data policy" | For the tested design, exactly this regime (no-raw-text, 12/16 GB) fails G-UB2 (max +0.5 vs 3.0). |
| SEP l.476–478 (H3) | "the split action matters" | Same; Split removed. |
| CSR `deployment-pivot/GO-NOGO-REPORT.md` l.32ff; `E0-SPLIT-VIABILITY.md` | SPLIT may open a quality tier at 12 GB / 30–60 s no-raw-text | Tested and falsified at G-UB2 (best cell is exactly 12 GB / 60 s: +0.5). |
| Weekly brief 2026-11-05 §5 | "Edge / Split / Remote work remains paused" | Obsolete: S1 and E0 ran 11-08 to 11-10. |

### Too strong
| Location | Claim | Correction |
|---|---|---|
| OV l.157, l.194 (Table I/II) | "Oracle utility; oracle cost — upper bounds"; "Oracle utility (upper bound)" | A single-draw hindsight oracle bounds *realised accuracy on those draws* only. Part of its gain is sampling noise (only 26.7% of winners stable), so it is not achievable headroom. Report it as a hindsight reference. |
| OV l.226 (§VI-A) | "oracle gain … bounds what any router can achieve" | Same. |
| SEP l.569 | oracle "‡Upper bound" | Same. |
| LRB `diagnostics/pair_learnability.md` l.26, l.78 | "The ceiling on usefulness is tiny … perfect oracle adds 8.5 pts" | "Ceiling" → "hindsight reference on single-draw labels". |
| LRB memory/notes; `pair_learnability.md` verdict | "signal is dataset-conditional, **not per-query**" | Mostly dataset-conditional; per-query signal exists on BBH/KorBench/MBPP and is partly hidden by label noise (A3/A4). |
| CSR `deployment-pivot/PROBLEM-FORMULATION.md` l.8; `decision/GO-PIVOT-REPORT.md` | "the semantic layer **is** a task lookup" | "Is mostly / is well approximated by" a task lookup. |
| CSR `GO-NOGO-REPORT.md` l.8–11, l.57; `PROBLEM-FORMULATION.md` l.19, l.68 | "Link RTT never changes an EDGE/REMOTE decision" | True only in a simulation with assumed throughputs. Must be labelled as simulation. |
| OV l.40 (abstract) | "the right choice depends both on what the query needs and on the current network and server conditions" | Query need is mostly task-level (A2); RTT effect not supported (simulation). |
| ORIG l.48 | HIPAA claim via a company blog | Unsupported source; already flagged in SEP l.101. Dropped. |
| LRB `official_router_f1_analysis.md` | "~0.60 is the TOP of the ladder, not poor" | True as a ladder statement, but frame as "a baseline that no tested design materially exceeds" (Film's point). |

### Weakened
| Location | Claim | Why |
|---|---|---|
| OV l.40, l.52, l.57, l.100–107 | Core contribution: compact encoder predicting calibrated per-model utility | Compact routers ≈ benchmark recognition on this pair; calibration was never evaluated. |
| Brief / prompt | "Capability+MiniLM 0.6082" as a headline | Secondary-threshold number; primary 0.5968. |
| Brief §4 | Target-only "passes this criterion" | Correct as a *practical* pre-declared criterion; not statistical. |

### Obsolete
| Location | Item |
|---|---|
| ORIG title | "Tiny-LM with Jacobi-Forced Micro-Encoder" (not revived) |
| OV l.52, l.58, l.120–122, Fig. 1 caption l.94 | "E0 = split-equivalence test" with uniform/query-dependent correction branches. The executed E0 is split *viability*; equivalence was checked only bitwise on CPU. |
| OV l.57 (contrib. 1), l.109–125 (§IV-C/E) | Runtime optimiser over Edge/Split/Remote as the contribution |
| OV l.131–135 | Testbed "pending confirmation"; SimpleQA as initial benchmark |
| OV l.137–160 | Baseline table (RouteLLM, RouteLMT, ICL-Router, Arch-Router, Bao/NetGPT rules) — none was run |
| OV l.165–173 | Experiment plan 1–4 |
| OV l.175–232 | All placeholder results tables/figure and analysis stubs |

### Supported (keep)
| Location | Claim |
|---|---|
| OV l.48, l.236 | Split activations are not privacy-guaranteed; "raw-query-constrained regime is a data-policy condition, not a privacy guarantee" |
| OV l.62, l.73 | No priority claim; components have precedents |
| OV l.118 (first half) | Under a latency-only cost with a faster server, Split is rarely selected (consistent with measured compute) |
| SEP §VI (Stage 0) | TF-IDF did not transfer across datasets (different pairs; optional) |

### Still untested
- Whether a router *trained* on repeated utility gains within-benchmark discrimination.
- Whether the target-only gain survives a paired bootstrap.
- Router calibration (ECE/Brier) and on-device router latency (only CPU timing exists).
- Whether an optimised split runtime (CUDA graphs, fused kernels) closes the UB1–UB2 gap.
- Physical 12/16 GB devices (emulated by capping).
- Any real-network latency for EDGE/REMOTE/SPLIT (Stage 3 not run).
- The leakage constraint in SEP l.139–145 (never measured).

### Specific checks requested
| Check | Where it appears | Verdict |
|---|---|---|
| Assumes Split is useful | OV l.52, l.57–58, l.118; SEP H3; GO-NOGO | Removed / rewritten |
| EDGE/SPLIT/REMOTE as a successful optimiser | OV abstract, contrib. 1, §IV | Never had results; removed |
| Pair Oracle as deployable / mathematical ceiling | OV l.157, l.194, l.226; SEP l.569; LRB pair_learnability l.26, l.78 | Replaced with "hindsight reference" (new §III paragraph) |
| Strong individual-query prediction | OV contrib. 1 and abstract | Removed; within-benchmark AUC 0.501 reported |
| Benchmark identity confused with deployable signal | — | New manuscript calls the benchmark-identity reference "diagnostic only, not a baseline" (§V-C, Table II footer) |
| Unstable labels = no preference | none found in the manuscript; risk in "not per-query" notes | Explicitly countered in §V-D |
| UB1 CONTINUE as latency evidence | none found; gate text itself disclaims | Manuscript §VI-D: "not evidence that Split meets any deadline" |
| UB2 STOP as "all split inference impossible" | none found | Manuscript §VII (ii) scopes the falsification |

---

## 3. Paper thesis options (ranked)

### Option 1 (rank 1): Premise-testing empirical paper (routing diagnostics + pre-registered Split falsification)
- **Thesis:** For edge LLM serving on these workloads, a lightweight router's measurable advantage is mostly benchmark recognition with noisy per-query labels, and splitting a 32B model across edge and server does not open a quality tier over a 4-bit edge model once measured server compute is used.
- **Primary contribution:** Two pre-declared, sequential tests of the two premises of the model-utility Edge/Split/Remote design, both reported, including the negative outcome.
- **Evidence available:** All of ledger rows 1–10; the gates recompute from archives.
- **Evidence missing:** The bootstrap CI for the target-only gain; artifact archiving of E0 in the repo; model citations.
- **Main reviewer objection:** "Two loosely connected studies on different models; and the Split result reflects your eager HF runtime." Answers: (a) the studies are tied by the design under test and never combined numerically; (b) the runtime threat was pre-stated, the falsification is scoped to this design, and UB1 is reported to show the size of the runtime gap.
- **Strength:** Moderate. Defensible and honest; novelty is empirical and methodological rather than algorithmic. Suits an IEEE edge/cloud or systems venue, or a workshop / negative-results track.

### Option 2 (rank 2): Routing-diagnostics paper only
- **Thesis:** On a hard model pair, lightweight router performance is explained largely by benchmark identity, and one-shot binary winner labels hide part of the per-query preference.
- **Primary contribution:** Within-benchmark evaluation plus a repeated-generation label audit.
- **Evidence available:** Rows 1–5 and 3b.
- **Evidence missing:** Bootstrap; a second model pair; ideally training on repeated utility. Without these it is a thin paper.
- **Main reviewer objection:** "Label noise and evaluation artifacts in routing are known" (cf. the May-2026 "unsolvability ceiling / evaluation artifacts" preprint noted in `CSR decision/LIT-REVIEW.md` l.23: a novelty threat to check), and "one pair, 120 queries".
- **Strength:** Moderate as a scientific claim, but weak for Film's edge/networking direction, and it discards the E0 work.

### Option 3 (rank 3): Deployment falsification paper only
- **Thesis:** A symmetric layer split of Qwen3-32B does not beat vLLM-served 4-bit edge models on emulated 12–24 GB edges under deadline utility.
- **Primary contribution:** A pre-registered staged split-viability protocol and its STOP.
- **Evidence available:** Rows 6–10.
- **Evidence missing:** Any real-network latency; an optimised runtime; physical devices.
- **Main reviewer objection:** "Your split runtime is eager HF (≈66 ms/step) against vLLM competitors; optimise it." This is pre-stated threat §11.1, and the result cannot answer it.
- **Strength:** Weakest. A systems venue will dismiss it as implementation-bound.

## 4. Recommended framing

**Option 1, written primarily as an empirical limits/diagnostic paper, with the Split falsification as a second, shorter empirical study.** It is not a lightweight-routing *method* paper, because no method beat a task-level policy. It is not a deployment *measurement* paper, because no end-to-end latency was measured. Option 1 is the only framing that uses all the verified evidence, keeps the negative results, and matches Film's actual decision trail (low F1 → CV → diagnose → labels → deployment headroom → staged Split test → STOP). It also makes a modest claim that the artifacts fully support. The deployment-optimiser results (RTT, joint vs B*) are simulations, so they appear only as context in the Discussion, behind a TODO. I recommend dropping them if Film prefers a tighter paper.

## 5. Titles, abstract, contributions

Candidate titles:
1. **What Can a Lightweight LLM Router Decide at the Edge? Routing Diagnostics and a Pre-Registered Test of Split Inference** (used in the draft)
2. Testing the Premises of Edge, Split, and Remote LLM Routing
3. Task Identity, Noisy Winner Labels, and Measured Split Compute: Limits of Lightweight Edge LLM Routing
4. Before Building an Edge–Split–Remote Router: Two Pre-Declared Tests and What They Found
5. Most Routing Signal Is Task Recognition, and Splitting a 32B Model Does Not Open an Edge Quality Tier

Abstract: see `main.tex` (≈260 words). Every number in it is in the §0 verification table.

Contributions (in the manuscript):
1. Within-benchmark analysis: 0.600 / 0.670 overall, within-benchmark macro AUC 0.501, benchmark-identity diagnostic 0.613 F1; three benchmarks with clear signal. [rows 1–3, 3b]
2. Repeated-generation label audit: 26.7% stable, 84.5% agreement on nonzero margins, within-benchmark AUC 0.573→0.640 with unchanged scores (descriptive). [rows 4–5]
3. Pre-registered staged Split test: F pass → UB1 +12.25 → measured H200 compute → UB2 +0.5 < 3.0 → STOP; gates recompute from archive. [rows 6–10]

## 6. Results restructure (as implemented in `main.tex`)

| § | Question | Experiment | Metric | Result | Interpretation | Limitation |
|---|---|---|---|---|---|---|
| IV, Table I | What was decided, in which order? | Ledger | Pre-declared criteria | 8 gates | Shows Film's feedback → diagnosis → deployment sequence | — |
| V-B | Is 0.60 a protocol artifact? | Stratified 5-fold CV + capacity + capability features | Macro-F1, AUC | 0.58–0.63 for all; max 0.626 | Capacity is not the bottleneck | One pair, binary labels |
| V-C | Per-query or per-benchmark? | Within-benchmark AUC; benchmark-identity diagnostic; E1 20-model pool | Within macro AUC; F1 | 0.501 vs 0.670 overall; 0.613 identity; E1 +0.42 [−0.18, 1.01] | Mostly task recognition; per-query signal on 3 benchmarks | Identity reference is not deployable; E1 is a different protocol |
| V-D | Are labels stable? | 120 × 5 repeats × 2 models | Stable ≥ 4/5; repeated margin | 26.7%; 7.2% reversals; 84.5% agreement | Labels are noisy draws of real preferences | Reconstructed serving; 120 q; chosen benchmarks |
| V-E | Do scores fit repeated preference better? | Target-only re-scoring | Within F1/AUC | +0.040 / +0.068; 5/6 | One-shot labels hid some signal | n = 103; no test yet; no retraining |
| VI-B | Quality headroom? | S1 | Gap 32B vs edge-best | up to +27.5 (12 GB) | CONTINUE | Not Split evidence |
| VI-C | Memory fit? | Stage 1 | U-max, competitor fit | (3,3)/(5,5)/(9,9); 24 GB blocked | Feasible | Emulated classes |
| VI-D | Optimistic bound? | G-UB1 | max Δ_bound | +12.25 | Not excluded | Not latency evidence |
| VI-E | Measured server? | Stage 2 + G-UB2 | max Δ_bound | +0.5 vs 3.0; 0/20 | STOP, Split removed | Eager HF runtime; no network measured |

The semantic diagnostics form Section V, and the E0 falsification forms Section VI. The Discussion scopes both.

## 7. Figures and tables (minimal set; all in `main.tex`)

1. **Table I – decision ledger** (doubles as the Split funnel S1 → Stage 1 → UB1 → Stage 2 → UB2).
2. **Table II – CV ladder** with the benchmark-identity diagnostic row.
3. **Fig. 1 – within-benchmark AUC per benchmark** with CIs, chance line and overall-AUC line (aggregate vs within-task in one picture). pgfplots; data from `benchmark_auc.csv`.
4. **Table III – label stability** (stable rates, win/tie/reversal split).
5. **Table IV – one-shot vs repeated target**, per benchmark plus macro.
6. **Table V – S1 gaps** (could be cut to save space; the ledger already carries the gate result).
7. **Fig. 2 – bounded Δ vs deadline**, UB1 vs UB2 at 12/16 GB, red +3.0 line, UB2 CIs. Shows +0.5 vs +3.0 directly.

The Oct-8 architecture figure was removed (the method was never built). If Film wants a figure for the design under test, reuse it annotated "P1 → Study A, P2 → Study B". That is optional.

## 8. Minimum remaining work before Wednesday night

### A. Must do
**A1. Paired benchmark-stratified bootstrap of the target-only gain.**
- Question: is the within-benchmark AUC gain (+0.068) robust to which queries were sampled?
- Data: `LRB diagnostics/winner_label_stability/target_only_eval_rows.csv` (103 rows: benchmark, held-out score, both targets).
- Runtime: < 1 min. CPU. Safe unattended.
- Procedure (fix before running): 10,000 resamples, seed fixed. Resample queries with replacement within each benchmark. In each replicate, compute per-benchmark AUC for both targets on the same resample. If either target is single-class for a benchmark in that replicate, drop that benchmark from both macro means. Δ = macro(repeated) − macro(one-shot). Repeat for macro Macro-F1.
- Decision criterion: if the 95% CI lower bound of Δ within-benchmark macro AUC is > 0, the paper says "the CI excludes zero (post hoc, n = 103)". Otherwise the paper keeps the current "descriptive" wording and adds the CI. Either way it never claims a trained-router improvement.
- Effect on paper: changes one sentence in §V-E and resolves the red TODO.

**A2. Archive E0 Stage 1 (valid) and Stage 2 in the experiment repo.**
- Why: the paper cites archived artifacts, but the gates, profiles and env files exist only in untracked tarballs (`e0_stage{1,2}_*.tgz`), and the `.sha256` files point at `/workspace/...` paths.
- Work: copy the gate JSONs, `f_results.json`, `umax_*.json`, the P-edge/P-server profiles, `selftest_*.json`, env and logs into `diagnostics/deployment_e0/results/` with a `RESULT.md`, and commit locally on `deployment-e0-split-prep`. Record the CPU recompute (identical, 2026-11-10). Leave pushing to you.
- CPU, ~30 min, attended (choose what to commit; the npz reference arrays are large).
- Effect: makes every Study-B number traceable.

**A3. Compile on Overleaf and resolve citation TODOs.**
- Compile (pgfplots; not compile-tested locally).
- Add citations for DeepSeek-R1-0528-Qwen3-8B, Qwen3, all-MiniLM-L6-v2 and GTE-Qwen2-7B from their official model cards or papers only.
- Fix the template boilerplate (the `\thanks` lines about the "IEEE Publication Technology Group", the 2021 `\markboth` journal line, `\IEEEpubid`). These are unchanged from the Oct-8 draft.

**A4. Decide the simulation paragraph** (Discussion, "Implications"). Either keep it, citing `deployment-pivot/evidence/joint_vs_sequential_sim.md` and `baseline_crossfit_check.md` with the assumed profiles stated, or delete it. Recommendation: delete if space is tight.

### B. Valuable if cheap
- **B1.** Add the hindsight-oracle numbers once, with the noise caveat (E1: oracle 0.904 vs lookup 0.707). CPU, existing file, 5 min.
- **B2.** Read the existing `vllm_Qwen3-32B-AWQ_c24_a0.log` and state the 24 GB engine-failure reason in one footnote. CPU, 5 min.
- **B3.** Report per-fold (not pooled) within-benchmark AUC as a sensitivity row (`B_auc_mean_of_folds` already exists in `benchmark_auc.csv`). No compute.

### C. Defer (after this review)
- Training a router on repeated-utility targets. This needs repeated generations at training scale (GPU) and a pre-registration.
- A second model pair for Study A.
- Any optimised split runtime or physical small-device study. That is a new hypothesis and needs a new pre-registration.

### D. Do not do
- Stage 3, G-link, or any joint H200 + edge networking run.
- Re-running S1 or E0, or using the §8.5 extension (not triggered: Δ = 0.5 < 3.0).
- New embeddings, classifiers or hyperparameter sweeps.
- Jacobi / Tiny-LM.
- System-cost integration or the Edge/Split/Remote optimiser.
- Relabelling past experiments.

## 9. Overleaf patch plan (Oct-8 → 11-10), as applied in `main.tex`

| Section (Oct-8 lines) | Action | Detail |
|---|---|---|
| Title (l.26) | **Rewrite** | Candidate 1 |
| Abstract (l.39–41) | **Rewrite** | Results now exist; "No experimental results" removed |
| Keywords (l.44) | **Rewrite** | + split inference, label noise, pre-registration, negative results |
| I. Intro ¶1 (l.48) | **Keep**, light edit | Cites SplitLLM; the latency/privacy detail moves to §III |
| I. Intro ¶2 (l.50) | **Delete** | "A router must do all three at once": superseded motivation |
| I. "Proposed idea" (l.52) | **Rewrite** | Becomes "design under test, premises P1/P2", plus a summary of findings |
| I. Contributions (l.54–62) | **Replace** | 3 evidence-traceable contributions; a note that the studies are never combined |
| II. Related: routing, network (l.67–69) | **Keep**, trim | + LLMRouterBench finding; + PRISM |
| II. Split computing (l.71) | **Rewrite** | + In-Browser split, Mix-or-Split, Cunningham inversion |
| II. Positioning (l.73) | **Delete** | Combination claim no longer the paper |
| III. Problem formulation (l.75–86) | **Rewrite** | "Design under test and its premises": one equation (route); P1, P2 definitions; **move** "admissibility ≠ privacy" here from l.236; **add** "oracle = hindsight reference" |
| IV. Proposed Method + Fig. 1 (l.88–125) | **Delete** | Never built. The useful content (model vs action, same weights) is compressed into §III. The two-systems-facts paragraph (l.118) is superseded by measurement. |
| V. Experimental Setup (l.127–173) | **Delete** | Replaced by study-specific setup subsections in §V-A and §VI-A |
| VI. Results placeholders (l.175–232) | **Delete** | Replaced by new §IV (ledger), §V (Study A), §VI (Study B) |
| — | **Add** | §IV Study design + Table I; §V A-B…E with Tables II–IV, Fig. 1; §VI A–E with Table V, Fig. 2; §VII Discussion (supports / implications / does not show / limitations) |
| VII. Conclusion (l.234–236) | **Rewrite** | States only what the evidence supports; one open question |
| Bibliography | **Edit** | Removed 5 now-uncited items (guo2017calibration, yuan2025nondeterminism, he2025nondeterminism, schuster2022calm, sqa). Added 5 from the verified `references/library.bib` (mudvari2024splitllm, zhan2025prism, lee2026browser, wang2026mix, cunningham2026privacy). No new unverified citations; missing model citations are red TODOs. |

Diff summary: `git diff --stat` → `paper/overleaf/main.tex | ~450 lines changed`. Static checks: all `\cite` keys resolve, all `\ref`s have labels, braces and environments balance. Not compile-tested (no TeX on this host).

## 10. LINE update for Film (draft)

> Film, quick update before you open Overleaf tonight.
>
> 1. After your comment that ~0.60 Macro-F1 was only a baseline, I redid the evaluation with stratified 5-fold CV. It stayed at ~0.60, so instead of adding model complexity I looked at why.
> 2. Within a single benchmark the router is near chance (AUC ~0.50 vs 0.67 overall). Most of the signal is recognising the benchmark, with real per-query signal only on BBH, KorBench and MBPP.
> 3. Re-running 120 queries 5× per model showed the one-shot winner labels are often unstable (27% stable). The same router scores fit the repeated preference better (within-benchmark AUC 0.57→0.64). So the labels were hiding some real signal, but routing is still hard.
> 4. On deployment: the quality gap between Qwen3-32B and edge-sized models was large enough (S1) to justify testing Split. Split fit in 12–24 GB edge memory and passed the optimistic bound (UB1).
> 5. With measured H200 server compute, the pre-registered UB2 gate stopped it: best case +0.5 pt vs the required +3.0, even ignoring the network. So Split is removed and Stage 3 is correctly not run.
> 6. Paper direction: an evidence-based paper on what a lightweight router can decide at the edge. It reports the routing diagnostics and the Split falsification honestly, instead of the original Edge/Split/Remote optimiser. The revised draft is in Overleaf; red TODOs are the remaining checks.

## 11. Exactly one next research question

**If a router is trained on repeated-sample utility (each model's expected success rate over several runs) instead of one-shot winner labels, does it gain within-benchmark discrimination beyond benchmark identity?**

This follows directly from rows 3–5: aggregate signal is mostly benchmark identity, the training labels are noisy single draws, and unchanged scores already align better with the repeated target. It is the cheapest test that could change P1's verdict. It is also a learning question, not another encoder or classifier. It needs repeated generations at training scale (GPU) and its own pre-registration, so it is future work, not a pre-Wednesday task.
