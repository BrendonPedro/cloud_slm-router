# Objective

Determine whether the research direction currently titled:

"Tiny-LM with Jacobi-Forced Micro-Encoder for Collaborative Inference
between Edge SLMs and Split-LLMs"

still contains a defensible research gap as of September 2026, determine
what "Jacobi-Forced Micro-Encoder" could technically mean, identify the
closest prior art, and produce a decision-ready research package and
revised paper draft for discussion with the advisor.

This is an academic research audit and prototype exercise.

DO NOT fabricate:
- citations
- papers
- implementations
- benchmark results
- experimental measurements
- model capabilities
- novelty claims

A manuscript may look complete only where evidence is complete.
Unrun experiments must remain explicitly marked as proposed/TODO.
Never convert predicted or hypothetical results into past-tense findings.

Read source/main-original.tex first.
Preserve it unchanged.

Each iteration:
1. Read previous gnhf notes.
2. Make one coherent research/build improvement.
3. Verify claims against primary sources whenever possible.
4. Commit the change.
5. Record uncertainty and unresolved questions.

## Primary research questions

1. What exact research problem does the current paper formulate?
2. What novelty does the current draft actually claim?
3. Which parts of that novelty already exist in the literature?
4. Does a meaningful research gap remain in September 2026?
5. What is Jacobi Forcing technically?
6. Is "Jacobi-Forced Micro-Encoder" an established method?
7. If not, what technically coherent architecture could that phrase describe?
8. Is Jacobi Forcing actually appropriate for a router/encoder, given that
   Jacobi Forcing was developed for causal parallel decoding?
9. Does the router need generative decoding at all?
10. Could a decision-specific architecture such as Jev/System One-type
    models change the motivation or proposed design?
11. What are the closest academic and production systems to this work?
12. What would have to be implemented and experimentally demonstrated
    for this paper to make a defensible contribution?
13. Are the current datasets, baselines, metrics, model choices, and
    optimization objective appropriate?
14. Which claims in main-original.tex are currently unsupported?
15. What should the advisor consider:
    continue as written, narrow the contribution, redesign the method,
    or change direction?

Do NOT make the final continue/redesign decision as a fact.
Provide evidence and options for the advisor.

## Source hierarchy

Prefer, in order:

1. Peer-reviewed conference/journal papers
2. Official paper/arXiv + official code repository
3. Official model/project documentation
4. Reputable technical reports
5. Company engineering/research posts
6. Secondary reporting only when primary material is unavailable

For every source record:
- title
- authors/company
- date
- venue/status
- URL/DOI/arXiv
- what it actually establishes
- relevance to our paper
- limitations
- whether code/models/data are available

Never cite a secondary article when the primary source supports the same claim.

## Required literature areas

Research comprehensively:

### A. LLM routing
- weak/strong model routing
- query-level model routing
- cost-aware routing
- confidence-aware routing
- learned routing
- router calibration
- multi-model routing
- preference-based routing

### B. Edge-cloud inference
- SLM/LLM collaborative inference
- cloud-edge routing
- edge offloading
- latency-aware inference
- energy-aware routing
- communication-aware routing
- privacy-aware routing

### C. Split LLMs
- Split-LLM inference
- split learning vs split inference
- activation transmission
- partition placement
- privacy claims and limitations
- communication costs

### D. Fast/specialized decision models
- Jev / TypeSafe System One Models
- structured-decision models
- calibrated classifiers
- small routing encoders
- discriminative vs generative routers
- confidence estimation
- selective prediction / abstention

### E. Jacobi-related methods
- Jacobi decoding
- Jacobi Forcing
- consistency LMs
- diffusion language models
- speculative decoding
- parallel decoding
- multi-token prediction

Explicitly determine whether Jacobi Forcing has previously been used
for routing or encoder-only decision systems.

### F. Existing systems and code
Find public repositories, checkpoints, benchmarks, and implementations
that could accelerate our build.

Include:
- JacobiForcing official repository
- LLMRouterBench
- RouteLLM
- RouteLMT
- ICL-Router
- IRT-Router
- Arch-Router
- relevant edge-cloud routers
- any comparable 2026 systems discovered

## Required deliverables

### 1. research/problem-as-written.md

Explain the current paper from main-original.tex:
- problem
- objective
- variables/equations
- claimed contributions
- proposed evaluation
- unsupported assumptions
- unfinished sections

Quote line/section locations from the source.

### 2. research/current-landscape.md

A chronological state-of-the-art review through September 2026.

Separate:
- peer-reviewed work
- preprints
- released open-source systems
- proprietary/industry systems

### 3. research/closest-prior-art.md

Identify the 10-20 papers/systems closest to this proposal.

For each:
- what problem it solves
- router architecture
- local/cloud setup
- optimization targets
- datasets
- metrics
- results
- implementation availability
- exact overlap with our proposal
- exact difference from our proposal

### 4. research/novelty-matrix.md

Rows = prior work.
Columns include:

- edge SLM
- cloud LLM
- Split-LLM
- query-level routing
- learned router
- lightweight router
- confidence/calibration
- latency-aware
- cost-aware
- communication-aware
- privacy-aware
- heterogeneous model pool
- no-retraining adaptation
- parallel/Jacobi mechanism
- structured decision output
- open source

