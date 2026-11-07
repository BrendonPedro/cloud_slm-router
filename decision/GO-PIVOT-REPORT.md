# GO / PIVOT decision on the semantic-routing contribution (2026-11-07)

## Recommendation: **PIVOT**

Make **deployment optimisation** of edge-SLM / split-LLM / cloud collaborative
inference the main contribution. Demote semantic routing to a **cheap
task-recognition component** that feeds a **cost-aware routing table**. Reject the
factored prior+residual router, and direct winner/utility prediction, as headline
contributions.

The decision rests on three pre-registered cached-data experiments (E1, E2, E3), an
independent pair-level test run by another session, and a fresh literature review
(`LIT-REVIEW.md`). Every number below is ours, from cached LLMRouterBench labels
(20 open 7–9B models, 11,467 queries, 15 benchmarks, 5 frozen folds). No new model
inference was run.

## 1. The evidence

| # | Question | Result | Source |
|---|---|---|---|
| E1 | Accuracy-only: does query-level routing beat a predicted-task lookup? | **NO HEADROOM.** The best query-level router (R4 factored) adds +0.42 pt [−0.18, +1.01] and closes 2% of the lookup→oracle gap. The lookup itself is +3.33 pt over the best single model. The pair restriction is also NO HEADROOM (+0.16). | `E1-pool-headroom/RESULTS.md` |
| Pair §9 | Factored task-centred residual on the DS/Qwen pair (other session, own prereg) | **FAIL.** Within-benchmark macro-F1 changes by −0.6 pt, positive in only 1/5 folds. | `~/research/LLMRouterBench/diagnostics/gte_task_centered_residual_3class_run.log` |
| E2 | Cost-aware (correctness − λ·k-tokens): is there per-query signal a task table misses? | **MARGINAL** (does not support GO). R\* = kNN passes at only 2/11 band λ. Post hoc, R4 gains +1.3 to +2.2 pt (≈20–25% fewer tokens at matched accuracy) for λ ∈ [0.01, 0.05], but it beats a train-only cluster table (R6) only at λ = 0.02–0.03 (+0.7/+0.9 pt) and **reverses** for λ ≥ 0.15. Of its +1.98 pt at λ = 0.03, korbench (+1.30) and livecodebench (+0.76) account for all of it, and the other 13 benchmarks net −0.08. Both of those benchmarks have known sub-categories. This is **finer task taxonomy, not per-query semantics.** Every router closes ≤ 7.4% of the oracle gap. | `E2-cost-aware/RESULTS.md` |
| E3 | Does the routing component need a 7B embedder? | **SUFFICIENT.** TF-IDF + LinearSVC reaches 99.58% task accuracy (GTE-7B: 99.67%), with lookup utility within 0.14 pt of GTE at every λ, at about 5 ms per query on a CPU. | `E3-cheap-recognizer/RESULTS.md` |
| Earlier Stage 0 | Edge-vs-cloud deferral (Qwen3-8B vs 235B), TF-IDF router | Never better than random in 8 leave-one-dataset-out folds. | `paper/main-revised.tex` §Stage 0 |

**Reading.** On the only cached data with correctness and cost for a
heterogeneous open pool, the recoverable routing value is (i) *recognising the
task* (+3.3 pt accuracy; +11 pt at a 1k-token budget over the best single model)
and (ii) a *cost-aware table* over tasks or sub-tasks. A CPU lexical classifier
delivers both. The per-query semantic residual is not distinguishable from the
table on accuracy. On cost it adds ≤ 1 pt over a sub-task table in a narrow λ window
and becomes harmful outside it.

## 2. The literature agrees, and has already published the headline

- *"Most of the LLM Routing Gap Is Task Type"* (Lee, arXiv 2608.23023, Aug 2026)
  makes our E1 claim directly, at small scale (294 questions, no holdout).
  **LLMRouterBench** (Findings ACL 2026) finds that routers tie, often fail to beat
  Best Single, and that embeddings barely matter. **kNN beats learned routers**
  (2505.12601). A negative "routing ≈ task lookup" result is therefore a
  *confirmation*, not a novel headline. Ours is larger, held-out, pre-registered and
  cost-aware, which makes it a strong *motivation/analysis section*.
- The semantic-routing formulations that still show gains are **taken**:
  cost-aware cluster tables (Avengers-Pro 2508.12631; UniRoute, ICLR 2026), and
  joint model + length-budget routing (R2-Router, ICML 2026). Single-draw labels
  inflate the oracle gap (Chen 2607.03436: 12–36% is noise), which further shrinks
  what any router can claim.
- Serving work shows that **deployment decides outcomes at fixed routing quality**.
  RouterWise (2604.10907) optimises allocation and routing jointly under a latency
  SLO, with quality varying by up to 87% across setups on one cluster. BOute
  (2602.10729) shows that routing and placement are interdependent. None of these
  covers the **edge SLM ↔ layer-split LLM ↔ cloud** setting with activation-transfer
  cost, which remains the paper's unresolved gap U1 (`advisor/one-page-brief.md` §4).

## 3. Formulations compared and why each was rejected as the main contribution

