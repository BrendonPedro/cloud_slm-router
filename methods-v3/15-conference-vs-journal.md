# 15 — Conference core versus journal continual-learning extension (brief §18)

*Deliverable 15 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 18). Replaces
`methods-v2/13-journal-continual-learning-extension.md` and the scope table of
`methods-v2/14-publication-staging.md` §0. `methods-v2` is unchanged.*

Inputs: `01` §5 (Issue-B table: what each pool change requires), `02`
(Branches X/L1/L2/L3/E), `03` §0, §9, §10 (C\*, E1 rule, N2 withdrawn), `09`
§0, §2, §6 (C-1, `L̂`, E-COST), `10` §8 (M0/M1/M2), `11` (B-IRT, ICL-Router),
`12` (claim register), `13` E6, E8, `14` (Henry H-rows), and
`source/main-original.tex` L54, L65, L182 (read only).

New checks for this file (2026-10-04): arXiv abstract-page `citation_*` meta
tags for the seven CL/calibration papers v2 cited (§6). Only bibliographic
identity and abstract text were checked. **No CL paper body was read in this
sprint**, so no CL source is `[VERIFIED-BODY]`.

Tags follow `00` §0: `[VERIFIED-BODY]`, `[VERIFIED-META]`, `[AUTHOR-CLAIM]`,
`[PROPOSED]`, `[OPEN]`, `[REJECT]`; `[DERIVED]` = follows from the stated
definitions; `[MS]` = stated in `main-original.tex`.

---

## 0. Bottom line

1. **Boundary rule.** The conference paper trains the router **once**, on a
   **fixed** pool, a **fixed** action set and a **fixed** query distribution,
   and then freezes `θ`. Anything that updates `θ` (or a per-model head or
   calibrator) **after deployment because the pool, the edge SLM or the query
   distribution changed** is journal scope. Every conference claim must stand
   if the journal is never written. `[PROPOSED]`
2. **What stays in the conference core:** the micro-encoder student with
   per-model utility heads `Û_θ(M|q)` (`01`), training with C\* and the
   KD variants plus the E1 falsification rule (`03`), post-hoc per-model
   calibration on a fixed calibration split (`03` §7), the C-1 runtime rule with
   measured latency (`09`), Split execution and the E0 equivalence test (`02`,
   `13`), and experiments E0–E8 (`13`). E8 **measures** domain shift. It does
   not adapt to it.
3. **What moves to the journal:** edge-SLM swap, model addition and removal
   after deployment, domain-shift adaptation, continual recalibration, replay,
   previous-router (LwF-style) distillation, adapters, frozen-head model
   addition, profile-conditioned heads for zero/few-shot expansion, and
   forgetting analysis.
4. **Network or hardware change is not a continual-learning problem for `θ`,
   by construction.** It is not "free", though. `L̂`'s offline profiles must be
   re-measured or re-fitted on new hardware (`09` §2, E-COST), and if E-COST
   forces a learned queue/tail model `g_φ`, that component is learned and may
   need refitting. v2's "D4 needs no learning at all" and "robustness for free"
   are corrected to this (§8). `[DERIVED]`
5. **A new split depth of an already-profiled model is not a journal item in
   Branch X.** It needs E0 at the new depth and new cost profiles, nothing in
   `θ` (`01` §5.1). In Branch L2/L3 it needs labels at that depth. The
   conference paper fixes its depth set at the depths that passed E0. If
   Henry's depth is fixed at launch (`14`), depth is a deployment parameter and
   no per-query depth change exists at all.
