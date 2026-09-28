# 09 — Implementation Roadmaps

*Deliverable 09 of the METHOD_BRIEF sprint. A **plan**, not an execution log:
nothing here has been run except the stdlib-only Stage-0 pieces already recorded
in `experiments/prototype/`. Each roadmap gives concrete technical steps,
dependencies, file/module suggestions and verification checks — but the brief is
explicit (§9, §21): **do NOT execute them.** No large training run, no GPU
experiment, no invented result.*

Tags: **[M]** measured/released; **[S: …]** sourced from an earlier deliverable;
**[P]** our proposal; **[E]** untested expectation.

> **Scope-lock.** Every roadmap implements the same router
> `R(q)=argmax_a f_θ(q,a)` selected by `argmax_a Û(a|q) − λ·C(a,s)`
> (Eq. 1–3, `source/main-original.tex`, SHA `06f5f9d7…1707cf6`, unmodified). The
> phases differ only in backbone and label semantics, never in the research
> question [S: 00-scope-lock; 02-candidate-methods].

---

## 0. Which candidates get a roadmap, and why

From the comparison [S: 03-method-comparison; architecture/options.md §7]:

| Candidate | Status | Reason |
|---|---|---|
| **B — micro-encoder** | **viable (conservative)** | cheapest, most reproducible; the N2 comparison anchor |
| **C-pre — prefill-state probe** | **viable** | reuses edge compute; the only option with a structural link to the split path (via P2) |
| **D — structured multi-head utility** | **viable (higher-risk, N1)** | thin layer on B or C; the only option that represents privacy explicitly → gives SPLIT a learned reason |
| A — generative Tiny-LM | **baseline / fidelity anchor** | title concept; run as released (Arch-Router) + a 0.5B LoRA, but not a standalone contribution [S: 03; 02] |
| A-J / E-J (Jacobi) | **ablation only** | single-token decision ⇒ 1× speed-up; E-J is a generator change, not a router [S: 04-jacobi-role] |

So three roadmaps below (B, C-pre, D), plus a short shared **Phase A/B**
(data + labels) they reuse, and a note on running A as a baseline. The stop
condition needs ≥2 viable candidates with post-approval roadmaps; this gives 3.

The phases follow the brief §9 exactly: **A** data prep · **B** label generation ·
**C** router implementation · **D** training · **E** calibration · **F** offline
eval · **G** edge deployment · **H** Split-LLM integration · **I** network/system
experiments · **J** paper-results generation. Phases A/B/F/I/J are largely
**shared**; C/D/E/G/H are candidate-specific.

---

## Shared Phase A — Data preparation (all candidates)

Reuses the frozen artefacts from `experiments/prototype/` [S: 08-experiment-design §2/§13].

1. **Read the bundle, don't re-download.** Load LLMRouterBench release
   (sha256 `b79f8cde…48c8f1` [M]) from local cache; build the per-(model, query)
   score table over the Stage-0 primary pool (mmlupro/test_1000, gpqa/test,
   livecodebench/test, livemathbench/test, aime/hybrid = 2,432 unique queries [M]).
   - *Module:* `experiments/prototype/data/build_table.py` (already exists in
     stdlib form). *Verify:* row count == 2,432 after query-string dedup.
2. **Freeze splits** (60/20/20 in-domain, stratified by dataset × 4-cell outcome;
   4 leave-one-dataset-out OOD folds). Write `splits/{fold}.json` (query-hash →
   split) and hash them **before** any router touches data.
   - *Verify:* no query hash appears in two splits; hash matches a committed
     manifest [S: 08 §9].
3. **Stage-1 data (deferred to GPU):** the same datasets + SimpleQA to be re-run
   on the manuscript's real edge pool (2–4B + diffusion LMs) — this is the step
   that actually produces the paper's labels, because the manuscript's models are
   absent from the release [S: 08 §2, M].

*Depends on:* nothing beyond the local bundle for Stage 0; a ≥24 GB GPU for
Stage-1 re-runs.

## Shared Phase B — Label generation (all candidates)

One campaign → every target [S: 06-label-and-training-design].

1. Derive from the score table: binary `y=[score_weak ≥ score_strong]`; soft
   `Δ=score_strong−score_weak`; the 4-cell outcome. For D, additionally the
   per-model competence vector and a **sensitivity** label (open dependency — no
   dataset identified yet; synthetic/derived labels are the fallback
   [S: 02 §D; options.md §8 item 4]).
