# methods-v2 / 15 — Architecture figure specification

*Deliverable for `MICROENCODER_KD_BRIEF.md` §21 (architecture figure
specification) and the §16 "publication-quality figure specification" item.
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 16).*

## 0. Purpose, grounding, and sourcing

This file is the **drawing contract** for the paper's main architecture figure. It
turns the ASCII diagram and the learned/measured/training-only partition already
locked in `06-proposed-method` §4/§8 into an unambiguous, implementable figure
specification: panels, nodes, edges, labels, a visual-encoding legend, layout
geometry, colour/line conventions, and a caption. A companion
`architecture-figure.tex` (TikZ source) renders this spec; this `.md` is the
authority and the `.tex` is one faithful rendering of it.

**Reuse, not re-research.** Every element here is inherited from `06` (method),
`07` (labels), `08` (cost), `09` (Split), `04` (teacher); no new web search was
required. This is a figure-design deliverable, not a literature deliverable.

**Evidence tags** (from `00`): `[VERIFIED]` primary source supports; `[RELATED]`
adjacent/canonical fact not re-opened; `[PROPOSED]` our design choice; `[OPEN]`
requires experiment/advisor/licence confirmation; `[S:NN]` sourced to prior
deliverable NN.

**No results in the figure.** Per brief §20/§26 the figure carries **no** numbers
that would read as measured (no latencies, no accuracies, no byte counts, no
"×faster"). Every quantity shown is a symbol (`Û_θ`, `C`, `λ`, `d`), never a
value. Any slot that might later hold a measured number is drawn as a labelled
placeholder, not a number. `[S:06 §9]`

---

## 1. What the figure must show (brief §21 checklist)

The brief fixes the content. The figure **must** make all of the following legible
at a glance:

1. **TRAINING:** teacher + observed outcomes → distilled student. `[S:06 §5]`
2. **INFERENCE:** query → micro-encoder → utility; **plus** live system state →
   cost; **then** decision → Edge / Split / Strong. `[S:06 §6]`
3. **Distinct visual treatment** for three channels that must never be confused:
   - the **learned / training-only** path (teacher, soft targets, KD loss),
   - the **inference** path (student forward pass, routing rule, dispatch),
   - the **measured system values** (live `C(a|s)` and its inputs). `[S:06 §4]`

The single most important readability goal: a reviewer must see **at a glance that
the teacher is gone at inference** and that **system cost is never inside the
student**. These two facts are the N3 separation lane and the "lightweight at
inference" requirement, and the figure is where they are won or lost. `[S:11, S:06 §4]`

---

## 2. Visual encoding legend (the three channels + two value types)

This legend is **normative**: every node and edge in both panels is assigned
exactly one channel and (for value nodes) one value type. The legend box appears
in the figure itself.

### 2.1 Channels (by line style + fill)

| Channel | Line style | Node fill | Appears in | Meaning |
|---|---|---|---|---|
| **Training-only** | **dashed** outline, grey | light grey fill | Training panel only | Exists at train time, **discarded before deployment** (teacher, soft targets, KD loss, oracle labels). `[S:06 §4]` |
| **Inference / learned** | **solid** outline, blue | blue-tint fill | Both panels | The shipped student `g_θ` and everything it computes (`h(q)`, `Û_θ`). Blue = the manuscript's "Proposed Solution" colour convention (`proposed-solution-blue.tex`). `[S:06 §3]` |
| **Measured system value** | **solid** outline, **double/bold** border, orange | orange-tint fill | Inference panel only | Live quantities measured at runtime, **outside θ** (`s`, `C(a|s)` and its inputs). `[S:08]` |

### 2.2 Value-type decoration (a small corner glyph on value nodes)

To reinforce brief §16's "distinguish learned values vs measured values":

- **Learned value** (`Û_θ(a|q)`): blue node, small **"θ"** superscript glyph in the
  corner → "comes from the weights."
- **Measured value** (`C(a|s)`, `s`): orange node, small **gauge/meter** glyph in
  the corner → "read from a live monitor." `[PROPOSED]`

### 2.3 Edge semantics (arrowheads)

- **Data-flow arrow** (solid filled head): a tensor/scalar flows along it.
- **Supervision/KD arrow** (open head, dashed): a *loss* pulls the student toward a
  target (teacher soft target, hard label). Labelled with its loss term and weight
  (`(1−α)·L_KD`, `α·L_task`). `[S:06 §5]`
