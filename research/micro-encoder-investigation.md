# Deliverable 7 — "Jacobi-Forced Micro-Encoder": does it exist, and what could it mean?

Date of search: **2026-09-23**. Prepared in an AI-assisted research sprint (see
`advisor/research-sprint-report.md` once it exists). Every source below was
opened at its primary location (the arXiv abstract page through
`export.arxiv.org/abs/<id>`, the GitHub API, or the Hugging Face API) unless it is
marked otherwise. Numbers are quoted from abstracts or READMEs only. None of them
was reproduced by us.

---

## 1. Short answer

> **No established method with this exact name was found as of 2026-09-23.**

- The exact phrase "Jacobi-Forced Micro-Encoder" returned no ML result. The only
  hits were the Jacobi Forcing repo and blog, which do not use the phrase, plus
  unrelated hardware "micro encoders" (rotary position sensors: Harmonic Drive,
  Scancon, CALT, and USPTO patents 5982169 and 6744385).
- "Micro-encoder" is **not** an established term in the LLM-routing literature.
  The nearest ML use of "micro" is *micro language models* (μLMs, arXiv 2604.19642,
  §3.4). Those are **decoder-only generators** of 8M–30M parameters, not encoders
  or routers.
- The combination of "Jacobi Forcing" with encoder, router or classification returned
  nothing relevant. Hits were unrelated uses of "Jacobi" (Jacobi saliency maps
  for adversarial attacks, Jacobian sparse autoencoders, Jacobi-algorithm traffic
  classification). This agrees with the finding in `research/jacobi-forcing.md` §8
  that the Jacobi Forcing paper (arXiv 2512.14681, ICML 2026) never mentions
  classification, encoders or routing.
- Inside `source/main-original.tex`, "Jacobi", "Micro" and "Encoder" occur **only in
  the title (L22)**. The body calls the router a "Tiny Language Model (TLM)"
  (L40, L56, L61, L129, L152, L185–191), and the Proposed Solution section
  (L193–195) is empty (see `research/problem-as-written.md`). So the manuscript does
  not define the phrase either.

The phrase therefore has **no meaning in the literature and no meaning in the
manuscript**. Any meaning has to be proposed by the authors, and it must be labelled
as a proposal (§5).

### Search log (reproducible)

| # | Query (WebSearch, 2026-09-23) | Relevant result |
|---|---|---|
| 1 | `"Jacobi-Forced Micro-Encoder"` | None. JF repo/blog (no phrase) plus hardware encoders |
| 2 | `"micro-encoder" LLM routing` | No use of the term. Surfaced encoder-based routers: 2603.20895, 2606.31163, 2606.18774 |
| 3 | `"Jacobi Forcing" encoder OR router OR classification` | None relevant |
| 4 | `lightweight encoder router LLM routing ModernBERT DeBERTa …` | HyDRA 2605.17106, vLLM-SR 2603.12646, BEST-Route, RAGRouter baseline 2604.03455 |
| 5 | `"micro encoder" language model transformer arXiv` | μLMs 2604.19642 (decoder, not encoder); MicroNet 2005.07877 (LM compression) |
| 6 | `"tiny encoder" OR "routing encoder" LLM router edge cloud …` | tinyrouter (GitHub), gemma4-edge-cloud-router (GitHub), Pro-Router 2608.28726 |
| 7 | `Jacobi decoding encoder-only bidirectional classification … router` | Only JF / CLLM / Jacobi decoding papers, all about generation |
| 8 | `"query encoder" router … RouterDC` | RouterDC 2409.19886, CSCR 2508.12491 |

Limitations of this search: web search engines only, with no Google Scholar, Semantic
Scholar API, ACL Anthology or DBLP full-text search. Non-English literature
(e.g. Chinese-language venues) was not searched. A paper using the phrase could
exist behind a paywall or in a venue this search does not index. Absence of
evidence here is **bounded** evidence of absence, not proof.

