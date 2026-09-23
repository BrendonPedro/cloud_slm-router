"""Stage-0 prototype (deliverable 12): zero-inference routing baselines on
LLMRouterBench's released per-query scores.

Implements the parts of architecture/recommended-experiment.md sections 4-5 that run
on a CPU-only host with the Python standard library alone (numpy/sklearn/torch are not
installed here):

  * label building for pairs P-L and P-Q from the released bundle
  * frozen, hashed train/dev/test splits (5 seeds) and leave-one-group-out (LODO) folds
  * routers/baselines: always-edge, always-cloud, random, dataset-prior (leak control),
    TF-IDF (word 1-2 gram) + L2 logistic regression, oracle
  * metrics: CCR@-1 (dev-tuned threshold applied to test), deferral AUC, ECE, Brier
  * paired bootstrap CI of the deferral-AUC difference TF-IDF+LR minus each baseline

It does NOT train the neural routers B-s/B-m/A/C-pre; those need torch (and C-pre a GPU).
Every number it writes is computed from the bundle; nothing is estimated.

Usage: python3 stage0.py config/stage0.json
"""
import collections
import hashlib
import json
import math
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1]))
ROOT = cfg["bundle_root"]
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


def qhash(q):
    return hashlib.sha256(q.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- data loading
def load_split(dataset, split):
    """Return {model: {query: score}}; if several files exist keep the largest
    (same rule as research/raw/experiment/inventory_llmrouterbench.py)."""
    out, dup_info = {}, {}
    for dirpath, _, files in os.walk(os.path.join(ROOT, dataset)):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            d = json.load(open(os.path.join(dirpath, fn)))
            if d.get("dataset_name") != dataset or d.get("split") != split:
                continue
            scores, seen, disagree = {}, collections.Counter(), 0
            for r in d.get("records", []):
                q, s = r.get("origin_query") or r.get("prompt"), r.get("score")
                if q is None or s is None:
                    continue
                s = float(s)
                seen[q] += 1
                if q in scores and scores[q] != s:
                    disagree += 1
                scores[q] = s  # last occurrence wins, as in the inventory script
            m = d.get("model_name")
            if m in out and len(out[m]) >= len(scores):
                continue
            out[m] = scores
            dup_info[m] = (sum(1 for c in seen.values() if c > 1), disagree)
    return out, dup_info


def build_pairs():
    data = {}
    for pname, pm in cfg["pairs"].items():
        rows = []
        for dataset, split, group in cfg["splits"]:
            models, dups = load_split(dataset, split)
            w, s = models[pm["weak"]], models[pm["strong"]]
            common = sorted(set(w) & set(s))
            for m in (pm["weak"], pm["strong"]):
                if dups[m][0]:
                    log(f"{pname} {dataset}/{split} {m}: {dups[m][0]} duplicated query strings, "
                        f"{dups[m][1]} with disagreeing scores (last kept)")
            for q in common:
                if w[q] not in (0.0, 1.0) or s[q] not in (0.0, 1.0):
                    raise ValueError(f"non-binary score in {dataset}/{split}")
                rows.append(dict(h=qhash(q), q=q, group=group, ds=f"{dataset}/{split}",
                                 w=w[q], s=s[q], y=1 if w[q] >= s[q] else 0))
        hs = [r["h"] for r in rows]
        assert len(hs) == len(set(hs)), "query-hash collision or cross-split duplicate"
        data[pname] = rows
        log(f"{pname}: {len(rows)} queries; weak acc {mean(r['w'] for r in rows):.4f}, "
            f"strong acc {mean(r['s'] for r in rows):.4f}, P(y=1) {mean(r['y'] for r in rows):.4f}")
    return data


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


# ---------------------------------------------------------------- splits
def stratified_split(rows, fracs, seed):
    """fracs: list of fractions summing to 1. Stratify by (group, w, s)."""
    rng = random.Random(seed)
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r["group"], r["w"], r["s"])].append(r["h"])
    parts = [[] for _ in fracs]
    for key in sorted(cells):
        hs = sorted(cells[key])
        rng.shuffle(hs)
        n, start = len(hs), 0
        cum = 0.0
        for i, f in enumerate(fracs):
            cum += f
            end = n if i == len(fracs) - 1 else round(cum * n)
            parts[i].extend(hs[start:end])
            start = end
    return [set(p) for p in parts]


