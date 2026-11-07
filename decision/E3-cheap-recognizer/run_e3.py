#!/usr/bin/env python3
"""E3: tiny lexical task recognizer vs GTE-7B recognizer inside the cost-aware lookup.

Implements PREREG.md. Reads the pool read-only via the E1 loaders and ../cache/gte_pool.npy.
Writes results/ only.

  ~/research/LLMRouterBench/.venv/bin/python -B decision/E3-cheap-recognizer/run_e3.py
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "E1-pool-headroom"))
sys.path.insert(0, str(HERE.parent / "E2-cost-aware"))
import run_e1 as e1  # noqa: E402
from run_e2 import LAMBDAS, choose  # noqa: E402

OUT = HERE / "results"
OUT.mkdir(exist_ok=True)


def main():
    df, S, T, models = e1.load_pool()
    T = T / 1000.0
    meta = json.loads((HERE.parent / "cache" / "gte_pool_meta.json").read_text())
    assert meta["query_sha256"] == hashlib.sha256("\n".join(df["query"]).encode()).hexdigest()
    X = np.load(HERE.parent / "cache" / "gte_pool.npy").astype(np.float64)
    q = df["query"].to_numpy()
    task, fold = df["dataset"].to_numpy(), df["fold"].to_numpy()
    N = len(df)
    rows = np.arange(N)
    folds = sorted(np.unique(fold))
    rec = ("G_gte_ridge", "L_tfidf_svm", "O_oracle_task")
    pred = {r: np.empty(N, dtype=object) for r in rec}
    choice = {r: np.zeros((len(LAMBDAS), N), dtype=int) for r in rec}
    timing = []
    for k in folds:
        tr, te = fold != k, fold == k
        ytr = task[tr]
        pred["G_gte_ridge"][te] = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(X[tr], ytr).predict(X[te])
        vw = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
        vc = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2)
        Ltr = hstack([vw.fit_transform(q[tr]), vc.fit_transform(q[tr])]).tocsr()
        svm = LinearSVC(C=1.0, class_weight="balanced").fit(Ltr, ytr)
        t0 = time.perf_counter()
        Lte = hstack([vw.transform(q[te]), vc.transform(q[te])]).tocsr()
        pred["L_tfidf_svm"][te] = svm.predict(Lte)
        timing.append((time.perf_counter() - t0) / te.sum() * 1000)
        pred["O_oracle_task"][te] = task[te]
        tabS = {t: S[tr][ytr == t].mean(0) for t in np.unique(ytr)}
        tabT = {t: T[tr][ytr == t].mean(0) for t in np.unique(ytr)}
        gS, gT = S[tr].mean(0), T[tr].mean(0)
        for r in rec:
            sh = np.stack([tabS[t] for t in pred[r][te]])
            th = np.stack([tabT[t] for t in pred[r][te]])
            for li, lam in enumerate(LAMBDAS):
                choice[r][li, te] = choose(sh, th, lam, gS, gT)
        print(f"fold {k}: " + " ".join(f"{r}={np.mean(pred[r][te] == task[te]):.4f}" for r in rec), flush=True)

    boot = np.random.default_rng(0).integers(0, N, size=(2000, N))
    acc = {r: float(np.mean(pred[r] == task)) for r in rec}
    per_lam = []
    for li, lam in enumerate(LAMBDAS):
        U = S - lam * T
        u = {r: U[rows, choice[r][li]] for r in rec}
        d = u["L_tfidf_svm"] - u["G_gte_ridge"]
        bs = d[boot].mean(1)
        per_lam.append({"lambda": lam, **{f"U_{r}": float(u[r].mean()) for r in rec},
                        "dU_L_minus_G_pt": 100 * float(d.mean()),
                        "ci95_pt": [100 * float(np.percentile(bs, 2.5)), 100 * float(np.percentile(bs, 97.5))]})
    ok_acc = acc["L_tfidf_svm"] >= 0.98
    ok_u = all(abs(x["dU_L_minus_G_pt"]) <= 0.3 or x["dU_L_minus_G_pt"] >= 0 for x in per_lam)
    verdict = "SUFFICIENT" if ok_acc and ok_u else "INSUFFICIENT"
    conf = {}
    for t_true, t_pred in zip(task, pred["L_tfidf_svm"]):
        if t_true != t_pred:
            conf[f"{t_true}->{t_pred}"] = conf.get(f"{t_true}->{t_pred}", 0) + 1
    rep = {"task_acc": acc, "per_lambda": per_lam, "verdict": verdict,
           "L_inference_ms_per_query_cpu": float(np.mean(timing)),
           "L_confusions": dict(sorted(conf.items(), key=lambda kv: -kv[1]))}
    (OUT / "e3_results.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(acc))
    for x in per_lam:
        print("lam=%.3f U_G=%.4f U_L=%.4f U_O=%.4f L-G=%+.2f [%+.2f,%+.2f]" % (
            x["lambda"], x["U_G_gte_ridge"], x["U_L_tfidf_svm"], x["U_O_oracle_task"],
            x["dU_L_minus_G_pt"], *x["ci95_pt"]))
    print(f"L ms/query (featurise+predict, CPU): {rep['L_inference_ms_per_query_cpu']:.3f}")
    print(f"top confusions: {list(rep['L_confusions'].items())[:8]}")
    print(f"VERDICT = {verdict}")


if __name__ == "__main__":
    main()
