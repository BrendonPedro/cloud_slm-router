# Qwen3 vendor numbers used by evidence/split_vs_quant_desk_check.py (fetched 2026-11-07)

Vendor-reported; not our measurements.

## Model cards: bf16 vs AWQ-int4 (huggingface.co/Qwen/<name>/raw/main/README.md, section Performance)

### Qwen3-8B-AWQ
| Mode | QUANTIZATION TYPE | LiveBench 2024-11-25 | GPQA | MMLU-Redux | AIME24 |
| --- | --- | --- | --- | --- | --- |
| Thinking | bf16 | 67.1 | 62.0 | 87.5 | 76.0 |
| Thinking | AWQ-int4 | 65.5 | 59.0 | 86.4 | 71.3 |
| Non-Thinking | bf16 | 53.5 | 39.3 | 79.5 | - |
| Non-Thinking | AWQ-int4 | 48.9 | 35.9 | 79.1 | - |

### Qwen3-14B-AWQ
| Mode | QUANTIZATION TYPE | LiveBench 2024-11-25 | GPQA | MMLU-Redux | AIME24 |
| --- | --- | --- | --- | --- | --- |
| Thinking | bf16 | 71.3 | 64.0 | 88.6 | 79.3 |
| Thinking | AWQ-int4 | 70.0 | 62.1 | 88.5 | 77.0 |
| Non-Thinking | bf16 | 59.6 | 54.8 | 82.0 | - |
| Non-Thinking | AWQ-int4 | 57.4 | 53.8 | 81.5 | - |

### Qwen3-32B-AWQ
| Mode | QUANTIZATION TYPE | LiveBench 2024-11-25 | GPQA | MMLU-Redux | AIME24 |
| --- | --- | --- | --- | --- | --- |
| Thinking | bf16 | 74.9 | 68.4 | 90.9 | 81.4 |
| Thinking | AWQ-int4 | 73.1 | 69.0 | 90.8 | 79.4 |
| Non-Thinking | bf16 | 59.8 | 54.6 | 85.7 | - |
| Non-Thinking | AWQ-int4 | 59.8 | 53.1 | 85.6 | - |

Model card guidance (line 130): thinking mode uses T=0.6, TopP=0.95, TopK=20, MinP=0; "DO NOT use greedy decoding, as it can lead to performance degradation and endless repetitions."

## Qwen3 Technical Report (arXiv 2505.09388v1, HTML), thinking-mode tables, Qwen3 columns only

| Bench | Qwen3-8B (T17) | Qwen3-14B (T15) | Qwen3-32B (T13) | Qwen3-30B-A3B (T15) |
|---|---|---|---|---|
| MMLU-Redux | 87.5 | 88.6 | 90.9 | 89.5 |
| GPQA-Diamond | 62.0 | 64.0 | 68.4 | 65.8 |
| AIME'24 | 76.0 | 79.3 | 81.4 | 80.4 |
| AIME'25 | 67.3 | 70.4 | 72.9 | 70.9 |
| LiveCodeBench v5 | 57.5 | 63.5 | 65.7 | 62.6 |
| MATH-500 | 97.4 | 96.8 | 97.2 | 98.0 |

## Checkpoint sizes / configs (HF API, safetensors total)

Qwen3-32B 65.5 GB, 64 layers, hidden 5120, 8 KV heads x 128; -AWQ 19.3 GB.
Qwen3-14B 29.5 GB, 40 layers, hidden 5120; -AWQ 10.0 GB.
Qwen3-8B 16.4 GB, 36 layers, hidden 4096; -AWQ 6.1 GB.
