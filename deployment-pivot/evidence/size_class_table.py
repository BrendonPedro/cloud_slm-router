"""Cached-data check: edge-sized (7-9B) vs remote-sized models on the benchmarks
where LLMRouterBench has BOTH pools. No new inference. Reads per-record score and
completion_tokens from ~/research/LLMRouterBench/results/bench/<bench>/<split>/<model>/*.json
(latest file per model). Prints accuracy, median and p90 completion tokens.

Usage: python3 -I size_class_table.py [LLMRouterBench_root]
"""
import glob, json, os, statistics as st, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/research/LLMRouterBench")
BENCH = [("aime", "hybrid"), ("gpqa", "test"), ("livecodebench", "test"),
         ("livemathbench", "test"), ("mmlupro", "test_1000")]
MODELS = {  # role -> models
    "edge-class (7-9B, open)": ["Qwen3-8B", "DeepSeek-R1-0528-Qwen3-8B",
                                 "NVIDIA-Nemotron-Nano-9B-v2", "Llama-3.1-8B-Instruct"],
    "remote-class (open, large)": ["qwen3-235b-a22b-2507", "qwen3-235b-a22b-no-thinking",
                                   "qwen3-235b-a22b-thinking-2507", "deepseek-v3-0324"],
    "remote-class (API frontier)": ["gpt-5"],
}

def load(b, s, m):
    fs = sorted(glob.glob(os.path.join(ROOT, "results/bench", b, s, m, "*.json")))
    if not fs:
        return None
    return json.load(open(fs[-1]))["records"]

def p90(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.9 * len(xs)))]

print("| benchmark | n | role | model | acc | median out tok | p90 out tok |")
print("|---|---|---|---|---|---|---|")
for b, s in BENCH:
    for role, ms in MODELS.items():
        for m in ms:
            r = load(b, s, m)
            if r is None:
                print(f"| {b} | - | {role} | {m} | NA | NA | NA |")
                continue
            acc = sum(float(x["score"]) for x in r) / len(r)
            toks = [int(x["completion_tokens"]) for x in r]
            print(f"| {b} | {len(r)} | {role} | {m} | {acc:.3f} | {int(st.median(toks))} | {p90(toks)} |")
