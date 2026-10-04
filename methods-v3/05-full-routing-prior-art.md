# 05 — Full-body routing prior art (v3)

*Deliverable 05 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iterations 2–3). Resolves findings
RF-G1 (input), RF-H1, RF-H2, RF-H3 of `00-review-findings.md`.*

This file replaces the abstract/API-level routing characterisations in
`methods-v2/01-*.md` and `methods-v2/17-verified-references.md` with
**body-level** readings of the ten priority-A/B routing papers. For each paper it
records what the router actually predicts, how it is supervised, how cost and
system state enter, what adding a model costs, and what it does and does not
take away from our proposed method. Systems/split-inference prior art is handled
separately in `06-systems-prior-art-map.md`; backbone facts (ModernBERT etc.) in
`07-backbone-verification.md`.

---

## 0. Inspection protocol and limits

* **What "body read" means here.** The full paper text (all sections,
  equations, appendices where present) was retrieved from the arXiv HTML
  rendering of the version stated in each card and read end-to-end, then
  key claims were re-checked by string search in the saved text (2026-10-04).
  For RouteLLM and RouterDC the official repositories were also cloned and
  inspected.
* **Locators are sections / equations / tables, not page numbers.** arXiv HTML
  has no pagination. Where proceedings page ranges are known they are given as
  bibliographic metadata only; a page-level locator for proceedings PDFs is
  `[OPEN]` and is resolved, where needed, in `17-verified-references-v3.md`.
* **Tags** follow brief §29. Inside each card, statements about what the paper
  *does* (its architecture, equations, data) are `[VERIFIED-BODY]`; performance
  and latency numbers the authors report are `[AUTHOR-CLAIM]` (marked **[C]**);
  overlap judgements are our interpretation and marked `[PROPOSED]`.
