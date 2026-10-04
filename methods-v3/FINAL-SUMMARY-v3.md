# FINAL-SUMMARY-v3 — Hardening the distilled micro-encoder + Split-LLM routing method

Sprint: `MICROENCODER_HARDENING_BRIEF.md` (methods-v3), completed 2026-10-04.
This file answers the 28 questions of brief §28. Every answer points to the v3
deliverable that holds the evidence. **No experiment has been run. No number
below is an experimental result of ours.** Numbers quoted from papers are tagged
`[AUTHOR-CLAIM]`.

Evidence tags follow brief §29: `[VERIFIED-BODY]`, `[VERIFIED-META]`,
`[AUTHOR-CLAIM]`, `[PROPOSED]`, `[OPEN]`, `[REJECT]`. `[DERIVED]` marks our own
mathematical derivations, `[CODE]`/`[ARTIFACT]` marks facts read from public repos,
configs or the Hugging Face API, and `[MS]` marks `source/main-original.tex` line references.

---

## 0. Deliverables and integrity

| Brief §27 item | File | Status |
|---|---|---|
| Review findings | `00-review-findings.md` | done. 30+ findings RF-A1…RF-K3 |
| Issue A/B | `01-model-vs-action-utility.md` | done |
| Issue D, E0 | `02-split-equivalence-analysis.md` | done |
| Issue F | `03-kd-hardening.md` | done |
| Issue E | `04-routeLLM-terminology-review.md` | done |
| Routing prior art | `05-full-routing-prior-art.md` | done. 10 papers read in full |
| Systems prior art | `06-systems-prior-art-map.md` (+ pointer `systems-prior-art-map.md`) | done. About 60 works plus an iteration-15 addendum |
| Backbone | `07-backbone-verification.md` | done |
| Utility | `08-utility-definition.md` | done |
| Cost | `09-cost-policy.md` | done |
| Pool | `10-model-pool.md` | done |
| Baselines | `11-baselines-v3.md` | done |
| Novelty | `12-novelty-v3.md` | done |
| Experiments | `13-experiments-v3.md` | done |
| Henry | `14-henry-checklist.md` | done |
| Conference/journal | `15-conference-vs-journal.md` | done |
| Citation audit | `16-citation-audit.md` (+ identical `citation-audit.md`) | done |
| References | `17-verified-references-v3.md`, `method-references-v3.bib` (44 entries) | done |
| Figure | `architecture-figure-v3.tex` (+ `.pdf`, `latex-compile.log`) | done, compiled |
| Manuscript section | `proposed-solution-blue-v3.tex` (+ `proposed-solution-compile.log`) | done, compiled |
| This file | `FINAL-SUMMARY-v3.md` | done |

**Protected files, re-checked for this summary (2026-10-04):**

| Artifact | Command | Baseline (`00` §1) | Now |
|---|---|---|---|
| `source/main-original.tex` | `sha256sum` | `06f5f9d7…` | `06f5f9d7…` ✔ |
| `methods-v2/` | `find methods-v2 -type f \| sort \| xargs sha256sum \| sha256sum` | `562faa69…` | `562faa69…` ✔ |

`git log -- methods-v2 source/main-original.tex` shows no commit after
the v2 sprint's final commit (`b455274`). No v3 iteration touched either.

---

## 1. Answers to the 28 questions (brief §28)

### Q1. What from v2 remains correct?

`00` §3 lists what survives. Each item needs v3 citations.

1. Learned query-conditioned utility is **kept separate** from runtime-measured
   system cost. This is the advisor-approved core. Only its justification was
   wrong (Q2, Issue C).
2. The observed-outcome oracle is a **label**, not a teacher.
3. A non-distilled control and a pre-registered "KD dropped" branch. The
   direction was right but v2's control was too weak (Q10).
4. TF-IDF+LR as the non-neural floor, and an oracle-headroom degeneracy guard.
5. Hidden-state self-routing as a baseline. Continual learning stays in the journal.
6. Henry's code is treated as `[OPEN]` and nothing about it is invented.
7. Constrained/SLA and Pareto evaluation alongside the λ form.
8. v2 recorded honestly that it had no LaTeX toolchain.
9. Independent sigmoids rather than a softmax are still the right output layer,
   though for a different reason (`01` §7.1): success events are not mutually
   exclusive, and a softmax would need renormalising when the pool changes.

### Q2. What from v2 was wrong or too strong?

The full register is in `00` §2. The load-bearing errors:

