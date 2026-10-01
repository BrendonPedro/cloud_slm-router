# methods-v2 / 11 — Novelty stress test

*Deliverable for `MICROENCODER_KD_BRIEF.md` §15 (and §23 evidence discipline).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 12).*

## 0. Purpose and method

The brief demands one hard question be answered before any manuscript claim is
written: **what, exactly, could be new here?** The brief forbids *novelty by
adjective* — no claim may rest on the word "micro-encoder", "lightweight",
"distilled", or "novel" unless a primary source shows the closest prior work and
the gap to it. This file applies the §15 procedure to each of the six candidate
novelty axes N1–N6:

1. state the candidate claim precisely;
2. name the **closest prior work** with its primary-source identifier (reusing
   the primary-source checks locked in `01-microencoder-prior-art.md` and
   `02-kd-prior-art.md` — no new claim is asserted here that was not checked
   there);
3. state the **overlap** (what the prior work already does);
4. state **what would have to be experimentally demonstrated** for the claim to
   stand;
5. issue a **verdict**: `SURVIVES` (defensible as PROPOSED/OPEN pending the named
   experiment), `DOWNGRADE` (true but weaker than first stated), or `REJECT`
   (already occupied — do not claim).

This is a **stress test**, not an advertisement. Where an axis is occupied, it is
rejected in writing so that the manuscript cannot accidentally re-assert it.

**Evidence tags** (from `00` §Evidence discipline): `[VERIFIED]` primary source
directly checked (in `01`/`02`); `[RELATED]` adjacent, not exact precedent;
`[PROPOSED]` our design idea; `[OPEN]` requires experiment/advisor confirmation;
`[UNSUPPORTED]` must not be used.

**Carried headline from `01`/`02` (the two facts that govern everything below):**

- **F-A [VERIFIED]:** a small discriminative encoder that reads a query and emits
  a routing decision is **standard practice** (RouteLLM-BERT, RouterDC,
  BEST-Route, HyDRA, ConsRoute). LLMRouterBench further found the **backbone
  embedding choice has limited impact** on routing quality. ⇒ the *encoder
  itself* carries no novelty.
- **F-B [VERIFIED]:** **no** surveyed encoder router is built or compressed by
  knowledge distillation of the routing decision, and **none** has a Split-LLM
  action with measured activation-transfer cost. The closest KD-adjacent router
  is RouteLLM's GPT-4-judge *label augmentation* (arXiv:2406.18665) — a plain
  classification loss, no KL/temperature, binary strong-vs-weak, server-side.

---

## 1. The baseline rejection (stated first, on purpose)

Before the six axes, the brief §26 hard constraint is discharged explicitly:

> **REJECTED [VERIFIED]: "micro-encoder routing is novel."** Occupied by RouteLLM
> (arXiv:2406.18665, ICLR 2025, BERT classifier), RouterDC (arXiv:2409.19886,
> NeurIPS 2024), BEST-Route, HyDRA (ModernBERT 4-head), ConsRoute. The word
> "micro-encoder" is a size label, not a contribution.

> **REJECTED [VERIFIED]: "our encoder architecture is better for routing."**
> Directly contradicted by LLMRouterBench's finding that backbone choice has
> limited impact. The ModernBERT-base choice in `05` is justified on
> *engineering* grounds (same-family Apache teacher for clean KD, demonstrated
> ONNX-INT8 CPU path), **explicitly not** as a quality contribution.

