# 07 — System-Cost Integration (Approaches S1–S4)

*Method-selection sprint, iteration 4. Planning document. Nothing here has been
trained, run, or measured by us. Cost quantities below are **definitions and
formulas**, not measured values; the actual bytes/RTT/latency numbers come from
the SIGCOMM testbed (`10`, `14`, `15`) and have not been collected. This document
does not choose an approach — it lays out S1–S4 so the advisor can.*

Evidence tags: **[S: …]** sourced in a cited earlier deliverable; **[M]**
measured from the released bundle; **[O]** our analysis; **[P]** our proposal;
**[E]** untested expectation.

`source/main-original.tex` unchanged (SHA-256 `06f5f9d7…1707cf6`, re-checked).
`paper/main-revised.tex` unchanged.

---

## 0. The object we are integrating

The manuscript's objective (`00-scope-lock.md`) is

```
max_R  E_q [ U(R(q), q) − λ · C(R(q), q) ]          (Eq. 2)
R(q) = argmax_{M_k ∈ M} f_θ(q, M_k)                 (Eq. 3)
```

`06-label-and-training-design.md` fixed what the *utility* side `U` is trained
against. This document fixes the **cost** side `C` and, crucially, **where in the
system it is computed** — inside the neural router, or outside it. That placement
is the difference between "an ML classifier" and "a networked-systems router",
which is the pivotal SIGCOMM-fit question (`14`, brief §5, §13). It is a genuine
design fork, so we present four approaches (the brief's S1–S4) with explicit math
and keep the choice open.

### 0.1 What is in the cost `C` and the state `s`

The manuscript lists cost components (`00-scope-lock`): computation,
communication, latency, memory, operational/monetary. We split them into a
per-action structural part and a live-state part. For action `a ∈ 𝒜 =
{EDGE, SPLIT(d), CLOUD, ABSTAIN}` and system state `s`:

```
C(a, s) =  w_comp · c_comp(a)                 # edge/server compute (FLOPs, energy)
         + w_comm · c_comm(a, s)              # bytes transferred / bandwidth
         + w_lat  · c_lat(a, s)               # TTFT + TPOT·len + RTT terms
         + w_mem  · c_mem(a)                  # VRAM / resident memory
         + w_op   · c_op(a)                   # $ API / operational
```

The state vector `s` (measurable at the edge at decision time) [S: brief §9;
recommended-experiment §6]:

```
s = ( RTT, available_bandwidth, transmitted_activation_bytes(d),
      server_load?, edge_utilisation, prompt_length,
      split_depth d, predicted/observed inference latency )
```

Two facts constrain the design:

1. **Some of `C` depends on `q` only through length/features** (`c_comp`, `c_mem`,
   `c_op` are mostly per-action constants or functions of prompt/gen length), and
   **some depends on live `s`** (`c_comm`, `c_lat` depend on RTT/bandwidth that
   change second-to-second). A router that bakes `s` into weights cannot track the
   changing part [O; ties to `06 §1` targets B/E].
2. **The Split action's cost is where the paper's networking novelty lives**: for
   a lossless partition, `SPLIT(d)` and `CLOUD` give the *same answer quality*, so
   `U` cannot separate them — **only `c_comm` (activation bytes at depth `d`) and
   leakage do** [S: recommended-experiment §6 H3; 03 §3 N1]. Hence how `C` is
   integrated is not a detail; it is what makes the Split-LLM part of the title
   testable at all.

---

## 1. S1 — Single neural router over (query + live system variables)

**Idea.** One network takes `q` *and* `s` and emits the decision (or the scores).

```
f_θ(q, s, M_k)  →  score;   R(q,s) = argmax_k f_θ(q, s, M_k)
```

**Map to Eq. (2).** The `− λ·C` structure is *implicit*: the network is trained on
labels `argmax_k[ y(M_k,q) − λ·C(M_k,s) ]` (target B or E of `06`), so both λ and
the cost model are **absorbed into θ**.

**Advantages.** Can learn interactions between query difficulty and system state
(e.g. "escalate a hard query only when bandwidth is high"). Single artifact.

**Disadvantages** [O]:
- **λ and the cost table are frozen in the weights** → any change to the
  cost weighting, to pricing, or to the *distribution* of `s` requires
  relabelling + retraining (`06 §1` B/E weakness).
- **Poor extrapolation to unseen network conditions** — a neural net trained on a
  bandwidth range need not behave monotonically outside it; for a paper whose
  claim is "behaves well under changing/adverse networks" this is the central risk
  [E].
- **Not interpretable**: cannot show reviewers the U vs C curve.
- Retraining requirement: **high**.

**When defensible.** Only if `s` has a small, stationary support and the
interaction with `q` is genuinely nonlinear and important. Otherwise dominated by
S2. **[O]**

---

## 2. S2 — Learn utility only; combine with **measured** cost outside the net

**Idea.** The neural router predicts *only* query/model utility (target C of `06`).
The cost is measured live and combined by a fixed rule.

```
Û(M_k, q) = f_θ(q, M_k)                         # learned, query-only
Ĉ(M_k, s) = measured cost table (Eq. 0.1)       # NOT learned
R(q,s) = argmax_k  Û(M_k,q) − λ · Ĉ(M_k, s)     # explicit U − λC
```

**Map to Eq. (2).** *Exact and literal.* This is the U−λC objective with `U := Û`
and `C := Ĉ`. This is the same object as target **F** in `06 §1`.

**Advantages** [O]:
- **λ is a run-time knob**; `s` enters at inference → the router **reacts to live
  bandwidth/RTT/server-load with no retraining**. This is the property that turns
  the work into a networked-systems result: the *same* learned utility model,
  swept across measured network conditions, produces the latency/byte/cost curves
  in `15` [S: recommended-experiment §6; 14].
- **Interpretable and separately debuggable**: the learned part is validated by
  calibration (`06 §4`); the cost part is validated by direct measurement on the
  testbed (`10`).
- **Adaptable**: the cost table for a *new* model/action is just measured; the
  utility head is extended per `06 §1` C. Retraining requirement: **low–moderate**.

**Disadvantages** [O]:
- Cannot capture true query×network interactions (assumes the cost is
  query-independent given length/action). For most of `C` this holds; where it
  does not (e.g. a query whose *output length* depends on difficulty, changing
  `c_lat`), the length can be predicted and fed into `Ĉ` — a small regressor, not
  a change of architecture [P].
- Requires a trustworthy measured cost table → depends on the testbed existing
  (`10`, `14`).

**Assessment.** This is the approach that best fits the manuscript's own equation
and the SIGCOMM framing. **[O]** It is the one we carry as the reference design in
`12`.

---

## 3. S3 — Two learned predictors: quality **and** system cost

**Idea.** As S2, but the cost (or its uncertain parts, e.g. latency under load) is
*predicted* by a second learned model instead of read from a static table.

```
Û(M_k, q)      = f_θ(q, M_k)                     # learned quality
Ĉ(M_k, q, s)   = g_φ(M_k, q, s)                  # learned cost/latency predictor
R = argmax_k   Û − λ · Ĉ
```

**Map to Eq. (2).** Same explicit U−λC as S2; the only change is that `Ĉ` is
learned. λ stays a run-time knob.

**Advantages** [O]:
- Handles cost that genuinely depends on `q` (output length, split-depth
  activation size as a function of prompt) and on hard-to-instrument state
  (predicted server queueing latency).
- Still modular: the two models are trained and calibrated separately.

**Disadvantages** [O]:
- A second labelling target: needs **measured** latency/bytes labels from the
  testbed to train `g_φ` → strictly more data than S2, and the testbed must exist
  first.
- Two calibration problems instead of one; error compounds in the argmax.
- Retraining requirement: **moderate** (`g_φ` may need re-fitting when hardware
  changes, but `f_θ` does not).

**When defensible.** When the cost is stochastic/queue-dependent enough that a
static measured table (S2) is a bad approximation — plausibly true for
`server_load` and tail latency, which is exactly the SIGCOMM-interesting regime.
A reasonable **hybrid** is S2 for the deterministic cost terms (bytes, base
TTFT) + S3's `g_φ` only for the queueing/tail term. **[P]**

---

## 4. S4 — Systems-only policy (baseline, not a router of the paper)

**Idea.** No learned query utility. Decide by system state alone.

```
R(s) = argmax_a  U_const(a) − λ · Ĉ(a, s)
```
e.g. lowest-estimated-latency path, bandwidth-threshold, RTT-threshold,
cost-minimising rule [S: brief §12 system baselines].

**Map to Eq. (2).** A degenerate case where `U` is a per-action constant
independent of `q` — so it is *not* query-aware and is **not** the manuscript's
router (Eq. 3 requires `f_θ(q,·)`).

**Role.** **Baseline, not a candidate.** Its purpose is to answer the paper's most
dangerous reviewer question (brief §13, §22 C; H3 in recommended-experiment §6):
*does query-aware routing add anything over a good systems rule?* If S4 matches the
learned router on the eventual Split testbed, the contribution collapses to a
systems policy and the paper must lean on N1/N2 novelty [S: 03 §3;
gap-assessment]. S4 must therefore be strong, not a straw man. **[O]**

---

## 5. Comparison (S1–S4)

Ratings **[O]**; `+` favourable, `~` moderate, `−` unfavourable.

| Criterion | S1 joint net | S2 util + measured C | S3 util + learned C | S4 systems-only |
|---|---|---|---|---|
| Maps literally to U−λC | ~ (implicit) | **+** | **+** | + (no query U) |
| λ a run-time knob | − | **+** | **+** | + |
| Reacts to live `s` w/o retrain | ~ (in-support only) | **+** | **+** | **+** |
| Extrapolates to unseen network | − [E] | **+** (rule is explicit) | ~ | + |
| Query-aware (is it the paper's router?) | + | + | + | **−** |
| Interpretable U vs C curve | − | **+** | ~ | + |
| New-model / new-hardware add | − retrain | + measure | ~ refit g_φ | + |
| Extra labels beyond `06` utility | none | measured cost table | + latency labels | none |
| Depends on testbed existing | for eval | for C table | **for training** | for C |
| SIGCOMM story strength | ~ | **+** | + | baseline only |
| Retraining burden | high | **low** | moderate | none |

**Reviewer-pass note (brief §22 A/C).** S2 and S3 are the two that are *both*
faithful to Eq. (2)–(3) *and* produce a networked-systems effect (the learned
utility is swept across measured network conditions to yield latency/byte/cost
curves). S1 risks looking like a black-box classifier and extrapolates poorly;
S4 is not query-aware and so cannot be the paper's router — it is the baseline that
makes the query-awareness claim falsifiable. No approach changes the research
question. **[O]**

---

## 6. How each maps to the candidate architectures and to `06` targets

| | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| Compatible arch (`02`) | A/B/D | **B, C, D** (utility head) | **D** (multi-head) | none learned |
| Required `06` target | B or E (bakes λ) | **C / F** | **C/F + measured latency** | — |
| λ knob | frozen | run-time | run-time | run-time |

The chain is: architecture (`02`) → utility target (`06 §1` C/F) → cost placement
(`07` S2/S3). The **coherent reference stack** for the SIGCOMM framing is
**D-backbone (or B) → utility-regression labels (C/F) → S2 cost integration,
with S3 for the tail-latency term**, and **S4 as the mandatory systems baseline**.
**[P]** — the advisor confirms; this is not decided here.

---

## 7. Formal statement of the run-time decision (reference, S2/S3)

For completeness, the inference-time rule the testbed will exercise (`15`):

```
given q, and live state s_t at time t:
  for each admissible action a ∈ {EDGE, SPLIT(d): d∈D, CLOUD}:
      Û_a  = f_θ(q, a)                    # calibrated to P(correct) or graded utility
      Ĉ_a  = w·[c_comp(a), c_comm(a,s_t), c_lat(a,s_t), c_mem(a), c_op(a)]   # S2 measured / S3 g_φ
  a* = argmax_a  Û_a − λ · Ĉ_a
  (optional) if max_a Û_a < τ_abstain:  a* = ABSTAIN/ESCALATE
```

Sweeping `s_t` (bandwidth, RTT, server load) with **fixed θ and fixed labels**
produces every dependent-variable curve in `15` — this is precisely the
"networked-systems effect, not classification accuracy" evidence the brief
requires (§13, §22 C), and it is only possible under S2/S3, not S1/E. **[O]**

Hand-offs: the measured cost quantities are specified as testbed measurements in
`10-lab-requirements.md`; the sweep grid is `15-sigcomm-experiment-matrix.md`; the
falsification of query-awareness vs S4 is H3 in `08-experiment-design.md`.
