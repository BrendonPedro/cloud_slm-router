# 04 — RouteLLM terminology review: judge labels are not knowledge distillation

*Deliverable 04 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 4). Resolves finding **RF-G1**
of `00-review-findings.md` and covers brief §6 (Issue E). Inputs: the RouteLLM
body reading in `05-full-routing-prior-art.md` §1.1, re-checked against the saved
arXiv v4 HTML text for this file, plus body reads of the KD source papers listed
in §6.*

---

## 0. Ruling (summary)

1. **RouteLLM does not perform knowledge distillation, and the manuscript must
   not say it does.** That includes "KD in all but name", "judge→classifier soft
   supervision" and "distils GPT-4 preferences". RouteLLM trains query-only win
   predictors by **maximum likelihood on hard categorical pairwise-preference
   labels** (Eq. 1). One of its three label sources is produced by **GPT-4 acting
   as an LLM judge** over the two models' responses (§4.1.1). The paper calls this
   **"data augmentation"** with **"LLM-judge-labeled datasets"** and describes it
   as **"synthetic data from an LLM judge"**. `[VERIFIED-BODY]`
2. **Recommended manuscript description** (use verbatim or close to it):
   > RouteLLM \cite{ong2025routellm} trains binary strong-versus-weak routers on
   > human pairwise preferences from Chatbot Arena, augmented with pairwise labels
   > produced by an LLM judge (GPT-4) \cite{zheng2023judging} and with labels
   > derived from golden answers.
   This wording describes RouteLLM in its own terms and puts no taxonomy label on
   it. If a category is needed, the accurate one is **LLM-as-a-judge preference
   supervision (hard labels) used for data augmentation**.
3. **v2 statements withdrawn.** `methods-v2/02-kd-prior-art.md` §1 (L44–52) and
   §2.1 (L70–90), and `methods-v2/03-kd-formulations.md` L12, L103, L178, L190 and
   L210, all call RouteLLM "KD-in-all-but-name", "label distillation" or "soft"
   supervision, and treat KD as "RouteLLM-occupied". All of these are `[REJECT]`.
   v2 §2.1's author list ("Ong, Almahairi, Wu, Zhang, Zhu, …") is also wrong. The
   correct list is in §1.
4. **Consequence for our KD claim.** Withdrawing the "RouteLLM already does KD"
   framing **does not make our KD novel**. It only removes an inaccurate
   precedent. Whether soft teacher targets add anything still has to be shown
   against the four-way supervision comparison in §5 (owned by `03`/`13` E1). See
   `05` §5 item 4 for the parallel rulings on Hybrid LLM and HyDRA.

---

## 1. What RouteLLM actually does (body facts)

Source: Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica, "RouteLLM:
Learning to Route LLMs from Preference Data", ICLR 2025 (OpenReview
`8sSqNntaMr`); arXiv 2406.18665 (v4 read, v1 cross-checked; the arXiv title says
"with" where the proceedings title says "from"). Repository `lm-sys/RouteLLM`
inspected. All locators are sections/equations of the arXiv HTML. Tag:
`[VERIFIED-BODY]` unless marked.

