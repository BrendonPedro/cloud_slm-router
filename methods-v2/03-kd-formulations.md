# methods-v2 / 03 — Candidate knowledge-distillation formulations for the micro-encoder router

*Deliverable for `MICROENCODER_KD_BRIEF.md` §6 (required investigation C).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 4).*

## 0. Purpose, grounding, and sourcing

The advisor approved a micro-encoder as the routing backbone and asked whether
**knowledge distillation (KD)** can further optimize it (`00-meeting-decisions-lock.md`,
CONFIRMED #1, #7). Deliverable `02-kd-prior-art.md` established the governing fact
for this file: **no surveyed work distils the routing decision itself**; the only
near-precedent is RouteLLM's GPT-4-judge→BERT *label augmentation* (KD-in-all-but-name,
plain classification loss, no soft-target/temperature term), and every *mechanical*
KD ingredient (soft-target KL, encoder hidden-state KD, ranking distillation,
calibration) already exists in mature form (`02` §2, §3). This deliverable does
**not** claim any KD mechanism is novel. It does what brief §6 mandates: develop
several *technically valid* KD formulations for **our fixed f_θ**, compare them on
the brief's criteria, and — only if the evidence supports it — recommend one,
while carrying the explicit "KD may not add value → reject with evidence" branch
that brief stop-condition #4 permits.

**Reuse, not re-research.** The KD families are already primary/secondary-checked
in `02` §3 (RELATED table). The *supervision targets* these KD schemes distil
into are already enumerated and compared in the v1 sprint,
`methods/06-label-and-training-design.md` (targets A–F). This file is the
*intersection*: (KD family) × (supervision target), inheriting both prior
analyses rather than redoing them. No new web search was required.

**Evidence tags** (from `00` §Evidence discipline / `02` §0):
`[VERIFIED]` primary source directly supports; `[RELATED]` adjacent prior work,
not exact precedent; `[PROPOSED]` our design idea; `[OPEN]` requires
experiment/advisor confirmation; `[ext]` stated from well-established external
literature named but not re-opened this sprint (re-verify in `17` before
load-bearing); `[O]` our analysis; `[S:…]` sourced to a cited prior deliverable.

---

## 1. The fixed target the KD must serve (so "fidelity" is well-defined)

From `00` (unchanged manuscript Eqs.):

- Eq. (1) `R : Q → M`
- Eq. (2) `max_R  E_q[ U(R(q),q) − λ·C(R(q),q) ]`
- Eq. (3) `R(q) = argmax_{M_k ∈ M} f_θ(q, M_k)`

The advisor's confirmed decomposition (`00` CONFIRMED #2) keeps **learned
query-conditioned utility** separate from **measured live system cost**:

```
R(q, s) = argmax_{a ∈ 𝒜}  [ Û_θ(a | q)  −  λ · C(a | s) ]
          \__________/     \__________/
           distilled        measured at runtime, OUTSIDE student weights
           micro-encoder    (08-system-cost-integration)
```

with action set `𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD}` (split depth `d` makes
`a` an *action*, not only a model `M_k`; the reduction to Eq. (3) is written out
in `06-proposed-method` / brief §9). **KD is applied only to `Û_θ(a|q)`** — the
student's query-conditioned utility head. It is *not* applied to `C(a|s)`, which
is measured. This single constraint determines what "fidelity to f_θ" means for
every formulation below: **a KD scheme is high-fidelity iff the distilled target
is exactly `Û(a|q)` (or a monotone transform of it) and leaves `λ` and `s` as
run-time knobs** [O]. Formulations that bake `λ` or cost into the distilled
target are *low*-fidelity to the advisor's decomposition even if they fit Eq. (2)
literally — the same objection v1 raised against supervision targets B/E
(`methods/06` §1, §6). [S: methods/06]

---

## 2. The five formulations (brief §6)

Each maps a **KD family** (`02` §3) onto a **supervision target**
(`methods/06` §1). Notation: `z` = pre-softmax logits; `T` = KD temperature;
`y(a,q)` = observed graded quality of action `a` on query `q` (correctness or
judge score); teacher `t`, student `s`.

### KD-1 — Soft utility-vector distillation  *(Hinton soft targets → per-action utility)*

- **Teacher emits:** a probability/utility vector over the action set,
  `p_t(a|q) = softmax(z_t(·|q)/T)`.
