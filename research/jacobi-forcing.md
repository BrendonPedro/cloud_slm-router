# Jacobi Forcing: technical review and applicability to a routing encoder

Deliverable 6 of 18. Written 2026-09-23 (gnhf iteration 2).

**Status of evidence.** Every numeric claim below was read from the primary
source: the arXiv v1 HTML of arXiv:2512.14681, the official GitHub repository,
the Hugging Face model API, and the ICML 2026 virtual-conference page. Where
the authors' blog disagrees with the paper, the paper is used and the
discrepancy is recorded (§8). Sections 9–10 contain **our own analysis and
proposals**. They are labelled as such, and none of them is backed by an
experiment.

---

## 1. Source record

| Field | Value |
|---|---|
| Title | *Fast and Accurate Causal Parallel Decoding using Jacobi Forcing* |
| Authors | Lanxiang Hu, Siqi Kou, Yichao Fu, Samyam Rajbhandari, Tajana Rosing, Yuxiong He, Zhijie Deng, Hao Zhang |
| Date | arXiv v1 submitted 2025-12-16. Only v1 existed when checked on 2026-09-23 |
| Venue / status | **ICML 2026 poster** (Seoul; Wed 8 Jul 2026, Hall A #2207). Confirmed on icml.cc/virtual/2026/poster/64353; OpenReview id `ORy2hyPd4G` |
| arXiv | https://arxiv.org/abs/2512.14681 |
| Code | https://github.com/hao-ai-lab/JacobiForcing. Apache-2.0 (GitHub API `license.spdx_id`); repo created 2025-06-25, last push 2026-02-20 |
| Checkpoints | `JacobiForcing/JacobiForcing_Coder_7B_v1` (base Qwen2.5-Coder-7B-Instruct, trained on OpenCodeInstruct) and `JacobiForcing/JacobiForcing_Math_7B_v1` (base Qwen2.5-Math-7B-Instruct, trained on the OpenThoughts2 math split). Both were created on HF on 2025-12-15. The HF API returned **no license field** in either model card, so reuse terms must be checked before any redistribution |
| Blog | https://haoailab.com/blogs/jacobi-forcing/ (secondary to the paper; see §8) |
| What it establishes | That a pretrained causal AR LLM can be post-trained into a parallel (multi-token-per-forward) decoder with causal attention and an exact KV cache, reaching ~3.5–4.0× wall-clock speedup at 7B scale on code/math with a small accuracy change |
| What it does not establish | Anything about classification, routing, encoder-only models, sub-7B models, edge hardware, non-greedy sampling, or open-domain chat |

Lineage (all verified on arXiv / proceedings pages):

| Work | Venue | Role |
|---|---|---|
| Song, Meng, Liao, Ermon, *Accelerating Feedforward Computation via Parallel Nonlinear Equation Solving*, arXiv:2002.03629 | ICML 2021 | Recasts sequential feed-forward/AR computation as a nonlinear system solved by Jacobi / Gauss-Seidel iteration, and proves that the fixed point equals the sequential result |
| Santilli et al., *Accelerating Transformer Inference for Translation via Parallel Decoding*, arXiv:2305.10427 | ACL 2023 | Jacobi / Gauss-Seidel decoding for MT transformers with no retraining: "up to 38%" speedup, "nearly 2x" with more parallel resources |
| Fu, Bailis, Stoica, Zhang, *Break the Sequential Dependency of LLM Inference Using Lookahead Decoding*, arXiv:2402.02057 | ICML 2024 (PMLR 235:14060–14079) | Exact, training-free parallel decoding built on Jacobi iteration plus n-gram verification (up to 1.8× on MT-Bench) |
| Kou, Hu, He, Deng, Zhang, *CLLMs: Consistency Large Language Models*, arXiv:2403.00835 | ICML 2024 | Consistency distillation on Jacobi trajectories (2.4–3.4× speedup). Jacobi Forcing's direct predecessor |
| Hu et al. (above), Jacobi Forcing | ICML 2026 | Progressive consistency distillation with a noise-aware causal mask, plus multi-block decoding and rejection recycling |

The Jacobi Forcing paper (§5 related work) also cites CEED-VLA (robotics),
FastCoT, Speculative Jacobi Decoding (text-to-image) and MSN / TR-Jacobi. **None
of these uses Jacobi decoding for routing or classification.** We have not
verified those papers individually.

---

## 2. The original problem

Greedy autoregressive (AR) decoding takes one forward pass per generated
token. The paper's Eq. 1 is `y_i = argmax_y p_θ(y | y_<i, x)`, so producing *n*
tokens needs *n* sequential passes. At small batch sizes decoding is
memory-bandwidth-bound, which leaves GPU compute idle.

The paper positions itself against two families that already predict several
tokens per step:

* **Diffusion LLMs (dLLMs) adapted from AR models**, e.g. Fast-dLLM, D2F,
  Dream and LLaDA. According to the paper they suffer a *pretrain-to-posttrain
  mismatch*: masked-token training data differ from the pretraining
  distribution, and bidirectional attention conflicts with the causal prior
  and prevents exact KV-cache reuse. The abstract states both points.
* **Consistency distillation on Jacobi trajectories (CLLM).** Per the paper
  (§1), the number of tokens decoded correctly per iteration "remains
  essentially constant" as the block size grows.

## 3. Jacobi decoding from first principles

Rewrite greedy AR decoding of an *n*-token block as a system of *n* equations
(paper Eq. 2):

```
f(y_i, y_<i, x) := y_i − argmax_y p_θ(y | y_<i, x) = 0,   i = 1..n
```

Solve the system by **Jacobi fixed-point iteration** (paper Eq. 3). Start
from a random guess `y^(0)`. At each iteration, update **every** position in
parallel using the *previous* iterate:

```
y_i^(j+1) = argmax_y p_θ(y | y_<i^(j), x)    for all i simultaneously
```

Under a causal attention mask, all *n* updates come from **one** forward pass
over the block. Iteration stops when `y^(k) = y^(k−1)`. That fixed point `y*`
is provably identical to greedy AR output (Song et al., 2021). Position 1 is
correct after the first iteration, and each later iteration fixes at least one
more token, so convergence takes at most *n* iterations. A long response is
decoded block by block (paper Eq. 4).

**Why vanilla Jacobi decoding barely helps.** An LLM trained only with
teacher forcing rarely predicts a token correctly when earlier tokens in its
context are still wrong. In practice about one token converges per iteration.
The paper's Tables 1–2 confirm this: vanilla Jacobi reaches TPF (tokens per
forward) 1.01–1.05 and speedup 0.97–1.02×.

