#!/usr/bin/env python3
"""E1: query-level semantic routing vs task lookup on the 20-model pool.

Implements PREREG.md exactly. It reads LLMRouterBench read-only (data, folds,
GTE cache, loader functions) and writes only under this directory's results/.
Run with the LLMRouterBench venv:

  ~/research/LLMRouterBench/.venv/bin/python -B run_e1.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeClassifier, RidgeCV

LRB = Path.home() / "research" / "LLMRouterBench"
sys.dont_write_bytecode = True
sys.path.insert(0, str(LRB / "diagnostics" / "scripts"))
import run_cv_eval as cv  # noqa: E402  (read-only import: paths + loaders)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)

ALPHAS = (0.1, 1.0, 10.0, 100.0)
K_NN = 50
N_BOOT = 2000
DS, QWEN = cv.DS, cv.QWEN


def load_pool():
    d = cv.split_dir(cv.SOURCE_SEED)
    rows = []
    for f in ("train.jsonl", "test.jsonl"):
        with (d / f).open() as fh:
            for line in fh:
                x = json.loads(line)
                rows.append(x)
    models = sorted(rows[0]["records"])
    df = pd.DataFrame({
        "row": np.arange(len(rows)),
        "dataset": [r["dataset"] for r in rows],
        "index": [r["index"] for r in rows],
        "query": [r["query"] for r in rows],
    })
    S = np.array([[r["records"][m] for m in models] for r in rows], dtype=float)
    T = np.array([[r["usages"][m]["completion_tokens"] for m in models] for r in rows], dtype=float)
    folds = pd.read_csv(cv.OUT / "fold_assignments.csv")[["dataset", "index", "fold"]]
    df = df.merge(folds, on=["dataset", "index"], how="inner").sort_values("row").reset_index(drop=True)
    assert (df["row"].to_numpy() == np.arange(len(rows))).all(), "fold join lost or reordered rows"
    return df, S, T, models


def argmax_tiebreak(P, order_key):
    """argmax over columns; ties broken by order_key (higher first) then column index."""
    # add a tiny, strictly ordered epsilon derived from rank of order_key
    rank = np.argsort(np.argsort(-order_key, kind="stable"), kind="stable")  # 0 = best
    eps = (len(order_key) - rank) * 1e-9
    return np.argmax(P + eps[None, :], axis=1)


def route_fold(Xtr, Xte, Str, ytr_task, models_idx):
    """Return dict router -> chosen column (index into models_idx) for test rows."""
    Str = Str[:, models_idx]
    gmean = Str.mean(axis=0)
    tasks = np.unique(ytr_task)
    choices = {}

    # R0 best single
    best = argmax_tiebreak(gmean[None, :], gmean)[0]
    choices["R0_best_single"] = np.full(len(Xte), best)

    # task table (train)
    table = {t: Str[ytr_task == t].mean(axis=0) for t in tasks}

    clf = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(Xtr, ytr_task)
    pred_task = clf.predict(Xte)

    def lookup(task_arr):
        P = np.stack([table[t] for t in task_arr])
        return argmax_tiebreak(P, gmean), P

    # R3 direct per-model utility regression
    r3 = RidgeCV(alphas=ALPHAS).fit(Xtr, Str)
    P3 = r3.predict(Xte)
    choices["R3_direct_utility"] = argmax_tiebreak(P3, gmean)

    # R4 factored prior + residual on task-centred embedding
    cent = {t: Xtr[ytr_task == t].mean(axis=0) for t in tasks}

    def center(X, tl):
        Z = X - np.stack([cent[t] for t in tl])
        return Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-12)

    prior_tr = np.stack([table[t] for t in ytr_task])
    r4 = RidgeCV(alphas=ALPHAS).fit(center(Xtr, ytr_task), Str - prior_tr)
    prior_te = np.stack([table[t] for t in pred_task])
    P4 = prior_te + r4.predict(center(Xte, pred_task))
    choices["R4_factored_prior_residual"] = argmax_tiebreak(P4, gmean)

    # R5 kNN
    sims = Xte @ Xtr.T
    nn = np.argpartition(-sims, K_NN, axis=1)[:, :K_NN]
    P5 = Str[nn].mean(axis=1)
    choices["R5_knn50"] = argmax_tiebreak(P5, gmean)

    # R1/R2 lookups (oracle task filled in by caller)
    choices["R2_task_lookup_pred"], _ = lookup(pred_task)
    alpha_info = {"R3_alpha": float(r3.alpha_), "R4_alpha": float(r4.alpha_)}
    return choices, lookup, pred_task, alpha_info


def main():
    df, S, T, models = load_pool()
    assert len(df) == 11467 and S.shape == (11467, 20)
    # Pre-dumped by ../dump_gte.py (same GTE cache, same seed-42 row order, L2-normalised).
    import hashlib
    meta = json.loads((HERE.parent / "cache" / "gte_pool_meta.json").read_text())
    assert meta["query_sha256"] == hashlib.sha256("\n".join(df["query"]).encode()).hexdigest()
    X = np.load(HERE.parent / "cache" / "gte_pool.npy").astype(np.float64)
    task = df["dataset"].to_numpy()
    fold = df["fold"].to_numpy()

    pools = {"pool20": list(range(len(models))),
             "pair_ds_qwen": [models.index(DS), models.index(QWEN)]}
    report = {"models": models, "n": int(len(df)), "pools": {}}
    perq_all = []

    for pname, midx in pools.items():
        Sp, Tp = S[:, midx], T[:, midx]
        chosen = {}
        meta = []
        for k in sorted(np.unique(fold)):
            tr, te = fold != k, fold == k
            ch, lookup, pred_task, ainfo = route_fold(X[tr], X[te], S[tr], task[tr], midx)
            ch["R1_task_lookup_oracle"], _ = lookup(task[te])
            meta.append({"fold": int(k), "task_acc": float((pred_task == task[te]).mean()), **ainfo})
            for r, c in ch.items():
                chosen.setdefault(r, np.zeros(len(df), dtype=int))[te] = c
            print(f"[{pname}] fold {k} done task_acc={meta[-1]['task_acc']:.4f} {ainfo}", flush=True)

        rows = np.arange(len(df))
        acc = {r: Sp[rows, c] for r, c in chosen.items()}
        acc["OR_oracle"] = Sp.max(axis=1)
        tok = {r: Tp[rows, c] for r, c in chosen.items()}
        base = acc["R2_task_lookup_pred"]
        rng = np.random.default_rng(0)
        boot_idx = rng.integers(0, len(df), size=(N_BOOT, len(df)))
        res = {}
        for r, a in acc.items():
            d = a - base
            bs = d[boot_idx].mean(axis=1)
            fold_d = [float(d[fold == k].mean()) for k in sorted(np.unique(fold))]
            macro = float(np.mean([a[task == t].mean() for t in np.unique(task)]))
            ent = None
            if r in chosen:
                p = np.bincount(chosen[r], minlength=len(midx)) / len(df)
                p = p[p > 0]
                ent = float(-(p * np.log2(p)).sum())
            res[r] = {
                "acc": float(a.mean()), "macro_acc": macro,
                "delta_vs_R2": float(d.mean()),
                "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                "fold_delta": fold_d, "folds_pos": int(sum(x > 0 for x in fold_d)),
                "mean_tokens": float(tok[r].mean()) if r in tok else None,
                "choice_entropy_bits": ent,
            }
        gap = res["OR_oracle"]["acc"] - res["R2_task_lookup_pred"]["acc"]
        for r in res:
            res[r]["gap_closed"] = res[r]["delta_vs_R2"] / gap if gap > 0 else None
        # per-benchmark breakdown
        per_b = {}
        for t in np.unique(task):
            m = task == t
            per_b[t] = {r: float(a[m].mean()) for r, a in acc.items()}
            per_b[t]["n"] = int(m.sum())
        cand = ["R3_direct_utility", "R4_factored_prior_residual", "R5_knn50"]
        rstar = max(cand, key=lambda r: res[r]["acc"])
        rs = res[rstar]
        if rs["delta_vs_R2"] >= 0.010 and rs["ci95"][0] > 0 and rs["folds_pos"] >= 4:
            verdict = "HEADROOM"
        elif rs["delta_vs_R2"] < 0.005 or rs["ci95"][0] <= 0:
            verdict = "NO HEADROOM"
        else:
            verdict = "MARGINAL"
        report["pools"][pname] = {"routers": res, "per_benchmark": per_b, "fold_meta": meta,
                                  "R_star": rstar, "verdict": verdict}
        for r, c in chosen.items():
            perq_all.append(pd.DataFrame({"pool": pname, "router": r, "dataset": task,
                                          "index": df["index"], "fold": fold,
                                          "choice": [models[midx[i]] for i in c],
                                          "score": acc[r]}))
        print(f"\n== {pname} ==")
        for r in sorted(res):
            x = res[r]
            print(f"  {r:28s} acc={x['acc']:.4f} macro={x['macro_acc']:.4f} "
                  f"d={x['delta_vs_R2']:+.4f} [{x['ci95'][0]:+.4f},{x['ci95'][1]:+.4f}] "
                  f"folds+={x['folds_pos']} gap={x['gap_closed'] if x['gap_closed'] is None else round(x['gap_closed'],3)} "
                  f"tok={x['mean_tokens']} H={x['choice_entropy_bits']}")
        print(f"  R* = {rstar}; VERDICT ({pname}) = {verdict}")

    (OUT / "e1_results.json").write_text(json.dumps(report, indent=1, sort_keys=True))
    pd.concat(perq_all).to_csv(OUT / "e1_per_query_choices.csv.gz", index=False)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