* **Not read in v3:** RouteLMT (in v2's list, priority B). It remains
  `[VERIFIED-META]` at most and must not be used for a load-bearing statement.

---

## 1. Paper cards

### 1.1 RouteLLM `[VERIFIED-BODY]` (arXiv v4 + v1; repo inspected)

* **Identity.** "RouteLLM: Learning to Route LLMs with Preference Data" (arXiv
  2406.18665 title); the ICLR 2025 poster is titled "RouteLLM: Learning to Route
  LLMs **from** Preference Data" (OpenReview `8sSqNntaMr`). Authors: Isaac Ong\*,
  Amjad Almahairi\*, Vincent Wu, Wei-Lin Chiang, Tianhao Wu, Joseph E. Gonzalez,
  M. Waleed Kadous, Ion Stoica. Repo `lm-sys/RouteLLM`. The BibTeX must use the
  proceedings title.
* **What it predicts.** Binary strong-vs-weak routing: P_θ(win_strong | q) over
  labels {win_s, tie, win_w} (Eq. 1); route to strong iff the probability exceeds
  a threshold α (Eq. 2). Metrics APGR / CPT (§3.2, Eq. 6–8).
* **Routers.** §4.2: similarity-weighted Bradley–Terry ranking (Eq. 9–10),
  matrix factorisation over text-embedding-3-small embeddings (Eq. 11–12), a
  BERT-base classifier (Eq. 13), and a Llama-3-8B causal-LM classifier.
* **Supervision.** §4.1: ~65k Chatbot Arena human pairwise votes (responses
  dropped); D_gold ≈ 1,500 MMLU validation items with golden labels; §4.1.1
  D_judge — responses from a strong and weak model on Nectar prompts, with
  "pairwise comparison labels using GPT-4 as a judge", ≈120K samples at ≈$700,
  debiasing per Zheng et al. (footnote). Paper labels are **hard** categorical
  preferences. The words "distill", "pseudo" and "soft label" occur **zero**
  times in v1 and v4 (string search). The paper calls this **dataset
  augmentation** (§5.1, §6).
* **Artifact-vs-paper discrepancy.** The released causal-LLM router and the HF
  `routellm/gpt4_dataset` use GPT-4 **1–5 scores** (`mixtral_score`, threshold 4)
  rather than win/tie/loss. The manuscript should describe the paper's method
  and, if it reproduces the released checkpoint, name the score variant
  explicitly.
* **Cost / system state.** Cost = fraction of calls to the strong model. No
  network state, no latency model; router overhead ≤0.4% of generation cost,
  expressed as throughput (§5.5, Table 7) **[C]**.
* **Pool change.** Transfer to unseen strong/weak *pairs* without retraining on
  MT Bench (§5.2, Table 4) **[C]**; restricted to a binary pair.
* **Limitations (§6).** Two-model routing only.
* **Overlap with ours.** Query-only learned utility, threshold routing, a
  BERT-class encoder baseline, LLM-judge supervision. **Does not overlap:** >2
  models, split execution, measured system cost, KD.
* **Consequence.** v2's "KD in all but name" is withdrawn; RouteLLM uses
  LLM-as-a-judge **preference supervision / data augmentation with hard
  labels**. Full terminology ruling in `04-routeLLM-terminology-review.md`.

### 1.2 RouterDC `[VERIFIED-BODY]` (arXiv v1; repo inspected)

* **Identity.** "RouterDC: Query-Based Router by Dual Contrastive Learning for
  Assembling Large Language Models". Shuhao Chen, Weisen Jiang, Baijiong Lin,
  James T. Kwok, Yu Zhang. NeurIPS 2024, pp. 66305–66328, DOI
  10.52202/079017-2120. Repo `shuhao02/RouterDC`.
* **What it predicts.** Cosine similarity between an mDeBERTaV3-base (86M) query
  embedding and **T learnable 768-d LLM embeddings**, softmaxed over LLMs (Eq. 3).
* **Supervision.** Per-LLM correctness scores: mean of M=10 sampled 0/1
  outcomes (Eq. 1) or multiple-choice option probability (Eq. 2). Losses:
  sample–LLM contrastive (Eq. 4; K⁺=K⁻=3, negatives s<0.5) + sample–sample
  contrastive over t-SNE+k-means clusters, N=5 (Eq. 5).
* **Setting.** 7 LLMs of 7–8B; in-distribution MMLU, GSM8K, CMMLU, ARC-C,
  HumanEval; OOD PreAlgebra, MBPP, C-EVAL. Cost appears only in App. I
  (score + cost); limitations App. J.
* **Pool change.** No unseen-model claim; the LLM embedding table is fixed, so
  adding a model requires scores for it plus retraining (our reading of Eq. 3–4,
  `[PROPOSED]` interpretation, consistent with absence of any such claim).
* **Overlap with ours.** Query-encoder router producing a per-model score; it is
  the closest published example of **model-level** (not action-level) utility.
  **Does not overlap:** calibrated per-model probabilities (softmax over models
  is not a calibrated P(success) per model), system cost, split, KD.

### 1.3 HyDRA `[VERIFIED-BODY]` (arXiv 2605.17106, v1 and v2)

* **Identity.** "HyDRA: Hybrid Dynamic Routing Architecture for Heterogeneous
  LLM Pools". arXiv metadata lists 5 authors (Garg, Singha Roy, Jang, Brancasi,
  Fu); the v2 PDF header adds Giuseppe Cianci (6). Microsoft. **Preprint, no
  public repo.** The author list must be reconciled to the cited version in the
  BibTeX (`17` / `.bib`).
* **What it predicts.** A fine-tuned ModernBERT-base (149M) with **K=4
  independent sigmoid heads that output per-query capability REQUIREMENT
  scores** for reasoning, code generation, debugging and tool use (abstract,
  §1, §3.1). These are **not** per-model or per-route utilities.
