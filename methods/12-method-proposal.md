# 12 — Method Proposal (advisor meeting document)

*This is the main document for next week's advisor meeting. It is a **planning
proposal**, not an approved method and not a set of results. Nothing here has been
implemented, trained, or measured. It synthesises deliverables 00–11, 14, 15 and
does **not** make the advisor's decision — §10 lists exactly what the advisor must
decide. Per the brief §16/§17 no single method is declared the winner.*

`source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`, re-verified
this iteration). `paper/main-revised.tex` is unchanged.

Evidence tags: **[S: …]** sourced in a cited deliverable · **[O]** our analysis ·
**[P]** our design proposal · **[E]** untested expectation.

---

## 1. Fixed research objective (not up for change)

For an input query `q`, a lightweight router at the edge must choose which model /
execution path in the pool `M = {M_1,…,M_K}` processes `q`, via a routing function
`R : Q → M` that maximises expected utility minus a weighted system cost:

```
max_R   E_q [ U(R(q), q) − λ · C(R(q), q) ]
R(q) = argmax_{M_k ∈ M}  f_θ(q, M_k)
```

`U` = expected response quality; `C` = system cost (compute, communication,
latency, memory, operational cost); `λ` = the utility/cost trade-off weight. This
is fixed by the manuscript [S: 00-scope-lock]. The advisor has stated the research
direction may **not** change; only the *method* (what `f_θ` is and how it is built)
is open.

Every candidate below maps explicitly to these two equations. The four fixed
requirements from the paper — **lightweight, query understanding, system
awareness, adaptability** — are carried as evaluation criteria, and "adaptability"
is treated as a claim to be tested per candidate, not assumed [S: 00, 03 row 12].

## 2. What is currently missing

The manuscript's *Proposed Solution* section is empty: it says `f_θ` is a
"lightweight TLM-based scoring mechanism" but never defines it. The whole gap is:

**What is `f_θ`, how is it trained, how does system cost `C` enter the decision,
and how is it evaluated so the result is a networked-systems contribution rather
than a classification score?** [S: 00, 02]

A second gap: the title says **"Jacobi-Forced Micro-Encoder,"** but no method by
that name exists in the literature, and a literal reading is incoherent (Jacobi
Forcing accelerates *causal autoregressive generation*; a micro-encoder does not
autoregress) [S: 04-jacobi-role]. The only technically defensible placement of
"Jacobi" is on the **edge generator**, not the router. This must be resolved with
the advisor (§10, and `04`/`11`).

## 3. Candidate Approach A — Tiny generative LM router (fidelity anchor)

**Idea.** Prompt a sub-2B causal LM with the query (± textual model/route
descriptions) and have it **generate** the routing decision as text [S: 02 §1].

- **`f_θ`:** label-token probabilities give `p(action | q)`, thresholded/argmax'd
  → the binary-sufficiency or utility-then-cost form of the objective [S: 02 §7].
- **Cost/state:** enter *outside* the LM via the cost table (S2), so `λ` and live
  network state stay run-time knobs [S: 07 §S2].
- **Pros:** literal "Tiny Language Model" of the title; released baseline exists
  (Arch-Router-1.5B) [S: 03 row 17]. **Cons:** heaviest on the edge (0.5–1.5B
  resident), slowest (prefill + ≥1 decode), calibration ill-defined for
  multi-token labels; one published head-to-head has it *slower and less accurate*
  than a hidden-state probe [S: 03 §2.1].
- **Honest role:** baseline / fidelity anchor, and the subject of hypothesis H2 —
  not the presumptive headline method.

## 4. Candidate Approach B — Lightweight discriminative micro-encoder (conservative)

**Idea.** A small bidirectional encoder (~20–150M) + scoring head maps `q` to
per-action utilities `Û(a|q)` in **one forward pass** — the plain reading of
"micro-encoder" [S: 02 §2].

- **`f_θ`:** `argmax_a Û(a|q) − λ·C(a|s)` with `C` measured outside the net (S2)
  [S: 02 §7, 07 §S2].
