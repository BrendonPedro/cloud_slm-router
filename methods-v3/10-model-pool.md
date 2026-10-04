# 10 — Model pool: verification, selection criteria, initial vs full pool

*Deliverable for `MICROENCODER_HARDENING_BRIEF.md` §16. Resolves RF-K1 and
RF-K3 (`00` §2.6) and the pool hand-offs from `01` §8, `08` §6.2 and `09` §8.
Evidence tags follow brief §29: `[VERIFIED-BODY]`, `[VERIFIED-META]`,
`[AUTHOR-CLAIM]`, `[PROPOSED]`, `[OPEN]`, `[REJECT]`. This file also uses
`[API]` for facts read from the Hugging Face Hub API, `config.json` or model card
on 2026-10-04, `[CODE]` for facts read from library source code, and
`[DERIVED]` for arithmetic on those facts. `source/main-original.tex` and
`methods-v2/` are not modified.*

> **What this file does not do.** It does not pick the final pool and does not
> reconstruct the advisor's B1/Gemma remark. The remark stays `[OPEN]`
> (`methods-v2/16` O7). Nothing below claims advisor approval for any model.
> The Split model is whatever Henry's code supports (`14`). Every pair proposed
> here is conditional on that.

---

## 1. Decisions in one table

| # | Question | Answer | Tag |
|---|---|---|---|
| P1 | Are the manuscript's model names valid? | 8 of 11 resolve to an official checkpoint. **`Qwen3-72B-Instruct` does not exist.** The Gemma-4 **"-A4B" suffix** on E2B/E4B/12B is invalid. The **Nemotron** name is informal. Several descriptions are wrong or uncited (§3). | `[API]` |
| P2 | Which models can be Split cleanly? | Standard dense decoders (Qwen3, Qwen2.5, Phi-4-mini, Llama-3.x, Gemma-4-12B): the cut carries only the residual stream. **Gemma-4 E2B/E4B are poor first Split candidates**: the cut must also carry per-layer input embeddings, and for deep cuts shared KV states. Hybrid Mamba/linear-attention and MoE models can be split but add E0 risk. Diffusion LMs are **EDGE-only** (§4). | `[CODE]`/`[API]`/`[DERIVED]` |
| P3 | Is N=2 the cleanest first milestone? | **Yes**: one edge SLM `M_E` plus one Split-capable model `M_S`, with actions `EDGE(M_E)`, `SPLIT_d(M_S)` for `d ∈ D`, and `REMOTE(M_S)`. This is case C1 of `01` §1.1, so `K = 2` utility heads. It isolates E0, E1 and the `09` §2.3(b) Split-vs-Remote check before the pool grows (§7). | `[PROPOSED]` |
| P4 | Does `REMOTE(M_S)` exist in the action set? | **Yes, as an action and a baseline**. The deployed policy is evaluated in two regimes: **open** (raw prompt may leave the edge) and **private** (`REMOTE` masked by a data-policy constraint). Which regime the paper headlines is an advisor decision (§6). | `[PROPOSED]` / `[OPEN]` |
| P5 | Can the pool be fixed now? | **No.** It must first pass a **headroom pilot** (§5.2) on the actual datasets and specifications. SimpleQA alone is likely near the floor for edge SLMs (`08` §6.2(3)). | `[PROPOSED]` |
| P6 | Initial implementation pool | Two candidate pairs, both conditional on Henry (§7.2). **P-A, manuscript continuity:** `Phi-4-mini-instruct` + `Llama-3.3-70B-Instruct`. **P-B, ungated, one family:** `Qwen3-4B-Instruct-2507` + `Qwen3-32B` (non-thinking). If Henry's code supports only one checkpoint, that checkpoint is `M_S` and the edge model is chosen by §5. | `[PROPOSED]` / `[OPEN]` |
| P7 | Full paper pool | `K` of about 4–6 model specifications: ≥ 2 edge SLMs from different families, ≥ 1 Split-capable model, ≥ 1 strong model with no Split variant, and optionally one diffusion SLM as an EDGE-only action (§8). Its composition is an advisor decision. | `[PROPOSED]` / `[OPEN]` |

