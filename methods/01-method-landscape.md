# methods/01 — Method landscape (primary-source review)

*Method-selection sprint, iteration 1. Answers METHOD_BRIEF §6 and §19 file 01.
This consolidates the primary-source records already gathered and saved by the
earlier sprint — `research/closest-prior-art.md` (**[cpa]**, raw copies under
`research/raw/prior-art/`), `research/micro-encoder-investigation.md` (**[me]**),
`research/jacobi-forcing.md` (**[jf]**) and `research/jev-system-one.md`
(**[jev]**) — into the seven method families the brief enumerates. Evidence tags:
**[abs]** authors' abstract claim, **[body]** read in the paper body, **[api]**
GitHub/HF/ACL/arXiv metadata, **[O]** our analysis. **Nothing here was
reproduced by us; every number is a number the authors report.** A search
result pointing back to THIS repository is not evidence and none is used.*

Coverage limits (carried from [cpa §6], [me §1]): searches were arXiv- and
WebSearch-centric; IEEE (INFOCOM/TMC/JSAC) and ACM (MobiCom/SenSys/MobiSys)
venues and non-English literature are under-covered. Several venues/numbers are
still marked "to verify in body". This is a strong but non-systematic review.

---

## 1. Generative routers

Small causal LMs that **generate** the route decision as text.

| Work | Venue / status | Router | Output | Code | Note |
|---|---|---|---|---|---|
| **Arch-Router-1.5B** (Tran et al., 2506.16655) | preprint 2025-06 | Qwen2.5-1.5B-Instruct base, causal LM (HF `pipeline_tag=text-generation`) [api] | Generated domain/action policy name; new models added without retraining | HF `katanemo/Arch-Router-1.5B` (license "other"); serving repo `katanemo/plano`, Apache-2.0 [api] | The reference generative small router. Manuscript L317 "fine-tune its routing head" **does not match** a head-less causal LM [me §2] |
| **ICL-Router** (Wang et al., 2510.09719) | **AAAI 2026** [api] | An **LLM-based** router over projected query vectors + in-context capability profiles | Per-model correctness; adds models without retraining | `lalalamdbf/ICL-Router` (no SPDX) [api] | Router is itself an LLM — opposite of "lightweight"; cloud only [cpa §2.13] |

**[O]** Direct evidence against generation: ConsRoute's Table III (below) shows a
*generated* tier choice was slower (36 ms; 1,868 ms with CoT) and no more
accurate than a hidden-state probe (20.9 ms, 87.92%) [cpa §2.1]. One paper, one
dataset. Also `n=1` label ⇒ Jacobi gives 1× [jf §9].

## 2. Discriminative routers (encoders / classifiers)

The plain reading of "micro-encoder": a small encoder + scoring head.

| Work | Venue / status | Body | Output | Code |
|---|---|---|---|---|
| **RouteLLM** (Ong et al., 2406.18665) | **ICLR 2025** [api] | BERT classifier, matrix factorisation, SW-ranking, causal-LLM variants | Binary strong-vs-weak win prob, thresholded | `lm-sys/RouteLLM`, Apache-2.0 [api] |
| **RouterDC** (Chen et al., 2409.19886) | **NeurIPS 2024** [api] | mDeBERTaV3-base query encoder + per-LLM embeddings, dual contrastive loss | Cosine-argmax over pool | `shuhao02/RouterDC` [me §2] |
| **BEST-Route** (Ding et al., 2506.22716) | **ICML 2025** [api] | Multi-head on DeBERTa-v3-small (to verify in body) | Model **and** #samples | `microsoft/best-route-llm`, MIT [api] |
| **CSCR** (Shirkavand et al., 2508.12491) | preprint | Contrastive encoder + FAISS k-NN | Cheapest accurate expert; **"no retraining when pool changes"**, "microsecond latency" [abs] | not checked |
| **HyDRA** (Garg et al., 2605.17106) | preprint v2, **production (GitHub Copilot)** | **ModernBERT-base 149M, ONNX INT8**, 4 sigmoid capability heads | Capability vector → shortfall matching; **zero retraining** on catalogue change | not found |
| **vLLM Semantic Router** (2603.12646) | preprint 2026-03 | ModernBERT-class safety/domain/PII classifiers, ONNX/CK-Flash | Classification → path | vLLM project |
| **ComplianceGate** (Dey, 2606.31163) | preprint, single author | Encoder classifier ahead of any decoder | complexity×sensitivity → tier/geography; 99.2% acc, 7 ms overhead, 600-query eval [abs] | not stated |
| **TF-IDF / MiniLM baseline** (Bansal & Agarwal, 2604.03455) | 5-pg preprint | TF-IDF / MiniLM + classical classifiers | Retrieval-strategy class; TF-IDF+SVM macro-F1 0.928 [abs] | not stated |