| v2 statement | Verdict | Fixed in |
|---|---|---|
| One utility head per action, while split is also assumed lossless (RF-A1) | Internally inconsistent: `m` redundant heads with identical labels, so depth gets chosen by head noise | `01` |
| `y(SPLIT(d),q) = y(full,q)` stated as fact (RF-D) | `[REJECT]` as a premise; it is a hypothesis that E0 tests | `02` |
| "Add an action = add a head", "without costly retraining" (RF-B) | Overclaim: a new model needs labels, head training and recalibration | `01` §5, `15` |
| "Putting `s` into θ forces retraining on every network change" (RF-C) | `[REJECT]`; replaced by the real justification (Q15/Q16) | `09` §7 |
| λ "is the KKT multiplier" (RF-E) | True only for an average budget over randomised policies | `09` §4 |
| "Probability of success" (RF-F) | Undefined for graded or open-ended tasks | `08` |
| RouteLLM = "KD in all but name" (RF-G1) | `[REJECT]` | `04` |
| Same-data ModernBERT-large teacher provides "dark knowledge"; control is α=1 at the same hyperparameters (RF-G2) | Teacher holds no extra label information; control is too weak | `03` |
| Calibration preservation as a standalone novelty (RF-G3) | Withdrawn; it must beat non-KD + post-hoc calibration | `03` §7.3 |
| HyDRA has "4-head sigmoid **utility** output" (RF-H1) | Wrong: the heads are capability requirements | `05` §3 |
| LLMRouterBench "backbone choice has limited impact" as a general fact; "neural routers often tie TF-IDF" (RF-H2) | Over-generalised, and the second part is not in the paper at all | `05` §4, `11` §0 |
| Prior-art search was arXiv/ACL only (RF-H4) | Systems venues were missing | `06` |
| "The first router to …" (RF-I1) | `[REJECT]` | `12` |
| Blue tex had zero `\cite` (RF-I2) | Fixed: 38 verified keys | `proposed-solution-blue-v3.tex`, `16` |
| Figure used `\blacktriangledown`, `\Letter`, `\dashrightarrow`; per-action heads; no CL separation (RF-J1–J4) | Fixed | `architecture-figure-v3.tex` |
| Invented thresholds (ECE ≤ 0.10/0.15, "beat TF-IDF by ≥ 5 points", ≥ 3/4 folds, 2×seed-std), inferred 2×RTX3090 server | Withdrawn | `11`, `13` §8 |
| `Qwen3-72B-Instruct` and Gemma-4 "-A4B" names in the manuscript | Invalid checkpoints | `10` §3 |

### Q3. Should utility be model-level or action-level?

**Model-level** `[PROPOSED]` (`01` §0). Utility attaches to the model
specification `M(a)` that an action executes, and cost attaches to the action:

```
R(q, s) = argmax_{a ∈ 𝓕(q,s)} [ Û_θ(M(a) | q) − Δ̂(a, q) − λ · L̂(a | q, s) ]      (A1 / C-1)
```

Δ̂ ≡ 0 in the default exact branch. "Model specification" includes the weights,
weight quantization, dtype and decoding configuration (`02` §1.1). Model-level
utility is a **parameter-tying constraint**, so it does not have to be assumed:
it holds exactly when E0 passes. When E0 fails, the tie is relaxed as little as
the data requires. v2's per-action heads are the fully untied special case
(Branch L3). The model-level form also maps literally onto the manuscript's
`f_θ(q, M_k)` (Q6). It needs K heads rather than |𝒜|, so it requires less
supervision. Split depth becomes a pure cost decision, and changing the depth
set needs no router training. The ten Issue-A questions are answered one by
one in `01` §4.

### Q4. Under what conditions do Split depths share utility?

They share utility when, at each tested depth, **split execution is
per-query score-equivalent to unsplit execution of the same specification,
within the unsplit model's own run-to-run noise floor** (`02` §2–§5). E0
measures this (Q5, `13` E0). It requires a TOST equivalence decision against
the noise floor `R_A`/`R_B` with thresholds frozen before E0, at greedy decoding
as the primary setting. The conditions that make sharing likely are a raw
same-dtype or upcast transfer, a lossless binary serialization, no activation
quantization, compression or noise, no early exit or split-only adapters, and
KV handling that does not quantize or evict (`02` §3, F1–F14). Even then, bit
exactness is not guaranteed: batch size, GPU type and kernel choice change
floating-point reduction order (`yuan2025nondeterminism` [META+abstract],
`he2025nondeterminism` [BODY]). For that reason the criterion is score
equivalence, not bit equality. Any sharing claim covers only the tested
(configuration, depth) cells.

### Q5. What happens if split execution is lossy?

The method branches on the E0 result (`02` §4.4), and each branch is a relaxation of A1:

* **Branch X:** E0 passes. `Û_θ(M|q)` is shared and Δ̂ ≡ 0.
* **Branch L1:** uniform degradation. A per-depth constant `Û_θ(M|q) − Δ̂(d)`,
  estimated from E0 data, with no router retraining.
* **Branch L2:** degradation that depends on the query. `Û_θ(M|q) − Δ̂(d,q)`,
  a small correction model trained on split-run labels at the failing depths.
* **Branch L3:** only if L2 fails. Untied per-(M,d) heads, which is v2's design
  and is justified only by measured depth-dependent quality, as in BEST-Route's
  action-level heads.
* **Branch E:** early exit, split-only adapters, or any transform that changes
  semantics. The action is a **different model** `M'` and needs its own labels.

The manuscript's own description already allows compression [MS L76]
and a noise-adding split [MS L78], so the lossy case is realistic.
Following brief §5, the lossy formulation is **not** chosen unless Henry's
implementation and E0 require it. Δ̂ is not distilled (`03` §6).

