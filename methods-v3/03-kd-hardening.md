# 03 — Knowledge-distillation hardening (Issue F)

*Deliverable 03 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 12). Resolves findings RF-G2
and RF-G3 from `00-review-findings.md` and stop item 4 ("KD teacher logic has
survived a skeptical review"). Answers brief §7 and supplies FINAL-SUMMARY
questions 7–10.*

Inputs: `01` (utility attaches to the model specification `M(a)`, K heads,
optional depth correction `Δ̂`), `04` (supervision conditions S1, S1-MS, S2,
S2-J, S3, S4 and KD terminology), `05` (prefill-activation router, Hybrid LLM,
ConsRoute body readings), `07` (ModernBERT/Ettin sizes, same tokenizer across
the ladder), `08` (target `U(M|q) = E_ξ[S_D]`, BCE with targets in [0,1],
calibration split, metrics), `09` (decision rule C-1 and frontier evaluation).

Eight KD and calibration papers were read for this file (§13). Every one of them
studies image classification, speech or translation. **None studies routing.**
Each transfer of their findings to a router is therefore our hypothesis
(`[PROPOSED]`/`[OPEN]`), and the experiment in §10 is what tests it.

Evidence tags as in brief §29: `[VERIFIED-BODY]`, `[VERIFIED-META]`,
`[AUTHOR-CLAIM]`, `[PROPOSED]`, `[OPEN]`, `[REJECT]`. `[DERIVED]` marks our own
algebra, shown inline so it can be checked.

---

## 0. Bottom line

1. **A teacher trained on the same labels holds no extra information about
   those labels.** v2's teacher T1 (ModernBERT-large on the same `y(a,q)`) can
   help the student only *statistically*, in one of four ways (§2):
   (M1) replacing noisy single-run labels with estimates of their mean,
   (M2) regularising like learned label smoothing, (M3) transferring an
   easier-to-fit function, and (M4) supplying targets on queries that have no
   labels. Each way has a cheaper non-KD competitor. "Dark knowledge" in Hinton's
   sense (similarity between wrong classes) **barely exists here**, because the
   student has K independent sigmoid heads, not a softmax (§3.1).
2. **Two teachers *do* hold more than the student can see.** (a) A teacher that
   reads **privileged inputs** at training time, such as the edge SLM's prefill
   activations (generalized distillation, Lopez-Paz et al. 2016). (b) A teacher
   used on a large **unlabelled query pool** (a transfer set). These are the KD
   variants with a real mechanism. Same-data T1 is kept, but it is now tested as
   a regulariser, not assumed to carry dark knowledge (§5).
3. **With untempered sigmoid BCE, KD is just training on a mixed target.**
   `α·BCE(p,y) + (1−α)·BCE(p,t̃) = BCE(p, α·y + (1−α)·t̃)` exactly `[DERIVED]`
   (§3.2). Label smoothing mixes in a constant, and prior smoothing mixes in a
   per-(dataset, model) base rate. KD mixes in a query-dependent teacher output.
   This gives a clean **ladder of controls** that isolates what the teacher adds.
4. **Teacher targets on training queries must be cross-fitted.** A
   large encoder fine-tuned on a few thousand queries can fit them almost exactly. Its
   in-sample outputs then come close to the hard labels, and "KD" collapses into S1. Teacher
   targets are therefore produced **out-of-fold** (§4).
5. **Teacher predicts** the calibrated per-model expected score
   `t̃(q,M) = Platt_M(z_T(q,M)) ≈ E_ξ[S_D | q, M]`, the same object as `08` (U1).
   It does **not** predict a ranking, a pass/fail label or a cost-aware route (§6).
   The teacher is calibrated **before** distillation. Every student, KD or not,
   is calibrated **after** training on the same calibration split (§7).
6. **Strongest non-KD control (C\*)** (§9): same student, same labelled data,
   S1 targets (S1-MS where it exists at an equal budget), with label smoothing
   *and* prior smoothing in its search space, weight decay, dropout and early
   stopping. It gets **the same number of hyperparameter trials** as the KD
   student, and per-model post-hoc calibration. A **self-distillation**
   control (teacher = same-size student) separates "any teacher" from
   "a larger teacher".
7. **E1 can conclude "KD adds no value"** (§10). The decision rule is
   pre-registered. If KD does not beat C\* on the primary decision metric, with
   a paired bootstrap CI that excludes 0, the paper ships C\* and reports KD as a
   negative or neutral finding. The conference method does not depend on KD
   working.
8. **v2's calibration novelty lane (N2) is withdrawn as a contribution.** Any
   calibration claim must beat "C\* + post-hoc Platt/temperature scaling" (Guo
   et al. 2017). Müller et al. 2019 show that label smoothing alone already
   recovers much of the calibration benefit, in their (non-routing) settings (§7.3).

---

## 1. What the review must decide (brief §7)

| Brief §7 question | Answer location | Short answer |
|---|---|---|
| Why should the large teacher contain information beyond `y`? | §2 | It does not, if it sees only the same `(q, y)`. It can still help statistically (M1–M4). It holds real extra information only with privileged inputs or unlabelled queries. |
| When can soft outputs help? | §2, §3 | When single-run labels are noisy estimates of `U` (M1), when the student overfits (M2), when the student optimises poorly (M3), or when more queries exist than labels (M4). |
| What is gained over label smoothing? | §3.2 | Only the *query dependence* of the mixed-in target. Tested directly by the control ladder. |
| What is gained over ordinary regularisation? | §9 | Unknown. C\* includes it with an equal tuning budget. |
| What is gained over a directly trained student? | §10 | That is E1's primary contrast, against C\*, not against α = 1 with fixed hyperparameters. |
| Teacher calibrated before distillation? | §7.1 | Yes (primary). Uncalibrated teacher is an ablation. |
| Student calibrated after distillation? | §7.2 | Yes, every condition, same split. |
| Can teacher uncertainty be useful? | §8 | As the target value itself, yes. As sample weights or a runtime signal, only as an optional ablation. Not in the conference core. |
| P(success), expected score, or ranking? | §6 | Expected score `E[S|q,M]` (equals P(success) for binary datasets). Ranking only as an ablation. |
| Logits, probabilities, regression or pairwise? | §6 | Probabilities with BCE (primary). Logit MSE and pairwise as ablations. |
| Strongest non-KD control? | §9 | C\* plus self-distillation. |

---

## 2. What a same-data teacher can and cannot add

### 2.1 The information argument `[DERIVED]`

Let `D_L = {(q_i, y_i(M))}` be the labelled training set. A teacher `T` trained
only on `D_L` produces `t(q, M) = g(D_L, q)` for a fixed training procedure `g`.
For any query in `D_L`, its target is a function of data the student also
receives. So `t` adds **no information** about the labels. Whatever KD
contributes is in **how** the student uses `D_L`: a different loss target, a
different effective prior, a different optimisation path. These are
legitimate effects. They are statistical, not informational, and each one has a
non-teacher way of getting it. v2 (`methods-v2/04` T1, "Circular labels: No")
said T1 adds generalisation because "the student distills T1's generalisation,
not the raw outcomes". That is the right intuition, but it does not show that T1
beats a well-regularised student. That is an empirical question (RF-G2).

### 2.2 The four statistical mechanisms

| # | Mechanism | Literature (tag) | Router-specific reading `[PROPOSED]` | Non-KD competitor |
|---|---|---|---|---|
| **M1** | **Denoising / variance reduction.** The best teacher outputs the Bayes class-probability `p*(x)`. Training on `p*` instead of one-hot labels lowers the variance of the empirical risk. An imperfect teacher trades bias for variance. | Menon et al., ICML 2021, §3 (Bayes teacher) and §3.2 (bias–variance trade-off for approximate class-probabilities) `[VERIFIED-BODY]` (arXiv v1 body; see §13) | Our target *is* a mean, `U(M|q) = E_ξ[S]` (`08` U1). A single run gives `y ∈ {0,1}`, a one-sample draw. A teacher that estimates `E[S|q,M]` is exactly Menon's "approximate Bayes" teacher. **This is the most credible KD mechanism for routing**, because routing labels are inherently stochastic (sampling, numeric noise, grader noise; `02` §2.3, `08` §2.2). | **S1-MS**: estimate the mean directly with k real runs (Hybrid LLM's r_prob; `04` §5, `05` §1.6). Prior smoothing (§3.2). |
| **M2** | **Regularisation, "learned label smoothing".** KD acts as label-smoothing regularisation. Even a poorly trained teacher, or a reversed one (student teaching teacher), helps. Hand-designed soft targets get comparable gains. | Yuan et al., CVPR 2020, abstract, §2.1–2.2 (reversed / defective KD), §3 (KD ↔ LSR), §4–5 (Tf-KD) `[VERIFIED-BODY]` `[AUTHOR-CLAIM]` for the numbers | If T1 helps mainly through M2, label smoothing or prior smoothing on the student should match it. | Label smoothing, prior smoothing, weight decay, dropout, early stopping (C\*). |
| **M3** | **Optimisation / function transfer.** Students often do *not* match their teachers ("low fidelity") even when they have the capacity to. In self-distillation, generalisation improves anyway. With large teachers (ensembles), better fidelity does translate into better generalisation. | Stanton et al., NeurIPS 2021, abstract, §1, §4.1–4.4 `[VERIFIED-BODY]` | Whether a ModernBERT-large → base/Ettin student is a "large-teacher" or a "self-distillation-like" regime here is unknown. Report teacher–student agreement (fidelity) next to accuracy so the mechanism can be identified rather than assumed. | Self-distillation (same-size teacher), Born-Again style (Furlanello et al., ICML 2018: identical-architecture students outperform their teachers, abstract, §3.2) `[VERIFIED-BODY]` `[AUTHOR-CLAIM]`. |
| **M4** | **Transfer set.** The teacher labels inputs that have no ground truth, and the student learns from more queries than were labelled. | Hinton et al. 2015 §6, Table 5 (teacher on 100% of the data, student on 3%) `[VERIFIED-BODY]` (via `04`). Stanton et al. §5 (choice of distillation data matters) `[VERIFIED-BODY]` | Unlabelled **queries** are cheap. Router labels are expensive: every `(q, M)` label is an LLM inference run plus grading (`08` §6). So a large unlabelled query pool is a realistic asymmetry that favours KD. | **Self-training**: the C\* student labels the pool itself and is retrained. This separates "more queries" from "a better teacher". |

