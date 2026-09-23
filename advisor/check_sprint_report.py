#!/usr/bin/env python3
"""Stdlib check: all 18 deliverables exist, and every factual anchor in
advisor/research-sprint-report.md appears in the file it is attributed to."""
import pathlib, re, sys, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
rep = (R / "advisor/research-sprint-report.md").read_text()
fail = 0
DELIVERABLES = [
    "research/problem-as-written.md", "research/current-landscape.md",
    "research/closest-prior-art.md", "research/novelty-matrix.md",
    "research/jev-system-one.md", "research/jacobi-forcing.md",
    "research/micro-encoder-investigation.md", "research/gap-assessment.md",
    "architecture/options.md", "architecture/recommended-experiment.md",
    "experiments/reproducibility-plan.md", "experiments/prototype/stage0.py",
    "research/claim-audit.md", "references/library.bib",
    "paper/main-revised.tex", "advisor/one-page-brief.md",
    "advisor/talking-points.md", "advisor/research-sprint-report.md",
]
for d in DELIVERABLES:
    p = R / d
    if not p.is_file() or p.stat().st_size == 0:
        print("MISSING deliverable:", d); fail = 1
    if d not in rep and not d.startswith("experiments/prototype") and d != "advisor/research-sprint-report.md":
        print("report does not list", d); fail = 1
ANCHORS = [  # (string in report, evidence file that must contain it)
    ("Python 3.12.3", "experiments/prototype/logs/environment.txt"),
    ("Ryzen 5 8500G", "experiments/prototype/logs/environment.txt"),
    ("3f83fff0", "experiments/prototype/logs/environment.txt"),
    ("byte-identical", "experiments/prototype/logs/determinism.txt"),
    ("2.57×", "research/jacobi-forcing.md"),
    ("3.97×", "research/jacobi-forcing.md"),
    ("still\n  unverified", "research/closest-prior-art.md"),
    ("only Llama-3.1-8B-Instruct appears in the bundle", "research/claim-audit.md"),
    ("## 4. Tally", "research/claim-audit.md"),
    ("n-gram text-reuse check was run against one source only", "research/gap-assessment.md"),
    ("## 5. Self-review (contradiction check)", "research/novelty-matrix.md"),
    ("IEEE Xplore / ACM DL direct search", "research/novelty-matrix.md"),
    ("## 5. Model pool named in the manuscript", "experiments/reproducibility-plan.md"),
    ("U(\\textsc{Split}(d),q)=U(\\textsc{Cloud},q)", "paper/main-revised.tex"),
    ("Mix-or-Split", "research/gap-assessment.md"),
]
for s, f in ANCHORS:
    if s not in (R / f).read_text():
        print("MISSING in", f, ":", s); fail = 1
# counts stated in the report
nbib = len(re.findall(r"^@\w+\{", (R / "references/library.bib").read_text(), re.M))
nraw = sum(1 for d in ["research/raw", "references/raw"] for p in (R / d).rglob("*") if p.is_file())
for claim, actual in [("101 entries", nbib), ("311 files", nraw)]:
    if str(actual) not in claim:
        print(f"count mismatch: report says '{claim}', actual {actual}"); fail = 1
    if claim not in rep:
        print("report lacks", claim); fail = 1
# Stage-0 recount (same logic as check_brief.py)
summ = (R / "experiments/prototype/results/stage0_summary.md").read_text()
secs = re.split(r"^## ", summ, flags=re.M)
lodo = [s for s in secs if "LODO" in s.split("\n")[0]]
L = lambda s, b: [l for l in s.splitlines() if f"tfidf-lr minus {b}" in l]
better = sum(1 for s in lodo for l in L(s, "random") if "excludes 0" in l and re.search(r"\): \+", l))
worse = sum(1 for s in lodo for l in L(s, "random") if "excludes 0" in l and re.search(r"\): -", l))
pq = [s for s in secs if s.startswith("P-Q — in-domain")][0]
sig = sum(1 for l in L(pq, "dataset-prior") if "excludes 0" in l and "] (" in l and re.search(r": \+", l))
print(f"recount: LODO better {better}, worse {worse} of {len(lodo)}; P-Q sig>dataset-prior {sig}/5")
if (better, worse, len(lodo), sig) != (0, 3, 8, 2) or not all(x in rep for x in ["0/8", "3/8", "2/5"]):
    print("Stage-0 recount disagrees with report"); fail = 1
# the report must not claim unrun experiments or human review
low = rep.lower()
for bad in ["we trained", "we measured the speed", "human-reviewed and approved", "outperforms"]:
    if bad in low:
        print("banned phrase:", bad); fail = 1
if "No human review is recorded" not in rep:
    print("report must state absence of recorded human review"); fail = 1
# source unchanged
sha = hashlib.sha256((R / "source/main-original.tex").read_bytes()).hexdigest()
if sha != "06f5f9d7e9548c04ff59e098c1bd3c63a33d686114ccb8e37363d052b1707cf6":
    print("main-original.tex changed!"); fail = 1
print("FAIL" if fail else "PASS")
sys.exit(fail)
