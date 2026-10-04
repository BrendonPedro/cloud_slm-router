# 09 — Cost function and runtime decision policy (brief §15, Issue C)

*Deliverable 09 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 11). Resolves findings RF-C
(the "network change forces retraining" overclaim) and RF-E (the "λ **is** the
KKT multiplier" overclaim and the arbitrary normalisation) from
`00-review-findings.md`. Takes over the hand-offs from `01` §1.4, §7.2 and §7.3,
from `02` §4.1 and §6, and from `08` §3.2.*

Inputs: `01` (formulation A1, the exact two-stage factorization, Issue-B table),
`02` (Branches X/L1/L2/L3/E, the cost terms of `SPLIT(d)`), `06` (Bao et al.,
NetGPT-routing, Edgent, Neurosurgeon-type partitioners), `08` (`U ∈ [0,1]`,
λ in "normalised score per unit cost"), the manuscript's own system model and
metrics (`source/main-original.tex` L76, L125–L174, L208–L262, read only), and
v2 `methods-v2/08-system-cost-integration.md` (read only).

New checks made for this file (2026-10-04): the official
`Qwen/Qwen2.5-7B-Instruct` `config.json` on Hugging Face (`hidden_size` 3584,
28 layers, `torch_dtype` bfloat16), used only as a worked example of
activation size. No other new sources. The mathematical statements in §4 are
standard results about additive objectives and linear programs. They are
tagged `[DERIVED]` (our derivation, checkable on paper), not cited as
literature.

Evidence tags follow `00` §0. `[DERIVED]` = follows from the stated
definitions by a short argument given here. `[MS]` = what the manuscript
(`source/main-original.tex`) itself says, with line numbers.

---

## 0. Bottom line

1. **Theory keeps the manuscript's objective.** The manuscript's
   `max_R E_q[U(R(q),q) − λ C(R(q),q)]` (L171) stays the theoretical objective.
   Because it is additive over queries, the per-query rule
   `argmax_a [Û − λĈ]` maximizes the plug-in version of it exactly. No duality
   argument is needed for that (§4.1). `[DERIVED]`
2. **No normalised multi-metric scalar online.** v2's choice (SC1: min–max
   normalised, weighted sum of latency, bytes, money and memory) is **rejected
   as the online rule**. Its normalisation ranges and weights are arbitrary,
   they depend on the calibration set and the pool, and they make λ unitless
   and hard to interpret (§3, Option 1). `[REJECT]` for the online rule.
3. **First implementation (C-1): latency is the only priced cost, inside hard
   feasibility constraints.**

   ```
   𝓕(q, s) = { a ∈ 𝒜 :  L̂(a | q, s) ≤ L_SLA,
                         mem_edge(a) ≤ mem_avail(s),
                         a allowed by the deployment's data policy }
   R(q, s) = argmax_{a ∈ 𝓕(q,s)} [ Û_θ(M(a) | q) − Δ̂(a, q) − λ · L̂(a | q, s) ]     (C-1)
   ```

   `L̂` is the predicted end-to-end latency in seconds, built from the
   manuscript's own `T_total = TTFT + (N − 1)·TPOT` (L218) and filled from
   offline profiles plus live RTT, bandwidth and server-queue measurements
   (§2). λ has the unit "normalised score per second". Bytes, energy, money
   and memory are **measured and reported separately** (§5). Bytes enter the
   decision only physically, as transfer time `bytes / bandwidth` inside `L̂`.
   `[PROPOSED]`
