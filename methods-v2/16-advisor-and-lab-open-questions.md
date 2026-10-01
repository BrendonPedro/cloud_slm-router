# 16 — Advisor & Lab Open Questions

*Deliverable for `MICROENCODER_KD_BRIEF.md` §2 (UNRESOLVED / DO NOT GUESS),
answering FINAL-SUMMARY questions **14** (hardware/software still unknown) and
**15** (what must be asked of Henry). This is the sprint's single **question
register**: every `[OPEN]` item flagged in `00`–`15` is collected here, each
tagged with its **owner** (advisor / Henry / experiment / manuscript) and the
**downstream deliverable it blocks**. Nothing here is answered or guessed — per
brief §26 the sprint invents no hardware names, no Henry-code details, and no
final model pool. The original manuscript is unmodified.*

Evidence tags (brief §23): `[VERIFIED]` primary source · `[RELATED]` adjacent ·
`[PROPOSED]` our design · `[OPEN]` needs advisor/Henry/experiment ·
`[UNSUPPORTED]` do not use.

> **How to use this file.** Items are grouped by **owner** because that is how
> they get resolved: the advisor block is the agenda for the next meeting; the
> Henry block is the message to send Henry (= `09 §4` checklist in question
> form); the experiment block is resolved by Stage-0/1/2 work in `12`, not by
> asking anyone; the manuscript block is a correction to carry when the blue
> text is eventually merged. An item is **closed** only when its right-hand
> "resolves to" is filled from a primary/authoritative source, never by
> assumption.

---

## 0. Why these are open and not decided

The brief fixes the research problem and the advisor fixed the *method family*
(micro-encoder + investigate-KD + journal-only-CL), but eight classes of fact
were explicitly left **UNRESOLVED** at the 2026-10-01 meeting (brief §2), and
the sprint's own design work surfaced further unknowns that only an experiment
or Henry's code can settle. Recording them as open questions — rather than
filling them with plausible guesses — is a hard constraint (brief §26) and is
what lets the conference-core design in `06` stay honest: every quantity the
method depends on is either `[VERIFIED]` from the manuscript, `[PROPOSED]` by
us, or listed below as `[OPEN]`.

The eight brief §2 UNRESOLVED items are carried as **O1–O8** (same numbering as
`00 §3`). Sprint-surfaced unknowns are numbered within each owner block.

---

## 1. ADVISOR questions (agenda for the next meeting)

These require a human decision or a disambiguation of the 2026-10-01 notes. The
sprint has prepared the *options* for each; the advisor picks.

