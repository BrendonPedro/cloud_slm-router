# methods-v2 / FINAL-SUMMARY — Distilled micro-encoder router sprint

*Deliverable for `MICROENCODER_KD_BRIEF.md` §24/§25. Prepared 2026-10-02 (gnhf
`microencoder-kd-brie-aaf36a` sprint, iteration 20). This file answers the 20
plain-English questions of brief §25 and is the entry point to the 21 deliverables
in `methods-v2/`.*

## 0. How to read this file

Each answer below is a **synthesis** of a locked deliverable; the `→ NN` pointer
is where the full argument, sourcing, and evidence tags live. The sprint's
evidence discipline (brief §23) is preserved: `[VERIFIED]` = primary source
supports; `[RELATED]` = adjacent/canonical, not exact precedent; `[PROPOSED]` =
our design; `[OPEN]` = needs experiment/advisor/Henry confirmation. **No
experimental results are claimed anywhere** (brief §26); every performance
statement is a hypothesis routed to a named experiment in `12`.

The deliverable set is complete: `00`–`17` (markdown), `method-references.bib`,
`proposed-solution-blue.tex`, `architecture-figure.tex`, plus the optional
`architecture-figure.tex`. `source/main-original.tex` is **unmodified** (SHA
`06f5f9d7…`, git clean).

---

## 1. What did the advisor approve? (→ `00`)

At the 2026-10-01 meeting the advisor approved (CONFIRMED items, `00`):

1. **The MICRO-ENCODER family as THE proposed routing backbone** — the sprint
   stops comparing A/B/C as equal candidates.
2. **Decoupling learned semantic/model utility `Û(a|q)` from measured live system
   cost `C(a|s)`**, combined at runtime as `argmax_a[Û(a|q) − λ·C(a|s)]`.
3. Reuse of **Henry's existing lab Split-LLM code** (contents `[OPEN]`).
4. **Lab GPU resources** are available for training-only work.
5. **Two-machine use** appears available.
6. **Hidden-state self-routing (old Candidate C) is demoted to a baseline**, not
   the proposed method.
7. **Investigate knowledge distillation** to further optimize the micro-encoder
   (investigate, do not assume it is novel or that it helps).
8. **Continual learning is a possible JOURNAL extension, not the conference core.**
9. The manuscript will later gain an **architecture figure, a detailed Proposed
   Solution, and the proposed method highlighted in BLUE**.
10. **Jacobi decoding is NOT a required component.**

Eight items were left **UNRESOLVED / do-not-guess** (edge GPU, server GPU, machine
names, Henry's exact repo, link-shaping permissions, exact model pool, the
B1/SLM/"possible Gemma" note, conference-vs-journal ordering) — carried into `16`,
never invented.

## 2. What exactly is the proposed micro-encoder architecture? (→ `05`, `06`)

A **distilled ModernBERT-base encoder (~149 M params, H=768) with N parallel
scalar utility heads**, one head per routable action, deployed INT8/ONNX on the
edge. At inference it is **one encoder forward pass + N sigmoid heads + the
arithmetic of the routing rule** — the teacher is discarded at ship. Student size
range `[PROPOSED]` 22–150 M; primary candidate ModernBERT-base chosen on
engineering grounds (same-family Apache-licensed teacher exists; demonstrated
ONNX/INT8 CPU path) **not** on routing quality, because LLMRouterBench
`[VERIFIED]` found backbone choice has limited impact on routing quality. `[S:05]`

## 3. What is f_θ? (→ `06` §3)

The action set is `𝒜 = { EDGE_SLM, SPLIT(d₁…d_m), STRONG/CLOUD }`. The proposed
f_θ is the **per-action learned utility**:

```
f_θ(q, a) := Û_θ(a | q) = σ( w_aᵀ · Pool(ModernBERT-base_θ(q)) + b_a )      (Eq. 3′)
```

with **independent sigmoid heads** (not a softmax — a softmax would re-couple the
actions and break both the cost-separation and cheap pool-addition). The runtime
routing rule is:

```
R(q, s) = argmax_{a∈𝒜} [ Û_θ(a|q) − λ·C(a|s) ]                             (Eq. 4)
```