### Q6. What exactly should f_θ be now?

From `proposed-solution-blue-v3.tex` Eq. (ftheta):

```
f_θ(q, M_k) := Û_θ(M_k | q) = σ( w_kᵀ h_θ(q) + b_k ),    h_θ(q) = pool(E_θ(q)),   k = 1..K
```

`E_θ` is a compact bidirectional encoder with mean pooling and **one sigmoid head
per model specification** (K heads, not |𝒜|). Each head is followed by per-model
post-hoc calibration. Live state `s` is **not** an input. f_θ is purely
semantic. Execution actions and their costs are handled by the runtime
controller (C-1). With Δ̂ ≡ 0 and no cost term, the rule reduces to the
manuscript's `R(q) = argmax_{M_k} f_θ(q, M_k)` (`01` §6).

### Q7. What exactly should the student predict?

For each model specification M in the pool, it predicts the **calibrated
expected normalised task score** (`08` U1):

```
U(M | q) := E_ξ[ S_D(y_M(q; ξ), q) ] ∈ [0, 1]
```

`S_D` is dataset D's pre-registered score mapped to [0,1]. `ξ` covers decoding,
numeric and grader randomness. For binary metrics this is `P(pass | q, M)`
(option A), and for graded metrics it is `E[S | q, M]` (option B). Both are
trained with BCE on targets in [0,1], which is a proper scoring rule for a mean
(`08` §2.3). Pairwise preference (C) and "beats the edge" (D) are **not** the
decision variable, because the objective is linear in expected scores. They
remain baselines and diagnostics (`08` §3.2). Task instantiations are in
`08` §4. SimpleQA is our 0/1 mapping of its correct, incorrect and not-attempted
grades, and heterogeneous benchmarks keep a separate `S_D` per dataset
(`08` §4–§5). The student does **not** predict cost, depth or route.

### Q8. What teacher should be used?

Per `03` §5, re-ranked:

* **Primary T1-OOF:** a larger same-tokenizer encoder router. The default
  candidate is ModernBERT-large, with Ettin-400m as an alternative. It
  predicts the same per-model `E[S|q,M]`, is **Platt-calibrated per model
  before distillation**, and its targets on training queries are
  **cross-fitted out-of-fold**. In-sample targets collapse toward the hard
  labels (`03` §4).
* **Required control S3-SD:** self-distillation, where the teacher is the same
  size as the student. It separates "a teacher" from "a larger teacher".
* **T-PI (secondary, most mechanistically justified):** a privileged-information
  teacher that also reads the edge SLM's prefill activations at training time
  (generalized distillation, `lopezpaz2016unifying`). This links E1 and E3.
* **S3-U (secondary):** T1 applied to an unlabelled transfer set, compared
  against self-training on the same pool.
* `[REJECT]`: an LLM teacher, oracle-as-teacher, and using the judge API as the teacher.

The loss is untempered sigmoid-BCE KD on probabilities. Tempered,
logit-MSE and ranking variants are ablations (`03` §6).

### Q9. Is the teacher genuinely providing useful KD information?

**Not by assumption, and probably not as "dark knowledge"** (`03` §0–§3). A
teacher trained on the same labelled data has no extra information about those labels
`[DERIVED]`. With K independent sigmoid heads, Hinton's channel of
similarities between wrong classes largely disappears. For untempered
BCE, KD is exactly BCE against the mixed target `α·y + (1−α)·t̃`
`[DERIVED]`. A same-data teacher can therefore help only statistically:
by denoising single-run labels (Menon et al.), by acting as learned label
smoothing (Yuan et al.), by transferring an easier function (Stanton et al.;
Born-Again), or by supplying targets on unlabelled queries (Hinton's transfer
set). Each of these has a cheaper non-KD competitor. Only T-PI and the transfer-set
variant have a real information mechanism. **Whether KD helps is an E1
outcome. It is not established**, and the conference method is built so
that nothing breaks if KD is dropped.

### Q10. What is the strongest non-KD control?

**C\*** (`03` §9) uses the same architecture, heads and labelled data and
S1 (or S1-MS) targets. Its hyperparameter search includes constant label smoothing
**and** per-(dataset, model) prior smoothing, weight decay,
dropout and early stopping. It gets **the same number of HPO trials** as the KD
student, whose α and T are counted inside that student's budget. It receives
the same per-model post-hoc calibration, and both use ≥ 5 seeds on a shared
seed set. It is accompanied by **S3-SD** (self-distillation) and, for S3-U,
**self-training**. The E1 rule (`03` §10, `13` E1) says KD adds value only if it
beats C\* on the primary decision metric with a paired bootstrap 95% CI that
excludes 0, without being worse on Brier. If it does not, the paper states
**"KD did not improve the router over a tuned, calibrated non-distilled
student in our setting"** and ships C\*. Any calibration claim (E4) must beat
"C\* + post-hoc calibration" (`guo2017calibration`, `muller2019labelsmoothing`).

### Q11. What does RouteLLM actually do?

