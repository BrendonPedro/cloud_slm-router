# 14 — Henry checklist: the Split-LLM code request and the decisions it unblocks

Status: `[OPEN]` throughout. This file contains **questions only**. No answer
about Henry's repository, model, API, numerics, network or hardware is known to
this sprint, and none is filled in here (brief §26, §30). The one hardware fact
quoted below comes from the manuscript itself (`source/main-original.tex` L202)
and is marked as such. It still needs Henry to confirm it is the machine his code
runs on.

Replaces `methods-v2/16-advisor-and-lab-open-questions.md` §2 (O4-1…O4-13).
`methods-v2` is unchanged. Inputs: `01` §1.1 (action→model cases C1/C2), `02`
§3–§5 (factors F1–F14, branches X/L/E, E0), `09` §2 (latency model, the two
derived consequences §2.3(a)/(b)), `10` §4/§7 (Split compatibility, pairs
P-A/P-B/P-H), `11` O-B3/O-B5/O-B6, `13` §9 (O-E5, O-E7, O-E8), `03` O-F2.

Tags: `[OPEN]` needs Henry · `[PROPOSED]` our design · `[MANUSCRIPT]` stated in
`main-original.tex`, not independently confirmed.

---

## 1. The message (send as-is, or trim)

> Hi Henry,
>
> We're building a query router that, for each request, chooses between running
> a small model on the edge, running a larger model split between edge and
> server at some layer d, or running that larger model fully on the server. To
> design it correctly we need to understand your Split-LLM code before we
> assume anything about it. Could you help with the points below? Short answers,
> or "don't know" / "not supported", are fine. The starred items block us; the
> rest can wait.
>
> **Access**
> 1. ★ Repository URL, and the licence or the lab's terms for using, modifying
>    and publishing results from it.
>
> **Model and split interface**
> 2. ★ Which model(s) does it run? Exact Hugging Face ID (and revision, if
>    pinned), and how the weights are quantized (the paper draft says 4-bit:
>    which method and settings?).
> 3. ★ How is the split layer d chosen: config file, launch argument or
>    per-request? Which depths are valid? Can the depth be changed without
>    restarting either side?
> 4. Can the same server run the same model *unsplit* (all layers on the
>    server), with the same weights and numerics? Is that a supported mode?
>
> **What crosses the network**
> 5. ★ What exactly is sent at the cut: only the hidden state, or also KV cache,
>    position ids, masks, per-layer inputs, token ids? Shape (as a function of
>    prompt length and d) and dtype?
> 6. ★ Is anything done to the activations before sending: dtype cast,
>    quantization, compression, added noise (e.g. a Split-N-Denoise-style
>    mechanism), or a learned transform?
> 7. ★ As far as you know, is the split output identical to unsplit inference
>    (same tokens under greedy decoding), approximately equal, or not checked?
>    Any early exit, adapters, or layers that exist only in the split version?
> 8. Serialization format (pickle / torch.save / safetensors / raw buffer /
>    protobuf / JSON) and transport (TCP socket, gRPC, HTTP, torch.distributed,
>    other)?
>
> **Decoding**
> 9. ★ During generation, what happens per output token: does the server send
>    each new token back to the edge, which runs layers [0,d) and sends one
>    hidden-state row, or is there batching, speculative or lookahead decoding
>    to avoid one round trip per token?
> 10. Where does sampling happen, which decoding settings are used (greedy or
>     temperature/top-p), and can the seed be fixed?
> 11. Where does each part of the KV cache live, what dtype is it, and is it
>     ever quantized, evicted or recomputed? Is prefill chunked?
>
> **Machines and software**
> 12. ★ Edge machine: is it the one in the draft (Xeon W-2123, 64 GB RAM,
>     2× RTX 3090 24 GB, Ubuntu 20.04.6)? Does your code use one GPU or both?
> 13. ★ Server machine: CPU, RAM, GPU model(s) and VRAM, OS. Is it a fixed
>     server or the serverless setup mentioned in the draft (cold starts)?
> 14. Software versions on both sides: Python, PyTorch, CUDA, driver,
>     transformers, and the inference engine if any (vLLM, TGI, llama.cpp,
>     plain transformers), plus the attention kernel/backend.
> 15. Is the edge-to-server link a LAN, a WAN, or the same host? Ports and
>     protocol?
>
> **Measurement and permissions**
> 16. Are there existing logs or hooks for TTFT, per-token time, bytes sent and
>     received, and GPU/CPU/memory use? If not, where would you put them?
> 17. ★ Do we get sudo (or a pre-configured setup) to shape the link with
>     `tc`/`netem` (delay, bandwidth, loss) on the edge or server interface?
> 18. Any way to read energy or power (nvidia-smi power draw, RAPL, an external
>     meter)?
> 19. Can the edge GPU also host a small router model (~100–400M parameters)
>     and, as an optional baseline, a ~7B model next to the edge SLM?
> 20. Do you have a load generator or a way to run concurrent requests against
>     the server?
>
> Thanks! Even partial answers let us start the equivalence check (split vs
> unsplit outputs) as soon as we can run the code.

