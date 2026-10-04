# 07 — Backbone verification: is ModernBERT the right *first* implementation candidate?

**Sprint:** methods-v3 hardening (brief §13; findings RF-H2, RF-K2 in `00`).
**Date of checks:** 2026-10-04.
**Inputs:** `05-full-routing-prior-art.md` (LLMRouterBench §1.4/§4, HyDRA §1.3),
`methods-v2/05-student-architecture.md` (v2 comparison matrix, audited below).

> **BACKBONE CHOICE IS AN ENGINEERING DECISION, NOT A NOVELTY CLAIM.**
> Nothing in this file may be cited in the manuscript as a contribution. The
> encoder is a replaceable component of f_θ. The method is defined independently
> of it, and the backbone is chosen by a pre-registered rule (§6) and tested
> by ablation (§7).

---

## 0. Evidence conventions used here

| Tag | Meaning in this file |
|---|---|
| `[VERIFIED-BODY]` | Paper body (arXiv HTML full text) inspected; section/table cited. |
| `[VERIFIED-META]` | Bibliographic identity confirmed (ACL Anthology / ICLR / arXiv abs page). |
| `[ARTIFACT]` | Read directly from the official checkpoint: `config.json`, HF model API (`/api/models/<id>?blobs=true`), or the official model card, fetched 2026-10-04. These are primary facts about the released artifact, not paper claims. |
| `[AUTHOR-CLAIM]` | Number reported by the authors, not reproduced by us. |
| `[DERIVED]` | Our arithmetic from `[ARTIFACT]` values (shown inline). |
| `[PROPOSED]` / `[OPEN]` / `[REJECT]` | As in the brief §29. |

---

## 1. ModernBERT — verified facts

**Identity** `[VERIFIED-META]`: Warner, Chaffin, Clavié, Weller, Hallström,
Taghadouini, Gallagher, Biswas, Ladhak, Aarsen, Adams, Howard, Poli. *"Smarter,
Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient,
and Long Context Finetuning and Inference."* Proc. ACL 2025 (Vol. 1: Long Papers),
pp. 2526–2547, DOI `10.18653/v1/2025.acl-long.127`; arXiv `2412.13663`.
*Author-list note:* the arXiv version also lists **Nathan Cooper**, but the ACL
Anthology record does not. The BibTeX in `method-references-v3.bib` must
copy the **ACL Anthology** list.

| Fact | ModernBERT-base | ModernBERT-large | Source / tag |
|---|---|---|---|
| Total parameters | **149,655,232** (paper: "149M") | **395,881,664** (paper: "395M") | HF safetensors total `[ARTIFACT]`; paper §2.1.3 / Table 4 `[VERIFIED-BODY]` |
| Layers | 22 | 28 | `config.json` `[ARTIFACT]`; Table 4 |
| Hidden size | **768** | **1024** | `config.json` `[ARTIFACT]` |
| Attention heads | 12 | 16 | `config.json` `[ARTIFACT]` |
| GLU expansion | 2,304 (config `intermediate_size` 1152 per GLU half) | 5,248 (config 2624) | Table 4 `[VERIFIED-BODY]`; config `[ARTIFACT]` |
| Vocabulary | 50,368 | 50,368 | config `[ARTIFACT]` |
| Max context | 8,192 | 8,192 | config `max_position_embeddings` `[ARTIFACT]` |
| Attention pattern | local window **128** tokens; a global layer every **3** layers | same | config `local_attention`, `global_attn_every_n_layers` `[ARTIFACT]` |
| Non-embedding parameters | ≈ **111.0 M** (149.66 M − 50,368×768) | ≈ **344.3 M** | `[DERIVED]` |
| Pre-training data | 2T tokens, mainly English (web, code, scientific text) | same | Abstract, §2.2.1 `[VERIFIED-BODY]` |
| Licence (weights) | **Apache-2.0** | **Apache-2.0** | HF `cardData.license` `[ARTIFACT]` (the arXiv *paper* is CC BY 4.0; this is not the weights licence) |
| Checkpoint | `answerdotai/ModernBERT-base`, rev `8949b909…` | `answerdotai/ModernBERT-large`, rev `45bb4654…` | HF API `[ARTIFACT]` |
| Transformers support | native from `transformers` **v4.48.0** | same | release notes `[ARTIFACT]` |
| ONNX artifacts in official repo | `onnx/model.onnx` (599 MB), `model_fp16` (300 MB), **`model_int8` / `model_quantized` / `model_uint8` (151 MB)**, `model_q4`, `model_q4f16`, `model_bnb4` | same set (int8 398 MB) | HF file listing `[ARTIFACT]` |
| ONNX export tooling | `ModernBert` is on Optimum's supported-architecture list | same | optimum-onnx docs `[ARTIFACT]` |
| GLUE avg. | 88.4 (vs DeBERTa-v3-base 88.1) | 90.4 (vs DeBERTa-v3-large 91.4) | §3.2, Table 1 `[AUTHOR-CLAIM]` |
| Throughput claims | GPU only: single **RTX 4090**, designed against a basket of inference GPUs (T4, A10, L4, **RTX 3090**, RTX 4090, A100, H100) | same | §2.1.3, §4.2, Table 2 `[AUTHOR-CLAIM]` |

