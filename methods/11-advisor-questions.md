# 11 — Advisor Questions

*Deliverable 11 of the METHOD_BRIEF sprint. Every question below is a **decision the
advisor owns** or a **fact only the advisor/lab can supply** — this sprint
deliberately does not answer them, because the brief forbids making the advisor's
method decision for them (brief §17, §23). Each question names the deliverable that
raised it and, where relevant, the fact that makes it live. Nothing here is a
result. The original manuscript is unmodified (source SHA `06f5f9d7…1707cf6`).*

> **Scope-lock reminder.** These questions choose *how* to implement
> `R(q)=argmax_{M_k} f_θ(q,M_k)` under `max_R E_q[U − λ·C]` — they never reopen the
> research question itself [S: 00-scope-lock].

Legend: **[BLOCKER]** = downstream work cannot start until this is answered;
**[M]** = grounded in a primary-source fact; **[S: …]** = raised by that deliverable.

---

## TOP 10 (prioritized) — ask these first

The ordering is by how many downstream deliverables each unblocks.

1. ★ **[BLOCKER] Which novelty axis should we pursue** — N1 (a genuine Split-LLM
   action with activation-transfer cost + split-depth privacy leakage) or N2
   (calibration/selective-prediction under domain shift)? No candidate is a
   contribution on architecture alone; this choice, not the backbone, is the real
   decision, and it determines candidates, labels, and the whole experiment plan
   [S: 03-method-comparison §3; 08 §0].
2. ★ **[BLOCKER] What is the cloud-server hardware?** The manuscript's testbed
   sentence is literally unfinished — *"a dedicated server, which is equipped with
   …"* (L202) — so the cloud GPU class/VRAM/count are undefined, and they decide
   whether a 70B strong model can run at all [M: L202; S: 10 §3.2].
3. ★ **[BLOCKER] Is there an existing Split-LLM codebase/framework in the lab, or
   do we build a minimal split ourselves?** No lab split code was found in the repo;
   Stage 2 (the SIGCOMM core) cannot start without this [M; S: 10 §6; repro §6].
4. ★ **[BLOCKER] Fix the model pool.** The manuscript names models that **do not
   exist officially** — **Qwen3-72B-Instruct** (no such Qwen model) and the
   **Gemma-4 "-A4B" edge suffixes** — and uses effective-size ("E2B/E4B") names.
   Which exact HF revisions define the weak and strong pools? [M: repro §5;
   S: 08 §14 Q2].
5. **Can two machines + a controllable network be reserved simultaneously, with
   `sudo` and `tc/netem`?** This is the difference between a real networked-systems
   result and a single-host emulation [S: 10 §3.3; 14 §4].
6. **Confirm the training target** to prioritize: separated utility + measured cost
   (F, best fit to Eq. 2 and the run-time-λ story) vs binary weak≥strong (cheapest
   to falsify first). All targets share one labelling campaign, so this ranks
   effort, not architecture [S: 06-label-and-training-design §5].
7. **Confirm the cost-integration approach:** S2 (learn `U`, combine with
   *measured* `C(s)` outside the net) is the only design that can express the
   network-adaptivity claim; approve it as primary, with S4 (system-only) as a
   mandatory baseline? [S: 07-system-cost-integration §S2/§S4].
8. **What is the role of "Jacobi-Forced" in the title?** No method by that name
   exists in the literature; the only coherent placement is on the edge *generator*,
   not the router. Should Jacobi stay as an edge-generator ablation (E-J), a
   router-output ablation (A-J, only if the router emits multi-token), or be
   clarified? [S: 04-jacobi-role].
9. **Confirm the success/falsification thresholds** (CCR@−1 ≥ 5 pt over TF-IDF+LR;
   A vs B non-inferiority 2 pt; ECE ≤ 0.10/0.15; H3 across ≥ 2 network conditions)
   — these are *our proposals*, not approved bars [S: 08 §11].
10. **Compute/API budget and long-run limits** — how much GPU time and API spend is
    available? (LLMRouterBench's own collection cost ~1K GPU-hours + ~$3000 API
    [M: readme]; our Stage 1 is a fraction but still budget-gated) [S: repro §6].

---

## A. Architecture questions
- A1. Which candidate backbone(s) to build first: B (micro-encoder, conservative),
  C-pre (prefill probe), or D (multi-head utility, N1)? [S: 02; 03].
- A2. Is a generative Tiny-LM (candidate A) required for the "Tiny-LM" title, or is
  a discriminative router acceptable if it matches A? (This is H2.) [S: 02; 08 §1].
- A3. Should the router run *before* generation (pre-generation, all candidates) or
  reuse the edge SLM's own prefill state (C-pre)? Trade-off: C-pre reuses compute
  but ties the router to one edge model [S: 02 candidate C].
- A4. Same neural model for query + system state (S1), or separated (S2/S3)?
  [S: 07].

## B. Jacobi questions
- B1. See Top-10 #8. What did the title intend by "Jacobi-Forced Micro-Encoder"?
- B2. If Jacobi is kept, is it acceptable that no sub-7B Jacobi-Forcing checkpoint
  exists, so it cannot run on a 2–4B edge model without training one? [M: repro §4].
- B3. Is Jacobi in scope for the *first* paper, or future work? (It is excluded from
  the minimum experiment as written [S: 08 §4].)

