# 03 — Method Comparison

*Method-selection sprint, iteration 3. This is a planning document. Nothing here
has been implemented, trained, or measured by us. Every latency or accuracy
figure is quoted from a source already primary-checked in the earlier sprint
(with a pointer) or is explicitly marked as an untested expectation. Per the
brief §17, this document does **not** declare a winner.*

Evidence tags (same convention as `02-candidate-methods.md`):

- **[S: …]** sourced; the record is in the cited earlier deliverable.
- **[O]** our analysis.
- **[P]** our design proposal, not established practice.
- **[E]** an untested expectation; needs measurement before it can be claimed.

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-checked
this iteration). `paper/main-revised.tex` is unchanged.

---

## 0. Scope of this comparison

Candidates carried from `02-candidate-methods.md`:

| ID | Candidate | Status |
|---|---|---|
| A | Tiny generative LM router | viable (baseline / fidelity anchor) |
| B | Lightweight discriminative micro-encoder | viable |
| C | Self-routing edge SLM (hidden-state probe), C-pre / C-post | viable |
| D | Structured multi-head utility/cost model (policy layer on B or C) | viable |
| A-J | Jacobi-forced generative router | ablation only (variant of A) |
| E-J | Jacobi Forcing on the edge *generator* | **not a router** — cost-table change |

A-J and E-J are shown in a separate row block because neither is an independent
realisation of `f_θ`: A-J is A with a different decoder; E-J changes the cost
table `C(a|s)`, not the router. They are compared where it is meaningful and
otherwise marked "n/a (not a router)".

The three admissible forms of `f_θ` are unchanged from `02` §0:
**utility-then-cost** (`argmax_a Û(a|q) − λ·C(a|s)`) and its **binary-sufficiency**
reduction (`p̂(edge suffices|q)` thresholded at τ(λ)). Every "Yes" in the
*Maps to Eq. (2)/(3)* row below is justified in `02` §7.

---

## 1. Master comparison matrix

Legend: `●` strong / **`◐`** partial or conditional / `○` weak or absent. All
cell judgements are **[O]** unless a source is cited inline; the underlying facts
are in `02-candidate-methods.md` and the `research/` deliverables it cites. These
are relative judgements *among these candidates*, not absolute claims.

| # | Criterion (brief §17) | A Generative TLM | B Micro-encoder | C Self-routing SLM | D Structured multi-head |
|---|---|---|---|---|---|
| 1 | **Fidelity to original paper** (literal wording) | ● literal "Tiny Language Model" | ◐ "micro-encoder" reading | ◐ "lightweight" self-router | ◐ adds explicit privacy var the motivation implies |
| 2 | **Lightweight edge feasibility** | ○ needs a 0.5–1.5B LM resident | ● 20–150M encoder | ● no separate model (probe on SLM) | ● as B or C |
| 3 | **Query understanding** | ● full LM | ● encoder repr. | ● SLM internal state | ● + typed heads |
| 4 | **System awareness** (of C, network state) | ○ only via external cost table | ○ only via cost table | ○ cost table (probe is query-only) | ◐ length head feeds cost; privacy→path |
| 5 | **Routing latency** | slowest: prefill + ≥1 decode [S: d3 §2.1] | low: 1 fwd pass [S: d7 §2] | lowest if query stays local; wasted prefill on escalation [S: d3 §2.1] | as B or C |
| 6 | **Memory footprint** | ○ 0.5–1.5B params | ● 20–150M | ● probe ~10K–1M on top of SLM already resident | ● backbone + <1M heads |
| 7 | **Training complexity** | ◐ LoRA SFT | ● standard fine-tune | ◐ labelling runs + probe | ◐ multi-task + extra data |
| 8 | **Label complexity** | per-query route labels | per-query per-model utility | edge-sufficiency labels | + sensitivity + length labels (new) |
| 9 | **Inference complexity** | ◐ decode step(s) | ● single pass | ● single prefill (reused if local) | ● single pass + policy layer |
| 10 | **Calibration support** | ◐ ill-defined for multi-token labels | ● temp. scaling per head | ● temp. scaling + cluster τ | ● per-head, but more to report |
| 11 | **Adaptability (λ retune, no retrain)** | ● λ is runtime knob | ● runtime knob | ● τ(λ) on dev split | ● policy (ρ,λ) outside weights |
| 12 | **New-model integration w/o retraining** | ◐ semantic route add only | ◐ B3/profile-head add | ○ retrain on edge-SLM change | ◐ policy only; caps still relabel |
| 13 | **Split-LLM compatibility** | ○ nominal token only | ○ SPLIT is just another action | ◐ probe on split-head activations (P2) — only structural link | ◐ privacy head gives SPLIT a *reason* (N1) |
| 14 | **Interpretability** | ○ opaque generation | ◐ per-model scores | ◐ one probability | ● typed, per-head probabilities |
| 15 | **Exploits changing network conditions** | ○ (cost table does, not the model) | ○ (cost table does) | ○ (cost table does) | ◐ length→cost is query-side; rest is cost table |
| 16 | **SIGCOMM / networked-systems relevance** | ○ weakest alone | ○ needs systems eval to matter | ◐ routing cost folded into inference; split-activation touches bytes | ● privacy→split-depth→activation bytes is a systems trade-off |
| 17 | **Reproducibility** | ● Arch-Router-1.5B released | ● RouteLLM/RouterDC code | ◐ ConsRoute-style; needs hidden-state access | ◐ B/C + sensitivity data effort |
| 18 | **Dependence on unavailable code** | ○ low (released) | ○ low (released) | ◐ needs runtime exposing hidden states | ◐ + sensitivity dataset TBD |
| 19 | **Required GPU resources** | ◐ 1 GPU LoRA SFT | ● 1 GPU / CPU | ◐ 1 GPU for labelling runs | ◐ as B/C + data |
| 20 | **Overall implementation risk** | MEDIUM (superseded-as-contribution risk) | LOW (but not novel alone) | MEDIUM (mechanism occupied; novelty from N1/N2) | MEDIUM (PRISM overlap; new data dep.) |