---

## 2. What *does* exist: lightweight encoders used as LLM routers

The idea behind the phrase, a *small, non-generative encoder that reads the
query and emits a routing decision*, is **well occupied**. This matters for the
novelty assessment: renaming an encoder-classifier router a "micro-encoder" does
not create novelty.

| Work | Date / status | Router body | Output | Setting | What it establishes | Code |
|---|---|---|---|---|---|---|
| **RouteLLM** — Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, … (arXiv 2406.18665) | 2024-06, v-latest 2025-02; ICLR 2025 per the authors (venue not re-verified this iteration) | Four routers, including a **BERT classifier**, matrix factorization (`mf`, recommended in the README), similarity-weighted ranking, and a causal-LLM classifier | Win-probability strong vs weak, thresholded | Cloud, binary strong/weak | A small encoder classifier is a standard baseline for binary routing | `lm-sys/RouteLLM`, Apache-2.0 (GitHub API) |
| **RouterDC** — Chen, Jiang, Lin, Kwok, Zhang (arXiv 2409.19886) | NeurIPS 2024 (arXiv comment) | **mDeBERTaV3-base** query encoder plus learnable per-LLM embeddings, dual contrastive loss | Cosine-similarity argmax over the LLM pool | Multi-LLM, cloud | Contrastive query encoder routing; +2.76% ID / +1.90% OOD over prior routers (abstract) | `shuhao02/RouterDC` |
| **BEST-Route** — Ding, Mallick, Zhang, Wang, … (arXiv 2506.22716) | ICML 2025 (arXiv comment) | Multi-head router on **DeBERTa-v3-small** (per search-result snippet; not yet checked in the paper body) | Model *and* number of samples | Multi-LLM, cloud | Encoder router whose output is a structured decision (model × sampling budget) | not checked |
| **CSCR** — Shirkavand, Gao, Yu, Huang (arXiv 2508.12491) | 2025-08, preprint | Contrastive encoder into a shared prompt/model space, k-NN via FAISS | Cheapest accurate expert within cost bands | Dynamic pools, "no retraining when the pool changes" (abstract) | **Pre-empts the "without retraining" claim** (main-original L40, L61) | not checked |
| **HyDRA** — Garg, Roy, Jang, Brancasi, Fu (arXiv 2605.17106) | 2026-05, preprint v2 (2026-06) | **ModernBERT** with 4 independent sigmoid capability heads | Capability vector, then shortfall matching against config-defined model profiles | Production (GitHub Copilot VS Code auto-mode, per the abstract) | 86 ms median **CPU** latency; "zero retraining" when the catalogue changes; SWE-Bench Verified 5-model pool results (abstract) | not stated |
| **vLLM Semantic Router** (Liu, He, Liu, Luo, Zhang, Chen; arXiv 2603.12646) | 2026-03, preprint | ModernBERT-class classifiers (safety, domain, PII), optimised with CK Flash Attention/ONNX on MI300X | Classification labels to routing path | Co-located with vLLM | Engineering of encoder-classifier routers without a dedicated GPU | vLLM project (not checked this iteration) |
| **ComplianceGate** — Dey (arXiv 2606.31163) | 2026-06, preprint, single author | Encoder classifier ahead of any decoder | Complexity × data-sensitivity, then tier and geography | Multi-tier, PII-aware residency routing | 99.2% accuracy, 7 ms overhead, 600-query evaluation (abstract; small evaluation) | not stated |
| **Prefill-activation router** — Varshney, Surla, Xu, Krishnan, Jeblick, Austin, … (arXiv 2603.20895) | 2026-03, v2 2026-08, preprint | Residual-stream activations from an open-weight "Encoder" model, then SharedTrunkNet MLP | Per-model correctness probabilities | Closed-source targets | Calls the feature-producing LLM an **"Encoder"** (Encoder-Target Decoupling). This is the nearest *terminological* neighbour to "micro-encoder" we found | not stated |
| **Lightweight RAG routing baseline** — Bansal, Agarwal (arXiv 2604.03455) | 2026-04, 5-page preprint | TF-IDF / MiniLM + classical classifiers | Retrieval strategy class | RAG strategy selection | TF-IDF+SVM macro-F1 0.928 on RAGRouter-Bench (abstract). A reminder that **non-neural baselines** are mandatory | not stated |
| **Pro-Router** — Gui, Wang, Sun, Wang, Yu, Yang (arXiv 2608.28726) | 2026-08-28, preprint | Lightweight *prompt pre-scorer* plus a token-level verifier on SLM output | Ship or escalate edge to cloud | **Edge–cloud**, multimodal | Two-stage (pre-generation classifier + post-generation confidence) edge–cloud routing; claims >10× routing speed (abstract) | `xinyuangui2/pro-router` (per abstract) |
| **Arch-Router-1.5B** — Tran, Paracha, Hafeez, Chen (arXiv 2506.16655) | 2025-06, preprint | **Generative** 1.5B model; HF `pipeline_tag = text-generation`, `base_model = Qwen/Qwen2.5-1.5B-Instruct` (HF API) | Generated route/policy name | Preference-aligned domain/action routing | The main *generative* small-router baseline. **Note for the claim audit:** main-original L317 says the authors will "fine-tune its routing head", but the checkpoint is a causal LM with no separate head, so the baseline description needs rewriting | HF `katanemo/Arch-Router-1.5B` (license field `other`); serving code in `katanemo/plano` (formerly archgw; Apache-2.0) |

