#!/usr/bin/env python3
"""E2: cost-aware routing (correctness - lambda * k-tokens) on the 20-model pool.

Implements PREREG.md. Reads LLMRouterBench read-only via ../E1-pool-headroom/run_e1.py
loaders and the pre-dumped ../cache/gte_pool.npy; writes only under results/.

  ~/research/LLMRouterBench/.venv/bin/python -B decision/E2-cost-aware/run_e2.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import RidgeClassifier, RidgeCV

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "E1-pool-headroom"))
import run_e1 as e1  # noqa: E402  (load_pool, ALPHAS, K_NN)

OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
LAMBDAS = [0, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5]
N_BOOT = 2000
SHRINK = 20.0
PREREG = ["R0_best_single", "R2_task_lookup", "R3_direct", "R4_factored", "R5_knn50", "R6_cluster_lookup"]
POSTHOC = ["R4s_factored_s_only", "R4t_factored_t_only"]
CAND = ["R3_direct", "R4_factored", "R5_knn50"]


def predict_fold(Xtr, Xte, Str, Ttr, ytr):
    """Return dict router -> (s_hat, t_hat) for test rows, plus diagnostics."""
    tasks = np.unique(ytr)
    out = {}
    gS, gT = Str.mean(0), Ttr.mean(0)
    out["R0_best_single"] = (np.tile(gS, (len(Xte), 1)), np.tile(gT, (len(Xte), 1)))
    clf = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(Xtr, ytr)
    pt = clf.predict(Xte)
    tabS = {t: Str[ytr == t].mean(0) for t in tasks}
    tabT = {t: Ttr[ytr == t].mean(0) for t in tasks}
    priS_te = np.stack([tabS[t] for t in pt])
    priT_te = np.stack([tabT[t] for t in pt])
    out["R2_task_lookup"] = (priS_te, priT_te)

    rS = RidgeCV(alphas=e1.ALPHAS).fit(Xtr, Str)
    rT = RidgeCV(alphas=e1.ALPHAS).fit(Xtr, Ttr)
    out["R3_direct"] = (rS.predict(Xte), rT.predict(Xte))

    cent = {t: Xtr[ytr == t].mean(0) for t in tasks}

    def center(X, tl):
        Z = X - np.stack([cent[t] for t in tl])
        return Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-12)

    Ztr, Zte = center(Xtr, ytr), center(Xte, pt)
    priS_tr = np.stack([tabS[t] for t in ytr])
    priT_tr = np.stack([tabT[t] for t in ytr])
    fS = RidgeCV(alphas=e1.ALPHAS).fit(Ztr, Str - priS_tr)
    fT = RidgeCV(alphas=e1.ALPHAS).fit(Ztr, Ttr - priT_tr)
    s4, t4 = priS_te + fS.predict(Zte), priT_te + fT.predict(Zte)
    out["R4_factored"] = (s4, t4)
    out["R4s_factored_s_only"] = (s4, priT_te)
    out["R4t_factored_t_only"] = (priS_te, t4)

    sims = Xte @ Xtr.T
    nn = np.argpartition(-sims, e1.K_NN, axis=1)[:, :e1.K_NN]
    out["R5_knn50"] = (Str[nn].mean(1), Ttr[nn].mean(1))
    del sims

    # R6 cluster lookup inside predicted benchmark (train-only k-means, shrunk to task mean)
    s6, t6 = priS_te.copy(), priT_te.copy()
    ks = {}
    for t in tasks:
        mtr = ytr == t
        k = int(np.clip(round(mtr.sum() / 200), 1, 16))
        ks[str(t)] = k
        mte = pt == t
        if k == 1 or not mte.any():
            continue
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xtr[mtr])
        lab_tr, lab_te = km.labels_, km.predict(Xte[mte])
        cs, ct = np.zeros((k, Str.shape[1])), np.zeros((k, Ttr.shape[1]))
        for c in range(k):
            m = lab_tr == c
            n = m.sum()
            cs[c] = (n * Str[mtr][m].mean(0) + SHRINK * tabS[t]) / (n + SHRINK)
            ct[c] = (n * Ttr[mtr][m].mean(0) + SHRINK * tabT[t]) / (n + SHRINK)
        s6[mte], t6[mte] = cs[lab_te], ct[lab_te]
    out["R6_cluster_lookup"] = (s6, t6)
    diag = {"task_acc": None, "alphas": {"R3s": rS.alpha_, "R3t": rT.alpha_, "R4s": fS.alpha_, "R4t": fT.alpha_},
            "k_per_task": ks}
    return out, pt, gS, gT, diag


def choose(sh, th, lam, gS, gT):
    u = sh - lam * th
    gu = gS - lam * gT
    rank = np.argsort(np.argsort(-gu, kind="stable"), kind="stable")
    eps = (len(gu) - rank) * 1e-9
    return np.argmax(u + eps[None, :], axis=1)


def frontier(tok, acc):
    """Non-dominated (tokens up, acc strictly up) points."""
    o = np.argsort(tok)
    ft, fa = [], []
    for i in o:
        if not fa or acc[i] > fa[-1]:
            ft.append(tok[i]); fa.append(acc[i])
    return np.array(ft), np.array(fa)


def tokens_at_acc(ft, fa, a):
    if a > fa[-1] + 1e-12:
        return float("nan")
    if a <= fa[0]:
        return float(ft[0])
    return float(np.interp(a, fa, ft))


def acc_at_budget(ft, fa, b):
    if b < ft[0]:
        return float("nan")
    return float(np.interp(b, ft, fa))


def main():
    df, S, T, models = e1.load_pool()
    T = T / 1000.0  # k-tokens
    meta = json.loads((HERE.parent / "cache" / "gte_pool_meta.json").read_text())
    assert meta["query_sha256"] == hashlib.sha256("\n".join(df["query"]).encode()).hexdigest()
    X = np.load(HERE.parent / "cache" / "gte_pool.npy").astype(np.float64)
    task, fold = df["dataset"].to_numpy(), df["fold"].to_numpy()
    N, M = S.shape
    folds = sorted(np.unique(fold))
    routers = PREREG + POSTHOC
    choice = {r: np.zeros((len(LAMBDAS), N), dtype=int) for r in routers}
    That = {r: np.zeros((N, M)) for r in ("R2_task_lookup", "R4_factored", "R3_direct", "R5_knn50", "R6_cluster_lookup")}
    Shat = {r: np.zeros((N, M)) for r in That}
    fmeta = []
    for k in folds:
        tr, te = fold != k, fold == k
        pred, pt, gS, gT, diag = predict_fold(X[tr], X[te], S[tr], T[tr], task[tr])
        diag["task_acc"] = float((pt == task[te]).mean())
        diag["fold"] = int(k)
        fmeta.append(diag)
        for r, (sh, th) in pred.items():
            if r in That:
                Shat[r][te], That[r][te] = sh, th
            for li, lam in enumerate(LAMBDAS):
                choice[r][li, te] = choose(sh, th, lam, gS, gT)
        print(f"fold {k} done {diag}", flush=True)

    rows = np.arange(N)
    rng = np.random.default_rng(0)
    boot = rng.integers(0, N, size=(N_BOOT, N))
    res = {r: [] for r in routers + ["OR_oracle"]}
    for li, lam in enumerate(LAMBDAS):
        U = S - lam * T
        base_u = U[rows, choice["R2_task_lookup"][li]]
        orc = U.max(1)
        for r in routers + ["OR_oracle"]:
            if r == "OR_oracle":
                c = U.argmax(1)
            else:
                c = choice[r][li]
            u = U[rows, c]
            d = u - base_u
            bs = d[boot].mean(1)
            fd = [float(d[fold == k].mean()) for k in folds]
            gap = float(orc.mean() - base_u.mean())
            res[r].append({
                "lambda": lam, "U": float(u.mean()), "acc": float(S[rows, c].mean()),
                "mean_ktok": float(T[rows, c].mean()), "dU": float(d.mean()),
                "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                "fold_dU": fd, "folds_pos": int(sum(x > 0 for x in fd)),
                "gap_closed": float(d.mean() / gap) if gap > 0 else None,
            })
        print(f"lambda={lam}: " + " ".join(f"{r.split('_')[0]}:dU={res[r][-1]['dU']*100:+.2f}"
                                          f"/acc={res[r][-1]['acc']:.4f}/tok={res[r][-1]['mean_ktok']:.2f}"
                                          for r in routers), flush=True)

    # operating band from R2 alone
    cheapest = T.mean(0).min()
    best_single_tok = T[:, int(np.argmax(S.mean(0)))].mean()
    band = [li for li, lam in enumerate(LAMBDAS)
            if lam > 0 and cheapest < res["R2_task_lookup"][li]["mean_ktok"] < best_single_tok]
    mean_band = {r: float(np.mean([res[r][li]["dU"] for li in band])) for r in CAND}
    rstar = max(CAND, key=lambda r: mean_band[r])
    pass_l = [li for li in band if res[rstar][li]["dU"] >= 0.010 and res[rstar][li]["ci95"][0] > 0
              and res[rstar][li]["folds_pos"] >= 4]
    weak_l = [li for li in band if res[rstar][li]["dU"] < 0.005 or res[rstar][li]["ci95"][0] <= 0]
    if band and len(pass_l) >= len(band) / 2:
        verdict = "COST HEADROOM"
    elif len(weak_l) == len(band):
        verdict = "NO COST HEADROOM"
    else:
        verdict = "MARGINAL"
    tax = {LAMBDAS[li]: res["R6_cluster_lookup"][li]["dU"] - res[rstar][li]["dU"] for li in [0] + band}
    tax_finer = sum(v >= -0.003 for k_, v in tax.items() if k_ > 0) > len(band) / 2 if band else None

    # curves, matched-accuracy savings, budget accuracies
    curves = {}
    for r in routers:
        tok = np.array([x["mean_ktok"] for x in res[r]])
        acc = np.array([x["acc"] for x in res[r]])
        curves[r] = frontier(tok, acc)
    matched = {}
    for r in CAND + ["R6_cluster_lookup", "R4s_factored_s_only", "R4t_factored_t_only"]:
        ft, fa = curves[r]
        matched[r] = []
        for li in band:
            a, t2 = res["R2_task_lookup"][li]["acc"], res["R2_task_lookup"][li]["mean_ktok"]
            tr_ = tokens_at_acc(ft, fa, a)
            matched[r].append({"lambda": LAMBDAS[li], "R2_acc": a, "R2_ktok": t2, "ktok": tr_,
                               "saving_pct": float(100 * (1 - tr_ / t2)) if tr_ == tr_ else None})
    budgets = {r: {b: acc_at_budget(*curves[r], b) for b in (1.0, 2.0, 3.0)} for r in routers}

    # predictability of tokens / correctness beyond the benchmark mean (held-out R^2)
    def r2(y, yh):
        return float(1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    pred_r2 = {r: {"tokens_R2": r2(T, That[r]), "score_R2": r2(S, Shat[r])} for r in That}

    report = {"lambdas": LAMBDAS, "models": models, "band_lambdas": [LAMBDAS[li] for li in band],
              "cheapest_model_ktok": float(cheapest), "best_single_ktok": float(best_single_tok),
              "mean_band_dU": mean_band, "R_star": rstar, "verdict": verdict,
              "pass_lambdas": [LAMBDAS[li] for li in pass_l],
              "taxonomy_R6_minus_Rstar": {str(k_): v for k_, v in tax.items()},
              "taxonomy_finer_task_majority": tax_finer,
              "routers": res, "matched_accuracy_tokens": matched,
              "acc_at_budget_ktok": budgets, "heldout_R2": pred_r2, "fold_meta": fmeta,
              "posthoc_routers": POSTHOC}
    (OUT / "e2_results.json").write_text(json.dumps(report, indent=1, default=float))
    print(f"\nband lambdas: {report['band_lambdas']} (cheapest {cheapest:.3f}k, best-single {best_single_tok:.3f}k)")
    print(f"mean band dU: {mean_band}")
    print(f"R* = {rstar}; pass lambdas = {report['pass_lambdas']}; VERDICT = {verdict}")
    print(f"taxonomy R6 - R*: {report['taxonomy_R6_minus_Rstar']}; finer-taxonomy majority = {tax_finer}")
    print(f"matched-accuracy savings: " + json.dumps({r: [m['saving_pct'] for m in v] for r, v in matched.items()}))
    print(f"acc at budget: {json.dumps(budgets)}")
    print(f"held-out R2: {json.dumps(pred_r2)}")


if __name__ == "__main__":
    main()
