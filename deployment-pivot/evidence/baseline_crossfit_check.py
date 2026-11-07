"""Cross-fitted baseline check for BASELINES.md (EDGE / REMOTE only, assumed profiles).

joint_vs_sequential_sim.py picks each table on the same queries it scores (in-sample).
This script re-runs the comparison with
  * 2-fold cross-fitting by query (tables fitted on one half, scored on the other),
  * the full baseline set of BASELINES.md (incl. "router over fixed placements",
    the ECO-LLM-style baseline that the earlier sim did not have),
  * a paired, task-stratified bootstrap 95% CI for joint+live minus each baseline.

Quality / token counts: cached LLMRouterBench. Throughput / RTT / power: the SAME
assumptions as joint_vs_sequential_sim.py (imported, not redefined).

Usage: python3 -I baseline_crossfit_check.py [LLMRouterBench_root]
"""
import os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joint_vs_sequential_sim as S  # noqa: E402

SEED, B = 20261107, 1000
EDGE_TPS, SLOS = 40.0, [60.0, 300.0]   # fast edge = the only regime where the sim found a gap
ALL = list(S.actions())
HOME = [a for a in ALL if (a[0] in S.EDGE_MODELS) == (a[1] == "EDGE")]  # each model in one place


def lat_ok(rec, a, st, slo):
    t, e = S.lat_energy(rec, a[0], a[1], EDGE_TPS, st)
    return (rec[0] if t <= slo else 0.0), (0.0 if e == float("inf") else e)


def util(data, task, keys, a, st, slo):
    recs = data[task][a[0]]
    return sum(lat_ok(recs[k], a, st, slo)[0] for k in keys) / max(len(keys), 1)


def pick(data, task, keys, acts, st, slo):
    return max(acts, key=lambda a: (round(util(data, task, keys, a, st, slo), 3),
                                    -sum(lat_ok(data[task][a[0]][k], a, st, slo)[1] for k in keys)))