Rows for the two non-primary variants (compared only where meaningful):

| # | Criterion | A-J Jacobi-forced router | E-J Jacobi edge generator |
|---|---|---|---|
| 1 | Fidelity to title phrase | ◐ only reading where *router* is Jacobi-forced [S: d6 §9] | ◐ only natural place for "Jacobi" [S: d6 §9 J1] |
| 5 | Routing latency benefit | ○ ~1× on a 1-token decision [S: d6 §9] | n/a (not a router) — changes edge decode `TPOT` |
| 16 | SIGCOMM relevance | ○ micro-opt of a non-contribution mechanism | ◐ separable systems ablation (edge decode speed) [E] |
| 20 | Implementation risk | MED–HIGH for ~zero routing benefit | HIGH (must JF-post-train a sub-2B SLM ourselves; public ckpts 7B only) [S: d6 §7] |

**The single most important reading of this matrix:** no row 20 entry is "LOW +
novel". Every candidate is either low-risk-but-not-novel (B) or
medium-risk-with-a-conditional-novelty-path (C, D). **No candidate is a
contribution on its architecture alone** — the earlier novelty map found
encoders, prefill probes, generative small routers, and multi-head capability
heads all already exist [S: d7 §2; d8 §4]. Novelty, if any, comes from **what the
router decides** (N1: a genuine Split-LLM action with measured activation-transfer
and leakage) and **how it is evaluated** (N2: calibration under domain shift on
edge hardware), not from picking A vs B vs C.

---

## 2. Pairwise trade-off notes (not captured by the matrix)

**A vs B — does generation buy anything?** The only head-to-head we have
(ConsRoute Table III) had generative tier-selection *slower* (36.2 ms, or 1,868 ms
with CoT) *and less accurate* (85.79% vs 87.92% on GSM8K) than a hidden-state
probe [S: d3 §2.1]. One paper, one dataset, not our hardware — but it is the only
published evidence and it points against A. A's value is therefore as the
**fidelity anchor / released baseline** (Arch-Router-1.5B), not the headline
method. This is exactly hypothesis H2 in `08`/§18 of the brief.

**B vs C — text vs internal state.** B needs a *second* model resident on the edge
and sees only query text; C reuses the SLM already present and sees its internal
state, so it may predict SLM failure better — but it wastes the prefill when the
query must be escalated, and its probe must be **retrained whenever the edge SLM
changes** [O]. Which effect wins is unknown on our (unspecified) edge hardware and
is precisely the cheap comparison the minimum experiment (`08`) should run first.
**This B-vs-C comparison is itself a finding**, not a settled choice.

