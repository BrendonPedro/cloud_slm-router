# 02 — Split Equivalence Analysis (Issue D)

*Deliverable for `MICROENCODER_HARDENING_BRIEF.md` §5 (Issue D) and §25 (E0).
Resolves review finding **RF-D** and supplies the exact/lossy branch structure that
`01-model-vs-action-utility.md` depends on (RF-A1/RF-A2). Evidence tags follow brief
§29: `[VERIFIED-BODY]`, `[VERIFIED-META]`, `[AUTHOR-CLAIM]`, `[PROPOSED]`, `[OPEN]`,
`[REJECT]`. Nothing here is a measured result: Henry's Split-LLM code has not been
obtained, and every statement about it is `[OPEN]`. `source/main-original.tex` and
`methods-v2/` are unmodified.*

---

## 0. Bottom line

1. **`y(SPLIT(d), q) = y(full, q)` is not a premise of the method. It is a
   hypothesis that experiment E0 tests.** v2 stated it as fact in `07` §3 and in
   the FINAL-SUMMARY (RF-D). `[REJECT]` that wording.
2. "Equivalent" has at least **five different meanings**: bit-exact, greedy-token
   identical, per-query score identical, distributionally identical, and
   aggregate-metric identical (§2). The router needs only **per-query score
   equivalence measured against a noise floor** (§2.3). It does not need bit
   exactness.
3. Even a split that copies tensors exactly is **not guaranteed to be bit-exact**:
   batch size, GPU type, GPU count and kernel choice change floating-point reduction
   order, and BF16 greedy decoding can then diverge
   [Yuan et al. 2025; He 2025]. E0 must therefore compare the split against the
   **unsplit model's own run-to-run variation**, not against a single reference run
   (§5.2).
4. The manuscript itself describes the edge side as one that may "compress
   intermediate representations before transmitting them" (L76), and it cites a
   noise-adding split method, Split-and-Denoise (L78). Both are **lossy by
   construction**. Lossy split is therefore a real possibility for Henry's code and
   cannot be dismissed. `[OPEN]`
5. Two method branches result (§4):
   * **Branch X (exact or within the noise floor):** one model-level utility
     `Û_θ(M|q)` is shared by every depth; depth enters only through `C(a|s)`.
   * **Branch L (lossy):** quality may depend on depth. Start with a
     **per-depth constant penalty** `Û_θ(M|q) − Δ̂(d)`, and move to
     `Û_θ(M|q) − Δ̂(d,q)` or per-(M,d) heads only if E0 shows query-dependent
     degradation.
   * **Branch E (early exit, or any transform that changes semantics):** the
     action is a **different model** `M'` and needs its own utility label.
6. Brief §5 says not to choose the lossy formulation unless Henry's
   implementation requires it. **Branch X is therefore the default. E0 decides
   whether it survives.**

---

## 1. What exactly is being compared

### 1.1 The model identity must include the numerics

The manuscript says all strong/split models run at **4-bit quantization** (L295).
For split equivalence to mean anything, "the model" `M` must be a full execution
specification, not just a checkpoint name: `[PROPOSED]`

```
M = (HF checkpoint + revision hash,
     weight-quantization scheme + config  (e.g. 4-bit method, group size),
     compute dtype                        (fp16 / bf16 / fp32 accumulate),
     tokenizer + chat template,
     decoding config                      (greedy | temperature, top-p, max tokens, seed policy))
```

A 4-bit split model and an FP16 cloud model built from the same checkpoint are
**two different models** for routing purposes. This resolves part of RF-A2:
`M(SPLIT(d))` is not automatically `M(STRONG)`. The equivalence reference for
`SPLIT(d)` is the **unsplit run of the same specification `M(SPLIT)`**. It is not
"the strong model" in general. `[PROPOSED]`

### 1.2 The action-to-model map

`a ∈ 𝒜 = {EDGE_SLM, SPLIT(d₁), …, SPLIT(d_m), STRONG}` with `M(a)` defined as:

