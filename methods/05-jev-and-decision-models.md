# methods/05 — Jev / System One as inspiration, and the open academic methods that realise it

*Method-selection sprint, iteration 1. Answers METHOD_BRIEF §7 and §19 file 05.
This is a synthesis of `research/jev-system-one.md` (**[J]**, which read
TypeSafe's blog, docs, GitHub org, legal terms, and two independent
non-peer-reviewed evaluation repos, all saved under `research/raw/jev/` on
2026-09-23) and `research/micro-encoder-investigation.md` / `research/closest-prior-art.md`
for the open academic side. **We hold no TypeSafe API key and made no Jev
calls.** Evidence labels follow [J]: **[V]** vendor claim, **[I]** independent
third-party (non-peer-reviewed) measurement, **[S]** secondary/press, **[O]**
our analysis, **[P]** our proposal.*

The purpose here is **not** to recreate Jev. It is to (a) extract Jev's public
*design philosophy*, (b) state precisely what is unknown/unverifiable, and (c)
map the usable principles onto **open academic methods that can actually be
implemented** for the original paper.

---

## 1. What Jev is (interface — verifiable by using the API)

- **Vendor / launch:** TypeSafe AI, "System One Models & Jev", 2026-09-15 — **8
  days before the source research** [V, J §1]. No paper, no weights, no model
  card, no parameter count [J §1, §3].
- **Input:** text only ("state") + one or more typed questions; 64k context
  (32k for state + longest question) [V, J §2].
- **Output primitives** [V, J §2]:
  - **Choice** — one of ≤255 options; returns `choice`, a `probabilities` map,
    `confidence`.
  - **Score** — a level on an ordered rubric; returns `score`, `probabilities`,
    `confidence`.
  - **Noul** — a yes/no statement; returns a value in [0,1], no confidence.
- **Parallel questions:** every question is evaluated in parallel against the
  same state in one call; adding questions barely changes latency [V]; broadly
  corroborated by an independent repo (800 judgements in 985 ms) [I, J §2].
- **`confidence` is a deterministic transform of `probabilities`** (`(K·p_max −
  1)/(K−1)`), not a separate uncertainty head [V, J §2].
- **Type safety:** the answer space is fixed in advance, so output is always in
  schema. "Can't hallucinate" means only "cannot emit an out-of-schema token" —
  it can still pick the wrong option with high probability [V + O, J §2].
- **No per-account fine-tuning:** the same weights serve every account;
  adaptation is only through the state/question text [V, J §2].
- **Deployment:** hosted API only (US West Coast), also via OpenRouter/Vercel;
  price $0.042 / 1M input tokens, output free [V, J §2].

## 2. Architecture disclosures (almost none) and what is unverifiable

- Disclosed only in words: "a new model architecture, parallel sampler, and a
  training method we call RLCD"; "neither small nor an LLM"; "generates all
  outputs in a single query" [V, J §3].
- **Unverifiable / unknown:** model class, size, backbone, loss, reward, and
  training data. RLCD **cannot be reimplemented** from public information
  [J §7]. The `typesafe-ai` GitHub org holds forks of LLaDA and vLLM, but **a
  fork is not evidence** of Jev's architecture and must not be presented as such
  [O, J §3].
- Press-sourced facts (funding, "transformer-based", "synthetic data only") are
  **secondary [S]** and must not enter the paper [J §9 item 6].

## 3. Vendor claims vs independently shown facts (the honest picture)

From [J §4], directions (not magnitudes) are the robust finding; the two
independent repos [I] are small, days-old, single-author, and one already
self-corrected:

| Claim | Status |
|---|---|
| 70–500 ms end-to-end | Partially corroborated for a *cloud* call; a ~430 ms floor was measured via a gateway from Western Europe [I]. Includes a WAN round trip. |
| 40–200× faster / 444× cheaper | Vendor-only; baseline choice (frontier LLMs with a constrained-output wrapper) inflates the ratio [V, O]. List price is third-party-verifiable; long-run cost unknown. |
| "Can't hallucinate" / 0% type errors | Format guarantee holds (0 invalid in 4,621 calls [I]); says nothing about correctness [O]. |
| Calibrated probabilities | **Contested / task-dependent** [I]. Well calibrated on in-distribution *semantic* judgements (ECE 0.024–0.032, possibly contaminated); **over-confident when the label is not recoverable from the text** (ECE 0.107; 44.7% accuracy at 0.74 mean probability) and on out-of-scope inputs (0/30 flagged, at 0.99) [I, J §4]. |
| Accuracy "similar to frontier" on its tasks | Strong on *semantic* classification per two independent tests (95.9% vs 66–77% for TF-IDF/keywords) [I]. No standard-benchmark comparison [J §4]. |

## 4. Why Jev cannot be the paper's router (structural limits) [J §6]

| Limit | Consequence for the original paper [O] |
|---|---|
| **API-only, US-hosted, "not small"** | Jev cannot run **on the edge**. Using it as the router means sending every query to the cloud *before* deciding whether to use the cloud — this defeats the privacy motivation (L40, L76) and adds a ≥~430 ms WAN round trip before any model runs. It fails the paper's own on-device "lightweight requirement" (L179). |
| Inputs licensed to TypeSafe for processing | Adds a third-party data processor into a privacy-motivated pipeline (ZDR enterprise-only). |
| **Terms forbid distillation / imitation / competing product** (MCA §2.3(b)) | We **cannot** use Jev outputs as teacher labels to train our router. Using Jev only as an *evaluation baseline* appears allowed by the terms read, but needs a university legal check before publishing. |
| No fine-tuning | It cannot learn our pool's per-query capability labels — exactly the label type our router needs (§5). |
| No weights / silent alias changes | Not reproducible unless a specific version is pinned (`jev-1.13.0`) and the returned `model` field is logged. |
| Always answers without a "none" option | A routing schema must include an explicit "uncertain/escalate" option [I]. |

