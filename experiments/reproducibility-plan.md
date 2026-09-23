# Deliverable 11: Reproducibility plan

*Written 2026-09-23 (iteration 13). This is a list of dependencies and a plan. It
contains no results. Licence and metadata fields were taken from the GitHub REST API
and the Hugging Face (HF) Hub API on 2026-09-23. The raw responses are saved in
`research/raw/repro/` (with a timestamped `fetch-log.txt`) and in
`research/raw/experiment/` (iterations 10–11). Only the Stage-0 commands in §1 have
actually been run in this project.*

Tags: **[api]** a field copied from a saved API response (file named);
**[readme]** quoted from the saved upstream README; **[run]** a command this
project executed, with its log; **[E]** our estimate, not measured;
**[?]** unknown, and must be checked by a person before use.

"Licence" below means the machine-readable field only (GitHub `license.spdx_id` or
the HF `license:` tag / `cardData.license_name`). **A missing field does not mean
the work is public domain.** Where it is missing, reuse terms must be confirmed by
hand, for example by reading the repo for a LICENSE file or asking the authors.

---

## 0. Host this audit ran on (the only hardware actually used)

| Item | Value | Source |
|---|---|---|
| CPU | AMD Ryzen 5 8500G, 4 vCPU visible | `experiments/prototype/logs/environment.txt` [run] |
| RAM | ~9.7 GiB | same |
| GPU | none (`nvidia-smi` not present) | `research/raw/repro/fetch-log.txt` [run] |
| OS | WSL2, Linux 6.6.87.2 | same |
| Python | 3.12.3, standard library only | same |
| Package tooling | no `pip`/`ensurepip`, no `uv`/`conda`/`pipx`; `python3 -m venv` fails until `apt install python3.12-venv` | `research/raw/repro/fetch-log.txt` [run] |

Consequence: on this host, only the stdlib Stage-0 pipeline can run. Every neural
router (B-s, B-m, A, A-zs, C-pre) first needs a Python environment with torch, and
C-pre and Stages 1–2 need a GPU.

## 1. Already reproducible: Stage 0 (zero-inference)

This is the only part of the plan that has been executed [run].

```bash
# 1. data bundle (1,283,503,080 bytes; sha256 must equal the HF LFS oid)
curl -sSL -C - -o /tmp/llmrb.tar.gz \
  https://huggingface.co/datasets/NPULH/LLMRouterBench/resolve/main/bench-release.tar.gz
sha256sum /tmp/llmrb.tar.gz   # expect b79f8cde1a6f029c2efa663a3a3b6f7748defb22341fe59f328cebef6648c8f1
mkdir -p /tmp/llmrb && tar xzf /tmp/llmrb.tar.gz -C /tmp/llmrb

# 2. inventory (optional; reproduces research/raw/experiment/inventory_output.txt)
python3 research/raw/experiment/inventory_llmrouterbench.py /tmp/llmrb/bench-release

# 3. Stage-0 baselines (cwd = experiments/prototype; ~4m44s on the host above)
python3 stage0.py config/stage0.json
python3 summarize.py
```

Checks that a re-run has to pass: `preds/` and `splits/` are byte-identical to the
committed files (`logs/determinism.txt`), and the config sha256 is
`db39e3e8…a0` (`logs/environment.txt`). The script expects the bundle at
`/tmp/llmrb/bench-release` (the path is set in `config/stage0.json`).

## 2. Data

| Dependency | Source | Licence | Install / fetch | Used for | Notes |
|---|---|---|---|---|---|
| LLMRouterBench code | `github.com/ynulihao/LLMRouterBench`, last push 2026-04-06 | **no SPDX field** [api: `gh_ynulihao_LLMRouterBench.json`]. The README shows an MIT badge. The repo root has **no LICENSE file** [api: `gh_contents_ynulihao_LLMRouterBench.json`] | `git clone …; pip install -r requirements.txt` [readme] | baseline adaptors, data collector (Stage 1) | the badge alone is weak evidence of a licence; ask the authors before redistributing code |
| LLMRouterBench data bundle | HF `NPULH/LLMRouterBench`, `bench-release.tar.gz` | same caveat | §1 | Stage 0 labels (P-L, P-Q) | not committed here; only query hashes are committed |
| SimpleQA | `openai/simple-evals`, loaded by `simpleqa_eval.py` from `https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv` [api/readme: `simpleqa_eval.py`] | MIT (repo SPDX [api]; the README lists SimpleQA under MIT [readme]) | `curl -O <csv url>` | Stage 1 labels for the manuscript's pool (L205) | the repo has not been updated for new models since July 2025, but it still hosts SimpleQA [readme]. Grading uses an LLM judge, so the grader model and prompt must be pinned and logged |
| MMLU-Pro, GPQA, LiveCodeBench, LiveMathBench, AIME | as packaged inside the LLMRouterBench bundle | per-dataset licences [?] not checked | via the bundle | Stage 0 | GPQA ships as a password-protected zip with a canary string, an anti-contamination measure [readme: `research/raw/repro/readme_idavidrein_gpqa.md`]. Our committed files hold hashes only, never text |

