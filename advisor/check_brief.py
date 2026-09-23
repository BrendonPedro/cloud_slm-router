#!/usr/bin/env python3
"""Stdlib check: every factual anchor in advisor/one-page-brief.md must appear
verbatim in the deliverable it is attributed to, and the brief must fit one page."""
import pathlib, re, sys, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
brief = (R / "advisor/one-page-brief.md").read_text()
# (string quoted in brief, evidence file that must contain it)
ANCHORS = [
    ("L193", "research/problem-as-written.md"),
    ("Jacobi", "research/problem-as-written.md"),
    ("PRISM (AAAI'26", "research/novelty-matrix.md"),
    ("ICL-Router (AAAI'26)", "research/novelty-matrix.md"),
    ("RouteLMT (ACL'26 Industry)", "research/novelty-matrix.md"),
    ("BEST-Route (ICML'25)", "research/novelty-matrix.md"),
    ("IRT-Router (ACL'25)", "research/novelty-matrix.md"),
    ("launched 2026-09-15", "research/closest-prior-art.md"),
    ("Findings of ACL 2026", "research/closest-prior-art.md"),
    ("IEEE/CIC ICCC 2025 workshop", "research/closest-prior-art.md"),
    ("2602.16760", "research/closest-prior-art.md"),
    ("Mix-or-Split", "research/gap-assessment.md"),
    ("No established method with this exact name was found as of 2026-09-23", "research/micro-encoder-investigation.md"),
    ("2.57×", "research/jacobi-forcing.md"),
    ("3.97×", "research/jacobi-forcing.md"),
    ("redirects", "research/jev-system-one.md"),
    ("| tfidf-lr | 0.299", "experiments/prototype/results/stage0_summary.md"),
    ("| dataset-prior | 0.410", "experiments/prototype/results/stage0_summary.md"),
    ("| oracle | 0.113", "experiments/prototype/results/stage0_summary.md"),
    ("Qwen3-72B-Instruct", "experiments/reproducibility-plan.md"),
    ("identical, word for word", "research/gap-assessment.md"),
    ("5 percentage points", "architecture/recommended-experiment.md"),
    ("ECE ≤ 0.10", "architecture/recommended-experiment.md"),
]
fail = 0
for s, f in ANCHORS:
    if s not in (R / f).read_text():
        print("MISSING in", f, ":", s); fail = 1
# brief-side presence of the numbers it asserts
for s in ["0.299", "0.410", "0.113", "2/5", "3/8", "2026-09-15", "2512.14681"]:
    if s not in brief:
        print("brief lacks", s); fail = 1
# recount Stage-0 bootstrap claims (2/5 seeds vs dataset-prior, P-Q; 0 better / 3 worse of 8 LODO vs random)
summ = (R / "experiments/prototype/results/stage0_summary.md").read_text()
secs = re.split(r"^## ", summ, flags=re.M)
def lines(sec, base):
    return [l for l in sec.splitlines() if f"tfidf-lr minus {base}" in l]
pq_in = [s for s in secs if s.startswith("P-Q — in-domain")][0]
sig_dp = sum(1 for l in lines(pq_in, "dataset-prior") if "excludes 0" in l and "] (" in l and re.search(r": \+", l))
lodo = [s for s in secs if "LODO" in s.split("\n")[0]]
better = sum(1 for s in lodo for l in lines(s, "random") if "excludes 0" in l and re.search(r"\): \+", l))
worse = sum(1 for s in lodo for l in lines(s, "random") if "excludes 0" in l and re.search(r"\): -", l))
print(f"P-Q in-domain seeds tfidf>dataset-prior significant: {sig_dp}/5; LODO vs random: better {better}, worse {worse} of {len(lodo)}")
if (sig_dp, better, worse, len(lodo)) != (2, 0, 3, 8):
    print("Stage-0 recount disagrees with brief"); fail = 1
# no past-tense result claims for unrun routers
for bad in ["outperforms", "we show that", "experiments demonstrate that our", "achieves state"]:
    if bad in brief.lower():
        print("banned phrase:", bad); fail = 1
# venue labels in the brief follow library.bib entry types (confirmed = not @misc)
bib = (R / "references/library.bib").read_text()
for key, confirmed in [("ong2025routellm", 1), ("song2025irt", 1), ("ding2025best", 1), ("wang2026icl", 1),
                       ("luo2026routelmt", 1), ("li2026llmrouterbench", 1), ("ding2024hybrid", 0), ("zhan2025prism", 0)]:
    m = re.search(r"^@(\w+)\{" + key + ",", bib, flags=re.M)
    if not m or (m.group(1) != "misc") != bool(confirmed):
        print("venue status mismatch:", key, m and m.group(1)); fail = 1
words = len(brief.split())
print("words:", words)
if words > 1000:
    print("too long for one page"); fail = 1
orig = hashlib.sha256((R / "source/main-original.tex").read_bytes()).hexdigest()
print("main-original sha256:", orig[:8], "...", orig[-5:])
if not (orig.startswith("06f5f9d7") and orig.endswith("07cf6")):
    print("main-original.tex changed!"); fail = 1
print("FAIL" if fail else "PASS"); sys.exit(fail)