## 4. Training objective

**CLLM consistency loss (paper Eq. 5).** Collect Jacobi trajectories by
running Jacobi decoding with the base model on a prompt set. Then train the
model so that an intermediate (noisy) state `y^(j)` maps to the fixed point
`y*`: minimise the KL divergence between the model's predictions on the fixed
point (stop-gradient teacher `p_θ⁻`) and its predictions on the noisy state.
Consistency loss on its own degrades quality, so an AR loss is added.

**What Jacobi Forcing changes (paper §3.1):**

1. **Progressive noise schedule (Eq. 7).** Instead of one large block
   conditioned on a long noisy prefix, the response is split into smaller
   blocks. Block *i* gets noise ratio `t_i = W[i mod w]`, where
   `W = {0, 1/w, …, (w−1)/w}`. Within each window the noise rises linearly from
   clean to fully noisy, then cycles. The paper says this cuts the longest run
   of consecutive noisy inputs from O(nN) to O(⌈tn⌉). Ablation (Table 4):
   linear progressive beats random and reverse schedules.
2. **Progressive consistency loss `L_pc` (Eq. 8).** Averaged over the *N*
   blocks, the KL between the teacher's distribution given clean
   (fixed-point) previous blocks and the student's distribution given noisy
   previous blocks at their scheduled noise levels.
3. **Final objective (Eq. 9).** `L(θ) = L_pc + w·L_AR`, with *w* a tunable
   weight. We did not find the value of *w* in the main text.
4. **Noise-aware causal attention with sequence packing (Fig. 2).** Noisy
   blocks `y_Bi^{t_i}` and clean blocks `y_Bi*` are interleaved in one packed
   sequence under a block-sparse causal mask. All loss terms then come from
   **one forward/backward pass** rather than O(2N). Two mask variants are
   ablated (Table 5: NC vs NC-IC).
5. **Progressive distillation.** Round 1 uses block size 16 and window 16 for
   10k steps. Trajectories are then regenerated with the trained model, and
   round 2 uses block size 32 and window 8 for another 10k steps (paper §4.1).

Training setup as reported (§4.1): 8× A100-80GB and 8× H200 instances;
batch size 4; max new sequence length 2048; 10k + 10k steps. 450k coding
prompts from OpenCodeInstruct were used for trajectory generation (paper
§4.1). **GPU-hours and total training cost are not reported.**

## 5. Inference: parallel decoding, causality and the KV cache

* **Causality is preserved.** The architecture and attention mask stay those
  of the original AR model, so the model is a near drop-in replacement and
  keeps **exact KV-cache reuse**. The paper contrasts this with bidirectional
  dLLMs. This property is the paper's main argument and the reason the method
  is tied to *causal* decoders.
* **Multi-block decoding (§3.2, Alg. 1).** Up to *K* blocks are refined at
  once. An automated summary of the HTML gave K = 2 and a spawn ratio of 0.85,
  but those values sit inside MathML that our text extraction strips, so they
  are **unverified**. Check them in the PDF or code before citing them. Only the "real-active" block nearest
  the KV-cache boundary commits tokens to the KV cache. "Pseudo-active" blocks
  are drafted under a noisy context and re-verified once promoted.
