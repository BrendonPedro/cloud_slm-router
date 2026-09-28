# 15 — SIGCOMM Experiment Matrix

Scope: a concrete
**METHOD × QUERY TYPE × NETWORK CONDITION × EXECUTION PATH × METRICS** matrix
for the eventual Stage-2 evaluation (`08-experiment-design.md`). This is a
*plan*, not results. Nothing here is run in this sprint (brief §18). All cells
are UNRESOLVED-until-measured; the point is to enumerate the conditions so the
testbed and label pipeline are sized correctly.

Every row still evaluates the fixed objective: pick `R(q)=argmax_k f_θ(q,M_k)`
to maximize `U − λC`, and *measure* the resulting `U`/`C` as network quantities.

---

## 1. Factor definitions

### 1.1 METHOD (the router under test)
From `02-candidate-methods.md` / `03-method-comparison.md`:

| ID | Method | Role |
|---|---|---|
| B | Lightweight discriminative micro-encoder | conservative candidate |
| C-pre | Prefill/hidden-state probe (pre-answer) | higher-risk candidate |
| D | Multi-head utility/cost predictor (S2 policy layer) | can wrap B or C |
| A | Generative Tiny-LM router | fidelity anchor / baseline |
| A-J / E-J | Jacobi variants | **ablation only** (see `04`) |
| **Baselines** | Always-Edge, Always-Split, Random, prior, lowest-latency, BW-threshold, RTT-threshold, cost-min, **system-state-only**, Oracle | see `14` §6 |

The **system-state-only scheduler** and **Oracle** bound the useful range: a
learned method must sit above the former and below the latter.

### 1.2 QUERY TYPE (strata; see `08`/`11` for pool + data)
- **Difficulty:** easy vs hard (by oracle answerability on the weak model).
- **Length:** short vs long prompt (drives prefill compute + activation bytes).
- **Domain strata:** in-domain vs held-out domain (OOD / calibration-under-shift,
  the N2 axis).

### 1.3 NETWORK CONDITION (independent variable, tc/netem — `10`)
- **Bandwidth:** low / medium / high.
- **RTT:** low / medium / high.
- **Contention:** none vs injected cross-traffic (justified only for the tail-
  latency claim).
- (optional) **packet loss:** off/low — only if a claim needs it.

### 1.4 EXECUTION PATH (action space — must include a real split, `14` §5 R-ML-4)
- **Local SLM (EDGE):** answer on-device; no edge→server transfer.
- **Split-LLM (SPLIT):** prefill/partial compute on edge, activations sent to
  server at split depth `d`, completion on server.
- **Cloud/strong path:** only if the original architecture's model pool includes
  a full-strong remote model (advisor Q, `11`); otherwise omitted, not invented.

### 1.5 METRICS (dependent variables; from `08` §6 and `14` §7)
Quality: task quality / utility `U` (grader-scored), matched-quality operating
point. Routing: route distribution, route accuracy vs oracle, escalation rate.
Systems: TTFT, TPOT, e2e p50/p95/p99, **transmitted activation bytes**,
throughput (req/s, tok/s), GPU/CPU util, memory, energy (if available),
operational cost `C`.

---

## 2. Master matrix (condition → primary claim → metrics)

Each block is one **headline claim** with its IV/DV/baseline/falsifier
(consistent with `08` §7). Rows are the conditions swept; every METHOD above is
run in every row (that is the METHOD dimension), but the *claim* is stated
against the named baseline.

### Claim C1 — Lower e2e latency at matched quality
| QUERY | NETWORK | PATHS compared | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| all strata | BW×RTT grid (3×3) | EDGE vs SPLIT chosen per query | e2e p50/p95 at matched `U` | best system-only rule | latency ≥ baseline at matched `U` |

### Claim C2 — Fewer transmitted bytes at matched quality
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| short vs long | fixed mid BW/RTT | EDGE vs SPLIT@d | activation+link bytes/query | Always-Split@d | bytes ≥ Always-Edge-then-escalate |

### Claim C3 — Lower Split/cloud invocation rate at matched quality
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| easy vs hard | fixed | EDGE vs SPLIT | SPLIT invocation % at matched `U` | Always-Split / threshold | invocation % ≥ baseline |

