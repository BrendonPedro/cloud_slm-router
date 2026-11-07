"""Analytic lower bound: per-decoded-token latency of SPLIT(d) vs REMOTE vs EDGE.
Pure arithmetic over the cost model in paper/main-revised.tex §cost (Eq. T(Split(d))).
No measurements -- every throughput number below is an ASSUMPTION to be replaced by E0.

Key structural fact: in REMOTE, the server loops autoregressively and streams tokens
one-way, so the network contributes ~RTT/2 once (plus negligible per-token bytes).
In SPLIT with the embedding/first-d layers on the edge, every decoded token needs the
next token's hidden state to cross edge->server and the sampled token to come back:
one full RTT + h*b bytes uplink PER TOKEN.
"""
import itertools

H = {"Qwen3-8B": 4096, "Qwen3-14B": 5120, "Qwen3-32B": 5120}   # hidden sizes (model cards)
B_ELEM = 2          # fp16 activations
RTTS_MS = [1, 5, 20, 50, 100]
BW_MBPS = [10, 100, 1000]
# ASSUMED compute per token (ms) for a 32B-class model: server full model, edge share
T_SERVER_FULL = 25.0   # assumed server decode ms/token for the whole model
EDGE_FRAC = 0.25       # assumed fraction of layers on the edge
T_EDGE_PART = 4 * T_SERVER_FULL * EDGE_FRAC   # assume edge GPU 4x slower per layer

print("| RTT ms | BW Mbps | act KB/tok | REMOTE ms/tok | SPLIT ms/tok | SPLIT/REMOTE |")
print("|---|---|---|---|---|---|")
h = H["Qwen3-32B"]
for rtt, bw in itertools.product(RTTS_MS, BW_MBPS):
    act_bytes = h * B_ELEM
    tx_ms = act_bytes * 8 / (bw * 1e6) * 1e3
    remote = T_SERVER_FULL                       # streamed; RTT amortised over the response
    split = T_EDGE_PART + rtt + tx_ms + T_SERVER_FULL * (1 - EDGE_FRAC)
    print(f"| {rtt} | {bw} | {act_bytes/1024:.1f} | {remote:.1f} | {split:.1f} | {split/remote:.2f} |")
