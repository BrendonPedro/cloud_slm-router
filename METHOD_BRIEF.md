cat > METHOD_BRIEF.md <<'EOF'
# METHOD / APPROACH RESEARCH BRIEF

## Purpose

Determine the strongest technically defensible APPROACHES / METHODS for
implementing the EXISTING research paper:

"Tiny-LM with Jacobi-Forced Micro-Encoder for Collaborative Inference
between Edge SLMs and Split-LLMs"

The advisor has explicitly stated that the student must NOT deviate from the
original paper's research direction.

The advisor IS flexible regarding the method / approach used to implement the
proposed system.

The intended target venue is ACM SIGCOMM 2027.

This run therefore has ONE central goal:

"What are the best technically defensible ways to implement the routing
mechanism already proposed in the original manuscript, what are the trade-offs
between those methods, and what hardware / data / experiments will be required
to evaluate them?"

This is a METHOD-SELECTION AND IMPLEMENTATION-PLANNING sprint.

It is NOT an implementation sprint.

It is NOT an experiment sprint.

It is NOT permission to rewrite the research question.

It is NOT permission to rewrite the manuscript.

It is NOT permission to generate experimental results.

Do NOT train large models.
Do NOT download large checkpoints unless a tiny metadata/config file is needed
for verification.
Do NOT run expensive GPU experiments.
Do NOT modify source/main-original.tex.
Do NOT modify paper/main-revised.tex.
Do NOT modify the original main manuscript.

Small scripts, pseudocode, diagrams, calculations, and feasibility checks are
allowed.

======================================================================
1. AUTHORITATIVE SOURCE — READ THIS FIRST
======================================================================

Read:

source/main-original.tex

before doing anything else.

Treat source/main-original.tex as the authoritative definition of the research
project.

Other files from the previous research sprint may be consulted as supporting
material, including:

research/
advisor/
architecture/
experiments/
references/

However:

If a previous AI-generated document proposes changing the research direction,
the ORIGINAL manuscript takes precedence.

The purpose of this run is to find a METHOD for the original paper.

======================================================================
2. FIXED RESEARCH PROBLEM
======================================================================

The research problem is FIXED.

For an input query q, a lightweight router deployed at the edge must decide
which available inference model/path should process that query.

The manuscript defines a model set:

M = {M_1, M_2, ..., M_K}

and a routing function:

R : Q -> M

The desired decision maximizes expected response utility while penalizing
system cost:

max_R E_q [ U(R(q),q) - lambda * C(R(q),q) ]

where:

U(M_k,q)
= expected response quality / utility for model M_k on query q.

C(M_k,q)
= the cost of using model M_k, including potentially:
- computation;
- communication;
- latency;
- memory/resource use;
- operational/monetary cost.

lambda
= the weighting between response utility and system cost.

The manuscript currently approximates the routing decision as:

R(q) = argmax_{M_k in M} f_theta(q,M_k)

where f_theta is described as a lightweight TLM-based scoring mechanism.

THE CENTRAL MISSING METHOD QUESTION IS:

What should f_theta actually be, and how should it be implemented?

The Proposed Solution section of the original manuscript is currently empty.

This run must focus on that methodological gap.

======================================================================
3. FIXED REQUIREMENTS FROM THE ORIGINAL PAPER
======================================================================

Every serious candidate method must preserve the following requirements.

A. LIGHTWEIGHT

The router must have low enough computational and latency overhead to make
edge deployment worthwhile.

B. QUERY UNDERSTANDING

The method must capture enough information about the query to estimate things
such as:
- difficulty;
- intent;
- uncertainty;
- expected model capability / expected gain from escalation.

C. SYSTEM AWARENESS

The final routing decision must be capable of reflecting:
- communication overhead;
- computation;
- memory limitations;
- latency;
- response time;
- potentially current network/system state.

D. ADAPTABILITY

The original manuscript wants the framework to work with heterogeneous and
evolving model pools without requiring prohibitively expensive retraining.

Do not preserve this claim automatically.

For every candidate method, determine whether and how it can actually satisfy
this property.

