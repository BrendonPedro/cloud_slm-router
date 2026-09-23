#!/usr/bin/env python3
"""Structural checks for references/library.bib (stdlib only; no BibTeX on host).

1. every entry's braces balance and keys are unique
2. required fields per type are present
3. every `% source:` file exists on disk
4. every arXiv ID in references/raw/arxiv_ids.txt and every DOI in
   references/raw/dois.txt is represented (as eprint or doi)
5. the 20 bibitems of source/main-original.tex each map to a library key
   (references/manuscript-keys.tsv)
Exit status 1 on any failure.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
bib = open(os.path.join(HERE, "library.bib"), encoding="utf-8").read()
fail = []
chunks = re.split(r"\n(?=% source:)", bib)
entries = {}
for c in chunks:
    m = re.search(r"@(\w+)\{([^,]+),", c)
    if not m:
        continue
    etype, key = m.group(1), m.group(2)
    body = c[m.start():]
    if body.count("{") != body.count("}"):
        fail.append(f"unbalanced braces: {key}")
    if key in entries:
        fail.append(f"duplicate key: {key}")
    entries[key] = (etype, body)
    need = {"article": ["author", "title", "journal", "year"],
            "inproceedings": ["author", "title", "booktitle", "year"],
            "misc": ["author", "title"]}[etype]
    for f in need:
        if not re.search(rf"^\s*{f}\s*=", body, re.M):
            fail.append(f"{key}: missing {f}")
    for src in re.search(r"% source: (.*?) \|", c).group(1).split(" + "):
        if not os.path.exists(os.path.join(ROOT, src)):
            fail.append(f"{key}: source file missing {src}")
low = bib.lower()
for aid in open(os.path.join(HERE, "raw", "arxiv_ids.txt")).read().split():
    if f"= {{{aid}}}" not in bib:
        fail.append(f"arXiv {aid} not in bib")
for doi in open(os.path.join(HERE, "raw", "dois.txt")).read().split():
    if doi.lower() not in low:
        fail.append(f"DOI {doi} not in bib")
mk = os.path.join(HERE, "manuscript-keys.tsv")
rows = [l.rstrip("\n").split("\t") for l in open(mk, encoding="utf-8")][1:]
if len(rows) != 20:
    fail.append(f"manuscript-keys.tsv has {len(rows)} rows, expected 20")
for r in rows:
    if r[1] not in entries:
        fail.append(f"manuscript key {r[0]} -> {r[1]} not in bib")
print(f"{len(entries)} entries checked")
print("\n".join(fail) if fail else "ALL CHECKS PASSED")
sys.exit(1 if fail else 0)
