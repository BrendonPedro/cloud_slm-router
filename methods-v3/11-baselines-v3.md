# 11 — Baseline plan (v3)

*Deliverable 11 of `MICROENCODER_HARDENING_BRIEF.md` §27 (brief §17). Prepared
2026-10-04 (gnhf run `microencoder-hardeni-d272f9`, iteration 14). Inputs:
`01` (model-level utility, rule A1, content-blind-split hand-off), `03` (C\*,
S3-SD, privileged teacher), `04` (supervision conditions S1/S1-MS/S2/S2-J/S3/S4),
`05` (body reads of ten routers), `06` (systems prior art: Bao, NetGPT-routing,
Neurosurgeon/SPINN, EdgeRL), `07` (backbone ladder), `08` (utility `E[S]`,
dataset prior), `09` (rule C-1, oracle-cost / oracle-utility controls, E6
integrated challenger), `10` (N = 2 pool M0, actions `EDGE(M_E)`,
`SPLIT_d(M_S)`, `REMOTE(M_S)`, open/private regimes).*

This file rebuilds the baseline table after the deeper prior-art review. It
replaces `methods-v2/10-model-pool-and-baselines.md` §7–8, which is left
unchanged. Every baseline is listed with the question it answers, whether code
exists (checked on 2026-10-04, §2), whether exact reproduction is realistic,
whether we must reimplement it, its compute cost, and what a fair comparison
requires.

Tags (brief §29): statements about published routers carry the inspection
level recorded in `05`/`06`. The baseline design is `[PROPOSED]`. Anything
that depends on Henry, the advisor or a pilot is `[OPEN]`. **No baseline
result exists yet.** Nothing here reports or implies a number from our own
experiments.

---

## 0. Summary

1. **Compare utility estimators inside one decision rule.** Most published
   routers output a quality estimate or a binary escalate/keep decision. They
   do not output a choice among `EDGE`, `SPLIT_d` and `REMOTE` under live
   network state. Each baseline therefore plugs into the **same** C-1
   optimizer (`09`) through one of three adapters (§1.2). The comparison
   isolates "which `Û` is better" from "which cost model is better". The cost
   side gets its own baselines (§3.F) and oracles (§3.G).
2. **v2 mistakes corrected.**
   * TF-IDF+LR stays as the non-neural floor. v2 justified it by saying
     "LLMRouterBench found neural routers often tie this". That attribution is
     **withdrawn**: LLMRouterBench has no TF-IDF/LR baseline in its body (`05`
     §4). v2's "beat TF-IDF+LR by ≥ 5 points" success bar was invented and is
     also withdrawn. It is replaced by a paired-bootstrap CI against a
     pre-registered metric (§4).
   * v2's KD control (α = 1 at the KD student's hyperparameters) is replaced
     by **C\*** and **S3-SD** (`03` §9).
   * v2's "Always-Split(d)" per depth is kept. Under rule A1 (`01`) the
     content-blind **best split** is now part of the proposed method's own
     depth policy. The informative content-blind baseline is therefore
     "content-blind *model* choice + best realization" (B-CB, §3.A).
   * The manuscript's adapted baselines (`source/main-original.tex` §Baseline
     Routing Methods) need four corrections (§5).
