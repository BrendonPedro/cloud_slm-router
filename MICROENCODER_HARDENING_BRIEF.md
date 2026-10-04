# MICROENCODER_HARDENING_BRIEF.md

# Research Sprint:
# Hardening the Distilled Micro-Encoder + Split-LLM Routing Method

## 0. Purpose

This sprint follows the completed `methods-v2/` research sprint.

DO NOT restart open-ended method selection.

The advisor has already selected the MICRO-ENCODER family as the proposed
conference routing backbone.

This sprint has a different role:

> Act as a skeptical systems/ML reviewer and harden the proposed method before
> anything is merged into the main manuscript.

Time and iteration count are NOT primary constraints.
Depth, primary-source verification, mathematical consistency, systems validity,
and citation quality are more important.

The previous sprint produced a useful proposed method, but review identified
several issues that must now be investigated rather than patched by assumption.

Preserve `methods-v2/` unchanged.

Create all new outputs in:

`methods-v3/`

Do NOT modify `source/main-original.tex`.

---

# 1. Fixed research scope

The original research problem remains fixed:

R : Q -> M

max_R E_q [ U(R(q), q) - lambda C(R(q), q) ]

R(q) = argmax_{M_k in M} f_theta(q, M_k)

The approved direction remains:

- lightweight micro-encoder router
- edge deployment
- Edge SLM / Split-LLM / strong-remote collaborative inference
- learned query/model utility
- measured runtime system cost
- knowledge distillation investigated as an optimization
- hidden-state/self-routing approach as a baseline
- continual learning reserved for a journal extension
- Jacobi is not required

Do not change these decisions.

---

# 2. Problems identified during external review

The following issues MUST be independently investigated and resolved.

## ISSUE A — Model utility versus execution-action utility

`methods-v2` defines one independent sigmoid utility head for every action:

A = {
  EDGE_SLM,
  SPLIT(d1),
  ...,
  SPLIT(dm),
  STRONG/CLOUD
}

This may be unnecessarily duplicating semantic utility.

If SPLIT(d1), SPLIT(d2), and full remote execution use the SAME underlying
model and split execution is numerically/losslessly equivalent, then answer
quality may be a MODEL property while split depth is primarily a SYSTEM-COST
property.

Investigate whether the cleaner decomposition is:

U_hat_theta(M | q)

combined with:

C(a | s)

where action `a` maps to an underlying model M(a):

R(q,s) =
argmax_{a in A} [
    U_hat_theta(M(a) | q)
    - lambda C(a | s)
]

Compare this carefully against the v2 formulation:

U_hat_theta(a | q)

Do not assume either is correct.

Required analysis:

1. When should utility attach to MODEL identity?
2. When should utility attach to EXECUTION ACTION?
3. When can multiple split depths safely share one model-utility prediction?
4. What changes if activation quantization/compression makes Split(d) lossy?
5. What changes if early-exit/split execution modifies inference semantics?
6. Does a separate utility head for every split depth waste supervision?
7. Does it create unnecessary retraining when split depths are changed?
8. Which formulation maps most faithfully to the original f_theta(q, M_k)?
9. Which formulation gives the cleanest systems/ML decomposition?
10. Which formulation is easiest to implement and falsify?

Produce an explicit recommendation.

---

# 3. ISSUE B — "Add a head without retraining" claim

`methods-v2` argues that independent sigmoid heads allow cheap model-pool
addition because an action can be added by adding one head.

Stress-test this statement.

Questions:

- Does a newly added head require labelled data?
- Does it require head training?
- Does it require backbone fine-tuning?
- Does calibration need to be redone?
- Could frozen-backbone + new-head training work?
- What generalization is possible to unseen models/actions?
- Would a model-profile or embedding-based architecture be required for true
  zero/few-shot pool expansion?

Rewrite this claim conservatively.

Do not claim "no retraining" unless technically demonstrated.

---

# 4. ISSUE C — System state and retraining

