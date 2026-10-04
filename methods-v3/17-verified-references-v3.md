# 17 — Verified references register (v3)

*Deliverable 17 of `MICROENCODER_HARDENING_BRIEF.md` §27 (brief §8 and §23).
Prepared 2026-10-04 (gnhf run `microencoder-hardeni-d272f9`, iteration 19).
Companion file: `method-references-v3.bib` (44 entries). This register
replaces `methods-v2/17-verified-references.md` and `methods-v2/method-references.bib`,
which are left unchanged.*

**Purpose.** For every source that v3 relies on, this file records the exact
identity, where that identity was confirmed, the inspection level, the sections
that support each load-bearing claim, and whether the claim is a fact about
the paper, an author claim, or our interpretation. `proposed-solution-blue-v3.tex`
may cite **only** the keys in §2, and only for the claim types allowed in the
"may support" column. `16-citation-audit.md` checks each manuscript sentence
against that column.

---

## 0. Protocol

* **Identity check (all 44 .bib entries, 2026-10-04).** Every title, author
  list, venue, year, page range and DOI in the .bib was re-fetched in this
  iteration from one official record. Nothing was copied from methods-v2. The
  records used were:
  * **Crossref** `api.crossref.org/works/<DOI>` for every entry with a DOI
    (ACM, IEEE, ACL Anthology, NeurIPS `10.52202/…`, FITEE, report DOI);
  * **proceedings.iclr.cc** `citation_*` meta tags (RouteLLM 2025, Hybrid LLM
    2024, Ettin 2026);
  * **papers.nips.cc** meta tags (Müller 2019, MiniLM 2020, Stanton 2021);
  * **proceedings.mlr.press** meta tags (Guo v70, Furlanello v80, Menon v139,
    Mai v235, BEST-Route v267 `ding25d`);
  * **arXiv abs pages** `citation_*` meta tags plus comments/journal-ref for
    every arXiv ID in the .bib (43 entries carry an `eprint`), for preprints and as a cross-check of proceedings entries.
* **Conflict rule.** Where the proceedings record and arXiv disagree, the
  .bib copies the **proceedings** record. The disagreement is logged in §4.
* **Body inspection** was done in earlier v3 iterations. The file and section
  where each body read is recorded are given in the "Body read in" column. No
  new body reads were done in this iteration. The level in this register is
  therefore the level recorded in those files, not a new claim.
* **Tags** follow brief §29. Additional column values:
  * **BODY-partial**: only the named sections were read. Citations are limited
    to those sections.
  * **ABS**: abstract or landing page only.
* **Unreachable from this machine:** dblp (bot challenge), OpenReview API
  (403 challenge), Semantic Scholar API (429). Consequences: DeBERTaV3's ICLR
  2023 venue rests on the iclr.cc virtual-site listing, with no page range.
  Lopez-Paz (ICLR 2016) and FitNets (ICLR 2015) rest on arXiv/secondary
  evidence only and are flagged.

---

## 1. Coverage of brief §8 priority lists

| Brief §8 item | v3 status | Key | Body read in |
|---|---|---|---|
| RouteLLM | `[VERIFIED-BODY]` (arXiv v1 + v4, repo) | `ong2025routellm` | `05` §1.1, `04` |
| RouterDC | `[VERIFIED-BODY]` (arXiv v1, repo) | `chen2024routerdc` | `05` §1.2 |
| HyDRA | `[VERIFIED-BODY]` (v1 + v2) | `garg2026hydra` | `05` §1.3, §3 |
| LLMRouterBench | `[VERIFIED-BODY]` + repo | `li2026llmrouterbench` | `05` §1.4, §4; `08` §6.1 |
| ConsRoute | `[VERIFIED-BODY]` (v1 only) | `qiao2026consroute` | `05` §1.5 |
| Hybrid-LLM | `[VERIFIED-BODY]` | `ding2024hybridllm` | `05` §1.6 |
| BEST-Route | `[VERIFIED-BODY]` (v1) | `ding2025bestroute` | `05` §1.7 |
| Prefill-activation / hidden-state routing | `[VERIFIED-BODY]` (v3); ConsRoute also uses a hidden-state router | `varshney2026prefill` | `05` §1.8 |
| ModernBERT | `[VERIFIED-BODY]` + `[ARTIFACT]` (config, HF API) | `warner2025modernbert` | `07` §1 |
| Split-LLM / collaborative-inference systems | BODY: Edgent, SPINN, MCDNN (tech report), EdgeRL, Bao et al., NetGPT-routing, CR², Splitwise-UCC, Chen FITEE; META: Neurosurgeon, survey | §2.4 keys | `06` §1 |
| Foundational KD paper | `[VERIFIED-BODY]` (§1, §2, §2.1, §6) | `hinton2015distilling` | `04` §6 |
| Calibration paper | `[VERIFIED-BODY]` (§2, §3, §4.1, §4.2) | `guo2017calibration` | `03` §13 |
| Arch-Router (B) | `[VERIFIED-BODY]` (v1) | `tran2025archrouter` | `05` §1.9 |
| RouteLMT (B) | `[VERIFIED-BODY]` (v1, §3, §4, §5.1–5.3, Limitations) | `luo2026routelmt` | `11` §2 |
| IRT-Router (B) | `[VERIFIED-BODY]` | `song2025irtrouter` | `05` §1.10 |
| DistilBERT (B) | **not read in v3** → excluded from .bib | — | — |
| TinyBERT (B) | **not read in v3** → excluded from .bib | — | — |
| MiniLM (B) | `[VERIFIED-META]` only (abstract + official card) | `wang2020minilm` | `07` §2 |
| Ranking KD (B) | v2's PLaD / PAD were abstract-only and are generative-LM KD. **Not read in v3** → excluded. `03` §6 argues from first principles, not from them | — | — |
| Edge/cloud collaborative-inference surveys (B) | META: Matsubara (ACM CSUR 2022). Li et al. arXiv 2507.16731 taxonomy BODY in `06` but not in .bib | `matsubara2022splitsurvey` | `06` §1.5 |

