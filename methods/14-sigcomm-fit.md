# 14 — SIGCOMM Fit for the Original Project

Scope: assess whether the **original** paper ("Tiny-LM with Jacobi-Forced
Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs")
can be a defensible ACM SIGCOMM submission **without changing the research
question**. This document does not select a method; it states what the venue
requires of *any* method chosen in `02-candidate-methods.md`, and where the
project risks reading as an ML-classification paper.

Every claim about SIGCOMM below is tagged VERIFIED (primary source, dated),
UNANNOUNCED (not yet published for 2027), or PROPOSED (our design inference).
Per brief §5/§20, nothing about 2027 dates, page limits, or requirements is
invented.

---

## 1. Confirmed current SIGCOMM 2027 information [VERIFIED]

From the official conference site
`https://conferences.sigcomm.org/sigcomm/2027/` (fetched 2026-09-28):

- **Event:** ACM SIGCOMM 2027, the 41st edition of the series. [VERIFIED]
- **Dates:** **August 8–12, 2027.** [VERIFIED]
- **Location:** **Queen Sirikit National Convention Center, Bangkok,
  Thailand.** [VERIFIED]
- **Site status:** first version of the website went live **July 2026**; a
  Main-Track CFP shell exists (abstract registration mentioned) but all
  deadlines are marked **TBA**. [VERIFIED]

## 2. What is NOT yet announced for 2027 [UNANNOUNCED]

The 2027 site does **not** yet publish any of the following, so we do not rely
on or invent them:

- submission / abstract-registration deadlines;
- page limits and formatting;
- artifact-evaluation rules;
- review model specifics;
- the 2027 topic list;
- acceptance criteria.

**Action:** monitor the 2027 site; re-verify before the abstract deadline.
Until then, orientation below is taken from the most recent *published* CFP
(SIGCOMM 2026), used only to understand the conference's networked-systems
character — not as a promise about 2027.

## 3. SIGCOMM's orientation, from the most recent published CFP (2026) [VERIFIED]

Primary sources, fetched 2026-09-28:
- CFP: `https://conferences.sigcomm.org/sigcomm/2026/cfp/`
- Submission instructions:
  `https://conferences.sigcomm.org/sigcomm/2026/submission/`

Verified facts about SIGCOMM 2026 (used only as orientation for a networked-
systems venue; **2027 may differ**):

| Item | 2026 fact | Source |
|---|---|---|
| Scope | "significant research contributions or significant deployment experiences in communication **networks and networked systems**"; explicitly all lifecycle phases, performance, robustness, energy | CFP |
| Tracks | **Research** and **Experience** (deployment insights others cannot replicate); surveys/tutorials excluded | CFP |
| Page limit | **up to 12 pages** two-column 10-pt body, figures/tables included; unlimited references + optional appendices (PC not obliged to read appendices) | Submission |
| Review | **Double-blind**; anonymize authors, affiliations, funding, self-cites in third person, no identity-revealing repo links; rebuttal for papers reaching discussion | Submission / CFP |
| Artifacts | **Artifact Evaluation is voluntary, no influence on acceptance, but "strongly encouraged"**; badges awarded | CFP |
| Integrity | `.bbl` file required to validate references / prevent hallucinated citations; mandatory **ethics** statement; ORCID; disclosure of generative-AI tool use | CFP |

The single most load-bearing phrase for us: SIGCOMM wants **networked systems**,
and its own tracks reward either novel networked-systems research *or* real
deployment experience. A router whose contribution is measured only in
classification accuracy sits outside both.

## 4. Why THIS project can be a networked-systems project [PROPOSED, grounded in the manuscript]

The original problem is not "classify queries." It is: an **edge** router
decides, per query, whether to answer on a local SLM or **transmit
computation to a Split-LLM server over a network**, maximizing
`E_q[U(R(q),q) − λ·C(R(q),q)]`. The cost term `C` in the manuscript already
includes **communication, latency, and resource use** — i.e. `C` is a *network*
quantity, not an ML quantity. That makes the routing decision a control knob
over an edge/cloud communication system:

1. **The action space crosses the network.** A `SPLIT` decision sends
   intermediate activations edge→server; the byte volume, TTFT, TPOT, and
   end-to-end latency of that path are all network-observable and network-
   sensitive (they change with bandwidth/RTT/contention). This is the N1
   novelty axis from `03-method-comparison.md`.
2. **`λ` and system state `s` are run-time knobs, not weights.** Per
   `07-system-cost-integration.md`, the S2 design (learn `U`, combine with
   *measured* `C(s)` outside the network) lets the same trained router change
   its route distribution as bandwidth/RTT/load change. That "reacts to the
   live network" behaviour is a systems result, not a classifier metric.
3. **The dependent variables are SIGCOMM metrics.** Per
   `08-experiment-design.md` §6.2: TTFT, TPOT, e2e p50/p95/p99, transmitted
   activation bytes, throughput, tail latency under contention, energy,
   operational cost.

Mapping back to the fixed formulation (brief §2): the router still computes
`R(q)=argmax_k f_θ(q,M_k)` and still optimizes `U − λC`. SIGCOMM relevance
comes from *measuring the U−λC trade-off as a network effect*, not from
redefining the objective.

## 5. Which parts risk looking like "only an ML paper" [PROPOSED — reviewer-risk analysis]

| Risk | Why it reads as ML-only | Mitigation (no change to research question) |
|---|---|---|
| **R-ML-1: accuracy-only evaluation** | Reporting routing accuracy / AUC on SimpleQA/LLMRouterBench and stopping there | Make the *headline* claim a system claim (latency/bytes/cost at matched quality); accuracy becomes a mechanism plot, not the result |
| **R-ML-2: no real network** | All numbers from a cost *model*, no measured link | Stage-2 testbed with tc/netem sweep (`10-lab-requirements.md`); measure bytes/TTFT on a real 2-machine link |
| **R-ML-3: static conditions** | One fixed bandwidth/RTT | Sweep `s`; show route distribution and e2e latency *move* with the network (S2 design) |
| **R-ML-4: Split-LLM is a stub** | "cloud path" = one API call, no activation transfer | Implement a genuine split with activation-transfer byte accounting and split-depth; the transfer *is* the network contribution |
| **R-ML-5: no systems baseline** | Compared only to RouteLLM/Arch-Router etc. | Add system baselines (§6 below); show query-awareness beats a systems-only rule (H3) |
| **R-ML-6: novelty is the encoder** | "we picked ModernBERT" | Per `03`, architecture is *not* the novelty; frame novelty as the split-aware action space (N1) and/or calibration-under-shift (N2) |

R-ML-2 and R-ML-4 are the two that most often sink an ML-flavoured paper at a
networking venue; both are Stage-2 (testbed) items and both are advisor/lab-
gated (see `10`, `11`).

## 6. Required networking baselines [PROPOSED, per brief §12]

Beyond the ML routers (RouteLLM, Arch-Router, RouteLLMT/RouterBench, ICL-Router
— see `02`/`08`), a SIGCOMM evaluation needs **systems baselines** so the
learned router is shown to add value *over policies a network engineer would
already deploy*:

- **Always-Edge** and **Always-Split** (endpoints of the trade-off);
- **Random** and **dataset-prior** (sanity floors);
- **Lowest-estimated-latency path** (greedy on measured `C`);
- **Bandwidth-threshold** policy (split only if BW > τ);
- **RTT-threshold** policy (edge only if RTT > τ);
- **Cost-minimizing rule** (argmin measured `C`, ignore `U`);
- **System-state-only scheduler** (no query features at all) — this is the
  direct H3 competitor;
- **Oracle upper bound** (labels known) — headroom, not a baseline to beat.

The decisive comparison for the venue is **learned router vs. system-state-only
scheduler at matched quality**: if query-awareness cannot beat a network rule,
the ML component is not earning its place (H3, `08`).

## 7. Required system measurements [VERIFIED metric list from 08 §6.2; PROPOSED targets]

Measured on the Stage-2 testbed, per query and aggregated:

- **Latency:** TTFT, TPOT, end-to-end p50/p95/p99.
- **Communication:** transmitted activation bytes/query; total bytes on the
  edge↔server link; bytes vs. always-split at fixed split depth.
- **Throughput:** requests/s, tokens/s at the server under load.
- **Resource:** GPU/CPU utilization (edge and server), memory, energy/power via
  `nvidia-smi` if the lab permits (advisor Q, `11`).
- **Network conditions (IV):** bandwidth, RTT, contention, packet loss (tc/netem).
- **Operational cost:** modelled `C` per route from measured bytes + compute +
  (if API path exists) price.

Each headline claim is pre-registered as IV→DV with a falsifier in
`08-experiment-design.md` §7 and enumerated per-cell in
`15-sigcomm-experiment-matrix.md`.

## 8. Reproducibility expectations [VERIFIED from 2026; treated as guidance, not a 2027 promise]

Inferred only from the SIGCOMM 2026 CFP (2027 rules UNANNOUNCED):

- **Artifact Evaluation is voluntary but "strongly encouraged," badges
  awarded, and does not affect acceptance.** We should *plan* for artifact
  submission from the start (reproducible label pipeline, testbed scripts,
  tc/netem configs, seeds) because it is cheap if designed in and expensive to
  retrofit. See `16-next-week-action-plan.md` "reproducibility setup."
- **Double-blind** submission: no identity-revealing repo links in the paper;
  use an anonymized artifact. [VERIFIED 2026]
- **`.bbl` submission** to validate references — a concrete anti-hallucination
  check we already satisfy by keeping primary-source citations
  (`01-method-landscape.md`). [VERIFIED 2026]
- **Ethics statement, ORCID, GenAI-use disclosure** required. Our data
  pipeline uses public benchmarks + self-generated model outputs; the ethics
  statement is straightforward (no human subjects, no PII), but the split-depth
  **privacy-leakage** analysis (N1) is worth surfacing in the ethics section.
  [VERIFIED 2026 requirement; PROPOSED content]

**We do NOT claim any of these are 2027 requirements.** Re-verify against the
2027 CFP when published.

## 9. Potential reviewer concerns [PROPOSED — anticipated, per brief §22 Pass C]

1. *"This is a query classifier with a latency plot bolted on."* → §5 R-ML-1/2/3.
2. *"The Split-LLM path isn't real; bytes come from a formula."* → R-ML-4;
   Stage-2 real transfer.
3. *"A simple bandwidth/RTT threshold does just as well."* → H3, §6 systems
   baselines; if true, the paper must report it honestly (falsifier fired).
4. *"Gains vanish once the network varies."* → sweep `s`; S2 design is built to
   show gains *because* the network varies.
5. *"Router overhead eats the savings."* → measure router latency/memory on the
   edge device and net it out (routing-overhead measurement, `08`/`18`).
6. *"Why Jacobi? The name isn't justified."* → `04-jacobi-role.md`: only J1
   (edge-generator speedup) is defensible; Jacobi is an *ablation*, not the
   contribution, so a skeptical reviewer cannot sink the core claim on it.
7. *"Only tested on one model pool."* → pool is an advisor decision (`11`);
   plan ≥1 nested and ≥1 complementary pool (LLMRouterBench headroom finding).

## 10. How to address concerns WITHOUT changing the research question [PROPOSED]

- Keep `R(q)=argmax f_θ` and `U − λC` verbatim as the framing; every
  mitigation above is an *evaluation* or *engineering* choice, not a redefinition.
- Lead the paper with the **system** claim (latency/bytes/cost at matched
  quality under varying network), and present routing accuracy as the mechanism
  that produces it — the ordering signals "networked system," not "classifier."
- Make the **network the independent variable** (sweep bandwidth/RTT/contention)
  so the router's value is expressed as network-adaptivity — the property a
  pure ML classifier structurally cannot claim.
- Treat Jacobi as an optional edge-generator accelerator (ablation), so the
  contribution stands even if the advisor drops the Jacobi framing.
- Plan artifacts and double-blind hygiene from day one (§8), matching the
  venue's stated values without any research-question change.

---

### Summary

SIGCOMM 2027 is **confirmed** (Bangkok, Aug 8–12, 2027) but its detailed CFP is
**not yet published**; orientation is drawn from the verified SIGCOMM 2026 CFP.
The original project *is* a networked-systems project because its cost term and
its `SPLIT` action are network quantities — provided the evaluation (i) uses a
real testbed with real activation transfer, (ii) makes the network the
independent variable, and (iii) beats a system-state-only baseline at matched
quality. Those are evaluation requirements, not changes to the research
question. The concrete per-condition plan is `15-sigcomm-experiment-matrix.md`;
the hardware to run it is `10-lab-requirements.md`.

**We make no claim that this project will be accepted by SIGCOMM.**

### Sources (fetched 2026-09-28)
- ACM SIGCOMM 2027: https://conferences.sigcomm.org/sigcomm/2027/
- ACM SIGCOMM 2026 CFP: https://conferences.sigcomm.org/sigcomm/2026/cfp/
- ACM SIGCOMM 2026 submission instructions:
  https://conferences.sigcomm.org/sigcomm/2026/submission/