`methods-v2` states that putting live system state `s` into theta would force
retraining whenever network conditions change.

This statement is too strong.

A learned router could theoretically take bandwidth, RTT, load, or resource
state as inputs and generalize across them.

Investigate the REAL justification for keeping:

U_hat_theta(M|q)

separate from:

C(a|s)

Possible arguments to assess:

- direct use of fresh measurements
- interpretability
- reduced training-distribution dependence
- easier systems adaptation
- cleaner debugging
- independent semantic and systems updates
- less dependence on simulated network-state training data
- reuse of one semantic router under multiple runtime environments

Rewrite the justification accurately.

Do not claim that integrated state necessarily requires retraining after every
network change.

---

# 5. ISSUE D — Split-LLM losslessness

Do NOT assume:

y(SPLIT(d), q) = y(full, q)

without conditions.

Research the technical conditions under which layer splitting is numerically or
semantically equivalent to non-split inference.

Consider:

- exact tensor transfer
- dtype changes
- FP16/BF16/FP32
- activation quantization
- compression
- serialization
- stochastic inference
- KV cache handling
- model-parallel/split inference
- early exit
- partition-specific transforms

Produce two method branches:

### Exact/lossless split
Model quality is shared:
U_hat(M|q)

and split depth differs through cost.

### Lossy/approximate split
Quality may depend on split depth:
U_hat(M,d|q)

or:
U_hat(M|q) - Delta_quality(d,q)

Do not choose the lossy formulation unless Henry's implementation requires it.

Create an empirical equivalence test to run immediately when Henry's code is
obtained.

---

# 6. ISSUE E — Knowledge-distillation terminology

Re-examine RouteLLM carefully.

Do NOT casually call GPT-4-generated preference labels
"knowledge distillation in all but name" unless the literature supports that
terminology.

Distinguish:

- pseudo-labelling
- teacher-generated labels
- LLM-as-a-judge supervision
- preference supervision
- knowledge distillation
- soft-logit distillation
- representation distillation

Determine exactly how RouteLLM should be described in the manuscript.

Our proposed KD method must be compared fairly to:

1. hard observed labels
2. teacher-generated labels / preference supervision
3. actual soft teacher outputs
4. optional representation distillation

---

# 7. ISSUE F — What exactly is the KD teacher learning?

The v2 teacher is a larger ModernBERT router trained on the SAME observed
per-action outcomes as the student.

Stress-test whether this produces meaningful "dark knowledge" or merely a more
powerful supervised regressor.

Investigate:

- why should the large teacher contain information beyond y?
- when can soft outputs help?
- what is gained over label smoothing?
- what is gained over ordinary regularization?
- what is gained over a directly trained student?
- should teacher calibration happen before distillation?
- should student calibration happen after distillation?
- can teacher uncertainty be useful?
- should the teacher predict P(success), expected score, or ranking?
- should KD use logits, probabilities, regression targets, or pairwise ranking?

Explicitly identify the strongest non-KD control.

The final experimental design MUST be able to conclude honestly:

"KD adds no value"

if that is what the data shows.

---

# 8. Full primary-source verification

Several v2 references were only abstract/API inspected.

Upgrade important sources to full-body inspection where legally accessible.

PRIORITY A — must read body:

- RouteLLM
- RouterDC
- HyDRA
- LLMRouterBench
- ConsRoute
- Hybrid-LLM
- BEST-Route
- prefill-activation / hidden-state routing work
- ModernBERT
- relevant Split-LLM / collaborative inference systems papers
- foundational KD paper
- calibration paper

PRIORITY B — read where relevant:

- Arch-Router
- RouteLMT
- IRT-Router
- DistilBERT
- TinyBERT
- MiniLM
- relevant ranking KD
- edge/cloud collaborative inference surveys

For each source record:

- exact title
- exact authors
- venue/status
- year
- DOI/arXiv/official URL
- official repo
- exact pages/sections supporting each load-bearing claim
- whether body was actually inspected
- whether the claim is fact, author claim, or our interpretation

