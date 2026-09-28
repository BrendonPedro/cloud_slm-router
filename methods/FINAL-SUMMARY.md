# FINAL SUMMARY — Method-selection sprint for the Tiny-LM / Jacobi router paper

*Plain-English wrap-up of the whole methods brief (brief §23). This is a
**planning** synthesis of deliverables 00–16: no method is approved, no model was
trained, no experiment was run, and no result was invented. It does **not** make
the advisor's decision — it lays out the options and what must be asked. Read
`methods/12-method-proposal.md` for the meeting document and
`methods/13-presenter-notes.md` for the spoken version.*

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-verified
this iteration); `paper/main-revised.tex` is unchanged.

---

## 1. What problem are we still solving?

Unchanged from the manuscript. For an input query `q`, a **lightweight router at
the edge** must choose which model / execution path in a pool `M = {M_1,…,M_K}`
should answer it, so as to maximise answer quality minus a weighted system cost:

```
maximise  E_q [ U(R(q), q) − λ · C(R(q), q) ]        with   R(q) = argmax_k f_θ(q, M_k)
```

`U` = answer quality, `C` = system cost (compute, communication, latency, memory,
money), `λ` = the trade-off knob. The **only** thing the manuscript leaves open —
and the whole point of this sprint — is **what `f_θ` actually is and how it is
built, trained, and evaluated**. The *Proposed Solution* section is empty; it just
calls `f_θ` a "lightweight TLM-based scoring mechanism" [S: 00, 02].

## 2. What are the 3 strongest method options?

No option wins on architecture alone — encoders, prefill probes, and small
generative routers all already exist. So these are framed as the brief's three
*discussion categories*, not a ranking [S: 03 §1, brief §17]:

- **A — Tiny generative LM router** (closest to the title's "Tiny Language Model").
- **B — Lightweight discriminative micro-encoder** (the conservative, lowest-risk
  floor).
- **C — Self-routing edge SLM via a hidden-state probe**, optionally with **D**, a
  typed **utility/cost policy layer**, on top (the higher-risk, higher-payoff path
  that gives the Split-LLM action a real reason to exist).

## 3. How does each work?

- **A:** prompt a sub-2B causal LM with the query (± route descriptions) and let it
  **generate** the decision; use label-token probabilities as `f_θ` [S: 02 §1].
- **B:** a small bidirectional encoder (~20–150M) + scoring head maps `q` to
  per-action utilities `Û(a|q)` in **one forward pass**; decide
  `argmax_a Û(a|q) − λ·C(a|s)` with cost measured outside the net [S: 02 §2].
- **C:** the edge SLM routes for itself — a tiny probe reads its **prefill hidden
  state** (C-pre, near-free when the query stays local) or its first-`k`-token
  confidence (C-post) to estimate whether the local model will succeed [S: 02 §3].
- **D (policy layer on B or C):** typed heads (route / edge-ok / sensitivity /
  expected-length) that let the **Split path** trade privacy → split-depth →
  activation-transfer bytes — a genuine networked-systems trade-off [S: 02, 03 §3].

All four map explicitly to `R(q) = argmax f_θ` and `U − λC` [S: 02 §7].

## 4. What does each require?

- **A:** heaviest on the edge (0.5–1.5B resident), slowest (prefill + ≥1 decode
  step), calibration ill-defined for multi-token labels; a released baseline exists
  (Arch-Router-1.5B) [S: 03 §2.1, row 17].
- **B:** a *second* small model resident on the edge; sees only query text; trains
  on one GPU or even CPU; standard temperature-scaling calibration; released code
  (RouteLLM / RouterDC) [S: 03 §3].
- **C:** reuses computation already done (cheapest when local), but **wastes
  prefill on escalated queries** and the probe must be **retrained whenever the
  edge SLM changes** [S: 03 §2, row 12].
- **D/N1:** needs a **real layer-split path with measured leakage**, plus
  sensitivity labels; must clear the PRISM (AAAI 2026) privacy-routing prior work
  to be novel [S: 03 §2–3].

## 5. What are the most important differences?

- **Cost/latency on the edge:** C-pre (cheapest when local) < B < A (heaviest) [S: 03 §2].
- **What the router sees:** B = query text only; C = the SLM's own internal state;
  A = text, generatively [S: 02].
- **Calibration & adaptability:** B calibrates cleanly and swaps models easily; C
  is retrain-bound to its host SLM; A's multi-token calibration is unresolved
  [S: 03 rows 11–12].
- **The one difference that matters most:** *novelty comes from what the router
  decides and how it is evaluated, not from the architecture.* Two axes:
  **N1** = a genuine Split-LLM action with measured activation-transfer + leakage;
  **N2** = calibration under domain shift on real edge hardware [S: 03 §3].

## 6. What should be asked of the advisor before choosing?

The meeting's real purpose (full list in `11`/`12 §10`; ★ = blocker):

1. ★ **Which novelty axis — N1 (Split-LLM action) or N2 (calibration under
   shift)?** The architecture follows this one choice.
2. ★ **What is Jacobi's intended role?** — router-side (≈zero benefit on a
   1-token decision), edge-generator (defensible but needs JF-post-training a
   sub-2B SLM ourselves), or drop the title phrase [S: 04].