4. **Experimentally, C-1 is run as a constrained/SLA policy and evaluated as
   a frontier.** λ is swept to trace quality–latency frontiers (E5). For the
   headline operating point, λ is chosen on validation data to meet a stated
   mean-latency or remote-call budget, and every metric is reported at that
   point (§4.3, §6). This is exactly the brief §15 fallback ("retain λ for
   theory, use a constrained/SLA implementation experimentally"). `[PROPOSED]`
5. **λ is the Lagrange multiplier only of an *average* budget, and only under
   conditions.** For an expected-cost budget over randomized policies, the
   λ-rule is optimal at the right λ, and randomization is needed only on ties.
   For deterministic policies, a λ sweep reaches only the supported (convex
   hull) points of the achievable frontier. A per-query SLA is a feasibility
   filter, not a dualized constraint. v2's "λ **is** the KKT multiplier" is
   replaced by this statement (§4.2). `[DERIVED]`
6. **Systems finding that the method must face (§2.3).** For a standard dense
   decoder, the activation crossing a layer cut is `n_tokens × hidden_size ×
   bytes(dtype)`, so **prefill bytes do not depend on the depth `d`**. Under a
   pipeline split with sampling on the server, each decode step needs a full
   edge↔server round trip. Consequently, (i) depth trades edge compute against
   server compute, not bytes; (ii) if the pool also contains a full-remote
   action for the *same* model, a latency-only cost does not choose
   `SPLIT(d)` whenever the (loaded) server is faster than the edge. `SPLIT` is then justified only by a data-policy constraint
   (raw text may not leave the edge, the manuscript's own privacy motivation,
   L76) or by a server-compute budget. This must be confirmed against Henry's
   implementation (`14`) and changes the novelty wording in `06`/`12`
   (§8). `[DERIVED]` `[OPEN]`
7. **Issue C, rewritten (§7).** System state stays out of `Û_θ` because fresh
   measurements enter the decision directly, the semantic labels need no
   synthetic distribution of network states, one semantic router can be
   reused across deployments, and the two parts can be validated and updated
   separately. It is **not** because an integrated router would necessarily
   need retraining for each network change. That claim is `[REJECT]`.

---

## 1. What the decision has to trade, and what is already fixed

| Item | Fixed by | Content |
|---|---|---|
| Action set | `01` §1 | `𝒜 = {EDGE(M_E), SPLIT_d(M_S) for d ∈ 𝒟, REMOTE(M_R)}`, each action with its model `M(a)`. Whether `M_R = M_S` is `[OPEN]` (`10`, `14`). |
| Utility | `08` (U1) | `U(M|q) = E_ξ[S_D] ∈ [0,1]`; `Û_θ(M|q)` is the student's calibrated estimate. |
| Depth correction | `02` §4, `01` (A1) | `Δ̂ ≡ 0` (Branch X), `Δ̂(d)` (L1), `Δ̂_φ(d,q)` (L2). It is in score units, on the utility side, and never mixed with seconds. |
| Factorization | `01` §1.4 | Under Branch X, `max_a[U(M(a)) − λC(a)] = max_M[U(M) − λ min_{a∈𝒜(M)} C(a)]`. The depth choice is a pure systems decision. |
| Manuscript cost notion | `[MS]` L125, L165 | "`C(M_k,q)` … may include computation, communication, and latency." |
| Manuscript metrics | `[MS]` L208–L262 | TTFT, TPOT, `T_total = TTFT + (N−1)·TPOT`, cold start, throughput, cost per request (RunPod dedicated and Flex), edge energy cost, total cost. |

The manuscript lists several cost dimensions but never says how they combine.
That is the gap brief §15 asks this file to close.

---

## 2. The latency model `L̂(a | q, s)`

### 2.1 State `s`

Measured at decision time on the edge node. `[PROPOSED]`

| Symbol | Meaning | How obtained |
|---|---|---|
| `RTT` | edge↔server round-trip time | smoothed probe / transport-level estimate |
| `BW_up`, `BW_down` | available bandwidth | smoothed throughput estimate; conservative quantile for the SLA check |
| `Q_srv` | server queue length / load | reported by the server with each response or by a heartbeat |
| `cold` | serverless cold/warm indicator | platform status (manuscript L221 measures cold starts) |
| `u_edge`, `mem_avail` | edge utilisation and free memory | local counters |

In the emulated experiments `RTT` and `BW` are set by `tc/netem` (needs
permission, `14`). The router's semantic part never sees `s`.

### 2.2 Per-action latency

Let `n = |q|` (prompt tokens) and `N̂_M` be the expected output length of
model `M`. For the first implementation `N̂_M` is the **per-model median**
output length on the profiling split, so no second learned predictor enters
the conference core. A query-dependent length predictor is an ablation
(§6). `[PROPOSED]`

Profiled tables (offline, on Henry's hardware): `p_E(n)`, `t_E` (edge prefill
and per-token decode time of the edge SLM); `p^{[0,d)}(n)`, `t^{[0,d)}` (edge
time for the first `d` layers of `M_S`); `p^{[d,L)}(n)`, `t^{[d,L)}` (server
time for the remaining layers); `p_R(n)`, `t_R` (server time for the full
remote model). Server times are taken at the measured load level `Q_srv`.

```
EDGE:      L̂ = p_E(n) + N̂·t_E

REMOTE:    L̂ = RTT + bytes_text(n)/BW_up + w_queue(Q_srv) + w_cold
               + p_R(n) + N̂·t_R                       (output tokens streamed back; text bytes are tiny)

SPLIT(d):  TTFT_d = p^{[0,d)}(n) + B_pre(n)/BW_up + RTT/2 + w_queue(Q_srv) + w_cold + p^{[d,L)}(n) + RTT/2
           TPOT_d = t^{[0,d)} + b_dec/BW_up + RTT + t^{[d,L)}           (one round trip per token, §2.3)
           L̂     = TTFT_d + (N̂ − 1)·TPOT_d                              (manuscript L218)
```

`[PROPOSED]` (model structure). `[OPEN]`: every profiled quantity, the queue
model `w_queue`, and the exact SPLIT message pattern depend on Henry's code.
The router's own encoder time is the same for every action, so it does not
change the argmax, but it is added to every reported end-to-end latency.

### 2.3 Two consequences of the split cost model `[DERIVED]`

**(a) Prefill bytes do not depend on depth in a standard dense decoder.**
The tensor crossing the cut after layer `d` is the residual-stream hidden
state, of shape `n × hidden_size`. In standard dense decoder-only models
`hidden_size` is one configuration value shared by all layers. Example:
`Qwen/Qwen2.5-7B-Instruct` has `hidden_size = 3584`, 28 layers,
`torch_dtype = bfloat16` (official `config.json`, checked 2026-10-04). So for
any `d`,

```
B_pre(n) = n × 3584 × 2 bytes = 7,168·n bytes     (≈ 3.6 MB for n = 500)
b_dec    = 7,168 bytes per decode step (one new row)
```

Bytes become depth-dependent only if (i) the split transmits extra state
(position ids or masks are negligible; KV-cache migration is not), (ii) the
compression or quantization at the cut differs by depth, or (iii) the
architecture has non-uniform widths or extra per-layer streams. Each of these
is a question for Henry (`14`). **Consequence:** v2's and `06`'s phrase
"depth-dependent activation bytes" is not a property of the problem by
default. In the exact Branch X, depth trades **edge compute** (`p^{[0,d)}`,
`t^{[0,d)}`, and edge memory for weights and KV) against **server compute**.
This is unlike CNN partitioning (Neurosurgeon-style), where intermediate
tensor sizes vary strongly with the cut. The cost model must say this
explicitly, and the novelty row in `06` §2 must be reworded (§8).

**(b) A pipeline split pays one round trip per output token.** If layers
`[0,d)` run on the edge and sampling happens on the server, then for every
new token the server must return the token (or its id) to the edge, which
embeds it and runs layers `[0,d)` before sending one hidden-state row back.
TPOT is therefore at least `RTT`. The full-remote action streams tokens
without this dependency. **Consequence:** if `REMOTE(M_S)` exists for the same
model `M_S` as `SPLIT_d(M_S)`, then, in the exact branch,
`U(SPLIT_d) = U(REMOTE)` while `L̂(SPLIT_d) > L̂(REMOTE)` whenever the edge
is slower than the server and `RTT > 0`. A latency-only cost then **never**
picks `SPLIT_d` unless `REMOTE(M_S)` is infeasible. That is legitimate when
the deployment forbids raw prompts from leaving the edge, which is the
manuscript's own motivation for Split-LLM (L76, privacy; split activations
are not private by themselves, which is why the manuscript cites SnD, L78).
Otherwise, Split needs a priced reason such as a server GPU-time budget
(§3, C-2). Both conditions depend on Henry's message pattern (speculative or
batched schemes can avoid the per-token round trip) and on the pool (`10`).
`[OPEN]`

