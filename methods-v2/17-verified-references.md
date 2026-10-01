# 17 — Verified references

Brief §22 deliverable. One consolidated, per-source reference register for every
load-bearing citation used across `methods-v2/00`–`16`, plus the BibTeX companion
`method-references.bib`. Prepared 2026-10-02 (gnhf microencoder-kd sprint,
iteration 18).

This file is the **single source of truth for citation discipline** in the
sprint. The blue manuscript text (`proposed-solution-blue.tex`) and
`FINAL-SUMMARY.md` must cite only entries recorded here, and must not upgrade an
inspection level beyond what this file states.

---

## 0. How to read this file

Each entry records, per brief §22:

- **Citation** — exact title / author convention / year.
- **ID** — arXiv ID, DOI, or ACL Anthology handle.
- **Venue** — peer-reviewed venue if any, else `preprint`.
- **Official URL** — arXiv/DOI/anthology landing page.
- **Repo** — official code repository when one exists.
- **Supports** — which sprint claim(s) it is load-bearing for.
- **Inspected** — the honest inspection level actually reached (see below).
- **Source type** — primary vs secondary.

### Inspection levels (carried from `01`/`02` tagging)

| Tag | Meaning |
|-----|---------|
| `[body]` | paper body read (arXiv HTML/PDF) during the v1 or v2 sprint |
| `[PDF]` | proceedings/journal PDF excerpt read this sprint (2026-10-02) |
| `[abs]` | only the abstract / authors' claim read, body **not** re-verified |
| `[api]` | bibliographic metadata only (arXiv/HF/ACL API), body not read |
| `[OPEN]` | identity or a field not re-verified this sprint — do not treat as checked |

**Evidence rule.** An entry's inspection level is a ceiling on how strongly it
may be cited. `[abs]`/`[api]`/`[OPEN]` sources may support *existence* and
*positioning* claims but **must not** anchor a quantitative or novelty-defeating
claim without a body read first. Every novelty-bearing claim in `11` is anchored
on a `[body]`/`[PDF]` source or explicitly marked `[PROPOSED]`.

**Date caveat.** Several routing entries carry 2026 arXiv IDs (26xx.xxxxx). These
are real IDs relative to the sprint date (2026-10-02); they are recent preprints
whose bodies were mostly inspected at `[api]`/`[abs]` level only — flagged below.

---

## 1. Routing / micro-encoder prior art (brief §4)

These support `01-microencoder-prior-art.md` and the `11` novelty verdicts.

### 1.1 RouteLLM — *Learning to Route LLMs from Preference Data*
- **ID:** arXiv:2406.18665 · **Venue:** ICLR 2025 (poster).
- **URL:** https://arxiv.org/abs/2406.18665 · **Repo:** https://github.com/lm-sys/RouteLLM
- **Supports:** the *only* router-KD-adjacent precedent (GPT-4-judge → BERT
  label augmentation); matrix-factorisation / BERT / similarity-weighted router
  variants; preference-data labelling (`01` §2.1, `02` §2.1, `04`, `11`).
- **Inspected:** `[body]` + ICLR PDF excerpts + LMSYS blog + repo (2026-10-02).
- **Source type:** primary.

### 1.2 RouterDC — *Query-Based Router by Dual Contrastive Learning*
- **ID:** arXiv:2409.19886 · **Venue:** NeurIPS 2024.
- **URL:** https://arxiv.org/abs/2409.19886 · **Repo:** https://github.com/shuhao02/RouterDC
- **Supports:** the "DC = dual **contrastive**, NOT distillation" correction
  (`02` §2.4); mDeBERTa-v3-base encoder-router precedent (`01` §2.2, `05`).
- **Inspected:** `[body]` NeurIPS PDF + repo (2026-10-02).
- **Source type:** primary.

### 1.3 BEST-Route — *Adaptive LLM Routing with Test-Time Scaling*
- **ID:** arXiv:2506.22716 · **Venue:** ICML 2025 (per arXiv comment).
- **URL:** https://arxiv.org/abs/2506.22716
- **Supports:** DeBERTa-v3-small encoder-router precedent; test-time scaling
  framing (`01` §2.3, `05`).