6. **Manuscript text that is journal-scoped must leave the conference
   version:** L65 ("without reliance on costly retraining … flexible
   integration of heterogeneous models") and the L182 design goal ("remain
   effective as the model pool evolves") make pool-evolution claims the
   conference experiments do not test (§5).
7. **The conference code carries only near-zero-cost hooks** (§4): per-model
   heads and calibrators addressed by model ID, logged per-model outcomes,
   versioned checkpoints and label sets, and the teacher's outputs kept. No CL
   code, no replay buffer, no adapters in the conference build.
8. **No continual-learning element appears in the conference architecture
   figure** (§7).

---

## 1. Why the boundary is drawn here

The test is simple: **could a reviewer reject a conference claim because a
journal experiment failed?** If yes, the claim or the experiment is in the
wrong paper.

* E1 must be able to kill KD (`03` §10). If KD also served as the anti-forgetting
  mechanism of the conference paper, a negative E1 would weaken two claims at
  once. Keeping LwF-style distillation in the journal keeps E1 clean.
* E6 holds by construction (`13` E6). The design keeps system state out of `θ`,
  so network change cannot require retraining `θ`. That is a design property,
  not a continual-learning result. The journal must not re-sell it as one
  (§8, v2 JC1/J5 corrected).
* E8 is a generalization measurement on held-out datasets or topics. It reports
  the drop. It does not recalibrate, replay or adapt (`13` E8). Adaptation to
  the shift it measures is journal scope.

---

## 2. Conference core inventory

| Component | Conference role | Source | CL content |
|---|---|---|---|
| Micro-encoder student + per-model sigmoid heads `Û_θ(M\|q)` | the router | `01`, `07` | none: trained once |
| Optional depth term `Δ̂(d,q)` (Branch L1/L2) | only if E0 fails | `02` | none |
| Teacher (same-data, cross-fitted; optional privileged-information or transfer-set variants) | training only, discarded at inference | `03` §5 | none |
| C\* and the KD ladder, E1 rule | falsifiable KD question | `03` §9–10 | none |
| Per-model post-hoc calibration | fit once on the calibration split | `03` §7 | none |
| C-1 rule, `L̂`, SLA filter | runtime decision | `09` | `L̂` profiles re-measured per testbed (not CL) |
| Split execution, E0 | action realization | `02`, `13` | none |
| Pool M0 (N = 2), M1, M2 | fixed per experiment | `10` §8 | none: each milestone trains its own router |
| E0–E8, E-PILOT, E-BB, E-COST | evaluation | `13` | E8 measures shift only |

Note on M0→M1→M2 (`10` §8): growing the pool **between milestones before
submission** is not continual learning. Each milestone trains its router from
scratch on that milestone's full label set. The conference paper reports each
milestone as its own fixed-pool result. Only **incremental update of a deployed
router** is journal scope.

---

## 3. Journal extension: research questions

The conference router assumes four things stay fixed. Three of them are
learned and give journal research questions. The fourth is measured.

| # | Change after deployment | What breaks | Learned or measured | Scope |
|---|---|---|---|---|
| J-D1 | **Edge SLM swapped or re-quantized** (new checkpoint, new 4-bit method) | `Û_θ(M_edge\|q)` labels are stale | learned | journal |
| J-D2a | **New model added** to the pool | no head for `M_new`; the argmax set changed | learned | journal |
| J-D2b | **Model removed** | operating points of λ/SLA move; no `θ` change needed (`01` §5.1) | recalibration of operating points only | journal (trivial case, reported for completeness) |
| J-D3 | **Query distribution shifts** (new domains or task mix) | `Û_θ` extrapolates; calibration degrades | learned | journal (E8 only measures it in the conference) |
| J-D4 | **Network, server load or hardware change** | `C(a\|s)` changes | measured (`L̂` re-profiled; `g_φ` refit if one exists) | **not CL for `θ`**; conference E6 already covers network change within the profiled hardware |
| J-D5 | **New split depth or new split configuration** (e.g. Henry adds compression) | Branch X: cost only. Branch L: quality at that depth unknown | X: measured (E0 + profile). L2/L3: learned | X: deployment step. L2/L3: journal |

Journal-scope questions that follow (all `[OPEN]`):

* **JQ1 (J-D1, J-D3).** How much does a deployed router forget, and how much
  routing utility does it lose, when it is updated on new outcomes only? Which
  mechanism (replay, regularization, previous-router distillation, adapters)
  recovers it at what label and compute cost?
* **JQ2 (J-D2a).** Does a **frozen-encoder new head**, trained on outcomes of
  `M_new` only, recover the routing utility of full retraining? (`01` §5.2:
  plausible, not demonstrated.) This is a cheap experiment and the most
  directly useful one for the manuscript's L182 goal.
* **JQ3 (J-D2a, zero/few-shot).** Can a **profile-conditioned head**
  `Û_θ(M|q) = σ(g(h_θ(q), p_M))` route to a model with zero or few routing
  labels? IRT-Router and ICL-Router are the prior art for profile/model-as-input
  routing (`05` §1.10, `11` B-IRT/ICL); HyDRA's zero-retraining claim is
  `[AUTHOR-CLAIM]` (`05` §1.3). Any journal claim here must beat these, not
  just our own per-model heads.
* **JQ4 (continual calibration).** After each update, does per-model
  calibration need refitting, and does calibration degrade faster than
  ranking quality? Only the measurement is proposed. v2's statement that "no
  prior CL work measures ECE-under-forgetting for a router" is a
  bounded-search absence claim that was never searched for, so it is
  `[REJECT]` until a search is run.
* **JQ5 (J-D5, lossy branch).** If Henry's split becomes lossy (compression,
  low-bit activations), how many labels at a new depth are needed to fit
  `Δ̂(d,q)`, and can `Δ̂` transfer across depths?

