"""Pre-hardware upper bound on E0-R: can SPLIT beat the quantised edge model by >= 3.0 pt
of on-time utility in ANY no-raw-text cell, even under assumptions that favour SPLIT?

No new inference. What is cached vs assumed:
- CACHED: per-query (score, completion_tokens, prompt_tokens) of Qwen3-8B (thinking) on
  the four E0 sample benchmarks (LLMRouterBench). Used as the per-query length AND
  correctness base for every action, so length/hardness correlation is preserved.
- VENDOR: the Qwen3-32B-bf16 vs Qwen3-8B-AWQ mean accuracy gap (+8.4 pt, AWQ model cards,
  evidence/split_vs_quant_desk_check.md).
- ASSUMED: spec-sheet roofline decode speeds (evidence/hardware_roofline.py, eff 0.7),
  scaled by a runtime-efficiency factor; prefill at 2,000 tok/s on every path.

Bias, all in SPLIT's favour (so a FAIL here is strong, a PASS is weak):
1. SPLIT gets the full +8.4 pt of extra correct answers, capped only by the share of
   base-wrong queries it finishes on time (the extra answers must be on-time ones), and
   placed on exactly those queries.
2. The edge competitor gets Qwen3-8B correctness even when it is Qwen3-14B-AWQ
   (vendor +3.9 pt over 8B-AWQ is withheld).
3. SPLIT speed is the zero-serialisation roofline bound (Mix-or-Split: serialisation
   dominates real transfer cost); the edge competitor gets the same efficiency factor.
4. Good state only (no-raw-text: contention slows SPLIT but not EDGE).
5. Optional SPLIT length scale < 1 (a larger model may think for fewer tokens).

Usage: python3 -I e0_r_prior.py [LLMRouterBench_root] > e0_r_prior.md
"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hardware_roofline import HW, decode_bound, split_bound  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/research/LLMRouterBench")
# E0 §4.4 sample weights (60/60/40/40 of 200)
BENCH = [("mmlupro", "test_1000", 0.3), ("gpqa", "test", 0.3),
         ("livemathbench", "test", 0.2), ("livecodebench", "test", 0.2)]
BASE = "Qwen3-8B"
G_SPLIT = 0.084          # vendor: Qwen3-32B bf16 minus Qwen3-8B-AWQ, mean of 4 benchmarks
PREFILL_TPS = 2000.0
DEADLINES = [30, 60, 120, 300, 600, 1200, 1800, float("inf")]
MARGIN = 0.030

E3090, A100, H100, L4090 = ("RTX 3090 (manuscript edge, 1 of 2)", "A100 80GB SXM (DGX A100 / Station)",
                            "H100 80GB SXM (DGX H100)", "RTX 4090 Laptop")
# (label, edge hw, server hw, memory class, edge layers in U-max(M), edge competitor model)
CONFIGS = [
    ("12 GB, 3090-capped + A100", E3090, A100, 12, 6, "Qwen3-8B-AWQ"),
    ("16 GB, 3090-capped + A100", E3090, A100, 16, 10, "Qwen3-14B-AWQ"),
    ("24 GB, 3090 + A100", E3090, A100, 24, 18, "Qwen3-14B-AWQ"),
    ("16 GB, 4090 Laptop + A100", L4090, A100, 16, 10, "Qwen3-14B-AWQ"),
    ("12 GB, 3090-capped + H100", E3090, H100, 12, 6, "Qwen3-8B-AWQ"),
]


def load(b, s):
    fs = sorted(glob.glob(os.path.join(ROOT, "results/bench", b, s, BASE, "*.json")))
    recs = json.load(open(fs[-1]))["records"]
    return [(float(x["score"]), int(x["completion_tokens"]), int(x.get("prompt_tokens") or 0)) for x in recs]


DATA = {b: load(b, s) for b, s, _ in BENCH}


def util(tps, D, rtt_s, len_scale, gain):
    """Benchmark-weighted on-time utility. `gain` = extra correct share (SPLIT-favouring):
    added per benchmark, capped by the share of base-wrong queries that finish on time."""
    u = 0.0
    for b, _, w in BENCH:
        rs = DATA[b]
        ok = [rtt_s + ni / PREFILL_TPS + n * len_scale / tps <= D for sc, n, ni in rs]
        on = sum(sc for (sc, _, _), o in zip(rs, ok) if o)
        wrong_on = sum(1 - sc for (sc, _, _), o in zip(rs, ok) if o)
        u += w * (on + min(gain * len(rs), wrong_on)) / len(rs)
    return u


def fmt_d(d):
    return "∞" if d == float("inf") else f"{int(d)}"


def main():
    print("# E0-R prior: SPLIT (Qwen3-32B bf16, U-max) vs quantised edge, no-raw-text, good state\n")
    print("Upper bound on `U_SPLIT − U_EDGE-best` in points. Biased **for** SPLIT (see script docstring). "
          f"R needs ≥ +{MARGIN*100:.1f} pt at some D ≤ 600 s.\n")
    print("Base data: cached Qwen3-8B (thinking) per-query score + completion tokens, "
          "benchmarks weighted as the E0 sample (MMLU-Pro .3, GPQA .3, LiveMathBench .2, LiveCodeBench .2). "
          f"Base on-time utility at D = ∞: {util(1e9, float('inf'), 0, 1, 0):.3f}.\n")
    hdr = "| config | runtime eff | RTT ms | SPLIT len scale | SPLIT tok/s | EDGE model tok/s | " + \
          " | ".join(f"D={fmt_d(d)}" for d in DEADLINES) + " | min D passing |"
    print(hdr)
    print("|" + "---|" * (6 + len(DEADLINES) + 1))
    summary = []
    for label, ehw, shw, M, k, em in CONFIGS:
        for eff in (1.0, 0.6):
            for rtt in (1, 20):
                for ls in (1.0, 0.7):
                    stps = split_bound(HW[ehw][1], HW[shw][1], k, rtt) * eff
                    etps = decode_bound(em, HW[ehw][1]) * eff
                    cells, first = [], None
                    for D in DEADLINES:
                        m = util(stps, D, rtt / 1000, ls, G_SPLIT) - util(etps, D, 0, 1.0, 0.0)
                        cells.append(f"{m*100:+.1f}")
                        if first is None and m >= MARGIN:
                            first = D
                    print(f"| {label} | {eff} | {rtt} | {ls} | {stps:.1f} | {em} {etps:.0f} | " +
                          " | ".join(cells) + f" | {fmt_d(first) if first else 'never'} |")
                    summary.append((label, eff, rtt, ls, first))
    n = len(summary)
    p600 = sum(1 for s in summary if s[4] is not None and s[4] <= 600)
    print(f"\nRows where the upper bound reaches +3.0 pt at some D ≤ 600 s: {p600}/{n}.")
    strict = [s for s in summary if s[1] == 0.6 and s[3] == 1.0]
    p_strict = sum(1 for s in strict if s[4] is not None and s[4] <= 600)
    print(f"Of the rows with runtime eff 0.6 and unscaled SPLIT length: {p_strict}/{len(strict)}.")


if __name__ == "__main__":
    main()
