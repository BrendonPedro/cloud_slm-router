"""Hardware-branch desk check for HARDWARE-PLAN.md (no hardware touched).

The repo does not document the "Asus" edge machine or the "DGX" server. This script
takes each plausible identity of those machines and asks two questions, using public
spec-sheet numbers only:

1. Memory: which E0 / F3 models fit (weights + bf16 KV for 16k tokens + 1.5 GB overhead,
   the same memory model as split_vs_quant_desk_check.py)?
2. Speed: what is the batch-1 decode *upper bound* in tok/s? Decode at batch 1 is
   memory-bandwidth bound: every token reads all weights plus the KV cache. The bound is
   eff * BW / (weight_bytes + kv_bytes(ctx)), with eff = 0.7 (ASSUMED achievable fraction
   of peak; vLLM/llama.cpp typically reach 0.6-0.8 at batch 1).

It also checks the assumed throughputs used by joint_vs_sequential_sim.py and
baseline_crossfit_check.py (edge 8B at 15/40 tok/s; server 8B at 90 tok/s) against the
bound, and gives the SPLIT per-token bound for each (edge, server) pair at U-max(16).

These are upper bounds from spec sheets, not measurements. They decide which hardware
branches can host E0 at all, not any E0 outcome.

Run: python3 hardware_roofline.py > hardware_roofline.md
"""

GB = 1e9
EFF = 0.7          # ASSUMED achievable fraction of peak memory bandwidth at batch 1
CTX_FIT = 16384    # context the memory check must hold (thinking traces are long)
CTX_DECODE = 4096  # mean context during decode for the speed bound
OVERHEAD = 1.5     # GB, same as split_vs_quant_desk_check.py

# name: (checkpoint GB [HF API, fetched 2026-11-07], layers, kv_heads, head_dim)
MODELS = {
    "Qwen3-8B-AWQ": (6.1, 36, 8, 128),
    "Qwen3-8B": (16.4, 36, 8, 128),
    "Qwen3-14B-AWQ": (10.0, 40, 8, 128),
    "Qwen3-32B-AWQ": (19.3, 64, 8, 128),
    "Qwen3-32B": (65.5, 64, 8, 128),
}

# name: (memory GB usable by the accelerator, peak memory BW GB/s, bf16 native, role, note)
# Spec-sheet values (vendor product pages). "bf16 native" matters because E0 forbids an
# fp16 cast of Qwen3 hidden states (E0 §7).
HW = {
    "RTX 3090 (manuscript edge, 1 of 2)": (24, 936, True, "edge", "manuscript L202"),
    "RTX 4090 desktop": (24, 1008, True, "edge", "if Asus is a desktop"),
    "RTX 4090 Laptop": (16, 576, True, "edge", "if Asus is a ROG/Strix/Zephyrus laptop"),
    "RTX 4070 Laptop": (8, 256, True, "edge", "if Asus is a mid-range laptop"),
    "GB10 (ASUS Ascent GX10 / DGX Spark)": (128, 273, True, "edge or server", "unified LPDDR5x"),
    "Jetson AGX Orin 64GB": (64, 204.8, True, "edge", "reference edge board"),
    "Ryzen 5 8500G CPU (this WSL box)": (9, 83, False, "none", "9 GB RAM in WSL, no CUDA"),
    "A100 80GB SXM (DGX A100 / Station)": (80, 2039, True, "server", "per GPU"),
    "H100 80GB SXM (DGX H100)": (80, 3350, True, "server", "per GPU"),
    "V100 32GB (DGX-1 / DGX-2)": (32, 900, False, "server", "per GPU; no bf16 tensor cores"),
}


def kv_gb(L, kvh, hd, ctx):
    return L * kvh * hd * 2 * 2 * ctx / GB


def need_gb(m):
    w, L, kvh, hd = MODELS[m]
    return w + kv_gb(L, kvh, hd, CTX_FIT) + OVERHEAD


def decode_bound(m, bw, n_gpu=1):
    """Batch-1 decode tok/s upper bound; tensor parallel over n_gpu splits the bytes."""
    w, L, kvh, hd = MODELS[m]
    return EFF * bw * n_gpu / (w + kv_gb(L, kvh, hd, CTX_DECODE))


def split_bound(edge_bw, srv_bw, edge_layers, rtt_ms, srv_gpus=1):
    """Per-token SPLIT bound for Qwen3-32B bf16, U-shaped, edge holds embed/head + k+j layers."""
    w, L, kvh, hd = MODELS["Qwen3-32B"]
    emb_head = 2 * 151936 * 5120 * 2 / GB
    per_layer = (w - emb_head) / L + kv_gb(1, kvh, hd, CTX_DECODE)
    t_edge = (emb_head * 0.5 + edge_layers * per_layer) / (EFF * edge_bw)  # LM head is half of emb+head
    t_srv = (L - edge_layers) * per_layer / (EFF * srv_bw * srv_gpus)
    return 1.0 / (t_edge + t_srv + rtt_ms / 1000)


