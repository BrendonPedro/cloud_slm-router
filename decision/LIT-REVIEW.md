# Fresh literature review for the GO / PIVOT decision (2026-11-07)

Scope: will a **semantic-routing** contribution still be publishable in November 2026,
given E1 (NO HEADROOM: query-level routing ≈ predicted-task lookup on the
20-model LLMRouterBench pool)? Searches were run on 2026-11-07 (web search plus
arXiv abstract pages). Almost none of these papers are in `research/` or
`references/library.bib` yet (checked by grepping the arXiv ids), so this review is new
relative to the earlier sprint.

**How firmly each source is verified.** **[abs]** means the arXiv abstract page
was fetched and read in this iteration. **[snip]** means the claim comes only from
search-result snippets or secondary summaries and must be checked against the PDF
before it is cited in the paper. No full PDFs were read, and no numbers below were
reproduced by us except where they are explicitly marked as ours.

## 1. Router-benchmark critiques and simple baselines (most relevant)

| Paper | Claim relevant to us | Status |
|---|---|---|
| **LLMRouterBench** (Li et al., arXiv 2601.07206, Findings of ACL 2026) | Under unified evaluation, many routers perform about the same, and several recent ones (including OpenRouter) fail to reliably beat **Best Single** or to cut cost without losing accuracy. The gap to the oracle is "driven by model-recall failures". **The embedding model has little impact.** | [snip]; already in `research/closest-prior-art.md` |
| **"Most of the LLM Routing Gap Is Task Type"** (J. Lee, arXiv 2608.23023, Aug 2026, preprint) | 14 models × 294 questions × 7 task types × 3 languages, each run twice. A fixed per-task-type table recovers 21 of 29 routable questions, and language adds 2 more. Only 6 of 294 are left for a learned router, which is fewer than the 5.37% run-to-run flip rate. There is **no holdout**: the table is fit and scored on the same 294 questions. | [abs] |
| **kNN beats learned routers** (Y. Li, arXiv 2505.12601, preprint, rev. May 2026) | A tuned kNN matches or beats SOTA learned routers. "Performance is local in embedding space." | [abs] |
| **Unsolvability ceiling / evaluation artifacts** (Garg & Sagtani, arXiv 2605.07395, May 2026) | Headroom estimates are inflated by judge/exact-match mismatch, truncation and parse failures. Routers collapse to the majority class. They recommend cost-sensitive objectives. | [snip] |
| **How much of the routing gap is real?** (T.-R. Chen, arXiv 2607.03436, Jul 2026) | Using ≥10 samples per cell, 12–36% of the router-to-oracle gap is single-draw label noise and the rest is "recoverable specialist advantage". The paper proposes a multi-sample oracle protocol. | [snip], title confirmed |
| **RouterArena** (Lu et al., arXiv 2510.00202, ICLR 2026) | Multi-dimensional leaderboard (accuracy, cost, optimality, robustness, latency), 8.4k queries, 44 categories. Snapshots from third parties list Avengers-Pro (a cluster router) as the strongest on cost-performance. | [snip] |

**Implication.** Our E1 headline, that accuracy-only routing is benchmark
recognition plus a table, is **already in the literature**. Lee (2608.23023)
states it directly at small scale, and LLMRouterBench and the kNN paper support it
indirectly. On its own, E1 is a *confirmation* rather than a contribution. Its
real added value over Lee would be scale (11,467 held-out queries, 20 models, 5
pre-registered folds, paired CIs). That is a solid analysis section, but not a main
contribution for a methods paper. Chen (2607.03436) also implies that part of our
oracle gap (0.904 vs 0.711) is noise that no single-commit router can close, which
further shrinks the space a semantic router could claim.

## 2. Semantic-routing formulations (what a GO would have to beat)