### 1.1 What the ModernBERT paper does *not* establish

1. **No CPU, mobile or edge-accelerator latency.** All efficiency results are on
   GPU (§4.2) `[VERIFIED-BODY]`.
2. **No quantization or ONNX results.** The paper says nothing about INT8 or ONNX
   `[VERIFIED-BODY]`. The INT8 ONNX files in the repo are released artifacts, but
   no one in the paper measured their accuracy.
3. **The headline speed gains are long-context, variable-length effects**
   (unpadding, alternating 128-token local attention, FlashAttention) measured at
   up to 8,192 tokens. For router queries that are mostly **shorter than 128
   tokens**, every layer's attention covers the whole input in practice, so
   most of the long-context advantage does not apply. Per-token compute is then
   dominated by the ≈111 M non-embedding parameters `[DERIVED]`. This is our
   reasoning from the config, not a measured result `[OPEN]` until E7-router
   latency is measured.
4. **"The first encoder designed in a hardware-aware way"** (Conclusion) is an
   author priority claim `[AUTHOR-CLAIM]`. Do not repeat it in our manuscript.

### 1.2 ONNX / INT8 fidelity is a real risk, not a formality

A public report on the official model discussion (HF `answerdotai/ModernBERT-base`
discussion #77, 25–27 Mar 2025) `[ARTIFACT]` shows that:
* the Python API export of a *fine-tuned* ModernBERT failed (FX trace of a
  dynamo-compiled function), while the `optimum-cli export onnx --task
  text-classification --opset 14` path succeeded;
* the exported graph differed from PyTorch by **max abs diff 0.0047**, above the
  default 1e-4 tolerance.

That is a single user report, not a systematic study. But for a router whose
decision is `argmax_a [Û(M(a)|q) − λC(a|s)]`, small shifts in logits can flip
decisions near the margin, and they move calibration. **Requirement
`[PROPOSED]`:** every deployed router format (PyTorch FP32 → ONNX FP32 → ONNX
INT8) must report, on the same test split, (i) the decision-agreement rate with the
FP32 router, (ii) ΔECE, and (iii) Δ routing utility at the chosen operating point.
This goes into `13` as a sub-check of E3/E7, and it is the same "is the
transformation lossless?" question that E0 asks of Split execution.

---

## 2. Comparison candidates — verified facts

All rows are `[ARTIFACT]` (config + HF API + official card) unless tagged otherwise.
"Non-emb." is `[DERIVED]` = total − vocab×hidden, or taken from the card where
the card states backbone parameters separately.

| Model (HF ID) | Total params | Non-emb. (≈ per-token compute driver) | L × H | Vocab | Max ctx | Licence | Official ONNX/INT8 files | Paper / tag |
|---|---|---|---|---|---|---|---|---|
| `answerdotai/ModernBERT-base` | 149.7 M | ≈111 M | 22 × 768 | 50,368 | 8,192 | Apache-2.0 | yes (int8 151 MB) | ACL 2025 `[VERIFIED-BODY]` |
| `answerdotai/ModernBERT-large` | 395.9 M | ≈344 M | 28 × 1024 | 50,368 | 8,192 | Apache-2.0 | yes (int8 398 MB) | same |
| `microsoft/deberta-v3-xsmall` | ≈70 M (card: 22 M backbone + 48 M emb.) | **22 M** | 12 × 384 | 128,100 | 512 | MIT | no (PyTorch `.bin` only) | ICLR 2023 `[VERIFIED-META]`; Table 9 `[VERIFIED-BODY]` |
| `microsoft/deberta-v3-small` | ≈142 M (card: **44 M backbone + 98 M emb.**) | **44 M** | 6 × 768 | 128,100 | 512 | MIT | no | same |
| `microsoft/deberta-v3-base` | ≈184 M (card: 86 M + 98 M) | 86 M | 12 × 768 | 128,100 | 512 | MIT | no | same |
| `microsoft/MiniLM-L12-H384-uncased` | 33 M (card) | ≈21 M | 12 × 384 | 30,522 | 512 | MIT | no | NeurIPS 2020 `[VERIFIED-META]` (abstract + official card only) |
| `sentence-transformers/all-MiniLM-L6-v2` | 22.7 M | ≈11 M | 6 × 384 | 30,522 | 512 (card: inputs truncated at 256 word pieces) | Apache-2.0 | yes (incl. qint8 arm64/avx512/avx2, 23 MB) | contrastive sentence-embedding fine-tune of `nreimers/MiniLM-L6-H384-uncased` (card) |
| `jhu-clsp/ettin-encoder-17m` | 17 M | ≈4 M | 7 × 256 | 50,368 | 7,999 | MIT | no | ICLR 2026 `[VERIFIED-META]`; §/Table sizes `[VERIFIED-BODY]` |
| `jhu-clsp/ettin-encoder-32m` | 32 M | ≈13 M | 10 × 384 | 50,368 | 7,999 | MIT | no | same |
| `jhu-clsp/ettin-encoder-68m` | 68 M | ≈42 M | 19 × 512 | 50,368 | 7,999 | MIT | no | same |
| `jhu-clsp/ettin-encoder-150m` | 150 M | ≈111 M | 22 × 768 | 50,368 | 7,999 | MIT | no | same |
| `jhu-clsp/ettin-encoder-400m` | 400 M | ≈349 M | 28 × 1024 | 50,368 | 7,999 | MIT | no | same |

**Ettin identity** `[VERIFIED-META]`: Weller, Ricci, Marone, Chaffin, Lawrie, Van
Durme. *"Seq vs Seq: An Open Suite of Paired Encoders and Decoders."* ICLR 2026
(poster; OpenReview `z5Mn8Rxi3l`); arXiv `2507.11412`. From the body
`[VERIFIED-BODY]`, Ettin encoders are an **open-data replication of the ModernBERT
recipe** with five listed differences (open data, decay during context extension,
no model merging, 15% masking in decay, equal local/global RoPE). They are trained
on up to 2T tokens and reported at **GLUE 88.9 (150 M) vs ModernBERT-base 88.4**,
83.5 (32 M), 87.2 (68 M) `[AUTHOR-CLAIM]`. The paper reports no latency figures.

**Shared tokenizer** `[ARTIFACT]`: `tokenizer.json` SHA-256 `9fd55248…74b7b1` is
**byte-identical** for ModernBERT-base, Ettin-17m, Ettin-32m and Ettin-400m.
ModernBERT and the whole Ettin ladder therefore tokenize every query identically.

**DeBERTa-v3 body numbers** (Table 9, `[AUTHOR-CLAIM]`; card agrees): MNLI-m/mm
base 90.6/90.7, small 88.3/87.7, xsmall 88.1/88.3; SQuAD 2.0 F1 base 88.4, small
82.8, xsmall 84.8. The paper makes no inference-speed claims `[VERIFIED-BODY]`.

**MiniLM** `[VERIFIED-META]`: Wang, Wei, Dong, Bao, Yang, Zhou, *"MiniLM: Deep
Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained
Transformers"*, NeurIPS 2020 (Advances in NeurIPS 33). The official card states
"12-layer, 384-hidden, 12-heads, 33M parameters, 2.7x faster than BERT-Base"
`[AUTHOR-CLAIM]`. Body not re-read in v3 → MiniLM must not support any load-bearing
manuscript sentence beyond its existence.

---

## 3. Corrections to the v2 comparison (`methods-v2/05-student-architecture.md` §3–4)

| v2 statement | Problem | v3 status |
|---|---|---|
| "DeBERTa-v3-small (44 M bb)" placed as lighter than ModernBERT-base (149 M) | It compares **backbone-only** with **total** parameters. DeBERTa-v3-small totals ≈142 M, so its on-disk/RAM size is about the same as ModernBERT-base. Per-token compute (6 layers × 768, 44 M non-emb.) is ≈2.5× *lower* than ModernBERT-base (≈111 M non-emb.), *before* DeBERTa's disentangled-attention overhead, which this arithmetic does not capture. | **Corrected.** Compare memory by total params and compute by non-emb. params, and measure latency. |
| "ModernBERT-base … micro-encoder" | 149 M total / 111 M non-emb. is a *base*-size encoder. "Micro" is only defensible relative to the LLMs being routed. | **Reword:** "compact encoder" in the manuscript. Reserve "micro" for ≤ ~70 M, or drop the word. `[PROPOSED]` |
| "ONNX/INT8: DeBERTa ★ (disentangled-attn friction)" | No evidence was given. `Deberta-v2` (the v3 model type) is on Optimum's supported-architecture list `[ARTIFACT]`. Unlike ModernBERT, Microsoft ships no official ONNX files. | **Downgrade to `[OPEN]`.** Friction is unproven, and ModernBERT has export issues of its own (§1.2). |
| "ModernBERT ★★★ ONNX (HyDRA precedent)" | Official ONNX/INT8 files do exist `[ARTIFACT]`, but they are the *pre-trained MLM* graph. Our fine-tuned router must be re-exported, which has one reported fidelity issue (§1.2). | **Partially upheld**, gated on the fidelity check. |
| "Primary CPU-latency evidence: 86 ms / 55 ms P50 (HyDRA)" | Both numbers are HyDRA author claims on HyDRA's hardware, from two different arXiv versions (`05` §1.3). HyDRA App. F also reports ModernBERT-large at ≈3× base latency (77.3 vs 26.6 ms) `[AUTHOR-CLAIM]`. | **Kept as `[AUTHOR-CLAIM]` analogy only.** It is not evidence for our edge node. |
| "no candidate is dominated on routing quality (LLMRouterBench: backbone choice has limited impact)" | Over-extended. LLMRouterBench covers 3 *frozen* embedding models × 3 embedding routers, with a ≤2.2-point spread and no significance test (`05` §4). It says nothing about **fine-tuned** encoders, calibration, or latency. | **Bounded.** Allowed sentence: `05` §4. The routing-quality comparison between backbones is an *experiment* (§7), not a citation. |
| "Student size range 22–150 M; below ~22 M risks tinyrouter 'ties random'" | The tinyrouter evidence is a README observation about *low-headroom pools*, i.e. a property of the pool, not of the size. | **Reword:** headroom is a model-pool question (`10`). Size floor is an ablation result `[OPEN]`. |
| Teacher = ModernBERT-large "cleanest same-family" | Still true. Ettin-400m is now an equally same-tokenizer alternative, so the same-family argument no longer favors ModernBERT alone. | **Upheld with alternative.** |

**RF-K2 (edge node class).** The manuscript's edge machine is a workstation
(Xeon W-2123, 64 GB, 2×RTX 3090; `00` RF-K2). This changes the backbone question:
* If the router runs on the **edge GPU**, ModernBERT's GPU-targeted design
  is relevant: RTX 3090 is in its design basket `[AUTHOR-CLAIM]`. But the router
  then **contends with the Edge SLM / Split head for the same GPU**, and that
  contention must be measured (E7).
* If the router runs on the **Xeon CPU** (W-2123 supports AVX-512; INT8 VNNI
  availability `[OPEN]`, to be checked on the actual machine), then ModernBERT's GPU
  advantages do not transfer, and the smaller Ettin/MiniLM rows become more
  attractive.
* Phone/Jetson-class latency is **not** claimed anywhere in v3 unless measured on such a
  device.

---

## 4. Requirements re-scored (R1–R7 from v2, evidence-only)

| Requirement | ModernBERT-base | Ettin-32m / 68m | DeBERTa-v3-small | MiniLM-L12-H384 |
|---|---|---|---|---|
| R1 strong fine-tuned NLU at its size | GLUE 88.4 `[AUTHOR-CLAIM]` | 83.5 / 87.2 `[AUTHOR-CLAIM]` | MNLI 88.3 `[AUTHOR-CLAIM]` | MNLI 85.7 `[AUTHOR-CLAIM]` (card) |
| R2 per-query compute | highest (≈111 M non-emb.) | low (≈13 M / ≈42 M) | medium (44 M + disentangled-attn) | low (≈21 M) |
| R3 multi-output head | trivially supported (all) | same | same | same |
| R4 same-tokenizer larger teacher | ModernBERT-large / Ettin-400m | **ModernBERT-base/large, Ettin-150m/400m — one tokenizer across the whole ladder** | DeBERTa-v3-base/large | cross-family only |
| R5 permissive licence | Apache-2.0 | MIT | MIT | MIT |
| R6 deployable export | official ONNX + INT8 files; Optimum-listed; fidelity caveat | Optimum lists `ModernBert` (same model_type) — export path same as ModernBERT `[OPEN]` until done | Optimum lists `Deberta-v2`; no official files `[OPEN]` | Optimum lists `Bert`; mature |
| R7 context ≥ query length | 8,192 | 7,999 | 512 | 512 |
| Routing-specific precedent | HyDRA (ModernBERT-base, multi-sigmoid) `[VERIFIED-BODY]`; HyDRA App. F encoder ablation `[AUTHOR-CLAIM]` | none found | BEST-Route (DeBERTa-v3-small), Hybrid LLM (DeBERTa-v3-large) `[VERIFIED-BODY]` (`05`) | none in `05` set |

Two facts the v2 matrix missed: **DeBERTa-v3 has the stronger routing precedent**
(BEST-Route uses DeBERTa-v3-small with per-action sigmoid heads; Hybrid LLM uses
DeBERTa-v3-large). So DeBERTa-v3-small is the *routing-literature-matched*
control, not merely an "accuracy option". Also, **R7 matters only if our
query-length distribution exceeds 512 tokens.** That is an empirical property of
the chosen datasets (`10`/`13`) `[OPEN]`, not a reason by itself.

---

## 5. Recommendation `[PROPOSED]`

**First implementation candidate: ModernBERT-base (149.7 M; Apache-2.0;
`answerdotai/ModernBERT-base`).** It remains the first candidate, but for
narrower and more honest reasons than v2 gave:

1. **Lowest integration risk today.** Native in `transformers` ≥ 4.48. Official
   ONNX FP32/FP16/INT8 artifacts exist. Optimum lists the architecture. The 8k
   context removes truncation as a confound while datasets are still being chosen.
2. **One tokenizer from 17 M to 1 B.** ModernBERT-base/large and the Ettin ladder
   share a byte-identical tokenizer. Teacher↔student KD (incl. S4
   representation distillation in `04`) and the size ablation then need no
   vocabulary alignment. This is the strongest *method-level* reason, and it
   comes from the ModernBERT+Ettin family together, not ModernBERT alone.
3. **Direct routing precedent** for an encoder + multi-sigmoid-head router on this
   backbone (HyDRA) `[VERIFIED-BODY]`. This also means it carries **no novelty**
   (`05` §1.3).
4. **Competitive fine-tuned NLU** relative to DeBERTa-v3-base `[AUTHOR-CLAIM]`.

**It is *not* recommended because** it is the fastest on our edge hardware (unmeasured),
because LLMRouterBench shows backbones don't matter (it does not, for this
setting), or because it is "micro" (it is base-size).

