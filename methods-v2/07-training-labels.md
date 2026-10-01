# methods-v2 / 07 — Training labels: how the micro-encoder's supervision is constructed

*Deliverable for `MICROENCODER_KD_BRIEF.md` §10 (training labels). Prepared
2026-10-02 (gnhf microencoder-kd sprint, iteration 8).*

## 0. Purpose, grounding, and sourcing

This file fixes the **supervision signal** for the distilled micro-encoder router:
what number `f_θ` is trained to produce, the exact chain by which each label is
*constructed* from raw model outputs, and which of the brief §10 prediction targets
(A–E) is most consistent with the fixed manuscript formulation. It is the hand-off
`06 §10` requested: it defines `y(a,q)` construction feeding the KD-5 training
algorithm (`06 §5` steps 1–3) and confirms `N = |𝒜|`.

**Reuse, not re-research.** The label taxonomy and the A–F target comparison were
already developed and primary-/measurement-checked in v1
`methods/06-label-and-training-design.md` (and its upstream
`recommended-experiment` / LLMRouterBench-bundle measurements). This file is their
re-casting onto the brief §10 list and the locked KD-3/KD-5 design (`03`, `06`); it
required **no new web search**. The one genuinely new content here is the explicit
seven-way *label-provenance* chain the brief §10 demands (true observed utility →
… → final route label) and the resolution of which single target the deployed
student predicts.

**Evidence tags** (from `00`): `[VERIFIED]` primary source supports; `[RELATED]`
adjacent/canonical fact not re-opened this iteration; `[PROPOSED]` our design
choice; `[OPEN]` requires experiment/advisor/pool confirmation; `[M]` measured from
the released LLMRouterBench bundle (raw file named in the cited v1 deliverable);
`[S:NN]` sourced to prior deliverable NN.

`source/main-original.tex` is **not modified** (brief §20/§26).

---

## 1. The seven label objects, kept strictly distinct (brief §10)

The brief demands these seven be distinguished and **not blurred**. They form a
*provenance chain*: raw model execution produces (1); (1) is thresholded/scored to
(2)/(3)/(4); any of those is the **hard target** `y(a,q)`; the teacher turns `y`
into (6); and (7) is the runtime argmax output, *never a training label*.

| # | Label object | Definition | Who/what produces it | Role in our method |
|---|---|---|---|---|
| 1 | **True observed utility** | `y*(a,q)` — the realised quality of action `a`'s *actual* answer on `q` (graded correctness or judge score), observed by running `a` | offline eval harness on lab GPU (`00` #4) | the **raw substrate**; everything else is derived from it |
| 2 | **Binary correctness** | `1[a's answer is correct]` for exact-match/QA datasets | eval harness, deterministic metric | one concrete form of `y*`; the hard target when datasets are exact-match |
| 3 | **Benchmark-specific score** | the dataset's native graded metric (EM, F1, pass@1, accuracy) | dataset scorer | `y*` for graded datasets; must be pinned per-dataset |
| 4 | **Judge score** | an LLM-judge grade of `a`'s open-ended answer, in `[0,1]` | pinned judge model (T5 is a **label source, not a teacher**, `04`) | `y*` for open-ended datasets (e.g. SimpleQA uses an LLM judge [S:v1 §3]) |
| 5 | **Teacher-predicted utility** | `Û_T(a|q)` = the larger encoder router's (ModernBERT-large, T1) head output | teacher, **training-only** (`04`/`06`) | input to the **soft** KD loss; *not* ground truth |
| 6 | **Soft teacher target** | `Û_T(a|q)` used as a regression target for the student (KD-3) | derived from (5) | the `(1−α)` term in `06 §5` step 7 |
| 7 | **Final route label** | `a* = argmax_a[Û_θ(a|q) − λ·C(a|s)]` — the runtime decision | the deployed student + cost monitor at inference | an **output**, never a training label (would bake λ and `s`, re-coupling cost) |

Two provenance rules the method depends on:

- **The hard target `y(a,q)` is one of {2,3,4}, i.e. a form of (1).** It is the
  *observed-outcome oracle* T4, which `04 §4` established is **ground truth, not a
  teacher** — regressing to it is supervised learning, and it is exactly the α=1
  control that KD must beat (`06 §5`). Calling (1) a "teacher" re-introduces the
  oracle-vs-teacher collapse. `[S:04]`
- **The soft target (6) is a *function of* (5), which is fit on (1).** The teacher
  only adds information where `Û_T` generalises *beyond* the labelled `y` (soft
  targets differ from `y` on interpolated queries, `04 §6`). If `Û_T ≈ y`
  everywhere, (5)=(1) and KD is vacuous — the sharpest standing threat, tested by
  E1. `[OPEN]`

Per brief §10's explicit instruction: the illustrative "good / medium / poor"
labels that appear in slide-level discussion are **not** an experimental label
definition and are not used anywhere below. The experimental substrate is `y*(a,q)`
as constructed in §3. `[VERIFIED: brief §10]`

---

## 2. Which target does the student predict? (brief §10 A–E)

The brief asks whether the core student should predict **A** binary edge
sufficiency, **B** multiclass route, **C** per-model utility, **D** pairwise
preference, or **E** calibrated probability of success — and which is most
consistent with the original formulation.

The method (`06 §3`) already locked the **structure**: `f_θ(q,a) := Û_θ(a|q)`,
**N independent per-action sigmoid heads** (not a joint softmax). Mapping that onto
the A–E list:

- The **structure** is **C** (per-action / per-model utility — one scalar per
  action), *not* A (two-way only), *not* B (joint softmax over a fixed class set).
- The **semantics** of each scalar is **E** (a *calibrated probability of
  success*), i.e. each head outputs `P(action a succeeds on q)`, calibrated
  post-hoc (`06 §5` step 11).

So the recommended target is **C-structured, E-valued**: *per-action calibrated
probability of success*. Written explicitly:

```
Û_θ(a | q)  :=  P̂( y*(a,q) = success | q )        for each a ∈ 𝒜          (one head per action)
```

**Why this is the most consistent with the fixed formulation** (brief §10 asks for
the reason):

1. **It keeps λ and `s` at runtime (Eq. 2/4).** C/E learn only the
   query-conditioned utility; the cost `C(a|s)` and the knob λ enter *only* at the
   argmax (`06 §3.2`). Targets **B** (multiclass) and the v1 "E=direct U−λC" and
   "F" variants that bake a chosen λ or static cost into the *weights* cannot
   express the manuscript's **system-awareness / react-to-changing-network**
   requirement without relabelling+retraining [S:v1 §1, §6]. `[VERIFIED: v1 matrix]`
2. **It maps cleanly to Eq. (3).** `f_θ(q,M_k) = Û_θ(M_k|q)` is exactly the form
   brief §9 says is preferred, and `06 §2` showed the `M_k→a` extension reduces to
   Eq. (3) under split-off, λ=0. `[S:06]`
