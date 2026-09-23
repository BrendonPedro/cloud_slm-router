# Deliverable 3 — Closest prior art

*Prepared 2026-09-23 (gnhf iteration 5). Subject: "Tiny-LM with Jacobi-Forced
Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs"
(`source/main-original.tex`, unchanged; SHA-256 06f5f9d7…07cf6).*

## 0. How to read this document

**What was checked.** Every entry below was opened at its primary location and
a raw copy saved under `research/raw/prior-art/` (see `fetch-log.txt` there for URL,
byte count and UTC time):

- arXiv abstract pages (`abs_<id>.html`). Title, authors, date and the arXiv
  "Comments" field were extracted to `abstracts.txt`;
- full arXiv HTML for the four entries closest to the edge-to-cloud setting
  (`html_2603.21237`, `html_2608.28726`, `html_2605.17106`, `html_2508.11291`, with
  stripped `.txt` versions). Anything reported below *from the paper body* comes
  from these files;
- ACL Anthology pages for IRT-Router, RouteLMT and LLMRouterBench (venue and page numbers);
- GitHub REST API for repo existence, SPDX license and last push (`github-api.txt`).

**Evidence tags.** Every result is tagged by where it came from:

| Tag | Meaning |
|---|---|
| **[abs]** | Stated in the paper's own arXiv abstract. It is the authors' claim, **not re-verified by us** |
| **[body]** | Read in the paper body (arXiv HTML) this iteration. Still the authors' claim, not reproduced |
| **[api]** | Taken from the GitHub/HF API or the ACL Anthology / arXiv metadata |
| **[O]** | Our analysis or inference, not a fact about the source |

**Nothing in this document was reproduced by us.** Every number is a number the
authors report. None of these systems has been run in this project.

**Ranking criterion [O].** Closeness to the proposal is judged on the setting the
manuscript actually formulates (§III, L136–189, Eq. 1–3): a small router **on the edge**
that decides, **per query and before generation**, whether an **edge SLM** or a
**cloud LLM / Split-LLM** answers, trading quality against a cost that "may
include computation, communication, and latency" (L165). Title terms that the body
never defines ("Jacobi-Forced", "Micro-Encoder"; see deliverables 6 and 7) were not
used for ranking.

**How to read "overlap" and "difference".** "Overlap" lists what the prior work
already does from the manuscript's contribution list C1–C4 (L60–67; see
`research/problem-as-written.md` §4). "Difference" lists only differences that
could matter to a reviewer. It does not list differences of wording.

---

## 1. Summary table (ranked by closeness, most similar first)