* **How models enter.** Each model m has a static **capability profile** c_m
  (YAML, derived from public benchmarks; App. H, Eq. 3–4). Decision (Eq. 5):
  weighted shortfall s_m = Σ_k w̃_k · max(0, r̂_k − c_{m,k}); a model is eligible
  if s_m ≤ τ, and HyDRA picks the **cheapest eligible** model. Service health is
  only a veto; **no network state** enters the decision.
* **Supervision.** A judge (gpt-5.2-chat) scores a cheap (gpt-5.4-mini) and a
  strong (gpt-5.3-codex) response; per-dimension target
  r_k = max(0, s_strong − s_cheap)/5 (Eq. 7); 50,159 Copilot queries; two
  repo-dependent task types receive a constant 0.8. The word "distills from"
  the judge appears only in the Limitations.
* **Pool change.** "Zero retraining" for adding a model = adding a YAML profile
  (§1, §8, §9) **[AUTHOR-CLAIM]**; it still needs benchmark scores to build the
  profile, and quality of the profile mapping is not independently validated.
* **Latency.** v2 §5.6: 55 ms P50 / 120 ms P99 on CPU INT8 offline **[C]**; v1:
  86 ms median production inference, 142 ms end-to-end **[C]**. The two figures
  come from different versions and settings; cite one with its version.
* **Encoder ablation.** App. F, Table 19: ModernBERT-large +1.1 routing quality
  at ~3× latency (77.3 vs 26.6 ms) **[C]**.
* See §3 for the overlap analysis required by brief §11.

### 1.4 LLMRouterBench `[VERIFIED-BODY]` (arXiv 2601.07206)

* **Identity.** "LLMRouterBench: A Massive Benchmark and Unified Framework for
  LLM Routing". Hao Li, Yiqun Zhang, Zhaoyan Guo, Chenxu Wang, Shengji Tang,
  Qiaosheng Zhang, Yang Chen, Biqing Qi, Peng Ye, Lei Bai, Zhen Wang, Shuyue Hu.
  Findings of ACL 2026, pp. 37733–37754, DOI 10.18653/v1/2026.findings-acl.1881.
  Repo `ynulihao/LLMRouterBench`.
* **Scope.** 21 datasets, 33 models, 391,645 instances. Performance pool: 20
  ~7B models on 15 datasets. Performance–cost pool: 13 flagship models on 10
  datasets (incl. SimpleQA, 4,326 items, o3-mini judge).
* See §4 for the bounded backbone conclusion required by brief §12.

### 1.5 ConsRoute `[VERIFIED-BODY]` (arXiv 2603.21237 v1 only)

* **Identity.** "ConsRoute: Consistency-Aware Adaptive Query Routing for
  Cloud–Edge–Device Large Language Models". Haoyu Qiao, Hao Zhang (corr.),
  Shanwen Mao, Siyao Cheng, Jie Liu (Harbin Institute of Technology).
  **Unrefereed preprint** (IEEEtran template placeholder), no repo.
* **Tiers.** Device Qwen3-1.7B (i5-12500H + RTX 3050), edge Qwen3-14B (A6000),
  cloud Qwen3-32B (2×A6000) (§V-A).
* **Router.** A routing prompt is appended (Eq. 1); the **frozen device LM's
  final-layer EOS prefill hidden state** (Eq. 2) feeds a ~5M-parameter MLP
  producing **one scalar consistency score** Ŝ (Eq. 7), trained with MSE (Eq. 8).
* **Labels.** Qwen3-Reranker-4B similarity (Eq. 3) + correctness (rule-based
  with reference, DeepSeek-V3 judge soft score otherwise; Eq. 4), averaged
  (Eq. 5) and fused cloud/edge with β (Eq. 6).
* **Decision.** K-means query clusters with per-cluster thresholds τ₁>τ₂ (Alg. 1,
  Eq. 11); thresholds tuned by GP Bayesian optimisation of
  U = λ₁Acc − λ₂Lat − λ₃Cost (Eq. 9–10), re-tuned online every M=200 queries
  (Alg. 2).
