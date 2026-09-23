#!/usr/bin/env python3
"""Stdlib check: factual anchors in advisor/talking-points.md must appear in the
deliverable they are attributed to; Stage-0 counts are recomputed from the raw summary;
venue labels follow library.bib; no unrun result is stated as a finding."""
import pathlib, re, sys, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
tp = (R / "advisor/talking-points.md").read_text()
# (string asserted in talking points, evidence file that must contain it)
ANCHORS = [
    ("Jacobi", "research/problem-as-written.md"),
    ("Findings of ACL 2026", "research/closest-prior-art.md"),
    ("launched 2026-09-15", "research/closest-prior-art.md"),
    ("PRISM (AAAI'26", "research/novelty-matrix.md"),
    ("59%", "research/closest-prior-art.md"),
    ("35% at 8 layers", "research/closest-prior-art.md"),
    ("2.57×", "research/jacobi-forcing.md"),
    ("3.97×", "research/jacobi-forcing.md"),
    ("No established method with this exact name was found as of 2026-09-23", "research/micro-encoder-investigation.md"),
    ("redirects", "research/jev-system-one.md"),
    ("Table III", "research/novelty-matrix.md"),
    ("Mix-or-Split", "research/gap-assessment.md"),
    ("identical, word for word", "research/gap-assessment.md"),
    ("Lyra, LSCI, DABO and LLMSwitchBench were read at abstract depth only", "research/gap-assessment.md"),
    ("1.4–3.7", "research/claim-audit.md"),
    ("0.15–0.54", "research/claim-audit.md"),
    ("**maintaining** end-to-end inference latency", "research/claim-audit.md"),
    ("They support \"split learning\"", "research/claim-audit.md"),
    ("only Llama-3.1-8B-Instruct appears in the bundle", "research/claim-audit.md"),
    ("same function", "research/claim-audit.md"),
    ("**never cited**", "research/claim-audit.md"),
    ("No router code found", "experiments/reproducibility-plan.md"),
    ("Qwen3-72B-Instruct", "experiments/reproducibility-plan.md"),
    ("5 percentage points", "architecture/recommended-experiment.md"),
    ("ECE ≤ 0.10", "architecture/recommended-experiment.md"),
    ("≤ 0.15", "architecture/recommended-experiment.md"),
    ("2 points CCR@−1", "architecture/recommended-experiment.md"),
    ("ICML 2026", "references/README.md"),
    ("| tfidf-lr | 0.299", "experiments/prototype/results/stage0_summary.md"),
    ("| dataset-prior | 0.410", "experiments/prototype/results/stage0_summary.md"),
    ("| oracle | 0.113", "experiments/prototype/results/stage0_summary.md"),
]
fail = 0
for s, f in ANCHORS:
    if s not in (R / f).read_text():
        print("MISSING in", f, ":", s); fail = 1
for s in ["0.299", "0.410", "0.113", "2/5", "3/8", "2512.14681", "2602.16760", "1.4–3.7×",
          "0.15–0.54", "No neural, generative or Jacobi router has been run"]:
    if s not in tp:
        print("talking points lack", s); fail = 1
# required sections of deliverable 17
for h in ["60-second explanation", "60-second literature update", "Questions I should ask",
          "Terms I should understand", "Likely professor questions", "NOT claim to know"]:
    if h not in tp:
        print("missing section:", h); fail = 1
# Stage-0 recount (same rule as check_brief.py)
summ = (R / "experiments/prototype/results/stage0_summary.md").read_text()
secs = re.split(r"^## ", summ, flags=re.M)
def rows(sec, base):
    return [l for l in sec.splitlines() if f"tfidf-lr minus {base}" in l]
pq_in = [s for s in secs if s.startswith("P-Q — in-domain")][0]
sig_dp = sum(1 for l in rows(pq_in, "dataset-prior") if "excludes 0" in l and re.search(r": \+", l))
lodo = [s for s in secs if "LODO" in s.split("\n")[0]]
better = sum(1 for s in lodo for l in rows(s, "random") if "excludes 0" in l and re.search(r"\): \+", l))
worse = sum(1 for s in lodo for l in rows(s, "random") if "excludes 0" in l and re.search(r"\): -", l))
print(f"recount: P-Q seeds sig>dataset-prior {sig_dp}/5; LODO vs random better {better}, worse {worse} of {len(lodo)}")
if (sig_dp, better, worse, len(lodo)) != (2, 0, 3, 8):
    print("Stage-0 recount disagrees"); fail = 1
# venue status: labels presented as confirmed must be non-@misc; PRISM/Jacobi Forcing must be @misc
bib = (R / "references/library.bib").read_text()
for key, confirmed in [("ong2025routellm", 1), ("song2025irt", 1), ("ding2025best", 1), ("wang2026icl", 1),
                       ("luo2026routelmt", 1), ("li2026llmrouterbench", 1), ("zhan2025prism", 0)]:
    m = re.search(r"^@(\w+)\{" + key + ",", bib, flags=re.M)
    if not m or (m.group(1) != "misc") != bool(confirmed):
        print("venue status mismatch:", key, m and m.group(1)); fail = 1
m = re.search(r"^@(\w+)\{hu2025fast,[^@]*2512\.14681", bib, flags=re.M)
if not m or m.group(1) != "misc":
    print("Jacobi Forcing should be a preprint (@misc) in library.bib"); fail = 1
if "PRISM, whose arXiv comment says AAAI'26" not in tp:
    print("PRISM venue must be attributed to the arXiv comment"); fail = 1
# no past-tense results for unrun routers
for bad in ["outperforms", "we show that", "experiments demonstrate that our", "achieves state", "our router beats"]:
    if bad in tp.lower():
        print("banned phrase:", bad); fail = 1
orig = hashlib.sha256((R / "source/main-original.tex").read_bytes()).hexdigest()
if not (orig.startswith("06f5f9d7") and orig.endswith("07cf6")):
    print("main-original.tex changed!"); fail = 1
print("words:", len(tp.split()))
print("FAIL" if fail else "PASS"); sys.exit(fail)