======================================================================
4. DO NOT CHANGE THE PAPER INTO ANOTHER RESEARCH PROJECT
======================================================================

Do NOT replace the project with:

- a generic cloud scheduler;
- a generic edge scheduler;
- a pure network scheduling paper;
- a calibration-only paper;
- an OOD/domain-shift-only paper;
- a standalone Jacobi Forcing paper;
- a Jev replication;
- a generic benchmark paper;
- a pure Split-LLM partition-placement paper;
- a progressive-compute paper unrelated to the original TLM router;
- another newly invented research problem.

Supporting ideas from those areas may be incorporated if they help implement
the ORIGINAL routing objective.

Every method must map explicitly back to:

R(q) = argmax f_theta(q,M_k)

and:

maximize U - lambda*C.

======================================================================
5. TARGET VENUE — ACM SIGCOMM 2027
======================================================================

The advisor intends to target ACM SIGCOMM 2027.

Research the CURRENT official SIGCOMM 2027 information from:

https://conferences.sigcomm.org/sigcomm/2027/

Use official sources wherever possible.

If the detailed 2027 CFP is not yet available, say so explicitly.

In that case, use recent official SIGCOMM CFP material only to understand the
conference's networked-systems orientation.

Do NOT invent:
- submission dates;
- page limits;
- artifact requirements;
- acceptance criteria;
- topics that have not been published for SIGCOMM 2027.

The original research problem must remain fixed.

However, method selection should consider whether the resulting work can
support a convincing NETWORKED-SYSTEMS evaluation.

For every method answer:

"Why would the eventual system evaluation matter to networking / networked
systems rather than being merely an ML-classification result?"

Pay particular attention to measurable effects on:

- edge/cloud communication;
- bandwidth;
- RTT;
- activation-transfer volume;
- Split-LLM communication;
- TTFT;
- TPOT;
- end-to-end latency;
- throughput;
- tail latency;
- server/edge load;
- network variability;
- operational cost;
- resource utilization.

Do NOT claim that any approach is guaranteed to be accepted by SIGCOMM.

======================================================================
6. RESEARCH THE METHOD SPACE
======================================================================

Investigate at least the following families.

Do NOT assume any one of them is correct before the research is complete.

----------------------------------------------------------------------
METHOD FAMILY A — TINY GENERATIVE LANGUAGE-MODEL ROUTER
----------------------------------------------------------------------

Investigate an implementation closest to the original phrase
"Tiny Language Model".

Possible idea:

query + model descriptions / profiles
    ->
small generative LM
    ->
model / execution-path decision

Determine:

- reasonable model sizes;
- whether generation is actually required;
- whether label-token probabilities could be used;
- latency implications;
- training/fine-tuning requirements;
- calibration;
- how multiple candidate models could be represented;
- how new models could be added;
- whether this is genuinely lightweight on edge hardware.

Find relevant prior art and code.

----------------------------------------------------------------------
METHOD FAMILY B — LIGHTWEIGHT DISCRIMINATIVE MICRO-ENCODER
----------------------------------------------------------------------

Investigate a small encoder/classifier architecture.

Possible structure:

query
    ->
small encoder
    ->
query representation
    ->
model-conditioned scoring head
    ->
score for each M_k

Investigate suitable families such as compact BERT/DeBERTa/ModernBERT-style
encoders or other efficient encoders.

Do NOT automatically choose DeBERTa or ModernBERT.

Determine which architectures are realistic for an edge router.

Consider parameter count, memory, latency, quantization, and calibration.

----------------------------------------------------------------------
METHOD FAMILY C — MODEL-CONDITIONED UTILITY PREDICTOR
----------------------------------------------------------------------

Instead of directly predicting a class, investigate:

f_theta(q,M_k) ~= predicted utility of M_k for q

Possible input:

query embedding
+
model profile / model embedding

Output:

predicted quality / probability of success for candidate M_k.

Then combine predicted utility with measured system cost:

score(q,M_k,s)
=
predicted_utility(q,M_k)
-
lambda * measured_or_predicted_cost(M_k,s)

This is especially important because it maps naturally to the original
U - lambda*C formulation.

