# methods-v2 / 05 — Student micro-encoder architecture

*Deliverable for `MICROENCODER_KD_BRIEF.md` §8 (student backbone) and §9 (exact
f_θ, prepared here only to the extent the backbone constrains it; the full f_θ
definition is `06-proposed-method.md`). Prepared 2026-10-02 (gnhf
microencoder-kd sprint, iteration 6).*

## 0. Purpose, grounding, and sourcing

The advisor approved a **micro-encoder** router (`00-meeting-decisions-lock.md`,
CONFIRMED #1). This deliverable fixes *what encoder* the deployed student is, so
that:

1. the student is genuinely **lightweight at inference** (the non-negotiable
   constraint from `00` and brief §8/§26);
2. there is a real **teacher↔student size gap** for the KD-3 utility-regression
   distillation recommended in `03-kd-formulations.md` and the T1 larger-encoder
   teacher recommended in `04-teacher-options.md` (hand-off `04` §5 → `05`:
   *"fix the T1 teacher↔student size gap so the distillation is non-trivial;
   confirm open licences"*);
3. the backbone cleanly supports **multi-head per-action utility outputs**
   `Û(a|q)` (the KD-3 target), not just a single class label.

**Brief §8 discipline.** Do *not* auto-select a backbone because it is popular.
Compare the named classes — MiniLM-scale, DeBERTa-v3-small class, ModernBERT
class, and other current lightweight encoders — on parameter count, hidden
dimension, sequence length, licensing, released checkpoints, CPU/GPU latency
evidence, ONNX/quantization suitability, training-resource needs, and whether the
architecture supports multi-head utility outputs cleanly. Propose a **size
range** and a **primary candidate**, and mark everything that still needs
empirical ablation as `[OPEN]`.

**Reuse, not re-research.** The encoder-router prior art (who uses which backbone
at what measured latency) is primary-checked in v1
`research/micro-encoder-investigation.md` §2 and `research/closest-prior-art.md`
(HyDRA = ModernBERT-base 149M, ONNX INT8, 55 ms P50 / 120 ms P99 CPU [body];
ComplianceGate 7 ms overhead [abs]; RouterDC = mDeBERTa-v3-base; BEST-Route =
DeBERTa-v3-small [snippet]), and the size-target band (20–150 M, encoder choice
is an ablation) is in v1 `methods/02-candidate-methods.md` §B. **No new web
search was required.** The one load-bearing empirical finding carried forward is
LLMRouterBench's result that **backbone embedding choice has limited impact on
routing quality** (iter-2 learning) — which is *why* this file recommends a
primary candidate but treats the exact backbone as an ablation rather than a
contribution.

**Honesty on parameter counts.** The param/hidden/context/license numbers below
are the canonical model-card / paper values named in the v1 research and in the
original model releases, but they were **not re-opened at their primary source
this iteration**. Every number is therefore tagged `[RELATED]` (adjacent prior
fact) and routed to `17-verified-references.md` for primary re-verification
before any becomes load-bearing in the manuscript. Latency numbers measured by
other groups on other hardware are tagged `[E]` (estimate for *our* hardware) per
`00`.

**Evidence tags** (from `00`): `[VERIFIED]` primary source supports; `[RELATED]`
adjacent prior work / canonical release value not re-opened this iteration;
`[PROPOSED]` our design idea; `[OPEN]` requires experiment/advisor/licence
confirmation; `[E]` estimate, not measured on our hardware.

---

## 1. What the backbone must deliver (requirements derived from 03/04)

| # | Requirement | Source | Why |
|---|---|---|---|
| R1 | **Encoder (non-generative), one forward pass** per query | `00` CONFIRMED #1; brief §9 | Eq. (3) is `argmax_k f_θ(q,M_k)`, a scoring problem; no sequential decode. |
| R2 | **Lightweight at inference** — CPU/NPU-feasible, ≤~150 M params | brief §8/§26; `02` §B | Edge deployment (fixed requirement #5). |
| R3 | **Multi-head utility output** `Û(a|q)` — one scalar head per action | `03` KD-3; brief §8 last bullet | Student must emit per-action calibrated utility, not a single label. |
| R4 | **A strictly larger same-family teacher exists** (for T1 KD) | `04` §5 → `05` | KD is non-trivial only if teacher ≫ student; same tokenizer/family also enables optional KD-4 representation distillation. |
| R5 | **Permissive open licence** (training *and* redistribution of a fine-tuned checkpoint) | brief §8; `04` O-T1 | The deployed router is ours to release; teacher licence must permit distillation. |
| R6 | **ONNX / INT8 export path** with existing evidence | brief §8; `closest-prior-art` §HyDRA | Edge latency target; avoid backbones with known export friction. |
| R7 | **Context length sufficient for query + optional system/context prompt** | brief §11 (`s` is separate, but q may be long) | A system-prompt- or context-aware query can exceed 512 tokens. |

R3 is satisfied by *every* candidate below (a pooled representation → N parallel
heads; HyDRA does exactly this with 4 sigmoid heads on ModernBERT [body]), so R3
is **not** a discriminator. R4–R6 are the real discriminators.

---

## 2. Candidate backbones (brief §8 field template)

### 2.1 MiniLM class — `microsoft/MiniLM-L12-H384` / `all-MiniLM-L6-v2`

- **Param count:** L6-H384 ≈ 22.7 M; L12-H384 ≈ 33 M. [RELATED → 17]
- **Hidden dim:** 384. **Seq length:** 512 (backbone); the popular
  `all-MiniLM-L6-v2` sentence checkpoint truncates at 256. [RELATED → 17]
- **Licensing:** MIT (microsoft MiniLM) / Apache-2.0 (sentence-transformers
  `all-MiniLM-L6-v2`). [RELATED → 17] — satisfies R5.
- **Released checkpoints:** yes, widely mirrored on HF. [RELATED]
- **CPU latency evidence:** sub-10 ms single-query encode is routinely reported
  for L6-H384 on CPU, but not by us → [E]. [OPEN]
- **GPU latency:** negligible (single forward of a 22–33 M encoder) → [E].
- **ONNX / quant suitability:** excellent; standard BERT ops, well-trodden ONNX +
  dynamic INT8 path. Satisfies R6. [RELATED]
- **Training resources:** fine-tunes on a single small GPU or even CPU. [RELATED]
- **Multi-head utility (R3):** clean — mean/[CLS] pool → N sigmoid/linear heads.
- **Teacher gap (R4):** a MiniLM student pairs with a ModernBERT-large /
  DeBERTa-v3-large teacher (cross-family) — gap is real but tokenizer differs, so
  KD-4 representation distillation is **not** clean; KD-3 output-space regression
  still works. [PROPOSED]
- **Role:** aggressive lower-bound **student** / compression-ablation anchor.

### 2.2 DeBERTa-v3-small class — `microsoft/deberta-v3-xsmall` / `-small`

- **Param count:** xsmall ≈ 22 M backbone (~70 M incl. the 128 K-vocab
  embedding); small ≈ 44 M backbone (~142 M incl. embedding). The large embedding
  dominates the on-disk size. [RELATED → 17]
- **Hidden dim:** xsmall 384, small 768. **Seq length:** 512. [RELATED → 17]
- **Licensing:** MIT. [RELATED → 17] — satisfies R5.
- **Released checkpoints:** yes (HF `microsoft/deberta-v3-*`). Used as a router
  backbone by BEST-Route (DeBERTa-v3-small) and RouterDC (mDeBERTa-v3-base).
  [RELATED, snippet for BEST-Route]
- **CPU latency:** no primary figure for us → [E]/[OPEN].
- **ONNX / quant suitability:** **known friction.** DeBERTa's *disentangled
  attention* uses custom ops (relative-position gather) that historically require
  special handling for ONNX export and complicate INT8 quantization vs plain
  BERT/ModernBERT. This is a genuine edge-deployment con against R6. [RELATED →
  17 to confirm current tooling state] [OPEN]
- **Training resources:** single GPU. [RELATED]
- **Multi-head utility (R3):** clean.
- **Teacher gap (R4):** DeBERTa-v3-large (~304 M backbone / ~434 M total) is the
  same-family teacher → clean tokenizer match, enables optional KD-4. [PROPOSED]
- **Role:** strong-accuracy student option; flagged for ONNX risk.

### 2.3 ModernBERT class — `answerdotai/ModernBERT-base` / `-large`

- **Param count:** base ≈ 149 M; large ≈ 395 M. [RELATED → 17]
- **Hidden dim:** base 768, large 1024. **Seq length:** **8192** (native long
  context) — satisfies R7 with large margin. [RELATED → 17]
- **Licensing:** Apache-2.0. [RELATED → 17] — satisfies R5 for **both** student
  and teacher (critical: the T1 teacher licence must permit distillation; Apache
  does).
- **Released checkpoints:** yes (Answer.AI / LightOn, late 2024). [RELATED]
- **CPU latency evidence:** HyDRA runs ModernBERT-base with 4 heads at **86 ms
  median on CPU**; ONNX dynamic-INT8 architecture figure gives **55 ms P50 / 120
  ms P99 on CPU** [body, `closest-prior-art` §HyDRA]. This is the **strongest
  primary-ish CPU evidence for any candidate** — but it is HyDRA's hardware, not
  ours → still [E] for our edge box. [RELATED/[E]]
- **GPU latency:** negligible; also benefits from Flash-Attention-style kernels.
- **ONNX / quant suitability:** demonstrated by HyDRA (ONNX dynamic INT8). R6
  satisfied with direct precedent. [RELATED]
- **Training resources:** single GPU for base; large fine-tunes on one larger GPU
  — within lab GPU availability (`00` CONFIRMED #4), no large-scale training. [RELATED]
- **Multi-head utility (R3):** clean — this is exactly HyDRA's 4-sigmoid-head
  design. [VERIFIED for the pattern, via `closest-prior-art`]
- **Teacher gap (R4):** **base (149 M) student ↔ large (395 M) teacher is the
  cleanest T1 pairing** — same tokenizer, same family, same ONNX path; enables
  KD-3 (output utility regression) *and* optional KD-4 (representation
  distillation) without tokenizer mismatch. [PROPOSED]
- **Role:** **recommended primary student**; `-large` = recommended T1 teacher.

### 2.4 Other current lightweight encoders (surveyed, not selected)

| Model | ~Params | Licence | Why not primary |
|---|---|---|---|
| DistilBERT | 66 M | Apache-2.0 | Fine, but older; no long context; ModernBERT dominates it on the same budget. [RELATED] |
| BERT-base / RoBERTa-base | 110–125 M | Apache-2.0 | Legacy baseline; superseded by ModernBERT at similar size. [RELATED] |
| GTE-small / BGE-small (embedding encoders) | ~33 M | MIT/Apache | Tuned for retrieval embeddings; usable as a frozen-embedding + small-head variant (tinyrouter pattern), kept as an ablation. [RELATED] |
| NeoBERT / EuroBERT (2025 ModernBERT-likes) | ~150–210 M | varies [OPEN] | Newer long-context encoders; licences/checkpoints not re-verified → [OPEN], not load-bearing. |
| μLM-scale (8–30 M, decoder) | 8–30 M | varies | Decoder-only generators, *not* encoders (`micro-encoder-investigation` §3.1); out of scope for R1. |

The **frozen-encoder + tiny-head** pattern (tinyrouter: frozen 0.6 B encoder +
~10 K-param head) is worth noting as an extreme-compression ablation, but its own
README reports it **tied random routing when oracle headroom was small**
(`micro-encoder-investigation` §2) — a warning that student *size* is not the
binding constraint when the pool leaves little headroom (see `10`). [RELATED]

---

## 3. Comparison matrix

| Criterion | MiniLM (22–33 M) | DeBERTa-v3-small (44 M bb) | **ModernBERT-base (149 M)** | DistilBERT (66 M) |
|---|---|---|---|---|
| Inference lightness (R2) | ★★★ | ★★ | ★★ (CPU-proven by HyDRA) | ★★ |
| Context length (R7) | 512/256 | 512 | **8192** | 512 |
| ONNX/INT8 (R6) | ★★★ | ★ (disentangled-attn friction) | ★★★ (HyDRA precedent) | ★★★ |
| Same-family teacher (R4) | cross-family only | DeBERTa-v3-large ✓ | **-large ✓ (cleanest)** | none clean |
| Licence (R5) | MIT/Apache ✓ | MIT ✓ | **Apache ✓ (teacher too)** | Apache ✓ |
| Multi-head utility (R3) | clean | clean | clean (HyDRA pattern) | clean |
| Primary CPU-latency evidence | none (ours) | none | **86 ms / 55 ms P50 (HyDRA)** | none |
| Role | compression ablation | accuracy option (ONNX risk) | **PRIMARY STUDENT** | legacy baseline |

Reading: no candidate is dominated on *routing quality* grounds (LLMRouterBench:
backbone choice has limited impact), so the matrix is decided by the
*engineering* rows — teacher-gap cleanliness (R4), ONNX path (R6), and
same-family-Apache licensing (R5). ModernBERT wins all three.

---

## 4. Recommendation [PROPOSED]

**Student SIZE RANGE:** **22 M – 150 M parameters.** Below ~22 M (μLM/tiny-head
regime) risks the tinyrouter "ties random" failure when headroom is small; above
~150 M stops being a "micro"-encoder and erodes the edge-latency story.

**Primary student candidate:** **`ModernBERT-base` (≈149 M)** with **N parallel
scalar utility heads** (one per action `a ∈ {EDGE, SPLIT(d), STRONG}`), pooled
representation → per-head `Û_θ(a|q)`, trained by KD-3 (utility regression) in the
KD-5 hybrid of `03`. Rationale: only candidate that simultaneously gives (a) a
clean same-family **Apache-2.0** teacher (`ModernBERT-large`, R4+R5), (b) a
**demonstrated ONNX-INT8 CPU path** (HyDRA, R6), and (c) long context (R7).

**T1 teacher:** **`ModernBERT-large` (≈395 M)** — same tokenizer/family enables
both KD-3 output distillation and the optional KD-4 representation-distillation
ablation; Apache licence permits distillation (resolves part of `04` O-T1 for the
*teacher model*, though the judge/label *source* licence stays `[OPEN]`).

**Required ablations (not contributions) `[OPEN]`:**
- **A-size:** ModernBERT-base vs a 22–44 M student (MiniLM / DeBERTa-v3-xsmall) —
  does the smaller student hold routing quality? (feeds E4 param/latency axis).
- **A-backbone:** swap ModernBERT-base → DeBERTa-v3-small to test the
  LLMRouterBench "backbone doesn't matter" claim *on our task*; also quantifies
  the DeBERTa ONNX-friction cost.
- **A-repr:** KD-3 only vs KD-3 + KD-4 (representation distillation) — only
  feasible on the same-family ModernBERT pair.
- **A-frozen:** frozen-encoder + tiny-head (tinyrouter pattern) as the
  extreme-compression lower bound.

**Explicitly deferred to other deliverables (not guessed here):** the exact edge
GPU/NPU model and our measured CPU/NPU latency (`[OPEN]` → `16`); whether the
pool regime shrinks the student's useful capacity (`04` O-T3 → `10`); the full
f_θ definition and training/inference algorithms (→ `06`).

---

## 5. Open questions and hand-off

Carried as `[OPEN]`:

- **O-S1.** Our *measured* CPU/NPU single-query encode latency for ModernBERT-base
  INT8 on the (unknown) edge device — HyDRA's 55–86 ms is **not** our hardware. →
  `12` (E7 latency), `16` (edge-device unknown).
- **O-S2.** Does the 22–44 M student match ModernBERT-base routing quality, or is
  149 M needed? Decides where in the 22–150 M band the primary sits. → E4, `12`.
- **O-S3.** Current ONNX-export/INT8 tooling state for DeBERTa-v3 disentangled
  attention (is the friction still real in 2026?). → `17`.
- **O-S4.** NeoBERT/EuroBERT licence + checkpoint status, if a newer long-context
  student is wanted. → `17`.

**Hand-off:**
- **→ `06-proposed-method`:** instantiate f_θ as ModernBERT-base + N utility heads;
  teacher = ModernBERT-large; write train/inference algorithms with the α hybrid
  (KD-5), α=1 ≡ no-teacher control.
- **→ `07-training-labels`:** heads regress to `y(a,q)` (hard) + teacher
  `Û_teacher(a|q)` (soft); N = |action set| fixed by the pool (`10`).
- **→ `10-model-pool-and-baselines`:** confirm the action set size N and the
  "non-distilled ModernBERT-base" baseline (brief §14) = our primary student with
  α=1.
- **→ `11-novelty-stress-test`:** backbone choice is **not** novelty
  (LLMRouterBench; HyDRA already runs ModernBERT multi-head on CPU) — residual
  novelty stays on target+deployment (N3/N4/N6).
- **→ `12-conference-experiment-plan`:** E4 teacher(large) vs student(base) on
  quality/calibration/params/latency; A-size and A-backbone as the ablation rows;
  E7 to measure *our* edge latency (resolves O-S1).
- **→ `17` / `method-references.bib`:** primary-verify every param/hidden/
  context/licence number tagged `[RELATED]` above (ModernBERT base/large,
  DeBERTa-v3 xsmall/small/large, MiniLM, DistilBERT) and the HyDRA CPU-latency
  figures before any is load-bearing.
