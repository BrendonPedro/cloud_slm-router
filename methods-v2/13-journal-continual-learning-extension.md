# 13 — Journal-Extension Track: Continual Learning for the Distilled Micro-Encoder Router

Brief §18. This deliverable is the **journal-extension plan only**. Continual
learning (CL) is explicitly **NOT** part of the conference core (advisor
decision #8 in [00-meeting-decisions-lock.md](00-meeting-decisions-lock.md);
brief §0, §18, §26). Nothing here may be silently folded back into
[06-proposed-method.md](06-proposed-method.md) or
[12-conference-experiment-plan.md](12-conference-experiment-plan.md).

Evidence tags per brief §23: `[VERIFIED]` primary source inspected,
`[RELATED]` adjacent prior work, `[PROPOSED]` our design idea, `[OPEN]`
needs experiment/advisor confirmation.

---

## 0. Scope boundary (what makes this a *separate* paper, not creep)

The conference paper (brief §16, deliverable 06) trains the student **once**,
on a **fixed** model pool, with a **fixed** teacher, and then freezes it:
inference is one encoder pass, teacher discarded. The decoupled runtime rule
Eq.(4) `R(q,s)=argmax_a[Û_θ(a|q) − λ·C(a|s)]` is static in θ; only `C(a|s)`
moves, and it moves because it is **measured**, not learned.

The journal extension asks the question the conference paper deliberately does
not: **what happens to θ after deployment when the world the student was
trained on changes?** That is a different contribution, a different experiment
set, and a different threat model. Keeping it separate protects the conference
paper's falsifiability (E1 must still be able to kill KD) and gives the journal
version a genuine delta rather than a re-run with one more baseline.

---

## 1. Motivation — the four non-stationarities (brief §18 research questions)

The conference router is trained against four implicit stationarity
assumptions. Each failure mode is a CL research question:

| # | Non-stationarity | What breaks | Which part of the system | Learned or measured? |
|---|---|---|---|---|
| D1 | **Edge SLM is swapped/upgraded** (e.g. new quantization, new checkpoint) | `y(EDGE,q)` labels are now stale → `Û_θ(EDGE\|q)` mispredicts | student head for EDGE | **learned** (needs CL) |
| D2 | **A new strong/remote model is added** to the pool | no head exists for the new action; `𝒜` grew | student output heads | **learned** (needs CL) |
| D3 | **Query domain shifts** (new task mix at the edge) | `Û_θ(a\|q)` extrapolates off its training distribution | student encoder + heads | **learned** (needs CL) |
| D4 | **System/network conditions drift** (new link, new hardware, new contention regime) | `C(a\|s)` changes | runtime cost table / `g_φ` | **measured** (NO CL) |

The single most important observation for this whole track, and the cleanest
dependency on the conference architecture:

> **D4 needs no continual learning at all.** [PROPOSED] Because
> [08-system-cost-integration.md](08-system-cost-integration.md) placed the
> cost term **outside** θ, any change in bandwidth/RTT/contention/activation
> bytes is absorbed by re-measuring `C(a|s)` at runtime — no retraining, no
> forgetting, no replay. The *system-drift* robustness that other routers would
> need CL for, our conference design already gets for free. The journal paper's
> CL contribution is therefore scoped **only** to the three *learned*
> non-stationarities D1–D3, which is a sharper and more honest claim than
> "continual router."

This is the connective tissue to the conference core: the decoupling that
earned novelty lane N3 also **shrinks the CL problem** to Û-only.

---

## 2. CL method options — primary-source checked (brief §18)

The brief lists eight candidate mechanisms. They collapse into four established
families (each primary-checked below) plus three that are our adaptations of
the conference machinery. No method is claimed novel on its own — CL families
are as mature as the KD families were in
[02-kd-prior-art.md](02-kd-prior-art.md).

### 2.1 Regularization-based CL — `[VERIFIED]`

