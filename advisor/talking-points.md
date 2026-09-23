# Advisor meeting: talking points

*Prepared 2026-09-23 from deliverables 1–16. This is an AI-assisted audit (see `advisor/research-sprint-report.md`), so treat every point as something to check, not something already confirmed. Tags in brackets name the deliverable that holds the evidence, using the key at the end. Nothing here makes the continue/redesign decision; that belongs to the advisor.*

---

## 1. 60-second explanation of the paper (as it stands)

> "The draft proposes a small router that runs on the edge device. For each query it picks one of three paths: answer locally with a small language model, send the query to a Split-LLM where the first layers run on the device and the rest in the cloud, or send it to a full cloud LLM. The goal is to trade answer quality against cost and latency, written as a weighted objective in Eqs. 2–3. The body calls the router a 'Tiny Language Model'. The words 'Jacobi', 'Micro' and 'Encoder' appear only in the title, so the mechanism the title names is not defined anywhere. The Proposed Solution and Results sections are empty, but the abstract and contribution C4 still say 'extensive experiments demonstrate'. So right now it is a problem formulation with an experiment plan, not a finished method or result." [d1]

## 2. 60-second literature update

> "Between 2024 and 2026 this area became crowded. Peer-reviewed routers now cover what the draft claims: RouteLLM at ICLR'25, IRT-Router at ACL'25, BEST-Route at ICML'25, ICL-Router at AAAI'26 (which adapts to new models without retraining), RouteLMT at ACL'26 Industry (which routes on the small model's own state), and LLMRouterBench in Findings of ACL'26. LLMRouterBench reports that many routers do not reliably beat a simple baseline. PRISM, whose arXiv comment says AAAI'26, already routes three ways between edge, collaborative and cloud with privacy as a criterion. The closest preprints are ConsRoute and Pro-Router. On 2026-09-15 a company called TypeSafe launched Jev, a commercial cloud 'decision model' marketed for routing. Jacobi Forcing is a real method (arXiv 2512.14681; its repo lists ICML 2026), but it speeds up *generation* in causal decoders, not classification. What remains open in our search is narrow: routing that includes a real Split-LLM path, calibration of an on-device router under domain shift, and whether any router beats the simple baseline on a real device and link." [d2, d3, d4, d6, d8]

---

## 3. Questions I should ask the advisor

1. **Direction.** Should we continue as written, narrow to N1 (split-aware routing) or N2 (calibrated on-device routing), redesign, or move to N3 (Jacobi Forcing for a small edge generator) as a separate paper? [d8 §4]
2. **Title.** "Jacobi-Forced Micro-Encoder" has no established meaning, and Jacobi Forcing does not apply to a router [d6 §9, d7]. Keep it, drop it, or reword it?
3. **Mix-or-Split (IEEE TPDS 2026).** It is closed access and we have not read it. Can the library get it? Is reading it a precondition for N1? [d8 §7]
4. **What makes the Split path different?** If the split path runs the same model as the cloud path, answer quality is the same and the choice is a systems rule, not a learned routing decision. Which model or split depth did the authors intend? [d4 §4.3 caveat a]
5. **Thresholds.** The pre-registered success criteria (5 pt call-rate gain, 2 pt non-inferiority margin, ECE ≤ 0.10 in-domain and ≤ 0.15 OOD) are our proposals. Are they acceptable? [d10 §9]
6. **Model pool.** "Qwen3-72B-Instruct" has no official checkpoint, and the Gemma-4 names in the draft are wrong. Which models do we actually have access to? [d11]
7. **Hardware.** Which edge device and network link can we use for the Split-LLM stage (H3)? Is there a GPU for the neural Stage-0 routers? torch cannot be installed on the machine used for this audit. [d10 §8, d12]
8. **Text reuse.** The first sentence of the abstract matches Li et al. (ACM CSUR 2026) word for word. How should we handle this before the draft circulates? [d8 §5]
9. **Venue and timeline.** Which venue is the target? That decides whether a mainly empirical N2 paper, possibly with a negative result, is acceptable.

---

## 4. Terms I should understand

