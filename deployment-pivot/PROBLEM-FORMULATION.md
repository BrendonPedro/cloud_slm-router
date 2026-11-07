# Deployment-pivot problem formulation (2026-11-07)

This document compares candidate systems formulations, selects the minimal one, and
writes it down as an explicit optimisation problem.

Inputs:
- `LIT-REVIEW.md`: the novelty gap and the regimes where split helps.
- `decision/GO-PIVOT-REPORT.md` with E1–E3: the semantic layer is a task lookup.
- Three cached-data / analytic checks in `evidence/`:
  - `size_class_table.md`: edge-class vs remote-class accuracy and output tokens.
  - `split_bound.md`: per-token SPLIT vs REMOTE bound.
  - `joint_vs_sequential_sim.{py,md}` (new): joint vs decomposed policies under four live states.

**Bottom line.**
- **Selected: F3, a constraint- and load-indexed joint (model, path) table.**
  SPLIT enters the action set **only if E0 passes**.
- On assumed profiles, the joint EDGE/REMOTE part is worth **≤ ~3 pt** over the
  strongest decomposed baseline, and only when the server is contended.
- **Link RTT never changes an EDGE/REMOTE decision** for these workloads.
- So the contribution cannot rest on "network-aware routing". It rests on:
  1. measured coupling between model feasibility and path (edge memory, privacy class,
     server load);
  2. SPLIT, if and only if E0 finds a regime for it.

  If neither yields the frozen margin (§6), the deployment thesis fails (see GO-NOGO).

---

## 1. What the evidence fixes before any formulation is chosen

| Fact | Source | Consequence for the formulation |
|---|---|---|
| Semantic value = recognising the task (+3.3 pt), plus a cost-aware task/sub-task table; the per-query residual is ≤ 1 pt and λ-fragile | E1, E2 | The model-utility layer is a **lookup** `Q[t,m]`, not a predictor. |
| TF-IDF + LinearSVC recognises the task at 99.58% in about 5 ms on a CPU | E3 | The recognizer costs nothing in the systems budget; it sends `t̂` and a confidence. |
| Edge-class 8B models match 235B accuracy on 4/5 shared benchmarks but emit **2–20× more tokens** (median 400–16,900) | `size_class_table.md` | Latency is dominated by `N_out × per-token time`. The per-(task, model) **token distribution** is a first-class input. |
| SPLIT pays one RTT **per generated token**; REMOTE pays RTT once | `split_bound.md`, In-Browser, Cunningham, HAT | Link state matters **for SPLIT only**. For REMOTE it is a constant ≤ 0.3 s against generations of tens to hundreds of seconds. |
| Every measured split study except one (Splitwise-UCC, questionable) finds SPLIT slower than an uncontended REMOTE | `LIT-REVIEW.md` §4 | SPLIT can only be chosen when REMOTE is **excluded or degraded** and EDGE is **infeasible or too weak**. |
| Joint routing + allocation is published for the datacenter; EDGE/REMOTE model selection is crowded; Mix-or-Split already does per-request mode choice from live state without model choice | `LIT-REVIEW.md` §3, §5 | A formulation without (model choice × edge path × measured state) duplicates prior art. |

### 1.1 New pre-hardware check: does joint choice or live state matter for EDGE/REMOTE?

`evidence/joint_vs_sequential_sim.py` setup:
- **Data:** the 5 benchmarks cached for both pools; 3 edge-class and 2 remote-class
  models. The actions are an 8B on EDGE, an 8B on REMOTE, or a large model on REMOTE.
- **Utility:** correct **and** on time, so a late answer counts as 0.
- **Profiles (ASSUMED):**
  - edge 8B at 15 or 40 tok/s;
  - server single-stream decode: 8B at 90 tok/s, 235B-A22B at 45 tok/s, DeepSeek-V3 at 30 tok/s;
  - device power: 30 W while computing, 3 W while waiting.
- **States:**
  - good: RTT 20 ms;
  - high-RTT: 300 ms;
  - server-contended: 0.25× throughput;
  - remote-down.

