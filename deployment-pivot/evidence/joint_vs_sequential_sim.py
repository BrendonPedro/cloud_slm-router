"""Pre-hardware headroom check for the deployment formulations (EDGE / REMOTE only).

Question: on cached per-query correctness + output-token counts, does
(a) choosing (model, path) JOINTLY beat choosing the model first (deployment-oblivious
    task table) and the path second, and
(b) does LIVE link/server state change the optimal (model, path) per task?

No new inference. Quality and token counts are cached (LLMRouterBench). EVERY
throughput / RTT / power number below is an ASSUMPTION (to be replaced by measured
profiles from E0/E1-hw); the point is to find which state variables can flip a
decision at all, not to estimate final numbers. SPLIT is not simulated: no mid-size
(14-32B) model has cached labels on these benchmarks, and E0 decides whether SPLIT
enters the action set.

Task = benchmark (the TF-IDF recognizer is 99.6% accurate on benchmark identity, E3).
Latency(q, model, path, state) = path_overhead + prompt_prefill + N_q / decode_tps.

Usage: python3 -I joint_vs_sequential_sim.py [LLMRouterBench_root]
"""
import glob, json, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/research/LLMRouterBench")
BENCH = [("aime", "hybrid"), ("gpqa", "test"), ("livecodebench", "test"),
         ("livemathbench", "test"), ("mmlupro", "test_1000")]
EDGE_MODELS = ["Qwen3-8B", "NVIDIA-Nemotron-Nano-9B-v2", "Llama-3.1-8B-Instruct"]
BIG_MODELS = ["qwen3-235b-a22b-2507", "deepseek-v3-0324"]

# ---- ASSUMED profiles (single stream) ----
SERVER_TPS = {m: 90.0 for m in EDGE_MODELS}            # 8B on a datacentre GPU
SERVER_TPS.update({"qwen3-235b-a22b-2507": 45.0, "deepseek-v3-0324": 30.0})
EDGE_TPS_SWEEP = [15.0, 40.0]                          # 8B on laptop-class / desktop GPU
PREFILL_TPS_EDGE, PREFILL_TPS_SERVER = 800.0, 8000.0
P_EDGE_ACTIVE_W, P_EDGE_WAIT_W = 30.0, 3.0             # device power: computing vs waiting on radio
SLO_SWEEP_S = [60.0, 300.0]                            # per-query deadline; need >=95% within it per task
# live states: (name, RTT s, server throughput multiplier, remote available)
STATES = [("good", 0.02, 1.0, True), ("high-RTT", 0.30, 1.0, True),
          ("server-contended", 0.02, 0.25, True), ("remote-down", 0.02, 1.0, False)]


def load(b, s, m):
    fs = sorted(glob.glob(os.path.join(ROOT, "results/bench", b, s, m, "*.json")))
    if not fs:
        return None
    out = {}
    for x in json.load(open(fs[-1]))["records"]:
        key = x.get("index", x.get("id", len(out)))
        out[key] = (float(x["score"]), int(x["completion_tokens"]), int(x.get("prompt_tokens") or 0))
    return out


def actions():
    for m in EDGE_MODELS:
        yield (m, "EDGE")
        yield (m, "REMOTE")
    for m in BIG_MODELS:
        yield (m, "REMOTE")


def lat_energy(rec, m, path, edge_tps, state):
    _, rtt, mult, up = state
    _, n, p = rec
    if path == "EDGE":
        t = p / PREFILL_TPS_EDGE + n / edge_tps
        return t, t * P_EDGE_ACTIVE_W
    if not up:
        return float("inf"), float("inf")
    t = rtt + p / PREFILL_TPS_SERVER + n / (SERVER_TPS[m] * mult)
    return t, t * P_EDGE_WAIT_W