Do not carry a `[VERIFIED]` label from v2 if the underlying source was actually
abstract/API only.

---

# 9. Dedicated systems-literature novelty search

The v2 sprint explicitly under-covered IEEE/ACM systems literature.

Perform a broader, targeted search for prior work in:

ACM:
- SIGCOMM
- MobiCom
- MobiSys
- SenSys
- CoNEXT
- ASPLOS
- EuroSys
- IMC where relevant

IEEE:
- INFOCOM
- TMC
- JSAC
- ICDCS
- EDGE
- relevant communications/networking venues

Also search:
- USENIX ATC / NSDI where relevant
- MLSys
- NeurIPS/ICML systems-routing work

Search combinations of:

- split LLM routing
- collaborative LLM inference
- edge-cloud LLM inference
- split neural network routing
- dynamic split point selection
- adaptive partitioning
- semantic routing with network cost
- model routing with communication cost
- activation-transfer-aware inference
- bandwidth-aware split inference
- latency-aware DNN partitioning
- learned edge/cloud routing
- query-aware model offloading
- model selection plus network state
- quality-cost routing

The goal is NOT merely to find papers supporting us.

Actively try to invalidate the proposed novelty.

Create:

`methods-v3/systems-prior-art-map.md`

with a table:

| Work | Routing? | Query-aware? | Model selection? | Split depth? | Measured activation bytes? | Live network state? | Learned utility? | Edge deployment? | Closest overlap |

---

# 10. Ban "first" claims unless proven

The current v2 contribution sentence contains:

"the first router to ..."

This MUST NOT survive by default.

The v3 manuscript should use language such as:

"We investigate..."
"We propose..."
"We evaluate..."

unless the expanded systematic search provides unusually strong evidence for a
priority claim.

Even if the bounded search finds no precedent, prefer:

"To our knowledge..."

and document the search scope.

Do not manufacture novelty from absence.

---

# 11. Reassess HyDRA overlap correctly

Verify HyDRA's architecture from its actual paper.

In particular determine whether its multiple sigmoid heads represent:

- per-model utilities
- per-route utilities
- capability dimensions
- something else

Do not describe "four sigmoid heads" as equivalent to our proposed per-action
heads unless the paper actually says that.

Explain:

- what HyDRA predicts
- how model profiles enter its decision
- where it overlaps with our design
- where it differs
- what it invalidates as novelty
- what it does NOT invalidate

---

# 12. Reassess LLMRouterBench conclusion

Read the paper body.

Determine exactly what the statement about encoder/backbone choice means.

Do not turn:

"limited effect in the benchmark under tested settings"

into:

"encoder architecture never matters."

Report:

- tested backbones
- tested routers
- datasets
- model pools
- metrics
- actual scope of the conclusion

Use it only within those limits.

---

# 13. Backbone choice: ModernBERT is a candidate, not dogma

Verify:

- ModernBERT-base parameters
- ModernBERT-large parameters
- hidden dimensions
- licences
- checkpoint availability
- ONNX support
- INT8 support
- realistic edge latency evidence

Then compare against at least:

- DeBERTa-v3-small/base
- MiniLM-class encoder
- another current compact encoder justified by evidence

The goal is NOT to reopen the entire method search.

The goal is to determine whether ModernBERFIRST implementation
candidate.

State clearly:

BACKBONE CHOICE IS AN ENGINEERING DECISION, NOT A NOVELTY CLAIM.

If ModernBERT is still recommended, explain why.

---

# 14. Define utility precisely

The phrase "probability of success" is currently underspecified.

Define what success means for:

- factual QA
- reasoning tasks
- open-ended generation
- benchmark scoring
- pairwise preference
- partial-credit metrics

Investigate whether the router should predict:

A. P(pass threshold | q,M)
B. expected task score E[S|q,M]
C. pairwise model preference
D. calibrated probability of outperforming an edge baseline
E. another measurable utility