## C. Model-pool questions
- C1. Resolve the non-existent/renamed models (Top-10 #4): Qwen3-72B →
  Qwen2.5-72B / Qwen3-32B / Qwen3-235B-A22B? Gemma-4 E2B/E4B/12B exact IDs?
  [M: repro §5].
- C2. Nested (Llama-3.1-8B, cost-saving only) vs complementary (Qwen3-8B, quality
  *gain* possible) weak/strong regime — which defines the headline result?
  [M; S: 06; 08 §2].
- C3. Are all models really deployable at 4-bit, including the diffusion LMs
  (LLaDA-MoE, Dream, Fast-dLLM-v2)? No source confirms 4-bit decoders work for them
  [M: repro §8].
- C4. Which strong model is the "cloud/split" target, and does it fit the (still
  undefined) cloud hardware? [S: 10 §3.2].

## D. Data questions
- D1. The manuscript assumes SimpleQA labels come free from LLMRouterBench (L205),
  but **none of the manuscript's own models appear on SimpleQA in the release** — so
  labels must be *generated* for the whole pool. Is the GPU cost of that acceptable?
  [M: repro §2; S: 08 §2].
- D2. Should `arenahard*` (judge win/tie/loss) enter as a secondary soft-label pool,
  or stay excluded? [M; S: 08 §14 Q5].
- D3. Is the LLMRouterBench data licence (no LICENSE file, MIT badge only) acceptable
  for our use / redistribution? [M: repro §2/§7].
- D4. For SimpleQA grading, which judge model + prompt should be pinned? (grading is
  LLM-judged) [M: repro §2].

## E. Split-LLM questions
- E1. See Top-10 #3 (framework/codebase).
- E2. What split depth(s) `d` should be evaluated? `d` sets both activation size and
  the edge/server VRAM division [S: 07; 10 §6].
- E3. Is split-depth **privacy leakage** (an N1 novelty precondition) something we
  should measure, and against what threat model? [S: 03; 09 phase H].
- E4. Serverless (RunPod Flex, cold-start) in scope, or dedicated-instance only?
  [M: L221/L241].

## F. Lab / hardware questions
- F1–F25: the full brief-§15 checklist is enumerated in [S: 10 §8]; the blockers
  there (two machines, Split-LLM codebase, controllable network, `tc/netem`,
  `sudo`) are lifted into Top-10 #2/#3/#5.
- F-cloud. The unfinished cloud spec (Top-10 #2) — lab-owned server or rented
  RunPod (which matches the paper's cost model, L231)? [M: L202/L231].
- F-storage. Where do large checkpoints live, and how much storage? [S: 10 §1].
- F-licence. Llama gating + Arch-Router research licence approvals — who requests
  them? [M: repro §7].

## G. Networking questions
- G1. What real link exists between edge and cloud (LAN? campus? WAN?), and what
  bandwidth/RTT range can we emulate on it? This defines the C4 adaptivity curve
  [S: 15 C4; 10 §3.3].
- G2. Is injected contention / background traffic allowed (for the p99 tail-latency
  claim)? [S: 15 C5].
- G3. Can we count activation bytes on the link at the tensor level? [S: 08 §6.2].

## H. SIGCOMM / venue questions
- H1. The **SIGCOMM 2027 CFP is not yet published** (site live, but deadlines/page
  limits/artifact rules all TBA); the plan uses the SIGCOMM 2026 CFP only as
  orientation. Is SIGCOMM 2027 still the target, or a fallback venue? [M: 14 §1].
- H2. Should we plan for **Artifact Evaluation** (voluntary-but-encouraged at
  SIGCOMM 2026)? It shapes how we package code/data from day one [M: 14 §2].
- H3. Which SIGCOMM claim is the headline — e2e-latency-at-matched-quality,
  bytes-saved, or network-adaptivity (C4)? [S: 15].
- H4. Given the "looks like an ML paper" risk, does the advisor agree the real
  network testbed (not emulation) is required for submission? [S: 14 §4].

## I. Success-criteria questions
- I1. Confirm thresholds (Top-10 #9) [S: 08 §11].
- I2. 5-seed protocol + Holm–Bonferroni across routers × regimes × OOD folds —
  acceptable, or different statistical bar? [S: 08 §8].
- I3. What counts as "lightweight enough" for edge deployment (a latency/memory
  budget for the router itself)? The paper claims "lightweight" but sets no number
  [M: L61; S: 00 constraint A].
- I4. Is the "adaptable without costly retraining" claim (L65) something we must
  *demonstrate* (train-size ablation + new-model-addition test), given the brief
  says it must not be assumed? [S: 00 §D; 02 §adaptability; 08 §10 ablation 4].

---

*Cross-refs: aggregates open questions from every prior deliverable, especially
`methods/03` (novelty axis), `methods/04` (Jacobi), `methods/06`/`07` (target/cost),
`methods/08 §14` (experiment), `methods/10 §8` (lab), `methods/14`/`15` (SIGCOMM),
and `experiments/reproducibility-plan.md` (model/licence facts). Feeds
`methods/12-method-proposal.md §10 (decisions needed)` and
`methods/13-presenter-notes.md`. Manuscript unmodified (SHA `06f5f9d7…1707cf6`).*