---

## 4. Forward-compatible hooks in the conference code

Only hooks with near-zero cost and no effect on conference results. Each one
exists so a journal experiment can run later without re-collecting data.

| Hook | Cost | Enables |
|---|---|---|
| Heads and calibrators stored per model ID (a dict, not a fixed-width output layer) | none: `01` already uses independent per-model heads | JQ2 (add a head), J-D2b (drop a head) |
| L-GEN outcome log keyed by (query ID, model spec, depth, seed, decoding config, score function version) (`13` §2.3) | storage only | replay sets for JQ1, label reuse for JQ2 |
| Model-spec record: HF ID + revision, quantization method and settings, Split configuration (`10`, `14` H2/H6) | none | detecting J-D1 / J-D5 as a spec change, not silent drift |
| Checkpoint versioning of `θ`, heads, calibrators and the teacher, with the training-label set hash | storage only | previous-router distillation (`θ_old` as teacher), forgetting baselines |
| Teacher outputs `t̃(q,M)` stored for all labelled and transfer-set queries | storage only | journal refresh/distillation without re-running the teacher |
| `L̂` profile tables stored with hardware/software environment log (`14` smoke protocol) | none | J-D4 re-profiling and comparison |
| Query-domain/source tag per query | none | J-D3 splits; E8 already needs it |

**Not in the conference build:** replay buffers, CL losses, adapters,
profile-conditioned heads, any online update path, or any code that writes to
`θ` after training. `[PROPOSED]`

---

## 5. Manuscript consequences (conference version)

| Location `[MS]` | Text | Problem | Conference action |
|---|---|---|---|
| L65 (contribution 3) | "Adaptive and scalable routing without reliance on costly retraining … flexible integration of heterogeneous models … without requiring expensive retraining or large-scale supervision" | Claims pool-integration without retraining. Per-model heads need labels and head training for a new model (`01` §5.1). The router *is* trained on supervised outcomes. | Remove from conference contributions. Replacement per `12` banned-wording table: system adaptation to network state without retraining the semantic router, stated as a design property tested by E6 against the oracle-cost frontier, not as a contribution (`12` K5 `[REJECT]` as novelty). |
| L182 (design goal "Adaptability") | "should generalize across diverse queries and remain effective as the model pool evolves" | The second half is a journal question (JQ2/JQ3). | Keep "generalize across diverse queries" (tested by E8). Move "as the model pool evolves" to future work / journal. |
| L54 (motivation) | "remaining adaptable to evolving model pools and deployment conditions" | Fine as motivation for the problem, but the conference paper only addresses deployment conditions. | Keep as problem motivation. Add one sentence in the conclusion/limitations that pool evolution is future work. |

Conference wording for limitations (draft, `[PROPOSED]`):

> The router is trained once on a fixed model pool. Adding a model requires
> outcome labels for that model and training of its utility head; updating a
> deployed router under model or domain change, and the forgetting and
> recalibration this entails, are left to future work.

---

## 6. Journal mechanisms and their source status

These are the established families a journal method would compose. None is
claimed novel. The status below reflects what was checked **in this sprint**.
v2 labelled all of them `[VERIFIED]` after abstract-level inspection; that
label is downgraded.

