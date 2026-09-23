# Deliverable 5 — Jev / TypeSafe "System One Models": what is known, and what it means for our router

Date of review: **2026-09-23**. Prepared in an AI-assisted research sprint (see
`advisor/research-sprint-report.md` once it exists). Jev was publicly announced
**8 days before this review**. Everything here is young, and most of it is
self-reported by the vendor.

**Evidence labels used throughout**

| Label | Meaning |
|---|---|
| **[V]** | Vendor claim: TypeSafe's blog, docs, homepage or terms. Not independently checked by the vendor's own admission unless noted. |
| **[I]** | Independent third-party measurement. Here that means **non-peer-reviewed GitHub repos** that publish raw responses. We read their READMEs only. **We did not re-run or re-audit their raw data.** |
| **[S]** | Secondary reporting (Wikipedia, press). Used only where no primary source exists, and flagged. |
| **[O]** | Our inference or analysis. Not a fact about Jev. |
| **[P]** | Our proposal. Not an established technique. |

**We have no TypeSafe API key, and we made no Jev calls.** Every Jev number below
comes from someone else.

Raw copies of every page used were saved on 2026-09-23 under
`research/raw/jev/`. `fetch-log.txt` there records the URL, byte count and UTC
timestamp for each file. Vendor pages can change, so quote from those copies.

---

## 1. Source records

| # | Title | Author / org | Date | Type / status | URL | Establishes | Code / models / data |
|---|---|---|---|---|---|---|---|
| J1 | "Introducing System One Models & Jev" | Diogo Almeida (founder), TypeSafe AI | 2026-09-15 | Company blog [V] | https://typesafe.ai/blog/introducing-system-one-models-and-jev | The launch claims: architecture described only in words, RLCD, parallel sampler, speed, price, "can't hallucinate", workflow evals, FAQ | No paper, no weights |
| J2 | TypeSafe docs: Introduction, System One, Confidence, AI primer, Models, Intent routing, Confidence-gated routing, Jev 1.13 jaggedness, SDE cascade, Choice | TypeSafe AI | fetched 2026-09-23 | Official docs [V] | https://docs.typesafe.ai/ (index: `/llms.txt`) | Interface (state plus Choice/Score/Noul), limits (64k context, ≤255 options), price, vendor-listed failure modes, routing patterns | Proprietary API. MIT SDKs (J4) |
| J3 | Workflow evals site | TypeSafe AI | fetched 2026-09-23 | Vendor eval [V] | https://evals.typesafe.ai/ | 4 in-house workflows. Reference labels are the average of GPT-6 Astra and Claude Fable 5.1 at high thinking | Queries shown on site |
| J4 | GitHub org `typesafe-ai` | TypeSafe AI | queried 2026-09-23 | Code (API clients only) | https://github.com/typesafe-ai | MIT-licensed SDKs (`typesafe-sdk-python`, `typesafe-sdk-js`), `skills`, and `system-one-adapter-python`: "A drop-in replacement for `typesafe_sdk`'s `system_one` evaluation API, backed by LLM APIs instead of TypeSafe" | **No model code, no weights.** The org also holds forks of vLLM (Apache-2.0) and ML-GSAI/LLaDA (MIT) (see §3) |
| J5 | Master Customer Agreement | TypeSafe AI | fetched 2026-09-23 | Legal terms [V] | https://typesafe.ai/legal/mca | §2.3(b) prohibits using the Services or Output "to perform model distillation, train a model to imitate the output of the Services, or develop … a similar or competing product" | — |
| J6 | "Does Jev know when it doesn't know?" (`scienthoon/jev-ood-calibration`) | GitHub user scienthoon | created 2026-09-19, updated 2026-09-22 | Independent eval, not peer-reviewed [I] | https://github.com/scienthoon/jev-ood-calibration | ECE/NLL on 3 public benchmarks plus a 900-item synthetic set that includes a label the text cannot determine. Includes a published self-correction (2026-09-22) | MIT code, CC0 data, raw responses included |
| J7 | "PriorBench — Jev" (`priorbench/jev`) | "1j6c" (PriorBench org) | 2026-09-20 | Independent, pre-registered, not peer-reviewed [I] | https://github.com/priorbench/jev | 5,721 calls through OpenRouter. Latency floor, thresholding behaviour, out-of-scope behaviour | MIT. Raw JSONL and a pre-registration file |
| J8 | Ouyang et al., "Training language models to follow instructions with human feedback" | incl. **Almeida, Diogo** (4th author) | 2022 | NeurIPS 2022 / arXiv 2203.02155 | https://arxiv.org/abs/2203.02155 | Supports only the founder's InstructGPT authorship (checked against export.arxiv.org author metadata) | — |
| J9 | "Jev (AI model)" | Wikipedia | fetched 2026-09-23 | Secondary [S] | https://en.wikipedia.org/wiki/Jev_(AI_model) | Funding ($40M seed, DCVC-led, per Forbes/TechCrunch); "transformer-based, trained exclusively on synthetic data" is attributed to press, **not** found in TypeSafe's own pages | — |