The choice must align with the datasets/model pool.

Avoid pretending a heterogeneous benchmark has one natural binary definition.

Produce a recommended general mathematical definition plus task-specific
instantiations.

---

# 15. Revisit the cost function

The v2 online rule uses:

argmax [ U_hat - lambda C ]

but C remains under-specified.

Develop a defensible conference implementation.

Compare:

### Option 1
Normalized scalar cost

### Option 2
Latency-only online penalty
Report bytes/energy/cost separately.

### Option 3
Constrained optimization
Max utility subject to latency/bandwidth/budget SLA.

### Option 4
Pareto policy/frontier evaluation.

Determine which is:

- easiest to interpret
- easiest to implement
- faithful to the original paper
- appropriate for systems evaluation
- least arbitrary

Do not add milliseconds + bytes + dollars directly.

If no single scalar is defensible yet, explicitly retain lambda formulation for
theory but use a constrained/SLA implementation experimentally.

---

# 16. Model pool

Do not invent the advisor's unclear B1/Gemma comment.

Instead:

- inspect original manuscript model names
- identify invalid/stale model names
- verify current official checkpoints
- design selection criteria

The pool should create meaningful routing headroom:

- at least one genuinely edge-feasible SLM
- at least one stronger model
- Split-compatible model where possible
- meaningful quality gap but overlapping competencies
- open/reproducible checkpoints
- feasible VRAM

Investigate whether starting with N=2 is the cleanest first milestone.

Clearly separate:

INITIAL IMPLEMENTATION POOL

from:

FULL PAPER POOL.

Do not claim advisor approval for a specific model unless recorded.

---

# 17. Baseline plan

Rebuild the baseline table after the deeper prior-art review.

At minimum assess:

- Always Edge
- Always Strong
- Always Split
- random
- dataset prior
- TF-IDF + Logistic Regression
- non-distilled micro-encoder
- teacher router
- hidden-state / prefill-activation router
- RouteLLM-style classifier if reproducible
- RouterDC if reproducible/relevant
- HyDRA-style capability router if relevant
- generative router baseline if feasible
- oracle

For every baseline specify:

- what question it answers
- whether code exists
- whether exact reproduction is realistic
- whether it must be reimplemented
- compute cost
- fair-comparison requirements

---

# 18. Conference core versus journal extension

Keep continual learning OUT of the conference core.

Conference core should be independently publishable without CL.

Journal extension:

- changing model pool
- new SLMs
- domain shift
- continual calibration
- replay
- previous-router distillation
- adapters
- forgetting analysis

Only include minimal forward-compatible logging/interfaces in conference code.

Do not put continual-learning boxes into the main conference architecture figure.

---

# 19. Rewrite the architecture

Create a cleaner architecture based on the outcome of ISSUE A.

Preferred conceptual separation if supported:

TRAINING:

observed query/model outcomes
        |
        +------> larger teacher router
        |              |
        |              +--> soft utility targets
        |                       |
        +-----------------------+
                                v
                         micro-encoder student

INFERENCE:

query q
   |
   v
micro-encoder
   |
   v
model utility estimates
U_hat(M|q)
   |
   |             live system state
   |                    |
   |                    v
   |                 C(a|s)
   |                    |
   +---------+----------+
             v
      runtime optimizer
             |
    +--------+--------+
    |        |        |
   EDGE    SPLIT(d)  REMOTE

Do not force this shape if the investigation demonstrates that per-action
utility is technically superior.

The figure must distinguish:

- semantic/model prediction
- runtime systems measurement
- training-only teacher
- execution actions

Do not include journal continual learning in the primary conference figure.

---

# 20. Fix LaTeX figure implementation

The current `architecture-figure.tex` has compile issues including use of
unsupported/undefined TikZ or symbol constructs.

Create a replacement:

`methods-v3/architecture-figure-v3.tex`

Requirements:

- self-contained minimal compilable LaTeX
- use standard TikZ libraries only
- no undefined custom styles
- no unsupported arrow tips
- no undefined `\blacktriangledown`, `\Letter`, `\dashrightarrow`
- no hidden external assets
- professional two-phase training/inference figure
- readable in two-column paper format

If `pdflatex` or `latexmk` is installed:
compile it and save compilation log.

If no LaTeX toolchain is available:
state this explicitly and perform static syntax review only.

Do not claim compile success unless it was actually compiled.

---

# 21. Rewrite manuscript-ready Proposed Solution

Create:

`methods-v3/proposed-solution-blue-v3.tex`

Do NOT modify main-original.tex.

The section must contain REAL citations using verified BibTeX keys.

It should cover:

1. design overview
2. micro-encoder
3. precise utility definition
4. teacher/student KD training
5. model-vs-action mapping
6. runtime cost integration
7. Split-LLM execution
8. training algorithm
9. inference algorithm
10. assumptions and limitations

Avoid claims such as:

- "the first..."
- "requires no retraining"
- "network changes force retraining"
- "split quality is identical"

unless qualified and supported.

All new manuscript text remains BLUE.

Do not cite internal GNHF documents in the manuscript.
Use research papers.

---

# 22. Citation audit

Create:

`methods-v3/citation-audit.md`

For EVERY paragraph in `proposed-solution-blue-v3.tex`, state:

- which sentences are our proposed design and need no prior-art citation
- which factual sentences need citations
- citation key
- exact source section/page
- inspection status
- whether the citation really supports the wording

No naked factual claims.

No citation laundering.

---

# 23. BibTeX

Create:

`methods-v3/method-references-v3.bib`

Only include verified references.

For each entry verify:

- authors
- title
- venue
- year
- DOI if known
- arXiv ID if applicable

Do not fabricate metadata.

Use official proceedings metadata when available.

---

# 24. Contribution statement

After the expanded search, produce THREE versions:

### Conservative
Safe before experiments.

### Conditional
Allowed if E1/E4/E7 succeed.

### Strong
Only allowed if experiments succeed AND literature search supports the
novelty wording.

Do not use "first" in Conservative or Conditional.

The final summary must recommend which version should currently go into the
paper.

---

# 25. Experiments

Update E1-E8 as needed based on architecture changes.

Required falsification structure:

E1 — Does KD actually beat direct student training?

E2 — Does learned router beat TF-IDF+LR?

E3 — Does it beat / complement hidden-state self-routing? Does KD improve or preserve calibration versus:
     non-KD + post-hoc calibration?

E5 — utility/cost tradeoff sweep

E6 — bandwidth/RTT variation without semantic-router retraining

E7 — real Split execution with:
     TTFT
     TPOT
     p50/p95/p99
     activation bytes
     throughput
     GPU/CPU/memory
     split-depth effects

E8 — generalization/domain-shift

Add:

E0 — SPLIT EQUIVALENCE TEST

Before treating split depths as cost-only actions:

for each tested split depth:
compare output/score against unsplit execution.

Report:
- exact token equality where meaningful
- output metric equality
- numerical activation effects
- quantization/compression configuration

E0 determines whether utility can be model-level or must be action/depth-level.

---

# 26. Henry dependency

Do not invent any Henry/lab detail.

Create a concise message/checklist requesting:

- repository
- license
- supported model HF ID
- split-layer API
- valid depths
- activation shape
- activation dtype
- activation compression/quantization
- exact-vs-approximate split
- serialization
- networking
- edge machine
- server machine
- GPU models + VRAM
- software versions
- logging hooks
- sudo / tc/netem permission

Explain exactly which method decisions depend on each answer.

---

# 27. Required outputs

Create under `methods-v3/`:

00-review-findings.md
01-model-vs-action-utility.md
02-split-equivalence-analysis.md
03-kd-hardening.md
04-routeLLM-terminology-review.md
05-full-routing-prior-art.md
06-systems-prior-art-map.md
07-backbone-verification.md
08-utility-definition.md
09-cost-policy.md
10-model-pool.md
11-baselines-v3.md
12-novelty-v3.md
13-experiments-v3.md
14-henry-checklist.md
15-conference-vs-journal.md
16-citation-audit.md
17-verified-references-v3.md
method-references-v3.bib
architecture-figure-v3.tex
proposed-solution-blue-v3.tex
FINAL-SUMMARY-v3.md

Optional:
architecture-figure-v3.pdf
latex-compile.log

Do not overwrite anything in `methods-v2/`.

---

# 28. FINAL-SUMMARY-v3 questions

Answer clearly:

1. What from v2 remains correct?
2. What from v2 was wrong or too strong?
3. Should utility be model-level or action-level?
4. Under what conditions do Split depths share utility?
5. What happens if split execution is lossy?
6. What exactly should f_theta be now?
7. What exactly should the student predict?
8. What teacher should be used?
9. Is the teacher genuinely providing useful KD information?
10. What is the strongest non-KD control?
11. What does RouteLLM actually do?
12. What does HyDRA actually do?
13. What does LLMRouterBench actually establish?
14. Which backbone should we implement first and why?
15. What should C(a|s) be in the first implementation?
16. What is the corrected conference architecture?
17. What novelty claims survive the expanded systems search?
18. What wording is safe BEFORE experiments?
19. What wording becomes possible AFTER successful experiments?
20. Which references are now full-body verified?
21. Which references remain incomplete?
22. Is the architecture figure compile-clean?
23. Is the blue Proposed Solution citation-complete?
24. What still requires advisor approval?
25. What still requires Henry?
26. What are the first 10 coding/experiment steps?
27. What should NOT be merged into main yet?
28. What is ready to merge into main after advisor review?

---

# 29. Evidence rules

Use:

[VERIFIED-BODY]
Full primary paper body checked.

[VERIFIED-META]
Bibliographic identity confirmed only.

[AUTHOR-CLAIM]
Claim reported by paper authors but not independently reproduced.

[PROPOSED]
Our method.

[OPEN]
Needs experiment/advisor/Henry confirmation.

[REJECT]
Do not use.

An absence-of-prior-work statement is NEVER automatically `[VERIFIED-BODY]`.

It must be phrased as bounded-search evidence.

---

# 30. Hard prohibitions

DO NOT:

- change the original research problem
- restart A/B/C method selection
- make Jacobi part of the method
- move continual learning into the conference core
- assume KD works
- assume ModernBERT is optimal
- assume split execution is lossless
- claim new split depth can be added without training
- claim a system-state-aware learned router necessarily needs retraining for each
  network change
- call teacher-generated hard labels soft KD without qualification
- claim "first" based only on arXiv/ACL search
- fabricate Henry's hardware
- fabricate model names
- fabricate references
- fabricate experimental results
- overwrite methods-v2
- modify source/main-original.tex

---

# 31. Stop condition

Stop only when:

1. model-vs-action utility ambiguity is resolved with a reasoned recommendation;
2. exact-vs-lossy split cases are explicitly separated;
3. E0 split-equivalence experiment exists;
4. KD teacher logic has survived a skeptical review;
5. RouteLLM terminology has been corrected;
6. HyDRA body has been checked and overlap accurately described;
7. LLMRouterBench body has been checked and conclusion bounded correctly;
8. ModernBERT facts have been verified;
9. systems-venue prior-art search has materially expanded beyond arXiv/ACL;
10. no unsupported "first" claim remains;
11. conference and journal scopes remain separated;
12. corrected architecture is specified;
13. blue manuscript contains real paper citations;
14. citation audit is complete;
15. verified BibTeX exists;
16. figure source is repaired;
17. figure compilation is attempted if toolchain exists;
18. every novelty statement is evidence-tagged and experiment-gated;
19. no results are invented;
20. FINAL-SUMMARY-v3 answers all 28 questions.