3. **It supports cheap model-pool addition (requirement #4).** Adding an action =
   adding one head on the shared representation; a joint softmax (B) would need the
   output dimension changed and the whole normalization retrained [S:v1 §1.C].
4. **It is the KD-3 target.** KD-3 utility-regression distillation (`03`) regresses
   the student's per-action utility toward the teacher's per-action utility —
   which *is* this object. Any other target would change the KD formulation. `[S:03]`
5. **Calibration is the N2 novelty lane.** Because the argmax moves an operating
   point under λ and `s`, the per-action output must be a *trustworthy* probability
   — "calibrated per-action utility preserved under distillation" is the defensible
   contribution (`11` lane N2), and that requires the **E** (calibrated-probability)
   semantics, not a bare logit. `[S:03/11]`

**Relationship to A and D (why they survive only as ablations/baselines):**

- **A — binary edge sufficiency** is the **N=2** special case of C (heads
  {EDGE, ESCALATE}). It is the **cheapest to falsify first**: Stage-0 "weak ≥
  strong" labels already exist from released LLMRouterBench scores with *no new
  inference* [M], so A answers H1 ("does a learned router beat simple baselines at
  all?") before any expensive K-model labelling [S:v1 §6]. Carried as the **first
  milestone + a baseline**, not the final target. `[PROPOSED]`
- **D — pairwise preference** (`ΔU = U(strong,q) − U(weak,q)`) is the sample-
  efficient middle option for the core edge-vs-strong decision and is the *only*
  router-KD precedent's shape (RouteLLM's GPT-4-judge preference labels, `02`). It
  is carried as an **ablation of C** (does the signed margin learn the cost-saving
  boundary more sample-efficiently on nested pools?) [S:v1 §1.D], **not** as the
  primary target, because `O(K²)` pairwise heads do not scale to the split-depth
  action set. `[PROPOSED]`
- **B — multiclass route** is retained **only as a published-style baseline** (it
  is what most prior routers do) and as the thing the decoupled C/E design is
  argued against; it is not a candidate primary target because it bakes λ. `[S:v1]`

---

## 3. Exact construction of the hard target `y(a,q)` (brief §10: "define exactly")

This is the recipe the KD-5 algorithm (`06 §5` step 1) consumes. **No totals are
fabricated** — the pool size K and query count N are `[OPEN]` until `10`/advisor fix
the pool (the manuscript's named pool has unverified model names, carried from
`00`/`01`).

```
INPUT:   query set {q_i};  action set 𝒜 (N = |𝒜|, from 10);  per-dataset metric.
OUTPUT:  y(a, q_i) ∈ [0,1]  for every (action a, query q_i)   # the hard substrate (label object #1)

for each query q_i:
  for each action a ∈ 𝒜:
    1. run a on q_i  → answer â           # one GPU inference per (a,q); label object #1 raw execution
    2. grade â:
         exact-match / QA dataset  → binary correctness (#2) or benchmark score (#3)
         open-ended dataset        → pinned-judge score (#4), judge model recorded & frozen
       → y*(a,q_i) ∈ [0,1]
    3. store y*(a,q_i) in the LLMRouterBench record format (one row per (model,query)) [S:v1 §3]
```

Three economics facts that govern the whole pipeline, carried forward verbatim from
v1 (brief §10 "how training data can be created"):

- **One labelling campaign serves every target.** From the single `y(a,q)` table:
  binary A = threshold, pairwise D = subtract, utility C = regress, calibrated E =
  post-hoc map. The number of GPU calls is set by **pool size K × query count N**,
  *not* by how many targets are compared — so the A-vs-C-vs-D ablation is nearly
  free once labels exist [S:v1 §3]. `[VERIFIED: v1 §3]`
- **Calls ≈ N·K** for QA/exact-match; **+ N·K judge calls** for open-ended. With the
  Stage-0 pool (N≈2,432, K=2) the labels **already exist for free** from released
  scores [M]; the manuscript's larger pool on SimpleQA does **not** exist in the
  bundle and is a Stage-1 GPU job [S:v1 §3]. `[M]`
- **The split actions `SPLIT(d)` need no separate quality labels.** A split is a
  *latency/communication* operating point of the *same* model, so its **utility**
  `y(SPLIT(d),q) = y(full model,q)` (the answer is mathematically the full model's
  answer); only its **cost** `C(SPLIT(d)|s)` differs and lives outside θ (`08`/`09`).
  This is why N split depths do **not** multiply the labelling cost. `[PROPOSED,
  S:09]` `[OPEN]` — must be confirmed once Henry's split interface is known (exact
  numerical equivalence can depend on quantization at the cut; `09`).

---

## 4. From hard target to soft target to calibrated output (the three-stage label flow)

```
 (1) OBSERVED        (2) SOFT TEACHER        (3) CALIBRATED STUDENT OUTPUT
     y(a,q)   ──fit──► teacher T1            student Û_θ(a|q) trained on
   [ground truth,     ModernBERT-large       α·L_task(Û_θ,y) + (1−α)·L_KD(Û_θ,Û_T)
    T4, hard]         Û_T(a|q) [soft,                 │
                      training-only]                  ▼
                                              post-hoc calibration (temp/isotonic)
                                              → Û_θ(a|q) = calibrated P(success)  [target E]
```