This is the single most important systems check of the method. It is
recorded here so that the experiments (`13` E7) measure it instead of
assuming Split is attractive.

---

## 3. Options compared (brief §15)

### Option 1 — Normalised scalar cost (v2 SC1)

`Ĉ = Σ_j w_j · ñ_j` with min–max or z-score normalised metrics.

* The normalisation is a hidden weight: the min and max of each metric depend
  on the calibration set, the pool and the network range emulated, so the
  same `w` means different trade-offs in different experiments.
* λ becomes unitless; "λ = 0.3" has no operational meaning to a systems
  reader.
* It still adds milliseconds, bytes and dollars, only after rescaling. Brief
  §15 asks precisely not to do that.

**Verdict:** `[REJECT]` as the online rule. It may appear only as a reported
sensitivity analysis, if at all.

### Option 2 — Latency-only online penalty, other metrics reported

`Ĉ = L̂(a|q,s)` in seconds.

* One physical unit; λ = "score points per second" is interpretable: λ = 0.01
  means one extra second is worth one percentage point of expected accuracy.
* Bytes are not ignored. They enter through `bytes/BW`, which is the physical
  way communication hurts a user.
* It is what the manuscript measures first (TTFT, TPOT, `T_total`, L210–L218).
* Weakness: by itself it neither caps tail latency nor accounts for money,
  energy or privacy (§2.3(b)).

