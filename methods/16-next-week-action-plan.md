# 16 — What I should do between now and the advisor decision

*Practical action plan for the week(s) between now and the advisor meeting where
the method / novelty axis is chosen. This is a **planning** document: nothing here
trains a large model, runs a GPU experiment, or generates a result — all of that
waits for method approval and lab access (brief §16, §18). It synthesises
deliverables 08 (staging), 09 (roadmaps), 10 (lab tiers), 11 (advisor questions),
12 (proposal). `source/main-original.tex` is unchanged (SHA-256 `06f5f9d7…1707cf6`,
re-verified this iteration); `paper/main-revised.tex` is unchanged.*

Evidence tags: **[S: …]** sourced in a cited deliverable · **[O]** our analysis ·
**[P]** design proposal · **[E]** untested expectation.

The three buckets below map onto the staged experiment plan: the CAN-DO-NOW bucket
is everything that feeds **Stage 0** (CPU, released data), which can falsify H1/H2
*before* any lab spend [S: 08 §0]. WAIT-FOR-ADVISOR is every decision that gates
architecture and Stages 1–2. AFTER-LAB-ACCESS is the first concrete implementation
steps once the method and hardware are settled.

---

## A. CAN DO NOW — WITHOUT LAB, WITHOUT ADVISOR SIGN-OFF

These require only a laptop/CPU and public artefacts. None of them commits to a
candidate, so they are safe no matter which novelty axis the advisor picks. They
are ordered so the cheapest, most decision-relevant work comes first.

### A.1 Literature reading (close the remaining primary-source gaps)
- [ ] Read **Mix-or-Split / any prior "collaborative Split-LLM routing" work**
  end-to-end. This is the single unread paper that could pre-empt novelty axis
  **N1** (the Split-LLM action space); confirming what it does or does not cover
  is the highest-value reading task [S: 03 §3, 11 Q5]. **[O]**
- [ ] Read **PRISM (AAAI 2026)** in full — it already does privacy-aware 3-way
  routing, so it bounds what "D as a policy layer" can claim as new [S: 03 §2]. **[O]**
- [ ] Re-read the **Jacobi Forcing** primary paper (arXiv:2512.14681 / ICML 2026)
  and its official repo to lock the ESTABLISHED/PROPOSED boundary for the advisor
  Jacobi question [S: 04-jacobi-role]. **[O]**
- [ ] Skim the released baselines' papers+code (RouteLLM, RouterDC, Arch-Router,
  ICL-Router, RouteLMT) to confirm exact routing mechanism and code availability
  before proposing to reproduce them [S: 12 §3–4, brief §12]. **[O]**

### A.2 Codebase / artefact inspection (no downloads of large checkpoints)
- [ ] Inspect the **LLMRouterBench release**: confirm which per-(model,query)
  quality scores it actually ships, its schema, licence, and — critically — that
  it does **not** contain the manuscript's real intended pool (this is why Stage 1
  exists) [S: 08 §0, §2]. **[O]**
- [ ] Pull only **tiny config/metadata files** (not weights) for candidate edge
  SLMs and encoders to verify parameter counts, context length, and licence
  against the "lightweight edge" requirement [S: 10, brief §Purpose "tiny
  metadata/config only"]. **[O]**
- [ ] Inventory this repo's earlier sprint outputs (`research/`, `architecture/`,
  `experiments/`) that Stage 0 code will reuse, so nothing is re-derived. **[O]**

### A.3 Dataset preparation (Stage 0 inputs only)
- [ ] Download the **released LLMRouterBench / SimpleQA-style score tables** (small
  text/JSON, CPU-scale) and build the leakage-controlled train/val/test splits and
  the domain-shift (OOD) split defined in `08` — *this can be finished with no GPU*
  [S: 08 §0, §8]. **[P]**
- [ ] Implement the **quality-scoring / label-construction functions** for every
  training target (binary, utility-regression, pairwise-gain, direct U−λC,
  separated). All targets derive from the one per-(model,query) score table, so
  building them now makes the A-vs-B-vs-C-vs-D comparison nearly free later
  [S: 06, notes it4]. **[P]**

### A.4 Baseline + candidate code planning (skeletons, not training runs)
- [ ] Write the **simple-baseline harness**: Always-Edge, Always-Strong/Split,
  Random, dataset-prior, TF-IDF+logistic-regression, and the **oracle upper bound**
  — all CPU-runnable on the released scores; these define the H1 bar [S: 08 §5]. **[P]**
- [ ] Stub the **learned-router interfaces** so B (encoder), C-pre (prefill probe),
  C-post (first-k confidence), and A (generative) share one `f_θ(q, M_k)` →
  `argmax Û − λ·C` API. Building the interface now avoids committing to a candidate
  [S: 09, 12 §3–5]. **[P]**
- [ ] Draft the **cost table `C(a, s)` (S2 design)** as a pure run-time function of
  measured state `s` (RTT, bandwidth, activation bytes, prompt/split-depth), kept
  *outside* the network so λ and network state stay knobs — this is the piece that
  later produces the SIGCOMM route-mix-vs-bandwidth curve [S: 07 §S2, 15 C4]. **[P]**

### A.5 Environment & reproducibility setup
- [ ] Pin a **reproducible environment** (Python, PyTorch, Transformers versions;
  lockfile) and a **5-seed harness + paired significance tests** so Stage 0 results
  are trustworthy [S: 08 §8]. **[P]**