* **System state.** **Not a router input.** Network conditions are emulated
  good/bad link profiles (§V-A) that change observed latency, which then moves
  the tuned thresholds (Fig. 11). **No split execution, no activation bytes.**
* **Results.** Table III GSM8K 87.92% @ 20.9 ms (prompted) vs 86.44% @ 1868 ms
  (CoT) **[C]**; headline ≥95% of cloud quality at 60–65% latency **[C]**;
  figures only, no variance; no limitations section.
* **Overlap with ours.** Strongest edge/cloud LLM routing overlap in the routing
  literature: tiered deployment, latency in the objective, hidden-state router.
  **Does not overlap:** split-depth actions, measured activation transfer,
  per-model calibrated utility, live state in the per-query rule, KD.
  ConsRoute's prefill-hidden-state router is a natural **self-routing baseline**
  design (`11`).

### 1.6 Hybrid LLM `[VERIFIED-BODY]` (arXiv 2404.14618)

* **Identity.** "Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing".
  Dujian Ding, Ankur Mallick, Chi Wang, Robert Sim, Subhabrata Mukherjee, Victor
  Rühle, Laks V. S. Lakshmanan, Ahmed Hassan Awadallah. ICLR 2024. Repo
  `m365-core/hybrid_llm_routing`.
* **Router.** DeBERTa-v3-large (~300M) (§4.1). Quality = BARTScore. Three label
  types: r_det hard indicator (Eq. 1); r_prob **soft label** Pr[H ≥ 0]
  estimated from 10 samples (Eq. 2); r_trans Pr[H ≥ −t] with t chosen by Eq. 3
  (Eq. 4).
* **Cost.** Percentage of queries sent to the small model (§2.3); the paper
  explicitly does not model latency/network. Edge/cloud is motivation only
  (Fig. 2). Router latency 0.036 s (Table 2) **[C]**.
* **Limitations (§5).** Two models, no OOD.
* **Relevance.** Hybrid LLM's r_prob is an **empirical soft target from
  repeated sampling** — the clearest prior example that a router target can be
  a probability rather than a hard label *without* any teacher model. This is
  a direct non-KD competitor to soft teacher targets (`03`, `08`).

### 1.7 BEST-Route `[VERIFIED-BODY]` (arXiv v1)

* **Identity.** "BEST-Route: Adaptive LLM Routing with Test-Time Optimal
  Compute". Dujian Ding, Ankur Mallick, Shaokun Zhang, Chi Wang, Daniel
  Madrigal, Mirian Del Carmen Hipolito Garcia, Menglin Xia, Laks V. S.
  Lakshmanan, Qingyun Wu, Victor Rühle. ICML 2025, PMLR 267:13870–13884. Repo
  `microsoft/best-route-llm`.
* **Router.** Shared DeBERTa-v3-small (44M) backbone + **K×N independent sigmoid
  heads**, one per (model k, best-of-n) pair (Eq. 5). Label
  y_n(q) = Pr[R_GT(best-of-n small) ≥ R_GT(reference)] with an ArmoRM reward,
  BCE (Eq. 3–4). Cost = price × length (Alg. 1); pick the cheapest (k, n) whose
  predicted probability exceeds threshold t.
* **Results.** 60% cost reduction at <1% drop **[C]**; overhead 0.04 s + 0.58 s
  on A100 **[C]**.
* **Relevance — important for Issue A.** BEST-Route is a published
  **action-level** utility design: n changes the *output distribution*
  (best-of-n is a different inference procedure), so a separate head per (k, n)
  is justified. This is exactly the condition under which action-level utility
  is warranted (quality depends on the action, not only the model). It is the
  precedent for our **lossy** split branch, and an argument *against*
  per-depth heads when the split is exact (`01`, `02`).
* No KD wording in its method.

### 1.8 Prefill-activation router `[VERIFIED-BODY]` (arXiv 2603.20895 v3)