Results at edge 40 tok/s (on-time utility; full table in `evidence/joint_vs_sequential_sim.md`):

| State | Deadline | Joint + live | Strongest decomposed baseline: deadline-aware model table, REMOTE-only, live, + edge failover | Deployment-oblivious model → best path | Edge-only |
|---|---|---|---|---|---|
| good | 60 s | 0.546 | 0.546 | 0.442 | 0.278 |
| high-RTT | 60 s | 0.546 | 0.546 | 0.442 | 0.278 |
| contended | 60 s | **0.349** | 0.332 | 0.200 | 0.278 |
| down | 60 s | 0.278 | 0.278 | 0.027 | 0.278 |
| good | 300 s | 0.723 | 0.723 | 0.719 | 0.556 |
| contended | 300 s | **0.600** | 0.573 | 0.559 | 0.556 |

Readings, all conditional on the assumed profiles:
1. **RTT 20 → 300 ms changes the optimal action for 0 of 5 tasks.** A network-aware
   EDGE/REMOTE optimiser has nothing to optimise on these workloads.
2. **Server contention flips 2–3 of 5 tasks.** The decision-relevant live state is
   **server load and availability, not the link**.
3. Joint + live beats the strongest decomposed baseline **only when the edge is fast and the
   server is contended**: +1.7 pt at 60 s, +2.7 pt at 300 s. At 15 tok/s it gives +0.0.
4. Big apparent gains appear only against weak baselines:
   - +10 pt over the deployment-oblivious table at a 60 s deadline. That is
     deadline-aware model choice, i.e. cost-aware routing (Avengers-Pro / R2-Router
     style), not a systems effect.
   - +∞ over a REMOTE-only policy on outage. That is trivial failover.
5. **Device energy always favours REMOTE.** Waiting on the radio costs less than decoding
   locally. An energy objective therefore creates no EDGE regime unless *server*
   energy or money is charged to the request.

Implication: **EDGE/REMOTE-only joint optimisation is unlikely to clear any
meaningful margin.** The value has to come from constraints that exclude REMOTE
(privacy class, outage, capacity) combined with an action that is stronger than
EDGE-small. That action is SPLIT of a model too big for the edge, which is why E0
is decisive.

---

## 2. Candidate formulations compared

| | F1 Static task-aware (model, path) table | F2 Split-aware constrained table | **F3 Constraint- and load-indexed joint table (selected)** | F4 Fleet capacity sharing | F5 Full joint MINLP |
|---|---|---|---|---|---|
| Actions | (m, EDGE / REMOTE) | (m, EDGE / SPLIT(d) / REMOTE) | (m, EDGE / REMOTE [/ SPLIT(d) iff E0 passes]) | per-task offload fraction across K edge clients + 1 server | m, path, d, resident set, memory, batch, bandwidth share |
| State used online | none | none (privacy class only) | server load/availability bucket; link bucket only if SPLIT is in the set | server queue (endogenous) | everything |
| Offline optimisation | per-task argmax | per-(task, privacy) argmax + resident set | per-(task, privacy, state-bucket) argmax + resident set | MILP / fluid model over routing fractions | MINLP |
| Closest prior art | ECO-LLM, 2507.15553 (already a lookup table) | Unified AI Gateway (analytical, PD split); EdgeShard (no model choice) | Mix-or-Split (no model choice), HW-Router (no edge), Unified AI Gateway (analytical) | RouterWise / 2604.07472 (datacenter), Mix-or-Split (multi-device) | BOute, RouterWise |
| Novelty | **Weak.** Duplicates ECO-LLM + 2507.15553 | Medium, but **conditional on E0** | Narrow but real *as a measured combination*; conditional on E0 or a contention regime | Medium; queueing coupling is new at the edge | None from the algorithm; the variables are unidentifiable on our testbed |
| Pre-hardware evidence of value | Collapses to "REMOTE + deadline-aware model table" in good states (§1.1) | Unknown; needs E0 + 14–32B utility entries | ≤ +2.7 pt (EDGE/REMOTE); SPLIT unknown | Contention is where decisions flip (§1.1), so making it endogenous is the natural escalation | — |
| Semester feasibility | Easy | Medium: one split runtime + E0 | Medium: F2 + a server-load probe | Hard: multi-client load emulation, queueing validation | Infeasible |
| Verdict | **Reject as contribution**; keep as the "static" ablation | **Merged into F3** as its SPLIT branch | **Select** | **Reserve** as the escalation if F3 misses its margin only for lack of contention | **Reject** |