Source: `[VERIFIED-BODY]`, `04` §1 and `05` §1.1. RouteLLM trains **binary
strong-versus-weak** routers. Each predicts `P(win_strong | q)` from the query
alone by maximum likelihood on **hard categorical pairwise preference labels**
(Eq. 1) and routes to the strong model when that probability exceeds a
threshold (Eq. 2). It has four router types: similarity-weighted Bradley–Terry,
matrix factorisation, a BERT classifier, and a Llama-3-8B classifier. The
labels are about 65k Chatbot Arena human votes, about 1.5k
golden-answer MMLU items, and GPT-4-as-judge pairwise labels on Nectar prompts,
which the paper calls **data augmentation**. The words "distill", "pseudo" and
"soft label" do not occur in the paper. Cost is the fraction of calls to the
strong model. RouteLLM has no network state, no latency model and no split
execution, and it handles two models only. The released checkpoint uses GPT-4 1–5 scores rather than win/tie/loss, so a
reproduction must name the variant. **Manuscript wording:** "RouteLLM trains
binary strong-versus-weak routers on human pairwise preferences, augmented with
pairwise labels produced by an LLM judge (GPT-4) and with labels derived from
golden answers." It must **not** be described as KD.

### Q12. What does HyDRA actually do?

Source: `[VERIFIED-BODY]` v1 and v2, `05` §1.3 and §3. HyDRA is a fine-tuned
ModernBERT-base with **four independent sigmoid heads that predict per-query
capability requirements** for reasoning, code generation, debugging and tool use.
They are **not** per-model or per-route utilities. Each model has a static,
benchmark-derived capability profile in YAML. The decision computes a weighted
shortfall of requirement over profile and picks the **cheapest model whose
shortfall is ≤ τ**. Service health acts only as a veto, and **no network state**
is used. Supervision comes from a judge-scored strong-minus-cheap gap. It is a
Microsoft preprint with no public code.
**HyDRA invalidates as novelty** "a compact fine-tuned ModernBERT router with
independent sigmoid heads" and "adding a model without retraining the encoder",
which HyDRA claims through profiles `[AUTHOR-CLAIM]`. **It does not
invalidate** model-level calibrated utility fused with measured runtime cost
over edge, split and remote actions, the E0 treatment, or KD as an investigated
optimisation. Its latency figures differ between v1 and v2, so any citation
must name the version and setting `[AUTHOR-CLAIM]`.

### Q13. What does LLMRouterBench actually establish?

Source: `[VERIFIED-BODY]` plus repo, `05` §4 and `08` §6. The benchmark has 21 datasets,
33 models and 391,645 instances. The performance pool has 20 models of about 7B on 15 datasets. The
performance–cost pool has 13 flagship models on 10 datasets, including SimpleQA.
The backbone statement covers only **frozen** embedders
(gte-Qwen2-7B-instruct, nli-bert-base, all-MiniLM-L6-v2) feeding **three
embedding-consuming routers** (GraphRouter, EmbedLLM, Avengers). The metric is
average accuracy with a spread of ≤ 2.2 points and no significance test. Fine-tuned encoders,
ModernBERT, DeBERTa, latency, edge hardware, calibration and cost-aware routing
were not tested. The body contains **no TF-IDF/LR baseline**. **Allowed use:**
"swapping the frozen embedding model among three choices changed average
accuracy of three embedding-based routers by at most ≈2 points." **Not
allowed:** "encoder architecture does not matter", or any claim about TF-IDF.
**Data finding** `[CODE]`: SimpleQA labels exist only for the 13 flagship API
models. The manuscript's plan to build routing labels from pre-computed
LLMRouterBench results [MS L205] therefore does **not** cover its edge SLMs
or Split models. New inference runs (L-GEN) are required.

### Q14. Which backbone should we implement first and why?

**ModernBERT-base** `[PROPOSED]` (`07` §5): 149.66 M parameters, 22 layers,
hidden size 768, Apache-2.0, `answerdotai/ModernBERT-base`. ModernBERT-large has
395.88 M parameters, 28 layers and hidden size 1024 [ARTIFACT + VERIFIED-BODY]. The reasons are
narrow. It has the lowest integration risk: native in transformers ≥ 4.48,
official ONNX FP32/FP16/INT8 artifacts, and support in Optimum. It shares a
byte-identical tokenizer with the Ettin ladder (17 M–1 B) and with
ModernBERT-large, so KD and size ablations need no vocabulary alignment. HyDRA
gives a direct routing precedent, which also means it carries no novelty. Its
fine-tuned NLU is competitive with DeBERTa-v3-base `[AUTHOR-CLAIM]`. It is
**not** chosen because it is fastest on our hardware (unmeasured), because
LLMRouterBench says backbones do not matter, or because it is "micro" (it is
base-sized). INT8 and ONNX fidelity is a real risk that E-BB-Q checks. **The
deployment backbone comes from the pre-registered rule (`07` §6):** the
smallest-latency candidate among {ModernBERT-base, Ettin-68m, Ettin-32m,
DeBERTa-v3-small, MiniLM-L12-H384} whose validation utility is within δ of the
best and whose measured p95 latency on the real edge fits the router budget.
**BACKBONE CHOICE IS AN ENGINEERING DECISION, NOT A NOVELTY CLAIM.**