This **reduces to the manuscript's Eq. (3)** `R(q)=argmax_{M_k∈M} f_θ(q,M_k)`
when split depths are disabled (`𝒜 ≡ M`) and `λ=0` — a refinement, not a
redefinition (brief §9 satisfied without touching the manuscript). `[PROPOSED]`

## 4. What does the student predict? (→ `07`)

**Per-action calibrated probability of success** — `Û_θ(a|q) := P̂(success | q, a)`
(brief §10 target "C-structured, E-valued"). It is the KD-3 target. The simplest
milestone/baseline instantiation is `A = N = 2` (one edge-class vs one
strong-class action = binary edge-sufficiency); per-model utility (C) and pairwise
preference (D) are ablations; multiclass route (B) is a baseline only. Calibration
is a **claim to be measured (ECE)**, not a given. `[S:07]`

## 5. What teacher is proposed and why? (→ `04`)

**T1 — a larger same-family encoder router, ModernBERT-large (~395 M), training
only.** It is the only teacher option that is simultaneously genuinely larger,
openly/Apache-licensed (so distillation is permitted), reproducible, native to the
per-action utility target, and native to the optional representation-matching
ablation (same tokenizer/family). Crucially, the **observed-outcome oracle (T4) is
NOT a teacher — it is the ground-truth label `y(a,q)`**; and the strong model /
judge (T5/T2) is a **label source, not a teacher**. Conflating either would make
the method ordinary supervised regression (the "oracle-vs-teacher collapse") and
make the KD claim vacuous. `[S:04]`

## 6. What exactly is distilled? (→ `03`, `04`)

The teacher's **soft per-action calibrated utility vector** `Û_T(a|q)` — i.e. the
routing decision's utility estimate — is regressed by the student. This is the
single element that is **not** already occupied by prior work: RouteLLM (the only
close router-KD precedent) distils *preference labels* into a classifier with a
plain loss; no surveyed router distils a calibrated per-action utility head.
`[S:02/03]`

## 7. What training loss is proposed? (→ `03` §KD-5, `06` §5)

A **KD-5 hybrid of a hard-label task loss and a soft-target regression KD loss**:

```
L = α · L_task(Û_θ, y)  +  (1−α) · L_KD(Û_θ, Û_T)   [ + γ · L_repr  (optional KD-4) ]
```

`L_task` and `L_KD` are BCE / smooth-L1 regressions (primary KD-3 regresses raw
per-action utilities, so **no softmax temperature is required**; a temperature
appears only in the KD-1 softmax ablation). **α is the experiment, not a hidden
hyperparameter: α=1 is exactly the non-distilled control** against which KD must
prove itself (experiment E1). `[S:03/06]`

## 8. What remains measured rather than learned? (→ `08`)

The **entire system cost `C(a|s)` stays outside θ** — a measured table (+ optional
tiny `g_φ` only for stochastic tail-latency), never in the student weights. State
`s` = bandwidth, RTT, contention, activation-transfer bytes, edge/server compute
latency, TTFT/TPOT, resource pressure. Scalarization: the online decision uses
**SC1 normalized weighted-scalar cost** (the Lagrangian dual of SC3
constrained-optimization, `λ` = the KKT multiplier), evaluated with **SC4 Pareto
fronts + SC2 report-each-metric-separately** to neutralize the arbitrary-weights
objection. Because `y(SPLIT(d),q)=y(full,q)`, **all** Edge/Split/Strong
differentiation is forced into this cost term — the activation-byte cost function
is the most load-bearing quantity in the method. `[S:08]`

## 9. How does Split-LLM enter the system? (→ `09`)

`SPLIT(d)` is a **first-class routable action**: run layers `[0,d)` on the edge,
transmit the activation tensor, run `[d,L)` on the server. The router is
**decoupled from split internals** — it consumes only a measured scalar `bytes(d)`
(structural, cached once) plus live BW/RTT to form `c_comm`, and never touches
activations. The sprint produced a **13-row acquisition checklist for Henry's
code** (`09 §4` / `16 §2`), every field `[OPEN]`. The sharpest risk: if the split
is **not lossless** (F5 fails), `y(SPLIT(d),q)=y(full,q)` breaks and `Û_θ` needs a
per-depth quality head. Split is **never** silently replaced by a cloud API (brief
§26); the fallback is a minimal honest custom single-model split. `[S:09]`

