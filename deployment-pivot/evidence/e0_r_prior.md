# E0-R prior: SPLIT (Qwen3-32B bf16, U-max) vs quantised edge, no-raw-text, good state

Upper bound on `U_SPLIT − U_EDGE-best` in points. Biased **for** SPLIT (see script docstring). R needs ≥ +3.0 pt at some D ≤ 600 s.

Base data: cached Qwen3-8B (thinking) per-query score + completion tokens, benchmarks weighted as the E0 sample (MMLU-Pro .3, GPQA .3, LiveMathBench .2, LiveCodeBench .2). Base on-time utility at D = ∞: 0.664.

| config | runtime eff | RTT ms | SPLIT len scale | SPLIT tok/s | EDGE model tok/s | D=30 | D=60 | D=120 | D=300 | D=600 | D=1200 | D=1800 | D=∞ | min D passing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 GB, 3090-capped + A100 | 1.0 | 1 | 1.0 | 19.0 | Qwen3-8B-AWQ 98 | -23.1 | -30.5 | -35.0 | -18.4 | -0.8 | +7.9 | +8.4 | +8.4 | 1200 |
| 12 GB, 3090-capped + A100 | 1.0 | 1 | 0.7 | 19.0 | Qwen3-8B-AWQ 98 | -18.8 | -24.5 | -27.4 | -8.9 | +5.6 | +8.4 | +8.4 | +8.4 | 600 |
| 12 GB, 3090-capped + A100 | 1.0 | 20 | 1.0 | 13.9 | Qwen3-8B-AWQ 98 | -25.0 | -35.4 | -40.6 | -27.6 | -8.0 | +5.8 | +8.0 | +8.4 | 1200 |
| 12 GB, 3090-capped + A100 | 1.0 | 20 | 0.7 | 13.9 | Qwen3-8B-AWQ 98 | -22.5 | -29.7 | -34.0 | -16.5 | +0.3 | +8.0 | +8.4 | +8.4 | 1200 |
| 12 GB, 3090-capped + A100 | 0.6 | 1 | 1.0 | 11.4 | Qwen3-8B-AWQ 59 | -16.6 | -24.8 | -32.3 | -31.4 | -12.7 | +2.9 | +7.2 | +8.4 | 1800 |
| 12 GB, 3090-capped + A100 | 0.6 | 1 | 0.7 | 11.4 | Qwen3-8B-AWQ 59 | -15.9 | -19.6 | -25.8 | -20.8 | -5.1 | +6.8 | +8.4 | +8.4 | 1200 |
| 12 GB, 3090-capped + A100 | 0.6 | 20 | 1.0 | 8.4 | Qwen3-8B-AWQ 59 | -16.7 | -28.2 | -37.3 | -39.0 | -21.6 | -4.3 | +4.8 | +8.4 | 1800 |
| 12 GB, 3090-capped + A100 | 0.6 | 20 | 0.7 | 8.4 | Qwen3-8B-AWQ 59 | -16.6 | -24.3 | -31.5 | -30.0 | -12.2 | +3.7 | +7.8 | +8.4 | 1200 |
| 16 GB, 3090-capped + A100 | 1.0 | 1 | 1.0 | 17.8 | Qwen3-14B-AWQ 61 | -16.0 | -19.7 | -24.9 | -18.0 | -2.9 | +7.8 | +8.4 | +8.4 | 1200 |
| 16 GB, 3090-capped + A100 | 1.0 | 1 | 0.7 | 17.8 | Qwen3-14B-AWQ 61 | -12.2 | -13.3 | -17.2 | -8.8 | +4.9 | +8.4 | +8.4 | +8.4 | 600 |
| 16 GB, 3090-capped + A100 | 1.0 | 20 | 1.0 | 13.3 | Qwen3-14B-AWQ 61 | -17.5 | -24.2 | -30.1 | -27.0 | -9.0 | +5.5 | +8.0 | +8.4 | 1200 |
| 16 GB, 3090-capped + A100 | 1.0 | 20 | 0.7 | 13.3 | Qwen3-14B-AWQ 61 | -15.5 | -18.3 | -23.8 | -16.5 | -0.6 | +7.9 | +8.4 | +8.4 | 1200 |
| 16 GB, 3090-capped + A100 | 0.6 | 1 | 1.0 | 10.7 | Qwen3-14B-AWQ 37 | -10.0 | -16.6 | -21.3 | -26.2 | -13.6 | +1.6 | +6.7 | +8.4 | 1800 |
| 16 GB, 3090-capped + A100 | 0.6 | 1 | 0.7 | 10.7 | Qwen3-14B-AWQ 37 | -9.4 | -11.9 | -14.3 | -15.8 | -5.7 | +6.5 | +8.0 | +8.4 | 1200 |
| 16 GB, 3090-capped + A100 | 0.6 | 20 | 1.0 | 8.0 | Qwen3-14B-AWQ 37 | -10.1 | -19.6 | -25.8 | -32.6 | -22.4 | -5.2 | +3.9 | +8.4 | 1800 |
| 16 GB, 3090-capped + A100 | 0.6 | 20 | 0.7 | 8.0 | Qwen3-14B-AWQ 37 | -10.0 | -16.1 | -20.0 | -24.6 | -12.1 | +2.9 | +7.4 | +8.4 | 1800 |
| 24 GB, 3090 + A100 | 1.0 | 1 | 1.0 | 16.0 | Qwen3-14B-AWQ 61 | -16.9 | -21.1 | -26.6 | -21.1 | -5.2 | +6.7 | +8.4 | +8.4 | 1200 |
| 24 GB, 3090 + A100 | 1.0 | 1 | 0.7 | 16.0 | Qwen3-14B-AWQ 61 | -13.4 | -15.3 | -20.4 | -10.7 | +2.9 | +8.0 | +8.4 | +8.4 | 1200 |
| 24 GB, 3090 + A100 | 1.0 | 20 | 1.0 | 12.3 | Qwen3-14B-AWQ 61 | -17.5 | -25.0 | -31.8 | -29.6 | -11.9 | +4.4 | +7.8 | +8.4 | 1200 |
| 24 GB, 3090 + A100 | 1.0 | 20 | 0.7 | 12.3 | Qwen3-14B-AWQ 61 | -16.2 | -20.0 | -25.2 | -18.4 | -3.2 | +7.6 | +8.4 | +8.4 | 1200 |
| 24 GB, 3090 + A100 | 0.6 | 1 | 1.0 | 9.6 | Qwen3-14B-AWQ 37 | -10.1 | -18.1 | -22.9 | -28.4 | -17.6 | -0.5 | +6.0 | +8.4 | 1800 |
| 24 GB, 3090 + A100 | 0.6 | 1 | 0.7 | 9.6 | Qwen3-14B-AWQ 37 | -9.9 | -13.7 | -16.9 | -19.2 | -8.0 | +5.7 | +8.0 | +8.4 | 1200 |
| 24 GB, 3090 + A100 | 0.6 | 20 | 1.0 | 7.4 | Qwen3-14B-AWQ 37 | -10.1 | -20.0 | -26.9 | -34.1 | -25.4 | -6.8 | +2.0 | +8.4 | ∞ |
| 24 GB, 3090 + A100 | 0.6 | 20 | 0.7 | 7.4 | Qwen3-14B-AWQ 37 | -10.0 | -17.0 | -21.5 | -26.5 | -14.0 | +1.5 | +6.5 | +8.4 | 1800 |
| 16 GB, 4090 Laptop + A100 | 1.0 | 1 | 1.0 | 14.9 | Qwen3-14B-AWQ 38 | -9.9 | -12.5 | -15.8 | -17.2 | -6.2 | +6.4 | +8.0 | +8.4 | 1200 |
| 16 GB, 4090 Laptop + A100 | 1.0 | 1 | 0.7 | 14.9 | Qwen3-14B-AWQ 38 | -6.7 | -7.0 | -9.5 | -6.0 | +2.1 | +8.0 | +8.4 | +8.4 | 1200 |
| 16 GB, 4090 Laptop + A100 | 1.0 | 20 | 1.0 | 11.6 | Qwen3-14B-AWQ 38 | -10.3 | -16.2 | -20.6 | -24.6 | -11.9 | +3.5 | +7.6 | +8.4 | 1200 |
| 16 GB, 4090 Laptop + A100 | 1.0 | 20 | 0.7 | 11.6 | Qwen3-14B-AWQ 38 | -9.5 | -10.8 | -14.0 | -13.6 | -3.9 | +7.2 | +8.4 | +8.4 | 1200 |
| 16 GB, 4090 Laptop + A100 | 0.6 | 1 | 1.0 | 9.0 | Qwen3-14B-AWQ 23 | -3.7 | -11.3 | -12.8 | -20.0 | -15.1 | -2.2 | +5.5 | +8.4 | 1800 |
| 16 GB, 4090 Laptop + A100 | 0.6 | 1 | 0.7 | 9.0 | Qwen3-14B-AWQ 23 | -3.6 | -7.3 | -6.5 | -10.9 | -5.9 | +5.4 | +7.9 | +8.4 | 1200 |
| 16 GB, 4090 Laptop + A100 | 0.6 | 20 | 1.0 | 7.0 | Qwen3-14B-AWQ 23 | -3.7 | -12.6 | -16.4 | -24.5 | -22.7 | -7.6 | +1.4 | +8.4 | ∞ |
| 16 GB, 4090 Laptop + A100 | 0.6 | 20 | 0.7 | 7.0 | Qwen3-14B-AWQ 23 | -3.7 | -10.1 | -10.8 | -16.9 | -11.6 | +0.7 | +6.4 | +8.4 | 1800 |
| 12 GB, 3090-capped + H100 | 1.0 | 1 | 1.0 | 27.0 | Qwen3-8B-AWQ 98 | -18.8 | -24.5 | -27.5 | -8.9 | +5.6 | +8.4 | +8.4 | +8.4 | 600 |
| 12 GB, 3090-capped + H100 | 1.0 | 1 | 0.7 | 27.0 | Qwen3-8B-AWQ 98 | -13.0 | -18.2 | -16.9 | -0.3 | +7.9 | +8.4 | +8.4 | +8.4 | 600 |
| 12 GB, 3090-capped + H100 | 1.0 | 20 | 1.0 | 17.9 | Qwen3-8B-AWQ 98 | -23.7 | -31.8 | -36.0 | -19.9 | -2.9 | +7.8 | +8.4 | +8.4 | 1200 |
| 12 GB, 3090-capped + H100 | 1.0 | 20 | 0.7 | 17.9 | Qwen3-8B-AWQ 98 | -19.8 | -25.4 | -28.3 | -10.7 | +4.9 | +8.4 | +8.4 | +8.4 | 600 |
| 12 GB, 3090-capped + H100 | 0.6 | 1 | 1.0 | 16.2 | Qwen3-8B-AWQ 59 | -15.9 | -19.6 | -25.8 | -20.8 | -5.1 | +6.7 | +8.4 | +8.4 | 1200 |
| 12 GB, 3090-capped + H100 | 0.6 | 1 | 0.7 | 16.2 | Qwen3-8B-AWQ 59 | -12.4 | -13.9 | -19.2 | -10.5 | +3.4 | +8.0 | +8.4 | +8.4 | 600 |
| 12 GB, 3090-capped + H100 | 0.6 | 20 | 1.0 | 10.7 | Qwen3-8B-AWQ 59 | -16.6 | -25.3 | -33.5 | -33.0 | -14.2 | +1.6 | +6.7 | +8.4 | 1800 |
| 12 GB, 3090-capped + H100 | 0.6 | 20 | 0.7 | 10.7 | Qwen3-8B-AWQ 59 | -16.1 | -20.5 | -26.5 | -22.6 | -6.3 | +6.5 | +8.0 | +8.4 | 1200 |