### 2.3 Capacity is not automatically good

Cho & Hariharan (ICCV 2019, abstract, §5.2–5.3) `[VERIFIED-BODY]`
`[AUTHOR-CLAIM]`: "larger models do not often make better teachers". They
attribute this to mismatched capacity, and stopping the teacher's training early
mitigates it. Their §5.3 goes further: on ImageNet, "all teachers lead to lower
student accuracy than a student trained from scratch". So KD can hurt, not just
fail to help, and E1 must allow that outcome. Consequences `[PROPOSED]`:

* Teacher size is a **factor**, not a premise. Use at least two sizes from the
  same-tokenizer ladder (`07` §2: ModernBERT-base 149.7 M / ModernBERT-large
  395.9 M / Ettin-150m / Ettin-400m), with the student held fixed.
* The teacher checkpoint is selected by **calibration-split Brier score**, not by
  training loss. The training budget is set to this rule before E1 runs, so
  the checkpoint cannot be picked on test results.

### 2.4 Teachers with genuine extra information

These are the only teacher designs in which "the teacher knows something the
student cannot see" is literally true:

* **T-PI, privileged-information teacher.** Generalized distillation (Lopez-Paz,
  Bottou, Schölkopf, Vapnik, ICLR 2016, §4) `[VERIFIED-BODY]` trains a teacher
  on privileged features `x*` that exist at training time only, then distils into
  a student that sees only `x`. For us, `x*` = **the edge SLM's prefill
  activations**, which are exactly the input of the prefill-activation router
  (`05` §1.8: per-target P(correct) heads with BCE on encoder-LLM activations)
  and of ConsRoute (`05` §1.5). At inference those activations cost an SLM
  prefill, which the micro-encoder is meant to avoid. At training they cost
  nothing extra. This turns the hidden-state baseline (brief §2, `11`) into a
  **candidate teacher**. E1 and E3 then share a clear question: *how much of the
  hidden-state router's accuracy can a text-only micro-encoder recover by
  distillation, at what latency?* `[PROPOSED]` `[OPEN]` (depends on SLM access
  and on the pool, `10`).