- **"Discarded" scissors marker** on the boundary between panels, cutting the
  teacher's edges, to visually assert the teacher does not cross into inference.
  `[PROPOSED]`

---

## 3. Panel layout (two stacked panels, shared horizontal flow)

The figure is **one figure, two panels**, stacked vertically, each spanning the
column/page width, with a labelled horizontal divider between them. Flow is
**top-to-bottom within each panel** and the panels read **training (top) →
inference (bottom)**, matching `06` §8.

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  PANEL A — TRAINING  (lab GPU; training-only components dashed-grey)        │
 │  …nodes per §4…                                                            │
 └──────────────────────────────────────────────────────────────────────────┘
      ─ ─ ─ ─ ─ ─ ─ ─ ─  "ship θ only · teacher discarded"  ✂  ─ ─ ─ ─ ─ ─ ─ ─
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  PANEL B — INFERENCE  (edge device; learned=blue, measured=orange)          │
 │  …nodes per §5…                                                            │
 └──────────────────────────────────────────────────────────────────────────┘
      LEGEND (per §2):  ▢ dashed-grey = training-only · ▢ blue = learned (θ) ·
                        ▣ orange = measured live · →KD = supervision arrow
```

The divider line carries the text **"ship θ only — teacher discarded"** and the
scissors glyph, so the discard is impossible to miss. The student node appears in
**both** panels (same blue shape) to show it is the one artifact that survives the
cut. `[PROPOSED, S:06 §4]`

---

## 4. PANEL A — Training (node + edge list)

Nodes (id · label · channel · shape):

- **A1** · `query set {qᵢ}` · neutral (white, solid thin) · rounded rectangle.
- **A2** · `OBSERVED PER-ACTION OUTCOMES  y(a,q)` with sub-label
  *"= oracle T4 = GROUND TRUTH, not a teacher"* · **training-only (dashed-grey)** ·
  cylinder (datastore). Sub-note: *"judge / strong model = label SOURCE"*. `[S:04 §4, S:07]`
- **A3** · `TEACHER ROUTER  T1 — ModernBERT-large (~395M)` · **training-only
  (dashed-grey)** · rectangle. Corner tag: *"training-only"*. `[S:04, S:05]`
- **A4** · `STUDENT — ModernBERT-base (~149M) + N heads`, body line
  `Û_θ(a|q)=σ(wₐᵀh+b)` · **learned (blue)** · rectangle (bold). This is the shared
  node that also appears as B2. `[S:05, S:06 §3]`
- **A5** · `KD-5 LOSS  L = α·L_task(Û_θ,y) + (1−α)·L_KD(Û_θ,Û_T) [+ γ·L_repr]` ·
  **training-only (dashed-grey)** · hexagon (operator). Annotation badge:
  **"α=1 ⇒ non-distilled control (E1)"**. `[S:06 §5, S:03]`
- **A6** · `calibrate heads (temperature / isotonic)` · learned (blue, thin) ·
  rounded rectangle. `[S:07, S:08]`

Edges:

1. A1 → A2  (data-flow, solid): queries are run through the pool to produce
   outcomes.
2. A1 → A3  (data-flow, solid): queries fed to the teacher.
3. A1 → A4  (data-flow, solid): queries fed to the student.
4. A2 → A5  (supervision, dashed open head) labelled **`α·L_task` (hard labels)**.
5. A3 → A5  (supervision, dashed open head) labelled **`(1−α)·L_KD` (soft `Û_T`)**.
   This arrow carries the KD; it is the line a reader traces to understand "what is
   distilled." `[S:06 §5]`
6. A4 → A5  (data-flow, solid): student predictions enter the loss.
7. A5 → A4  (gradient, solid, curved back) labelled **`θ ← θ − η∇L`**.
8. A3 ⇢ A4  (optional, thin dashed, open head) labelled **`γ·L_repr` (KD-4,
   same-family only)** — drawn faint to signal "optional ablation, not core."
   `[S:03, S:06 §5]`
9. A4 → A6  (data-flow, solid): trained student goes to calibration.

**Teacher-is-training-only cue:** A3 and A2 and A5 are all dashed-grey; only A4/A6
(blue) cross the divider. `[S:06 §4]`

---

## 5. PANEL B — Inference (node + edge list)

Nodes:

- **B1** · `query q` · neutral · rounded rectangle (top-left).
- **B2** · `STUDENT g_θ — 1 forward pass, INT8/ONNX`, body `h(q)=Pool(ModernBERT_θ(q))`
  · **learned (blue, bold)** · rectangle. Same shape as A4. `[S:05 R6, S:06 §6]`
- **B3** · `Û_θ(a|q)  for a∈𝒜` · **learned value (blue, "θ" glyph)** · parallelogram
  (value). `[S:06 §3]`
- **B4** · `live system state s` with sub-label
  *"bw · RTT · contention · act-bytes · TTFT/TPOT · compute-lat · mem"* ·
  **measured (orange, gauge glyph)** · parallelogram. `[S:08]`
- **B5** · `C(a|s)  for a∈𝒜` with sub-label *"scalarized cost (S1–S4), outside θ"* ·
  **measured value (orange, gauge glyph)** · parallelogram. `[S:08]`
- **B6** · `a* = argmax_a [ Û_θ(a|q) − λ·C(a|s) ]   (Eq. 4)` · decision operator ·
  **diamond**, half-blue / half-orange fill to show it fuses a learned term and a
  measured term. Side badge: **`λ set at runtime (swept E5)`**. `[S:06 §3.2]`
- **B7a** · `EDGE_SLM — run small model locally` · dispatch · rounded rectangle.
- **B7b** · `SPLIT(d) — run [0,d) local → send activation → server runs [d,L)` ·
  dispatch · rounded rectangle. Sub-label: *"activation bytes(d) feed C(SPLIT(d)|s)
  — 09"*. `[S:09]`
- **B7c** · `STRONG / CLOUD — full remote execution` · dispatch · rounded rectangle.
- **B8** · (optional, faint dashed) `log (q,a*,Û,C,outcome) → journal CL (13)` ·
  training-only-style dashed-grey · small note box. Explicitly labelled
  *"logging only; no conference-core effect"*. `[S:06 §6, S:13]`

Edges:

1. B1 → B2 (data-flow): query to student.
2. B2 → B3 (data-flow): forward pass produces per-action utilities.
3. B4 → B5 (data-flow, **orange**): live state scalarized into cost.
4. B3 → B6 (data-flow, **blue**) labelled **`Û_θ(a|q)` (learned term)**.
5. B5 → B6 (data-flow, **orange**) labelled **`−λ·C(a|s)` (measured term)**.
   Edges 4 and 5 **meet at the diamond** — the visual heart of the decoupled
   design: one blue line and one orange line converging, never crossing into each
   other's node. `[S:06 §3.2, S:11 N3]`
6. B6 → B7a / B6 → B7b / B6 → B7c (dispatch, solid, one chosen): the argmax selects
   exactly one path; draw all three outgoing but style the three equally (do not
   pre-select a "winner," since that would imply a result). `[S:06 §9]`
7. B6 ⇢ B8 (optional, faint dashed): the journal logging hook.

**Measured-is-outside-θ cue:** B4 and B5 are the only orange nodes; no orange edge
ever enters B2 or B3 (the student). This is the figure-level proof that `s` is not
in the weights. `[S:06 §4, S:11 N3]`

---

## 6. Layout geometry and sizing

- **Format:** vector (PDF/EPS via TikZ). Must remain legible at single-column
  width (~3.3 in / ~8.4 cm) and scale to double-column/page-width without raster
  blur. Target aspect ratio ≈ 3:4 (taller than wide) given two stacked panels;
  if the venue column is narrow, the two panels may be allowed to break to a
  full-page-width `figure*`. `[PROPOSED, OPEN — venue unknown, 16]`
- **Flow direction:** top→bottom in each panel; the shared student node sits at the
  panel boundary so its blue shape literally straddles the divider.
- **Node spacing:** uniform vertical rhythm; align A4 (student, training) directly
  above B2 (student, inference) on the same x so the eye tracks the surviving
  artifact down through the scissors line.
- **Colour (see §7 for accessibility):** training-only = grey `#9AA0A6`; learned =
  blue `#1A56DB` (the manuscript blue); measured = orange `#E8820C`; neutral =
  white with thin black outline.
