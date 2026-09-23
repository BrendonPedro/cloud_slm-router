# Advisor brief: "Tiny-LM with Jacobi-Forced Micro-Encoder for Collaborative Inference between Edge SLMs and Split-LLMs"

*Status as of 2026-09-23. AI-assisted audit (see `advisor/research-sprint-report.md`). Every point cites the deliverable holding the evidence. Nothing here is a decision.*

**1. The original idea** (d1). A small router on the edge device picks, per query, one of an edge SLM, a Split-LLM or a cloud LLM, trading quality against cost and latency (Eqs. 2–3). The body calls the router a "Tiny Language Model". "Jacobi", "Micro" and "Encoder" appear **only in the title** (L22). The Proposed Solution (L193–195) and Results (§V) sections are empty, yet the abstract and C4 say "extensive experiments demonstrate…" (d1, d13).

**2. What changed in the field** (d2, d3). Between 2024 and 2026 edge–cloud and SLM/LLM query routing became crowded: RouteLLM (ICLR'25), IRT-Router (ACL'25), BEST-Route (ICML'25), ICL-Router (AAAI'26), RouteLMT (ACL'26 Industry), and LLMRouterBench (Findings ACL'26), which reports that many routers tie a simple baseline. These venues are confirmed in `references/library.bib`. Hybrid LLM (ICLR'24) and PRISM (AAAI'26; edge/collaborative/cloud with privacy) are venue-claimed by arXiv comment only. Among preprints, ConsRoute (device–edge–cloud, a probe on the SLM prefill state) and Pro-Router are close. Jev (TypeSafe) launched on 2026-09-15 as a commercial cloud "decision model" API.

**3. Closest prior work** (d3 ranking): ConsRoute, Bao et al. (ICCC'25 workshop), Pro-Router, Hybrid LLM, SWARM-LLM, RouteLMT, then PRISM for the three-way framing. On the split side, Cunningham (2602.16760) runs split inference over a WAN with lookahead decoding, but has no router.

**4. Novel / not novel** (d4 §4, d8 §4). The following are **occupied**: a tiny or encoder router, a generative router, no-retraining adaptation, the joint cost–quality objective, and three-way routing with privacy as a criterion. **Unresolved in our bounded search:** (U1) a query router whose actions include a **Split-LLM path** with measured activation-transfer cost and split-depth leakage; (U2) **calibration** of an on-device, pre-generation capability router under domain shift; (U3) whether any router beats the simple baseline with a real edge SLM and link. **Caveats:** U1 could be closed by Mix-or-Split (IEEE TPDS 2026), which we could not read (closed access). U1 is also only a *learning* problem if the split and cloud paths differ in quality or sensitivity. Otherwise a rule would do.

**5. "Jacobi-Forced Micro-Encoder"** (d6, d7). *No established method with this exact name was found as of 2026-09-23.* Jacobi Forcing (arXiv 2512.14681, repo lists ICML 2026) trains **causal AR decoders** for parallel decoding. The paper reports about 2.6–4.0× at 7B for code and math, with only two 7B checkpoints released. It does not apply to a router: a classifier head needs no sequential decoding, and a one-token label makes Jacobi decoding identical to AR decoding. The phrase could coherently describe only a **Jacobi-Forced edge/split generator** paired with a separate small router (d7 P1). That would be a decoding contribution, orthogonal to routing.

**6. Jev relevance** (d5). Jev **redirects** the motivation. It weakens "fast lightweight router" and "generative TLM" claims, and it supports treating routing as a typed, calibrated decision. It leaves open on-device, pool-specific, open-weight routing. Its architecture is undisclosed and its performance claims come from the vendor.

**7. Measured so far** (d12, `experiments/prototype/`, released LLMRouterBench scores, no model inference). On Qwen3-8B vs Qwen3-235B in-domain, TF-IDF+LR sends 0.299 of queries to the cloud, against 0.410 for the dataset-prior router and 0.113 for the oracle. On deferral AUC it significantly beats dataset-prior in only 2/5 seeds. In leave-one-dataset-out folds it is never significantly better than random and is significantly worse in 3/8. **No neural, generative or Jacobi router has been run.** (torch is not installable on the host.)

**8. Recommended research questions** (d8 N1–N3). N1: split-aware routing (only if Mix-or-Split leaves room). N2: calibrated on-device capability routing, evaluated OOD against the simple baseline. N3: Jacobi Forcing on a sub-2B edge generator, as a separate paper.

**9. Minimum experiment** (d10). Stage 0 on released scores (Llama-3.1-8B or Qwen3-8B vs a flagship; 5 seeds plus 4 leave-one-dataset-out folds), comparing encoder router B, small generative router A and simple baselines on cloud-call rate at −1 pt quality, deferral AUC and ECE. The pre-registered criteria can falsify H1 (the router beats simple baselines) and H2 (a Tiny-LM is needed). This needs one GPU. The Split-LLM stage (H3) needs a real device plus a link.

**10. Decisions needed from you**
- Continue, narrow (N1/N2), redesign, or change direction to N3?
- Keep, drop or reword the title's "Jacobi-Forced Micro-Encoder"?
- Is getting Mix-or-Split through the library a precondition for N1?
- Confirm or change the success thresholds in d10 §9 (5 pt, 2 pt, ECE 0.10/0.15).
- The first abstract sentence matches Li et al. (ACM CSUR 2026) verbatim (d8 §5). How should this be handled before the draft is circulated?
- Model pool: "Qwen3-72B-Instruct" has no official checkpoint, and the Gemma-4 names are wrong (d11). Which models are actually available?

*d1 = `research/problem-as-written.md`, d2 = `current-landscape.md`, d3 = `closest-prior-art.md`, d4 = `novelty-matrix.md`, d5 = `jev-system-one.md`, d6 = `jacobi-forcing.md`, d7 = `micro-encoder-investigation.md`, d8 = `gap-assessment.md`, d10 = `architecture/recommended-experiment.md`, d11 = `experiments/reproducibility-plan.md`, d12 = `experiments/prototype/`, d13 = `research/claim-audit.md`.*