**Gap in the manuscript's data plan (L205).** The released bundle has **no** SimpleQA
records for any of the manuscript's weak or strong models (deliverable 10 §1 [run]).
So SimpleQA must be *generated* for the whole pool. This is the single most expensive
item in §5.

## 3. Router code and baselines

| Dependency | Source | Licence | Install | Reproduction command (from README) | Status for our use |
|---|---|---|---|---|---|
| **RouteLLM** | `lm-sys/RouteLLM`, last push 2024-08-10 | Apache-2.0 [api] | `pip install "routellm[serve,eval]"` or `git clone … && pip install -e .[serve,eval]` [readme] | `python -m routellm.calibrate_threshold --routers mf --strong-model-pct 0.5 --config config.example.yaml`; `python -m routellm.evals.evaluate --routers random sw_ranking bert --benchmark gsm8k --config config.example.yaml` [readme] | usable. The released BERT checkpoint `routellm/bert_gpt4_augmented` has **no licence field** [api: `research/raw/experiment/hf_model_routellm_bert_gpt4_augmented.json`] |
| **RouteLMT** (manuscript baseline, L311) | paper arXiv 2604.22520 (ACL 2026 Industry). The `NiuTrans/LMT` README describes the paper [readme] | repo: **no SPDX field** [api] | n/a | none published | **No router code found.** The full `NiuTrans/LMT` tree has 12 entries: data files plus `src/inference.py` and `src/utils.py` [api: `gh_tree_NiuTrans_LMT.json`]. The manuscript's RouteLMT baseline must be **re-implemented from the paper**, and the paper should say so |
| **ICL-Router** (L313) | `lalalamdbf/ICL-Router`, last push 2025-10-14 | **no SPDX field**, no LICENSE file in the root listing [api] | `pip install -r requirements.txt` [readme] | `sh ./scripts/generate_experts_information.sh`; `sh ./scripts/train_stage1.sh 0,…,8`; `sh ./scripts/train_stage2.sh 0,…,8` ("Multi-GPU: 8-GPU Training") [readme] | code exists. The README's scripts assume 8 GPUs, and evaluation is inside the training script [readme]. Reuse terms [?] |
| **IRT-Router** | `Mercidaiha/IRT-Router`, last push 2025-02-19 | **no SPDX field**, no LICENSE file in the root listing [api] | (no requirements file listed) | `python train_mirt.py`; `python test_router.py --router mirt --emb_name bert --test_path test1 --a 0.8 --lamda 0.3` [readme] | ships `mirt_bert.snapshot` (bert-base-uncased embeddings) and train/test CSVs [readme] |
| **Arch-Router-1.5B** (L317) | HF `katanemo/Arch-Router-1.5B` (base Qwen2.5-1.5B-Instruct, 1,543,714,304 params) | `other` → `katanemo-research` licence [api: `research/raw/experiment/hf_model_katanemo_Arch-Router-1.5B.json`] | `transformers` load | zero-shot prompt (A-zs) | the terms of the research licence need reading before fine-tuning (the manuscript fine-tunes it, L317). The serving repo `katanemo/archgw` now redirects to `katanemo/plano` (Apache-2.0) [api] |
| BEST-Route (optional) | `microsoft/best-route-llm`, last push 2026-07-02 | MIT [api] | `pip install -r requirements.txt` [readme] | see README | option-D relevant, not in the minimum experiment |
| DeBERTa-v3-small (B-s) | HF `microsoft/deberta-v3-small` | MIT [api: `research/raw/experiment/`] | `transformers` | fine-tune script (to be written) | not run |
| ModernBERT-base (B-m) | HF `answerdotai/ModernBERT-base`, 149.7M params | Apache-2.0 [api] | `transformers` (minimum version [?]) | same | not run |
| Qwen2.5-0.5B-Instruct (A) | HF `Qwen/Qwen2.5-0.5B-Instruct`, 494M params | Apache-2.0 [api] | `transformers` + `peft` | LoRA script (to be written) | not run |

## 4. Jacobi-related code (ablation / option E-J only)