* **T-U, transfer-set use of any teacher** (M4 above).

Other privileged inputs that are allowed at training time (model responses,
reference answers) are **rejected as teacher inputs**. A teacher that sees the
response and the reference re-derives `y` from the run itself. It estimates
nothing about `E_ξ[S]` beyond the one draw, and it is the label-construction
step `08` already owns (S2-J), not a teacher `[REJECT]`.

---

## 3. What KD reduces to for per-model sigmoid heads

### 3.1 Hinton's "dark knowledge" channel narrows

Hinton et al. (§1–2) locate the benefit in the relative probabilities of the
*incorrect* classes of a softmax. Furlanello et al. (§3.2) decompose the KD
gradient into a dark-knowledge term and a term that acts as **importance
weighting of samples by the teacher's confidence**. `01` gives the student **K
independent sigmoid heads**, one per model specification, so there is no
softmax over models and no "incorrect class" whose relative mass could carry
similarity information. Per head, the teacher supplies one number per `(q,M)`,
namely its confidence. What remains of dark knowledge is:

1. the **per-pair confidence** (Furlanello's weighting term, and M1's
   mean estimate), and
2. **cross-model correlation**: the teacher's heads share a trunk, so its
   targets for `M_1` and `M_2` on the same query are correlated in ways that
   reflect query difficulty. The student's heads also share a trunk, so it can
   absorb this. It is a weaker channel than softmax dark knowledge. It is also
   reproducible without a teacher, through multi-task training on all K heads,
   which C\* already does.

So the softmax-based KD story should **not** be told for this router.
`methods-v2/03` KD-1 (softmax over actions) is `[REJECT]`ed as the primary
formulation. It couples the models in one softmax, against `01`/`08`, and it
was the formulation in which dark knowledge was meant to live.

### 3.2 The mixed-target identity and the control ladder `[DERIVED]`

For a prediction `p = σ(z_S)` and targets `y, t̃ ∈ [0,1]`, with
`ℓ(p,t) = −[t·log p + (1−t)·log(1−p)]` (`08` §2.3):

```
α·ℓ(p, y) + (1−α)·ℓ(p, t̃)
  = −[ (α y + (1−α) t̃) log p + (α(1−y) + (1−α)(1−t̃)) log(1−p) ]
  = ℓ(p, m),   with m = α y + (1−α) t̃ ,   because ℓ is linear in t.
```

