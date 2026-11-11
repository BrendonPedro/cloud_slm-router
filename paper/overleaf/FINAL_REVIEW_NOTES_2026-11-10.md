# Final review notes for the second and third revision passes (2026-11-10, updated 2026-11-11)

Scope of this file: remaining TODOs, unverified claims, compile issues, advisor hardware references, the optional bootstrap result, and sentences to review by hand. Nothing else.

## 1. Remaining TODOs

1. Template header. The `\thanks` lines ("IEEE Publication Technology Group", "Manuscript received April 19, 2021"), the `\markboth` journal line and `\IEEEpubid` are placeholder text from the 2026-10-08 draft. No target venue is recorded anywhere in the repository (`research/problem-as-written.md` l.34 calls the header "template placeholder text"). Replace once the venue is chosen. The `\todo` for this is a LaTeX comment next to `\author`, so it does not print.
2. Benchmark citations. MMLU-Pro, GPQA, LiveMathBench, LiveCodeBench, BBH, KorBench, MBPP, MELD, MedQA, FinQA are named without citations. LLMRouterBench [dataset] cites them; add the primary citations only from the official papers.
3. `paper/overleaf/architecture-compact-2026-10-08.pdf` is still tracked in the repo but is no longer referenced by `main.tex`. It shows the Edge/Split/Remote optimiser that was never built. Delete it with `git rm` when you commit, or keep it for history; the manuscript does not use it.
4. E0 archives. The Stage-1 and Stage-2 tarballs are untracked in `~/research/LLMRouterBench`. The paper says the gates "recompute from the archived profiles"; archive them in the experiment repo (audit §8 A2) before submission.
5. Overleaf compile. The local build used Tectonic (XeTeX engine, Computer Modern fallback for Times). Overleaf uses pdfLaTeX. Expect identical layout logic but recheck page breaks and the four figures after upload.
6. Freeze E1-OPT. Review `~/research/LLMRouterBench/diagnostics/deployment_e1opt/PREREG_E1OPT.md`, then tag `e1opt-prereg-v1` before any GPU time. Nothing in E1-OPT has run on a GPU.
7. Lab inventory (E1-OPT Stage 0). Run the RUNBOOK §1 commands on the Asus server and the DGX Spark, decide roles from the output, run the desk gate with the server GPU's datasheet bandwidth. Ask the lab who assigns roles, whether `tc netem` is allowed, and whether the 2 x RTX 3090 edge server of the October manuscript is the Asus machine.
8. E1-OPT GPU equivalence driver (`e1_bench.py equivalence`), the runtime freeze writer, the edge-segment profiler and the joint cell driver remain to be written (IMPLEMENTATION_PLAN work items 1 to 5).
9. Overleaf recompile of the third pass: Fig. 5 uses `x dir=reverse` and a rotated node; check it renders under pdfLaTeX. Local Tectonic build: see §3.
10. Memory classes in Table I row B2 say "U-max (3,3), (5,5), (9,9) at 12/16/24 GB" and the text explains that the 24 GB class is blocked by the competitor rule. Check that this reads correctly to you; the split itself fits at 24 GB.

## 2. Unverified or deliberately weak claims