* **Rejection recycling.** High-quality n-grams from earlier non-converged
  iterations are pooled and verified in parallel as candidates. The paper says
  both techniques are **lossless** relative to greedy AR because acceptance in
  the real-active block uses greedy rejection sampling (Leviathan et al.).
* **Hardware knee.** Their roofline analysis (§4.3, App. D) finds that
  generation latency stays flat up to ~64–126 parallel tokens on H200/B200 and
  has a shorter plateau on A100. The final configuration was chosen near that
  "knee". **This matters for us.** The speedup relies on spare compute during
  bandwidth-bound decoding, so it is hardware-dependent.

## 6. Reported speedups (paper, v1)

Baseline AR: Qwen2.5-Coder-7B-Instruct (code) / Qwen2.5-Math-7B-Instruct
(math), greedy decoding, A100 unless stated. "MR" = multi-block + rejection
recycling.

| Benchmark | AR acc. | JF acc. | JF speedup (TPF) | JF-MR speedup (TPF) | CLLM speedup |
|---|---|---|---|---|---|
| HumanEval | 87.8 | 83.5 | 3.86× (4.01) | 3.97× (4.09) | 2.50× |
| MBPP | 74.3 | 70.4 | 2.57× (2.74) | 2.62× (2.84) | 1.94× |
| GSM8K | 92.4 | 91.4 | 3.50× (3.72) | 3.71× (4.04) | 2.08× |
| MATH | 77.0 | 77.4 | 3.65× (3.82) | 3.68× (3.98) | 2.04× |

* The adapted-dLLM baselines were slower and less accurate in these tables:
  e.g. on HumanEval D2F had 1.77× at 54.3% and Fast-dLLM (DC) 1.45× at 53.0%.
* On B200 (Table 6), JF-MR reports TPF 4.21 and **327.96 TPS** on HumanEval.
  The repo summarises this as ~330 vs ~80 tok/s AR.
* **Relevance to our manuscript:** in the same Table 6, **Fast-dLLM v2 scores
  63.4% on HumanEval versus 87.8% for the AR baseline**. The original
  manuscript lists *Fast-dLLM-v2-7B* in its model pool (main-original.tex
  L290). Its quality relative to AR models should be discussed if it stays in
  the pool.

## 7. Limitations (from the paper plus our reading)

Stated or implied in the paper:

* Evaluated **only on code and math** (HumanEval, MBPP, GSM8K, MATH) and
  **only at 7B** (Qwen2.5 variants).
* Fixed points and the "lossless" claims are defined relative to **greedy**
  decoding. Stochastic sampling is not addressed.
* Accuracy is not fully preserved: −4.3 pts on HumanEval, −3.9 on MBPP, −1.0
  on GSM8K, +0.4 on MATH. The paper describes this as "minimal loss" /
  "largely preserving accuracy".
* The paper has **no dedicated Limitations or Future-Work section**.
* Training cost is described qualitatively (Fig. 1) but not given in
  GPU-hours.

Our observations (not claims from the paper):

* Speedup depends on idle compute during memory-bound decoding (§5). Whether
  3–4× carries over to **edge NPUs/mobile GPUs** or to **sub-1B models** has
  not been shown. We found no source that measures it.
* The method needs **model-specific post-training**: trajectories are
  collected from the target model itself. Only two 7B checkpoints are public,
  and neither is a small edge model.
* The gain grows with generation length. For very short outputs there is
  little to parallelise (see §9).

## 8. Discrepancies noted during verification

* **Blog vs paper numbers.** The blog summary reports HumanEval "4.0× speedup
  with 82.3% accuracy". The paper's Table 1 reports **83.5%** at 3.86× (JF)
  and 3.97× (JF-MR). The figure 82.3% appears in the paper only in the
  mask-variant ablation (Table 5: NC 3.6×/82.3, NC-IC 1.9×/82.3). **Cite the
  paper's Table 1, not the blog.**
* **Repo title vs paper title.** The GitHub repo is titled "Jacobi Forcing:
  Fast and Accurate *Diffusion-style* Decoding". The paper title is "…*Causal
  Parallel* Decoding…". Use the paper title in BibTeX.
* The abstract's "3.8× wall-clock speedup" is the paper's summary figure. The
  per-benchmark tables range from 2.57× (MBPP) to 3.86× (HumanEval).
* The arXiv HTML's ethics statement refers to the "ICLR Code of Ethics",
  apparently left over from an earlier submission. The confirmed venue is ICML
  2026.

---

## 9. Does Jacobi Forcing naturally apply to a tiny routing encoder?

**Short answer: no, not directly.** This is our analysis, not a claim from
any paper.