- **Fonts:** match the manuscript body font; math set in the manuscript math font;
  minimum effective size ≥ 7 pt after final scaling.
- **Line weights:** dashed-grey 0.6 pt; solid-blue 1.0 pt; measured-orange
  double/bold 1.2 pt; supervision/KD arrows 0.8 pt open-head.

---

## 7. Accessibility and print-robustness (do not rely on colour alone)

Because many readers print greyscale or are colour-vision-deficient, **channel is
encoded redundantly** by line style + fill + an explicit text/corner tag, never by
hue alone (`dataviz` guidance; brief §21 "different visual treatment"):

- training-only = **dashed** + grey + *"training-only"* tag,
- learned = **solid** + blue + *"θ"* glyph,
- measured = **solid bold/double** + orange + **gauge** glyph.

In pure greyscale the three are still distinguishable by **dashed vs solid vs
bold-double** outlines and by the θ / gauge glyphs. `[PROPOSED]`

---

## 8. Caption (draft, no results)

> **Figure X. Distilled micro-encoder router: training and inference.**
> *Training (top, dashed-grey = training-only):* queries produce observed
> per-action outcomes `y(a,q)` (ground truth; a judge or strong model is only a
> label source, not a teacher) and are scored by a larger same-family teacher
> router (ModernBERT-large). The student micro-encoder (ModernBERT-base + N
> per-action utility heads) is trained with the KD-5 hybrid loss
> `L = α·L_task(Û_θ,y) + (1−α)·L_KD(Û_θ,Û_T)`; `α=1` recovers the non-distilled
> control. The teacher is discarded after training.
> *Inference (bottom, blue = learned in θ, orange = measured live):* a single
> encoder forward pass yields per-action calibrated utilities `Û_θ(a|q)`; these are
> combined with the separately **measured** runtime cost `C(a|s)` via
> `a* = argmax_a[Û_θ(a|q) − λ·C(a|s)]` to dispatch to Edge, Split(d), or
> Strong/Cloud. System cost is never inside the student weights.
> *No quantities in this figure are measured results.*

