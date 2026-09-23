"""Inventory the LLMRouterBench release bundle (bench-release.tar.gz).

Purpose: check which (dataset, model) pairs the manuscript's L205 plan can
actually reuse, and compute simple headroom statistics from the *released*
per-query scores. Nothing here runs a model; every number is derived from
LLMRouterBench's published records.

Usage: python3 inventory_llmrouterbench.py /path/to/extracted/results/bench > inventory.txt
"""
import collections
import glob
import json
import os
import sys

root = sys.argv[1]
pairs = collections.defaultdict(dict)  # dataset -> model -> (n, mean score, {query: score})

for path in sorted(glob.glob(os.path.join(root, "*", "*", "*", "*.json"))):
    rel = os.path.relpath(path, root).split(os.sep)
    dataset, split, model = rel[0], rel[1], rel[2]
    try:
        d = json.load(open(path))
    except Exception as e:  # keep going; report the failure
        print(f"UNREADABLE {path}: {e}")
        continue
    recs = d.get("records", [])
    scores = {}
    for r in recs:
        q = r.get("origin_query") or r.get("prompt")
        s = r.get("score")
        if q is None or s is None:
            continue
        scores[q] = float(s)
    key = f"{dataset}/{split}"
    # If several timestamps exist, keep the one with the most records.
    if key in pairs and model in pairs[key] and pairs[key][model][0] >= len(scores):
        continue
    mean = sum(scores.values()) / len(scores) if scores else float("nan")
    pairs[key][model] = (len(scores), mean, scores)

print("# (dataset/split) -> models with records: n, mean score")
for key in sorted(pairs):
    print(f"\n## {key}  ({len(pairs[key])} models)")
    for model in sorted(pairs[key]):
        n, mean, _ = pairs[key][model]
        print(f"  {model:55s} n={n:5d} mean={mean:.4f}")

# Pairwise edge/strong headroom for a few pre-registered pairs, on the
# intersection of queries both models answered (matched by origin_query).
PAIRS = [
    # (dataset-prefix, weak-model substring, strong-model substring)
    ("mmlu_pro", "Llama-3.1-8B-Instruct", "qwen3-235b-a22b-2507"),
    ("mmlu_pro", "Llama-3.1-8B-Instruct", "deepseek-v3-0324"),
    ("gpqa", "Llama-3.1-8B-Instruct", "qwen3-235b-a22b-2507"),
]
print("\n# Cross-setting pairs (weak from performance pool, strong from performance-cost pool)")
for ds, weak, strong in PAIRS:
    wk = [(k, m) for k in pairs if k.startswith(ds) for m in pairs[k] if weak.lower() in m.lower()]
    st = [(k, m) for k in pairs if k.startswith(ds) for m in pairs[k] if strong.lower() in m.lower()]
    if not wk or not st:
        print(f"{ds}: weak={wk} strong={st} -> pair NOT available")
        continue
    (kw, mw), (ks, ms) = wk[0], st[0]
    a, b = pairs[kw][mw][2], pairs[ks][ms][2]
    common = sorted(set(a) & set(b))
    if not common:
        print(f"{ds}: {mw} [{kw}] vs {ms} [{ks}] -> 0 shared queries")
        continue
    wacc = sum(a[q] for q in common) / len(common)
    sacc = sum(b[q] for q in common) / len(common)
    orac = sum(max(a[q], b[q]) for q in common) / len(common)
    weak_only = sum(1 for q in common if a[q] > b[q])
    strong_needed = sum(1 for q in common if b[q] > a[q])
    print(f"{ds}: {mw} [{kw}] vs {ms} [{ks}] shared={len(common)} "
          f"weak={wacc:.4f} strong={sacc:.4f} oracle={orac:.4f} "
          f"weak>strong={weak_only} strong>weak={strong_needed}")