## 5. The design philosophy worth borrowing (generation-free, calibrated, typed)

Jev's **interface** — not its weights — encodes a useful stance that agrees with
this project's other findings [J §8; research/architecture options §4]:

1. **Routing is a structured, calibrated decision, not a generation task.**
   "typed decision + probability + threshold → act or escalate" is exactly the
   pattern TypeSafe documents (intent routing, confidence-gated routing, and an
   SDE-cascade that uses Jev as a weak→strong escalation gate) [V, J §5]. This
   reinforces `methods/04`: the router needs **no decoding** [O].
2. **Calibration is a first-class metric.** Even a model trained for calibration
   is badly miscalibrated when the label is not visible in the text [I] — and
   capability routing ("will *this* SLM answer *this* query?") is exactly that
   regime [J §5]. That makes calibration a **measurable, publishable gap** for a
   pool-specific router.
3. **Parallel typed questions ≈ a multi-head discriminative encoder** — one head
   per decision (difficulty, domain, privacy sensitivity, expected length), all
   in one pass, no Jacobi decoding needed [P, J §8].

## 6. Open academic methods that realise these principles (implementable)

These are the verified, open works that occupy each borrowed principle. Full
records and code/venue in `research/closest-prior-art.md` (**[cpa]**) and
`research/micro-encoder-investigation.md` (**[me]**); consolidated in
`methods/01-method-landscape.md`.

| Borrowed principle | Open academic realisation (verified) | Code |
|---|---|---|
| Structured classification / typed decision | **RouteLLM** BERT/mf variants (ICLR 2025); **BEST-Route** model×samples (ICML 2025); **HyDRA** 4 sigmoid capability heads (ModernBERT, production) | RouteLLM Apache-2.0; BEST-Route MIT [cpa §2.9, §2.16, §2.8] |
| Calibrated decision / selective prediction / deferral | **Pro-Router** coverage-based selective prediction (Geifman & El-Yaniv 2017), Apache-2.0; **AutoMix** POMDP self-verification (NeurIPS 2024) | pro-router Apache-2.0 [cpa §2.3, §2.10] |
| Lightweight query router / capability prediction | **RouterDC** contrastive mDeBERTa (NeurIPS 2024); **CSCR** contrastive + FAISS, "no retraining" (preprint); **IRT-Router** ability/difficulty (ACL 2025) | RouterDC public; IRT-Router repo [me §2; cpa §2.12, §2.14] |
| Semantic query encoder | **vLLM Semantic Router** ModernBERT classifiers (preprint 2026-03) | vLLM project [me §2] |
| Hidden-state probe / capability from representation | **ConsRoute** MLP on device-SLM prefill state (preprint); **RouteLMT** in-model probe (ACL 2026 Industry); **prefill-activation router** (preprint) | none found [cpa §2.1, §2.6, §2.7] |
| Model-selection scoring | **Arch-Router-1.5B** generative (preprint); **LLMRouterBench** unified eval (Findings ACL 2026) | Arch-Router HF; LLMRouterBench repo [cpa §2.15, §2.17] |
| Open re-implementation of the Jev *interface* | **`system-one-adapter-python`** (MIT): a drop-in re-impl of the System One Noul/Score/Choice interface backed by ordinary LLM APIs | typesafe-ai org, MIT [J §4, §7] |

**[P] Usable open artefact for our baselines:** `system-one-adapter-python` can
be pointed at a local OpenAI-compatible server hosting the edge SLM, giving an
open, reproducible "structured-decision via prompted SLM" baseline with the same
typed interface as Jev — without any Jev call [J §7]. This is a baseline, not
the method, and it is **not yet tested by us**.

## 7. How Jev is used in the paper (its only legitimate roles)

- **Related-work entry / motivating contrast** [O, J §8]: a cloud, API-only,
  calibrated *System-One-type* decision model marketed for routing — contrasted
  with our **on-device, pool-specific, calibrated, open** router. Jev *redirects*
  the motivation: it weakens the generic "fast lightweight router" novelty and
  the generative-TLM framing, and it *strengthens* the "routing = typed
  calibrated decision" and "calibration as a metric" framing.
- **Optional evaluation baseline** [O]: only with a pinned version, measured
  latency including the network, per-decision-type calibration metrics (ECE with
  a noise floor, reliability diagrams, coverage–risk curves following the
  independent repos), and a university legal check on the MCA. Report as
  non-primary evidence.
- **It cannot serve as a teacher** (MCA §2.3(b)) and **cannot run on the edge**.

## 8. Citation / honesty notes (feed the claim audit and library.bib)

- Cite the launch blog as `@misc` (company blog, accessed 2026-09-23) and the
  InstructGPT paper (Ouyang et al., NeurIPS 2022) only for the founder's
  authorship [J §10]. Cite the independent repos only as `@misc` software,
  clearly marked "non-peer-reviewed", if at all.
- Do **not** state or imply Jev's architecture from the GitHub forks [J §3].
- Do **not** carry press-sourced facts into the paper [J §9 item 6].

## 9. Open questions (feed `methods/11`)

1. Is Jev's ~430 ms floor the model, the gateway, or distance? Unresolved (no
   key) [J §9].
2. Would Jev be a strong capability router if given the edge SLM's own signals
   (draft, token log-probs) in the state? A fair but cloud-bound baseline
   experiment [J §9].
3. Does the MCA distillation clause cover *evaluation-only* reference use? Our
   reading: no — but needs legal review [J §9].
4. The independent repos have not been re-audited by us; treat directions, not
   magnitudes, as robust [J §9].
