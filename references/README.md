# Deliverable 14: `references/library.bib`

**Built:** 2026-09-23, generated from saved primary-source records with no
hand-typed metadata. **Entries:** 101.
**Rebuild and check:** `python3 references/build_bib.py && python3 references/check_bib.py`
(stdlib only). A rebuild is byte-identical, which was checked with `cmp` on 2026-09-23.

## Files

| File | Purpose |
|---|---|
| `library.bib` | The bibliography. **Generated; do not edit by hand.** Each entry has a `% source:` comment naming the raw record(s) it was built from, and a `status` |
| `build_bib.py` | The generator. Precedence when a work appears in several records: ACL/ICLR proceedings `.bib` > Crossref > PMLR volume index > arXiv abs page |
| `check_bib.py` | Structural checks (there is no BibTeX/LaTeX on the host, so a real `bibtex` run was **not** possible; see below) |
| `misc_sources.json` | The 9 non-paper sources (vendor blog/docs, patent, repositories, the manuscript's company blog). Each one points to its fetched raw file |
| `key-map.tsv` | Key → arXiv ID / DOI / status / title, for every entry |
| `manuscript-keys.tsv` | The 20 `\bibitem` keys of `source/main-original.tex` → library keys, with the metadata change made to each (cross-reference: `research/claim-audit.md` §1) |
| `raw/` | Everything fetched this iteration, with a timestamped `fetch-log.txt`: 27 Crossref JSONs, 4 ACL Anthology `.bib`s, the ICLR 2025 index and RouteLLM `.bib`, PMLR indexes for v70/139/202/235/267 plus the PMLR front page, and 9 arXiv abs pages that had not been saved before. Other abs pages are reused from `research/raw/*/` |

## Scope

The library includes **every arXiv ID (68) and DOI (27) cited anywhere in
deliverables 1–13** (`research/*.md`, `architecture/*.md`,
`experiments/*.md`). `check_bib.py` enforces this against `raw/arxiv_ids.txt`
and `raw/dois.txt`, which were extracted from those files by grep. It also
includes all 20 works in the original manuscript's bibliography.

## Status breakdown

| Status | n | What confirms it |
|---|---|---|
| peer-reviewed (proceedings `.bib` export) | 5 | ACL Anthology (IRT-Router, RouteLMT, LLMRouterBench, BiCSRouter); ICLR 2025 proceedings (RouteLLM) |
| peer-reviewed (Crossref record) | 26 | Crossref `works` API, type journal-article / proceedings-article |
| peer-reviewed (PMLR index) | 10 | Title match in a PMLR volume index: Medusa, EAGLE, CLLMs, Lookahead, MTP (Gloeckle), SnD (v235); BEST-Route (v267); Song et al. 2021 (v139); Leviathan et al. (v202); Guo et al. (v70) |
| preprint (arXiv abs page) | 51 | `citation_*` meta tags on the arXiv abs page |
| vendor blog / documentation | 3 | TypeSafe Jev blog and docs (vendor claims) |
| patent | 1 | Google Patents record, US12505362B2 |
| code repository | 4 | GitHub API records |
| company blog | 1 | The manuscript's Edenlab citation. Kept only for traceability; flagged as unsuitable |

## Rules the generator follows

1. **arXiv comments are never promoted to a venue.** They are quoted in `note`
   with the prefix "arXiv comments (author-supplied, not verified as venue)".
   14 preprints have comments that claim a venue we have not confirmed at a
   proceedings source: AutoMix (NeurIPS 2024), RouterDC (NeurIPS 2024), Hybrid
   LLM (ICLR 2024), Santilli et al. (ACL 2023; the arXiv page supplies DOI
   10.18653/v1/2023.acl-long.689), PRISM (AAAI 2026), TRINITY (ICLR 2026),
   Moslem & Kelleher survey (TMLR 2026), DiP-SD (VTC2026-Spring), Splitwise
   (UCC '25), Yuan et al. (MobiHoc 2025 → ToN), RouteJudge (ICML 2026
   workshop), Bao et al. (ICCC workshop), Uzor et al. (ICSC 2025), MicroNet
   ("Accepted by PMLR"). Two other comment-claimed venues (Guo et al. 2017,
   ICML; Leviathan et al. 2023, ICML) were confirmed via PMLR, so those
   entries were upgraded.
2. **Title matching for merges is exact after normalisation.** There is one
   hand-checked alias: RouteLLM arXiv 2406.18665 ("…*with* Preference Data")
   = ICLR 2025 ("…*from* Preference Data"). The author lists are identical.
3. Crossref `1--1` pages (early access) are dropped and noted, e.g. LLMSwitchBench.
4. Author names are copied as the registry gives them. **BiCSRouter's first
   author appears as "Keyu, Mao" in the ACL Anthology record.** That may be a
   given-name/family-name inversion at the source, but it is left as recorded.

## Findings from building the library

- **Split-and-Denoise (manuscript `Mai2023`) is confirmed as ICML 2024**,
  PMLR 235:34281–34302 (`raw/pmlr_v235_index.html`). This resolves the open
  item in claim-audit §1.
- **RouteLLM's ICLR 2025 pages 34433–34448 are confirmed** by the official ICLR
  proceedings BibTeX (`raw/iclr2025_routellm.bib`).
- **BEST-Route is ICML 2025** (PMLR 267:13870–13884). Deliverables 3 and 11
  cite it only by arXiv ID.
- **Jacobi Forcing (arXiv 2512.14681) remains a preprint in this library.**
  The official repository describes it as "[ICML 2026]" (GitHub API), but its
  arXiv page has no comments field, and the PMLR front page fetched on
  2026-09-23 lists no ICML 2026 volume. Cite it as a preprint, and add the
  ICML 2026 venue once the proceedings are published.
- **CITER's "COLM'25"** comes only from the repository description. Its arXiv
  page has no comments field, so it is kept as a preprint.
- OpenReview's API returned a 403 challenge for automated access, so it could
  not be used as a verifier. The ICLR proceedings site worked.

## What was not checked

- **No BibTeX compile.** `bibtex`, `biber` and `pdflatex` are not installed.
  `check_bib.py` checks braces, unique keys, required fields, that source files
  exist, and coverage. It does **not** check how styles render titles.
  `protect_caps` braces acronyms and camel-case words, but its output has not
  been seen through IEEEtran.
- Author lists taken from arXiv pages are the arXiv listing, not necessarily
  the camera-ready version.
- Venues of the preprints listed under rule 1 are unconfirmed.
- The 3 manuscript citations to split *learning* (Pham2025, Hukkeri2025,
  Alhindi2025) are metadata-correct, but, as claim-audit §1 notes, they do
  **not** support split-*inference* claims. Correct metadata does not make a
  citation appropriate.