## 10. What is likely already prior art? (→ `01`, `02`, `11`)

- **Micro-encoder routing itself** — occupied (RouteLLM, RouterDC, HyDRA,
  ConsRoute, BEST-Route, …). `[VERIFIED] REJECT as novelty.`
- **"Our encoder architecture is better for routing"** — contradicted by
  LLMRouterBench's limited-impact finding. `[VERIFIED] REJECT.`
- **Knowledge distillation as a mechanism** — mature (Hinton; DistilBERT/
  TinyBERT/MiniLM; ranking distillation; temperature scaling). `[VERIFIED]
  REJECT "KD is novel".`
- **Lightweight / CPU / no-retrain / comm-aware cost** — each independently
  occupied (HyDRA, CSCR, ConsRoute, Hybrid-LLM). `[S:01/11]`

## 11. What potential contribution remains defensible? (→ `11` §9)

**One compound, experiment-gated contribution** `[PROPOSED]`:

> A distilled micro-encoder router that predicts **calibrated per-action utility**
> and, by keeping that learned utility strictly separate from a **live-measured
> system cost that includes Split-LLM activation bytes**, routes among edge-SLM /
> Split(d) / strong-cloud — the first router to (i) be built by soft-target
> distillation of a **calibrated** per-action utility head shown to beat hard-label
> supervision at matched edge cost (lanes N1/N2), and (ii) treat **Split(d) as a
> first-class routable action with measured activation-transfer cost on real edge
> hardware** (lanes N3/N4/N6).

Of the six axes, **N2** (calibration preserved under distillation) and **N4**
(measured Split activation cost) are the only *standalone-defensible* ones; N1/N3/N6
survive only in combination; N5 folds into N3/N4. **No novelty by adjective.**
`[S:11]`

## 12. What would falsify the contribution? (→ `11` §10, `12`)