def evaluate(data, task, a, edge_tps, state, slo):
    """mean acc, SLO attainment, mean device energy of action a on task under state."""
    recs = data[task][a[0]]
    acc = att = en = 0.0
    for r in recs.values():
        t, e = lat_energy(r, a[0], a[1], edge_tps, state)
        ok = t <= slo
        acc += r[0] if ok else 0.0          # a missed deadline earns zero utility
        att += ok
        en += e if e != float("inf") else 0.0
    k = len(recs)
    return acc / k, att / k, en / k


def joint_pick(data, task, edge_tps, state, slo, allowed=None):
    """max deadline-aware utility (correct AND on time); tie-break lower device energy."""
    best = None
    for a in actions():
        if allowed is not None and a[1] not in allowed:
            continue
        acc, att, en = evaluate(data, task, a, edge_tps, state, slo)
        key = (round(acc, 3), -en)
        if best is None or key > best[0]:
            best = (key, a)
    return best[1]


def main():
    data = {}
    for b, s in BENCH:
        data[b] = {}
        for m in EDGE_MODELS + BIG_MODELS:
            r = load(b, s, m)
            if r is not None:
                data[b][m] = r
    tasks = [b for b, _ in BENCH if all(m in data[b] for m in EDGE_MODELS + BIG_MODELS)]
    print(f"tasks with all models cached: {tasks}\n")
    # deployment-oblivious task table: argmax raw accuracy (no deadline), then best path
    oblivious_model = {t: max(EDGE_MODELS + BIG_MODELS,
                              key=lambda m: sum(r[0] for r in data[t][m].values()) / len(data[t][m]))
                       for t in tasks}
    print("deployment-oblivious model per task:", oblivious_model, "\n")
    print("| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks whose action differs from state-oblivious |")
    print("|---|---|---|---|---|---|---|---|")
    for edge_tps in EDGE_TPS_SWEEP:
        for slo in SLO_SWEEP_S:
            nominal = {t: joint_pick(data, t, edge_tps, STATES[0], slo) for t in tasks}
            for st in STATES:
                live = {t: joint_pick(data, t, edge_tps, st, slo) for t in tasks}
                pols = {
                    "joint+live": live,
                    "deadline-aware model table, REMOTE-only, live": {
                        t: joint_pick(data, t, edge_tps, st, slo, {"REMOTE"}) for t in tasks},
                    "deadline-aware model table, REMOTE-only, nominal": {
                        t: joint_pick(data, t, edge_tps, STATES[0], slo, {"REMOTE"}) for t in tasks},
                    "joint, remote-down -> edge failover only": {
                        t: (nominal[t] if st[3] else joint_pick(data, t, edge_tps, st, slo, {"EDGE"}))
                        for t in tasks},
                    "joint, state-oblivious": nominal,
                    "oblivious model -> best path": {
                        t: min(((m, p) for (m, p) in actions() if m == oblivious_model[t]),
                               key=lambda a: -evaluate(data, t, a, edge_tps, st, slo)[0])
                        for t in tasks},
                    "edge-only best model": {
                        t: max(((m, "EDGE") for m in EDGE_MODELS),
                               key=lambda a: evaluate(data, t, a, edge_tps, st, slo)[0])
                        for t in tasks},
                }
                for name, pol in pols.items():
                    vals = [evaluate(data, t, pol[t], edge_tps, st, slo) for t in tasks]
                    u = sum(v[0] for v in vals) / len(vals)
                    a = sum(v[1] for v in vals) / len(vals)
                    e = sum(v[2] for v in vals) / len(vals)
                    diff = sum(pol[t] != nominal[t] for t in tasks) if name == "joint+live" else ""
                    print(f"| {edge_tps:.0f} | {slo:.0f} | {st[0]} | {name} | {u:.3f} | {a:.3f} | {e:.0f} | {diff} |")
            print("\nnominal-state joint actions (edge %.0f tok/s, SLO %.0f s): %s\n" % (edge_tps, slo, nominal))
            print("| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks differing |")
            print("|---|---|---|---|---|---|---|---|")


if __name__ == "__main__":
    main()