**Mandatory size/backbone ladder in experiments (§7):** ModernBERT-base is the
*default* student. The paper's deployment claim must rest on the **smallest
backbone that passes the pre-registered rule in §6**. That may well be Ettin-32m/68m
or MiniLM rather than ModernBERT-base.

**Teacher:** ModernBERT-large (395.9 M, Apache-2.0) as primary; Ettin-400m as a
same-tokenizer alternative. Whether a teacher is useful at all is decided in
`03` / E1, not here.

---

## 6. Pre-registered backbone selection rule `[PROPOSED]`

Fix this before any test-set result is seen:

* Candidates **B** = {ModernBERT-base, Ettin-68m, Ettin-32m, DeBERTa-v3-small,
  MiniLM-L12-H384}. TF-IDF+LR stays as the non-neural floor (`11`).
* Train each with the **same** non-KD protocol (S1 / S1-MS from `04`), the same
  heads, the same HPO budget (equal trials), and **≥3 seeds**.
* Validation metric: routing utility at the operating point(s) defined in `09`,
  plus AUROC/ECE of Û, all on the **validation** split.
* **Deployment backbone** = the smallest-latency candidate whose validation
  utility is within **δ** of the best candidate (δ fixed in advance; suggested
  δ = 1 point of normalized utility, or the seed std if larger, `[OPEN]` for
  advisor) **and** whose measured p95 router latency on the real edge node
  (device chosen per RF-K2) is ≤ the router-overhead budget from `09`.