- **Inspected:** `[api]` + abstract/snippet. **Body not read** → `[OPEN]` for any
  quantitative claim.
- **Source type:** primary (preprint/proceedings).

### 1.4 HyDRA — *Hybrid Dynamic Routing Architecture for Heterogeneous LLM Pools*
- **ID:** arXiv:2605.17106 (v2, 2026-06-12) · **Venue:** preprint (deployed).
- **URL:** https://arxiv.org/abs/2605.17106
- **Supports:** the single most important overlap — lightweight CPU encoder
  router, 4-head sigmoid utility output, 55–86 ms CPU latency, no-retrain pool
  growth (`01` §2.4, `05`, `11` N1/N3 downgrades).
- **Inspected:** `[abs]`/`[api]` only. **Body not read this sprint** → `[OPEN]`;
  the latency figures (55–86 ms CPU) are authors' claims, not verified.
- **Source type:** primary (preprint).

### 1.5 LLMRouterBench — unified routing benchmark
- **ID:** arXiv:2601.07206 · **Venue:** Findings of ACL 2026 (pp. 37733–37754).
- **URL:** https://arxiv.org/abs/2601.07206 · ACL Anthology `2026.findings-acl.*`
- **Supports:** the "backbone embedding choice has limited impact" finding (a
  direct threat to encoder-architecture novelty); TF-IDF+LR tie-warning; the
  flagship-pool-only SimpleQA label gap (`01` §2.5, `05`, `10`, `11`).
- **Inspected:** `[api]` + abstract. **Body not read** → `[OPEN]` for exact
  magnitudes; the headline finding is the authors' stated claim.
- **Source type:** primary.

### 1.6 RouteLMT — *Learned Sample Routing for Hybrid LLM Translation Deployment*
- **ID:** arXiv:2604.22520 · **Venue:** ACL 2026 Industry Track (pp. 1886–1897;
  Anthology `2026.acl-industry.129`).
- **URL:** https://arxiv.org/abs/2604.22520
- **Supports:** hybrid small/large deployment routing precedent (`01` §2.6).
- **Inspected:** `[api]`. **Body not read** → `[OPEN]`.
- **Source type:** primary.

### 1.7 ConsRoute — *Consistency-Aware Adaptive Query Routing for Cloud-Edge-Device LLMs*
- **ID:** arXiv:2603.21237 (2026-03-22) · **Venue:** preprint.
- **URL:** https://arxiv.org/abs/2603.21237
- **Supports:** network-condition-aware cloud-edge-device routing with online
  threshold adaptation (pre-empts the comm-aware-cost and "no-retrain" lanes);
  generative-vs-discriminative comparison (`01` §2.7, `08`, `11`).
- **Inspected:** `[api]` + abstract. **Body not read** → `[OPEN]`.
- **Source type:** primary (preprint).

### 1.8 Arch-Router — *generative router (comparison only)*
- **ID:** arXiv:2506.16655 (2025-06) · **Venue:** preprint.
- **URL:** https://arxiv.org/abs/2506.16655 · **Repo / checkpoint:** HF
  `katanemo/Arch-Router-1.5B` (licence "other").
