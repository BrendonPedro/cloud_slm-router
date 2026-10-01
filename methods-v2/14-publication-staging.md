# 14 — Publication Staging: Conference Core vs Journal Continual-Learning Extension

Brief §19. This deliverable produces the two staging plans the brief requires
(**Plan A**: conference first, then journal; **Plan B**: parallel preparation)
and, for each, states benefits, risks, code reuse, experimental overlap, what
must stay novel/additional in the journal version, and the advisor decision
needed. It does **not** choose a plan — the submission sequencing is an
explicit `[OPEN]` advisor item (brief §2, [00-meeting-decisions-lock.md](00-meeting-decisions-lock.md))
— and it invents **no venue names and no deadlines** (brief §19, §26).

Evidence tags per brief §23: `[VERIFIED]` primary source inspected,
`[RELATED]` adjacent prior work, `[PROPOSED]` our design idea, `[OPEN]`
needs experiment/advisor confirmation.

---

## 0. What is fixed before either plan

The conference/journal split itself is **not** open — the advisor fixed it
(decision #8, [00-meeting-decisions-lock.md](00-meeting-decisions-lock.md); brief
§0, §18, §26):

- **Conference core** = the distilled micro-encoder router: `f_θ=Û_θ(a|q)` (06),
  KD-5 training (03) with the T1 larger-encoder teacher (04), decoupled runtime
  cost `C(a|s)` (08), Split-LLM action (09), experiments **E1–E8** (12).
- **Journal extension** = continual learning **only**, scoped to the three
  learned non-stationarities D1–D3, experiments **J1–J5**
  ([13-journal-continual-learning-extension.md](13-journal-continual-learning-extension.md)).

What is `[OPEN]` is purely the **ordering and overlap** of the two write-ups —
that is the entire subject of this deliverable. Nothing here may move CL into
the conference core or weaken E1's ability to kill KD.

The structural facts that constrain any ordering (all established in earlier
deliverables, re-used not re-derived):

