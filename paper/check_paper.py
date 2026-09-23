"""Consistency checks for paper/main-revised.tex (stdlib only; no TeX needed).

1. source/main-original.tex is unchanged (sha256).
2. Every \\cite key resolves to references/library.bib; every \\input file exists.
3. Generated tables are up to date with stage0_raw.json (re-runs make_tables.py
   into a temp dir and compares bytes).
4. Every Stage-0 number stated in the prose of Section VI is present in the
   generated tables or in experiments/prototype/results/stage0_summary.md.
5. The bootstrap counts stated in the prose are recomputed from stage0_summary.md.
6. Phrases that the claim audit flagged as unsupported do not appear outside
   comments.
Usage: python3 paper/check_paper.py   (exit code 0 = all checks pass)
"""
import hashlib, os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TEX = os.path.join(ROOT, "paper", "main-revised.tex")
BIB = os.path.join(ROOT, "references", "library.bib")
SUMMARY = os.path.join(ROOT, "experiments", "prototype", "results", "stage0_summary.md")
ORIG_SHA_PREFIX, ORIG_SHA_SUFFIX = "06f5f9d7", "07cf6"
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in t.splitlines())


# 1
sha = hashlib.sha256(open(os.path.join(ROOT, "source", "main-original.tex"), "rb").read()).hexdigest()
check(sha.startswith(ORIG_SHA_PREFIX) and sha.endswith(ORIG_SHA_SUFFIX), f"main-original.tex unchanged ({sha[:8]}…{sha[-5:]})")

tex = open(TEX).read()
body = strip_comments(tex)

# 2
bibkeys = set(re.findall(r"^@\w+\{([^,]+),", open(BIB).read(), re.M))
cites = set()
for grp in re.findall(r"\\cite\{([^}]*)\}", body):
    cites |= {k.strip() for k in grp.split(",")}
missing = sorted(cites - bibkeys)
check(not missing, f"{len(cites)} cited keys all in library.bib" + (f"; missing {missing}" if missing else ""))
inputs = re.findall(r"\\input\{([^}]*)\}", body)
for i in inputs:
    check(os.path.exists(os.path.join(ROOT, "paper", i)), f"\\input file exists: {i}")
check("../references/library" in body, "bibliography points at references/library.bib")

# 3
tmp = tempfile.mkdtemp()
try:
    src = open(os.path.join(ROOT, "paper", "make_tables.py")).read()
    src = src.replace('OUT = os.path.join(HERE, "tables")', f'OUT = {tmp!r}')
    script = os.path.join(tmp, "mk.py")
    open(script, "w").write(src.replace('HERE = os.path.dirname(os.path.abspath(__file__))',
                                        f'HERE = {os.path.join(ROOT, "paper")!r}'))
    subprocess.run([sys.executable, script], check=True, capture_output=True)
    for f in ("stage0_indomain.tex", "stage0_lodo.tex"):
        same = open(os.path.join(tmp, f), "rb").read() == open(os.path.join(ROOT, "paper", "tables", f), "rb").read()
        check(same, f"tables/{f} matches a fresh regeneration from stage0_raw.json")
finally:
    shutil.rmtree(tmp)

# 4
sec = body.split(r"\label{sec:stage0}")[1].split(r"\section{")[0]
prose = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", sec, flags=re.S)
evidence = open(SUMMARY).read() + "".join(open(os.path.join(ROOT, "paper", "tables", f)).read()
                                          for f in ("stage0_indomain.tex", "stage0_lodo.tex"))
nums = re.findall(r"(?<![\w.-])(\d+\.\d+)(\\%)?", prose)
for n, pct in nums:
    val = f"{float(n) / 100:.3f}" if pct else n
    check(val in evidence, f"Stage-0 prose number {n}{'%' if pct else ''} -> {val} found in raw-derived tables/summary")

# 5
summ = open(SUMMARY).read()
blocks = re.split(r"^## ", summ, flags=re.M)[1:]
lodo_better = lodo_worse = 0
indom = {}
for b in blocks:
    head = b.splitlines()[0]
    for line in b.splitlines():
        m = re.match(r"- seed (\d+): tfidf-lr minus (random|dataset-prior) \(deferral AUC\): ([+-]\d\.\d+) .*\((excludes|includes) 0", line)
        if not m:
            continue
        seed, base, diff, ex = m.groups()
        sig = ex == "excludes"
        if "LODO" in head and base == "random":
            lodo_better += sig and float(diff) > 0
            lodo_worse += sig and float(diff) < 0
        if "in-domain" in head:
            pair = head.split()[0]
            indom[(pair, base)] = indom.get((pair, base), 0) + (sig and float(diff) > 0)
check(lodo_better == 0 and lodo_worse == 3, f"LODO vs random: better={lodo_better} (prose 0), worse={lodo_worse} (prose 3)")
check(indom.get(("P-L", "random")) == 5 and indom.get(("P-Q", "random")) == 4,
      f"in-domain > random seeds: P-L={indom.get(('P-L','random'))} (prose 5), P-Q={indom.get(('P-Q','random'))} (prose 4)")
check(indom.get(("P-L", "dataset-prior")) == 2 and indom.get(("P-Q", "dataset-prior")) == 2,
      f"in-domain > dataset-prior seeds: P-L={indom.get(('P-L','dataset-prior'))}, P-Q={indom.get(('P-Q','dataset-prior'))} (prose 2 each)")

# 6
banned = [r"extensive experiments", r"\bnovel\b", r"state-of-the-art", r"significantly reduces",
          r"we demonstrate", r"results (show|indicate|demonstrate)"]
low = body.lower()
for pat in banned:
    hits = [m.group(0) for m in re.finditer(pat, low)]
    check(not hits, f"no unsupported phrase /{pat}/" + (f": {hits}" if hits else ""))
# Sentence-level: these phrases are allowed only when attributed to prior work or negated.
sentences = re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", low))
for pat in [r"without (requiring )?(costly )?retraining", r"outperform", r"lightweight and adaptive"]:
    bad = [x for x in sentences if re.search(pat, x)
           and not any(w in x for w in ("\\cite", "not open", "{not} open", "reported", "shared", "did not", "do not", "whether"))]
    check(not bad, f"/{pat}/ only in attributed or negated sentences" + (f": {bad}" if bad else ""))

print(f"\n{'ALL CHECKS PASSED' if not fails else str(len(fails)) + ' CHECK(S) FAILED'}")
sys.exit(1 if fails else 0)
