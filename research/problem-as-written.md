# Problem as Written: `source/main-original.tex`

**Deliverable 1 of 18.** Status: complete for the source as it stands. Nothing external was verified here. Citation accuracy, model-name accuracy and novelty are left to `research/claim-audit.md`, `research/closest-prior-art.md` and `research/gap-assessment.md`.

- File analysed: `source/main-original.tex` (411 lines)
- SHA-256 at the time of analysis: `06f5f9d7e9548c04ff59e098c1bd3c63a33d686114ccb8e37363d052b1707cf6`. Later iterations should re-check this hash to confirm the original has not changed.
- Date of analysis: 2026-09-23
- Line numbers below point into `source/main-original.tex`. They are written as `L<n>`.

---

## 0. The most important observation

**The title's technical ideas appear nowhere else in the manuscript.**

The title (L22) is *"Tiny-LM with Jacobi-Forced Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs"*. A case-insensitive search of the file for `jacobi`, `micro` and `encoder` finds only one real match: L22, the title. (L280 also matches, but only because "Microsoft" contains "micro".)

As a result:

- The **Jacobi** mechanism is never defined, motivated, cited or evaluated.
- The **micro-encoder** is never defined. The body always calls the router a "Tiny Language Model (TLM)" (L40, L56, L61, L152, L185–191). It never calls it an encoder.
- The **Proposed Solution** section (L193–195) contains a single period (`.`).

So the manuscript does not say what "Jacobi-Forced Micro-Encoder" means. Any meaning has to come from outside the text. `research/micro-encoder-investigation.md` and `research/jacobi-forcing.md` will cover this. It is also a question for the authors and advisor: *what did the title's author intend?*

---

## 1. Metadata and template residue

| Item | Location | Observation |
|---|---|---|
| Title | L22 | As above |
| Authors | L24 | B. Pedro, S. Nuannimnoi, P. Saetee, H. Baghban (Member, IEEE), K. Honda, C.-Y. Huang |
| Target venue (header) | L30 | "IEEE Transactions on Engineering Management, Vol. 14, No. 8, August 2021". This is **template placeholder text**, not a real submission target |
| Running head | L31 | "Nuannimnoi *et al.*: A Sample Article Using IEEEtran.cls for IEEE Journals". Template placeholder |
| Thanks/received notes | L26–27 | IEEE template boilerplate (April/August 2021) |
| Pub ID | L33 | Template placeholder |
| Keywords | L44 | LLMs, SLMs, LLM-SLM collaboration, Collaborative Inference. No keyword for routing, Split-LLM, Jacobi or encoder |

---

## 2. The research problem

### 2.1 Motivation chain (Introduction, L47–56)

1. LLMs are used in high-stakes areas such as finance and healthcare, where privacy matters (L48, citing `Zhang2025`, `He2025`, `Ostrovskiy2025`).
2. Split-LLM architectures are put forward as the privacy answer: "sensitive data remains local while still leveraging the capabilities of powerful remote models" (L48, citing `Pham2025`, `Hukkeri2025`, `Alhindi2025`). *Note: all three are split **learning** papers (their titles say so). Whether they support claims about split **inference** of LLMs is left to the claim audit.*
3. LLM inference costs too much for simple queries. SLMs are cheaper but less accurate (L50, citing `slm1`, `slm2`).
4. Hybrid inference sends each query to an SLM or an LLM depending on how complex it is (L50, citing 8 works).
5. The key challenge is routing that is accurate and efficient under several constraints (L52).
6. The stated gap (L54) has four parts. Existing routers:
   - (a) "struggle to jointly optimize accuracy and system-level efficiency"
   - (b) are not "adaptable to evolving model pools and deployment conditions"
   - (c) do not account for "communication overhead, memory constraints, and response latency — especially in edge–cloud and Split-LLM collaborative settings"
   - (d) conclusion: "Designing routing mechanisms that are both adaptive and lightweight therefore remains an open challenge."
