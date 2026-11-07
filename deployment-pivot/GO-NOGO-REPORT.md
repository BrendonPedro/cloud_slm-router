# GO / NO-GO on the deployment-optimisation pivot (2026-11-07)

## Decision: **MODIFY**

Keep the pivot to deployment optimisation, but **do not write the paper that was
proposed** ("a network-aware joint EDGE/SPLIT/REMOTE optimiser"). Pre-hardware evidence
already falsifies two of its three pillars:
- **Network awareness.** Link RTT from 20 to 300 ms changes the optimal EDGE/REMOTE
  action for 0 of 5 tasks.
- **Joint EDGE/REMOTE choice.** It is worth −0.8 to +0.0 pt against the strongest
  baseline family, `B*` (cross-fitted, assumed profiles). The pre-registered margin is 3.0 pt.

What survives is one narrow, testable systems question. It is gated by an experiment
that costs about 6 server GPU-hours and needs no new code:

> **Does running a model too large for edge memory as a layer split open a
> deadline-aware quality tier, for traffic whose raw text must stay on the device,
> that the best weight-quantised edge model cannot reach?**

- **If yes (E0 passes):** the paper is the F3 deployment table with SPLIT as that tier,
  judged against `B*`.
- **If no:** SPLIT is removed. The systems thesis then most likely fails (§8), and the
  paper becomes a pre-registered measurement/analysis paper (§8.3).

Both outcomes are publishable in some form. **Only the first is a systems contribution.**

**Prior, stated before any hardware run** (`evidence/e0_r_prior.md`, new this iteration):
- *Thinking mode.* An upper bound that favours SPLIT clears E0-R's 3.0 pt margin at
  D ≤ 600 s in only **6 of 40** hardware/assumption rows, and in **0 of 10** at
  realistic runtime efficiency. So thinking-mode SPLIT is **likely to fail**.
- *Non-thinking mode.* The one plausible regime is non-thinking Qwen3-32B, split, on
  a **12 GB** edge at **30–60 s** deadlines. It was not in the original E0 and was added
  before any hardware access (E0 §3.1 amendment).
- **Our subjective estimate is that the systems version survives with probability well
  below one half.** That is why the first days of work go to the cheap test that can
  kill it (§9, §10).

The decision rests on:
- `LIT-REVIEW.md`: primary sources, including the Mix-or-Split PDF;
- `PROBLEM-FORMULATION.md`: five formulations compared, F3 selected;
- `E0-SPLIT-VIABILITY.md`: frozen, with a pre-hardware amendment;
- `BASELINES.md`: 12 policies and the `B*` rule;
- `HARDWARE-PLAN.md`;
- seven pre-hardware checks in `evidence/`.

**Nothing has been measured on edge or server hardware.** The local machine has no CUDA
GPU, and the DGX and Asus machines are undocumented. Every throughput figure is an
assumption or a spec-sheet roofline.

---

## What changed from the original proposal, and why

| Original element | Status | Evidence |
|---|---|---|
| A semantic router as the core | **Demoted** to a TF-IDF task recogniser feeding a lookup | E1–E3 (`decision/GO-PIVOT-REPORT.md`) |
| Network-aware dynamic path selection | **Dropped** as a claim. RTT never flips EDGE/REMOTE; it matters only for SPLIT | `joint_vs_sequential_sim.md`; LIT-REVIEW §4 |
| "Joint model + path" as the contribution | **Dropped** for EDGE/REMOTE. A live router over fixed deployments (ECO-LLM design) already ties F3 | `baseline_crossfit_check.md`; BASELINES §5 |
| SPLIT as a latency optimisation | **Rejected.** At the roofline SPLIT is 0.31–0.83× REMOTE's per-token rate; every measured study finds SPLIT slower | `hardware_roofline.md` §4; LIT-REVIEW §4 |
| SPLIT as a quality tier under an admissibility constraint | **Kept, conditional on E0** | `split_vs_quant_desk_check.md`; `e0_r_prior.md` |
| Energy as an objective | **Demoted** to a reported metric and an optional budget. Device energy favours REMOTE everywhere | PROBLEM-FORMULATION §1.1 |
| 2×RTX 3090 (48 GB) as "the edge" | **Rejected** for SPLIT. 32B-AWQ fits there, within 2 pt of bf16. The edge class is ≤ 24 GB | E0 §1 |
| Online split-depth optimisation | **Dropped.** Per-token network time does not depend on the cut; depth is fixed offline | In-Browser Split; E0 §3.2 |
| Thinking mode only | **Extended** to (model, mode) actions | `e0_r_prior.md` reading 4 |