3. ★ **The cloud-server hardware spec** (the manuscript sentence is literally
   truncated: "…equipped with …") and ★ **which Split-LLM framework** the lab has.
4. **The concrete model pool** (no verifiable pool is named in the manuscript).
5. **Is the Split-LLM action in the router's scope**, and does Mix-or-Split
   pre-empt it? [S: 03 §3]
6. **Training target/label formulation** and **λ + success/falsification bars**
   [S: 06, 08 §11].

## 7. What hardware do we need?

Three tiers, per `10`:

- **Stage 0 (H1/H2 on released data):** a **CPU / laptop** — no lab.
- **Stage 1 (label the real pool):** **one GPU**.
- **Stage 2 (the SIGCOMM-shaped stage):** **two machines + a controllable network**
  (Linux `tc`/`netem`), a real Split-LLM serving stack, and telemetry for
  TTFT/TPOT/bytes/GPU-util/power. The manuscript fixes the edge node (Xeon W-2123,
  64 GB, 2×RTX 3090 24 GB, Ubuntu 20.04.6) but **not** the cloud server or the
  Split framework — the two ★ hardware blockers [S: 10, 12 §8].

## 8. What can be done before lab access?

Everything that feeds **Stage 0** on CPU, and none of it commits to a candidate
(full checklist in `16 §A`): finish the remaining primary-source reading
(Mix-or-Split, PRISM, Jacobi Forcing), inspect the LLMRouterBench release, build
the leakage-controlled + OOD splits, implement the label-construction functions for
all training targets, write the simple-baseline + oracle harness, stub the shared
`f_θ` interface and the run-time `C(a,s)` cost table, and pin a reproducible 5-seed
environment. This can already return a CPU read on **H1** (does a learned router
beat simple baselines?) and **H2** (is generative A worth its cost over a cheaper
probe?) [S: 08 §0, 16 §A].

## 9. What begins immediately after method approval?

The first 10 steps in `16 §C`: provision the confirmed edge + cloud machines, stand
up the two-machine `tc`/`netem` testbed, generate Stage-1 labels on the *real*
pool, rebuild splits, implement and train the approved `f_θ`, calibrate (incl. on
OOD), evaluate against all baselines, integrate the Split path with **measured
activation bytes + leakage**, then run the bandwidth/RTT sweep experiments that
test **H3** and produce the SIGCOMM claim curves [S: 09, 16 §C].

## 10. What evidence will ultimately be needed for the paper?

Not classification accuracy alone. The result must show a **networked-systems
effect** [S: 14, 15]:

- Lower **end-to-end latency / TTFT / tail (p95, p99)** at matched answer quality.
- Fewer **transmitted bytes** / lower **Split invocation** at matched quality.
- **The route mix provably shifts as bandwidth/RTT are swept** — the single claim
  (C4) that separates this from an ML classifier, winnable only by the S2 design
  (learn utility, measure cost at run time) [S: 07 §S2, 15 C4].
- **H3:** query-aware routing adds value **beyond a systems-only rule**, or it does
  not — stated as a falsifiable test, not an assumption.
- All with **5 seeds, in-domain + domain-shift splits, paired significance tests,
  and pre-registered falsification bars**, and a `.bbl`-clean bibliography [S: 08
  §8, 14 §1].

VERIFIED venue context: SIGCOMM 2027 is confirmed for **Aug 8–12, 2027, Bangkok**;
its detailed CFP is **not yet published** — orientation is taken only from the
SIGCOMM 2026 CFP, and no 2027 dates/limits/requirements are invented [S: 14 §1].

---

### The one sentence to remember

*The research question is fixed; the open question is which **novelty axis** to
commit to (Split-LLM action vs calibration-under-shift), and the router
architecture — A, B, or C+D — follows from that single decision, which is the
advisor's to make.*