Non-peer-reviewed open-source artefacts (low evidential weight, listed for completeness):

- **tinyrouter** (`harrrshall/tinyrouter`, created 2026-06-22, no licence file,
  ~315 stars at retrieval). A frozen **0.6B encoder** produces a 1024-d vector, and a
  **~10K-parameter head** trained by sep-CMA-ES picks the model and role, following
  TRINITY (arXiv 2512.04695, stated as ICLR 2026 in the README, not verified). Its own
  README reports that on math the router scores **0.792 vs 0.794 for the best single
  model and 0.792 for random routing** on 120 held-out questions. That is an honest
  negative result: when the pool leaves little oracle headroom, a tiny router adds
  nothing. This is directly relevant to experiment design (oracle-headroom check;
  see §6).
- **gemma4-edge-cloud-router** (`a2o-labs/gemma4-edge-cloud-router`, MIT,
  created 2026-09-18, 0 stars). A light/heavy classifier dispatches to an edge Gemma
  model or a cloud endpoint. An optional "V1.5" sends a 4096-d **edge-encoder
  embedding** to the cloud through a trainable soft-prompt adapter (BLIP-2 Q-Former
  pattern). This is a 5-day-old research artefact with no paper and no reported
  results. Its only use here is as a sign that "edge encoder → cloud" designs are being
  built openly.

**Implication.** A "micro-encoder router" in the plain sense (a small encoder plus a
classification head) is already standard practice in academic work (RouteLLM
BERT, RouterDC, BEST-Route), in production (HyDRA, vLLM-SR, ComplianceGate) and in
edge–cloud settings (Pro-Router pre-scorer). Both "no retraining when the pool changes"
(CSCR, HyDRA) and "sub-10 ms / CPU-only" operation (ComplianceGate, HyDRA,
vLLM-SR) are claimed by prior work. Any contribution has to lie elsewhere.

---

## 3. Related uses of "micro" / "tiny" that could be confused with the title

### 3.1 Micro language models (μLMs) — arXiv 2604.19642
Cheng, Chen, Helwani, Srinivasan, Zettlemoyer, Gollakota; 2026-04-21; preprint.
These are 8M–30M-parameter **decoder-only** models that generate the first 4–8 words
on-device while a cloud model continues the response. The abstract reports a checkpoint
and demo at `Sensente/micro_language_model_swen_project` (not opened this iteration).
*Relevance:* this is the closest "micro-scale edge model + cloud collaboration" work, but
it does **handoff/continuation**, not routing. It shows that "micro" in 2026 ML usage
points to a tens-of-millions-parameter scale, and the manuscript gives no parameter target
for its TLM at all.

