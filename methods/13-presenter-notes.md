# 13 — Presenter Notes (plain-English speaking notes)

*Speaking notes for presenting `12-method-proposal.md` to the advisor. Written for
a Master's student who knows software engineering / CS but is new to LLM-routing
research. Read the jargon boxes once before the meeting. Nothing here is a result —
every method is a **plan**, and the goal of the meeting is a **decision**, not a
demo. Timings are rough targets, not a script to read verbatim.*

`source/main-original.tex` and `paper/main-revised.tex` are unchanged (verified).

---

## Jargon you must be comfortable saying out loud

- **Router / `f_θ`.** A small model that looks at a query and decides *which* AI
  model or path should answer it. `θ` = its trainable weights. `f_θ(q, M_k)` = a
  score for using model `M_k` on query `q`. We pick the highest-scoring option.
- **`U − λC`.** Utility (answer quality) minus λ times cost (compute /
  network / latency / money). `λ` is a dial: high λ = "be cheap," low λ = "be
  good." The router maximises this.
- **Edge SLM.** A small language model running on the local/edge device.
- **Split-LLM.** A big model split across two machines: the first layers run at
  the edge, then intermediate **activations** are sent over the network to a server
  that finishes the computation. The bytes sent = "activation-transfer volume."
- **TTFT / TPOT.** Time-To-First-Token / Time-Per-Output-Token — standard latency
  metrics for text generation.
- **Calibration.** Whether a model's confidence numbers are trustworthy (if it
  says "70% sure," is it right ~70% of the time?).
- **Jacobi Forcing.** A published training trick that speeds up *text generation*
  by letting a model refine several future tokens in parallel instead of strictly
  one-at-a-time.

---

## 60 seconds — the original problem

"Imagine a phone or edge device that can answer easy questions locally with a small
model, but hard questions need a big model in the cloud — or a 'split' model where
the edge does part of the work and sends intermediate data to a server. Sending
everything to the cloud is slow and expensive; doing everything locally gives worse
answers. So we need a tiny, fast **router** on the edge that looks at each incoming
query and decides: answer here, or escalate — and if escalate, over what path. The
paper writes this as picking the option that maximises **quality minus a
cost penalty**, `U − λC`. That routing function is the whole paper. The research
direction is fixed; we're not changing it."

## 30 seconds — why the method is still undecided

"The manuscript says the router is a 'lightweight TLM-based scoring mechanism' but
the *Proposed Solution* section is empty — it never says what the router actually
**is** or how to build it. That's the gap I researched. There are several
defensible ways to build it, and picking one is genuinely a trade-off, not an
obvious call — so I want your steer rather than guessing. I looked at the method
options and did **not** run any experiments; this is a planning sprint."

## 60 seconds each — the three candidates

**A — Tiny generative LM router.** "A small (<2B) language model reads the query
and literally *writes out* the decision. It matches the paper's title 'Tiny
Language Model' most literally, and there's a released model we can use as a
baseline. Downside: it's the heaviest and slowest option to run on the edge, and in
the one published head-to-head it was actually *slower and less accurate* than a
lighter probe. So I'd treat it as a **baseline / fidelity anchor**, not the
headline method."

**B — Lightweight micro-encoder.** "A small encoder — think a mini-BERT, 20–150M
parameters — scores each option in a single fast pass. This is the safe, low-risk
choice: the code exists, it trains on one GPU or even CPU, and calibration is
standard. The honest catch is it's **not novel by itself**, and it needs a second
model living on the edge alongside the SLM. It's the floor everything else must
beat."

**C — Self-routing edge SLM (+ D policy layer).** "Instead of a separate router,
the edge SLM routes *for itself*: a tiny probe reads the model's internal state
after it reads the query and predicts whether the local model will succeed. It
reuses work already done, so it's cheap when the query stays local. On top of C (or
B) we can add **D**, a policy layer with typed outputs — including a
**privacy/sensitivity** signal. D is the most interesting for a networking venue
because privacy → how deep we split the model → how many bytes cross the network,
which is a real systems trade-off, not just a classification score. It's also the
highest-risk one, because a 2026 paper (PRISM) already does privacy-aware routing,
so D only counts as new if our split path is a *real* layer-split with *measured*
data leakage."

