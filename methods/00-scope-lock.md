# methods/00 — Scope lock

*Written for the method-selection sprint (see `METHOD_BRIEF.md`). Iteration 1.*
*Authoritative source: `source/main-original.tex` (SHA-256 `06f5f9d7…1707cf6`,*
*re-verified unmodified this iteration). This document restates what is fixed by*
*the original paper and what the advisor has left open. It does not choose a*
*method. Every claim about the source is traceable to `research/problem-as-written.md`*
*(deliverable 1 of the earlier sprint), abbreviated **[d1]** below, with line*
*numbers `L<n>` into the source.*

---

## 1. The original paper's problem (fixed)

For each incoming query `q` at an **edge device**, a lightweight router chooses
between answering **locally with an edge SLM** and **offloading** (fully, or
partially through a **Split-LLM**) to a larger cloud model. The choice is made
by a small learned router **on the edge**, and it should maximise expected
answer quality minus a λ-weighted system cost [d1 §2.2; L137–189].

This is a **capability-routing** decision (which model will answer *this* query
well enough), not a semantic-intent decision. The label depends on how the pool
models behave on `q`, and it is not recoverable from the query text alone
[research/jev-system-one.md §5; research/architecture options §0.2].

## 2. Original objective (fixed)

| Eq. | Source | Content |
|---|---|---|
| (1) | L141–143 | `R : Q → M`, a routing function |
| (2) | L170–172 | `max_R E_q[ U(R(q),q) − λ·C(R(q),q) ]` |
| (3) | L187–189 | `R(q) = argmax_{M_k∈M} f_θ(q, M_k)` |

- `U(M_k,q)` = expected response quality/utility of `M_k` on `q` (L124, L164).
- `C(M_k,q)` = cost of `M_k` on `q`; "may include computation, communication,
  and latency" (L165).
- `λ` = utility-vs-cost trade-off weight (L126).
- `f_θ` = a lightweight scoring function ("TLM-based", L128–130, L185–191).

**Every viable candidate method in this sprint must map explicitly to Eq. (3)
and Eq. (2).** Deliverable `methods/02` records that mapping per candidate.

## 3. Original architecture (fixed roles)

Three roles, from L147–159:

```
   ┌─────────────── EDGE DEVICE ───────────────┐        ┌──── CLOUD ────┐
   │  edge SLM(s)  +  routing module (TLM)      │  WAN   │  LLM /        │
   │  the router runs HERE, before data leaves  │◀──────▶│  Split-LLM    │
   └────────────────────────────────────────────┘        └───────────────┘
```

- **Edge device**: hosts one or more lightweight SLMs (L150).
- **Cloud server**: hosts powerful LLMs or Split-LLMs (L151).
- **Routing module (the TLM)**: deployed **at the edge**, selects the inference
  path (L152). Per-query actions: answer locally with an SLM, **or** offload
  "`q` (or part of it, in Split-LLM settings)" to the cloud (L155–159).

## 4. Original constraints (fixed requirements)

From L176–183, restated as the four requirements the METHOD_BRIEF enumerates:

- **A. Lightweight** — minimal latency and compute overhead, edge-deployable
  (L179).
- **B. Query understanding** — capture query complexity, intent, uncertainty
  (L180).
- **C. System awareness** — reflect communication overhead, memory limits,
  response latency (L181).
- **D. Adaptability** — generalise across queries and remain effective as the
  model pool evolves (L182). **Not preserved automatically**: the METHOD_BRIEF
  and `research/gap-assessment.md` require each candidate to *prove* whether it
  can add models cheaply. Prior art already claims "no retraining" (CSCR, HyDRA,
  ICL-Router, Arch-Router) [research/closest-prior-art.md §4 item 4], so this is
  a requirement to satisfy, not a contribution to assert.

## 5. What is FIXED (do not change)

1. The research question: on-edge routing between edge SLM and cloud
   LLM/Split-LLM (§1).
2. The objective `U − λC` and the argmax-of-`f_θ` form (§2).
3. The three architectural roles, with the **router on the edge** (§3).
4. The four requirements A–D (§4).
5. The Split-LLM as a member of the action space (L137, L155–159).
6. The intent to evaluate latency / cost / communication (Section IV metrics,
   L207–265).