7. Proposal (L56): a TLM that does "fast and lightweight query understanding to guide inference selection between SLMs and Split-LLMs".

### 2.2 The problem in one sentence (reconstructed)

> For each incoming query at an edge device, choose between answering locally with an edge SLM and offloading (fully or partially, through a Split-LLM) to a larger model. The choice is made by a small learned router at the edge and should maximise expected answer quality minus a λ-weighted system cost (computation + communication + latency).

This is a reconstruction, not a quote. The closest verbatim statements are L137–145 and L168–174.

---

## 3. Formal model (Section III, L135–191)

### 3.1 Entities (L137, L147–159)

- Model pool $\mathcal{M} = \{M_1,\dots,M_K\}$. Each $M_k$ is an edge SLM **or** a cloud LLM/Split-LLM (L137).
- Three roles: **edge device** hosting SLM(s) (L150), **cloud server** hosting LLMs/Split-LLMs (L151), and a **routing module (TLM) deployed at the edge** (L152).
- Action per query (L155–159): process locally with an SLM, **or** offload "$q$ (or part of it, in Split-LLM settings)" to the cloud.
  - *Unclear:* "part of it" could mean part of the query (for example, some tokens) or part of the computation (split layers). The text does not say which.

### 3.2 Equations

| Eq. | Line | Content | Role |
|---|---|---|---|
| (1) | L141–143 | $R: \mathcal{Q} \to \mathcal{M}$ | Routing function |
| (2) | L170–172 | $\max_R \mathbb{E}_{q}\,[U(R(q),q) - \lambda\,C(R(q),q)]$ | Utility-minus-cost objective |
| (3) | L187–189 | $R(q) = \arg\max_{M_k} f_\theta(q, M_k)$ | Router as argmax of a learned TLM scoring function |
| (4) | L217–219 | $T_{total} = TTFT + (N-1)\cdot TPOT$ | End-to-end latency metric |
| (5) | L235–237 | $C_{cloud} = P_{gpu} T_{alloc} / N_{req}$ | Dedicated-GPU cost per request |
| (6) | L243–245 | $C_{serverless} = P_{flex} T_{exec} + C_{overhead}$ | Serverless cost per request |
| (7) | L252–254 | $C_{edge} = E_{query} R_{elec} + C_{device}/L$ | Edge energy + amortised hardware cost |
| (8) | L261–263 | $C_{total} = \sum_i C_i$ | Workload cost |

### 3.3 Variables (Table II, L109–133)

$\mathcal{Q}, q, \mathcal{M}, M_k, K, R(\cdot), U(M_k,q), C(M_k,q), \lambda, \mathbb{E}, f_\theta, \theta$.

### 3.4 Gaps in the formulation itself

These are internal-consistency observations. They do not depend on any literature.

1. **$U$ is undefined in practice.** It is "expected utility (response quality)" (L124, L164), but the paper never says how quality is measured: exact-match accuracy on SimpleQA, a judge score, or something else.
2. **$C$ is not tied to Eqs. (5)–(7).** $C(M_k,q)$ "may include computation, communication, and latency" (L165). Section IV-C defines monetary costs (Eqs. 5–8) and latency metrics (Eq. 4) separately. The paper never says how latency (seconds) and money (USD) combine into one scalar $C$, or what units $\lambda$ has.
3. **The link between $f_\theta$ and the objective is not stated.** Eq. (3) takes the argmax of a "suitability score" $f_\theta$. There is no training loss, no label definition, and no statement that $f_\theta$ approximates $U - \lambda C$. There is also no mechanism for changing λ at inference time (a threshold on a score, for example).
4. **The Split-LLM partition point is not a decision variable.** Split-LLMs are treated as members of $\mathcal{M}$, but nothing defines the split point, the activation size sent, or the effect of the split on $C$. The "fewer than S/2 splits at the edge" remark (L76) is never used in the formulation.
5. **Privacy is not in the objective.** Privacy is the main motivation (L40, L48, L63, L76–78), but no variable or constraint in Eq. (2) represents privacy leakage. Choosing the SLM keeps data local by construction, but the trade-off is never modelled.
6. **Joint optimisation of routing and system cost is only claimed.** Contribution 2 (L63) says the router "explicitly consider[s]" communication, latency and compute. In the formulation this appears only through the generic $C$. No system state (bandwidth, queue length, device load) is an input to $f_\theta$. The router's inputs are just $(q, M_k)$.
7. **Scoring function versus "language model".** Eq. (3) is a scoring/classification problem. Nothing in Sections III–V needs the TLM to generate text. This matters for research question 9 ("does the router need generative decoding at all?"), which is analysed in `architecture/options.md`.