| Mechanism | Source (identity checked 2026-10-04 via arXiv `citation_*` tags) | Status | Role for us |
|---|---|---|---|
| Regularization (EWC) | Kirkpatrick et al., "Overcoming catastrophic forgetting in neural networks", arXiv 1612.00796; DOI 10.1073/pnas.1611835114 (from arXiv `citation_doi`) | `[VERIFIED-META]` | data-free ablation if old queries cannot be stored |
| Replay (GEM) | Lopez-Paz, Ranzato, "Gradient Episodic Memory for Continual Learning", arXiv 1706.08840 | `[VERIFIED-META]`; NeurIPS 2017 venue per v2, not re-checked | replay with gradient constraints |
| Replay (A-GEM) | Chaudhry, Ranzato, Rohrbach, Elhoseiny, "Efficient Lifelong Learning with A-GEM", arXiv 1812.00420 | `[VERIFIED-META]`; ICLR 2019 per v2, not re-checked | cheaper GEM |
| Replay (ER, tiny memories) | Chaudhry et al. (7 authors), "On Tiny Episodic Memories in Continual Learning", arXiv 1902.10486 | `[VERIFIED-META]`. The abstract states that joint training on current examples plus a small episodic memory "significantly outperforms specifically designed CL approaches" on four benchmarks `[AUTHOR-CLAIM]` | default candidate for J-D1/J-D3; our items are small `(q, M, S)` tuples |
| Previous-model distillation (LwF) | Li, Hoiem, "Learning without Forgetting", arXiv 1606.09282 | `[VERIFIED-META]`; ECCV 2016 / TPAMI 2018 per v2, not re-checked | `θ_old` as teacher on new queries |
| Adapters | Houlsby et al. (8 authors), "Parameter-Efficient Transfer Learning for NLP", arXiv 1902.00751 | `[VERIFIED-META]`. Abstract: within 0.4% of full fine-tuning on GLUE with 3.6% added parameters per task `[AUTHOR-CLAIM]`; ICML 2019 per v2, not re-checked | parameter isolation for J-D2a |
| Post-hoc recalibration | Guo, Pleiss, Sun, Weinberger, "On Calibration of Modern Neural Networks", arXiv 1706.04599 | as recorded in `03`/`17` (conference citation) | continual recalibration (JQ4) |

The Huszár (PNAS 2018) EWC correction that v2 cited was **not** re-checked;
it must be verified before journal use. **None of the CL entries goes into
`method-references-v3.bib`**, because the conference text should not cite
them except possibly one future-work sentence. If the advisor wants that
sentence, cite at most LwF and one replay paper, after a body read.

Interaction with the v3 KD design `[DERIVED]`: with untempered sigmoid BCE,
an LwF-style term `β·BCE(Û_θ, Û_θold)` on replayed or new queries is again a
mixed-target loss (`03` §3.2), with `θ_old` in place of the teacher. So the
conference trainer can be reused. But LwF's purpose (keep old outputs while
learning new ones) differs from E1's question (does a teacher improve a fixed
student). **A negative E1 does not invalidate LwF as a CL mechanism**, which
corrects v2 `14` §0 ("E1 is a gate on the journal's LwF mechanism").

Interaction with adapters `[DERIVED]`: forgetting on existing heads is zero
by construction **only** if the shared encoder path seen by old heads is
unchanged, i.e. head-only addition or an adapter used only on the new head's
path (which costs an extra partial forward pass). An adapter inserted into the
shared encoder changes the features of every head, so v2's "zero forgetting
on existing actions by construction" holds only in the first case.

---

## 7. Figure and text separation

* `architecture-figure-v3.tex`: training phase (outcomes → teacher → soft
  targets → student) and inference phase (student → `Û_θ(M|q)`; live state →
  `C(a|s)`/`L̂`; runtime optimizer → EDGE / SPLIT(d) / REMOTE). **No** replay
  buffer, adapter, update loop, "model pool evolves" arrow or CL box.
* `proposed-solution-blue-v3.tex`: one sentence in "Assumptions and
  limitations" (§5 draft above). No CL citations in the method body.
* A separate journal figure, if ever drawn, adds the update loop around the
  frozen conference figure, not inside it.

---

## 8. Corrections to `methods-v2/13` and `methods-v2/14`

| v2 statement | Location | v3 status |
|---|---|---|
| "D4 needs no continual learning at all … system-drift robustness … for free" | v2 13 §1 | Partly right. `θ` needs no update by construction, but `L̂` profiles need re-measurement on new hardware and any learned `g_φ` may need refitting (§0 item 4). "For free" `[REJECT]`. |
| "Demonstrating D4 needs zero learning is itself a result" (JC1), J5 as an experiment that "confirms the conference decoupling" | v2 13 §4, §5 | `[REJECT]` as a research result: it holds by construction (`13` E6). The measurable question (decision regret under network change versus the oracle-cost frontier and B-INT) is already the conference E6. |
| "No prior CL work measures ECE-under-forgetting for a router" (JC2) | v2 13 §4 | `[REJECT]`: unsearched absence claim. Kept only as a measurement question (JQ4). |
| CL calibration builds on "N2 calibration advantage of the distilled student" | v2 13 §2.5, §4, §8 | N2 is withdrawn (`03` §0 item 8). JQ4 measures calibration under updates for whatever router E1/E4 select. |
| "adding a new strong model = freeze encoder, add head + adapter → zero forgetting by construction" | v2 13 §2.4 | True only for head-only or new-path adapters (§6). |
| "adding a model … at O(one head) cost" (JC3) | v2 13 §4 | Label cost dominates: `M_new` must be run and scored on (a subset of) training queries (`01` §5.1). Head-training cost is the small part. |
| Heads are "per-action" (N sigmoid heads, one per action) | v2 13 §2.4, §6 | Heads are per model (`01`). Split depths are not heads. |
| "E1 is a gate on the journal's LwF-self-distillation mechanism" | v2 14 §0 | `[REJECT]` (§6). |
| All CL sources `[VERIFIED]` | v2 13 §2 | Downgraded to `[VERIFIED-META]` (§6). |
| Conference core = "Û_θ(a\|q)", "KD-5 with T1", "N2/N4 lanes" | v2 14 §0 | Superseded by `01`, `03`, `12`. |

