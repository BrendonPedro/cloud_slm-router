"""Desk check before E0: does weight quantisation make SPLIT pointless?

For each edge accelerator memory class, find the best Qwen3 variant that fits fully on
the edge, and compare its vendor-reported quality with Qwen3-32B bf16. A lossless
fp16/bf16 split of 32B would deliver the bf16 quality.

Sources (fetched 2026-11-07):
- checkpoint sizes and configs: huggingface.co/api/models/Qwen/<name> and config.json
- thinking-mode scores: model cards huggingface.co/Qwen/Qwen3-{8B,14B,32B}-AWQ, table
  "Performance" (bf16 vs AWQ-int4). These are vendor numbers from one eval harness
  and are not our measurements. They are used only to locate the regime, not to
  size an effect.

Run: python3 split_vs_quant_desk_check.py > split_vs_quant_desk_check.md
"""

GB = 1e9
CTX = 16384            # context the edge must hold KV for (tokens); thinking traces are long
RUNTIME_OVERHEAD = 1.5  # GB: CUDA context, activations, allocator slack (assumed)

# name: (checkpoint GB, layers, kv_heads, head_dim, {bench: score})
BENCH = ["LiveBench", "GPQA", "MMLU-Redux", "AIME24"]
MODELS = {
    "Qwen3-8B-AWQ":  (6.1, 36, 8, 128, dict(zip(BENCH, [65.5, 59.0, 86.4, 71.3]))),
    "Qwen3-8B":      (16.4, 36, 8, 128, dict(zip(BENCH, [67.1, 62.0, 87.5, 76.0]))),
    "Qwen3-14B-AWQ": (10.0, 40, 8, 128, dict(zip(BENCH, [70.0, 62.1, 88.5, 77.0]))),
    "Qwen3-14B":     (29.5, 40, 8, 128, dict(zip(BENCH, [71.3, 64.0, 88.6, 79.3]))),
    "Qwen3-32B-AWQ": (19.3, 64, 8, 128, dict(zip(BENCH, [73.1, 69.0, 90.8, 79.4]))),
    "Qwen3-32B":     (65.5, 64, 8, 128, dict(zip(BENCH, [74.9, 68.4, 90.9, 81.4]))),
}
SPLIT_REF = "Qwen3-32B"  # bf16; a lossless split delivers these scores


def kv_gb(layers, kv_heads, head_dim, ctx=CTX, bytes_=2):
    return layers * kv_heads * head_dim * 2 * bytes_ * ctx / GB  # K and V


def need_gb(name):
    w, L, kvh, hd, _ = MODELS[name]
    return w + kv_gb(L, kvh, hd) + RUNTIME_OVERHEAD


def split_prefix_layers(mem):
    """Layers of 32B bf16 an edge can hold in a U-shaped split (embedding + head local)."""
    w, L, kvh, hd, _ = MODELS[SPLIT_REF]
    emb_head = 2 * 151936 * 5120 * 2 / GB      # untied embedding + lm_head, bf16
    per_layer = (w - emb_head) / L + kv_gb(1, kvh, hd)
    free = mem - RUNTIME_OVERHEAD - emb_head
    return max(0, min(L, int(free // per_layer)))


def main():
    print("Edge memory class vs best fully edge-resident Qwen3 variant "
          f"(KV for {CTX} tokens + {RUNTIME_OVERHEAD} GB overhead).\n")
    print("| name | ckpt GB | need GB @16k ctx |")
    print("|---|---|---|")
    for n in MODELS:
        print(f"| {n} | {MODELS[n][0]:.1f} | {need_gb(n):.1f} |")
    print()
    ref = MODELS[SPLIT_REF][4]
    print("| edge mem GB | best edge-resident (mean score) | 32B-bf16 split gain per bench "
          "(LiveBench/GPQA/MMLU-R/AIME24) | mean gain | max gain | 32B layers on edge in U-split |")
    print("|---|---|---|---|---|---|")
    for mem in [8, 12, 16, 24, 32, 48]:
        fits = [n for n in MODELS if need_gb(n) <= mem]
        if not fits:
            print(f"| {mem} | none | - | - | - | {split_prefix_layers(mem)} |")
            continue
        best = max(fits, key=lambda n: sum(MODELS[n][4].values()))
        s = MODELS[best][4]
        gains = [ref[b] - s[b] for b in BENCH]
        mean_s = sum(s.values()) / len(s)
        print(f"| {mem} | {best} ({mean_s:.1f}) | {' / '.join(f'{g:+.1f}' for g in gains)} | "
              f"{sum(gains)/len(gains):+.1f} | {max(gains):+.1f} | {split_prefix_layers(mem)}/64 |")
    print()
    print("Activation crossing per generated token at a 32B cut: hidden 5120 x 2 B = 10 KB "
          "(bf16), each direction in a U-split.")
    print("Reading: a split of 32B bf16 can only add quality over the edge when the edge cannot "
          "hold 32B-AWQ (about 25 GB with a 16k KV cache). At >= 32 GB the best edge-resident "
          "model already reaches 32B quality within vendor noise, so SPLIT has no quality "
          "regime there; it remains only as a latency/capacity option, which every measured "
          "study finds it loses to REMOTE.")


if __name__ == "__main__":
    main()