* **Identity.** v1 "LLM Router: Prefill is All You Need"; v2/v3 "LLM Router:
  Rethinking Routing with Prefill Activations". Varshney\*, Surla\*, Xu,
  Krishnan, Jeblick, Austin, Vaidya, Onofrio (NVIDIA). Preprint. Cite the
  version read (v3) with its title.
* **Router.** Encoder–target decoupling (§3.1): activations from an encoder LLM
  at layers L/2…L, layer chosen by a Fisher-J criterion, PCA to 100 dims, last
  token; a SharedTrunkNet MLP outputs P(correct) for each of K targets (BCE).
  Score λp̂ − (1−λ)C̃ (Eq. 1–2). Pools drawn from LLMRouterBench's frontier set
  (11 models).
* **Results.** AUC 0.856 vs 0.804 for the best semantic router (Table 3)
  **[C]**; overhead 510 ms vs 159 ms, from published TTFTs (App. I) **[C]**. No
  edge, no split.
* **Relevance.** The hidden-state/self-routing baseline (`11`), and a
  per-**model** P(correct) design with an additive cost term — the same
  model-level shape as hypothesis H-A.

### 1.9 Arch-Router `[VERIFIED-BODY]` (arXiv 2506.16655 v1)

* "Arch-Router: Aligning LLM Routing with Human Preferences". Co Tran, Salman
  Paracha, Adil Hafeez, Shuguang Chen (Katanemo). Qwen2.5-1.5B fully fine-tuned
  to **generate a policy identifier** from user-defined domain/action policies.
  No routing head and no quality prediction; 51 ms on L40S, 93.17% **[C]**
  (App. B, Table 9). Relevance: generative-router baseline option only;
  preference *policies*, not utility.

### 1.10 IRT-Router `[VERIFIED-BODY]` (arXiv 2506.01048)

* "IRT-Router: Effective and Interpretable Multi-LLM Routing via Item Response
  Theory". Wei Song, Zhenya Huang, Cheng Cheng, Weibo Gao, Bihan Xu, GuanHao
  Zhao, Fei Wang, Runze Wu. ACL 2025 (main, per arXiv comment). Repo
  `Mercidaiha/IRT-Router`.
* bert-base-uncased embeds queries **and textual LLM profiles**;
  P̂ = σ(aᵀθ_M − b) (Eq. 4–5), BCE; score S = αP̂ − βC (Eq. 1); 20 LLMs, 8 ID +
  4 OOD datasets.
* **Relevance.** A per-model calibrated-probability-shaped utility where the
  **model is an input** (via a profile embedding θ_M) rather than a head — the
  architecture family that would be needed for genuine zero/few-shot pool
  expansion (Issue B, `01`, `15`).

---

## 2. Cross-paper comparison

| Work | Unit of utility | Target | Encoder | Models enter as | Cost term | Live system state | Split / partition | KD (in the Hinton sense) |
|---|---|---|---|---|---|---|---|---|
| RouteLLM | strong-vs-weak pair | P(win_strong), hard prefs | BERT-base / Llama-3-8B / MF / SW | fixed pair | % strong calls | no | no | no (judge prefs) |
| RouterDC | **model** | softmax over models from correctness | mDeBERTaV3-base | learned embedding table | App. only | no | no | no |
| HyDRA | **capability dimension** | requirement r_k (judge Δ) | ModernBERT-base | static YAML profiles | cheapest eligible | health veto only | no | no ("distills" in Limitations) |
| LLMRouterBench | (benchmark) | per-model correctness / score | many | — | $ cost, approx. latency | no | no | — |
| ConsRoute | single scalar (cloud–edge consistency) | MSE on fused similarity+correctness | frozen device-LM hidden state + MLP | 3 fixed tiers | λ-weighted latency/cost in threshold tuning | no (emulated links move thresholds offline/online) | no | no |
| Hybrid LLM | pair | hard / sampled-soft / transformed | DeBERTa-v3-large | fixed pair | % small calls | no | no | no (soft via sampling) |
| BEST-Route | **action** (model × best-of-n) | Pr[reward ≥ ref], BCE | DeBERTa-v3-small | heads per (k, n) | price × length | no | no | no |
| Prefill router | **model** | P(correct), BCE | encoder-LLM activations + MLP | heads per target | λ-weighted normalised cost | no | no | no |
| Arch-Router | policy | generated policy id | Qwen2.5-1.5B (generative) | policy text | — | no | no | no |
| IRT-Router | **model** (as input) | P̂ = σ(aᵀθ_M − b), BCE | bert-base + profile text | profile embedding | αP̂ − βC | no | no | no |
| **Ours (v3, proposed)** | **model** under exact split; model+depth correction under lossy split (`01`/`02`) | calibrated E[S] / P(pass) (`08`) | micro-encoder (`07`) | heads per model (initial) | measured C(a\|s) (`09`) | **yes, at decision time** | **yes, Split(d) actions** | **investigated, falsifiable** (`03`) |

