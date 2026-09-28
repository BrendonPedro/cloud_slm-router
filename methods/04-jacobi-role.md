# methods/04 — The role of "Jacobi-Forced Micro-Encoder"

*Method-selection sprint, iteration 1. This deliverable answers METHOD_BRIEF §6
Family F and §19 file 04. It is a synthesis of two primary-source-checked prior
deliverables — `research/jacobi-forcing.md` (**[JF]**, which read arXiv:2512.14681
v1 HTML, the official GitHub repo, the HF model API and the ICML 2026 page) and
`research/micro-encoder-investigation.md` (**[ME]**, a bounded literature search).
Nothing here was re-run or reproduced this iteration. Where this document adds
analysis for method selection it is tagged **[O]** (our analysis) or **[P]**
(our proposal).*

Every statement below is filed under one of the four labels the METHOD_BRIEF
requires: **ESTABLISHED**, **PROPOSED**, **UNRESOLVED**, **UNSUPPORTED**.

---

## 1. Primary source of record

| Field | Value | Where verified |
|---|---|---|
| Title | *Fast and Accurate Causal Parallel Decoding using Jacobi Forcing* | arXiv:2512.14681 v1 [JF §1] |
| Authors | Hu, Kou, Fu, Rajbhandari, Rosing, He, Deng, Zhang | arXiv metadata [JF §1] |
| Venue | **ICML 2026 poster** (OpenReview `ORy2hyPd4G`) | icml.cc/virtual/2026 [JF §1] |
| Code | github.com/hao-ai-lab/JacobiForcing, Apache-2.0 | GitHub API [JF §1] |
| Checkpoints | `JacobiForcing_Coder_7B_v1`, `JacobiForcing_Math_7B_v1` (both 7B, no license field on HF) | HF API [JF §1] |

Lineage (all verified in [JF §1]): Song et al. 2021 (parallel nonlinear
equation solving) → Santilli et al. ACL 2023 (parallel decoding for MT) → Fu et
al. ICML 2024 (Lookahead) → Kou et al. ICML 2024 (CLLM, Jacobi Forcing's direct
predecessor) → Jacobi Forcing ICML 2026.

## 2. ESTABLISHED — what Jacobi Forcing is

1. **The problem.** Greedy autoregressive (AR) decoding needs one forward pass
   per token; at small batch it is memory-bandwidth-bound, leaving compute idle
   [JF §2].
2. **Jacobi decoding.** Rewrite greedy decoding of an *n*-token block as a
   nonlinear system and solve it by Jacobi fixed-point iteration; under a causal
   mask all *n* positions update in one forward pass, and the fixed point is
   provably identical to greedy AR output [JF §3]. Vanilla Jacobi barely helps
   (≈1 token converges per iteration; TPF 1.01–1.05, ~1× speedup) [JF §3].
3. **The training method.** Progressive consistency distillation on Jacobi
   trajectories: a noise-aware causal mask, a progressive noise schedule, loss
   `L = L_pc + w·L_AR`, two distillation rounds (block 16/window 16 → block
   32/window 8) [JF §4]. Trained on 8×A100-80GB + 8×H200; GPU-hours not
   reported [JF §4].
4. **What it preserves.** Causal attention and **exact KV-cache reuse** — its
   central argument versus bidirectional diffusion LLMs. This ties the method to
   *causal decoders* [JF §5].
5. **Reported result.** ~2.57–3.86× wall-clock speedup (TPF up to ~4) on
   HumanEval/MBPP/GSM8K/MATH at **7B**, with a small accuracy change (−4.3 to
   +0.4 pts) [JF §6]. Speedup depends on spare compute during memory-bound
   decoding, with a hardware "knee" near 64–126 parallel tokens on H200/B200,
   shorter on A100 [JF §5].

**Established scope.** Causal AR decoders, 7B, code/math, greedy decoding,
long generations. Nothing about classification, routing, encoder-only models,
sub-7B scale, edge hardware, sampling, or open-domain chat is shown [JF §1, §7].

## 3. ESTABLISHED — the title phrase has no external meaning

- The exact phrase **"Jacobi-Forced Micro-Encoder" returns no ML result**; hits
  are the Jacobi Forcing repo/blog (which never use the phrase) and unrelated
  hardware rotary encoders [ME §1].
- **"Micro-encoder" is not an established term** in LLM routing; the nearest
  "micro" usage is μLMs (8–30M decoder-only generators, arXiv 2604.19642), which
  are not encoders or routers [ME §1, §3.1].
- Combining "Jacobi Forcing" with encoder/router/classification returns nothing
  relevant [ME §1].
- **Inside `source/main-original.tex`, "Jacobi", "Micro" and "Encoder" occur only
  in the title (L22)**; the body always says "Tiny Language Model (TLM)" and the
  Proposed Solution (L193–195) is empty [ME §1; research/problem-as-written.md §0].

The search was WebSearch-only (no Scholar/Semantic Scholar/DBLP full text, no
non-English venues), so this is **bounded** evidence of absence, not proof [ME §1].

## 4. UNSUPPORTED — the literal reading

Read literally, "Jacobi-Forced Micro-Encoder" = "a small **encoder** trained with
**Jacobi Forcing**". This is technically incoherent [ME §4; JF §9]:

1. Jacobi Forcing needs a **causal decoder**; a bidirectional encoder
   (BERT/ModernBERT/DeBERTa) has no left-to-right fixed-point iteration to
   accelerate.
2. Routing as formulated (Eq. 3, `argmax_k f_θ(q,M_k)`) needs **no sequential
   decoding** — a scoring head emits all `K` scores in one pass. A single-token
   label gives `n=1`, so Jacobi decoding reduces to AR decoding and the speedup
   is exactly **1×** [JF §9].
3. The claimed benefit is in the **wrong place**: Jacobi Forcing lowers
   *per-token generation latency for long outputs*; a router's latency is
   dominated by **prefill of the query**, which Jacobi Forcing does not change
   [ME §4].

So no established method with this name exists, and the literal construction
names a technique with nothing to act on.

## 5. PROPOSED — coherent placements (none tested by us)

These are constructions, tagged **[P]**; none has been implemented or found in
prior work under this name [JF §9; ME §5].

| ID | Placement | When justified | Main risk |
|---|---|---|---|
| **J1 / P1** | **On the edge SLM (the generator), not the router.** Post-train the local SLM with Jacobi Forcing so on-device answers decode faster. Orthogonal to the router. | When local generation latency (not routing latency) dominates end-to-end cost. Faster local decode lowers the local cost term `C(edge)` in Eq. (2), which **moves the routing threshold** toward keeping more queries local. | No public sub-7B JF checkpoints (only 7B code/math) → we would train it ourselves. Edge-hardware speedup unmeasured. −1 to −4 pt accuracy could offset the gain. The contribution is "JF-accelerated edge SLM **+** router", and the title's "Jacobi-forced" would describe the generator, not the encoder. |
| **J2 / P3** | **Generative router with structured multi-token output** (`{model, split_depth, confidence, …}`) decoded with Jacobi Forcing. Only reading where the *router itself* is Jacobi-forced. | Only if the decision must be a multi-field structured string a classifier head cannot produce. | The output is tens of tokens, far below where JF's long-generation gains appear; a multi-head classifier emits the same fields in one pass. Keep as an **ablation only**. |
| **J3** | **Jacobi-trajectory statistics as routing features** (e.g. iterations-to-converge on the first block as a difficulty/uncertainty signal). | Only if such signals predict edge-model failure better than cheap baselines (token entropy, probe confidence). | Purely speculative; no evidence convergence speed tracks correctness. Requires running the SLM first, adding latency before the decision. |

**[O] Our read for the advisor to weigh (not a decision):** J1/P1 is the most
defensible and honestly evaluable — it is a *systems* contribution (faster edge
generation → changed cost table → shifted route boundary) that composes with any
router in `methods/02`. J2/P3 belongs in the ablation set. J3 is a research
hypothesis, not a method.

Note the adjacent verified fact: **Split-LLM over a WAN has already been paired
with a Jacobi-family decoder** (lookahead decoding, arXiv 2602.16760) to
amortise round trips [research/closest-prior-art.md §2.11]. That is the
technically sensible role for Jacobi-style decoding here — amortising Split-LLM
generation round trips — and it is *partially occupied* by that preprint;
replacing lookahead with a JF-trained model there is not reported.

## 6. UNRESOLVED — questions only the advisor/authors can settle

1. **What did the authors mean by "Jacobi-Forced"?** Jacobi Forcing (the ICML
   2026 parallel-decoding method), the classical Jacobi iterative method from
   numerical linear algebra, or a placeholder? The body never says.
2. **What scale is "micro"?** μLM (8–30M), MiniLM/ModernBERT (22–150M), or
   tinyrouter-scale (0.6B encoder + tiny head)? No parameter target is given
   anywhere in the source [ME §7].
3. **Must "Jacobi" survive at all in the method?** If its only defensible role
   is J1 (the generator), the *title* would need to change to describe the
   generator, not the encoder — a decision for the authors.
4. Does JF work at 0.5–3B scale and on edge accelerators? Not reported; needs an
   experiment [JF §10].
5. License of the two 7B HF checkpoints (no license field exposed) [JF §10].

## 7. Consequences for this sprint

- **Do not** state that a method called "Jacobi-Forced Micro-Encoder" exists
  (§3, §4). Any use of the phrase in `methods/12`/`methods/02` must be flagged
  PROPOSED and attached to J1/J2/J3.
- The candidate methods in `methods/02` are defined **independently of Jacobi**;
  J1 appears there as an **orthogonal systems add-on** (an ablation/roadmap
  branch, `methods/09`), not as the router.
- **Do NOT remove Jacobi from the paper** (METHOD_BRIEF §6 F). Its unresolved
  role becomes a top advisor question (`methods/11`, question A/B block).

## 8. Advisor questions (Jacobi block — feeds `methods/11`)

1. By "Jacobi-Forced Micro-Encoder", did you mean Jacobi Forcing (arXiv
   2512.14681, ICML 2026), the numerical Jacobi method, or a working title?
2. Is Jacobi meant to accelerate the **router**, the **edge SLM generator**, or
   the **Split-LLM generation round trips**? (Only the latter two are coherent.)
3. If we keep a Jacobi component as J1 (edge-generator speedup), are you willing
   to have the title describe the generator rather than the encoder?
4. What parameter scale did you intend for "micro"?
5. Is training a sub-2B model with Jacobi Forcing ourselves (no public
   checkpoint exists) in scope for the lab/compute budget?