The message deliberately does not propose a model, depth range or hardware,
so it cannot plant an answer.

---

## 2. Checklist with method dependencies

★ = blocking. "Decides" names the method choice that waits on the answer.
"If unanswered" is the conservative default the sprint uses until then.

### 2.1 Access and model

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H1 ★ | repository, licence | URL; licence or lab terms for modification and publication (#1) | Whether the code can be used, modified, released with the paper; whether a reproducibility artefact can include it | No Split result in any submission; `13` stage S cannot start |
| H2 ★ | supported model HF ID | Exact HF ID, revision, weight-quantization method and config (#2) | `M_S` and so the pool pair (`10` §7.2: P-A / P-B / P-H); `M` includes numerics (`02` §1.1), so the 4-bit config is part of the model identity; Split compatibility SC2 (`10` §6); server VRAM for SC6 | Keep P-A and P-B as candidates; do not label anything P-H |
| H3 | — | Is an unsplit run of the *same* specification supported on the server? (#4) | Case C1 (`REMOTE` = `SPLIT(0)`, K=2) vs C2 (K=3) in `01` §1.1; whether `REMOTE(M_S)` exists for `09` §2.3(b) and the open/private regimes (`10` O-P3); E0's reference run `R_A` (`02` §5.2) | E0 cannot run without an unsplit reference; we would need to build one from the same checkpoint and numerics |

### 2.2 Split interface

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H4 ★ | split-layer API | Static vs per-request depth; restart needed? (#3) | Whether `SPLIT_d` for several `d` are live runtime actions or deployment-time configurations. If depth is fixed at launch, the runtime action set is `{EDGE, SPLIT_{d*}, REMOTE}` and depth becomes a deployment parameter swept offline in E5/E7 | Treat depth as deployment-time; per-query depth choice is not claimed |
| H5 ★ | valid depths | Range and granularity of `d` (#3) | The set `D` in `01`/`02`; E0's depth grid (`02` §5.1); edge memory feasibility per `d` (`10` SC1) | E0 grid waits |
| H6 ★ | activation shape | Shape at the cut as a function of `n` and `d`; extra tensors (KV, per-layer inputs, ids, masks) (#5) | `B_pre(n)` and `b_dec` in `09` §2.2; prediction `09` §2.3(a) "bytes independent of depth" holds only for a residual-only cut on a dense decoder. Extra per-layer streams (e.g. Gemma-4 E-series, `10` §4.2) or KV migration make bytes depth-dependent | Use the residual-only formula as a hypothesis, tested by E7 check (a) |
| H7 ★ | activation dtype | Dtype on the wire and server compute dtype (#5, #14) | Factors F2/F3 (`02` §3): upcast vs downcast/cross-cast (BF16↔FP16 is lossy); bytes per value | Assume nothing; E0 records it |

### 2.3 Numerics and equivalence (decides model-level vs depth-level utility)

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H8 ★ | compression / quantization | Any cast, quantization, compression, noise or learned transform at the cut (#6) | Branch prior (`02` §4.4): none or lossless codec → expect Branch X; quantization/lossy/noise → E0 decides between X, L1, L2, L3; noise (F7) also makes outputs stochastic, so only E-L3 applies | E0 runs all configurations Henry exposes, each as a separate cell |
| H9 ★ | exact vs approximate split | Known equivalence; early exit; split-only adapters (#7) | Early exit or adapters → **Branch E**: the split is a different model `M'` with its own utility label (`01` Q5, `02` §4.3), and every exit threshold is a distinct `M'`. Henry's answer is a prior only: E0 is still required, because cross-GPU kernels (F11) can break equality even with exact transfer | Default to the shared utility (Branch X) only **after** E0 passes, never on Henry's word alone |
| H10 | serialization | Format and transport (#8) | F8: binary formats preserve bits, text formats may not; endianness across machines; wire-byte overhead over raw `shape × dtype` (`09`, E7 bytes raw vs on-wire) | E0 sha256 round-trip check settles it empirically |
| H11 | — (KV) | KV location, dtype, eviction, recompute, prefill chunking (#11) | F10: exact in exact arithmetic only without cache quantization/eviction/different chunking; also the KV bytes if the cache migrates | E0 logs it |
| H12 | — (decoding) | Sampling location, decoding config, seed control (#10) | F9: greedy → E0 compares token sequences (E-L1/E-L2); sampled → only distributional E-L3 with `k` samples; whether labels are single-run or S1-MS (`13` O-E6) | Greedy is the primary E0 setting (`02` §5.1) |

### 2.4 Message pattern and networking

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H13 ★ | networking (decode pattern) | Per-token round trip, or batched/speculative/lookahead decoding (#9) | **The most consequential systems answer.** With one round trip per token, TPOT(`SPLIT_d`) ≥ RTT and, in the exact branch, `SPLIT_d` is dominated by `REMOTE(M_S)` under a latency-only cost (`09` §2.3(b)); Split is then justified only in the private regime or with a priced server budget (C-2), and novelty candidate K9 can collapse (`12` §4.2.2). Lookahead-style schemes claim to amortise the round trip (Cunningham, arXiv 2602.16760, abstract-level) | Assume per-token round trip; E7 check (b) measures it |
| H14 | networking (link) | LAN/WAN/same host; protocol and ports (#15) | Whether `tc/netem` shaping is meaningful on that interface; baseline RTT and bandwidth before emulation; the E6 network grid (`13` O-E5, `11` O-B5) | E6 grid not fixed |
| H15 ★ | sudo, `tc/netem` | Permission to shape delay, bandwidth, loss (#17) | Whether E6 and E7 can vary `(RTT, BW)` on real hardware; otherwise E6 relies on trace-driven cost replay, which is allowed only after E-COST validates `L̂` (`13` E-COST) | E6 limited to trace-driven cells; say so in the paper |

### 2.5 Machines and software

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H16 ★ | edge machine | Confirm the manuscript's edge server (Xeon W-2123, 64 GB, 2× RTX 3090 24 GB, Ubuntu 20.04.6) `[MANUSCRIPT]` L202; one GPU or two (#12) | Edge feasibility SC1 for `M_E` plus the router plus layers `[0,d)` of `M_S` (`10` §9 weight bounds); whether an "edge" with 48 GB of GPU memory is representative of edge deployment (a limitation to state, not to hide) | Use L202 only as the manuscript's description; no edge latency number is assumed |
| H17 ★ | server machine, GPU models + VRAM | CPU, RAM, GPUs and VRAM, OS; fixed server vs serverless (#13) | Server VRAM for `M_S` (and `M_L` in case C2) at the chosen weight quantization, plus the E0 unsplit reference; whether cold-start `w_cold` is part of `C(a\|s)` (`09` §2.1); the manuscript's cloud-server sentence at L202 is unfinished | Pool pairs stay candidates (`10` O-P1) |
| H18 | software versions | Python, PyTorch, CUDA, driver, transformers, engine, attention backend (#14) | F11 kernel differences between edge and server; reproducibility record in E0/E7; whether hidden-state baselines (B-PFA, RouteLMT-style) can hook the edge SLM (`03` O-F2) | E0 records what it finds |
| H19 | — | Room on the edge GPU for the router (~100–400M) and optionally a ~7B LLM router baseline (#19) | Router overhead measurement on the real edge; feasibility of the prompted-LLM router baseline (`11` O-B6) | That baseline is reported as infeasible on the edge rather than run elsewhere silently |

### 2.6 Instrumentation

| ID | Brief §26 item | Question (msg #) | Decides | If unanswered |
|---|---|---|---|---|
| H20 | logging hooks | Existing TTFT, per-token, byte, resource logs (#16) | Where we instrument the serialization boundary for E0's sha256 and byte checks and E7's TTFT/TPOT/p50–p99/bytes/throughput | We add hooks at the send/receive boundary |
| H21 | — | Energy/power counters (#18) | Whether energy is reported in E7 at all (`13` O-E7); it is never estimated from TDP | Energy not reported |
| H22 | — | Load generator or concurrency support (#20) | E7 throughput at ≥ 2 concurrency levels; `w_queue(Q_srv)` profiling (`09` §2.2) | We write a simple closed-loop client |
| H23 | — | Can the edge stack reuse the `M_E` prefill after a routing decision? (follows from #11, #14) | Cost accounting for hidden-state self-routing B-PFA in E3 (`11` O-B3, `13` O-E8) | Charge the prefill as overhead |

---

## 3. Decision map: answer → method change

| Answer pattern | Consequence `[PROPOSED]` |
|---|---|
| Raw same-dtype transfer, no early exit, binary serialization (H7, H8, H9, H10) | Expect Branch X; still run E0. If E0 passes: one model-level utility `Û_θ(M_S\|q)`, depth affects only `C(a\|s)`, Split labels come from unsplit runs (`02` §4.1) |
| Any activation quantization, lossy compression or noise (H8) | E0 per (configuration, depth). Pass → Branch X with the config recorded in `M`; uniform fail → L1 `Δ̂(d)` table; heterogeneous fail → L2 (L3 only if L2 fails) |
| Early exit or split-only adapters (H9) | Branch E: new model `M'` per configuration; utility labels must be collected for `M'` |
| Same spec can run unsplit on the server (H3) | Case C1, K = 2 for the M0 pool; `REMOTE(M_S)` ≡ `SPLIT(0)` |
| Different spec for the strong cloud model (H2, H3) | Case C2, K = 3; Split still shares `M_S` utility across depths under Branch X |
| Depth fixed at launch (H4) | Runtime action set has one Split depth; the depth sweep is an offline deployment study, and per-query depth selection is not claimed |
| Extra per-layer streams or KV migration (H6) | Bytes depend on `d`; `09` §2.3(a) does not apply; E7 check (a) must model this |
| One round trip per token (H13) | Split dominated by Remote in the exact branch under latency-only cost; headline must use the private regime or a priced budget, or report the negative (`13` E7) |
| Batched / speculative / lookahead decoding (H13) | Redo `09` §2.3(b) for that pattern before E5/E7; if the scheme claims token identity, E0 still verifies it |
| No `tc/netem` (H15) | E6 trace-driven only, after E-COST; stated as a limitation |
| Model not open on the Hub, or licence forbids publication (H1, H2) | Split results cannot be released; the paper needs the advisor's decision on whether to proceed with a self-built split (§5) |

---

## 4. First actions after receiving the code `[PROPOSED]`

1. Read the licence (H1) before copying code anywhere.
2. Record the environment on both machines (H16–H18) in the E0 log header.
3. Run the unsplit reference twice (`R_A`, `R_B`) on a 20-query smoke set to
   measure the run-to-run floor (`02` §2.3).
4. Run one depth with sha256 hashing of the activation before send and after
   receive, and check raw bytes = `shape × dtype size` (`02` §5.3, transport).
5. Measure one generation's per-token timing to see the message pattern (H13)
   empirically, whatever the documentation says.
6. Then the full E0 (`13` E0) on `Q_E0`, every exposed depth and configuration.

Steps 3–5 are smoke checks. They are not E0 results and must not be reported as
such.

---

## 5. If the code is unavailable or unusable

`methods-v2/09` §6 proposed a minimal self-built single-model split
(layers `[0,d)` on the edge, `[d,L)` on the server, raw tensor transfer) as a
contingency. It remains a contingency only: `[OPEN]`, needs advisor approval,
and it would not be "Henry's Split-LLM" in the manuscript. It must still pass E0,
and the manuscript text would have to describe it as our implementation. It must
not be replaced by a cloud API, which would remove the activation-transfer cost
the method is about.

---

## 6. Changes relative to v2 (`methods-v2/16` §2)

| v2 | v3 |
|---|---|
| O4-6 "Is the split lossless?" treated Henry's answer as resolving losslessness | Henry's answer is a prior; only E0 decides (H9), because kernel/hardware differences (F11) and nondeterminism (`02` §2.3) exist even with exact transfer |
| O4-10 "runs on the L202 edge (2×RTX 3090) as-is?" | Kept as a confirmation question (H16), quoting L202 as `[MANUSCRIPT]`; the server is not inferred (the L202 cloud sentence is unfinished) |
| O4-12 decode transfer asked as a TPOT detail | Promoted to blocking (H13): it decides whether Split can ever beat Remote in the open regime (`09` §2.3(b)) |
| No question on unsplit mode of the same spec | Added H3 (case C1/C2, E0 reference) |
| No question on extra tensors at the cut | Added H6 (per-layer inputs, KV, ids), from `10` §4.2 |
| No question on sampling, seed, KV dtype, early exit, adapters, noise | Added H8, H9, H11, H12 (from `02` F7, F9, F10, F13, F14) |
| No energy, load-generator, router-memory or prefill-reuse questions | Added H19, H21, H22, H23 (from `13` O-E7/O-E8, `11` O-B3/O-B6) |

---

## 7. Hand-offs

| File | Use |
|---|---|
| `15-conference-vs-journal.md` | The conference core needs H1–H9, H13, H15–H17. Nothing here belongs to the journal extension. |
| `proposed-solution-blue-v3.tex` | Describe Split execution conditionally on H6–H9 and E0; do not state depth-independent bytes or one round trip per token as facts about Henry's system. |
| `FINAL-SUMMARY-v3.md` | Q25 ("What still requires Henry?") = the starred rows H1, H2, H4–H9, H13, H15–H17, plus H3. |

## 8. Open items

All rows H1–H23 are `[OPEN]` (owner: Henry, with the advisor for H1 and the §5
contingency). No experiment depending on them has been run.
