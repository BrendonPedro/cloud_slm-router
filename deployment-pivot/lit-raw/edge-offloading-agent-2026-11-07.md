# Raw lit notes: edge-cloud offloading, MEC, split, speculative decoding (subagent, 2026-11-07)

Produced by a research subagent with WebFetch (arXiv HTML) on 2026-11-07. RAW input for LIT-REVIEW.md;
numbers are as extracted, so re-check before citing.

## Full-text read
- **TMO** (2502.11007v5, MobiHoc'25 extension). Phi-3-mini on device vs GPT-4o in the cloud, chosen per turn.
  - RL under latency and $ budgets. On-device latency is MODELLED from FLOPs on a Jetson TX2, not measured.
  - No split. Network is not modelled: the cloud's 20 s latency is dominated by provider inference.
- **PRISM** (2511.22788; AAAI venue unverified on the arXiv page). Three modes, gated by privacy.
  - "Collaboration" exchanges perturbed text, not activations.
  - Hardware: RTX 3070 laptop with llama.cpp.
  - Results — Cloud: 5.13 s / 296 J; Edge: 17.84 s / 1574 J (edge-side energy only).
- **RecServe** (2505.16502v2). Device→edge→cloud confidence cascade over small encoders. Simulated; no latency results.
- **Edge continuum measurement** (2609.08307, WIMS 2026).
  - Hardware: Jetson AGX Orin 64GB vs a T4 server vs GPT-4o; Ollama GGUF 1–7B models; MMLU.
  - Energy measured with a smart plug and RAPL. The network was not measured, only a 30/60 ms per-token sensitivity analysis.
- **ConsRoute** (2603.21237; venue unverified). Device Qwen3-1.7B / edge 14B / cloud 32B.
  - The router reads the prefill EOS hidden state; per-cluster thresholds are tuned by Bayesian optimization.
  - Hardware: RTX 3050 laptop / A6000 / 2×A6000.
  - Network profiles emulated as test conditions, not as decision inputs: good 10/5 Mbps, 40 ms; bad 0.8/0.2 Mbps, 250 ms.
  - ≥95% of cloud quality at about 60–65% of cloud latency.
- **CR²** (2605.12001). On-device margin gate, then an edge utility selector over Qwen3-4B/8B/14B.
  - Profiled on Jetson AGX Orin, RTX 4070Ti/4090/A40. Wireless is analytical (Shannon).
  - Cost = 0.5·latency + 0.5·energy. No split.
- **Yu, Goudarzi, Toosi** (2507.15553v2). Real testbed: CPU edge nodes with Qwen2.5-1.5B variants, A40 cloud with gemma3:27b.
  - NSGA-II offline tuning produces a RUNTIME LOOKUP TABLE. Placement is fixed.
  - Edge 3.97 s vs cloud 1.06 s vs proposed 1.11 s (35% lower cost).
- **Splitwise edge-cloud** (2512.23310, UCC'25). Head/FFN-level split of ONE model.
  - Real Jetson Orin NX / S23 / RPi5, with an 8×A100 cloud. tc emulation from 4G 10 Mbps/80 ms to WiFi 100/10.
  - Edge-leaning at 10 Mbps, even split at 100 Mbps. Internal inconsistencies noted.
- **Hyperion** (2511.14450v2). Multi-tier Jetson block partitioning of one model (Llama3-8B / Phi-3-14B).
- **Cloud, Edge, or Split? Drone VLM** (2609.25415, iEdge 2026). CLEANEST measured EDGE/SPLIT/REMOTE comparison.
  - Setup: SmolVLM-256M, Jetson vs A6000, replayed LTE trace.

    | Bandwidth | Edge | Cloud | Split |
    |---|---|---|---|
    | 2.1 Mbps | **2.77 s** | 3.87 s | 3.59 s |
    | 43.5 Mbps | 2.73 s | **0.83 s** | 2.19 s |
    | 65 Mbps | 2.73 s | **0.77 s** | 2.17 s |

  - Split NEVER won on latency. It won only on device energy (15 J vs 26 J onboard) and memory.
- **T2DRL** (2501.14205). MEC LLM caching + cloud-offload fractions under GPU memory and energy. Simulated.
- **QoS-aware multi-expert edge routing** (2508.00234; TMC venue unverified). SAC router over edge 7B experts on a 4090.
- **Unified AI Gateway** (2609.06940, Huawei). Per-request (model, site∈end/edge/cloud, KV action), with PD disaggregation as the split.
  - ANALYTICAL ONLY (DistServe A100 coefficients). Closest "model + site + split-like" formulation.
- **Edge-First LM inference** (2505.16508, ICDCS'25). AGX Orin Qwen2.5-7B: TTFT 0.28 s, about 593 J/query. GPT-4: TTFT 0.71 s.
- **To Offload or Not** (2504.15162v4). Jetson clients, A2/4070 edge servers, tc 2–50 Mbps.
  - Offloading pays off above ~15 Mbps (Orin Nano) or ~5 Mbps (TX2). Load also flips the decision.
- **Speculative decoding edge-cloud** (2505.21594, TMLR 2025). Jetson drafts, A100 verifies.
  - 1.35× over cloud autoregressive decoding. Some model pairs are SLOWER (0.42–0.69×). 96–120 ms of communication per operation.

## Abstract / metadata only
- **Lyra** (INFOCOM 2026, DOI 10.1109/INFOCOM59046.2026.11571307). Lyapunov online SLM/LLM routing.
- **LSCI** (IEEE TMC vol 25(2) 2691–2706, DOI 10.1109/TMC.2025.3608303). SLM caching (DRL) + offloading (belief propagation); numerical results.
- **Hybrid LLM** (ICLR 2024).
- **Speculation at a Distance** (2606.25091). Analytical: distributed speculative decoding loses at WAN RTT and pays off only through multi-tenant capacity.
- **Snippets only:** DSSD, QSV, SPADE, CoCaR.
- **DABO (IEEE Access 2026): NOT FOUND.** Do not cite without a DOI.

## Agent synthesis
1. MEC caching + routing (LSCI, T2DRL) already covers "which models on the edge server + where each request goes".
   All of it is simulated or numerical, with no split and no task-level lookup.
2. Model selection + EDGE/REMOTE on real hardware exists (2507.15553, ConsRoute, PRISM, CR²).
   SPLIT on real hardware exists only with ONE fixed model (Splitwise, Hyperion, drone VLM).
   Model + site + split-like path exists only analytically (Unified AI Gateway).
   No paper found chooses EDGE/SPLIT/REMOTE using measured profiles + live network state.
3. Network state does flip the optimal path in measured studies, at crossovers around 2–50 Mbps.
   These involve large payloads (images, activations) or short outputs. For text-only remote calls,
   RTT and server queueing matter more than bandwidth.
4. Measured split loses on latency (drone VLM) and wins only on device energy and memory,
   which is consistent with our analytic bound in evidence/split_bound.md.

## Notes for the next iteration (main agent)
- The bandwidth sensitivity in these studies comes from SHORT outputs or LARGE uploads.
  Our cached tables show 400–13,000-token outputs, which makes one-time network costs negligible
  and strengthens the "network rarely flips EDGE vs REMOTE for long-generation text tasks" hypothesis.
  E0/E-net should test this at controlled bandwidth/RTT.
- Recommended E0 sweep (agent): bandwidth 2–100 Mbps, RTT 10–250 ms. Measure the activation payload. Count server energy.