7. The manuscript's model-pool *intent* (edge SLMs + strong Split-LLMs,
   L267–303) and its baseline *intent* (RouteLMT, ICL-Router, RouteLLM,
   Arch-Router, L305–320). Exact model names are subject to the claim audit but
   the *category* is fixed.

## 6. What the advisor has left OPEN (we may choose)

The advisor is flexible on **method / approach**, and the source leaves the
method entirely undefined:

- **The Proposed Solution section (L193–195) is a single `.`** [d1 §7]. There is
  no architecture, loss, label definition, training procedure, Jacobi mechanism
  or encoder anywhere in the body.
- The title phrase **"Jacobi-Forced Micro-Encoder" is never defined** in the
  body and has no established meaning in the literature
  [research/jacobi-forcing.md §9; research/micro-encoder-investigation.md §1].
  Its intended role is an **open advisor question**, not something we may
  invent as established (see `methods/04`).

Therefore the following are ours to *propose* (subject to advisor approval):

- **What `f_θ` actually is**: generative TLM, discriminative encoder, self-routing
  SLM probe, or structured multi-head model (candidates in `methods/02`).
- The **training target** (binary / multiclass / utility regression / pairwise
  gain / direct `U−λC` / separated `Û` and measured `C`) — `methods/06`.
- **How system state enters** the decision (S1–S4) — `methods/07`.
- The **model-addition mechanism** for requirement D — per candidate in
  `methods/02` and `methods/09`.
- The **role, if any, of Jacobi Forcing** — analysed in `methods/04`; the only
  technically coherent placement is on the *edge generator*, not the router.

## 7. Boundaries the METHOD_BRIEF sets on us

We must **not** turn this into another project: not a generic cloud/edge
scheduler, not a network-scheduling paper, not a calibration-only or OOD-only
paper, not a standalone Jacobi paper, not a Jev replication, not a benchmark
paper, not a split-point-placement paper. Supporting ideas from those areas may
be **incorporated** only insofar as they help implement Eq. (2)/(3). We must
not modify `source/main-original.tex` or `paper/main-revised.tex`, must not run
large training or GPU experiments, and must not invent results.

## 8. Venue note (context, not a change to the problem)

The advisor now targets **ACM SIGCOMM 2027**. This does not change the fixed
problem. It does raise the evaluation bar: the eventual system evaluation must
show a **networked-systems** effect (communication volume, RTT/bandwidth
sensitivity, TTFT/TPOT, tail latency, throughput, load), not only router
classification accuracy. Each candidate's SIGCOMM relevance is recorded in
`methods/02`, `methods/14` and `methods/15`. SIGCOMM 2027 CFP facts are gathered
in `methods/14` and must not be invented.

---

## 9. Scope-lock checklist — "Would this proposed method still be the original paper?"

Apply to every candidate in `methods/02`. A candidate passes only if **all**
boxes are ✓.

- [ ] Decides **per query**, at the **edge**, **before** committing to a path.
- [ ] Chooses among {edge SLM, Split-LLM, cloud LLM} — the Split-LLM path is a
      real member of the action space, not dropped.
- [ ] Implements `R(q) = argmax_{M_k} f_θ(q, M_k)` (or a monotone
      reparametrisation, e.g. a thresholded utility) — the mapping is written out.
- [ ] Optimises `U − λC` with `U` a defined quality metric and `C` a scalar cost
      with stated units; λ is adjustable.
- [ ] The router is **lightweight** and edge-resident (requirement A).
- [ ] Captures query difficulty/uncertainty (requirement B).
- [ ] Can reflect communication / compute / latency cost (requirement C).
- [ ] States honestly whether/how it adapts to new models (requirement D) — no
      unearned "no-retraining" claim.
- [ ] Does **not** silently become a scheduler, a benchmark, a calibration-only
      study, or a Jacobi/Jev paper (§7).
- [ ] Preserves the original privacy/edge motivation: the routing decision is
      made on-device before data leaves.

This checklist is re-applied in the final contrarian review (Reviewer Pass A,
`methods/FINAL-SUMMARY.md`).