| Action | `M(a)` | Reference for equivalence |
|---|---|---|
| `EDGE_SLM` | edge SLM spec | — (not split) |
| `SPLIT(d)` | split-capable spec `M_S` (Henry's model, `[OPEN]`) | unsplit `M_S` with the same numerics |
| `STRONG` | strong spec `M_L`; may or may not equal `M_S` `[OPEN]` | — (not split) |

If Henry's model **is** the STRONG model with identical numerics, then
`SPLIT(d)` and `STRONG` share one utility under Branch X, and they differ only in
cost (activation transfer plus edge compute versus full remote compute). If it is
not, there are three model utilities (`EDGE`, `M_S`, `M_L`), and the split depths
still share `M_S`'s utility under Branch X. `[PROPOSED]`

---

## 2. Levels of equivalence

### 2.1 Definitions `[PROPOSED]`

Let `h_ℓ(q)` be the hidden state after layer `ℓ`, `z_t` the logits at decode
step `t`, `y` the generated sequence and `S(y,q)` the task score defined in
`08-utility-definition.md`. Compare split execution at depth `d` (superscript `d`)
with the unsplit reference (superscript `ref`):

| Level | Name | Condition | What it guarantees |
|---|---|---|---|
| E-L0 | Bit-exact | `h^d_ℓ = h^ref_ℓ` and `z^d_t = z^ref_t` bitwise, for all `ℓ,t` | everything below |
| E-L1 | Greedy-token identical | `y^d = y^ref` under greedy decoding | identical outputs and scores |
| E-L2 | Per-query score identical | `S(y^d,q) = S(y^ref,q)` for (almost) every `q` | routing labels are unchanged |
| E-L3 | Distributional | under sampling, `P(y \| q, d) = P(y \| q, ref)` (tested via per-query success rates over `k` samples) | expected-score labels unchanged |
| E-L4 | Aggregate | `\|E_q[S^d] − E_q[S^ref]\| ≤ δ` | benchmark score unchanged; **per-query labels may still differ** |

E-L0 ⇒ E-L1 ⇒ E-L2 ⇒ E-L4. E-L3 is the stochastic counterpart of E-L1/E-L2.

### 2.2 Which level the router actually needs

The router is trained on per-query labels `(q, M) → S`. Sharing one model-level
utility across depths is safe when the label it would have received at every depth
is the same, up to noise that is already present in the unsplit model. That
requires **E-L2 (greedy decoding) or E-L3 (sampled decoding)**. `[PROPOSED]`

* E-L0/E-L1 are **sufficient** but not necessary. Bit-exactness is often
  unachievable even without splitting (§3, row "kernel/hardware"), so requiring it
  would reject almost every real split implementation.
* E-L4 is **not sufficient**. A split can keep the same mean score while flipping
  many individual queries in both directions. Those flips are label noise
  attached to depth, and a per-query router would be trained on the wrong targets
  for those queries.

### 2.3 The noise floor

The unsplit model is not perfectly reproducible either. At temperature 0, 1000
repeated completions of one prompt on a production-style vLLM server produced
**80 unique completions**; with batch-invariant kernels all 1000 were identical
[He 2025, "Experiments"] `[VERIFIED-BODY]`. Under BF16 greedy decoding, changing
batch size, GPU count or GPU version changed reasoning-model accuracy by up to
**9%** and response length by up to **9,000 tokens** [Yuan et al. 2025, abstract]
`[AUTHOR-CLAIM]`.

The operational definition is therefore: `[PROPOSED]`

> **Split depth `d` is utility-equivalent** if the per-query score disagreement
> between `SPLIT(d)` and the unsplit reference is **not larger than the
> disagreement between two unsplit runs** that differ only in incidental
> execution conditions (batch size, run, device placement), within a
> pre-registered margin.

This prevents E0 from failing a perfectly good split because of nondeterminism
that the unsplit "full" model also has.

---

## 3. Factor-by-factor analysis

For each factor: does it break equivalence, at which level, and what E0 must
record. "Exact" means the same bits arrive as were sent.

| # | Factor | Effect on equivalence | Breaks level | E0 must record |
|---|---|---|---|---|
| F1 | **Exact tensor transfer** (raw bytes, same dtype, same shape, same layout) | The transport is lossless. The downstream compute is identical *if* the server runs the same kernels on the same shapes. | none from transport | sha256 of the tensor before send and after receive |
| F2 | **Dtype upcast** at the cut (FP16/BF16 → FP32) | Lossless for the transmitted values. Downstream layers may then compute in a different precision than the unsplit run, which changes numerics. | E-L0 (possibly E-L1) | dtype on both sides, compute dtype of the server layers |
| F3 | **Dtype downcast or cross-cast** (FP32 → FP16/BF16; BF16 ↔ FP16) | **Lossy.** BF16 → FP16 can overflow or underflow, since FP16 has a narrower exponent range. FP16 → BF16 loses mantissa bits. FP32 → 16-bit loses precision. | E-L0, likely E-L1, possibly E-L2 | the cast, plus counts of overflow/inf/NaN |
| F4 | **Activation quantization** (INT8, 4-bit, per-tensor or per-channel) | **Lossy by construction.** SPINN sends 8-bit quantized activations [Laskaridis et al. 2020, §3.6], JALAD uses quantized activations, and BottleNet/BottleNet++ learn lossy bottlenecks (see `06` table). Accuracy loss was measured on CNNs in those papers; it is unknown for LLM hidden states and can be depth-dependent. | E-L0–E-L2 | scheme, bit-width, scale granularity, calibration data |
| F5 | **Lossless compression** (LZ4, zstd on raw bytes) | Lossless if decompression is verified. It changes bytes on the wire and CPU time, not values. SPINN applies LZ4 *after* 8-bit quantization, so its pipeline as a whole is still lossy. | none | codec, compressed and raw bytes, codec time |
| F6 | **Lossy compression or learned transforms** (bottleneck autoencoders, pruning, top-k sparsification, low-rank projection) | **Lossy.** | E-L0–E-L2 | transform definition and parameters |
| F7 | **Privacy transforms** (noise added to embeddings, as in Split-and-Denoise [Mai et al. 2024]) | **Lossy and stochastic by design.** SnD trades utility for privacy and reports only approximate utility. The manuscript cites SnD (L78), so a noise-adding path is plausible in the lab's design space. | E-L0–E-L3 | noise mechanism, privacy budget, seed |
| F8 | **Serialization** | `torch.save`/pickle, safetensors and raw buffers preserve bits. JSON/text float formatting may not round-trip unless shortest-round-trip formatting is used. Endianness mismatches are a silent risk across heterogeneous machines. | E-L0 if text-based | format, round-trip hash check (same as F1) |
| F9 | **Stochastic decoding** (temperature > 0, top-p) | The RNG state lives wherever sampling happens (normally the server). Split and unsplit runs cannot be compared token by token unless the seed and RNG call order are identical; only distributional equivalence (E-L3) is meaningful. | E-L1 (inapplicable) | decoding config, seed policy, `k` samples per query |
| F10 | **KV-cache handling** | In a pure layer split, layers `[0,d)` keep their KV cache on the edge and `[d,L)` on the server. Each decode step sends one new hidden-state row, so this is exact in exact arithmetic. It is **not exact** if the cache is quantized, truncated or evicted, recomputed under a different chunking, or if prefill is chunked differently from the reference. Attention is the hardest kernel to make batch-invariant [He 2025]. | E-L0 (more if the cache is quantized or evicted) | where each KV segment lives, cache dtype, prefill chunk size, eviction policy |
| F11 | **Kernel, batch and hardware differences** (edge GPU ≠ server GPU, different batch shapes, split-K matmuls, different attention kernels) | Floating-point addition is not associative, so a different reduction order gives a different result. Batch size, GPU count and GPU type change the reduction order [He 2025; Yuan et al. 2025]. A split adds a hardware boundary (edge RTX 3090 per L202, server GPU `[OPEN]`), so **some E-L0 divergence should be expected even with exact transfer**. With 4-bit weights (L295), dequantization kernels may also differ between the two GPUs. | E-L0, sometimes E-L1/E-L2 | GPU model, driver, CUDA, library versions and kernel backends on both sides; batch size |
| F12 | **Model-parallel or pipeline equivalence** | A layer split is pipeline partitioning across two hosts. It is mathematically the same function, so any differences come from F2–F11. | via F2–F11 | — |
| F13 | **Early exit** (stop computing at a layer `ℓ < L` when confident) | **Changes the semantics.** CALM explicitly lets early-exited outputs diverge from the full model's outputs within a tolerance δ, defined either as textual consistency `E[D(Y_early,Y_full)] ≤ δ` or as risk consistency [Schuster et al. 2022, §4, Defs. 1–2]. Skipped layers' states are approximated by copying [ibid. §3.3.1]. SPINN combines early exit with splitting [Laskaridis et al. 2020]. | E-L1 and above, by design | exit policy, thresholds, exit-layer histogram |
| F14 | **Partition-specific adaptation** (fine-tuned adapters or heads that exist only in the split model) | It is a different function and therefore a **different model** (Branch E). | all | adapter identity |

**Summary:** F1, F5, F8 (binary formats) and F12 preserve equivalence. F2, F10 and
F11 usually break only E-L0 and must be checked empirically against the noise
floor. F3, F4, F6 and F7 are lossy. F13 and F14 change the model.
`[PROPOSED]`, built on the cited sources.

---

## 4. Method branches

### 4.1 Branch X — exact split, or split within the noise floor (default)

**Condition:** E0 passes for depth `d` (§5.6).

```
R(q, s) = argmax_{a ∈ 𝒜}  [ Û_θ(M(a) | q)  −  λ · C(a | s) ]           (X)
```

* All `SPLIT(d)` actions share **one** utility output, `Û_θ(M_S|q)`.
* Depth affects only `C(a|s)`: edge compute for layers `[0,d)`, activation bytes
  `B(d, |q|)` divided by bandwidth, RTT, server compute for `[d,L)`, and decode-time
  per-step transfer.
* **Labels:** utility labels for `M_S` are collected once, from unsplit runs or
  from any single E0-validated depth. No per-depth label campaign is needed.
* **Adding a depth** `d_new` requires running E0 at `d_new` and profiling its
  cost. It does **not** require new utility labels or router training, provided
  E0 passes. This is the strongest honest form of the v2 "add an action cheaply"
  claim (RF-B), and it applies only to depths, not to new models. `[PROPOSED]`
* With deterministic greedy decoding, `argmax` over the split depths of `M_S`
  reduces to `argmin_d C(SPLIT(d)|s)`. The router's semantic decision is then
  "which model", and the depth choice is a pure systems decision. This
  decomposition is what makes Branch X clean (handed to `01`).

### 4.2 Branch L — lossy split

**Condition:** E0 fails for at least one depth because of F3, F4, F6 or F7 (a lossy
transform is present), and the failure exceeds the noise floor.

Three formulations, from cheapest to most expressive: `[PROPOSED]`

| Variant | Utility for `SPLIT(d)` | Extra supervision | When justified |
|---|---|---|---|
| **L1 — constant depth penalty** | `Û_θ(M_S\|q) − Δ̂(d)` | E0 calibration set only (score drop per depth, with a CI) | Degradation is roughly uniform across queries, so per-query flips are not concentrated in identifiable query types (§5.6 heterogeneity test) |
| **L2 — query-dependent penalty** | `Û_θ(M_S\|q) − Δ̂_φ(d,q)` with a small extra head `φ` | Labels at every lossy depth on a training subset | Degradation is concentrated: some query types break and others do not |
| **L3 — per-(M,d) heads** | `Û_θ(M_S,d\|q)`, one head per depth | Full labels at every depth (an m-fold labelling campaign) | Quality is strongly and non-monotonically depth-dependent, and L2 is insufficient |

* L1 keeps the model-level decomposition and adds a measured systems-side
  constant. It can be folded into the cost term as a quality penalty (or kept
  as a separate utility adjustment, preferred for interpretability).
* L3 is v2's original per-action design. It is justified **only** in this branch.
  BEST-Route is the published precedent: it uses one head per (model, best-of-n)
  action because `n` changes the output distribution (`05` §BEST-Route).
* Do not assume monotonicity in `d`. Hidden-state statistics vary by layer, so a
  fixed quantizer may hurt some depths more than others. This is `[OPEN]` for
  LLMs and is measured in E0.
* Lossy splits also give the cost side a second knob, such as the bit-width. Each
  `(d, bits)` pair is then a separate action, and the same E0 logic applies per
  pair.

### 4.3 Branch E — semantics-changing execution

**Condition:** early exit (F13), partition-specific adapters (F14), or any
transform for which the output is defined by a different function.

* Treat the action as running a **different model** `M' ≠ M_S`, with its own
  utility label `Û_θ(M'|q)`, exactly like adding a new model to the pool.
* Early exit with a per-token confidence threshold makes the effective model
  depend on the threshold. Each threshold setting is a distinct `M'`.
* **Conference scope:** out of scope unless Henry's code already does this. If it
  does, document it and treat it as Branch E. Do not hide it in Branch L.
  `[OPEN]`

### 4.4 Decision table

| Henry's code (`14`) | E0 outcome | Branch | Router outputs |
|---|---|---|---|
| raw same-dtype transfer, no early exit | pass at all depths | **X** | K model utilities |
| raw transfer, but different GPU/kernels | pass (within the floor) | **X** | K model utilities |
| raw transfer | fail beyond the floor, no lossy transform | investigate a bug first (dtype, chat template, cache, sampling seed); do not jump to Branch L | — |
| quantized or compressed or noised activations | pass | **X** (record the config as part of `M`) | K |
| quantized or compressed or noised activations | fail, uniform | **L1** | K + `Δ̂(d)` table |
| quantized or compressed or noised activations | fail, heterogeneous | **L2** (L3 if needed) | K + per-depth correction |
| early exit or adapters | — | **E** | K + 1 per distinct `M'` |

---

## 5. E0 — Split Equivalence Test (ready to run when Henry's code arrives)

This specification feeds `13-experiments-v3.md`. Everything below is a protocol.
**No result exists yet.** `[PROPOSED]`/`[OPEN]`

### 5.1 Inputs

* **Query set Q_E0:** a stratified sample from the routing training distribution,
  covering every task type and the length range used in E1–E8. Proposed size
  `n = 500`: at that size a disagreement rate of 1% has a 95% Wilson interval of
  roughly [0.4%, 2.3%], which is enough to detect flip rates of a few percent.
  Add a long-prompt subset (top 10% by length), because cache and attention
  effects scale with length.
* **Depths:** every depth `d` exposed by Henry's API (`14`), or a grid covering
  shallow, middle and deep cuts if the API allows many.
* **Configurations:** the exact deployment numerics, including 4-bit weights
  (L295), the activation dtype at the cut and any quantization or compression.
  Each configuration is a separate E0 cell.
* **Decoding:** (i) greedy decoding (primary); (ii) the deployment's sampling
  config, if it differs from greedy, with `k = 8` samples per query (secondary,
  for E-L3).

### 5.2 Reference runs (the noise floor)

| Run | Purpose |
|---|---|
| `R_A` | unsplit `M_S`, server GPU, batch size 1 |
| `R_B` | unsplit `M_S`, server GPU, deployment batch size (or a second run with a different batch composition) |
| `R_C` (if feasible) | unsplit `M_S` on the edge GPU type, batch size 1 (isolates the hardware effect) |
| `S_d` | `SPLIT(d)` for each depth `d`, batch size 1, deployment link |

Noise floor: the disagreement between `R_A` and `R_B` (and `R_A` vs `R_C`).
Split effect: the disagreement between `S_d` and `R_A`.

### 5.3 Measurements

**Transport level (per request)**

* sha256 of the activation tensor at the edge before serialization and at the
  server after deserialization: verifies F1/F5/F8.
* shape, dtype and byte count, both raw and on the wire. Check that measured raw
  bytes equal `shape × dtype size` (validates the cost model `B(d,|q|)` in `09`).

**Numerical level (first decode step plus a sample of later steps)**

* For the hidden state at the cut, after round-trip: max abs diff, relative L2,
  cosine similarity versus the reference, and the count of inf/NaN values.
* Final logits at step 1: max abs diff, KL(ref ‖ split), top-1 agreement and
  top-5 overlap.

**Token level (greedy)**

* Exact-sequence match rate.
* First-divergence position: its distribution, plus the share of divergences in
  the first 16 tokens, since early divergence cascades [Yuan et al. 2025].
* Length difference.

**Metric level (the decisive one)**

* Per-query score `S` from `08` for each run.
* Binary `S`: the 2×2 agreement table between `S_d` and `R_A`, the flip rate
  `f_d = P(S^d ≠ S^ref)`, and McNemar's test for directional asymmetry
  (split-worse vs split-better).
* Continuous `S`: the paired difference `S^d − S^ref`, with a bootstrap 95% CI of
  its mean and of the proportion with `|S^d − S^ref| > τ`.
* Equivalence is tested with **TOST** (two one-sided tests) on the mean paired
  difference, using margin `δ` (pre-registered, e.g. 1 accuracy point). A
  non-significant difference is **not** evidence of equivalence; only TOST is.

**Sampling level (if applicable)**

* Per-query success rates `p̂^d_q` and `p̂^ref_q` over `k` samples. Report the mean
  absolute difference and compare it to the same quantity between two reference
  sample batches.

**Heterogeneity (only needed when a depth fails)**

* Logistic regression of the flip indicator on task type, prompt length and
  output length. If the flips are predictable, use L2; if not, L1.

### 5.4 Configuration log (one record per cell)

Model spec `M` (§1.1); depth; activation dtype, quantization and compression;
serialization format; KV placement and dtype; prefill chunking; GPU, driver, CUDA,
torch and serving-library versions on both sides; batch size; decoding config and
seed; network link settings (they should not affect values, and E0 records them
to confirm that).

### 5.5 Pseudocode

```
for cfg in configs:                          # numerics/compression settings
  ref_A = run_unsplit(Q_E0, cfg, server, bs=1, greedy)
  ref_B = run_unsplit(Q_E0, cfg, server, bs=B_deploy, greedy)
  floor = disagreement(score(ref_A), score(ref_B))
  for d in depths:
    out_d = run_split(Q_E0, cfg, depth=d, bs=1, greedy, log_hashes=True)
    assert transport_hashes_match(out_d) or cfg.lossy_transport
    eff_d = disagreement(score(out_d), score(ref_A))
    tost_d = TOST(score(out_d) - score(ref_A), margin=δ)
    verdict[cfg, d] = PASS if (eff_d <= floor + ε and tost_d.equivalent) else FAIL
```

### 5.6 Pre-registered decision criteria

Thresholds are proposed here and must be frozen before E0 runs. The advisor
should confirm `δ` and `ε`. `[OPEN]`

* **PASS (Branch X) at depth `d`:** flip rate `f_d ≤ f_floor + ε` (proposed
  `ε = 1` percentage point) **and** TOST establishes `|E[S^d − S^ref]| < δ`
  (proposed `δ = 1` point).
* **FAIL:** either condition is violated. Apply §4.4: check for bugs first if the
  transport is lossless, then choose L1 or L2 using the heterogeneity test.
* **Report both** the E-L0/E-L1 statistics and the E-L2 verdict. Do not report
  "bit-exact" unless the hashes and logits actually match bitwise.
* The verdict applies per (configuration, depth). Do not extrapolate it to
  untested depths or numerics.

### 5.7 What E0 does **not** establish

* It does not establish that the split is lossless for queries outside Q_E0's
  distribution (domain shift is E8).
* It does not establish equivalence under a different serving stack or GPU, which
  needs a rerun.
* It establishes nothing about latency or bytes as costs. Those belong to E7.

---

## 6. Consequences for other deliverables

| File | Consequence |
|---|---|
| `01-model-vs-action-utility.md` | Branch X supports model-level `Û_θ(M\|q)`. Action-level heads are justified only by Branch L3 or Branch E. `M(a)` must include numerics (§1.1). |
| `08-utility-definition.md` | E0's metric-level test uses the same score `S` as the training labels, so `S` must be fixed before E0. |
| `09-cost-policy.md` | `C(SPLIT(d)\|s)` must include edge compute for `[0,d)`, prefill transfer `B(d,\|q\|)`, per-step decode transfer, RTT and server compute. Under L1, `Δ̂(d)` is a separate, reported quality term. It is not silently mixed into milliseconds. |
| `13-experiments-v3.md` | E0 runs **first**, before any label collection for `SPLIT`. E7 reuses E0's transport logs for byte accounting. |
| `14-henry-checklist.md` | Every row of §3 becomes a question to Henry: activation dtype, quantization and compression, serialization, KV placement, early exit, privacy noise, GPU types, kernel backends, and the seed and sampling location. |
| `proposed-solution-blue-v3.tex` | State the shared-utility design as conditional on an equivalence test. Cite [He 2025; Yuan et al. 2025] for nondeterminism and [Schuster et al. 2022] for early exit changing outputs. |

---

## 7. Manuscript wording

**Allowed** `[PROPOSED]`

* "When split execution reproduces the unsplit model's per-query task scores
  within its own run-to-run variation, all split depths of a model share a single
  utility estimate and differ only in system cost."
* "We verify this condition empirically for every deployed split depth and
  numerical configuration before training the router (E0)."
* "If activation quantization or compression degrades quality, we add a
  depth-specific quality penalty estimated on a held-out calibration set."
* "Floating-point non-associativity makes LLM outputs sensitive to batch size and
  hardware even without splitting [He 2025; Yuan et al. 2025]; we therefore
  define equivalence relative to this noise floor."

**Rejected** `[REJECT]`

* "Split inference is lossless, so `y(SPLIT(d),q) = y(full,q)`." (unconditional)
* "Split depth does not affect answer quality." (unconditional)
* "Split execution is bit-exact." (not measured, and unlikely across heterogeneous GPUs)
* "The split model's answer equals the strong/cloud model's answer." (only true if `M(SPLIT) = M(STRONG)` including numerics)

---

## 8. Sources used in this file

| Source | Identity | Inspection | Supports |
|---|---|---|---|
| He, H. & Thinking Machines Lab, "Defeating Nondeterminism in LLM Inference", *Connectionism* blog, 10 Sep 2025, thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference | technical blog (not peer-reviewed) | `[VERIFIED-BODY]` (sections on root cause, batch invariance, experiments, performance) | The lack of batch invariance as the main cause of temperature-0 nondeterminism; the RMSNorm/matmul/attention kernels; 80/1000 unique completions vs 1000/1000 identical (Qwen3-235B-A22B-Instruct-2507); a 26 s → 42–55 s slowdown. Cite as a blog/technical report and flag its status. |
| Yuan, J., Li, H., Ding, X., Xie, W., Li, Y.-J., Zhao, W., Wan, K., Shi, J., Hu, X., Liu, Z., "Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference" (v1 title: "Give Me FP32 or Give Me Death? Challenges and Solutions for Reproducible Reasoning"), arXiv 2506.09501 | NeurIPS 2025 oral per secondary sources; proceedings metadata not yet confirmed | `[VERIFIED-META]` (abstract) | Batch size, GPU count and GPU version change BF16 greedy outputs; up to 9% accuracy and 9,000-token length variation `[AUTHOR-CLAIM]`; LayerCast (BF16 weights, FP32 compute). Venue must be confirmed in `17` before it goes in the .bib. |
| Schuster, T., Fisch, A., Gupta, J., Dehghani, M., Bahri, D., Tran, V. Q., Tay, Y., Metzler, D., "Confident Adaptive Language Modeling", NeurIPS 2022, arXiv 2207.07061 | NeurIPS 2022 | `[VERIFIED-BODY]` for §3.3.1 and §4 (Defs. 1–2) only | Early-exit outputs may differ from the full model's within a tolerance δ (textual or risk consistency); skipped-layer states are copied |
| Laskaridis, S., Venieris, S. I., Almeida, M., Leontiadis, I., Lane, N. D., "SPINN: Synergistic Progressive Inference of Neural Networks over Device and Cloud", MobiCom 2020, 10.1145/3372224.3419194 | MobiCom 2020 | `[VERIFIED-BODY]` §3.2–3.6 (read in iteration 5, see `06`) | 8-bit quantization plus LZ4 of split activations; split combined with early exit |
| Mai, P., Yan, R., Huang, Z., Yang, Y., Pang, Y., "Split-and-Denoise: Protect Large Language Model Inference with Local Differential Privacy", ICML 2024 (PMLR 235), arXiv 2310.09130 | ICML 2024 | `[VERIFIED-META]` (abstract) | Client-side noise on transmitted embeddings, so utility is only approximate |
| JALAD, BottleNet, BottleNet++ | see `06` table | ABS/META | Examples of lossy activation transfer in DNN split computing |
| `source/main-original.tex` L76, L78, L202, L295 | the lab's manuscript (read-only) | read | "compress intermediate representations"; SnD citation; edge hardware; 4-bit quantization |

The claims that BF16/FP16 have different exponent and mantissa widths, and that
floating-point addition is not associative, are standard IEEE-754 / bfloat16
format facts. They need a citation only if the manuscript states them explicitly;
[He 2025] covers non-associativity in context.
