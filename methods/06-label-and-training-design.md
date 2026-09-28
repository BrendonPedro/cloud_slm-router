# 06 — Label and Training-Target Design

*Method-selection sprint, iteration 4. This is a planning document. Nothing here
has been trained, run, or measured by us. Every accuracy/headroom figure is
quoted from an earlier primary-checked deliverable with a pointer, or is marked
as an untested expectation. This document does **not** decide the training
target — it lays out the options so the advisor can.*

Evidence tags (same convention as `02-candidate-methods.md`):

- **[S: …]** sourced; the record is in the cited earlier deliverable / file.
- **[M]** measured from the released LLMRouterBench bundle (raw file named in
  the cited deliverable).
- **[O]** our analysis. **[P]** our design proposal, not established practice.
- **[E]** an untested expectation; needs measurement before it can be claimed.

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-checked
this iteration). `paper/main-revised.tex` is unchanged.

---

## 0. Why the training target is the pivotal methodological choice

The fixed problem (`00-scope-lock.md`) is:

- Eq. (1) `R : Q → M`
- Eq. (2) `max_R E_q[ U(R(q),q) − λ·C(R(q),q) ]`
- Eq. (3) `R(q) = argmax_{M_k ∈ M} f_θ(q, M_k)`

`02-candidate-methods.md` fixes the *architecture* of `f_θ` (A/B/C/D). This
document fixes the **supervision signal**: what number `f_θ` is trained to
produce, and where the labels come from. The two choices are largely orthogonal —
almost any architecture (B, C, D; A with a verbaliser) can be trained against any
target below. So the label design is a **separate advisor decision** from the
architecture decision, and it is the one that most directly determines:

1. whether the router can be **added to / extended for a new model** without a
   fresh labelling campaign (§10 of the brief);
2. how many **GPU inference calls** the label pipeline costs (§11 of the brief);
3. whether the output is **calibrated** enough to move an operating point under
   changing `λ` or changing network state (needed for the SIGCOMM systems story,
   `03 §3`, `07`).

A structural fact from the released data governs everything below: with
Llama-3.1-8B as the edge model the pool is nearly **nested** (`weak_better`
≤ 0.08 on every binary split) [M: recommended-experiment §2.1], so most targets
collapse to "detect the queries the edge already answers correctly". With
Qwen3-8B the pool is **complementary** (edge beats strong on 11.3% of
LiveCodeBench) [M], so richer targets (C/D/E below) can in principle *raise*
quality, not just save cost. The label target should be chosen knowing which
regime the eventual pool is in — an advisor/model-pool question, not something we
can settle here.

---

## 1. The six formulations (brief §8)

Notation: `q` a query; `M_k` a candidate action/model in
`𝒜 = {EDGE_SLM, SPLIT(d), CLOUD_LLM, ABSTAIN}`; `y(M_k,q)` the graded quality of
`M_k`'s answer on `q` (correctness for QA/exact-match datasets; judge score for
open-ended); `s` the live system state (`07`).

### A. Binary classification — EDGE vs STRONG/SPLIT

- **Predict:** `p̂(edge suffices | q)`, threshold at `τ`.
- **Label:** `1` if `y(edge,q) ≥ y(strong,q)` (a "weak ≥ strong" label), or the
  stricter `y(edge,q) = correct` ("weak correct"). Both are cheap: two model
  runs per query [O]. Stage 0 already builds them from released scores with **no
  inference** on the 7–9B→235B pool [S: recommended-experiment §4].
