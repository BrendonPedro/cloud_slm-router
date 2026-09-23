#!/usr/bin/env python3
"""Build references/library.bib mechanically from saved primary-source records.

No metadata is typed by hand. Every field comes from one of:
  * ACL Anthology .bib exports      references/raw/acl_*.bib
  * ICLR proceedings .bib export    references/raw/iclr2025_*.bib
  * Crossref works API JSON         references/raw/crossref_*.json
  * PMLR volume indexes (ICML 2017/2021/2023/2024/2025)  references/raw/pmlr_v*_index.html
  * arXiv abs pages (citation_* meta tags, Comments/Journal-ref cells)
                                    references/raw/abs_*.html, research/raw/*/abs_*.html
  * non-paper sources               references/misc_sources.json (URL + fetched raw file)

Precedence when the same work appears in several records (matched by
normalised title): ACL/ICLR bib > Crossref > PMLR index > arXiv. The arXiv
ID is kept as `eprint` on the peer-reviewed entry when both exist.

arXiv "Comments" are copied into `note` verbatim and are NEVER promoted to a
venue: a venue is only written when a registry/proceedings record confirms it.

Usage: python3 references/build_bib.py   (stdlib only; writes library.bib and
key-map.tsv next to this script)
"""
import glob
import html
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(HERE, "raw")

# arXiv IDs whose arXiv title differs from the peer-reviewed title. Each pair
# was checked by hand against the saved records named here.
ALIASES = {
    # arXiv v4 "...with Preference Data" vs ICLR 2025 proceedings "...from Preference Data";
    # same 8 authors in raw/iclr2025_routellm.bib and research/raw/prior-art/abs_2406.18665.html
    "2406.18665": "RouteLLM: Learning to Route LLMs from Preference Data",
}

STOP = {"a", "an", "the", "on", "of", "for", "to", "in", "and", "with", "via",
        "is", "are", "do", "does", "can", "towards", "toward", "when", "what",
        "how", "not", "all", "you", "your", "need", "we", "from", "by", "at"}