Variables rejected and why (the "reject unnecessary complexity" pass):
- **Batch / resource allocation.** The edge is single-user. The server runs vLLM with its
  own scheduler, and allocating it is RouterWise/BOute's problem, already solved.
  We *observe* server load; we do not control it.
- **Bandwidth as a decision variable.** It is state, not control. It matters only to
  SPLIT, and there only weakly: about 8–16 KB per token, so RTT dominates (`split_bound.md`).
- **Monetary cost.** We own the server, so $ is not a binding constraint. Report
  tokens, and price $ at published API rates as a secondary column only.
- **Energy as an objective.** Device energy favours REMOTE everywhere (§1.1, reading 5).
  Keep it as a **reported metric** and an optional per-query device budget
  `E_t`. Do not scalarise it into the objective.
- **Online split depth d.** Per-token network time is independent of the cut
  (In-Browser Split). So d is fixed **offline** by edge memory, edge compute
  share and leakage, and is not re-chosen per request.
- **Per-query output-length prediction.** E2 showed the per-query residual is ≤ 1 pt
  and λ-fragile. Use the task-conditional **distribution** `F_N[t,m]`.
- **Post-generation cascades** (edge first, then escalate). Generations are thousands of
  tokens long, so a failed edge attempt costs most of the deadline. Keep it as an
  ablation, not a formulation.

---

## 3. The selected problem (F3)

### 3.1 Sets and inputs

| Symbol | Meaning | Source |
|---|---|---|
| `t ∈ T ∪ {∅}` | task (recognizer class); `∅` = low-confidence / unknown | E3 recognizer label set |
| `m ∈ M` | candidate models (2–4 total: e.g. one edge-class 8B, one mid 14–32B split candidate, one large remote) | HARDWARE-PLAN |
| `a = (m, p, d)`, `p ∈ {EDGE, SPLIT, REMOTE}` | action. SPLIT is in `A` **iff E0 passes**; d is fixed per model offline | E0 |
| `c ∈ {open, no-raw-text, local-only}` | privacy class of the request (from application metadata or task, not inferred per query) | declared |
| `A(c, R)` | admissible actions: `local-only` → EDGE; `no-raw-text` → EDGE ∪ SPLIT(d ≥ d_min); `open` → all. Only models resident in `R` may use EDGE/SPLIT | declared + `R` |
| `s = (κ, up, ρ, B)` | live state: server per-token slowdown `κ ≥ 1` (from server queue / TPOT metrics), remote availability, RTT, uplink bandwidth | runtime probes |
| `S` | buckets of `s`: κ ∈ {1, 2, 4}, up ∈ {0, 1}; ρ ∈ {≤10, 10–50, >50 ms} **only if SPLIT ∈ A** | declared |
| `Q(q, m)` | per-query correctness of m (cached or measured, multi-sample mean when available) | LLMRouterBench / new labels |
| `N(q, m)`, `n_in(q)` | per-query output/input tokens of m | same |
| `D_t` | per-task deadline (end-to-end seconds) | declared, swept |
| `E_t` | optional device-energy budget per query | declared, swept |
| `M_e` | edge accelerator memory | HARDWARE-PLAN |

### 3.2 Measured system profiles (offline, per action)