| Aspect | What the paper says | Locator |
|---|---|---|
| Task | Binary routing R^α: Q → {M_weak, M_strong}. | §3.1 |
| Label space | l_{s,w} ∈ L = {win_s, tie, win_w}, "the outcome of comparing the responses" of a strong and a weak model on q. | §3.1 |
| Objective | **max_θ Σ log P_θ(l_{s,w} \| q)**: maximum likelihood of *observed* categorical preference labels. | Eq. 1 |
| Decision | Route to strong iff P(win_s \| q) ≥ α. | Eq. 2 |
| Label source 1 | D_arena: ~80k Chatbot Arena battles (65k after pruning) with **human** votes. Models are grouped into 10 tiers and "we exclude model responses and retain only the winner identities". | §4.1, §5 |
| Label source 2 | D_gold: ≈1,500 MMLU validation items. l_{s,w} is derived "simply by comparing the responses from M_s and M_w to the golden label". | §4.1.1 |
| Label source 3 | D_judge: Nectar queries with GPT-4 responses (as M_s) plus generated Mixtral-8x7B responses (as M_w), with "pairwise comparison labels using GPT-4 as a judge", de-biased per Zheng et al. (2023). ≈120K samples, ≈$700. | §4.1.1, fn. 4 |
| Authors' own terms | §4.1.1 is titled "**Data Augmentation**"; label source 3 is "**LLM-judge-labeled datasets**"; §5.1 calls it "**synthetic data from an LLM judge**"; §6 attributes the gains to "**dataset augmentation**". | §4.1.1, §5.1, §6 |
| Routers trained | SW-ranking Bradley–Terry (Eq. 9–10, solved at inference time); matrix factorisation (Eq. 11–12); BERT-base classifier σ(W h_CLS + b) with full fine-tuning on D_pref (Eq. 13); Llama-3-8B causal classifier, softmax over label tokens. | §4.2 |
| Absent terms | "distill", "pseudo" and "soft label" each occur **0** times in v1 and v4 (string search, 2026-10-04; see `05` §1.1). | whole text |
| Router vs judge | "Reward modeling assesses response quality *after* an LLM generates it, whereas routing involves selecting the appropriate LLM *beforehand*." | §2 |

**Open details (do not paper over them):**
* **Ties in the BERT head.** Eq. 13 is a single sigmoid for P(win_s | q), while
  the labels have three classes. The body does not say how ties enter the BERT
  loss. `[OPEN]` If we reproduce RouteLLM-BERT as a baseline (`11`), take tie
  handling from the released code and report it.
* **Paper versus released artefact.** The released causal-LLM router and the HF
  dataset `routellm/gpt4_dataset` use GPT-4 **1–5 scores** (`mixtral_score`,
  threshold 4) instead of win/tie/loss judgements (`05` §1.1, repo inspection).
  Even this graded score is thresholded into a hard target before training. A
  reproduction must name which variant it uses.

---

## 2. Terminology taxonomy (brief §6)

Each term below is defined by its **canonical primary source**, so the
manuscript uses words in the sense the literature does. Our setting appears as
the "router instance" column. Tag column: inspection level of the defining
source (see §6).

| Term | Defining characteristic | Canonical source (inspection) | Router instance |
|---|---|---|---|
| **Hard observed labels** | Targets are measured outcomes of the real process (correct/incorrect, score). There is no model in the labelling loop except the metric. | — (standard supervised learning) | y(M, q) = graded correctness of model M's actual answer to q, e.g. RouteLLM D_gold, our `08` targets. |
| **Pseudo-labelling** | A model trained on the labelled set predicts labels for **unlabelled inputs of the same task**. Its argmax prediction becomes a hard label for further training (semi-supervised). | Lee 2013, ICML-WS (`[VERIFIED-META]`, identity from secondary sources only) | A first-round router labels unseen queries with its own predicted "M succeeds" decisions. **Nobody in our design or in RouteLLM does this.** |
| **Teacher-generated hard labels / sequence-level KD** | A teacher for the **same input→output mapping** produces outputs (e.g. its beam-search output). The student is trained by ordinary cross-entropy on that "new dataset". The literature does call this a form of KD. | Kim & Rush 2016, EMNLP, §3.2 (`[VERIFIED-BODY]`, sections 3.1–3.2) | A large teacher *router* outputs argmax decisions or thresholded utilities, and the student learns them as hard labels. This is control S2 in §5. |
| **LLM-as-a-judge supervision** | An LLM **evaluates responses already generated**, pairwise or by scoring, as "a scalable and explainable way to approximate human preferences". The judge sees the responses, so it is an *annotator*, not a model of the downstream task. | Zheng et al. 2023, NeurIPS D&B (`[VERIFIED-META]` + abstract; RouteLLM cites it for exactly this use) | RouteLLM D_judge; a judge scoring open-ended answers in our `08` instantiations. |
| **Preference supervision** | Targets are **pairwise comparisons** between two models' responses (win/tie/loss), usually modelled with Bradley–Terry / logistic likelihoods. This says nothing about *who* produced the comparison (human, golden answer or judge). | RouteLLM §3.1 itself (`[VERIFIED-BODY]`) | RouteLLM's l_{s,w}, from all three sources. |
| **Knowledge distillation (soft-target KD)** | A trained "cumbersome" teacher's **class-probability outputs**, softened by temperature T, are the **targets** for a small student on a transfer set. Optionally these are combined with cross-entropy on correct labels as a weighted average, with the soft term scaled by T². | Hinton, Vinyals & Dean 2015, §1–§2, Eq. 1 (`[VERIFIED-BODY]`) | Student matches a teacher router's soft utility outputs. This is condition S3 in §5. |
| **Soft-logit distillation** | The special case of matching teacher **logits** (squared error), which Hinton et al. show is the high-temperature limit of distillation. | Hinton et al. 2015 §2.1 (`[VERIFIED-BODY]`) | Student regresses the teacher's pre-sigmoid utility logits. A variant of S3. |
| **Representation distillation** | The student's **intermediate** layer is trained (through a regressor) to predict a teacher **hidden layer** (a "hint"). | Romero et al. 2015 (FitNets), ICLR, §2.2 (`[VERIFIED-BODY]` for §2.2 via rendered HTML) | Student pooled embedding regressed onto the teacher's pooled embedding. Optional condition S4 in §5. |