So untempered KD with BCE is ordinary BCE training **against a mixed target
`m`**. The rest of the ladder takes the same form:

| Rung | Mixed-in target `t̃(q,M)` | What it isolates | Condition ID (→ `13` E1) |
|---|---|---|---|
| L0 | none (α = 1) | hard labels | S1 |
| L1 | constant 0.5 | binary label smoothing | S1 + LS |
| L2 | per-(dataset, model) training base rate `p̄_{D,M}` | **prior smoothing**: a query-independent but model-aware target (the "dataset prior" baseline of brief §17, used as a smoother) | S1 + PS |
| L3 | same-size student, out-of-fold | self-distillation (any teacher, no extra capacity) | S3-SD |
| L4 | larger teacher, out-of-fold, calibrated | **KD proper** (capacity) | S3 |
| L5 | privileged teacher (T-PI), out-of-fold | KD with information the student lacks | S3-PI |
| L6 | L4 or L5 on an unlabelled query pool | transfer-set KD | S3-U (vs self-training ST) |
| — | multi-sample empirical mean of k runs | soft targets, no teacher | S1-MS |

The teacher earns credit only for what the **upper** rungs gain over the **lower**
ones. "KD beats S1" says nothing on its own: L1/L2 may give the same gain. M1 is
established only if L4 > L2. M3 ("larger teacher") is established only if
L4 > L3. Real privileged information is established only if L5 > L4.

**Tempered variant (ablation only).** If the KD term instead uses
`ℓ(σ(z_S/T), σ(z_T/T))`, the identity breaks. The gradient of that term with
respect to `z_S` is `(σ(z_S/T) − σ(z_T/T))/T ≈ (z_S − z_T)/(4T²)` for large `T`
(first-order expansion of σ around 0) `[DERIVED]`. This is why a `T²` factor
keeps the term's magnitude comparable across temperatures, the same argument as
Hinton et al. §2.1 for softmax. It is kept as ablation S3-T. The primary S3
uses a **calibrated, untempered** teacher target (§7.1), which removes `T` as
a free hyperparameter. That leaves the analyst one fewer knob to tune
until KD wins.

---

## 4. In-sample memorisation: cross-fitted teacher targets

**Problem `[PROPOSED]`.** The teacher is a high-capacity encoder fine-tuned on
`D_L`. Its outputs on `D_L`'s own queries are in-sample predictions. The more
closely it fits, the closer `t̃(q_i,M)` gets to `y_i(M)`, and the mixed target
`m` approaches the hard label (rung L0). Müller et al. (§6, final bullet)
`[VERIFIED-BODY]` make the related point that a teacher in the interpolation
regime gives no information beyond the label on its training set, while a
teacher that does not fit perfectly passes its errors on to the student.
Neither outcome is what v2 intended.

**Remedy `[PROPOSED]`.** **Out-of-fold (cross-fitted) targets**: split `D_L`
into F folds (F = 5). Train F teachers, each on F−1 folds, and give each query
the target from the teacher that never saw it. Unlabelled-pool targets (L6) and
the deployed teacher use an all-folds teacher or the F-teacher mean. This is
standard stacking practice. It costs F teacher fine-tunes, which is affordable
for an encoder.

**Factor in E1.** In-sample vs out-of-fold targets for rung L4 (one
contrast, at the primary teacher size). If in-sample targets are
indistinguishable from S1, that by itself shows why v2's T1 design would
have been close to vacuous.

**Leakage rules.** Teacher folds use the training split only. The calibration
split (`08` §7) and test split are never seen by any teacher, by the
teacher's Platt fit (it has its own split, §7.1), or by the HPO of any
condition.

---

## 5. Teacher options, re-ranked

v2 (`methods-v2/04`) ranked six teachers and chose T1. The v3 ranking:

| ID | Teacher | Extra information? | Status | Notes |
|---|---|---|---|---|
| **T1-OOF** | Larger same-tokenizer encoder (ModernBERT-large / Ettin-400m), same `D_L`, cross-fitted, calibrated | No (statistical only, M1–M3) | `[PROPOSED]` **primary KD condition** | Kept because it is the cleanest and cheapest test. It no longer carries a dark-knowledge rationale. |
| **T-SD** | Same-size student as teacher, cross-fitted | No | `[PROPOSED]` **required control** | Isolates "larger" from "any teacher" (L3). |
| **T-PI** | Prefill-activation probe on the edge SLM (`05` §1.8 architecture), cross-fitted | **Yes** (privileged `x*`) | `[PROPOSED]` secondary, `[OPEN]` on SLM access | Strongest a-priori KD case. It also bridges E1 and E3. |
| **T-ENS** | Ensemble of F fold teachers (or 3–5 seeds) | No, but a better estimate of `E[S]` (M1) | `[PROPOSED]` optional | Stanton et al. §1: with large teachers such as ensembles, better fidelity translated into better generalisation. |
| T-U | Any of the above on an unlabelled query pool | Yes (more queries) | `[PROPOSED]` secondary, needs a pool | Must be compared with self-training (ST). |
| T2 | Generative LLM rating utilities | Possibly, but contaminated and not reproducible | `[REJECT]` as a KD teacher for the conference | Kept only as a label source, S2-J, where a task has no reference answer (`04` §5). |
| T4 | "Oracle" observed outcomes | — | `[REJECT]` as a teacher | These are the labels themselves (S1). Calling them a teacher would make "KD" a relabelling (v2 `03` §4 already flagged this). |
| — | Lab TypeSafe/"Jev" judge API | — | `[REJECT]` | Licence forbids it (`research/jev-system-one.md` §J5, unchanged from v2). |

