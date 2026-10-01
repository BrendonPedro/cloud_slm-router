# 10 — Model Pool and Baselines

*Deliverable for `MICROENCODER_KD_BRIEF.md` §13 (model-pool design) and §14
(baselines). This is a **verification + criteria + baseline-plan** document, not
a declaration of the final pool. Per the brief, the exact final pool is an
advisor decision and must NOT be invented (`[OPEN]`); this file inspects the
manuscript's named pool, verifies every model against primary sources, flags
stale/invalid names, and proposes model-SELECTION CRITERIA rather than a
decision. Evidence tags per brief §23: `[VERIFIED]` primary source directly
checked; `[RELATED]` adjacent / previously checked, re-verify in `17`;
`[PROPOSED]` our design; `[OPEN]` needs advisor/Henry/experiment;
`[UNSUPPORTED]` must not be used. The original manuscript is unmodified.*

> **Scope-lock.** The model pool `𝓜 = {M_1,…,M_K}` populates the fixed action set
> `𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD}` (`06 §2`); it does not change the
> objective `max_R E_q[U − λC]` or `R(q)=argmax_{M_k} f_θ(q,M_k)`. Baselines are
> alternative implementations of `f_θ` (or of the whole decision rule) against
> which the distilled micro-encoder is compared — the proposed method is the
> distilled micro-encoder, and Candidate C hidden-state self-routing is now a
> **baseline**, per advisor decision `00 §CONFIRMED-6`. `[S:00]`

---

## 1. Why this deliverable is verification-first, not design-first

The brief (§13) states the model-pool question "was largely answered during the
presentation, but the student's handwritten notes are incomplete," and lists
`exact edge SLM / strong model pool` as an explicit **do-not-guess** `[OPEN]`
item (`00 §UNRESOLVED`). The correct move is therefore:

1. inspect the pool the manuscript already names (`source/main-original.tex`
   §VI "Weak Models / SLMs" and "Strong Models");
2. verify every named model exists with its stated size and official ID;
3. flag stale/invalid names as fixes, not as new choices;
4. propose **selection criteria** the advisor can apply, and surface the
   routing-complexity question (too many SLMs);

without claiming a final pool. All model-existence facts below were primary-source
checked in the v1 claim-audit (`research/claim-audit.md` E11–E19, tag `[api]` =
Hugging Face API/model card inspected) and are re-tagged here for deliverable
`17` primary re-verification. `[S:research/claim-audit.md]`

---

## 2. Manuscript pool as written (the object to verify)

`source/main-original.tex` names the following (§VI, L267–300):

**Weak models / SLMs (edge):**

| # | Name as written | Stated size | L |
|---|---|---|---|
| W1 | Gemma-4-E2B-A4B | "2B-parameter" | 273 |
| W2 | Gemma-4-E4B-A4B | "4B-parameter" | 275 |
| W3 | Gemma-4-12B-A4B | larger SLM | 277 |
| W4 | Phi-4-mini-3.8B | 3.8B | 280 |
| W5 | Meta-Llama-3.1-8B-Instruct | 8B | 282 |
| W6 | LLaDA-MoE-7B-A1B-Instruct-Q4 | 7B-A1B diffusion MoE | 286 |
| W7 | Dream-v0-Instruct-7B | 7B diffusion | 288 |
| W8 | Fast-dLLM-v2-7B | 7B block-diffusion | 290 |

**Strong models (Split-LLM / cloud):**

| # | Name as written | Stated size | L |
|---|---|---|---|
| S1 | Qwen3-72B-Instruct | 72B | 298 |
| S2 | Llama-3.3-70B-Instruct | 70B | 300 |

All models "deployed using 4-bit quantization" (L295, L268). `[S:source/main-original.tex]`

---

## 3. Verification — which names are valid, stale, or invalid

Primary-source status from `research/claim-audit.md` (E11–E19, `[api]`). Re-tag
`[RELATED]` here because the HF cards were inspected in the v1 run, not re-opened
this iteration; deliverable `17` re-verifies before any are cited.