1. **The router's output needs no sequential decoding.** The manuscript's
   routing rule (Eq. 3; see `research/problem-as-written.md`) is an argmax of
   a score `f_θ(q, M_k)` over *K* candidate models. A score or classifier head
   produces all *K* scores in one forward pass. Jacobi Forcing speeds up only
   the part of inference that takes *n* sequential passes for *n* tokens, and
   a classification router has no such part.
2. **Degenerate case: a one-token label.** If the router is a generative LM
   that emits one label token (e.g. "EDGE" / "CLOUD"), then n = 1. Paper Eq. 3
   gives `y_1 = argmax p_θ(y | x)` in the first iteration, which is already
   the fixed point, so Jacobi decoding equals AR decoding and there is nothing
   to speed up. Prompt encoding (prefill) is already parallel in any
   transformer.
3. **Encoder-only models do not fit the method's premise.** Jacobi Forcing is
   defined for causal AR decoders. Its central argument is that it preserves
   the *causal* prior and exact KV-cache reuse, unlike bidirectional dLLMs. A
   bidirectional encoder (BERT/ModernBERT style) is neither causal nor
   generative. There is no trajectory to distil and no fixed-point iteration
   to accelerate.
4. **Nothing in the literature uses it for routing.** The Jacobi Forcing
   paper does not mention classification, encoders or routing (checked in the
   full v1 HTML). Web searches on 2026-09-23 for "Jacobi Forcing" with
   router/routing/encoder/classification, and for "micro-encoder" with
   "Jacobi", returned no work applying Jacobi decoding, CLLM consistency
   distillation or Jacobi Forcing to routing or encoder-only decision models.
   This is absence of evidence from a bounded search, not proof of absence;
   deliverable 7 extends the search.
   *Name-collision warning:* **ConsRoute** (arXiv:2603.21237, cloud–edge–device
   query routing) uses "consistency" to mean *semantic agreement between model
   outputs*, not consistency distillation. It is a routing paper for the
   closest-prior-art review, not a Jacobi method. It has not been verified in
   detail yet.

### What adaptation would make it technically coherent

These are **proposed interpretations**, not established techniques, and none
has been tested.

| # | Where Jacobi Forcing would sit | When it is justified | Main risk |
|---|---|---|---|
| J1 | **On the edge SLM (the generator), not the router.** Post-train the local SLM with Jacobi Forcing so that answers kept on-device decode faster | When local generation latency, not routing latency, dominates end-to-end cost. Faster local decoding changes the cost term and so moves the optimal routing threshold | No public sub-7B checkpoints. Edge-hardware speedup is unmeasured. Accuracy loss (−1 to −4 pts at 7B) could offset the routing benefit. The contribution would be "Jacobi-accelerated edge SLM + router", not a "Jacobi-forced encoder" |
| J2 | **A generative router with structured multi-token output**, e.g. a JSON decision `{model, confidence, max_tokens, reason}` of tens of tokens | Only if the decision must be a structured multi-field output that a classifier head cannot produce | A multi-head classifier/regressor can emit the same fields in one pass, cheaper. The baseline "classifier head" would probably dominate |
| J3 | **Jacobi-trajectory statistics as routing features** (hypothesis): e.g. the number of iterations the edge SLM needs to converge, or its fast-forward count on the first block, as a difficulty/uncertainty signal | Only if such signals predict edge-model failure better than cheap baselines (token entropy, the router's own confidence) | Purely speculative. We found no evidence that convergence speed tracks answer correctness. It also requires running the SLM first, which adds latency before the routing decision |

**Implication for the paper.** The title phrase "Jacobi-Forced
Micro-Encoder" does not describe a method that follows naturally from Jacobi
Forcing. If the authors keep a Jacobi component, J1 is the most defensible
reading: a speedup for the *generator*, evaluated as its own ablation. For
the *router* the question is what makes an accurate, calibrated and cheap
classifier, and Jacobi Forcing does not address that question. This supports
research question 9 ("Does the router need generative decoding at all?"): as
formulated in Eq. 3, it does not.

## 10. Open questions (carry forward)

1. What did the authors of main-original.tex mean by "Jacobi-Forced"? The
   manuscript never defines it (Proposed Solution L193–195 is empty). **Ask the
   advisor/authors before redesigning.**
2. Does Jacobi Forcing work at 0.5–3B scale and on edge accelerators? Not
   reported. Answering would need an experiment (deliverables 10–12).
3. What licence applies to the two HF checkpoints? The model cards expose
   none. Qwen2.5 base licences may apply. Unverified.
4. What is the value of the loss weight *w* in Eq. 9? It may be in the
   appendix or code; not checked.
5. Is there any correlation between Jacobi convergence behaviour and answer
   correctness (J3)? Unknown. It would be a new empirical question, not a known
   result.
