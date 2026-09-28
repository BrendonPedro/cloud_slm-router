# 10 — Lab Requirements (Hardware / Software / Network / Measurement)

*Deliverable 10 of the METHOD_BRIEF sprint. This is a **requirements plan**, not a
purchase order and not a result. No experiment here has been run. Numbers tagged
**[M]** are read from a primary source (the manuscript or a saved API response);
**[S: …]** is sourced from an earlier deliverable in this repo; **[E]** is our
arithmetic/estimate, not measured; **[?]** is unknown and must be confirmed by the
advisor/lab before use. The original manuscript is unmodified (source SHA
`06f5f9d7…1707cf6`).*

> **Scope-lock check.** Every requirement below serves the *same* router
> `R(q)=argmax_{M_k} f_θ(q,M_k)` under `max_R E_q[U(R(q),q) − λ·C(R(q),q)]`
> (Eq. 1–3, `source/main-original.tex`). The testbed exists to **measure `C(a,s)`**
> (bytes, TTFT, TPOT, latency, energy) so the router can trade it against `U`; it
> does not change the research question [S: 00-scope-lock; 07-system-cost-integration].

---

## 0. What the manuscript already fixes, and the one gap it leaves

The manuscript specifies the **edge side** of the testbed and leaves the **cloud
side blank**:

- **[M]** Edge server (L202): *Intel Xeon W-2123, 64 GB system memory, 2 × NVIDIA
  GeForce RTX 3090 (24 GB VRAM each), Ubuntu 20.04.6 LTS*, running the client-side
  Split-LLM computation.
- **[M]** Cloud server (L202): *"a dedicated server, which is equipped with …"* —
  **the sentence is unfinished; the cloud hardware is undefined in the paper.**
  This is the single largest hardware unknown and is escalated as an advisor
  question (§8 Q-cloud; [S: 11-advisor-questions A/F]).
- **[M]** Cost model (L228–247): operational cost is estimated from **RunPod**
  dedicated + Flex (serverless) GPU pricing, not from owning the cloud GPU. So the
  "cloud" can legitimately be a rented instance rather than lab hardware — this
  changes the hardware ask (§4) [S: 07 §cost-object].
- **[M]** All strong/split models are deployed at **4-bit quantization** (L295).
- **[M]** Latency metrics named by the paper: **TTFT** (prefill + activation
  transmission + server compute, L211), TPOT, end-to-end, and **serverless
  cold-start latency** (L221).

Everything in §1–§7 is written to be consistent with these fixed facts and to fill
the cloud-side gap with explicit options rather than an invented spec.

---

## 1. Three requirement tiers

Because the experiment is staged [S: 08-experiment-design §0], the hardware need
grows in three steps. We give a **MINIMUM viable**, a **PREFERRED**, and an
**IDEAL** tier. The minimum can falsify H1/H2 cheaply *before* any Split-LLM spend.

| Tier | What it can do | Blocks which claims |
|---|---|---|
| **MINIMUM** | Stage 0 (done) + Stage 0b/0c neural routers + Stage 1 labels for a *small* real pool, single machine, emulated network | H1, H2, calibration; a **single-host emulated** version of H3 |
| **PREFERRED** | Full Stage 1 pool + Stage 2 on **two physical machines** with a real controllable link | H3 + the SIGCOMM network-adaptivity claim (C4) [S: 15] |
| **IDEAL** | Preferred + energy telemetry + WAN emulation range + multi-GPU cloud for large strong models + serverless cold-start measurement | tail-latency-under-contention, energy, cold-start, full model pool |

---

## 2. MINIMUM viable setup

**Goal:** run everything that can falsify H1/H2 and produce calibration curves,
using as little as one GPU. Network effects are **emulated on one host** (loopback
+ `tc/netem` + a byte-accounting shim), which is honest for *relative* byte/latency
comparisons but must be labelled as emulation, not a real WAN [S: 14-sigcomm-fit
§4 "no real network" risk].