| # | Name as written | Verdict | Correct official ID / fact | Action |
|---|---|---|---|---|
| W1 | Gemma-4-E2B-**A4B** | **INVALID suffix** `[RELATED]` | `google/gemma-4-E2B-it`; **no "-A4B" variant exists** for E2B/E4B/12B (only `gemma-4-26B-A4B-it` carries A4B). "E"=*effective*; E2B stores **5.12B** params, not 2B | drop "-A4B"; correct param claim |
| W2 | Gemma-4-E4B-**A4B** | **INVALID suffix** `[RELATED]` | `google/gemma-4-E4B-it` | drop "-A4B" |
| W3 | Gemma-4-12B-**A4B** | **INVALID suffix** `[RELATED]` | `google/gemma-4-12B-it` | drop "-A4B" |
| W4 | Phi-4-mini-3.8B | **VALID** `[RELATED]` | `microsoft/Phi-4-mini-instruct`, 3,836,021,760 params, MIT licence; cite arXiv 2503.01743 | add citation |
| W5 | Meta-Llama-3.1-8B-Instruct | **VALID (gated)** | exists, Llama-3.1 community licence; at 8B it is the upper edge of "SLM" | keep; note gating |
| W6 | LLaDA-MoE-7B-A1B-Instruct-**Q4** | **VALID model, Q4 ambiguous** `[RELATED]` | `inclusionAI/LLaDA-MoE-7B-A1B-Instruct` exists in BF16 (Apache-2.0); a **Q4 build exists only as community GGUF** | name the exact quantised artefact `[OPEN]` |
| W7 | Dream-v0-Instruct-7B | **VALID, attribution wrong** `[RELATED]` | `Dream-org/Dream-v0-Instruct-7B` (Apache-2.0); README links **HKU NLP** blog, not solely Huawei Noah's Ark; "top-tier" uncited | fix attribution; drop "top-tier" |
| W8 | Fast-dLLM-v2-7B | **VALID** `[RELATED]` | adapts `Qwen2.5-7B-Instruct`; Jacobi-Forcing paper Table 6 reports 63.4% HumanEval vs 87.8% AR | add citation |
| S1 | **Qwen3-72B-Instruct** | **INVALID — does not exist** `[RELATED]` | **No official Qwen3-72B checkpoint.** Qwen 72B models are Qwen/Qwen2/Qwen2.5 only. HF "Qwen3-72B" hits are community merges | pick a real model (Qwen2.5-72B-Instruct, Qwen3-32B, or Qwen3-235B-A22B) — **advisor decision `[OPEN]`** |
| S2 | Llama-3.3-70B-Instruct | **VALID (gated)** | exists, gated with manual approval; "latest" is date-sensitive | drop "latest"; note gating |

**Summary of fixes required before the pool is usable:**

- **2 invalid names** must be corrected or replaced: `S1 Qwen3-72B` (no such
  model — real substitute is an advisor decision) and the **"-A4B" suffix** on
  all three Gemma-4 entries (W1–W3).
- **1 param misstatement**: Gemma-4-E2B is 5.12B stored / ~2B "effective", not
  "2B-parameter".
- **2 artefact ambiguities** (`[OPEN]`): the exact LLaDA-MoE Q4 build (W6) and
  whether 4-bit diffusion LMs run correctly at all.
- **1 attribution fix** (W7 Dream).

None of these are new pool *choices* — they are corrections to names the
manuscript already committed to. The `S1` substitute is the only genuine
advisor decision, and it is flagged `[OPEN]`, not guessed. `[S:research/claim-audit.md E11–E19]`

---

## 4. The decisive constraint the pool must satisfy: SimpleQA label availability

A pool-level fact overrides all of §3 and is the single most important input to
pool design:

> **The manuscript's evaluation claim is broken as written.** It says it evaluates
> "on the SimpleQA dataset **with pre-computed inference results in
> LLMRouterBench**" (L205). But SimpleQA appears in LLMRouterBench **only** in its
> performance-cost setting, whose 13–15 models are **flagship API models**. **None
> of the manuscript's weak or strong models has SimpleQA records** in the bundle;
> of the whole pool, only Llama-3.1-8B appears at all, and not on SimpleQA.
> `[VERIFIED: research/claim-audit.md E2, research/raw/experiment/inventory_output.txt L680–700]`

**Consequence for pool design.** The pool and the label source are coupled. Two
mutually exclusive routes, both of which are advisor decisions `[OPEN]`:

- **Route P-A (use the manuscript's own pool):** quality labels `y(a,q)` must be
  generated by **our own inference runs** on these models (cannot be lifted from
  LLMRouterBench). This is the labelling campaign scoped in `07 §4` (≈N·K
  generations, GPU, and the 4-bit-quantization quality effect of `E17` must be
  measured). This keeps the manuscript's diffusion-SLM / Split story intact.
- **Route P-B (use LLMRouterBench's released pool):** adopt the 13–15 flagship
  models that *do* have SimpleQA records, so labels are free — but these are API
  models, not edge-deployable 4-bit SLMs, which **breaks the edge/Split story**
  (`00` fixed requirements 5–6) and the N4 Split novelty lane.

These cannot be silently merged. The method's edge/Split identity requires
**Route P-A**; `07`'s label chain already assumes it. This must be put to the
advisor explicitly (→ `16`). `[PROPOSED][OPEN]`

---

## 5. Model-SELECTION CRITERIA (proposed, not a decision)

Per brief §13, propose criteria the advisor applies — do not invent the pool.
`[PROPOSED]`

| ID | Criterion | Why it matters to *this* method |
|---|---|---|
| MP1 | **Meaningful capability gap** edge↔strong | If edge ≈ strong on the data, `Û_θ` is flat and routing has nothing to predict — H1 (`08`) is unfalsifiable. Need a measurable per-query win rate spread. |
| MP2 | **Oracle headroom** (per-query-max ≫ always-edge AND ≫ always-strong) | The v1 analysis showed that if the oracle barely exceeds always-cloud, the routing problem is degenerate; conversely a pool where the oracle *raises* quality above every single model justifies a router. Pool must be chosen so `oracle − max(single model)` is non-trivial. `[S:methods/08 L93–97]` |
| MP3 | **Edge feasibility** of the weak side | SLMs must actually run 4-bit on the (unknown `[OPEN]`) edge GPU; this is why W1–W8 are ≤~8B. |
| MP4 | **Split compatibility** of the strong side | The strong model must be partitionable by Henry's Split-LLM runtime (layer-depth cut, `09 §2`); monolithic API-only models cannot be `SPLIT(d)`. |
| MP5 | **Open weights + licence permitting distillation & deployment** | Needed both to run inference for labels and because KD teachers must be openly licensed (`04`: the Jev/TypeSafe MCA §2.3(b) distillation prohibition is why we avoid prohibited teachers). |
| MP6 | **Reproducibility** (fixed official checkpoint, not a community merge) | Directly motivated by the `S1 Qwen3-72B` failure — the named model did not exist, so results would be irreproducible. |
| MP7 | **GPU memory fits the lab's two-machine setup** | e.g. Llama-3.3-70B @4bit ≈ 35 GB exceeds one 24 GB card, forcing a split or two GPUs (`E17`) — this interacts with the `[OPEN]` hardware. |
| MP8 | **Architectural diversity only if it buys a routing signal** | The manuscript's AR + diffusion-SLM mix (W6–W8) is defensible *only* if diffusion models have a distinct per-query win profile; otherwise it adds labelling cost without a routing signal. `[OPEN]` — must be checked, not assumed. |

---

## 6. Does the pool have too many SLMs? (brief §13 explicit question)

**Yes, probably — and it inflates the method without adding routing signal.**
`[PROPOSED]`

- The decoupled design (`06 §2`, `08 §3`) forces **all** Edge/Split/Strong
  differentiation into the **cost** term because `y(SPLIT(d),q)=y(full,q)`
  (`07 §3`). The *learned* utility only needs to separate the actions whose
  **quality** differs — i.e. essentially **edge-class vs strong-class**.
- With 8 weak + 2 strong = 10 models, the labelling campaign is ≈10·|Q|
  generations (Route P-A), the N utility heads grow to N≈10, and calibration
  must be maintained per head — all for a problem whose *quality* axis is
  largely binary (edge-sufficient vs needs-strong).
- **Recommendation `[PROPOSED]`:** for the **conference core**, collapse to a
  **minimal, defensible pool** — one representative edge SLM + one strong model
  partitionable by Henry's code + its `SPLIT(d)` depths — which is exactly the
  **A=N=2 first-milestone** already locked in `07 §2` (binary edge-sufficiency as
  the baseline target, per-action utility as the C-generalization). The full
  8+2 diffusion/AR zoo belongs in an **ablation / generalization** study (E8
  domain-shift, and a "does backbone/pool diversity matter" analysis), not the
  core claim. This keeps the routing problem well-posed (MP1/MP2) and the
  labelling tractable without inventing a final pool. The exact members remain
  `[OPEN]` for the advisor.

This recommendation is consistent with LLMRouterBench's warning that routers
often tie simple baselines (`01`, `02`) — a sprawling pool raises label cost but
not the chance of beating TF-IDF+LR; a pool chosen for **oracle headroom** (MP2)
is what makes the router beatable-beating. `[S:methods/08 L231]`

---

## 7. Baselines (brief §14) — the full plan and what each one answers

The proposed method is the **distilled micro-encoder** (`06`). Each baseline
isolates one competing explanation for any observed win, so that a win cannot be
attributed to a confound. Tags: `[PROPOSED]` plan; grounded in v1
`methods/08 §5`. The experiment IDs (E1–E8) are defined in deliverable `12`.

### 7.1 Trivial / non-learned baselines — "is routing even needed?"

| Baseline | What it is | Question it answers | Primary experiment |
|---|---|---|---|
| **Always-Edge** | route every query to EDGE_SLM | Lower bound on quality, upper bound on edge-cost savings; is any escalation ever needed? | E2 |
| **Always-Strong/Cloud** | route every query to STRONG | Quality ceiling of a single model; cost of never using the edge | E2 |
| **Always-Split(d)** | route every query to SPLIT at fixed depth `d` | Isolates the Split *cost* profile independent of routing (bytes/TTFT at fixed d) | E2, E7 |
| **Random@rate** | route to STRONG with prob. matched to the method's call rate | Controls for *how often* we escalate vs *which queries* — a win over random@rate means the router picks the *right* queries, not just the right frequency | E2 |
| **Dataset-prior** | route by dataset/domain ID majority label | The "no query understanding needed" null — if this ties the router, the contribution collapses (direct falsifier of H1) | E2, E8 |

### 7.2 Simple learned baselines — "does it beat the cheap classifier?"

| Baseline | What it is | Question it answers | Primary experiment |
|---|---|---|---|
| **TF-IDF (1–2-gram) + Logistic Regression** | classic sparse-feature classifier on the query text | **The bar.** LLMRouterBench found neural routers often *tie* this; the headline H1 success criterion is beating TF-IDF+LR by ≥5 pts (Holm-adjusted 95% CI excluding 0). If the micro-encoder cannot clear this, there is no encoder contribution. | E2 (gating) |
| **Standard (non-distilled) micro-encoder** | identical ModernBERT student trained on hard labels only (KD-5 **α=1** control) | **The KD ablation = E1.** The *entire* KD contribution (N1/N2) is the gap between this and the distilled student. If distillation does not beat its own α=1 control, brief stop-condition #4's reject-KD branch fires. | **E1** |
| **System-state-only scheduler (S4 baseline)** | ignores query content; routes on measured `C(a|s)` / lowest-estimated-latency only | Isolates the *query-understanding* contribution from the *cost-awareness* contribution — a win over this shows `Û_θ(a|q)` adds value beyond the cost term alone (defends N3 cost-separation) | E6, E7 |

### 7.3 Strong / published-router baselines — "does it beat the literature?"

| Baseline | What it is | Question it answers | Primary experiment |
|---|---|---|---|
| **Hidden-state probe / self-routing SLM (Candidate C)** | logistic probe on the weak model's own prefill hidden state (`C-pre`, needs 8B forward passes, GPU) | **Demoted from proposed method to baseline** (`00 §CONFIRMED-6`). Answers: does a *free* signal already inside the edge SLM's forward pass route as well as a dedicated micro-encoder? If yes, the separate encoder is unjustified. | E3 |
| **Published encoder router — RouteLLM** | re-trained on our labels/pool per the manuscript's adaptation note (L315) | Closest encoder-router prior art; does our target+KD beat the established pairwise router? | E2 |
| **Published generative router — Arch-Router-1.5B** | generative route-name model; **zero-shot and fine-tuned** (note: it has **no routing head** — it *generates* the route label, `E25` correction) | Generative-router comparison point; also a latency contrast (28× slower claim) for the lightweight-at-inference argument | E2, E4 |
| **Teacher (T1 larger encoder router)** | the KD teacher itself, evaluated directly | **E4.** Quantifies the student↔teacher gap in quality/calibration/params/latency — the KD value proposition is "student retains teacher quality at a fraction of the size/latency" | **E4** |

### 7.4 Upper bound — "how much routing headroom exists?"

| Baseline | What it is | Question it answers | Primary experiment |
|---|---|---|---|
| **Oracle** | per-query argmax over actual outcomes (the `y(a,q)` ground truth, `07`) | Upper bound on achievable routed quality; defines the gap the router is trying to close and validates MP2 (is there headroom at all?). **Not achievable at inference** — uses labels. | all |

**Note on fairness (carried from the manuscript, L306).** Published baselines are
re-trained/adapted on our labels, pool, and cost function; otherwise they are
*transfer* baselines, not like-for-like, and must be labelled as such. The
manuscript already commits to this adaptation; `E25` (Arch-Router has no routing
head) is the one correction to apply. `[S:source/main-original.tex L306–317; research/claim-audit.md E25]`

---

## 8. What each baseline *controls for* (one-line confound map)

- Always-Edge/Strong/Split → **is escalation ever worth it?**
- Random@rate → **right queries vs right frequency?**
- Dataset-prior → **is query understanding needed at all?** (H1 falsifier)
- TF-IDF+LR → **is a neural encoder needed over a sparse classifier?** (the bar)
- Non-distilled micro-encoder (α=1) → **does KD add anything?** (E1, the KD claim)
- System-state-only → **does learned utility add value over the cost term?** (N3)
- Hidden-state probe (Cand. C) → **is a *separate* encoder justified over a free internal signal?**
- RouteLLM / Arch-Router → **do we beat published routers?**
- Teacher (T1) → **does the student retain teacher quality cheaply?** (E4, the KD value prop)
- Oracle → **how much headroom is there?** (MP2 sanity)

---

## 9. Open items handed forward

| ID | Item | Owner | Tag |
|---|---|---|---|
| O10-1 | Real substitute for the non-existent `Qwen3-72B-Instruct` (Qwen2.5-72B / Qwen3-32B / Qwen3-235B-A22B) | advisor | `[OPEN]` → `16` |
| O10-2 | Route P-A (our own inference labels on manuscript pool) vs P-B (LLMRouterBench flagship pool) — they are mutually exclusive and P-B breaks the edge story | advisor | `[OPEN]` → `16` |
| O10-3 | Conference-core pool size: adopt the minimal N=2 pool and move the 8+2 zoo to ablation? | advisor | `[PROPOSED]` → `16` |
| O10-4 | Exact LLaDA-MoE Q4 artefact + whether 4-bit diffusion LMs run | Henry/experiment | `[OPEN]` → `09`, `12` |
| O10-5 | Whether diffusion vs AR SLMs have a distinct per-query win profile (MP8) — justifies or kills architectural diversity | experiment | `[OPEN]` → `12` E8 |
| O10-6 | 4-bit quantization effect on quality labels (`E17`) — published scores are BF16 | experiment | `[OPEN]` → `07`, `12` |
| O10-7 | Which strong model(s) Henry's Split-LLM runtime can actually partition (MP4) | Henry | `[OPEN]` → `09` |

---

## 10. Hand-offs

- **→ `11` (novelty):** the pool verification reinforces N3/N4 as the live lanes;
  a minimal well-posed pool (MP2 headroom) is what makes beating TF-IDF+LR
  (the `01`/`02` tie-warning) achievable.
- **→ `12` (experiments):** this file supplies the baseline roster for E1–E8 and
  the oracle-headroom sanity check; O10-5/O10-6 become experiments.
- **→ `16` (open questions):** O10-1/O10-2/O10-3 are the advisor-facing pool
  decisions; O10-7 is a Henry question.
- **→ `17` (references):** all `[RELATED]` HF-card facts (E11–E19) re-verified
  before citation; Phi-4-mini (2503.01743), Dream, Fast-dLLM citations added.

---

### Evidence ledger (this deliverable)

| Claim | Tag | Source |
|---|---|---|
| Qwen3-72B-Instruct does not exist (official) | `[RELATED]` | `research/claim-audit.md E18` (HF search `[api]`) — re-verify in `17` |
| Gemma-4 "-A4B" suffix invalid; E2B=5.12B stored | `[RELATED]` | `research/claim-audit.md E11` `[api]` |
| None of the pool has SimpleQA records in LLMRouterBench | `[VERIFIED]` | `research/claim-audit.md E2`; `research/raw/experiment/inventory_output.txt L680–700` |
| Oracle-headroom / degeneracy risk (MP2) | `[VERIFIED]` | `methods/08 L93–97` |
| Routers often tie TF-IDF+LR | `[VERIFIED]` | `01`, `02` (LLMRouterBench); `methods/08 L231` |
| Candidate C demoted to baseline | `[VERIFIED]` | `00 §CONFIRMED-6` |
| Arch-Router has no routing head (generates label) | `[RELATED]` | `research/claim-audit.md E25` `[api]` |
| Baseline roster / what each controls for | `[PROPOSED]` | this file, grounded in `methods/08 §5` |
| Minimal N=2 conference pool recommendation | `[PROPOSED]` | this file + `07 §2` |
| Final pool members | `[OPEN]` | advisor — not invented |
