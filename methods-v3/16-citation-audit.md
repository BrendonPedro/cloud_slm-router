# 16 — Citation audit of `proposed-solution-blue-v3.tex`

*Deliverable 16 of `MICROENCODER_HARDENING_BRIEF.md` §27, which is the
`citation-audit.md` of brief §22. Prepared 2026-10-04 (gnhf run
`microencoder-hardeni-d272f9`, iteration 21). `citation-audit.md` in this
folder is an identical copy kept under the §22 file name.*

**Scope.** Every paragraph `[P1]`–`[P20]` of
`methods-v3/proposed-solution-blue-v3.tex` (the paragraph anchors are the
`% [Pn]` comments in that file) and both algorithm floats. For each sentence
or clause the audit records:

* its **type**:
  * `DESIGN`: our proposed method. It needs no prior-art citation.
  * `FACT`: a factual statement about the world or about prior work. It needs a citation.
  * `DERIVED`: a mathematical consequence of our own definitions. It is shown in
    the text and needs no citation.
  * `OBS`: our own verified observation of an artifact (code or configs), not a
    paper. It is uncited in the manuscript, and the evidence is named here.
  * `SCOPE`: a limitation or non-claim.
* the **citation key** (`method-references-v3.bib`);
* the **source locator** (section, equation or table, from
  `17-verified-references-v3.md` §2 and the body-read files it points to);
* the **inspection status** of that source (brief §29 tags; `BODY-partial` and
  `META` as defined in `17` §0);
* the **verdict** on whether the cited source supports *this wording*:
  * `OK`: the source supports the wording.
  * `OK-bounded`: the source supports the wording only within the limit stated in the sentence.
  * `FIXED`: the wording was corrected in this iteration (see §3).
  * `OPEN`: the source supports the wording, but a follow-up remains.

**Method.** Each cited clause was checked against the "May support" column of
`17` §2. Where that column was not specific enough, it was also checked against
the body-read notes in `05`, `06`, `03`, `04`, `07` and `08`. No new body reads
were done in this iteration, so every status below is the status recorded in
`17`.

---

## 0. Bottom line

* **Citation-complete: yes, with the caveats listed in §4.** Every `FACT`
  clause in P1–P20 carries at least one citation. That citation's source was
  inspected at a level sufficient for the exact wording, after the five wording
  fixes in §3. No sentence cites an internal GNHF document.
* **Five wording fixes were applied to the tex in this iteration** (§3). One of
  them removes citation laundering: RouterDC had been cited as an example of
  routing to unseen models, but its per-model embeddings must be trained for
  each new model (`01` §B, `05` §1.2).
* **38 of the 44 .bib keys are cited.** The six uncited keys are listed in §5;
  they are related-work or baseline keys, not gaps.
* **META-level citations (4)**: `kang2017neurosurgeon`,
  `matsubara2022splitsurvey`, `wang2020minilm`, and `zheng2023judging`
  (META plus abstract). Each is used only for an existence or terminology
  statement that its META/abstract status allows (`17` §2). **Abstract-only
  citations (2)**: `yuan2025nondeterminism` and `mai2024splitdenoise`, each used
  only for its abstract's claim.
* **Preprints cited (7)**: `garg2026hydra`, `xue2026cr2`, `varshney2026prefill`,
  `qiao2026consroute`, `chen2025netgptrouting`, `wei2024simpleqa`, and the
  technical report `he2025nondeterminism`. Where a preprint carries a design
  comparison (P5, P6, P7, P8, P20), the text says "preprint" or "technical
  report". Where it supports only a positioning clause (P1, P3), it does not.
  See §4 item 3.
