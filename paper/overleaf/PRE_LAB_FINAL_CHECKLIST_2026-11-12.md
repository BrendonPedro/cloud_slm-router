# Pre-lab final checklist (2026-11-12)

Manuscript: `paper/overleaf/main.tex` (branch `paper-reframe-2026-11-10`, uncommitted, not uploaded).
Experiment repo: `~/research/LLMRouterBench`, branch `deployment-e1opt`.

## 1. Already complete

- [x] E1-OPT is pre-registered: tag `e1opt-prereg-v1` → commit `d9ba549f006bd18f960b385953acbce8259b9dff`. Never move the tag. The working tree of `diagnostics/deployment_e1opt/` equals the tag.
- [x] The manuscript separates three states: E0 = completed pre-registered screen (G-UB2 STOP); E1-OPT = pre-registered, not run; Asus server + DGX Spark = intended target, result pending. No sentence says E1-OPT ran.
- [x] Reanalysis numbers match `deployment_e1opt/reanalysis/out/`: Δ ≥ 3 at 1.21× (E0 float comparison), 1.19× (exact arithmetic), strict full pass at 1.45×, pass bandwidth 1,357 GB/s. The DGX Spark statement is scoped to the archived RTX 3090 edge profiles.
- [x] Repeated-target bootstrap is reported descriptively: AUC gain +0.068, 95% interval [−0.016, +0.155], no significance claim.
- [x] Benchmark citations: 11 entries, each from a saved primary record (`references/raw/benchmarks_2026-11-12/`).
- [x] Abstract: 354 → 281 words.
- [x] Local build: Tectonic 0.15.0, exit 0, 12 pages, no undefined citations or references, no overfull boxes.
- [x] E0 archives: all four SHA-256 values match their sidecars. Non-bulk members of the two valid archives are copied, with a manifest, to `diagnostics/deployment_e0/results/e0_2026-11-10/` (untracked; the commit is yours to make).

## 2. Waits on the lab hardware

- [ ] Stage 0: inventory on both machines, role assignment, lab answers (link, `tc netem`, roles).
- [ ] Stage 1a: freeze record `frozen/runtime_freeze.json`. Commit `frozen/` only: the checker rejects any committed change elsewhere in the E1 directory, `env/` included.
- [ ] Stage 1b: equivalence (no timing).
- [ ] Stage 2: server-segment profiles.
- [ ] Stage 3: edge fits, competitor fits, edge profiles, G-UB-E1.
- [ ] Stage 4, only if G-UB-E1 says CONTINUE: G-link, joint cells, G-R.
- [ ] Stage archives with SHA-256.

## 3. Evidence to insert after E1-OPT

Take every number from the gate files, not from logs.

- [ ] Outcome class (PREREG §11): Retain / Remove / INCOMPLETE / Stage-1b STOP. INVALID gives no claim.
- [ ] Roles and hardware from `env/roles.json`: which machine is edge and which is server, GPU model and memory, link.
- [ ] `freeze_sha256` and the freeze commit.
- [ ] Stage 1b decision (equivalence pass or fail).
- [ ] Stage 2: measured server decode step at 12 GB and 16 GB, as a fraction of the E0 step (66.9 / 61.3 ms) and as a multiple of the device roofline.
- [ ] Stage 3: U-max per class, competitors that passed the fit, and from `gates/gate_e1_ub.json` + `.e1decision.json`: decision, best bounded Δ with 95% CI, cells passing.
- [ ] Stage 4, if run: `linkcheck.json` (RTT p50, goodput) and from `gates/r/R_cells.json` + `.e1decision.json`: per-cell Δ with CI, retain or remove.
- [ ] Archive names and SHA-256.

Places in `main.tex` that change: abstract (last two sentences), Introduction (last paragraph), contribution 3, Table I (new row B6), Fig. 3 (last node), a new subsection after V-F, VI-D, Limitations, Open questions, Conclusion, header changelog.

## 4. Overleaf checks after the result is inserted

- [ ] pdfLaTeX compiles with no errors (the local build used the XeTeX engine).
- [ ] Figs. 1 to 5 render; check Fig. 3 box heights and Fig. 5 (`x dir=reverse`, rotated label).
- [ ] Table I fits the page with the new row.
- [ ] No `?` citations or references; bibliography numbering is continuous.
- [ ] `\IEEEpubidadjcol` still sits at the paragraph that starts column 2 of page 1.
- [ ] Search for "not yet run", "has not been run", "pending", "no result from that system": every hit is updated or removed.
- [ ] Abstract is still 250 to 280 words.
- [ ] Every E1-OPT number in the abstract, Table I and the Conclusion equals the gate file value.
- [ ] Template header (`\thanks`, `\markboth`, `\IEEEpubid`) replaced once the venue is chosen.