Per-request latency, written to match `paper/main-revised.tex` §Cost model with the
server slowdown `κ` added:
```
T_EDGE(m)   = τpre_e,m(n_in) + N · τdec_e,m
T_REMOTE(m) = ρ + 8·n_in·β_tok/B + w(κ) + τpre_c,m(n_in) + N · κ · τdec_c,m
T_SPLIT(m,d)= τpre_e,m,d(n_in) + n_in·h·b/B + ρ + κ·τpre_c,m,S−d(n_in)
              + (N−1) · ( τdec_e,m,d + ρ + h·b/B + κ·τdec_c,m,S−d )
```
Device energy: `E_a = P_active,a · t_compute,a + P_wait · t_wait,a`, measured with an
external meter or RAPL/NVML. Memory: `mem(m, p, d)` = weights + KV at the max context.
Each τ is **measured** as a distribution (per-token p50 and p95), not assumed.
`b` is the activation element size. It is fp16 unless E0 qualifies a compression
(LIT-REVIEW: naive INT8/INT4 is catastrophic).

### 3.3 Decision variables

- **Offline:**
  - the edge-resident set `R ⊆ M` (with the split prefix for split models);
  - the policy table `π: (T ∪ {∅}) × C × S → A`.
- **Online:** none beyond a lookup. Optionally, re-solve the same argmax over the
  continuous `s`. That is equivalent because `|A| ≤ ~6`, and is a reported ablation.

### 3.4 Objective and constraints

Utility and system cost are kept separate. **Utility is deadline-aware
correctness.** System quantities are constraints or tie-breaks, never folded into a λ.

For each `(t, c, s)`:
```
π*(t,c,s) = argmax_{a ∈ A(c,R)}  U(t,a,s) := (1/|Q_t|) Σ_{q∈Q_t} Q(q,m_a) · 1[ T_a(q,s) ≤ D_t ]
            s.t.  (1/|Q_t|) Σ_q E_a(q,s) ≤ E_t                      (optional device budget)
                  mem(m_a, p_a, d_a) fits in R                     (residency)
            tie-break: lower p95 latency, then lower device energy
```
`T_a(q, s)` uses the **per-query** cached `N(q, m)`, so correlated hardness and
length are preserved. Hard queries are the long ones. Taking the mean accuracy times
the mean length would bias U upwards.

Resident set (offline, enumerated, since `|M_edge-capable| ≤ 3` gives ≤ 8 subsets):
```
R* = argmax_R  Σ_{t,c,s} w_t · w_c · P(s) · U(t, π*(t,c,s;R), s)
     s.t. Σ_{(m,p,d) resident} mem(m,p,d) ≤ M_e
```
The state weights `P(s)` are **declared, not tuned**. Results are reported **per state**
and for two declared mixes: "good-dominated" (0.8 good / 0.15 contended / 0.05 down) and
"stressed" (0.4 / 0.4 / 0.2).

Unknown task `∅`:
- its row uses the pooled distribution over all tasks;
- `t̂` is mapped to `∅` when the recognizer margin is below a threshold fixed on
  validation data, at most 1% of in-distribution traffic.

Pareto reporting: sweep `D_t ∈ {30, 60, 120, 300, 600} s` and `E_t ∈ {∞, 2 budgets}`.
Report (on-time utility, p95 latency, device J per query) frontiers, not one scalar.

### 3.5 What is predicted, looked up, measured and optimised

| Item | Predicted | Looked up | Measured offline | Measured online | Optimised offline | Optimised online |
|---|---|---|---|---|---|---|
| Task `t̂` | ✔ TF-IDF + LinearSVC (≈5 ms CPU) | | | | | |
| `Q(q,m)`, `N(q,m)` distributions per task | | ✔ | ✔ (cached; new models labelled on a ≤ 200-query sample per task) | | | |
| τpre, τdec, P, mem per action | | ✔ | ✔ (E0 / profiling) | | | |
| κ, up (server load / availability) | | | | ✔ (server TPOT / queue metric, heartbeat) | | |
| ρ, B | | | | ✔ (only if SPLIT ∈ A) | | |
| `R`, `π` table | | | | | ✔ (enumeration) | |
| Action for a request | | ✔ `π(t̂, c, bucket(s))` | | | | ✔ optional exact argmax over ≤ 6 actions |

### 3.6 Interface from the routing component (Task D)

The deployed semantic component is **task lookup with the TF-IDF recognizer** (E3).
- It runs a sub-task table only where sub-labels exist (E2: korbench, livecodebench).
- No encoder is used unless the out-of-benchmark robustness test (GO-PIVOT §5) shows
  lexical recognition fails. That test is a separate, cheap check, not part of this sprint.