> **REJECTED [VERIFIED]: "knowledge distillation is novel."** KD is mature
> (Hinton 1503.02531; DistilBERT 1910.01108; TinyBERT 1909.10351; MiniLM
> 2002.10957; ranking distillation KDD'18; PLaD 2406.02886). Using KD is not a
> contribution; *what* is distilled and *where it is deployed* might be.

These three rejections are the floor. Everything that follows must clear it.

---

## 2. N1 — Distillation method specifically optimized for utility-aware LLM routing

**Candidate claim.** "We introduce a knowledge-distillation method tailored to
LLM routing."

**Closest prior work [VERIFIED].** RouteLLM (arXiv:2406.18665) augments router
training labels with GPT-4-judge preference data — distillation *in all but
name*, but with a plain classification loss, no temperature, no soft-target KL,
and a binary strong-vs-weak target. RouterDC (arXiv:2409.19886) uses **dual
contrastive** learning (InfoNCE), which is representation learning, **not** KD
(a trap flagged in `02` — do not cite it as a KD precedent). `dynamic_routing_LLM`
distils the *generative student*, not the router (conflation to avoid).

**Overlap.** The *idea* of improving a small router with signals from a larger
model already exists in weak form (RouteLLM label augmentation). A generic
soft-target KL applied to a router head is a trivial composition of mature parts.

**What would have to be demonstrated.** Experiment **E1** (`12`): a distilled
micro-encoder must beat the **α=1 non-distilled control** at matched student
size/latency on routing quality *and* calibration. If E1 shows no gain, N1 is a
negative result and KD is dropped (brief stop-condition #4 explicitly permits
this).

**Verdict: DOWNGRADE → `[OPEN]`.** "A KD *method* for routing" is too broad to
defend as stated. The defensible residual is narrow and conditional: *the first
application of soft-target/temperature distillation to a **calibrated per-action
utility** router head, shown to beat hard-label supervision at matched edge cost*
— and even that only if E1 confirms it. Claim as PROPOSED, gated on E1. Do **not**
claim a "new distillation algorithm"; the mechanism is standard (KD-3 regression
trained as KD-5 hybrid, `03`).

---

## 3. N2 — Distillation that preserves calibrated per-model utility while shrinking the router

**Candidate claim.** "Our distillation preserves calibrated per-action utility
while greatly reducing router size/latency."

**Closest prior work.** Temperature scaling (Guo et al., ICML 2017,
arXiv:1706.04599) [RELATED] is the standard router-calibration tool; no surveyed
router *distils* calibrated utility. HyDRA emits per-action sigmoid scores but is
trained directly, not distilled, and does not report calibration preservation
under compression [VERIFIED via `01`]. RouteLLM reports a binary decision, not a
calibrated per-action utility vector.

**Overlap.** Calibration methods are mature; sigmoid multi-head utility exists
(HyDRA). The novel element is specifically **calibration *preservation through
distillation*** — whether the soft teacher transfers well-calibrated
per-action P(success) to a much smaller student better than hard labels + post-hoc
temperature scaling do.

**What would have to be demonstrated.** E1/E4 (`12`): report ECE / Brier /
reliability curves for (teacher) vs (distilled student) vs (non-distilled student
+ temperature scaling), at matched size. The claim stands only if the distilled
student is **better calibrated** than the non-distilled student (a strictly
stronger bar than accuracy parity).

**Verdict: SURVIVES as `[PROPOSED]`/`[OPEN]`.** This is the most defensible KD
axis because it names a measurable quantity (calibration) that the obvious
baseline (hard labels + temperature scaling) might *not* match. It is still
conditional on E1/E4 and must not be stated as achieved.

---

## 4. N3 — Separation of distilled semantic utility from live measured edge/Split cost

**Candidate claim.** "We separate a learned, distilled utility predictor Û_θ(a|q)
from a live-measured system cost C(a|s), combined only at decision time by
argmax_a[Û_θ(a|q) − λ·C(a|s)]."

**Closest prior work.** Cost-/comm-aware routing exists: Hybrid-LLM, ConsRoute,
and the prefill-activation router all fold a cost or system term into the routing
decision [VERIFIED via `01`]. The manuscript's own Eq.(2) `U − λC` already states
the separation at the problem level. So the *decision rule* is not new.

**Overlap.** The `U − λC` scalarization is standard (and `08` shows it is the
Lagrangian dual of a constrained-optimization SLA budget — mature optimization,
`[RELATED]`). Comm-aware cost terms exist. The specific combination — a
*distilled* utility head whose weights contain **no** system state, feeding a
decoupled runtime cost term that includes **Split activation bytes** — is what is
unoccupied.

**What would have to be demonstrated.** E5/E6 (`12`): the router must change its
routes correctly as λ, bandwidth, and RTT vary **without retraining** (cost lives
outside θ), and an ablation that *bakes* cost into the weights (v1 S1-placement)
must be shown to be worse / less adaptable.

**Verdict: DOWNGRADE → SURVIVES only in combination.** The separation principle
alone is not novel (the manuscript already states it). What survives as
`[PROPOSED]` is the *implementation discipline*: a distilled utility head provably
free of system state + a runtime cost term carrying **measured Split activation
bytes** (ties to N4). Claim the combination, not the principle.

---

## 5. N4 — Genuine Split-LLM systems evaluation with measured activation transfer

**Candidate claim.** "We route among EDGE / SPLIT(d) / STRONG and evaluate the
SPLIT path with *measured* activation-transfer bytes and latency on real
hardware."

**Closest prior work.** No surveyed **router** has a Split-LLM action with
measured activation cost [VERIFIED via `01`/`02` — N4 lane found unoccupied].
Split/collaborative inference itself exists as a systems topic, but not *as a
routable action inside a learned utility-vs-cost router*. (The exact Split-LLM
precedents from Henry's codebase are `[OPEN]` — not yet provided; do not invent
them, per `09` and brief §26.)

**Overlap.** Split inference as a mechanism is prior art in systems literature
(general model partitioning / collaborative inference). The gap is integrating it
as **one action among others in a routing policy** with the byte cost *measured*,
not estimated.

**What would have to be demonstrated.** E7 (`12`): real Edge-vs-Split execution
with measured TTFT, TPOT, e2e p50/p95/p99, **activation bytes transferred**,
throughput. Crucially this depends on Henry's code (`09` checklist, all `[OPEN]`)
and on the **losslessness assumption F5** (`09`): if the split is *not* lossless
(e.g. activation quantization at the cut), `07`'s `y(SPLIT(d),q)=y(full,q)` breaks
and the method needs a per-depth quality head. N4 cannot be *claimed as measured*
until E7 is actually run — brief §26 forbids presenting estimated latency as
measured.

**Verdict: SURVIVES as `[OPEN]` — the strongest *systems* novelty, most at risk.**
This is genuinely unoccupied among routers and is the clearest contribution for a
systems audience. But it is entirely gated on (a) Henry's code arriving and (b)
the F5 losslessness check. It must be written as "we *will* measure", never "we
measured", until E7 exists. Highest external-dependency risk of all six axes.

---

## 6. N5 — Distilled router + network-adaptive decision layer

**Candidate claim.** "A distilled router with a network-adaptive decision layer
that re-routes under changing link conditions."

**Closest prior work.** Network-adaptive offloading is a mature systems idea;
comm-aware routers exist (ConsRoute, Hybrid-LLM) [VERIFIED/RELATED]. Adaptivity to
bandwidth/RTT via a runtime cost term is the direct consequence of N3's
separation, not an independent mechanism.

**Overlap.** Almost complete: N5 is N3 (decoupled cost) + N4 (Split path) observed
dynamically (E6). It introduces no new learned component — the adaptivity is just
C(a|s) being re-measured.

**Verdict: REJECT as a standalone claim; FOLD into N3/N4.** There is no separate
"adaptive layer" — adaptivity falls out of measuring C(a|s) live. Presenting it as
a distinct contribution would be double-counting N3. Keep it as an *experiment*
(E6 route-change-under-bandwidth), not a contribution axis.

---

## 7. N6 — Edge deployment / quality–latency–communication trade-off not previously measured for comparable routers

**Candidate claim.** "We measure the quality/latency/communication trade-off of a
distilled router *on edge hardware*, which comparable routers have not reported."

**Closest prior work.** HyDRA reports an ONNX-INT8 CPU latency path (55 ms P50 /
86 ms median) [VERIFIED via `01`/`05`, and explicitly **not our hardware**, `[E]`]
— so *an* encoder router has shown CPU-edge feasibility. No surveyed router
reports the **joint** quality × latency × **communication-bytes** trade-off,
because none has a Split action with measured bytes (F-B).

**Overlap.** Edge CPU latency alone for an encoder router is already shown (HyDRA)
— so "we run on the edge" is not novel. The communication-bytes axis is the
differentiator and it is inseparable from N4.

**What would have to be demonstrated.** E7 + E1: the full trade-off surface
(SC4 Pareto front, `08`) for the distilled student on the real edge/split testbed,
including activation bytes — and the distilled student must sit on a better
quality-vs-latency/bytes frontier than the non-distilled student and simple
baselines.

**Verdict: DOWNGRADE → SURVIVES only as the *three-axis* trade-off.** "Edge
deployment" alone is occupied (HyDRA). What survives as `[OPEN]` is the
*communication-inclusive* Pareto characterization, which is a consequence of N4.
Do not claim edge-deployment novelty on its own.

---

## 8. Consolidated verdict table

| Axis | Claim (short) | Closest prior work (primary) | Verdict | Status | Gating experiment |
|------|---------------|------------------------------|---------|--------|-------------------|
| — | micro-encoder routing is novel | RouteLLM/RouterDC/HyDRA/ConsRoute | **REJECT** | occupied | — |
| — | encoder architecture better | LLMRouterBench (limited-impact finding) | **REJECT** | contradicted | — |
| — | KD is novel | Hinton/DistilBERT/TinyBERT/MiniLM | **REJECT** | mature | — |
| N1 | KD *method* for routing | RouteLLM label-aug (2406.18665) | **DOWNGRADE** | `[OPEN]` | E1 |
| N2 | KD preserves *calibrated* utility under compression | temperature scaling (1706.04599); HyDRA | **SURVIVES** | `[PROPOSED]`/`[OPEN]` | E1, E4 |
| N3 | distilled Û separate from measured C | Hybrid-LLM/ConsRoute; manuscript Eq.(2) | **DOWNGRADE→combo** | `[PROPOSED]` | E5, E6 |
| N4 | Split-LLM action w/ *measured* activation bytes | none among routers (`[OPEN]` Henry code) | **SURVIVES** | `[OPEN]` | E7 (+ F5 check) |
| N5 | network-adaptive decision layer | ConsRoute/Hybrid-LLM | **REJECT→fold N3/N4** | — | E6 (experiment only) |
| N6 | edge quality/latency/**comm** trade-off | HyDRA CPU path | **DOWNGRADE→3-axis** | `[OPEN]` | E7, E1 |

---

## 9. The single defensible contribution sentence (for the manuscript)

Stripping every rejected and downgraded element, the residual that survives the
stress test is **one compound contribution**, not six:

> **[PROPOSED, gated on E1/E4/E7]** *A distilled micro-encoder router that predicts
> **calibrated per-action utility** and, by keeping that learned utility strictly
> separate from a **live-measured system cost that includes Split-LLM activation
> bytes**, routes queries among edge-SLM, Split(d), and strong/cloud execution —
> the first router to (i) be built by soft-target distillation of a calibrated
> per-action utility head shown to beat hard-label supervision at matched edge
> cost (N1/N2), and (ii) treat Split(d) as a first-class routable action with
> measured activation-transfer cost on real edge hardware (N3/N4/N6).*

Every load-bearing word maps to a gating experiment. None of it may be written in
past/achieved tense until those experiments exist (brief §26). If **E1 fails**,
strike clause (i) and the paper becomes a *Split-LLM-aware routing + measurement*
contribution resting on N4/N6 alone — still publishable, KD dropped as a
documented negative result.

---

## 10. Threats that could sink even the residual claim

1. **E1 collapse (KD adds nothing).** If the distilled student does not beat the
   α=1 control (`03`/`04`), N1/N2 vanish. **Mitigation:** pre-registered as the
   primary falsification test; paper survives on N4/N6.
2. **Oracle-vs-teacher collapse (`04`).** If the only "teacher" is the
   observed-outcome oracle T4, the method is supervised regression, not
   distillation. **Mitigation:** teacher fixed as a *genuinely larger* model (T1
   ModernBERT-large) whose soft targets differ from ground truth on interpolated
   queries; paper must state "T4 is not a teacher" so reviewers cannot read it as
   "regressed the oracle."
3. **F5 losslessness failure (`09`).** If Split is not lossless,
   `y(SPLIT(d),q)=y(full,q)` breaks and N4's clean story needs a per-depth quality
   head. **Mitigation:** verify empirically the moment Henry's code arrives; do
   not assume.
4. **Degenerate oracle headroom (`10`, MP2).** If the per-query oracle barely
   beats always-cloud, routing is pointless and no contribution stands.
   **Mitigation:** pool chosen for non-trivial oracle-minus-best-single-model
   headroom.
5. **Backbone-doesn't-matter (LLMRouterBench).** Guards against any reviewer
   reading a quality gain as an architecture claim. **Mitigation:** backbone is an
   ablation, never a contribution (already stated §1).

---

## 11. Hand-offs

- `12-conference-experiment-plan.md`: E1 (N1/N2 falsification), E4 (calibration,
  N2), E5/E6 (N3 adaptivity), E7 (N4/N6 measured Split). Each novelty axis above
  names its gating experiment — those become the E-numbered hypotheses.
- `17-verified-references.md` + `method-references.bib`: RouteLLM (2406.18665),
  RouterDC (2409.19886), LLMRouterBench, HyDRA, ConsRoute, Hybrid-LLM, Hinton
  (1503.02531), DistilBERT (1910.01108), TinyBERT (1909.10351), MiniLM
  (2002.10957), temperature scaling (1706.04599) — all already primary-checked in
  `01`/`02`; re-verify fields there.
- `proposed-solution-blue.tex`: the §9 contribution sentence is the *only*
  novelty prose permitted, wrapped in `\textcolor{blue}{}`, in future/PROPOSED
  tense, never "we achieve/outperform/demonstrate."
- `FINAL-SUMMARY.md` Q11/Q12: Q11 = the §9 residual; Q12 = the §10 threats
  (chiefly E1 failure and F5 failure).

---

## 12. Evidence-discipline summary for this file

- Everything tagged `[VERIFIED]` here was primary-source checked in `01`/`02`;
  this file asserts **no** new verified fact.
- Every novelty axis is `[PROPOSED]` or `[OPEN]`, never stated as established.
- Three baseline "novelty" temptations are explicitly `REJECT`ed in writing (§1)
  so they cannot leak into the manuscript.
- No experimental result is claimed; every surviving claim is gated on a named,
  not-yet-run experiment (brief §26 honoured).