Investigate whether new model profiles can be added without full router
retraining.

----------------------------------------------------------------------
METHOD FAMILY D — EDGE-SLM REPRESENTATION / HIDDEN-STATE ROUTER
----------------------------------------------------------------------

Investigate using representations already computed by the local SLM.

Possible idea:

query
    ->
local SLM prompt/prefill representation
    ->
small probe/head
    ->
expected benefit of local vs stronger execution

Relevant questions:

- Does this reuse computation?
- Does obtaining the representation cost too much before routing?
- Which layer/depth is appropriate?
- Can inference work be reused after an EDGE decision?
- What happens if a SPLIT decision is made?
- Does this fit the original lightweight TLM framing?

Find primary prior work.

----------------------------------------------------------------------
METHOD FAMILY E — HYBRID SEMANTIC + SYSTEM-AWARE ROUTER
----------------------------------------------------------------------

Investigate separating semantic capability estimation from measured system
conditions.

Example:

semantic model:
    predicted U(M_k,q)

systems module:
    measured C(M_k,s)

decision:
    argmax [ predicted U - lambda * measured C ]

where s may contain:
- bandwidth;
- RTT;
- queue/server load;
- prompt length;
- activation size;
- current hardware state.

Compare this against putting all variables into one neural model.

This method must remain a ROUTER for the original paper, not become a generic
scheduler.

----------------------------------------------------------------------
METHOD FAMILY F — JACOBI-FORCED MICRO-ENCODER INTERPRETATION
----------------------------------------------------------------------

The title of the original manuscript contains:

"Jacobi-Forced Micro-Encoder"

Investigate this seriously.

Read the primary Jacobi Forcing paper and official implementation.

Determine:

1. What Jacobi Forcing actually is.
2. What neural architecture it operates on.
3. What its training objective is.
4. Why it accelerates causal autoregressive generation.
5. Whether there is any established use of Jacobi Forcing for routing or
   encoder classification.
6. Whether the TRAINING PRINCIPLE can be adapted coherently to a micro-router.
7. What such an adaptation would mathematically mean.
8. Whether it would offer any plausible routing-latency or quality advantage.
9. Whether the name "Jacobi-Forced Micro-Encoder" can be technically justified.
10. What experiments would be necessary to validate it.

Distinguish very clearly:

ESTABLISHED:
facts supported by the Jacobi Forcing paper/code.

PROPOSED:
an adaptation designed for this project.

UNSUPPORTED:
ideas for which no technical justification can be found.

Do NOT state that an established method called "Jacobi-Forced Micro-Encoder"
exists unless a primary source demonstrates this.

Also do NOT remove Jacobi from the original paper.

If its intended role remains unclear, turn that into a precise advisor question.

======================================================================
7. JEV / SYSTEM ONE AS A REFERENCE, NOT A REPLACEMENT
======================================================================

Investigate TypeSafe Jev / System One.

The purpose is NOT to recreate Jev.

The purpose is to learn from its public design philosophy.

Determine:

- what TypeSafe publicly claims Jev does;
- what its observable input/output interface is;
- how it represents structured decisions;
- whether confidence/probability outputs are exposed;
- what is known;
- what is proprietary/unknown;
- what cannot be independently verified.

Then identify OPEN ACADEMIC approaches that implement related ideas:

- structured classification;
- calibrated decision models;
- lightweight query routers;
- capability prediction;
- selective prediction;
- deferral;
- semantic query encoders;
- hidden-state probes;
- model-selection scoring.

Use those academic works as potential implementation references.

Do NOT claim they reproduce Jev.

======================================================================
8. DEFINE THE TRAINING TARGET
======================================================================

This is a central methodological question.

Investigate at least the following formulations.

A. BINARY CLASSIFICATION

EDGE
vs
STRONG/SPLIT

B. MULTICLASS ROUTING

SLM_1
SLM_2
...
SPLIT_1
SPLIT_2
...

C. UTILITY REGRESSION

For each candidate M_k:

predict U(M_k,q)

D. PAIRWISE GAIN PREDICTION