| Formulation | Tested? | Verdict | Why rejected (or kept) |
|---|---|---|---|
| **Direct winner / per-model utility regression** (R3; RouteLLM- and MLP-style) | E1, E2 | **Reject** | Worst learned router: −0.60 pt vs lookup on accuracy, negative at 10/13 λ. It mislearns the task prior on large benchmarks. |
| **Factored prior + residual** (R4; the current proposal) | E1, E2, pair §9 | **Reject as headline; keep as ablation** | Best query-level router, but E1 NO HEADROOM, pair FAIL, E2 MARGINAL. Its gain is concentrated in two sub-structured benchmarks, and the token residual collapses at high λ. |
| **kNN / non-parametric** (R5) | E1, E2 | Reject | Ties the lookup on accuracy (0.00). It is E2's R\* but MARGINAL. It is also a published baseline (2505.12601), so it is not novel. |
| **Sub-task / cluster table** (R6; Avengers-Pro and UniRoute style) | E2 | **Keep as a component**, not as a contribution | Captures most of the cost-aware gain, robust at every λ. It is prior art, so it gives weak novelty. |
| **IRT / matrix factorisation / contrastive model embeddings** (IRT-Router, EmbedLLM, RouterDC) | Not run | Reject on evidence | These are low-rank factorisations of the same query×model matrix. When the task factor is removed, E1/E2 show that the query-level remainder is ≈ table-level. LLMRouterBench finds them tied with simple baselines. |
| **Length-budget routing** (R2-Router) | Not testable | Reject for us | Already published at ICML 2026. Our cache has no length-budget variants. |
| **Post-generation cascades / self-verification** | Not testable on one-shot cache | **Candidate *system* component** | Uses post-generation signals that pre-generation semantics lacks. It belongs in the deployment system (edge-first, then escalate) and is evaluated there, not as a semantic-routing claim. |
| **Think / no-think self-routing** | Not testable | Reject for this paper | The decision moves inside the model (2608.20256). That is a different paper. |
| **Micro-encoder / KD router** (methods-v2/v3) | E3 (indirectly) | **Revive narrowly** | It is not needed for winner prediction, because there is no headroom. It is justified only as a compact *task/sub-task recognizer* if lexical features fail on non-benchmark traffic, which is not yet tested. |
| **Jacobi-Forced micro-encoder** | n/a | Reject for the router | Jacobi decoding is meaningless for a classifier head (`research/jacobi-forcing.md`). At most it is a separate decoding paper for the edge generator. |

## 4. Exactly what to build next

**Paper thesis (proposed):** *For edge-SLM / split-LLM / cloud collaborative
inference, the routing policy can be a cost-aware task table driven by a
CPU-cheap recognizer. The achievable gains come from jointly choosing that table
together with model placement, split depth and resource allocation under measured
latency, energy and link constraints.*

1. **Routing component (done on cached data; package it).** The recognizer is a
   lexical TF-IDF + linear model. The table is a cost-aware λ-indexed task table
   (R2), with the sub-task table (R6) as a variant. The ablations are R4/R5
   query-level routers, which bound the most per-query semantics can add (E2: ≤ ~1
   pt over R6, λ-dependent). Report the E1/E2/E3 numbers as the at-scale,
   pre-registered motivation section, positioned against Lee 2608.23023.
2. **Deployment optimiser (the new contribution).** The decision variables are
   which models are resident on the edge device / split host / cloud, the split
   depth per split model, the batch/memory allocation, and the routing table entries
   (task → path, model). The objective is table utility under a p95 latency SLO,
   an edge memory/energy budget and link bandwidth. Cost comes from **measured**
   profiles: tokens → latency via measured throughput on the target hardware, plus
   activation-transfer cost for split paths. Tokens come from the cached
   per-(task, model) token tables. Baselines: (a) deployment-oblivious routing
   (best routing table with fixed placement, as in RouterWise's isolated baseline);
   (b) placement-only (best placement with Best Single); (c) RouterWise-style joint
   datacenter allocation without a split path; and (d) **ours**, joint and
   split-aware.
3. **Pre-registered falsifier for the pivot itself.** If (d) does not beat the
   better of (a) and (b) by a margin fixed before measurement (suggested: ≥ 10%
   SLO-attainment or ≥ 15% energy at equal utility) on the target hardware, the
   systems contribution also fails. The fallback is then an *analysis paper* (E1–E3
   at scale plus a multi-sample oracle).
4. **Minimum hardware.** One edge device (e.g. a Jetson-class board or laptop GPU)
   plus one server GPU, with 3–5 models from the pool profiled. The cached data
   supply quality and token tables. Only latency, energy and activation-transfer
   costs must be measured.

## 5. Open items that could change the recommendation

- **Out-of-benchmark traffic** (the main threat to PIVOT-as-designed, and the only
  route back to a semantic GO). LLMRouterBench queries carry format cues, which is
  why recognition is 99.6% accurate. On unlabeled or paraphrased traffic, the
  recognizer and table may degrade while query-level routers do not. Test this
  before writing the systems paper: hold out benchmarks, paraphrase prompts, or use
  real chat logs. If query-level routers then beat the table by ≥ 1 pt with CI > 0,
  re-open a GO on *robust task recognition*, which is where the micro-encoder/KD work
  would come back.
- **True sub-labels** for korbench and livecodebench, to confirm that R4's E2 gain
  equals a sub-category table. This is not available in the pool rows.
- **Multi-sample labels** (Chen protocol). This would shrink the oracle and could
  either shrink or sharpen the per-query residual.
- **Mix-or-Split (IEEE TPDS 2026)** is still unread and may close the split-aware
  gap U1. Read it before committing to the systems thesis.
- About half of the literature claims are tagged [snip] in `LIT-REVIEW.md`. Verify
  them against the PDFs before citing.
