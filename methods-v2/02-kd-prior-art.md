# methods-v2 / 02 — Knowledge-distillation prior art for routing

*Deliverable for `MICROENCODER_KD_BRIEF.md` §5 (required investigation B).
Prepared 2026-10-02 (gnhf microencoder-kd sprint, iteration 3).*

## 0. Purpose and sourcing

The advisor "explicitly suggested investigating KNOWLEDGE DISTILLATION to
further optimize the micro-encoder **because micro-encoder/router work likely
already exists**" (`00-meeting-decisions-lock.md`, CONFIRMED #7). Deliverable
`01-microencoder-prior-art.md` confirmed the premise: a small discriminative
encoder router is standard practice, so the contribution cannot rest on the
encoder. This file asks the sharper question the brief §5 mandates: **has
knowledge distillation (KD) already been applied to LLM routing / model
selection, and if so, exactly what was distilled, by whom, with what teacher,
student, and loss?**

**This is the one deliverable that required genuinely new web research.** The v1
sprint never ran a KD-for-routing search — its only "distillation" hits were
(a) *consistency distillation* in the Jacobi/CLLM line (`research/jacobi-forcing.md`,
unrelated to routing) and (b) the Jev/TypeSafe MCA clause that *forbids* using
Jev outputs as teacher labels (`research/jev-system-one.md` §J5). Both are
carried forward below as constraints, not precedent. All new searches were run
2026-10-02; primary locations (arXiv abstract/PDF, NeurIPS/ICLR proceedings,
official repos) were opened where cited.

**Evidence tags** (from `00` §Evidence discipline). To the `01` set
(`[abs]`/`[body]`/`[api]`/`[O]`/`[OPEN]`) this file adds, per brief §23:
`[VERIFIED]` = primary source directly supports the statement; `[RELATED]` =
adjacent prior work, not exact precedent; `[PROPOSED]` = our design idea;
`[ext]` = stated from well-established external literature whose primary source
is named but was **not** re-opened in this sprint (must be re-verified in
`17-verified-references.md` before it becomes load-bearing).

---

## 1. Headline finding (the §5 answer in one paragraph)

**Knowledge distillation has NOT been established as a method for building or
compressing an LLM *router*.** [VERIFIED by absence — see §2, §6.] Across the
encoder-router literature checked in `01` (RouteLLM, RouterDC, BEST-Route,
HyDRA, ConsRoute, the prefill-activation router, LLMRouterBench) **none frames
its training as teacher→student distillation of the routing decision.** The
single closest precedent is **RouteLLM's GPT-4-as-judge label augmentation**,
which distils a frontier judge's *pairwise preferences* into a small BERT
classifier in all but name [VERIFIED]. The term "distillation" also appears in
the routing neighbourhood in two **non-router** senses that must not be
conflated: (i) distilling a frontier LLM into a smaller *generative student*
that the router then routes *to* (e.g. the `dynamic_routing_LLM` project);
(ii) consistency/sequence KD of generative decoders (CLLM, DistiLLM-2). Neither
distils the *router*. **Consequence:** "we distil the router" is not itself
novel-by-adjective — RouteLLM already does judge→classifier soft supervision —
but **KD that distils *calibrated per-model utility over an edge/Split action
set* into an edge-deployable encoder, combined with a separate live cost term,
is not occupied.** This sharpens, but does not by itself establish, the novelty
lanes isolated in `01`; `11-novelty-stress-test` must still test them against
the RouteLLM precedent below. [O]

---

## 2. ESTABLISHED — KD (or KD-in-all-but-name) in routing / model selection

Direct prior work that trains a routing/model-selection decision using
teacher→student soft supervision. The honest finding is that this set has
**exactly one strong member**, and it does not call itself KD.

### 2.1 RouteLLM — LLM-judge label augmentation into a BERT router *(closest precedent)*

- **Title:** *RouteLLM: Learning to Route LLMs with Preference Data.* **Authors:**
  Ong, Almahairi, Wu, Zhang, Zhu, (Isaac) Ong et al. **Venue/year:** arXiv
  2024-06; **ICLR 2025**. **ID:** arXiv:2406.18665; ICLR 2025 proceedings PDF
  (iclr.cc/paper_files/paper/2025/…/5503a7c69d48…). **Code:**
  github.com/lm-sys/RouteLLM. [abs][body][api]
- **What is "distilled":** RouteLLM trains routers on Chatbot-Arena human
  preference data **augmented with pairwise comparison labels produced by a
  GPT-4 judge**; the paper reports that GPT-4-judge augmentation lifts the **BERT
  classifier** router's APGR by **>50% vs random** and cuts cost up to ~75% at
  matched quality. [VERIFIED — LMSYS blog + ICLR PDF read 2026-10-02]