| # | Question | Why it matters / what the sprint prepared | Blocks | Source |
|---|---|---|---|---|
| **O6-a** | **What is the final model pool?** The sprint proposes *selection criteria* (MP1–MP8), not a pool. | `10 §5` gives 8 criteria + a minimal **N=2** conference-core recommendation; the AR/diffusion zoo is pushed to ablation. Advisor confirms members. | `07`, `10`, `12` | `10 §5`; brief §13 |
| **O6-b** | **Replace the non-existent `Qwen3-72B-Instruct`** with a real strong model: Qwen2.5-72B-Instruct / Qwen3-32B / Qwen3-235B-A22B? | The manuscript names a checkpoint that **does not exist** (`[VERIFIED]` via claim-audit). This is a correction, not a new choice — but which real model is the advisor's call. | `07`, `10`, `12` | `10` row S1; `research/claim-audit.md` |
| **O-label-route** | **Route P-A vs Route P-B for labels.** P-A = run our own inference on the manuscript pool; P-B = adopt LLMRouterBench's flagship pool. | **Mutually exclusive.** P-B gives free labels but **destroys the edge/Split identity** of the paper (none of the manuscript pool has SimpleQA records in LLMRouterBench — only flagship API models do). Sprint recommends **P-A**. | `07`, `10`, `12` | `10 §3`; `02` |
| **O-pool-size** | **Collapse the conference core to N=2?** (one edge-class + one strong-class model, zoo → ablation) | Because `y(SPLIT(d),q)=y(full,q)`, the learned-utility quality axis is ~binary, so a large pool inflates labelling cost without adding routing signal. | `07`, `10`, `12` | `10 §4`; `08 §3` |
| **O7** | **What did the B1 / SLM-choice / "possible Gemma model" discussion decide?** The student's handwritten notes are incomplete. | Cannot be reconstructed without the advisor. The sprint does **not** guess a Gemma variant (and the "-A4B" suffix in the manuscript is invalid). | `10` | brief §2; `10` |
| **O8** | **Conference-vs-journal submission ordering: Plan A (serial) or Plan B (parallel)?** | `14` presents **both** plans fully (benefits/risks/overlap/firewall). The sprint deliberately does **not** pick; ordering is an advisor call. Also approve the contribution firewall + near-zero-cost CL hooks. | `13`, `14` | `14 §4`; brief §19 |
| **O-novelty-ok** | **Are the two surviving novelty lanes (N2 calibration-preserving KD, N4 measured Split activation cost) the agreed contribution?** | `11` rejects 3 claims and keeps N2+N4 as the only standalone-defensible axes, all experiment-gated. Advisor confirms this is the paper's thesis before writing. | `11`, `12`, blue-tex | `11 §4` |
| **O-kd-drop** | **If experiment E1 shows KD does not beat the α=1 non-distilled control, do we drop KD and reframe?** | Brief stop-cond #4 explicitly permits rejecting KD with evidence. The whole KD story is **conditional on E1**; the advisor should pre-agree the fallback framing (N4 Split-systems paper without KD). | `03`, `11`, `12` | `03 §6`; `12` E1 |
| **O5** | **Are `tc/netem` bandwidth/RTT shaping and `sudo`/two-machine use permitted** on the lab testbed? | E6 (route change under bandwidth/RTT) and the N4/N5 systems contribution are impossible without a controllable link. Permissions, not just hardware. | `12` E6/E7 | brief §2; `09` F7 |

---

## 2. HENRY questions (the Split-LLM code acquisition message)

This is the `09 §4` checklist restated as the message to send Henry. **Every row
is `[OPEN]`; none may be invented** (brief §26). Ordered blocker-first — the ★
rows gate whether `c_comm` can be written and whether the N4 lane and experiment
E7 are possible at all. Advisor CONFIRMED #3 says this code exists; its contents
do not.

| # | Ask Henry | Blocking? | Resolves | Blocks |
|---|---|---|---|---|
| **O4-1** | **Repository URL + license** (SPDX; redistribution / fine-tune / publish terms) | ★ | whether the code can be used/modified/published at all | everything Split |
| **O4-2** | **Which model(s)** does the split support (exact HF id + param size)? Do they intersect the strong-model pool (O6-a)? | ★ | server VRAM sizing (the undefined L202 server half); pool compatibility | `10`, `12` E7 |
| **O4-3** | **Split-layer interface + valid depth range** — how is cut layer `d` set (static vs per-request)? | ★ | the set of `SPLIT(d)` actions the router can offer (F1) | `06 §2`, `12` E5/E6 |
| **O4-4** | **Activation tensor shape at the cut** as a function of `d` and prompt length (e.g. `[B,T,H]`) | ★ | the byte count that *is* `c_comm` | `08 §3`, `12` E7 |
| **O4-5** | **Activation dtype / quantization at the cut** (fp16 / bf16 / int8 / 4-bit; compressed before transmit?) | ★ | `bytes = shape × dtype`; interacts with L295 4-bit | `08`, `12` E7 |
| **O4-6** | **Is the split lossless?** Does `y(SPLIT(d),q) == y(full,q)` hold, or is there a quality gap? (F5) | ★ | whether `07 §3` holds or `Û_θ` needs a per-depth quality head | `06`, `07`, `12` E7 |
| **O4-7** | **Activation transfer mechanism** (socket / gRPC / torch.distributed / HTTP) + **serialization** (pickle / safetensors / protobuf / raw) | yes | measured-byte overhead vs raw tensor bytes | `12` E7 |
| **O4-8** | **Network protocol + ports**; is it compatible with a `tc/netem`-shaped link? | yes | F7, hence E6 | `12` E6 |
| **O4-9** | **Server runtime** (vLLM / TGI / raw transformers) + **edge runtime**; GPU/VRAM at each half on the L202 hardware | yes | sizes the undefined server (O2); two-machine feasibility | `10`, `12` E7 |
| **O4-10** | **Supported CUDA/driver/torch versions** — runs on the L202 edge (2×RTX 3090) as-is? | yes | Stage-2 feasibility | `12` |
| **O4-11** | **Existing logging hooks** for TTFT / TPOT / bytes transferred, or do we add them at the serialization boundary? | yes (F2/F3/F4) | DV instrumentation for E7 | `12` E7 |
| **O4-12** | **Decode-phase transfer model** — does it exchange activations/KV *per decode token* (affects TPOT, L213) or only at prefill? | yes | TPOT accounting | `12` E7 |
| **O4-13** | **Does 4-bit quantization (L295) work** on the chosen model under this split? Batching across the link? | yes (feasibility) / no (nice-to-have) | throughput numbers | `12` E7 |