- [ ] Prepare a **`.bbl`-clean bibliography** discipline now (every cited work
  primary-source verified), matching the SIGCOMM 2026 anti-hallucinated-citation
  rule used as orientation [S: 14 §1]. **[O]**
- [ ] Draft `tc`/`netem` config *files* and a bytes/RTT logging plan on paper so
  the network testbed is turnkey the moment two machines exist — no network to
  control yet, just the scripts [S: 10, 15]. **[P]**

**What A can conclude before the advisor meeting:** a Stage-0 read on **H1**
(does *any* learned router beat the simple baselines + oracle gap?) and **H2**
(does generative A beat a cheaper encoder/probe enough to justify its cost?),
computed on released data on CPU. If Stage 0 already falsifies H1 or H2, that is
decision-changing information to bring to the advisor [S: 08 §0]. **[E]**

---

## B. WAIT FOR ADVISOR — do NOT decide these unilaterally

Each blocks a specific downstream deliverable/stage; the four ★ are the gating
blockers from `11`.

- [ ] ★ **Novelty axis: N1 (genuine Split-LLM action + measured leakage/bytes) vs
  N2 (calibration under domain shift on edge hardware).** Architecture follows this
  choice; do not start candidate-specific training until it is made [S: 12 §10.1]. 
- [ ] ★ **Jacobi's intended role** — router-side (A-J, ~zero benefit), edge-
  generator (E-J, defensible but needs JF-post-training a sub-2B SLM), or drop the
  phrase [S: 04, 12 §10.2].
- [ ] ★ **Cloud-server hardware spec** (manuscript sentence is truncated at
  "…equipped with …") and ★ **which Split-LLM framework** the lab supports — both
  gate all of Stage 2 [S: 10, 12 §8].
- [ ] **Final model pool** — the concrete edge SLM(s) and strong/Split-LLM; the
  manuscript names none verifiably [S: 11 Q, 12 §10.4]. Gates Stage 1 label
  generation.
- [ ] **Is the Split-LLM action in the router's scope** at all (needed before any
  D/N1 work) [S: 12 §10.5].
- [ ] **Training-target / label formulation** to standardise on [S: 06, 12 §10.6].
- [ ] **λ and the success/falsification bars** (quality floor + cost/latency
  targets) for the paper's headline claim [S: 08 §11, 12 §10.7].
- [ ] **Lab logistics** — GPU class/VRAM, two-machine reservation, sudo/Docker,
  HF/GitHub egress, storage, power telemetry (the brief §15 checklist in `10`/`11`).

---

## C. AFTER LAB ACCESS — first 10 concrete implementation steps

These begin only once the novelty axis, model pool, Split framework, and hardware
are confirmed. Steps are candidate-agnostic where possible; where a step depends on
the chosen candidate it says so. Full phase A–J detail is in `09`.

1. **Provision & verify the edge node** (Xeon W-2123 / 64 GB / 2×RTX 3090 24 GB /
   Ubuntu 20.04.6, per manuscript) and the *confirmed* cloud server: install pinned
   CUDA/PyTorch/Transformers + the lab's Split-LLM stack; run a GPU/network smoke
   test [S: 09 Phase A, 10]. **[P]**
2. **Stand up the two-machine network testbed:** wire edge↔server, apply the
   pre-written `tc`/`netem` profiles (bandwidth/RTT/loss sweep points), and verify
   the bytes/RTT/TTFT/TPOT telemetry logs correct values on a trivial request
   [S: 09 Phase I, 15]. **[P]**
3. **Generate Stage-1 labels for the real pool:** run the confirmed edge SLM(s) and
   strong/Split-LLM over the query set, score answer quality, and materialise the
   per-(model,query) table — the input to every training target [S: 08 §2, 09
   Phase B]. **[P]**
4. **Rebuild the leakage-controlled + OOD splits** on the real-pool labels using the
   Stage-0 split code [S: 08 §8]. **[P]**
5. **Implement the chosen router `f_θ`** on the approved backbone (B encoder / C-pre
   probe / C-post / A generative) behind the shared `argmax Û − λ·C` interface
   built in A.4 [S: 09 Phase C, 12 §3–5]. **[P]**
6. **Train the router** on one GPU with the standardised target/loss; keep the run
   bounded (no large-model training) [S: 09 Phase D]. **[P]**
7. **Calibrate** (temperature scaling / the calibration method for the chosen
   target) and check calibration on the OOD split — this is the N2 evidence if that
   axis was chosen [S: 09 Phase E, 06]. **[P]**
8. **Offline evaluation** against all simple + published baselines with 5 seeds and
   paired significance tests; decide H1/H2 on the *real* pool [S: 09 Phase F, 08
   §8]. **[P]**
9. **Integrate the Split-LLM path** and, for N1/D, instrument **activation-transfer
   bytes and split-depth leakage** so the Split action has a measured systems cost
   [S: 09 Phase H, 12 §5]. **[P]**
10. **Run the network/system experiments** — sweep bandwidth/RTT and measure the
    route mix, TTFT/TPOT, p50/p95/p99, throughput, bytes, cost — to test **H3** and
    produce the SIGCOMM claim curves (C1–C7) [S: 09 Phase I–J, 15]. **[P]**

Paper-results generation (Phase J write-up) follows once these produce
statistically tested, falsification-checked numbers — **not** before [S: 09 Phase
J, brief §21].

---

## D. One-line status

Everything in **A** can proceed immediately and may already settle H1/H2 on CPU;
**B** is the advisor meeting itself; **C** starts the day the novelty axis, pool,
Split framework, and confirmed hardware are in hand.
