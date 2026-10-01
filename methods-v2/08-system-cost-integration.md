# methods-v2 / 08 — System-cost integration: defining C(a|s) and its scalarization

*Deliverable for `MICROENCODER_KD_BRIEF.md` §11 (system-cost integration).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 9).*

## 0. Purpose, grounding, and sourcing

This file fixes the **cost side** of the routing rule and, critically, answers the
two questions the brief §11 poses:

1. **Placement** — is the system cost learned *inside* the student's weights, or
   measured *outside* them? (Brief §11: "Keep system cost OUTSIDE the student
   weights unless strong evidence shows otherwise.")
2. **Scalarization** — how are heterogeneous cost components (milliseconds, bytes,
   dollars, memory) combined into the decision? (Brief §11: "Do not blindly add
   milliseconds + bytes + dollars. Compare S1–S4.")

It is the hand-off `06 §10`/`07 §6` requested: `06 §3.2` locked the *form* of the
runtime rule `R(q,s)=argmax_a[Û_θ(a|q)−λ·C(a|s)]` (Eq. 4) but explicitly deferred
the `C(a|s)` **scalarization** to this file (`06 §9`: "S3/S4 would change the
decision rule's form — flagged, not decided here"). `07 §6` added the constraint
that **all** EDGE/SPLIT(d)/STRONG differentiation lives in `C` (the split actions
share the parent model's quality label `y`), so the cost model must carry the
entire Edge-vs-Split distinction.

**Two different "S1–S4" taxonomies — do not conflate.** The brief uses "S1–S4" in
§11 for **scalarization** (how to fold cost components into one decision). The v1
deliverable `methods/07-system-cost-integration.md` used "S1–S4" for a *different*
axis — **placement** (single joint net / utility+measured-cost / utility+learned-cost
/ systems-only). This file keeps them strictly separate: §2 resolves **placement**
(reusing v1's S1–S4-placement analysis as evidence), and §4 resolves the brief's
**scalarization** S1–S4 (labelled `SC1–SC4` here to avoid collision).

**Reuse, not re-research.** The cost-component decomposition, the state vector `s`,
and the placement argument were already developed in v1
`methods/07-system-cost-integration.md` (and `10-lab-requirements.md`,
`15-sigcomm-experiment-matrix.md`). This file re-casts them onto the brief §11
scalarization question and the locked micro-encoder design (`06`,`07`); it required
**no new web search** (consistent with the sprint pattern that only brief §4/§5 —
deliverables `01`/`02` — needed new research).

**Evidence tags** (from `00`): `[VERIFIED]` primary source supports; `[RELATED]`
adjacent/canonical fact not re-opened; `[PROPOSED]` our design choice; `[OPEN]`
requires experiment/advisor/lab confirmation; `[M]` measured from the released
LLMRouterBench bundle (raw file named in the cited v1 deliverable); `[S:NN]` sourced
to prior deliverable NN.

`source/main-original.tex` is **not modified** (brief §20/§26).

---

## 1. What is in `C` and in the state `s`

The manuscript lists cost components (computation, communication, latency, memory,
operational/monetary; `00`). We decompose `C` into a **per-action structural** part
(a function of the action and prompt/gen length, not of live network) and a
**live-state** part (depends on `s`, changing second-to-second). For action
`a ∈ 𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD}` (the set fixed in `06 §1`) and state `s`:

```
C(a, s) =  w_comp · c_comp(a)              # edge/server compute (FLOPs, energy)        [structural]
         + w_comm · c_comm(a, s)           # bytes transferred ÷ available bandwidth     [live]
         + w_lat  · c_lat(a, s)            # TTFT + TPOT·len + RTT terms                  [live]
         + w_mem  · c_mem(a)               # VRAM / resident memory                       [structural]
         + w_op   · c_op(a)                # $ API / operational                          [structural]
```

The measurable edge-side state vector at decision time (`s`), carried from v1 and
brief §11:

```
s = ( RTT, available_bandwidth, transmitted_activation_bytes(d), server_load?,
      edge_utilisation, prompt_length, split_depth d,
      predicted/observed inference latency, TTFT, TPOT, memory_pressure, op_cost )
```

Two facts constrain the design, carried from v1 (`07 §0.1`) and sharpened by `07`
(labels):

- **Part of `C` depends on `q` only through length/features** (`c_comp`, `c_mem`,
  `c_op`), and **part depends on live `s`** (`c_comm`, `c_lat` via RTT/bandwidth).
  A router that bakes `s` into weights cannot track the changing part. `[VERIFIED:
  v1 §0.1]`
- **The Split action's entire differentiation lives in `C`.** `07 §3` fixed
  `y(SPLIT(d),q) = y(full model,q)` — a lossless split returns the *same answer
  quality*, so `Û_θ` **cannot** separate SPLIT(d) from STRONG; **only** `c_comm`
  (activation bytes at depth `d`) and `c_lat` do. Hence the cost model is not a
  detail — it is what makes the Split-LLM part of the method testable at all.
  `[S:07 §3]` `[OPEN]` on the exact byte function pending Henry's split interface
  (`09`).

---

## 2. Placement: cost stays OUTSIDE the student's weights (brief §11 default, confirmed)

The brief instructs keeping system cost outside the student weights "unless strong
evidence shows otherwise." The micro-encoder design already committed to this in
`06 §3.2` / `07 §2`; this section states the evidence so the decision is not merely
asserted.

**Decision: the student learns `Û_θ(a|q)` only; `C(a|s)` is measured/predicted
outside θ and combined by the explicit Eq. (4) rule.** This is v1's
**S2-placement** ("learn utility only; combine with measured cost outside the
net"), with v1's **S3-placement** (a small learned cost/latency predictor `g_φ`)
reserved only for the stochastic tail-latency / queueing term. Evidence that this
beats baking cost into θ (v1's **S1-placement**):

1. **λ must be a runtime knob (Eq. 2/4).** Baking cost into θ freezes λ and the
   cost table in the weights; any change to pricing, to the weighting, or to the
   *distribution* of `s` forces relabelling + retraining. The manuscript's own
   requirement #4 (adaptability) and #3 (system awareness / react to changing
   network) cannot be met by a frozen cost. `[VERIFIED: v1 §1, §2]`
2. **Extrapolation to unseen network conditions.** A net trained on a bandwidth
   range need not behave monotonically outside it; for a paper claiming "behaves
   well under changing/adverse networks," an explicit `−λ·C` rule with a *measured*
   `C` extrapolates by construction, a joint net does not. `[RELATED, v1 §1]`
3. **Interpretability + separable validation.** The learned part is validated by
   calibration (`07 §5`, ECE/Brier); the cost part by direct measurement on the
   testbed (`10`). A joint net gives neither a U-vs-C curve nor separable
   debugging. `[VERIFIED: v1 §2]`
4. **It is literally the manuscript's Eq. (2).** `R=argmax[Û−λĈ]` is the U−λC
   objective with `U:=Û, C:=Ĉ`; the joint net only makes the structure *implicit*.
   `[VERIFIED: v1 §2]`
5. **It is the N3 novelty lane.** "Separation of distilled semantic utility
   prediction from live measured edge/Split system cost" (brief §15 N3) *requires*
   the cost be outside θ; baking it in forfeits the one structural novelty lane the
   method has (`06 §10`, `11`). `[S:06/11]`

**Why not fully outside (static table) for *every* term:** the deterministic terms
(activation bytes, base TTFT, per-action FLOPs/VRAM/$) are a measured table (v1
S2-placement); but **server-queue / tail latency under load is stochastic** and a
static table is a poor approximation exactly in the SIGCOMM-interesting regime —
there a small learned `g_φ(a,q,s)` (v1 S3-placement) may be fit *for that term
only*. This is a **hybrid**: S2-placement for deterministic cost + S3-placement for
the queueing/tail term. `[PROPOSED, S:v1 §3]` `[OPEN]` — whether `g_φ` is needed is
an empirical question (E6/E7), not assumed.

**Rejected placement:** v1 **S1-placement** (single joint net over `q`+`s`) — fails
rows 1–5 above. **S4-placement** (systems-only policy, no learned `Û`) is *not a
placement of our router* — it is the mandatory **systems-only baseline** that makes
query-awareness falsifiable (`10`/`14`; it answers "does query-aware routing beat a
good systems rule?"). `[VERIFIED: v1 §4]`

---

## 3. The decision rule, restated with the cost outside θ

For completeness, the inference-time rule the testbed exercises (consistent with
`06` Eq. 4):

```
given q, and live state s_t at time t:
  Û_a = Û_θ(a | q)                 for a ∈ 𝒜      # learned, query-only, one encoder pass (06)
  Ĉ_a = scalarize( c_comp(a), c_comm(a,s_t), c_lat(a,s_t), c_mem(a), c_op(a) )   # SC1–SC4, §4
  a*  = argmax_a  Û_a − λ · Ĉ_a                   # λ set/swept at runtime (E5)
  (optional) if max_a Û_a < τ_abstain:  escalate to STRONG   # selective-prediction guard (07)
```

Sweeping `s_t` (bandwidth, RTT, server load) with **fixed θ and fixed labels**
produces every network-dependent curve in E6/E7 — the "networked-systems effect,
not classification accuracy" evidence the brief requires — and is only possible
because `C` is outside θ. `[VERIFIED: v1 §7]` The open question this file now
resolves is what `scalarize(·)` is.

---

## 4. Scalarization (brief §11 SC1–SC4): how to combine the cost components

The brief warns against "blindly add milliseconds + bytes + dollars" and lists four
options. The core tension: **Eq. (4) as written needs a *scalar* `C`** (so the
argmax is well-defined), but the honest *evaluation* of a quality/latency/bytes/cost
trade-off should **not** hinge on one arbitrary weight vector.

### SC1 — Normalized weighted scalar cost
```
Ĉ(a,s) = Σ_j w_j · ñ_j(a,s)      where ñ_j = (metric_j − min_j)/(max_j − min_j)   (per-metric min-max or z-score normalization)
```
Each heterogeneous metric is normalized to a comparable `[0,1]` (or standardized)
scale *before* weighting, so the weights `w_j` are dimensionless trade-off
preferences rather than a raw ms+bytes+$ sum. This is the brief's explicit fix for
"don't blindly add."

- **Pro:** keeps Eq. (4) literally intact (scalar `C`); λ remains the single
  sensitivity knob; directly produces E5's λ-sweep curves. `[PROPOSED]`
- **Con:** requires choosing/justifying `w_j` and the normalization ranges; a
  reviewer can object to the specific weights. Mitigated because the evaluation
  (SC4) does **not** depend on them — see §5.
- **Normalization must be fit on a held-out calibration split, not test**, else the
  min/max leak. `[PROPOSED]`

### SC2 — Latency as the online penalty; report the rest separately
```
Ĉ(a,s) = c_lat(a,s)     # single dominant metric in the online rule
```
other metrics (bytes, $, memory) are **measured and reported separately**, not
folded into the decision.

- **Pro:** zero arbitrary weights in the online rule; latency is the user-facing
  metric and the one SIGCOMM reviewers care about; the clearest story. `[PROPOSED]`
- **Con:** ignores communication/$ in the *decision* — acceptable only if latency
  already correlates with bytes (true when bandwidth is the bottleneck, i.e. exactly
  the Split regime where `c_lat ⊃ c_comm/bandwidth`). `[OPEN]` on that correlation,
  testable in E7.

### SC3 — Constrained optimization (maximize quality subject to a budget)
```
a* = argmax_a Û_θ(a|q)   s.t.   c_lat(a,s) ≤ L_max,  c_comm(a,s) ≤ B_max,  c_op(a) ≤ $_max
```
- **Pro:** matches real deployment SLAs ("p95 ≤ 300 ms, ≤ $X/query"); no
  cross-metric weighting needed at all. `[PROPOSED]`
- **Key fact — SC3 and SC1 are duals.** By Lagrangian relaxation, the λ in Eq. (4)
  **is the KKT multiplier** of the SC3 latency/budget constraint: solving SC1 across
  a λ-sweep traces the same frontier SC3 traces across a budget-sweep. So SC1 (the
  online rule) and SC3 (the SLA framing) are two views of one object, not rivals —
  this is the clean way to present the method to both ML and systems reviewers.
  `[PROPOSED, RELATED: standard constrained-optimization / Lagrangian duality]`
- **Con:** the hard argmax changes form (it is no longer `Û−λC`); feasibility can be
  empty under adverse `s` → needs a fallback (escalate / best-effort). `[PROPOSED]`

### SC4 — Pareto-front evaluation (no single number)
Do not fold metrics into one scalar at all for *reporting*: present the
quality-vs-latency-vs-bytes-vs-$ **Pareto front** and show the method dominates (or
matches at lower cost) the baselines.

- **Pro:** the fairest, least-attackable evaluation; no weight choice to dispute;
  the natural way to show "router achieves same quality at fewer bytes / lower p95."
  `[PROPOSED]`
- **Con:** not an *online decision rule* — you still need SC1/SC2/SC3 to pick a
  single action at runtime. SC4 is an **evaluation framing**, not a router.

### Comparison

Ratings `[PROPOSED]` unless tagged; `+` favourable, `~` moderate, `−` unfavourable.

| Criterion | SC1 weighted scalar | SC2 latency-only | SC3 constrained | SC4 Pareto |
|---|---|---|---|---|
| Is an online decision rule | **+** | **+** | + (changed form) | − (eval only) |
| Keeps Eq. (4) `Û−λC` literally | **+** | + (λ·lat) | − (constrained argmax) | n/a |
| Avoids arbitrary cross-metric weights | − | **+** | **+** | **+** |
| Matches deployment SLA language | ~ | + | **+** | ~ |
| Produces E5 λ-sweep curves | **+** | + | + (budget-sweep dual) | + (is the front) |
| Attackable by a reviewer | weights | metric choice | budget choice | **least** |
| Needs held-out normalization fit | yes | no | no (uses raw units) | no |

---

## 5. Recommendation (conference core)

**Online decision rule = SC1 (normalized weighted scalar cost), presented as the
Lagrangian dual of SC3.** **Evaluation = SC4 (Pareto fronts) + SC2 report-separately
discipline.** Concretely:

1. **Runtime:** use SC1 so Eq. (4) stays literally `argmax_a[Û_θ(a|q)−λ·C(a|s)]`
   with `C` a normalized weighted scalar — one scalar, one knob λ. This is the form
   already locked in `06` Eq. (4); choosing SC1 means `06` needs **no revision**
   (the `06 §9` worry that SC3/SC4 would change Eq. (4)'s form is resolved by *not*
   making the online rule SC3). `[PROPOSED, S:06 §9]`
2. **Present SC3 as the dual, not an alternative:** state that λ is the multiplier
   of a latency/byte/budget constraint, so the same system serves an SLA deployment
   by sweeping the budget instead of λ. This pre-empts the systems reviewer who
   wants constraints, without a second implementation. `[PROPOSED]`
3. **Evaluate with SC4:** no quality claim rests on a particular `w_j`/λ — report
   the quality-vs-latency, quality-vs-bytes, quality-vs-$ **Pareto fronts** (E7)
   and show dominance/matching. This neutralizes the "arbitrary weights" objection
   that is SC1's only real weakness. `[PROPOSED]`
4. **Report every metric separately too (SC2 discipline):** TTFT, TPOT, e2e
   p50/p95/p99, activation bytes, $ are each reported, never silently summed — the
   brief's explicit "do not blindly add" requirement. `[VERIFIED: brief §11]`

This stack is internally consistent: SC1 is the *rule*, SC3 is its *SLA face*, SC4
is the *evaluation*, SC2 is the *reporting hygiene*. The weights `w_j` and λ are
**exposed parameters swept in E5/E7**, not hidden constants — so the method's claim
is "Pareto-dominant across the whole trade-off," not "best at one weight choice."
`[PROPOSED]`

**What stays measured vs learned (brief §11 core):** `Û_θ(a|q)` is learned (in θ);
**all** of `C(a|s)` is measured (deterministic terms as a table) or predicted by a
tiny `g_φ` for the tail-latency term only (never in the student); λ and `w_j` are
runtime parameters. `[PROPOSED, S:06/07]`

---

## 6. Open items (do not guess — brief §2 UNRESOLVED)

- **Exact `c_comm(SPLIT(d),s)` byte function** depends on Henry's split interface,
  activation tensor shape, serialization, and quantization at the cut (`09`). The
  `y(SPLIT(d),q)=y(full,q)` equivalence (`07 §3`) also hinges on whether the cut
  quantizes. `[OPEN]`
- **Whether `g_φ` (learned tail-latency term) is needed** vs a static table — an
  empirical question for E6/E7, not assumed. `[OPEN]`
- **Normalization ranges and `w_j`/λ defaults** require the testbed to exist
  (`10`,`16`); no numeric cost values are given here (none are measured). `[OPEN]`
- **Memory/op-cost weighting** is deployment-specific (edge device unknown, `16`);
  reported, not baked. `[OPEN]`

---

## 7. Hand-off

- **← from `06`/`07`:** resolves the `06 §9` deferral — online rule = SC1, so Eq.
  (4)'s scalar-`C` form is **retained** (no revision to `06`); `C` carries the
  entire EDGE/SPLIT(d)/STRONG differentiation (`07 §3`).
- **→ `09-split-llm-integration`:** supply `c_comm(SPLIT(d),s)` = activation bytes
  at depth `d` ÷ bandwidth + RTT, and confirm the split-quality equivalence; this is
  the single most load-bearing cost term (§1, §5).
- **→ `10-model-pool-and-baselines`:** register the **systems-only policy**
  (v1 S4-placement) as the mandatory baseline that falsifies query-awareness; set
  the action set `𝒜` whose per-action structural costs populate the table.
- **→ `11-novelty-stress-test`:** cost-side defensible lane is **N3**
  (learned-utility ↔ measured-cost *separation*, §2) and **N5** (distilled router +
  network-adaptive decision layer, §3–§4); the scalarization math (SC1↔SC3 duality)
  is **[RELATED]** standard optimization, **not** a novelty claim.
- **→ `12-conference-experiment-plan`:** E5 = λ/weight sweep over SC1 (= budget
  sweep over SC3 dual); E6 = route change under bandwidth/RTT via `C`; E7 = Pareto
  fronts (SC4) with every metric reported separately (SC2).
- **→ `proposed-solution-blue.tex`:** the `C(a|s)` decomposition (§1), the SC1 rule
  as Eq. (4)'s cost term, and the SC3-dual sentence are the "runtime cost
  integration / inference routing rule" prose to typeset in blue.