### 3.2 MicroNet — arXiv 2005.07877
An efficient language-modelling/compression paper from 2020. It is unrelated to routing and is
listed only because it matches the search term.

---

## 4. Why the literal reading is technically incoherent

Taken literally, "Jacobi-Forced Micro-Encoder" = "a small **encoder** trained with
**Jacobi Forcing**". That reading conflicts with what Jacobi Forcing is
(`research/jacobi-forcing.md` §§2–5):

1. **Jacobi Forcing needs a causal (decoder) model.** Its objective trains a causal
   AR model to predict the fixed point from its own noisy Jacobi-trajectory blocks, under
   a causal mask. A bidirectional encoder (BERT/ModernBERT/DeBERTa) has no
   left-to-right fixed-point iteration to accelerate.
2. **Routing as formulated needs no sequential decoding.** main-original Eq. (3)
   (L185–191) is `argmax_k f_θ(q, M_k)`, a scoring problem solved in one forward
   pass. If the decision is a single token, Jacobi decoding reduces to AR decoding
   (n = 1), so the speedup is exactly 1×.
3. **The claimed benefit is in the wrong place.** Jacobi Forcing lowers
   *per-token generation latency for long outputs* (the paper measures 7B models on
   code/math). A router's latency is dominated by *prefill of the query*, which
   Jacobi Forcing does not change.

So under the literal reading the phrase names a method that has nothing to act on.
This is an argument from the published mechanism, not an experimental result.

---

## 5. Proposed interpretations (labelled: **PROPOSED, not established**)

Each option below is our construction. None has been implemented or tested by us,
and we found no prior paper that implements any of them under this name. They extend
J1–J3 in `research/jacobi-forcing.md` §8.

### P1 — "Micro-encoder router + Jacobi-Forced edge SLM" (split the name across two components)
- **What:** a small encoder classifier (e.g. ModernBERT-base or a smaller variant)
  makes the edge/Split-LLM decision. *Separately*, the edge SLM that answers
  locally is post-trained with Jacobi Forcing to decode faster (= J1).
- **Why coherent:** each technique acts where its mechanism applies. The router
  cost model then includes a faster local decode term, which moves the
  cost-optimal threshold toward keeping more queries local.
- **Testable claim:** at a fixed quality target, Jacobi-Forced local decoding
  increases the fraction of queries the router can keep on-edge and lowers
  end-to-end latency compared with an AR edge SLM under the same router.
- **Risks:** there are no public sub-7B Jacobi Forcing checkpoints (the only ones are Coder/Math 7B), so
  the authors would have to run JF training themselves. Edge-hardware speedup is unmeasured.
  The contribution is a *system composition*, and the novelty then rests on the
  joint cost model and evaluation, not on either component.
- **Honest naming:** the title would need to change. The router is not "Jacobi-forced".

### P2 — "Micro-encoder" as a shared-prefix edge encoder whose state is reused by a Jacobi-Forced decoder
- **What:** the edge SLM's own prefill (first *L* layers or the final hidden state
  of the query) serves as the routing feature (as in the prefill-activation router,
  2603.20895, but computed on the *edge* model). A tiny head on those features decides
  local vs Split-LLM. If the query stays local, the same KV cache is reused for
  Jacobi-Forced decoding, so routing costs roughly zero extra prefill.
- **Why coherent:** it removes the separate router model entirely. The "encoder" is the
  causal model's prefill pass, which *is* compatible with Jacobi Forcing, and the
  Split-LLM split point could in principle reuse the same early-layer activations.
- **Testable claim:** shared-prefill routing matches a separate encoder router
  in routing quality (AUROC / cost-quality curve) at lower total edge latency.
