# methods-v2/00 — Meeting-decisions lock (micro-encoder + KD sprint)

*Sprint authority: `MICROENCODER_KD_BRIEF.md` (advisor meeting 2026-10-01).*
*Research problem authority: `source/main-original.tex` (SHA-256*
*`06f5f9d7e9548c04ff59e098c1bd3c63a33d686114ccb8e37363d052b1707cf6`,*
*re-verified **unmodified** this iteration).*

This document locks what is **decided**, what is **fixed by the paper**, and
what is **explicitly unresolved** for the methods-v2 sprint. It chooses nothing
that the advisor did not choose. It supersedes the open A/B/C method-selection
framing of the earlier `methods/` sprint: the family is now **decided**. All
grounding reuses primary-source-checked material already in the repo — no new
research is performed in this deliverable.

Evidence tags used throughout this sprint (`MICROENCODER_KD_BRIEF.md` §23):
**[VERIFIED]** primary source supports it · **[RELATED]** adjacent prior work ·
**[PROPOSED]** our design · **[OPEN]** needs experiment/advisor · **[UNSUPPORTED]**
do not use.

---

## 1. What the advisor APPROVED on 2026-10-01 (decided — do not re-open)

These are meeting decisions (`MICROENCODER_KD_BRIEF.md` §2 "CONFIRMED"). They are
treated as fixed inputs, not candidates:

1. **D1 — Micro-encoder is THE router backbone.** The proposed implementation of
   `f_θ` is a lightweight discriminative **micro-encoder**. The sprint stops
   comparing A/B/C as equal candidates; the earlier sprint's "Candidate B"
   (discriminative encoder) is now the selected family
   [`methods/02-candidate-methods.md`; `research/micro-encoder-investigation.md`].

2. **D2 — Learned utility stays separate from measured live cost.** Candidate
   runtime form:
   `Û(a | q)` (learned, on the micro-encoder) combined with `C(a | s)`
   (measured from live system state) via a decision such as
   `argmax_a [ Û(a|q) − λ · C(a|s) ]`. This is the earlier sprint's **S2**
   approach [`methods/07-system-cost-integration.md`], now the confirmed shape.

3. **D3 — A Split-LLM implementation exists in the lab; Henry has code that may
   be reused.** Details of that code are **[OPEN]** (see §3).

4. **D4 — Lab GPU resources are available.** Exact GPU models **[OPEN]**.

5. **D5 — Two-machine use appears available.** Exact machine names **[OPEN]**.

6. **D6 — Edge-SLM hidden-state / self-routing routing (earlier "Candidate C")
   is demoted to a BASELINE / comparison**, not the proposed architecture.

7. **D7 — Investigate knowledge distillation (KD)** as a way to further optimise
   the micro-encoder, on the advisor's explicit suggestion and on the premise
   that micro-encoder/router work likely already exists. KD is to be
   **investigated and either proposed with evidence or rejected with evidence**
   — it is **not** assumed to be novel (`MICROENCODER_KD_BRIEF.md` §26).

8. **D8 — Continual learning is a possible JOURNAL extension**, investigated
   separately, and must **not** be silently added to the conference core.

9. **D9 — The manuscript will be updated** with (a) an overall architecture
   figure, (b) a detailed Proposed Solution, (c) the proposed method highlighted
   in **blue**. In this sprint that update is produced as **standalone drafts**
   under `methods-v2/`, never by editing the original manuscript.

10. **D10 — Jacobi Forcing is NOT a required component** of the proposed method.
    This matches the earlier finding that the only coherent Jacobi placement was
    the edge *generator*, never the router [`methods/04-jacobi-role.md`;
    `research/jacobi-forcing.md`].

## 2. What the ORIGINAL PAPER fixes (cannot change — `MICROENCODER_KD_BRIEF.md` §1)

Unchanged from `methods/00-scope-lock.md §§1–5`; restated so v2 is self-contained.