Things we searched for and **did not find**: any arXiv paper, technical report,
model card, parameter count or peer-reviewed evaluation of Jev or of RLCD.
Independent write-ups report that an arXiv search on 2026-09-20 for "reinforcement
learning for calibrated decisions" returned nothing. We did not re-run that
arXiv search.

---

## 2. What Jev is: the interface (this part is verifiable by using the API)

- **Input** [V, J2 Models]: text only (a string, a JSON object or an array of text) as
  the "state", plus one or more typed questions. Context is **64k tokens per request,
  and 32k for the state plus the longest question**. No images, audio or video.
- **Output primitives** [V, J2 Introduction]:
  - **Choice**: one option from a set of **≤255** options. Returns `choice`, a
    `probabilities` map and `confidence`.
  - **Score**: a level on an ordered rubric. Returns `score`, `probabilities` and `confidence`.
  - **Noul**: a yes/no statement. Returns `noul` ∈ [0,1]. It has no confidence field.
- **Parallel questions** [V]: "Every question is evaluated in parallel and in
  isolation against the same state in one go. Adding questions barely changes the
  response time."
  - [I, J7] is broadly consistent with this: 800 typed judgements in one call took
    985 ms, against a ~430 ms per-call floor measured through OpenRouter from Western
    Europe.
- **`confidence` is a deterministic transform of `probabilities`** [V, J2
  Confidence page source]. For K options the docs' widget computes
  `(K·p_max − 1)/(K − 1)`, clipped to [0,1]. That is, it rescales the maximum
  probability. It is **not** a separate uncertainty head.
  - [O] So "confidence" adds no information beyond `probabilities`, which matches
    J6's advice not to threshold on it.
- **Type safety** [V]: the answer space is fixed in advance, so the output is
  always inside the schema.
  - TypeSafe itself says the "0% structured output error rate" is "not empirical.
    Schema matching is guaranteed" (J1).
  - [I, J6]: 0 invalid responses in 4,621 calls.
  - [O] This is a guarantee about output *format*, not *correctness*. "Can't
    hallucinate" means only that Jev cannot emit an out-of-schema token. It can
    still pick the wrong option with high probability (see §4).
- **Customisation** [V, J2 Models]: "Jev is not fine-tuned or LoRA-adapted with
  customer data … the same weights serve every account." Adaptation happens only
  through the state and the question text.
- **Deployment** [V]: hosted API only (`POST /v1/systemone`). Also reachable through
  OpenRouter and the Vercel AI Gateway, per J6 and J7. Service "currently based" on
  the US West Coast (J1). Early access with dynamic rate limits (J2 Models:
  250k tok/s and 1,200 RPM at the time of fetch).
- **Price** [V]: $0.042 per million input tokens. Output tokens are free. TypeSafe:
  "We can't prove it isn't subsidized" (J1).

## 3. Architecture disclosures (almost none)

| Aspect | What is disclosed | Label |
|---|---|---|
| Model class | "a new model architecture, parallel sampler … and training method we call RLCD" | [V] |
| Size | "Jev is neither small nor an LLM" (FAQ). No parameter count | [V] |
| Sampling | "Parallel. Generates all outputs in a single query." Contrasted with autoregressive decoding | [V] |
| Training objective | RLCD: "probabilities are optimized against outcomes to reflect uncertainty". No loss, reward or algorithm is published | [V] |
| Training data | "We make all the data ourselves." No detail ("we'd have to hire you") | [V] |
| Backbone | Undisclosed. Wikipedia attributes "transformer-based" and speculation about an open-weight LLM base to press | [S] |
| Public benchmarks | Deliberately not reported ("put no weight on public benchmarks") | [V] |