3. **Code status (checked 2026-10-04, §2).** Public code exists for RouteLLM
   (Apache-2.0), BEST-Route (MIT), RouterDC, IRT-Router, ICL-Router and
   LLMRouterBench (no licence file detected on all four). Arch-Router weights
   are on the Hub under a custom licence. **No public code was found** for
   Hybrid LLM (the paper's repo is behind Microsoft enterprise SSO), HyDRA,
   RouteLMT, the prefill-activation router, ConsRoute, Bao et al. or
   NetGPT-routing. These must be reimplemented and labelled "-style".
4. **The conference core is 16 baselines and controls plus three oracles
   (§4).** Together they answer seven falsification questions. The other baselines are recommended,
   optional or dropped, each with a reason.

---

## 1. Principles

### 1.1 One question per baseline

A baseline earns a place only if winning or losing against it settles a
specific competing explanation for the method's result. Each row of §3 states
that question. Baselines that answer no question the paper asks are dropped
(§3.H), even if a reviewer might expect them.

### 1.2 How baselines enter the multi-action decision (adapters)

The action set for M0 is `{EDGE(M_E), SPLIT_d(M_S) for d ∈ D_valid,
REMOTE(M_S)}`. In the private regime REMOTE is masked (`10` P4). The proposed
rule is C-1 (`09` §0.3):

```
R(q, s) = argmax_{a ∈ 𝓕(q,s)} [ Û_θ(M(a) | q) − Δ̂(a, q) − λ · L̂(a | q, s) ]
```

Baselines are adapted in one of three ways `[PROPOSED]`:

| Adapter | Baseline output | How it routes | What the comparison isolates |
|---|---|---|---|
| **U (utility)** | per-model estimate `Û_b(M \| q)` ∈ [0, 1] (after per-model post-hoc calibration) | Substituted for `Û_θ` in C-1. Same `𝓕`, `L̂`, `Δ̂`, λ grid | **Utility estimator only.** Cost model and optimizer held fixed |
| **P (pairwise / binary)** | a scalar score `z_b(q)` for "escalate from `M_E` to `M_S`" (P(win), predicted gain, consistency) | Escalate iff `z_b(q) > τ`. If escalated, the realization of `M_S` (`SPLIT_d` or `REMOTE`) is chosen by the **same** inner `min_{a ∈ 𝒜(M_S)} L̂(a \| q, s)` step as A1 (`01` §1.4). τ is swept to trace a frontier | **Escalation decision** with the cost-optimal realization given to the baseline for free |
| **F (fixed / content-blind)** | none, or a constant | A fixed action, or the same choice for every query | Whether content-aware routing is needed at all |

Adapter P is defined only for **N = 2 models** (`M_E`, `M_S`). It extends to
N ≥ 3 only through pairwise cascades. That is a different method and is not
attempted (§3.D notes for each router).

**Why give P-baselines the cost-optimal realization?** Otherwise a binary
router loses to us just because it cannot pick a split depth. That would be a
strawman: depth choice under live state is pre-empted prior art
(Neurosurgeon, SPINN, Edgent; `06` §3). The fair question is whether
**our utility estimate** improves the escalation decision. `[PROPOSED]`

### 1.3 Fairness rules (apply to every learned baseline)

| ID | Rule | Reason |
|---|---|---|
| F1 | Same labelled data `D_L`, same train/validation/calibration/test splits, same per-dataset scorer `S_D` (`08` §4) | Same information |
| F2 | Same model pool and action set, same `L̂` and same λ/SLA grid (adapters U/P) | Same decision problem |
| F3 | **Equal HPO budget**: same number of trials and the same search algorithm as the proposed student (`03` §9). Published defaults are one trial inside that budget | Tuning advantage is a common hidden confound |
| F4 | **Per-model post-hoc calibration** (Platt or temperature) on the shared calibration split for every adapter-U baseline. Report ECE/Brier before and after | Per-model calibration changes decisions after `− λC` (`03` learnings), so an uncalibrated baseline would be handicapped |
| F5 | ≥ 5 seeds for every trained baseline that the paper compares head-to-head; the same seed set | Seed variance is the noise floor |
| F6 | **Router overhead is charged.** The router's own latency on the edge node is measured on the same hardware and added to `L̂` of every action it routes (it is spent before any action runs). Hidden-state routers are charged the SLM prefill, minus any part reused by EDGE (§3.E) | A 7 B router that wins on accuracy but costs seconds is not a win in this setting |
| F7 | **Names.** "X" only for the released code or checkpoint run as published. "X-style" for our reimplementation or adaptation. "X (transfer)" for a released checkpoint used without retraining on our labels | The manuscript must not attribute our adaptation's numbers to the original authors |
| F8 | Labels for pairwise baselines are **derived from the same per-model runs** (`08` §3.2): win = `S_{M_S} > S_{M_E}`; ties handled as stated per baseline (`04` §2 for RouteLLM) | No extra judge budget for any one method |

---

## 2. Code availability (checked 2026-10-04)

Repository metadata was retrieved from the GitHub REST API
(`api.github.com/repos/<owner>/<repo>`: licence SPDX field, `pushed_at`,
archived flag). Code links in papers were found by grepping the arXiv HTML of
the version read for `github.com` / `huggingface.co`. "No licence detected"
means GitHub's licence detector returned null. Before reusing code we must read
the repository for licence terms. Without a licence, default copyright
applies: running it for research comparison is common practice, but
redistributing modified code is not permitted. `[OPEN]` for the advisor.

| Router | Code / artifact | Licence (as detected) | Last push | Notes |
|---|---|---|---|---|
| RouteLLM | `lm-sys/RouteLLM` | Apache-2.0 | 2024-08-10 | Released causal-LLM router uses 1–5 GPT-4 scores, not the paper's win/tie/loss (`05` §1.1) |
| RouterDC | `shuhao02/RouterDC` | none detected | 2025-04-14 | Repo inspected in iteration 2 (`05` §1.2) |
| BEST-Route | `microsoft/best-route-llm` | MIT | 2026-07-02 | — |
| Hybrid LLM | `m365-core/hybrid_llm_routing` (as cited in `05` §1.6) | — | — | **Not publicly accessible**: the URL redirects to Microsoft enterprise SSO, and the API returns "Not Found". Reimplement from §2–3 of the paper |
| IRT-Router | `Mercidaiha/IRT-Router` | none detected | 2025-02-19 | — |
| ICL-Router | `lalalamdbf/ICL-Router` (link in the paper's abstract, arXiv 2510.09719 v3) | none detected | 2025-10-14 | Data on HF `lalalamdbf/ICL-Router` |
| Arch-Router | weights `katanemo/Arch-Router-1.5B` (HF); serving code in `katanemo/archgw`, which now redirects to `katanemo/plano` (Apache-2.0) | weights: HF licence field `other` | plano: 2026-09-28 | Generative policy router; no routing head (`05` §1.9) |
| LLMRouterBench | `ynulihao/LLMRouterBench` | none detected | 2026-04-06 | Contains reimplementations of several routers; inspected in iterations 2 and 10 (`05`, `08`) |
| HyDRA | — | — | — | Preprint; no repo (`05` §1.3). Only `tau2-bench` linked, as an evaluation dataset |
| RouteLMT | — | — | — | No code link in arXiv 2604.22520 v1 HTML |
| Prefill-activation router | — | — | — | No code link in arXiv 2603.20895 HTML |
| ConsRoute | — | — | — | No code link in arXiv 2603.21237 HTML |
| Bao et al. (ICCC-W'25) | — | — | — | No code link in arXiv 2508.11291 HTML |
| NetGPT-routing | — | — | — | No code link in arXiv 2511.22217 HTML |

Two routers the manuscript lists as baselines were not body-read in `05`. Their
methods were read in this iteration from the arXiv HTML, at section level, to
specify the baselines:

* **RouteLMT** (Luo et al., "RouteLMT: Learned Sample Routing for Hybrid LLM
  Translation Deployment", arXiv 2604.22520 v1; arXiv comment "Accepted to ACL
  2026 Industry Track"). Read: §3 Problem Formulation, §4 Method ("In-model
  gain router", "Supervision and training", "Inference-time routing policy"),
  §5.1–5.3, Limitations. **What it does** `[VERIFIED-BODY, §4]`: a regression
  head on the **small translator's last-prompt-token hidden state**, trained
  **jointly with the small model through LoRA** (rank 8, Table 5). Loss: MSE
  against the gain label, i.e. the quality difference between large and small
  model (XCOMET-XXL) (Eq. 8). Inference: route the top-`p` fraction by
  predicted gain under a budget, or apply a threshold calibrated on held-out
  traffic. Models: LMT-60-0.6B small, LMT-60-8B large (§5.1). Machine
  translation only.
* **ICL-Router** (Wang et al., arXiv 2510.09719 v3; arXiv comment "Accepted by
  AAAI 2026"). Read: §3.1–3.4, §4.2, §4.3, App. A.4–A.5. **What it does**
  `[VERIFIED-BODY, §3.3–3.4, §4.2]`: Qwen3-Embedding-8B query vectors, a
  two-layer MLP projector, and a **Qwen2.5-7B-Instruct router**. Each model is
  represented by an in-context capability profile built from its correct/incorrect
  record on 500 "challenging" queries (Eq. 4). Cross-entropy on per-model
  correctness (Eq. 5). The router picks the model with the highest predicted
  probability of a correct answer (Eq. 6). Adding a model means profiling it
  on the query set, with no router retraining `[AUTHOR-CLAIM]` (§3.4, §4.5).
  Pool: eight 7–9 B open models. Training on 8 × A800-80G (App. A.2 baseline
  setting). App. A.4 argues the 7 B router's overhead is acceptable because it
  generates few tokens `[AUTHOR-CLAIM]`. No latency number is given.

Both entries go to `17-verified-references-v3.md` with these locators.

---

## 3. Baseline catalogue

Columns: **Q** = question answered; **Code** = §2; **Exact repro?** = can we
reproduce the published method on its own setting (not needed, but it shows
whether our adaptation is likely to be faithful); **Reimpl.** = must we write
it ourselves; **Cost** = training and inference compute on top of the shared
label-generation runs (those are paid once for all methods, `08`/`10`); **Fair**
= extra fairness requirements beyond F1–F8; **N** = pool sizes where it is
defined; **Exp** = experiments (`13`). Tier: **Core** (must run for the
conference paper), **Rec.** (recommended), **Opt.** (optional),
**Drop** (not run, with reason).

### 3.A Fixed and content-blind policies (adapter F)

| ID | Baseline | Q | Code / reimpl. | Cost | Fair | N | Exp | Tier |
|---|---|---|---|---|---|---|---|---|
| B-AE | **Always-Edge** `EDGE(M_E)` | Is escalation ever worth it? Quality floor, latency floor for zero network use | trivial | none | — | any | E2, E5 | Core |
| B-AS | **Always-Strong**: `REMOTE(M_S)` (open regime); the best-latency `SPLIT_d(M_S)` (private regime) | Single-model quality ceiling and its latency | trivial | none | Realization chosen by the shared `L̂` per state | any | E2, E5, E6 | Core |
| B-ASd | **Always-Split(d)**, one per valid depth `d` | Cost profile of each depth with routing removed; required to plot depth effects | trivial | none | Measured in the same `(RTT, BW, load)` cells as the method | any | E7 | Core |
| B-CB | **Content-blind model choice + best realization.** For each λ (or SLA), choose the single model `M*` maximising `Ū(M) − λ·E_q[L̂]` on the training set, then the latency-optimal realization of `M*` under the live state `s` | Does *query content* matter, given that the cost side already adapts to the network? Replaces v2's "system-state-only scheduler", which did not say what quality it assumed | trivial | none | Uses `Ū(M)` from the training split only | any | E2, E5, E6 | **Core** (key falsifier of the semantic router) |
| B-RND | **Random at matched action rates**: draws actions with the same marginal frequencies the method produced at each λ | Does the router pick the *right* queries, or only the right *frequency*? | trivial | none | Rates matched per λ and per network cell | any | E2, E5 | Core |
| B-DP | **Dataset prior**: per-dataset best model at λ, given the true dataset ID (an oracle input not available at deployment, `08` §5.2) | How much of the gain is coarse domain structure? | trivial | none | Labelled as using privileged dataset identity | any; **identical to B-CB on a single-dataset run** (e.g. SimpleQA only) | E2, E8 | Core when ≥ 2 datasets; otherwise reported as equal to B-CB |
| B-LO | **Latency-only scheduler**: choose the feasible action with the lowest `L̂(a \| q, s)`, ignoring quality | The pure-systems policy: what do we lose by ignoring quality entirely? | trivial | none | — | any | E5, E6 | Rec. (≈ B-AE when the edge model is fastest; report the coincidence) |

Neurosurgeon/SPINN-style latency-optimal split choice (`06` §3, rows 171–172)
is **not** a separate baseline. It is the inner realization step that B-AS,
B-CB and the proposed method all share (§1.2). We cite it as the foundation of
the cost side, not as a competitor.

### 3.B Simple learned routers (adapter U)

| ID | Baseline | Q | Code / reimpl. | Cost | Fair | N | Exp | Tier |
|---|---|---|---|---|---|---|---|---|
| B-TFIDF | **TF-IDF (word 1–2-gram) + per-model logistic regression** (K independent LR heads, calibrated) | Is a neural encoder needed at all? Non-neural floor | scikit-learn; ours | CPU, seconds to minutes; sub-millisecond inference | F3 applies: C, n-gram range and min-df searched with the equal trial budget | any | E2 | **Core** |
| B-FRZ | **Frozen sentence embedding + per-model LR** (e.g. MiniLM-class encoder from `07`'s ladder) | Does *fine-tuning* the encoder matter, or do frozen embeddings suffice? (LLMRouterBench's setting tests only frozen embeddings, `05` §4) | ours | CPU/GPU minutes | Same calibration; encoder from `07` | any | E2 | Rec. |

### 3.C Our own ablations and controls (adapter U unless stated)

| ID | Condition | Q | Source | Cost | N | Exp | Tier |
|---|---|---|---|---|---|---|---|
| B-S1 | Micro-encoder student, hard labels (S1), default hyperparameters | Plain supervised reference | `04` §5 | one fine-tune per seed | any | E1 | Core |
| **B-C\*** | **Strongest non-KD control**: same architecture and data; label smoothing and prior smoothing in the search space; regularisation; equal HPO budget; post-hoc calibration; ≥ 5 seeds | Is any KD gain attributable to distillation rather than regularisation/smoothing? | `03` §9 | = KD student | any | **E1** | **Core** |
| B-SD | Self-distillation (S3-SD), same out-of-fold protocol | Teacher vs *larger* teacher | `03` §9 | 2× student | any | E1 | Core |
| B-T | **Teacher router** (T1, larger encoder) evaluated directly | Student–teacher gap in quality, calibration and latency | `03` §2.3 | teacher fine-tune | any | E1, E4 | Core |
| B-MS | Student on multi-sample empirical rates (S1-MS) | Do soft targets need a teacher at all? (Hybrid LLM's r_prob construction) | `04` §5, `05` §1.6 | k× label generation (`03` O-F3) | any | E1 | Rec. if S1-MS labels are affordable |
| B-TIE | Untied per-depth heads (v2's design, `01` A-TIE) | Does tying utility across depths lose anything when E0 passes? | `01` §9 | one fine-tune | needs ≥ 2 depths | E0 follow-up | Opt. |
| B-INT | **Integrated state-input router**: learns `(q, s) → a` (or `(q, s) → Û − λL`) from emulated network states, EdgeRL-style joint policy | Does the separated design lose anything inside the training range? Is its advantage out-of-range robustness and reuse only? (Issue C) | `09` §7, `06` (EdgeRL) | needs labelled outcomes across emulated `s` cells; costly | any | **E6** | **Core** (the honest Issue-C challenger) |

### 3.D Published query routers

| ID | Baseline | What it is (`05`) | Q | Code / exact repro? | Reimpl. / adaptation | Cost | Fair | N | Exp | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| B-RLLM | **RouteLLM-BERT-style** (adapter P) | BERT-base classifier predicting P(strong wins) over {win_s, tie, win_w} (Eq. 13), threshold α | Does a calibrated per-model utility beat the established pairwise strong-vs-weak formulation at N = 2? | Apache-2.0 code; exact repro of the paper's Arena+judge data is unnecessary and expensive | Retrain the BERT classifier on F8 pairwise labels from our runs; tie handling as in `04` §2 | one BERT-base fine-tune; ~110 M parameters at inference | Name the label variant (paper win/tie/loss vs released 1–5 score) | **2 only** | E2, E5 | **Core** |
| B-RLLM-MF | RouteLLM matrix-factorisation router | MF over text-embedding-3-small embeddings (Eq. 11–12) | Same question, different router family | code exists; depends on an OpenAI embedding API | Swap the API embedding for a local encoder, or drop | small | API use violates the edge setting unless swapped | 2 | E2 | Opt. |
| B-RDC | **RouterDC** (adapter U after calibration) | mDeBERTaV3-base + learnable model embeddings, softmax over models, dual contrastive loss | Is a **softmax over models** (mutually exclusive) worse than independent calibrated per-model utility (`01` §6)? | code, no licence detected; exact repro realistic (7 open 7–8 B models) | Retrain on our per-model scores (Eq. 1 uses mean correctness, which matches `E[S]`); the softmax output is not a per-model probability, so map it to `Û` with per-model Platt on the calibration split (F4) | ~86 M encoder; small heads | Report both raw-softmax argmax and calibrated-adapter routing | ≥ 2; most informative at N ≥ 3 | E2, E5 | **Core** at M1 (N ≥ 3); Rec. at M0 |
| B-HYB | **Hybrid-LLM-style** (adapter P) | DeBERTa-v3-large; r_det / r_prob / r_trans labels (Eq. 1–4) | Do sampled soft labels with a transformation threshold beat our target? | **code not publicly accessible** (§2) | Reimplement §2–3; r_prob needs k samples per (q, M) (overlaps S1-MS) | ~300 M encoder | Use BARTScore only if the dataset needs it; otherwise the `S_D` of `08` | 2 | E2 | Rec. (Core if S1-MS labels exist, because it then costs one fine-tune) |
| B-BEST | **BEST-Route architecture** | DeBERTa-v3-small with K×N sigmoid heads, one per (model, best-of-n) | — | MIT code | With n = 1 (our action set has no best-of-n), its architecture **reduces to K independent per-model sigmoid heads on DeBERTa-v3-small**, which is the DeBERTa rung of `07`'s backbone ladder under C\* training | — | — | any | E2 (via `07`) | **Covered by `07`'s ladder; no separate run.** Cite it as the action-level precedent for the lossy branch (`01`, `02`) |
| B-IRT | **IRT-Router** (adapter U) | bert-base embeds queries and textual model profiles; P̂ = σ(aᵀθ_M − b) | Does a profile-conditioned model representation match per-model heads on a fixed pool? | code, no licence detected | Retrain on our labels; write profiles for our models | ~110 M | Profiles written before seeing test results | ≥ 2; meaningful at N ≥ 3 | E2 | Opt. for conference; **Core for the journal** pool-expansion study (`15`) |
| B-ICL | **ICL-Router** (adapter U) | Qwen3-Embedding-8B + projector + Qwen2.5-7B-Instruct router conditioned on in-context capability profiles | Does a 7 B LLM router with model profiles beat a ~100 M micro-encoder enough to pay for its cost? | code + data, no licence detected; exact repro needs ~8 × 80 GB GPUs for training (§4.2, App. A.2) | Retrain projector/router on our labels with 500-query profiles of our models | very high: ~15 B parameters at inference; does not fit an edge budget beside the edge SLM | F6 is decisive: charge the measured router latency; report accuracy-only and cost-charged results separately | ≥ 2 | E2 | Opt. (**accuracy reference only**). It is in the manuscript, so see §5 |
| B-ARCH | **Arch-Router-1.5B** | Generative policy-ID router over user-written domain/action policies; no quality prediction | Generative-router reference; latency contrast | weights on HF (licence `other`) | Writing domain/action policies for SimpleQA-style factual QA does not map to "which model will answer correctly" | 1.5 B generative | Zero-shot only; the manuscript's "fine-tune its routing head" is impossible (§5) | any | E2 | Opt. / Drop (§3.H) |
| B-HYD | **HyDRA-style capability router** | ModernBERT-base, four capability-requirement sigmoid heads matched against static model profiles, cheapest eligible | Does capability-requirement matching beat learned per-model utility? | **no code**; needs judge-scored requirement labels (Eq. 7) and benchmark-derived profiles | Full reimplementation plus a new judge labelling pass | ModernBERT-base | Requirement dimensions designed for coding-assistant traffic; meaningless for one-capability factual QA | any | — | **Drop for the conference** (§3.H); cite as prior art for encoder + sigmoid heads |

### 3.E Hidden-state / self-routing family (adapter U or P; E3)

Brief §1 fixes "hidden-state/self-routing approach as a baseline". `05`, `06`
and §2 give three published designs. They differ in where the signal comes
from and what is trained.

| ID | Baseline | Design (published) | Q | Code | Our version | Cost | N | Tier |
|---|---|---|---|---|---|---|---|---|
| **B-PFA** | **Prefill-activation router** (adapter U) | Activations of an encoder LLM at a layer chosen by Fisher-J in L/2…L, last token, PCA to 100 dims, SharedTrunkNet MLP with per-target P(correct) heads, BCE (`05` §1.8) | Does a "free" signal inside the edge SLM's prefill route as well as a separate micro-encoder? | none | Use **`M_E` as the encoder LLM** (the activations exist on the edge anyway); same per-model heads, calibration and C-1 | one `M_E` prefill per query + small MLP | any | **Core** (E3) |
| B-EOS | **ConsRoute-style** (adapter P) | Frozen device-LM final-layer EOS prefill hidden state + routing prompt, ~5 M-parameter MLP, one scalar consistency score (`05` §1.5) | Same question with the simplest probe | none | Train on the F8 escalation label (`S_{M_S} > S_{M_E}`), not ConsRoute's reranker-similarity label, which needs an extra model. **Name it "EOS-hidden-state probe (ConsRoute-style)"** | as B-PFA | 2 | Rec. (one more probe on the same activations) |
| B-LMT | **RouteLMT-style** (adapter P) | LoRA on the small model jointly with a regression head on the last-prompt-token hidden state, MSE on the quality gain (§2) | Does adapting the SLM itself (LoRA) beat a frozen probe? | none | Gain label = `S_{M_S} − S_{M_E}` from F8 runs; LoRA on `M_E`. **The adapted `M_E` must not be the one that generates EDGE answers**, or the EDGE action's quality changes; serve the router as a LoRA branch used only for scoring | LoRA fine-tune of `M_E`; one prefill per query | 2 | Rec. (it is in the manuscript; see §5) |

**Fair cost accounting for this family (F6).** The hidden-state router runs an
`M_E` prefill before routing. If the decision is `EDGE(M_E)` and the serving
stack can reuse that prefill (same prompt, same KV cache), the prefill is not
wasted. If the decision is `SPLIT_d(M_S)` or `REMOTE(M_S)`, the prefill is pure
overhead. Both cases are charged as measured on Henry's or our edge machine.
KV reuse is claimed only if the implementation actually does it `[OPEN]`. For
B-LMT, LoRA scoring and EDGE generation share the base weights but not
necessarily the cache. This fair accounting is what decides E3. "The
hidden-state router is more accurate but adds the SLM prefill to every
escalated query" is a legitimate result, not a failure.

`03` §2.4 also uses B-PFA's activations as a **privileged-information
teacher** (T-PI). E1 and E3 therefore share one activation-extraction pass.

### 3.F Network-aware routing baselines (systems prior art; adapter P)

| ID | Baseline | Design (`06`, body-read) | Q | Code | Our version | N | Exp | Tier |
|---|---|---|---|---|---|---|---|---|
| **B-BAO** | **Bao-style quality-latency threshold** | p̃ = p − α·(T_edge − T_local), thresholded (Bao et al., ICCC-W'25, Eq. 11–12); p from a RouteLLM-adopted BERT router | Does our multi-action C-1 rule beat the published binary utility-minus-latency rule? | none (§2) | p = calibrated `Û(M_S\|q) − Û(M_E\|q)` from **our** student, or B-RLLM's P(win); `T_edge` = `L̂` of the best realization of `M_S`; α swept | 2 | E5, E6 | **Core** (closest published decision rule) |
| B-NGPT | **NetGPT-style network-adaptive threshold** | Escalate iff score > τ, τ = τ₀ − α·RTT + β·BW (Chen et al., arXiv 2511.22217, Eq. 28) | Is a monotone threshold shift in measured RTT/BW as good as pricing each action's predicted latency? | none | Score from our student; τ₀, α, β fitted on emulated training cells; tested on held-out cells | 2 | E6 | **Core** (published "separated" design with a learned threshold) |
| B-EDRL | EdgeRL-style joint (model × cut) A2C policy | CNN setting; state = battery, tx power, motion (`06` row 111) | — | — | Subsumed by B-INT, which uses our state variables | any | E6 | Covered by B-INT |

### 3.G Oracles and diagnostic controls

| ID | Control | Definition | Q | Tier |
|---|---|---|---|---|
| B-OR | **Per-query oracle** | `argmax_a [S(q, M(a)) − λ·L(a \| q, s)]` with realised scores and measured latency | Headroom: how much can any router gain? (`10` H2) | Core |
| B-OU | **Oracle utility + predicted cost** | true `S` in place of `Û`, our `L̂` | How much value is lost to the cost model? (`09` §6) | Core |
| B-OC | **Predicted utility + oracle cost** | our `Û`, measured latency in place of `L̂` | How much value is lost to the utility estimator? (`09` §6) | Core |

Oracles use labels and are **never** reported as achievable. Under sampled
decoding, the "realised score" oracle overstates headroom because it selects on
noise. Report the oracle with `E[S]` (multi-sample) where S1-MS labels exist
`[PROPOSED]`.

### 3.H Dropped or deferred, with reasons

| Baseline | Decision | Reason |
|---|---|---|
| HyDRA-style | Drop (conference) | No code. Needs a new judge-labelling pass. Its capability dimensions (reasoning, code generation, debugging, tool use) do not apply to single-capability factual QA. Its overlap is already conceded in `05` §3 and `12` |
| Arch-Router fine-tuned | Drop | It has no routing head (`05` §1.9). Fine-tuning would change it into a different method. Zero-shot policy routing (B-ARCH) is optional and only as a latency/generative reference |
| Generative / prompted LLM router (e.g. a 7 B instruct model prompted with model descriptions, as ICL-Router's "LLM Router" baseline) | Opt. | Brief §17 asks "if feasible". It costs a full LLM forward per query on the edge. Run it once at M0 for a single latency-and-accuracy point, if GPU memory allows next to `M_E` |
| RouteLLM SW-ranking, causal-LLM router | Drop | Same pairwise question as B-RLLM. The causal-LLM router (8 B) adds cost without a new question |
| EmbedLLM, GraphRouter, Avengers (LLMRouterBench routers) | Opt. at M2 | Available inside the LLMRouterBench repo. Useful only at N ≥ 4 |
| BEST-Route best-of-n | Drop | Best-of-n is not in our action set. The architecture is covered by `07` (§3.D) |
| ConsRoute full system (K-means + per-cluster GP-BO thresholds) | Drop | Its router is B-EOS. The online threshold tuner answers a different question (adapting thresholds from observed latency) that B-NGPT covers more simply |

---

## 4. Conference core set and success criteria

**Core (16 baselines/controls plus 3 oracles, runnable at M0 with N = 2):**
B-AE, B-AS, B-ASd, B-CB, B-RND, B-DP (equals B-CB on a single dataset),
B-TFIDF, B-S1, **B-C\***, B-SD, B-T, B-INT, B-RLLM, B-PFA, B-BAO, B-NGPT,
plus oracles B-OR, B-OU, B-OC. B-RDC becomes Core at M1 (N ≥ 3).
B-ASd counts as one item although it runs once per valid depth.

**The seven falsification questions they settle:**

| # | Question | Comparison | Honest negative outcome to report |
|---|---|---|---|
| Q1 | Does query content matter? | method vs B-CB, B-RND, B-DP | Method frontier inside B-CB's frontier → no semantic-routing contribution in this pool |
| Q2 | Is a neural encoder needed? | method (and C\*) vs B-TFIDF | No significant gain → report it. The encoder is unjustified at this data scale |
| Q3 | Does KD help? | KD student vs B-C\*, B-SD | "KD did not improve the router over a tuned, calibrated non-distilled student" (`03` §10) |
| Q4 | Does the micro-encoder beat or complement self-routing? | method vs B-PFA (cost-charged), and KD-from-PFA (T-PI) | B-PFA dominates even after charging the prefill → the separate encoder is unjustified |
| Q5 | Does per-model calibrated utility beat pairwise escalation? | method vs B-RLLM (and B-RDC at N ≥ 3) | No gain at N = 2 → the advantage, if any, must come from N ≥ 3 or from the cost integration |
| Q6 | Does the multi-action C-1 rule beat published network-aware binary rules? | method vs B-BAO, B-NGPT | No gain at N = 2 → the contribution reduces to the Split(d) action set and its measured costs |
| Q7 | Does separation lose anything against an integrated state-aware router? | method vs B-INT inside and outside the training range of `s` | B-INT wins inside its range → reword Issue C (`09` §7): separation is justified by reuse and out-of-range behaviour only |

**Statistics** `[PROPOSED]`. The primary metric is realised normalised utility
at pre-registered SLA points, plus the area under the utility–latency frontier
(`09`, `03` §10). Use paired bootstrap 95% CIs over the same test queries and
the same seeds. Adjust for multiplicity across the seven questions with
Holm–Bonferroni. **No fixed "≥ X points" margin is pre-set.** v2's "≥ 5
points over TF-IDF+LR" had no source and is withdrawn. A minimum detectable
effect is computed from the pilot's variance before the main run (`03` §10,
`13`).

---

## 5. Corrections to the manuscript's baseline section

`source/main-original.tex` §Baseline Routing Methods (lines 305–320) lists
RouteLMT, ICL-Router, RouteLLM and Arch-Router-1.5B, adapted to "select
between an SLM and a stronger Split-LLM". It is **not modified** here. The v3
text in `proposed-solution-blue-v3.tex` and `13` should replace it with the
following corrections:

1. **"Select between an SLM and a Split-LLM"** treats Split as a model. Under
   rule A1, Split is a realization of `M_S`. Binary baselines decide `M_E` vs
   `M_S`, and the shared cost step chooses the realization (adapter P, §1.2).
2. **Arch-Router**: "fine-tune its routing head" is impossible, since it
   generates a policy identifier and has no routing head (`05` §1.9). Either
   run it zero-shot as a generative reference (B-ARCH, optional) or remove it.
3. **RouteLMT**: no public code was found, and it was designed for machine
   translation with LMT-60 models. Present it as "RouteLMT-style in-model gain
   regression" inside the hidden-state family (B-LMT), not as a reproduction.
4. **ICL-Router**: its router is a 7 B LLM plus an 8 B embedding model
   (§2). Its edge cost must be reported (F6). Without that, a comparison
   against a ~100 M micro-encoder is not like-for-like. Recommended: keep it
   as an accuracy reference with its measured or charged latency, or move it
   to the full-paper pool (M1+) where its profile-based pool expansion is
   relevant.
5. Add the baselines the manuscript lacks and the review requires: B-CB, B-RND,
   B-TFIDF, B-C\*, B-PFA, B-BAO, B-NGPT, B-INT and the oracles. RouterDC joins
   at N ≥ 3.

Whether the manuscript keeps RouteLMT, ICL-Router and Arch-Router is an
**advisor decision** `[OPEN]` (O-B1).

---

## 6. Baseline → experiment map

| Experiment (`13`) | Baselines used |
|---|---|
| E0 split equivalence | none (unsplit `M_S` is the reference); B-TIE optional follow-up |
| E1 KD value | B-S1, B-C\*, B-SD, B-T, (B-MS), T-PI uses B-PFA activations |
| E2 learned routing value | B-AE, B-AS, B-CB, B-RND, B-DP, B-TFIDF, (B-FRZ), B-RLLM, (B-RDC, B-HYB, B-IRT, B-ICL, B-ARCH) |
| E3 self-routing and calibration | B-PFA, (B-EOS, B-LMT); C\* + post-hoc calibration vs KD |
| E5 utility–latency trade-off | all adapter-U/P baselines, B-CB, B-RND, B-LO, oracles B-OR/B-OU/B-OC |
| E6 network variation | B-CB, B-AS, B-BAO, B-NGPT, **B-INT** |
| E7 real split execution | B-ASd per depth, B-AS |
| E8 domain shift | B-DP, B-TFIDF, B-C\*, B-RLLM, B-PFA |

---

## 7. Pool-size applicability (hand-off from `10`)

| Baseline | M0 (N = 2) | M1/M2 (N ≥ 3) |
|---|---|---|
| Fixed / content-blind (3.A), oracles (3.G) | yes | yes |
| B-TFIDF, B-FRZ, our ablations (3.B/3.C), B-PFA | yes | yes (one head per model) |
| B-RLLM, B-HYB, B-EOS, B-LMT, B-BAO, B-NGPT (adapter P) | **yes** | no. They are binary by design. A cascade extension is a new method and is not attempted |
| B-RDC, B-IRT, B-ICL | defined, but little to learn at N = 2 | **yes**: the natural multi-model competitors |

So M0 is where the pairwise/network-aware literature is compared, and M1 is
where the multi-model routers are compared. A paper reporting only M0 cannot
claim an advantage over multi-model routers.

---

## 8. Compute notes

* **Shared cost dominates.** Generating per-model outcome labels (and E0/E7
  runs) is paid once for all baselines (`08`, `10`). S1-MS multiplies it by k.
* **Cheap baselines** (CPU/minutes): 3.A, B-TFIDF, B-FRZ, B-BAO, B-NGPT,
  oracles.
* **Encoder fine-tunes** (one GPU, each fine-tune × seeds × HPO trials, all
  under the F3 budget): B-S1, B-C\*, B-SD, B-T, B-RLLM, B-RDC, B-HYB, B-IRT.
* **SLM-activation baselines**: one `M_E` prefill pass over all train/test
  queries, shared by B-PFA, B-EOS and T-PI. B-LMT also needs a LoRA fine-tune
  of `M_E`.
* **Expensive**: B-INT (outcomes over many emulated network cells; latency can
  be recomputed from measured profiles if `L̂` is accurate, see `09` E-COST),
  B-ICL (multi-GPU training, ~15 B parameters at inference).

No GPU-hour figure is given. It depends on Henry's hardware and the final pool
(`14`).

---

## 9. Open items

| ID | Item | Owner |
|---|---|---|
| O-B1 | Keep RouteLMT / ICL-Router / Arch-Router from the manuscript, or replace them with the §4 core set? | advisor |
| O-B2 | Licence status of the repos with no detected licence (RouterDC, IRT-Router, ICL-Router, LLMRouterBench) before any code is reused or redistributed | advisor / us |
| O-B3 | Can the edge serving stack reuse the `M_E` prefill after a hidden-state routing decision (F6)? | Henry |
| O-B4 | Are S1-MS labels affordable (enables B-MS and B-HYB at low cost)? | `03` O-F3, `13` |
| O-B5 | Range of emulated `(RTT, BW, load)` cells for training B-INT and B-NGPT, and which are held out | `13`, Henry (tc/netem) |
| O-B6 | GPU memory for a prompted 7 B LLM router next to `M_E` on the edge node | Henry |

---

## 10. Consequences for other deliverables

| File | Consequence |
|---|---|
| `12-novelty-v3.md` | Novelty must survive B-CB, B-BAO, B-NGPT and B-INT. Without a win over B-BAO/B-NGPT at N = 2, the remaining contribution is the multi-action Split(d) set with measured costs. Encoder + sigmoid heads remain conceded (HyDRA, BEST-Route) |
| `13-experiments-v3.md` | Use §6 as the baseline roster per experiment, §4 for statistics, F1–F8 as fairness rules, and the adapters of §1.2 |
| `14-henry-checklist.md` | Ask O-B3 and O-B6; the edge GPU memory decides B-PFA/B-LMT/B-ICL feasibility |
| `15-conference-vs-journal.md` | IRT-Router/ICL-Router-style profile-conditioned pool expansion belongs to the journal |
| `17-verified-references-v3.md` / `.bib` | Add RouteLMT (arXiv 2604.22520 v1; ACL 2026 Industry per arXiv comment, proceedings metadata still to confirm) and ICL-Router (arXiv 2510.09719 v3; AAAI 2026 per arXiv comment; the manuscript gives vol. 40, pp. 33413–33421, still to confirm) at the section-level inspection recorded in §2 |
| `proposed-solution-blue-v3.tex` | Baseline paragraph uses "X-style" naming (F7) and the §5 corrections |

---

## 11. Sources

| Source | Used for | Inspection |
|---|---|---|
| `05` §1.1–1.10, §2–4 | Router designs, overlaps, LLMRouterBench scope | body reads recorded there |
| `06` rows 80–138, §3–4 | Bao, NetGPT-routing, Neurosurgeon, SPINN, Edgent, EdgeRL | levels recorded there |
| RouteLMT, arXiv 2604.22520 v1 (HTML) | §2 card | §3, §4, §5.1–5.3, Limitations read 2026-10-04 |
| ICL-Router, arXiv 2510.09719 v3 (HTML); repo README | §2 card | §3.1–3.4, §4.2–4.3, App. A.4–A.5 read 2026-10-04 |
| GitHub REST API, HF model API | §2 code-availability table | queried 2026-10-04 |
| arXiv HTML of 2603.20895, 2508.11291, 2511.22217, 2603.21237, 2605.17106 | absence of code links | grep for github/huggingface URLs, 2026-10-04 |
| `methods-v2/10-model-pool-and-baselines.md` §7–8 | prior roster (corrected here) | cross-check only |
| `source/main-original.tex` L305–320 | manuscript baselines | read only; unmodified |