2. Freeze a **per-dataset scoring script** (exact-match / judge / unit-test pass)
   so Stage-1 labels are reproducible.
   - *Verify:* re-running the scorer on released generations reproduces the
     released scores bit-for-bit on a sample.
3. **Cost labels are NOT produced here** — real `C(a,s)` (activation bytes, TTFT,
   energy) is measured in Phase I only [S: 07-system-cost-integration; 08 §3].

---

## Roadmap 1 — Candidate B (micro-encoder) · difficulty LOW

### Phase C — router implementation
- Backbone: DeBERTa-v3-small (B-s) and ModernBERT-base (B-m, 149.7M [M]).
  Head options: B1 single logit `p̂(edge suffices|q)`; B2 K-way sigmoid
  `Û(M_k|q)`; B3 contrastive query-vs-model embeddings [S: 02 §B; options.md §2].
- *Module:* `routers/encoder/model.py` (backbone + head), `routers/encoder/featurize.py`
  (optional cheap metadata: length, language, detected PII flag [P]).
- *Verify:* forward pass on 8 dummy queries returns a K-vector in [0,1]; param
  count logged.

### Phase D — training
- Loss: BCE per model (B1/B2) or contrastive (B3). 5 seeds {0..4}. LoRA not
  needed (full fine-tune of a <150M encoder is cheap, CPU-feasible for B-s [E]).
- *Module:* `routers/encoder/train.py` reading frozen splits + labels.
- *Verify:* training loss decreases; dev metric logged per seed; no test-split
  file opened (assert on split manifest).

### Phase E — calibration
- Post-hoc **temperature scaling** on the dev split; report ECE(15) + Brier
  [S: 05-jev-and-decision-models; 08 §6.1].
- *Verify:* post-scaling ECE ≤ pre-scaling ECE on dev.

### Phase F — offline eval (shared harness)
- Metrics: CCR@−1, deferral AUC, APGR/CPT(50%), ECE, AURC; paired bootstrap +
  McNemar + Holm–Bonferroni; per-seed mean±std [S: 08 §6/§8].
- Baselines run alongside: always-edge/cloud, random@rate, TF-IDF+LR,
  dataset-prior, RouteLLM-BERT (transfer), oracle [S: 08 §5].
- *Verify:* success criteria of [S: 08 §11] evaluated; results written only by the
  stats script into `results/`.

### Phase G — edge deployment
- Quantise (int8/4) via ONNX or bitsandbytes; measure p50/p95 router latency on
  the **actual edge device** (advisor-defined; see [S: 10-lab-requirements]).
- *Verify:* quantised ECE within tolerance of fp; latency logged on target HW,
  not the dev host [S: options.md §8 item 6 — don't carry others' latency numbers].

### Phase H — Split-LLM integration
- Add `SPLIT(d)` as an action with its own utility entry + cost row. **Caveat:**
  a text-only encoder cannot exploit split computation; if SPLIT and CLOUD run the
  same weights, quality is equal and the choice collapses to a cost/leakage rule
  [S: 02 §B; options.md §2]. B therefore treats SPLIT as a cost-differentiated
  action, not a learned-quality one.
- *Verify:* route log shows SPLIT chosen only when its `Û−λC` dominates.

### Phase I — network/system experiments (shared, see below)
### Phase J — paper results (shared, see below)

**Adaptability note (brief §D, do not assume):** B1 needs relabelling when the
edge SLM changes; B2-with-profile / B3 can add a model by embedding a few labelled
probes without retraining the encoder [S: 02 §B; options.md §2]. The train-size
ablation (10/25/50/100%) quantifies the relabel budget [S: 08 §10].

---

## Roadmap 2 — Candidate C-pre (prefill-state probe) · difficulty MEDIUM

### Phase C — router implementation
- Extract the edge SLM's **prefill hidden state** (last-token, final or
  intermediate layer) via HF `output_hidden_states=True` or llama.cpp state
  access [S: 02 §C; options.md §3]. Small logistic/MLP probe head (10K–1M params).
- *Module:* `routers/probe/extract.py` (hidden-state dump), `routers/probe/head.py`.
- *Verify:* hidden-state shape == (hidden_dim); probe forward returns p̂∈[0,1];
  **which layer** is a logged hyperparameter (an ablation, not a constant).

### Phase D — training
- Labels = whether the edge SLM's own answer was acceptable [S: 02 §C]. BCE on the
  probe; the SLM stays frozen (probe-only training is cheap). 5 seeds.
