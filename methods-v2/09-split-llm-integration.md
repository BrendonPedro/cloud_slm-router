# 09 — Split-LLM Integration

*Deliverable for `MICROENCODER_KD_BRIEF.md` §12 (Split-LLM integration). This is a
**requirements / acquisition specification**, not a result and not an invented
interface. Its job is to state exactly what the proposed method needs from a real
Split-LLM implementation, produce a checklist to apply when Henry provides the
code, and mark every detail that is not yet known as `[OPEN]` rather than guess it.
Evidence tags per brief §23: `[VERIFIED]` primary source; `[RELATED]` adjacent;
`[PROPOSED]` our design; `[OPEN]` needs advisor/Henry/experiment. The original
manuscript is unmodified.*

> **Scope-lock.** Split-LLM enters the method only as the execution action
> `SPLIT(d)` inside the fixed action set `𝒜 = {EDGE_SLM, SPLIT(d), STRONG/CLOUD}`
> (`06 §2`). Nothing here changes `R(q)=argmax_{M_k} f_θ(q,M_k)` or the objective
> `max_R E_q[U − λC]`. The router does **not** perform the split; it *selects* a
> split depth and the Split-LLM runtime executes it. `[S:00; 06 §2]`

---

## 1. Why Split-LLM is load-bearing for this method (not an optional add-on)

Two already-locked decisions make the Split-LLM runtime the single most critical
external dependency of the whole method:

1. **The Split action's entire differentiation lives in the cost term.** `07 §3`
   fixed `y(SPLIT(d),q) = y(full model,q)` — a lossless split returns the *same
   answer quality* as running the full strong model, so the learned utility
   `Û_θ(a|q)` **cannot** distinguish `SPLIT(d)` from `STRONG/CLOUD`. The *only*
   thing that separates them is the measured communication/latency cost
   `c_comm(SPLIT(d),s)` = activation bytes at depth `d` ÷ bandwidth (+ RTT), and
   `c_lat`. `[S:07 §3; 08 §3]`

2. **Therefore `c_comm(SPLIT(d),s)` is the most load-bearing quantity in the
   method, and it is defined entirely by the split interface** — the activation
   tensor shape at the cut, its dtype/quantization, and the serialization. None of
   these can be invented; all come from Henry's code. `[S:08 §9 OPEN]`