**Distinctions that decide the RouteLLM case:**

* **(D1) Same task or different task.** Pseudo-labelling and sequence-level KD
  both use a labeller that solves **the same mapping the student learns**, from
  the **same input**. RouteLLM's GPT-4 judge solves a different mapping,
  (q, r_s, r_w) → preference, and has **privileged input**: it sees both
  responses, which the router never does (RouteLLM §2 draws exactly this
  router/reward-model line). The judge is a stand-in for the human rater, not a
  better router.
* **(D2) Hard or soft.** Hinton-style KD transfers the teacher's *probability
  vector*. RouteLLM's targets are categorical labels (paper), or 1–5 scores
  thresholded to a binary target (released artefact). Nothing soft is
  transferred.
* **(D3) Is there a teacher router?** RouteLLM has no trained model whose routing
  outputs the student imitates. Its BERT and causal-LLM routers are trained
  side by side on the same labels.

RouteLLM is on the "not KD" side of all three distinctions. The only one where
"teacher" vocabulary can even be argued is D1 if "teacher" is stretched to mean
any labeller, and that stretch would also make every human-annotated dataset
"KD from humans". The term is therefore not supported.

---

## 3. Why v2's wording was wrong, stated as a reviewer would

v2 §2.1 claimed: "a large teacher (GPT-4) supplies *soft pairwise preference
labels* that a small student (BERT classifier) is trained to reproduce".

* *"soft"*: false. The paper's labels are categorical (§3.1, Eq. 1), and the
  released artefact thresholds a 1–5 score (§1 above).
* *"teacher … student … reproduce"*: misleading. GPT-4 judges responses (D1).
  The BERT router predicts a query-only win probability and is trained with
  ordinary maximum likelihood, the same way as on the human Arena votes.
* *"KD in all but name"*: unsupported. The closest legitimate KD concept,
  sequence-level KD (Kim & Rush 2016), needs a teacher of the *same* mapping.
  A reviewer familiar with Hinton et al. (2015) and Zheng et al. (2023) would
  read the phrase as either a misunderstanding or an attempt to make our KD look
  like an incremental step on RouteLLM. Both readings hurt the paper.

A consequence v2 also missed: its claim that "teacher-generated labels" (its
KD-family 2) is "RouteLLM-occupied" was **double-counted**. That family is not
occupied by RouteLLM as KD. It is a standard supervision baseline (S2 below)
whose novelty is irrelevant because it is a *control*, not a contribution.