| Fact | Source | Consequence for staging |
|---|---|---|
| Journal is a **strict superset build** on the conference student/heads/loss/labels/teacher/pool | [13](13-journal-continual-learning-extension.md) §6 | journal cannot *finish* before the conference student exists; it can *start scaffolding* earlier (Plan B) |
| D4 (system drift) needs **no learning** | [13](13-journal-continual-learning-extension.md) §1, [08](08-system-cost-integration.md) | the conference core already owns the system-robustness story; the journal must not re-sell it |
| KD must **earn its place** via E1; a negative E1 drops KD (brief stop-cond #4) | [12](12-conference-experiment-plan.md) E1, [03](03-kd-formulations.md) | **conference result E1 is a gate on the journal's LwF-self-distillation mechanism** — see §3 |
| Split numbers need **Henry's code + the F5 losslessness check** | [09](09-split-llm-integration.md), [12](12-conference-experiment-plan.md) E7 | the single largest schedule risk sits in the conference core (E7), not the journal |
| LwF self-distillation = conference KD-5 loss with `θ_old` as teacher | [13](13-journal-continual-learning-extension.md) §2.3 | maximal code reuse; also the reason E1's verdict propagates (§3) |

---

## 1. Shared asset inventory (what both papers draw from)

Staging decisions are really decisions about **when each shared asset is
frozen**. The assets, and which paper first needs each:

| Asset | First needed by | Reused by journal as |
|---|---|---|
| Label pipeline `(q,a,y(a,q))` (07) | conference | replay reservoir items (13 §2.2) |
| ModernBERT-base student + N sigmoid heads (05, 06) | conference | CL update target; adapters insert here (13 §2.4) |
| KD-5 trainer + T1 teacher (03, 04) | conference | LwF self-distill loss; periodic refresh teacher JC4 (13 §2.3) |
| Decoupled cost `C(a|s)` table / `g_φ` (08) | conference | JC1/J5 depend on it being outside θ |
| Split-LLM harness from Henry (09) | conference (E7) | Split-action profile refresh under drift (13 §6) |
| Calibration (temperature scaling) (07) | conference (N2/E4) | continual recalibration (13 §2.5, JC2/J4) |
| Model pool + MP1–MP8 (10) | conference | D2 "add a model" is defined against this pool |

**Reading:** every journal asset is a conference asset plus one additive hook.
There is almost no journal-only infrastructure to build from scratch — the
journal cost is experiments J1–J5 and the CL update code, not a new system.
This is what makes Plan B feasible at all, and what makes the "what must stay
novel in the journal" question (brief §19) sharp: with the infrastructure
shared, the journal's *only* defensible delta is the **CL results and the
calibration-under-forgetting measurement**, never a re-presentation of the
shared stack.

---

## 2. PLAN A — Conference core first, then journal extension

Sequence: finish and submit the conference paper (E1–E8), freeze its student,
*then* build the CL layer and run J1–J5 for the journal.

**Benefits**
- `[PROPOSED]` Cleanest falsifiability firewall: the conference claims
  (N2, N4, and the E1 KD verdict) are settled and published before any CL
  result can entangle them. E1 cannot be "rescued" by a journal result because
  the journal does not exist yet.
- `[PROPOSED]` The journal builds on a **frozen, known-good** student, so J1–J5
  measure CL against a fixed, already-validated baseline rather than a moving
  target — exactly the regime CL evaluation protocols assume
  ([13](13-journal-continual-learning-extension.md) §2.2, single-pass).
- `[PROPOSED]` Lower peak resource and attention load: one paper's experiments
  at a time, matching the "no large-scale training this sprint / bounded GPU"
  posture (brief §0, [12](12-conference-experiment-plan.md) staging).
- `[PROPOSED]` The journal delta is unambiguous — it is literally the set of
  results added after the conference freeze.

**Risks**
- `[PROPOSED]` **Serial latency**: journal work cannot start its experiments
  until the conference student is frozen; total time-to-journal is longest.
- `[PROPOSED]` **Refactor tax**: if conference code is written without the CL
  hooks in mind, the journal may pay to retrofit adapter slots, a reservoir
  buffer, and `θ_old` snapshotting into a frozen codebase. Mitigation is cheap
  and belongs in the conference build — see §4 "forward-compatibility hooks".
- `[PROPOSED]` **Stale pool**: if the model pool (10) drifts between submissions,
  D2 ("add a model") may target models that have themselves changed — re-verify
  model names at journal start (the Qwen3-72B / Gemma `-A4B` invalid-name lesson
  from [10](10-model-pool-and-baselines.md) recurs).

**Code reuse** — maximal and **sequential**: the journal forks the frozen
conference repo and adds the CL update loop (ER buffer, adapter insertion, LwF
loss = existing KD-5 loss with `θ_old`). No shared asset is built twice.

**Experimental overlap** — essentially none by construction: E1–E8 complete
before J1–J5 begin. The only reused *runs* are the conference student
checkpoints and label sets, consumed by J1–J5 as fixed inputs. J5 re-uses the
E6/E7 network/Split testbed but as a *control* (drift needs no learning), not a
re-measurement for the conference claim.

**What must stay novel/additional in the journal** — the CL composition for a
utility-aware edge/Split router, JC2 calibration-under-forgetting, JC3 additive
pool growth, JC1/J5 learning-free system-drift robustness
([13](13-journal-continual-learning-extension.md) §4). The shared stack (student,
KD, cost decoupling, Split harness) is **conference contribution** and must be
cited as prior (self-)work in the journal, not re-claimed.

**Advisor decision needed** — `[OPEN]`: confirm serial ordering is acceptable
given the lab's timeline, and confirm it is acceptable to delay *all* CL
evidence until after the conference submission.

---

## 3. PLAN B — Parallel preparation (journal scaffolding while conference is under preparation/review)

Sequence: build the conference core; while the conference paper is being
written / is under review, begin journal scaffolding (CL update code, reservoir
buffer, adapter slots) and *pilot* J1–J5 on the same student, holding the
conference student frozen for its own experiments.

**Benefits**
- `[PROPOSED]` Shortest time-to-journal: the strict-superset structure
  ([13](13-journal-continual-learning-extension.md) §6) means journal
  infrastructure is ~90% conference infrastructure, so scaffolding can proceed
  the moment the conference student is frozen even if the conference *paper* is
  still in writing/review.
- `[PROPOSED]` Review-wait is not idle: conference review latency is absorbed by
  journal piloting.
- `[PROPOSED]` Early J5/JC1 piloting can *strengthen* (never weaken) the
  conference N3 decoupling story qualitatively — but only as independent
  confirmation; the conference claim must still stand without it (§5).

**Risks**
- `[PROPOSED]` **Falsifiability contamination — the central risk.** There is a
  real dependency: the journal's LwF-self-distillation mechanism
  ([13](13-journal-continual-learning-extension.md) §2.3) *is* the conference
  KD-5 loss. If conference **E1 comes back negative** (KD does not beat the
  α=1 non-distilled control → brief stop-cond #4 drops KD), then the journal's
  distillation-based CL mechanism loses its conference footing and must fall
  back to ER + adapters only. Running J-experiments **before E1 resolves**
  risks building journal results on a mechanism the conference is about to
  discard. **Mitigation / hard gate:** in Plan B, J1–J3 (replay/adapter) may
  pilot early because they do not depend on KD, but **J4 (calibration-through-
  distillation) and any LwF-self-distillation component must not be finalized
  until E1 and E4 have reported.** This gate is the price of parallelism.
- `[PROPOSED]` **Double-counting / salami-slicing perception**: with a shared
  stack, reviewers of the journal may see it as a thin increment. Must be
  pre-empted by a crisp, written conference-vs-journal contribution boundary
  (§5) and by ensuring the journal leads with J-results, not the shared system.
- `[PROPOSED]` **Resource contention**: conference E1–E8 and journal J-pilots
  compete for the same bounded GPU and the same Henry Split testbed — a direct
  conflict on E7/J5 which share hardware. Needs explicit scheduling.
- `[PROPOSED]` **Moving-target risk**: if journal piloting tempts a change to the
  student/heads/loss mid-stream, it can retro-invalidate conference numbers.
  Rule: **the conference student is frozen for conference experiments the moment
  E-runs begin**; journal piloting uses a *copy*.

**Code reuse** — maximal and **concurrent**: same repo, with CL code developed
on a branch against the frozen student. Highest reuse, highest coordination
cost.

**Experimental overlap** — real and must be managed:
- E6/E7 (network/Split testbed) and **J5** (system-drift control) share the same
  testbed and can share capture runs — a genuine efficiency *if* scheduled, a
  conflict if not.
- E4 (teacher-vs-student calibration, N2) and **J4** (calibration-under-
  forgetting) share the calibration harness; J4 extends E4's measurement over
  sequential updates. J4 must wait for E4's baseline.
- The reservoir buffer (13 §2.2) is populated from the *same* label pipeline (07)
  used for E1–E8 — build once, use in both.

**What must stay novel/additional in the journal** — identical to Plan A: the CL
composition + JC1–JC4. The parallelism does **not** change the contribution
boundary; it only changes *when* work happens. The boundary (§5) is what keeps
Plan B from reading as one padded paper.

**Advisor decision needed** — `[OPEN]`: (a) approve concurrent use of bounded
GPU and the Henry testbed for conference + journal; (b) approve the E1-gate on
journal distillation components; (c) confirm the lab is comfortable with the
salami-slicing perception risk and the mitigation (lead journal with
J-results).

---

## 4. Forward-compatibility hooks — the one thing to do *now* regardless of plan

`[PROPOSED]` Independent of A vs B, the conference build should include four
near-zero-cost hooks so the journal never pays a retrofit tax (§2 risk). None
of these changes the conference method, its experiments, or its claims:

1. **Snapshot `θ_old`**: checkpoint the student after conference training (needed
   for LwF self-distillation; it is just a saved checkpoint).
2. **Reservoir buffer interface**: store conference `(q,a,y(a,q))` label tuples
   in a form a reservoir sampler can later draw from (it is the same data 07
   already produces — persist it, don't discard it).
3. **Additive-head API**: keep the N per-action heads independently
   addable/removable (already true by the sigmoid-head design, 06 §2) so D2
   growth is a no-refactor operation.
4. **Adapter slots**: leave the ModernBERT encoder adapter-insertable (standard
   for the architecture, 13 §2.4) — no training cost unless adapters are used.

Documenting these as *conference-build hygiene* (not CL features) keeps CL out
of the conference core while removing the main Plan-A refactor risk.

---

## 5. The contribution firewall (applies to both plans)

The brief's recurring demand — "what must remain novel/additional in the journal
version" — resolves to one written boundary that **both** plans must enforce:

| Belongs to the CONFERENCE (cited as prior self-work in the journal) | Belongs ONLY to the JOURNAL |
|---|---|
| `f_θ=Û_θ(a|q)`, KD-5 training, T1 teacher (06, 03, 04) | CL update loop (ER + adapters + LwF self-distill) for D1–D3 (13 §2) |
| Decoupled cost `C(a|s)`, N3 separation (08) | JC1/J5: *learning-free* system-drift robustness as a **measured CL result** |
| N2 calibration-preserving KD, measured at a single training (E4) | JC2/J4: calibration-**under-forgetting** over sequential updates |
| N4 measured Split activation bytes (E7, 09) | Split-action profile refresh under drift (not a new claim, a maintenance result) |
| Static model pool + MP1–MP8 (10) | JC3: additive pool growth D2, cost vs full retrain |

**Rule, stated for reviewers:** the conference claims must stand **without any
journal result**; the journal claims must be **unobtainable from the conference
paper alone** (they all require *sequential post-deployment updates*, which the
conference design explicitly never performs — 13 §0). If any journal claim could
be made from the conference experiments, it belongs in the conference, not the
journal. This is the test that prevents double-counting under either plan.

---

## 6. Recommendation posture (not a decision)

`[OPEN]` The sprint does **not** pick A or B — sequencing is an advisor call
(brief §2, §19). The honest engineering read, offered as input only:

- **Plan A is the lower-risk default** because it keeps the E1 KD-falsification
  firewall absolutely clean and matches the bounded-resource posture.
- **Plan B is attractive only if** (i) review latency is expected to be long and
  (ii) the lab accepts the E1-gate on journal distillation components (§3) and
  the shared-testbed scheduling cost. The §4 forward-compatibility hooks make a
  *later* switch from A to B cheap, so **building conference code A-style with
  B-ready hooks dominates** — it preserves the option without committing to the
  parallel risk.

Either way the §5 firewall and the §4 hooks are unconditional.

---

## 7. Hand-offs

- **→ [16-advisor-and-lab-open-questions.md](16-advisor-and-lab-open-questions.md):**
  add the sequencing question (A vs B), the E1-gate approval, concurrent GPU /
  Henry-testbed approval, and the salami-slicing acceptance as explicit advisor
  `[OPEN]` items — none to be guessed.
- **→ [12-conference-experiment-plan.md](12-conference-experiment-plan.md):** the
  §4 hooks are conference-build hygiene; E1/E4 are the gates Plan B waits on;
  E6/E7 share a testbed with J5/J4.
- **→ [13-journal-continual-learning-extension.md](13-journal-continual-learning-extension.md):**
  J1–J5 scheduling and the shared reservoir buffer / JC4 teacher reuse are the
  concrete code-reuse items; J4 depends on E4, J5 on E6/E7.
- **→ FINAL-SUMMARY §19 (indirectly) / staging summary:** the two plans, the
  firewall, and the "A-with-B-hooks" posture.

---

## 8. One-paragraph summary for FINAL-SUMMARY

Submission sequencing is an **advisor `[OPEN]`**, not a sprint decision. Two
plans are specified. **Plan A** (conference first, then journal) keeps the E1
KD-falsification firewall cleanest and matches bounded resources, at the cost of
serial latency and a possible retrofit tax. **Plan B** (parallel) shortens
time-to-journal by exploiting the strict-superset structure (journal
infrastructure is ~90% conference infrastructure), but carries a real
falsifiability risk: the journal's LwF-self-distillation mechanism *is* the
conference KD-5 loss, so journal distillation components must be **gated on
conference E1/E4** and the shared GPU/Henry testbed must be scheduled. Four
near-zero-cost **forward-compatibility hooks** (snapshot `θ_old`, persist label
tuples for replay, keep heads additive, leave adapter slots) make conference
code journal-ready without adding any CL to the conference core, so the engineering
read is **"build Plan A with Plan B hooks."** A written **contribution firewall**
(conference = the static distilled router + N2/N3/N4; journal = CL results, JC2
calibration-under-forgetting, JC1/J5 learning-free system-drift, JC3 additive
pool growth) enforces that conference claims stand without any journal result and
journal claims are unobtainable from the conference paper alone. No deadlines or
venues were invented; no experiments were run.