Predict:

DeltaU =
U(strong,q) - U(weak,q)

E. DIRECT UTILITY-COST SCORE

Predict:

U(M_k,q) - lambda*C(M_k,q)

F. SEPARATED QUALITY AND SYSTEM COST

Learn:

U_hat(M_k,q)

Measure or separately predict:

C_hat(M_k,s)

Then:

score =
U_hat - lambda*C_hat

For each formulation explain:

- how labels are produced;
- how it maps to the original equations;
- ability to support multiple models;
- adaptability to new models;
- calibration;
- training complexity;
- inference cost;
- expected robustness;
- suitability for SIGCOMM-style systems evaluation.

======================================================================
9. SYSTEM-STATE INTEGRATION
======================================================================

The original paper discusses system constraints.

Determine exactly how they should enter the implementation.

Compare:

APPROACH S1:
Put query and live system variables into the same neural router.

APPROACH S2:
Use the learned router only to predict model/query utility, then combine that
with measured system costs outside the neural network.

APPROACH S3:
Train separate quality and system-cost predictors.

APPROACH S4:
Use a systems-only policy as a baseline.

System variables to consider include:

- RTT;
- available bandwidth;
- transmitted activation bytes;
- current server load if measurable;
- edge resource utilization;
- prompt length;
- split depth;
- predicted/observed inference latency.

Explain:

- advantages;
- disadvantages;
- retraining requirements;
- interpretability;
- robustness to changing networks;
- mapping to U - lambda*C.

======================================================================
10. ADAPTABILITY TO NEW MODELS
======================================================================

The original manuscript emphasizes heterogeneous/evolving model pools.

For each candidate method answer:

- What happens if a new SLM is added?
- What happens if a new Split-LLM is added?
- Must the full router be retrained?
- Can a model profile or embedding be added instead?
- Could zero-shot or few-shot model integration work?
- Which existing papers support such a design?
- What performance trade-off would likely result?

If a method cannot support inexpensive model addition, clearly say so.

Do not preserve an unsupported "no retraining" claim.

======================================================================
11. DATA AND LABEL PIPELINE
======================================================================

Do not assume the original SimpleQA / LLMRouterBench data is sufficient.

Investigate exactly what data is needed for the original intended model pool.

For each candidate method specify:

1. datasets;
2. approximate number of queries;
3. candidate SLMs;
4. candidate strong/Split-LLMs;
5. how every model output is generated;
6. how answer quality is scored;
7. how routing targets are created;
8. whether output labels can be shared between method candidates;
9. train/validation/test splitting;
10. prevention of data leakage;
11. OOD/domain-shift evaluation;
12. approximate number of model inference calls;
13. approximate storage requirements;
14. what can be prepared before lab access;
15. what requires GPU access.

Do not fabricate exact resource numbers when they depend on unresolved models.

Provide formulas/ranges and assumptions instead.

======================================================================
12. BASELINES
======================================================================

Preserve and investigate the original paper's proposed baseline methods:

- RouteLMT
- ICL-Router
- RouteLLM
- Arch-Router

For each:

- verify the primary paper;
- verify code availability;
- identify the exact routing mechanism;
- explain what must be adapted for SLM/Split-LLM routing;
- identify fairness concerns;
- state whether reproduction is feasible.

Also include simple baselines:

- Always Edge
- Always Strong / Always Split
- Random
- Dataset prior where meaningful
- lexical TF-IDF + logistic regression
- simple embedding classifier
- network/system rule
- oracle upper bound

Because the intended venue is SIGCOMM, do NOT compare only against ML routers.

Include system baselines such as:

- lowest-estimated-latency path;
- bandwidth-threshold policy;
- RTT-threshold policy;
- cost-minimizing rule;
- system-state-only scheduler.

======================================================================
13. SIGCOMM-ORIENTED SYSTEM EVALUATION
======================================================================

The eventual evaluation should determine whether the proposed router improves
the COMPLETE edge/cloud system, not merely classification accuracy.

For every candidate method define possible measurable claims.

Examples to investigate:

- lower end-to-end latency at matched response quality;
- lower cloud/Split invocation rate at matched quality;
- fewer transmitted bytes;
- improved TTFT;
- improved tail latency;
- better behavior under changing bandwidth/RTT;
- lower operational cost;
- improved throughput;
- better edge/cloud resource utilization.

For every potential claim specify:

INDEPENDENT VARIABLE

DEPENDENT VARIABLE

BASELINE

MEASUREMENT

FALSIFICATION CONDITION

Do not state the claim as true before experiments.

======================================================================
14. TESTBED DESIGN
======================================================================

Produce a detailed proposed testbed.

At minimum consider:

EDGE NODE
    |
controllable network
    |
CLOUD / SPLIT SERVER

Determine what can initially be emulated on one machine and what requires two
physical machines.

For the EDGE side document:

- candidate GPU class;
- minimum VRAM;
- preferred VRAM;
- CPU;
- RAM;
- storage;
- OS;
- CUDA;
- PyTorch;
- Transformers;
- quantization framework;
- energy telemetry.

For the SERVER side document:

- GPU class;
- minimum/preferred VRAM;
- number of GPUs;
- RAM;
- storage;
- model-serving software;
- Split-LLM requirements.

For the NETWORK document:

- two-machine connectivity;
- LAN/WAN assumptions;
- Ethernet vs other links;
- bandwidth control;
- RTT control;
- packet-loss control if useful;
- network contention;
- Linux tc/netem;
- traffic measurement;
- bytes transferred;
- tracing/logging.

For MEASUREMENT include:

- TTFT;
- TPOT;
- end-to-end latency;
- p50;
- p95;
- p99 where meaningful;
- requests/sec;
- tokens/sec;
- activation bytes;
- bandwidth;
- RTT;
- GPU utilization;
- CPU utilization;
- memory;
- energy/power if available;
- operational cost.

======================================================================
15. QUESTIONS FOR LAB ACCESS
======================================================================

Prepare a concise checklist to ask the advisor next week.

Include at minimum:

1. Which GPU models are available?
2. How much VRAM per GPU?
3. How many GPUs can one student reserve?
4. Can two machines be reserved simultaneously?
5. Is there a dedicated edge device?
6. What hardware is considered the edge node by the lab?
7. Is there an existing Split-LLM codebase in the lab?
8. Is there an existing edge/cloud testbed?
9. Are the machines connected over a controllable network?
10. Can I use Linux tc/netem?
11. Do I have sudo access?
12. Can I use Docker?
13. Can I install CUDA/PyTorch/Transformers/vLLM/etc.?
14. Is outbound Hugging Face access available?
15. Is GitHub access available?
16. Where should large model checkpoints be stored?
17. How much storage is available?
18. Can I collect nvidia-smi power measurements?
19. Is external power measurement hardware available?
20. Is there a preferred model family the lab already supports?
21. Is there a preferred Split-LLM framework?
22. Are cloud/API resources available?
23. Is there a compute budget?
24. Are there restrictions on long-running experiments?
25. Is there already prior lab work/code I should build upon?

======================================================================
16. METHOD CANDIDATE TEMPLATE
======================================================================

For every serious method candidate use this exact structure:

# Candidate Name

## One-sentence idea

## Why it solves the original paper's problem

## Architecture

ASCII diagram.

## Inputs

## Outputs

## Definition of f_theta

Show the mathematical mapping to the original equation.

## Parameter / model-size target

Do not invent exact numbers without justification.

## Training target

## Training objective / loss

## Label construction

## Inference procedure

Step by step.

## How U is estimated

## How C is incorporated

## How network/system state is incorporated

## How Split-LLM fits

## How a new model is added

## Whether retraining is required

## Calibration method

## Expected router overhead

## Hardware needed for training

## Hardware needed for inference

## Software dependencies

## Existing open-source components

## Closest primary research

## What we borrow from prior work

## What is our proposed implementation choice

## Main technical risk

## What would falsify this approach

## SIGCOMM relevance

## Implementation difficulty

LOW / MEDIUM / HIGH

## Implementation sequence

Detailed numbered implementation steps.