| Family | Representative work | Relation to our formulations |
|---|---|---|
| Direct per-model score/utility regression | RouteLLM-style classifiers, MLP/BERT routers (LLMRouterBench baselines) | = our R3. In E1 it **loses** to the lookup on pool20 (−0.60 pt). |
| Non-parametric neighbourhood | kNN router (2505.12601) | = our R5. In E1 it **ties** the lookup (0.00 pt). |
| Cluster lookup with cost trade-off | **Avengers-Pro** (arXiv 2508.12631), **UniRoute** (ICLR 2026; per-cluster error vectors, which allow unseen LLMs) | = our R6 (E1b, inside E2). This is the closest prior art to anything that "sub-task table" would yield, which is why the E2 prereg treats R6 ≈ R* as a lean-PIVOT outcome. |
| Latent ability × difficulty | **IRT-Router** (MIRT/NIRT), EmbedLLM (matrix factorisation), RouterDC (dual contrastive) | Factorisations of the query × model matrix. RouterArena snapshots rank RouterDC low and MIRT-BERT high [snip]. Our factored prior+residual (R4) is a special case of a task-level effect plus a query-level effect. In E1 it is the best query-level router, but it is not separable from the lookup (+0.42 pt, CI includes 0). |
| Joint model + length-budget routing | **R2-Router** (Xue et al., arXiv 2602.02823, ICML 2026) | Treats output length as a *controllable* variable and routes to an (LLM, budget) pair, reporting SOTA at 4–5× lower cost. **This is the strongest live semantic-routing formulation and it is already taken.** A cost-aware query-level router would have to beat it, and our cached data have no length-budget variants, so we cannot test that axis. |
| Self-routing on thinking mode | "Learning When to Think" (arXiv 2608.20256): a 1.5B model trained with GRPO picks NoThink/Short/Long. Qwen3 hybrid thinking budgets. | Moves the decision inside the model. Our pool has thinking and non-thinking 8B models but not paired modes of the same model, apart from the DS/Qwen derivatives. |
| Post-generation cascades | Confidence tokens (arXiv 2410.13284), AutoMix self-verification, conformal cascades (2607.25018), semantic-agreement cascades (2509.21837) | Use signals that come *after* a cheap generation, which a pre-generation semantic router cannot see. They are complementary to deployment work, but they need generation, so they cannot be tested on our cached one-shot labels. |

## 3. Cost/length prediction (the axis E2 tests)

- Predicting exact output length from the prompt is hard. Learning-to-rank on
  lengths (NeurIPS 2024) and distributional length predictors exist for
  *scheduling*. ALPS reports that a ridge probe on **prefill activations of the
  serving model** reaches R² > 0.85 [snip]. That is an inside-the-model signal,
  not one available to an external embedding router.
- So if E2 finds the per-query *token* residual predictable from GTE, it would
  connect routing to the length-prediction literature. If E2 finds that tokens are
  predictable only at the benchmark level, that matches the literature's
  observation that prompt-only length prediction is weak.

## 4. Deployment, serving and placement (the PIVOT destination)

| Paper | Claim |
|---|---|
| **RouterWise** (Kasnavieh et al., arXiv 2604.10907, 2026) [abs] | Latency depends on allocated GPUs and on the load that routing *creates*, so it solves deployment setup and routing fractions jointly under a latency SLO. Achievable quality varies by up to 87% across setups on the same cluster. At matched routing quality, the latency win comes from deployment. |
| **BOute** (arXiv 2602.10729) [snip] | Quality-aware scheduling across heterogeneous GPUs. Routing and placement are interdependent, and optimising them separately is suboptimal. |
| **Unified deployment-aware evaluation of open reasoning LMs** (Manik & Wang, arXiv 2604.07035) [abs] | Seven open reasoning configurations, with latency, VRAM and Pareto operating points. Top configurations are statistically near-tied, so *deployment trade-offs decide*. An oracle **task-aware** selector gives the routing headroom. |
| Edge-continuum measurement (arXiv 2609.08307) [snip] | Jetson Orin vs near-edge server vs cloud. Routing should weigh quality, latency, size and energy together. |
| Survey (Moslem & Kelleher, arXiv 2603.04445) | Six paradigms (difficulty, preference, clustering, RL, uncertainty, cascading). Generalisation is the main open problem. |

**Implication.** The serving literature already treats the routing policy as one
coupled component. RouterWise in particular shows that at *fixed* routing quality,
deployment dominates latency outcomes. A task-level routing table (our R2) is
exactly the low-dimensional routing policy such joint optimisers consume. This is
the natural home for the edge-SLM / split-LLM framing of the original manuscript,
and to our knowledge no paper in this list does the joint optimisation for the
**edge SLM ↔ split-LLM** setting with a pre-registered "is query-level routing worth
it" ablation. That novelty claim is provisional and must be re-checked against
RouterWise/BOute related-work sections before it is written into the paper.

## 5. Bottom line from the literature (before E2)

1. "Routers ≈ task lookup" is **known** (Lee 2608.23023 directly; LLMRouterBench and
   kNN indirectly). Our E1 is a larger, held-out, pre-registered confirmation:
   useful evidence, but not a headline.
2. The live semantic-routing formulations that *do* report gains (R2-Router
   length budgets; Avengers-Pro/UniRoute cluster-cost tables) are **taken**. Beating
   them would need data we do not have (length-budget variants, multi-sample labels)
   or would yield only a cluster table, which has weak novelty.
3. The defensible open space is in **deployment**: joint routing-table +
   placement/allocation for heterogeneous edge/split hardware, where the router is a
   cheap task-recognition component. RouterWise and BOute are the closest prior art
   to differentiate from.
4. E2 is still decisive for one remaining question: is there *cost-side* per-query
   signal (tokens) that a task table misses? If yes, and R* ≫ R6, a cost-aware
   query-level router could be a GO, but it would have to be positioned against
   R2-Router.