* **Uncited non-design statements** are either `DERIVED` (the P10 mixed-target
  identity, P14's per-query argmax and Lagrange reading, the P16 cut-tensor
  size, P17's factorization Eq. (factor), and the P18 round-trip consequence)
  or `OBS` (the last sentence of P4). §6 lists them.
* **Banned wording**: the tex contains no "first" priority claim, no "without
  retraining", no "network changes force retraining", and no assertion that
  split quality is equal (re-checked by grep after the edits; §7).

---

## 1. Paragraph-by-paragraph audit

### [P1] Design overview

| # | Sentence / clause (abridged) | Type | Key(s) | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 1.1 | Router chooses among edge SLM, split execution, and remote execution | DESIGN | — | — | `[PROPOSED]` | — |
| 1.2 | Semantic question answered by a compact encoder trained offline; systems question answered by a cost model with profiled + live measurements; runtime controller combines them | DESIGN | — | `01`, `09` | `[PROPOSED]` | — |
| 1.3 | Builds on learned query routers that predict, from the query text, which model will answer well | FACT | `ong2025routellm` | Eq. 1–2, §4.2 Eq. 13 (P(win_strong\|q)) | BODY | FIXED → OK. The earlier wording "predict model quality" fit RouteLLM's win probability poorly. The new wording covers win probability (RouteLLM), per-LLM scores (RouterDC) and per-action reward probabilities (BEST-Route) |
| | | | `ding2024hybridllm` | §4.1, Eq. 1–4 | BODY | OK |
| | | | `chen2024routerdc` | Eq. 1–3 | BODY | OK |
| | | | `ding2025bestroute` | Eq. 3–5 | BODY | OK |
| 1.4 | LLM routing at the network edge trading predicted quality against latency or communication cost | FACT | `bao2025qualitylatency` | §III Eq. 6–12 (p̃ = p − α(T_edge − T_local)) | BODY | OK |
| | | | `chen2025netgptrouting` | §IV Eq. 28 (threshold adapted with RTT, BW) | BODY | OK. The threshold is a function of live RTT and BW, which is a quality-vs-communication trade |
| | | | `xue2026cr2` | Eq. 4–18 (u = y − λ·c) | BODY | OK (mandatory neighbour, `17` §5) |
| 1.5 | …or tunes routing thresholds for latency across device, edge and cloud tiers | FACT | `qiao2026consroute` | Alg. 1–2, Eq. 9–11 (BO-tuned cluster thresholds); §V-A tiers | BODY (v1) | OK. The wording does not say the network is a router input, which matches `17` |
| 1.6 | Split computing selects a partition point under bandwidth and server-load conditions | FACT | `kang2017neurosurgeon` | abstract-level | META | OK-bounded. This is exactly the sentence that `17` allows for Neurosurgeon |
| | | | `li2020edgent` | §IV-B, §IV-C | BODY | OK (bandwidth) |
| | | | `laskaridis2020spinn` | §3.4 | BODY | OK (bandwidth/RTT; server load as a scheduler input, `06`) |
| | | | `matsubara2022splitsurvey` | — | META | OK-bounded. Survey pointer only |
| 1.7 | Roadmap of subsections | DESIGN | — | — | — | — |

### [P2] Execution actions and the action-to-model map

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 2.1 | Action set Eq. (actions); Split(d) runs first d decoder layers on edge | DESIGN | — | `01` §A | `[PROPOSED]` | — |
| 2.2 | Model specification M fixes checkpoint, revision, weight quantization, compute dtype, template and decoding; same checkpoint at two numerical configurations = two specifications | DESIGN | — | `01`, `02` | `[PROPOSED]` | — |
| 2.3 | M(a), 𝓜, K, 𝓐(M); depths are realizations of M_S | DESIGN | — | `01` (A1) | `[PROPOSED]` | — |
| 2.4 | f_θ(q, M_k) of Eq. (3) stays a function of query and model | DESIGN (mapping to `source/main-original.tex` Eq. 3) | — | `01` Q8 | — | — |

### [P3] Utility definition

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 3.1 | S_D ∈ [0,1] fixed per dataset from the benchmark's own grader; U = E_ξ[S_D] (Eq. utility) | DESIGN | — | `08` §2 | `[PROPOSED]` | — |
| 3.2 | ξ collects decoding sampling, numerical variation and grader stochasticity | DESIGN (definition) | — | `08` §2.2 | — | — |
| 3.3 | For binary metric, U = P(correct); for graded, expected score | DERIVED | — | follows from Eq. (utility) | — | — |
| 3.4 | SimpleQA grader labels each response correct / incorrect / not attempted | FACT | `wei2024simpleqa` | §2.4 | BODY-partial | FIXED → OK. The earlier wording ("a response scores 1 only if…, abstentions score 0") presented *our* 0/1 mapping as SimpleQA's own scoring. SimpleQA reports correct, correct-given-attempted and F-score (`08` §4.1). The text now cites SimpleQA only for the three-way grade and states the 0/1 mapping as our choice |
| 3.5 | We set S_D = 1[correct]; abstentions are failures in U and analysed separately | DESIGN | — | `08` §4 table, §4.1 | `[PROPOSED]` | — |
| 3.6 | No single cross-benchmark "success"; per-dataset S_D, macro-average | DESIGN | — | `08` §5 | `[PROPOSED]` | — |
| 3.7 | Utility does not depend on s, cost or λ | DESIGN | — | `01`, `08` | `[PROPOSED]` | — |

### [P4] Labels

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 4.1 | Labels from running every specification on training queries and scoring with S_D | DESIGN | — | `08` §6.2 | `[PROPOSED]` | — |
| 4.2 | A single run is a noisy but unbiased estimate of U | DERIVED | — | Eq. (utility): E_ξ of one draw equals U | — | — |
| 4.3 | Averaging k sampled runs follows Hybrid LLM's empirical soft labels from repeated sampling | FACT | `ding2024hybridllm` | Eq. 2–3 (r_prob from 10 samples) | BODY | OK. "Following" claims only the precedent, not identical labels |
| 4.4 | New inference runs are needed because pre-computed benchmark results do not cover these specifications | OBS | — (uncited by design) | `08` §6.1 `[CODE]` (LLMRouterBench README and configs, 2026-10-04) | `[CODE]` | OK as an uncited observation. The statement concerns our pool, not a paper's claim. If a reviewer asks, LLMRouterBench (`li2026llmrouterbench`) could be cited for the existence of pre-computed outcomes, but the "does not cover" half is ours |

### [P5] Encoder

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 5.1 | Compact bidirectional encoder + one sigmoid head per model, Eq. (ftheta), mean pooling | DESIGN | — | `01`, `07` | `[PROPOSED]` | — |
| 5.2 | Independent sigmoids because "M_k answers q correctly" events are not mutually exclusive | DESIGN rationale (logical) | — | `01` §345 | — | OK, no citation needed |
| 5.3 | Per-model sigmoid outputs used by the prefill-activation router (preprint) | FACT | `varshney2026prefill` | §3.1 (per-target P(correct) heads, BCE) | BODY (v3) | OK. Flagged as a preprint in the text |
| 5.4 | …and by CR² (preprint) | FACT | `xue2026cr2` | §VI (per-model sigmoid heads on frozen all-MiniLM-L6-v2) | BODY (§VI) | OK |
| 5.5 | BEST-Route trains one sigmoid head per (model, number-of-samples) action | FACT | `ding2025bestroute` | Eq. 3–5 | BODY (v1) | OK. The wording keeps the action-level nature explicit |

### [P6] Backbone

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 6.1 | Encoder choice is an engineering decision, not a contribution | SCOPE | — | brief §13, `07` | — | — |
| 6.2 | ModernBERT-base: 149M parameters, 22 layers, 8,192-token context | FACT | `warner2025modernbert` | §2.1.3 / Table 4; context length in §2 | BODY + `[ARTIFACT]` | OK |
| 6.3 | ModernBERT-base was also the encoder of HyDRA (preprint) | FACT | `garg2026hydra` | §3.1 | BODY | OK. No claim that HyDRA's heads resemble ours |
| 6.4 | Ettin replicates the ModernBERT recipe at sizes down to 17M | FACT | `weller2026ettin` | recipe section (open-data ModernBERT replication, five listed differences); sizes 17M–1B | BODY-partial | OK-bounded. "Replicate the recipe" is the authors' own description. The five differences are not mentioned, which is acceptable at this level of detail |
| 6.5 | DeBERTa-v3-small is an alternative | FACT (existence) | `he2023debertav3` | Table 9 | BODY-partial | OK |
| 6.6 | DeBERTa-v3 is the encoder family used by Hybrid LLM and BEST-Route | FACT | `ding2024hybridllm`, `ding2025bestroute` | §4.1 (v3-large); Eq. 3–5 setup (v3-small) | BODY | OK ("family" covers large and small) |
| 6.7 | A MiniLM encoder | FACT (existence) | `wang2020minilm` | — | META | OK-bounded (existence only, `17` §1) |
| 6.8 | LLMRouterBench reports only a limited effect of the embedding model for three frozen embedders with embedding-based routers | FACT (author claim, bounded) | `li2026llmrouterbench` | §4.2.1; App. Table 10 | BODY | OK-bounded. Exactly the `05` §4 bounded sentence; it says the result does not cover fine-tuned encoders |
| 6.9 | Same non-distilled protocol and tuning budget for every candidate; deploy the lowest-latency candidate within a pre-fixed tolerance of the best | DESIGN | — | `07` §4, `13` | `[PROPOSED]` | — |

### [P7] Pool changes

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 7.1 | New split depth of an existing model adds no head; needs E0 at that depth and a cost profile; no new utility labels if E0 passes | DESIGN (conditional) | — | `01` Issue B, `02` | `[PROPOSED]` | OK. The clause is conditional on E0; it does not claim "no training" unconditionally |
| 7.2 | New model needs labelled outcomes, at least a new head, and recalibration | DESIGN / SCOPE | — | `01` Issue B | `[PROPOSED]` | — |
| 7.3 | Routing to unseen models needs model descriptors as inputs, e.g. IRT-Router profile embeddings | FACT | `song2025irtrouter` | Eq. 4–5 (P̂ = σ(aᵀθ_M − b), θ_M from the profile) | BODY | OK |
| 7.4 | …or HyDRA capability profiles (preprint) | FACT | `garg2026hydra` | App. H Eq. 3–5 | BODY | OK. The text does not repeat HyDRA's "zero retraining" `[AUTHOR-CLAIM]` |
| 7.5 | RouterDC's learned per-model embeddings still have to be trained for each new model | FACT (our reading of the method) | `chen2024routerdc` | Eq. 1–3 (learnable LLM embeddings) | BODY | FIXED → OK. The earlier wording listed RouterDC among the descriptor-based routers that would enable unseen-model routing, which the paper does not support (`01` §B: "model embeddings alone do not give zero-shot expansion") |
| 7.6 | Our design does not provide such inputs | SCOPE | — | — | — | — |

### [P8] Teacher

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 8.1 | We investigate whether distilling a larger router improves on a well-tuned non-distilled student | DESIGN | — | `03` | `[PROPOSED]` / `[OPEN]` | — |
| 8.2 | Teacher = larger encoder, same tokenizer family (ModernBERT-large or Ettin), same heads, same labels | DESIGN | — | `03`, `07` | `[PROPOSED]` | — |
| 8.3 | Such a teacher sees no information beyond the labels, so any benefit must be statistical | DESIGN rationale (our argument) | — | `03` Issue F | — | OK as our argument; the two mechanisms are cited next |
| 8.4 | …such as reducing the variance of noisy single-run labels | FACT (their argument, applied by us) | `menon2021statistical` | §3, §3.2 (Bayes-probability teacher reduces variance) | BODY (arXiv version) | OK-bounded. Menon et al. argue variance reduction with respect to Bayes class probabilities. Calling the labels "noisy single-run labels" is our application, and the sentence frames it as an example ("such as") |
| 8.5 | …or acting as a learned, query-dependent form of label smoothing | FACT | `yuan2020revisiting` | §2–3 (KD as learned label smoothing) | BODY-partial | OK |
| 8.6 | Gains not guaranteed: students often do not match teachers | FACT | `stanton2021kd` | Abstract, §1 | BODY-partial | OK |
| 8.7 | Larger teachers are not always better teachers | FACT | `cho2019efficacy` | §5.2 | BODY-partial | OK |
| 8.8 | Teacher size is an experimental factor | DESIGN | — | `13` E1 | — | — |
| 8.9 | Teacher reading privileged inputs (edge SLM prefill activations) = generalized-distillation variant, secondary condition | FACT (definition) + DESIGN | `lopezpaz2016unifying` | §4, §4.1 | BODY | OK |
| 8.10 | CR² (preprint) distils an on-device gate from a teacher with privileged information | FACT | `xue2026cr2` | §VI-E | BODY (§VI) | OK (mandatory neighbour for router KD, `17` §5) |

### [P9] Cross-fitting and teacher calibration

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 9.1 | Out-of-fold teacher targets with F folds | DESIGN | — | `03` | `[PROPOSED]` | — |
| 9.2 | Without it a high-capacity teacher fits training queries almost exactly, so targets collapse to hard labels | DESIGN rationale | — | `03` | — | OK. This is a standard overfitting argument stated as motivation; it is not attributed to a paper. Guo §3 (capacity → NLL overfitting) could be added if a reviewer asks, but it is not needed |
| 9.3 | Each teacher head Platt-calibrated on a disjoint teacher-calibration split | FACT (method name) + DESIGN | `guo2017calibration` | §4.1 (Platt scaling, binary) | BODY | OK |
| 9.4 | Soft targets t̃ ∈ [0,1] estimate Eq. (utility) | DESIGN | — | `03`, `08` | — | — |

### [P10] Student loss

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 10.1 | Weighted sum of hard-label and soft-target terms, adapting Hinton's form to per-model sigmoid outputs | FACT (origin of the form) + DESIGN (adaptation) | `hinton2015distilling` | §2 (weighted soft + hard objective) | BODY | FIXED → OK. The text now says "adapting to per-model sigmoid outputs", because Hinton et al. use a temperature softmax with T² scaling, and our loss is a binary-target BCE without temperature |
| 10.2 | Definition of ℓ, y_i(M), w_D | DESIGN | — | — | — | — |
| 10.3 | Because ℓ is linear in t, Eq. (kdloss) equals BCE against the mixed target; expected BCE is minimized at p = E[t] | DERIVED | — | shown in the text | — | OK. This is a two-line derivation, not a claim about prior work |
| 10.4 | Label smoothing mixes in a constant | FACT (definition of LS) | `muller2019labelsmoothing` | §3 (LS as uniform-target mixing, used throughout §3–4) | BODY | OK |
| 10.5 | Base-rate smoothing mixes in a per-model prior; distillation mixes in a query-dependent teacher output | DERIVED / DESIGN | — | `03` | — | — |

### [P11] Controls and terminology

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 11.1 | Non-KD control: same student, same labels, LS + base-rate smoothing in the search, weight decay, early stopping, equal tuning trials | DESIGN | — | `03` (C*) | `[PROPOSED]` | — |
| 11.2 | Self-distillation control with a student-sized teacher | FACT (method) + DESIGN | `furlanello2018bornagain` | §3 (BAN: teacher and student of identical architecture); §3.2 | BODY-partial | OK. The same-architecture setup is the paper's defining premise (abstract, §3) |
| 11.3 | Every student calibrated post hoc with per-model Platt or temperature scaling on the same split | FACT (methods) + DESIGN | `guo2017calibration` | §4.1, §4.2 | BODY | OK |
| 11.4 | Calibration benefit of KD must exceed post-hoc calibration; deploy the non-KD student if KD does not win | DESIGN | — | `03`, `13` E1/E4 | `[PROPOSED]` | — |
| 11.5 | "Distillation" used only for training on a teacher router's soft outputs | DESIGN (terminology rule) | — | `04` | — | — |
| 11.6 | RouteLLM augments human preference data with labels from GPT-4 acting as a judge | FACT | `ong2025routellm` | §4.1 (D_judge "using GPT-4 as a judge"), §5.1/§6 ("dataset augmentation") | BODY | OK |
| | | | `zheng2023judging` | Abstract | META + abstract | OK-bounded (the term "LLM-as-a-judge" only) |
| 11.7 | …which is preference supervision with hard labels | FACT (our classification) | — | `04` ruling | — | OK. This is our classification, derived from RouteLLM's own description (binary win labels); no source is claimed to use this exact phrase |
| 11.8 | Training on teacher-generated hard targets is a recognized but distinct sequence-level KD variant | FACT | `kim2016sequence` | §3.1–3.2 | BODY-partial | OK. Kim and Rush train on the teacher's beam output (hard sequences). "Distinct" means distinct from soft-target KD, which is how they present it |

### [P12] Cost and state

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 12.1 | Measured state s: RTT, up/down bandwidth, server queue length, cold/warm status, edge utilization and free memory | DESIGN | — | `09` §2 | `[PROPOSED]` | — |
| 12.2 | Cost = predicted end-to-end latency, from T_total = TTFT + (N−1)·TPOT | DESIGN + definition | — | `09` §2 | — | OK. The decomposition is a definition of how TTFT and TPOT compose. It is not a claim about prior work, so no citation is needed |
| 12.3 | Compute terms from offline profiles; communication terms from measured state | DESIGN | — | `09` | `[PROPOSED]` | — |
| 12.4 | Split communication includes B/BW_up and per-step round trips | DERIVED | — | `09` §2.3 | — | — |
| 12.5 | N = per-model median on a profiling split | DESIGN | — | `09` | — | — |
| 12.6 | Bytes, energy, money and memory reported separately, not summed with latency | DESIGN | — | `09` (C-1), brief §15 | `[PROPOSED]` | — |

### [P13] Decision rule

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 13.1 | Eq. (route), Δ̂ zero unless E0 fails; feasible set Eq. (feasible) with SLA, memory and data policy | DESIGN | — | `09` C-1, `02` | `[PROPOSED]` | — |
| 13.2 | With Δ̂ ≡ 0 and 𝓕 = 𝓐 it instantiates the problem objective with f_θ = Û and C = L̂ | DERIVED | — | `source/main-original.tex` Eq. 1–3 | — | OK |
| 13.3 | Additive quality-minus-cost rules appear in prior routers | FACT | `song2025irtrouter` | Eq. 1 (S = αP̂ − βC) | BODY | OK |
| | | | `varshney2026prefill` | Eq. 1–2 (λp̂ − (1−λ)C̃) | BODY (v3) | OK |
| 13.4 | …including wireless-edge routers subtracting a latency or communication penalty | FACT | `bao2025qualitylatency` | Eq. 6–12 | BODY | OK |
| | | | `xue2026cr2` | Eq. 4–18 | BODY | OK |
| 13.5 | Empty 𝓕 → run Edge if it fits, log a violation | DESIGN | — | `09` | — | — |

### [P14] λ interpretation

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 14.1 | Per-query argmax maximizes the plug-in objective for fixed λ | DERIVED | — | separability of E_q of a per-query term | — | OK |
| 14.2 | Over randomized policies λ is the Lagrange multiplier of an average-latency budget; per-query SLA is not dualized | DERIVED | — | `09` §3 | — | OK. Standard Lagrangian duality, stated as a reading rather than as a theorem attributed to prior work |
| 14.3 | λ swept for frontiers; chosen on validation to meet a stated budget, then frozen | DESIGN | — | `09`, `13` E5 | — | — |
| 14.4 | We do not claim constrained routing as a contribution | SCOPE | — | MESS+ is ABS only (`17` §3, O-R1) | — | OK. This non-claim is the safe handling until MESS+ is body-read (§4 item 1) |

### [P15] Why s stays out of θ

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 15.1 | State enters only through the cost term, so the router reacts at the next query without updating the semantic predictor | DESIGN (property of Eq. route) | — | `01` Issue C | `[PROPOSED]` | — |
| 15.2 | A router taking s as input *could* learn the dependence but needs training data spanning the conditions | DESIGN rationale | — | brief §4, `01` Issue C | — | OK. This is the corrected Issue C wording; it makes no "must retrain" claim |
| 15.3 | Separation allows reuse across deployments, re-profiling without new labels, and attributable decisions | DESIGN rationale | — | `01` | — | — |

### [P16] Split execution

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 16.1 | Split(d): edge runs embeddings + first d layers of M_S and sends hidden states; server runs the rest and returns tokens | DESIGN | — | `02`, `14` (Henry `[OPEN]`) | `[PROPOSED]` / `[OPEN]` | OK. The message pattern is still to be confirmed with Henry (`14`) |
| 16.2 | For a dense decoder the cut tensor has n × d_model elements, so prefill transfer is independent of d | DERIVED | — | `09` §2.3(a); also assumed in `chen2025adaptivesplit` §II-B | — | OK. This follows from the residual-stream width. It holds only for "a standard dense decoder" with no compression, which the sentence states |
| 16.3 | Prior systems select split points under measured bandwidth and load | FACT | `kang2017neurosurgeon` | abstract-level | META | OK-bounded (the allowed Neurosurgeon sentence) |
| | | | `li2020edgent` | §IV-B, §IV-C | BODY | OK |
| | | | `laskaridis2020spinn` | §3.4 | BODY | OK |
| 16.4 | Recent work learns LLM split points under changing channel or bandwidth for a single model | FACT | `chen2025adaptivesplit` | §II–V (simulated channel, §III-A) | BODY | OK |
| | | | `younesi2025splitwise` | state/action design | BODY | OK. "Single model, not query-aware" matches `17` |

### [P17] When depths share utility

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 17.1 | Shared utility across depths is a tested hypothesis | DESIGN | — | `02` | `[OPEN]` | — |
| 17.2 | Exact transfer does not guarantee bit-identical outputs; floating-point results depend on batch size and hardware configuration, which can change greedy outputs without splitting | FACT | `yuan2025nondeterminism` | Abstract (batch size, GPU count/type change BF16 greedy outputs) | META + abstract | FIXED → OK-bounded. The earlier wording also listed "kernel choice", which the Yuan et al. abstract does not state. Kernels are now attributed only to the technical report |
| 17.3 | A technical report attributes run-to-run differences to non-batch-invariant kernels | FACT (author claim) | `he2025nondeterminism` | Root-cause section | BODY | OK. Labelled "technical report" in the text |
| 17.4 | Quantizing or compressing transmitted activations makes split approximate | FACT | `laskaridis2020spinn` | §3.6 (8-bit quantization + LZ4) | BODY | OK. SPINN quantizes; "approximate by design" is our inference from lossy 8-bit quantization (`02`), which is uncontroversial |
| 17.5 | …or adding noise to them for privacy | FACT | `mai2024splitdenoise` | Abstract | META + abstract | OK-bounded |
| 17.6 | Early exit changes semantics; outputs consistent with the full model only within a tolerance | FACT | `schuster2022calm` | §3.3.1, §4 Defs. 1–2 | BODY-partial | OK |
| 17.7 | E0 at every deployed depth and numerical configuration; compare per-query scores against unsplit run-to-run variation | DESIGN | — | `02`, `13` E0 | `[PROPOSED]` | — |
| 17.8 | Three branches (exact / lossy / semantics-changing) and the factorization Eq. (factor) | DESIGN + DERIVED | — | `02` | `[PROPOSED]` | OK. Eq. (factor) follows by grouping actions by M(a) when Û depends only on M(a) |

### [P18] Split cost caveat

| # | Clause | Type | Key | Locator | Status | Verdict |
|---|---|---|---|---|---|---|
| 18.1 | Under a pipeline split where the server samples, every decode step needs a round trip | DERIVED | — | `09` §2.3(b) | — | OK. Conditional on the stated message pattern; Henry `[OPEN]` |
| 18.2 | If same-spec remote exists and the server is faster, latency-only cost rarely selects Split; Split is chosen under a data policy or server-compute budget | DERIVED / DESIGN | — | `09` §2.3 | — | OK. This is stated as an expectation and is measured, not assumed (18.3) |
| 18.3 | Report action-selection frequencies | DESIGN | — | `13` | — | — |

### [P19] Algorithms 1–2

| # | Content | Type | Verdict |
|---|---|---|---|
| 19.1 | Algorithm 1: E0, labelling, out-of-fold teachers with Platt calibration, student + control, post-hoc calibration, keep-KD-only-if-better, profiling | DESIGN | No citations needed. It restates P4, P8–P11 and P12, which are cited above |
| 19.2 | Algorithm 2: one encoder pass, read s, compute L̂ and 𝓕, fallback, argmax with tie-break, logging | DESIGN | No citations needed. The logging line provides the conference-side forward-compatible hook (`15`) without any CL component |

### [P20] Assumptions and limitations

| # | Clause | Type | Key | Verdict |
|---|---|---|---|---|
| 20.1 | Fixed pool; post-deployment pool changes out of scope | SCOPE | — | OK. This matches the `15` boundary rule (no CL in the conference core) |
| 20.2 | Shared utility valid only where E0 passes; lossy/semantics-changing branches need depth-specific labels | SCOPE | — | OK |
| 20.3 | KD evaluated against a tuned, calibrated control; not required by the rest of the design | SCOPE | — | OK |
| 20.4 | Latency model is analytic, accuracy measured; decisions depend on calibration and L̂ accuracy | SCOPE | — | OK |
| 20.5 | HyDRA, CR², prefill router and NetGPT router are preprints; comparisons limited to published descriptions | FACT (status) | (cited earlier: `garg2026hydra`, `xue2026cr2`, `varshney2026prefill`, `chen2025netgptrouting`) | OK. Their status matches `17` §2.1. ConsRoute is also a preprint (see §4 item 3) |
| 20.6 | Bounded search; no claim that the combination is new | SCOPE | — | OK. This is the Conservative contribution wording (`12`) |

---

## 2. Key usage summary (38 cited keys)

| Key | Level (`17`) | Paragraphs | Within "May support"? |
|---|---|---|---|
| `ong2025routellm` | BODY | P1, P11 | Yes. It is never called KD |
| `ding2024hybridllm` | BODY | P1, P4, P6 | Yes |
| `chen2024routerdc` | BODY | P1, P7 | Yes, after the P7 fix |
| `ding2025bestroute` | BODY | P1, P5, P6 | Yes (action-level heads) |
| `bao2025qualitylatency` | BODY | P1, P13 | Yes |
| `chen2025netgptrouting` | BODY | P1 | Yes |
| `xue2026cr2` | BODY | P1, P5, P8, P13 | Yes. It is placed next to both the utility-minus-cost rule and router KD, as `17` §5 requires |
| `qiao2026consroute` | BODY (v1) | P1 | Yes |
| `kang2017neurosurgeon` | META | P1, P16 | Yes (allowed sentence only) |
| `li2020edgent` | BODY | P1, P16 | Yes |
| `laskaridis2020spinn` | BODY | P1, P16, P17 | Yes |
| `matsubara2022splitsurvey` | META | P1 | Yes (pointer) |
| `wei2024simpleqa` | BODY-partial | P3 | Yes, after the P3 fix |
| `varshney2026prefill` | BODY (v3) | P5, P13 | Yes |
| `warner2025modernbert` | BODY | P6 | Yes. No edge-latency claim is made |
| `garg2026hydra` | BODY | P6, P7 | Yes. Its heads are never called per-model heads |
| `weller2026ettin` | BODY-partial | P6 | Yes |
| `he2023debertav3` | BODY-partial | P6 | Yes |
| `wang2020minilm` | META | P6 | Yes (existence) |
| `li2026llmrouterbench` | BODY | P6 | Yes (bounded sentence) |
| `song2025irtrouter` | BODY | P7, P13 | Yes |
| `menon2021statistical` | BODY | P8 | Yes |
| `yuan2020revisiting` | BODY-partial | P8 | Yes |
| `stanton2021kd` | BODY-partial | P8 | Yes |
| `cho2019efficacy` | BODY-partial | P8 | Yes |
| `lopezpaz2016unifying` | BODY | P8 | Yes |
| `guo2017calibration` | BODY | P9, P11 | Yes |
| `hinton2015distilling` | BODY | P10 | Yes, after the "adapting" qualifier |
| `muller2019labelsmoothing` | BODY | P10 | Yes |
| `furlanello2018bornagain` | BODY-partial | P11 | Yes |
| `zheng2023judging` | META + abstract | P11 | Yes (term only) |
| `kim2016sequence` | BODY-partial | P11 | Yes |
| `chen2025adaptivesplit` | BODY | P16 | Yes |
| `younesi2025splitwise` | BODY | P16 | Yes |
| `yuan2025nondeterminism` | META + abstract | P17 | Yes, after the P17 fix |
| `he2025nondeterminism` | BODY | P17 | Yes |
| `mai2024splitdenoise` | META + abstract | P17 | Yes |
| `schuster2022calm` | BODY-partial | P17 | Yes |

---

## 3. Wording fixes applied to `proposed-solution-blue-v3.tex` in this iteration

| Para | Before | After | Reason |
|---|---|---|---|
| P1 | "learned query routers that predict model quality from the query text" | "learned query routers that predict, from the query text, which model will answer it well" | RouteLLM predicts P(win_strong \| q), a preference probability rather than a quality score. The new wording is accurate for all four cited routers |
| P3 | "On SimpleQA, for example, a response scores 1 only if the benchmark's grader marks it correct, and both incorrect answers and abstentions score 0 [wei]" | "the SimpleQA grader labels each response correct, incorrect or not attempted [wei]; we set S_D = 1 for a correct response and S_D = 0 otherwise, so abstentions count as failures in the utility and are analysed separately" | The 0/1 mapping is ours. SimpleQA itself reports correct, correct-given-attempted and F-score. Attributing our mapping to the paper would be citation laundering |
| P7 | "model descriptors as router inputs, as in IRT-Router, the learned model embeddings of RouterDC, or the capability profiles of HyDRA" | IRT-Router profile embeddings and HyDRA profiles kept; added "learned per-model embeddings, as in RouterDC, still have to be trained for each new model" | RouterDC learns a fixed embedding table, so it cannot route to unseen models (`01` §B, `05` §1.2) |
| P10 | "the form introduced for knowledge distillation by Hinton et al." | "adapting to per-model sigmoid outputs the form introduced for knowledge distillation by Hinton et al." | Hinton et al. use a temperature softmax with T² scaling; ours is a binary BCE |
| P17 | "depend on batch size, hardware and kernel choice … [yuan2025]" | "depend on batch size and hardware configuration … [yuan2025]" | The Yuan et al. abstract (the only part inspected) names batch size and GPU count/type, not kernels. Kernels stay attributed to `he2025nondeterminism` |

After the edits, the static checks were re-run (§7).

---

## 4. Open items and residual risks (not citation gaps)

1. **MESS+ (O-R1).** The NeurIPS 2025 paper (DOI 10.52202/085713-1804) is ABS
   only and therefore not in the .bib. P14 contains an explicit non-claim ("We
   do not claim constrained routing as a contribution"). If the paper later
   presents SLA-constrained routing as a contribution, or if the related-work
   section discusses constrained LLM routing, MESS+ must first be body-read and
   then cited.
2. **Page locators.** For proceedings papers, `17` records section, equation
   and table locators from the arXiv bodies. Proceedings-PDF page numbers for
   individual claims were not extracted (`05` §5 lists RouterDC, BEST-Route,
   Hybrid LLM and IRT-Router). Section-level locators are enough for the audit,
   but camera-ready checks should confirm that the section numbers match the
   proceedings versions.
3. **Preprint flags.** P1 cites ConsRoute, NetGPT-routing and CR² without
   saying "preprint" in that sentence, and P3 cites SimpleQA (arXiv) the same
   way. Those clauses only position the work, and P20 lists the preprint status
   of the related routers. ConsRoute is missing from the P20 list. Before
   merging, the advisor should decide whether to add ConsRoute to P20, or
   whether IEEEtran's bibliography entries (which show "arXiv preprint") are
   enough.
4. **META-level citations.** `kang2017neurosurgeon` and
   `matsubara2022splitsurvey` are cited for one-sentence characterizations.
   Upgrading Neurosurgeon to BODY would allow more specific wording, such as
   "layer-wise latency and energy prediction models", if the related work needs
   it.
5. **Henry dependency.** P16 and P18 describe the split message pattern
   conditionally ("under a pipeline split in which the server samples
   tokens"). If Henry's implementation batches or speculates, P18 must be
   revised (`14`).
6. **No compilation.** No LaTeX/BibTeX toolchain exists in the environment, so
   cite resolution was checked statically against the .bib (§7), not by
   BibTeX.

---

## 5. Uncited .bib keys (6) and why

| Key | Role | Why not cited in the Proposed Solution |
|---|---|---|
| `han2016mcdnn` | Prior joint model-variant + placement selection (CNNs) | Related-work / novelty-section key (`06`, `12`). It would fit P1 or P16, but the P16 split-point sentence already has BODY sources. Recommended for the related-work section |
| `mounesan2024edgerl` | Joint (model version, cut layer) RL action | Related-work key (`06`); venue unverified |
| `luo2026routelmt` | Learned translation routing | Baseline/related-work only (`11`) |
| `romero2014fitnets` | Representation distillation | Optional S4 arm only (`03`); not described in the method section |
| `tran2025archrouter` | Generative router | Baseline option only (`11`) |
| `wang2025iclrouter` | Model-representation routing | Pool-expansion baseline (`11`); P7 already cites IRT-Router and HyDRA |

These keys are kept in the .bib so that the related-work, baseline and
experiment sections can use them without re-verification.

---

## 6. Uncited non-design statements (all accounted for)

| Para | Statement | Classification | Evidence |
|---|---|---|---|
| P3 | Binary metric ⇒ U = P(correct) | DERIVED | Eq. (utility) |
| P4 | Single run is an unbiased estimate of U | DERIVED | Eq. (utility) |
| P4 | Pre-computed benchmark results do not cover our specifications | OBS | `08` §6.1 `[CODE]` |
| P5 | Correctness events across models are not mutually exclusive | Logical | — |
| P9 | A high-capacity teacher fits training queries and its targets collapse to hard labels | Motivation (standard overfitting) | `03` |
| P10 | BCE linear in t; minimized at p = E[t]; mixed-target identity | DERIVED | In text |
| P12 | T_total = TTFT + (N−1)·TPOT | Definition | `09` §2 |
| P13 | Instantiates the problem objective when Δ̂ ≡ 0, 𝓕 = 𝓐 | DERIVED | Manuscript Eq. 1–3 |
| P14 | Per-query argmax optimality; Lagrange reading of λ | DERIVED | `09` §3 |
| P16 | Cut tensor n × d_model, independent of d (dense decoder, uncompressed) | DERIVED | `09` §2.3(a) |
| P17 | Factorization Eq. (factor) | DERIVED | Grouping by M(a) |
| P18 | Per-token round trip; Split rarely latency-optimal against a faster same-spec remote | DERIVED (conditional) | `09` §2.3(b) |
| P11 | RouteLLM's judge labels are "preference supervision with hard labels" | Our classification | `04` ruling, from RouteLLM §4.1 |

No uncited factual claim about prior work remains.

---

## 7. Static checks re-run after the edits

* All `\cite{…}` keys resolve in `method-references-v3.bib`: 38 distinct keys,
  0 missing.
* Braces are balanced, and `\begin`/`\end` environments are balanced.
* All `\ref`/`\eqref` labels are defined.
* Banned-wording grep (`first`, `without retraining`, `no retraining`,
  `identical`, `novel`, `state-of-the-art`): `first` appears only as "first d
  decoder layers", "first implementation candidate" and similar. `identical`
  appears only in "does not by itself guarantee bit-identical outputs".
* `source/main-original.tex` and `methods-v2/` show no git diff.