- **Pros:** lowest implementation risk and highest reproducibility (RouteLLM /
  RouterDC code released); single pass; standard temperature-scaling calibration;
  trains on one GPU or CPU [S: 03 §3]. **Cons:** needs a *second* model resident on
  the edge, sees only query text, and is **not novel on its own** [S: 03 §3].
- **Honest role:** the safe floor every other candidate must beat; supplies the
  cheap side of the B-vs-C head-to-head.

## 5. Candidate Approach C — Self-routing edge SLM via hidden-state probe (+ D as a policy layer)

**Idea.** The edge SLM routes for itself: a tiny probe reads its **prefill hidden
state** (C-pre; near-free if the query stays local) or its first-`k`-token
confidence (C-post) to estimate whether the local SLM will succeed [S: 02 §3].

- **`f_θ`:** `p̂(edge suffices | q)` thresholded at `τ(λ)`, or utility-then-cost
  [S: 02 §7]. **Pros:** reuses computation already done, lowest latency when the
  query stays local, structural link to the Split path (probe on split-head
  activations) [S: 03 §2]. **Cons:** wastes prefill on escalated queries and the
  probe must be **retrained whenever the edge SLM changes** [S: 03 §2, row 12].
- **Policy layer D (higher-risk, higher-payoff).** On a B- or C-backbone, add
  typed heads (route / edge-ok / sensitivity / expected-length). D is the only
  candidate that gives the **Split path a query-content reason to exist** (privacy →
  split-depth → activation-transfer bytes), which is a genuine networked-systems
  trade-off [S: 03 §3]. Risk: PRISM (AAAI 2026) already does privacy-aware 3-way
  routing, so D is a contribution only if its "collaborative" path is a *real
  layer-split path with measured leakage* (novelty axis N1) [S: 03 §2].

## 6. Comparison (no winner — three discussion categories, brief §17)

Full 20-criterion matrix is in `03-method-comparison.md`. The key reading:
**no candidate is a contribution on its architecture alone** — encoders, prefill
probes, small generative routers, and multi-head capability heads all already
exist [S: 03 §1]. Novelty, if any, comes from **what the router decides** (N1: a
genuine Split-LLM action with measured activation-transfer + leakage) and **how it
is evaluated** (N2: calibration under domain shift on edge hardware).

| Category (brief §17) | Candidate | Why |
|---|---|---|
| Strongest **conservative** | **B** micro-encoder | Lowest risk, released code, CPU-trainable; but not novel alone [S: 03 §3] |
| Strongest **higher-risk** | **D on a C backbone (N1)** | Privacy→split-depth→bytes is a systems trade-off with SIGCOMM payoff; PRISM overlap + sensitivity-label dependency are the risks [S: 03 §3] |
| Closest to **title / TLM** | **A** generative Tiny-LM (A-J noted) | Literal "Tiny Language Model"; but slower/less accurate than a probe in the one published test [S: 03 §3] |

C-pre sits between them (cheaper than A, richer than B, the only one structurally
linked to Split). **The decision the advisor really faces is which novelty axis
(N1 vs N2) to pursue; the architecture follows from that choice** [S: 03 §3].

## 7. Proposed minimum experiment to choose between them

Do **not** run during this sprint. Detailed plan in `08-experiment-design.md`;
staged so cheap results can kill expensive work early:

- **Stage 0 (CPU, ~zero inference):** reuse released LLMRouterBench per-query
  scores. Tests **H1** (does a learned router beat simple baselines — Always-Edge,
  Random, TF-IDF+LR, oracle upper bound?) and **H2** (does generative A beat a
  cheaper encoder/probe enough to justify its cost?). If Stage 0 falsifies H1 or
  H2, we stop before any GPU spend [S: 08 §0].
- **Stage 1 (bounded GPU):** rebuild labels for the manuscript's *actual* pool
  (the released bundle does not contain it) [S: 08 §2].