def write_split(name, parts, labels=("train", "dev", "test")):
    path = os.path.join(HERE, "splits", f"{name}.json")
    obj = {lab: sorted(p) for lab, p in zip(labels, parts)}
    blob = json.dumps(obj, sort_keys=True).encode()
    open(path, "wb").write(blob)
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------- TF-IDF + LR
TOK = re.compile(cfg["tfidf"]["token_pattern"])


def ngrams(text):
    toks = TOK.findall(text.lower())
    return toks + [a + " " + b for a, b in zip(toks, toks[1:])]


def tfidf_fit(texts):
    df = collections.Counter()
    for t in texts:
        df.update(set(ngrams(t)))
    vocab = {g: i for i, g in enumerate(sorted(g for g, c in df.items() if c >= cfg["tfidf"]["min_df"]))}
    n = len(texts)
    idf = {vocab[g]: math.log((1 + n) / (1 + df[g])) + 1.0 for g in vocab}
    return vocab, idf


def tfidf_transform(text, vocab, idf):
    tf = collections.Counter(vocab[g] for g in ngrams(text) if g in vocab)
    v = {j: (1.0 + math.log(c)) * idf[j] for j, c in tf.items()}
    norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {j: x / norm for j, x in v.items()}


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))


def lr_fit(X, y, dim, l2):
    lc = cfg["logreg"]
    w, b = [0.0] * dim, 0.0
    gw_acc, gb_acc = [1e-8] * dim, 1e-8
    n = len(X)
    for _ in range(lc["epochs"]):
        g, gb = [0.0] * dim, 0.0
        for x, t in zip(X, y):
            p = sigmoid(b + sum(w[j] * v for j, v in x.items()))
            e = (p - t) / n
            gb += e
            for j, v in x.items():
                g[j] += e * v
        for j in range(dim):
            gj = g[j] + l2 * w[j]
            gw_acc[j] += gj * gj
            w[j] -= lc["lr"] * gj / math.sqrt(gw_acc[j])
        gb_acc += gb * gb
        b -= lc["lr"] * gb / math.sqrt(gb_acc)
    return w, b


def lr_predict(X, w, b):
    return [sigmoid(b + sum(w[j] * v for j, v in x.items())) for x in X]


def logloss(p, y):
    eps = 1e-12
    return -mean(t * math.log(max(q, eps)) + (1 - t) * math.log(max(1 - q, eps)) for q, t in zip(p, y))


def tfidf_lr(train, dev, test):
    vocab, idf = tfidf_fit([r["q"] for r in train])
    Xtr = [tfidf_transform(r["q"], vocab, idf) for r in train]
    Xdv = [tfidf_transform(r["q"], vocab, idf) for r in dev]
    Xte = [tfidf_transform(r["q"], vocab, idf) for r in test]
    ytr, ydv = [r["y"] for r in train], [r["y"] for r in dev]
    best = None
    for l2 in cfg["logreg"]["l2_grid"]:
        w, b = lr_fit(Xtr, ytr, len(vocab), l2)
        ll = logloss(lr_predict(Xdv, w, b), ydv)
        if best is None or ll < best[0]:
            best = (ll, l2, w, b)
    ll, l2, w, b = best
    return lr_predict(Xdv, w, b), lr_predict(Xte, w, b), dict(vocab=len(vocab), l2=l2, dev_logloss=ll)


# ---------------------------------------------------------------- metrics
def order(p, seed):
    """Escalation order: lowest p (least safe on edge) first; seeded random tie-break."""
    rng = random.Random(seed)
    tb = [rng.random() for _ in p]
    return sorted(range(len(p)), key=lambda i: (p[i], tb[i]))