| Term | Plain meaning | Where |
|---|---|---|
| **Query-level routing** | Choosing one model per query *before* generating, from the query alone | d2, d4 |
| **Cascade / post-generation routing** | Run the small model first and escalate if its answer looks unreliable (e.g. AutoMix). This costs extra latency | d3 |
| **Split inference vs split learning** | Split *inference* runs one model's layers across device and cloud at inference time. Split *learning* is a training protocol. The draft's three Split-LLM citations are split-*learning* papers | d13 R2 |
| **Activation transmission** | In split inference the hidden states at the cut layer are sent over the network for every generated token | d4, d15 |
| **Activation inversion** | Recovering input tokens from transmitted activations. Cunningham (2602.16760, preprint) reports about 59% of tokens recovered at a 2-layer split and about 35% at 8 layers | d3 §2.11 |
| **Jacobi decoding** | Guess a block of n future tokens, refine all of them in parallel until they stop changing (a fixed point). The result equals greedy AR decoding | d6 §3 |
| **Jacobi Forcing** | Training a causal decoder on its own Jacobi trajectories so it reaches the fixed point in fewer iterations. The paper reports about 2.6–4.0× speedups at 7B on code and math | d6 §4, §6 |
| **Lookahead decoding / CLLM** | Earlier Jacobi-family methods (both ICML 2024) | d6 §1 |
| **Discriminative vs generative router** | A classifier head that outputs a score per path in one pass, versus a language model that *writes* its decision as text | d9 |
| **Calibration / ECE** | Whether a stated confidence of 0.8 is right 80% of the time. Expected Calibration Error measures the gap | d10 §5.3 |
| **Selective prediction / risk–coverage** | Abstaining (here: escalating) when unsure, and plotting error against the fraction of queries kept locally | d5, d10 |
| **Deferral AUC** | How well the router's score ranks queries by whether the small model will fail | d10, d12 |
| **CCR@−1** | Cloud-call rate needed to stay within 1 percentage point of the strong model's accuracy. Lower is better | d10 §5.3 |
| **LODO** | Leave-one-dataset-out: train on some benchmarks and test on an unseen one. This is our out-of-domain test | d10 §4 |
| **Oracle router** | Uses the true outcomes, so it is an upper bound, not a method | d12 |
| **System One model (Jev)** | A vendor's term for a fast cloud model that returns typed decisions with probabilities instead of free text. Its architecture is undisclosed | d5 |

---

## 5. Likely professor questions, with concise answers

**Q: So is there still a gap?**
A: For the draft as written, mostly no. A tiny or encoder router, a generative router, no-retraining adaptation, the cost–quality objective, and three-way routing with privacy are all occupied [d4 §4.1]. Three narrow questions were not found in our bounded search: U1 (a router with a real Split-LLM action), U2 (calibration of an on-device router under domain shift), and U3 (whether a router beats the simple baseline on a real device) [d4 §4.3]. U1 could be closed by Mix-or-Split, which we have not read.

**Q: What is a "Jacobi-Forced Micro-Encoder"?**
A: No established method with this exact name was found as of 2026-09-23 [d7]. Jacobi Forcing speeds up multi-token generation in causal decoders. A router outputs one decision, and with a one-token label Jacobi decoding is identical to AR decoding, so there is nothing to speed up [d6 §9]. The only coherent reading we found puts Jacobi Forcing on the edge or split *generator*, with a separate small router (d7 P1). That would be a decoding contribution, not a routing one.

**Q: Why not keep the generative Tiny-LM router?**
A: Eq. 3 is an argmax over scores, which is a classification problem [d1]. ConsRoute's Table III reports that generated tier choices are slower than a hidden-state probe and not more accurate [d4 §4.3, d13 §3]. Jev's whole pitch is that decisions do not need text generation [d5]. We have pre-registered H2 to test this directly, but it has not been run.

**Q: What have you actually measured?**
A: Only Stage 0 with *simple* baselines, using LLMRouterBench's released per-query scores. No model inference was run. On Qwen3-8B vs Qwen3-235B in-domain, TF-IDF + logistic regression sends 0.299 of queries to the cloud, against 0.410 for the dataset-prior router and 0.113 for the oracle. It significantly beats dataset-prior on deferral AUC in only 2/5 seeds. In leave-one-dataset-out folds it is never significantly better than random and is significantly worse in 3/8 [d12, `experiments/prototype/results/stage0_summary.md`]. **No neural, generative or Jacobi router has been run.**