Do not estimate calendar duration unless supported by evidence.

======================================================================
17. COMPARE CANDIDATES WITHOUT PREMATURELY CHOOSING
======================================================================

Produce a matrix comparing all serious candidates across:

- fidelity to original paper;
- lightweight edge feasibility;
- query understanding;
- system awareness;
- routing latency;
- memory footprint;
- training complexity;
- label complexity;
- inference complexity;
- calibration support;
- adaptability;
- new-model integration;
- Split-LLM compatibility;
- interpretability;
- ability to exploit changing network conditions;
- SIGCOMM/networked-systems relevance;
- reproducibility;
- dependence on unavailable code;
- required GPU resources;
- overall implementation risk.

Do NOT simply declare a winner.

Instead identify:

- strongest conservative option;
- strongest higher-risk option;
- strongest option closest to the title/original TLM concept.

These are categories for discussion, NOT final advisor-independent decisions.

======================================================================
18. MINIMUM METHOD-SELECTION EXPERIMENT
======================================================================

Design the smallest fair experiment that could help select between candidate
methods AFTER the advisor approves moving to implementation.

Do NOT run it during this sprint.

Specify:

- datasets;
- model pair;
- label generation;
- simple baselines;
- learned candidates;
- calibration;
- 5-seed protocol if appropriate;
- in-domain testing;
- domain-shift testing;
- statistical tests;
- routing overhead measurement.

The experiment should help answer:

H1:
Does a learned router provide enough value over simple baselines?

H2:
Does a generative Tiny-LM provide enough benefit over a smaller
discriminative/utility-prediction approach to justify its additional cost?

H3:
When the Split-LLM system is eventually available, does query-aware routing
provide value beyond a systems-only rule?

These are experimental questions, not assumed truths.

======================================================================
19. REQUIRED DELIVERABLES
======================================================================

Create a new directory:

methods/

Create ALL of the following files.

----------------------------------------------------------------------
methods/00-scope-lock.md
----------------------------------------------------------------------

Exact summary of:

- original paper problem;
- original objective;
- original architecture;
- original constraints;
- elements that are fixed;
- elements the advisor allows us to choose.

End with a checklist:

"Would this proposed method still be the original paper?"

----------------------------------------------------------------------
methods/01-method-landscape.md
----------------------------------------------------------------------

Primary-source review of relevant method families.

Organize by:

- generative routers;
- discriminative routers;
- capability/utility prediction;
- hidden-state/prefill routing;
- structured decision models;
- adaptive model-selection methods;
- system-aware edge/cloud routing.

Include source URLs, venue/year, and code availability.

----------------------------------------------------------------------
methods/02-candidate-methods.md
----------------------------------------------------------------------

Produce 3–5 serious candidate methods.

Use the full candidate template.

At least:

- one method faithful to the Tiny-LM concept;
- one lightweight encoder/micro-encoder approach;
- one model-conditioned utility/system-cost approach.

Include a Jacobi-based router adaptation only if technically defensible.

----------------------------------------------------------------------
methods/03-method-comparison.md
----------------------------------------------------------------------

Detailed matrix comparing candidate methods.

Do not declare a final winner.

Clearly describe trade-offs.

----------------------------------------------------------------------
methods/04-jacobi-role.md
----------------------------------------------------------------------

Deep technical analysis of Jacobi Forcing and the phrase:

"Jacobi-Forced Micro-Encoder"

Clearly separate:

ESTABLISHED
PROPOSED
UNRESOLVED
UNSUPPORTED

Include primary paper and official repository.

End with specific questions for the advisor.

----------------------------------------------------------------------
methods/05-jev-and-decision-models.md
----------------------------------------------------------------------

Analyze Jev/System One only as architectural inspiration.

Then map the relevant principles to open academic methods that could actually
be implemented.

----------------------------------------------------------------------
methods/06-label-and-training-design.md
----------------------------------------------------------------------

Compare:

- binary classification;
- multiclass;
- utility regression;
- pairwise gain;
- direct utility-cost;
- separated utility and measured system cost.

Recommend what should be DISCUSSED with the advisor, without pretending the
choice has already been approved.