def curve(rows, idx, weights=None):
    """Quality after escalating the first k queries of idx, k = 0..n. Returns (xs, ys)."""
    wt = weights or [1] * len(rows)
    n = sum(wt)
    q = sum(rows[i]["w"] * wt[i] for i in range(len(rows)))
    xs, ys, c = [0.0], [q / n], 0
    for i in idx:
        if wt[i] == 0:
            continue
        q += (rows[i]["s"] - rows[i]["w"]) * wt[i]
        c += wt[i]
        xs.append(c / n)
        ys.append(q / n)
    return xs, ys


def auc(xs, ys):
    return sum((xs[i + 1] - xs[i]) * (ys[i + 1] + ys[i]) / 2 for i in range(len(xs) - 1))


def ccr(dev_rows, p_dev, test_rows, p_test, seed):
    """Pick the smallest dev call rate with dev quality >= dev strong acc - margin, express it as
    a threshold on p (escalate if p < tau, ties broken at the same seeded order), apply to test."""
    target = mean(r["s"] for r in dev_rows) - cfg["quality_margin"]
    idx = order(p_dev, seed)
    xs, ys = curve(dev_rows, idx)
    k = next(i for i, y in enumerate(ys) if y >= target - 1e-12)
    tau = p_dev[idx[k - 1]] if k > 0 else -math.inf  # escalate test queries with p <= tau
    esc = [p <= tau for p in p_test]
    rate = mean(esc)
    qual = mean(r["s"] if e else r["w"] for r, e in zip(test_rows, esc))
    s_acc = mean(r["s"] for r in test_rows)
    return dict(dev_call_rate=xs[k], test_call_rate=rate, test_quality=qual, test_strong=s_acc,
                test_target=s_acc - cfg["quality_margin"],
                met=qual >= s_acc - cfg["quality_margin"] - 1e-12,
                random_same_rate_quality=(1 - rate) * mean(r["w"] for r in test_rows) + rate * s_acc)


def ece(p, y, bins):
    tot, n = 0.0, len(p)
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [i for i in range(n) if (lo <= p[i] < hi) or (b == bins - 1 and p[i] == 1.0)]
        if sel:
            tot += len(sel) / n * abs(mean(p[i] for i in sel) - mean(y[i] for i in sel))
    return tot


def evaluate(name, dev, test, p_dev, p_test, seed):
    y = [r["y"] for r in test]
    m = dict(router=name)
    m["deferral_auc"] = auc(*curve(test, order(p_test, seed)))
    m.update(ccr(dev, p_dev, test, p_test, seed))
    m["ece"] = ece(p_test, y, cfg["ece_bins"])
    m["brier"] = mean((q - t) ** 2 for q, t in zip(p_test, y))
    return m


def paired_bootstrap_auc(test, pa, pb, seed, B):
    """95% percentile CI of AUC(a) - AUC(b), resampling test queries stratified by group."""
    oa, ob = order(pa, seed), order(pb, seed)
    by_group = collections.defaultdict(list)
    for i, r in enumerate(test):
        by_group[r["group"]].append(i)
    rng = random.Random(cfg["bootstrap"]["seed"] + seed)
    diffs = []
    for _ in range(B):
        wt = [0] * len(test)
        for g in sorted(by_group):
            idx = by_group[g]
            for _ in idx:
                wt[idx[rng.randrange(len(idx))]] += 1
        diffs.append(auc(*curve(test, oa, wt)) - auc(*curve(test, ob, wt)))
    diffs.sort()
    point = auc(*curve(test, oa)) - auc(*curve(test, ob))
    return dict(diff=point, lo=diffs[int(0.025 * B)], hi=diffs[int(0.975 * B) - 1], B=B)