- **Why it is KD-in-all-but-name:** a large teacher (GPT-4) supplies *soft
  pairwise preference labels* that a small student (BERT classifier) is trained
  to reproduce. That is preference/label distillation under a different name.
  The paper does **not** use a KL/temperature soft-target loss, does **not**
  distil logits or a utility vector, and does **not** frame it as KD — it frames
  it as *data augmentation*. [VERIFIED / O]
- **Gaps vs our setting:** no edge deployment, no Split-LLM action, no live
  system-cost term, binary strong-vs-weak target (not a per-model utility vector
  over an edge/Split/strong action set), judge-as-labeler (not
  soft-logit/temperature KD). These gaps are exactly where a defensible KD
  formulation could sit — see `03-kd-formulations`, `11-novelty-stress-test`. [O]

### 2.2 vLLM Semantic Router — LLM-as-judge preference labels for an edge/cloud router

- **Status:** named in the edge–cloud survey arXiv:2507.16731 (Collaborative
  Inference and Learning between Edge SLMs and Cloud LLMs) as using *"an external
  LLM-as-a-Judge to simulate human rating preferences, jointly optimizing
  response quality and system cost for edge–cloud routing."* [abs — via survey]
- **Classification:** ESTABLISHED for *LLM-judge-labeled* routing, **[OPEN] as a
  KD precedent** — the primary vLLM-semantic-router source was not opened in this
  sprint; do not claim it uses temperature/soft-target KD. It is the second
  judge→router instance and, like RouteLLM, uses the judge as a *labeler*, not a
  soft-target teacher. Re-open before citing as load-bearing. [OPEN]

### 2.3 `dynamic_routing_LLM` — KD makes the STUDENT, router is separate *(not a router-KD precedent)*

- **Source:** github.com/ur-miya/dynamic_routing_LLM (no associated paper/arXiv).
  [api — repo read 2026-10-02]
- **What it does:** distils a Qwen-32B **teacher** into a Qwen-1.5B **generative
  student** via token-wise KL with temperature (SKL on teacher outputs, SRKL on
  student outputs, CE stabiliser — DistiLLM-2 style) + SFT on OASST1; a *separate*
  router (strongest variant "Router D": classifier + uncertainty + IRT-difficulty
  + judge-quality features, plus a "gain-aware" ΔQ estimate) then routes between
  the distilled student and the teacher. [api]
- **Classification:** **KD is applied to the generative student, NOT to the
  router.** The routing decision itself is not distilled. Cloud-side, not edge,
  not Split-LLM, no paper. It is the canonical example of the *conflation to
  avoid* — "route to a distilled model" ≠ "distil the router." Useful only as a
  cautionary reference and as a source of a per-query *gain-aware* routing
  target (ΔQ), which echoes our oracle-utility label design. [O]

### 2.4 What is NOT in this set (common misreadings)

- **RouterDC** (NeurIPS 2024, arXiv:2409.19886) is **contrastive** (sample-LLM +
  sample-sample InfoNCE losses over an mDeBERTa-v3-base encoder and learnable LLM
  embeddings), **not distillation**, despite "DC" = *Dual Contrastive*. The teacher
  signal is top/bottom-performing LLMs per query, used as contrastive
  positives/negatives — not soft targets. Explicitly **excluded** from the KD set
  to avoid misclassification. [VERIFIED — NeurIPS PDF + repo read 2026-10-02]
- **BEST-Route** uses a multi-head DeBERTa-v3-small to estimate query difficulty
  and pick model+sampling; trained on observed outcomes, **no teacher→student
  distillation of the router**. [abs, carried from `01`]