**Fallback (contingency only, not a plan):** if Henry's code is unavailable or
incompatible, `09 §6` specifies a minimal custom single-model split that still
gives honest activation-byte accounting. It must **not** be replaced by a cloud
API (brief §26), and it independently re-opens O4-6 (losslessness). `[PROPOSED]`

---

## 3. HARDWARE / SOFTWARE still unknown (FINAL-SUMMARY Q14)

Hardware facts the manuscript partially fixes and partially leaves undefined.
These are advisor/lab facts, not guesses.

| # | Unknown | What IS known (`[VERIFIED]`) | What is `[OPEN]` | Owner |
|---|---|---|---|---|
| **O1** | Exact **edge GPU** model | L202: edge testbed = Xeon W-2123, 64 GB RAM, **2×RTX 3090 24 GB**, Ubuntu 20.04.6 | whether "edge GPU" = the RTX 3090s or a separate smaller edge device; the manuscript's edge is a workstation, not a phone/Jetson | advisor/lab |
| **O2** | Exact **server / cloud GPU** model | L202 sentence is **literally unfinished** ("…equipped with…") — the server half is undefined | the entire server spec; sized only once O4-2/O4-9 fix the split model's VRAM need | advisor/lab |
| **O3** | Exact **machine names** | two-machine use "appears available" (advisor D5) | hostnames / addressing for the two-machine Stage-2 testbed | lab |
| **O5** | **Link-shaping permissions** | — | `tc/netem`, `sudo`, two-machine networking allowed? (duplicated in §1 because it is both an advisor permission and a lab fact) | advisor/lab |

> The edge spec (2×RTX 3090 workstation) means "edge deployment" in this paper is
> a **workstation-class edge**, not a mobile/embedded one. The N6 edge-deployment
> novelty claim must be scoped to that hardware and **not** overstated as
> phone/Jetson deployment unless such hardware is actually added (`[OPEN]`, →
> `11 §N6`, `12` E7). The `05` ONNX/INT8 CPU-latency evidence is `[RELATED]`
> (published, not measured by us) and must not be presented as measured on the
> lab edge until Stage-2.

---

## 4. EXPERIMENT-resolved open items (no one to ask — run Stage 0/1/2)

These are not questions for a person; they are resolved by the `12` experiment
plan and must not be assumed one way or the other in the prose.

| # | Open empirical question | Resolved by | Risk if assumed |
|---|---|---|---|
| **OE-1** | Does distillation beat the α=1 **non-distilled** control? | E1 (Stage 0/1) | the entire KD contribution; brief stop-cond #4 permits dropping KD |
| **OE-2** | Does KD preserve **calibration** (ECE/Brier) better than non-distilled-student **+ post-hoc temperature scaling**? | E4 | N2 collapses if temperature scaling matches it for free |
| **OE-3** | Is the per-query **oracle headroom** over always-cloud non-trivial for the chosen pool? | E2/E8 label analysis | a degenerate pool makes routing pointless (MP2) |
| **OE-4** | Do **diffusion vs AR** SLMs have a distinct per-query win profile (justifies architectural diversity, MP8)? | E8 | an undifferentiated zoo inflates labelling cost with no routing signal |
| **OE-5** | Effect of **4-bit quantization** on quality labels (published scores are BF16) | E17/label QA | labels mis-rank models if measured at a different precision than deployed |
| **OE-6** | Does the measured **Split** path actually beat Edge/Strong on the quality-latency-comm frontier? | E7 (needs Henry code + O4-*) | N4 is the systems contribution most at risk |
| **OE-7** | **Losslessness (F5)** under Henry's actual cut | E7 pre-check | if false, `06`/`07` need a per-depth quality head (also O4-6) |