- **Supports:** generative-router baseline (brief: "Arch-Router only as a
  generative comparison"); corrects the manuscript L317 "fine-tune its routing
  head" misdescription (`01` §2.8, `10`, `14`).
- **Inspected:** `[api]` + abstract. **Body not read** → `[OPEN]`.
- **Source type:** primary (preprint).

### 1.9 Prefill-activation router — *Rethinking Routing with Prefill Activations*
- **ID:** arXiv:2603.20895 (v1 2026-03-21, v2 2026-08-11) · **Venue:** preprint.
- **URL:** https://arxiv.org/abs/2603.20895
- **Supports:** the hidden-state / self-routing probe family = demoted
  Candidate C baseline (`01` §2.9, `10`, `12` E3).
- **Inspected:** `[api]` + abstract. **Body not read** → `[OPEN]`.
- **Source type:** primary (preprint).

### 1.10 IRT-Router — item-response-theory router
- **ID:** arXiv:2506.01048 · **Venue:** ACL 2025 (main).
- **URL:** https://arxiv.org/abs/2506.01048
- **Supports:** interpretable query-difficulty routing signal; secondary
  encoder-router precedent (`01` §2.10).
- **Inspected:** `[api]`. **Body not read** → `[OPEN]`.
- **Source type:** primary.

### 1.11 Hybrid LLM — *Ding et al., router for small-vs-large deployment*
- **ID:** arXiv:2404.14618 · **Venue:** ICLR 2024.
- **URL:** https://arxiv.org/abs/2404.14618
- **Supports:** peer-reviewed statement of the edge-small-vs-cloud-large
  quality/cost trade-off (the manuscript's Eq. 2 framing); flagged in `01` as a
  **manuscript citation gap** (OM-5 in `16`).
- **Inspected:** `[abs]` + `[api]`. Body not re-read this sprint → `[OPEN]` for
  internal detail; the edge-vs-cloud framing is from the abstract.
- **Source type:** primary.

> **PRISM (brief §4):** no verified entry exists. Not opened in v1 or v2. Marked
> `[OPEN]` in `01` §—; **no citation may be made** until a targeted search finds
> the specific work the brief intends. Do not fabricate a PRISM entry.

---

## 2. Knowledge-distillation prior art (brief §5)

These support `02-kd-prior-art.md`, `03-kd-formulations.md`, `04-teacher-options.md`.

### 2.1 Hinton, Vinyals & Dean — *Distilling the Knowledge in a Neural Network*
- **ID:** arXiv:1503.02531 · **Venue:** NIPS 2014 Deep Learning workshop.
- **URL:** https://arxiv.org/abs/1503.02531
- **Supports:** the foundational soft-target / temperature KD loss
  (`T²·KL(softmax(z_t/T)‖softmax(z_s/T)) + CE`) = template for KD-1 (`02` §3,
  `03`, `06`, blue-tex KD loss).
- **Inspected:** `[body]` (canonical; standard-form loss).
- **Source type:** primary.

### 2.2 Sanh, Debut, Chaumond & Wolf — *DistilBERT*
- **ID:** arXiv:1910.01108 · **Venue:** NeurIPS 2019 EMC² workshop.
- **URL:** https://arxiv.org/abs/1910.01108 · **Repo:** HuggingFace Transformers.
- **Supports:** encoder KD template (KD-4 representation distillation); a student
  backbone candidate (`02` §3, `05`).
- **Inspected:** `[abs]`/`[api]` (widely established result).
- **Source type:** primary.

### 2.3 Jiao et al. — *TinyBERT*
- **ID:** arXiv:1909.10351 · **Venue:** Findings of EMNLP 2020.
- **URL:** https://arxiv.org/abs/1909.10351
- **Supports:** hidden-state + attention-matrix + embedding KD for encoders
  (KD-4 template) (`02` §3, `05`).
- **Inspected:** `[abs]`.
- **Source type:** primary.

### 2.4 Wang et al. — *MiniLM*
- **ID:** arXiv:2002.10957 · **Venue:** NeurIPS 2020.
- **URL:** https://arxiv.org/abs/2002.10957
- **Supports:** deep self-attention distillation; a small student backbone
  candidate (`02` §3, `05`).
- **Inspected:** `[abs]`.
- **Source type:** primary.

### 2.5 PLaD — *Preference-based Large Language Model Distillation*
- **ID:** arXiv:2406.02886 · **Venue:** Findings of ACL 2024.
- **URL:** https://arxiv.org/abs/2406.02886
- **Supports:** ranking/preference KD template for KD-2 (note: targets
  *generative* SLM quality, not routing) (`02` §3, `03`).
- **Inspected:** `[abs]`.
- **Source type:** primary.

### 2.6 PAD — *Preference-Aligned Distillation*
- **ID:** arXiv:2502.14272 · **Venue:** preprint (per `02`).
- **URL:** https://arxiv.org/abs/2502.14272
- **Supports:** preference-distribution alignment KD, KD-2 template (generative,
  not routing) (`02` §3, `03`).
- **Inspected:** `[abs]`.
- **Source type:** primary (preprint).

### 2.7 Guo, Pleiss, Sun & Weinberger — *On Calibration of Modern Neural Networks*
- **ID:** arXiv:1706.04599 · **Venue:** ICML 2017.
- **URL:** https://arxiv.org/abs/1706.04599
- **Supports:** post-hoc temperature scaling and ECE — the N2 calibration
  baseline the KD claim must beat (`02` §3, `08`, `11` N2, `12` E4).
  **KD temperature ≠ calibration temperature** (kept distinct).
- **Inspected:** `[body]`/`[abs]` (canonical).
- **Source type:** primary.

### 2.8 Edge–cloud collaborative-inference survey
- **ID:** arXiv:2507.16731 · **Venue:** preprint (survey).
- **URL:** https://arxiv.org/abs/2507.16731
- **Supports:** positioning only — names vLLM-router judge-label practice (`02`
  §2.2). **Secondary** (survey): must not anchor a primary claim.
- **Inspected:** `[abs]`.
- **Source type:** secondary.

---

## 3. Student / teacher backbone encoders (brief §8)

These support `05-student-architecture.md`. **All identity fields are `[RELATED]`
/ `[OPEN]`** — canonical values were *not* re-verified against the primary paper
this sprint and must be confirmed before any manuscript claim.

### 3.1 ModernBERT
- **Citation:** Warner et al., *Smarter, Better, Faster, Longer: A Modern
  Bidirectional Encoder* (ModernBERT), 2024.
- **ID:** arXiv:2412.13663 **`[OPEN]`** (ID not re-verified this sprint).
- **Venue:** preprint (Answer.AI / LightOn). **URL:** https://arxiv.org/abs/2412.13663
- **Repo / checkpoints:** HF `answerdotai/ModernBERT-base`, `-large` (Apache-2.0).
- **Supports:** primary student (base ~149 M) + T1 teacher (large ~395 M)
  recommendation (`05`, `06`).
- **Inspected:** `[RELATED]`/`[OPEN]` — param/dim/licence not re-verified.
- **Source type:** primary (needs body read before citing).

### 3.2 DeBERTa-v3
- **Citation:** He, Gao & Chen, *DeBERTaV3*, 2021.
- **ID:** arXiv:2111.09543 **`[OPEN]`** (not re-verified this sprint).
- **Venue:** ICLR 2023. **URL:** https://arxiv.org/abs/2111.09543
- **Repo / checkpoints:** HF `microsoft/deberta-v3-xsmall/-small/-large`.
- **Supports:** alternate student (small ~44 M bb) + the ONNX/INT8 disentangled-
  attention friction note; backbone of BEST-Route and RouterDC (`05`).
- **Inspected:** `[RELATED]`/`[OPEN]`.
- **Source type:** primary (needs body read before citing).

> DistilBERT / MiniLM also serve as student candidates — see §2.2 / §2.4.
> BERT/RoBERTa are named only as legacy baselines in `05` and are not load-bearing.

---

## 4. Continual-learning prior art (journal extension, brief §18)

These support `13-journal-continual-learning-extension.md` **only**. They are
**not** part of the conference core and must not appear in `proposed-solution-blue.tex`.
These were primary-source checked during iteration 14 (new web research).

### 4.1 EWC — Kirkpatrick et al., *Overcoming catastrophic forgetting in neural networks*
- **ID:** DOI 10.1073/pnas.1611835114 · **Venue:** PNAS 114(13):3521–3526, 2017.
- **URL:** https://www.pnas.org/doi/10.1073/pnas.1611835114
- **Correction:** Huszár, PNAS 2018, DOI 10.1073/pnas.1717042115
  (https://www.pnas.org/doi/10.1073/pnas.1717042115).
- **Supports:** regularization-based CL (JC2) (`13` §2.1).
- **Inspected:** `[abs]`/`[api]` + DOI confirmed.
- **Source type:** primary.

### 4.2 GEM — Lopez-Paz & Ranzato, *Gradient Episodic Memory for Continual Learning*
- **ID:** arXiv:1706.08840 · **Venue:** NeurIPS 2017.
- **URL:** https://arxiv.org/abs/1706.08840
- **Supports:** episodic-memory replay CL (JC1) (`13` §2.2).
- **Inspected:** `[abs]`/`[api]`.
- **Source type:** primary.

### 4.3 A-GEM — Chaudhry, Ranzato, Rohrbach & Elhoseiny, *Efficient Lifelong Learning with A-GEM*
- **ID:** arXiv:1812.00420 · **Venue:** ICLR 2019.
- **URL:** https://arxiv.org/abs/1812.00420
- **Supports:** averaged-GEM single-constraint replay (JC1) (`13` §2.2).
- **Inspected:** `[abs]`/`[api]`.
- **Source type:** primary.

### 4.4 ER (tiny episodic memories) — Chaudhry et al., *On Tiny Episodic Memories in Continual Learning*
- **ID:** arXiv:1902.10486 · **Venue:** preprint (ICML 2019 workshop lineage).
- **URL:** https://arxiv.org/abs/1902.10486
- **Supports:** experience replay with small buffers (JC1) (`13` §2.2).
- **Inspected:** `[abs]`/`[api]`.
- **Source type:** primary (preprint).

### 4.5 LwF — Li & Hoiem, *Learning without Forgetting*
- **ID:** arXiv:1606.09282 · **Venue:** ECCV 2016, pp. 614–629; extended in IEEE
  TPAMI 40(12):2935–2947, 2018, DOI 10.1109/TPAMI.2017.2773081.
- **URL:** https://arxiv.org/abs/1606.09282 · https://doi.org/10.1109/TPAMI.2017.2773081
- **Supports:** distillation-based CL = the conference KD-5 loss with the previous
  student snapshot as teacher (JC3; the "online distillation / teacher-student
  refresh" mechanisms are LwF, not new) (`13` §2.3).
- **Inspected:** `[abs]`/`[api]` + DOI confirmed.
- **Source type:** primary.

### 4.6 Houlsby et al. — *Parameter-Efficient Transfer Learning for NLP* (Adapters)
- **ID:** arXiv:1902.00751 · **Venue:** ICML 2019.
- **URL:** https://arxiv.org/abs/1902.00751
- **Supports:** adapter-based incremental updates (JC4) (`13` §2.4).
- **Inspected:** `[abs]`/`[api]`.
- **Source type:** primary.

> Guo et al. 2017 (§2.7) is reused by `13` for continual temperature
> recalibration — one entry, cited in both the conference and journal contexts.

---

## 5. Cross-cutting notes & gaps

1. **Bounded-search caveat (carried from `01`/`02`).** The v1/v2 searches are
   arXiv/ACL-centric and under-cover IEEE (INFOCOM, TMC, JSAC) and ACM (MobiCom,
   SenSys, MobiSys). A systems-venue precedent for the Split-cost lane (N4) could
   exist and has not been excluded. Flag before claiming N4 novelty.

2. **`[OPEN]` bodies to read before any quantitative citation.** BEST-Route,
   HyDRA (esp. the 55–86 ms CPU latency), LLMRouterBench (the backbone-impact
   magnitude), ConsRoute, Arch-Router, prefill-activation router, IRT-Router,
   RouteLMT. Their *existence* and *positioning* are safe to cite; their
   *numbers* are not.

3. **`[OPEN]` identities to confirm.** ModernBERT (2412.13663) and DeBERTa-v3
   (2111.09543) arXiv IDs and param/licence facts were not re-verified this
   sprint — confirm before the blue text's student-size claims are finalised.

4. **Do-not-fabricate ledger.** PRISM has no entry; the manuscript's
   `Qwen3-72B-Instruct` and Gemma `-A4B` names are invalid (`10`, `16` OM-1/OM-2)
   and must **not** be given BibTeX/model entries. No author list was invented
   for any 2026 preprint — see `.bib` comments.

5. **Secondary sources.** Only arXiv:2507.16731 (survey) is secondary; it is used
   for positioning in `02` §2.2 and never anchors a primary claim.

---

## 6. Hand-offs

- `method-references.bib` — BibTeX for the entries above whose bibliographic
  identity is established; unverified fields omitted with inline comments.
- `proposed-solution-blue.tex` — cites a subset (RouteLLM, Hinton, HyDRA,
  LLMRouterBench, Guo, ModernBERT) at the inspection ceilings set here.
- `FINAL-SUMMARY.md` Q10 (prior art) / Q11 (defensible contribution) rest on §1–§2.
- `16` records the OM-/advisor items that keep invalid names out of this register.