- **Stage 2 (edge↔server testbed with a real Split-LLM):** tests **H3** (is the
  Split action reducible to a fixed systems rule, or does query-aware routing add
  value beyond it?) and produces every networking claim (TTFT/TPOT/bytes/p95/p99,
  route-mix vs bandwidth/RTT sweep) [S: 08 §6.2, 15]. This is the stage that makes
  the work SIGCOMM-shaped rather than an ML result.

Protocol: 5 seeds, in-domain + domain-shift (OOD) splits, leakage-controlled
splits, paired significance tests, and explicit falsification bars decided before
running [S: 08 §8, §11].

## 8. Hardware / lab requirements (summary; full tiers in `10`)

- **Stage 0** runs on **CPU / a laptop** — no lab needed.
- **Stage 1** needs **one GPU** for label generation on the real pool.
- **Stage 2** needs **two machines + a controllable network** (Linux tc/netem),
  a real Split-LLM serving stack, and telemetry for TTFT/TPOT/bytes/GPU-util/power.
- The manuscript fixes the **edge node** (Xeon W-2123, 64 GB, 2×RTX 3090 24 GB,
  Ubuntu 20.04.6) but its **cloud-server sentence is literally truncated**
  ("…equipped with …") — the cloud spec is a genuine manuscript gap, and there is
  **no named Split-LLM framework** [S: 10, notes it7]. These two gaps gate all of
  Stage 2 and are ★blockers in `11`.

## 9. SIGCOMM relevance (full analysis in `14`)

VERIFIED: SIGCOMM 2027 is confirmed for **Aug 8–12, 2027, Bangkok**; its detailed
CFP is **not yet published (TBA)**, so orientation is taken only from the VERIFIED
SIGCOMM 2026 CFP (Research + Experience tracks, ≤12 pp two-column, double-blind,
voluntary-but-encouraged artifact evaluation, required `.bbl` to prevent
hallucinated citations) [S: 14 §1, §3]. We do **not** invent 2027 dates, page
limits, or requirements.

The single row that separates this from an ML classifier: **the route mix must
provably move as bandwidth/RTT are swept**, and this is only winnable by the S2
cost-integration design (utility learned, cost measured at run time) [S: 14, 15
claim C4; 07 §S2]. Required networking baselines (lowest-latency, bandwidth/RTT
threshold, cost-minimising, systems-only scheduler) are in `08 §5` / `14`.

## 10. Decisions needed from the advisor (this is what the meeting is for)

Prioritised; the four ★ are blockers that gate downstream work [S: 11].

1. ★ **Novelty axis:** N1 (genuine Split-LLM action, measured leakage/bytes) vs
   N2 (calibration under domain shift on edge hardware)? Architecture follows.
2. ★ **Jacobi's intended role:** router-side (A-J, ~zero benefit on a 1-token
   decision) vs edge-generator (E-J, defensible but requires JF-post-training a
   sub-2B SLM ourselves — public checkpoints are 7B) vs drop the phrase? [S: 04]
3. ★ **Cloud-server hardware spec** (manuscript sentence is truncated) and
   ★ **which Split-LLM framework** the lab supports.
4. **Model pool:** which real edge SLMs and strong/Split-LLM? The manuscript names
   no concrete pool; several referenced model names could not be verified [S: 11].
5. **Is the Split-LLM action in scope** for the router (needed before any D/N1
   work), and does Mix-or-Split (unread) pre-empt it? [S: 03 §3]
6. **Target/label formulation** to discuss: binary vs utility-regression vs
   pairwise vs separated U/measured-C — all derive from one labelling campaign, so
   the choice is cheap to defer but should be aligned [S: 06].
7. **λ and success bars:** what quality floor and cost/latency targets define
   success for the paper's headline claim? [S: 08 §11]

**We are not asking the advisor to rubber-stamp a method. We are asking which
novelty axis to commit to; every candidate above is ready to instantiate once that
and the Split/hardware blockers are resolved.**