| Eq. | Source line | Content |
|---|---|---|
| (1) | L141–143 | `R : Q → M`, a routing function |
| (2) | L170–172 | `max_R E_q[ U(R(q),q) − λ·C(R(q),q) ]` |
| (3) | L187–189 | `R(q) = argmax_{M_k∈M} f_θ(q, M_k)` |

- `U(M_k,q)` = expected response quality of `M_k` on `q` (L124, L164). **[VERIFIED]**
- `C(M_k,q)` = cost; "may include computation, communication, latency" (L165). **[VERIFIED]**
- `λ` = utility-vs-cost trade-off weight (L126). **[VERIFIED]**
- `f_θ` = lightweight scoring function (L128–130, L185–191). **[VERIFIED]**

The proposed micro-encoder must remain an implementation of `f_θ`, and its
runtime decision must reduce to Eq. (2)/(3). The notation extension where an
**action `a`** (edge / split-depth `d` / strong-cloud) replaces model `M_k`
must be shown to collapse back to Eq. (3) — done in `methods-v2/06` and `09`.

Fixed requirements (L176–183): **A** lightweight/edge-deployable · **B** query
understanding · **C** system awareness · **D** adaptability/generalisation.
Fixed roles (L147–159): edge device (hosts SLM + router), cloud (hosts
LLM/Split-LLM), router runs **on the edge** before data leaves. Split-LLM is a
real member of the action space (L137, L155–159), not a stub cloud API.

**Must not** redefine the problem as generic scheduling, classification, or
model selection; must not modify `source/main-original.tex` or
`paper/main-revised.tex`; must not run large training/GPU jobs; must not invent
results, references, BibTeX, hardware, Henry's code, or the final model pool.

## 3. What is UNRESOLVED — DO NOT GUESS (`MICROENCODER_KD_BRIEF.md` §2 "UNRESOLVED")

Each item is carried as **[OPEN]** into `methods-v2/16-advisor-and-lab-open-questions.md`
and must be **flagged, never invented**:

- **O1** exact edge GPU model.
- **O2** exact server/cloud GPU model (note: manuscript L202 fixes the *edge*
  testbed — Xeon W-2123, 64 GB, 2×RTX 3090 24 GB, Ubuntu 20.04.6 — but the
  cloud-server sentence is literally unfinished, "…equipped with …"
  [`methods/10-lab-requirements.md`]). **[VERIFIED that it is undefined]**
- **O3** exact machine names.
- **O4** exact Split-LLM repository/codebase from Henry (model, split-layer
  interface, activation shapes, transport, logging hooks) — checklist in
  `methods-v2/09`.
- **O5** exact bandwidth/RTT-control permissions (tc/netem allowed?).
- **O6** exact edge-SLM / strong-model pool. The earlier claim audit found
  **invalid names** to fix, not assume: "Qwen3-72B" and Gemma "-A4B" suffixes do
  not exist [`methods/11-advisor-questions.md`; `research/claim-audit.md`].
  v2 proposes **selection criteria**, not a final pool (`methods-v2/10`).
- **O7** meaning of the advisor discussion on B1 / SLM choice / possible Gemma
  model.
- **O8** conference-vs-journal submission sequencing (two plans, not one guess —
  `methods-v2/14`).

## 4. Scope boundary between this sprint and the earlier `methods/` sprint

- The earlier `methods/` sprint (18 files, complete) kept A/B/C/D **open** and
  refused to pick a winner. **This v2 sprint starts from the advisor having
  picked the micro-encoder family**, and narrows to: specify it, source its
  prior art, stress-test KD, and produce manuscript-ready blue text + figure.
- Reuse (do not re-research): `research/micro-encoder-investigation.md` and
  `research/closest-prior-art.md` → `methods-v2/01`; `research/*` + `methods/06`
  → `methods-v2/07`; `methods/07` (S1–S4) → `methods-v2/08`; `methods/08`,`15`
  (experiment matrix) → `methods-v2/12`; `methods/10` (lab tiers) + `11`
  (advisor Qs) → `methods-v2/16`; `references/library.bib` → `methods-v2/17` +
  `method-references.bib`. KD prior-art (`02`) and KD formulations (`03`) are the
  genuinely **new** investigation this sprint adds.