**Shortfall against brief §8.** DistilBERT, TinyBERT and ranking-KD papers
were not body-read. None of them carries a v3 decision: `03` does not use
them, and `07` drops DistilBERT from the backbone short-list. They are excluded
from the .bib rather than cited at META level. The MiniLM body is also unread,
so `wang2020minilm` may support only "MiniLM is a distilled compact encoder
family" (existence).

---

## 2. Register of .bib entries

Column guide. **Level** is the inspection level of the *content*, not of the
identity: identity is confirmed for all rows per §0. **May support** lists the
sentence types the blue manuscript may attach this key to. Any other use needs
a further body read first. **[C]** marks quantitative results that may be
quoted only as author claims.

### 2.1 LLM routing

| Key | Exact title (as cited) | Authors | Venue / status, year | IDs | Repo | Level | Load-bearing locators | May support |
|---|---|---|---|---|---|---|---|---|
| `ong2025routellm` | RouteLLM: Learning to Route LLMs from Preference Data | Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica | ICLR 2025, pp. 34433–34448 | arXiv 2406.18665 | `lm-sys/RouteLLM` | BODY | Eq. 1–2 (P(win_strong\|q), threshold α); §4.1 (Arena votes, D_gold, D_judge labelled "using GPT-4 as a judge"); §4.2 Eq. 13 (BERT classifier); §5.1/§6 ("dataset augmentation"); §6 (two-model limitation); Table 7 overhead **[C]** | Binary strong/weak routing from preference data; LLM-as-judge **preference supervision / data augmentation with hard labels** (`04` ruling). **Not** "knowledge distillation" |
| `chen2024routerdc` | RouterDC: Query-Based Router by Dual Contrastive Learning for Assembling Large Language Models | Chen, Jiang, Lin, Kwok, Zhang | NeurIPS 2024 (NeurIPS 37), pp. 66305–66328 | DOI 10.52202/079017-2120; arXiv 2409.19886 | `shuhao02/RouterDC` | BODY | Eq. 1–3 (per-LLM score labels; cosine between mDeBERTaV3-base query embedding and learnable LLM embeddings, softmax over LLMs); dual contrastive losses | Multi-LLM query routing with learned model embeddings; contrastive (not KD) training |
| `garg2026hydra` | HyDRA: Hybrid Dynamic Routing Architecture for Heterogeneous LLM Pools | Garg, Singha Roy, Jang, Brancasi, Fu (arXiv list; v2 PDF also lists Cianci) | Preprint (arXiv "preprint v2"), 2026 | arXiv 2605.17106 | none public | BODY | Abstract, §1, §3.1 (ModernBERT-base + 4 sigmoid **capability-requirement** heads); App. H Eq. 3–5 (static model capability profiles, shortfall, cheapest eligible); Eq. 7 (judge-derived targets); §1/§8/§9 "zero retraining" via YAML profile **[AUTHOR-CLAIM]**; App. F Table 19 encoder ablation **[C]** | Capability-requirement routing with model profiles; ModernBERT used as a router encoder in prior work. **Never** "per-model heads like ours" (`05` §3) |
| `li2026llmrouterbench` | LLMRouterBench: A Massive Benchmark and Unified Framework for LLM Routing | Li, Zhang, Guo, Wang, Tang, Zhang, Chen, Qi, Ye, Bai, Wang, Hu | Findings of ACL 2026, pp. 37733–37754 | DOI 10.18653/v1/2026.findings-acl.1881; arXiv 2601.07206 | `ynulihao/LLMRouterBench` | BODY | Abstract + §4.2.1 ("limited impact" of embedding models); App. Table 10 (3 **frozen** embedders × 3 embedding routers, ≤2.2 pt spread, no significance test); dataset/pool counts (21 datasets, 33 models) | Only the bounded sentence in `05` §4. Never "encoder choice does not matter" |
| `qiao2026consroute` | ConsRoute: Consistency-Aware Adaptive Query Routing for Cloud-Edge-Device Large Language Models | Qiao, Zhang, Mao, Cheng, Liu | Unrefereed preprint, 2026 | arXiv 2603.21237 | none | BODY (v1) | Eq. 2, 7–8 (frozen device-LM EOS prefill state → MLP consistency score); Alg. 1–2, Eq. 9–11 (cluster thresholds re-tuned by BO every 200 queries); §V-A (emulated link profiles; tiers Qwen3-1.7B/14B/32B); Table III **[C]** | Device/edge/cloud LLM routing with a hidden-state router and latency in the tuning objective; network not a router input |
| `ding2024hybridllm` | Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing | Ding, Mallick, Wang, Sim, Mukherjee, Rühle, Lakshmanan, Awadallah | ICLR 2024, pp. 41348–41366 | arXiv 2404.14618 | `m365-core/hybrid_llm_routing` | BODY | §4.1 (DeBERTa-v3-large router); Eq. 1–4 (r_det hard; r_prob soft label from 10 samples; r_trans); §2.3 (cost = share of queries to the small model); §5 (two models) | Small/large routing with **empirical soft labels from repeated sampling** (the non-KD soft-target precedent) |
| `ding2025bestroute` | BEST-Route: Adaptive LLM Routing with Test-Time Optimal Compute | Ding, Mallick, Zhang, Wang, Madrigal, Hipolito Garcia, Xia, Lakshmanan, Wu, Rühle | ICML 2025, PMLR 267:13870–13884 | arXiv 2506.22716 | `microsoft/best-route-llm` | BODY (v1) | Eq. 3–5 (DeBERTa-v3-small + one sigmoid head per (model, best-of-n) action, BCE on Pr[reward ≥ reference]); Alg. 1 (cheapest action above threshold); 60% cost **[C]** | Precedent for **action-level** heads when the action changes the output distribution (our lossy branch) |
| `varshney2026prefill` | LLM Router: Rethinking Routing with Prefill Activations | Varshney, Surla, Xu, Krishnan, Jeblick, Austin, Vaidya, Onofrio | Preprint, 2026 (v3 title; v1 "Prefill is All You Need") | arXiv 2603.20895 | none found | BODY (v3) | §3.1 (encoder-LLM activations, Fisher-J layer choice, PCA-100, per-target P(correct) heads, BCE); Eq. 1–2 (λp̂ − (1−λ)C̃); Table 3 AUC **[C]**; App. I overhead **[C]** | Hidden-state/prefill-activation routing baseline; per-model P(correct) with an additive cost term |
| `tran2025archrouter` | Arch-Router: Aligning LLM Routing with Human Preferences | Tran, Paracha, Hafeez, Chen | Preprint, 2025 | arXiv 2506.16655 | HF `katanemo/Arch-Router-1.5B` | BODY (v1) | Generative policy-ID router (Qwen2.5-1.5B); App. B Table 9 **[C]** | Generative-router baseline option only |
| `song2025irtrouter` | IRT-Router: Effective and Interpretable Multi-LLM Routing via Item Response Theory | Song, Huang, Cheng, Gao, Xu, Zhao, Wang, Wu | ACL 2025 (Long), pp. 15629–15644 | DOI 10.18653/v1/2025.acl-long.761; arXiv 2506.01048 | `Mercidaiha/IRT-Router` | BODY | Eq. 1 (S = αP̂ − βC); Eq. 4–5 (P̂ = σ(aᵀθ_M − b), model enters through a profile embedding) | Model-as-input routers, the architecture class required for zero/few-shot pool expansion (Issue B) |
| `xue2026cr2` | CR²: Cost-Aware Risk-Controlled Routing for Wireless Device-Edge LLM Inference | Xue, Chen, Chen, Yao, Sun, Hu, Tao | Preprint ("submitted to IEEE Journal"), 2026 | arXiv 2605.12001 | none found | BODY (§IV, §VI, §VII) | Eq. 4–18 (u = y − λ·c(x,ξ), wireless latency + energy normalised scalar, Eq. 17); §VI (per-model sigmoid heads on frozen all-MiniLM-L6-v2; on-device gate distilled from a privileged teacher's utility margins, §VI-E); §VII (fixed 18 ms RTT, simulated fading) | Prior multi-model routing with a wireless cost term **and** router-to-router distillation. Must be cited wherever we describe our utility-minus-cost rule or router KD |
| `bao2025qualitylatency` | Dynamic Quality-Latency Aware Routing for LLM Inference in Wireless Edge-Device Networks | Bao, Xue, Sun, Chen | IEEE/CIC ICCC Workshops 2025, pp. 1–6 | DOI 10.1109/ICCCWorkshops67136.2025.11147210; arXiv 2508.11291 | none found | BODY (§III, Eq. 6–12) | p̃ = p − α(T_edge − T_local), thresholded; BERT router adopted from RouteLLM; binary device/edge | Prior "quality minus latency penalty" LLM routing at the network edge |
| `chen2025netgptrouting` | Optimizing NetGPT via Routing-Based Synergy and Reinforcement Learning | Chen, Li, Chen, Wu, Peng, Zhao, Zhang | Preprint, 2025 (venue unverified) | arXiv 2511.22217 | none found | BODY (§IV) | Eq. 28 (τ = τ₀ − α·RTT + β·BW, network-adaptive threshold); Eq. 2, 5, 8, 29 | Prior learned edge/cloud routing whose threshold adapts to live RTT/BW |
| `luo2026routelmt` | RouteLMT: Learned Sample Routing for Hybrid LLM Translation Deployment | Luo, Liu, Lin, Chang, Wang, Li, Du, Xiao, Zhu | ACL 2026 Industry Track, pp. 1886–1897 | DOI 10.18653/v1/2026.acl-industry.129; arXiv 2604.22520 | see `11` §2 | BODY (v1 sections in `11`) | per `11` §2 card | Related learned routing (translation). Not load-bearing in the blue tex |
| `wang2025iclrouter` | ICL-Router: In-Context Learned Model Representations for LLM Routing | Wang, Li, Zhang, Chen, Chen, Jian, Ye, Zhang, Hu | arXiv 2025 (comment: "Accepted by AAAI 2026"; proceedings not checked) | arXiv 2510.09719 | per `11` §2 | BODY (v3 sections in `11`) | §3.1–3.4 (model representations learned in context) | Model-representation routing as a pool-expansion baseline (`11`) |
| `zheng2023judging` | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng, Chiang, Sheng, Zhuang, Wu, Zhuang, Lin, Li, Li, Xing, Zhang, Gonzalez, Stoica | NeurIPS 2023 Datasets & Benchmarks (NeurIPS 36), pp. 46595–46623 | DOI 10.52202/075280-2020; arXiv 2306.05685 | — | META + abstract | Abstract ("scalable and explainable way to approximate human preferences") | The term "LLM-as-a-judge" only |

### 2.2 Knowledge distillation and calibration

| Key | Title | Authors | Venue, year | IDs | Level | Load-bearing locators | May support |
|---|---|---|---|---|---|---|---|
| `hinton2015distilling` | Distilling the Knowledge in a Neural Network | Hinton, Vinyals, Dean | NIPS 2014 Deep Learning Workshop (arXiv, 2015) | arXiv 1503.02531 | BODY | §2 (softened softmax with temperature, weighted soft + hard objective, T² scaling); §2.1; §6 | Definition of soft-target KD; the mixed-target student loss form |
| `guo2017calibration` | On Calibration of Modern Neural Networks | Guo, Pleiss, Sun, Weinberger | ICML 2017, PMLR 70:1321–1330 | arXiv 1706.04599 | BODY | §2 (ECE); §3 (capacity/NLL overfitting → miscalibration); §4.1 (Platt / binary); §4.2 (temperature scaling, argmax unchanged) | Post-hoc calibration (Platt/temperature) as the calibration step and the non-KD calibration control |
| `muller2019labelsmoothing` | When does label smoothing help? | Müller, Kornblith, Hinton | NeurIPS 2019 (NeurIPS 32) | arXiv 1906.02629 | BODY | §3 (label smoothing ≈ temperature scaling for ECE); §4 (LS teachers distil worse) | Label smoothing as a non-KD regularisation control; LS-trained teachers can hurt distillation |
| `menon2021statistical` | A statistical perspective on distillation | Menon, Rawat, Reddi, Kim, Kumar | ICML 2021, PMLR 139:7632–7642 | arXiv 2005.10419 (title "Why distillation helps: a statistical perspective") | BODY (arXiv version) | §3 (Bayes-class-probability teacher reduces variance; §3.2 bias–variance trade-off) | Why soft targets can help even with the same data (variance reduction), stated as their argument |
| `lopezpaz2016unifying` | Unifying distillation and privileged information | Lopez-Paz, Bottou, Schölkopf, Vapnik | ICLR 2016 (arXiv journal-ref; no proceedings page checked) | arXiv 1511.03643 | BODY | §2; §4 (generalized distillation); §4.1 | Teacher with privileged information (T-PI) |
| `stanton2021kd` | Does Knowledge Distillation Really Work? | Stanton, Izmailov, Kirichenko, Alemi, Wilson | NeurIPS 2021 (NeurIPS 34), pp. 6906–6919 | arXiv 2106.05945 | BODY-partial (abstract, §1) | Abstract/§1 (students often do not match teacher predictions; fidelity ≠ generalisation) | Caution that KD gains are not guaranteed |
| `furlanello2018bornagain` | Born Again Neural Networks | Furlanello, Lipton, Tschannen, Itti, Anandkumar | ICML 2018, PMLR 80:1607–1616 | arXiv 1805.04770 | BODY-partial (§3.2) | §3.2 (gradient decomposition: dark knowledge vs confidence weighting) | Same-capacity self-distillation; decomposition of the KD gradient |
| `cho2019efficacy` | On the Efficacy of Knowledge Distillation | Cho, Hariharan | ICCV 2019, pp. 4793–4801 | DOI 10.1109/ICCV.2019.00489; arXiv 1910.01348 | BODY-partial (§5.2, §5.3) | §5.2 (larger teachers are not always better teachers; capacity gap) | Teacher-capacity caution |
| `yuan2020revisiting` | Revisiting Knowledge Distillation via Label Smoothing Regularization | Yuan, Tay, Li, Wang, Feng | CVPR 2020, pp. 3902–3910 | DOI 10.1109/CVPR42600.2020.00396; arXiv 1909.11723 | BODY-partial (abstract, §2.1–2.2, §3) | §2–3 (KD as learned label smoothing; poorly trained or smaller teachers still help) | KD vs label-smoothing control |
| `kim2016sequence` | Sequence-Level Knowledge Distillation | Kim, Rush | EMNLP 2016, pp. 1317–1327 | DOI 10.18653/v1/D16-1139; arXiv 1606.07947 | BODY-partial (§3.1–3.2) | §3.2 (student trained with cross-entropy on teacher-generated outputs) | Teacher-generated **hard** targets are recognised as a KD variant, which supports the qualified wording in `04` |
| `romero2014fitnets` | FitNets: Hints for Thin Deep Nets | Romero, Ballas, Kahou, Chassang, Gatta, Bengio | arXiv 2014 (ICLR 2015 per secondary sources, unconfirmed here) | arXiv 1412.6550 | BODY-partial (§2.2) | §2.2 ("hint" = teacher hidden-layer output) | Representation distillation definition (optional S4 arm only) |

### 2.3 Encoder backbones

| Key | Title | Authors | Venue, year | IDs | Level | Load-bearing locators | May support |
|---|---|---|---|---|---|---|---|
| `warner2025modernbert` | Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference | Warner, Chaffin, Clavié, Weller, Hallström, Taghadouini, Gallagher, Biswas, Ladhak, Aarsen, Adams, Howard, Poli (ACL Anthology list) | ACL 2025 (Vol. 1), pp. 2526–2547 | DOI 10.18653/v1/2025.acl-long.127; arXiv 2412.13663 | BODY + `[ARTIFACT]` | §2.1.3/Table 4 (149M base / 395M large; 22/28 layers); §2.2.1 (2T tokens); 8,192 context; local 128 / global every 3 layers (config); §3.2 Table 1 GLUE **[C]**; §4.2 GPU-only throughput **[C]** | ModernBERT's architecture, sizes and context length; licence and ONNX facts come from the HF artifact (`07` §1), not from the paper. No edge-latency claim |
| `he2023debertav3` | DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing | He, Gao, Chen | ICLR 2023 (iclr.cc virtual listing; no pages) | arXiv 2111.09543 | BODY-partial (Table 9) | Table 9 (xsmall/small/base results **[C]**); no speed claims | DeBERTa-v3 exists as a compact-encoder alternative; used by Hybrid LLM / BEST-Route routers |
| `wang2020minilm` | MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers | Wang, Wei, Dong, Bao, Yang, Zhou | NeurIPS 2020 (NeurIPS 33), pp. 5776–5788 | arXiv 2002.10957 | META | — | Existence of the MiniLM family only |
| `weller2026ettin` | Seq vs Seq: An Open Suite of Paired Encoders and Decoders | Weller, Ricci, Marone, Chaffin, Lawrie, Van Durme | ICLR 2026, pp. 143110–143133 | arXiv 2507.11412 | BODY-partial | Recipe = open-data ModernBERT replication with five listed differences; sizes 17M–1B; GLUE **[C]** | Ettin as a size ladder sharing ModernBERT's tokenizer (tokenizer identity is `[ARTIFACT]`, `07` §2) |

### 2.4 Split computing and edge–cloud systems

| Key | Title | Venue, year | IDs | Level | Load-bearing locators | May support |
|---|---|---|---|---|---|---|
| `kang2017neurosurgeon` | Neurosurgeon: Collaborative Intelligence Between the Cloud and Mobile Edge | ASPLOS 2017, pp. 615–629 | DOI 10.1145/3037697.3037698 | META | — (abstract-level characterisation in `06`) | "Runtime DNN partition-point selection under bandwidth/server load was studied in prior systems work" |
| `han2016mcdnn` | MCDNN: An Approximation-Based Execution Framework for Deep Stream Processing Under Resource Constraints | MobiSys 2016, pp. 123–136 | DOI 10.1145/2906388.2906396 | BODY (UW tech-report version, Alg. 1) | Scheduler choosing model variant + location {device, split, cloud} under budgets | Prior joint model-variant and placement selection for CNNs |
| `li2020edgent` | Edge AI: On-Demand Accelerating Deep Neural Network Inference via Edge Computing | IEEE TWC 19(1):447–457, 2020 | DOI 10.1109/TWC.2019.2946140; arXiv 1910.05316 | BODY (§III–IV) | §IV-B (per-layer data size, bandwidth); §IV-C/§V-C (offline configuration map over bandwidth states); exit-branch right-sizing | Joint exit-point × partition choice under bandwidth (non-LLM, not content-aware) |
| `laskaridis2020spinn` | SPINN: Synergistic Progressive Inference of Neural Networks over Device and Cloud | MobiCom 2020, pp. 1–15 | DOI 10.1145/3372224.3419194; arXiv 2008.06402 | BODY (§3.2–3.6) | §3.4 (bandwidth/RTT moving averages); §3.6 (8-bit quantization + LZ4 of split activations) | Split cost priced with live bandwidth/RTT; compressed activations make split **lossy** |
| `mounesan2024edgerl` | EdgeRL: Reinforcement Learning-driven Deep Learning Model Inference Optimization at Edge | arXiv 2024 (venue unverified) | arXiv 2410.12221 | BODY (§II-B,C, Eq. 8) | Joint action (model version, cut layer) | Prior model × split action shape (CNNs, RL policy) |
| `younesi2025splitwise` | Splitwise: Collaborative Edge–Cloud Inference for LLMs via Lyapunov-Assisted DRL | IEEE/ACM UCC 2025, pp. 1–11 | DOI 10.1145/3773274.3774267; arXiv 2512.23310 | BODY (state/action, accuracy proxy) | Learned LLM partitioning under live bandwidth; accuracy loss as a fixed quantization proxy | Prior learned split-LLM partitioning (single model, not query-aware). Do not confuse with Patel et al. ISCA 2024 |
| `chen2025adaptivesplit` | Adaptive layer splitting for wireless large language model inference in edge computing: a model-based reinforcement learning approach | FITEE 26(2):278–292, 2025 | DOI 10.1631/FITEE.2400468; arXiv 2406.02616 | BODY (§II–V) | §II-B (tensor size assumed constant across splits); §III-A (simulated channel) | Prior learned LLM split-point selection under channel state |
| `matsubara2022splitsurvey` | Split Computing and Early Exiting for Deep Learning Applications: Survey and Research Challenges | ACM CSUR 55(5):1–30, 2022 | DOI 10.1145/3527155 | META | — | Survey pointer for split computing / early exit |

### 2.5 Numerical equivalence, early exit, privacy noise, evaluation

| Key | Title | Venue, year | IDs | Level | Load-bearing locators | May support |
|---|---|---|---|---|---|---|
| `he2025nondeterminism` | Defeating Nondeterminism in LLM Inference | Thinking Machines Lab *Connectionism* technical blog, Sep 2025 (not peer reviewed) | DOI 10.64434/tml.20250910 | BODY | Root-cause section (lack of batch invariance in RMSNorm/matmul/attention kernels); experiments (80 unique completions of 1000 at temperature 0 **[C]**) | "Greedy LLM outputs can differ across runs because kernels are not batch-invariant", stated as a technical report |
| `yuan2025nondeterminism` | Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference | NeurIPS 2025 (NeurIPS 38), pp. 188045–188077 | DOI 10.52202/085713-5653; arXiv 2506.09501 | META + abstract | Abstract (batch size, GPU count/type change BF16 greedy outputs **[C]**) | Numerical precision and hardware configuration can change reasoning outputs. This record **resolves `02`'s open venue question** |
| `schuster2022calm` | Confident Adaptive Language Modeling | NeurIPS 2022 (NeurIPS 35), pp. 17456–17472 | DOI 10.52202/068431-1269; arXiv 2207.07061 | BODY-partial (§3.3.1, §4 Defs. 1–2) | Early-exit outputs are only guaranteed consistent with the full model within a tolerance | Early exit changes inference semantics (Branch E in `02`) |
| `mai2024splitdenoise` | Split-and-Denoise: Protect large language model inference with local differential privacy | ICML 2024, PMLR 235:34281–34302 | arXiv 2310.09130 | META + abstract | Abstract (client-side noise on transmitted embeddings) | Split pipelines that add noise to activations are approximate by design |
| `wei2024simpleqa` | Measuring short-form factuality in large language models | arXiv preprint, 2024 | arXiv 2411.04368 | BODY-partial (§2.4, Table 3) | §2.4 (correct / incorrect / not-attempted grading, F-score) | SimpleQA grading scheme if SimpleQA is in the dataset set (`08`) |

---

## 3. Sources used in v3 but **not** in the .bib

These sources must not appear in `proposed-solution-blue-v3.tex`. Each would
need the action listed before it could be cited.

| Source | Where used | Level | Why excluded / action to include |
|---|---|---|---|
| **MESS+** (Woisetschläger, Zhang, Wang, Jacobsen), "MESS+: Dynamically Learned Inference-Time LLM Routing in Model Zoos with Service Level Guarantees", NeurIPS 2025 (NeurIPS 38), pp. 60178–60211, DOI 10.52202/085713-1804; arXiv 2505.19947 | **New in this iteration.** Found as a Crossref neighbour of RouteLMT | ABS | The abstract describes per-request routing that minimises cost subject to an SLA on **quality** (request-satisfaction rate), using virtual queues and satisfaction probabilities learned online. This is direct prior art for `09` Option 3 (constrained routing) and for 12 K-claims about SLA-constrained routing. Our constraint is on **latency/bandwidth**, and our utility is learned offline. **Action:** body-read it, add a row to `05`/`12`, and cite it next to the constrained-policy sentence in the blue tex. Until then the blue tex must not claim that constrained/SLA routing of LLMs is new |
| Cunningham, arXiv 2602.16760 (lookahead decoding for split LLM) | `06` iter-15 addendum, `14` | ABS | Abstract only; venue unknown |
| FourierCompress (2510.16418), Sung et al. (2511.04002) | `06`, `09` §2.3(a) | ABS | Abstract only |
| Infer-EDGE (2501.18842), BottleNet (ISLPED 2019), JointDNN (TMC 2021), Edge-Intelligence co-inference (MECOMM 2018), EdgeLLM (TMC 2025), Qu et al. COMST 2025, ACM CSUR 2026 edge-LLM survey | `06` table | META / ABS | Not needed for the blue tex; upgrade first if cited |
| Li et al. arXiv 2507.16731 (edge LLM taxonomy) | `06` §1.5 | BODY (taxonomy section) | Preprint; not needed in the method section. Could support related-work text later |
| R. Zhang et al. arXiv 2602.13628 | `06` | BODY | Not needed for the method section |
| ICDCS 2025 "partitioned collaborative inference via evolutionary RL" | `06` | META-unconfirmed | Identity not confirmed. **Do not cite** |
| CoSense-LLM (arXiv 2510.19670) | `06` | — | Withdrawn by arXiv. **`[REJECT]`** |
| Splitwise (Patel et al., ISCA 2024) | `06` | — | Out of scope (datacenter prefill/decode split). Name clash with `younesi2025splitwise` |
| CL papers: EWC (1612.00796, DOI 10.1073/pnas.1611835114), Huszár (1712.03847), GEM (1706.08840), A-GEM (1812.00420), ER (1902.10486), LwF (1606.09282), Adapters (1902.00751) | `15` | META | Journal scope (`15`); excluded from the conference .bib on purpose |
| Pseudo-Label (Lee 2013) | `04` §6 | META (secondary only) | Primary PDF not retrieved. **Do not cite** |
| DistilBERT, TinyBERT, PLaD, PAD | v2 only | v2 `[abs]` | Not used by any v3 decision; not re-read |
| Edge-cloud survey (v2 `edgecloudsurvey2025`) | v2 only | v2 SECONDARY | Replaced by `matsubara2022splitsurvey` for taxonomy |
| Holm (1979), Schuirmann TOST (1987), Efron bootstrap | `13` §1 | not checked | Experiments section only. Verify before they enter an evaluation section; not needed in the Proposed Solution |
| Hugging Face model cards / configs / repos (ModernBERT, DeBERTa-v3, Ettin, Qwen3, Gemma, Nemotron) | `07`, `10` | `[ARTIFACT]` / `[API]` | Artifacts, not papers. Cite model technical reports when a model is named in the manuscript; those reports are **not yet verified** (`10` §12) |

---

## 4. Corrections relative to methods-v2's bibliography

| v2 entry | Problem in v2 | v3 resolution |
|---|---|---|
| `ong2025routellm` | arXiv title ("with Preference Data") used for an ICLR citation; no page range | Proceedings title "**from** Preference Data", pp. 34433–34448 (proceedings.iclr.cc) |
| `bestroute2025` (`@misc`) | Cited as arXiv, body not read, ICML venue only from the arXiv comment | `ding2025bestroute`: ICML 2025, PMLR 267:13870–13884, BODY |
| `hydra2026` | Abstract-level; "four sigmoid heads" read as per-model heads | `garg2026hydra`: BODY; heads are **capability requirements**; author-list discrepancy logged |
| `llmrouterbench2026` | Title "paraphrased from positioning; verify exact title"; conclusion over-generalised | `li2026llmrouterbench`: exact title, Findings ACL 2026 pp. 37733–37754, DOI; bounded conclusion (`05` §4) |
| `routelmt2026` | Body not read | `luo2026routelmt`: DOI, pages, BODY via `11` |
| `consroute2026`, `archrouter2025`, `prefillroute2026`, `irtrouter2025` | Body not read (`[OPEN]`) | BODY in `05`. IRT-Router gains its ACL Anthology DOI and pages; the prefill router uses its v3 title |
| `ding2024hybridllm` | Inspected `[abs]` | BODY; ICLR 2024 pp. 41348–41366 |
| `warner2024modernbert` (`@misc`, "ID/params [OPEN]") | arXiv-only, unverified parameters | `warner2025modernbert`: ACL 2025 pp. 2526–2547, DOI, **Anthology author list (13 authors; arXiv lists 14 incl. Nathan Cooper)** |
| `he2023debertav3` | "ID [OPEN]" | Venue confirmed via the iclr.cc virtual listing only; still no pages |
| `guo2017calibration` | Inspected `[body]` in v2, but v3's `08` listed it as META | BODY recorded in `03` §13; PMLR 70:1321–1330 |
| `sanh2019distilbert`, `jiao2020tinybert`, `plad2024`, `pad2025`, `edgecloudsurvey2025` | `[abs]` | Dropped (unused in v3) |
| CL entries (`kirkpatrick2017ewc` … `houlsby2019adapters`) | Labelled verified after abstract-only checks | Downgraded to META in `15`; excluded from the conference .bib |
| — (missing in v2) | No systems-venue entries; no CR²/Bao/NetGPT | Added the §2.4 systems keys and `xue2026cr2`, `bao2025qualitylatency`, `chen2025netgptrouting` |
| — (missing in v2) | `02`'s Yuan et al. venue open | `yuan2025nondeterminism`: NeurIPS 2025, DOI 10.52202/085713-5653 |

**Key aliases.** Earlier v3 files proposed some keys before this .bib existed.
The canonical keys are: `ding2024hybrid` (in `04`) → **`ding2024hybridllm`**;
`kim2016sequence`, `zheng2023judging`, `chen2024routerdc`, `ong2025routellm`,
`hinton2015distilling` are unchanged. The blue tex must use the canonical keys.

---

## 5. Usage rules for `proposed-solution-blue-v3.tex`

1. **Only §2 keys.** Every `\cite{}` must resolve to `method-references-v3.bib`.
2. **Respect "May support".** For example, `li2026llmrouterbench` may support
   only the bounded backbone sentence, and `wang2020minilm` only existence.
3. **Author claims stay author claims.** **[C]** numbers (latency, AUC, cost
   savings, GLUE) must be written as "X et al. report …", never as facts.
4. **Preprints are flagged in text** when they carry a comparison: HyDRA,
   ConsRoute, CR², the prefill router, NetGPT-routing, EdgeRL. The technical
   blog (`he2025nondeterminism`) is described as a technical report.
5. **Absence claims are never cited.** A statement such as "we did not find
   prior work that …" is our bounded-search result (`06` §0, `12`). It carries
   no citation and must state its scope.
6. **Our design needs no citation.** Sentences describing our own choices are
   `[PROPOSED]` and are listed as such in `16`. When a choice adopts a known
   technique (temperature scaling, soft-target KD, cross-fitting), the
   technique gets its citation and the choice itself does not.
7. **Mandatory neighbours.** Any sentence presenting the utility-minus-cost
   rule must also cite the closest prior forms (`xue2026cr2`,
   `bao2025qualitylatency`, `song2025irtrouter`, `varshney2026prefill`). Any
   sentence presenting router KD must cite `xue2026cr2`. Any sentence about
   split-point selection under bandwidth must cite `kang2017neurosurgeon`,
   `li2020edgent` and `laskaridis2020spinn`. Once MESS+ is body-read, the
   constrained-policy sentence must cite it.

---

## 6. Open items

| ID | Item | Blocks |
|---|---|---|
| O-R1 | Body-read MESS+ (arXiv 2505.19947) and add it to `05`/`09`/`12` and the .bib | constrained-policy wording in blue tex; novelty K-register |
| O-R2 | DeBERTaV3 ICLR 2023 page range and OpenReview record (unreachable here) | camera-ready only |
| O-R3 | Lopez-Paz ICLR 2016 and FitNets ICLR 2015 proceedings records | camera-ready only (both currently cited conservatively) |
| O-R4 | ICL-Router AAAI 2026 proceedings record | camera-ready only (cited as arXiv) |
| O-R5 | Neurosurgeon body read, to upgrade from META if the manuscript says more than "split-point selection under bandwidth/load" | related-work expansion |
| O-R6 | Model technical reports (Qwen3, Gemma, Nemotron, …) for whichever pool is chosen (`10`) | experimental-setup section, not the Proposed Solution |
| O-R7 | Page-level locators for proceedings PDFs. Current locators are sections/equations from arXiv versions | camera-ready only |
| O-R8 | HyDRA author list: arXiv metadata (5) vs v2 PDF header (6). Re-check at submission time | camera-ready only |