- "Longer queries were routed better than short ones (0.626 vs 0.556)". Source: `diagnostics/capability_profile/CAPABILITY_PROFILE_REPORT.md` l.143 (B Macro-F1 by length bucket). Verified, but it is a single split of one router; it supports only "truncation is not the limiting factor".
- The 24 GB competitor failure. The vLLM log says: "The model's max seq len (17920) is larger than the maximum number of tokens that can be stored in KV cache (12896)". The frozen rule (PREREG §8.4(b), C11) classifies any non-recognised error as "engine" and blocks the class. The paper describes the error literally and then states the rule. Do not call it "Split failed at 24 GB".
- The 20-model pool paragraph (E1, +0.42 [−0.18, +1.01]) uses accuracy over 20 models, not the pair. It is labelled "a different protocol" in the text. Source: `decision/E1-pool-headroom/RESULTS.md`.
- The simulation sentence in Section III-C ("changing the round-trip time from 20 to 300 ms changed the preferred Edge or Remote action for none of the five simulated tasks") is from `deployment-pivot/evidence/joint_vs_sequential_sim.md` (assumed throughputs). It is labelled exploratory and reports no utility numbers. Delete the paragraph if you prefer a tighter paper; nothing else depends on it.
- Bibliography entries added this pass without a DOI check: MiniLM NeurIPS 2020 pages (5776–5788), Sentence-BERT EMNLP 2019 pages (3982–3992), vLLM SOSP 2023 pages (611–626), AWQ MLSys 2024 pages (87–100). Titles, authors, venues and years are correct to my knowledge; verify page numbers on the publisher pages before submission. Qwen3 (arXiv 2505.09388), DeepSeek-R1 (Nature 645:633–638, doi 10.1038/s41586-025-09422-z), the DeepSeek-R1-0528-Qwen3-8B model card, and GTE (arXiv 2308.03281) were checked online on 2026-11-10.

## 3. Compile status

- Third pass (2026-11-11): `main.tex` compiles with the same Tectonic binary, exit 0; page count and the new Fig. 5 checked in the local PDF (see the final report). Static checks repeated: zero em dashes; every `\ref` has a label (`sec:b-reanalysis`, `fig:speedup` added).
- Second pass: `main.tex` compiles with Tectonic 0.15.0 (`tectonic main.tex`), exit 0, 10 pages, no undefined references or citations, no overfull boxes after the table and figure fixes. Local PDF: `/tmp/claude-1000/-home-brendonpedro-dev-cloud-slm-router/d68b30c1-dbbe-4d0d-a08d-ec28f5930c16/scratchpad/main_revised_local_build.pdf` (scratch; not in the repo).
- All four pgfplots/TikZ figures render: Fig. 1 within-benchmark AUC, Fig. 2 same scores two targets, Fig. 3 gate sequence, Fig. 4 bounded advantage vs deadline.
- `\IEEEpubidadjcol` was added at the start of the third introduction paragraph to stop the pubid footer overlapping column 1 on page 1. If Overleaf's column break differs, move it to whatever paragraph starts column 2 of page 1.
- Static checks: every `\cite` key has a `\bibitem` and vice versa; every `\ref` has a label; zero em dashes; zero `\textbf` in the body.

## 4. Advisor hardware instruction (corrected 2026-11-11)

The 2026-11-10 version of this section said that no explicit instruction from the advisor naming a hardware platform exists. That statement was wrong and is withdrawn. The instruction was missing from the repositories, not from the record. The advisor stated that the model pool is the SLMs and Split-LLMs in the paper and that "the computational resources will be the Asus server and DGX Spark", and later that the router would be tested "with our server resources" once it performed well.

What follows from it:
- The RTX 3090 (Stage 1, emulated 12/16/24 GB budgets) and the rented H200 (S1, Stage 2) are controlled screening hardware. The manuscript now says so in the abstract, Section V-A, the Limitations and the Conclusion, and says that the target-hardware measurement has not been made.
- The intended final system is the lab's Asus server and DGX Spark. The manuscript names them as the intended target system without naming the advisor.
- Roles are not assigned anywhere. The Asus machine's GPU, memory, OS and network are undocumented in both repositories. The DGX Spark is known only as a product (public spec: GB10, 128 GB unified at 273 GB/s, aarch64, 10 GbE + 2 x ConnectX-7). The physical link between the two machines and any SSH access are undocumented. The full audit table is in `SPLIT_RUNTIME_REASSESSMENT_2026-11-11.md` §6.3; the inventory commands are in the E1-OPT RUNBOOK §1.
- Does G-UB2 STOP remove the need for such hardware? No. G-UB2 removed the frozen eager implementation; the reanalysis shows the rule would have been met by a 1.2x faster server step while the measured step ran 5.7x above its roofline. The final deployment conclusion waits for the pre-registered E1-OPT on the lab pair. One derived fact constrains the roles: a server with 273 GB/s fails the gate at its bandwidth roofline in every cell, so the DGX Spark cannot be the Split server; the Asus machine's GPU decides whether the pair can host the experiment at all.