**Q: Does Jev kill the idea?**
A: It redirects it [d5 §8]. It weakens "fast lightweight router" and "generative TLM" as selling points. It supports treating routing as a typed, calibrated decision. It does not cover on-device routing, routers trained on a specific model pool, open weights, or coupling with a Split-LLM. Its performance claims come from the vendor, and its architecture is undisclosed.

**Q: Is the Split-LLM path private?**
A: Not by default. Cunningham's preprint reports token-recovery attacks on activations at shallow splits [d3 §2.11], and the draft's split-learning citations do not support privacy claims about split inference [d13 §3]. Any privacy claim needs a measured leakage-vs-split-depth curve.

**Q: Can we use the draft's datasets and models?**
A: Not as written. The SimpleQA plan is unworkable [d13 E2, E5]: none of the draft's weak or strong models has SimpleQA records in LLMRouterBench, and a lossless Split-LLM computes the same function as the unsplit model, so quality labels cannot tell SPLIT from CLOUD. In the LLMRouterBench bundle, flagship models score only 0.15–0.54 on SimpleQA, so an edge SLM would almost never be correct there. Several model names are wrong or have no official checkpoint [d11]. No router code was found in RouteLMT's public repository, so it would have to be re-implemented from the paper [d11].

**Q: What is the smallest experiment that could falsify the central claim?**
A: Stage 0 [d10]: two model pairs from released scores, 5 seeds plus 4 leave-one-dataset-out folds. It compares an encoder router (B), a small generative router (A) and simple baselines on CCR@−1, deferral AUC and ECE. If no learned router beats TF-IDF+LR by ≥ 5 points of call rate, H1 is falsified for this pool. It needs one GPU. The Split-LLM stage (H3) needs a real device and link.

**Q: Which of the draft's citations are wrong?**
A: None of the 20 bibitems is fabricated, but four need metadata fixes, one is never cited, and one is a marketing blog cited for a regulatory claim [d13 §1]. The figures quoted in related work need correcting. RouteLLM's cost saving is about 1.4–3.7×, not 2–3.6×. Arch-Router's 93.17% and 28× compare against prompted proprietary LLMs on the authors' own benchmark. TSLT's abstract says latency was *maintained*, not reduced [d13].

**Q: How much of this did you do yourself?**
A: Be direct: this is an AI-assisted sprint. Say which parts you have personally read and checked, and point to `advisor/research-sprint-report.md` for the rest.

---

## 6. What I should NOT claim to know yet

- **That U1 is novel.** Mix-or-Split (TPDS 2026) is unread, and IEEE Xplore and the ACM DL were not searched directly [d4 §4.3(b), d8 §7].
- **That any learned router beats the simple baseline.** Only simple baselines were run. Stage-0 LODO results are negative so far [d12].
- **Any latency, energy, throughput or privacy number for our system.** None was measured [d13 §3].
- **That Jacobi Forcing works on a sub-2B edge model or on edge hardware.** The only public checkpoints are 7B, for code and math [d6].
- **That Jacobi Forcing is peer-reviewed.** Its ICML 2026 venue comes from the repo only; library.bib cites it as a preprint [`references/README.md`].
- **Jev's architecture, accuracy or calibration.** These are vendor claims plus one independent non-peer-reviewed repo [d5 §4].
- **Details of preprints read at abstract depth only** (Lyra, LSCI, DABO, LLMSwitchBench) [d8 §7].
- **That the draft's model pool can be evaluated from released data.** In the LLMRouterBench bundle only Llama-3.1-8B-Instruct from the pool appears, and not on SimpleQA; everything else needs our own inference runs [d13 E2]. (d3 §2.17 still lists this as unverified; d13 E2 is the later check.)
- **That the claim-audit tallies were independently recounted.** They were counted by hand, with one self-check [d13 §4].
- **That `paper/main-revised.tex` compiles.** No TeX is installed on the audit host [d15].

---

*Key: d1 `research/problem-as-written.md`, d2 `current-landscape.md`, d3 `closest-prior-art.md`, d4 `novelty-matrix.md`, d5 `jev-system-one.md`, d6 `jacobi-forcing.md`, d7 `micro-encoder-investigation.md`, d8 `gap-assessment.md`, d9 `architecture/options.md`, d10 `architecture/recommended-experiment.md`, d11 `experiments/reproducibility-plan.md`, d12 `experiments/prototype/`, d13 `research/claim-audit.md`, d15 `paper/main-revised.tex` (see `paper/README.md`), d16 `advisor/one-page-brief.md`.*