---

## 1. What exactly is the new paper problem?

**Deployment selection for task-routed LLM traffic on a memory-limited edge device
plus a shared server.**

Each request carries:
- a task label from a lexical recogniser;
- an admissibility class `c ∈ {open, no-raw-text, local-only}`, set by the application.

The device has an edge memory class `M ≤ 24 GB`, and the server reports its live load
`κ` and availability. The system chooses, offline, which models are resident on the edge
(`R`), and a table `π(t, c, state) → (model, mode, path)` with path ∈ {EDGE, REMOTE},
plus SPLIT iff E0 passes. The table maximises **deadline-aware correctness**: the share
of queries answered correctly within `D_t`. Device energy is a budget, memory is a
constraint, and per-query output lengths are measured.

The formal problem is in PROBLEM-FORMULATION §3:
- the per-query on-time utility `U(t, a, s)`;
- the additive latency model including activation transfer;
- the admissible sets `A(c, R)`;
- enumeration of `R*` and `π*`.

The scientific question the problem exists to answer is the one in the box above.

## 2. Why is it not already solved?

All papers below were read in full text on 2026-11-07. Key numbers were re-checked
against the primary source for Mix-or-Split, RouterWise, BOute and ECO-LLM (LIT-REVIEW §2).

| Paper | What it already does | What it does not do |
|---|---|---|
| **Mix-or-Split** (TPDS 2026, DOI 10.1109/TPDS.2026.3729256; read from the author PDF) | Per-request mode choice {edge, cloud, split} from live state, measured | Runs one model at a time, with no model choice and **no quality term**. Its "split" is **prefill/decode disaggregation**, not a layer split. Its fixed Split was its worst policy (SLO 66.7%). It names multi-model deployment as future work |
| **RouterWise** (2604.10907) / **BOute** (2602.10729) / Cascadia / 2604.07472 | Joint model routing plus GPU allocation under SLOs | Datacenter only. No edge, no network, no split. Their decision variable (provisioning GPUs) does not exist in our setting. We treat server load as exogenous |
| **ECO-LLM** (arXiv v2 Jun 2026) / ConsRoute / CR² / 2507.15553 / HybridInfer | Per-query model + edge-or-cloud choice, some on real hardware. 2507.15553 already compiles the choice into a lookup table | **No split.** ECO-LLM assumes query clustering suffices; we *evidence* that a task table suffices (E1–E3) |
| **Unified AI Gateway** (2609.06940) | Writes down model + site + "split" | Analytical only, no code. Its split is again prefill/decode disaggregation |
| EdgeShard, HAT, Cunningham, In-Browser Split, the drone VLM study, Splitwise-UCC | Measured layer split of **one** model | No model choice, and no comparison with a weight-quantised edge model |

**Exact gap** (LIT-REVIEW §3): no measured system chooses the model, by task utility,
jointly with an execution path that includes a **layer split of a model larger than edge
memory**, and none compares that split against **quantised edge models**.

**Honest limit.** If SPLIT is removed, the remaining EDGE/REMOTE system is not
distinguishable from ECO-LLM + 2507.15553, apart from measured profiles, energy
reporting and our router-sufficiency evidence. That is not enough for a systems novelty
claim.

## 3. What is our single main contribution?

**A measured, pre-registered answer to whether a layer split of a model too large for
edge memory earns a place in the deployment action set against weight-quantised edge
models and remote execution, under deadline-aware utility.** The F3 table is the
vehicle that shows whether that place is worth anything end to end.

The claim takes one of two pre-declared forms, depending on E0:
- **Positive (systems paper).** "For raw-text-local traffic on 12–24 GB edges, a U-shaped
  split of Qwen3-32B is output-equivalent to the unsplit model, and opens an on-time
  quality tier ≥ 3.0 pt above the best quantised edge model. A task-indexed, load-aware
  deployment table that uses it beats the per-cell best of 10 baseline policies (`B*`)
  by ≥ 3.0 pt."
- **Negative (measurement paper).** "Weight quantisation dominates layer split at every
  edge memory class and deadline we measured. Deployment for task-routed traffic
  reduces to a load-aware table over fixed deployments, and network state does not
  change the decision."

We do not claim **algorithmic** novelty. The action set has ≤ ~12 entries, so the
optimiser is enumeration (PROBLEM-FORMULATION §3.7).

## 4. What role does the lightweight router now play?

