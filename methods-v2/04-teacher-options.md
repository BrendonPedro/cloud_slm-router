# methods-v2 / 04 — Teacher design options for distilling the micro-encoder router

*Deliverable for `MICROENCODER_KD_BRIEF.md` §7 (teacher design investigation).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 5).*

## 0. Purpose, grounding, and sourcing

The advisor approved a micro-encoder router and asked whether **knowledge
distillation (KD)** can further optimize it (`00-meeting-decisions-lock.md`,
CONFIRMED #1, #7). Deliverable `03-kd-formulations.md` recommended **KD-3
utility-regression distillation, trained as KD-5 (hybrid hard-label +
soft-teacher)**, and explicitly deferred the teacher choice here while flagging
the single sharpest threat to the whole KD story:

> *If the strongest "teacher" is the observed-outcome oracle, there is no larger
> model to distill from — the method is ordinary supervised regression, not
> distillation.* (`03` §4, §5 O-KD2)

Brief §7 forbids the lazy default ("just use a big LLM as teacher") and requires
each candidate teacher T1–T6 to be evaluated on: what it sees; what it predicts;
what supervision it needs; whether it **leaks evaluation information**; whether
it is **reproducible**; whether it creates **circular labels**; whether
**licensing/terms permit distillation**; whether it is needed **only during
training**; and expected **compute**. The non-negotiable constraint from the
brief and `00`: **the deployed system must stay lightweight AT INFERENCE** — so
every teacher below is a *training-only* component by construction, and any
teacher that must run at inference is disqualified as a teacher (it would instead
*be* the router).

**Reuse, not re-research.** The KD families and the one real router-KD precedent
(RouteLLM's GPT-4-judge→BERT label augmentation) are primary-checked in
`02-kd-prior-art.md`; the supervision targets A–F and the labelling campaign are
in v1 `methods/06-label-and-training-design.md`; the forbidden-teacher constraint
(the lab's TypeSafe/"Jev" System-One judge API) is primary-checked in
`research/jev-system-one.md` (MCA §2.3(b)). No new web search was required for
this deliverable; the one `[OPEN]` licensing item (which *open* judge/teacher
models permit distillation) is flagged for `17`, not guessed.

**Evidence tags** (from `00` / `02` §0): `[VERIFIED]` primary source supports;
`[RELATED]` adjacent prior work; `[PROPOSED]` our design idea; `[OPEN]` requires
experiment/advisor/licensing confirmation; `[ext]` established external
literature named but not re-opened (re-verify in `17`); `[O]` our analysis;
`[S:…]` sourced to a cited prior deliverable.

---

## 1. What the teacher must emit (so the options are comparable)

From `03` §1, KD is applied **only** to the student's query-conditioned utility
head `Û_θ(a|q)`; `λ` and the measured cost `C(a|s)` stay at run time and outside
the student weights. The recommended formulation is **KD-3**, so the teacher's
job is to emit a **per-action utility signal** `U_t(a|q)` for
`a ∈ 𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD}` — a real value per action (predicted
P(correct), expected judge score, or a calibrated quality estimate), **not** a
cost-aware route label (that would bake `λ`/`s` into the target and break the
advisor's decomposition, `03` §1). A teacher that only emits a top-1 route label
(cost-aware) is low-fidelity regardless of how good it is.

Two distinctions decide everything in §2:

- **Teacher vs ground truth.** A *teacher* is a model whose **predictions** we
  distill because it generalises beyond the labelled set (soft targets carry
  "dark knowledge" — inter-class similarity structure, Hinton [ext]). The
  **observed per-query outcome** of actually running action `a` is *ground
  truth*, not a teacher: regressing to it is **supervised learning**, the α=1
  hard-label branch of KD-5 (`03` §2, §4). Calling the oracle a "teacher" is the
  collapse `03` flagged. This file keeps the two strictly separate. [O]
- **Circular / leaked labels.** A teacher creates **circular labels** if its
  signal is derived from the *same* outcomes used to label/evaluate the student
  (the student then learns to imitate a relabelling of its own test signal). A
  teacher **leaks evaluation information** if it saw the held-out eval queries or
  their answers during its own construction. Both inflate measured gains and must
  be designed out, not discovered after. [O]

---

## 2. The six teacher options (brief §7)

Each is scored on the brief §7 checklist. "Training-only?" is **yes** for all
viable options by the §0 constraint; where it is *no*, that disqualifies the
candidate as a teacher.

### T1 — Larger encoder router  *(a bigger version of our own student)*

- **Sees:** the query text (same input modality as the student). [PROPOSED]
- **Predicts:** per-action utility `U_t(a|q)` from a larger encoder (e.g.
  DeBERTa-v3-large / ModernBERT-large class vs a MiniLM/DeBERTa-small student,
  `05-student-architecture`). [PROPOSED]
- **Supervision it needs:** the **same** `y(a,q)` outcome labels as the student
  (`methods/06` §3). It is trained *once* on those labels, then its softened
  utilities supervise the small student. [RELATED — this is the canonical
  "big-model→small-model" KD setup, DistilBERT/TinyBERT template, `02` §3 [ext]]
- **Eval leak:** none *if* the larger router is trained on the **same train split
  only** and never sees eval queries — identical discipline to the student. [O]
- **Reproducible:** **yes** — open backbone, open training code, deterministic
  given the label set. Strongest reproducibility of all six. [O]
- **Circular labels:** **No**, and this is the key point: T1 is trained on the
  ground-truth outcomes and then *generalises*; the student distills T1's
  **generalisation**, not the raw outcomes. The soft target `U_t(a|q)` differs
  from `y(a,q)` precisely on queries where the big model interpolates — that
  difference is what KD can add over hard labels. So T1 is the teacher that makes
  E1 a *real* test of distillation rather than a relabelling. [O]
- **Licensing:** permissive (MiniLM/DeBERTa/ModernBERT are MIT/Apache/MIT-class,
  `05`/`17`) — no distillation prohibition. [OPEN — confirm each checkpoint's
  licence in `17`] 
- **Training-only:** **yes** — the large router never runs at inference. [O]
- **Compute:** one large-encoder fine-tune on the lab GPU (`00` CONFIRMED #4);
  cheap relative to any LLM teacher. [O]
- **Verdict:** **[PROPOSED] primary teacher.** It is the *only* option that is
  simultaneously (a) a genuinely larger model (so distillation is not a
  relabelling), (b) fully reproducible and openly licensed, (c) training-only,
  and (d) emits exactly the KD-3 per-action utility target. [O]

### T2 — Generative LLM router  *(prompt an LLM to output the route/utility)*

- **Sees:** the query text (+ a routing prompt / model-pool description). [RELATED]
- **Predicts:** a route or per-action rating in natural language / structured
  output (Arch-Router–style generative routing, `01` §Arch-Router [abs]). [RELATED]
- **Supervision:** none to *train* the teacher (it is prompted), but its outputs
  must be parsed into `U_t(a|q)`; quality depends on prompt + model. [O]
- **Eval leak:** **risk** — a general LLM may have memorised the public benchmark
  answers used to build the eval set (contamination), inflating its utility
  estimates on exactly those items. Must be mitigated by held-out / private eval
  or decontamination reporting. [O/OPEN]
- **Reproducible:** **weak** if the teacher is a closed hosted model (version
  drift, non-determinism); **moderate** with a pinned open-weights LLM. [O]
- **Circular labels:** moderate — if the same LLM later serves as the STRONG/CLOUD
  action *and* as the judge that produced `y(a,q)`, the utility target for the
  strong action becomes self-referential. Separate the judge model from the pool
  members. [O]
- **Licensing:** **depends on the LLM's terms.** The lab's TypeSafe/"Jev"
  System-One API is **forbidden** as a teacher — MCA §2.3(b) prohibits using its
  output "to perform model distillation [or] train a model to imitate the
  output" (`research/jev-system-one.md` J5/§170). Any *open-weights* LLM with a
  distillation-permitting licence is allowed. [VERIFIED (prohibition) / OPEN
  (which open model)]
- **Training-only:** **yes** (prompted offline to generate targets). [O]
- **Compute:** high per-label (LLM inference over the whole training set), but
  offline and one-off. [O]
- **Verdict:** **[RELATED] secondary / ablation teacher.** This is the family of
  the one real precedent (RouteLLM uses a GPT-4 *judge*, `02` §2.1), so it is the
  **most novelty-occupied** teacher and is useful mainly (i) as a label *source*
  for `y(a,q)` where benchmarks lack graded quality, and (ii) as a comparison
  teacher in E4. Not primary because of leak/reproducibility/licensing fragility. [O]

### T3 — Ensemble of model-outcome predictors  *(bagged/averaged utility heads)*

- **Sees:** the query text. [PROPOSED]
- **Predicts:** per-action utility as the **average** of an ensemble of
  independently-trained utility predictors (different seeds/backbones/folds). [RELATED]
- **Supervision:** same `y(a,q)` labels; ensemble members trained on bootstraps
  or CV folds. [O]
- **Eval leak:** none with standard train-only discipline. [O]
- **Reproducible:** yes (open, deterministic given seeds). [O]
- **Circular labels:** **No** — like T1, the ensemble mean is a *smoothed
  generalisation* of the outcomes, and crucially the **ensemble variance** across
  members gives a free **calibration/uncertainty signal** that a single model
  cannot, which maps directly onto the per-model reliability map the router wants
  (`03` §3 calibration row; v1 target F). This is the ensemble's distinctive
  contribution as a teacher. [O]
- **Licensing:** same as T1 (open). [OPEN per checkpoint]
- **Training-only:** yes. [O]
- **Compute:** N× a single router fine-tune (N members) — more than T1, still
  cheap vs an LLM teacher. [O]
- **Verdict:** **[PROPOSED] optional teacher for calibration ablation.** Best
  when the contribution leans on *calibrated* utility (novelty lane N2, `01`/`11`);
  otherwise T1 is simpler. Can be combined with T1 (large-encoder ensemble). [O]

### T4 — Oracle constructed from actual per-query model outcomes  *(THE collapse)*

- **Sees:** the realised outcome of running **every** action on the query
  (requires executing the whole pool per query). [O]
- **Predicts:** nothing — it *is* `y(a,q)`, the observed utility. [O]
- **Supervision:** it is the supervision. [O]
- **Eval leak / circular:** **this is the collapse `03` flagged.** Regressing the
  student onto the oracle is **supervised learning on ground truth**, i.e. KD-5
  with **α=1** — the *non-distilled baseline*, not a teacher (`03` §2 KD-5, §4).
  Worse, if the "oracle" is built from outcomes that *overlap the eval set*, it
  leaks the test labels directly. [O]
- **Reproducible:** yes (it is just the labelled data). [O]
- **Licensing / training-only / compute:** labels are expensive to collect
  (run K actions × N queries, `methods/06` §3) but that cost is incurred anyway
  for `y(a,q)`. [O]
- **Verdict:** **[VERIFIED-by-definition] NOT a teacher — it is the hard-label
  branch / E1 control.** Naming it the "teacher" is the category error that would
  make the whole KD contribution vacuous ("we distilled the labels into a model"
  = we trained a model). It must appear in the paper as the **α=1 baseline that KD
  must beat**, never as the distillation source. Resolving this is the stop-gate
  `03`/`11` demanded. [O]  **← oracle-vs-teacher collapse resolved here.**

### T5 — Strong model / judge-generated utility labels  *(LLM-as-judge grades quality)*

- **Sees:** the query **and** each action's generated answer; emits a graded
  quality score per answer. [RELATED]
- **Predicts:** `y(a,q)` *scores* (a **label source**), which can then be used
  either as hard labels or to train a T1/T3 teacher. [RELATED]
- **Eval leak / circular:** the judge must **not** be a member of the routed pool,
  else the strong-action utility is self-graded (circular). Contamination risk as
  in T2. [O]
- **Reproducible:** moderate (pinned open judge) to weak (closed). [O]
- **Licensing:** **same hard constraint as T2** — the TypeSafe/Jev judge is
  forbidden for distillation (MCA §2.3(b), `research/jev-system-one.md` J5); an
  open judge with a permissive licence is allowed. [VERIFIED / OPEN]
- **Training-only:** yes (offline grading). [O]
- **Compute:** high (judge inference over all action outputs), offline, one-off. [O]
- **Verdict:** **[RELATED] a label *source*, not the distillation teacher.** T5 is
  how `y(a,q)` is *created* when benchmarks lack graded quality (`methods/06` §3,
  target "judge score"); the distillation teacher that then generalises those
  labels is T1/T3. Conflating "the judge that makes labels" with "the teacher we
  distill" re-introduces the T4 collapse one level up — avoid it. [O]

### T6 — Existing released router used as teacher  *(distill a public router)*

- **Sees / predicts:** whatever the released router exposes (e.g. RouteLLM's
  released BERT/MF classifiers emit an edge-vs-strong preference; `01`/`02`). [VERIFIED]
- **Supervision:** none (reuse released weights); but its **action set and pool
  are fixed to that paper's**, which do **not** include a Split-LLM action or our
  pool — so its utilities don't cover `𝒜` (`03` §3 Split row). [O]
- **Eval leak:** inherited and **unknown** — we cannot audit what the released
  router trained on relative to our eval. [O/OPEN]
- **Reproducible:** yes (weights are public). [O]
- **Circular / novelty:** distilling RouteLLM would make our router a *compression
  of RouteLLM*, maximally occupying the one precedent's territory — the worst
  possible novelty position (`02` §2.1, `11`). [O]
- **Licensing:** per released-model licence (RouteLLM is open, Apache-class
  [OPEN — confirm in `17`]). [OPEN]
- **Training-only:** yes. [O]
- **Verdict:** **[RELATED] baseline/ablation only, never the primary teacher.**
  Useful as an external comparison or to *initialise* features, but its fixed
  action set cannot supervise the Split action and distilling it forfeits novelty. [O]

---

## 3. Comparison matrix (brief §7 checklist)

Ratings `[O]` unless a cell cites a source. `+` favourable, `~` moderate,
`−` unfavourable/disqualifying.

| Criterion (brief §7) | T1 larger encoder | T2 generative LLM | T3 ensemble | T4 outcome oracle | T5 judge labels | T6 released router |
|---|---|---|---|---|---|---|
| Emits per-action utility (KD-3)? | **+** | ~ (parse) | **+** | n/a (is labels) | ~ (is labels) | − (no Split action) |
| Genuinely larger than student? | **+** | + | + (ensemble) | **− (it IS the labels)** | + | ~ (similar size) |
| Eval-leak safe? | **+** (train-split only) | ~ (contamination) | **+** | − (if overlaps eval) | ~ | − (unknown) |
| Reproducible? | **+** | ~/− (drift) | **+** | + | ~ | + |
| Avoids circular labels? | **+** | ~ (judge∈pool) | **+** | **− (collapse)** | ~ (judge∈pool) | − (compress precedent) |
| Licensing permits distillation? | + [OPEN] | **− if Jev** [V] / + if open | + | + | **− if Jev** [V] / + if open | + [OPEN] |
| Training-only (lightweight inference)? | **+** | + | + | + | + | + |
| Compute cost (offline, one-off) | + (1 fine-tune) | − (LLM×N) | ~ (N fine-tunes) | ~ (run pool) | − (judge×N) | **+** (reuse weights) |
| Novelty position | + (unoccupied) | − (RouteLLM family) | + | n/a | − (RouteLLM family) | **− (compress precedent)** |

---

## 4. Recommendation (brief §7)

**[PROPOSED] Primary teacher: T1 — a larger encoder router of the same input
modality**, trained on the identical train-split `y(a,q)` labels and emitting
softened per-action utilities `U_t(a|q)` for the student to regress (KD-3). It is
the only candidate that is at once a *genuinely larger model* (so distillation is
not a relabelling of the oracle), fully reproducible, openly licensed,
training-only, and natively producing the KD-3 target. [O]

**[PROPOSED] Optional calibration teacher: T3 (ensemble)** — layer on when the
contribution leans on *calibrated* utility (N2), using ensemble variance as the
reliability signal; combinable with T1 as a large-encoder ensemble. [O]

**Label source (distinct from teacher): T5 / T2** — an **open-weights** judge or
generative model may *create* `y(a,q)` graded quality where benchmarks lack it,
feeding both the hard-label branch and T1's training. This is a *label-generation*
role, not the distillation teacher, and must use a licence that permits
distillation — **the lab's TypeSafe/Jev System-One judge is excluded** (MCA
§2.3(b), `research/jev-system-one.md` J5). [VERIFIED (exclusion) / OPEN (which
open judge)]

**Explicitly rejected as teachers:**
- **T4 outcome oracle** — it *is* the ground-truth label; using it as the
  "teacher" collapses KD into supervised regression. It is the **α=1 E1 control
  KD must beat**, not a teacher. [O] **(oracle-vs-teacher collapse resolved.)**
- **T6 released router (e.g. RouteLLM)** — distilling it compresses the one
  precedent and forfeits novelty; its fixed action set cannot supervise the Split
  action. Keep as a baseline/comparison only. [O]

**The teacher is only justified if E1 shows T1's soft utilities beat the T4=α=1
hard-label control at matched student size/latency.** If E1 shows no gain, the
brief-sanctioned conclusion (stop-condition #4) is **"KD adds no sufficient value
here"** and T1 is dropped — the paper then reports a *well-engineered supervised
micro-encoder*, with KD as a negative result. This file therefore *proposes* T1
but does **not** assert the teacher helps; that is falsifiable in E1. [OPEN]

---

## 5. Open questions and hand-off

Carried as `[OPEN]` for advisor/experiment/licensing, not guessed:

- **O-T1.** Which *open* judge/generative model (if any) is used as a label
  source, and does its licence permit distillation? Jev is excluded; the positive
  choice is unresolved. → `17`, advisor (`16`).
- **O-T2.** Does T1's soft utility beat the T4 hard-label (α=1) control at matched
  student size? This is E1 and decides whether any teacher survives. → `12`.
- **O-T3.** Pool regime (nested Llama-3.1-8B vs complementary Qwen3-8B, `03` §5
  O-KD3 / `10`) changes how much a teacher can add — on a nested pool the utility
  target may collapse to "edge-sufficiency detection", shrinking KD headroom. → `10`.
- **O-T4.** Must the eval set be private/decontaminated if any LLM teacher/judge
  (T2/T5) is used? → `12`, `16`.

**Hand-off:**
- **→ `05-student-architecture`:** fix the T1 teacher↔student size gap (large vs
  small encoder) so the distillation is non-trivial; confirm open licences.
- **→ `06-proposed-method`:** adopt T1 as the KD-3 teacher; write the training
  algorithm with the α hybrid (KD-5) and the explicit note that α=1 = supervised
  (no teacher).
- **→ `07-training-labels`:** T5/T2 are the *label-source* row for `y(a,q)`; T1 is
  trained on those labels, not on the judge directly.
- **→ `11-novelty-stress-test`:** the teacher choice is **not** a novelty source
  (T1 big→small KD is textbook); argue residual novelty only on target+deployment
  (N3/N4/N6) and make the T4-is-not-a-teacher point explicit so reviewers cannot
  read the method as "regressed the oracle".
- **→ `12-conference-experiment-plan`:** E1 = KD-5 α-sweep with **α=1 ≡ T4 oracle
  hard-label control**; E4 = teacher (T1) vs student on quality/calibration/params/
  latency; design eval to be decontaminated if T2/T5 used.
- **→ `17` / `method-references.bib`:** re-verify the KD teacher primaries (Hinton
  1503.02531; DistilBERT/TinyBERT/MiniLM for T1; RouteLLM for T6) and the Jev MCA
  clause before any are load-bearing.
