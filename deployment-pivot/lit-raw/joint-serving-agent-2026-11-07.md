# Raw lit notes: joint routing + serving/placement (subagent, 2026-11-07)

Produced by a research subagent with WebFetch on 2026-11-07. Full-text reads are noted per
paper. This is RAW input for deployment-pivot/LIT-REVIEW.md; re-check key numbers before citing.

## Full-text verified
- **RouterWise** (arXiv 2604.10907 v2, 22 Jun 2026; arXiv only).
  - Joint per-model setup (GPUs, TP, MPS share) + routing fractions.
  - Maximizes predicted avg quality s.t. AVERAGE latency (TTFT) ≤ τ, plus GPU memory.
  - Per-prompt DeBERTa regressor with dual prices. 4–8× A100-80GB. No edge, no split, no network cost.
  - Up to 87% quality spread across setups at the same SLO.
  - Future work: p95, online calibration, adaptive reallocation.
- **BOute** (MLSys 2026, arXiv 2602.10729).
  - Two models (Llama3.1-8B/70B); RouteLLM thresholds + GPU allocation matrix + DP/TP/PP.
  - Multi-objective Bayesian optimization (qNEHVI). P95 ≤ L_max, quality ≥ Q_min, $ budget.
  - Heterogeneous datacenter GPUs. No edge. PP communication is profiled only inside clusters.
  - Up to 157% better at the same budget.
- **ECO-LLM** (arXiv 2507.09003 v2, Jun 2026). CLOSEST edge-cloud prior art.
  - Per-query choice of a resolution path (preprocessing, retrieval, context, model), 200–300 paths.
  - Edge models: SmolLM2/Llama3.2-3B/Phi-4 on Jetson Orin Nano, M1/M4, A4500. Cloud: GPT-4.1 family.
  - Maximizes accuracy s.t. TTFT ≤ L_max and $ ≤ C_max.
  - Offline k-means clustering for emulation; online prototype-encoder nearest-neighbour scoring.
  - No split, no network or activation cost, no energy objective.
  - Abstract numbers differ between v1 and v2.
- **Cascadia** (ICLR 2026 poster, arXiv 2506.04203).
  - Bi-level: an MILP for GPU/parallelism under p95, plus cascade thresholds. 4×8 H100. No edge.
- **Fast Heterogeneous Serving** (arXiv 2604.07472, Apr 2026; simulation only).
  - MILP over GPU tiers, TP/PP, placement and ROUTING FRACTIONS PER QUERY TYPE, with a per-type error SLO.
  - This is structurally "task→model table + allocation" in the datacenter.
- **HW-Router** (arXiv 2608.14575, Jun 2026).
  - Per-query (model, GPU) choice using LIVE queue/KV-cache signals. 2×H100. Placement is fixed.
- **Splitwise edge-cloud** (IEEE/ACM UCC 2025, arXiv 2512.23310).
  - Lyapunov+DRL places heads/FFN on edge, cloud or split for ONE model.
  - Models bandwidth B(t) and activation volume; tc-emulated links at 10–100 Mbps.
  - Hardware: Jetson Orin NX, Galaxy S23, RPi5, 8×A100.
  - 1.4–2.8× faster than cloud-only. NO model selection.
- **HybridInfer** (arXiv 2609.30270, Jul 2026).
  - Tabular Q-learning over device / edge / cloud (GPT-4o), with a 15-state thermal×complexity table.
  - Galaxy S25+. No split.

## Abstract/metadata only
- Bao et al. 2508.11291 (ICCC workshop 2025): network-aware SLM/edge-LLM routing; no split.
- HybridFlow 2512.22137 (ICML 2026): subtask DAG routing edge/cloud.
- QLMIO 2606.15210: quality-latency offloading of multimodal LLMs.
- GAR 2605.11603: per-request CO2 routing under accuracy floor + p95.
- DynamoLLM (HPCA 2025): energy-aware reconfiguration, no model choice.
- Helix (ASPLOS 2025), Mélange, MuxServe, CascadeServe, EdgeShard.
- Title only: Joint Inference Offloading and Model Caching for SLM/LLM (IEEE TMC, DOI 10.1109/TMC.2025.3608303).

## Agent's synthesis
- Joint routing + allocation under an SLO is TAKEN in the datacenter (RouterWise, BOute, Cascadia, 2604.07472).
- EDGE-vs-REMOTE with a task table is TAKEN or weak (ECO-LLM, HybridInfer, 2508.11291, and 2604.07472's per-type table).
- Open: SPLIT as a third option together with quality-based model choice; live link state; fixed (not provisionable)
  edge resources; energy + edge memory + p95 together; and an empirical justification that a task table
  suffices (our E1–E3).
- If SPLIT never wins on real hardware, the contribution collapses toward ECO-LLM-style routing.
  Our analytic bound (evidence/split_bound.md) predicts SPLIT loses to an uncontended REMOTE.
  Combined with Splitwise UCC'25 reporting split wins vs cloud-only, this conflict is exactly what E0 must resolve.
- Suggested baselines: RouteLLM; CARROT/IRT-Router; RouterWise-style dual price adapted to fixed resources;
  HW-Router-style live load; ECO-LLM static best path + oracle; Edge-only / Remote-only / fixed-split (EdgeShard L/2);
  2508.11291; GAR (energy); optional BOute-style Bayesian optimization.