The caption states the learned/measured separation in words so the figure is
self-contained for a skimming reviewer. `[S:06, S:08, S:11]`

---

## 9. Build / integration notes for the `.tex`

- The companion `architecture-figure.tex` is a **standalone-compilable** TikZ
  document (`\documentclass[tikz]{standalone}` + `\usepackage{xcolor}`), so it can
  be previewed on its own and `\input`/`\includegraphics` into the manuscript
  later. It defines three named colours (`trainonly`, `learned`, `measured`)
  and three node styles so the §2 legend is enforced by style, not by hand.
- Do **not** `\input` it into `source/main-original.tex` in this sprint (brief §20
  forbids modifying the manuscript). It is a methods-v2 asset only.
- The figure uses only `xcolor` + base TikZ (`positioning`, `shapes.geometric`,
  `arrows.meta`, `fit`) so it compiles without exotic packages.
- If the venue is single-column and the figure is too tall, the fallback is to
  render the two panels side-by-side (training left, inference right) with the
  divider rotated to vertical; the node/edge/legend content is unchanged. `[OPEN —
  venue unknown, 16]`

---

## 10. Checklist: does the figure satisfy the brief?

| Brief §21 requirement | Where satisfied |
|---|---|
| TRAINING: teacher + observed outcomes → distilled student | Panel A (§4), edges A2→A5, A3→A5, A5→A4 |
| INFERENCE: query → micro-encoder → utility | Panel B (§5), B1→B2→B3 |
| plus live system state → cost | B4→B5 (orange) |
| then decision → Edge/Split/Strong | B6→B7a/b/c |
| distinct visual treatment: learned/training-only path | dashed-grey channel (§2.1) |
| distinct visual treatment: inference path | solid-blue channel (§2.1) |
| distinct visual treatment: measured system values | orange bold/double + gauge glyph (§2.1–2.2) |
| suitable for later insertion into the paper | vector/TikZ, column-scalable, standalone (§6/§9) |
| no invented results | §0, §8 caption, all nodes symbolic |

---

## 11. Hand-off

- **→ `architecture-figure.tex`:** render §2–§5 with the §6 geometry and §7
  accessibility rules; this spec is authoritative if the two disagree.
- **→ `proposed-solution-blue.tex`:** reference this figure as the Proposed
  Solution overview figure; the blue text (Eqs. 3′/4, algorithms) and this figure
  must use the same symbols (`Û_θ`, `C(a|s)`, `λ`, `𝒜`, `SPLIT(d)`).
- **→ `16-advisor-and-lab-open-questions`:** carry the `[OPEN]` items (venue →
  column width / `figure` vs `figure*`; final N and enabled split depths → node
  count in 𝒜 fan-out; edge-device name → nothing shown as measured).
- **→ `FINAL-SUMMARY` (§18):** this figure is part of the "manuscript text ready to
  insert" answer.
