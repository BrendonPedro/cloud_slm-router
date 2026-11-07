#!/usr/bin/env python3
"""Dump the GTE-Qwen2-7B embeddings of the 11,467 pool queries to a .npy.

Streams the LLMRouterBench sqlite cache read-only (mode=ro) and keeps only the
pool queries, so peak memory is ~170 MB instead of the whole cache. Row order is
train.jsonl then test.jsonl of seed 42 (the same order run_e1.load_pool uses).
Output: decision/cache/gte_pool.npy (float32, L2-normalised) + gte_pool_meta.json.
"""
import hashlib, json, sqlite3
from pathlib import Path
import numpy as np

LRB = Path.home() / "research" / "LLMRouterBench"
SPLIT = LRB / "baselines/AvengersPro/data/small_models_seed_42/seed42_split0.7"
DB = LRB / "baselines/AvengersPro/cache/gte_qwen2_7b_embeddings.sqlite"
MODEL = "Alibaba-NLP/gte-Qwen2-7B-instruct"
OUT = Path(__file__).resolve().parent / "cache"
OUT.mkdir(exist_ok=True)

queries, keys = [], []
for f in ("train.jsonl", "test.jsonl"):
    for line in (SPLIT / f).open():
        r = json.loads(line)
        queries.append(r["query"]); keys.append([r["dataset"], r["index"]])
pos = {}
for i, q in enumerate(queries):
    pos.setdefault(q, []).append(i)
X = None
seen = np.zeros(len(queries), bool)
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
for t, e in con.execute("SELECT text, embedding FROM embeddings WHERE model = ?", (MODEL,)):
    if t in pos:
        v = np.asarray(json.loads(e), dtype=np.float32)
        if X is None:
            X = np.zeros((len(queries), v.size), np.float32)
        for i in pos[t]:
            X[i] = v; seen[i] = True
con.close()
assert seen.all(), f"missing {(~seen).sum()} embeddings"
X /= np.linalg.norm(X, axis=1, keepdims=True)
np.save(OUT / "gte_pool.npy", X)
h = hashlib.sha256("\n".join(queries).encode()).hexdigest()
(OUT / "gte_pool_meta.json").write_text(json.dumps(
    {"n": len(queries), "dim": int(X.shape[1]), "order": "seed42 train.jsonl then test.jsonl",
     "query_sha256": h, "model": MODEL, "keys": keys}))
print("saved", X.shape, h[:12])