Observation `[PROPOSED]`: **none of the ten body-read routing papers combines
query-conditioned model utility with live network/system state at decision time
or with split-depth actions.** This is a bounded-search statement over these ten
papers only; the systems literature (where split-point selection lives) is the
real test and is in `06`.

---

## 3. HyDRA overlap — corrected (brief §11)

**What HyDRA predicts.** Four per-query **capability requirement** scores
(how much reasoning / code generation / debugging / tool use the query needs),
supervised by the judge-scored gap between a cheap and a strong model's answer.

**How model profiles enter.** Each model has a static, benchmark-derived
capability vector. The decision is a cheapest-eligible rule under a weighted
shortfall threshold — not an argmax over learned model utilities.

**Where it overlaps with ours.**
* ModernBERT-base fine-tuned encoder with **independent sigmoid heads** and an
  INT8 CPU deployment target — our backbone choice and output nonlinearity are
  therefore **not novel** and must not be presented as such.
* A cost-aware selection rule on top of a query-only learned predictor.
* Pool change by editing model metadata rather than retraining the encoder.

**Where it differs.**
* Heads are **capability dimensions**, not models or actions. HyDRA never
  predicts P(success | q, M); model quality is inferred by comparing predicted
  requirements to profiles that were never fit to routing outcomes.
* No live system state, no split/partition actions, no activation-transfer cost,
  no edge/cloud execution — HyDRA routes between cloud API models.
* No distillation into a smaller student (the judge provides training targets).

**What it invalidates as novelty.** (i) "Small fine-tuned ModernBERT router with
independent sigmoid heads" as a contribution. (ii) "Adding a model without
retraining the encoder" as a new capability — HyDRA already claims this via
profiles **[AUTHOR-CLAIM]**, and IRT-Router already conditions on model
profiles.

**What it does NOT invalidate.** Model-level calibrated utility fused with
measured runtime cost over edge / split / remote execution actions; KD as an
investigated optimisation; the split-equivalence (E0) treatment.

**Correction to v2.** v2 `17` §1.4 ("4-head sigmoid utility output") is
**wrong**; v2 `01` §2.4 ("capability heads") is correct. The v2 downgrade of our
per-action heads "because HyDRA already has them" was based on a false
equivalence; the correct downgrade is of the *encoder + sigmoid head* design,
not of the utility semantics.

---

## 4. LLMRouterBench — bounded conclusion (brief §12)

