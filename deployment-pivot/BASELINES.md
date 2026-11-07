# Baselines for the deployment paper (frozen 2026-11-07)

This file fixes the baselines that F3 (`PROBLEM-FORMULATION.md` §3) and E0
(`E0-SPLIT-VIABILITY.md` §8-R) are compared against, along with the protocol that keeps
those comparisons fair.

New evidence for this file: `evidence/baseline_crossfit_check.{py,md}`. It re-runs the
EDGE/REMOTE simulation with three changes:
- 2-fold **cross-fitting** by query;
- the **full baseline set** below;
- a **paired, task-stratified bootstrap CI**.

Quality and token counts are cached LLMRouterBench data. Throughputs are the same
**assumptions** as in `joint_vs_sequential_sim.py`.

**Bottom line.**
- **The strongest baseline is a live router over fixed deployments, not the decomposed
  pipeline.** By "fixed deployments" we mean each model is served in one place: the 8Bs
  on EDGE, the large models on REMOTE. This is the ECO-LLM / HybridInfer / ConsRoute
  design.
  - On EDGE/REMOTE it **ties F3 in the contended and outage states**, and is within
    ±1.7 pt of F3 everywhere (cross-fitted).
  - A router whose actions are deployments already chooses "model and path jointly". So
    "joint" cannot be the contribution on EDGE/REMOTE.
  - What F3 adds over such a router is (i) **a new deployment, SPLIT**, which E0 decides,
    and (ii) **choosing which deployments exist** (the resident set `R` under edge
    memory).
- **H-joint is therefore judged against `B*`, the per-cell maximum over the whole
  baseline family** (§3). This tightens PROBLEM-FORMULATION's "strongest decomposed
  baseline".
  - The pre-hardware estimate of `F3 − B*` on EDGE/REMOTE is **−0.8 to +0.0 pt** (§5 table; F3 is within ±1.7 pt of `B-route`). That
    misses the 3.0 pt margin, so **H-joint is expected to fail without SPLIT or a
    privacy class**. This is stated in advance.
- **The quantised-edge baseline is mandatory** (`B-Q`, §2). Without it, any SPLIT result
  is refuted by the obvious reviewer baseline (E0 §1).
- RouterWise and BOute **cannot be implemented as published** on our testbed (§4). Their
  implementable core, load-aware model choice on a server, is already in `B-dec` and `B-route`.

---

## 1. Rules that keep baselines strong

1. **Same information.** Every table baseline gets:
   - the same per-query `(score, tokens)` data;
   - the same measured profiles;
   - the same task label `t̂` from the TF-IDF recognizer;
   - the same deadline `D_t`.

   A baseline uses live state whenever its prior-art analogue does (ECO-LLM, HW-Router,
   Mix-or-Split all do).
2. **Same objective.** Every baseline that picks a model picks it by **deadline-aware
   on-time utility**, the same score F3 maximises. The one exception is `B-obl`, which is
   deployment-oblivious by definition. No baseline is handicapped by being given raw
   accuracy when F3 gets on-time utility.
3. **Same admissibility.** For privacy class `no-raw-text`, REMOTE is inadmissible for
   **every** policy. For `local-only`, only EDGE is admissible. A baseline is never
   scored on an action that F3 is forbidden to take, or vice versa.
4. **Cross-fitting.** Tables are fitted on one half of the queries per task and scored on
   the other half (2 folds, `seed = 20261107`), then the folds are swapped. In-sample
   numbers are reported beside the cross-fitted ones, but **only cross-fitted numbers are
   used to decide**.
   - In the pre-hardware check, in-sample selection inflates utility by 0–1.5 pt for
     most policies.
   - It inflates `B-fixed` under contention by 9 pt, because the fixed choice is unstable.
5. **Hindsight is given to the baselines, not to F3.** `B*` takes the best baseline **per
   cell** after seeing the test results. This favours the baselines, which is the
   conservative direction.