---

## 4. Wording rules for the manuscript and later v3 files

**Allowed** (each needs the cited source):

* "RouteLLM \cite{ong2025routellm} learns a binary strong/weak router from
  human preference data, using LLM-judge-labelled and golden-labelled data for
  augmentation."
* "Following the LLM-as-a-judge methodology \cite{zheng2023judging}, RouteLLM
  obtains pairwise labels from GPT-4 for open-ended chat queries."
* "Unlike RouteLLM, which trains routers on hard preference labels, we
  investigate whether soft utility estimates from a larger teacher router
  \cite{hinton2015distilling} improve a compact student." Describe this as an
  investigation, not an improvement, until E1 has run.
* "Prior routers are trained on observed or judge-provided outcome labels
  \cite{ong2025routellm,ding2024hybrid,chen2024routerdc}." (Check each key
  against `05` before use.)

**Disallowed** (`[REJECT]`):

* "RouteLLM distils GPT-4 into a BERT router" / "RouteLLM performs knowledge
  distillation" / "KD in all but name".
* "RouteLLM uses soft labels". (Hybrid LLM's r_prob *is* a soft label from
  repeated sampling, `05` §1.6. Do not swap the two papers.)
* "Distillation has already been applied to LLM routing (RouteLLM)."
* "To our knowledge, no router uses distillation" or any absence claim about
  router KD, unless `12` records the bounded search behind it, and even then
  only with "to our knowledge" and the search scope stated (brief §10).

**Terms for our own method:**

* Use **"knowledge distillation"** only for condition S3: matching teacher soft
  utilities, probabilities or logits.
* Call S2 **"teacher-labelled training"** or **"hard teacher labels"**. If a
  KD term is wanted, say "analogous to sequence-level KD
  \cite{kim2016sequence}".
* Call any use of an LLM judge to *score open-ended answers* in our pipeline
  (`08`) **"judge-scored outcome labels"**. It belongs to label construction,
  not to KD.

---

## 5. Supervision conditions the KD experiment must compare (brief §6, hand-off to `03` / `13`)

Every condition uses the **same student architecture, the same training
queries, the same tuning budget, and the same calibration protocol** (post-hoc
temperature scaling on the same held-out split, `03`). Only the target changes.