# ---------------------------------------------------------------- routers
def run_routers(train, dev, test, seed, tag, preds_out):
    rng = random.Random(1000 + seed)
    prior_all = mean(r["y"] for r in train)
    gp = {g: mean(r["y"] for r in train if r["group"] == g) for g in {r["group"] for r in train}}
    routers = {
        "always-edge": ([1.0] * len(dev), [1.0] * len(test)),
        "always-cloud": ([0.0] * len(dev), [0.0] * len(test)),
        "random": ([rng.random() for _ in dev], [rng.random() for _ in test]),
        "dataset-prior": ([gp.get(r["group"], prior_all) for r in dev],
                          [gp.get(r["group"], prior_all) for r in test]),
        "oracle": ([float(r["y"]) for r in dev], [float(r["y"]) for r in test]),
    }
    t = time.time()
    pd, pt, info = tfidf_lr(train, dev, test)
    info["fit_seconds"] = round(time.time() - t, 1)
    routers["tfidf-lr"] = (pd, pt)
    results = []
    for name, (a, b) in routers.items():
        if name in ("always-edge", "always-cloud"):
            m = dict(router=name, deferral_auc=None,
                     test_call_rate=0.0 if name == "always-edge" else 1.0,
                     test_quality=mean(r["w" if name == "always-edge" else "s"] for r in test),
                     test_strong=mean(r["s"] for r in test))
        else:
            m = evaluate(name, dev, test, a, b, seed)
        m.update(tag)
        results.append(m)
    for name in ("random", "dataset-prior"):
        bs = paired_bootstrap_auc(test, routers["tfidf-lr"][1], routers[name][1], seed, cfg["bootstrap"]["resamples"])
        results.append(dict(router=f"bootstrap: tfidf-lr minus {name} (deferral AUC)", **bs, **tag))
    with open(preds_out, "w") as f:
        for i, r in enumerate(test):
            f.write(json.dumps(dict(h=r["h"], group=r["group"], w=r["w"], s=r["s"], y=r["y"],
                                    **{k: round(v[1][i], 6) for k, v in routers.items()})) + "\n")
    return results, info


# ---------------------------------------------------------------- main
def main():
    data = build_pairs()
    all_results, split_hashes, fit_info = [], {}, {}
    fr = cfg["split_fractions"]
    for pname, rows in data.items():
        by_h = {r["h"]: r for r in rows}
        for seed in cfg["seeds"]:
            tr, dv, te = stratified_split(rows, [fr["train"], fr["dev"], fr["test"]], seed)
            split_hashes[f"{pname}_seed{seed}"] = write_split(f"{pname}_seed{seed}", (tr, dv, te))
            pick = lambda hs: [by_h[h] for h in sorted(hs)]
            res, info = run_routers(pick(tr), pick(dv), pick(te), seed,
                                    dict(pair=pname, setting="in-domain", seed=seed, n_test=len(te)),
                                    os.path.join(HERE, "preds", f"{pname}_seed{seed}.jsonl"))
            all_results += res
            fit_info[f"{pname}_seed{seed}"] = info
            log(f"{pname} seed {seed}: train/dev/test {len(tr)}/{len(dv)}/{len(te)} tfidf {info}")
        for g in cfg["lodo_groups"]:
            held = [r for r in rows if r["group"] == g]
            rest = [r for r in rows if r["group"] != g]
            tr, dv = stratified_split(rest, [1 - cfg["lodo_dev_fraction"], cfg["lodo_dev_fraction"]], cfg["lodo_seed"])
            te = {r["h"] for r in held}
            split_hashes[f"{pname}_lodo_{g}"] = write_split(f"{pname}_lodo_{g}", (tr, dv, te))
            pick = lambda hs: [by_h[h] for h in sorted(hs)]
            res, info = run_routers(pick(tr), pick(dv), pick(te), cfg["lodo_seed"],
                                    dict(pair=pname, setting=f"LODO:{g}", seed=cfg["lodo_seed"], n_test=len(te)),
                                    os.path.join(HERE, "preds", f"{pname}_lodo_{g}.jsonl"))
            all_results += res
            fit_info[f"{pname}_lodo_{g}"] = info
            log(f"{pname} LODO {g}: train/dev/test {len(tr)}/{len(dv)}/{len(te)} tfidf {info}")
    json.dump(dict(results=all_results, split_sha256=split_hashes, tfidf_fit=fit_info),
              open(os.path.join(HERE, "results", "stage0_raw.json"), "w"), indent=1)
    log("done")


if __name__ == "__main__":
    main()