Consequence: if the Split-LLM runtime cannot measure activation bytes and
TTFT/TPOT at a controllable depth, experiment **E7** (measured Edge vs Split) and
the **N4** novelty lane (genuine Split-LLM systems evaluation with measured
activation transfer) cannot be demonstrated, and the Split action collapses to an
un-measurable cloud call — the exact failure mode the brief §26 forbids ("do not
silently turn Split-LLM into a cloud API"). `[S:11 novelty; 12 E7]` `[OPEN]`

---

## 2. What the manuscript already fixes about Split-LLM

These are the only Split-LLM facts that are primary-sourced; everything else is
Henry-dependent and `[OPEN]`.

- **[VERIFIED, L75–76]** Definition: "a model can be divided into `S` total
  splits … allocating a minority of the model partitions (fewer than `S/2`) to the
  edge node allows the system to extract high-level features and compress
  intermediate representations before transmitting them over the WAN." → The split
  is a **layer-depth partition**: edge runs the first (minority) partitions, the
  server runs the rest. This fixes the *shape* of `SPLIT(d)` but not the layer
  index, tensor shape, or protocol.
- **[VERIFIED, L202]** Edge node runs "the client-side Split-LLM computation" on
  2 × RTX 3090 (24 GB). The cloud-server sentence is **literally unfinished** → the
  server side is undefined. `[OPEN]` (carried from `10` §0 / v1 methods/10 §0).
- **[VERIFIED, L211]** TTFT = "prompt processing on the edge device **+ activation
  transmission to the cloud +** server-side computation" — the paper's own TTFT
  decomposition *requires* the activation-transfer term, i.e. requires a real
  split, not a cloud API.
- **[VERIFIED, L213]** TPOT "includes computation and **communication** costs
  during distributed decoding" — implies per-token activation/KV exchange after the
  prefill cut, which is a non-trivial interface detail (`§4` row "decode-phase
  transfer").
- **[VERIFIED, L295]** All strong/split models deployed at **4-bit quantization**
  → the activation at the cut may also be quantized; byte accounting must state the
  activation dtype, which is `[OPEN]`.

**The advisor decision (brief §2 CONFIRMED #3) that "Henry has code that may be
reused" supersedes the v1 finding (methods/10 §6) that no lab Split-LLM codebase
was located.** This deliverable therefore shifts from "which split framework to
build" to "what to extract from Henry's code" — but the exact repository, model,
and interface remain `[OPEN]` per brief §2 UNRESOLVED and must not be invented.

---

## 3. What the method needs from the Split-LLM runtime (functional requirements)

Each requirement maps to a specific downstream consumer so the ask is justified,
not a wish-list.

| # | Requirement | Why the method needs it | Consumer |
|---|---|---|---|
| F1 | **Controllable split depth `d`** (choose the cut layer at run time or per config) | `SPLIT(d)` are distinct actions in `𝒜`; the router selects among depths; E6/E5 sweep depth | `06 §2`; `12 E5/E6` |
| F2 | **Activation-byte accounting at the cut** (exact bytes transmitted edge→server for a given `d`, dtype) | *is* `c_comm`; defines the entire Edge/Split/Strong separation | `08 §3`; `12 E7` |
| F3 | **TTFT measurement hooks** at the prefill/transmit/server boundaries | manuscript TTFT decomposition (L211); DV of E7 | `08`; `12 E7` |
| F4 | **TPOT measurement hooks** incl. decode-phase communication | manuscript TPOT (L213); DV of E7 | `08`; `12 E7` |
| F5 | **Split-quality equivalence check** — confirm `y(SPLIT(d),q) == y(full,q)` (lossless) or quantify the gap | `07 §3` assumed losslessness; if false, `Û_θ` must regain a per-depth quality term and the label campaign multiplies | `07 §3`; `12 E7` |
| F6 | **Edge-runtime + server-runtime partition** that runs on the L202 hardware (edge) and the (undefined) server | Stage-2 two-machine measurement | `10`; `12 E7` |
| F7 | **A controllable link** between the two runtimes compatible with `tc/netem` | E6 bandwidth/RTT sweep is the N4/N5 contribution | `10 §3.3`; `12 E6` |

Requirements that are **nice-to-have, not blocking**: batching (F-batch), on-the-fly
depth switching without reload (F-switch), KV-cache handling across the cut
(F-kv) — these affect throughput numbers (E7) but not whether the method runs.

---

## 4. Henry-code acquisition checklist (brief §12 — apply when the code arrives)

Fill the right column **only from the delivered code / Henry**, never by assumption.
Until filled, each row is `[OPEN]`. Rows are ordered blocker-first.

| Field (brief §12) | What to extract | Blocking? | Status |
|---|---|---|---|
| **Repository / license** | git URL, SPDX license, redistribution/fine-tune terms | ★ yes (license gates any use) | `[OPEN]` |
| **Model(s) supported** | exact HF model id(s) + param size; does it match the strong-model pool (`10`)? | ★ yes | `[OPEN]` |
| **Split-layer interface** | how the cut layer `d` is specified; valid range of `d`; static vs runtime | ★ yes (defines F1) | `[OPEN]` |
| **Client/server partition** | which layers run edge vs server; where the boundary code lives | ★ yes | `[OPEN]` |
| **Activation tensor shape** | shape at the cut as a function of `d` and prompt length (e.g. `[B, T, H]`) | ★ yes (defines `c_comm`) | `[OPEN]` |
| **Activation dtype / quantization at the cut** | fp16 / bf16 / int8 / 4-bit; is the activation compressed before transmit? (L75 "compress") | ★ yes (bytes = shape × dtype) | `[OPEN]` |
| **Activation transfer mechanism** | how the tensor is moved (socket / gRPC / torch.distributed / HTTP) | yes | `[OPEN]` |
| **Serialization** | pickle / safetensors / protobuf / raw; overhead vs raw bytes | yes (affects measured bytes) | `[OPEN]` |
| **Network protocol** | TCP/gRPC/custom; port(s); compatible with a `tc/netem`-shaped interface? | yes (defines F7) | `[OPEN]` |
| **Server runtime** | serving stack (vLLM / TGI / raw transformers); GPU/VRAM need at the server half | yes (sizes the undefined server, L202) | `[OPEN]` |
| **Edge runtime** | what runs on the RTX 3090 edge; VRAM for edge half + edge SLM co-resident | yes | `[OPEN]` |
| **Supported hardware** | CUDA/driver/torch versions; does it run on the L202 edge as-is? | yes | `[OPEN]` |
| **Logging hooks** | existing timestamps/counters, or do we add them? | yes (F3/F4/F2) | `[OPEN]` |
| **TTFT measurement** | is prefill→transmit→server-compute instrumented? (L211) | yes | `[OPEN]` |
| **TPOT measurement** | is decode-phase comm instrumented? (L213) | yes | `[OPEN]` |
| **Bytes transferred** | is there a byte counter, or add one at the serialization boundary? | ★ yes (= `c_comm`) | `[OPEN]` |
| **Split-depth control** | can `d` be set per request / per config without recompiling? | yes (E5/E6) | `[OPEN]` |
| **Batching** | does it batch requests across the link? affects throughput (E7) | no (nice-to-have) | `[OPEN]` |
| **Quantization** | does 4-bit (L295) work on the chosen model under this split? | yes (feasibility) | `[OPEN]` |

★ = cannot size Stage-2 hardware, write `c_comm`, or claim N4 until resolved.

---

## 5. How `SPLIT(d)` connects to the rest of the method (interfaces, not internals)

The router is **decoupled** from the split mechanism — it only needs the *cost
table*, which the Split-LLM runtime populates at run time:

```
          ROUTER SIDE (ours)                         SPLIT-LLM SIDE (Henry's)
  Û_θ(a|q)  ──┐                                   ┌── runs layers [0,d) on edge
              │   decision Eq.(4):                 │   serializes activation tensor
  live s ─────┤   a* = argmax_a[Û_θ − λ·Ĉ_a]  ──►  │   transmits bytes(d) over link
  (RTT, BW)   │                                    │   runs layers [d,L) on server
              │   Ĉ_a needs, per action a:         │   returns tokens
  c_comm(d) ◄─┴── bytes(d)/BW + RTT  ◄─────────────┘   logs: bytes(d), TTFT, TPOT
```

- **The router never touches activations.** It consumes `bytes(d)` (a measured
  scalar per depth, from F2) and live `s` (RTT, bandwidth) to form `c_comm`, then
  applies the SC1 weighted-scalar rule (`08 §4`). `[PROPOSED, S:08]`
- **`bytes(d)` is a structural quantity** (fixed by activation shape × dtype at
  depth `d`, independent of `s`), so it can be measured **once per depth** and
  cached; only `BW`/`RTT` are live. This keeps the inference path at one encoder
  pass + a table lookup. `[S:08 §2 structural/live split]` `[OPEN]` pending F2.
- **If F5 fails** (split is *not* lossless, e.g. because of activation
  quantization at the cut), then `07 §3`'s `y(SPLIT(d),q)=y(full,q)` breaks and
  `Û_θ` needs a per-depth quality head after all — a material change flagged here
  and routed to `07`/`12`. This is the single most important thing to verify
  empirically once Henry's code arrives. `[OPEN, S:07 §3]`

---

## 6. Minimal honest fallback if Henry's code is unavailable or incompatible

Per brief §26 ("do not invent Henry's code details") this is stated as a
*contingency*, not a plan of record, and reuses the v1 fallback (methods/10 §6
option 3):

- **[PROPOSED]** A minimal custom split — run layers `[0,d)` on the edge, serialize
  the hidden state, ship it over a `tc/netem`-shaped socket, run `[d,L)` on the
  server — is implementable by one student for a *single* open-weight model and
  gives honest activation-byte accounting (exactly the `c_comm` term). It is the
  fallback that preserves N4 if Henry's code does not materialize.
- **Risk:** without Henry's code this adds systems-engineering scope and a second
  source of measurement variance; it also must independently verify F5
  (losslessness) because a hand-rolled cut may introduce dtype rounding. `[OPEN]`
- **Do not** substitute a plain cloud API for the split in the fallback — that
  would forfeit the activation-transfer measurement and the N4 claim (brief §26).

---

## 7. Open items (carried to `16-advisor-and-lab-open-questions`)

All are brief §2 UNRESOLVED or §12 unknowns — flagged, never guessed:

1. `[OPEN]` **Exact Henry repository / license** — governs whether the code can be
   used, modified, and published at all.
2. `[OPEN]` **Which model(s)** Henry's split supports, and whether they intersect
   the strong-model pool (`10`); determines server VRAM (the undefined L202 half).
3. `[OPEN]` **Split-layer interface + valid depth range** — defines the actions
   `SPLIT(d)` the router can even offer.
4. `[OPEN]` **Activation tensor shape + dtype/quantization at the cut** — defines
   `c_comm`, the quantity the whole Edge/Split/Strong separation rests on.
5. `[OPEN]` **Losslessness (F5)** — does `y(SPLIT(d),q)=y(full,q)` hold under this
   code? If not, `07`/`06` need a per-depth quality term.
6. `[OPEN]` **Server hardware** (L202 unfinished sentence) and **controllable-link
   permissions** (`tc/netem`, two-machine, `sudo`) — Stage-2 blockers from `10`.
7. `[OPEN]` **Decode-phase transfer model** — does the split exchange activations
   per decode token (affecting TPOT, L213), or only at prefill?

---

## 8. Hand-offs

- **← from `07 §3`:** inherits the `y(SPLIT(d),q)=y(full,q)` losslessness
  assumption that F5 must verify against Henry's actual cut.
- **← from `08 §3/§9`:** inherits the obligation to supply `c_comm(SPLIT(d),s)` =
  `bytes(d)/BW + RTT`; this file specifies that `bytes(d)` comes from F2 and is
  structural (cache-once).
- **→ `06 §2`:** confirms the `SPLIT(d)` action semantics (edge `[0,d)`, transfer,
  server `[d,L)`) match the manuscript's layer-partition definition (L75–76); the
  enabled depth set stays `[OPEN]`.
- **→ `10-model-pool-and-baselines`:** the strong-model pool must intersect the
  model(s) Henry's split supports (checklist row 2); "Always-Split" is a baseline
  that needs this runtime.
- **→ `12-conference-experiment-plan`:** E7 (measured Edge vs Split: TTFT, TPOT,
  activation bytes, e2e p50/p95/p99) and E6 (route change under bandwidth/RTT) are
  the experiments that consume F2–F4/F7; both are blocked on the §7 open items.
- **→ `16-advisor-and-lab-open-questions`:** all §7 items plus the Henry checklist
  (§4) become the Split-LLM block of the advisor/lab question set.
- **→ `proposed-solution-blue.tex`:** the Split-LLM integration paragraph describes
  `SPLIT(d)` and the activation-transfer cost in prose, with no measured numbers
  (brief §20/§26).