### 2.1 Compute
| Item | Minimum | Basis |
|---|---|---|
| GPU | 1 × 24 GB (e.g. one RTX 3090 from the L202 pair) | 8B BF16 ≈ 16 GB; 4-bit strong ≤ 24 GB for ≤ ~40B [E; §5 of repro-plan] |
| CPU / RAM | the Stage-0 host suffices for stdlib work (Ryzen 5 8500G, ~9.7 GiB) **[M: run]**; neural routers need the GPU host | [S: experiments/reproducibility-plan §0] |
| Storage | ~50–150 GB: data bundle 1.28 GB **[M]** + a handful of 2–8B checkpoints (few GB each at 4-bit) + generations/logs | [E] |

### 2.2 What runs here
Stage 0 (already run, CPU-only: labels, TF-IDF+LR, always-edge/cloud, random,
dataset-prior, oracle, deferral-AUC/CCR@−1/ECE/Brier, per-seed bootstrap)
[S: 08 §13]; then on the GPU: B-s/B-m fine-tune, A LoRA(0.5B), A-zs, and **C-pre**
(8B prefill hidden-state probe, the one router that *needs* a GPU) [S: 08 §4].

### 2.3 What it cannot honestly claim
A single-host emulation cannot measure real edge↔cloud RTT/bandwidth interaction,
serverless cold-start, or contention on a shared link. Those are Stage 2 /
PREFERRED. State this limitation explicitly in any write-up [S: 14 §4].

---

## 3. PREFERRED setup (the SIGCOMM core)

Two physical machines with a controllable link — this is what turns the work into a
networked-systems result rather than an ML-classification result [S: 14 §3].

### 3.1 EDGE node (matches the manuscript, L202)
| Field | Requirement | Source |
|---|---|---|
| GPU class | 2 × RTX 3090 (24 GB each) as in the paper; **minimum** 1 × 24 GB, **preferred** 2 × 24 GB (needed to hold an 8B edge model *and* the client-side split partition together) | [M: L202] |
| Min VRAM | 24 GB (single) | [E from 8B BF16 ≈ 16 GB] |
| Preferred VRAM | 48 GB (2×24) | [M: L202] |
| CPU | Intel Xeon W-2123 or comparable | [M: L202] |
| RAM | 64 GB | [M: L202] |
| Storage | ≥ 256 GB SSD (checkpoints + generations + traces) | [E] |
| OS | Ubuntu 20.04.6 LTS (or newer LTS) | [M: L202] |
| CUDA / driver | version that supports the chosen torch; **[?]** pin exact version | [?] |
| PyTorch | pin exact version per model card (Dream pins `torch==2.5.1`, `transformers==4.46.2` **[M: readme]**) | [S: repro §5] |
| Transformers | pinned per model; diffusion LMs are version-sensitive | [S: repro §5] |
| Quantization framework | bitsandbytes / AWQ / GPTQ for 4-bit (L295); **[?]** confirm 4-bit decoders work for LLaDA-MoE/Dream/Fast-dLLM | [S: repro §8] |
| Energy telemetry | `nvidia-smi` power draw; external meter if available (IDEAL) | [S: 08 §6.2] |

### 3.2 SERVER (cloud / split) side — **the undefined half (L202)**
Because the paper leaves this blank and models cost with **rented** GPUs
(RunPod, L231), there are two legitimate realizations — the advisor must pick one
[S: 11 A/F]:

| Field | Option A: lab-owned server | Option B: rented (RunPod, matches L231 cost model) |
|---|---|---|
| GPU class | ≥ 1 datacentre GPU (A100/H100) or 2–4 × 3090/4090 | RunPod dedicated + Flex (serverless) instance |
| Min VRAM | enough for the largest strong model at 4-bit: 70B ⇒ ~35 GB **[E]** so ≥ 48 GB or 2 GPUs; 30B Nemotron ⇒ ~16 GB **[E]** | pick instance ≥ that |
| # GPUs | 1–2 for ≤30B; 2+ for 70B | per instance |
| RAM | ≥ 2× total VRAM | per instance |
| Storage | ≥ 512 GB (large checkpoints) | ephemeral + network volume |
| Serving software | vLLM / TGI / transformers; **Split-LLM framework [?]** (see §6) | same, containerized |
| Split-LLM requirement | must expose a **layer-split boundary** so client-side partitions run on the edge and activations transfer over the link | same |