6. **No retuning after unblinding.** The baseline set, the fitting split and the
   metrics are frozen here. A baseline added later, e.g. on reviewer request, is
   reported but does not change a GO/NO-GO decision that has already been made.

## 2. The baseline set

`A_home` = each model in its natural place: edge-capable models on EDGE, large models on
REMOTE, and quantised models on EDGE.

| ID | Policy | Action set | Live state? | Prior-art analogue | Why it is not a strawman |
|---|---|---|---|---|---|
| `B-edge` | **Edge-only**: best edge-resident model per task | EDGE | — | on-device LLM apps; PRISM's local mode | lower anchor; also the only admissible policy for `local-only` |
| `B-remote` | **Remote-only**: best REMOTE (model) per task, deadline-aware | REMOTE | κ | HW-Router / cloud router | the policy F3 itself collapses to in the good state (§5) |
| `B-fixed` | **Best fixed deployment**: one (model, path) for all traffic | 1 action | — | "just deploy model X there" | the practitioner default |
| `B-route` | **Routing with fixed placement**: deadline-aware task table over `A_home` | `A_home` | κ, up | **ECO-LLM, HybridInfer, ConsRoute, CR², 2507.15553** | **strongest pre-hardware baseline**; it already picks a path implicitly through the model |
| `B-place` | **Placement without intelligent routing**: one model for all tasks, path from live state | {m_fix} × paths | κ, up, ρ | Mix-or-Split's mode selection (one model, per-request mode) | isolates the value of the router |
| `B-obl` | **Deployment-oblivious routing**: argmax-accuracy model per task, then best live path for it | m(t) × paths | κ, up | RouteLLM / Avengers-Pro / our E1–E3 router followed by a placer | the "router first, systems second" pipeline the pivot replaces |
| `B-dec` | **Decomposed**: deadline-aware REMOTE-only model table with live κ, plus failover to the best edge model when REMOTE is down | REMOTE ∪ failover | κ, up | HW-Router + an availability fallback | the decomposed baseline from PROBLEM-FORMULATION §1.1 |
| `F1` | **Static joint table**: F3 with the state fixed at nominal | all of `A` | — | ECO-LLM's offline table; 2507.15553's NSGA-II lookup table | equals the "no live state" ablation of F3 |
| `B-Q` | **Quantised edge**: best weight-quantised model that fits edge memory `M`, e.g. Qwen3-32B-AWQ with FP8 KV at 24 GB, 14B-AWQ at 16 GB, 8B-AWQ at 12 GB | EDGE | — | standard practice (AWQ / GPTQ / llama.cpp) | **mandatory for any SPLIT claim**: per vendor numbers it is within 2 pt of bf16 32B wherever it fits |
| `B-MoS` | **Mix-or-Split-style**, used only if SPLIT ∈ `A`: one model (Qwen3-32B) with mode ∈ {EDGE-AWQ, SPLIT, REMOTE} picked per request from live state, with no task-aware model choice | {32B} × paths | κ, up, ρ | Mix-or-Split (TPDS 2026), with its layer-split variant | isolates whether task-aware *model* choice adds anything once SPLIT exists |
| `B-casc` | **Cascade** (an ablation, not part of `B*`): EDGE first, escalate to REMOTE-large if the edge misses a checkpoint (deadline/2) or emits an abstention | EDGE → REMOTE | up | cascades (FrugalGPT, edge-cloud speculative decoding) | reported so reviewers see why cascades lose with long generations |
| `Oracle` | **Upper bound**: per-query best admissible action, in hindsight | all | all | — | headroom only; never a baseline |

### Policies listed in the brief that collapse into the set above

- **"Split-only where viable"** is `B-place` with m_fix = Qwen3-32B and its path fixed to
  SPLIT. It is reported only if E0 passes F. Mix-or-Split's fixed Split was its worst
  policy, with 66.7% SLO attainment.
- **"Routing with fixed placement"** is `B-route`.
- **"Placement optimisation without intelligent routing"** is `B-place`. With a resident-set
  search added it becomes `B-place+R`: the best single model *and* its residency, chosen
  offline. That is reported in the memory-class sweep.

