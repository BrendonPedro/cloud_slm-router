# Deliverable 13: Claim audit of `source/main-original.tex`

**Audited file:** `source/main-original.tex`, SHA-256
`06f5f9d7e9548c04ff59e098c1bd3c63a33d686114ccb8e37363d052b1707cf6`. This hash
was re-checked on 2026-09-23, so the file is unchanged since iteration 1.
Line numbers (Lnn) refer to that file.
**Audit date:** 2026-09-23.
**Scope.** Every substantive claim in the abstract, the introduction, the
contributions, the related work, Table I, the formulation and the experimental
setup. Sections IV, V and VI are empty (L195, L324–333, L337), so they have
nothing to audit. What their absence implies is covered in §3.
**Builds on.** Deliverable 1 (`problem-as-written.md`) for the claim inventory,
deliverable 8 (`gap-assessment.md`) for the novelty labels, deliverables 3 and 4
for prior art, deliverable 11 (`experiments/reproducibility-plan.md`) for the
model names, and deliverable 12 (`experiments/prototype/`) for measured
Stage-0 baselines. Novelty sentences are **not re-argued here**. Their rows
point to the gap-assessment row (G#/C#/F#) that holds the evidence.

## Evidence tags and column meanings

| Tag | Meaning |
|---|---|
| [B] | Paper body read: HTML full text, fetched and grepped |
| [A] | Abstract only (arXiv, Crossref or OpenAlex) |
| [M] | Metadata only (Crossref record: title, venue, pages, DOI) |
| [api] | HF or GitHub API record |
| [O] | Our analysis |

**"Supports?"** asks whether *the source cited at that location* supports *the
sentence as written*. Answers are **yes**, **partial**, **no** or **n/a** (no
citation given).
**"Rewrite?"** means the sentence cannot stay as written in `main-revised.tex`.
**"Exp. evidence?"** means the claim can only be kept once it has been measured
by *our own* experiment. None of those experiments has been run yet, except the
Stage-0 label-only baselines in `experiments/prototype/`.

Raw evidence gathered in this iteration is in `research/raw/claim-audit/`, with
a timestamped `fetch-log.txt`, plus `strip.py`, which produces the `.txt`
versions of the HTML files. Evidence from earlier iterations is cited by path.

---

## 1. Bibliography verification (L339–402)

Every `\bibitem` was checked against a primary registry.

| Key | Metadata as given | Registry check | Metadata correct? | Cited where | Note |
|---|---|---|---|---|---|
| Zhang2025 | "Understanding Users' Privacy Perceptions Towards LLM's RAG-based Memory", HAIPS workshop 2025, pp. 10–19 | Crossref: same title and pages, doi 10.1145/3733816.3760750 [M] | **yes** (DOI missing) | L48 | A user-perception study. It supports "privacy matters to users", not claims about LLM pipelines in finance or healthcare |
| He2025 | "The Emerged Security and Privacy of LLM Agent: A Survey with Case Studies", ACM CSUR 58(6), Dec 2025 | Crossref: CSUR 58(6), pp. 1–36, doi 10.1145/3773080 [M] | **yes** (DOI and pages missing) | L48 | A survey of agent security and privacy. Supports the general privacy motivation only |
| Ostrovskiy2025 | edenlab.io blog, 10 Dec 2025 | Fetched: "Posted: December 10, 2025 \| Updated: April 28, 2026". The author is "Partner, Business Development at Edenlab" [`raw/claim-audit/edenlab…txt`] | **yes** | L48 | A **company marketing blog** used to support a regulatory statement. The primary source would be the HIPAA Privacy Rule de-identification standard (45 CFR §164.514), which we have not fetched. Replace it or drop the claim |
| Ford2025 | AI and Ethics 5(5), 4441–4454 | Crossref: identical, doi 10.1007/s43681-025-00681-0 [M] | **yes** | **never cited** | This is the natural support for the re-identification sentence at L48. Cite it there or remove it |
| Pham2025 | IEEE TDSC 22(5), 5352–5365, doi …3565229 | Crossref: identical [M] | **yes** | L48, L76 | Split **learning** (training). It does not support claims about split **inference** |
| Hukkeri2025 | IEEE Access 13, 46312–46333 | Crossref: identical [M] | **yes** | L48, L76 | A survey of split-**fed learning**. Same problem |
| Alhindi2025 | IEEE Access 13, 10094–10110 | Crossref: identical [M] | **yes** | L48, L76 | Split **learning** with channel pruning. Same problem |
| slm1 | IEMENTech 2026, pp. 1–6 | Crossref: identical [M] | **yes** | L50 | A 6-page conference survey. slm2 (KDD) is the stronger of the two SLM citations |
| slm2 | KDD 2025 V.2, pp. 6173–6183 | Crossref: identical, doi 10.1145/3711896.3736563 [M] | **yes** (DOI missing) | L50 | Adequate for the SLM trade-off sentence |
| Mai2023 | arXiv 2310.09130, 2023 | arXiv: title "Split-and-Denoise: Protect large language model inference with local differential privacy". The comments field says "**Proceedings of the 41st International Conference on Machine Learning**" [A] | **partial**: it is cited as an arXiv preprint, but the comment gives ICML 2024 | L78 | The venue should be updated after the ICML proceedings entry is checked. The key says 2023; the ICML version is 2024 |
| WZheng2025 | CITER, arXiv 2502.01976 | arXiv abstract [A]. The repo description says "[COLM'25]" (deliverable 3) | **yes** as a preprint. Venue unconfirmed | L50, L52, L81, L95 | See the L81 row for how accurately it is paraphrased |
| CZheng2026 | "Fast Collaborative Inference via Distributed Speculative Decoding", J. Inf. Intell., 2026, "C. Zheng, K. Zhang, W. Zhang, Q. Liu, A. A. Tesfay, and Others" | Crossref: vol 4(1), pp. 67–85, doi 10.1016/j.jiixd.2025.12.008. Authors: Ce Zheng, Ke Zhang, **Chen Sun**, Wenqi Zhang, Qiong Liu, Angesom Ataklity Tesfay [M] | **partial**: the third author (C. Sun) is missing, "and Others" is wrong because the list is complete at 6, and volume, pages and DOI are missing | L50, L52, L83, L96 | The abstract was obtained from OpenAlex [A]. See the L83 row |
| Xu2026 | DiP-SD, arXiv 2604.20919 | arXiv comment: **IEEE VTC2026-Spring** (deliverable 3) [A] | **partial**: venue missing | L50, L52, L83, L97 | The 17.89× figure matches the abstract |
| Luo2026 | "RouteLMT: …", 2026, no venue | ACL Anthology: **ACL 2026 Industry Track**, pp. 1886–1897. arXiv 2604.22520 (deliverable 3) [A] | **no**: venue, pages and ID are all missing | L50, L52, L85, L98, L311 | The router is an **in-model probe**, not a generative model (deliverable 9, correction) |
| Wang2026 | ICL-Router, AAAI 2026, vol. 40, pp. 33413–33421 | Crossref: AAAI 40(39), 33413–33421, doi 10.1609/aaai.v40i39.40628 [M] | **yes** (issue and DOI missing) | L50, L52, L85, L99, L313 | |
| Song2025 | IRT-Router, ACL 2025, pp. 15629–15644 | ACL Anthology 2025.acl-long.761 (deliverable 3) [A] | **yes** | L50, L52, L85, L100 | |
| Ong2025 | RouteLLM, ICLR 2025, pp. 34433–34448 | ICLR 2025 poster (deliverable 3). arXiv 2406.18665 [B] | **yes** | L50, L52, L85, L101, L315 | The arXiv title is "…**with** Preference Data" and the ICLR title is "…**from** Preference Data". The manuscript uses the ICLR title, which is correct |
| Tran2025 | Arch-Router, arXiv 2506.16655 | arXiv [B] | **yes** (preprint) | L50, L52, L85, L102, L317 | |
| sqa | SimpleQA, arXiv 2411.04368 | arXiv: 8 authors, first is J. Wei [A] | **yes** | L205 | |
| dataset | LLMRouterBench, Findings of ACL 2026, pp. 37733–37754 | ACL Anthology (deliverable 3) [A]. Bundle downloaded and inventoried (iteration 11) | **yes** | L205 | See the L205 row: the *claim* built on it is false |

**Summary.** No bibitem is fabricated: all 20 resolve to real works. Four need
their metadata corrected (Luo2026, CZheng2026, Xu2026, Mai2023). One is never
cited (Ford2025). One is a marketing blog standing in for a regulation
(Ostrovskiy2025). The three Split-LLM citations are all split-*learning* works,
used to support statements about split-*inference* privacy.

---

## 2. Claim-by-claim audit

### 2.1 Title and abstract

| # | Manuscript claim (abridged) | Loc. | Current citation | Supports? | Better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| A1 | Title: "Tiny-LM with **Jacobi-Forced Micro-Encoder** …" | L22 | none | n/a | No method with this name exists as of 2026-09-23 (deliverable 7). If a Jacobi component is kept, cite Jacobi Forcing (arXiv 2512.14681, ICML 2026) for the *decoder* use only (deliverable 6) | **yes**. The mechanism is undefined in the body, and "encoder" contradicts the causal premise of Jacobi Forcing (gap G1) | yes, if any Jacobi component is kept |
| A2 | "deploying them solely in the cloud or compressing them for edge devices has become inadequate due to concerns about latency, privacy, cost, and personalization" | L40 s1 | none | n/a | Li et al., *Collaborative Inference and Learning between Edge SLMs and Cloud LLMs*, ACM CSUR 2026, doi 10.1145/3838593 (arXiv 2507.16731) | **yes, required.** The sentence is **word-for-word identical** to the first sentence of that survey's abstract, which is not cited (gap-assessment §5, `raw/gap/abstracts.txt`). This is an attribution problem as well as a citation gap | no |
| A3 | Hybrid inference is "a promising solution, enabling efficient and privacy-aware processing" | L40 s2 | none | n/a | The survey above; Hybrid LLM (ICLR 2024, 2404.14618); PRISM (AAAI 2026, 2511.22788) for the privacy-aware case | minor: add citations and qualify "privacy-aware" (G3) | no |
| A4 | "a key challenge … lies in designing lightweight and adaptive routing mechanisms" | L40 s3 | none | n/a | The survey above; LLMRouterBench | **yes**. It overstates an occupied space (G4) | no |
| A5 | "we propose an intelligent routing framework based on a TLM … between SLMs and Split-LLMs" | L40 s4 | none | n/a | — | **yes**. The method is undefined (L195 is "."), and the formulation has no split variable (G5) | **yes** |
| A6 | "enables low-latency decision-making while accounting for … communication overhead, computational cost, and response time" | L40 s5 | none | n/a | Prior art: Bao et al. 2508.11291, ConsRoute 2603.21237, Lyra (INFOCOM 2026), LSCI (TMC 2026) | **yes**. Eq. 3 takes only (q, M_k), so link state cannot enter the decision (G6, F3) | **yes**: router latency and cost accounting must be measured |
| A7 | "**Unlike existing routing methods that rely on heavy models or complex scoring mechanisms**, our framework is lightweight, scalable, and adaptable … **without requiring costly retraining**" | L40 s6 | none | n/a | Contradicted by RouteLLM-BERT/MF (ICLR 2025), RouterDC (NeurIPS 2024), HyDRA 2605.17106, ICL-Router (AAAI 2026), Arch-Router, CSCR 2508.12491 | **yes: delete the contrast.** It is also contradicted by the manuscript's own L85, which credits RouteLMT with needing "no external predictors" and Arch-Router with "flexible integration of new models without retraining" (G7) | **yes**, for any retained "adaptable" claim |
| A8 | "**Extensive experiments demonstrate** that the proposed method significantly reduces inference cost and latency while maintaining competitive response quality" | L40 s7 | none | n/a | — | **yes: delete.** No experiment exists: §V is empty and the testbed ends in "…" (L202) (G8) | **yes** |
| A9 | "The results indicate that TLM-based routing provides a practical and scalable solution" | L40 s8 | none | n/a | — | **yes: delete** (G8) | **yes** |

### 2.2 Introduction

| # | Manuscript claim (abridged) | Loc. | Current citation | Supports? | Better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| I1 | LLMs are rapidly adopted "in high-stakes domains such as finance and healthcare" | L48 s1 | none | n/a | A survey or deployment study. Not verified by us | minor: cite or soften | no |
| I2 | "practical LLM pipelines require robust mechanisms for identifying domain-relevant information and safeguarding sensitive data" | L48 s3 | Zhang2025, He2025 | **partial**. Zhang2025 is a user-perception study of RAG memory. He2025 surveys agent security and privacy. Together they support "privacy is a concern", not "pipelines require robust mechanisms" | He2025 alone is adequate for a softened sentence | minor | no |
| I3 | "Privacy-preserving architectures are particularly critical in regulated environments (e.g., HIPAA-compliant systems), where governed representations and anonymization pipelines are employed to mitigate re-identification risks" | L48 s4 | Ostrovskiy2025 | **partial**. A vendor blog asserts it. It is not a primary or regulatory source | Ford2025 (already in the bib, uncited) for re-identification risk from de-identified clinical text. The HIPAA de-identification rule itself (not fetched) | **yes**: swap the citation | no |
| I4 | "Split-LLM architectures have emerged as a promising solution, partitioning model execution … such that **sensitive data remains local**" | L48 s5 | Pham2025, Hukkeri2025, Alhindi2025 | **no**. All three are split-**learning** (training-time) papers. None evaluates split *inference* of an LLM | Split inference over a WAN with measured leakage: Cunningham 2602.16760 (inversion recovers ~59% of tokens at a 2-layer split, ~35% at 8 layers [B], preprint); SnD (Mai2023) for LDP protection; the in-browser split-inference study (IEEE Access 2026, doi 10.1109/ACCESS.2026.3720562) | **yes**. "Sensitive data remains local" is false for activations without added protection. Say "raw tokens stay local; activations can leak input content" (G9) | yes, if a leakage-vs-split-depth claim is made |
| I5 | "the high computational and monetary cost of LLM inference—particularly on a per-token basis—renders the use of large models inefficient for simple queries" | L50 s1 | none | n/a | RouteLLM (ICLR 2025); Hybrid LLM (ICLR 2024) | minor: add a citation | no |
| I6 | SLMs "offer lower latency, reduced energy consumption, and improved deployability … at the expense of reduced accuracy" | L50 s2–3 | slm1, slm2 | **yes** (survey-level support) [M] | — | no | no |
| I7 | Hybrid paradigms "dynamically allocate inference workloads based on query complexity" | L50 s4 | WZheng2025, CZheng2026, Xu2026, Luo2026, Wang2026, Song2025, Ong2025, Tran2025 | **partial**. CZheng2026 (TSLT) and Xu2026 (DiP-SD) are speculative-decoding systems. They do not allocate workloads by query complexity. CITER routes per *token*, not per query | Hybrid LLM, ConsRoute, Lyra for query-level allocation | **yes**: split the citation list by granularity | no |
| I8 | "routine queries are handled locally by SLMs, while complex … queries are escalated to … cloud **or Split-LLM** environments" | L50 s5 | (same list) | **partial**. SLM→cloud escalation is supported. **No cited or found work escalates to a Split-LLM** (G10, U1) | — | **yes**: present the Split-LLM tier as the paper's proposal, not as existing practice | **yes** |
| I9 | "This collaborative approach has the potential to significantly reduce latency, bandwidth usage, and operational costs while maintaining high response quality" | L50 s6 | none | n/a | RouteLLM Table 6 (cost); Hybrid LLM; ConsRoute (latency) | minor: "has the potential" is acceptable with citations | no |
| I10 | "**Early heuristic-based methods have been largely superseded** by learning-based approaches" | L52 s2 | none | n/a | LLMRouterBench reports that many learned routers fail to reliably beat a simple baseline [A]. Our Stage-0 prototype measured TF-IDF+LR at an in-domain deferral AUC near the dataset-prior leak control and **not better than random under leave-one-dataset-out** (`experiments/prototype/results/stage0_summary.md`) | **yes**: soften (G11) | no |
| I11 | Token-level routing (WZheng2025), communication-efficient inference (CZheng2026), throughput via pipelined decoding (Xu2026), marginal gain (Luo2026), capability representations (Wang2026), ability–difficulty modelling (Song2025), preference alignment (Ong2025, Tran2025) | L52 s3–4 | as listed | **yes**, each as a one-line characterisation (abstracts checked [A]; RouteLLM and Arch-Router [B]) | — | no | no |
| I12 | "existing routing methods … struggle to jointly optimize accuracy and system-level efficiency, while remaining adaptable to evolving model pools and deployment conditions" | L54 s2 | none | n/a | Contradicted by IRT-Router, BEST-Route, Hybrid LLM, ICL-Router, HyDRA, Lyra | **yes** (G13) | no |
| I13 | "Designing routing mechanisms that are both adaptive and lightweight therefore remains an open challenge" | L54 s4 | none | n/a | See G7 and G13 | **yes**: narrow it to the Split-LLM tier and to OOD calibration (G15; deliverable 8 §3) | no |

### 2.3 Contributions (L61–L67)

| # | Claim | Loc. | Citation | Supports? | Better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| K1 | "We propose a **novel** routing architecture that leverages a TLM … **Unlike existing routing approaches** that rely on heavy models or complex scoring pipelines, the proposed method achieves low-latency decision-making suitable for real-time deployment" | L61 | none | n/a | Prior art: Hybrid LLM, TMO (MobiHoc 2025), PRISM (AAAI 2026), Lyra (INFOCOM 2026), ConsRoute, Arch-Router (a 1.5B generative router) | **yes**. "Novel architecture" is superseded (C1). "Achieves low-latency" is a result claim with no measurement | **yes** |
| K2 | "explicitly consider … communication overhead, inference latency, and computational cost … particularly suitable for resource-constrained and **privacy-sensitive** settings, such as Split-LLM" | L63 | none | n/a | Bao et al. 2508.11291; ConsRoute; PRISM for privacy-aware three-way routing (whose collaborative path is LDP plus a sketch, not a layer split) | **yes** (C2). Keep only the Split-LLM-specific part, as a proposal | **yes**: per-path bytes, latency and leakage |
| K3 | "**without requiring expensive retraining or large-scale supervision**, improving scalability compared to existing learned routing methods" | L65 | none | n/a | Pre-empted by ICL-Router, Arch-Router, CSCR, HyDRA (C3). It is also internally unsupported: Eq. 3 learns f_θ over a fixed pool and gives no mechanism for adding M_{K+1}. Our Stage-0 run also showed that dev-tuned thresholds fail under dataset shift, even for the oracle (P-Q, LODO:MMLU-Pro; `experiments/prototype/README.md`) | **yes: delete or specify the mechanism** | **yes** |
| K4 | "We conduct **extensive experiments** … showing that the proposed method significantly reduces inference overhead while maintaining competitive response quality compared to conventional LLM-only and existing routing-based approaches" | L67 | none | n/a | — | **yes: delete or recast as future work** (C4) | **yes** |

### 2.4 Related work: Split-LLM (L75–78)

| # | Claim | Loc. | Citation | Supports? | Better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| R1 | A model "can be divided into S total splits, thus called 'Split-LLM'" | L76 s2 | none | n/a | Neurosurgeon (ASPLOS 2017) for DNN partitioning. Splitwise-edge (ACM UCC '25, 2512.23310). DIO-LLMs (ICC 2025) | minor: add citations. "Split-LLM" is used in the literature but is not a standard term; define it | no |
| R2 | "closely related to split learning and collaborative inference frameworks that distribute model execution across multiple nodes" | L76 s3 | Pham2025, Hukkeri2025, Alhindi2025 | **partial**. They support "split learning". None of them is about collaborative *inference* | Add split-inference work (R1 sources) | **yes**: separate learning from inference | no |
| R3 | "allocating a **minority** of the model partitions (fewer than S/2) to the edge node allows the system to extract high-level features and compress intermediate representations before transmitting them over the WAN" | L76 s4 | none | **no source** | The in-browser split-inference study finds that the optimal split depends on the client device and that per-token RTT is invariant to the split point [A]. Cunningham reports that leakage *decreases* with depth [B], which pulls toward *more* edge layers | **yes**. This is a design assertion with no citation. The "<S/2" rule is not supported by any source we found | **yes**, if the split rule is kept |
| R4 | SnD "adds calibrated noise to transmitted embeddings combined with client-side denoising … under differential privacy guarantees" | L78 | Mai2023 | **yes**. The arXiv abstract describes perturbed embeddings, server output, and client-side denoising under *local* differential privacy [A] | Same paper, ICML 2024 version | minor: "local differential privacy"; update the venue | no |

### 2.5 Related work: LLM–SLM collaborative inference (L81–85)

| # | Claim | Loc. | Citation | Supports? | Better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| R5 | CITER: a token-level router, "optimized via reinforcement learning with joint quality–cost objectives, **enhanced by preference-based learning** and efficient reward estimation, achieving significant cost reduction **without degrading output quality**" | L81 | WZheng2025 | **partial**. The abstract gives a policy-optimisation router with a quality-plus-cost reward and a reward-estimation shortcut, and says it "reduces the inference costs while preserving high-quality generation" [A]. "Preference-based learning" is **not in the abstract** (the body was not checked). "Without degrading" is stronger than "preserving high-quality" | same | minor: drop "preference-based" unless the body confirms it | no |
| R6 | TSLT "transmits only a subset of logits while **preserving decoding correctness**. Combined with multi-candidate token-tree verification, the approach **improves throughput and reduces latency**" | L83 s1–2 | CZheng2026 | **partial**. The abstract (OpenAlex [A]) guarantees that the **acceptance rate** is preserved, and claims TSLT "significantly reduces **uplink communication** while **maintaining** end-to-end inference latency and model quality". It does **not** claim reduced latency or higher throughput. "Token-tree verification" is not in the abstract: it says "multi-candidate case" | same | **yes**: "reduces uplink communication while maintaining latency and quality" | no |
| R7 | DiP-SD "achieves up to 17.89× throughput gains over conventional decoding" | L83 s3 | Xu2026 | **yes**. It matches the abstract (numerical results, Qwen3-1.7B/Qwen3-32B) [A] | same, with its VTC2026-Spring venue | no (add the venue) | no |
| R8 | RouteLMT "formulates routing as a budget allocation problem and uses marginal gain … predicted directly from SLM representations … **superior quality–cost trade-offs without external predictors**" | L85 s1–2 | Luo2026 | **yes** [A]. Note that the abstract says "quality-budget Pareto frontier" and targets **machine translation** only | same, with full ACL 2026 Industry metadata | minor: say MT-specific | no |
| R9 | ICL-Router "encodes model capabilities as in-context vectors and decouples capability profiling from routing, enabling scalable integration of new models while achieving **state-of-the-art** performance" | L85 s3 | Wang2026 | **yes** as the authors' claim [A]: "state-of-the-art routing performance in both in-distribution and out-of-distribution tasks" and "integration of new models without retraining the router" | same | minor: attribute "state-of-the-art" to the authors | no |
| R10 | IRT-Router "enables transparent, cost-aware routing and achieves strong performance–cost trade-offs across **20 LLMs and 12 datasets**" | L85 s4–5 | Song2025 | **yes**. It matches the abstract [A] | same | no | no |
| R11 | RouteLLM "reduces inference cost by **2–3.6×** while retaining approximately **87–95%** of strong-model performance, with minimal routing overhead and good generalization to unseen models" | L85 s6–7 | Ong2025 | **partial** [B]. The paper's Table 6 gives best-router cost-saving ratios over GPT-4 of **3.66× (MT Bench, 95% GPT-4 quality), 1.41× (MMLU, 92%) and 1.49× (GSM8K, 87%)**. The range is therefore about **1.4–3.7×**, not "2–3.6×". The abstract says "over 2 times". The 87–95% quality range is correct. Overhead (§5.5) and transfer to unseen pairs without retraining (§5.3) are supported | same | **yes**: fix the range to match Table 6, or quote the abstract's "over 2×" | no |
| R12 | Arch-Router "maps queries to natural language-defined routing policies based on a Domain–Action taxonomy … enables flexible integration of new models without retraining" | L85 s8–9 | Tran2025 | **yes** [B] | same | no | no |
| R13 | Arch-Router: "A compact 1.5B generative router … achieves **state-of-the-art** performance with **93.17% accuracy** while being **over 28× faster** than competing models" | L85 s10 | Tran2025 | **partial** [B]. 93.17% is the overall score in Table 1, on the **authors' own** preference-routing benchmark. "Over 28 times faster than its closest competitor" compares against Claude-sonnet-3.7 used as a router, with commercial-model latency "benchmarked from OpenRouter" (Table 9). It is therefore a comparison with *proprietary LLMs prompted as routers*, not with other trained routers, and the serving conditions differ | same | **yes**: add "on the authors' benchmark, versus proprietary LLMs prompted as routers" | no |

### 2.6 Table I (L87–107)

| # | Cell or claim | Loc. | Supports? | Issue | Rewrite? |
|---|---|---|---|---|---|
| T1 | TSLT "Sequence-level" | L96 | **no** | TSLT is speculative decoding with per-step logit transmission, so it is token- or step-level, not sequence-level (R6) | yes |
| T2 | TSLT and DiP-SD "Learning-Based ✗" | L96–97 | **yes** | Both are optimisation or systems methods [A] | no |
| T3 | RouteLLM "Lightweight ✗" | L101 | **no** | RouteLLM includes BERT-classifier and matrix-factorisation routers, and its §5.5 reports routing overhead at a small fraction of generation cost [B]. It should be ✓ or ◐ | yes |
| T4 | RouteLMT "System-Aware ✗" | L98 | **partial** | It is explicitly **budget**-aware (cost), though not network-aware. IRT-Router and RouteLLM get "✓ (Cost)" for the same property, so the table is inconsistent | yes |
| T5 | ICL-Router, IRT-Router, RouteLLM, Arch-Router "Adaptive ✓" | L99–102 | **yes** | Consistent with the sources, which undercuts the "Ours" row's claim to be distinctive on this column | — |
| T6 | "Ours": System-Aware (Full) ✓, Learning-Based ✓, Lightweight ✓, Adaptive ✓, Split-LLM ✓ | L104 | **no evidence** | These are claims about a system that has not been built. The table also omits the closest prior art (ConsRoute, PRISM, Bao et al., TMO, Lyra, Hybrid LLM, DABO), several of which would take ✓ on System-Aware, Lightweight and Adaptive (T1 in the gap assessment) | **yes**: rebuild from `research/novelty-matrix.md`, and mark "Ours" as "proposed" |

### 2.7 Problem formulation (L137–191)

| # | Claim | Loc. | Supports? | Issue | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|
| P1 | Cloud hosts "powerful LLMs **or Split-LLMs**". The TLM router is deployed at the edge | L151–152 | n/a | A Split-LLM is not hosted *in the cloud*: by definition it spans edge and cloud. The action set {edge SLM, split(d), cloud} is never written down (deliverable 9, constraint 1) | **yes** | no |
| P2 | "offload q (or part of it, in Split-LLM settings)" | L158 | n/a | A split offloads *layers* (activations of all of q), not "part of q". It is conflated with prompt partitioning | **yes** | no |
| P3 | C(M_k, q) "may include computation, communication, and latency" | L165 | n/a | Never defined. The cost models at L233–265 are monetary only, so latency and communication never enter Eq. 2 | **yes**: define C and the units of λ | **yes**: measured cost table |
| P4 | Eq. 2 maximises E[U − λC] | L171 | n/a | Well-formed as an objective. But Eq. 3's argmax over f_θ has no λ, so it cannot trade off cost at inference time unless f_θ is retrained per λ. That contradicts K3 | **yes**: make Eq. 3 score predicted U minus λ times a measured C (deliverable 9) | no |
| P5 | "Query understanding: accurate routing requires capturing query complexity, intent, and **uncertainty**" | L180 | n/a | There is no uncertainty term anywhere in Eqs. 1–3 (F2) | yes | yes, if calibration is claimed |
| P6 | "f_θ … a lightweight scoring function learned by the TLM … enabling fast routing with minimal overhead while **maintaining high-quality inference**" | L191 | n/a | This is a result claim (F5). "Scoring function" also describes a discriminative classifier, which undercuts the need for a *language model* (deliverables 6 and 9) | **yes**: phrase it as a design goal | **yes** |

### 2.8 Experimental setup (L199–320)

| # | Claim | Loc. | Current citation | Supports? | Evidence / better source | Rewrite? | Exp. evidence? |
|---|---|---|---|---|---|---|---|
| E1 | "we **established** a testbed … Intel Xeon W-2123, 64 GB, 2× RTX 3090 … The cloud environment is hosted on a dedicated server, which is equipped with ..." | L202 | none | n/a | The edge hardware is stated but **unverifiable by us**. The cloud server is unspecified ("..."). The edge server "executes the client-side Split-LLM computation", yet no edge-*SLM* hardware (phone or Jetson) is described, so "edge device" (L150) and "edge server" are conflated | **yes**: complete it or mark it TODO. Distinguish edge device from edge server | **yes**: hardware logs (`nvidia-smi`, `lscpu`) |
| E2 | "We evaluate … on the SimpleQA dataset **with pre-computed inference results in LLMRouterBench**" | L205 s1 | sqa, dataset | **no** | SimpleQA exists in LLMRouterBench **only** in the performance-cost setting, whose 13–15 models are flagship API models. **None of the manuscript's weak or strong models has SimpleQA records.** Of the whole pool, only Llama-3.1-8B-Instruct appears in the bundle at all, and not on SimpleQA (`research/raw/experiment/inventory_output.txt`, lines 680–700; iterations 10–11) | **yes** | **yes**: our own inference runs |
| E3 | "SimpleQA consists of **4,326** short factual questions" | L205 s2 | sqa | **yes**. The bundle's `simpleqa/test` has n = 4326 per model [run: inventory_output.txt L697–700]. The paper's abstract does not state the count | — | no | no |
| E4 | "Compared with larger multi-task benchmarks such as MMLU-Pro, SimpleQA offers a computationally efficient yet **sufficiently diverse** evaluation setting for studying query-level routing" | L205 s3 | none | **unsupported** [O] | SimpleQA is adversarially collected against GPT-4 and has one indisputable answer per question [A]. It measures *factual recall*, where small models score near zero (even the released *flagship* models score only 0.15–0.54 on the bundle's `simpleqa/test`, [run: inventory_output.txt L697–711]), so the edge SLM would rarely be correct and the oracle would call the cloud for almost everything. One task type also cannot support the "adaptable/generalises" claims | **yes**: justify it, or use a multi-domain pool (deliverable 10 Stage 0 uses 6 datasets) | **yes**: headroom check |
| E5 | "Since SimpleQA is already directly integrated into LLMRouterBench, routing labels can be automatically constructed without repeatedly executing every … pair of SLMs and Split-LLMs" | L205 s4 | dataset | **no** | See E2. Also, a Split-LLM computes the **same function** as its unsplit model (lossless split), so quality labels cannot distinguish SPLIT from CLOUD. Split-specific labels must be measured (iteration 11 learning) | **yes** | **yes** |
| E6 | TTFT "captures the latency of the prefill phase, including prompt processing on the edge device, activation transmission to the cloud, and server-side computation". T_total = TTFT + (N−1)·TPOT | L211–218 | none | n/a (standard definitions) | Standard serving metrics. For the Split path, TPOT also contains a WAN round trip per token, which the in-browser split study reports is invariant to split depth [A] | minor: the formula ignores router latency, which should be added as a term | **yes** |
| E7 | "since the proposed framework **targets serverless cloud environments**, we measure … cold-start events" | L221 | none | n/a | Serverless is mentioned nowhere else: not in the problem, contributions or formulation. The Split-LLM server side must hold per-session KV state, which sits uneasily with stateless serverless functions [O] | **yes**: either motivate serverless in §I/§III or drop it | **yes** |
| E8 | Throughput via RPS and TPS "to evaluate system scalability" | L224 | none | n/a | Standard metrics. "Scalability" requires a concurrency sweep, which is not specified | minor | **yes** |
| E9 | Cost per request from "RunPod" and "RunPod Flex" pricing | L231–247 | **none** | n/a | No price, date or URL is given. Prices change, so a snapshot (date plus archived page) is needed. Not fetched by us | **yes**: cite a dated pricing page | no (it is an estimate, but must be labelled as one) |
| E10 | Edge cost = E_query·R_elec + C_device/L | L253 | none | n/a | A reasonable model. E_query must be **measured** (power logging), and C_device and L are assumptions to be stated | minor | **yes** (E_query) |
| E11 | "**Gemma-4-E2B-A4B**: A lightweight **2B-parameter** instruction model"; "Gemma-4-E4B-A4B: A 4B-parameter variant"; "Gemma-4-12B-A4B" | L273–277 | none | **no** | The official IDs are `google/gemma-4-E2B-it`, `E4B-it` and `12B-it`. **No "-A4B" suffix exists for them**; the only A4B model is `gemma-4-26B-A4B-it`. E2B stores **5.12B** parameters ("E" means *effective*) [api; reproducibility plan §5] | **yes** | no |
| E12 | "Phi-4-mini-3.8B: … compact model designed for efficient reasoning and code generation" | L280 | none | **partial** | `microsoft/Phi-4-mini-instruct`, 3,836,021,760 parameters, MIT [api]. The capability description is not checked; cite arXiv 2503.01743 (tag on the HF card [api]) | minor | no |
| E13 | "Meta-Llama-3.1-8B-Instruct: … a strong baseline among current SLMs" | L282 | none | **partial** | The model exists and is gated under the llama3.1 licence [api]. At 8B it is at the upper edge of "SLM"; in LLMRouterBench it is in the ~7–9B "performance" pool | minor | no |
| E14 | "LLaDA-MoE-7B-A1B-Instruct-**Q4**: … competitive reasoning performance while activating only a small subset of parameters" | L286 | none | **partial** | `inclusionAI/LLaDA-MoE-7B-A1B-Instruct` exists in BF16 (Apache-2.0). A Q4 build exists only as community GGUF files [api] | **yes**: name the exact quantised artefact | whether 4-bit diffusion LMs run is [?] |
| E15 | "Dream-v0-Instruct-7B: A diffusion language model **from Huawei Noah's Ark Lab** … **with top-tier performance**" | L288 | none | **partial** | The checkpoint is `Dream-org/Dream-v0-Instruct-7B` (Apache-2.0) [api], and the README links an HKU NLP blog (`hkunlp.github.io/blog/2025/dream`). We did **not** verify the attribution to Huawei Noah's Ark alone. "Top-tier performance" is uncited | **yes**: cite the Dream paper and correct the attribution; drop "top-tier" | no |
| E16 | "Fast-dLLM-v2-7B: … adapts a pretrained AR model (Qwen2.5-7B-Instruct) into a diffusion-style decoder" | L290 | none | **yes** [api: the card lists base Qwen2.5-7B-Instruct] | Note that the Jacobi Forcing paper's Table 6 reports Fast-dLLM v2 at 63.4% HumanEval against 87.8% for AR (deliverable 6) | minor: add a citation | no |
| E17 | "All models are deployed using 4-bit quantization to reduce GPU memory consumption during Split-LLM execution" | L295 | none | n/a | Llama-3.3-70B at 4 bits is ~35 GB of weights [E], which exceeds one 24 GB RTX 3090, so it needs both edge GPUs or a split. The effect of quantisation on quality labels must be measured, because published scores are usually BF16 | minor | **yes** |
| E18 | "**Qwen3-72B-Instruct**: Alibaba's flagship 72B instruction-tuned model with state-of-the-art … capabilities" | L298 | none | **no** | **No official Qwen3-72B checkpoint exists.** The Qwen org's 72B models are Qwen/Qwen2/Qwen2.5. HF hits for "Qwen3-72B" are community merges [api: `raw/repro/hf_search_Qwen3-72B.json`, `hf_search_Qwen_author_72B.json`] | **yes**: pick a real model (Qwen2.5-72B-Instruct, Qwen3-32B or Qwen3-235B-A22B-2507); this is an advisor decision | no |
| E19 | "Llama-3.3-70B-Instruct: **Meta's latest** 70B instruction model" | L300 | none | **partial** | It exists and is gated with manual approval [api]. "Latest" is date-sensitive and should be removed | minor | no |
| E20 | "NVIDIA Nemotron-3 Nano-30B: NVIDIA's 30B reasoning-oriented language model" | L302 | none | **partial** | The official name is `NVIDIA-Nemotron-3-Nano-30B-A3B` (MoE, 31.6B stored, about 3B active), under the NVIDIA Nemotron Open Model License [api]. "Relatively smaller parameter count" ignores that only about 3B parameters are active, which matters for any latency comparison | **yes**: give the full name and MoE status | no |
| E21 | Baselines are "slightly adapted" and the "adaptations enable a **controlled and fair comparison**" | L306, L320 | none | n/a | Fairness is asserted, not shown. Replacing model pairs, labels, heads and cost functions (L306) is a substantial re-implementation | **yes**: list each change per baseline | **yes** |
| E22 | RouteLMT "learns a lightweight in-model router from the prompt-token representations of a small translation model"; "we replace the translation-specific backbone" | L311 | Luo2026 | **yes** for the description [A] | **The NiuTrans/LMT repo contains no router code**: its tree has 12 entries, only `src/inference.py` and utils (`raw/repro/gh_tree_NiuTrans_LMT.json`). The baseline must be described as a **re-implementation from the paper** | **yes** | **yes** |
| E23 | ICL-Router's two-stage description | L313 | Wang2026 | **yes**. It matches the abstract closely [A] | The training scripts in its README assume 8 GPUs (reproducibility plan) | no | **yes** |
| E24 | RouteLLM's "cost-aware decision threshold is also calibrated according to the measured computational and communication costs" | L315 | Ong2025 | **partial** | RouteLLM's cost threshold α turns the predicted win probability into a decision. The paper sweeps α to trace call-performance curves, reported as APGR and CPT (the minimum % of strong-model calls needed to reach a target PGR) [B, §3]. It does not map α to measured compute or communication cost. Mapping a cost budget to a threshold is our adaptation and must be described as such | minor | **yes** |
| E25 | Arch-Router: "fine-tune its **routing head**" | L317 | Tran2025 | **no** | Arch-Router-1.5B is a generative model (`pipeline_tag=text-generation`, base Qwen2.5-1.5B-Instruct). It outputs a route name as text and has no separate routing head [api; deliverable 7] | **yes**: "fine-tune the model to generate the route label" | **yes** |
| E26 | "The principal representation-learning and routing strategies of each baseline remain unchanged, ensuring that the comparison reflects their core methodological characteristics" | L320 | none | n/a | E22 (no code) and E25 (no head) contradict "unchanged" for two of the four baselines. No simple baselines are included, although LLMRouterBench shows they are competitive. Our Stage-0 run supplies such baselines (TF-IDF+LR, random at matched call rate, dataset prior, oracle) | **yes**: add the simple baselines | **yes** |

---

## 3. Special-attention phrases

| Phrase class | Occurrences | Verdict |
|---|---|---|
| **"novel"** | L61 ("novel routing architecture") | Superseded (K1; G7 and C1 in deliverable 8). No novelty claim survives unless it is narrowed to the Split-LLM action and its evaluation (deliverable 8 §3) |
| **"unlike existing methods"** | L40 s6, L61 | Both are contradicted by prior work *and by the manuscript's own L85* (A7, K1) |
| **"without (costly) retraining"** | L40 s6, L65 | Pre-empted (ICL-Router, Arch-Router, CSCR, HyDRA). It is also internally unsupported: Eq. 3 has no λ and no mechanism for new models. Our Stage-0 run showed dev-tuned thresholds failing under dataset shift (A7, K3, P4) |
| **privacy claims** | L40 s2 "privacy-aware", L48 "sensitive data remains local", L63 "privacy-sensitive settings" | The split-learning citations do not support split-inference privacy. Activation inversion is documented (Cunningham 2602.16760 [B]). The manuscript has no privacy variable, threat model or leakage metric (I4, R2, R3, K2). Every privacy claim needs a measured leakage-vs-split-depth curve or must be removed |
| **latency claims** | L40 s5 "low-latency decision-making", L61 "achieves low-latency decision-making suitable for real-time deployment", L191 | No latency has been measured. The router's own latency is missing from the T_total formula (E6). ConsRoute's Table III [B] reports that a generative tier choice is slower than a hidden-state probe, which is direct evidence against a *generative* router being the low-latency option |
| **scalability claims** | L40 s6 "scalable", L40 s8 "scalable solution", L65 "improving scalability", L224 | Undefined (scale of what: the model pool, users or requests?). There is no concurrency sweep and no pool-growth experiment |
| **"extensive experiments demonstrate…"** | L40 s7–8, L67 | **No experiment exists.** §V is ".", the testbed stops at "…", and the dataset plan is unworkable as written (E2, E5). These must be deleted or recast in the future tense |
| **empty sections** | §IV Proposed Solution (L195), §V Results (L324–333), Conclusion (L337) | The paper's method is unspecified. Every claim that depends on the method (A5, A6, K1–K4, P6) is therefore unverifiable in principle, not merely unverified |

---

## 4. Tally

Rows in §2: 9 abstract + 13 introduction + 4 contributions + 13 related work +
6 Table I + 6 formulation + 26 setup = **77 audited claims**. For rows with no
citation that assert a checkable fact (Table I cells, model names, dataset
facts), "Supports?" records whether the evidence supports the claim.

| "Supports?" value | Count | Rows |
|---|---|---|
| **yes** | 14 | I6, I11, R4, R7, R8, R9, R10, R12, T2, T5, E3, E16, E22, E23 |
| **partial** | 17 | I2, I3, I7, I8, R2, R5, R6, R11, R13, T4, E12, E13, E14, E15, E19, E20, E24 |
| **no** | 9 | I4, R3, T1, T3, E2, E5, E11, E18, E25 |
| no evidence / unsupported | 2 | T6, E4 |
| n/a (no citation; a design statement, definition or proposal) | 35 | A1–A9, I1, I5, I9, I10, I12, I13, K1–K4, R1, P1–P6, E1, E6–E10, E17, E21, E26 |

| Other counts | Count | Rows |
|---|---|---|
| Rewrite **yes** | 49 | |
| Rewrite **minor** | 19 | A3, I1, I2, I5, I9, R1, R4, R5, R8, R9, E6, E8, E10, E12, E13, E16, E17, E19, E24 |
| No rewrite | 9 | I6, I11, R7, R10, R12, T2, T5, E3, E23 |
| Needs our own experimental evidence (unconditionally) | 27 | A5–A9, I8, K1–K4, P3, P6, E1, E2, E4–E8, E10, E17, E21–E26 |
| Needs it only if the claim is kept | 5 | A1, I4, R3, P5, E14 |
| Wrong about a named artefact (model, dataset, repo) | 5 | E2, E5, E11, E18, E25 |
| Asserts a result that has no evidence at all | 6 | A8, A9, K1, K4, P6, T6 |

Table I rows (T1–T6) have no experimental-evidence column and are not counted
in the two experimental-evidence rows. These counts were made by hand from the
tables above, and a second pass checked that each of the first three blocks sums
to 77. They have not been independently recounted.

---

## 5. Instructions carried into `paper/main-revised.tex` (deliverable 15)

1. **Delete** A8, A9 and K4. Recast every result as a hypothesis with a named
   test (deliverable 10, H1–H3).
2. **Replace** the L40 opening sentence (A2) with original wording and cite
   Li et al. (ACM CSUR 2026).
3. **Replace** the split-learning citations for split-*inference* privacy (I4,
   R2) with split-inference sources and a qualified statement about activation
   leakage.
4. **Fix** the model pool (E11, E18, E20) and the dataset plan (E2, E5). SimpleQA
   labels for our models require our own inference. Stage 0 uses the released
   LLMRouterBench performance-setting scores instead.
5. **Correct** the RouteLLM numbers (R11), Arch-Router's framing (R13, E25), the
   TSLT paraphrase (R6) and the RouteLMT code status (E22).
6. **Rebuild** Table I from `research/novelty-matrix.md`, including the closest
   prior art, with the "Ours" row marked as *proposed*.
7. **Define** C(M_k, q), λ, the action set {EDGE, SPLIT(d), CLOUD} and a λ-aware
   Eq. 3 (P1–P4), following `architecture/options.md`.
8. **Fix** bibliography metadata (§1) and remove or cite Ford2025.
9. Keep the setup's metric definitions (E6, E8, E10), but add router latency
   and state which quantities are measured and which are estimated.

## 6. Unresolved items

- **Mix-or-Split** (IEEE TPDS 37(11), pp. 2423–2439, Nov 2026, doi
  10.1109/TPDS.2026.3729256; the page range was confirmed via Crossref this
  iteration) is **still unread**. It is closed access, and neither Crossref nor
  OpenAlex has an abstract. It remains the main risk to the residual gap (U1)
  on which the revised framing depends.
- CITER "preference-based learning" (R5), TSLT "token-tree verification"
  (R6) and Phi-4-mini's capability wording (E12) were checked against
  abstracts only.
- The Dream attribution (E15) and the ICML 2024 proceedings entry for SnD
  (Mai2023) were not verified at the proceedings or paper level.
- The HIPAA primary source (I3) and the RunPod pricing pages (E9) were not
  fetched.
- The testbed hardware (E1) cannot be verified by us. It needs the authors'
  own logs.
- The tallies in §4 are hand counts, checked only for summing to 77.
