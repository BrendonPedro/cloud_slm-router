"""Inventory the LLMRouterBench release bundle (bench-release.tar.gz).

Purpose: check which (dataset, model) pairs the manuscript's L205 plan can
actually reuse, and compute simple headroom statistics from the *released*
per-query scores. Nothing here runs a model; every number is derived from
LLMRouterBench's published records.

Revision (iteration 11): the bundle's directory depth is not uniform
(e.g. arenahard/<model>/<file>.json vs mmlupro/test_1000/<model>/<file>.json),
so dataset/split/model are read from each file's own metadata fields
(dataset_name, split, model_name) instead of from the path.

Usage: python3 inventory_llmrouterbench.py /path/to/bench-release > inventory.txt
"""
import collections
import json
import os
import sys

root = sys.argv[1]
# (dataset, split) -> model -> dict(n, mean, cost, ctok, scores{query: score}, file)
pairs = collections.defaultdict(dict)
unreadable = []

for dirpath, _, files in os.walk(root):
    for fn in sorted(files):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(dirpath, fn)
        try:
            d = json.load(open(path))
        except Exception as e:  # keep going; report the failure
            unreadable.append(f"{path}: {e}")
            continue
        dataset, split, model = d.get("dataset_name"), d.get("split"), d.get("model_name")
        scores, ctok = {}, 0
        for r in d.get("records", []):
            q = r.get("origin_query") or r.get("prompt")
            s = r.get("score")
            if q is None or s is None:
                continue
            try:
                scores[q] = float(s)
                ctok += int(float(r.get("completion_tokens") or 0))
            except (TypeError, ValueError):
                continue
        key = (dataset, split)
        # If several files exist for one (dataset, split, model), keep the one with most records.
        if model in pairs[key] and pairs[key][model]["n"] >= len(scores):
            continue
        n = len(scores)
        pairs[key][model] = dict(
            n=n,
            mean=sum(scores.values()) / n if n else float("nan"),
            cost=float(d.get("cost") or 0.0),
            ctok=ctok / n if n else float("nan"),
            scores=scores,
            file=os.path.relpath(path, root),
        )

print(f"# root={root}")
print(f"# unreadable files: {len(unreadable)}")
for u in unreadable:
    print(f"#   {u}")
print("# (dataset, split) -> models: n, mean score, total cost (USD, as released), mean completion tokens")
for key in sorted(pairs, key=str):
    print(f"\n## {key[0]} / {key[1]}  ({len(pairs[key])} models)")
    for model in sorted(pairs[key]):
        p = pairs[key][model]
        print(f"  {model:40s} n={p['n']:5d} mean={p['mean']:.4f} cost={p['cost']:9.3f} ctok={p['ctok']:8.1f}")

# Pre-registered weak/strong pairs. Weak = the manuscript's Llama-3.1-8B-Instruct (L208)
# and Qwen3-8B (closest open 8B in the pool). Strong = a set of flagship models.
WEAK = ["Llama-3.1-8B-Instruct", "Qwen3-8B"]
STRONG = ["qwen3-235b-a22b-2507", "deepseek-v3-0324", "gpt-5", "gemini-2.5-flash"]
print("\n# Weak/strong headroom on shared queries (matched by origin_query).")
print("# weak=acc of weak; strong=acc of strong; oracle=mean max(weak,strong);")
print("# need_strong = share of queries where strong > weak (upper bound on queries routing can fix);")
print("# weak_better = share where weak > strong.")
print(f"{'dataset/split':28s} {'weak':24s} {'strong':22s} {'shared':>6s} {'weak':>6s} {'strong':>6s} {'oracle':>6s} {'need_strong':>11s} {'weak_better':>11s}")
for key in sorted(pairs, key=str):
    for w in WEAK:
        for s in STRONG:
            if w not in pairs[key] or s not in pairs[key]:
                continue
            a, b = pairs[key][w]["scores"], pairs[key][s]["scores"]
            common = sorted(set(a) & set(b))
            if not common:
                print(f"{key[0]+'/'+key[1]:28s} {w:24s} {s:22s} 0 shared queries")
                continue
            m = len(common)
            wacc = sum(a[q] for q in common) / m
            sacc = sum(b[q] for q in common) / m
            orac = sum(max(a[q], b[q]) for q in common) / m
            need = sum(1 for q in common if b[q] > a[q]) / m
            wb = sum(1 for q in common if a[q] > b[q]) / m
            print(f"{key[0]+'/'+key[1]:28s} {w:24s} {s:22s} {m:6d} {wacc:6.3f} {sacc:6.3f} {orac:6.3f} {need:11.3f} {wb:11.3f}")

print("\n# Availability of the manuscript's named pool members (L205-L210) per (dataset, split):")
for name in ["Llama-3.1-8B-Instruct", "Qwen3-8B", "gemma-2-9b-it"]:
    have = sorted(f"{k[0]}/{k[1]}" for k in pairs if name in pairs[k])
    print(f"  {name}: {len(have)} splits -> {', '.join(have)}")
simple = sorted(m for k in pairs if k[0] == "simpleqa" for m in pairs[k])
print(f"  simpleqa models (all splits): {sorted(set(simple))}")