## 5. Optional bootstrap (run; post hoc)

- Data: the exact 103 rows in `diagnostics/winner_label_stability/target_only_eval_rows.csv` (dataset, B_student_score, original_target, repeated_target). No retraining, no thresholds changed, no embeddings, CPU only.
- Script and result saved beside the artifact: `diagnostics/winner_label_stability/target_only_bootstrap.py` and `target_only_bootstrap.json` (untracked, in the experiment repo).
- Procedure: 10,000 replicates, seed 20261110; resample queries with replacement within each benchmark; score both targets on the same resampled rows; drop a benchmark from both macro means if either target is single-class in that replicate (happened in 0.16% of replicates).
- Within-benchmark macro AUC: observed +0.0677 (0.5728 → 0.6405); bootstrap median +0.0666; 95% percentile interval [−0.0164, +0.1549]; 94.56% of replicates > 0.
- Within-benchmark macro Macro-F1: observed +0.0401; median +0.0404; interval [−0.0115, +0.0940]; 93.7% > 0.
- Per-benchmark AUC difference, fraction of replicates > 0: BBH 68%, FinQA 94%, KorBench 76%, MBPP 64%, MELD 77%, MedQA 3% (MedQA median −0.083).
- Interpretation used in the paper: the interval includes zero, so the gain is reported as descriptive and not called statistically significant. The text labels the analysis post hoc.

## 6. Sentences to review by hand (may still not sound like you)

1. Abstract: now 343 words after the third pass (the screening-hardware sentence and the reanalysis sentence were added). IEEE journals usually want about 250. Cut the semantic numbers first if you need to shorten; keep the hardware and reanalysis sentences.
2. Introduction ¶2 now reads: "Without useful query-level model-suitability information, the semantic choice reduces to a fixed or task-level model policy, although placement may still respond to memory, deadline and system state."
3. Section III-C, last paragraph: the simulation paragraph is gone; the structural argument replaced it. Check that the three sentences are how you would argue it.
4. Section IV-C, last paragraph now reads: "Adding representation or classifier capacity had produced gains of at most 0.03 Macro-F1 and had not changed the within-benchmark picture, so we examined the formulation and the labels instead."
5. Section IV-D (ordinal): the description of "cumulative decomposition into two binary boundaries ... enforced to be consistent" summarises `run_ordinal_cv.py`; adjust wording to how you described it to Film.
6. Section V-E, last paragraph now reads: "G-UB1 and G-UB2 differ only in the server-compute term. Replacing the datasheet estimate with the measured H200 compute of the frozen runtime reduced the best bound from +12.25 to +0.5 points."
6b. New Section V-F (reanalysis) and Discussion VI-D (runtime limitation and the pre-registered follow-up): long paragraphs; split them if you prefer. They name the Asus server and DGX Spark as the intended target system; check that this is acceptable in a submitted paper, or replace with "the laboratory's edge and server machines".
7. Discussion A: "Aggregate Macro-F1 and AUC overstated within-task signal because the benchmarks differ in which model wins on average, and the router can learn that difference from the query text."
8. Discussion C, last sentences now quantify the mechanism (27 % late at 60 s; 0.63 vs 0.58 at long deadlines).
9. Conclusion now says the deployment conclusion is provisional until E1-OPT runs on the target system, and that the Split conclusion can change only under that pre-registration. Check that you agree.
10. Contribution list in the Introduction: three items, not four. Film's "deployment pivot" is in the narrative and in contribution 3; add a fourth item only if you want the pivot itself listed.