---

## 4. Claimed contributions (L58–68, repeated in the Abstract L40)

| # | Claim (condensed; quoted phrases verbatim) | Line | What would be needed to support it |
|---|---|---|---|
| C1 | "A lightweight TLM-based routing framework"; "a **novel** routing architecture"; "**Unlike existing routing approaches that rely on heavy models or complex scoring pipelines**, the proposed method achieves low-latency decision-making" | L61 | A defined architecture, measured router latency and parameter count against baselines, and a novelty argument against prior small routers (Arch-Router 1.5B and RouteLMT are themselves called lightweight in Table I, L98 and L102) |
| C2 | "Joint optimization of accuracy and system-level efficiency"; considers "communication overhead, inference latency, and computational cost"; "particularly suitable for resource-constrained and **privacy-sensitive** settings" | L63 | A cost term that actually includes communication and latency, measured on the testbed, plus any privacy evaluation (none is proposed) |
| C3 | "Adaptive and scalable routing **without reliance on costly retraining**"; "flexible integration of heterogeneous models"; "without requiring expensive retraining or large-scale supervision" | L65 | A mechanism for adding or removing models without retraining (none is described) and an experiment with a changing model pool (none is proposed in Section IV) |
| C4 | "**Comprehensive evaluation**"; "**extensive experiments** … showing that the proposed method **significantly reduces** inference overhead while maintaining competitive response quality" | L67 | Results. **Section V (L322–333) is empty.** |

Abstract-only claims (L40) that go beyond C1–C4:

- "enables efficient and privacy-aware processing" (hybrid paradigm in general)
- "**Extensive experiments demonstrate** that the proposed method significantly reduces inference cost and latency while maintaining competitive response quality"
- "**The results indicate** that TLM-based routing provides a practical and scalable solution"

⚠ **The Abstract and C4 describe experimental results in the past or present tense, but the manuscript contains no results.** This is the most serious integrity problem in the source. Section V has only headings and placeholders (L324 "…", L327 ".", L330 ".", L333 "."). The revised manuscript must not keep these sentences unless raw evidence exists.

### 4.1 Comparison table (Table I, L87–107)

Table I rates 8 prior methods on six properties. The proposal ("Ours") is the only row with every box ticked, including "System-Aware: ✓ (Full)" and "Split-LLM Support: ✓". Observations:

- The table is never referenced in the text (`\ref{tab:comparison}` does not appear), and the column criteria are not defined.
- Three rows (CITER, TSLT, DiP-SD) are token-level or speculative-decoding systems, not query routers. The comparison therefore mixes different problem types.
- Whether each ✓/✗ for the prior methods is correct needs checking against the primary papers. That is left to `research/claim-audit.md` and `research/novelty-matrix.md`. Example to check: RouteLLM is marked "Lightweight ✗", yet its paper describes several router types, including simple ones such as matrix factorisation. Its "Adaptive ✓" rating also needs checking.
- The "Ours" row describes the goal, not a demonstrated result, because no method (L195) or results (L322–333) exist.

---

## 5. Related work as written (Section II, L72–107)