- **E1 collapse:** if no α<1 beats the α=1 non-distilled control, clause (i)
  (the whole KD story) is struck and the paper reframes onto N4 Split-systems
  alone — KD dropped as a documented negative result (brief stop-cond #4 branch).
- **Oracle-vs-teacher collapse:** if `Û_T ≈ y` everywhere, KD = supervised
  regression; mitigated by fixing a genuinely larger teacher (T1).
- **E4 calibration collapse:** if a non-distilled student + post-hoc temperature
  scaling matches the distilled student's ECE, N2 collapses (calibration was free).
- **F5 losslessness failure:** breaks `y(SPLIT(d),q)=y(full,q)` and the clean
  decoupled design.
- **Degenerate oracle headroom (MP2):** if the per-query oracle barely beats
  always-cloud, the routing problem is degenerate and nothing is defensible.
  `[S:11/12]`

## 13. What baseline methods are required? (→ `10` §baselines, `12`)

Trivial: Always-Edge, Always-Strong/Cloud, Always-Split, Random, Dataset-prior,
System-state-only scheduler. Simple-learned: **TF-IDF + Logistic Regression (the
bar to beat)**, **non-distilled ModernBERT-base (α=1 = the E1 KD ablation)**.
Comparison: **hidden-state self-router (demoted Candidate C)**, a published
encoder router, a published generative router (Arch-Router). Upper bound:
**per-query oracle** and the **T1 teacher** (= experiment E4). Each baseline is
annotated with the confound it controls for. `[S:10]`

## 14. What hardware/software details are still unknown? (→ `16` §3)

`[OPEN]`, never guessed: exact **edge GPU** (manuscript L202 fixes the edge
testbed as a Xeon W-2123 / 64 GB / **2×RTX 3090** workstation — so "edge" here is
**workstation-class, not phone/Jetson**, and N6 must be scoped to that); exact
**server/cloud GPU** (the L202 server sentence is **literally unfinished** —
"…equipped with…"); exact **machine names/hostnames**; **link-shaping permissions**
(`tc/netem`, `sudo`, two-machine networking). Published ONNX/INT8 CPU-latency
numbers are `[RELATED]`, not measured by us. `[S:16]`

## 15. What must be asked of Henry? (→ `16` §2)

The 13-row Split-LLM acquisition message, blocker-first. **Hard blockers (★):**
repo URL + license; which model(s) the split supports (HF id + size); split-layer
interface + valid depth range; **activation tensor shape at the cut** (this *is*
`c_comm`); **activation dtype/quantization at the cut**; **is the split lossless
(F5)?** Non-blocking: transfer mechanism/serialization, network protocol +
`tc/netem` compatibility, server/edge runtime + VRAM, CUDA/torch versions, existing
TTFT/TPOT/bytes logging hooks, per-decode-token transfer model, 4-bit + batching.
None of these may be invented. `[S:16]`

## 16. What belongs in the conference core? (→ `06`, `12`, `14`)

The distilled ModernBERT micro-encoder router (f_θ = per-action calibrated
utility), the KD-5 training with the E1 α-sweep, the runtime `argmax[Û−λC]` rule
with measured cost outside θ, the Split(d)-as-action with measured activation
bytes, and experiments **E1 (KD falsification), E2 (beat TF-IDF+LR), E3 (vs
hidden-state baseline), E4 (teacher-vs-student calibration), E5 (λ sweep), E6
(route change under BW/RTT), E7 (measured Edge-vs-Split), E8 (generalization)**.
Minimum irreducible set: **E1 + E2 + E4 + E7**. `[S:06/12]`

## 17. What belongs only in the journal continual-learning extension? (→ `13`, `14`)

Everything post-deployment and learned: adapting to **edge-SLM swap, pool growth,
and domain shift** (the three *learned* non-stationarities). The decoupled design
means **system/network drift needs no learning** (C is re-measured), so the journal
contribution is honestly scoped (JC1–JC4, experiments J1–J5). "Online
distillation / teacher-student refresh" is **not** a new mechanism — LwF is the
conference KD-5 loss with the previous student snapshot as teacher. Journal
distillation components are gated on conference E1/E4. The conference build adds
four near-zero-cost hooks (snapshot θ, persist `(q,a,y)` tuples, additive heads,
adapter slots) so CL stays out of the core. `[S:13/14]`

## 18. What manuscript text is ready to insert? (→ `proposed-solution-blue.tex`, `15`)

`methods-v2/proposed-solution-blue.tex` — a standalone-compilable Proposed Solution
draft in the manuscript's own notation (TLM router, `𝒜`/`f_θ`/`λ`), covering the
action set + Eq.(3) reduction, f_θ via independent sigmoid heads, the `argmax[Û−λC]`
rule, the KD α-hybrid loss (α=1 control), Alg.1 training + Alg.2 edge inference,
Split-LLM integration, calibrated-P(success) labels, and five honest limitations.
New prose is wrapped in a `\prop{} = \textcolor{blue}{}` macro (brief §20 BLUE
convention); the merge requires adding `\usepackage{xcolor}` at the manuscript's
empty `\section{Proposed Solution}` (L193). Figure contract in
`15-architecture-figure-spec.md` + optional `architecture-figure.tex` (three-channel
learned/measured/training-only visual encoding). **No LaTeX toolchain exists in this
environment, so the .tex files are authored but not compile-verified** — flagged
honestly, never claimed as rendered. `[S:19/15]`

## 19. Which claims still need advisor approval? (→ `16` §1)

The final **model pool** (sprint gives criteria MP1–MP8 + an N=2 recommendation,
not a pool); the **Qwen3-72B-Instruct replacement** (named checkpoint does not
exist); the **P-A vs P-B label route** (P-B destroys the edge/Split identity —
sprint recommends P-A); whether to **collapse to N=2**; the **B1 / Gemma note**
(cannot be reconstructed — do not guess); **conference-vs-journal ordering** (Plan
A vs B); **confirmation that N2+N4 are the agreed thesis**; the **E1-fails KD-drop
fallback framing**; and **link-shaping permissions**. All are `[OPEN]`. `[S:16]`

## 20. What are the next 10 implementation steps after approval? (→ `12`, `16`)

1. **Advisor meeting** — resolve the `16 §1` agenda: pool, Qwen3-72B replacement,
   P-A/P-B, N=2, novelty thesis, submission ordering, KD-drop fallback,
   permissions.
2. **Send Henry the `16 §2` message** — get the repo + the six ★ blocker answers;
   without activation shape/dtype and the F5 losslessness answer, the N4 lane and
   E7 cannot exist.
3. **Fix the model pool and action set 𝒜** (set `N`, the enabled `SPLIT(d)` depths)
   from the advisor + Henry answers; correct the invalid manuscript model names at
   merge time (as notes, `16 §5`).
4. **Stage-0 labelling on released data** (CPU): build `y(a,q)` for the chosen pool
   via the agreed label route; verify non-trivial oracle headroom (MP2) **before**
   investing — this is the degeneracy guard.
5. **Fit the T1 teacher** (ModernBERT-large) on `y`; verify it genuinely generalizes
   beyond `y` (guard against the oracle-vs-teacher collapse).
6. **Run E1 (the α-sweep)** — the KD falsification test. Decide KD in-or-out per
   stop-cond #4 *before* building anything downstream of it.
7. **Run E4** (teacher-vs-student quality/calibration/params) and E2/E3 (vs
   TF-IDF+LR and vs hidden-state baseline); measure ECE for the N2 claim.
8. **Integrate Henry's split**, instrument TTFT/TPOT/bytes, and run the **F5
   losslessness check**; wire `bytes(d)` into `c_comm`.
9. **Run the systems experiments** E5 (λ sweep), E6 (route change under
   `tc/netem` BW/RTT), E7 (measured Edge-vs-Split) on the two-machine testbed.
10. **Merge the blue Proposed Solution + architecture figure** into the manuscript
    (add `xcolor`, drop the blue block at L193), paste the verified citations from
    `17`/`.bib`, and tense every claim to what the experiments actually showed.

---

## 21. Stop-condition check (brief §27)

| # | Condition | Status |
|---|---|---|
| 1 | All required deliverables exist | ✅ `00`–`17`, `.bib`, `proposed-solution-blue.tex`, `architecture-figure.tex`, this file |
| 2 | Micro-encoder specified as implementable architecture | ✅ `05`/`06` (ModernBERT-base + N sigmoid heads, Eqs. 3′/4) |
| 3 | ≥3 realistic KD formulations investigated | ✅ `03` (KD-1…KD-5) |
| 4 | One defensible KD formulation proposed **or** KD rejected with evidence | ✅ KD-3-as-KD-5 proposed, **conditional on E1** (reject branch pre-specified) |
| 5 | Closest micro-encoder/router prior work primary-source checked | ✅ `01`/`17` (RouteLLM, RouterDC bodies read) |
| 6 | Closest KD-for-routing prior work primary-source checked | ✅ `02`/`17` (RouteLLM = only close precedent) |
| 7 | Every novelty claim sourced or marked PROPOSED/OPEN | ✅ `11` |
| 8 | Conference-core architecture fully specified | ✅ `06`/`12` |
| 9 | Continual learning isolated as journal extension | ✅ `13`/`14` |
| 10 | Real Split-LLM integration path without inventing Henry's code | ✅ `09`/`16` (all `[OPEN]`) |
| 11 | Baseline and experiment plan exists | ✅ `10`/`12` |
| 12 | Verified references and BibTeX exist | ✅ `17`/`method-references.bib` |
| 13 | Manuscript-ready blue Proposed Solution text exists | ✅ `proposed-solution-blue.tex` |
| 14 | Architecture figure specification exists | ✅ `15` (+ optional `.tex`) |
| 15 | Original manuscript not modified | ✅ SHA `06f5f9d7…`, git clean |
| 16 | No experimental results invented | ✅ all performance statements are hypotheses routed to `12` |

**All 16 stop conditions are met.**