- **CLLM / Jacobi Forcing / DistiLLM-2** are *generative-decoder* consistency/
  sequence KD — orthogonal to routing. Carried from `research/jacobi-forcing.md`.
  Jacobi is explicitly not a required component (`00`, CONFIRMED #10). [body]

---

## 3. RELATED — KD methods from adjacent areas (adaptable, not router precedent)

These are well-established KD families that *could* be adapted to a router but
are **not** established LLM-routing methods. Tagged `[RELATED]`; IDs stated from
external literature `[ext]` must be re-opened in `17` before load-bearing use.

| Family | Representative primary source | What it distils | Loss | Relevance to our router |
|---|---|---|---|---|
| **Foundational soft-target KD** | Hinton, Vinyals, Dean, *Distilling the Knowledge in a Neural Network*, arXiv:1503.02531 (NIPS-2014 DL workshop) | Class **logits** → softened probabilities | `T²·KL(softmax(z_t/T)‖softmax(z_s/T))` + CE on hard labels | The template for **KD-1** soft utility-vector distillation (`03`). Directly applicable if the router emits a path/utility logit vector. [ext] |
| **Encoder KD (task-agnostic)** | Sanh et al., **DistilBERT**, arXiv:1910.01108 · Jiao et al., **TinyBERT**, Findings of EMNLP 2020, arXiv:1909.10351 · Wang et al., **MiniLM**, NeurIPS 2020, arXiv:2002.10957 | Hidden states / attention / embeddings of a BERT teacher → smaller encoder | Hidden-state MSE, attention-matrix KL, embedding MSE | The template for **KD-4** representation distillation (`03`); also *the student backbones themselves* (`05-student-architecture`) are KD-produced encoders. [ext] |
| **Ranking / preference KD** | **PLaD**, Findings of ACL 2024, arXiv:2406.02886 · **PAD** (Preference-Aligned Distillation), arXiv:2502.14272 | Teacher-over-student **preference / ranking** | Ranking/calibration loss (PLaD); preference-distribution alignment (PAD) | The template for **KD-2** pairwise/ranking distillation (`03`). Note: both target *generative* SLM quality, not routing. [abs] |
| **Learning-to-rank distillation** | Tang & Wang, *Ranking Distillation* (RD), KDD 2018 | Teacher's top-K item ordering → student ranker | Hybrid ground-truth + teacher-rank loss | Precedent that *ranking* (not just class labels) is distillable — supports KD-2 for route ordering. [ext — re-verify] |
| **Calibration / dark-knowledge** | Guo et al., *On Calibration of Modern Neural Networks*, ICML 2017 (temperature scaling) | — (calibration, not a teacher) | Post-hoc temperature scaling | Needed because the router's `Û(a|q)` must be *calibrated* to combine with `λ·C(a|s)` (`08-system-cost-integration`); KD temperature ≠ calibration temperature — keep distinct. [ext] |

**Reading of the RELATED set:** every mechanical ingredient a router-KD scheme
needs (soft-target KL, encoder hidden-state KD, ranking distillation,
calibration) **already exists in mature form**. None is novel in isolation. This
is the same lesson `01` drew for the encoder: the novelty, if any, is in the
*combination and target* (calibrated per-model utility over an edge/Split action
set, distilled into an edge encoder, decoupled from live cost), **not** in any
single KD mechanism. [O] Feeds `11-novelty-stress-test` directly.

---

## 4. PROPOSED — our design adaptations (flagged, not claimed as prior art)

Detailed in `03-kd-formulations`; listed here only to keep the three categories
unblurred per brief §5.

- **[PROPOSED]** Distil a teacher's **calibrated per-action utility vector**
  `Û(a|q)` — where actions `a` span {Edge-SLM, Split(d), Strong/Cloud} — into a
  micro-encoder student (KD-1/KD-3 hybrid). Distinct from RouteLLM (binary
  strong-vs-weak, judge-as-labeler, no soft-target loss). [PROPOSED]
- **[PROPOSED]** Keep the distilled utility strictly **query-conditioned** and
  the system cost `C(a|s)` strictly **runtime-measured and outside the student
  weights** (`00` CONFIRMED #2; `08`). No surveyed KD-routing work separates a
  distilled utility head from a live cost term — this is the separation axis N3
  in `01`/`11`. [PROPOSED/OPEN]
- **[OPEN]** Whether KD beats training the same student directly on observed
  outcome labels is an **empirical** question for experiment E1
  (`12-conference-experiment-plan`). KD must earn its place; if ablation E1 shows
  no gain over hard-label supervision, the defensible conclusion is **"KD does
  not add sufficient value"** (brief stop-condition #4 explicitly permits this
  outcome). [OPEN]

---

## 5. Brief §5 question-by-question answers

Using only what the primary sources above support; `[OPEN]` where no established
router-KD source answers the question.

1. **Has distillation already been used for LLM routers?** Not under that name
   for the routing decision. The one strong precedent is RouteLLM's GPT-4-judge
   *preference-label augmentation* of a BERT classifier — KD-in-all-but-name,
   not framed or lossed as KD. [VERIFIED]
2. **If yes, what was distilled?** GPT-4's **pairwise strong-vs-weak
   preferences** (as augmented hard/soft labels), not logits/utility vectors.
   [VERIFIED]
3. **Teacher?** A frontier **LLM-as-judge** (GPT-4 in RouteLLM; an unnamed LLM
   judge in vLLM Semantic Router [OPEN]). Not a larger *router*. [VERIFIED/OPEN]
4. **Student?** A small **BERT classifier** (one of RouteLLM's four router
   variants). [VERIFIED]
5. **Hard labels / logits / probs / rankings / embeddings / hidden states /
   pairwise prefs?** **Pairwise preferences → (augmented) classification labels.**
   No logit/probability/ranking/embedding/hidden-state distillation of a router
   in any surveyed work. [VERIFIED]
6. **Loss?** RouteLLM: standard classification loss on augmented preference
   labels (binary cross-entropy / preference loss). **No KL/temperature
   soft-target loss** is used for the router. [VERIFIED — no router uses the
   Hinton loss]
7. **Temperature scaling?** Not reported for the router in RouteLLM. Temperature
   scaling appears only as a *generative-student* KD device in
   `dynamic_routing_LLM` and in the general KD literature (§3). [VERIFIED/OPEN]
8. **Size / latency reduction measured?** For a *router* specifically: **none
   measured as a KD result** — RouteLLM's BERT router is already small; the paper
   reports *cost* savings from routing, not a KD compression ratio. [VERIFIED]
9. **Quality degraded?** N/A for router-KD (no such ablation exists in the
   surveyed set). [OPEN]
10. **Student deployed on edge hardware?** **No** surveyed router-KD work deploys
    the router on edge hardware (RouteLLM is server-side). This is an unoccupied
    lane (N6 in `01`). [VERIFIED by absence]
11. **Live network/system cost included?** vLLM Semantic Router claims to jointly
    optimize quality and *system cost* [OPEN — re-verify]; RouteLLM does not model
    live network/RTT/bandwidth. No surveyed router-KD work uses *measured* live
    cost. [VERIFIED/OPEN]
12. **Split-LLM execution?** **No.** No surveyed KD-routing work involves
    Split-LLM / activation-transfer execution. This is the strongest unoccupied
    lane (N4 in `01`). [VERIFIED by absence]

---

## 6. Primary-source checklist (what was opened 2026-10-02)

| Source | ID | Opened at | Supports |
|---|---|---|---|
| RouteLLM | arXiv:2406.18665; ICLR 2025 PDF; LMSYS blog; lm-sys/RouteLLM | abstract, ICLR PDF excerpts, blog, repo | §2.1 judge→BERT label distillation [VERIFIED] |
| RouterDC | arXiv:2409.19886; NeurIPS 2024 PDF; shuhao02/RouterDC | abstract, NeurIPS PDF, repo | §2.4 contrastive ≠ KD [VERIFIED] |
| Edge–cloud survey | arXiv:2507.16731 | abstract (via search) | §2.2 vLLM-router judge labels [abs] |
| `dynamic_routing_LLM` | github.com/ur-miya/dynamic_routing_LLM | repo README | §2.3 KD makes student not router [api] |
| PLaD | arXiv:2406.02886; Findings ACL 2024 | abstract | §3 ranking/preference KD [abs] |
| PAD | arXiv:2502.14272 | abstract | §3 preference-aligned KD [abs] |

**Not re-opened this sprint (must verify in `17` before load-bearing):** Hinton
2015 (1503.02531), DistilBERT (1910.01108), TinyBERT (1909.10351), MiniLM
(2002.10957), Ranking Distillation (KDD 2018), Guo 2017 temperature scaling,
primary vLLM-semantic-router source. All tagged `[ext]`/`[OPEN]` above.

---

## 7. Hand-off

- **To `03-kd-formulations`:** the RELATED table maps 1:1 to KD-1…KD-4; KD must
  be benchmarked against RouteLLM's *judge-label* approach (the real precedent),
  not a strawman. Carry the "KD may not add value → reject with evidence"
  branch (E1).
- **To `04-teacher-options`:** the only *established* teacher for routing is an
  **LLM-as-judge** (RouteLLM §2.1). A *larger router* teacher (T1) and an
  *oracle from observed outcomes* (T4) are `[PROPOSED]`, not precedented. The
  Jev/TypeSafe MCA forbids distilling that specific API
  (`research/jev-system-one.md` §J5) — exclude it as a teacher. [VERIFIED]
- **To `11-novelty-stress-test`:** novelty must be argued against RouteLLM's
  judge→classifier precedent. Defensible residual lanes (each unoccupied by the
  KD literature): per-action **calibrated utility vector** distillation (vs
  binary), **edge-deployed** router (N6), **Split-LLM action + measured
  activation cost** (N4, N12), **distilled-utility / live-cost separation** (N3).
  "We distil a router" alone is **not** defensible. [O]
- **To `17-verified-references.md` / `method-references.bib`:** add RouteLLM,
  RouterDC (as contrastive non-KD), PLaD, PAD, edge–cloud survey as verified;
  mark the `[ext]` foundational KD papers for primary re-verification before any
  BibTeX entry is finalized.