---

## 2. What a "model" is in this pool

From `01` §1.1, a pool member is a **model specification**: checkpoint,
weight quantization artefact, decoding configuration (temperature, max tokens,
thinking flag, chat template) and serving numerics. Consequences for pool
design:

* "All models are deployed using 4-bit quantization" (main-original.tex L268,
  L295) makes the **4-bit artefact** the specification. Utility labels must be
  generated with that same artefact. Weight quantization is a property of `M`,
  not a Split loss, provided split and unsplit runs use the same weights
  (`02` §3).
* Models with a **thinking mode** need the flag fixed in the specification.
  Qwen3-32B defaults to `enable_thinking=True` (model card, "Switching Between
  Thinking and Non-Thinking Mode"). Qwen3-4B-Instruct-2507 "supports only
  non-thinking mode" (model card). Nemotron-3-Nano "first generat[es] a
  reasoning trace" by default and can be switched off via the chat template
  (model card). `[API]` Thinking on and thinking off are **two different
  specifications** with different utility and very different decode length,
  and therefore different `C`. The initial pool uses non-thinking for every
  model. A thinking variant is a separate pool member only if the advisor
  wants it. `[PROPOSED]`
* Diffusion LMs need their sampler (steps, block size, remasking) fixed in the
  specification for the same reason.

---

## 3. Manuscript pool as written, re-verified

Source: `source/main-original.tex` §"Weak Models / SLMs" (L267–292) and
§"Strong Models" (L294–303). Hub facts were fetched on 2026-10-04 from
`huggingface.co/api/models/<id>` (fields `gated`, `safetensors.parameters`,
licence tag, `createdAt`) and from each repo's `config.json`. `[API]`
Parameter counts are stored BF16 parameters from the safetensors index.

### 3.1 Edge / weak models

| # | As written (line) | Official HF ID | Stored params | Licence; gating | Architecture (from `config.json`) | Verdict |
|---|---|---|---|---|---|---|
| W1 | Gemma-4-E2B-A4B (L273) | `google/gemma-4-E2B-it` | 5,123,178,051 | Apache-2.0; ungated | `gemma4_text`, 35 layers, hidden 1536, `hidden_size_per_layer_input` 256, `num_kv_shared_layers` 20; multimodal wrapper | **Name invalid**: no "-A4B" variant. The text says "2B-parameter", but 5.12 B are stored ("E" = effective, `methods-v2/10` §3). Fix to `gemma-4-E2B-it` and state the stored count. |
| W2 | Gemma-4-E4B-A4B (L275) | `google/gemma-4-E4B-it` | 7,996,156,490 | Apache-2.0; ungated | `gemma4_text`, 42 layers, hidden 2560, per-layer input 256, 18 KV-shared layers | **Name invalid** (drop "-A4B"). "4B-parameter" understates the 8.0 B stored. |
| W3 | Gemma-4-12B-A4B (L277) | `google/gemma-4-12B-it` | 11,959,730,224 | Apache-2.0; ungated | `gemma4_unified_text`, 48 layers, hidden 3840, no per-layer input, no KV sharing | **Name invalid** (drop "-A4B"). The only "A4B" Gemma-4 checkpoint is `gemma-4-26B-A4B-it` (MoE, 128 experts, 25.8 B stored). |
| W4 | Phi-4-mini-3.8B (L280) | `microsoft/Phi-4-mini-instruct` | 3,836,021,760 | MIT; ungated | `phi3`, 32 layers, hidden 3072 | **Valid.** Use the official ID. |
| W5 | Meta-Llama-3.1-8B-Instruct (L282) | `meta-llama/Llama-3.1-8B-Instruct` | 8,030,261,248 | Llama 3.1 licence; **gated (manual)** | dense decoder | **Valid.** Gating is a reproducibility cost. 8 B is the upper end of "SLM". |
| W6 | LLaDA-MoE-7B-A1B-Instruct-Q4 (L286) | `inclusionAI/LLaDA-MoE-7B-A1B-Instruct` | 7,356,880,896 | Apache-2.0; ungated | diffusion MoE | **Model valid; "Q4" artefact unnamed.** The official repo is BF16. A Q4 build must be named exactly `[OPEN]`. |
| W7 | Dream-v0-Instruct-7B (L288) | `Dream-org/Dream-v0-Instruct-7B` | 7,615,616,512 | Apache-2.0; ungated | diffusion | **Valid.** The attribution "from Huawei Noah's Ark Lab" and "top-tier performance" were flagged in `methods-v2/10` §3; drop both unless a source is cited. |
| W8 | Fast-dLLM-v2-7B (L290) | `Efficient-Large-Model/Fast_dLLM_v2_7B` | 7,615,616,512 (BF16 entry; the API's `total` field reads 333,312 and is ignored) | Apache-2.0; ungated | block-diffusion adaptation of Qwen2.5-7B-Instruct | **Valid.** Cite the Fast-dLLM v2 paper for the adaptation claim. |

### 3.2 Strong / Split models

| # | As written (line) | Official HF ID | Stored params | Licence; gating | Architecture | Verdict |
|---|---|---|---|---|---|---|
| S1 | Qwen3-72B-Instruct (L298) | **none** | — | — | — | **Does not exist.** `api/models/Qwen/Qwen3-72B-Instruct` returns an error, and a Hub search of author `Qwen` for "72B" returns only Qwen, Qwen1.5, Qwen2 and Qwen2.5 72B repos (plus VL/Math/RM variants). The substitute is an advisor decision (§7.3). `[REJECT]` the name. |
| S2 | Llama-3.3-70B-Instruct (L300) | `meta-llama/Llama-3.3-70B-Instruct` | 70,553,706,496 | Llama 3.3 licence; **gated (manual)** | dense decoder | **Valid.** Delete "Meta's latest": Llama-4 checkpoints exist on the Hub (for example `Llama-4-Scout-17B-16E-Instruct`, created 2025-04-02). |
| S3 | NVIDIA Nemotron-3 Nano-30B (L302) | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 31,577,937,344 | NVIDIA Nemotron Open Model License; ungated | `nemotron_h`, 52 layers, hidden 2688, 128 routed experts, Mamba-2/attention/MoE pattern | **Valid model, informal name.** Use the official ID. The card says "23 Mamba-2 and MoE layers, along with 6 Attention layers … 3.5B active parameters and 30B parameters in total" `[AUTHOR-CLAIM]`. Cite the technical report (arXiv 2512.20848, linked from the card) if the description is kept. |

### 3.3 Required manuscript corrections (to apply in the v3 text, not in main-original.tex)

1. Replace `Qwen3-72B-Instruct` with an existing checkpoint chosen by the
   advisor (§7.3), or remove it.
2. Drop "-A4B" from all three Gemma-4 entries. Replace "2B-/4B-parameter" with
   the effective/stored distinction, or with stored counts only.
3. Use official HF IDs throughout. Nemotron becomes
   `NVIDIA-Nemotron-3-Nano-30B-A3B`.
4. Remove the uncited adjectives "latest", "top-tier", "state-of-the-art",
   "flagship", or cite them.
5. Remove "routing labels can be automatically constructed without repeatedly
   executing … SLMs and Split-LLMs" (L205). None of these models has SimpleQA
   records in LLMRouterBench (`08` §6.1). The LLMRouterBench performance
   setting does contain `Llama-3.1-8B-Instruct` and `Qwen3-8B` on 15 other
   datasets, but not under our 4-bit specifications (`08` §6.2(2)).
6. Name the exact 4-bit artefact (method and repo) for every model.

---

## 4. Split compatibility depends on architecture

`09` §2.3(a) derived that for a standard dense decoder the tensor crossing a
cut after layer `d` is the residual stream, `n × hidden_size`, the same for
every `d`. It also listed "extra per-layer streams" as an exception. The
current pool contains a concrete instance of that exception.

### 4.1 Standard dense decoders: residual-only cut `[API]`/`[DERIVED]`

Qwen3 dense, Qwen2.5, Phi-4-mini, Llama-3.x and Gemma-4-12B (no per-layer
input, no KV sharing in its config) carry one residual row per token.
In BF16 that is `2 × hidden_size` bytes per token:

| Model | hidden | layers | Bytes/token across the cut (BF16) |
|---|---|---|---|
| `Qwen/Qwen3-32B` | 5120 | 64 | 10,240 |
| `Qwen/Qwen2.5-72B-Instruct` | 8192 | 80 | 16,384 |
| `google/gemma-4-12B-it` | 3840 | 48 | 7,680 |
| `Qwen/Qwen3-8B` | 4096 | 36 | 8,192 |
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 2688 | 52 | 5,376 |

(Llama-3.3-70B's `config.json` is gated and was not fetched. Its hidden size
is not stated here.)

### 4.2 Gemma-4 E2B/E4B: per-layer inputs and KV sharing `[CODE]`

From `transformers/models/gemma4/modeling_gemma4.py` (main branch, fetched
2026-10-04):

* **Per-layer inputs.** When `hidden_size_per_layer_input > 0`, each decoder
  layer has a `per_layer_input_gate` and a `per_layer_projection` and
  multiplies its hidden state by a layer-specific `per_layer_input`. Those
  inputs are built once from the token ids (`embed_tokens_per_layer(input_ids)`)
  and from a projection of the input embeddings (`get_per_layer_inputs`,
  `project_per_layer_inputs`). A server running layers `[d, L)` therefore
  needs either the **token ids**, which means raw content leaves the edge and
  defeats the privacy motivation for Split, or the **per-layer inputs for
  every remaining layer**, `(L − d) × 256` extra values per token.
  `[DERIVED]` For E2B (`L = 35`, hidden 1536), a cut at `d = 8` carries
  `1536 + 27·256 = 8,448` values per token instead of 1,536, about 5.5×, and
  the payload **shrinks as `d` grows**. Bytes are depth-dependent for this
  family, which is the opposite of the dense default in `09` §2.3(a).
* **KV sharing.** Layers with index `≥ L − num_kv_shared_layers` (15 for E2B,
  24 for E4B) compute no K/V. They read `shared_kv_states[layer_type]`, which
  the last non-shared layer of each attention type stores
  (`store_full_length_kv`). If the cut falls after those source layers, the
  full-length shared K/V for each attention type must also cross the
  network. If it falls before, the server recomputes them. Either way the
  message pattern is not "one residual row".

**Consequence `[PROPOSED]`.** Gemma-4 E2B/E4B are valid **EDGE-only** pool
members. They are poor first **Split** models: their bytes depend on `d`, and
Henry's split API would have to forward per-layer inputs and, for deep cuts,
shared KV. If the advisor's Gemma remark (O7) meant a Gemma-4 E-series model
as the Split model, that is a question for Henry (`14`), not something to
assume.

### 4.3 Hybrid and MoE models

* **Nemotron-3-Nano** (Mamba-2 + attention + MoE) and **Qwen3.5**
  (`layer_types` mixes `linear_attention` and `full_attention`, e.g. 24/8 for
  Qwen3.5-9B) still pass one residual row at a cut. Recurrent or
  linear-attention state stays on the side that owns the layer. `[API]`
  Splitting is feasible in principle. The extra risk is in E0: MoE routing
  ties and custom scan kernels are additional sources of numerical divergence
  (`02` §3). Prefer a dense model for the first E0.
* **Gemma-4-26B-A4B** (MoE, 128 experts): same comment.

### 4.4 Diffusion LMs

LLaDA-MoE, Dream and Fast-dLLM-v2 decode by iterative denoising over blocks,
not token by token. The per-token pipeline-split pattern in `09` §2.3(b) does
not apply, and no Split implementation for them is known to this sprint.
They are **EDGE-only** actions. Their 4-bit behaviour is unverified
(`methods-v2/10` §3, W6). `[OPEN]`

---

## 5. Selection criteria

### 5.1 Criteria `[PROPOSED]`

| ID | Criterion | Test | Source of the requirement |
|---|---|---|---|
| SC1 | **Edge feasibility.** `M_E` fits the edge device with KV cache for the evaluation prompt lengths. | Measured peak memory on Henry's edge machine (`14`). §9 gives only weight lower bounds. | brief §16 |
| SC2 | **Split compatibility.** `M_S` is supported by Henry's split API; the cut is residual-only, or its extra streams are known. | Henry's answer plus the §4 config check. | `02`, `09` §2.3 |
| SC3 | **Headroom.** The oracle gain over the best single model is material, and the edge model succeeds on a non-trivial share of queries. | Pilot metrics H1–H4 (§5.2). | `08` §6.2(3) |
| SC4 | **Overlapping competence.** Neither model dominates on every query: `P(M_E correct ∧ M_S wrong) > 0`. | H3 | brief §16 |
| SC5 | **Open and reproducible.** Official checkpoint, licence allows research use, and the exact 4-bit artefact is named. Ungated is preferred. | §3 tables | brief §16 |
| SC6 | **Feasible VRAM** on the server, including the unsplit reference run that E0 needs. | §9 plus Henry's GPU list | `02` §5 |
| SC7 | **Specification stability.** Thinking mode, template and sampler are fixed; greedy decoding is possible for E0. | §2 | `02` §5, `08` |
| SC8 | **Label cost.** Running every specification on every training query is affordable. | Tokens × models × datasets | `08` §6.2(1) |

### 5.2 Headroom pilot `[PROPOSED]`

Before fixing the pool, run each candidate specification on a stratified
sample (about 500 queries per dataset, from the datasets in `08`/`13`). Score
with the pinned evaluator `S_D` and report per dataset:

* **H1** `Ū(M)` = mean score of each model;
* **H2** oracle score `E_q max_M S(q, M)` and the oracle gain over the best
  single model;
* **H3** complementarity `P(S(q,M_E) ≥ τ ∧ S(q,M_S) < τ)` (edge-only wins),
  with `τ` the dataset's pass threshold (`08` §3);
* **H4** the cost-free routing ceiling: the fraction of queries the edge can
  answer as well as `M_S`.

No numeric thresholds are pre-set in this file, because none can be justified
without data. The decision is recorded with the pilot numbers. **Warning
sign:** if H1 for the edge model is near 0 on a dataset (likely for SimpleQA,
`08` §6.2(3)), that dataset cannot teach the router when to stay on the edge
and must not be the only dataset. LLMRouterBench's released performance-setting
outcomes for `Llama-3.1-8B-Instruct` and `Qwen3-8B` may serve as a free
**pre-pilot** indication on its 15 datasets. They are not our specifications
(`08` §6.2(2)).

---

## 6. Action→model map and the `REMOTE(M_S)` question

From `01` §1.1 and `09` §2.3(b):

```
N = 2 pool (case C1):   𝓜 = {M_E, M_S}
𝒜 = { EDGE(M_E),  SPLIT_d(M_S) for d ∈ D,  REMOTE(M_S) }
M(EDGE) = M_E,   M(SPLIT_d) = M(REMOTE) = M_S
```

`09` §2.3(b) showed that in the exact branch `SPLIT_d(M_S)` has the same
utility as `REMOTE(M_S)` and, with server-side sampling, at least one RTT per
output token. Under a latency-only cost it loses to `REMOTE` unless `REMOTE` is
infeasible. The pool design therefore keeps `REMOTE(M_S)`, because removing it
would hide the most important systems comparison, and evaluates two regimes:

| Regime | Constraint | What it tests |
|---|---|---|
| **Open** | All actions allowed. | Whether Split is ever chosen on cost grounds (E7). If not, report it. |
| **Private** | `REMOTE` masked: raw prompts may not leave the edge (data-policy constraint, `09` §3). | Router value when the choice is EDGE vs SPLIT_d, which is the manuscript's privacy motivation (L76). Activations are not private by themselves (L78, SnD). The paper must say so. |

Which regime is the paper's headline is **advisor-owned** `[OPEN]`. If
Henry's message pattern avoids the per-token round trip (speculative or
batched schemes), the open regime changes and `09` must be revisited.

---

## 7. INITIAL IMPLEMENTATION POOL (milestone M0, N = 2)

### 7.1 Why N = 2 first

* **E0 is cleanest.** One Split model, a few depths and one unsplit reference.
  `02` §5 can run before any router exists.
* **Issue A is decided at N = 2.** Model-level vs depth-level utility is a
  question about `SPLIT_d(M_S)` vs `REMOTE(M_S)`. It does not need a third model.
* **The baselines are well defined.** RouteLLM-style binary routers, TF-IDF+LR,
  Always-Edge, Always-Strong, Always-Split and the oracle are all defined for
  two models (`11`).
* **E1 (KD vs C\*) has a single comparison axis** and the label cost is
  smallest.
* **Risk.** With `K = 2` the per-model-head design is barely distinguishable
  from a single binary classifier. Claims about multi-model routing, and the
  advantage of independent heads under pool change, **need N ≥ 3** (M1). This
  is a limitation of M0, not a reason to skip it.

### 7.2 Candidate pairs `[PROPOSED]`, all conditional on Henry `[OPEN]`

| Pair | `M_E` (edge) | `M_S` (Split + Remote) | For | Against |
|---|---|---|---|---|
| **P-A, manuscript continuity** | `microsoft/Phi-4-mini-instruct` (3.84 B, MIT) | `meta-llama/Llama-3.3-70B-Instruct` (70.6 B, gated) | Both names are already in the manuscript and valid. Large quality gap expected. Dense residual cut. | `M_S` is gated (manual approval). 4-bit weights alone are ≥ 35 GB (§9), so the E0 unsplit reference needs a large server GPU. Different tokenizers, which only matters for cost accounting. |
| **P-B, open, one family** | `Qwen/Qwen3-4B-Instruct-2507` (4.02 B, Apache-2.0, non-thinking only) | `Qwen/Qwen3-32B` (32.8 B, Apache-2.0; `enable_thinking=False` fixed) | Ungated, permissive licence, dense residual cut (hidden 5120, 10,240 B/token in BF16), 4-bit weights ≥ 16 GB. One tokenizer and template family. | Not in the manuscript, so the advisor must accept the change. Same-family models may have more correlated failures and therefore less headroom; the pilot (§5.2) checks this. |
| **P-H, Henry-determined** | chosen by §5 | **the checkpoint Henry's code supports** | Avoids porting the Split code. | Unknown until `14` is answered. |

**Recommendation.** If Henry's code is model-agnostic for standard HF decoders,
start with **P-B**: it has the fewest access, licence and VRAM obstacles to
running E0 and the pilot quickly. Keep P-A as the manuscript-continuity
option. If Henry's code is tied to one checkpoint, use **P-H**. Any choice is
recorded as `[OPEN]` until the advisor confirms it. Gemma-4 E2B/E4B are not
proposed as `M_S` (§4.2). They are reasonable `M_E` candidates if the advisor's
Gemma remark points there.

### 7.3 Substitute for `Qwen3-72B-Instruct` (advisor decision) `[OPEN]`

Existing checkpoints that fill the "very large dense Split-LLM" role:

| Option | Params (stored) | Licence | Note |
|---|---|---|---|
| `Qwen/Qwen2.5-72B-Instruct` | 72.7 B | Qwen licence (`license: other`, `license_name: qwen`) | Closest to the intended name and size; previous generation. |
| `Qwen/Qwen3-32B` | 32.8 B | Apache-2.0 | Largest dense Qwen3; thinking flag must be fixed. |
| `Qwen/Qwen3.5-27B` | (not fetched) | (not fetched) | Newer, but a hybrid linear/full-attention architecture (48/16 layers); more E0 risk (§4.3). |

The sprint does not choose among these.

---

## 8. FULL PAPER POOL (milestones M1 and M2)

| Milestone | Pool | Purpose | Gate |
|---|---|---|---|
| **M1** (N = 3) | M0 plus one more model: a second edge SLM from another family (e.g. Phi-4-mini with Qwen3-4B), or the C2 case (`01` §1.1, a different-numerics strong model) | First multi-model routing claim; the C2 action map is exercised. | M0 E0 and E1 complete. |
| **M2** (paper) | About 4–6 specifications: ≥ 2 edge SLMs (different families; ≤ 8 B), ≥ 1 Split-capable model, ≥ 1 strong model without a Split variant (REMOTE-only), and optionally one diffusion SLM as an EDGE-only action | Generalisation across families and paradigms (main-original.tex L268 motivation). | Pilot headroom per added model (each model must add oracle gain on at least one dataset, otherwise it only adds label cost). |

The manuscript's list of eight weak and three strong models is **too large for
the conference core**. Every added model multiplies label cost (SC8), and a
model without unique wins adds no routing signal. The paper should state the
pool-size rationale instead of listing every available SLM. Further pool
growth, new SLMs and pool change belong to the **journal extension** (`15`).
`[PROPOSED]`

---

## 9. Weight-memory lower bounds `[DERIVED]`

`bytes ≥ stored params × bits / 8`, decimal GB. Excludes KV cache,
activations, quantization scales, unquantized embeddings and framework
overhead, so real peaks are higher. Use only to rule models **out**.

| Model | Stored params | BF16 weights | 4-bit weights |
|---|---|---|---|
| Phi-4-mini-instruct | 3.84 B | 7.7 GB | 1.9 GB |
| Qwen3-4B-Instruct-2507 | 4.02 B | 8.0 GB | 2.0 GB |
| Gemma-4-E2B-it | 5.12 B | 10.2 GB | 2.6 GB |
| Gemma-4-E4B-it | 8.00 B | 16.0 GB | 4.0 GB |
| Llama-3.1-8B-Instruct | 8.03 B | 16.1 GB | 4.0 GB |
| Qwen3-8B | 8.19 B | 16.4 GB | 4.1 GB |
| Gemma-4-12B-it | 11.96 B | 23.9 GB | 6.0 GB |
| NVIDIA-Nemotron-3-Nano-30B-A3B | 31.58 B | 63.2 GB | 15.8 GB |
| Qwen3-32B | 32.76 B | 65.5 GB | 16.4 GB |
| Llama-3.3-70B-Instruct | 70.55 B | 141.1 GB | 35.3 GB |
| Qwen2.5-72B-Instruct | 72.71 B | 145.4 GB | 36.4 GB |

For `SPLIT_d`, the edge holds layers `[0, d)` plus embeddings, and the server
holds `[d, L)` plus the head. E0's unsplit reference needs the **whole**
`M_S` on one side. Feasibility depends on Henry's GPUs (`14`), which this
sprint does not know.

---

## 10. Manuscript wording `[PROPOSED]`

**Allowed (after the pool is fixed):** "We instantiate the pool with
⟨official IDs⟩ under ⟨named 4-bit artefact⟩ and fixed decoding settings. The
edge model is chosen to have non-trivial accuracy on each evaluation dataset,
and the strong model to provide headroom (Section ⟨pilot⟩)."

**Not allowed:** invalid names (§3.3); "state-of-the-art"/"top-tier"/"latest"
without a citation; "pre-computed labels in LLMRouterBench" for this pool; any
statement that the advisor selected a specific model, until recorded.

---

## 11. Hand-offs

| To | Item |
|---|---|
| `11-baselines-v3.md` | Baselines are defined first for N = 2 (M0); list which ones extend to N ≥ 3. |
| `13-experiments-v3.md` | Add the headroom pilot (§5.2) as a pre-E1 gate. E0 runs on `M_S` of the chosen pair. E7 runs both regimes (§6). |
| `14-henry-checklist.md` | Supported HF IDs; whether the split API forwards extra per-layer streams or KV (§4.2); where sampling runs; edge/server GPUs and VRAM (§9). |
| `15-conference-vs-journal.md` | M2 growth beyond about 6 models, and pool change, are journal scope. |
| `proposed-solution-blue-v3.tex` | Pool described abstractly (`M_E`, `M_S`, `𝒜`). Concrete names only in the experimental section, after the decision. |
| `FINAL-SUMMARY-v3.md` | Q24 (advisor: pair, Qwen3-72B substitute, regime, Gemma remark); Q25 (Henry: supported model). |

### 11.1 Open items

* O-P1: initial pair (P-A / P-B / P-H). Advisor + Henry. `[OPEN]`
* O-P2: substitute for `Qwen3-72B-Instruct`. Advisor. `[OPEN]`
* O-P3: headline regime (open vs private). Advisor. `[OPEN]`
* O-P4: the B1/Gemma remark (`methods-v2/16` O7). Advisor. Not reconstructed. `[OPEN]`
* O-P5: exact 4-bit artefacts and whether 4-bit diffusion LMs behave. `[OPEN]`
* O-P6: datasets beyond SimpleQA, chosen jointly with the pilot (`08`, `13`). `[OPEN]`

---

## 12. Sources and how they were checked

| Source | What was read | Supports | Tag |
|---|---|---|---|
| Hugging Face Hub API `api/models/<id>` for the 28 IDs in §3, §7 and §9 (2026-10-04) | `gated`, `safetensors.parameters`, licence tags, `cardData.license_name`, `createdAt` | Existence, stored params, licences, gating | `[API]` |
| `config.json` of 15 repos (2026-10-04) | `hidden_size`, `num_hidden_layers`, `hidden_size_per_layer_input`, `num_kv_shared_layers`, `layer_types`, `hybrid_override_pattern`, expert counts | §4 cut sizes and architecture classes | `[API]` |
| Hub search `author=Qwen&search=72B`, `author=google&search=gemma-4`, `author=Qwen&search=Qwen3.5` | Repo listings | Qwen3-72B absence; Gemma-4 variant names | `[API]` |
| `huggingface/transformers` `src/transformers/models/gemma4/modeling_gemma4.py` (main, 2026-10-04) | KV-sharing logic (`first_kv_shared_layer_idx`, `store_full_length_kv`, `shared_kv_states`); per-layer input path (`get_per_layer_inputs`, `project_per_layer_inputs`, `per_layer_input_gate`) | §4.2 | `[CODE]` |
| Model cards: Qwen3-32B, Qwen3-4B-Instruct-2507, NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | Thinking-mode sections; architecture and parameter statements | §2, §3.2 | `[AUTHOR-CLAIM]` |
| LLMRouterBench `README.md` (ynulihao/LLMRouterBench@main) | Performance-setting model table | §3.3(5), §5.2 pre-pilot | `[CODE]` (also `08` §6.1) |
| `methods-v2/10-model-pool-and-baselines.md` §3 | Prior verdicts (re-checked here, not inherited) | Cross-check | — |

No paper is cited as `[VERIFIED-BODY]` in this file. Model facts come from
official repositories and code, not from papers. If the manuscript describes
a model's capabilities, it must cite that model's technical report, and `17`
must verify it.