## Pros / cons in one breath each

- **A:** most faithful to the title; heaviest and slowest — baseline role.
- **B:** lowest risk, reproducible; not novel alone, needs a 2nd edge model.
- **C:** cheap, reuses computation; probe must be retrained if the edge model
  changes.
- **D (on C/B):** biggest networking payoff via privacy→split→bytes; overlaps
  PRISM and needs a sensitivity-label dataset we don't have yet.

**The one-line takeaway:** "No option is novel on its *architecture* alone. The
real decision is **which novelty angle to pursue** — a genuine Split-LLM action
with measured network cost, or calibration under domain shift on edge hardware —
and the architecture follows from that."

## The Jacobi issue — say this clearly

"The title says 'Jacobi-Forced Micro-Encoder.' I checked the primary Jacobi Forcing
paper and its code. **There is no established method by that name**, and a literal
reading doesn't type-check: Jacobi Forcing speeds up *generation*, but an encoder
doesn't generate. The only place 'Jacobi' fits technically is on the **edge
generator** (making the local model produce text faster), not on the router. I did
**not** delete Jacobi from the paper — I turned it into a precise question for you:
what did you intend its role to be?"

## Likely professor questions → simple answers

- **"Isn't this just a classifier?"** → "That's exactly the SIGCOMM risk. It stays
  a networking result only if we measure real system effects — bytes transferred,
  TTFT, tail latency — and show the route mix *changes as network conditions
  change*. That last point is only winnable if we keep cost measured at run time,
  outside the learned model (our S2 design)."
- **"Why not just always use the cloud / a fixed rule?"** → "That's baseline H3.
  We test whether query-aware routing beats a systems-only rule; if it doesn't, we
  report that honestly."
- **"What's actually new?"** → "Not the architecture — those all exist. Either the
  Split-LLM action with measured leakage/bytes, or calibration under domain shift.
  I need your call on which." 
- **"How much will this cost to run?"** → "Stage 0 is free (CPU, reuses released
  data) and can already kill the idea if a learned router doesn't beat simple
  baselines. Only what survives goes to GPU (Stage 1) and the testbed (Stage 2)."
- **"Can it handle new models without retraining?"** → "Depends on the candidate —
  I did *not* assume the paper's 'no-retraining' claim; for each option I noted
  whether adding a model needs a full retrain or just a new profile/head."

## What hardware is needed (say plainly)

"Three tiers. **Stage 0 needs nothing** — my laptop, reusing released scores.
**Stage 1 needs one GPU** to regenerate labels for the real model pool. **Stage 2
needs two machines and a controllable network** (Linux tc/netem) plus a real
Split-LLM stack — that's the part I need the lab for. Two gaps block Stage 2: the
manuscript's **cloud-server spec is literally cut off mid-sentence**, and **no
Split-LLM framework is named**. I need those from you, plus which GPUs I can
reserve and whether I can get two machines and sudo for network shaping."

## What I plan to do after your approval

"Immediately, without waiting for the lab: run **Stage 0** on released data to test
whether a learned router even beats simple baselines (H1) and whether the
generative model is worth its cost over a cheaper encoder (H2). In parallel I'll
prepare environments and baseline code. I will **not** start GPU labelling or the
testbed until you confirm the novelty axis, the Split-LLM framework, the cloud
hardware, and the model pool. Full step lists are in `16-next-week-action-plan.md`
and the per-candidate roadmaps in `09`."

## Meeting close — the ask

"So the four decisions I need from you today: (1) which novelty axis — Split-action
or calibration-under-shift; (2) what Jacobi was meant to do; (3) the cloud hardware
and Split-LLM framework; (4) the concrete model pool. Everything else is ready to
instantiate once those are set."