### Q15. What should C(a|s) be in the first implementation?

**C-1** (`09` §0). Predicted **end-to-end latency in seconds** is the only
priced cost, applied inside hard feasibility constraints:

```
𝓕(q,s) = { a : L̂(a|q,s) ≤ L_SLA,  mem_edge(a) ≤ mem_avail(s),  a permitted by data policy }
R(q,s) = argmax_{a ∈ 𝓕} [ Û_θ(M(a)|q) − Δ̂(a,q) − λ · L̂(a|q,s) ]
```

`L̂` is built from the manuscript's `T_total = TTFT + (N−1)·TPOT` [MS L218],
filled from offline compute profiles plus live RTT, bandwidth and
server-queue measurements. Bytes enter **only physically**, as
`bytes / bandwidth` inside `L̂`. Bytes, energy, money and memory are measured and
**reported separately**, never added to milliseconds. λ is in units of normalised
score per second and is kept for theory and for frontier sweeps (E5). The
headline operating point is set on validation data to meet a stated budget. v2's
normalised multi-metric scalar is `[REJECT]` as the online rule.
`[DERIVED]` caveats: for a dense decoder, prefill bytes at the cut **do not
depend on depth**. A pipeline split with server-side sampling pays **one round trip
per token**, so with `REMOTE(M_S)` available a latency-only rule will rarely
pick Split. Split matters mainly in the **private regime**, where raw text may
not leave the edge, or under a server-compute budget. Henry's answer to H13
decides this. MESS+ (constrained LLM routing, NeurIPS 2025) has been read only
at abstract level, so constrained routing is explicitly **not** claimed as a
contribution.

### Q16. What is the corrected conference architecture?

It is drawn in `architecture-figure-v3.tex/.pdf` and written up in
`proposed-solution-blue-v3.tex`.

* **(a) Offline training.** Each model specification M is run and scored on the
  training queries to give `y_i(M)`. Split labels are taken from unsplit runs
  only at depths that pass E0. A **training-only** larger teacher produces
  out-of-fold, per-model Platt-calibrated soft targets. The **student** micro-encoder
  `E_θ` with K sigmoid heads is trained on the mixed target. Post-hoc
  per-model calibration follows. A selection gate keeps KD only if E1 shows that it beats
  C\*. E0 fixes Δ̂ and offline profiling feeds `L̂`.
* **(b) Online inference.** A query q goes through one encoder pass, giving `Û_θ(M|q)`
  for every model (semantic prediction). Live state s feeds the latency model
  `L̂(a|q,s)` (runtime systems measurement). The runtime optimizer applies C-1 over
  the feasible set using the map `M(a)`. The execution actions are **EDGE(M_E) /
  SPLIT_d(M_S) / REMOTE**. The teacher is not deployed.
* State `s` stays out of θ, and the reason is not "retraining on every network change". The
  reasons are that fresh measurements enter the decision directly, the semantic labels need no synthetic
  distribution of network states, one semantic router can be reused across
  deployments, and the two parts can be validated and updated separately (`09` §7).
  An integrated state-input router B-INT is a baseline in E6.
* **No continual-learning element** appears in the figure or the conference
  method (`15`).

### Q17. What novelty claims survive the expanded systems search?

From `06` §3 and `12` §0 and §3–§4: **no "first" claim survives, and every
individual component is published.** The components and their prior work:

* encoder with per-model sigmoid heads: HyDRA, BEST-Route, CR²
* utility minus λ·network-dependent cost: Bao et al., NetGPT routing, CR²
* split-point selection under live bandwidth: Neurosurgeon, SPINN, Edgent
* model × split joint actions: MCDNN, EdgeRL
* learned LLM splitting: Chen (FITEE), Splitwise-UCC
* distilling a router into a cheaper deployable router: CR²

**One integration candidate survives, as bounded-search absence and not as
`[VERIFIED-BODY]`.** It is a single per-query decision over {edge SLM, split
execution of a larger LLM at depth d, remote execution}, in which a learned
**model**-level utility, shared across depths only where E0 shows equivalence,
is combined with a measured, depth-aware latency model. Its strength is
**weak to moderate**. It collapses if Split is dominated by Remote, if the
chosen depth distribution is degenerate, or if there is no routing headroom. The
search covered ACM (ASPLOS, MobiCom, MobiSys, SIGCOMM, EuroSys, SoCC, CSUR),
IEEE (INFOCOM, TMC, TWC, ICDCS, COMST and others), USENIX NSDI/ATC, MLSys and ICML.
JSAC, SenSys, CoNEXT and the MLSys proceedings were searched with no relevant hit.
dblp, ACM DL full text and OpenReview were unreachable, so the search is bounded
(`06` §0, `12` §1). The paper's value must rest on evidence from E0, E1, E6 and E7,
not on priority.

### Q18. What wording is safe BEFORE experiments?

The **Conservative** statement, `12` §5.1, recommended now:

> We study query routing for edge–cloud LLM serving in which a query can be
> answered by an on-device small language model, by split execution of a larger
> model across the edge and a server, or by remote execution. We propose a
> router that separates *what* a model is likely to answer well from *how
> much* it costs to run it: a compact text encoder estimates, for each candidate
> model, the expected task score on the query, and a runtime controller combines
> these estimates with predicted end-to-end latency from live network and load
> measurements to choose an execution action under latency, memory and
> data-policy constraints. Split depths of the same model share one utility
> estimate only if a split-equivalence test shows that split execution preserves
> task scores. We also investigate whether distilling a larger teacher router
> into the compact encoder improves routing over a tuned, calibrated
> non-distilled student.

Its three contribution bullets are a formulation, a runtime controller and an
evaluation protocol, all `[PROPOSED]`. "First", "only", "novel paradigm",
"without retraining", "lossless" and "extensive experiments demonstrate" are
banned (`12` §6).

### Q19. What wording becomes possible AFTER successful experiments?

* **Conditional** (`12` §5.2) is allowed clause by clause, and each clause must
  report its measured Δ with a CI. Its clauses and gates:
  * C-a frontier over content-blind and lexical baselines (E2, E5)
  * C-b KD beats C\* (E1)
  * C-c calibration versus post-hoc-calibrated non-KD (E4)
  * C-d depths are score-equivalent (E0)
  * C-e network variation without retraining the semantic router, within x of the oracle-cost frontier (E6)
  * C-f the edge/split/remote choice extends the frontier on real hardware in the private or budgeted regime (E7, Q6)
  * C-g measured router overhead

  Every clause has a pre-written fallback for failure, for example "KD did not improve
  the router …". The Conditional statement never says "first".
* **Strong** (`12` §5.3) is "To our knowledge — based on a search of ACM, IEEE,
  USENIX and ML venues … — this is the first *evaluation* of a learned query
  router that jointly selects among an on-device model, split execution at
  multiple depths, and remote execution using measured network and compute
  costs." It is allowed **only if** C-a, C-d (or the L variant) and C-f pass,
  a dblp/ACM/IEEE table-of-contents scan of 2023–2026 has been completed and logged in the
  supplement, the scope qualifiers are kept, and the advisor signs off. Even then,
  Conditional is preferred.

### Q20. Which references are now full-body verified?

From `17` §1–§2. `[VERIFIED-BODY]`, meaning method sections read:

* **Routing:** RouteLLM, RouterDC, HyDRA (v1+v2), LLMRouterBench (+repo),
  ConsRoute (v1), Hybrid LLM, BEST-Route, prefill-activation router (v3),
  Arch-Router, IRT-Router, RouteLMT, ICL-Router, CR² (§IV, §VI, §VII), Bao et al.,
  NetGPT routing (§IV)
* **Backbone:** ModernBERT, plus config and HF artifacts
* **KD and calibration:** Hinton et al., Guo et al., Müller et al., Menon et al.,
  Lopez-Paz et al.
* **Systems:** Edgent, SPINN, MCDNN (tech-report version), EdgeRL, Splitwise-UCC,
  Chen FITEE
* **Numerics:** He 2025 (Thinking Machines blog, not peer reviewed)

**BODY-partial**, meaning only the cited sections were read: Stanton et al.,
Born-Again, Cho & Hariharan, Yuan et al. 2020, Kim & Rush, FitNets, DeBERTaV3
(Table 9), Ettin, CALM, SimpleQA. Every key is cited only within the
"May support" limits in `17` §2.

### Q21. Which references remain incomplete?