| Subsection | Lines | Works | Summary as written |
|---|---|---|---|
| Split-LLM | L75–78 | Pham2025, Hukkeri2025, Alhindi2025, Mai2023 | Split the model into $S$ parts and put fewer than $S/2$ at the edge to "extract high-level features and compress intermediate representations" (L76). Split-N-Denoise adds calibrated noise plus client-side denoising (L78) |
| LLM–SLM collaborative inference | L80–85 | CITER (WZheng2025), TSLT (CZheng2026), DiP-SD (Xu2026), RouteLMT (Luo2026), ICL-Router (Wang2026), IRT-Router (Song2025), RouteLLM (Ong2025), Arch-Router (Tran2025) | Token-level RL routing; sparse-logit speculative decoding; pipelined distributed speculative decoding; marginal-gain routing from SLM representations; in-context model vectors; IRT ability/difficulty; preference-trained strong/weak router; 1.5B generative router with a Domain–Action taxonomy |

The related work does **not** discuss:

- Jacobi decoding, Jacobi Forcing, consistency LLMs, diffusion LMs or parallel decoding, even though the title mentions Jacobi and L284–291 use diffusion SLMs as candidate edge models
- Encoder-only or classifier routers (for example, BERT-style routers)
- Calibration, selective prediction or self-routing/cascades using the SLM's own confidence
- Router benchmarks, apart from LLMRouterBench as a data source (L205)
- Structured-decision / "System One"-type models (Jev)

Specific numbers attributed to prior work, which the claim audit must check against the primary sources:

- DiP-SD: "up to 17.89× throughput gains" (L83)
- RouteLLM: "reduces inference cost by 2–3.6× while retaining approximately 87–95% of strong-model performance" (L85)
- IRT-Router: "20 LLMs and 12 datasets" (L85)
- Arch-Router: "1.5B generative router … 93.17% accuracy … over 28× faster than competing models" (L85)
- RouteLMT is described as "translation"-specific (L311 and the bib title at L382). Its general-routing framing at L85 needs checking.

---

## 6. Proposed evaluation (Section IV, L197–320)

### 6.1 Testbed (L201–202)

- **Edge:** Intel Xeon W-2123, 64 GB RAM, 2× RTX 3090 (24 GB), Ubuntu 20.04.6. It "is responsible for executing the client-side Split-LLM computation."
  - *Note:* This "edge" is a workstation with two 24 GB GPUs, not a phone or embedded device. Whether that fits the "edge device" / "resource-constrained" framing (L40, L150) is a question for the advisor.
- **Cloud:** "equipped with ..." The sentence stops there (L202). **Unfinished.**

### 6.2 Data (L204–205)

- SimpleQA (`sqa`) with **pre-computed inference results from LLMRouterBench** (`dataset`). The paper says it has 4,326 short factual questions.
- Stated rationale: it is efficient and diverse, and routing labels can be built "without repeatedly executing every computationally expensive pair of SLMs and Split-LLMs."
- **Internal tension:**
  - LLMRouterBench's pre-computed outputs come from *LLMRouterBench's* model pool. The weak/strong models listed in L267–303 (Gemma-4 variants, diffusion SLMs, Split-LLM deployments of Qwen/Llama/Nemotron) would only have pre-computed labels if they are in that benchmark. This needs checking against the LLMRouterBench release.
  - Latency, communication and cost metrics (L207–265) cannot come from pre-computed accuracy labels. They need live runs on the testbed.
- A single dataset (short factual QA) is used, even though C3 claims adaptation across "varying query complexity" (L65). SimpleQA is known as a factuality benchmark on which even strong models score low. Whether routing on it is informative needs examining (to be checked against the SimpleQA paper).

### 6.3 Metrics (L207–265)