## 5. Conference-core vs journal-extension boundary (locked)

| Belongs in CONFERENCE CORE | Belongs ONLY in JOURNAL EXTENSION |
|---|---|
| Distilled micro-encoder `f_θ` = `Û(a|q)` | Continual learning after deployment |
| Separated learned `Û` + measured `C(a|s)` | Router update when edge SLM changes |
| Runtime `argmax_a[Û − λC]` decision | Router update when a new strong model is added |
| KD training scheme (if `methods-v2/03` keeps it) | Domain-shift online adaptation / replay / rehearsal |
| Real Split-LLM measured evaluation | Continual calibration / teacher–student refresh |
| Baselines incl. demoted hidden-state self-router | — |

Continual learning stays in `methods-v2/13` and must not leak into `06`/`12`
(`MICROENCODER_KD_BRIEF.md` §18, §26).

## 6. Scope-lock checklist — re-applied to the proposed micro-encoder

The proposed architecture in `methods-v2/06` passes only if **all** boxes are ✓
(carried forward from `methods/00 §9`, retargeted to the single decided family):

- [ ] Decides **per query**, at the **edge**, **before** committing to a path.
- [ ] Chooses among {edge SLM, Split-LLM(d), cloud LLM}; the Split path is real.
- [ ] Implements `R(q)=argmax f_θ` (or a monotone reparametrisation via `Û`),
      with the action↔model notation reduction written out.
- [ ] Optimises `U − λC`; `U` a defined quality metric, `C` a scalar cost with
      stated units, λ adjustable at runtime (not baked into weights).
- [ ] Router is **lightweight** and edge-resident (req. A); the micro-encoder is
      the only learned inference-time component.
- [ ] Captures query difficulty/uncertainty (req. B).
- [ ] Reflects communication/compute/latency cost via measured `C(a|s)` (req. C).
- [ ] States honestly how it adapts to new models (req. D) — **no unearned
      "no-retraining" claim**; adaptation beyond cheap re-profiling is journal
      work (§5).
- [ ] KD is justified against primary prior art or dropped — **no novelty by
      adjective** (`MICROENCODER_KD_BRIEF.md` §15, §26).
- [ ] Does not silently become a scheduler, benchmark, calibration-only study,
      Jacobi paper, or a cloud-API stub for Split.

---

## 7. Deliverable manifest for this sprint (status tracker)

Required under `methods-v2/` (`MICROENCODER_KD_BRIEF.md` §24):

| File | Status |
|---|---|
| `00-meeting-decisions-lock.md` | **DONE (this file)** |
| `01-microencoder-prior-art.md` | TODO |
| `02-kd-prior-art.md` | TODO |
| `03-kd-formulations.md` | TODO |
| `04-teacher-options.md` | TODO |
| `05-student-architecture.md` | TODO |
| `06-proposed-method.md` | TODO |
| `07-training-labels.md` | TODO |
| `08-system-cost-integration.md` | TODO |
| `09-split-llm-integration.md` | TODO |
| `10-model-pool-and-baselines.md` | TODO |
| `11-novelty-stress-test.md` | TODO |
| `12-conference-experiment-plan.md` | TODO |
| `13-journal-continual-learning-extension.md` | TODO |
| `14-publication-staging.md` | TODO |
| `15-architecture-figure-spec.md` | TODO |
| `16-advisor-and-lab-open-questions.md` | TODO |
| `17-verified-references.md` | TODO |
| `method-references.bib` | TODO |
| `proposed-solution-blue.tex` | TODO |
| `FINAL-SUMMARY.md` | TODO |
| `architecture-figure.tex` (if practical) | TODO |

This tracker is advisory; the gnhf `notes.md` remains the authoritative progress
log.