def policies(data, tasks, train, st, slo):
    """return {name: {task: action}} fitted on `train` keys only."""
    nominal = S.STATES[0]
    up = st[3]
    edge_acts = [a for a in ALL if a[1] == "EDGE"]
    rem_acts = [a for a in ALL if a[1] == "REMOTE"]
    pol = {}
    pol["F3 joint+live"] = {t: pick(data, t, train[t], ALL, st, slo) for t in tasks}
    pol["F1 joint, state-oblivious (ECO-LLM/2507.15553 static table)"] = {
        t: pick(data, t, train[t], ALL, nominal, slo) for t in tasks}
    pol["B-route|fixed-placement, live (router over home deployments)"] = {
        t: pick(data, t, train[t], HOME, st, slo) for t in tasks}
    # placement without routing: ONE model for all tasks (best on train under nominal), path by live state
    def tot(m, p, stt):
        return sum(util(data, t, train[t], (m, p), stt, slo) for t in tasks)
    m_fix = max({a[0] for a in ALL}, key=lambda m: max(tot(m, p, nominal) for p in ("EDGE", "REMOTE")
                                                         if (m, p) in ALL))
    pol["B-place|no-routing (one model, live path)"] = {
        t: max([a for a in ALL if a[0] == m_fix], key=lambda a: util(data, t, train[t], a, st, slo))
        for t in tasks}
    # deployment-oblivious routing: argmax raw accuracy per task, then best live path for that model
    def acc(t, m):
        return sum(data[t][m][k][0] for k in train[t]) / len(train[t])
    obl = {t: max({a[0] for a in ALL}, key=lambda m: acc(t, m)) for t in tasks}
    pol["B-oblivious route -> live path"] = {
        t: max([a for a in ALL if a[0] == obl[t]], key=lambda a: util(data, t, train[t], a, st, slo))
        for t in tasks}
    # decomposed: deadline-aware REMOTE-only table using live kappa, + edge failover on outage
    pol["B-dec REMOTE table(live) + edge failover"] = {
        t: (pick(data, t, train[t], rem_acts, st, slo) if up else pick(data, t, train[t], edge_acts, st, slo))
        for t in tasks}
    # best fixed deployment: one (model, path) for everything, chosen under nominal state
    a_fix = max(ALL, key=lambda a: sum(util(data, t, train[t], a, nominal, slo) for t in tasks))
    pol["B-best fixed deployment"] = {t: a_fix for t in tasks}
    pol["Edge-only (best edge model per task)"] = {t: pick(data, t, train[t], edge_acts, st, slo) for t in tasks}
    pol["Remote-only (best remote action per task, live)"] = {
        t: pick(data, t, train[t], rem_acts, st, slo) for t in tasks}
    return pol


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else S.ROOT
    data = {}
    for b, s in S.BENCH:
        data[b] = {m: S.load(b, s, m) for m in S.EDGE_MODELS + S.BIG_MODELS}
    tasks = [b for b, _ in S.BENCH if all(data[b][m] for m in data[b])]
    keys = {t: sorted(set.intersection(*[set(data[t][m]) for m in data[t]]), key=str) for t in tasks}
    rng = random.Random(SEED)
    fold = {t: {k: rng.random() < 0.5 for k in keys[t]} for t in tasks}
    print(f"# baseline_crossfit_check.py output (seed {SEED}); edge 8B at {EDGE_TPS:.0f} tok/s; "
          "profiles ASSUMED (see joint_vs_sequential_sim.py). 2-fold cross-fit by query.\n")
    print("| SLO s | state | policy | cross-fit U | in-sample U | Δ(F3 − policy) pt | 95% CI |")
    print("|---|---|---|---|---|---|---|")
    for slo in SLOS:
        for st in S.STATES:
            per_q = {}   # policy -> {(t,k): utility}
            insample = {}
            for f in (False, True):
                train = {t: [k for k in keys[t] if fold[t][k] != f] for t in tasks}
                test = {t: [k for k in keys[t] if fold[t][k] == f] for t in tasks}
                for name, pol in policies(data, tasks, train, st, slo).items():
                    d = per_q.setdefault(name, {})
                    for t in tasks:
                        for k in test[t]:
                            d[(t, k)] = lat_ok(data[t][pol[t][0]][k], pol[t], st, slo)[0]
            for name, pol in policies(data, tasks, keys, st, slo).items():
                insample[name] = sum(util(data, t, keys[t], pol[t], st, slo) for t in tasks) / len(tasks)
            def U(name):
                # macro-average over tasks, matching joint_vs_sequential_sim.py
                return sum(sum(per_q[name][(t, k)] for k in keys[t]) / len(keys[t]) for t in tasks) / len(tasks)
            ref = "F3 joint+live"
            others = [n for n in per_q if n != ref]
            diff = {n: {t: [per_q[ref][(t, k)] - per_q[n][(t, k)] for k in keys[t]] for t in tasks} for n in others}
            boot = {n: [] for n in others}
            for _ in range(B):
                idx = {t: rng.choices(range(len(keys[t])), k=len(keys[t])) for t in tasks}
                for n in others:
                    boot[n].append(sum(sum(diff[n][t][i] for i in idx[t]) / len(idx[t]) for t in tasks) / len(tasks))
            print(f"| {slo:.0f} | {st[0]} | **{ref}** | {U(ref):.3f} | {insample[ref]:.3f} | — | — |")
            for name in others:
                u = U(name)
                ds = sorted(boot[name])
                lo, hi = ds[int(0.025 * B)], ds[int(0.975 * B) - 1]
                print(f"| {slo:.0f} | {st[0]} | {name} | {u:.3f} | {insample[name]:.3f} | "
                      f"{100 * (U(ref) - u):+.1f} | [{100 * lo:+.1f}, {100 * hi:+.1f}] |")

if __name__ == "__main__":
    main()