| ID | Condition | Target for (q, M) | Uses a teacher? | Terminology |
|---|---|---|---|---|
| **S1** | Hard observed labels | y(M,q) ∈ {0,1}, or a graded score s ∈ [0,1], from one measured run of M on q | no | supervised learning |
| **S1-MS** | Multi-sample empirical rate | ŷ(M,q) = mean of k sampled runs (Hybrid LLM's r_prob construction, `05` §1.6) | no | soft *empirical* label, **not KD** |
| **S2** | Teacher-generated hard labels | 1[T(M,q) ≥ τ], where T is the trained teacher router | yes (hard) | teacher-labelled / sequence-KD-analogous |
| **S2-J** | Judge-generated preference labels *(only where open-ended tasks need a judge)* | pairwise or graded judge label | judge, not a router | LLM-as-a-judge supervision (RouteLLM-style) |
| **S3** | Soft teacher outputs (KD) | α·ℓ(y, p_S) + (1−α)·ℓ(σ(z_T/T), σ(z_S/T))·T², the Hinton weighted form adapted to sigmoids | yes (soft) | knowledge distillation |
| **S4** *(optional)* | S3 + representation distillation | adds ‖W h_S − h_T‖² on pooled embeddings | yes (soft + hidden) | representation distillation (FitNets-style) |

Notes for `03`:

* **S1-MS is the most dangerous competitor to S3.** It gives soft targets with
  no teacher. If S3 does not beat S1-MS at an equal labelling budget, the honest
  conclusion is "soft targets help, a teacher does not".
* **Hinton et al.'s strongest evidence (§6, Table 5)** uses a teacher trained on
  **100%** of the data and a student trained on **3%**. In v2's T1 design the
  teacher and student see the **same** labels (RF-G2), which is the regime where
  KD's advantage is least supported by its founding paper. `03` must decide
  whether the teacher gets strictly more information (more data, more samples,
  privileged inputs such as response text) or whether KD is tested only as a
  regulariser against label smoothing and tuned regularisation.
* **S2-J is a label-construction choice, not a KD condition.** Use it only where
  a task has no reference answer (`08`), and apply it identically across S1–S4.

---

## 6. Sources used in this file

| Source | Identity | Inspection in v3 | Supports |
|---|---|---|---|
| RouteLLM | Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica. ICLR 2025, OpenReview `8sSqNntaMr`; arXiv 2406.18665 | `[VERIFIED-BODY]` (arXiv v4 HTML, v1 cross-check, repo) | §1 table, §3 |
| Distilling the Knowledge in a Neural Network | Hinton, Vinyals, Dean. NIPS 2014 Deep Learning Workshop; arXiv 1503.02531 | `[VERIFIED-BODY]`: §1, §2 (Eq. 1, weighted objective, T² scaling), §2.1, §6 (Table 5) read in the ar5iv rendering, 2026-10-04 | soft-target KD definition; S3 loss form; §5 data-regime note |
| Sequence-Level Knowledge Distillation | Yoon Kim, Alexander M. Rush. EMNLP 2016; arXiv 1606.07947 | `[VERIFIED-BODY]` for §3.1 (word-level KD loss) and §3.2 ("train the student network with cross-entropy on this new dataset", generated by teacher beam search), via a tool-extracted rendering of the ar5iv page. Other sections not read. | teacher-generated hard labels as a recognised KD variant |
| FitNets: Hints for Thin Deep Nets | Romero, Ballas, Kahou, Chassang, Gatta, Bengio. ICLR 2015; arXiv 1412.6550 | `[VERIFIED-BODY]` for §2.2 ("A hint is defined as the output of a teacher's hidden layer responsible for guiding the student's learning process"). Other sections not read. | representation distillation definition |
| Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng, Chiang, Sheng, Zhuang, Wu, Zhuang, Lin, Li, Li, Xing, Zhang, Gonzalez, Stoica. NeurIPS 2023 Datasets & Benchmarks; arXiv 2306.05685 | `[VERIFIED-META]` + abstract ("a scalable and explainable way to approximate human preferences") | LLM-as-a-judge definition. **The body is not read; upgrade before a load-bearing use.** |
| Pseudo-Label (Lee 2013) | Dong-Hyun Lee, ICML 2013 Workshop on Challenges in Representation Learning | `[VERIFIED-META]` only (secondary descriptions; primary PDF not retrieved) | pseudo-labelling definition. **Do not cite in the manuscript unless the primary text is retrieved.** |
| Hybrid LLM | Ding et al., ICLR 2024; arXiv 2404.14618 | `[VERIFIED-BODY]` (`05` §1.6) | S1-MS construction (r_prob, Eq. 2) |

BibTeX keys used above (`ong2025routellm`, `hinton2015distilling`,
`kim2016sequence`, `zheng2023judging`, `ding2024hybrid`, `chen2024routerdc`) are
**proposed**. They become valid only once they are entered with verified
metadata in `method-references-v3.bib` / `17-verified-references-v3.md`.
FitNets and Lee 2013 are not needed in the manuscript unless S4 or
pseudo-labelling is actually discussed there.

---

## 7. Limits of this review

* Hinton et al. was read in full through the ar5iv rendering. Kim & Rush and
  FitNets were read **only in the sections named**, through a rendered page
  (local PDF text extraction failed: no PDF library is installed and pip is
  unavailable on this machine). Their claims above are confined to those
  sections.
* No search was made for papers that *do* apply KD to LLM routers. This file
  only rules on terminology. Any absence claim about router KD belongs to `12`,
  backed by bounded-search evidence.