* **META or abstract only:** Neurosurgeon (cited only for "partition-point
  selection under bandwidth/load"), the Matsubara survey, MiniLM (existence only),
  Yuan et al. 2025 nondeterminism, Split-and-Denoise.
* **Not in the .bib and must not be cited until upgraded:** MESS+ (O-R1, ABS
  only; blocks any constrained-routing claim) and the ABS-level systems hits in
  `06` §1 and §6. The ICDCS 2025 evolutionary-RL paper has an unconfirmed identity
  and is **not** to be cited. CoSense-LLM was withdrawn from arXiv and is `[REJECT]`.
  The CL papers are journal scope (META).
* **Not read in v3, a shortfall against brief §8 priority B:** DistilBERT,
  TinyBERT and ranking-KD papers (PLaD, PAD). No v3 decision depends on them, so
  they are excluded rather than cited at META level. Pseudo-Label (Lee 2013):
  the primary PDF was not retrieved.
* **Camera-ready metadata (O-R2–O-R8):**
  * DeBERTaV3 ICLR page range
  * Lopez-Paz and FitNets proceedings records
  * ICL-Router AAAI record
  * proceedings-PDF page locators, since current locators are sections and equations from arXiv
  * HyDRA author list (5 vs 6)
  * model technical reports for the final pool
  * statistics references (Holm, TOST, bootstrap), not yet checked
* **Pre-submission search (`12` §7):** the dblp table-of-contents scan has not been
  done because dblp was unreachable.

### Q22. Is the architecture figure compile-clean?

**Yes, under Tectonic 0.15.0 (XeTeX engine).** It has 0 errors and 0 overfull or underfull boxes
(`latex-compile.log`). A fresh recompile on 2026-10-04 for this summary gave 0
errors and 0 overfull boxes again. The machine has **no system LaTeX**
(`which pdflatex latexmk xelatex lualatex tectonic` returns nothing). Tectonic was
a user-space static binary in `/tmp`, and nothing was installed system-wide.
**pdflatex/latexmk are untested.** The source uses only standard TikZ libraries
(positioning, arrows.meta, fit, backgrounds, calc), defines all its styles, has no
external assets, and contains none of v2's undefined symbols. The PDF was
inspected visually.

### Q23. Is the blue Proposed Solution citation-complete?

**Yes, by the audit's criteria** (`16`). Every clause of P1–P20 and of both
algorithms is classified as DESIGN, FACT, DERIVED, OBS or SCOPE. Every FACT
carries a key from `method-references-v3.bib`, with a section or equation locator,
an inspection level and a verdict on whether the source supports that wording.
The 38 cited keys all resolve. Six .bib keys are deliberately uncited, with
reasons (`16` §5). Derivations are marked as such and are not left as naked
facts (`16` §6). Five wording fixes were applied, including one case of citation
laundering (RouterDC had been cited for zero-shot models). The section compiles
under Tectonic both standalone and inside an IEEEtran two-column merge wrapper,
with 0 errors, 0 undefined citations and 0 overfull boxes (`16` §8,
`proposed-solution-compile.log`, re-confirmed today). The compile found and fixed two defects: equations too wide for two columns, and internal provenance notes that
would have printed in the reference list. Residual issues are listed under Q21
and in `16` §4: MESS+ is not cited and constrained routing is explicitly disclaimed,
page-level locators are missing, and ConsRoute is absent from P20's preprint list.

### Q24. What still requires advisor approval?

1. The **contribution tier** (Conservative now) and replacing the manuscript's
   contribution and abstract claims [MS L40, L61, L65].
2. **Pool:** the choice of the M0 pair (P-A Phi-4-mini + Llama-3.3-70B, P-B
   Qwen3-4B-Instruct-2507 + Qwen3-32B, or P-H from Henry), the substitute for the
   non-existent `Qwen3-72B-Instruct`, the full-pool composition, and correcting the
   manuscript's invalid model names (`10`). The advisor's **B1/Gemma remark**
   remains unreconstructed `[OPEN]`, and no model is claimed as approved.
3. **Datasets:** whether SimpleQA alone is acceptable, given near-floor edge
   performance and missing labels, or whether a dataset with edge headroom such as
   MMLU-Pro, BBH or MATH500 is added (`08` §6.2).
4. **Headline regime:** open, or private with REMOTE masked (`10` O-P3, `13` O-E3).
5. **Pre-registered thresholds:** δ for the backbone rule, the TOST margins for E0,
   SLA points and the MDE method (`07` §6, `13` §3).
6. Whether to keep RouteLMT, ICL-Router and Arch-Router as manuscript baselines (`11` O-B1). Licence handling for
   baseline code that has no licence file.
7. Whether ConsRoute is added to P20's preprint list. Approval of the merge of the blue
   section, the figure and the .bib.
8. **Journal ordering** and whether the conference conclusion mentions pool evolution
   (`15` O-J1, O-J2). Whether a self-built split is acceptable if Henry's code is
   unavailable (`14` §5).

### Q25. What still requires Henry?

Everything in `14` H1–H23. The send-ready message is in `14` §1. These items are blocking:

* repository and licence (H1)
* exact HF model ID, revision and weight quantization (H2), and whether the same specification runs unsplit (H3)
* split API, static or per-request depth (H4), and valid depths (H5)
* activation shape and extra tensors (H6) and wire dtype (H7)
* compression, quantization or noise at the cut (H8), and exact vs approximate split / early exit (H9)
* **the per-token decode message pattern (H13)**, which is the most consequential systems answer
* `sudo`/`tc netem` permission (H15)
* edge machine (H16) and server machine, GPUs and VRAM (H17)

Also needed: serialization, KV handling, decoding and seed control, link type, software versions,
logging hooks, energy counters, load generator, router memory headroom, and
prefill reuse. The decision map in `14` §3 says which method branch each answer
triggers. **No Henry or lab detail has been invented.** The manuscript's edge
machine (Xeon W-2123, 2×RTX 3090) is quoted as `[MS]` and needs confirmation.
The server is unknown.

### Q26. What are the first 10 coding/experiment steps?

From `13` §7, condensed. Nothing here has been run.

1. **Pre-register**: the partition, `S_D` per dataset, δ, the E0 margins, the MDE method and the SLA points.
2. **Send Henry the `14` §1 message.** In parallel, write the label-campaign harness
   (L-GEN), logging keyed by model-spec record and query ID.
3. **E-PILOT headroom** (H1–H4) on the candidate pairs and datasets, with an oracle
   gap check. Then the advisor freezes the M0 pool and the datasets.
4. **L-GEN** on unsplit specifications: run, grade and store raw grades. Run the `M_E`
   prefill pass for the hidden-state baselines and T-PI.
5. **Baselines first:** fixed policies, random, dataset prior, TF-IDF+LR,
   C\* on ModernBERT-base, all inside the shared C-1 harness with adapters U/P/F.
6. **E-BB / E-BB-Q** backbone ladder plus ONNX/INT8 fidelity, giving the deployment backbone.
7. **E1** with the minimal set S1, C\*, S3-SD, S3(T1-OOF), followed by E4, E2, E3 and E8.
8. **When Henry's code arrives:** the smoke protocol (`14` §4), then **E0** for each
   (configuration, depth), which decides Branch X/L/E.
9. **Profiling, then E-COST** (accuracy of `L̂` and decision regret), then E5 on the testbed,
   then E6 (with B-INT), then **E7** in both regimes, including the pre-registered
   checks of whether bytes vary with depth and whether Split is ever picked over Remote.
10. Optional A-TIE if E0 passes at ≥ 2 depths. Then M1 (N=3), repeating E1, E2, E5 and
    E8 with RouterDC.

### Q27. What should NOT be merged into main yet?

* Any **results, numbers or Conditional/Strong wording**: nothing has been run.
* Any claim that Split is lossless, that depths share utility, or that Split
  beats Remote. These wait for E0, E7 and H13.
* Any KD-benefit or calibration-benefit claim (waits for E1/E4), and v2's N2 calibration lane.
* Pool-evolution or "no retraining" claims [MS L40, L65, L182 second half] and
  any CL content, which are journal scope.
* Specific model names, the Henry hardware and the server sentence until the advisor
  and Henry confirm them. The manuscript's invalid names must be corrected first.
* A constrained-routing contribution, until MESS+ is body-read.
* A "to our knowledge … first" sentence, until the table-of-contents scan is done.
* The methods-v3 working files themselves: they are internal and must not be cited
  in the manuscript. Nothing from `methods-v2/` should be merged.

### Q28. What is ready to merge into main after advisor review?

* **`proposed-solution-blue-v3.tex`** (body between the BEGIN/END MERGE markers) into the empty
  `\section{Proposed Solution}`, with `\usepackage{xcolor}`, keeping the text blue.
  It has been compile-tested inside IEEEtran.
* **`method-references-v3.bib`**, appended to the manuscript bibliography.
  Provenance is in non-printing fields.
* **`architecture-figure-v3.tex`** as a `figure*`, using the merge snippet and caption in
  its header.
* The **Conservative** contribution statement (`12` §5.1), replacing L61/L65 and the
  abstract overclaims at L40.
* The RouteLLM description (`04` §0), the bounded LLMRouterBench sentence
  (`05` §4) and the limitations sentence on pool changes (`15` §5).
* The model-name corrections list (`10` §3.3) and the baseline-section
  corrections (`11` §5), as edits for the advisor to approve. They are not yet applied, because
  `source/main-original.tex` was left untouched as required.

---

## 2. Stop-condition check (brief §31)

| # | Condition | Met? | Evidence |
|---|---|---|---|
| 1 | Model-vs-action resolved with recommendation | ✔ | `01` §0 (model-level, E0-gated tie) |
| 2 | Exact vs lossy split separated | ✔ | `02` §4 (X / L1–L3 / E) |
| 3 | E0 exists | ✔ | `02` §5, `13` E0 |
| 4 | KD teacher survived skeptical review | ✔ | `03` (same-data teacher = regulariser; C\*; E1 can say "no value") |
| 5 | RouteLLM terminology corrected | ✔ | `04` |
| 6 | HyDRA body checked, overlap accurate | ✔ | `05` §1.3, §3 |
| 7 | LLMRouterBench body checked, bounded | ✔ | `05` §4 |
| 8 | ModernBERT facts verified | ✔ | `07` §1 |
| 9 | Systems-venue search expanded beyond arXiv/ACL | ✔ (bounded; dblp unreachable) | `06` §0–§2, `12` §1 |
| 10 | No unsupported "first" | ✔ | `12` §6; banned-wording grep of the tex is clean (`16` §7) |
| 11 | Conference and journal separate | ✔ | `15`; no CL in the figure or the tex |
| 12 | Corrected architecture specified | ✔ | Q16, the figure, and the tex |
| 13 | Blue manuscript has real citations | ✔ | 38 verified keys |
| 14 | Citation audit complete | ✔ | `16` / `citation-audit.md` |
| 15 | Verified BibTeX exists | ✔ | `method-references-v3.bib`, BibTeX-run via Tectonic |
| 16 | Figure source repaired | ✔ | `architecture-figure-v3.tex` |
| 17 | Compilation attempted | ✔ compiled (Tectonic/XeTeX; pdflatex untested) | `latex-compile.log` |
| 18 | Novelty statements evidence-tagged and experiment-gated | ✔ | `12` §3, §5 |
| 19 | No results invented | ✔ | no experiment run; all numbers are `[AUTHOR-CLAIM]`, `[ARTIFACT]` or `[DERIVED]` |
| 20 | All 28 questions answered | ✔ | §1 above |

Protected files: `source/main-original.tex` and `methods-v2/` are unchanged (§0).