Finish with:
- clearly occupied research space
- partially occupied space
- genuinely unresolved questions

Do NOT declare novelty merely because exact wording differs.

### 5. research/jev-system-one.md

Deep review of Jev/System One Models.

Separate vendor claims from independently demonstrated facts.

Analyze:
- architecture disclosures
- structured typed outputs
- calibrated probabilities
- routing/classification suitability
- parallel sampling
- latency claims
- price claims
- API-only limitations
- reproducibility limitations

Answer:
"Does Jev weaken, strengthen, or redirect the motivation for our router?"

### 6. research/jacobi-forcing.md

Explain Jacobi Forcing from first principles.

Include:
- original problem
- Jacobi decoding
- training objective
- parallel decoding
- causal properties
- KV-cache behavior
- speedups
- limitations
- released code/checkpoints

Then explicitly answer:

"Does Jacobi Forcing naturally apply to a tiny routing encoder?"

If not directly, explain what adaptation would be necessary.

### 7. research/micro-encoder-investigation.md

Search for:
- "micro-encoder"
- "micro encoder"
- lightweight encoders
- tiny encoders
- routing encoders
- query encoders

Determine whether "Jacobi-Forced Micro-Encoder" exists in prior literature.

If no evidence is found, state:
"No established method with this exact name was found as of [date]."

Do NOT invent a definition.

Then propose 2-3 technically coherent interpretations, clearly labeled
as proposed interpretations rather than established techniques.

### 8. research/gap-assessment.md

Evaluate the current gap claim sentence by sentence.

Use four labels:
- supported
- partially supported
- superseded by prior work
- unresolved / needs evidence

Identify the narrowest defensible contribution that appears to remain.

### 9. architecture/options.md

Develop 2-4 candidate architectures.

At minimum compare:

A. Tiny generative LM router
B. Lightweight discriminative encoder/router
C. confidence/self-routing edge SLM
D. structured decision model inspired by System One/Jev concepts

For each:
- inputs
- outputs
- training labels
- objective
- latency
- parameter target
- adaptability
- deployment position
- compatibility with Split-LLM
- expected advantages
- risks
- implementation difficulty

Only include a Jacobi-Forcing variant if technically justified.

### 10. architecture/recommended-experiment.md

Design the smallest experiment capable of falsifying or supporting
the paper's central claim.

Specify:
- hypothesis
- dataset
- train/dev/test split
- candidate models
- router
- baselines
- metrics
- ablations
- statistical tests
- hardware assumptions
- exact success/failure criteria

### 11. experiments/reproducibility-plan.md

List exact public repos/data/checkpoints that can be reused.

For every dependency:
- source
- license
- install path
- expected hardware
- reproduction command if known

### 12. experiments/prototype/

If hardware/time permits, implement a minimal research prototype.

Rules:
- Do not fake performance.
- Log every command.
- Save raw outputs.
- Record hardware/software versions.
- Fix random seeds.
- Keep experiment configuration files.
- Separate measured results from estimates.

If a full experiment is impossible overnight, implement only enough
to validate the pipeline and state what remains.

### 13. research/claim-audit.md

Audit every substantive claim in source/main-original.tex.

Columns:
- manuscript claim
- location
- current citation
- citation actually supports claim? yes/no/partial
- better source
- rewrite required?
- experimental evidence required?

Pay special attention to:
- "novel"
- "unlike existing methods"
- "without retraining"
- privacy claims
- latency claims
- scalability claims
- "extensive experiments demonstrate..."

### 14. references/library.bib

Produce clean BibTeX from verified primary sources.

No fabricated metadata.

### 15. paper/main-revised.tex

Create a revised academic manuscript based on verified research.

Rules:
- never overwrite source/main-original.tex
- use cautious academic language
- reflect the actual novelty assessment
- remove unsupported results
- proposed experiments must remain future tense
- measured experiments may be past tense only when raw evidence exists
- distinguish system design from experimental validation
- citations must resolve to references/library.bib

A paper without completed experiments may still be structurally complete,
but must not pretend results exist.

### 16. advisor/one-page-brief.md

One page only:

- what the original idea is
- what changed in the field
- closest prior work
- what appears novel / not novel
- what "Jacobi-Forced Micro-Encoder" currently means or does not mean
- Jev relevance
- recommended research questions
- proposed minimum experiment
- key decisions needed from advisor

### 17. advisor/talking-points.md

Prepare me for the meeting.

Include:
- 60-second explanation of the paper
- 60-second literature update
- questions I should ask
- terms I should understand
- likely professor questions
- concise answers
- what I should NOT claim to know yet

### 18. advisor/research-sprint-report.md

Explain transparently:
- what was done in this one-day AI-assisted research sprint
- which tools were used
- what was human-reviewed
- what has not been independently validated
- what experiments were/weren't actually run

This must make the workflow transparent rather than presenting
machine-generated work as independently completed human research.

## Stop condition

Stop only when:
- all 18 deliverables exist,
- every research claim has a traceable source,
- novelty matrix has been self-reviewed,
- source/main-original.tex has been claim-audited,
- main-revised.tex has no invented experimental result,
- advisor brief has been checked against the full evidence,
- unresolved questions are explicitly listed.