The router is **a component, not a contribution.**
- It is a **TF-IDF + LinearSVC task recogniser**: 99.58% task accuracy, about 5 ms per
  query on a CPU (E3).
- It uses a **sub-task** label only where one exists (korbench, livecodebench; E2).
- It sends exactly **⟨t̂, margin, n_in⟩** per request.
- If the margin falls below a threshold fixed on validation data (≤ 1% of traffic),
  `t̂ = ∅` and the pooled row is used.
- It sends **no utility prediction**: utility is the table row keyed by `t̂`.
- **No encoder** is used unless the separate out-of-benchmark robustness check
  (GO-PIVOT §5) shows that lexical recognition fails.

Its measured value is +1.3 to +10 pt over the task-blind policies `B-place` and `B-obl`
(BASELINES §5). That value comes from the task-indexed, deadline-aware table, which the
paper reports as an ablation ("F3 with `t̂ = ∅`"). It is not claimed as new.

## 5. Is Split actually necessary to the contribution?

**For a systems contribution, yes.** That is exactly why it must be tested, not assumed.
- Without SPLIT, F3 collapses to `B-route` (ECO-LLM's design). The pre-hardware gap to
  `B*` is −0.8 to +0.0 pt (and within ±1.7 pt of `B-route` everywhere), against a 3.0 pt margin, so **H-joint is expected to fail**,
  as stated in advance (PROBLEM-FORMULATION §4).
- SPLIT is the only action that can create a **new quality tier** inside an admissible
  set. REMOTE is excluded for `no-raw-text`, and quantisation caps the edge.

**For the paper's existence, no.** If E0 fails, SPLIT is removed without changing any
criterion. The paper then takes its negative form (§3) or becomes the analysis paper
(§8.3). Split is never kept because the original paper proposed it.

**Weakness that must be stated.** `no-raw-text` is an *admissibility* rule ("raw text never
leaves the device"), **not privacy**. Activations at shallow cuts are invertible:
Cunningham recovers about 35% of tokens at an 8-layer cut, and our first cut sits only 1–9
layers deep (k ∈ {1, 3, 5, 9}). A reviewer may call the class artificial. The paper must:
- name a concrete deployment rule that forbids plaintext egress;
- report leakage from the literature, or from a cheap inversion test;
- never call SPLIT privacy-preserving.

## 6. What is E0?

E0 is frozen in `E0-SPLIT-VIABILITY.md`, including the 2026-11-07 pre-hardware
amendment that added mode variants.

- **Model and split.** Qwen3-32B bf16, split U-shaped. The edge runs the embedding, the
  first k and last j layers, and the LM head. Two depths: U-min (1,1) and U-max(M) for
  M ∈ {12, 16, 24} GB. Raw bf16 activations cross the link, about 10 KB per token in
  each direction.
- **Hardware.** One ≥ 24 GB NVIDIA edge GPU, with the 12 and 16 GB classes emulated by a
  memory cap. One A100/H100-class server. A wired LAN shaped with `tc netem`.
- **Q, output equivalence.** Two tests:
  - Teacher-forced top-1 disagreement and KL against two noise floors: an in-host
    pipeline cut and Qwen3-8B run on edge vs server. Threshold ≤ floor + 0.2 pp, and
    KL ≤ 2× the floor.
  - A greedy free-run near-tie test: ≥ 27 of 30 first divergences at a margin < 0.5 nats.
- **F, feasibility.** U-max(M) runs at 16k context within the cap, with zero
  transport errors or out-of-memory failures.
- **R, a useful regime.** Some (memory class, admissibility class, state, RTT, deadline
  ∈ {30…600 s}) cell must show **U_SPLIT − U_best-admissible-non-SPLIT ≥ 3.0 pt**, with
  a paired-bootstrap 95% CI > 0.
  - Both sides use (model, mode) pairs.
  - The competitors include the quantised edge models (Qwen3-8B-, 14B- and 32B-AWQ).
- **Measurements.**
  - Q3 accuracy on 200 stratified queries, run on the server only.
  - A 22-cell latency, transfer-volume and energy matrix: RTT {native, 5, 20, 50} ms,
    bandwidth {100 Mbps, 1 Gbps}, server load {0, 8, 32}, plus held-out cells that
    validate the latency model to within ±10%.
- **Pass rule.** E0 PASS = Q ∧ F ∧ R.
- **Early stop.** If, on every task and in each mode, 32B-bf16 beats EDGE-best(16) by
  < 3.0 pt, only the 12 GB class is run.

## 7. What result makes us abandon Split?

Any one of the following, all pre-registered in E0 §8:

1. **Q fails** after one implementation fix. No activation compression is allowed as a
   rescue.
2. **F fails** at every memory class.
3. **R fails.** No cell in the frozen sweep, in either mode, reaches +3.0 pt with CI > 0
   over the best admissible non-SPLIT action.
   - This includes the case where the S1 early stop (Q3 accuracy gaps) already rules
     out 16 and 24 GB and the 12 GB cells then fail.
   - Wins that appear **only at D ≥ 1200 s** do not count. They lie outside the frozen
     sweep, and at such deadlines the decision is trivially "the largest admissible
     model", so it is not an optimisation regime (`e0_r_prior.md` reading 2).
4. **A passing cell disappears** once Qwen3-30B-A3B (4-bit) is added as an edge
   competitor at a memory class where it fits (E0 §3.1).
5. **E0 cannot run.** Day-0 inventory shows no A100/H100-class server (for example, the
   "DGX" is a DGX Spark/GB10, or a V100 DGX with no bf16) and none can be borrowed.
   GPUs are not rented. SPLIT is then **not established**. The paper must not include it
   and proceeds as if E0 failed, with "blocked" recorded rather than "failed".

## 8. What result makes us abandon the deployment-optimisation thesis?

### 8.1 Falsifiers (pre-registered; decided on cross-fitted, measured-profile numbers)

The systems thesis is **falsified** if **SPLIT is removed (§7)** and **either** of
these holds:
- **H-joint fails.** On measured profiles (S4/S5 plus E0-L), no non-outage cell shows
  F3 − `B*` ≥ 3.0 pt with CI > 0. Pre-hardware expectation: −0.8 to +0.0 pt, so it
  fails.
- **H-state fails.** Live state changes π* in < 20% of (task, class) cells between the
  good and contended states. A static table (F1, which is ECO-LLM / 2507.15553) then
  suffices.

It is **also falsified, even with SPLIT**, if any of these holds:
- **Replay is unvalidated.** Trace-driven replay misses the live 50-query × 2-state run
  by more than ±10% on p50 latency, and the live cells alone do not show the margin.
- **Duplication.** A paper appears before submission that does model choice plus a layer
  split, measured against quantised edge models. LIT-REVIEW §5 is re-run once before
  submission.
- **The hardware branch invalidates the setting.** For example, the only available
  server is slower than the edge (GB10), so "REMOTE" is not a meaningful action.

### 8.2 The only permitted escalation

**F4, fleet capacity sharing** (PROBLEM-FORMULATION §2) may be tried only if both hold:
- H-joint fails, **and** the measured F3 − `B-route` gap grows by ≥ 2.0 pt from κ = 1
  to κ = 4 (contention is the variable that matters, but it is too weak when exogenous);
- Film approves.

Otherwise there is no further reformulation. Adding variables until something wins is
the failure mode this sprint exists to prevent.

### 8.3 What the paper becomes if the systems thesis fails

**A pre-registered measurement/analysis paper: "For task-routed LLM traffic, semantic
routing reduces to task lookup, deployment reduces to a load-aware table over fixed
deployments, and layer split loses to weight quantisation."**

Its components:
- E1–E3: no headroom over task lookup; TF-IDF is sufficient;
- the `B*` comparison on measured profiles: "joint" adds nothing over ECO-LLM-style
  routing;
- E0's negative result: quantised-edge dominance, with the measured mechanism (one RTT
  per token × thinking-length outputs);
- the network-irrelevance result.

This is a workshop or analysis-track contribution, not a systems-venue paper. **Film must
agree to this fallback before split-runtime coding starts** (§10, step 1).

## 9. Minimum experiment set for a paper

The schedule is in HARDWARE-PLAN §6. Nothing beyond this list is needed for either form
of the paper.

| # | Block | Machine | Cost | Decides |
|---|---|---|---|---|
| 0 | Day-0 inventory and E0 hardware go/no-go (HARDWARE-PLAN §3) | both | 0.5 h | which branch; whether E0 can run |
| 1 | **S1: Q3 accuracy**, thinking + non-thinking, 32B-bf16 + 8B/14B/32B-AWQ + 8B-bf16, 2 seeds, 200 queries | server | ≈ 6–7 GPU-h, unattended | **E0 early stop**; the quality rows of F3 |
| 2 | S5 EDGE profiles per memory class; S6 F feasibility, edge half; S3 edge noise floor | edge | ≈ 3.5 h | F; edge rows of the latency model |
| 3 | S4 REMOTE profiles vs load; S2 Q1 reference + in-host floor | server | ≈ 3 h | κ(load); Q1 thresholds |
| 4 | **Re-run `baseline_crossfit_check.py` with the measured S4/S5 profiles** (EDGE/REMOTE only) | WSL | minutes | H-joint/H-state without SPLIT, i.e. whether the EDGE/REMOTE conclusions survive real numbers |
| 5 | Split runtime + J1 (Q1/Q2) — **only if S1 does not early-stop every class** | both | ≈ 1 day code + 2 h | Q |
| 6 | J2: E0-L, 22 cells (or the 6 core cells after an early stop) | both, exclusive | 1.5–4 h | R; transfer volume; energy |
| 7 | R computation; F3 vs all baselines on measured profiles | WSL | ≈ 1 h | E0 PASS/FAIL; H-joint; H-state |
| 8 | J3: live replay validation, 50 queries × 2 states | both | 2–3 h | whether the replay numbers can be trusted |

**Total:** about 10–14 server GPU-h, about 6 edge GPU-h, about 6 h with both machines
reserved, and about 1 day of runtime code. No rentals, no field runs, no multi-device
fleet.

## 10. What should Brendon physically do next?

In this order. Steps 2–5 fit in the first day.

1. **Send this report to Film**, and get two answers before building anything:
   - Is MODIFY with this narrowed question acceptable?
   - Is the §8.3 measurement paper an acceptable fallback?

   If Film says the fallback is not acceptable, the right move is to settle the paper's
   direction now, not after a week of benchmarking.
2. **Find out what the "DGX" and "Asus" machines are.** Log in to each machine and to
   the 2×3090 workstation. Run the HARDWARE-PLAN §3 inventory commands and save the
   output to `deployment-pivot/e0/env/<host>.txt`. Read the result against the
   pre-declared branch tables (HARDWARE-PLAN §2.1/§2.2).
   - If the DGX is a GB10/DGX Spark or a V100 machine, stop: E0 is blocked (§7 item 5).
     Ask Film or the lab for A100/H100 time.
3. **Ask for the access E0 needs:**
   - root (`CAP_NET_ADMIN`) on the edge for `tc netem`;
   - an exclusive 6-hour window on both machines (or a SLURM reservation);
   - permission to lock GPU clocks.
4. **On the server:** download Qwen3-32B, Qwen3-8B, and Qwen3-{8B,14B,32B}-AWQ (about
   120 GB), pinned by commit hash. Draw the 200-query sample (`seed=20261107`, E0 §4.4).
   **Start S1** (vLLM batched, both modes, 2 seeds) and let it run unattended.
5. **On the edge, while S1 runs:** do S5/S6. Check that each AWQ model and the U-max
   edge slices load and run within the 12, 16 and 24 GB caps, and record power and
   tokens per second.
6. **When S1 finishes, apply the early-stop rule the same day** and write a one-paragraph
   note to Film:
   - if 32B-bf16 beats EDGE-best(16) by < 3 pt in both modes on every task, only the
     12 GB class remains;
   - if the 12 GB gap is also < 3 pt, SPLIT is effectively dead before any runtime
     code is written.
7. **Then re-run the EDGE/REMOTE baseline check with the measured profiles** (§9 row 4).
   It tells you whether anything other than SPLIT is still alive.
8. **Write the split runtime only after steps 6–7 leave SPLIT alive.** The day-by-day
   version of this, ordered by information gain, goes in `WEEK-EXECUTION-PLAN.md`.

---

## Appendix: stop-condition checklist for this sprint

| Requirement | Where |
|---|---|
| 2025–2026 competitors checked in primary sources; Mix-or-Split read in full | LIT-REVIEW §2 (F / F+V records), `lit-raw/` |
| ≥ 3 materially different formulations compared; one selected | PROBLEM-FORMULATION §2 (F1–F5; F3 selected) |
| Exact novelty gap | §2 above; LIT-REVIEW §3 |
| Explicit optimisation problem | PROBLEM-FORMULATION §3 |
| E0 frozen, with pass/fail rules | E0 §8; pre-hardware amendment in §3.1/§4.3 |
| Hardware measurements known | HARDWARE-PLAN §3–§4 |
| Strong baselines | BASELINES §2–§3 (`B*`, `B-route`, `B-Q`, `B-MoS`) |
| Falsification of the deployment thesis | §7–§8 above |
| GO / MODIFY / ABANDON | **MODIFY** (top) |