* Report all candidates on test. Do not report only the winner.

This makes "which encoder" a falsifiable engineering outcome. The paper's
claim is "a compact encoder suffices", not "ModernBERT is best".

---

## 7. Experiment hooks handed to `13`

| Hook | What it measures | Gate |
|---|---|---|
| **E-BB (backbone/size ladder)** | §6 rule across B; utility, AUROC, ECE, p50/p95 router latency (PyTorch & ONNX), RAM | decides deployment backbone; feeds Conservative/Conditional claims in `12` |
| **E-BB-Q (export fidelity)** | FP32 vs ONNX-FP32 vs ONNX-INT8: decision agreement, ΔECE, Δutility | must pass before any INT8 latency is quoted |
| **E-BB-ctx** | query token-length distribution per dataset (ModernBERT tokenizer and DeBERTa SentencePiece); % > 128, > 512 | decides whether R7 / local-attention arguments matter at all |
| **E1 interaction** | KD gain measured **per student size**: KD often helps small students more | prevents "KD adds nothing" or "KD helps" from being an artifact of one size |

---

## 8. What may be written in the manuscript

**Allowed** (with citations from `method-references-v3.bib`):
* "We instantiate the encoder with ModernBERT-base~\cite{warner2025modernbert},
  a 149M-parameter bidirectional encoder released under Apache-2.0; smaller
  encoders from the Ettin suite~\cite{weller2026ettin}, which share its tokenizer,
  and DeBERTa-v3~\cite{he2023debertav3} are evaluated as alternatives."
  (Parameter count and licence from the released checkpoint; cite the paper for
  the model.)
