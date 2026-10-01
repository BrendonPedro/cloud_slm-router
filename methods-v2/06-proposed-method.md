# methods-v2 / 06 — Proposed method: the distilled micro-encoder router (conference core)

*Deliverable for `MICROENCODER_KD_BRIEF.md` §9 (exact f_θ definition) and §16
(one coherent conference-core architecture). Prepared 2026-10-02 (gnhf
microencoder-kd sprint, iteration 7).*

## 0. Purpose, grounding, and sourcing

This file assembles the single coherent proposed architecture for the conference
paper out of the decisions already locked by deliverables `00`–`05`:

- **Backbone / shape** (`05`): student = `ModernBERT-base` (≈149 M) + **N parallel
  scalar utility heads**; teacher = `ModernBERT-large` (≈395 M), same family.
- **KD formulation** (`03`): **KD-3 utility-regression distillation, trained as the
  KD-5 hybrid** (hard observed-outcome labels + soft teacher utility), with an α
  sweep whose α=1 end is the non-distilled control.
- **Teacher** (`04`): **T1 larger same-family encoder router**, training-only; the
  observed-outcome oracle T4 is **ground truth, not a teacher** (`04` §4) and the
  judge/strong-model T5 is a **label source, not a teacher**.
- **Decoupling** (`00` CONFIRMED #2, `03` §1): learned query-conditioned utility
  `Û_θ(a|q)` stays in the student; measured live system cost `C(a|s)` stays
  **outside** the student weights and is combined only at runtime.

This deliverable writes (1) the exact f_θ definition and its reduction to the
manuscript's Eq. (3), (2) the training and inference algorithms, (3) the ASCII
architecture (training + inference), and (4) the training-only / inference-time /
learned / measured / optional partition that brief §16 demands. The
publication-quality figure *specification* and TikZ source are deliverable `15`
(brief §21); this file provides the ASCII diagram and the content contract `15`
must render.

**No results are claimed.** Per brief §20/§26 this file contains no "we
outperform / achieves / demonstrates" language; every performance statement is a
hypothesis routed to `12-conference-experiment-plan`.

**Reuse, not re-research.** Every component here is inherited from `00`–`05` and
the v1 `methods/`; no new web search was required. **Evidence tags** (from `00`):
`[VERIFIED]` primary source supports; `[RELATED]` adjacent/canonical fact not
re-opened this iteration; `[PROPOSED]` our design choice; `[OPEN]` requires
experiment/advisor/licence confirmation; `[S:NN]` sourced to prior deliverable NN.

---

## 1. The fixed objective this method implements (unchanged)

From `00` (verbatim from `source/main-original.tex`, **not modified**):

- Eq. (1) `R : Q → M`
- Eq. (2) `max_R  E_q[ U(R(q), q) − λ · C(R(q), q) ]`
- Eq. (3) `R(q) = argmax_{M_k ∈ M} f_θ(q, M_k)`

The proposed method is an **implementation of f_θ**. It does not redefine the
research problem (brief §1/§26). The six fixed requirements — lightweight router,
query understanding, system awareness, adaptability/generalization, edge
deployment, routing among edge-SLM / Split-LLM / strong-remote paths — are each
satisfied by a named component in §7.

---

## 2. Notation: from "model M_k" to "action a" (the only notation extension)

The manuscript writes the decision over models `M_k ∈ M`. The advisor's confirmed
decomposition (`00` CONFIRMED #2) and the Split-LLM path (`09`) require the
decision to range over **execution actions**, because a split happens at a *depth*
`d` and two different split depths of the same model are two different
cost/quality operating points. We therefore define the **action set**:

```
𝒜 = { EDGE_SLM ,  SPLIT(d₁), …, SPLIT(d_m) ,  STRONG/CLOUD }
```

- `EDGE_SLM` — run the small model entirely on the edge device.
- `SPLIT(d)` — run layers `[0,d)` on the edge, transfer the activation tensor,
  run `[d, L)` on the server (`09-split-llm-integration`). Each enabled depth `d`
  is its own action.
- `STRONG/CLOUD` — run the strong/remote model (full remote execution).

`N = |𝒜|` is fixed by the model pool (`10-model-pool-and-baselines`); the exact
pool and the exact enabled split depths are `[OPEN]` → `10`/`16`.

**Reduction to Eq. (3) (brief §9, "show how it reduces").** Each action `a ∈ 𝒜`
corresponds to a concrete execution path that produces an output; call that path's
induced model-of-record `M(a)`. The manuscript's `M` is the image
`{ M(a) : a ∈ 𝒜 }`, and when every model is reachable by exactly one action (no
split depths, m=0) the map `a ↦ M(a)` is a bijection and `𝒜 ≡ M`. Thus Eq. (3)

```
R(q) = argmax_{M_k ∈ M}  f_θ(q, M_k)
```

is the special case of the proposed rule (Eq. (4) below) in which (i) split depths
are disabled so `𝒜 ≡ M`, and (ii) the system-cost term is dropped (`λ = 0`, or
`C` folded into `f_θ`). The extension is therefore **a refinement, not a
redefinition**: it enriches the choice set with split depths and factors the
score into a learned term plus a measured term, and collapses back to Eq. (3)
under the stated conditions. `[PROPOSED]`

---

## 3. Exact definition of f_θ

### 3.1 The student scoring function

The deployed student is `g_θ : Q → ℝ^N`, a ModernBERT-base encoder [S:05] with a
pooled representation feeding **N parallel scalar heads**, one per action:

```
h(q)        = Pool( ModernBERT-base_θ(q) )            ∈ ℝ^H      (H = 768)   [S:05]
Û_θ(a | q)  = ϕ( w_aᵀ h(q) + b_a )        for each a ∈ 𝒜        (one head per action)
```

- `Pool` = the student's pooling of the encoder output ([CLS] or mean; an ablation,
  `[OPEN]`).
- `ϕ` = the head activation. Because utility is defined as a **calibrated
  probability of success** (`07-training-labels`, target E), `ϕ = σ` (sigmoid)
  and each head is an **independent** per-action utility — *not* a softmax over
  actions. This is deliberate (`03` §1, KD-3 over KD-1): a softmax couples the
  actions and would entangle the learned utility with the cost term, and it breaks
  cheap **model-pool addition** (adding an action = adding one head, not
  retraining a joint normalization). `[PROPOSED, S:03]`

So the **proposed f_θ is the per-action learned utility**:

```
f_θ(q, a)  :=  Û_θ(a | q)                                            (Eq. 3′)
```

which is exactly the `f_θ(q, M_k) = Û_θ(M_k | q)` form the brief §9 says is
preferred, with `M_k` generalized to `a` per §2.

### 3.2 The runtime routing rule (learned utility − measured cost)

```
R(q, s)  =  argmax_{a ∈ 𝒜}  [ Û_θ(a | q)  −  λ · C(a | s) ]          (Eq. 4)
                               \________/       \________/
                                LEARNED          MEASURED at runtime,
                                (student,         OUTSIDE student weights
                                 one fwd pass)    (08-system-cost-integration)
```

- `Û_θ(a | q)` — query-conditioned, system-*un*aware, learned once (and
  distilled). One forward pass of the encoder produces all N head values.
- `C(a | s)` — the scalarized live system cost of action `a` under measured system
  state `s` (bandwidth, RTT, contention, activation-transfer bytes, edge/server
  compute latency, TTFT/TPOT, resource pressure). Its scalarization (S1–S4) is
  decided in `08`; **it is not learned and not in θ.** `[S:08]`
- `λ` — the single quality↔cost trade-off knob from Eq. (2), set at runtime
  (swept in experiment E5).

**Why decoupled (one-line justification carried from `00`/`03`):** utility is a
property of the *query↔model* match and is stable; system cost is a property of
the *live network/hardware* and changes second-to-second. Baking `s` into θ would
force retraining on every network change and destroy the edge-deploy story; the
residual novelty lane N3 (`11`) is precisely this separation. `[PROPOSED]`

---

## 4. What is learned vs measured vs training-only (brief §16 partition)

| Symbol | Role | Where it lives | Phase |
|---|---|---|---|
| `g_θ` = ModernBERT-base + N heads | student router | **edge device** | **inference** (learned) |
| `Û_θ(a|q)` | per-action learned utility | output of `g_θ` | **inference** (learned) |
| `C(a|s)` | scalarized system cost | runtime monitor (`08`) | **inference** (measured, not in θ) |
| `λ` | quality/cost knob | runtime config | inference (set, swept E5) |
| teacher `ModernBERT-large` router | soft-target source for KD | lab GPU | **training only** [S:04] |
| `Û_teacher(a|q)` | soft utility targets | teacher output | **training only** |
| `y(a,q)` observed outcome | hard labels (= oracle T4, **ground truth**) | offline eval harness | **training only** [S:04/07] |
| judge / strong-model scores | a *source* of `y`, not a teacher | offline | **training only** [S:04] |
| KD-4 representation matching | optional backbone-improvement ablation | lab GPU | **training only, optional** [S:03] |

The inference-time footprint is therefore **exactly**: one encoder forward pass +
N scalar heads + the cheap arithmetic of Eq. (4). Everything with "training only"
disappears at deployment — this is what keeps the method *lightweight at
inference* (fixed requirement #1).

---

## 5. Training algorithm (KD-3 as KD-5 hybrid) [PROPOSED, S:03/04]

**Inputs:** query set `{q_i}`; action set `𝒜`; observed outcomes `y(a, q_i) ∈
[0,1]` (per-action success/utility, from the eval harness = oracle T4 ground
truth, `07`); teacher router `T = ModernBERT-large` already fit to the same
`y`; hybrid weight `α ∈ [0,1]`; (optional) KD-4 layer-matching weight `γ`.

```
# ---- training-only; runs on lab GPU (00 CONFIRMED #4); no large-scale jobs ----
1.  Build labels:     for each (q_i, a):  hard target  y(a, q_i)            # T4 = ground truth
2.  Fit teacher T on y (larger encoder router), freeze T.                   # T1, 04
3.  Precompute soft targets:  Û_T(a|q_i) = σ(head_a of T(q_i))             # training-only
4.  for each minibatch B:
5.      h = Pool(ModernBERT-base_θ(q));   Û_θ(a|q) = σ(w_aᵀh + b_a)  ∀a
6.      L_task = (1/|B|N) Σ_q Σ_a  ℓ( Û_θ(a|q), y(a,q) )                    # hard, BCE or smooth-L1
7.      L_KD   = (1/|B|N) Σ_q Σ_a  ℓ_reg( Û_θ(a|q), Û_T(a|q) )             # soft, regression KD
8.      L_repr = γ · representation_match(θ, T)         # OPTIONAL KD-4, same-family only
9.      L      = α · L_task + (1 − α) · L_KD + L_repr                       # KD-5 hybrid
10.     θ ← θ − η ∇_θ L
11. Calibrate heads on held-out data (temperature / isotonic) so Û_θ is a
    calibrated P(success).                                                  # 07/08; N2 lane
```

Notes:
- **α is the whole experiment, not a hyperparameter to hide** (`03` §KD-5): **α=1
  ⇒ L = L_task ⇒ the non-distilled control** (E1). KD "adds value" iff some α<1
  beats α=1 on held-out routing quality/calibration at matched student size.
  Falsification is built in. `[S:03/12]`
- **ℓ_reg** is MSE / smooth-L1 (or BCE-to-soft-target); temperature `T` only
  appears if a softmax variant (KD-1) is run as an ablation — the primary KD-3
  regresses raw per-action utilities, so no temperature is required. `[S:03]`
- **KD-4 (`L_repr`)** is available *only* because student and teacher share the
  ModernBERT family/tokenizer (`05` R4) — it is an ablation (A-repr), **not** part
  of the core claim.
- **No teacher at inference.** Steps 2–3, 8 are training-only; the shipped model is
  just `g_θ`.

---

## 6. Inference algorithm (edge-deployed) [PROPOSED]

```
# ---- runs on the edge device; one encoder pass; teacher absent ----
Input:  query q;  live system state s (from runtime monitor, 08);  λ
1.  h      = Pool( ModernBERT-base_θ(q) )               # 1 forward pass, INT8/ONNX (05 R6)
2.  for a in 𝒜:  Û_a = σ( w_aᵀ h + b_a )               # N scalar heads (calibrated)
3.  for a in 𝒜:  C_a = C(a | s)                         # measured now, not learned (08)
4.  a*    = argmax_a [ Û_a − λ · C_a ]                   # Eq. (4)
5.  dispatch:
        EDGE_SLM   -> run small model locally
        SPLIT(d)   -> run [0,d) local, send activation, run [d,L) on server (09)
        STRONG     -> full remote execution
6.  (optional, journal track) log (q, a*, Û, C, outcome) for continual update (13)
```

The optional step 6 is the **only** hook to the journal continual-learning
extension; it is **logging only** and changes no conference-core behaviour (`13`,
brief §18/§26).

---

## 7. How each fixed requirement is met (traceability)

| Fixed requirement (`00`/brief §1) | Component that satisfies it |
|---|---|
| 1. Lightweight router | `g_θ` = 149 M encoder, INT8/ONNX, one forward pass; teacher dropped at inference (§4). |
| 2. Query understanding | ModernBERT-base contextual encoding of `q` → `h(q)` (§3.1). |
| 3. System awareness | `C(a|s)` measured at runtime and combined in Eq. (4) (§3.2, `08`). |
| 4. Adaptability / generalization | per-action heads: add an action = add a head (no joint-softmax retrain); KD soft targets aid generalization to interpolated queries (`04` §6). |
| 5. Edge deployment | INT8/ONNX ModernBERT-base, HyDRA CPU precedent (`05` R6); `C` monitor is cheap arithmetic. |
| 6. Route among EDGE / SPLIT / STRONG | `𝒜` includes all three path classes incl. split depths (§2). |

---

## 8. ASCII architecture (brief §16 — training and inference)

```
================================  TRAINING PHASE (lab GPU, training-only)  ================================

   query set {q_i}
        |
        |------------------------------> OBSERVED PER-ACTION OUTCOMES  y(a,q)   [= oracle T4 = GROUND TRUTH,
        |                                 (eval harness; judge/strong = label    not a teacher — 04 §4]
        |                                  SOURCE, not teacher)
        |                                        |
        |                                        |  (hard labels, all α)
        v                                        v
   TEACHER ROUTER  T1                      +------------------------+
   ModernBERT-large (~395M) --soft Û_T-->  |   STUDENT              |
   [training-only, 04]        (1-α) weight |   ModernBERT-base      |
        ^                                  |   (~149M) + N heads    |
        |  fit on same y                   |   Û_θ(a|q) = σ(wᵀh+b)  |
        +----------------------------------+------------------------+
        (optional KD-4 representation match, same-family only, γ)   |
                                                                    v
                            L = α·L_task(Û_θ,y) + (1-α)·L_KD(Û_θ,Û_T) [+ γ·L_repr]
                                         α=1  ==  NON-DISTILLED CONTROL (E1)
                                                                    |
                                                                    v
                                                   calibrate heads (temp/isotonic)
                                                                    |
                                               === ship θ only; teacher discarded ===

================================  INFERENCE PHASE (edge device, lightweight)  ============================

      query q                                      live system state s
        |                                          (bw, RTT, contention,
        v                                           act-bytes, TTFT/TPOT,
   STUDENT g_θ  (1 forward pass, INT8/ONNX)         compute lat, mem)  [MEASURED]
        |                                                 |
        v                                                 v
   Û_θ(a|q)  for a in 𝒜   [LEARNED]              C(a|s)  for a in 𝒜   [MEASURED, not in θ — 08]
        \________________________   ______________________/
                                 \ /
                                  v
                 a* = argmax_a [ Û_θ(a|q) - λ·C(a|s) ]   (Eq. 4; λ set at runtime, swept E5)
                                  |
            +---------------------+----------------------+
            v                     v                      v
         EDGE_SLM             SPLIT(d)               STRONG/CLOUD
      (local small model)  (local [0,d) -> send    (full remote exec)
                            activation -> server
                            [d,L); 09)

   LEGEND:  [LEARNED] in student weights θ   |   [MEASURED] live, outside θ   |
            training-only components vanish at inference.
```

---

## 9. Design assumptions and limitations (honest, no results) [OPEN]

- **KD may not help.** The entire value of the teacher is tested by the α sweep
  (E1). If no α<1 beats α=1, the conference method degrades gracefully to a
  *non-distilled* per-action utility micro-encoder with runtime cost separation —
  still a coherent system, but the "distilled" adjective is dropped (brief
  stop-condition #4 branch). `[S:03/12]`
- **The teacher must genuinely generalize beyond `y`.** If `Û_T ≈ y` everywhere,
  KD = supervised regression and adds nothing (`04` §4 collapse). `[OPEN]`
- **N and split depths are pool-dependent.** The head count and enabled `SPLIT(d)`
  actions are fixed only once the model pool (`10`) and Henry's split interface
  (`09`) are known — do not guess (`16`). `[OPEN]`
- **Calibration is a claim, not a given.** Per-action calibrated utility (lane N2)
  must be *measured* (ECE) in E4; sigmoid heads are not automatically calibrated.
- **`C(a|s)` scalarization is unresolved** across S1–S4 (`08`); Eq. (4) assumes a
  scalar `C`, but S3 (constrained) / S4 (Pareto) would change the decision rule's
  form — flagged, not decided here. `[S:08]`
- **No measured latency.** All "one forward pass is cheap" statements are
  architectural, not measured on our (unknown) edge device (`16`). `[OPEN]`

---

## 10. Hand-off

- **→ `07-training-labels`:** define `y(a,q)` construction (observed utility /
  binary correctness / judge score → calibrated P(success), target E) feeding
  §5 steps 1–3; confirm N = |𝒜|.
- **→ `08-system-cost-integration`:** fix the `C(a|s)` scalarization (S1–S4); if
  S3/S4 is chosen, revise Eq. (4)'s form accordingly.
- **→ `09-split-llm-integration`:** supply the enabled `SPLIT(d)` depths and the
  activation-transfer cost that feeds `C(SPLIT(d)|s)`.
- **→ `10-model-pool-and-baselines`:** set N and the action set; register the
  **non-distilled ModernBERT-base (α=1)** and **hidden-state self-router
  (Candidate C)** baselines against this exact f_θ.
- **→ `11-novelty-stress-test`:** the defensible lanes are N3 (learned-utility ↔
  measured-cost separation, §3.2), N2 (calibrated per-action utility preserved
  under distillation), N4/N6 (Split action + edge deployment) — **not** the
  encoder, **not** the KD mechanism.
- **→ `12-conference-experiment-plan`:** E1 = α sweep (α=1 control); E4 =
  teacher(large) vs student(base) quality/calibration/params/latency; E5 = λ
  sweep over Eq. (4); E6 = route change under bandwidth/RTT via `C`.
- **→ `15-architecture-figure-spec`:** render §8 as the publication figure with
  distinct visual treatment for learned / measured / training-only paths.
- **→ `proposed-solution-blue.tex`:** this file's Eqs. (3′)/(4), §5/§6 algorithms,
  and §8 diagram are the content to typeset as the blue Proposed Solution.