**C-pre vs C-post — pay before or after deciding.** C-pre decides from the prefill
state (near-free if the query stays local); C-post first decodes `k` tokens for a
confidence read, adding decode cost *before* every offload decision. C-post can be
more accurate but forfeits C's main latency advantage on escalated queries.

**D relative to B/C — a layer, not a rival.** D is a thin policy layer on a B or C
backbone; it is the *only* candidate that represents privacy explicitly and thereby
gives the Split path a query-content reason to exist. But **PRISM (AAAI 2026)
already does privacy-aware three-way edge/collaborative/cloud routing**
[S: d4 row I-1], so D is only a contribution if its "collaborative" path is a
genuine layer-split path with *measured* leakage (N1). If measured leakage shows
split depth does not protect sensitive queries, D collapses back to B/C plus a rule.

**A-J / E-J — do not confuse them with the router choice.** A-J is an ablation of
A (near-zero expected benefit on a short decision). E-J is orthogonal to A–D
entirely: it changes the edge decode time in the cost table and, through the cost
table, shifts the routing threshold — it is a *separable systems ablation*, not a
value of `f_θ`. Neither should be presented as "the Jacobi-Forced Micro-Encoder";
`04-jacobi-role.md` establishes no such method exists.

---

## 3. The three categories the brief asks for (§17) — for discussion, not decision

The brief explicitly forbids declaring a winner and instead asks for three
labelled categories. These are **discussion categories for the advisor**, not
advisor-independent decisions.

### Strongest conservative option → **B (lightweight micro-encoder)**
Lowest implementation risk and highest reproducibility: released baseline code
(RouteLLM/RouterDC), single forward pass, standard temperature-scaling
calibration, one GPU (or CPU) to train. Its weakness is honest: it is **not novel
on its own** and needs a second model resident on the edge. It is the safe floor
every other candidate must beat, and it supplies the cheap side of the B-vs-C
head-to-head.

### Strongest higher-risk option → **D on a C backbone, aimed at N1**
Highest potential SIGCOMM payoff: privacy → split-depth → activation-transfer
volume and end-to-end path selection is a networked-systems trade-off with
measurable bytes and latency, not a classification score. Its risks are equally
concrete: PRISM overlap, an unresolved sensitivity-label dependency (`11`), the
untested assumption that split-head activations predict edge-SLM failure (P2), and
the open question of whether split-vs-cloud can be *learned* at all rather than
being a rule. It should only be pursued if the advisor confirms the Split-LLM
action is in scope and Mix-or-Split (still unread) does not pre-empt it.

### Strongest option closest to the title / original TLM concept → **A (generative Tiny-LM)**, with A-J noted
A is the literal "Tiny Language Model" of the manuscript, and A-J is the only
reading in which the router itself is "Jacobi-forced". Both are carried for
fidelity, but current published evidence has A slower and less accurate than a
probe for the same decision [S: d3 §2.1], and A-J offers ~1× speed-up on a
short-token decision [S: d6 §9]. A's honest role is **baseline / fidelity anchor**,
and its selection over B/C is the subject of hypothesis H2 — an experimental
question, not a foregone conclusion.

**What connects the three:** C-pre sits between them — cheaper than A, richer than
B, and the only one with a structural link to Split. The recommended minimum
experiment (`08`) therefore tests **B vs C-pre (with A as released)** first,
because that comparison is cheap and directly falsifies the "tiny generative
router" premise, before any D- or split-specific work.

---

## 4. What this comparison does *not* settle (hand-offs)

- **The label/target choice** (binary vs multiclass vs utility regression vs
  pairwise vs direct U−λC vs separated U/C) → `06-label-and-training-design.md`.
- **System-state integration** (S1 all-in-one net vs S2 utility-then-measured-cost
  vs S3 separate predictors vs S4 systems-only baseline) → `07-system-cost-integration.md`.
- **The minimum selection experiment** that would actually rank A/B/C on our
  hardware → `08-experiment-design.md` and brief §18 (H1/H2/H3).
- **Which hardware is "edge"** — the latency ordering of rows 5/6 depends on it and
  is unresolved (advisor question) [S: d1 open q4].

The comparison above is deliberately inconclusive on purpose: the matrix shows no
architecture is a contribution by itself, so the decision the advisor faces is
**which novelty axis (N1 vs N2) to pursue**, and the architecture follows from that
choice — not the other way around.