| # | Work | Venue / status | Edge SLM ↔ cloud? | Router on device? | Pre-generation? | Cost terms | Code |
|---|---|---|---|---|---|---|---|
| 1 | **ConsRoute** (2603.21237) | preprint 2026-03 | **Yes, device–edge–cloud, 3 tiers** | **Yes** (MLP on the device SLM's prefill state) | Yes | quality, latency, cost, network conditions | not found |
| 2 | **Dynamic Quality-Latency Aware Routing** (Bao et al., 2508.11291) | IEEE/CIC ICCC 2025 workshop | **Yes** (mobile SLM ↔ edge-server LLM) | BERT router; placement not confirmed | Yes | quality + **explicit wireless communication + compute latency model**, KV-switch cost | not found |
| 3 | **Pro-Router** (2608.28726) | preprint 2026-08 | Yes, edge and cloud *tiers* (edge tier = A10G GPU nodes) | pre-scorer + verifier on the serving side | two-stage: pre-gen **and** post-gen | accuracy, routing speed, throughput | `xinyuangui2/pro-router`, Apache-2.0 [api] |
| 4 | **Hybrid LLM** (Ding et al., 2404.14618) | **ICLR 2024** | Yes, framed as edge-small vs cloud-large | not specified in the abstract | Yes | quality vs large-model call fraction, tunable at test time | not checked |
| 5 | **SWARM-LLM** (2606.14711) | preprint 2026-04 | Yes (edge SLM swarm + 70B cloud via API) | Yes (lightweight uncertainty/safety estimates) | mixed | accuracy, cloud-call fraction, latency | `mdahshan/swarm_llm`, Apache-2.0 [api] |
| 6 | **RouteLMT** (2604.22520) | **ACL 2026 Industry**, pp. 1886–1897 [api] | small vs large translator (hybrid deployment) | **in-model** probe on the small model's prompt representation | Yes | marginal gain under a budget | not found (NiuTrans/LMT is the translator, not the router) |
| 7 | **Prefill-activation router** (2603.20895) | preprint 2026-03, v2 2026-08 | no (open "Encoder" → closed targets) | n/a | Yes | correctness per model, cost | not found |
| 8 | **HyDRA** (2605.17106) | preprint v2 2026-06, **production (GitHub Copilot)** | no (cloud model pool) | CPU encoder at the serving side | Yes | capability shortfall, cost | not found |
| 9 | **RouteLLM** (2406.18665) | **ICLR 2025** [ICLR proceedings page] | binary strong/weak, cloud | n/a (BERT, mf, SW-ranking and causal-LLM variants) | Yes | win probability vs cost threshold | `lm-sys/RouteLLM`, Apache-2.0 [api] |
| 10 | **AutoMix** (2310.12963) | **NeurIPS 2024** | small → large cascade | self-verification by the small LM | **post**-generation | cost vs performance (POMDP) | not checked |
| 11 | **Privacy-aware split inference + lookahead decoding** (Cunningham, 2602.16760) | preprint 2026-02, single author | **Split-LLM over WAN** (local GPU ↔ cloud GPU) | **no router** | n/a | throughput, privacy (inversion attack), RTT | not found |
| 12 | **CSCR** (2508.12491) | preprint 2025-08 | no (dynamic cloud pool) | n/a | Yes | cheapest accurate expert within cost bands | not checked |
| 13 | **ICL-Router** (2510.09719) | **AAAI 2026** | no | n/a (LLM-based router) | Yes | per-model correctness | `lalalamdbf/ICL-Router`, no SPDX license [api] |
| 14 | **IRT-Router** (2506.01048) | **ACL 2025 main**, pp. 15629–15644 [api] | no | n/a | Yes | performance-cost via IRT ability/difficulty | `Mercidaiha/IRT-Router`, no SPDX license [api] |
| 15 | **Arch-Router** (2506.16655) | preprint 2025-06 | no | n/a (**generative** 1.5B) | Yes | human preference match (domain/action) | HF `katanemo/Arch-Router-1.5B` (license "other"); serving repo moved (`katanemo/archgw` → 301) [api] |
| 16 | **BEST-Route** (2506.22716) | **ICML 2025** | no | n/a | Yes | model **and** number of samples, cost | `microsoft/best-route-llm`, MIT; README links this arXiv ID [api] |
| 17 | **LLMRouterBench** (2601.07206) | **Findings of ACL 2026**, pp. 37733–37754 [api] | benchmark, not a router | — | — | performance-oriented and performance-cost metrics; "latency-aware analysis" | `ynulihao/LLMRouterBench`, no SPDX license [api] |
| 18 | **Jev / System One** (TypeSafe) | proprietary API, launched 2026-09-15 | no (cloud API only) | no | Yes | vendor-claimed latency/cost | API only; see deliverable 5 |

"not found" means the abstract and the fetched HTML gave no code link and we did
not search further. It does **not** mean the authors have released no code.

---

## 2. Detailed entries

### 2.1 ConsRoute — *Consistency-Aware Adaptive Query Routing for Cloud-Edge-Device LLMs*
- **Record.** H. Qiao, H. Zhang, S. Mao, S. Cheng, J. Liu (Harbin Institute of
  Technology). arXiv 2603.21237, submitted 2026-03-22, preprint, no venue in the
  arXiv comments. [api]
- **Problem.** Per-query routing across three tiers: a device LM (DLM, <4B, e.g.
  Qwen3-1.7B), an edge LM (ELM, 7–30B, e.g. Qwen3-14B) and a cloud LM (CLM,
  e.g. Qwen3-32B). [body]
- **Router architecture.** A short prompt is appended to the query. The router
  takes the **DLM's final-layer prefill hidden state of the last token** and feeds
  it to a **small MLP** consistency predictor. Queries are clustered, and Bayesian
  optimisation learns **cluster-specific thresholds**, with online threshold
  adaptation. Training labels are reranker-scored (Qwen3-Reranker-4B) semantic
  consistency between tiers' responses. [abs][body]
- **Local/cloud setup.** Device: Intel i5-12500H + RTX 3050 (Qwen3-1.7B). Edge:
  1× RTX A6000 (Qwen3-14B). Cloud: 2× RTX A6000 (Qwen3-32B). **Network conditions
  are emulated** ("good": device→edge 10,000/5,000 Kbps with 40/20 ms one-way;
  device→cloud 8,000/4,000 Kbps with 80/40 ms; plus a "bad" profile). A
  cross-family configuration is also reported. [body]
- **Optimisation targets.** Quality, end-to-end latency and inference cost,
  through per-cluster thresholds. [abs]
- **Datasets / metrics.** Trained on RouterBench (36.5K queries, 8 datasets).
  Main results on MMLU, GSM8K, HumanEval and MT-Bench (GPT-4o judge). Metrics are
  accuracy relative to CLM-only, end-to-end latency, cost, router latency and
  device-side overhead. [body]
- **Results (authors' claims).** "near-cloud performance (≥95%) while reducing
  end-to-end latency and inference cost by nearly 40%" [abs]. In Table III (GSM8K),
  asking the DLM *explicitly* to choose a tier reaches 85.79% at 36.2 ms router
  latency, or 86.44% at 1868.2 ms with CoT. The implicit hidden-state router
  reaches 87.92% at 20.9 ms. [body]
- **Code.** No link found in the abstract or HTML.
- **Overlap with the proposal [O].** Very high. It is an edge-side lightweight
  router for SLM-vs-larger-model selection before generation (C1). It is aware of
  latency, cost and network conditions (C2, partly). Its threshold adaptation
  covers part of C3. It also **pre-empts interpretation P2** from deliverable 7
  (routing on the edge SLM's own prefill state, so no separate encoder is needed).
  Its Table III is direct evidence on research question 9 (does the router need
  generation?): generating the tier decision was slower and no more accurate than
  a hidden-state probe.
- **Difference [O].** It has **no Split-LLM tier** (all tiers run full models), no
  activation-transmission cost, and no privacy mechanism or privacy evaluation.
  Bandwidth is an emulated *condition*, not an input to the router. We saw no
  calibration metric (ECE) reported. No code was found.

### 2.2 Dynamic Quality-Latency Aware Routing for LLM Inference in Wireless Edge-Device Networks
- **Record.** R. Bao, N. Xue, Y. Sun, Z. Chen. arXiv 2508.11291 (2025-08-15),
  "accepted by IEEE/CIC ICCC workshop" (arXiv comment; proceedings not checked). [api]
- **Problem.** Route between a mobile-device SLM (e.g. Qwen2.5-3B) and an
  edge-server LLM (e.g. QwQ-32B), for single-turn and multi-turn queries. [body]
- **Router architecture.** A "lightweight BERT router inspired by RouteLLM"
  produces a semantic score. It is **fused with an explicit latency cost model**
  covering on-device compute and **wireless communication**, plus a context-aware
  cost for model switching and **KV-cache management** in multi-turn dialogue. [abs][body]
- **Setup / evaluation.** "a series of **simulated** experiments". The on-device
  compute time is taken from published mobile benchmarks. [body]
- **Datasets / metrics.** MMLU, GSM8K, MT-Bench-101. Metrics are response latency
  and large-model invocation rate at maintained quality. [abs]
- **Results (authors' claims).** Latency −5 to 15% and large-model invocations
  −10 to 20% against baselines "while maintaining full inference quality". [abs]
- **Overlap [O].** This is the closest match to **C2 as written**: an explicit
  communication plus computation latency term in the routing score for SLM vs LLM
  at the edge. The manuscript's Eq. 2 cost term C(M_k, q) is structurally this.
- **Difference [O].** Its evaluation is simulated. The LLM is on an edge server,
  not a Split-LLM. The router is a standard BERT classifier, and no "tiny-LM" or
  parallel-decoding mechanism is involved.

### 2.3 Pro-Router — *Token-Aware Progressive Model Routing with Adaptive Edge-Cloud Collaboration*
- **Record.** X. Gui, S. Wang, S. Sun, Z. Wang, Z. Yu, Z. Yang (affiliations
  include Anyscale, Mississippi State, ICT-CAS). arXiv 2608.28726 (2026-08-28),
  9 pp., preprint. Code at `xinyuangui2/pro-router`, Apache-2.0, last push
  2026-08-27. [api]
- **Problem.** Routing for **multimodal** LLM serving between small models and a
  72B cloud model. [abs]
- **Router architecture.** Two stages. (1) A lightweight **prompt pre-scorer**
  runs before generation. (2) A **token-aware verifier** reads the small model's
  per-token sampling distributions and decides ship vs escalate. The ship
  threshold is set by coverage-based **selective prediction** (Geifman & El-Yaniv
  2017), calibrated on a validation split. [abs][body]
- **Setup.** Small models Qwen2.5-VL-7B, LLaVA-OneVision-7B and Pixtral-12B.
  Large model Qwen2.5-VL-72B. The **"edge" tier is AWS g5.12 nodes (4× A10G)**
  and the cloud tier is p4d (8× A100), on Ray. Added one-way network latency of
  0/200/1000 ms was tested. [body]
- **Datasets / metrics.** 15 benchmarks (11 vision-language, 4 text: MMLU, GSM8K,
  CoQA, TriviaQA; test splits of 106–682 items). Metrics are routing AUROC,
  throughput (req/s) and latency. [body]
- **Baselines.** RouteLLM (278M), FrugalGPT (DistilBERT-66M), P(True) and AutoMix.
  The paper reports that RouteLLM and FrugalGPT add 47–119 ms of GPU time that
  competes with decoding. [body]
- **Results (authors' claims).** "highest routing accuracy", routing signal
  ">10× faster", pipeline throughput "+75%". The full model's AUROC is
  0.805/0.753/0.685 for Qwen/LLaVA-OV/Pixtral. [abs][body]
- **Overlap [O].** Edge–cloud escalation, a pre-generation lightweight scorer,
  selective-prediction thresholds (the confidence/abstention aspects of C1/C3),
  and a public Apache-2.0 implementation with ready baselines.
- **Difference [O].** Its "edge" is a datacenter GPU tier, not an on-device SLM.
  The small models are 7–12B. It is multimodal-first, has no Split-LLM and no
  privacy claims. The main signal is **post**-generation, so the SLM always runs
  first.

### 2.4 Hybrid LLM — *Cost-Efficient and Quality-Aware Query Routing*
- **Record.** D. Ding, A. Mallick, C. Wang, R. Sim, S. Mukherjee, V. Rühle,
  L. V. S. Lakshmanan, A. H. Awadallah (Microsoft / UBC). arXiv 2404.14618,
  **ICLR 2024 main** (arXiv comment). [api]
- **Problem.** Hybrid inference between small models "deployed on lower cost
  (e.g., edge) devices" and large cloud models. [abs]
- **Router.** Predicts query difficulty against a desired quality level, and the
  quality level is **tunable at test time**. [abs]
- **Results (authors' claims).** "up to 40% fewer calls to the large model, with
  no drop in response quality". [abs] The router backbone, datasets and hardware
  were not checked this iteration.
- **Overlap [O].** It is the original peer-reviewed statement of *exactly* the
  manuscript's Eq. 2 trade-off, in the edge-small vs cloud-large framing. The
  manuscript does not cite it. **This is a citation gap.**
- **Difference [O].** It does not model communication or latency explicitly,
  has no Split-LLM, and (as far as the abstract shows) the edge side is a framing
  rather than on-device measurement.

### 2.5 SWARM-LLM — *Collaborative Inference for Edge-based Small Language Models*
- **Record.** M. Dahshan, Q. Mamun, T. Debnath. arXiv 2606.14711 (dated
  2026-04-22 in the metadata), preprint. Code at `mdahshan/swarm_llm`,
  Apache-2.0. [api]
- **Router.** Per query, it chooses to answer locally, collaborate with peer
  SLMs, or "summon" a cloud FM, using "lightweight uncertainty estimates and
  safety signals". [abs]
- **Setup / evaluation.** Three heterogeneous SLMs on commodity hardware plus a
  70B FM via API, on a "controlled study workload" of easy, hard and safety
  queries. [abs] That is a small, self-constructed workload [O].
- **Results (authors' claims).** Better on hard questions than edge-only, with
  cloud usage at "roughly one quarter of queries". [abs]
- **Overlap [O].** An on-edge, privacy-motivated, uncertainty-gated escalation
  to the cloud with public code (C1/C2 framing).
- **Difference [O].** Its main mechanism is a peer swarm (a multi-SLM consensus
  layer). The evaluation is small and there is no Split-LLM.

### 2.6 RouteLMT — *Learned Sample Routing for Hybrid LLM Translation Deployment*
- **Record.** Y. Luo, H. Liu, D. Lin, K. Chang, C. Wang, B. Li, Q. Du, T. Xiao,
  J. Zhu (NiuTrans / Northeastern Univ.). arXiv 2604.22520. **ACL 2026 Industry
  Track, pp. 1886–1897** (ACL Anthology 2026.acl-industry.129). [api]
- **Router.** An **in-model** router that probes the *small translator's
  prompt-token representation* to predict the **marginal gain** of the large
  model, with no external model and no hypothesis decoding. Routing is posed as
  budget allocation, with a guarded variant for regression risk. [abs]
- **Scope.** Machine translation only. [abs]
- **Overlap [O].** Its mechanism is the same idea as ConsRoute and deliverable 7
  P2 (a probe on the small model's own representation). The **marginal-gain**
  label is a better-justified target than the absolute "suitability" f_θ(q, M_k)
  in Eq. 3.
- **Difference [O].** Translation only, no edge measurement, no Split-LLM. The
  manuscript's citation (L85; bib L381–382) lacks venue and ID. Correct form: ACL
  2026 Industry, arXiv 2604.22520.

### 2.7 LLM Router: Rethinking Routing with Prefill Activations
- **Record.** T. Varshney, A. Surla, M. Xu, G. V. Krishnan, M. Jeblick, D. Austin,
  N. Vaidya, D. Onofrio. arXiv 2603.20895, v1 2026-03-21, v2 2026-08-11,
  preprint. [api]
- **Router.** An "Encoder-Target Decoupling" design. Residual-stream prefill
  activations of an open-weight **"Encoder"** LLM, with layers chosen by Fisher
  separability, feed a **SharedTrunkNet** MLP that predicts **per-model
  correctness probabilities**, including for closed target models. [abs]
- **Results (authors' claims).** Closes 45.58% of the best-single-to-oracle gap
  at 74.31% cost savings vs the most expensive model. [abs]
- **Overlap [O].** The nearest *terminological* neighbour to "micro-encoder",
  and the same activation-probe idea as 2.1 and 2.6.
- **Difference [O].** It is cloud-side and uses no edge budget. The "Encoder" is
  a full LLM, not a tiny model.

### 2.8 HyDRA — *Hybrid Dynamic Routing Architecture for Heterogeneous LLM Pools*
- **Record.** A. Garg, S. S. Roy, J. Jang, F. Brancasi, S. Fu. arXiv 2605.17106,
  v2 2026-06-12, preprint. Deployed in **GitHub Copilot VS Code Chat auto-mode**
  (authors' statement). [abs]
- **Router.** **ModernBERT-base (149M), ONNX dynamic INT8**, with 4 independent
  sigmoid capability heads (reasoning, code generation, debugging, tool use).
  **Shortfall matching** against configuration-defined model profiles, so
  catalogue changes need **zero retraining**. Trained on 50,159 LLM-judge labels
  from de-identified Copilot telemetry. [abs][body]
- **Latency (authors' claims).** 86 ms median CPU in production [abs]. The
  architecture figure gives 55 ms P50 / 120 ms P99 (ONNX INT8, CPU) [body]. The
  two figures differ and the reason is not reconciled here.
- **Results (authors' claims).** SWE-Bench Verified, 5-model pool: 75.4% vs
  74.2% (always-Sonnet 4.6) at 12.9% cost savings; iso-quality at 54.1% savings.
  Generalises to LiveCodeBench, BigCodeBench and τ-bench. [abs]
- **Overlap [O].** A lightweight CPU-grade encoder router with a structured
  multi-head output, no retraining when the pool changes, and a heterogeneous pool.
  It pre-empts C1's "lightweight" and C3's "without retraining" in production.
- **Difference [O].** Cloud pool only, no edge SLM, no communication term, no
  Split-LLM. Training data is proprietary telemetry and no code was found.

### 2.9 RouteLLM — *Learning to Route LLMs from Preference Data*
- **Record.** I. Ong, A. Almahairi, V. Wu, W.-L. Chiang, T. Wu, J. E. Gonzalez,
  M. W. Kadous, I. Stoica. arXiv 2406.18665. **ICLR 2025 poster**: the ICLR
  proceedings page and poster page were found by web search this iteration, and
  OpenReview returned a 403 challenge. [api] Code at `lm-sys/RouteLLM`, Apache-2.0,
  last push 2024-08-10. [api]
- **Router.** Binary strong-vs-weak win-probability predictors trained on
  Chatbot Arena preferences plus augmentation (BERT classifier, matrix
  factorisation, similarity-weighted ranking, causal-LLM classifier). [abs; variants per deliverable 7]
- **Results (authors' claims).** Costs cut "by over 2 times in certain cases"
  without quality loss, with transfer when the model pair changes. [abs] The
  manuscript's "2–3.6×" and "87–95%" (L85) are **not in the abstract**, so they
  need checking against the paper body (claim audit).
- **Overlap [O].** The canonical learned weak/strong router and the obvious
  baseline for C1/C4.
- **Difference [O].** Cloud pair only, no edge, no communication cost.

### 2.10 AutoMix — *Automatically Mixing Language Models*
- **Record.** P. Aggarwal, A. Madaan, et al. (13 authors). arXiv 2310.12963,
  **NeurIPS 2024** (arXiv comment). [api]
- **Router.** **Few-shot self-verification** by the small LM, then a **POMDP**
  router over model sizes. [abs]
- **Results (authors' claims).** ">50%" compute-cost reduction at comparable
  performance across 5 LMs and 5 datasets. [abs]
- **Overlap [O].** The reference design for *architecture option C*
  (confidence/self-routing SLM). Pro-Router already uses it as a baseline.
- **Difference [O].** It is post-generation (the SLM answers first), with no
  edge measurement and no Split-LLM.

### 2.11 Privacy-Aware Split Inference with Speculative Decoding for LLMs over WANs
- **Record.** M. Cunningham. arXiv 2602.16760 (2026-02-18), 21 pp., preprint,
  single author. [api]
- **What it is.** It is **not a router**. It is a Split-LLM system: the
  embedding and unembedding layers stay local, so "raw tokens never leave the
  trusted device", and only activations cross an ~80 ms WAN. It applies
  **lookahead decoding** to amortise round trips, and reports an empirical
  **inversion attack** that recovers about 59% of tokens at a 2-layer split vs
  about 35% at 8 layers. [abs]
- **Results (authors' claims).** 8.7–9.3 tok/s (Mistral 7B) and 7.8–8.7 tok/s
  (NeMo 12B, 4.9 GB local VRAM). An RTT model projects 15–19 tok/s at 20 ms. [abs]
- **Why it is in this list [O].** This is the only work we found that pairs
  **Split-LLM over a WAN** (the manuscript's L76 framing) with a **Jacobi-family
  parallel decoder**: lookahead decoding descends from Jacobi decoding (see
  deliverable 6 §1, lineage table). It gives two things:
  1. The **technically sensible role** for Jacobi-style decoding in this paper
     is **amortising Split-LLM round trips during generation**, not routing, which
     agrees with deliverable 6's J1. That role is *partially occupied* by this
     preprint. Replacing lookahead with a Jacobi-Forcing-trained model is not
     reported there, and we found no report of it elsewhere (bounded search only).
  2. Its inversion numbers are direct evidence against treating a Split-LLM as
     private by default. The manuscript's privacy reasoning at L76 (fewer than S/2
     layers at the edge) must be qualified.
- **Difference [O].** No routing, no SLM path.

### 2.12 CSCR — *Cost-Aware Contrastive Routing for LLMs*
- **Record.** R. Shirkavand, S. Gao, P. Yu, H. Huang. arXiv 2508.12491 (v1
  2025-08-17, latest 2025-11-24), preprint. [api]
- **Router.** A contrastive encoder maps prompts and models (via logit
  footprints or perplexity fingerprints) into a shared space, then does a
  **FAISS k-NN** lookup. The authors say it needs "**no retraining when the
  expert pool changes**" and gives "microsecond latency". [abs]
- **Results (authors' claims).** Up to 25% better accuracy-cost trade-off. [abs]
- **Overlap [O].** Pre-empts C3 ("without retraining") and the lightweight
  aspect of C1. **Difference:** cloud pools, no edge.

### 2.13 ICL-Router — *In-Context Learned Model Representations for LLM Routing*
- **Record.** C. Wang, H. Li, Y. Zhang, L. Chen, J. Chen, P. Jian, P. Ye,
  Q. Zhang, S. Hu. arXiv 2510.09719, **AAAI 2026** (arXiv comment and AAAI OJS
  page found by search). Code at `lalalamdbf/ICL-Router` (no SPDX license
  detected). [api]
- **Router.** An **LLM-based** router that reads projected query vectors and
  in-context capability profiles and predicts whether each model answers
  correctly. New models are added **without retraining the router**. [abs]
- **Overlap / difference [O].** Pre-empts C3. The router is itself an LLM, which
  is the opposite of the lightweight goal. No edge. The authors overlap with
  LLMRouterBench.

### 2.14 IRT-Router
- **Record.** W. Song, Z. Huang, C. Cheng, W. Gao, B. Xu, G. Zhao, F. Wang,
  R. Wu. arXiv 2506.01048. **ACL 2025 main, pp. 15629–15644** [api]. Code at
  `Mercidaiha/IRT-Router`. [api]
- **Router.** Item-response-theory model of LLM ability and query difficulty,
  with a cost objective and a semantic-similarity warm-up for cold start. [abs]
- **Results (authors' claims).** 20 LLMs, 12 datasets, and it "outperforms most
  baseline methods". [abs] This matches the manuscript's L85 description.
- **Overlap / difference [O].** It provides an interpretable query-difficulty
  signal and cost-aware multi-LLM routing. Cloud only.

### 2.15 Arch-Router
- **Record.** C. Tran, S. Paracha, A. Hafeez, S. Chen (Katanemo). arXiv
  2506.16655, preprint. [api]
- **Router.** A **generative** 1.5B model (Qwen2.5-1.5B-Instruct base, HF
  `pipeline_tag=text-generation`; see deliverable 7) that maps queries to
  user-defined domain/action policies. New models are added without retraining. [abs]
- **Overlap / difference [O].** It is the only well-known **generative small
  router** and so the natural comparator for architecture option A. It is not
  edge-cost-aware. The "93.17%" and "28×" figures quoted in the manuscript (L85)
  are not in the abstract and must be checked in the body.

### 2.16 BEST-Route
- **Record.** D. Ding, A. Mallick, S. Zhang, C. Wang, et al. arXiv 2506.22716,
  **ICML 2025**. Code at `microsoft/best-route-llm` (MIT; its repo description
  cites this arXiv ID). [api]
- **Router.** Chooses the model **and the number of samples** (best-of-n from
  small models) from query difficulty. [abs]
- **Results (authors' claims).** Up to 60% cost reduction at <1% performance
  drop. [abs]
- **Overlap / difference [O].** A structured decision output (model × budget)
  that is relevant to option D. Cloud only.

### 2.17 LLMRouterBench
- **Record.** H. Li, Y. Zhang, Z. Guo, C. Wang, …, S. Hu. arXiv 2601.07206.
  **Findings of ACL 2026, pp. 37733–37754** [api]. Code and data at
  `ynulihao/LLMRouterBench`. [api]
- **What it establishes (authors' claims).** 400K+ instances, 21 datasets,
  33 models and 10 baselines. Under unified evaluation "many routing methods
  exhibit similar performance", several recent routers including commercial ones
  "fail to reliably outperform a simple baseline", the oracle gap is driven by
  "model-recall failures", and "backbone embedding models have limited
  impact". [abs]
- **Relevance [O].** It supplies the manuscript's pre-computed evaluation data (L205: SimpleQA results "in LLMRouterBench"). Its
  finding that the embedding backbone has limited impact directly weakens a
  contribution that rests on the router's *architecture*, whether micro-encoder
  or TLM. Any claimed gain must beat its simple baseline under its protocol.
  Whether its 33 models include the manuscript's edge pool is **still
  unverified** (carried from iteration 1).

### 2.18 Jev / System One (TypeSafe) — production decision model
Covered in full in `research/jev-system-one.md`. In short: an API-only, cloud,
calibrated structured-decision model that its vendor markets for intent routing
and confidence-gated weak→strong escalation. It is the closest *production*
analogue of the "fast decision model" idea. It cannot run on-device, and its
terms forbid distillation.

---

## 3. Adjacent work (verified, but not a query-level SLM-vs-LLM router)

These are listed so that the novelty matrix does not miss them. They are not
counted among the 18.

| Work | Record | Why adjacent, not closest [O] |
|---|---|---|
| CITER (2502.01976) | W. Zheng et al.; repo `aiming-lab/CITER` whose description says "[COLM'25]" [api] | **Token-level** SLM/LLM routing trained with RL. It is already cited in the manuscript as WZheng2025 with an arXiv-only entry, so the venue could be updated to COLM 2025 after confirming on the COLM site |
| DiP-SD (2604.20919) | Y. Xu, S. Zhou, Z. Niu; **IEEE VTC2026-Spring** (arXiv comment) [api] | Device–edge speculative decoding. The 17.89× figure in manuscript L83 **matches the abstract** (Qwen3-1.7B/Qwen3-32B, numerical results) |
| Splitwise (edge–cloud, 2512.23310) | A. Younesi et al.; **ACM UCC '25** [api] | Lyapunov-DRL fine-grained LLM *partitioning* across edge and cloud (Jetson Orin NX, Galaxy S23, RPi 5). It is split-point placement, not model routing. **Name collision** with Microsoft's datacenter "Splitwise" (prefill/decode splitting); cite with care |
| Efficient and Privacy-Aware Edge-Cloud Collaborative Inference (2607.13093) | C. Li, J. Liu, Y. Chen, Y. Li; preprint [api] | Split inference with local embedding and heads, AES-GCM-encrypted transfers and an authenticated KV cache. Privacy engineering for split LLMs, not routing |
| Federate the Router (2601.22318) | B. Askin, …, G. Joshi, C. Joe-Wong; preprint [api] | Federated training of MLP/K-means routers for edge and enterprise clients from decentralised evaluations. Relevant to the privacy side of router *training* |
| FrugalGPT (2305.05176) | L. Chen, M. Zaharia, J. Zou [api] | LLM cascade, "up to 98% cost reduction" [abs]. Cloud APIs. It is the historical baseline for cascades |
| RouterDC (2409.19886) | NeurIPS 2024 [api] | Contrastive mDeBERTa encoder router (see deliverable 7) |
| Hao et al., "Hybrid SLM and LLM for Edge-Cloud Collaborative Inference" | ACM EdgeFM workshop 2024, DOI 10.1145/3662006.3662067 (**from search results only, not opened**) | Token-level edge SLM (TinyLlama) ↔ cloud LLM. Metadata needs checking before it is cited |
| Survey: Li et al. (2507.16731) | Collaborative inference and learning between edge SLMs and cloud LLMs. A search result shows an ACM Computing Surveys DOI 10.1145/3838593 (not opened) | This is the survey to cite for the edge-SLM/cloud-LLM taxonomy. The manuscript cites none |

**Excluded:** *CoSense-LLM* (arXiv 2510.19670). Its arXiv page says "**This paper
has been withdrawn by arXiv due to unverifiable authorship and affiliation**". It
must not be cited, although it looks topically close (edge-first, "PromptRouter",
cost- and uncertainty-aware cloud escalation).

---

## 4. What the closest prior art already covers (input to deliverables 4 and 8)

All points in this section are our analysis [O], based on the entries above.

1. **An edge-side lightweight pre-generation router between an on-device SLM and
   larger remote models is occupied.** ConsRoute (real device-class hardware,
   emulated network, 3 tiers), Bao et al. (simulated, explicit wireless latency
   model), SWARM-LLM (uncertainty gate), and in the peer-reviewed literature Hybrid
   LLM (ICLR 2024). C1 as written ("novel … unlike existing routing approaches
   that rely on heavy models", L61) is not defensible.
2. **Routing on the SLM's own prefill representation is occupied**: ConsRoute
   (edge), RouteLMT (ACL 2026 Industry) and the prefill-activation router. This
   removes most of the novelty from deliverable 7's P2. A narrower version
   remains open (see item 6).
3. **Communication- and latency-aware routing costs exist**: Bao et al.'s explicit
   compute plus wireless-communication model with KV-switching cost, and
   ConsRoute's evaluation across network conditions. C2 therefore depends on what
   the *Split-LLM* path adds.
4. **"Without retraining" when the pool changes is occupied** by HyDRA
   (production), CSCR, ICL-Router and Arch-Router. C3 is not a contribution unless
   it is narrowed.
5. **The generative vs discriminative router question has direct evidence.**
   ConsRoute's Table III shows explicit generated tier choices are slower (36 ms,
   or 1,868 ms with CoT) and no more accurate than a hidden-state probe (20.9 ms,
   87.92%). This is one paper on one dataset, but it supports deliverables 6 and 7:
   the router does not need generative (or Jacobi) decoding.
6. **Not found in this set (our bounded search).** No work has a **query-level
   router whose action space includes a Split-LLM path**, i.e. the cost of
   *partial-local* execution with activation transmission and split-depth-dependent
   privacy leakage, next to "edge SLM only" and "full cloud". The split-inference
   works (2602.16760, 2512.23310, 2607.13093) optimise the split and do not route.
   The routers (2.1–2.10) do not include a split tier. This is the **candidate
   residual gap**. It is **unconfirmed**: it rests on two targeted searches this
   iteration plus the earlier micro-encoder search, not a systematic review.
7. **Jacobi-family decoding has met Split-LLM once** (2602.16760, lookahead
   decoding) but **not routing**. A Jacobi-Forcing-trained edge or split
   generator amortising WAN round trips is a plausible *system* component. It is
   not a routing contribution.
8. **Evaluation bar.** LLMRouterBench reports that most routers tie a simple
   baseline under unified evaluation. Any positive result would have to clear
   that bar with reported variance.

## 5. Citation consequences for the claim audit (deliverable 13)

- **Missing but necessary:** Hybrid LLM (ICLR 2024), ConsRoute, Bao et al.
  2508.11291, AutoMix (NeurIPS 2024), HyDRA, CSCR, the edge-SLM/cloud-LLM survey
  (2507.16731), and 2602.16760 (Split-LLM over WAN, privacy numbers).
- **Metadata to fix:** Luo2026 → ACL 2026 Industry Track, pp. 1886–1897, arXiv
  2604.22520. Xu2026 → VTC2026-Spring. WZheng2025 → possibly COLM 2025 (needs
  confirming). RouteLLM title: the arXiv title is "…**with** Preference Data" and
  the ICLR title is "…**from** Preference Data". Both occur, so cite the ICLR
  version.
- **Numbers still to check in paper bodies:** RouteLLM "2–3.6×" and "87–95%"
  (L85), Arch-Router "93.17%" and "28×" (L85). The IRT-Router "20 LLMs and
  12 datasets" (L85) and DiP-SD "17.89×" (L83) match their abstracts [api].

## 6. Uncertainties and open questions

- ConsRoute, Bao et al., Pro-Router, SWARM-LLM and 2602.16760 are **preprints or
  workshop papers**. Their results are authors' claims that we have not reproduced.
- The residual-gap statement (§4 item 6) could be overturned by one paper we
  missed. Before the advisor meeting, a targeted search is needed on "routing" ×
  "split inference/split computing/partial offloading" in IEEE (INFOCOM, TMC,
  JSAC) and ACM (MobiCom, SenSys, MobiSys) venues, which arXiv-centric searching
  under-covers.
- ConsRoute's code availability, calibration reporting and exact router size
  were not checked.
- HyDRA's two latency figures (86 ms median vs 55 ms P50) are unreconciled.
- For Hybrid LLM, the router backbone and datasets are unchecked, and the edge
  side may be framing rather than measurement.
- The Hao et al. (EdgeFM 2024) and survey DOI metadata come from search results
  only.
- ICL-Router, IRT-Router and LLMRouterBench repos report no SPDX license through
  the GitHub API. Their reuse terms must be checked by hand for the
  reproducibility plan (deliverable 11).