- **Risks:** activation-based routing already exists (2603.20895), so novelty would rest
  on the *edge* and *Split-LLM activation reuse* angle. Privacy claims would need care,
  because transmitting activations is not automatically private (see the Split-LLM literature,
  still to review). This is the closest option to a genuinely new combination, and it is also
  the most engineering-heavy.

### P3 — Tiny generative router emitting a structured multi-token decision, decoded with Jacobi Forcing (= J2)
- **What:** a small causal LM (e.g. 0.5–1.5B, like Arch-Router) generates a
  structured decision (`{target, split_layer, max_tokens, confidence}`), and
  Jacobi Forcing parallelises that short structured output.
- **Why coherent:** it is the only reading in which the *router itself* is
  Jacobi-forced.
- **Why weak:** the output is tens of tokens at most, so JF's gains, measured on
  long code/math generations, are unlikely to be material. A multi-head
  encoder (as in HyDRA or BEST-Route) emits the same fields in one pass. P3 should be
  kept only as an **ablation** that tests whether generative routing brings
  anything, not as the main method.

**Our read (for the advisor to weigh, not a decision):** P1 is the most defensible
and the easiest to evaluate honestly. P2 is the most interesting research question
but needs the Split-LLM prior-art review (deliverables 2–4) before its novelty can
be judged. P3 is mainly useful as a negative-control ablation. Under every
interpretation, the literal title overstates what is Jacobi-forced.

---

## 6. Consequences for other deliverables

- **Claim audit (13):** the title (L22) names a mechanism that is not defined anywhere in the body.
  "Unlike existing routing methods that rely on heavy models" (L40, L61) is contradicted
  by RouteLLM-BERT, RouterDC, HyDRA and ComplianceGate, which are all lightweight encoders.
  "Without requiring costly retraining" (L40) is pre-empted by CSCR and HyDRA. The Arch-Router
  baseline description (L317, "fine-tune its routing head") does not match a causal-LM
  checkpoint.
- **Closest prior art / novelty matrix (3, 4):** add HyDRA, Pro-Router, CSCR,
  ComplianceGate, the prefill-activation router and μLMs as candidates. Pro-Router is
  the closest **edge–cloud** router found so far. ConsRoute (2603.21237, flagged in
  iteration 2) is still unverified.
- **Experiment (10):** include (a) an oracle-headroom check before training any
  router (tinyrouter's README shows a router can tie random routing when headroom
  is small), (b) TF-IDF/logistic-regression and a ModernBERT/DeBERTa classifier as
  baselines, and (c) Arch-Router as the generative baseline, used as released.
- **Revised paper (15):** the title should not keep "Jacobi-Forced Micro-Encoder" unless
  one of P1–P3 is implemented and evaluated.

## 7. Open questions / uncertainty

1. Did the original authors intend a specific meaning (e.g. the Jacobi iterative method
   from numerical linear algebra, not Jacobi Forcing)? Only the authors can answer.
   Question for the advisor meeting.
2. What parameter scale does "micro" mean to the authors: μLM-scale (8–30M),
   MiniLM/ModernBERT-scale (22–150M), or tinyrouter-scale (0.6B encoder + 10K head)?
3. BEST-Route's DeBERTa-v3-small router, CSCR's encoder details, and the RouteLLM ICLR 2025
   venue come from search snippets or author statements and have not been checked in the paper
   bodies. Verify them before they go into `references/library.bib`.
4. Pro-Router's code link and μLM checkpoint link were taken from the abstracts and were not opened.
5. The search did not cover Semantic Scholar/DBLP APIs or non-English venues. A follow-up
   pass with the Semantic Scholar API (`/graph/v1/paper/search?query=micro-encoder+routing`)
   would tighten the "not found" statement. It was attempted on 2026-09-23 and
   returned HTTP 429 (unauthenticated rate limit) for all three queries, so it is still
   outstanding.
