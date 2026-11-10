# Final review notes for the second revision pass (2026-11-10)

Scope of this file: remaining TODOs, unverified claims, compile issues, advisor hardware references, the optional bootstrap result, and sentences to review by hand. Nothing else.

## 1. Remaining TODOs

1. Template header. The `\thanks` lines ("IEEE Publication Technology Group", "Manuscript received April 19, 2021"), the `\markboth` journal line and `\IEEEpubid` are placeholder text from the 2026-10-08 draft. No target venue is recorded anywhere in the repository (`research/problem-as-written.md` l.34 calls the header "template placeholder text"). Replace once the venue is chosen. The `\todo` for this is a LaTeX comment next to `\author`, so it does not print.
2. Benchmark citations. MMLU-Pro, GPQA, LiveMathBench, LiveCodeBench, BBH, KorBench, MBPP, MELD, MedQA, FinQA are named without citations. LLMRouterBench [dataset] cites them; add the primary citations only from the official papers.
3. `paper/overleaf/architecture-compact-2026-10-08.pdf` is still tracked in the repo but is no longer referenced by `main.tex`. It shows the Edge/Split/Remote optimiser that was never built. Delete it with `git rm` when you commit, or keep it for history; the manuscript does not use it.
4. E0 archives. The Stage-1 and Stage-2 tarballs are untracked in `~/research/LLMRouterBench`. The paper says the gates "recompute from the archived profiles"; archive them in the experiment repo (audit §8 A2) before submission.
5. Overleaf compile. The local build used Tectonic (XeTeX engine, Computer Modern fallback for Times). Overleaf uses pdfLaTeX. Expect identical layout logic but recheck page breaks and the four figures after upload.
6. Memory classes in Table I row B2 say "U-max (3,3), (5,5), (9,9) at 12/16/24 GB" and the text explains that the 24 GB class is blocked by the competitor rule. Check that this reads correctly to you; the split itself fits at 24 GB.

## 2. Unverified or deliberately weak claims

- "Longer queries were routed better than short ones (0.626 vs 0.556)". Source: `diagnostics/capability_profile/CAPABILITY_PROFILE_REPORT.md` l.143 (B Macro-F1 by length bucket). Verified, but it is a single split of one router; it supports only "truncation is not the limiting factor".
- The 24 GB competitor failure. The vLLM log says: "The model's max seq len (17920) is larger than the maximum number of tokens that can be stored in KV cache (12896)". The frozen rule (PREREG §8.4(b), C11) classifies any non-recognised error as "engine" and blocks the class. The paper describes the error literally and then states the rule. Do not call it "Split failed at 24 GB".
- The 20-model pool paragraph (E1, +0.42 [−0.18, +1.01]) uses accuracy over 20 models, not the pair. It is labelled "a different protocol" in the text. Source: `decision/E1-pool-headroom/RESULTS.md`.
- The simulation sentence in Section III-C ("changing the round-trip time from 20 to 300 ms changed the preferred Edge or Remote action for none of the five simulated tasks") is from `deployment-pivot/evidence/joint_vs_sequential_sim.md` (assumed throughputs). It is labelled exploratory and reports no utility numbers. Delete the paragraph if you prefer a tighter paper; nothing else depends on it.
- Bibliography entries added this pass without a DOI check: MiniLM NeurIPS 2020 pages (5776–5788), Sentence-BERT EMNLP 2019 pages (3982–3992), vLLM SOSP 2023 pages (611–626), AWQ MLSys 2024 pages (87–100). Titles, authors, venues and years are correct to my knowledge; verify page numbers on the publisher pages before submission. Qwen3 (arXiv 2505.09388), DeepSeek-R1 (Nature 645:633–638, doi 10.1038/s41586-025-09422-z), the DeepSeek-R1-0528-Qwen3-8B model card, and GTE (arXiv 2308.03281) were checked online on 2026-11-10.

## 3. Compile status

- `main.tex` compiles with Tectonic 0.15.0 (`tectonic main.tex`), exit 0, 10 pages, no undefined references or citations, no overfull boxes after the table and figure fixes. Local PDF: `/tmp/claude-1000/-home-brendonpedro-dev-cloud-slm-router/d68b30c1-dbbe-4d0d-a08d-ec28f5930c16/scratchpad/main_revised_local_build.pdf` (scratch; not in the repo).
- All four pgfplots/TikZ figures render: Fig. 1 within-benchmark AUC, Fig. 2 same scores two targets, Fig. 3 gate sequence, Fig. 4 bounded advantage vs deadline.
- `\IEEEpubidadjcol` was added at the start of the third introduction paragraph to stop the pubid footer overlapping column 1 on page 1. If Overleaf's column break differs, move it to whatever paragraph starts column 2 of page 1.
- Static checks: every `\cite` key has a `\bibitem` and vice versa; every `\ref` has a label; zero em dashes; zero `\textbf` in the body.