## 3. The comparison that decides H-joint

```
B*(cell) = max over {B-edge, B-remote, B-fixed, B-route, B-place, B-obl, B-dec, F1, B-Q, B-MoS}
           of the cross-fitted on-time utility in that cell
cell     = (memory class M, privacy class c, state bucket s, deadline D)
H-joint passes iff ∃ cell with s ∉ {remote-down}:
           U_F3 − U_B* ≥ 3.0 pt, with a paired, task-stratified bootstrap 95% CI > 0
           (10,000 resamples)
```

- This **replaces** "strongest decomposed baseline" in PROBLEM-FORMULATION §4/§6. The
  decomposed baseline `B-dec` is weaker than `B-route` (§5), so keeping it would
  overstate F3.
- **Outage cells are excluded.** Every policy that fails over is equal there, so a "win"
  there is just failover.
- **Secondary comparisons are reported but do not decide anything:**
  - `F3 − B-route` isolates what SPLIT plus the choice of resident set add over a router
    built on existing deployments;
  - `F3 − B-MoS` isolates what task-aware model choice adds over Mix-or-Split-style mode
    selection;
  - `F3 − B-Q` restricted to `no-raw-text` is E0-R's own test.

## 4. Baselines considered but not implemented

| Candidate | Why it is not implemented | What stands in for it |
|---|---|---|
| **RouterWise** (2604.10907): joint routing fractions + GPU allocation in a cluster | Its decision variables, GPU allocation and parallelism across a pool we provision, do not exist on a single owned server plus one edge. We *observe* server load (κ); we do not allocate it. Reimplementing it would mean optimising a variable our system does not have. | `B-dec`/`B-route` with live κ. These are the load-aware model choice that is RouterWise's routing half. The paper must state that RouterWise solves the server-side allocation that we treat as exogenous, and that the two are complementary. |
| **BOute** (2602.10729): multi-objective BO over model mix × heterogeneous GPUs | Same reason. Its search space is datacenter provisioning, and with `|A| ≤ 6` BO is pointless next to enumeration. | Exhaustive enumeration of `R` and `π` (F3 is already the global optimum over its own space) |
| **Unified AI Gateway** (2609.06940) | Analytical only, with no released code. Its "split" is prefill/decode disaggregation, which is irrelevant where SPLIT could matter (E0 §1, item 4). | Its decision space (model + site) **is** `B-route` + `F3` on measured profiles |
| **TMO / HybridInfer** (RL offloading) | RL over ≤ 6 actions with a known per-cell model is dominated by exact enumeration. An RL baseline would be a weaker policy *by construction* (a strawman). | `F1`/`F3` enumeration |
| Activation-compressed split (RAC) | E0 forbids compression as a rescue. If SPLIT passes uncompressed, RAC is future work. | — |

## 5. Pre-hardware evidence (cross-fitted, EDGE/REMOTE only, edge 8B at 40 tok/s, assumed profiles)

From `evidence/baseline_crossfit_check.md`. Δ = F3 − baseline in points, with the 95% CI.

| Deadline | State | F3 U | `B-route` | `B-dec` | `F1` (static) | `B-place` | `B-obl` | `B-fixed` | Δ vs `B*` |
|---|---|---|---|---|---|---|---|---|---|
| 60 s | good | 0.544 | +1.7 [+0.2, +3.1] | +0.0 | +0.0 | +1.3 | +9.6 | +1.3 | **+0.0** (B-dec / F1 / remote tie) |
| 60 s | contended | 0.349 | **+0.0** | +2.1 [+1.0, +3.6] | +4.2 | +3.0 | +10.1 | +3.0 | **+0.0** |
| 300 s | good | 0.709 | **−0.8** [−2.2, +0.2] | +0.0 | +0.0 | +2.8 | +0.0 | +2.8 | **−0.8** |
| 300 s | contended | 0.593 | **+0.0** | +3.5 [+1.8, +5.5] | +10.0 | +4.6 | +4.2 | +12.8 | **+0.0** |
| either | remote-down | = B-edge | +0.0 | +0.0 | +27.8 / +55.1 | +27.8 / +26.6 | — | — | excluded (failover) |