**Elastic Weight Consolidation (EWC).** Kirkpatrick, Pascanu, Rabinowitz,
Veness, Desjardins, Rusu, Milan, Quan, Ramalho, Grabska-Barwinska, Hassabis,
Clopath, Kumaran, Hadsell. *Overcoming catastrophic forgetting in neural
networks.* PNAS 114(13):3521–3526, 2017. DOI
[10.1073/pnas.1611835114](https://www.pnas.org/doi/10.1073/pnas.1611835114).
Adds a quadratic penalty `Σ_i (F_i/2)(θ_i − θ*_i)²` anchoring important weights
(Fisher-information-weighted) to their post-previous-task values. No stored
data. **Fit for us:** cheap, data-free — attractive when D1–D3 updates cannot
store old queries for privacy reasons. **Risk:** Fisher estimation on a
~150M-param encoder; known to underperform replay under the single-pass
protocol (see 2.2). Caveat: a follow-up (Huszár, PNAS 2018,
[10.1073/pnas.1717042115](https://www.pnas.org/doi/10.1073/pnas.1717042115))
corrected the multi-penalty formulation — cite the correction if EWC is used.

### 2.2 Replay / rehearsal — `[VERIFIED]`

**Gradient Episodic Memory (GEM).** Lopez-Paz, Ranzato. *Gradient Episodic
Memory for Continual Learning.* NeurIPS 2017, arXiv
[1706.08840](https://arxiv.org/abs/1706.08840). Stores a per-task episodic
buffer; projects the current gradient so losses on stored memories do not
increase (inequality-constrained QP). **A-GEM** (Chaudhry, Ranzato, Rohrbach,
Elhoseiny, *Efficient Lifelong Learning with A-GEM*, ICLR 2019, arXiv
[1812.00420](https://arxiv.org/abs/1812.00420)) relaxes the QP to a single
averaged constraint — far cheaper, the realistic variant for us.

**Experience Replay (ER) with reservoir sampling.** Chaudhry, Rohrbach,
Elhoseiny, Ajanthan, Dokania, Torr, Ranzato. *On Tiny Episodic Memories in
Continual Learning.* arXiv [1902.10486](https://arxiv.org/abs/1902.10486),
2019. Reservoir-sample a tiny buffer; interleave stored and new examples.
Finding we rely on: **ER with a very small memory beats regularization (EWC)
under the single-pass protocol.** **Fit for us:** our training examples are
`(q, a, y(a,q))` tuples — tiny, text + a few scalars — so a reservoir buffer of
old queries is cheap to keep and replay. This is the **recommended default
mechanism** for D1/D3. **Risk:** buffer may hold privacy-sensitive edge
queries → interacts with the same deployment constraint that motivated the
Jev/TypeSafe exclusion in [04-teacher-options.md](04-teacher-options.md); flag
`[OPEN]`.

### 2.3 Distillation-based CL — `[VERIFIED]`

**Learning without Forgetting (LwF).** Li, Hoiem. *Learning without
Forgetting.* ECCV 2016, pp. 614–629, arXiv
[1606.09282](https://arxiv.org/abs/1606.09282); extended in IEEE TPAMI
40(12):2935–2947, 2018, DOI
[10.1109/TPAMI.2017.2773081](https://doi.org/10.1109/TPAMI.2017.2773081). Code:
[github.com/lizhitwo/LearningWithoutForgetting](https://github.com/lizhitwo/LearningWithoutForgetting).
Mechanism: before updating on new data, record the **old model's outputs** on
the new inputs and add a distillation loss keeping the updated model close to
those outputs — i.e. the previous student snapshot is its own teacher. **This
is the pivotal dependency on the conference core:** the KD-5 training machinery
from [03-kd-formulations.md](03-kd-formulations.md) (soft-target regression on
`Û`) is *already* LwF's loss shape. "Online distillation / teacher-student
refresh" from the brief's list is **LwF applied to our utility heads**, not a
new mechanism. `[PROPOSED]` the self-distillation CL update:
`L_CL = L_task(new) + β·Σ_a ||Û_θ(a|q) − Û_θold(a|q)||²` over replayed/new q.

### 2.4 Adapter / parameter-isolation CL — `[VERIFIED]`

**Adapters.** Houlsby, Giurgiu, Jastrzebski, Morrone, de Laroussilhe,
Gesmundo, Attariyan, Gelly. *Parameter-Efficient Transfer Learning for NLP.*
ICML 2019, arXiv [1902.00751](https://arxiv.org/abs/1902.00751). Code:
[github.com/google-research/adapter-bert](https://github.com/google-research/adapter-bert).
Insert small bottleneck modules (~3.6% params/task), freeze the backbone.
**Fit for us (D2 especially):** adding a new strong model = freeze the shared
ModernBERT encoder, add a new utility head + a small adapter, train only those
→ zero forgetting on existing actions **by construction**. This is the
cleanest match for the "new model added to the pool" case because our output
is already N parallel per-action heads (06 §2) — growth is additive. `[OPEN]`
whether a per-action adapter is needed or a bare new head suffices (ablation).

### 2.5 Continual calibration — `[RELATED]` / `[PROPOSED]`

The conference novelty lane N2 ([11-novelty-stress-test.md](11-novelty-stress-test.md))
is **calibration preserved through distillation** (ECE/Brier). Its continual
analogue — *keeping Û calibrated as the pool/domain drifts* — has no single
canonical primary source in the routing setting; post-hoc temperature scaling
(Guo et al., ICML 2017, arXiv [1706.04599](https://arxiv.org/abs/1706.04599),
already in [07-training-labels.md](07-training-labels.md)) is the obvious
recalibration knob. `[PROPOSED]` **continual recalibration**: re-fit the
temperature on a small recent validation stream after each update — cheap,
scalar, and a natural journal-only measurement (does CL degrade calibration
faster than accuracy?).

### 2.6 Model-profile updates — `[PROPOSED]` (and the honest non-contribution)

"Model-profile updates" in the brief's list largely means **D4** — updating the
measured cost/latency/byte profile of each action. Per §1 this is **not CL**:
it is re-measurement of `C(a|s)`. Stating this explicitly in the journal paper
prevents overclaiming a learning result where there is only a table refresh.

---

## 3. Mapping the brief's eight mechanisms → four decisions

| Brief §18 mechanism | Established family | Our verdict |
|---|---|---|
| replay buffers / rehearsal | ER, GEM/A-GEM `[VERIFIED]` | **primary** for D1/D3 |
| regularization-based CL | EWC `[VERIFIED]` | fallback / privacy-constrained ablation |
| adapter-based updates | Houlsby adapters `[VERIFIED]` | **primary** for D2 (pool growth) |
| online distillation | LwF `[VERIFIED]` | reuse of conference KD-5 loss |
| teacher–student refresh | LwF self-distill `[VERIFIED]`+`[PROPOSED]` | periodic teacher re-distillation |
| continual calibration | temperature scaling `[RELATED]`+`[PROPOSED]` | journal-only measurement |
| model-profile updates | — | **not CL** (D4 re-measurement) |
| (rehearsal variant above) | — | — |

Net: the journal method is **ER (D1/D3) + additive adapters/heads (D2) +
LwF-style self-distillation to anchor old actions + continual temperature
recalibration**, with EWC as a data-free ablation. Every component is
`[VERIFIED]` prior art; the contribution is their composition for a
*utility-aware edge/Split router* (§4), not the mechanisms.

---

## 4. Additional contribution beyond the conference version (brief §18)

The conference paper cannot claim any of these; they are the journal delta:

- **JC1** `[PROPOSED]/[OPEN]` CL confined to Û because cost is decoupled —
  a *router that adapts to pool/domain change without retraining the cost
  model*. Demonstrating D4 needs zero learning is itself a result.
- **JC2** `[PROPOSED]/[OPEN]` **Calibration-aware continual routing**: does the
  N2 calibration advantage of the distilled student *survive* sequential
  updates, or does forgetting hit calibration before accuracy? No prior CL work
  measures ECE-under-forgetting for a router.
- **JC3** `[PROPOSED]/[OPEN]` **Additive pool growth (D2)** via new head+adapter
  with frozen encoder — adding a model to the routable set at O(one head) cost,
  quantified against full retraining.
- **JC4** `[PROPOSED]/[OPEN]` The teacher is **training-only** in the conference
  design but becomes a **periodic refresh oracle** in the journal design — a
  clean reuse that no conference claim depends on.

No measured numbers. All `[OPEN]` until the journal experiments run.

---

## 5. Additional experiments (journal-only; do NOT run this sprint)

Pre-registered in the brief §17 style, disjoint from conference E1–E8:

| ID | Hypothesis | IV | DV | Baseline | Success | Falsification |
|---|---|---|---|---|---|---|
| **J1** (D1) | ER keeps EDGE-head accuracy after the edge SLM is swapped | update method ∈ {none, EWC, ER, LwF} | post-swap accuracy + backward transfer | naive fine-tune (forgets) | ER ≥ joint-retrain − ε, naive forgets | ER ≈ naive (no forgetting to prevent) |
| **J2** (D2) | adapter+new head adds a strong model with ~0 forgetting on old actions | growth method ∈ {full retrain, head-only, head+adapter} | old-action acc. retention, new-action acc., params updated | full retrain | head+adapter ≥ retrain − ε at ≪ params | adapter underperforms a bare new head |
| **J3** (D3) | router survives domain shift via ER | domain sequence | avg acc / forgetting across domains | static conference student | CL > static under shift | static ≥ CL (shift immaterial) |
| **J4** (calib) | calibration survives sequential updates (JC2) | #updates | ECE/Brier over time | hard-label CL | distilled-CL ECE stays ≤ baseline | calibration degrades ≥ accuracy |
| **J5** (D4 control) | system drift needs no learning (JC1) | network/HW regime | routing quality under drift, params updated=0 | re-trained cost model | re-measure matches retrain, 0 params | re-measurement insufficient → cost must be learned (would also wound N3) |

J5 is the sharpest: it is the experiment that **confirms the conference
decoupling**, and a negative J5 would retro-actively threaten conference lane
N3 — so it belongs in the journal, not the conference, precisely so the
conference claim is not hostage to it.

---

## 6. Dependencies on the conference architecture (brief §18)

The journal paper is a strict superset build; it cannot start before the
conference core exists:

1. **Student + heads (06 §2).** CL updates act on the exact ModernBERT-base +
   N sigmoid heads; adapters (2.4) insert into that backbone.
2. **KD-5 loss (03).** LwF self-distillation (2.3) is the same soft-target
   regression loss with `θ_old` as teacher — reused, not rebuilt.
3. **Decoupled cost (08).** JC1/J5 depend entirely on `C(a|s)` living outside θ.
4. **Label pipeline (07).** CL replay items are `(q,a,y(a,q))` tuples from the
   same construction recipe; the reservoir buffer stores these.
5. **Teacher (04).** The training-only T1 larger encoder becomes the periodic
   refresh teacher (JC4).
6. **Model pool / `𝒜` growth (10).** D2 presupposes the pool-selection criteria
   (MP1–MP8) so "add a model" is well-defined.

`[OPEN]` items inherited, do not guess: edge-SLM swap cadence, whether edge
queries may be buffered (privacy → interacts with replay 2.2), and the Henry
Split interface for any Split-action profile refresh — all remain in
[16-advisor-and-lab-open-questions.md](16-advisor-and-lab-open-questions.md).

---

## 7. Hand-offs

- **→ [14-publication-staging.md](14-publication-staging.md):** Plan A/B must
  schedule J1–J5 after (or parallel to) conference E1–E8; JC4's teacher reuse
  and the shared replay buffer are the main code-reuse items.
- **→ [11-novelty-stress-test.md](11-novelty-stress-test.md):** J5 is the
  journal-side guard on conference lane N3; JC2 extends N2 — note the
  conference claims must stand *without* these.
- **→ [17-verified-references.md](17-verified-references.md) / method-references.bib:**
  add EWC (PNAS 2017 + Huszár 2018 correction), GEM (NeurIPS 2017), A-GEM
  (ICLR 2019), ER/tiny-memories (arXiv 1902.10486), LwF (ECCV 2016 / TPAMI
  2018), Houlsby adapters (ICML 2019), Guo temperature scaling (ICML 2017) —
  all inspected at abstract level this iteration; mark primary-vs-secondary and
  "full text inspected" honestly in 17.

---

## 8. One-paragraph summary for FINAL-SUMMARY §17

Continual learning is a **journal extension, not conference core**. Because the
conference design decouples learned utility `Û_θ` from measured cost `C(a|s)`,
**system/network drift (D4) needs no learning** — only the three learned
non-stationarities remain: edge-SLM swap (D1), pool growth (D2), domain shift
(D3). The proposed CL method composes **established** mechanisms — experience
replay with a tiny reservoir buffer (ER/A-GEM) for D1/D3, additive
adapters+heads on a frozen encoder for D2, and LwF-style self-distillation
(which is literally the conference KD-5 loss with the old student as teacher) —
plus **continual temperature recalibration** to test whether the N2 calibration
advantage survives forgetting. No mechanism is novel alone; the journal
contribution is their composition for a utility-aware edge/Split router and the
measurement of calibration-under-forgetting (JC2) and learning-free
system-drift robustness (JC1/J5). No experiments were run this sprint.