| Item | What the body shows |
|---|---|
| Statement | Abstract: "backbone embedding models have limited impact"; §4.2.1: "the embedding models have consistently little differences across routing methods". |
| Tested backbones | **Frozen** gte-Qwen2-7B-instruct (default) vs nli-bert-base vs all-MiniLM-L6-v2 (App., Table 10). |
| Tested routers | Only the **embedding-consuming** routers GraphRouter, EmbedLLM and Avengers in that ablation. |
| Pool / datasets | Our reading of Table 10's context: the performance pool (20 ~7B models, 15 datasets). The paper does not restate the pool next to the table — `[OPEN]`, inferred. |
| Metric | Average accuracy; spread ≤ 2.2 points; **no significance test**. |
| Not tested | Fine-tuned encoders; ModernBERT; DeBERTa; encoder latency; edge hardware; calibration; per-model probability heads; cost-aware routing under backbone change. |
| Baselines | **No TF-IDF/kNN/LR baseline** in the body; the "simple baseline" routers fail to beat is **Best Single model**. |
| Limitations | Router coverage, 21 datasets, approximate latency. |

**Bounded use.** We may say: *"In LLMRouterBench, swapping the frozen embedding
model among three choices changed average accuracy of three embedding-based
routers by at most ≈2 points [VERIFIED-BODY]."* We may **not** say that encoder
architecture does not matter for fine-tuned routers, for calibration, or for
edge latency; nor may we cite LLMRouterBench as showing TF-IDF is competitive.
It supports treating the backbone as an **engineering decision** (`07`), not a
claim that any encoder is equivalent.

---

## 5. Consequences for v3 decisions

1. **Issue A (model vs action utility, `01`).** The literature contains both
   shapes: model-level (RouterDC, prefill router, IRT-Router) and action-level
   (BEST-Route). BEST-Route's action-level heads are justified because its
   actions change the output distribution. This supports H-A: **model-level
   under exact split, action/depth-level only if E0 shows split changes output**.
2. **Issue B (pool expansion, `01`, `15`).** True zero/few-shot expansion in the
   literature requires model **profiles as inputs** (HyDRA YAML, IRT-Router
   profile embeddings). A per-model head design cannot claim it; adding a model
   needs labelled outcomes + head training + recalibration.
3. **Issue C (system state, `09`).** No routing paper here puts live network
   state into the learned router. ConsRoute handles changing links by
   **re-tuning thresholds** (Alg. 2), not by retraining the encoder — a published
   example that semantic and systems adaptation can be separated. This is an
   accurate supporting citation for our separation, *without* claiming that an
   integrated learned router must be retrained per network change.
4. **Issue E (terminology, `04`).** RouteLLM = LLM-as-a-judge hard preference
   labels used as data augmentation. Hybrid LLM = sampled soft labels without a
   teacher. HyDRA = judge-scored regression targets. None is KD in the
   soft-target teacher→student sense.
5. **Issue F (KD controls, `03`).** Hybrid LLM's r_prob shows that **soft
   targets from repeated sampling** are a strong non-KD alternative: any KD
   gain must be compared against a student trained on multi-sample empirical
   success rates, not only on single hard outcomes.
6. **Baselines (`11`).** RouteLLM BERT classifier (code exists), RouterDC (code
   exists), BEST-Route (code exists), Hybrid LLM (code exists), prefill-activation
   router (reimplementation, ConsRoute's EOS-hidden-state MLP as a simpler
   variant), HyDRA-style capability router (no code; reimplementation only),
   Arch-Router (generative; optional).
7. **Novelty (`12`).** Survives only at the combination level (query-conditioned
   model utility × measured live-state cost × Split(d) actions), and only
   subject to `06`. Encoder choice, sigmoid heads, cost-penalised argmax and
   model-profile pool expansion are all prior art.

---

## 6. Remaining gaps

* RouteLMT: not re-read in v3 → `[VERIFIED-META]`; do not cite load-bearingly.
* HyDRA: author list differs between arXiv metadata (5) and v2 PDF (6); pick the
  cited version explicitly.
* RouteLLM: proceedings page numbers for ICLR 2025 not recorded (OpenReview has
  none); cite OpenReview ID.
* LLMRouterBench Table 10 pool attribution is inferred, not stated.
* Proceedings-PDF page locators for RouterDC, BEST-Route, Hybrid LLM, IRT-Router
  are `[OPEN]`; section/equation locators above are from the arXiv HTML.