---

## 5. MANUSCRIPT corrections to carry (not modifications — merge-time notes)

These are `[VERIFIED]` errors in `source/main-original.tex` found by the v1 claim
audit. The sprint **does not touch the manuscript** (brief §20/§26); these are
recorded so the blue text in `proposed-solution-blue.tex` does not inherit them
and so they can be fixed by the authors when the Proposed Solution is merged.

| # | Location | Issue | Corrective action (author's, not sprint's) |
|---|---|---|---|
| **OM-1** | model pool | `Qwen3-72B-Instruct` does not exist | replace with a real strong model (O6-b) |
| **OM-2** | model pool | Gemma **"-A4B"** suffix is invalid; E2B ≈ 5.12B stored | use the correct Gemma variant/name (pending O7) |
| **OM-3** | L202 | server-hardware sentence is unfinished ("…equipped with…") | complete once O2 is known |
| **OM-4** | pool/labels | claims SimpleQA evaluation via LLMRouterBench pre-computed results, but the named pool has **no** SimpleQA records there | resolve via O-label-route (P-A vs P-B) |
| **OM-5** | citations | missing citations for Hybrid-LLM / ConsRoute / HyDRA / CSCR noted in v1 audit | add when the related-work paragraph is updated (`01`, `17`) |

---

## 6. Open-item roll-up by blocking severity

**★ Hard blockers — the N4 systems contribution and experiment E7 cannot exist
until these are resolved:** O4-1…O4-6 (Henry code: license, model, depth
interface, activation shape, activation dtype, losslessness), O2 (server
hardware), O5 (link permissions).

**Design-shaping — change the labelling campaign or the pool, must be settled
before Stage-1 labelling spends compute:** O6-a/O6-b (pool), O-label-route
(P-A/P-B), O-pool-size (N=2 collapse), OE-5 (4-bit label precision).

**Framing — settle before writing the final blue prose, not before experiments:**
O-novelty-ok (N2+N4 is the thesis), O-kd-drop (E1 fallback), O8 (submission
ordering), O7 (Gemma/B1 note reconstruction).

**Self-resolving via `12`:** OE-1…OE-7 — recorded so nothing is assumed, resolved
by running the plan, not by asking.

---

## 7. Hand-offs

- **← from `00 §3`:** inherits O1–O8 (brief §2 UNRESOLVED) verbatim; this file is
  their consolidated register with owners attached.
- **← from `09 §4/§7`:** the Henry checklist becomes §2 (O4-1…O4-13).
- **← from `10 §9`:** O10-1…O10-7 become O6-a/O6-b, O-label-route, O-pool-size,
  OE-4, OE-5, O4-2.
- **← from `11`/`14`:** O-novelty-ok, O-kd-drop, O8 (framing/ordering).
- **→ `FINAL-SUMMARY.md`:** this file answers FINAL-SUMMARY Q14 (hardware/software
  unknown = §3) and Q15 (what to ask Henry = §2); Q19 (claims still needing
  advisor approval) = §1 O-novelty-ok/O-kd-drop.
- **→ `proposed-solution-blue.tex`:** every quantity the blue prose cites must be
  `[VERIFIED]` or `[PROPOSED]`; anything on this register stays out of the prose
  or is written as an explicit assumption, never as a measured/decided fact.
- **→ the next meeting / the message to Henry:** §1 is the meeting agenda; §2 is
  the Henry message; neither is to be pre-filled with guesses (brief §26).
