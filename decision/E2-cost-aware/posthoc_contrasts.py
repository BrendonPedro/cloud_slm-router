#!/usr/bin/env python3
"""E2 post-hoc (NOT pre-registered): paired contrasts between query-level routers and
the cluster lookup R6, plus a per-benchmark and per-model decomposition of R4 vs R2.

Reads results/e2_choices.npz (written by run_e2.py) and the LLMRouterBench pool via
the E1 loaders (read-only). Writes results/e2_posthoc.json and prints a summary.

  ~/research/LLMRouterBench/.venv/bin/python -B decision/E2-cost-aware/posthoc_contrasts.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "E1-pool-headroom"))
import run_e1 as e1  # noqa: E402

CONTRASTS = [("R4_factored", "R6_cluster_lookup"), ("R4s_factored_s_only", "R6_cluster_lookup"),
             ("R5_knn50", "R6_cluster_lookup"), ("R4_factored", "R5_knn50"),
             ("R4s_factored_s_only", "R4_factored"), ("R6_cluster_lookup", "R2_task_lookup")]
DECOMP_LAMBDAS = [0.01, 0.02, 0.03, 0.05]


def main():
    df, S, T, models = e1.load_pool()
    T = T / 1000.0
    z = np.load(HERE / "results" / "e2_choices.npz")
    lambdas = [float(x) for x in z["lambdas"]]
    fold = z["fold"]
    assert (fold == df["fold"].to_numpy()).all()
    task = df["dataset"].to_numpy()
    N = len(df)
    rows = np.arange(N)
    boot = np.random.default_rng(0).integers(0, N, size=(2000, N))
    folds = sorted(np.unique(fold))
    out = {"contrasts": {}, "per_benchmark": {}, "model_share": {}}
    for a, b in CONTRASTS:
        key = f"{a} - {b}"
        out["contrasts"][key] = []
        for li, lam in enumerate(lambdas):
            U = S - lam * T
            d = U[rows, z[a][li]] - U[rows, z[b][li]]
            bs = d[boot].mean(1)
            fd = [float(d[fold == k].mean()) for k in folds]
            out["contrasts"][key].append({
                "lambda": lam, "dU_pt": 100 * float(d.mean()),
                "ci95_pt": [100 * float(np.percentile(bs, 2.5)), 100 * float(np.percentile(bs, 97.5))],
                "folds_pos": int(sum(x > 0 for x in fd))})
    for lam in DECOMP_LAMBDAS:
        li = lambdas.index(lam)
        U = S - lam * T
        c2, c4 = z["R2_task_lookup"][li], z["R4_factored"][li]
        per = {}
        for t in sorted(np.unique(task)):
            m = task == t
            per[t] = {"n": int(m.sum()),
                      "dU_pt": 100 * float((U[rows, c4] - U[rows, c2])[m].mean()),
                      "dacc_pt": 100 * float((S[rows, c4] - S[rows, c2])[m].mean()),
                      "R2_ktok": float(T[rows, c2][m].mean()), "R4_ktok": float(T[rows, c4][m].mean())}
        out["per_benchmark"][str(lam)] = per
        share = {}
        for r, c in (("R2_task_lookup", c2), ("R4_factored", c4),
                     ("R6_cluster_lookup", z["R6_cluster_lookup"][li])):
            cnt = np.bincount(c.astype(int), minlength=len(models)) / N
            share[r] = {models[i]: round(float(cnt[i]), 4) for i in np.argsort(-cnt) if cnt[i] >= 0.01}
        out["model_share"][str(lam)] = share
    (HERE / "results" / "e2_posthoc.json").write_text(json.dumps(out, indent=1))
    for key, v in out["contrasts"].items():
        print(key)
        for x in v:
            print("  lam=%.3f dU=%+.2f [%+.2f, %+.2f] folds+=%d" % (x["lambda"], x["dU_pt"], *x["ci95_pt"], x["folds_pos"]))
    for lam, per in out["per_benchmark"].items():
        print(f"R4 - R2 per benchmark at lambda={lam}:")
        for t, x in sorted(per.items(), key=lambda kv: -kv[1]["dU_pt"] * kv[1]["n"]):
            print("  %-14s n=%5d dU=%+6.2f dacc=%+6.2f tok %.2f -> %.2f" % (t, x["n"], x["dU_pt"], x["dacc_pt"], x["R2_ktok"], x["R4_ktok"]))
    print(json.dumps(out["model_share"], indent=1))


if __name__ == "__main__":
    main()