**Recommendation.** The conference E1 runs **S1, C\*, S3-SD and S3 (T1-OOF)**
as the minimal set. S3-PI and S3-U are added only if their prerequisites (SLM
activations, unlabelled pool) are cheap once the pool (`10`) is fixed.
None of these is a novelty claim. KD mechanisms are generic (`04`).

---

## 6. What the teacher predicts, and the KD loss

* **Target object.** `t̃(q,M) ≈ E_ξ[S_D | q, M] ∈ [0,1]`, the same quantity as
  the student's head (`08` U1), per model specification `M`. For binary
  datasets this is `P(pass | q, M)`.
* **Not P(S ≥ τ) on graded data.** Thresholding discards information, and the
  decision rule needs expectations (`08` §3.2).
* **Not a ranking.** The C-1 decision rule (`09`) is linear in per-model
  expectations, so a ranking teacher would be supervising something the
  decision does not use. Pairwise KD stays an ablation (S3-RANK). It is also the
  part of the space closest to RouteLLM's preference supervision (`04`).
* **Not a cost-aware route label.** That bakes `λ` and the training-time system
  state into the weights. This was rejected in v2 already and is unchanged.
* **Probabilities, BCE (primary).** BCE is a proper scoring rule for a mean in
  [0,1] (`08` §2.3), so the student is consistent for whatever mean the mixed
  target `m` encodes. Ablations: logit-matching MSE (S3-LOGIT) and the tempered
  form (S3-T, §3.2).
* **Depth correction `Δ̂`.** If E0 fails and `01` activates `Δ̂(a,q)`, `Δ̂` is
  trained directly on depth-specific labels. It is **not** distilled: it is
  small, it exists only if E0 fails, and adding KD to it would multiply
  conditions for no stated mechanism.

Primary student loss `[PROPOSED]`:

```
L_S(θ) = Σ_i Σ_{M ∈ 𝓜} w_{D(i)} · ℓ( σ(z_θ(q_i, M)),  α·y_i(M) + (1−α)·t̃_OOF(q_i, M) )
         + weight decay
```

`w_D` is the per-dataset weight from `08` §5. α ∈ {0, 0.25, 0.5, 0.75} is
searched on the validation split, with α = 1 being S1, which is part of C\*'s
space through rung L0. For C\*, the same form applies with `t̃` replaced by 0.5 (L1) or
`p̄_{D,M}` (L2), and ε = 1 − α is searched over the same grid.

---

## 7. Calibration order

### 7.1 Teacher: calibrate **before** distillation (primary)

Guo et al. (ICML 2017, §3) `[VERIFIED-BODY]` relate increased model capacity to
overconfidence: once training samples are classified correctly, "NLL can be
further minimized by increasing the confidence of predictions". An overconfident
teacher pushes `t̃` towards 0/1, back to the hard labels. Under M1 (§2.2), the
teacher's job is to estimate `E[S]`, and a calibrated teacher is closer to
Menon's Bayes teacher. So:

* Fit **per-model Platt scaling** (two parameters per head; Guo et al. §4.1
  treat Platt scaling for binary models, and temperature scaling as its
  single-parameter variant, §4.2) on a **teacher-calibration split** carved out
  of the training data. It is never the student's calibration split or the test split.
* Ablation: uncalibrated teacher targets (S3-RAW).

### 7.2 Student: calibrate **after** training, every condition

Every student, S1, C\*, S3-SD, S3 and the rest, gets the same per-model post-hoc
Platt / temperature fit on the same calibration split (`08` §7). ECE and Brier
are reported **both before and after** that step. A KD calibration advantage
counts only if it survives post-hoc calibration of the control.

### 7.3 Why calibration is decision-relevant here (and why N2 is withdrawn)

* In multiclass softmax, temperature scaling leaves the argmax unchanged, so
  accuracy is unaffected (Guo et al. §4.2). **Our decision is not a single
  softmax argmax.** The rule compares `Û(M_1|q) − λC(a_1|s)` with
  `Û(M_2|q) − λC(a_2|s)` across independently calibrated heads. Per-model
  calibration therefore **does** change routes, and the realised
  utility-latency frontier with them `[DERIVED]`. Calibration is part of the
  method, not a cosmetic report.