What this says, under the assumed profiles:
1. **Against `B-dec` alone, H-joint would have "passed"** in the 300 s contended cell
   (+3.5 pt, CI > 0). That is exactly the overclaim the `B*` rule exists to prevent.
   `B-route` closes the whole gap, because the "joint" advantage was only that a router
   over {8B@EDGE, big@REMOTE} can send traffic to the edge when the server is slow, and
   that is already ECO-LLM's design.
2. **Live state is worth +4 to +10 pt** under contention (`F1` vs F3). It is worth 0 under
   RTT changes. Live state is therefore necessary but not novel: `B-route` uses it too.
3. **F3's extra freedom over `B-route`** (an 8B on REMOTE as well as on EDGE) is worth
   +1.7 pt at most, and costs 0.8 pt of overfitting in one cell. Adding actions only pays
   if an action opens a **new quality tier** in some admissible set. Only SPLIT of a
   model larger than edge memory, for `no-raw-text` traffic, can do that.
4. **The router matters** (`B-place` +1.3 to +4.6, `B-obl` up to +10). But the matter is
   a task-indexed deadline-aware table, which is the E1–E3 lookup, not a new semantic router.

**Consequence for the GO/NO-GO decision.** The EDGE/REMOTE-only deployment paper is
**pre-falsified** against `B*` on the simulated profiles. The deployment thesis survives
only through one of:
- E0-R passing, so that SPLIT opens a `no-raw-text` quality tier over `B-Q`;
- measured profiles that differ materially from the assumptions, e.g. a far slower
  contended server or a faster edge. To be checked once with measured numbers before
  any scaling-up.

## 6. Ablations of F3 (reported, never used as `B*`)

| Ablation | Equals | Question |
|---|---|---|
| F3 − live state | `F1` | Does live state matter? (H-state) |
| F3 − SPLIT | F3 on `A \ SPLIT` | What does SPLIT add? |
| F3 − resident-set search | R = the largest model that fits | Does choosing `R` matter? |
| F3 bucketed vs exact argmax over continuous `s` | — | Does state discretisation cost anything? |
| F3 with the task label replaced by `∅` (pooled row) | a task-blind deployment policy | What does the recognizer contribute? (cf. `B-place`) |
| F3 with TF-IDF `t̂` vs gold `t` | — | Recognizer error cost; expected ≤ 0.4% mislabels (E3) |

## 7. Evaluation protocol shared by all policies

- **Metrics:**
  - primary: on-time utility (correct and within `D_t`);
  - secondary: SLO attainment, p50/p95 end-to-end latency, device J/query, server
    GPU-seconds/query, bytes on the wire/query;
  - $ at published API rates, as a secondary column only.
- **Reporting:** per cell, plus the two declared state mixes (PROBLEM-FORMULATION §3.4).
  No single headline scalar unless it is one of the two mixes.
- **Evaluation:** all policies are scored by **trace-driven replay**. Per-query cached or
  Q3-measured `(score, tokens)` are combined with **measured** latency/energy profiles
  from E0-L and the edge profiling runs.
- **Validation of the replay:**
  - F3, `B*`'s winning policy and `B-fixed` are run **live end-to-end** on 50 queries ×
    2 states (good, contended at load 32);
  - replay must match the live run to within ±10% on p50 latency, with identical
    actions;
  - if not, decisions are made only on the live cells.
- **Statistics:** paired, task-stratified bootstrap over queries, 10,000 resamples for
  the decision (the pre-hardware check used 1,000). Holm correction is applied when more
  than one cell is claimed as a win.
- **Code:** one policy module scores every baseline. The pre-hardware version is
  `evidence/baseline_crossfit_check.py`, which is to be extended with measured
  profiles and SPLIT actions, not rewritten.