- *Verify:* probe trains on cached hidden states without re-running the 8B model
  per epoch (cache the states in Phase A/B).

### Phase E — calibration
- Temperature scaling; optionally **per-cluster thresholds** τ(λ) (ConsRoute-style
  Bayesian-opt on query clusters) [S: 02 §C; options.md §3]. Report ECE/Brier/AURC.
- *Verify:* per-cluster τ improves AURC over a single global τ on dev, else keep global.

### Phase F — offline eval
- As shared harness. **Cost accounting subtlety:** C-pre is "free" only if the
  query stays local (prefill is reused for generation); if the query is offloaded,
  the prefill is wasted — this must appear in the measured `C` [S: 02 §C;
  options.md §3]. Log a "wasted-prefill" counter.
- *Verify:* wasted-prefill cost included in the `U−λC` score for offloaded queries.

### Phase G — edge deployment
- Needs hidden-state access inside the edge runtime (HF/llama.cpp expose it;
  closed runtimes may not [E]). Probe runs in-process with the SLM.
- *Verify:* end-to-end path (prefill → probe → route) on target HW; ConsRoute
  reports 20.9 ms probe latency on an RTX 3050 laptop [S: 03 §2.1] — **our number
  must be measured, not quoted**.

### Phase H — Split-LLM integration (C-pre's differentiator)
- **P2:** probe the **split head's early-layer activations** (the large model's
  first layers already run on the edge in a split) instead of the SLM's — decide
  `SPLIT(d)` using computation the split path needs anyway [S: 02 §C; options.md §3
  P2]. This is the structural split link no other candidate has.
- *Empirical precondition [E]:* that early large-model activations predict edge-SLM
  failure is **untested** (options.md §8 item 2) — Phase H must test it before any
  N1 claim.
- *Verify:* an ablation comparing probe-on-SLM vs probe-on-split-head activations
  on the same queries.

### Phase I / J — shared.

**Adaptability note:** the probe head must be retrained whenever the edge SLM
changes (labels are that SLM's capability) [S: 02 §C]. Adding cloud/split models
changes only the cost table if the head predicts edge-sufficiency only.

---

## Roadmap 3 — Candidate D (structured multi-head utility) · difficulty MEDIUM

D is a **thin layer on B's or C's backbone** — the backbone choice is itself an
ablation [S: 02 §D; options.md §4]. It is the higher-risk, N1-aligned option.

### Phase C — router implementation
- Backbone (B encoder **or** C prefill state) + several typed heads evaluated in
  one pass [S: 02 §D; options.md §4]:
  `route∈𝒜` (softmax incl. ABSTAIN); `edge_ok` (sigmoid); `sensitivity∈{none,PII,
  confidential}` (softmax); `expected_length` bucket (ordinal); optional `domain`.
  All heads return probabilities; **none generates text** (generation-free reading
  of Jev's parallel-questions interface; Jev outputs cannot be teacher labels —
  distillation forbidden [S: 05; 02 §D]).
- *Module:* `routers/structured/heads.py`, `routers/structured/policy.py` (the
  explicit combination rule).
- *Verify:* each head returns a valid probability vector; policy layer is pure
  code (no learned weights) so ρ, λ, allowed-action rules change without retraining.

### Phase D — training
- Sum of per-head losses (CE/BCE/ordinal). **Sensitivity head is the open data
  dependency** — needs a PII/privacy dataset or synthetic labels (not yet
  identified) [S: 02 §D; options.md §8 item 4]. 5 seeds.
- *Verify:* each head's dev metric logged separately; missing-sensitivity-label
  path degrades gracefully to B/C behaviour.

### Phase E — calibration
- **Per-head** temperature scaling; report ECE/Brier per head [S: 08 §6.1].
- *Verify:* every head individually calibrated on dev.

### Phase F — offline eval
- As shared harness, plus the **cost-placement ablation** S1/S2/S3/S4
  [S: 07-system-cost-integration; 08 §10 item 5]. D's default is **S2/S3** (learn
  `Û`, combine with measured `C(s)` outside the net) so λ and `s` stay run-time
  knobs — the property that makes the "react to changing network" SIGCOMM claim
  expressible [S: 07 §S2].
- *Verify:* sweeping λ at fixed θ reproduces the frontier without retraining.

### Phase G — edge deployment
- As B or C depending on backbone; extra heads are linear layers [E: negligible
  overhead, unmeasured].