**Note (L298 model gap):** the manuscript names **"Qwen3-72B-Instruct", which does
not exist officially** [S: repro §5]; the strong-model choice (and therefore the
server VRAM need) is an unresolved advisor decision, not a hardware fact.

### 3.3 NETWORK (between edge and server)
| Field | Requirement | Source |
|---|---|---|
| Two-machine connectivity | direct Ethernet or same-rack LAN, plus a WAN-emulation path | [S: 08 §7 SIGCOMM claim] |
| LAN/WAN assumptions | LAN baseline; WAN emulated (the paper's WAN framing, L76) | [M: L76] |
| Link type | ≥ 1 GbE (10 GbE preferred for large-activation splits) | [E] |
| Bandwidth control | **Linux `tc`/`netem`** (rate) | [M: brief §14; standard] |
| RTT control | `tc/netem delay` | standard |
| Packet-loss control | `tc/netem loss` (only if a loss claim is made) | optional |
| Contention | background traffic generator (iperf) for the tail-latency claim | [S: 15 C5] |
| Traffic measurement | byte counters on the split link (`/proc/net`, `nstat`, or app-level accounting of activation tensors) | [S: 08 §6.2] |
| Tracing/logging | per-request timestamps at prefill/transmit/server/return boundaries → TTFT/TPOT/e2e | [M: L211] |

**Requires:** `sudo` (for `tc/netem` and driver/CUDA installs), and ideally Docker
for reproducible serving — both are advisor/lab questions [S: 11 F/G].

---

## 4. IDEAL setup (adds the claims MINIMUM/PREFERRED cannot)

- **Energy:** external power meter on the edge node (wall-plug) for whole-device
  energy, since `nvidia-smi` misses CPU/DRAM/NIC; enables the energy column of the
  §15 matrix [S: 15].
- **Serverless path:** a real serverless GPU endpoint (RunPod Flex, L241) to
  measure **cold-start latency** (L221) rather than emulate it.
- **WAN range:** a programmable range of bandwidth (e.g. 10 Mbps–1 Gbps) and RTT
  (5–200 ms) to draw the **network-adaptivity curve C4** — the single row that
  separates this from an ML paper [S: 15 C4; 07 §S2].
- **Full pool:** enough server VRAM (or budget) to run *all* strong models named
  in L295–302 at 4-bit, including a 70B — needs ≥ 48 GB or multi-GPU.
- **Repeatability:** a second identical edge node to test cross-device variance.

---

## 5. Software stack (all tiers) and licence gates

| Layer | Requirement | Notes / [?] |
|---|---|---|
| Python env | venv/conda with torch (the Stage-0 host has **no pip/venv** until `apt install python3.12-venv`, sudo) **[M: run]** | [S: repro §0] |
| Core ML | torch, transformers, peft (LoRA for A), scikit-learn (TF-IDF+LR), numpy | pin versions |
| Quantization | bitsandbytes / AWQ / GPTQ | 4-bit (L295); **[?]** diffusion-LM 4-bit support |
| Serving | vLLM or TGI (server); optional for edge | version **[?]** |
| Split-LLM | **framework undecided** — see §6 | [?] advisor |
| Baselines | RouteLLM (Apache-2.0 **[M: api]**), Arch-Router-1.5B (research licence **[M: api]**), ICL-Router (no SPDX, **8-GPU** train scripts **[M: readme]**), RouteLMT (**no code — reimplement from paper** **[M: api]**) | [S: 01-method-landscape; repro §3] |
| Data | LLMRouterBench bundle (1.28 GB, **no LICENSE file** **[M: api]**), SimpleQA (MIT **[M]**) | [S: repro §2] |
| **Licence gates** | Llama-3.1/3.3 **gated** (manual approval) **[M: api]**; Arch-Router **research licence** before fine-tuning; LLMRouterBench licence unconfirmed | resolve **before** redistribution/fine-tune [S: repro §7] |

---

## 6. The Split-LLM software gap (blocks Stage 2)

The paper asserts a Split-LLM ("model divided into S splits, minority to the edge",
L76) but **names no framework** and the repo audit found **no lab Split-LLM
codebase** [S: repro §6]. Stage 2 cannot start until this is resolved. Options to
put to the advisor [S: 11 E]:

1. An existing lab Split-LLM codebase (does one exist? [?]).
2. A public split-inference framework (must expose a layer boundary + activation
   transfer) — candidate frameworks to be verified against primary sources, **not**
   assumed to exist.
3. A minimal custom split (run layers 0..d on edge, ship the hidden state, run
   d+1..L on server) — feasible for a Master's student but must be built and
   verified; this is the honest fallback and its activation-byte accounting is
   exactly the `C` term the paper needs [S: 07].

Until (1)/(2)/(3) is chosen, Stage 2 hardware sizing (server VRAM, link bandwidth)
cannot be finalized — the split depth `d` determines both activation size and the
edge/server VRAM division.

---

## 7. Measurement requirements (map each to `U − λC`)

| Quantity | Tool | Term | Tier |
|---|---|---|---|
| Quality (per dataset metric / judge) | frozen scoring script per dataset | **U** | MIN |
| Calibration: ECE, Brier, AURC | offline from p̂ | U (reliability) | MIN |
| TTFT | request-boundary timestamps | C (latency) | PREF (real link) / MIN (emulated) |
| TPOT | per-token timestamps | C | PREF |
| e2e p50/p95/p99 | request log | C | PREF |
| Activation bytes / link bytes | app-level tensor accounting + `nstat` | C (communication) | PREF |
| Throughput (req/s, tok/s) | load driver | C | PREF |
| GPU util / mem | `nvidia-smi` | C (compute/memory) | MIN(edge)/PREF(both) |
| CPU util / RAM | `psutil`/`/proc` | C | MIN |
| Energy / power | `nvidia-smi` power; external meter | C (operational) | IDEAL |
| Cold-start latency | serverless endpoint timing | C | IDEAL |
| Operational cost (CPR/OPEX) | modelled from bytes+compute+RunPod price (L228–247) | C (monetary) | PREF |

Each dependent variable is stated as IV→DV→falsifier in [S: 08 §7; 15]; no value
is asserted here.

---

## 8. Advisor lab-access checklist (brief §15, all 25 + the cloud-spec question)

These are carried into the prioritized set in [S: 11-advisor-questions F/G]. The
**top blockers** are marked ★.

1. Which GPU models are available? 2. VRAM per GPU? 3. How many GPUs can one
student reserve? 4. ★ **Can two machines be reserved simultaneously** (Stage 2)?
5. Is there a dedicated edge device? 6. What does the lab consider the edge node?
7. ★ **Is there an existing Split-LLM codebase?** (§6) 8. Is there an existing
edge/cloud testbed? 9. ★ **Are the machines on a controllable network?**
10. ★ **Can I use `tc`/`netem`?** 11. **Do I have `sudo`?** 12. Can I use Docker?
13. Can I install CUDA/PyTorch/Transformers/vLLM? 14. Outbound Hugging Face
access? 15. GitHub access? 16. Where to store large checkpoints? 17. How much
storage? 18. `nvidia-smi` power measurement allowed? 19. External power meter
available? 20. Preferred model family the lab supports? 21. Preferred Split-LLM
framework? 22. Cloud/API resources available (matches the RunPod cost model)?
23. Compute budget? 24. Restrictions on long-running experiments? 25. Prior lab
work/code to build on?

**Plus one the brief implies from L202:** ★ **What is the cloud-server hardware?**
The manuscript's sentence is unfinished — the cloud GPU class, VRAM, and count are
undefined, and they determine whether a 70B strong model is even runnable
[M: L202; S: repro §6].

---

*Cross-refs: consumes the model-pool + licence audit from
`experiments/reproducibility-plan.md` and the metrics/staging from
`methods/08-experiment-design.md` and `methods/07-system-cost-integration.md`;
feeds the advisor questions (`methods/11-advisor-questions.md`), the proposal
(`methods/12-method-proposal.md`), and the action plan
(`methods/16-next-week-action-plan.md`). Manuscript unmodified (SHA
`06f5f9d7…1707cf6`).*