**[O]** A lightweight encoder-classifier router is **standard practice** across
academia (RouteLLM-BERT, RouterDC, BEST-Route), production (HyDRA, vLLM-SR,
ComplianceGate) and edge–cloud (Pro-Router pre-scorer). Both "no retraining on
pool change" (CSCR, HyDRA) and "sub-10 ms / CPU" (ComplianceGate, HyDRA) are
already claimed [me §2]. Renaming this a "micro-encoder" creates no novelty.

## 3. Capability / utility prediction

Predict per-model quality/correctness rather than a class label.

| Work | Venue / status | Signal | Note |
|---|---|---|---|
| **IRT-Router** (Song et al., 2506.01048) | **ACL 2025 main** [api] | Item-Response-Theory ability × difficulty, cost-aware | Interpretable difficulty signal; cloud only; matches manuscript L85 [cpa §2.14] |
| **RouteLMT** (Luo et al., 2604.22520) | **ACL 2026 Industry** [api] | In-model probe on the small model's prompt representation → **marginal gain** of the large model | **Marginal-gain** target is better-justified than absolute `f_θ(q,M_k)`; translation only [cpa §2.6] |
| **Prefill-activation router** (Varshney et al., 2603.20895) | preprint | Residual-stream prefill activations of an open "Encoder" LLM → SharedTrunkNet MLP → per-model correctness | Nearest *terminological* neighbour to "micro-encoder" (calls its feature model "Encoder"); cloud-side [me §2; cpa §2.7] |
| **Hybrid LLM** (Ding et al., 2404.14618) | **ICLR 2024** [api] | Predict query difficulty vs a **test-time-tunable** quality level | Peer-reviewed statement of *exactly* the manuscript's Eq. 2 trade-off in edge-small vs cloud-large framing — **and the manuscript does not cite it (citation gap)** [cpa §2.4] |

## 4. Hidden-state / prefill routing

Route from representations the local model already computes.

| Work | Venue / status | Mechanism | Note |
|---|---|---|---|
| **ConsRoute** (Qiao et al., 2603.21237) | preprint 2026-03 | MLP on the **device SLM's final-layer prefill hidden state**; clustered Bayesian-optimised thresholds; reranker-scored consistency labels | **Closest overall**: 3-tier device–edge–cloud, on-device router, emulated network profiles; but **no Split-LLM tier**, no activation-transfer cost, no privacy mechanism [cpa §2.1] |
| **RouteLMT** | (as §3) | In-model probe on the small model's own representation | Same idea, translation only |
| **Prefill-activation router** | (as §3) | Prefill activations of an "Encoder" LLM | Cloud-side |

**[O]** Routing on the SLM's own prefill representation is **occupied** (ConsRoute
edge, RouteLMT, prefill-activation router). This pre-empts most of the novelty of
a "route from the edge SLM's state" idea; a narrower version (probe on the
*Split-LLM head's* early-layer activations) remains open but untested [cpa §4
items 2, 6].

## 5. Structured decision models (System One / typed decisions)

| Work | Type | Note |
|---|---|---|
| **Jev / System One** (TypeSafe) | Proprietary API, launched 2026-09-15 | Calibrated typed decision (Choice/Score/Noul + probabilities), marketed for intent routing and weak→strong escalation. **Cloud-only, not small, no fine-tuning, no distillation allowed.** Inspiration + optional baseline only — see `methods/05` [jev] |
| **`system-one-adapter-python`** | MIT re-impl of the *interface* | Reproduces the Noul/Score/Choice interface over ordinary LLM APIs; usable as an open baseline pointed at a local SLM [jev §7] |
| **BEST-Route / HyDRA multi-head** | (as §2) | Open academic realisations of "parallel typed heads in one pass" |

## 6. Adaptive model-selection methods (pool changes without full retraining)

| Work | Mechanism for adding a model |
|---|---|
| **CSCR** | Embed the new model's fingerprint; FAISS lookup — no encoder retraining [abs] |
| **HyDRA** | Add a config-defined capability profile; shortfall matching — "zero retraining" [abs, body] |
| **ICL-Router** | Add an in-context capability profile — no router retraining [abs] |
| **Arch-Router** | Describe the new route in the prompt policy — no retraining [abs] |

**[O]** Requirement D ("adapt without costly retraining") is therefore **already
occupied** by prior work; it is a bar to clear, not a contribution to assert
[cpa §4 item 4]. Each of these adapts *semantic/profile* changes cheaply but
still needs relabelling for genuine *capability* changes of the edge model [O].

## 7. System-aware edge/cloud routing (the SIGCOMM-relevant family)