* Müller et al. (NeurIPS 2019, §3) `[VERIFIED-BODY]` `[AUTHOR-CLAIM]` find that
  label smoothing reduces ECE about as well as temperature scaling, in image
  classification and translation. v2's lane N2 ("calibration preserved under
  distillation" as a standalone contribution) is therefore `[REJECT]`ed as a
  contribution. Calibration under KD is **measured** in E4 against "C\* +
  post-hoc calibration", and any result is reported as a finding, not as a
  novelty lane (RF-G3; hand-off to `12`).
* Müller et al. (§4) `[VERIFIED-BODY]` also report that teachers trained **with**
  label smoothing make worse students, because label smoothing "erases"
  similarity information in the logits. That evidence concerns multiclass
  softmax teachers, and §3.1 argues the channel is narrow here, so its
  transfer is unproven. As a precaution `[PROPOSED]`, **the teacher is trained
  without label smoothing**, and label smoothing is applied only on the control
  side. The teacher's calibration comes from Platt scaling (§7.1).

---

## 8. Teacher uncertainty

* **Aleatoric (outcome) uncertainty** is already the target. A teacher output
  of 0.6 *is* "60% expected score". Nothing extra is needed.
* **Epistemic uncertainty** (disagreement between fold teachers or seeds, T-ENS)
  is **not** mixed into the target. Mixing it in would confuse "this query is a
  coin-flip for M" with "the teacher does not know". Two optional,
  non-core uses: (a) confidence weighting of KD samples (Furlanello et al. §3.2
  read KD's gradient partly as importance weighting by teacher confidence), as
  ablation S3-W; (b) a diagnostic plot of student error vs teacher
  disagreement. **No runtime use** in the conference method. The student does
  not carry the teacher, and a deferral rule based on uncertainty would be a new
  routing policy outside `09`.

---

## 9. The strongest non-KD control (C\*)

`[PROPOSED]`, fixed before E1:

| Element | C\* specification | Why |
|---|---|---|
| Architecture | Identical to the KD student (same backbone, K heads, pooling) | Same inference latency, so a gain cannot come from capacity. |
| Labelled data | Identical `D_L` and splits | Same information. |
| Targets | S1. S1-MS where the multi-sample labels already exist for every condition | Do not deny the control soft empirical targets that the KD student implicitly benefits from. |
| Smoothing | Search space includes ε for L1 (constant) **and** L2 (prior) smoothing | KD must beat smoothing, not just hard labels (M2). |
| Regularisation | Weight decay, dropout, early stopping on validation Brier, all searched | "Ordinary regularisation" competitor. |
| Tuning budget | **Same number of HPO trials** and the same search algorithm as the KD student. The KD student's α (and T in S3-T) are counted inside its budget | Without this, KD's extra hyperparameters are an unfair advantage (`00` H-B). |
| Calibration | Per-model post-hoc Platt / temperature on the shared calibration split | Calibration gains cannot be credited to KD (§7.2). |
| Seeds | ≥ 5 seeds per condition, the same seed set | Seed variance of C\* is the noise floor for "KD helps". |
| Companion control | **S3-SD** self-distillation, same OOF protocol | Separates "teacher" from "larger teacher" (M3). |
| For S3-U only | **Self-training (ST)** on the same unlabelled pool | Separates "more queries" from "better teacher" (M4). |

v2's control (α = 1 at the KD student's hyperparameters, `methods-v2/03` §2
KD-5) is **not** C\*. It gives the control fewer tuned knobs than the treatment,
and it lacks smoothing, which is the cheapest competitor of all. RF-G2 is
resolved by replacing it.

---

## 10. E1 design (hand-off to `13`)

**Question.** Does distilling a larger (or privileged) teacher into the
micro-encoder improve routing over C\*, at identical student inference cost?

**Conditions (minimal conference set).** S1, C\*, S3-SD, S3 (T1-OOF, calibrated).
**Secondary, if prerequisites are met:** S3-PI, S3-U vs ST, S1-MS, S3 in-sample
(the §4 contrast), teacher size ×2 (§2.3), S3-RAW, S3-T, S3-RANK, S3-W.

**Metrics** (defined in `08` §7 and `09`):

1. **Primary decision metric**: realised normalised utility under the C-1 rule
   at the pre-registered latency SLA points, and the area under the
   utility–latency frontier (`09`). Per dataset, plus a macro average.
2. **Primary estimation metric**: per-model test **Brier score** of `Û`, a
   proper scoring rule. Lower is better.
3. Secondary: AUROC per model (binary datasets), ECE / mean-calibration error
   before and after post-hoc calibration, regret vs oracle, and teacher–student
   agreement (fidelity, for mechanism M3; Stanton et al. §3.2 define agreement
   metrics).

**Pre-registered decision rule `[PROPOSED]`.**