- **Student learns:** `p_s(a|q)` toward `p_t` plus ground-truth outcome labels.
- **Candidate loss (brief §6, to be verified not assumed):**
  `L = α·L_task(p_s, y) + β·T²·KL( softmax(z_t/T) ‖ softmax(z_s/T) )`.
  This is exactly the Hinton template (`02` §3, arXiv:1503.02531 [ext]); the
  `T²` factor rescales the softened-gradient magnitude and **is** established
  [ext — re-verify in `17`]. [RELATED]
- **KD family:** foundational soft-target KD. [RELATED]
- **Maps to f_θ:** the softmaxed vector is a *distribution over actions*, not a
  calibrated per-action utility; it collapses to a **multiclass** target
  (v1 target B) once softmaxed across actions, which *couples* the actions and
  tends to **bake the training-time cost ranking into the vector** if the teacher
  already saw cost. High fidelity **only if the teacher's vector is pure
  query-utility** (no cost), otherwise medium. [O]

### KD-2 — Pairwise / ranking distillation  *(teacher preference → route ordering)*

- **Teacher emits:** relative preference `M_i ≻ M_j | q` (or a full ordering).
- **Student learns:** route *ordering*, not only the top-1 class.
- **Loss:** ranking/margin loss on teacher preferences, optionally + ground-truth
  pairwise outcomes (PLaD/PAD ranking-KD template, `02` §3, arXiv:2406.02886 /
  2502.14272 [abs]; Ranking Distillation KDD-2018 [ext]). [RELATED]
- **KD family:** ranking/preference KD. This is also the family **closest to the
  one real router precedent** — RouteLLM distils GPT-4 *pairwise preferences*
  into a classifier (`02` §2.1), so KD-2 is the formulation whose novelty is
  **most occupied** and must be argued hardest in `11`. [VERIFIED precedent]
- **Maps to f_θ:** maps to v1 target **D (pairwise gain ΔU)**; natural for the
  manuscript's core **edge-vs-strong** decision, but `O(K²)` heads for a K-way
  pool and does not natively express a continuous split-depth action set
  (`methods/06` §1.D). Medium fidelity. [S: methods/06]

### KD-3 — Utility-regression distillation  *(teacher per-model utility → student regression)*

- **Teacher emits:** per-action utility estimate `U_t(a|q)` (a real value, e.g.
  predicted P(correct) or expected judge score).
- **Student learns:** regress `Û_s(a|q) → U_t(a|q)`, optionally + observed
  `y(a,q)` (hybrid → KD-5).
- **Loss:** MSE / smooth-L1 (or BCE if utility is a probability) to teacher
  utilities; **no softmax across actions**, so actions stay **decoupled**. [RELATED]
- **KD family:** regression KD (the DistilBERT/TinyBERT hidden-/output-matching
  idea applied to a scalar utility head) [ext]. [RELATED]
- **Maps to f_θ:** maps **exactly** to v1 target **C (utility regression)** and,
  with the separated cost module, to target **F** — the two v1 recommended as
  best-fitting Eq. (2) because `λ` and `s` stay at run time and new models can be
  added by supplying a profile + small calibration set (`methods/06` §1.C/F, §6).
  **Highest fidelity to the advisor's decomposition.** [S: methods/06] [O]

### KD-4 — Representation distillation  *(teacher encoder embedding → student encoder)*

- **Teacher emits:** hidden states / pooled embeddings of a larger encoder (or
  LLM) teacher.
- **Student learns:** its encoder representation toward the teacher's (hidden-state
  MSE / attention-matrix KL / embedding MSE), then a small utility head on top.
- **Loss:** DistilBERT/TinyBERT/MiniLM template (`02` §3, arXiv:1910.01108 /
  1909.10351 / 2002.10957 [ext]). [RELATED]
- **KD family:** encoder KD — **note the student backbones themselves are already
  KD-produced** (MiniLM/DistilBERT), so KD-4 risks "distilling a distilled model";
  its marginal value over simply *using* those checkpoints is unclear (`05`). [O]
- **Maps to f_θ:** indirect — it improves the *representation*, not the utility
  target; must be *combined with* KD-1/2/3 to produce a routing decision. Fidelity
  is therefore "neutral" — it neither helps nor hurts the U−λC structure, it only
  changes the feature extractor. [O]

### KD-5 — Hybrid hard-label + soft-teacher  *(observed outcomes + teacher soft targets)*