## 4. Advisor hardware references found

Searched: `~/dev/cloud_slm-router` (all .md/.txt/.tex, the untracked `tasks/` files, the memory directory) and `~/research/LLMRouterBench` (.md) for DGX, DGX Spark, Spark, ASUS, Ascent, GB10, Jetson, Orin, and for quoted instructions from Film.

- No explicit instruction from Film naming a hardware platform was found.
- The only origin of "DGX" and "Asus" is your own task brief `tasks/deployment-optimization-pivot-2026-11-07.md` §F ("We potentially have: local desktop / laptop-class edge hardware; Asus / edge machine; DGX / server-class hardware. Do not assume exact capabilities without checking repository documentation."). It is a list of possibly available machines, not an experimental requirement.
- Everything else (`deployment-pivot/HARDWARE-PLAN.md`, `GO-NOGO-REPORT.md`, `WEEK-EXECUTION-PLAN.md`, `diagnostics/deployment_e0/RUNBOOK.md`) is derived planning text that calls both machines "undocumented" and pre-declares what to do if the DGX turns out to be a DGX Spark/GB10 (not a valid E0 server) or a V100 DGX (no bf16).
- Does G-UB2 STOP remove the need for such hardware? Yes for E0. The gate stopped on measured H200 server compute with zero network time; a slower server (GB10 at 273 GB/s) could only lower the bound further, and the edge side was already measured on a physical RTX 3090.
- Would a small physical validation still answer a different question? Only two candidates, both outside E0: (a) running the best 12 GB edge competitor (Qwen3-8B-AWQ, vLLM) on a physical 12 or 16 GB device to check that the emulated-cap latency is not optimistic for the competitor (this can only make Split look better by a bounded amount and cannot flip UB2 unless the physical device is dramatically slower); (b) measuring the eager split runtime against an optimised one, which is a new design and needs its own pre-registration. Neither is needed for the current manuscript's claims.

## 5. Optional bootstrap (run; post hoc)

- Data: the exact 103 rows in `diagnostics/winner_label_stability/target_only_eval_rows.csv` (dataset, B_student_score, original_target, repeated_target). No retraining, no thresholds changed, no embeddings, CPU only.
- Script and result saved beside the artifact: `diagnostics/winner_label_stability/target_only_bootstrap.py` and `target_only_bootstrap.json` (untracked, in the experiment repo).
- Procedure: 10,000 replicates, seed 20261110; resample queries with replacement within each benchmark; score both targets on the same resampled rows; drop a benchmark from both macro means if either target is single-class in that replicate (happened in 0.16% of replicates).
- Within-benchmark macro AUC: observed +0.0677 (0.5728 → 0.6405); bootstrap median +0.0666; 95% percentile interval [−0.0164, +0.1549]; 94.56% of replicates > 0.
- Within-benchmark macro Macro-F1: observed +0.0401; median +0.0404; interval [−0.0115, +0.0940]; 93.7% > 0.
- Per-benchmark AUC difference, fraction of replicates > 0: BBH 68%, FinQA 94%, KorBench 76%, MBPP 64%, MELD 77%, MedQA 3% (MedQA median −0.083).
- Interpretation used in the paper: the interval includes zero, so the gain is reported as descriptive and not called statistically significant. The text labels the analysis post hoc.

## 6. Sentences to review by hand (may still not sound like you)

1. Abstract, last two sentences ("Because the semantic router stayed too weak to carry a deployment system on its own, we moved the main problem to deployment optimisation and tested the one execution option whose value does not depend on a strong per-query router"). Long; split if you prefer.
2. Introduction ¶2: "a deployment optimiser that cannot tell which model a query needs reduces to a fixed placement policy." Check that this is how you would put it.
3. Section III-C, last paragraph (the simulation justification). Delete if unwanted.
4. Section IV-C, last paragraph: "This result changed the next step: more classifier capacity would not help if the input signal is mostly task identity, so we examined the formulation and the labels instead."
5. Section IV-D (ordinal): the description of "cumulative decomposition into two binary boundaries ... enforced to be consistent" summarises `run_ordinal_cv.py`; adjust wording to how you described it to Film.
6. Section V-E, last paragraph: "The change from G-UB1 to G-UB2 is the whole result of the deployment test."
7. Discussion A: "Aggregate Macro-F1 and AUC overstated within-task signal because the benchmarks differ in which model wins on average, and the router can learn that difference from the query text."
8. Discussion C, last sentence: "At short deadlines Split loses because its decode step is slow; at long deadlines the 8B model's thinking traces finish and its accuracy catches up."
9. Conclusion, last two sentences (next experiment for the semantic conclusion; new design needed for the Split conclusion). Check that you agree with naming an optimised split runtime as the only route to a different Split result.
10. Contribution list in the Introduction: three items, not four. Film's "deployment pivot" is in the narrative and in contribution 3; add a fourth item only if you want the pivot itself listed.
