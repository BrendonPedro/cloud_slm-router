# 00 — Review findings: skeptical audit of `methods-v2/`

*Deliverable 00 of `MICROENCODER_HARDENING_BRIEF.md` §27. Prepared 2026-10-04
(gnhf run `microencoder-hardeni-d272f9`, iteration 1).*

This file is the **entry register** for the v3 hardening sprint. It audits the
completed `methods-v2/` sprint as a skeptical systems/ML reviewer, records every
claim that is wrong, internally inconsistent, or stronger than its evidence, and
assigns each finding to the v3 deliverable that must resolve it. It does **not**
resolve the issues; it states them precisely enough that later deliverables can
be checked against them.

Scope guard (brief §0/§1/§30): the research problem, the micro-encoder family,
the learned-utility / measured-cost split, KD-as-investigation, hidden-state
routing as baseline, CL-as-journal and "no Jacobi" are **fixed** and are not
re-litigated here.

---

## 0. Evidence tags used in v3 (brief §29)

| Tag | Meaning |
|---|---|
| `[VERIFIED-BODY]` | full primary paper body checked **in v3** |
| `[VERIFIED-META]` | bibliographic identity confirmed only |
| `[AUTHOR-CLAIM]` | claim stated by paper authors, not reproduced |
| `[PROPOSED]` | our method / design choice |
| `[OPEN]` | needs experiment / advisor / Henry |
| `[REJECT]` | do not use |

**Migration rule from v2.** No v2 `[VERIFIED]` label carries over automatically.
Every v2 citation enters v3 as `[VERIFIED-META]` at most, and is upgraded to
`[VERIFIED-BODY]` only when the body is (re-)inspected in v3 and the supporting
section/page is recorded in `17-verified-references-v3.md`. v2's own register
(`methods-v2/17-verified-references.md`) records BEST-Route, HyDRA,
LLMRouterBench, RouteLMT, ConsRoute, Arch-Router, the prefill-activation router
and IRT-Router as **`[abs]`/`[api]` only** — none of these may be cited for a
quantitative, architectural or novelty-defeating statement until re-read.
"Verified by absence" statements (e.g. `methods-v2/02-kd-prior-art.md` §1,
"[VERIFIED by absence]") are reclassified as **bounded-search evidence**, never
`[VERIFIED-BODY]`.

---

## 1. Immutability baseline (recorded before any v3 file was written)