It sends exactly `⟨t̂, margin, n_in⟩` per request. The privacy class `c` comes from the
application, not the recognizer. The recognizer sends no utility estimate: utility is a
table row keyed by `t̂`.

### 3.7 Why the "optimizer" is a lookup, and where the contribution must be

The action set is ≤ 6 and the table has ≤ |T| × 3 × 6–18 cells, so the optimisation is
**enumeration**. **No algorithmic novelty is claimed.** The claim is empirical:
1. Model choice and path must be chosen jointly. A decomposed design is (a) a
   deadline-aware model table on the best fixed path, (b) state-aware path selection,
   and (c) trivial failover. Joint choice should beat this decomposed design in a
   **measured** regime: one where the feasible set of a model depends on path
   (memory, privacy) and state (server load).
2. SPLIT of a model larger than edge memory opens a quality tier for `no-raw-text`
   and degraded-remote traffic that EDGE cannot reach. This holds **only if E0 passes**.

---

## 4. Hypotheses this formulation must survive

- **H-split** (E0; frozen in `E0-SPLIT-VIABILITY.md`). Splitting the same model is
  output-equivalent, and in some measured (RTT, κ) regime it beats the better of
  EDGE-best-resident and REMOTE on on-time utility or on p95 at equal utility.
- **H-joint.** For at least one non-trivial state (contended or `no-raw-text`; *not*
  plain outage), joint + live on-time utility beats the **strongest decomposed
  baseline** (BASELINES.md) by **≥ 3.0 pt** with a paired-bootstrap 95% CI > 0, on
  measured profiles.
  - Pre-hardware estimate for EDGE/REMOTE only: +0.0 to +2.7 pt (§1.1). This is
    **expected to fail without SPLIT or a privacy constraint**, which is stated in
    advance.
- **H-state.** Live state changes `π*` for ≥ 20% of (task, class) cells between the
  good and contended buckets. Otherwise a static table suffices, and the formulation
  is F1, which is prior art.
  - Pre-hardware estimate: 40–60% of tasks flip under contention; 0% under RTT.

If H-split fails, SPLIT is removed from `A`. F3 then reduces to EDGE/REMOTE, and
H-joint must pass on contention or privacy alone. If H-joint fails as well, the
deployment thesis is falsified (GO-NOGO §8). The fallback is the F4 escalation, but
only if the failure is explained by insufficient contention; otherwise the measurement/
analysis paper.

## 5. Known weaknesses of the selected formulation

- **Contention is exogenous here.** We emulate κ with a server load generator, and a
  reviewer can call the state mix arbitrary. Mitigation: per-state reporting, two
  declared mixes, and F4 as the principled version.
- **The privacy class leans on SPLIT** being less leaky than REMOTE. Cunningham recovers
  about 35% of tokens at an 8-layer cut, so `no-raw-text` must be defined as
  "raw text never leaves the device", and the measured leakage must be reported, not
  claimed as privacy.
- **The quality entries for a mid-size split model (14–32B) are not cached.** They need
  new labels on a small per-task sample. This is the only new quality measurement F3
  requires.
- **All §1.1 numbers use assumed profiles.** They show which variables *can* matter;
  they do not size the final effect.

## 6. Frozen numbers carried forward

| Name | Value | Used by |
|---|---|---|
| H-joint margin | ≥ 3.0 pt on-time utility vs strongest decomposed baseline, 95% CI > 0, in ≥ 1 non-outage state | GO-NOGO, BASELINES |
| H-state threshold | `π*` changes in ≥ 20% of cells between good and contended | GO-NOGO |
| Deadlines | {30, 60, 120, 300, 600} s per query | all |
| State buckets | κ ∈ {1, 2, 4}; up ∈ {0, 1}; ρ buckets only with SPLIT | all |
| Declared mixes | good-dominated 0.8/0.15/0.05; stressed 0.4/0.4/0.2 | reporting only |
| Unknown-task threshold | margin quantile giving ≤ 1% ∅ on validation | recognizer |