* "KD adds value" **iff** S3 (or S3-PI / S3-U) beats C\* on the primary
  decision metric, with a paired (same queries, same seeds) bootstrap 95% CI of
  the difference that excludes 0, **and** is not worse on Brier.
* If S3 > S1 but S3 ≈ C\*: report "the gain is attributable to
  regularisation/smoothing, not to distillation". Ship C\*.
* If S3 ≈ S3-SD > C\*: report "self-distillation effect; teacher capacity not
  needed". Ship whichever is cheaper to train.
* If S3-PI > S3 > C\*: report "privileged-information distillation helps".
  This is the most interesting positive outcome, and it is still a combination of
  known techniques (`12`).
* If no KD condition beats C\*: the paper states **"KD did not improve the
  router over a tuned, calibrated non-distilled student in our setting"** and
  uses C\* as the deployed router. Nothing else in the method changes. The
  model-level utility, the cost rule and Split execution are independent of KD.

**Statistical floor.** With ≥ 5 seeds and per-dataset test sets of a few
hundred to a few thousand queries, small KD effects (< 1 Brier point, < 1
utility point) may be undetectable. `13` must report the minimum detectable
effect from the C\* seed variance before claiming either direction. A
non-significant result is reported as "no detectable improvement", not as
"KD is harmful" `[OPEN]`.

**Data-regime caveat.** On near-floor datasets such as SimpleQA for edge SLMs
(`08` §6), almost all targets are 0. Teacher targets will also be near 0, and
every rung of the ladder converges. Per-dataset reporting prevents this from
diluting or faking an aggregate effect.

---

## 11. Corrections to v2

| v2 statement (location) | v3 ruling |
|---|---|
| T1 is "not circular" because the student "distills T1's generalisation" (`methods-v2/04` T1) | Partly right: not circular. But on training queries, in-sample targets approach the labels (§4), and the gain over a regularised student is unproven. **Cross-fit, and test against C\*.** |
| α = 1 at fixed hyperparameters is the non-distilled control (`methods-v2/03` KD-5, `12` E1) | **Insufficient.** Replaced by C\* + S3-SD (§9). |
| Primary formulation KD-3 (utility regression) as KD-5 hybrid (`methods-v2/03` §4) | **Retained in substance**, now per *model* (not per action, `01`), with BCE on probabilities and the mixed-target view (§3.2). |
| KD-1 softmax utility vector (`methods-v2/03` §2) | `[REJECT]` as primary: it couples models, and its dark-knowledge rationale does not hold for independent heads (§3.1). |
| KD temperature `T` and calibration temperature kept separate (`methods-v2/03` O-KD4) | Right in principle. v3 removes the free KD `T` from the primary condition by distilling a calibrated, untempered teacher (§3.2, §7.1). |
| Calibration under KD as standalone novelty lane N2 (`methods-v2/11`) | `[REJECT]` as a contribution. Measured in E4 against C\* + post-hoc calibration (§7.3). |
| Hidden-state router only as a baseline | It is now also a candidate **privileged teacher** (T-PI, §2.4). |

---

## 12. Manuscript wording

**Allowed (before E1):**

* "We investigate whether distilling a larger router's calibrated utility
  estimates \cite{hinton2015distilling} improves a compact encoder router over
  a tuned non-distilled student with label smoothing \cite{muller2019when} and
  post-hoc calibration \cite{guo2017calibration}."
* "Teacher targets are produced out-of-fold so that the teacher's predictions on
  a query never come from a model trained on that query."
* "Because larger teachers are not necessarily better teachers
  \cite{cho2019efficacy}, teacher size is treated as an experimental factor."

**Allowed only after E1 supports it:** "Distillation improves routing utility at
equal student cost by X ± Y" (with the C\* comparison stated).

**Disallowed `[REJECT]`:** "the teacher transfers dark knowledge about
inter-model similarity"; "KD improves calibration" without the post-hoc
control; "KD is necessary for edge deployment"; any wording implying the
teacher has information beyond the labels, unless the condition is S3-PI or S3-U.

BibTeX keys above are **proposed** (`guo2017calibration`, `muller2019when`,
`cho2019efficacy`, `hinton2015distilling`). They become valid only once entered
with verified metadata in `method-references-v3.bib` / `17`.

---

## 13. Sources read for this file

Body text was retrieved on 2026-10-04 from ar5iv (arXiv-derived HTML) or
arxiv.org/html, converted to plain text, and the named sections were read.
"Venue" comes from the arXiv comments/journal-ref field (author-supplied) unless
stated otherwise. `17` must confirm proceedings metadata before BibTeX entry.