| Artifact | Check | Value at 2026-10-04 |
|---|---|---|
| `source/main-original.tex` | `sha256sum` | `06f5f9d7e9548c04ff59e098c1bd3c63a33d686114ccb8e37363d052b1707cf6` (matches v2's recorded `06f5f9d7…`) |
| `methods-v2/` (22 files) | `find methods-v2 -type f \| sort \| xargs sha256sum \| sha256sum` | `562faa69bdaeb69afc443739a40dfa5518d3a13f0a3adcffbe7c5f6dc75f1849` |
| Git working tree | `git status` | clean on branch `gnhf/microencoder-hardeni-d272f9` |

`FINAL-SUMMARY-v3.md` must re-run both hash commands and show identical values.

**LaTeX toolchain check (brief §20).** `which pdflatex latexmk xelatex lualatex
tectonic` returned **nothing** on 2026-10-04. Unless a toolchain is installed
later, `architecture-figure-v3.tex` and `proposed-solution-blue-v3.tex` can only
receive a **static syntax review**, and no compile success may be claimed.

---

## 2. Findings register

Severity: **B** = blocking (a stop-condition item or a mathematical/logical error
in the method); **M** = major (overclaim that would draw a reviewer rejection);
**m** = minor (wording/consistency).

### 2.1 Method formulation

| ID | v2 location | v2 statement | Problem | Sev. | Resolve in |
|---|---|---|---|---|---|
| **RF-A1** | `06-proposed-method.md` §3.1; `07-training-labels.md` §3 (L176); `09` §1 (L26) | One independent sigmoid head per action `a ∈ {EDGE, SPLIT(d₁…d_m), STRONG}` **and** `y(SPLIT(d),q) = y(full,q)`. | **Internal inconsistency.** If the split is lossless, every `SPLIT(d)` head and the head of the model it executes receive *identical* labels. The router then has `N = 2+m` heads but only `K` distinct supervision targets: `m` heads are redundant copies, they can disagree only through noise, and their disagreement can flip the argmax for reasons unrelated to quality. v2 itself says the learned axis "cannot distinguish SPLIT(d) from STRONG" (`09` L26–30) yet still allocates it separate heads. | **B** | `01`, `02` |
| **RF-A2** | `09` §1 (L26: "the full strong model") vs. `00`/`16` (Henry's model `[OPEN]`) | `SPLIT(d)` returns the *strong/cloud* model's answer. | The action→model map `M(a)` is never stated. Henry's split model may not be the same checkpoint as the STRONG/CLOUD model (a 70B cloud model and a split-able model on two RTX 3090s are not obviously the same). If `M(SPLIT(d)) ≠ M(STRONG)`, Split needs its own *model* utility but still no per-depth utility. | **B** | `01`, `10`, `14` |
| **RF-A3** | `06` §3.1 | A softmax "would entangle the learned utility with the cost term". | Unsupported. A softmax over actions is still query-only and does not see `s`; the real arguments against softmax are (i) mutually-exclusive normalization when several models can all succeed and (ii) re-normalization when the pool changes. The cost-entanglement argument should be dropped. | m | `01` |
| **RF-B** | `06` §3.1 (L120), `06` §6 table (L247), `FINAL-SUMMARY` §3 | Independent heads give "cheap model-pool addition": "add an action = add a head (no joint-softmax retrain)". | Reads as a no-retraining claim. A new head still needs **labelled outcomes for the new model**, **head training** (at minimum on a frozen backbone), and **its own calibration**; backbone drift may be needed if the new model's competence is not linearly decodable from the frozen features. True zero/few-shot expansion requires a model-profile / model-embedding architecture (cf. HyDRA's config profiles, RouterDC's learned model embeddings — both to be body-checked). Under RF-A1's fix, a new **split depth** of an existing model needs *no* new head at all (if E0 passes), which is the strongest honest version of this claim. | **M** | `01`, `15` |
| **RF-C** | `06` §3.2 (L153); echoed `11` (L157), `12` (L224–230), `13` (L51) | "Baking `s` into θ would force retraining on every network change." | Too strong (brief §4). A router taking bandwidth/RTT/load as inputs can generalize across states seen in training. The defensible arguments are different: fresh measurements enter directly; no need to synthesize a training distribution over network states; one semantic router reusable across deployments; independently testable/debuggable parts; out-of-support states (new link types, new split depths) need no relearning. | **M** | `09`, `proposed-solution-blue-v3.tex` |
| **RF-D** | `07` §3 (L176: "mathematically the full model's answer"); `FINAL-SUMMARY` §8 (L135 "Because `y(SPLIT(d),q)=y(full,q)`") | Split is lossless. | v2's deliverables `07`/`09` hedged this `[OPEN]` (F5), but the FINAL-SUMMARY and `10`/`12`/`16` state it as a premise. Losslessness depends on dtype at the cut, activation quantization/compression, serialization, KV-cache placement, sampling determinism, and kernel/hardware non-determinism (different GPUs or batch shapes can change floating-point reduction order even with no compression). "Bit-exact", "token-identical under greedy decoding", and "metric-equivalent" are three different conditions and must be separated. | **B** | `02`, `13` (E0) |
| **RF-E** | `08` §SC1/SC3 (L211–216) | λ in `argmax[Û − λC]` "**is** the KKT multiplier" of the SLA-constrained problem. | Only under conditions not stated: the per-query decision is discrete, so the constrained average-cost problem can have a duality gap unless randomized policies are allowed; λ is a Lagrange multiplier of the *expected* constraint, not of a per-query SLA. Also v2 still adds heterogeneous units after "normalization" whose reference scales are arbitrary. | **M** | `09` |
| **RF-F** | `07` §2 (target E), `FINAL-SUMMARY` §4 | Student predicts "per-action calibrated probability of success". | "Success" is undefined for open-ended generation, partial-credit metrics and pairwise-preference data. The manuscript's dataset (SimpleQA via LLMRouterBench, manuscript §Experimental Setup) is binary-gradable, but the full-paper pool/datasets may not be. | **M** | `08` |

### 2.2 Knowledge distillation

| ID | v2 location | v2 statement | Problem | Sev. | Resolve in |
|---|---|---|---|---|---|
| **RF-G1** | `02-kd-prior-art.md` §1 (L44–52) | RouteLLM "distils a frontier judge's pairwise preferences into a small BERT classifier **in all but name**"; "RouteLLM already does judge→classifier **soft** supervision". | Terminology not supported by the literature as stated. Teacher/judge-generated **hard** labels are pseudo-labelling / LLM-as-a-judge supervision / data augmentation, not soft-target KD in the Hinton sense. Whether RouteLLM's judge labels are hard or graded must be read from its body (§ on data augmentation) before any wording is chosen. | **M** | `04` |
| **RF-G2** | `04-teacher-options.md`, `FINAL-SUMMARY` §5–6 | Teacher T1 = ModernBERT-large trained on the **same** observed `y(a,q)` as the student. | The "dark knowledge" rationale is weak: T1 sees no information beyond `y`. Its soft outputs can only help via (a) smoothing label noise, (b) transferring a better-generalizing function learned with more capacity, (c) encoding inter-action correlation. All three have cheaper non-KD competitors: label smoothing, stronger regularization, longer/tuned training of the student, self-distillation/ensembling, and post-hoc temperature scaling. v2's only control is α=1 with the same hyperparameters — this is **not** the strongest non-KD control. | **B** | `03`, `13` (E1) |
| **RF-G3** | `11` §9 N2; `12` E4 | "Calibration preserved under distillation" proposed as a standalone-defensible novelty lane. | Must be compared against *non-KD student + post-hoc temperature scaling* (Guo et al.) at matched validation data; otherwise calibration "gain" is an artefact. v2 lists this as a falsifier but still ranks N2 as standalone-defensible before any data. | **M** | `03`, `12`, `13` |

### 2.3 Prior-art characterisation

| ID | v2 location | v2 statement | Problem | Sev. | Resolve in |
|---|---|---|---|---|---|
| **RF-H1** | `01` §2.4 (L160–163) vs. `17` §1.4 (L84) and `11` N1/N3 downgrades | HyDRA has "4 independent sigmoid **capability** heads (reasoning, code-gen, debugging, tool-use)" (`01`) **vs.** "4-head sigmoid **utility** output" (`17`). | **v2 is internally inconsistent.** Capability dimensions matched against model profiles are not per-model or per-action utilities. v2 used the overlap to downgrade our per-action-head novelty without establishing equivalence. In addition `17` records HyDRA as `[abs]/[api]` only while `01` tags some items `[body]` — the inspection ceiling is unclear. Two unreconciled latency figures (86 ms median vs 55 ms P50) are both author claims. | **B** | `05` |
| **RF-H2** | `01` §2.5 (L198); `FINAL-SUMMARY` §2, §10 | LLMRouterBench: "backbone embedding choice has limited impact" — used as `[VERIFIED]` to justify ModernBERT and to REJECT encoder-architecture novelty. | Body never read (`17` §1.5: `[api]`+abstract). Tested backbones, routers, datasets, model pools and metrics are unknown, so the scope of "limited impact" is unknown. It cannot be generalised to "encoder architecture never matters" or used for an edge-latency argument. | **B** | `05`, `07` |
| **RF-H3** | `17` §1.3, §1.6–1.10 | BEST-Route, RouteLMT, ConsRoute, Arch-Router, prefill-activation router, IRT-Router used for positioning. | All `[api]`/`[abs]`. ConsRoute in particular is used to pre-empt the "comm-aware cost" lane — a novelty-defeating use that requires a body read. | **M** | `05`, `17` |
| **RF-H4** | v2 sprint scope (`11` limitations) | Prior-art search was arXiv/ACL-centric. | ACM (SIGCOMM, MobiCom, MobiSys, SenSys, CoNEXT, ASPLOS, EuroSys), IEEE (INFOCOM, TMC, JSAC, ICDCS), USENIX ATC/NSDI and MLSys were not systematically searched. Classic DNN-partitioning work (dynamic split-point selection under bandwidth) and edge-cloud LLM collaborative-inference systems are exactly where the Split(d)-as-action lane is most likely to be pre-empted. | **B** | `06` |

### 2.4 Novelty and manuscript text

| ID | v2 location | v2 statement | Problem | Sev. | Resolve in |
|---|---|---|---|---|---|
| **RF-I1** | `11-novelty-stress-test.md` L98, L278; `FINAL-SUMMARY` §11 | "…**the first router to** (i) … and (ii) treat Split(d) as a first-class routable action…" | Banned by brief §10. Based on arXiv/ACL search only (RF-H4). Must become "We propose / we investigate / to our knowledge (search scope documented)". | **B** | `12` |
| **RF-I2** | `methods-v2/proposed-solution-blue.tex` | Manuscript-ready Proposed Solution. | Contains **zero** `\cite` commands (`grep -c cite` = 0). Every factual sentence (ModernBERT, KD, temperature scaling, split inference, prior routers) is naked. Fails brief §21/§22. | **B** | `proposed-solution-blue-v3.tex`, `16` |
| **RF-I3** | `11` §9 | N2 and N4 "standalone-defensible" before experiments. | Defensibility is experiment-gated (E1/E4/E7) and search-gated (RF-H4). Should be the *Conditional* tier of the three-tier contribution statement (brief §24), not a pre-experiment claim. | M | `12` |

### 2.5 Architecture figure

| ID | v2 location | Problem | Sev. | Resolve in |
|---|---|---|---|---|
| **RF-J1** | `methods-v2/architecture-figure.tex` L100 | Uses `$\blacktriangledown$` without `\usepackage{amssymb}` → undefined control sequence. | **B** | `architecture-figure-v3.tex` |
| **RF-J2** | same, L100 | Uses `\Letter` (a `marvosym` glyph) — package not loaded; also decorative and unnecessary. | **B** | same |
| **RF-J3** | same, L158 | Uses `$\dashrightarrow$` without `amssymb`. | **B** | same |
| **RF-J4** | same (whole figure, per `15` spec) | Figure encodes per-action utility heads, which RF-A1 may invalidate; it must be redrawn from the `01` decision, separating semantic prediction, runtime measurement, training-only teacher and execution actions, with no CL boxes. | M | same |
| **RF-J5** | v2 `FINAL-SUMMARY` §18 | Correctly states no toolchain existed. Retain this honesty; still true on 2026-10-04 (§1). | — | `FINAL-SUMMARY-v3` |

### 2.6 Model pool and testbed

| ID | v2 / manuscript location | Problem | Sev. | Resolve in |
|---|---|---|---|---|
| **RF-K1** | `source/main-original.tex` model list (Gemma-4 "E2B-A4B", "E4B-A4B", "12B-A4B"; Phi-4-mini-3.8B; Llama-3.1-8B; Fast-dLLM-v2-7B; "Qwen3-72B-Instruct"; Llama-3.3-70B) | v2 found `Qwen3-72B-Instruct` does not exist. The Gemma-4 variant names (dense "E2B"/"E4B" labels combined with MoE-style "A4B" suffixes) look malformed and must be checked against official model cards; no name may be corrected by guess. | M | `10` |
| **RF-K2** | manuscript §Experimental Setup (edge = Xeon W-2123, 64 GB, 2×RTX 3090; server sentence unfinished) | "Edge" in this paper is a **workstation-class** node, not a phone/Jetson. Edge-latency evidence for the encoder (ONNX/INT8 CPU numbers from other papers) is only analogical. | m | `07`, `14` |
| **RF-K3** | `16` §1 | The advisor's B1/Gemma remark cannot be reconstructed. Keep `[OPEN]`; do not invent. | — | `10`, `14` |

---

## 3. What v2 got right (retain, subject to re-citation)

These survive the audit as design content; each still needs v3-grade citations.

1. **Decoupling learned query-conditioned utility from runtime-measured system
   cost** — the advisor-approved core (`methods-v2/00` item 2). Only its
   *justification* (RF-C) is wrong, not the decision.
2. **The observed-outcome oracle is a label, not a teacher** (`04`): conflating
   them would make KD vacuous. Correct and important.
3. **α = 1 as the built-in non-distilled control** and a pre-registered
   "KD dropped" branch (`03`, `12` E1). Correct direction; insufficient alone
   (RF-G2).
4. **TF-IDF + LR as the bar to beat** and the oracle-headroom degeneracy guard
   (MP2). Correct.
5. **Hidden-state self-routing kept as a baseline**; **CL isolated to the
   journal** with only near-zero-cost hooks in conference code. Correct.
6. **Honest `[OPEN]` treatment of Henry's code** — nothing invented. Correct.
7. **Constrained/SLA + Pareto evaluation alongside the λ form** (`08` SC3/SC4).
   Correct direction; λ's interpretation needs the caveats in RF-E.
8. **Recording that no LaTeX toolchain exists** rather than claiming a compile.

---

## 4. Preliminary hypotheses to be tested in later deliverables (not decisions)

These are *starting positions* for the v3 investigations, written down so that
later deliverables can be checked for having actually argued them rather than
assumed them. All are `[PROPOSED]`/`[OPEN]`.

- **H-A (for `01`).** Under exact/lossless split, utility should attach to the
  **model** `M(a)`, with depth entering only through `C(a|s)`:
  `R(q,s) = argmax_a [Û_θ(M(a)|q) − λ·C(a|s)]`. This removes RF-A1's redundant
  heads, makes adding a split depth a pure systems change, and maps literally onto
  the manuscript's `f_θ(q, M_k)`. Action-level utility is needed only if E0 shows
  depth-dependent quality, in which case the preferred fallback is
  `Û(M|q) − Δ̂(d,q)` (shared model term + small depth correction) rather than
  fully independent per-depth heads. *To be stress-tested, not assumed.*
- **H-B (for `03`).** The strongest non-KD control is a student with the same
  architecture and data, given the **same total hyperparameter-tuning budget** as
  the KD student, with label smoothing and post-hoc temperature scaling enabled.
  KD must beat *that*, not just α=1 at fixed hyperparameters.
- **H-C (for `08`).** The general target is an expected task score
  `E[S(y_M(q), q)]` with `S ∈ [0,1]`; `P(pass)` is the special case of a binary
  `S`. Whether a binary or graded target is used should follow the dataset's
  native metric.
- **H-D (for `09`).** The first implementation should use a **latency-SLA
  constrained** decision (maximize Û subject to predicted latency ≤ SLA, bytes
  reported separately), keeping λ only as the theoretical Lagrangian view and
  for Pareto sweeps.
- **H-E (for `06`/`12`).** The Split(d)-as-routable-action lane is the most
  exposed to systems prior art (dynamic DNN partitioning, edge-cloud
  collaborative LLM inference). Expect a downgrade to "we combine query-aware
  model utility with partition-point selection" unless the search finds
  otherwise.

---

## 5. v3 work plan (dependency order)

| Order | Deliverable(s) | Depends on | Primary findings addressed |
|---|---|---|---|
| 1 | `00` (this file) | — | register |
| 2 | `05-full-routing-prior-art.md` (body reads: RouteLLM, RouterDC, HyDRA, LLMRouterBench, ConsRoute, Hybrid-LLM, BEST-Route, prefill-activation) | — | RF-G1, RF-H1–H3 |
| 3 | `04-routeLLM-terminology-review.md` | `05` (RouteLLM body) | RF-G1 |
| 4 | `06-systems-prior-art-map.md` (ACM/IEEE/USENIX/MLSys search) | — | RF-H4, RF-I1 |
| 5 | `07-backbone-verification.md` | `05` (LLMRouterBench body) | RF-H2, RF-K2 |
| 6 | `02-split-equivalence-analysis.md` | `06` (split-inference systems) | RF-D |
| 7 | `01-model-vs-action-utility.md` | `02`, `05` (HyDRA, RouterDC) | RF-A1–A3, RF-B |
| 8 | `08-utility-definition.md`, `09-cost-policy.md` | `01` | RF-F, RF-C, RF-E |
| 9 | `03-kd-hardening.md` | `04`, `08` | RF-G2, RF-G3 |
| 10 | `10-model-pool.md`, `11-baselines-v3.md` | `05`, `06` | RF-K1, RF-K3 |
| 11 | `12-novelty-v3.md`, `13-experiments-v3.md` (incl. E0) | all above | RF-I1, RF-I3, RF-D |
| 12 | `14-henry-checklist.md`, `15-conference-vs-journal.md` | `01`, `02`, `13` | RF-A2, RF-B |
| 13 | `17-verified-references-v3.md`, `method-references-v3.bib` | all reads | migration rule §0 |
| 14 | `architecture-figure-v3.tex`, `proposed-solution-blue-v3.tex`, `16-citation-audit.md` | `01`–`17` | RF-I2, RF-J1–J4 |
| 15 | `FINAL-SUMMARY-v3.md` | everything | brief §28 |

---

## 6. Checklist mapping to the brief §31 stop condition

| §31 item | Finding(s) | Owner |
|---|---|---|
| 1 model-vs-action resolved | RF-A1–A3, RF-B | `01` |
| 2 exact vs lossy split separated | RF-D | `02` |
| 3 E0 exists | RF-D | `13` |
| 4 KD teacher survives skeptical review | RF-G2, RF-G3 | `03` |
| 5 RouteLLM terminology corrected | RF-G1 | `04` |
| 6 HyDRA body checked | RF-H1 | `05` |
| 7 LLMRouterBench body checked, bounded | RF-H2 | `05`, `07` |
| 8 ModernBERT facts verified | RF-H2, RF-K2 | `07` |
| 9 systems-venue search expanded | RF-H4 | `06` |
| 10 no unsupported "first" | RF-I1 | `12`, blue tex |
| 11 conference/journal separated | (retained, §3.5) | `15` |
| 12 corrected architecture specified | RF-A1, RF-J4 | `01`, figure |
| 13 blue text has real citations | RF-I2 | blue tex |
| 14 citation audit complete | RF-I2 | `16` |
| 15 verified BibTeX | §0 migration rule | `.bib` |
| 16 figure source repaired | RF-J1–J3 | figure |
| 17 compile attempted if toolchain | §1 (none found) | figure / FINAL |
| 18 novelty evidence-tagged, gated | RF-I3 | `12` |
| 19 no invented results | — (none in v2 either) | all |
| 20 FINAL-SUMMARY answers 28 Qs | — | `FINAL-SUMMARY-v3` |
