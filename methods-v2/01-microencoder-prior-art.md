# methods-v2 / 01 — Micro-encoder & encoder-router prior art

*Deliverable for `MICROENCODER_KD_BRIEF.md` §4 (required investigation A).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 2).*

## 0. Purpose and sourcing

The advisor has fixed the **micro-encoder** as THE proposed router backbone
(`00-meeting-decisions-lock.md`). The brief therefore stops treating encoder
routing as a candidate to be discovered and instead asks a sharper question:
**which encoder-router works already occupy this design space, and with exactly
what architecture, so that any micro-encoder contribution can be defined against
them rather than re-inventing them.**

This file **reuses** the primary-source checks already performed and logged in
the v1 research sprint — chiefly
`research/micro-encoder-investigation.md` (the "does a micro-encoder router
already exist?" search, dated 2026-09-23) and
`research/closest-prior-art.md` (18 ranked entries, each opened at its primary
location with raw copies under `research/raw/prior-art/`). It does **not**
re-run those searches; it re-tabulates them into the per-work field template the
brief §4 mandates and applies the `00` evidence discipline tags. Where a field
was **not** checked in the v1 sprint, it is marked `[OPEN]` rather than guessed.

**Evidence tags** (from `00` §Evidence discipline, aligned with
`closest-prior-art.md` §0): `[abs]` = authors' arXiv abstract claim, not
re-verified; `[body]` = read in the paper body (arXiv HTML) in the v1 sprint;
`[api]` = GitHub/HF API or ACL Anthology / arXiv metadata; `[O]` = our analysis;
`[OPEN]` = not verified, do not treat as fact.

**Headline finding (carried, [VERIFIED] against the works below).** A
"micro-encoder router" in the plain sense — a small non-generative encoder that
reads the query and emits a routing decision — is **already standard practice**,
in academic work (RouteLLM-BERT, RouterDC, BEST-Route), in production (HyDRA,
vLLM Semantic Router, ComplianceGate) and in edge–cloud settings (Pro-Router
pre-scorer, ConsRoute). Renaming an encoder-classifier a "micro-encoder" creates
**no novelty**. This constrains the whole sprint: the contribution must lie in
the **distillation**, the **Split-LLM action/cost integration**, or the **edge
measurement**, not in "we use a small encoder." (feeds `11-novelty-stress-test`.)

---

## 1. Scope of the review and what "encoder router" means here

The brief names specific works to check: RouteLLM, RouterDC, BEST-Route, HyDRA,
LLMRouterBench, RouteLMT, ConsRoute, Arch-Router (generative comparison only),
PRISM where relevant, "any newer encoder-router work directly relevant." Each is
covered below. Two scoping notes:

- **In scope** = a *small, discriminative* model (encoder + head, or encoder +
  similarity lookup) that predicts a routing target before generation. This is
  the family the advisor approved.
- **Comparison only** = *generative* routers (Arch-Router) and *LLM-as-router*
  designs (ICL-Router). They are listed as the generative baseline, not as the
  proposed family.
- **PRISM:** the brief lists "PRISM where relevant." No work under this name was
  opened or verified in the v1 sprint. It is therefore `[OPEN]` — see §5. We do
  **not** fabricate an entry.

---

## 2. Per-work records (brief §4 field template)

Field order per work: **title · authors · venue/year · ID/URL · code · router
architecture · parameter size · input representation · output/target · training
labels · training loss · calibration · model-pool adaptability · runtime/system
integration · edge deployment · Split-LLM relationship · KD used? · CL used? ·
what is actually novel.** Unchecked fields are `[OPEN]`.

### 2.1 RouteLLM — *Learning to Route LLMs from Preference Data*
- **Authors.** I. Ong, A. Almahairi, V. Wu, W.-L. Chiang, T. Wu, J. E. Gonzalez,
  M. W. Kadous, I. Stoica. [api]
- **Venue / year.** arXiv 2406.18665 (2024-06); **ICLR 2025** poster (ICLR
  proceedings/poster page found by search; OpenReview returned 403). [api]
- **ID / URL.** arXiv:2406.18665 · https://arxiv.org/abs/2406.18665
- **Code.** `lm-sys/RouteLLM`, Apache-2.0, last push 2024-08-10. [api]
- **Router architecture.** Four interchangeable routers: a **BERT classifier**,
  **matrix factorisation** (`mf`, the README's recommended default),
  **similarity-weighted (SW) ranking**, and a **causal-LLM classifier**. [abs;
  variants per `research/micro-encoder-investigation.md` §2]
- **Parameter size.** BERT-base class (~110M) for the encoder variant; Pro-Router
  reports the released RouteLLM router as **278M** [body of Pro-Router]. `[OPEN]`
  which exact checkpoint.
- **Input representation.** Raw query text. [abs]
- **Output / target.** Binary **win-probability** of strong-vs-weak, thresholded
  at a cost-controlled operating point. [abs]
- **Training labels.** **Chatbot Arena human preference** pairs plus data
  augmentation. [abs]
- **Training loss.** `[OPEN]` (classification/ranking objective per variant; not
  re-verified in the body).
- **Calibration.** Threshold calibrated to hit a target cost level; no ECE
  reported. `[OPEN]`
- **Model-pool adaptability.** Binary strong/weak only; authors claim **transfer**
  when the model pair changes. [abs]
- **Runtime/system integration.** None — win probability vs a cost **threshold**,
  no live latency/bandwidth term. [abs]
- **Edge deployment.** No; cloud pair. [O]
- **Split-LLM.** None. [O]
- **KD used?** No. [O]  **CL used?** No. [O]
- **Actually novel [O].** The canonical learned weak/strong router from
  preference data. It is the **standard binary-routing baseline** for this sprint,
  not a micro-encoder-for-edge precedent. Manuscript numbers "2–3.6×"/"87–95%"
  (main-original L85) are **not in the abstract** and remain `[OPEN]` (claim
  audit).

### 2.2 RouterDC — *Query-Based Router by Dual Contrastive Learning*
- **Authors.** S. Chen, Z. Jiang, L. Lin, J. Kwok, Y. Zhang. [abs]
- **Venue / year.** arXiv 2409.19886; **NeurIPS 2024** (arXiv comment). [api]
- **ID / URL.** arXiv:2409.19886 · https://arxiv.org/abs/2409.19886
- **Code.** `shuhao02/RouterDC`. [api]
- **Router architecture.** **mDeBERTa-v3-base** query encoder + **learnable
  per-LLM embeddings**; route = cosine-similarity argmax over the pool. [abs]
- **Parameter size.** mDeBERTa-v3-base (~86M backbone params) + small per-LLM
  embedding table. `[OPEN]` exact head size.
- **Input representation.** Query text → encoder embedding. [abs]
- **Output / target.** Argmax model index over the LLM pool. [abs]
- **Training labels.** Per-LLM correctness/score on training queries. [abs]
- **Training loss.** **Dual contrastive** loss (sample–LLM and sample–sample). [abs]
- **Calibration.** `[OPEN]`.
- **Model-pool adaptability.** Per-LLM embeddings are learned, so adding a model
  requires learning its embedding (not zero-shot). [O]
- **Runtime/system integration.** None (semantic only). [O]
- **Edge deployment.** No. [O]  **Split-LLM.** None. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel [O].** **Contrastive** query-encoder routing with learnable
  model embeddings; reports +2.76% ID / +1.90% OOD over prior routers [abs]. This
  is the closest *encoder-with-learned-model-embeddings* precedent — directly
  relevant because a KD student could inherit this contrastive structure (feeds
  `03-kd-formulations` KD-4 representation distillation).

### 2.3 BEST-Route — *Adaptive LLM Routing with Test-Time Scaling*
- **Authors.** D. Ding, A. Mallick, S. Zhang, C. Wang, et al. [api]
- **Venue / year.** arXiv 2506.22716; **ICML 2025** (arXiv comment). [api]
- **ID / URL.** arXiv:2506.22716 · https://arxiv.org/abs/2506.22716
- **Code.** `microsoft/best-route-llm`, MIT (repo description cites this ID). [api]
- **Router architecture.** Multi-head router; search snippet says the backbone is
  **DeBERTa-v3-small** (not re-checked in the body — `[OPEN]`). [abs/O]
- **Parameter size.** DeBERTa-v3-small class (~44M backbone) if the snippet holds;
  `[OPEN]`.
- **Input representation.** Query text. [abs]
- **Output / target.** **Structured**: which model **and the number of samples**
  (best-of-n from small models). [abs]
- **Training labels.** Per-(query, model, n) outcome/quality. [O from abs]
- **Training loss / calibration.** `[OPEN]`.
- **Model-pool adaptability.** `[OPEN]`; cloud pool. [O]
- **Runtime/system integration.** Cost = model + sampling budget; no live network
  term. [abs]
- **Edge deployment.** No. [O]  **Split-LLM.** None. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel [O].** The routing **action space includes a sampling budget**
  (model × best-of-n), up to 60% cost cut at <1% drop [abs]. This is the clearest
  precedent that a router's output can be a *structured action*, which matters for
  our Split-depth action space (`06-proposed-method`, `09-split-llm-integration`).

### 2.4 HyDRA — *Hybrid Dynamic Routing Architecture for Heterogeneous LLM Pools*
- **Authors.** A. Garg, S. S. Roy, J. Jang, F. Brancasi, S. Fu. [abs]
- **Venue / year.** arXiv 2605.17106 (v2 2026-06-12), preprint; **deployed in
  GitHub Copilot VS Code Chat auto-mode** (authors' statement). [abs]
- **ID / URL.** arXiv:2605.17106 · https://arxiv.org/abs/2605.17106
- **Code.** Not found in abstract/body. `[OPEN]`
- **Router architecture.** **ModernBERT-base, ONNX dynamic INT8**, **4 independent
  sigmoid capability heads** (reasoning, code-gen, debugging, tool-use), then
  **shortfall matching** against config-defined model profiles. [abs][body]
- **Parameter size.** **149M** (ModernBERT-base). [abs]
- **Input representation.** Query text. [abs]
- **Output / target.** A **capability vector**, matched against model profiles →
  route. [abs]
- **Training labels.** **50,159 LLM-judge labels** from de-identified Copilot
  telemetry. [abs]
- **Training loss.** Per-head sigmoid (multi-label). [body/O]
- **Calibration.** `[OPEN]` (no ECE reported in what was read).
- **Model-pool adaptability.** **Zero retraining** when the catalogue changes
  (profiles are config, not weights). [abs]
- **Runtime/system integration.** Capability-shortfall + cost; no live
  network/RTT term. [abs]
- **Edge deployment.** **CPU-grade**: 86 ms median CPU in production [abs]; figure
  gives 55 ms P50 / 120 ms P99 ONNX-INT8 CPU [body] — **two figures unreconciled**
  `[OPEN]`. Not an on-*device* SLM setting though. [O]
- **Split-LLM.** None. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel [O].** The strongest **production** evidence that a
  **lightweight CPU encoder with a structured multi-head output and
  no-retraining pool updates** already works. It **pre-empts** the manuscript's
  "lightweight" (C1) and "without costly retraining" (C3) claims. Any micro-encoder
  novelty must be stated relative to HyDRA. This is the single most important
  "already occupied" datapoint for `11-novelty-stress-test`.

### 2.5 LLMRouterBench — unified routing benchmark
- **Authors.** H. Li, Y. Zhang, Z. Guo, C. Wang, …, S. Hu. [api]
- **Venue / year.** arXiv 2601.07206; **Findings of ACL 2026, pp. 37733–37754**. [api]
- **ID / URL.** arXiv:2601.07206 · ACL Anthology 2026.findings-acl.* [api]
- **Code / data.** `ynulihao/LLMRouterBench` (no SPDX license via API — check by
  hand). [api]
- **Architecture.** Not a router — a **benchmark**: 400K+ instances, 21 datasets,
  33 models, 10 baselines. [abs]
- **Key findings [abs].** Under unified evaluation **many routers perform
  similarly**; several recent and commercial routers **fail to beat a simple
  baseline**; the oracle gap is driven by **model-recall failures**; **backbone
  embedding choice has limited impact**.
- **Edge / Split / KD / CL.** None. [O]
- **Relevance [O].** Sets the **evaluation bar** for the whole sprint: any claimed
  gain must clear its simple baseline under its protocol, with reported variance.
  Its "embedding backbone has limited impact" finding **directly weakens** any
  contribution resting on the encoder *architecture* — which is exactly why this
  sprint must anchor novelty on **KD + Split-LLM cost**, not on the encoder.
  Supplies the manuscript's pre-computed SimpleQA data (main-original L205).
  Whether its 33 models include the manuscript's edge pool is `[OPEN]`.

### 2.6 RouteLMT — *Learned Sample Routing for Hybrid LLM Translation Deployment*
- **Authors.** Y. Luo, H. Liu, D. Lin, K. Chang, C. Wang, B. Li, Q. Du, T. Xiao,
  J. Zhu (NiuTrans / Northeastern Univ.). [api]
- **Venue / year.** arXiv 2604.22520; **ACL 2026 Industry Track, pp. 1886–1897**
  (ACL Anthology 2026.acl-industry.129). [api]
- **ID / URL.** arXiv:2604.22520
- **Code.** Not found (NiuTrans/LMT is the translator, not the router). [api]
- **Router architecture.** **In-model** router that probes the **small
  translator's prompt-token representation** — no external model, no hypothesis
  decoding. [abs]
- **Parameter size.** Probe head only (shares the translator). `[OPEN]` size.
- **Input representation.** The small model's **own prompt representation**
  (hidden state), not a separate encoder. [abs]
- **Output / target.** **Marginal gain** of calling the large model. [abs]
- **Training labels.** Realised marginal gain (large − small quality). [O from abs]
- **Training loss.** Budget-allocation objective with a **guarded** variant for
  regression risk. [abs]
- **Calibration.** Guarded regression (risk control). [abs]
- **Model-pool adaptability.** Small-vs-large pair (translation). [O]
- **Runtime/system integration.** Budget allocation; no live network term. [O]
- **Edge deployment.** Hybrid deployment framing; no device measurement. [O]
- **Split-LLM.** None. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel [O].** The **marginal-gain target** is a better-justified
  routing label than the manuscript's absolute "suitability" f_θ(q,M_k) (Eq. 3),
  and it is a **hidden-state self-probe** (same family as Candidate C, now a
  baseline). Feeds `07-training-labels` (what the student should predict) and the
  baseline plan in `10-model-pool-and-baselines`.

### 2.7 ConsRoute — *Consistency-Aware Adaptive Query Routing for Cloud-Edge-Device LLMs*
- **Authors.** H. Qiao, H. Zhang, S. Mao, S. Cheng, J. Liu (Harbin Inst. of Tech.). [api]
- **Venue / year.** arXiv 2603.21237 (2026-03-22), preprint, no venue in comments. [api]
- **ID / URL.** arXiv:2603.21237
- **Code.** No link found in abstract/HTML. `[OPEN]`
- **Router architecture.** Short prompt appended to the query; router reads the
  **device LM's final-layer prefill hidden state of the last token** → **small
  MLP** consistency predictor; queries **clustered**, Bayesian-optimised
  **per-cluster thresholds** with online adaptation. [abs][body]
- **Parameter size.** Small MLP on top of the DLM hidden state; exact size not
  reported `[OPEN]`. [O]
- **Input representation.** **Device-SLM prefill hidden state** (not a separate
  encoder). [body]
- **Output / target.** Route among **3 tiers** — device LM (<4B, Qwen3-1.7B),
  edge LM (7–30B, Qwen3-14B), cloud LM (Qwen3-32B). [body]
- **Training labels.** **Reranker-scored** (Qwen3-Reranker-4B) semantic
  consistency between tiers' responses. [abs][body]
- **Training loss.** `[OPEN]` (consistency prediction).
- **Calibration.** Per-cluster thresholds via Bayesian optimisation + online
  adaptation. [body] No ECE reported. [O]
- **Model-pool adaptability.** Thresholds adapt online; adding a tier not
  evaluated. [O]
- **Runtime/system integration.** Optimises **quality + end-to-end latency +
  cost**; **network conditions emulated** (good/bad bandwidth + one-way delay
  profiles) but bandwidth is a *condition*, **not a router input**. [body]
- **Edge deployment.** **Real device-class hardware**: i5-12500H + RTX 3050
  (device), RTX A6000 (edge), 2× A6000 (cloud). [body]
- **Split-LLM.** **None** — all tiers run full models; no activation transfer. [O]
- **KD?** No. **CL?** Online threshold adaptation only, not CL. [O]
- **Actually novel [O].** The **closest edge-side, pre-generation, multi-tier
  SLM-vs-larger router** found. It **pre-empts interpretation "route on the SLM's
  own prefill state"** and gives direct evidence (its Table III) that **generated
  tier choices are slower and no more accurate than a hidden-state probe** (87.92%
  @ 20.9 ms vs 85.79% @ 36.2 ms / 86.44% @ 1868 ms CoT). Crucial gap for us: it
  has **no Split-LLM tier and no activation-transfer cost** — that is where our
  action space differs.

### 2.8 Arch-Router — *generative router, comparison only*
- **Authors.** C. Tran, S. Paracha, A. Hafeez, S. Chen (Katanemo). [api]
- **Venue / year.** arXiv 2506.16655 (2025-06), preprint. [api]
- **ID / URL.** arXiv:2506.16655
- **Code.** HF `katanemo/Arch-Router-1.5B` (license "other"); serving repo
  `katanemo/plano` (ex-archgw, Apache-2.0). [api]
- **Router architecture.** **Generative 1.5B** model (base Qwen2.5-1.5B-Instruct,
  HF `pipeline_tag=text-generation`). [api]
- **Output / target.** **Generated** route/policy name (user-defined
  domain/action). [abs]
- **Model-pool adaptability.** New models added **without retraining**. [abs]
- **Runtime/system integration / edge / Split-LLM.** None; not cost-aware. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel / role [O].** The main **generative small-router comparison**
  (brief: "Arch-Router only as a generative comparison"). **Not** a micro-encoder.
  **Claim-audit flag:** main-original L317 says the authors will "fine-tune its
  routing head," but the checkpoint is a causal LM with **no separate head** — the
  baseline description must be rewritten. Manuscript "93.17%"/"28×" (L85) are
  `[OPEN]` (not in abstract).

### 2.9 Prefill-activation router — *Rethinking Routing with Prefill Activations*
- **Authors.** T. Varshney, A. Surla, M. Xu, G. V. Krishnan, M. Jeblick, D. Austin,
  N. Vaidya, D. Onofrio. [api]
- **Venue / year.** arXiv 2603.20895 (v1 2026-03-21, v2 2026-08-11), preprint. [api]
- **ID / URL.** arXiv:2603.20895
- **Code.** Not found. `[OPEN]`
- **Router architecture.** **"Encoder-Target Decoupling"**: residual-stream
  **prefill activations** of an open-weight **"Encoder" LLM** (layers chosen by
  Fisher separability) → **SharedTrunkNet MLP** → per-model correctness. [abs]
- **Output / target.** **Per-model correctness probabilities**, incl. for closed
  target models. [abs]
- **Input representation.** Full-LLM prefill activations (the "Encoder" is a full
  LLM, not a tiny model). [abs]
- **Runtime/system/edge/Split-LLM.** Cloud-side, no edge budget, no Split. [O]
- **KD?** No. **CL?** No. [O]
- **Actually novel / role [O].** The nearest **terminological** neighbour to
  "micro-encoder" (it literally calls its feature producer an "Encoder") and the
  precedent for **per-model correctness probability** targets. Its "Encoder" is a
  full LLM, so our *small* encoder differs — but the **target design** (calibrated
  per-model success prob.) directly informs `07-training-labels` option E.

### 2.10 Secondary encoder-router / classifier precedents (tabular)

All confirmed in `research/micro-encoder-investigation.md` §2 (opened at primary
location). Listed to show the design space is saturated; fields abbreviated.

| Work | ID | Backbone / size | Output | Edge? | Split? | KD? | Novel point [O] |
|---|---|---|---|---|---|---|---|
| **vLLM Semantic Router** | 2603.12646 | ModernBERT-class, ONNX + CK FlashAttn on MI300X | safety/domain/PII labels → path | co-located w/ vLLM | no | no | engineering encoder-classifier routers without a dedicated GPU |
| **ComplianceGate** | 2606.31163 | encoder classifier | complexity×sensitivity → tier+geo | serving-side | no | no | 99.2% acc, **7 ms** overhead (600-query eval — small) |
| **Pro-Router** | 2608.28726 | lightweight **prompt pre-scorer** + token-level verifier | ship vs escalate (edge↔72B cloud, multimodal) | "edge"=A10G GPU tier, not device | no | no | 2-stage pre+post-gen; selective-prediction threshold; ">10×" routing speed; **public Apache-2.0 baseline** |
| **Dynamic Quality-Latency Routing** (Bao et al.) | 2508.11291 | "lightweight BERT router inspired by RouteLLM" | score **fused with explicit wireless+compute latency model** + KV-switch cost | mobile SLM↔edge-server LLM (**simulated**) | no | no | closest to **C2 as written**: explicit comm+compute latency term |
| **CSCR** | 2508.12491 | contrastive encoder + **FAISS k-NN** | cheapest accurate expert in cost bands | no | no | no | "**no retraining when pool changes**", "microsecond latency" — pre-empts C3 |
| **IRT-Router** | 2506.01048 | IRT ability/difficulty model | perf-cost route (20 LLMs, 12 datasets) | no | no | no | interpretable query-difficulty signal (ACL 2025 main) |
| **ICL-Router** | 2510.09719 | **LLM-based** (in-context model profiles) | per-model correctness; add models w/o retrain | no | no | no | opposite of lightweight; AAAI 2026 |
| **Hybrid LLM** (Ding et al.) | 2404.14618 | router predicting query difficulty vs quality level | large-call fraction, test-time tunable | edge-small vs cloud-large *framing* | no | no | **ICLR 2024** peer-reviewed statement of the Eq. 2 trade-off; **manuscript citation gap** |
| **tinyrouter** (OSS, low weight) | GitHub `harrrshall/tinyrouter` | frozen **0.6B encoder** + **~10K-param head** (sep-CMA-ES) | model+role | — | no | no | **honest negative**: ties random routing (0.792 vs 0.792) when oracle headroom is small → oracle-headroom check mandatory |

---

## 3. Cross-cutting answers the brief §4 asks for

[VERIFIED against the entries above unless tagged otherwise.]

1. **Does encoder/micro-encoder routing already exist?** **Yes, saturated.**
   Academic (RouteLLM-BERT, RouterDC, BEST-Route, IRT-Router), production (HyDRA,
   vLLM-SR, ComplianceGate) and edge–cloud (ConsRoute, Pro-Router, Bao et al.).
   [VERIFIED]
2. **Is "lightweight / CPU / sub-10 ms" already claimed?** Yes — ComplianceGate
   (7 ms), HyDRA (55–86 ms CPU), CSCR ("microsecond"). [VERIFIED]
3. **Is "no retraining when the pool changes" already claimed?** Yes — HyDRA,
   CSCR, ICL-Router, Arch-Router. [VERIFIED] → C3 is not a standalone contribution.
4. **Is communication/latency-aware routing cost already done?** Yes — Bao et al.
   (explicit wireless+compute latency + KV-switch) and ConsRoute (network-condition
   evaluation). [VERIFIED] → C2's novelty depends entirely on the **Split-LLM**
   path.
5. **Does any encoder router use knowledge distillation?** **None found** in this
   set. [VERIFIED as "not found" within the bounded v1 search] → see
   `02-kd-prior-art.md` for the dedicated KD search; this is the main open lane.
6. **Does any use continual learning?** **None** (ConsRoute has online threshold
   adaptation, not CL). [VERIFIED] → consistent with keeping CL as a journal
   extension.
7. **Does any include a Split-LLM action with activation transfer?** **None of the
   routers.** Split-inference works exist (`closest-prior-art.md` §2.11, §3) but
   they **optimise the split, they do not route**. [VERIFIED as "not found", but
   bounded] → the **candidate residual gap** (feeds `11-novelty-stress-test` N4).
8. **Generative vs discriminative router — settled?** ConsRoute Table III is
   direct (one-dataset) evidence that a generated tier choice is **slower and no
   more accurate** than a hidden-state probe. [body] → supports keeping the router
   discriminative and Jacobi non-required (`00` decision 10).

---

## 4. What this fixes in the manuscript (carry to claim audit / blue text)

From `research/micro-encoder-investigation.md` §6 and `closest-prior-art.md` §5,
re-affirmed:

- **"Unlike existing methods that rely on heavy models" (main-original L40, L61)**
  is contradicted by RouteLLM-BERT, RouterDC, HyDRA, ComplianceGate — all
  lightweight encoders. Must be softened. [VERIFIED]
- **"Without requiring costly retraining" (L40)** is pre-empted by CSCR and HyDRA.
  Must be narrowed. [VERIFIED]
- **Arch-Router baseline (L317)** "fine-tune its routing head" — wrong, it is a
  causal LM. Must be rewritten. [VERIFIED api]
- **Missing-but-necessary citations:** Hybrid LLM (ICLR 2024), ConsRoute, Bao et
  al. 2508.11291, HyDRA, CSCR — all occupy claimed-novel ground and must be cited.
  (Carried to `17-verified-references.md` / `method-references.bib`.)

---

## 5. Open items and search limits (do not overstate "not found")

- **PRISM** (brief §4): **no verified entry** — not opened in the v1 sprint.
  `[OPEN]`. A targeted search is owed before any PRISM claim is made; absent that,
  it must not appear in references. Do not fabricate.
- **The "no Split-LLM router" residual-gap statement is bounded**, not systematic:
  it rests on the v1 arXiv-centric searches. `closest-prior-art.md` §6 notes
  arXiv under-covers IEEE (INFOCOM, TMC, JSAC) and ACM (MobiCom, SenSys, MobiSys);
  a targeted "routing × split inference / partial offloading" search in those
  venues is still owed. `[OPEN]`
- **Unverified fields** flagged `[OPEN]` above (RouteLLM exact checkpoint size,
  BEST-Route backbone, HyDRA code + reconciled latency, ConsRoute router size/
  calibration/code, loss functions for several works) must be checked in the
  paper bodies before any of these become load-bearing in the blue text.
- **All numbers here are authors' claims**; nothing was reproduced in this project.
- **Semantic Scholar / DBLP full-text and non-English venues were not searched**
  (S2 API returned HTTP 429 in the v1 attempt). Absence of evidence is bounded.

---

## 6. Hand-off

- `02-kd-prior-art.md` — the dedicated KD-for-routing search (the one lane left
  genuinely open by this review: **no encoder router here uses KD**).
- `06-proposed-method.md` — must state the proposed micro-encoder **against**
  HyDRA/RouterDC/ConsRoute, not as if the family were new.
- `10-model-pool-and-baselines.md` — baseline set is largely populated by this
  file: TF-IDF/LogReg, RouteLLM, a ModernBERT/DeBERTa classifier, ConsRoute-style
  hidden-state probe (Candidate C), Arch-Router (generative), oracle upper bound.
- `11-novelty-stress-test.md` — every "already occupied" row above is an input;
  the only unoccupied lanes found are **KD-for-routing** and **Split-LLM action +
  measured activation cost**.
- `17-verified-references.md` / `method-references.bib` — IDs, venues and repos in
  §2 are the verified-source list; `[OPEN]` fields must not be emitted as fact.