----------------------------------------------------------------------
methods/07-system-cost-integration.md
----------------------------------------------------------------------

Compare S1-S4 system-state approaches.

Include mathematical formulations.

Show explicitly how each maps to:

U - lambda*C.

----------------------------------------------------------------------
methods/08-experiment-design.md
----------------------------------------------------------------------

Detailed experiment plan for evaluating the original paper after a method is
chosen.

Include:

- datasets;
- label generation;
- routers;
- baselines;
- quality metrics;
- routing metrics;
- networking metrics;
- latency;
- throughput;
- cost;
- statistics;
- ablations;
- falsification criteria.

----------------------------------------------------------------------
methods/09-implementation-roadmaps.md
----------------------------------------------------------------------

For EACH viable candidate:

PHASE A:
data preparation

PHASE B:
label generation

PHASE C:
router implementation

PHASE D:
training

PHASE E:
calibration

PHASE F:
offline evaluation

PHASE G:
edge deployment

PHASE H:
Split-LLM integration

PHASE I:
network/system experiments

PHASE J:
paper results generation

Give actual technical steps, dependencies, file/module suggestions, and
verification checks.

Do NOT execute them.

----------------------------------------------------------------------
methods/10-lab-requirements.md
----------------------------------------------------------------------

Exact hardware/software/network requirements.

Include:

MINIMUM viable setup

PREFERRED setup

IDEAL experimental setup

And the advisor lab-access questions.

----------------------------------------------------------------------
methods/11-advisor-questions.md
----------------------------------------------------------------------

Organize into:

A. architecture questions
B. Jacobi questions
C. model-pool questions
D. data questions
E. Split-LLM questions
F. lab/hardware questions
G. networking questions
H. SIGCOMM/venue questions
I. success-criteria questions

Prioritize the top 10 questions.

----------------------------------------------------------------------
methods/12-method-proposal.md
----------------------------------------------------------------------

This is the MAIN document for next week's advisor meeting.

Keep it concise and readable.

Structure:

1. Fixed research objective
2. What is currently missing
3. Candidate Approach A
4. Candidate Approach B
5. Candidate Approach C
6. Comparison
7. Proposed minimum experiment to choose between them
8. Hardware/lab requirements
9. SIGCOMM relevance
10. Decisions needed from advisor

Do NOT present a method as already approved.

----------------------------------------------------------------------
methods/13-presenter-notes.md
----------------------------------------------------------------------

Plain-English speaking notes.

Include:

- 60-second explanation of the original problem;
- 30-second explanation of why the method is still undecided;
- 60-second explanation of each candidate;
- pros/cons;
- likely professor questions;
- simple answers;
- explanation of what hardware is needed;
- explanation of what I plan to do after advisor approval.

Write for a Master's student who understands software engineering/CS but is
new to this particular LLM routing research area.

----------------------------------------------------------------------
methods/14-sigcomm-fit.md
----------------------------------------------------------------------

Research the fit of the ORIGINAL project to ACM SIGCOMM.

Include:

1. Confirmed current SIGCOMM 2027 information.
2. What is not yet announced.
3. Why this project can be a networked-systems project.
4. Which parts risk looking like only an ML paper.
5. What system experiments are necessary.
6. Required networking baselines.
7. Required system measurements.
8. Reproducibility expectations inferred only from official/recent sources.
9. Potential reviewer concerns.
10. How to address them WITHOUT changing the original research question.

----------------------------------------------------------------------
methods/15-sigcomm-experiment-matrix.md
----------------------------------------------------------------------

Create a concrete matrix:

METHOD
x
QUERY TYPE
x
NETWORK CONDITION
x
EXECUTION PATH
x
METRICS

Include possible conditions such as:

Query:
- easy/hard;
- short/long;
- domain strata.

Network:
- low/medium/high bandwidth;
- low/medium/high RTT;
- contention if justified.

Execution:
- local SLM;
- Split-LLM;
- cloud/strong path where original architecture supports it.

