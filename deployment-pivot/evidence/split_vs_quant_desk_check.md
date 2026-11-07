Edge memory class vs best fully edge-resident Qwen3 variant (KV for 16384 tokens + 1.5 GB overhead).

| name | ckpt GB | need GB @16k ctx |
|---|---|---|
| Qwen3-8B-AWQ | 6.1 | 10.0 |
| Qwen3-8B | 16.4 | 20.3 |
| Qwen3-14B-AWQ | 10.0 | 14.2 |
| Qwen3-14B | 29.5 | 33.7 |
| Qwen3-32B-AWQ | 19.3 | 25.1 |
| Qwen3-32B | 65.5 | 71.3 |

| edge mem GB | best edge-resident (mean score) | 32B-bf16 split gain per bench (LiveBench/GPQA/MMLU-R/AIME24) | mean gain | max gain | 32B layers on edge in U-split |
|---|---|---|---|---|---|
| 8 | none | - | - | - | 3 |
| 12 | Qwen3-8B-AWQ (70.5) | +9.4 / +9.4 / +4.5 / +10.1 | +8.4 | +10.1 | 7/64 |
| 16 | Qwen3-14B-AWQ (74.4) | +4.9 / +6.3 / +2.4 / +4.4 | +4.5 | +6.3 | 10/64 |
| 24 | Qwen3-14B-AWQ (74.4) | +4.9 / +6.3 / +2.4 / +4.4 | +4.5 | +6.3 | 18/64 |
| 32 | Qwen3-32B-AWQ (78.1) | +1.8 / -0.6 / +0.1 / +2.0 | +0.8 | +2.0 | 26/64 |
| 48 | Qwen3-32B-AWQ (78.1) | +1.8 / -0.6 / +0.1 / +2.0 | +0.8 | +2.0 | 41/64 |

Activation crossing per generated token at a 32B cut: hidden 5120 x 2 B = 10 KB (bf16), each direction in a U-split.
Reading: a split of 32B bf16 can only add quality over the edge when the edge cannot hold 32B-AWQ (about 25 GB with a 16k KV cache). At >= 32 GB the best edge-resident model already reaches 32B quality within vendor noise, so SPLIT has no quality regime there; it remains only as a latency/capacity option, which every measured study finds it loses to REMOTE.