| Dependency | Source | Licence | Install | Commands | Hardware |
|---|---|---|---|---|---|
| **JacobiForcing** | `hao-ai-lab/JacobiForcing`, last push 2026-02-20; LICENSE file present | Apache-2.0 [api] | `conda create -n jacobi_forcing python=3.12 -y`; `git clone …`; `pip install -r requirements.txt` [readme] | trajectories: `bash generate_trajectory/generation/generate_trajectory_opencodeinstruct_greedy.sh`; training: `bash scripts/train/train_jacobi_forcing_coder_n32.sh`; inference tests: `python inference_engine/tests/test_jacobi_decoding_greedy.py --model-path …` [readme] | GPU-only (FlashAttention, CUDA graphs). The README reports 800–1000 tok/s "on a single GPU" and ~330 vs ~80 tok/s on a B200 [readme; authors' claims, not verified] |
| JacobiForcing checkpoints | HF `JacobiForcing/JacobiForcing_Coder_7B_v1` (7,615,616,512 params), `JacobiForcing/JacobiForcing_Math_7B_v1` | **no licence tag** on either model [api] | `transformers` | as above | ≥ 1 GPU [E]. There are **no sub-7B checkpoints**, so none fits the manuscript's 2–4B edge models. Community fine-tunes (`melhoushi/JacobiForcing_*`) exist but are unvetted [api: `hf_search_JacobiForcing.json`] |
| Consistency LLM (CLLM) | `hao-ai-lab/Consistency_LLM`, last push 2024-11-16 | Apache-2.0 [api] | see repo | not needed for the minimum experiment | — |

Deliverables 6 and 10 give the reasons Jacobi components are **excluded** from the
minimum experiment. This table exists so that the E-J option (Jacobi Forcing on the
edge *generator*) can be costed if the advisor chooses it.

## 5. Model pool named in the manuscript (Stage 1 / 2)

The params column is the HF API `safetensors.total` and counts all stored tensors,
embeddings included. Weight memory at 4-bit ≈ params × 0.5 bytes. That is our
arithmetic [E]; it excludes the KV cache, activations and quantisation overhead.

| Manuscript name (line) | Closest official HF ID found | Licence [api] | Params [api] | 4-bit weights [E] | Discrepancy |
|---|---|---|---|---|---|
| Gemma-4-E2B-A4B (L273), "2B-parameter" | `google/gemma-4-E2B-it` | Apache-2.0 | 5,123,178,051 | ~2.6 GB | **no "-A4B" suffix exists for E2B/E4B/12B**. The only Gemma-4 A4B model is `gemma-4-26B-A4B-it` [api: `hf_search_gemma-4.json`]. "E2B" is an *effective* size; the stored parameter count is 5.1B |
| Gemma-4-E4B-A4B (L275), "4B" | `google/gemma-4-E4B-it` | Apache-2.0 | 7,996,156,490 | ~4.0 GB | same naming problem |
| Gemma-4-12B-A4B (L277) | `google/gemma-4-12B-it` | Apache-2.0 | 11,959,730,224 | ~6.0 GB | same |
| Phi-4-mini-3.8B (L280) | `microsoft/Phi-4-mini-instruct` | MIT | 3,836,021,760 | ~1.9 GB | none |
| Meta-Llama-3.1-8B-Instruct (L282) | `meta-llama/Llama-3.1-8B-Instruct` | llama3.1, **gated** [api: `research/raw/experiment/`] | — | ~4 GB | the only pool model that also appears in LLMRouterBench |
| LLaDA-MoE-7B-A1B-Instruct-Q4 (L286) | `inclusionAI/LLaDA-MoE-7B-A1B-Instruct` (BF16). A Q4 build exists only as community GGUF (e.g. `mradermacher/…-GGUF`) [api] | Apache-2.0 | 7,356,880,896 | ~3.7 GB | "Q4" must name the exact quantised artefact; its GitHub `inclusionAI/LLaDA-MoE` returned 404 [api] |
| Dream-v0-Instruct-7B (L288) | `Dream-org/Dream-v0-Instruct-7B`; code `DreamLM/Dream` (redirected from `HKUNLP/Dream`) | Apache-2.0 (model and repo) | 7,615,616,512 | ~3.8 GB | the README pins `transformers==4.46.2`, `torch==2.5.1` and says it "requires a GPU with at least 20GB memory" [readme]. That is for BF16; whether a 4-bit Dream runs is [?] |
| Fast-dLLM-v2-7B (L290) | `Efficient-Large-Model/Fast_dLLM_v2_7B` (base Qwen2.5-7B-Instruct); code `NVlabs/Fast-dLLM` (Apache-2.0) | Apache-2.0 | BF16 7,615,616,512 (the API's `total` field says 333,312, which is inconsistent) | ~3.8 GB | none on naming |
| **Qwen3-72B-Instruct** (L298) | **none.** The Qwen org has no Qwen3 72B model. Its 72B models are Qwen/Qwen2/Qwen2.5 generations [api: `hf_search_Qwen_author_72B.json`]. Search hits named "Qwen3-72B" are community merges ("Embiggened", GGUF re-uploads) [api: `hf_search_Qwen3-72B.json`] | — | — | — | **the manuscript names a model that does not exist officially.** Candidate replacements: `Qwen/Qwen2.5-72B-Instruct` (licence `qwen`, 72.7B), `Qwen/Qwen3-32B` (Apache-2.0, 32.8B) or `Qwen/Qwen3-235B-A22B-Instruct-2507` (Apache-2.0, 235.1B; the Stage-0 strong model). This is an advisor decision |
| Llama-3.3-70B-Instruct (L300) | `meta-llama/Llama-3.3-70B-Instruct` | llama3.3, **gated (manual approval)** | 70,553,706,496 | ~35 GB | 4-bit weights exceed one 24 GB RTX 3090, so it needs both edge GPUs or a split (L200) [E] |
| Nemotron-3 Nano-30B (L302) | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` (plus FP8/NVFP4 variants) | `other` → NVIDIA Nemotron Open Model License | 31,577,937,344 | ~16 GB | the name should include "A3B" (it is MoE). A separate Nemotron-3-Nano-**4B** also exists; do not confuse the two |
| strong model in Stage 0 | `Qwen/Qwen3-235B-A22B-Instruct-2507` | Apache-2.0 | 235,093,634,560 | ~118 GB | used only through released scores in Stage 0; not runnable on the L200 testbed [E] |

## 6. Hardware needed by stage

| Stage | Work | Minimum hardware | Basis | Available? |
|---|---|---|---|---|
| 0 (done) | stdlib baselines | any CPU | [run] 4m44s on the host | yes |
| 0b | B-s/B-m fine-tuning, A LoRA 0.5B, A-zs inference on 2,432 queries | CPU possible, a GPU is strongly preferred | [E] untimed; A-LoRA on 4 vCPUs is expected to take hours | the host lacks torch and venv; this needs `apt install python3.12-venv` (sudo) or another machine |
| 0c | C-pre probes (8B prefill hidden states) | 1 × ≥ 16–24 GB GPU | [E] from 8B BF16 weights ≈ 16 GB | no |
| 1 | SimpleQA + Stage-0 datasets generated by 8 edge models and the chosen strong models; LLM judge for SimpleQA | L200's 2 × RTX 3090 for the edge models; the strong models need ≥ 48 GB (70B at 4-bit) or API access | [E] from §5 arithmetic. LLMRouterBench reports "~1K GPU hours + $3000 API spend" for its own collection [readme] | not run; the owner of the L200 server must confirm access |
| 2 | Split-LLM testbed: activation bytes per split depth, TTFT/TPOT, cold start, leakage | L200 edge server + a cloud server | the manuscript leaves the cloud spec blank (L200 "…") | not run; the cloud hardware is undefined |
| opt. | JacobiForcing reproduction or E-J | ≥ 1 datacentre GPU | [readme] | no |

## 7. Order of work (our proposal)

1. **Resolve licences first** for anything that will be redistributed or fine-tuned:
   LLMRouterBench (no LICENSE file), ICL-Router, IRT-Router, the RouteLLM BERT
   checkpoint, the Arch-Router research licence, the JacobiForcing checkpoints,
   Llama gating and the Nemotron licence. Using data and models internally for
   research is a different question from redistributing them. Ask the advisor or
   the university which standard applies.
2. **Fix the model list** (§5): the Gemma-4 names, Qwen3-72B and the Nemotron naming.
   Pin the exact HF revision (commit sha) of every model in a config file before
   Stage 1.
3. **Stage 0b** on a machine with torch: B-s, B-m, A, A-zs, and the RouteLLM BERT
   transfer baseline. Reuse `experiments/prototype/splits/` unchanged so results stay
   comparable with the committed baselines.
4. **Stage 1**: generate labels with vLLM or transformers, logging the sampling
   parameters, the judge model and the prompt template. Store per-query scores in the
   LLMRouterBench record format so `stage0.py` can consume them without changes.
5. **Stage 2** only if the advisor keeps the Split-LLM framing (deliverable 10 §6).

## 8. Unresolved / to verify by hand

- Is LLMRouterBench under MIT? The badge says so, but there is no LICENSE file and no
  SPDX field.
- Is RouteLMT's router code released anywhere other than `NiuTrans/LMT`? Only that
  repo was checked.
- The Fast-dLLM-v2 HF `safetensors.total` (333,312) does not match its BF16 count
  (7.6B). This is probably a metadata artefact; not investigated.
- Whether 4-bit builds of the diffusion LMs (LLaDA-MoE, Dream, Fast-dLLM-v2) work
  with their reference decoders. The manuscript asserts 4-bit for all models (L268,
  L295); no source for that was found.
- GPQA/MMLU-Pro/LiveCodeBench licence terms were not checked individually.
- Which Llama-3.1-8B build and prompt template LLMRouterBench used, which Stage 1
  must match if it mixes our labels with released ones.