Metrics:
- quality;
- route selection;
- TTFT;
- TPOT;
- p50/p95 latency;
- throughput;
- bytes transmitted;
- compute;
- memory;
- cost;
- energy if measurable.

----------------------------------------------------------------------
methods/16-next-week-action-plan.md
----------------------------------------------------------------------

Create a very practical document titled:

"What I should do between now and the advisor decision"

Separate into:

CAN DO NOW WITHOUT LAB:
- literature reading;
- codebase inspection;
- dataset preparation;
- environment preparation;
- baseline code planning;
- reproducibility setup.

WAIT FOR ADVISOR:
- final method selection;
- model pool;
- edge hardware;
- server hardware;
- Split-LLM framework;
- network testbed;
- compute budget.

AFTER LAB ACCESS:
give the first 10 concrete implementation steps.

======================================================================
20. SOURCE QUALITY
======================================================================

Prioritize:

1. peer-reviewed primary paper;
2. official conference proceedings;
3. official arXiv paper;
4. official author GitHub repository;
5. official model/project documentation;
6. company documentation only for proprietary systems such as Jev.

Avoid relying on:

- search snippets;
- AI summaries;
- SEO articles;
- uncited blogs;
- generated GitHub content from this repository as evidence of external prior
  work.

Important:

A search result pointing back to THIS repository is NOT independent evidence.

Verify claims against external primary sources.

For every important method claim record:

- title;
- authors;
- venue/year;
- URL/DOI/arXiv;
- code URL if available;
- what the source actually supports.

======================================================================
21. HONESTY / REPRODUCIBILITY RULES
======================================================================

Never fabricate:

- citations;
- paper titles;
- authors;
- model names;
- code availability;
- hardware requirements claimed by a paper;
- benchmark numbers;
- experimental results;
- implementation status.

Clearly label statements as:

VERIFIED
PROPOSED
UNRESOLVED

where appropriate.

Do not turn proposed experiments into completed experiments.

Do not state that code was run when it was not.

Do not modify the original manuscript.

======================================================================
22. FINAL CONTRARIAN REVIEW
======================================================================

Before stopping, conduct Reviewer Pass A:

"For each candidate, does it still solve the exact problem defined in
source/main-original.tex?"

Reject or rewrite candidates that change the research question.

Conduct Reviewer Pass B:

"Could this realistically be implemented by a Master's student using a
university lab?"

Mark unresolved dependencies.

Conduct Reviewer Pass C:

"Would the eventual evidence demonstrate a networked-system effect, or merely
router classification accuracy?"

Flag weak SIGCOMM fit.

Conduct Reviewer Pass D:

"Have we accidentally treated AI-generated content from this repository as an
external source?"

Remove any such evidence.

======================================================================
23. FINAL SUMMARY
======================================================================

Create:

methods/FINAL-SUMMARY.md

It should answer, in plain English:

1. What problem are we still solving?
2. What are the 3 strongest method options?
3. How does each work?
4. What does each require?
5. What are the most important differences?
6. What should be asked of the advisor before choosing?
7. What hardware do we need?
8. What can be done before lab access?
9. What begins immediately after method approval?
10. What evidence will ultimately be needed for the paper?

Do NOT make the advisor's decision.

======================================================================
STOP CONDITION
======================================================================

Stop only when:

- methods/ contains all 18 requested deliverables:
  00 through 16 plus FINAL-SUMMARY.md;

- at least 3 serious method candidates have been investigated;

- at least 2 candidates remain technically viable;

- every viable candidate maps explicitly to the original R(q) and
  U - lambda*C formulation;

- the original manuscript has NOT been modified;

- no large training run has been executed;

- no experimental result has been invented;

- Jacobi Forcing has been checked against primary sources;

- Jev has been treated as inspiration rather than a reproducible open method;

- SIGCOMM 2027 fit has been investigated without inventing unpublished 2027
  requirements;

- lab GPU, network, edge-device, storage, software and measurement requirements
  are explicit;

- the next advisor meeting can be conducted using methods/12-method-proposal.md
  and methods/13-presenter-notes.md;

- a concrete post-approval implementation roadmap exists for every viable
  candidate.
EOF