### Option 3 — Constrained optimization (SLA / budget)

`max Û` subject to latency, memory and policy constraints.

* Per-query hard constraints (SLA, memory, data policy) are natural as a
  feasibility set.
* "Maximize utility subject to a per-query SLA" **alone is degenerate**: it
  picks the strongest feasible model on every query and never saves cost.
  The cost saving must come from an *average* budget (mean latency, remote
  call rate, GPU-seconds), whose Lagrangian form is Option 2's λ (§4.2).

### Option 4 — Pareto frontier evaluation

* Not a decision rule. It is the fairest way to evaluate: no weight choice to
  dispute, and it matches the routing literature's quality–cost curves
  (RouteLLM's APGR/CPT, `05` §1.1).

### Comparison

| Criterion (brief §15) | Opt 1 normalised scalar | Opt 2 latency penalty | Opt 3 constraints | Opt 4 frontier |
|---|---|---|---|---|
| Easiest to interpret | − (unitless λ, hidden ranges) | **+** (score/second) | + (SLA language) | **+** |
| Easiest to implement | ~ (needs fitted ranges) | **+** | + (filter) / ~ (average budget needs λ tuning) | + (sweep) |
| Faithful to manuscript (L171) | + (scalar `C`) | **+** (`C` = latency, one of L165's components) | ~ (different form) | ~ |
| Appropriate for systems evaluation | − | + | **+** (SLA, tails) | **+** |
| Least arbitrary | − | + (one unit) | + (budget is a stated requirement) | **+** |
| Online rule? | yes | yes | filter yes; average budget via λ | no |

**Recommendation: C-1 = Option 2 inside Option 3's hard constraints,
evaluated with Option 4.** `[PROPOSED]`

**C-2 (only if needed, ablation).** If §2.3(b) shows that `SPLIT` is
dominated and the deployment has no data-policy reason to forbid
`REMOTE(M_S)`, add one more priced resource with its own physical unit:

```
R(q,s) = argmax_{a ∈ 𝓕} [ Û − Δ̂ − λ·L̂(a|q,s) − μ·G_srv(a|q) ]
```

with `G_srv` the server GPU-seconds the action consumes. μ is then the price
of server time (score per GPU-second) and relates to the manuscript's
cost-per-request model (L233–L247), since dollar cost per request is
`P_gpu × GPU-time`. Two knobs with physical units are defensible; a weighted
sum of normalised heterogeneous metrics is not. `[PROPOSED]` `[OPEN]` (only
if E7 shows it is necessary).

---

## 4. The mathematics, stated correctly (RF-E)

### 4.1 Per-query argmax is exact for the manuscript objective `[DERIVED]`

For a fixed λ, `E_q[U(R(q),q) − λC(R(q),q)]` is an expectation of a function
of `(q, R(q))` alone. Choosing `R(q)` pointwise as
`argmax_a [U(M(a)|q) − λ C(a|q,s)]` maximizes the integrand at every `q`, so it
maximizes the expectation. Nothing more is needed. With estimates `Û`, `Ĉ`
in place of `U`, `C`, this is optimal only for the plug-in objective. The
decision quality then depends on the calibration of `Û` (`08` §5, `03`) and
on the accuracy of `L̂` (§6, E-COST).

### 4.2 Relation to a budget-constrained problem `[DERIVED]`

Average-budget problem: `max_π E[U] s.t. E[L] ≤ L̄`.

* Over **randomized** policies `π(a|q)`, on a finite query set this is a
  linear program: per-query simplex constraints plus one coupling constraint.
  LP strong duality holds. An optimal policy is the λ-rule at the optimal
  multiplier λ*, and a basic optimal solution randomizes on at most one query
  (one coupling constraint). On a continuous query distribution without
  atoms at ties, the λ*-rule is optimal and deterministic.
* Over **deterministic** policies, sweeping λ reaches only the points on the
  upper concave envelope of the achievable `(E[L], E[U])` set. Points below
  the envelope (non-supported) can be optimal for some budget and are missed.
  So there can be a duality gap. In practice the gap is at most one query's
  worth on a finite test set, but it should not be denied.
* A **per-query** SLA `L̂(a|q,s) ≤ L_SLA` is not dualized. It is the
  feasibility filter `𝓕`, and λ is not its multiplier.

**Allowed sentence:** "For a fixed λ the rule maximizes the empirical
objective; λ can equivalently be interpreted as the Lagrange multiplier of an
average-latency budget." **Rejected:** "λ is the KKT multiplier of the SLA."

### 4.3 How λ is set `[PROPOSED]`

1. **Frontier (E5):** sweep λ on a log grid that includes 0 (always-best
   quality within `𝓕`) and a value large enough to give always-fastest.
2. **Operating point (headline tables):** pick λ on the **validation** split
   so that mean latency (or remote-call rate) meets a pre-stated budget; then
   freeze it for test. Report the budget, not just λ.
3. **Online adaptation (ablation, not core):** dual ascent
   `λ_{t+1} = [λ_t + η(L_t − L̄)]_+` keeps a running mean-latency budget under
   drift. Listed for E6 as an optional variant only.

Tie-breaking: when two actions have equal objective (always true for the
`SPLIT` depths of one model in Branch X before cost), prefer lower predicted
server compute, then lower bytes. This makes the depth choice deterministic
and reproducible.

### 4.4 Fallback

If `𝓕(q,s)` is empty (for example, a link outage makes every remote action
miss the SLA), run `EDGE` if it fits memory, and log an SLA miss. This is
stated as a policy choice, not a guarantee. `[PROPOSED]`

---

## 5. Metric hygiene: what enters the decision and what is reported

| Metric | Unit | In decision? | Reported as |
|---|---|---|---|
| End-to-end latency `L̂` | s | **yes** (λ·L̂, and SLA filter) | mean, p50/p95/p99 measured |
| TTFT, TPOT | s | via `L̂` | per action and per routing policy (manuscript L211–L218) |
| Activation / prompt bytes | bytes | only as `bytes/BW` inside `L̂` | per query and per action; prefill vs decode separated |
| Server GPU-seconds | s | no (yes only in C-2) | per query |
| Cost per request | USD | no | manuscript formulas L233–L262, never added to seconds |
| Edge energy | kWh | no | manuscript L250–L256 |
| Edge memory | GB | hard constraint `mem_edge(a) ≤ mem_avail(s)` | peak per action |
| Data policy | — | hard constraint | which actions were allowed in each experiment |
| Router overhead | s | no (constant across actions) | encoder latency p50/p95, added to every end-to-end number |
| Cold start | s | via `w_cold` in `L̂` | count and added latency (manuscript L221) |

---

## 6. Falsification and validation (handed to `13`)

| ID | Question | Design | Honest negative outcome |
|---|---|---|---|
| **E-COST** | Is `L̂` accurate enough to route on? | For each action and each emulated `(RTT, BW, load)` cell, compare predicted `L̂` with measured latency: MAPE, rank agreement of actions, and **decision regret** = utility loss of routing on `L̂` vs. routing on measured latency with the same `Û`. | High regret means the cost model, not the semantic router, limits the system; a learned `g_φ` for queueing/tails is then justified. |
| **E5** | Utility–latency trade-off | λ sweep; frontiers of quality vs mean, p95 latency; also quality vs bytes and vs USD from the same runs. Matched-latency and matched-quality comparisons with bootstrap CIs against baselines (`11`). | Router frontier inside a content-blind baseline's frontier. |
| **E6** | Network variation without retraining the semantic router | Fix θ and λ; vary RTT/BW (tc/netem) and server load; record decisions and outcomes. Include an **integrated state-input router** (`(q, s) → a`, trained on emulated states) as the fair challenger to the separated design (§7). | The integrated router matches or beats the separated design inside its training range; then the case for separation rests on reuse and out-of-range behaviour only, and must be worded that way. |
| **E7** | Real Split costs | Per depth: TTFT, TPOT, p50/95/99, prefill and decode bytes, GPU/CPU/memory, throughput. Explicitly test §2.3(a) (bytes vs `d`) and §2.3(b) (TPOT ≥ RTT; is `SPLIT` ever chosen when `REMOTE(M_S)` is allowed?). | `SPLIT` dominated in all tested states with no policy constraint; then report it and use C-2 or the policy constraint, rather than hiding it. |
| ablation | Output-length prediction | Replace per-model median `N̂_M` with a query-dependent predictor; measure regret change. | No gain; keep the median. |

Oracle-cost and oracle-utility controls separate the two error sources:
(i) true utility + predicted cost; (ii) predicted utility + measured cost;
(iii) both oracle. These isolate where the system loses value. `[PROPOSED]`

---

## 7. Issue C: the real justification for keeping `s` out of `Û_θ`

Brief §4 lists candidate arguments. Assessment, with the strength we can
defend:

| Argument | Strength | Why / caveat |
|---|---|---|
| Fresh measurements enter the decision directly | **Strong** | A change in RTT/BW changes `L̂` at the next query, exactly as far as the analytic latency model is right (E-COST). An integrated router responds only as well as it learned the dependence. |
| No synthetic network-state distribution in the semantic training data | **Strong** | Semantic labels are `(q, M) → S`; they do not depend on `s` in Branch X. An integrated router needs training tuples spanning the states it must handle, for example emulated regimes (as NetGPT-routing does, `06`). |
| One semantic router reused across deployments | **Strong** | A new site or link type needs re-profiling of the cost tables, not new semantic labels. |
| Independent updates | **Strong (engineering)** | Retrain θ without re-profiling; re-profile cost without touching θ. |
| Exact factorization under Branch X | **Strong (formal)** | `01` §1.4: depth is a pure cost decision, so putting `s` into θ would make the network learn something already known in closed form. |
| Interpretability and debugging | Moderate | Every routing decision decomposes into `Û`, `Δ̂` and `λL̂`; changes in decisions can be attributed. |
| Out-of-range network states | Moderate | The analytic `L̂` extrapolates by physics (bytes/BW + RTT); a learned model has no guarantee outside its training support, but may still generalize. Tested in E6, not asserted. |
| "Network change forces retraining" | **`[REJECT]`** | A router with `s` as input can generalize across states seen in training; ConsRoute re-tunes thresholds rather than retraining its encoder, and NetGPT-routing adapts a threshold analytically (`05` §1.5, `06`). |

**When the separation weakens.** If the split is lossy and the compression
level is chosen from bandwidth (adaptive compression), then quality depends on
`s`, and the depth correction becomes `Δ̂(a, q, s)`. The separation then holds
only for the semantic part `Û_θ(M|q)`; the correction term must take the
compression setting as input. This is a Branch L2 extension in `02`. `[OPEN]`

**A valid point from v2 kept.** Regressing `U − λC` directly into θ (`08`
option E1) freezes λ and the cost weights inside the weights; changing the
trade-off then does require retraining. That is an argument about putting
**λ and the cost targets** into the learned target, not about giving the
network `s` as an input. The two must not be conflated.

**Allowed manuscript wording:**

> Network state enters the decision only through the measured cost term, so
> the router reacts to bandwidth and RTT changes without updating the
> semantic predictor. An integrated router could learn this dependence from
> data, but it would need training data spanning the network conditions it
> must handle; keeping the two separate lets one semantic predictor be reused
> across deployments and validated independently of the cost model.

**Rejected:** "Incorporating system state into the router would require
retraining whenever network conditions change." "Our router adapts to any
network condition."

---

## 8. Corrections to v2 and consequences

| v2 location | v2 statement | v3 status |
|---|---|---|
| `08` §5 | Online rule = SC1 (normalised weighted scalar) | `[REJECT]` for the online rule; replaced by C-1 (§0.3) |
| `08` §4 SC3 | "λ **is** the KKT multiplier" | Corrected (§4.2) |
| `08` §2 item 1 | Baking cost into θ forces relabelling and retraining | Kept **only** for regressing `U − λC`; rejected for `s`-as-input (§7) |
| `08` §2 item 5 | Separation is the "N3 novelty lane" | `[REJECT]` as a justification: separation is pre-empted by Bao et al. and NetGPT-routing (`06`) |
| `08` §1 | Split's "entire differentiation lives in C" | Holds only in Branch X (`02`) |
| `06` §2 row "depth-dependent measured activation bytes" | Novelty candidate | Weakened: for dense decoders, prefill bytes are depth-independent (§2.3(a)). Reword as "depth-dependent edge/server compute split and measured transfer cost" in `12`. |

| Deliverable | Consequence |
|---|---|
| `10-model-pool.md` | Decide whether `REMOTE(M_S)` exists alongside `SPLIT_d(M_S)`; if yes, the data-policy constraint or C-2 must be stated (§2.3(b)). |
| `11-baselines-v3.md` | Add: content-blind model choice + best split (`01`); Bao-style utility − α·ΔT; NetGPT-style network-adaptive threshold; integrated state-input router (E6 challenger); oracle-cost and oracle-utility controls. |
| `12-novelty-v3.md` | Drop "depth-dependent activation bytes" as stated; the cost-side contribution is the measured, depth-aware latency model inside a multi-action router, cited against Bao/NetGPT/Edgent. |
| `13-experiments-v3.md` | E-COST, E5, E6, E7 as in §6. |
| `14-henry-checklist.md` | Ask: what tensor crosses the cut (shape, dtype, extras), whether compression differs by depth, where sampling happens and whether each decode step is a round trip, serialization overhead, transport, server queueing and batching, tc/netem access, and whether raw prompts may be sent to the server at all. |
| `proposed-solution-blue-v3.tex` | Use (C-1) with the §4.2 sentence; cite the manuscript's own latency definitions; no "first", no "adapts to any network". |

---

## 9. Open items

* All profiled latencies, the queue model, and the split message pattern:
  Henry's code and hardware (`14`). `[OPEN]`
* Whether `REMOTE(M_S)` is in the pool and whether raw prompts may leave the
  edge: advisor and pool decision (`10`). `[OPEN]`
* The values of `L_SLA`, the mean-latency budget, and the λ grid: set after
  profiling, before test data are touched. `[OPEN]`
* Whether a learned queue/tail predictor `g_φ` is needed: decided by E-COST
  regret, not assumed. `[OPEN]`