* "Backbone choice is treated as an engineering parameter; we select the
  smallest encoder within δ of the best validation utility (§…)."
* Bounded LLMRouterBench sentence, exactly as in `05` §4.

**Not allowed** `[REJECT]`:
* "ModernBERT is the fastest/most efficient encoder" (GPU-only author claim, not
  our hardware).
* "ModernBERT runs in X ms on edge devices" (unless *we* measure X on *our* node).
* "Encoder choice does not matter for routing" (LLMRouterBench over-extension).
* "micro-encoder" for a 149 M model without qualification.
* Any novelty claim attached to the backbone, the multi-sigmoid head on
  ModernBERT (HyDRA), or the INT8/ONNX deployment.

---

## 9. Residual gaps

* MiniLM and DeBERTa-v3 bodies were only partially read (DeBERTa Table 9; MiniLM
  abstract + card) → `[VERIFIED-META]` for bib; not load-bearing.
* No independent CPU/edge latency study of ModernBERT or Ettin was found in this
  check; HyDRA's numbers remain the only routing-relevant latency, as `[AUTHOR-CLAIM]`.
* Ettin ONNX export not attempted (no Python ML stack on this machine; see `00` §1).
* NeoBERT / EuroBERT / mmBERT were not assessed. The brief asks for "at least one"
  other current compact encoder, and Ettin is the most relevant because it shares
  ModernBERT's tokenizer. Adding more would reopen method search, which the brief §13 forbids.