### Claim C4 — Adapts to changing bandwidth/RTT (the SIGCOMM-defining claim)
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| all | **sweep** BW low→high, RTT low→high (θ fixed) | route mix shifts EDGE↔SPLIT | route distribution + e2e latency **as a function of `s`** | fixed-threshold policy | route distribution invariant to `s` (router ignores the network) |

> C4 is the row only the **S2** design (`07`) can win: `λ` and measured `C(s)`
> are run-time inputs, so route mix *should* move with the network. If it does
> not, the ML router adds nothing over a static threshold.

### Claim C5 — Better tail latency under contention
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| all | injected contention on/off | EDGE vs SPLIT | e2e **p99** | system-only scheduler | p99 not improved |

### Claim C6 — Query-awareness beats a systems-only rule (H3)
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| in-domain + OOD | mid BW/RTT | full action space | quality-at-matched-cost **and** cost-at-matched-quality | **system-state-only scheduler** | learned router within CI of system-only |

### Claim C7 — Robust under domain shift / calibration (N2)
| QUERY | NETWORK | PATHS | Primary DV | Baseline | Falsifier |
|---|---|---|---|---|---|
| **held-out domain** | mid | full | ECE / selective-risk + regret vs oracle | in-domain-tuned threshold | OOD regret ≥ non-adaptive baseline |

## 3. Full cross-product size (for testbed/label sizing, not enumeration)

Cardinalities (to size Stage-2 runs; keep small, `08` staging gates spend):

- METHOD: ~4 learned (B, C-pre, D, A) + ~10 baselines = **~14**.
- QUERY strata: difficulty(2) × length(2) × domain(2) = **8** (analysis strata,
  not separate runs — one test set, sliced).
- NETWORK: BW(3) × RTT(3) = 9 grid points **+** contention(2) for C5 only.
- EXECUTION: EDGE, SPLIT@≥1 depth, (cloud if pool has it) = **2–3**.
- SEEDS: 5 (per `08` protocol) for the learned methods.

**Practical run budget:** do **not** run 14×8×9×3×5 (~150k configs). Instead:
1. **Core grid (C1/C4):** learned methods + key baselines over the 3×3 BW/RTT
   grid, 5 seeds → the network-adaptivity story.
2. **Point studies (C2/C3/C5/C6/C7):** one representative network point each,
   varying only the factor that claim needs.
3. Query strata are *slices of one test set*, not extra runs.

This keeps Stage-2 to O(hundreds) of testbed runs, feasible on the 2-machine
lab setup (`10`). Any coverage cut (e.g., single split depth, no packet-loss)
is **logged as a limitation** per brief §22 / `08` (no silent truncation).

## 4. Coverage check against the brief §15 metric list

| Brief-required measurement | Covered by |
|---|---|
| quality | all claims (matched-quality axis) |
| route selection | C1–C7 route distribution/accuracy |
| TTFT | C1, C4, C5 |
| TPOT | C1, C5 |
| p50/p95/p99 latency | C1 (p50/p95), C5 (p99) |
| throughput | C5 (load), server metrics |
| bytes transmitted | C2, C4 |
| compute | resource metrics (all) |
| memory | resource metrics; router overhead |
| cost | C3, C6 (operational `C`) |
| energy (if measurable) | resource metrics, advisor Q `11` |

## 5. What this matrix does NOT do

- It does **not** contain any measured values — every cell is UNRESOLVED until
  the Stage-2 testbed runs post-approval (`09` Phase I).
- It does **not** fix the model pool, split depth, `λ`, or graders — those are
  advisor decisions (`11`) and appear here as parameters, not constants.
- It does **not** assert any claim is true; each is stated with its falsifier so
  a negative result is a publishable systems finding, not a failure to hide.

---

### Mapping back to the fixed objective
Every row selects `R(q)=argmax_k f_θ(q,M_k)` and reports the realized
`U − λC` as *network-measured* quality vs latency/bytes/cost. The matrix's job
is to prove (or falsify) that this selection produces a **networked-systems**
effect — the requirement in `14-sigcomm-fit.md` — under conditions a networking
reviewer will demand. Sources for the SIGCOMM orientation are listed in
`14-sigcomm-fit.md` §11.