- **Map to Eq. (2)–(3):** monotone reduction of the argmax when `𝒜 = {EDGE,
  ESCALATE}`. `f_θ(q,EDGE) = p̂`, `f_θ(q,ESCALATE) = 1−p̂ + (bias set by λ)`;
  the threshold `τ(λ)` *is* the U−λC trade-off knob [S: 02 §0 "binary
  sufficiency"].
- **Multi-model:** no. Two actions only. A third model needs a re-definition of
  the label and, in general, retraining.
- **Adaptability:** poor. Adding an SLM or a Split path is not expressible.
- **Calibration:** straightforward — one scalar; Platt/temperature scaling and
  ECE/Brier are standard [S: recommended-experiment §5.3].
- **Training / inference cost:** lowest of all six. Single sigmoid head; a TF-IDF+LR
  or a small encoder suffices [S: recommended-experiment §5].
- **Robustness:** the "weak ≥ strong" label leaks dataset identity when
  headroom is dataset-correlated [M: §2.2 item 3]; must be checked with the
  leave-one-dataset-out protocol [S: recommended-experiment §4].
- **SIGCOMM suitability:** supports the cleanest systems claim — *cloud-call
  rate at matched quality* [S: recommended-experiment §2.2 item 1] — but only for
  a two-way decision; cannot express activation-byte / split-depth trade-offs.

### B. Multiclass routing — SLM_1 … SPLIT_1 …

- **Predict:** a softmax over the concrete action set; `R(q) = argmax`.
- **Label:** the argmax action under the *training-time* λ, i.e.
  `argmax_k [ y(M_k,q) − λ·C(M_k,·) ]`, computed after running every candidate on
  every query.
- **Map to Eq. (2)–(3):** direct — the class scores *are* `f_θ(q,M_k)`. But λ is
  **baked into the labels**: changing the cost weight or the network state means
  relabelling and retraining. This is the formulation's core weakness against the
  U−λC framing, which wants λ to be a run-time knob.
- **Multi-model:** yes, but with a **fixed** class count. Adding a model changes
  the output dimension → new head → retrain [O].
- **Adaptability:** poor for evolving pools (the brief's requirement D). The
  manuscript's "heterogeneous/evolving pool" claim is *not* well served here;
  say so rather than preserving it [S: 00-scope-lock; brief §10].
- **Calibration:** multiclass calibration is harder (per-class temperature,
  Dirichlet); a mis-calibrated softmax cannot be re-thresholded for a new λ.
- **Cost:** K model runs per query for labels (K = pool size); moderate training.
- **SIGCOMM suitability:** weak — the class boundary hides the continuous
  cost/quality curve reviewers want.

### C. Utility regression — predict `y(M_k,q)` per candidate

- **Predict:** `Û(M_k,q)` for each `M_k` (a regression head, model-conditioned by
  a model profile/embedding — this is candidate **D**'s backbone [S: 02 §4]).
- **Label:** the graded quality `y(M_k,q)` itself (continuous, or the binary
  correctness treated as a regression target / BCE).
- **Map to Eq. (2)–(3):** the cleanest of all. `f_θ(q,M_k) := Û(M_k,q)`, and the
  **cost enters only at inference** via `argmax_k Û(M_k,q) − λ·C(M_k,s)`
  [S: 02 §0 "utility-then-cost"]. λ and `s` are run-time knobs; **no retraining**
  to re-weight cost or react to the network.
- **Multi-model:** yes, and this is its key advantage — a per-model head or a
  model-embedding input means a **new model can be added by supplying its
  profile + a small calibration set**, not by retraining the query encoder
  [S: 02 §4 "How a new model is added"; brief §10]. Whether that is cheap in
  practice is [E] and is exactly hypothesis-worthy (does zero/few-shot model
  addition hold its accuracy?).
- **Calibration:** per-model reliability curves; the regression output can be
  calibrated to a probability of correctness. Richer but more work than binary.
- **Cost:** labels need every model on (a subset of) queries — K runs/query,
  same as multiclass, but the labels are **reusable across λ and across method
  candidates** [S: recommended-experiment §6 ablation 1]. This is a real saving:
  one labelling campaign serves A/B/C/D and every λ.
- **Robustness / SIGCOMM:** best supports the continuous quality–cost curve and
  the "raise quality on complementary pools" story (Qwen3-8B regime) [M: §2.2
  item 2].

### D. Pairwise gain — predict `ΔU = U(strong,q) − U(weak,q)`

- **Predict:** a single signed scalar per (weak,strong) pair.
- **Label:** `y(strong,q) − y(weak,q)`, from the same two runs as target A.
- **Map to Eq. (2)–(3):** escalate iff `ΔÛ > λ·ΔC`. A one-pair specialisation of
  C; `f_θ(q,ESCALATE) − f_θ(q,EDGE) = ΔÛ`.
- **Multi-model:** one head per ordered pair → `O(K²)` heads; does not scale to a
  large pool but is natural for the manuscript's **edge-vs-strong** core decision.
- **Adaptability:** poor beyond the trained pair.
- **Calibration / cost / SIGCOMM:** between A and C. The signed target often
  learns the *cost-saving* margin more sample-efficiently than absolute utility
  regression on nested pools [O]; worth an ablation [S: recommended-experiment §6
  ablation 1 already lists a soft `score_strong − score_weak` label].

### E. Direct utility-cost score — predict `U(M_k,q) − λ·C(M_k,q)`

- **Predict:** the final objective value directly.
- **Label:** `y(M_k,q) − λ·C(M_k,q)`, requiring a *chosen* λ and a cost table at
  labelling time.
- **Map to Eq. (2):** literal — `f_θ` *is* the objective. But this **bakes both λ
  and the (static) cost model into the weights**, so it inherits multiclass's
  worst property: any change to λ, to the cost table, or to live network state
  requires relabelling. For a systems paper whose whole point is reacting to
  *changing* network conditions, this is the least attractive target [O].
- **Use:** acceptable only if λ and the cost structure are genuinely fixed for the
  deployment — which contradicts the manuscript's system-awareness requirement C
  [S: 00-scope-lock].

### F. Separated quality and measured system cost

- **Predict:** `Û(M_k,q)` (learned, from queries only), and **measure or
  separately predict** `Ĉ(M_k,s)` from the live system.
- **Decision:** `argmax_k Û(M_k,q) − λ·Ĉ(M_k,s)`.
- This is **target C's output plus an explicit, non-learned (or separately
  learned) cost module**. It is the same object as system-integration approach
  **S2/S3** in `07`, and it is the target that maps most faithfully to the
  manuscript's Eq. (2) while keeping λ and `s` at run time.
- **Cost/adaptability/SIGCOMM:** inherits C's advantages; adds the requirement of
  a measured cost table (activation bytes, RTT, TTFT/TPOT) that the SIGCOMM
  testbed produces anyway [S: recommended-experiment §6 H3; `07`, `14`, `15`].

---

## 2. Comparison matrix (targets × criteria)

Ratings are **[O]** unless a cell cites a source. `+` good / low cost, `~`
moderate, `−` poor / high cost, for the router's benefit.

| Criterion | A binary | B multiclass | C utility-reg | D pairwise | E direct U−λC | F separated |
|---|---|---|---|---|---|---|
| Label cost (runs/query) | 2 | K | K (reusable) | 2 | K + cost table | K + measured cost |
| Maps cleanly to Eq. (3) | ~ (2-action) | + | **+** | ~ (pairwise) | + (literal Eq.2) | **+** |
| λ is a **run-time** knob | + (τ) | − (baked) | **+** | + | − (baked) | **+** |
| Reacts to live `s` w/o retrain | − | − | + (via cost) | ~ | − | **+** |
| Multi-model / K>2 | − | + fixed-K | **+** | − O(K²) | + fixed-K | **+** |
| Cheap new-model add | − | − | **+ [E]** | − | − | **+ [E]** |
| Calibration difficulty | + easy | − hard | ~ | ~ | ~ | ~ |
| Training complexity | + | ~ | ~ | + | ~ | ~ |
| Inference complexity | + | + | ~ (K heads) | + | + | ~ |
| Split-depth expressible | − | ~ (as classes) | + (as actions) | − | + | **+** |
| SIGCOMM curve story | ~ (CCR only) | − | + | ~ | ~ | **+** |
| Robust to dataset-ID leak | − [M §2.2] | − | ~ | ~ | ~ | ~ |

Reviewer-pass note (brief §22 A): **every** target above still solves the
original problem — each defines `f_θ` and selects by U−λC. None changes the
research question. Targets differ only in *how much of the U−λC structure is
learned vs supplied at inference* [O].

---

## 3. Label-sharing and pipeline economics (brief §8 item 8, §11)

The single most consequential practical finding: **targets A, C, D, E, F can all
be derived from one labelling campaign** — the per-(model, query) quality scores
`y(M_k,q)`. Only the *loss* differs. Therefore:

- Run every candidate model once per query, store `y(M_k,q)` in the
  LLMRouterBench record format [S: reproducibility-plan §7 step 4]. From that one
  table: binary = threshold, pairwise = subtract, utility = regress,
  direct/separated = combine with a cost table.
- Multiclass (B) is the exception only in that its *class definition* bakes λ;
  the underlying `y` table is the same.
- Consequence for cost: the number of GPU inference calls is set by the **pool
  size K and query count N**, *not* by how many targets we compare. This makes an
  A-vs-C-vs-D ablation nearly free once labels exist [S: recommended-experiment §6
  ablation 1 already schedules this].
- Storage/inference formulas (no fabricated totals — the pool is unresolved):
  calls `≈ N · K` for QA/exact-match; `+ N · K` judge calls for open-ended
  (SimpleQA uses an LLM judge [S: reproducibility-plan §2]). With the Stage-0
  pool N ≈ 2,432 and K = 2 the labels already exist for free from released scores
  [M]; the manuscript's own 8-model pool on SimpleQA does **not** exist in the
  bundle and must be generated — a Stage-1 GPU job
  [S: recommended-experiment §1, §8].

---

## 4. Calibration (required by the brief for every target)

Calibration is not optional here: the U−λC decision moves an operating point, so
`f_θ`'s output must be a trustworthy probability/utility, especially **out of
domain** where LLMRouterBench routers degrade [M: §2.2 item 3].

- **Binary (A):** temperature/Platt scaling; report ECE (15-bin), Brier, and AURC
  for the selective "stay on edge" decision [S: recommended-experiment §5.3].
- **Utility/separated (C/F):** per-model reliability curves + a monotone
  post-hoc map from `Û` to P(correct); this is what lets the argmax be trusted
  across models.
- **Multiclass/direct (B/E):** hardest; a re-thresholding for a new λ is not even
  possible without relabelling, so calibration cannot rescue a λ change.
- **Cross-domain calibration is a candidate contribution axis** (N2 in
  `gap-assessment` / `03 §3`): "calibrated routing under domain shift" is a
  defensible novelty that most prior routers do not claim [S: 03 §3].

---

## 5. What to DISCUSS with the advisor (not decide here)

Presented as questions, per the brief's instruction not to pretend the choice is
approved (these feed `11-advisor-questions.md` group D):

1. **Is the eventual pool nested or complementary?** (Determines whether the
   target should optimise cost-saving only (A/D) or also quality gain (C/F).)
   Depends on the model-pool decision [S: reproducibility-plan §5, the Qwen3-72B
   and Gemma naming issues are unresolved].
2. **Must λ / cost be a run-time knob?** If the SIGCOMM story is "reacts to
   changing bandwidth/RTT", then targets that bake λ (B, E) are ruled out and the
   choice narrows to **C or F** [O].
3. **How many models must the router support at once, and how often does the pool
   change?** A static 2–3 model pool tolerates A/D; an evolving pool needs C/F's
   model-conditioning [brief §10].
4. **Which quality metric defines `y`?** Exact-match/correctness vs LLM-judge
   score changes label cost and reproducibility (judge model must be pinned
   [S: reproducibility-plan §2]).
5. **Is a soft label (`score_strong − score_weak`) acceptable, or must labels be
   binary correctness?** Already an ablation [S: recommended-experiment §6].

## 6. Our reading (proposal, for discussion — brief §22)

- The target that **best fits the manuscript's own Eq. (2) and system-awareness
  requirement** is **F (separated utility + measured cost)**, with **C
  (utility regression)** as its learning core, because it keeps λ and live `s` at
  inference and supports cheap-ish new-model addition. **[P]**
- The target that is **cheapest to falsify first** is **A (binary, "weak ≥
  strong")**, because Stage-0 labels already exist with no inference and it
  answers H1 (does a learned router beat simple baselines at all?) before any
  expensive pool labelling [S: recommended-experiment §2, §9]. **[P]**
- **D (pairwise gain)** is the sample-efficient middle option for the core
  edge-vs-strong decision and is worth carrying as an ablation of A/C. **[P]**
- **B and E are not recommended as the primary target** because both bake λ into
  the weights and so cannot express the "react to changing network state" claim
  that gives the paper its SIGCOMM identity — but B remains a legitimate baseline
  and E a sanity-check upper bound at a fixed λ. **[O]**

These are proposals; the advisor chooses. Every option above preserves
`R(q) = argmax f_θ` and `U − λC`. Hand-off: the cost side of F is specified in
`07-system-cost-integration.md`; the labelling economics feed
`08-experiment-design.md` and `09-implementation-roadmaps.md`.