def norm_title(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[{}\\]", "", t)
    return re.sub(r"[^a-z0-9]", "", t.lower())


def ascii_word(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", s)


def make_key(last, year, title):
    words = [w for w in re.findall(r"[A-Za-z0-9]+", re.sub(r"[{}\\]", "", title))
             if w.lower() not in STOP and not w.isdigit()]
    first = ascii_word(words[0]) if words else "untitled"
    return f"{ascii_word(last).lower()}{year}{first.lower()}"


def tex_escape(s):
    s = s.replace("\\", "\\textbackslash{}")
    for ch in "&%$#_":
        s = s.replace(ch, "\\" + ch)
    return s


def protect_caps(title):
    """Brace words with internal capitals/digits so BibTeX styles keep them."""
    def rep(m):
        w = m.group(0)
        if re.search(r"[A-Z].*[A-Z]|[0-9]", w) or (len(w) > 1 and w[1:] != w[1:].lower()):
            return "{" + w + "}"
        return w
    return re.sub(r"[A-Za-z0-9][A-Za-z0-9\-]*", rep, title)


# ---------------------------------------------------------------- parsers

def parse_bibtex_file(path):
    """Minimal parser for the one-entry .bib exports from ACL/ICLR."""
    s = open(path, encoding="utf-8").read()
    m = re.match(r"\s*@(\w+)\{([^,]+),", s)
    etype = m.group(1).lower()
    fields = {}
    for fm in re.finditer(r"^\s*(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"(?:[^\"\\]|\\.)*\"|\d+)\s*,?\s*$",
                          s, re.M):
        v = fm.group(2)
        if v[0] in "{\"":
            v = v[1:-1]
        fields[fm.group(1).lower()] = re.sub(r"\s+", " ", v).strip()
    return etype, fields


def authors_from_bib(a):
    out = []
    for name in re.split(r"\s+and\s+", a):
        name = name.strip()
        if "," in name:
            last, first = [x.strip() for x in name.split(",", 1)]
        else:
            parts = name.split()
            last, first = parts[-1], " ".join(parts[:-1])
        out.append((last, first))
    return out


def load_acl_iclr():
    recs = []
    for path in sorted(glob.glob(os.path.join(RAW, "acl_*.bib")) +
                       glob.glob(os.path.join(RAW, "iclr2025_*.bib"))):
        etype, f = parse_bibtex_file(path)
        authors = authors_from_bib(f["author"])
        rec = {
            "type": etype,
            "title": re.sub(r"[{}]", "", f["title"]),
            "authors": authors,
            "year": f.get("year"),
            "booktitle": re.sub(r"[{}]", "", f.get("booktitle", "")),
            "pages": f.get("pages", "").replace("--", "--"),
            "publisher": re.sub(r"[{}]", "", f.get("publisher", "")),
            "doi": f.get("doi"),
            "url": f.get("url"),
            "volume": f.get("volume") if "iclr" in path else None,
            "source": os.path.relpath(path, ROOT),
            "status": "peer-reviewed (proceedings .bib export)",
        }
        recs.append(rec)
    return recs


def load_crossref():
    recs = []
    for path in sorted(glob.glob(os.path.join(RAW, "crossref_*.json"))):
        m = json.load(open(path, encoding="utf-8"))["message"]
        authors = [(a.get("family", a.get("name", "")), a.get("given", ""))
                   for a in m.get("author", [])]
        dp = m.get("issued", {}).get("date-parts", [[None]])[0]
        ctype = m["type"]
        container = (m.get("container-title") or [""])[0]
        rec = {
            "type": "article" if ctype == "journal-article" else "inproceedings",
            "title": html.unescape(re.sub(r"<[^>]+>", "", m["title"][0]
                                          + (": " + m["subtitle"][0] if m.get("subtitle") else ""))),
            "authors": authors,
            "year": str(dp[0]) if dp and dp[0] else None,
            "journal" if ctype == "journal-article" else "booktitle": container,
            "volume": m.get("volume"),
            "number": m.get("issue"),
            "pages": (m.get("page") or "").replace("-", "--"),
            "publisher": m.get("publisher"),
            "doi": m.get("DOI"),
            "source": os.path.relpath(path, ROOT),
            "status": "peer-reviewed (Crossref record)",
        }
        if rec["pages"] in ("1--1",):
            rec["note_extra"] = "Crossref lists pages 1--1 (early access); final pagination not yet assigned"
            rec["pages"] = ""
        recs.append(rec)
    return recs


def load_pmlr_index():
    """Map normalised title -> PMLR record, from every saved PMLR volume index."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RAW, "pmlr_v*_index.html"))):
        s = open(path, encoding="utf-8").read()
        for m in re.finditer(r'<p class="title">(.*?)</p>\s*<p class="details">\s*<span class="authors">(.*?)</span>;'
                             r'\s*<span class="info"><i>(.*?)</i>, PMLR (\d+):(\d+)-(\d+)</span>.*?'
                             r'<a href="(https://proceedings.mlr.press/v\d+/[^"]+\.html)">abs</a>', s, re.S):
            title = html.unescape(m.group(1)).strip()
            out[norm_title(title)] = {"title": title, "booktitle": html.unescape(m.group(3)).strip(),
                                      "volume": m.group(4), "pages": f"{m.group(5)}--{m.group(6)}",
                                      "url": m.group(7), "raw": os.path.relpath(path, ROOT)}
    return out


def load_arxiv():
    recs = {}
    paths = glob.glob(os.path.join(RAW, "abs_*.html")) + \
        glob.glob(os.path.join(ROOT, "research", "raw", "*", "abs_*.html")) + \
        glob.glob(os.path.join(ROOT, "research", "raw", "*", "export.arxiv.org_abs_*.html"))
    for path in sorted(paths):
        s = open(path, encoding="utf-8", errors="replace").read()
        def meta(name):
            return [html.unescape(x) for x in re.findall(rf'<meta name="{name}" content="([^"]*)"', s)]
        aid = meta("citation_arxiv_id")
        if not aid:
            continue
        aid = aid[0]
        if aid in recs:
            continue
        authors = []
        for a in meta("citation_author"):
            last, _, first = a.partition(",")
            authors.append((last.strip(), first.strip()))
        date = (meta("citation_date") or [""])[0]
        def cell(cls):
            m = re.search(rf'class="tablecell {cls}[^"]*">(.*?)</td>', s, re.S)
            return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip() if m else None
        recs[aid] = {
            "type": "misc",
            "title": re.sub(r"\s+", " ", meta("citation_title")[0]).replace("$\\times$", "\u00d7").strip(),
            "authors": authors,
            "year": date[:4],
            "eprint": aid,
            "comments": cell("comments"),
            "jref": cell("jref"),
            "doi_meta": (meta("citation_doi") or [None])[0],
            "source": os.path.relpath(path, ROOT),
            "status": "preprint (arXiv abs page)",
        }
    return recs


# ---------------------------------------------------------------- output

def fmt_authors(authors):
    return " and ".join(f"{tex_escape(l)}, {tex_escape(f)}" if f else "{" + tex_escape(l) + "}"
                        for l, f in authors)


def entry(key, rec):
    fields = [("author", fmt_authors(rec["authors"])),
              ("title", "{" + protect_caps(tex_escape(rec["title"])) + "}")]
    for k in ("booktitle", "journal", "series", "volume", "number", "pages", "publisher", "year", "doi", "url"):
        v = rec.get(k)
        if v:
            fields.append((k, tex_escape(v) if k not in ("url", "doi") else v))
    if rec.get("eprint"):
        fields += [("eprint", rec["eprint"]), ("archiveprefix", "arXiv")]
        if rec["type"] == "misc":
            fields.append(("howpublished", f"arXiv preprint arXiv:{rec['eprint']}"))
    notes = []
    if rec.get("note_extra"):
        notes.append(rec["note_extra"])
    if rec.get("comments"):
        notes.append("arXiv comments (author-supplied, not verified as venue): " + rec["comments"])
    if rec.get("jref"):
        notes.append("arXiv journal-ref: " + rec["jref"])
    if notes:
        fields.append(("note", tex_escape("; ".join(notes))))
    body = ",\n".join(f"  {k:<13}= {{{v}}}" if not v.startswith("{") or k != "title" else f"  {k:<13}= {v}"
                      for k, v in fields)
    return f"% source: {rec['source']} | status: {rec['status']}\n@{rec['type']}{{{key},\n{body}\n}}\n"


def main():
    peer = load_acl_iclr() + load_crossref()
    pmlr = load_pmlr_index()
    arx = load_arxiv()

    by_title = {}
    for rec in peer:
        t = norm_title(rec["title"])
        if t not in by_title:  # ACL/ICLR loaded first -> wins over Crossref
            by_title[t] = rec

    for aid, rec in sorted(arx.items()):
        t = norm_title(ALIASES.get(aid, rec["title"]))
        if t in by_title:
            by_title[t].setdefault("eprint", aid)
            by_title[t]["source"] += " + " + rec["source"]
            continue
        if t in pmlr:
            p = pmlr[t]
            year = re.search(r"\b(20\d\d)\b", p["booktitle"])
            year = year.group(1) if year else {"70": "2017", "139": "2021", "202": "2023", "235": "2024", "267": "2025"}[p["volume"]]
            by_title[t] = {"type": "inproceedings", "title": rec["title"], "authors": rec["authors"],
                           "booktitle": p["booktitle"], "series": "Proceedings of Machine Learning Research",
                           "volume": p["volume"], "pages": p["pages"], "year": year,
                           "publisher": "PMLR", "url": p["url"], "eprint": aid,
                           "source": p["raw"] + " + " + rec["source"],
                           "status": "peer-reviewed (PMLR index)"}
            continue
        if rec.get("doi_meta"):
            rec["doi"] = rec["doi_meta"]
        by_title[t] = rec

    keys, out, keymap = {}, [], []
    for t, rec in sorted(by_title.items(), key=lambda kv: (kv[1]["authors"][0][0].lower() if kv[1]["authors"] else "", kv[1].get("year") or "")):
        last = rec["authors"][0][0] if rec["authors"] else "anon"
        key = make_key(last, rec.get("year") or "nd", rec["title"])
        base, n = key, 1
        while key in keys:
            n += 1
            key = f"{base}{chr(ord('a') + n - 1)}"
        keys[key] = rec
        out.append(entry(key, rec))
        keymap.append((key, rec.get("eprint", ""), rec.get("doi", "") or "", rec["status"], rec["title"]))

    misc_path = os.path.join(HERE, "misc_sources.json")
    for m in json.load(open(misc_path, encoding="utf-8")):
        fields = [("author", "{" + tex_escape(m["author"]) + "}"),
                  ("title", "{" + protect_caps(tex_escape(m["title"])) + "}"),
                  ("howpublished", "\\url{" + m["url"] + "}")]
        if m.get("year"):
            fields.append(("year", m["year"]))
        fields.append(("note", tex_escape(m["note"])))
        body = ",\n".join(f"  {k:<13}= {v}" if v.startswith("{") else f"  {k:<13}= {{{v}}}" for k, v in fields)
        out.append(f"% source: {m['raw']} | status: {m['status']}\n@misc{{{m['key']},\n{body}\n}}\n")
        keymap.append((m["key"], "", "", m["status"], m["title"]))

    header = ("% references/library.bib -- GENERATED by references/build_bib.py; do not edit by hand.\n"
              "% Every entry is built from a saved primary record (see the `% source:` line above it).\n"
              "% `status` distinguishes peer-reviewed records from arXiv preprints and non-paper sources.\n"
              "% arXiv comments are quoted in `note` and never promoted to a venue.\n\n")
    with open(os.path.join(HERE, "library.bib"), "w", encoding="utf-8") as f:
        f.write(header + "\n".join(out))
    with open(os.path.join(HERE, "key-map.tsv"), "w", encoding="utf-8") as f:
        f.write("key\tarxiv\tdoi\tstatus\ttitle\n")
        for row in keymap:
            f.write("\t".join(row) + "\n")
    print(f"{len(out)} entries written")


if __name__ == "__main__":
    main()