- **Student learns from both:** actual per-query/per-model outcomes `y(a,q)`
  **and** teacher soft targets (any of KD-1/2/3's teacher signal).
- **Loss:** convex combination, e.g. `L = α·L_task(Û_s, y) + (1−α)·L_KD(Û_s, U_t)`.
  This is just the general KD objective (Hinton already combines CE + soft-KL);
  KD-5 is **not a distinct mechanism** but the **default instantiation** of KD-1
  or KD-3 with `α>0`. [RELATED]
- **Maps to f_θ:** inherits the fidelity of whichever teacher signal it hybridises
  (best with KD-3). Its importance is *empirical*: the α sweep **is** the test of
  whether the teacher adds anything over hard labels — i.e. KD-5 with α=1 (pure
  hard label) **is the non-distilled baseline** for experiment E1
  (`12-conference-experiment-plan`). This makes KD-5 the natural experimental
  frame for the whole KD question. [O]

---

## 3. Comparison matrix (brief §6 criteria)

Ratings **[O]** unless a cell cites a source. `+` favourable / low cost / low
risk, `~` moderate, `−` unfavourable / high cost / high risk — from the router's
standpoint. "Fidelity" = fidelity to the advisor's decoupled f_θ (§1).

| Criterion (brief §6) | KD-1 soft-vector | KD-2 ranking | KD-3 utility-reg | KD-4 representation | KD-5 hybrid |
|---|---|---|---|---|---|
| Fidelity to f_θ (§1) | ~ (softmax couples actions) | ~ (pairwise/O(K²)) | **+** (= target C/F) | ~ (feature only) | **+** (if over KD-3) |
| Simplicity | + | ~ | + | − (two-stage) | ~ |
| Student inference cost | + (one softmax head) | + | + (K small heads) | + (head unchanged) | + |
| Label requirements | teacher vec + y | teacher prefs + pairs | teacher U + y | teacher embeddings | both |
| Teacher requirements | path-prob teacher | preference teacher | per-action utility teacher | larger encoder/LLM | any of the above |
| Calibration | ~ (needs post-hoc per-class T) | ~ | **+** (per-model reliability map) | n/a (feature) | **+** |
| Model-pool flexibility | − (fixed softmax dim) | − (O(K²)) | **+** (profile-conditioned add) [E] | + (backbone reusable) | **+** |
| Compat. with runtime C(a|s) | ~ (risk of baking cost in vector) | ~ | **+** (cost strictly external) | + | **+** |
| Compat. with Split-LLM action | ~ (split depth as classes) | − (ordering over depths awkward) | **+** (depth = action, utility per depth) | + | **+** |
| Implementation risk | + | ~ | + | − (hidden-state alignment, dims) | ~ |
| Novelty risk (occupied?) | ~ (Hinton-generic) | **− (RouteLLM-occupied)** [VERIFIED] | ~ (utility-reg generic, but per-action+edge+Split unoccupied) | ~ | ~ |
| Reproducibility | + | ~ | + (labels reusable across λ) [S:methods/06 §3] | ~ | + |
| Edge feasibility | + | + | + | + | + |

**Cross-reading.** The matrix reproduces, at the KD layer, the exact conclusion
v1 reached at the supervision-target layer: the formulations that keep `λ` and
`s` at run time and support cheap new-model addition (**KD-3**, and **KD-5 built
on KD-3**) dominate on fidelity, cost-flexibility, Split compatibility, and
reproducibility; the ones that couple actions or bake cost (**KD-1 when the
teacher saw cost**, and anything mapping to targets B/E) are weaker on exactly
the "react to changing network state" axis that gives the paper its systems
identity (`methods/06` §6). **KD-2 is the highest-novelty-risk** because it is the
one family the single real router precedent (RouteLLM) already occupies (`02`
§2.1). [O]

---

## 4. Recommendation (brief §6 "MAY recommend one")

**[PROPOSED] Primary formulation: KD-3 utility-regression distillation, trained as
KD-5 (hybrid hard-label + soft-teacher), with an α sweep.**

Rationale, each tied to evidence:

1. **Fidelity.** KD-3's target *is* the advisor-approved `Û(a|q)` (v1 target C/F),
   so the distilled quantity and the run-time decision rule coincide; `λ` and
   `C(a|s)` stay external and measured (`00` CONFIRMED #2; `methods/06` §1.C/F). [S]
2. **It subsumes the others as ablations, not rivals.** KD-5 with α=1 is the
   non-distilled baseline (E1); KD-1 is KD-3 + a softmax; KD-2 is the pairwise
   specialisation for the edge-vs-strong sub-decision; KD-4 is an optional
   backbone-improvement that can be layered on. So *recommending KD-3/5 does not
   discard the others* — it orders them as a primary + ablation set. [O]
3. **It is the only family not already occupied by the real precedent.** RouteLLM
   occupies pairwise-preference distillation (KD-2's territory); **per-action
   calibrated utility-vector regression distilled into an edge encoder with a
   separate Split-LLM action and measured activation cost is unoccupied** (`02`
   §7; `01` novelty lanes N3/N4/N6). Novelty, if it survives `11`, lives here —
   **not** in the KD mechanism (generic) but in the *target + deployment*
   (per-action utility, edge, Split, cost-separation). **No novelty by adjective.**
   [VERIFIED by absence / O]

**[OPEN] The recommendation is conditional on experiment E1.** KD must earn its
place: the α sweep in KD-5 directly tests whether a teacher's soft utility beats
training the identical student on observed outcomes alone. If E1 shows no
calibration/accuracy gain at matched student size, the defensible conclusion is
**"KD does not add sufficient value for this router"** — which brief
stop-condition #4 explicitly permits and which `12` must be designed to be able
to report. This deliverable therefore *proposes* KD-3/5 but does **not** assert
KD works; that is falsifiable and deferred to E1. [OPEN]

**Teacher choice is deferred to `04-teacher-options`.** KD-3 needs a teacher that
emits *per-action utility*; the only *established* routing teacher is an
LLM-as-judge (RouteLLM), while a *larger router* teacher (T1) and an
*oracle-from-observed-outcomes* "teacher" (T4) are `[PROPOSED]` and in fact
T4 blurs into **pure hard-label supervision** (the oracle *is* the ground truth),
which is a subtlety `04` must resolve: *if the best "teacher" is the observed
outcome oracle, there is no distillation — it is just supervised regression.* This
is the single sharpest threat to the KD story and is handed to `04`/`11`. [O/OPEN]

---

## 5. Open questions and hand-off

Carried as `[OPEN]` for advisor/experiment, not guessed:

- **O-KD1.** Does soft-teacher utility beat hard-label regression at matched
  student size/latency? → E1 (`12`).
- **O-KD2.** Is the teacher a *larger model* (true KD) or the *observed-outcome
  oracle* (then it is supervision, not KD)? → `04`, `11`.
- **O-KD3.** On a **nested** pool (Llama-3.1-8B edge regime, `methods/06` §0) the
  utility target collapses to "detect what the edge already answers", possibly
  erasing any KD benefit; on a **complementary** pool (Qwen3-8B regime) KD may
  help more. Pool regime is unresolved (model-pool question, `10`). → `10`, `13`.
- **O-KD4.** KD temperature `T` (soft-target) vs calibration temperature
  (post-hoc) are **different** and must not be merged (`02` §3 note). → `08`.

**Hand-off:**
- **→ `04-teacher-options`:** evaluate T1–T6 specifically for emitting *per-action
  utility* (KD-3); resolve the oracle-vs-teacher collapse (§4). Exclude the Jev
  API teacher (MCA forbids, `02` §7 / `research/jev-system-one.md` §J5). [VERIFIED]
- **→ `06-proposed-method`:** adopt KD-3/KD-5 as the training core; write the
  exact loss with the §1 decoupling and the Eq. (3) reduction.
- **→ `07-training-labels`:** the reusable `y(a,q)` table (one labelling campaign,
  `methods/06` §3) serves KD-5's hard-label branch for all α; teacher targets are
  the added soft branch.
- **→ `11-novelty-stress-test`:** argue KD-3's residual novelty against RouteLLM
  (KD-2 territory) and the generic-KD baseline; downgrade any "we distil a router"
  claim to the per-action-utility + edge + Split + cost-separation combination. [O]
- **→ `12-conference-experiment-plan`:** E1 = KD-5 α-sweep (α=1 is non-distilled
  control); design it to be able to *reject* KD. [OPEN]
- **→ `17` / `method-references.bib`:** re-verify the `[ext]` KD primaries (Hinton
  1503.02531, DistilBERT/TinyBERT/MiniLM, Ranking Distillation KDD-2018) before
  any are cited as load-bearing for a loss claim.