### Phase H — Split-LLM integration (D's N1 rationale)
- The `sensitivity` head gives SPLIT a **query-content-dependent reason to exist**:
  the action for queries too hard for the edge but too sensitive for full cloud —
  precisely the N1 precondition "why must split-vs-cloud be *learned*?"
  [S: 02 §D; options.md §4]. **Risk:** PRISM (AAAI 2026) already does privacy-aware
  three-way routing, so D differs only if its collaborative path is a genuine
  layer-split with **measured** leakage [S: options.md §4; 01-method-landscape].
- *Verify:* a leakage measurement (embedding-inversion attack success vs split
  depth d) exists **before** claiming SPLIT protects sensitive queries — assumption,
  not fact [S: 08 §6.2; options.md §8 item 3].

### Phase I / J — shared.

---

## Shared Phase I — Network / system experiments (SIGCOMM core, all candidates)

This is the stage that makes the work a networked-systems result, not a classifier
[S: 08 §0/§7; 14-sigcomm-fit TBD].

1. **Testbed:** edge node ↔ controllable link (Linux `tc`/`netem`) ↔ cloud/split
   server [S: 10-lab-requirements TBD]. Start emulated on one machine; move to two
   physical machines for real RTT/bandwidth.
2. **Measure `C(a,s)`:** activation bytes per split depth d, edge↔server link
   bytes, TTFT, TPOT, e2e p50/p95/p99, throughput (req/s, tok/s), GPU/CPU util,
   memory, energy via `nvidia-smi` if available [S: 08 §6.2; 07 §cost-object].
3. **Sweep `s`** (bandwidth low/med/high × RTT low/med/high × optional contention)
   **at fixed θ** to produce latency/byte/cost curves and route-distribution
   shifts — the "adapts to changing network" claim [S: 08 §7].
4. **System baselines:** lowest-latency-path, bandwidth-threshold, RTT-threshold,
   cost-minimizing, and the **system-only scheduler** (S4) that ignores query
   content — H3 is "learned router > best system-only rule" [S: 07 §S4; 08 §5].
- *Verify:* each claim in [S: 08 §7] recorded as IV→DV with its falsifier; no claim
  asserted true before the run.

## Shared Phase J — Paper-results generation (all candidates)

1. Assemble tables/figures **only** from `results/` (script-produced); anything
   else stays tagged **[E]** [S: 08 §13].
2. Map every reported number to a hypothesis (H1/H2/H3) and its success criterion
   [S: 08 §11].
3. **Do not write results into `source/main-original.tex` or
   `paper/main-revised.tex`** — the sprint forbids modifying the manuscript
   (brief §Purpose, §21). Results land in `experiments/` and a results appendix
   only after the advisor approves a method.
- *Verify:* SHA of both manuscripts unchanged at end of every phase.

---

## Cross-candidate dependency & sequencing summary

```
Phase A (data) ─┬─> Phase B (labels) ─┬─> B: C→D→E→F ─┐
   [CPU/GPU]     │      [CPU/GPU]      ├─> C-pre: C→D→E→F ─┼─> Phase G (edge, target HW)
                 │                     └─> D: C→D→E→F ─┘        │
                 │                                              v
                 └──────────────────────────────────> Phase H (Split-LLM) ─> Phase I (network) ─> Phase J (paper)
```

- **Cheapest first:** B on CPU (Stage 0) falsifies H1/H2 before any GPU spend
  [S: 08 §0]. C-pre and Stage-1 labels need a GPU. D reuses B/C, so it is nearly
  free to add once either exists.
- **Gating:** if Stage-0 falsifies H1, stop before Phase G. If it falsifies H2,
  drop A/A-J and re-scope toward N2 [S: 08 §11; 04-jacobi-role].
- **Advisor-blocked steps** (cannot start without decisions): real model pool
  (Phase A Stage-1), edge/cloud/split hardware (Phase G/H/I), sensitivity dataset
  (D Phase B/D) — see [S: 11-advisor-questions TBD; 16-next-week-action-plan TBD].

---

*Cross-refs: consumes candidates from `02-candidate-methods.md`, the comparison
from `03-method-comparison.md`, training targets from `06-`, cost integration from
`07-`, and the staged plan + metrics from `08-experiment-design.md`. Feeds
`10-lab-requirements.md`, `12-method-proposal.md`, and `16-next-week-action-plan.md`.
Original manuscript unmodified (source SHA `06f5f9d7…1707cf6`).*