| Source | Identity | Venue (as verified) | Sections read | Tag | Load-bearing use here |
|---|---|---|---|---|---|
| On Calibration of Modern Neural Networks | Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger; arXiv 1706.04599 | ICML 2017 (arXiv comments) | Abstract, §2 (ECE), §3 (capacity, NLL overfitting), §4.1 (binary/Platt), §4.2 (temperature scaling; argmax unchanged) | `[VERIFIED-BODY]` | §7.1, §7.3 |
| When Does Label Smoothing Help? | Rafael Müller, Simon Kornblith, Geoffrey Hinton; arXiv 1906.02629 | NeurIPS 2019 (arXiv comments) | Abstract, §3 (calibration: LS ≈ temperature scaling for ECE), §4 (LS teachers make worse students; "erased" information), §6 (interpolation-regime bullet) | `[VERIFIED-BODY]`; numbers `[AUTHOR-CLAIM]` | §4, §7.3 |
| Does Knowledge Distillation Really Work? | Samuel Stanton, Pavel Izmailov, Polina Kirichenko, Alexander A. Alemi, Andrew Gordon Wilson; arXiv 2106.05945 | NeurIPS 2021 (arXiv comments) | Abstract, §1, section list §3–§7; §1 claims on self-distillation and large-teacher fidelity | `[VERIFIED-BODY]` for the abstract/§1 statements used; §4–§6 detail not relied on | §2.2 M3, §5 T-ENS, §10 fidelity |
| Born Again Neural Networks | Tommaso Furlanello, Zachary C. Lipton, Michael Tschannen, Laurent Itti, Anima Anandkumar; arXiv 1805.04770 | ICML 2018 (arXiv comments) | Abstract, §3.2 (dark-knowledge vs confidence-weighting gradient decomposition) | `[VERIFIED-BODY]`; results `[AUTHOR-CLAIM]` | §2.2 M3, §3.1, §8 |
| A statistical perspective on distillation (arXiv title: "Why distillation helps: a statistical perspective") | Aditya Krishna Menon, Ankit Singh Rawat, Sashank J. Reddi, Seungyeon Kim, Sanjiv Kumar; arXiv 2005.10419 | **ICML 2021, PMLR 139:7632–7642** (verified on the PMLR page `proceedings.mlr.press/v139/menon21a.html`) | arXiv version: abstract, §1 contributions, §3 (Bayes teacher; §3.2 bias–variance trade-off) | `[VERIFIED-BODY]` (**arXiv version**; the PMLR text was not compared) | §2.2 M1, §7.1 |
| Revisiting Knowledge Distillation via Label Smoothing Regularization | Li Yuan, Francis E. H. Tay, Guilin Li, Tao Wang, Jiashi Feng; arXiv 1909.11723 | CVPR 2020 (arXiv journal-ref) | Abstract, §2.1–2.2, §3, §4 headings | `[VERIFIED-BODY]` for the abstract claims used; results `[AUTHOR-CLAIM]` | §2.2 M2 |
| On the Efficacy of Knowledge Distillation | Jang Hyun Cho, Bharath Hariharan; arXiv 1910.01348 | ICCV 2019 (arXiv journal-ref) | Abstract, §5.2 (capacity), §5.3, early-stopping claim | `[VERIFIED-BODY]`; results `[AUTHOR-CLAIM]` | §2.3 |
| Unifying distillation and privileged information | David Lopez-Paz, Léon Bottou, Bernhard Schölkopf, Vladimir Vapnik; arXiv 1511.03643 | ICLR 2016 (arXiv journal-ref) | §2, §4 (generalized distillation procedure), §4.1 | `[VERIFIED-BODY]` | §2.4 T-PI |
| Distilling the Knowledge in a Neural Network | Hinton, Vinyals, Dean; arXiv 1503.02531 | NIPS 2014 Deep Learning Workshop | per `04` §6 | `[VERIFIED-BODY]` (via `04`) | §2.2 M4, §3.1, §3.2 |
| Prefill-activation router; ConsRoute; Hybrid LLM | see `05` §1.5, §1.6, §1.8 | see `05` | per `05` | `[VERIFIED-BODY]` (via `05`) | §2.4, §2.2 M1 |

**Scope limits.** (1) Every source above is outside routing, so transfer to
routers is untested and is what E1 measures. (2) Stanton et al. was used only
for its abstract/§1 claims. Its detailed experimental sections were not
analysed. (3) No search was made for papers applying KD to LLM routers. Any
absence claim belongs to `12`, with bounded-search evidence, and `04` §4
already forbids "no router uses distillation".

---

## 14. Open items

| ID | Item | Owner |
|---|---|---|
| O-F1 | Is an unlabelled query pool available (size, domain match) for S3-U / ST? | `10`, `13` |
| O-F2 | Can SLM prefill activations be extracted for T-PI on the chosen edge SLM (open weights, hooks)? | `10`, `14` (Henry, if the SLM runs in his stack) |
| O-F3 | Is S1-MS affordable (k runs per `(q,M)`) for at least one dataset? If so it enters C\*. | `13` |
| O-F4 | Minimum detectable effect from C\* seed variance (needs a pilot run) | `13` |
| O-F5 | Fold count F and teacher-calibration split size (pilot) | `13` |
| O-F6 | Advisor: is a negative KD result acceptable as a reported finding in the conference paper? | advisor (FINAL-SUMMARY Q24) |