[O] Circumstantial only: the `typesafe-ai` GitHub org holds a fork of **LLaDA**
(Large Language Diffusion Models, forked 2025-07-13) and a fork of vLLM. A
diffusion- or mask-based parallel predictor *would* fit the claims of "parallel
sampler" and "all outputs in a single query". Still, a fork is **not evidence**
of Jev's architecture, and we must not state or imply one in the paper.

[O] Relation to Jacobi Forcing (see `research/jacobi-forcing.md`): both claim
"parallel" output, but Jacobi Forcing parallelises *free-form token generation*
while keeping the AR distribution. Jev removes free-form generation altogether and
scores a closed answer set. Our reading of the disclosed interface is that
it behaves like **a classifier over a schema supplied at request time**, not a
parallel decoder. That supports the conclusion of deliverables 6 and 7: a
routing decision needs no decoding at all.

## 4. Vendor claims vs independently shown facts

| Claim | Vendor source | Independent evidence | Status |
|---|---|---|---|
| End-to-end 70–500 ms | J1 | J7: a ~430 ms floor via OpenRouter from Western Europe; gateway and model latency are not separated (J7 says so) | **Partially corroborated** for a cloud call. Depends on network and gateway |
| 40–200× faster, 193.6× (homepage) | J1, J3 | None independent. TypeSafe calls 193.6× "on the higher end of real world gains". The workflows were built by its own team ("some bias could exist"). Baselines are frontier LLMs at default reasoning with a constrained-output wrapper | **Vendor-only.** Baseline choice inflates the ratio [O] |
| 444.6× cheaper | J1 | Price list verifiable. J6 and J7 report very low spend ($0.06 and $0.176 for their studies). Sustainability is unproven, and TypeSafe says so | **List price verified by third parties. Long-run cost unknown** |
| "Can't hallucinate" / 0% type errors | J1 | J6: 0 invalid of 4,621 | **Format guarantee holds. It says nothing about correctness** |
| Calibrated probabilities | J1, J2 | J6: in-domain public benchmarks ECE 0.024–0.032 (possibly contaminated). On an unseen synthetic set ECE 0.107 = 4.4× the noise floor. On a label the text cannot determine, accuracy was 44.7% while the mean probability of the chosen level was 0.74. The sign of miscalibration differs by type (Noul under-confident; Choice/Score over-confident). Probabilities are quantised to 0.01 and are often exactly 0/1. J7: accuracy above the threshold is flat from 0.50 to 0.95, then 100% at 0.99 (60.2% coverage) on its own 400-item benchmark. Without a "none" option, 0/30 out-of-scope inputs were flagged, at 0.99 confidence. J6 cites further repos (jev-phishing-bench: ECE 0.154 vs Claude Haiku 4.5's 0.097) that we **did not open** | **Contested / task-dependent.** Well calibrated on in-distribution semantic judgements. Over-confident when the label is not recoverable from the text or the input is out of scope |
| Accuracy "similar to frontier" on System One tasks | J1, J3 | J7: 95.9% zero-shot on its own 400-item set vs 77.2% keywords and 66.0% TF-IDF+LR. J6: 89–92% on recoverable synthetic labels | **Strong on semantic classification per two independent tests.** No standard benchmark comparison |
| Vendor-listed weaknesses (numbers, dates, negation) | J2 jaggedness | J7: 99.6% across 13 designs on number/date comparison, and 100% on negation, i.e. the docs *understate* the model | Independent evidence is **more favourable** than the vendor on these points |

Caveats on [I]: J6 and J7 were each built in days by single, pseudonymous or
unaffiliated authors. J6 has already corrected itself once. Neither is peer-reviewed.
Both publish raw data, which makes them checkable. That is better than the vendor
evidence, but we have **not** checked it.

## 5. Suitability for routing / classification

TypeSafe markets routing directly. The docs contain an "Intent routing" pattern
("TypeSafe can sit in front of all of these as a fast, cheap classifier that
determines which handler to invoke") and a "Confidence-gated routing" pattern
(action-specific thresholds, "Below 0.6 … route to a human"). The SDE-cascade
cookbook uses Jev as a *verifier* that decides when to escalate from
`gpt-5.4-mini` to `gpt-5.5`. That is structurally a **weak→strong cascade
escalation gate**, the same decision our paper's router makes [V, J2].

[O] So a production decision model that is explicitly positioned as an LLM
router/escalation gate existed as of 2026-09-15. The key question is what kind of
routing decision it is suited to:

1. **Semantic routing** (which intent, domain or handler): the label is recoverable
   from the query text. Independent tests suggest Jev is strong here.
2. **Capability routing** (will the edge SLM answer *this* query correctly?): the
   label depends on the SLM's behaviour, which is **not in the text**. It is
   exactly the "unknowable from the text" regime in which J6 found Jev over-confident
   (0.74 mean probability at 44.7% accuracy). Capability routers in the literature
   (RouteLLM, RouterDC, BEST-Route, etc.; see
   `research/micro-encoder-investigation.md`) are trained on **outcome labels
   collected from the specific model pool**. Jev cannot be trained on those
   (no fine-tuning, per J2 Models), and its terms forbid distilling it (J5).

[O] Our paper's Eq. (3), argmax_k f_θ(q, M_k), is a **capability-routing**
problem (see `research/problem-as-written.md`). A general zero-shot decision model
has no access to how Gemma-4 or Qwen3 perform on a particular query unless that
information is placed in the state. That leaves a real niche for a **trained,
pool-specific, calibrated** router. Jev narrows the space for *semantic* routing
and does not remove the capability-routing problem.

## 6. Structural limitations for our edge–cloud setting

| Limitation | Source | Consequence for our paper [O] |
|---|---|---|
| **API-only, US-hosted, not small** | J1, J2 | Jev cannot run *on the edge device*. Using it as the router means sending every query to the cloud before deciding whether to use the cloud. That defeats the privacy motivation (main-original L40, L76) and adds ≥~430 ms (J7, via gateway) per query before any model runs. The paper's own "Lightweight requirement" (L179) is an on-device requirement Jev cannot meet |
| Terms license inputs to TypeSafe for processing | J5 §4.1 | This adds a third-party data-processing party in a privacy-motivated pipeline. ZDR is offered only to enterprise customers (J2 Legal) |
| **No distillation / imitation / competing product** | J5 §2.3(b) | We **cannot** use Jev outputs as teacher labels to train our router. Using Jev as an evaluation baseline appears allowed by the terms we read, but a university legal check is advisable before publishing Jev comparisons |
| No weights, no version-stable gateway id | J2, J6 | Results against the `jev-latest` alias are not reproducible. Pin `jev-1.13.0` and log the returned `model` field |
| No per-account fine-tuning | J2 | It cannot learn our pool's outcome labels, which matters for §5 point 2 |
| English-first, CJK "not equally well" | J2 Models | Relevant if the thesis evaluates Chinese-language queries (the authors are in Taiwan). Test before use |
| Always answers unless given a "none" option | J7 | A routing schema must include an explicit "uncertain / escalate" option |

## 7. Reproducibility limitations

- No paper, no disclosed architecture, no weights, no training data description.
  RLCD cannot be reimplemented from public information.
- Vendor evals use references produced by other proprietary models (GPT-6 Astra and
  Claude Fable 5.1), so they measure *agreement with frontier LLMs*, not accuracy
  against ground truth (J3).
- The model behind aliases can change silently (J2 Models, J6).
- The only replicable evidence is the independent repos (J6, J7). They are small, fresh and unreviewed.
- **Usable open artefact:** `system-one-adapter-python` (MIT) re-implements the
  System One *interface* (Noul, Score, Choice, with probabilities) over any
  OpenAI-compatible, Anthropic or Gemini endpoint. [P] We could point it at a
  local OpenAI-compatible server hosting the edge SLM. That gives an open,
  reproducible "structured-decision via prompted SLM" baseline with the same
  interface as Jev. It would be implemented in `experiments/`. It is **not yet tested by us**.

## 8. Answer: does Jev weaken, strengthen, or redirect the motivation for our router?

**Short answer [O]: it redirects the motivation. It weakens the draft as written,
and it strengthens a narrower, decision-model-shaped version.**

**Weakens** (claims in `source/main-original.tex` that Jev pressures):
- "unlike existing methods that rely on heavy models" and "fast and efficient"
  (L40, L61). A commercial decision model with 70–500 ms cloud latency, marketed for
  routing and escalation, now exists alongside the encoder routers in deliverable 7.
  A "fast lightweight router" is not new as a product category.
- The **generative "Tiny Language Model"** framing (L40, L56, L61, L129). Jev's whole
  pitch, and its independent evidence, is that decisions do not need string
  generation. This agrees with deliverables 6 and 7: a router that *generates* its
  decision needs a specific justification.

**Strengthens:**
- The premise that **routing is a structured, calibrated decision**, not a
  generation task: "typed decision + probability + threshold → act or escalate"
  is exactly the design pattern TypeSafe documents (confidence-gated routing).
- The case for **calibration as a first-class metric**. The independent results
  (J6, J7) show that even a model trained for calibration can be badly
  mis-calibrated when the label (here, SLM capability) is not visible in the text.
  That is a measurable and publishable gap for a pool-specific router.

**Redirects** — the defensible space Jev does *not* occupy:
1. **On-device** decision-making. The query never leaves the device before the routing decision, and latency does not include a WAN round trip.
2. **Pool-specific capability routing** trained on outcome labels from the actual
   edge/cloud models. Jev is zero-shot, has no fine-tuning and cannot be distilled.
3. **Open, reproducible** weights and training recipe. Jev offers neither.
4. **Coupling with the Split-LLM / edge SLM** (e.g. reusing the SLM's prefill
   state, interpretation P2 in deliverable 7). This cannot be done through a cloud API.

[O] Jev therefore works best in the paper as (a) a **related-work entry and
motivating contrast** (a "System One-type" cloud decision model versus our on-device
calibrated router) and optionally (b) an **evaluation baseline**, subject to its
terms, reported with version pinning and measured latency including the network.
It **cannot** serve as a teacher.

### Proposed design takeaways (labelled [P], for `architecture/options.md`, option D)

- [P] Router output should be a typed decision over {edge SLM, split-LLM, cloud LLM,
  *uncertain*} with a full probability vector, not generated text.
- [P] Report ECE with a noise floor, reliability diagrams, and **selective-prediction
  coverage–risk curves**, following J6's method. Report per decision type.
- [P] Include out-of-scope and "label not recoverable from text" probes, following J6
  and J7, because capability routing is inherently the second kind.
- [P] Multiple independent "questions" in one pass (Jev's parallel primitives) map to
  a **multi-head discriminative encoder**: one head per decision (difficulty,
  domain, privacy sensitivity, expected output length). That is a coherent,
  generation-free reading of "parallel" that needs no Jacobi decoding.

## 9. Open questions / uncertainty

1. Is Jev's ~430 ms floor (J7) caused by the model, OpenRouter or distance? J7 says
   native API access would settle it. We have no key.
2. Would Jev, given the edge SLM's own signals in the state (e.g. its answer
   draft or token log-probs), be a strong capability router? That would be a fair
   baseline experiment, but it still sends data to the cloud.
3. Does the MCA's distillation clause also cover using Jev outputs *only as
   evaluation references*? Our reading is that it does not, but this needs legal review.
4. The independent results (J6, J7) have not been re-audited by us. The J6
   correction shows its magnitudes are fragile. Treat directions, not magnitudes,
   as the robust finding.
5. We did not open the further independent repos that J6 cites (jev-spam-eval,
   jev-phishing-bench, jev-exploration). They should be verified before being cited.
6. Press-sourced facts (funding, "transformer-based", "synthetic data only") were
   not verified against a primary source and must not go into the paper.

## 10. Inputs for other deliverables

- **Claim audit (13):** L40/L61 "unlike existing methods that rely on heavy models":
  add Jev (commercial decision model marketed for routing) to the contrary evidence.
  The privacy motivation (L40, L76) should be framed as "the decision is made
  on-device", which also sets us apart from Jev.
- **Novelty matrix (4):** Jev row = cloud-only, not edge. Lightweight in latency
  but not in size ("neither small"). Structured decision output: yes.
  Calibration: claimed [V], contested [I]. Learned router: zero-shot only.
  Open source: no (SDKs only). Parallel mechanism: undisclosed "parallel sampler",
  not Jacobi.
- **Experiment (10):** a "prompted SLM through `system-one-adapter`" baseline [P];
  an optional pinned `jev-1.13.0` baseline if a key and legal clearance exist; and
  calibration metrics per J6.
- **library.bib (14):** cite J1 as `@misc` (company blog, accessed 2026-09-23) and
  J8 as NeurIPS 2022. Cite J6/J7 only as `@misc` software, clearly marked
  "non-peer-reviewed", if at all.