Rows where the upper bound reaches +3.0 pt at some D ≤ 600 s: 6/40.
Of the rows with runtime eff 0.6 and unscaled SPLIT length: 0/10.

## Readings (hand-written 2026-11-07; re-check if the script changes)

1. **Within E0's frozen deadline sweep (D ≤ 600 s), thinking-mode SPLIT clears +3.0 pt in only 6/40 rows,
   all at D = 600 s, and only with roofline speed plus a 30% shorter 32B trace, or an H100 server.**
   At the more realistic 0.6 runtime efficiency with unscaled lengths: **0/10**. This is an *upper bound*
   (extra correct answers placed on exactly the on-time base-wrong queries; edge denied its 14B uplift;
   zero serialisation). So the pre-registered prior for E0-R in thinking mode is **likely FAIL**.
2. **SPLIT's thinking-mode quality tier appears only at D ≥ 1200–1800 s**, i.e. for latency-insensitive
   (asynchronous / batch) `no-raw-text` traffic. There the decision is trivial ("use the largest
   admissible model"), so it is not an optimiser regime and does not rescue H-joint.
3. **Cause:** thinking traces (Qwen3-8B median 1.9k–9.5k tokens on these benchmarks) × a SPLIT
   rate of 7–27 tok/s versus an edge quantised model at 23–98 tok/s. The 3–8× speed gap costs more
   on-time answers than the +4.5–8.4 pt vendor quality gap can buy back.
4. **A gap the frozen E0 did not cover: non-thinking mode.** Vendor non-thinking Qwen3-32B bf16
   (LiveBench 59.8 / GPQA 54.6 / MMLU-Redux 85.7) is below *thinking* 8B-AWQ (65.5 / 59.0 / 86.4)
   but far above *non-thinking* 8B-AWQ (48.9 / 35.9 / 79.1; +12.1 mean). Non-thinking outputs are
   short (hundreds of tokens), so a non-thinking SPLIT could plausibly win the **12 GB class at
   D = 30–60 s**, where thinking edge traces do not finish. No cached per-query data exist for
   Qwen3-8B/32B non-thinking, so this cannot be bounded here. E0 §3.1/§4.3 were amended
   (pre-hardware) to add mode as a model variant.