- **Loss on the hard target** (`L_task`): BCE for binary correctness (#2) /
  judge-as-Bernoulli, smooth-L1 / MSE for graded scores (#3/#4). `[S:06 §5]`
- **Loss on the soft target** (`L_KD`): MSE / smooth-L1 regression to `Û_T` (KD-3);
  **no temperature** unless a softmax KD-1 ablation is run (the primary KD regresses
  raw per-action utilities). `[S:03/06]`
- **α is the experiment** (`03`/`06`): **α=1 ⇒ hard-only ⇒ the non-distilled E1
  control**; KD "adds value" iff some α<1 beats it on held-out routing
  quality/calibration at matched student size. `[S:12]`
- **Calibration is mandatory, not automatic** — sigmoid heads are not calibrated by
  construction; ECE/Brier are measured in E4 and the output is mapped to a
  trustworthy P(success) (lane N2). `[S:04 §4-calibration / 06 §9]`

---

## 5. Calibration and leakage discipline (required by brief for every target)

- **Report** ECE (15-bin), Brier, and AURC for the selective "stay on edge"
  decision; per-action reliability curves for the C/E output [S:v1 §4]. `[RELATED]`
- **Dataset-ID leakage:** the "weak ≥ strong" label leaks dataset identity when
  headroom is dataset-correlated [M: v1 §2.2]; **all** targets must be validated
  under the **leave-one-dataset-out** protocol so a reported gain is query
  understanding, not dataset memorisation [S:v1 §4]. `[M]`
- **Nested vs complementary regime decides whether richer targets *help*.** With a
  nearly-nested pool (Llama-3.1-8B edge, `weak_better ≤ 0.08` [M]) C/E collapse to
  "detect what edge already answers" and may not beat A; with a complementary pool
  (Qwen3-8B edge beats strong on 11.3% of LiveCodeBench [M]) C/E can *raise*
  quality. The pool regime is an **advisor/model-pool question** (`10`/`16`), not
  settled here. `[M]` `[OPEN]`

---

## 6. Decision and hand-off

**Decision (conference core):** the deployed student predicts **per-action
calibrated probability of success** — C-structured, E-valued — realised as N
independent sigmoid heads `Û_θ(a|q)` and trained as the KD-5 hybrid on the hard
substrate `y(a,q)` + soft teacher `Û_T(a|q)`. A (binary edge sufficiency) is the
N=2 first-milestone/baseline; D (pairwise) is a C-ablation; B (multiclass) and the
λ-/cost-baking targets are baselines only. `[PROPOSED, S:03/04/06, v1 §6]`

- **← from `06`:** satisfies the `07` hand-off — `y(a,q)` construction (§3) feeds
  `06 §5` steps 1–3; `N = |𝒜|` confirmed as pool-dependent (`10`).
- **→ `08-system-cost-integration`:** `y` carries **no** cost term; all cost is
  `C(a|s)` (S1–S4) at runtime. The split actions share the parent model's `y` (§3),
  so cost integration must supply the *entire* differentiation between EDGE /
  SPLIT(d) / STRONG.
- **→ `09-split-llm-integration`:** confirm `y(SPLIT(d),q) = y(full,q)` once the
  split interface/quantization at the cut is known (§3 `[OPEN]`).
- **→ `10-model-pool-and-baselines`:** fix K, N=|𝒜|, and the nested-vs-complementary
  regime (§5); register the α=1 non-distilled and the A/B/D variants as baselines.
- **→ `11-novelty-stress-test`:** the label-side defensible lane is **N2**
  (calibrated per-action utility preserved under distillation); the label *shape*
  itself (per-action utility) is **prior art** (HyDRA 4-head, utility regression) —
  not a novelty claim.
- **→ `12-conference-experiment-plan`:** E1 = α sweep on this exact target; E4 =
  teacher-vs-student calibration/quality; leave-one-dataset-out leakage protocol
  (§5) is a precondition for every quality claim.
- **→ `proposed-solution-blue.tex`:** the target definition (§2 equation) and the
  three-stage label flow (§4) are the "utility prediction / training labels" prose
  to typeset in blue.