- Latency: TTFT, TPOT, $T_{total}$ (Eq. 4), and **serverless cold-start latency** (L221). The claim that "the proposed framework targets serverless cloud environments" (L221, L228) appears here for the **first time**. Serverless is not mentioned in the Abstract, Introduction or formulation.
- Throughput: RPS, TPS (L223–224).
- Cost: dedicated GPU (Eq. 5), RunPod Flex serverless (Eq. 6), edge energy + amortisation (Eq. 7), total (Eq. 8). Pricing reference: RunPod (L231, L241). No price values, date or source are given.
- The metric intro also lists **"communication overhead, and resource utilization"** (L208). Neither has a defined metric.
- **Missing router-quality metrics:**
  - No routing accuracy / AUROC, no quality–cost curve (for example, APGR/CPT as in RouteLLM, or the Pareto/AUC metrics used in routing benchmarks), and no answer-quality metric for the end-to-end system, even though C4 claims "maintaining competitive response quality."
  - No router overhead metric, meaning the router's own latency, parameter count and memory, which is the core of C1.

### 6.4 Candidate models (L267–303)

Weak / edge (L267–292), all described as 4-bit quantised:

- Gemma-4-E2B-A4B, Gemma-4-E4B-A4B, Gemma-4-12B-A4B
- Phi-4-mini-3.8B
- Meta-Llama-3.1-8B-Instruct
- Diffusion SLMs: LLaDA-MoE-7B-A1B-Instruct-Q4, Dream-v0-Instruct-7B, Fast-dLLM-v2-7B

Strong / Split-LLM (L294–303), all described as 4-bit quantised:

- Qwen3-72B-Instruct
- Llama-3.3-70B-Instruct ("Meta's latest 70B instruction model")
- NVIDIA Nemotron-3 Nano-30B

⚠ Model names, parameter counts and descriptions have **not** been checked in this deliverable. Several need checking against official model cards in the claim audit:

- whether a "Qwen3-72B-Instruct" checkpoint exists
- whether the Gemma-4 variant names and sizes are correct (for example, whether "E2B-A4B" is a real designation)
- whether "Meta's latest" is still accurate as of 2026-09
- Nemotron naming

No model citations are given for any of the 11 models.

### 6.5 Baselines (L305–320)

- RouteLMT, ICL-Router, RouteLLM and Arch-Router-1.5B, each "slightly adapt[ed]" (L306): candidate models replaced, I/O standardised, objectives reformulated to SLM vs Split-LLM, and "where necessary … prediction heads, training labels, and cost functions" modified.
- Arch-Router's routing head is to be **fine-tuned** on the same supervision (L317).
- Missing baselines that routing papers usually include:
  - random routing at matched cost
  - always-SLM and always-LLM
  - an oracle router
  - SLM self-confidence / cascade thresholding
  - a simple embedding + classifier (kNN/MLP) router, as used in RouteLLM and LLMRouterBench-style evaluations
- The Abstract's comparison against "conventional LLM-only" (L67) implies an always-LLM baseline, but Section IV-E does not list one.

---

## 7. Unfinished sections (inventory)

| Section | Lines | State |
|---|---|---|
| III-? / IV **Proposed Solution** | L193–195 | **Empty** (single `.`). No architecture, training procedure, labels, loss, Jacobi mechanism or encoder |
| IV-A System Implementation | L202 | Cloud server spec cut off ("equipped with ...") |
| V Results and Discussion | L322–324 | Placeholder "…" |
| V-A Overall System Latency | L326–327 | Empty (`.`) |
| V-B Cost Reduction | L329–330 | Empty (`.`) |
| V-C Research Limitations | L332–333 | Empty (`.`) |
| VI Conclusion | L335–337 | "The conclusion goes here." |
| Header/venue metadata | L26–33 | IEEE template placeholders |
| Bibliography | L339–402 | 20 entries. `Ford2025` (L351–352) is **never cited**. `Luo2026` (L382) has no venue, arXiv ID or URL. `CZheng2026` (L376) has "and Others" and no volume, pages or DOI. `Ostrovskiy2025` (L349) is a company blog used to support a regulatory claim |
| Tables | L87–133 | Tables I and II are never referenced in the text |