def main():
    print("# Hardware-branch roofline (spec sheets + assumed eff = %.1f; NOT measured)\n" % EFF)
    print("Memory need at 16k ctx (weights + bf16 KV + %.1f GB):" % OVERHEAD,
          ", ".join(f"{m} {need_gb(m):.1f} GB" for m in MODELS), "\n")
    print("## 1. Fit (F = fits at 16k ctx) and batch-1 decode bound (tok/s) per machine\n")
    print("| machine | mem GB | BW GB/s | bf16 | role | " + " | ".join(MODELS) + " |")
    print("|---|---|---|---|---|" + "---|" * len(MODELS))
    for h, (mem, bw, bf16, role, _) in HW.items():
        cells = []
        for m in MODELS:
            fits = need_gb(m) <= mem
            cells.append(f"{'F ' if fits else '— '}{decode_bound(m, bw):.0f}" if fits
                         else f"— ({decode_bound(m, bw):.0f})")
        print(f"| {h} | {mem} | {bw} | {'yes' if bf16 else 'NO'} | {role} | " + " | ".join(cells) + " |")
    print("\nParenthesised = bound if it fitted (it does not on one device).\n")

    print("## 2. Server branches for REMOTE Qwen3-32B bf16 (the SPLIT reference)\n")
    print("| server branch | GPUs used | fits | 32B bf16 bound tok/s | 4k-token trace (s) | 16k-token trace (s) |")
    print("|---|---|---|---|---|---|")
    for h, n in [("A100 80GB SXM (DGX A100 / Station)", 1), ("A100 80GB SXM (DGX A100 / Station)", 2),
                 ("H100 80GB SXM (DGX H100)", 1), ("H100 80GB SXM (DGX H100)", 2),
                 ("GB10 (ASUS Ascent GX10 / DGX Spark)", 1), ("V100 32GB (DGX-1 / DGX-2)", 4)]:
        mem, bw, bf16, _, _ = HW[h]
        fits = need_gb("Qwen3-32B") <= mem * n
        tps = decode_bound("Qwen3-32B", bw, n)
        flag = "" if bf16 else " (no native bf16)"
        print(f"| {h}{flag} | {n} | {'yes' if fits else 'no'} | {tps:.1f} | {4096/tps:.0f} | {16384/tps:.0f} |")

    print("\n## 3. Assumed sim throughputs vs bound\n")
    print("| assumption (joint_vs_sequential_sim.py) | value | bound on plausible hardware | verdict |")
    print("|---|---|---|---|")
    r3090 = decode_bound("Qwen3-8B", 936)
    r3090q = decode_bound("Qwen3-8B-AWQ", 936)
    r4090l = decode_bound("Qwen3-8B-AWQ", 576)
    gb10 = decode_bound("Qwen3-8B-AWQ", 273)
    a100 = decode_bound("Qwen3-8B", 2039)
    print(f"| edge 8B fast | 40 tok/s | 3090 bf16 {r3090:.0f}, 3090 AWQ {r3090q:.0f}, 4090L AWQ {r4090l:.0f}, GB10 AWQ {gb10:.0f} | plausible on a discrete GPU |")
    print(f"| edge 8B slow | 15 tok/s | Orin AWQ {decode_bound('Qwen3-8B-AWQ', 204.8):.0f}, CPU 8500G AWQ {decode_bound('Qwen3-8B-AWQ', 83):.0f} | plausible for board/CPU class |")
    print(f"| server 8B | 90 tok/s | A100 bf16 {a100:.0f}, H100 bf16 {decode_bound('Qwen3-8B', 3350):.0f}, GB10 bf16 {decode_bound('Qwen3-8B', 273):.0f} | plausible only on A100/H100 |")

    print("\n## 4. SPLIT per-token bound, Qwen3-32B bf16, U-max(16) = 10 edge layers\n")
    print("| edge | server | RTT ms | SPLIT tok/s bound | REMOTE tok/s bound (same server) | SPLIT/REMOTE |")
    print("|---|---|---|---|---|---|")
    pairs = [("RTX 3090 (manuscript edge, 1 of 2)", "A100 80GB SXM (DGX A100 / Station)"),
             ("RTX 3090 (manuscript edge, 1 of 2)", "H100 80GB SXM (DGX H100)"),
             ("RTX 4090 Laptop", "A100 80GB SXM (DGX A100 / Station)"),
             ("GB10 (ASUS Ascent GX10 / DGX Spark)", "A100 80GB SXM (DGX A100 / Station)"),
             ("RTX 3090 (manuscript edge, 1 of 2)", "GB10 (ASUS Ascent GX10 / DGX Spark)")]
    for e, s in pairs:
        for rtt in (1, 20, 50):
            sp = split_bound(HW[e][1], HW[s][1], 10, rtt)
            rem = decode_bound("Qwen3-32B", HW[s][1])
            print(f"| {e} | {s} | {rtt} | {sp:.1f} | {rem:.1f} | {sp/rem:.2f} |")


if __name__ == "__main__":
    main()