| Work | Venue / status | System awareness | Note |
|---|---|---|---|
| **Bao et al., Dynamic Quality-Latency Aware Routing** (2508.11291) | IEEE/CIC ICCC 2025 workshop [api] | BERT router **fused with an explicit wireless-communication + compute latency model** and a KV-switch cost | Closest match to contribution C2 as written; but **simulated**, LLM on an edge server (not a Split-LLM) [cpa §2.2] |
| **ConsRoute** | preprint | Evaluated across emulated network conditions (bandwidth/one-way delay profiles) | Network is a *condition*, not a router input [cpa §2.1] |
| **Pro-Router** (Gui et al., 2608.28726) | preprint 2026-08 | Two-stage (pre-gen pre-scorer + post-gen token verifier); tested with +0/200/1000 ms one-way latency; throughput reported | Apache-2.0 code + ready baselines (RouteLLM, FrugalGPT, P(True), AutoMix); "edge" tier is datacenter A10G GPUs, not on-device [cpa §2.3] |
| **Privacy-Aware Split Inference + lookahead decoding** (Cunningham, 2602.16760) | preprint | **Split-LLM over WAN**; embedding/unembedding stay local; lookahead (Jacobi-family) decoding amortises RTT; inversion attack recovers ~59% tokens at 2-layer split vs ~35% at 8 | Not a router. Only work pairing Split-LLM-over-WAN with a Jacobi-family decoder; and its inversion numbers **refute "split = private by default"** [cpa §2.11] |
| **AutoMix** (2310.12963) | **NeurIPS 2024** | Post-generation self-verification + POMDP cascade | Reference for a confidence/self-routing baseline [cpa §2.10] |
| **SWARM-LLM** (2606.14711) | preprint | On-edge uncertainty/safety-gated escalation to a 70B cloud FM; Apache-2.0 | Main mechanism is a peer swarm; small self-made workload [cpa §2.5] |

Adjacent but **not** query-level SLM-vs-LLM routers (do not miscount as prior
routers): CITER (token-level, COLM'25), DiP-SD (device–edge speculative
decoding, VTC2026), Splitwise/2512.23310 (split-point *placement*, not routing),
FrugalGPT (cloud cascade), Federate-the-Router (federated router *training*)
[cpa §3]. **Excluded:** CoSense-LLM (2510.19670) — withdrawn by arXiv for
unverifiable authorship; must not be cited [cpa §3].

## 8. What the landscape implies for method selection [O]

Consolidated from [cpa §4]:

1. **On-edge lightweight pre-generation SLM-vs-remote routing is occupied**
   (ConsRoute, Bao et al., SWARM-LLM, Hybrid LLM/ICLR 2024). The bare "novel
   lightweight router" claim (L61) is not defensible.
2. **Prefill-state routing is occupied** (ConsRoute, RouteLMT, prefill-activation
   router).
3. **Communication/latency-aware cost is occupied** (Bao et al.; ConsRoute
   conditions). C2 therefore depends on **what the Split-LLM path adds**.
4. **"Without retraining" is occupied** (HyDRA, CSCR, ICL-Router, Arch-Router).
5. **Generation is not needed** for the decision (ConsRoute Table III; `n=1`
   Jacobi argument).
6. **Candidate residual gap (unconfirmed):** no verified work has a **query-level
   router whose action space includes a genuine Split-LLM path** — with
   activation-transfer cost and split-depth-dependent privacy leakage — beside
   "edge SLM only" and "full cloud". Split-inference works optimise the split but
   do not route; routers omit a split tier [cpa §4 item 6]. This is the space
   the candidate methods in `methods/02` target. It rests on bounded search and
   must be confirmed against IEEE/ACM networking venues before the advisor
   meeting.
7. **Evaluation bar:** LLMRouterBench (Findings ACL 2026) reports most routers
   *tie a simple baseline* under unified evaluation; tinyrouter ties random
   routing when oracle headroom is small. Any positive result must clear that bar
   with reported variance [cpa §4 item 8; me §2].

## 9. Source table (for `references/library.bib` cross-check)

All records with venue/date/URL/code are in `research/closest-prior-art.md` §1–2
and `research/micro-encoder-investigation.md` §2, with raw copies under
`research/raw/`. Metadata still to fix before citing: Luo2026 → ACL 2026
Industry pp.1886–1897 (2604.22520); Xu2026 → VTC2026-Spring; WZheng2025 →
possibly COLM 2025; RouteLLM title "from" (ICLR) vs "with" (arXiv). Numbers still
to check in bodies: RouteLLM "2–3.6×"/"87–95%", Arch-Router "93.17%"/"28×"
[cpa §5].