---

## 8. Unsupported or questionable assumptions (as written)

These are assumptions the manuscript makes without evidence. Each will be scored in `research/claim-audit.md` and `research/gap-assessment.md`.

1. **Split-LLM keeps data private** (L48: "such that sensitive data remains local"). Intermediate activations sent from a partial model can leak input information. The manuscript's own Mai2023 reference (L78) exists because plain split inference is *not* private without extra mechanisms. The claim needs qualifying.
2. **Placing fewer than S/2 partitions at the edge "compress[es] intermediate representations"** (L76). Transformer hidden states have the same width at every layer, so a split by itself does not compress anything. Compression needs an explicit mechanism. No source is cited for this specific claim.
3. **Existing routers "rely on heavy models or complex scoring mechanisms"** (L40, L61). Table I itself marks RouteLMT and Arch-Router as lightweight (L98, L102), which contradicts this.
4. **No costly retraining is needed** (L40, L65). No mechanism is described. The baselines include methods designed for model-pool changes (ICL-Router, Arch-Router, as described at L85). "Without retraining" is therefore neither demonstrated nor clearly different from prior work.
5. **The router can account for communication overhead** (L54, L63). The router's inputs in Eq. (3) are only $(q, M_k)$. Without network state as an input, the router can at most learn a fixed average cost per model.
6. **A "Tiny Language Model" is the right router form** (L56, L185). This is never justified against discriminative encoders or classifiers. The decision in Eq. (3) is a K-way score.
7. **LLMRouterBench pre-computed results can provide labels for the paper's own model pool** (L205). This needs verification. See §6.2.
8. **Serverless deployment** (L221, L228) is added in the metrics section without appearing in the problem formulation.
9. **Edge hardware = a 2×RTX 3090 workstation** (L202) is treated as representative of "resource-constrained" edge devices.
10. **Quality is maintained** (L40, L67) without a quality metric being defined.

---

## 9. What the paper is, stripped to what exists

- **What exists:** a motivation (edge–cloud LLM/SLM routing with Split-LLMs); a standard utility-minus-cost routing objective (Eq. 2) and argmax-scoring router (Eq. 3); a related-work summary of 8 routing/collaboration methods; a proposed testbed, dataset, cost model, metric list, model pool and 4 baselines.
- **What does not exist:** the method (including any "Jacobi" or "micro-encoder" component), training details, the cloud testbed spec, any results, any limitations analysis, and a conclusion.
- **Therefore:** C1–C4 and the Abstract's result claims are currently all **unsupported inside the manuscript itself**, whatever the literature says. The paper's central idea as it can be recovered from the text is: *a small learned router at the edge chooses between local SLMs and a Split-LLM, using a utility − λ·cost objective that includes communication/latency/compute cost.* Whether that idea is novel as of September 2026 is the job of `research/gap-assessment.md`.

---

## 10. Open questions for the authors/advisor (from the source alone)

1. What was "Jacobi-Forced Micro-Encoder" meant to refer to? Was it Jacobi Forcing (the parallel-decoding training method), something else, or a placeholder title?
2. Is the router meant to *generate* anything (for example, a route label as text, as Arch-Router does), or only to score models? Eq. (3) suggests scoring.
3. Is the Split-LLM partition point fixed per model, or should the router choose it?
4. Is the edge meant to be the 2×3090 workstation, or a smaller device (phone/Jetson)?
5. Is serverless deployment in scope for the main claim, or only for the cost model?
6. Is privacy meant to be evaluated, or only used as motivation?
7. Does "without retraining" mean adding new models to the pool without retraining the router? If so, what mechanism is intended?
8. Which pre-computed LLMRouterBench models overlap with the intended pool? Will the paper's own SLM/Split-LLM outputs be generated fresh?