v2 `14`'s Plan A / Plan B staging analysis is not repeated. **Submission
ordering stays an advisor decision `[OPEN]`.** Two v3 facts affect it: E0/E7
depend on Henry (`14`) and are the main schedule risk for the conference; the
journal's JQ2 can start as soon as M0 labels and the trained router exist,
because it needs only outcomes for one more model.

---

## 9. Journal experiment sketch (journal-only; not run, no thresholds)

Each uses the conference router as the starting point and full retraining on
the union of data as the reference. Margins are set from conference variance
data, not invented here (`13` §3.4).

| ID | Question | Conditions | Reference | Honest negative |
|---|---|---|---|---|
| J1 (JQ1, J-D1) | Edge-SLM swap: does the updated router keep routing utility? | no update; naive fine-tune on new outcomes; ER; EWC; LwF-style; ER + LwF | full retrain | naive fine-tune ≈ ER (no forgetting to prevent) |
| J2 (JQ2, J-D2a) | Does a frozen-encoder new head match full retraining? | head-only; head + new-path adapter; full fine-tune with replay | full retrain | head-only clearly worse → new models need encoder updates |
| J3 (JQ3) | Zero/few-shot model addition | profile-conditioned head at 0/k labels; IRT-Router-style; ICL-Router-style (cost-charged) | J2 head-only at full labels | profile conditioning fails to beat a content-blind prior for `M_new` |
| J4 (JQ1, J-D3) | Sequential domain shift | as J1 over a domain sequence | full retrain per stage; static conference router | static router ≈ CL (shift immaterial) |
| J5 (JQ4) | Calibration under updates | recalibrate every update vs never | conference calibration | calibration stable without refitting |
| J6 (JQ5, J-D5) | Lossy new depth: labels needed for `Δ̂(d)` | 0/k labels at new depth; transfer from other depths | full labels at that depth | `Δ̂` does not transfer → per-depth labels required |

Metrics reuse the conference set (`13` §3.1) plus forgetting (drop on earlier
data after an update), backward transfer, labels used and parameters updated.

---

## 10. Open items

* **O-J1** `[OPEN]` advisor: submission ordering (v2 14 Plan A/B).
* **O-J2** `[OPEN]` advisor: whether the conference conclusion carries one
  future-work sentence with CL citations, or none.
* **O-J3** `[OPEN]` lab/deployment: whether edge queries may be stored for
  replay (privacy). Decides ER versus EWC/LwF as the default journal mechanism.
* **O-J4** `[OPEN]` Henry (`14` H3): whether depth can change without restart.
  If not, J-D5 is a redeployment, not an online change.
* **O-J5** CL bodies (LwF, ER, A-GEM, EWC + Huszár correction, Houlsby) must be
  read before any journal writing. Not required for the conference.

---

## 11. Consequences for other deliverables

| File | Consequence |
|---|---|
| `architecture-figure-v3.tex` | No CL element (§7). |
| `proposed-solution-blue-v3.tex` | Limitations sentence (§5). No L65-style retraining claim. "As the model pool evolves" is not a conference design goal. |
| `16-citation-audit.md` | The limitations sentence is our design statement and needs no citation unless CL papers are named. |
| `17-verified-references-v3.md` | List the seven §6 entries as `[VERIFIED-META]`, journal-only, not in the `.bib`. |
| `FINAL-SUMMARY-v3.md` | Q27 (what not to merge): L65 and L182 pool-evolution wording, any CL text. Q24: O-J1, O-J2. |
