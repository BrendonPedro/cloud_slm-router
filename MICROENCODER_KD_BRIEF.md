# MICROENCODER_KD_BRIEF.md

# Deep-Dive Research Brief:
# Distilled Micro-Encoder Router for Edge SLM / Split-LLM Collaborative Inference

## 0. Purpose of this sprint

This sprint follows an advisor meeting on 2026-10-01.

The research problem is FIXED and must not be changed.

The advisor has now selected the MICRO-ENCODER family as the main proposed
router direction.

This sprint must therefore STOP comparing A/B/C as equal candidate methods.

The goal is now to define, source, stress-test, and document one technically
defensible micro-encoder-based routing architecture that can be inserted into
the original manuscript's Proposed Solution section.

The sprint must also investigate KNOWLEDGE DISTILLATION as a possible way to
further optimize the micro-encoder.

Continual learning is NOT part of the core conference method at this stage.
It should be investigated separately as a possible JOURNAL EXTENSION.

No large-scale model training or expensive experiments should be run in this
sprint.

This is a research/design sprint.

---

# 1. Authoritative source and scope lock

The authoritative research problem remains the original manuscript:

`source/main-original.tex`

Do not change its research question.

The fixed routing formulation is:

R : Q -> M

max_R E_q [ U(R(q), q) - lambda C(R(q), q) ]

R(q) = argmax_{M_k in M} f_theta(q, M_k)

The proposed method must remain an implementation of f_theta.

The fixed requirements from the original paper remain:

1. lightweight router
2. query understanding
3. system awareness
4. adaptability/generalization
5. edge deployment
6. routing among edge SLM / Split-LLM / stronger remote execution paths

Do not redefine the research problem as generic scheduling, generic
classification, or generic model selection.

---

# 2. Advisor decisions from 2026-10-01

Treat the following as meeting decisions unless marked unresolved.

CONFIRMED:

1. Use a MICRO-ENCODER as the proposed routing backbone.

2. Keep learned semantic/model utility separate from measured live system cost.

   Candidate form:

   U_hat(a | q)

   combined at runtime with:

   C(a | s)

   using a decision such as:

   argmax_a [ U_hat(a|q) - lambda C(a|s) ]

3. A Split-LLM implementation/codebase exists in the lab.
   Henry has code that may be reused.

4. Lab GPU resources are available.

5. Two-machine use appears available.

6. Candidate C / edge-SLM hidden-state routing may be used as a BASELINE or
   comparison, not the main proposed architecture.

7. The advisor explicitly suggested investigating KNOWLEDGE DISTILLATION to
   further optimize the micro-encoder because micro-encoder/router work likely
   already exists.

8. CONTINUAL LEARNING should be investigated as additional work for a possible
   JOURNAL submission/extension, not automatically added to the conference core.

9. The manuscript should be updated with:
   - overall architecture figure
   - detailed Proposed Solution
   - proposed method clearly highlighted in BLUE

10. Jacobi is NOT a required component of the proposed method.

UNRESOLVED / DO NOT GUESS:

- exact edge GPU model
- exact server GPU model
- exact machine names
- exact Split-LLM repository/codebase from Henry
- exact bandwidth/RTT-control permissions
- exact edge SLM / strong model pool
- exact meaning of advisor discussion involving B1 / SLM choice / possible
  Gemma model
- exact conference vs journal submission sequencing

Do not invent any of these.

---

# 3. Main research question for this sprint

Given the fixed paper objective, what should the exact MICRO-ENCODER implementation
of f_theta be?

More specifically:

How can we build a lightweight micro-encoder router that predicts model/path
utility for each query, combine that prediction with measured runtime system
cost, and improve the router using a technically justified knowledge-distillation
scheme without changing the original research objective?

---

# 4. Required investigation A:
# What micro-encoder / encoder routing work already exists?

Perform a focused prior-art review of encoder-based or lightweight discriminative
LLM routers.

At minimum investigate, where primary sources exist:

- RouteLLM
- RouterDC
- BEST-Route
- HyDRA
- LLMRouterBench
- RouteLMT
- ConsRoute
- Arch-Router only as a generative comparison
- PRISM where relevant
- any newer encoder-router work directly relevant to this method

For each work record:

- exact title
- authors
- venue / arXiv status
- year
- DOI / arXiv / official URL
- official code repository if available
- router architecture
- router parameter size
- input representation
- output / target
- training labels
- training loss
- calibration approach
- model-pool adaptability
- runtime/system-state integration
- edge deployment evidence
- Split-LLM relationship
- whether knowledge distillation is used
- whether continual learning is used
- what is actually novel in that paper

Primary sources are mandatory for load-bearing claims.

Do not cite blog posts when a paper or official repository exists.

---

# 5. Required investigation B:
# Knowledge distillation for routing

Investigate whether knowledge distillation has already been applied to:

- LLM routing
- model selection
- mixture-of-model routing
- selective prediction
- edge/cloud routing
- lightweight query classifiers
- capability prediction
- model utility prediction

Separate:

ESTABLISHED:
direct prior work that actually uses knowledge distillation for a comparable
routing/model-selection task.

RELATED:
knowledge distillation methods from adjacent areas that could reasonably be
adapted but are not established LLM-routing methods.

PROPOSED:
our own design adaptations.

Do not blur these categories.

Answer:

1. Has distillation already been used for LLM routers?
2. If yes, exactly what was distilled?
3. What acted as the teacher?
4. What acted as the student?
5. Were hard labels, logits, probabilities, rankings, embeddings, hidden states,
   or pairwise preferences distilled?
6. What loss was used?
7. Was temperature scaling used?
8. What size reduction / latency reduction was measured?
9. Did quality degrade?
10. Was the student deployed on edge hardware?
11. Did the work include live network/system cost?
12. Did it involve Split-LLM execution?

---

# 6. Required investigation C:
# Candidate distillation formulations

Develop and compare several technically valid KD formulations for OUR fixed
micro-encoder router.

At minimum consider:

KD-1: Soft utility-vector distillation

Teacher outputs a probability/utility vector over execution paths.

Student learns:

p_student(a|q)

from:

p_teacher(a|q)

plus ground-truth model outcome labels.

Possible conceptual loss:

L = alpha * L_task
  + beta * T^2 * KL(
        softmax(z_teacher / T)
        ||
        softmax(z_student / T)
    )

Do not assume this is the final loss.
Verify it against established KD literature.

KD-2: Pairwise/ranking distillation

Teacher provides relative preference:

M_i > M_j for q

Student learns route ordering rather than only class labels.

KD-3: Utility regression distillation

Teacher estimates per-model utility:

U_teacher(M_k | q)

Student regresses toward those utility estimates.

KD-4: Representation distillation

Student encoder learns from a larger teacher representation/embedding.

KD-5: Hybrid hard-label + soft-teacher supervision

Student learns from both:

- actual per-query/per-model outcomes
- teacher soft targets

For each formulation compare:

- fidelity to original f_theta
- simplicity
- student inference cost
- label requirements
- teacher requirements
- calibration
- model-pool flexibility
- compatibility with runtime C(a|s)
- compatibility with Split-LLM
- implementation risk
- novelty risk
- reproducibility
- likely edge feasibility

The sprint MAY recommend one formulation if the evidence supports it.

Do not manufacture novelty.

---

# 7. Teacher design investigation

Do not simply assume "use a big LLM as teacher."

Investigate possible teacher designs:

T1. Larger encoder router

T2. Generative LLM router

T3. Ensemble of model-outcome predictors

T4. Oracle constructed from actual per-query model outcomes

T5. Strong model / judge-generated utility labels

T6. Existing released router used as teacher

For each, explain:

- what the teacher sees
- what it predicts
- what supervision it requires
- whether using it would leak evaluation information
- whether it is reproducible
- whether it creates circular labels
- whether licensing/terms permit distillation
- whether the teacher is needed only during training
- expected compute requirements

The final proposed system must remain lightweight AT INFERENCE.

---

# 8. Student micro-encoder architecture

Investigate realistic student backbones.

Do not automatically select a model because it is popular.

Compare suitable classes such as:

- MiniLM-scale encoders
- DeBERTa-v3-small class
- ModernBERT class
- other current lightweight encoder models found in primary literature

For each candidate record:

- parameter count
- hidden dimension
- sequence length
- licensing
- released checkpoints
- CPU latency evidence if available
- GPU latency evidence if available
- ONNX / quantization suitability
- training resource requirements
- whether architecture supports multi-head utility outputs cleanly

Propose a sensible student SIZE RANGE and a primary implementation candidate,
but clearly mark anything that still requires empirical ablation.

---

# 9. Exact f_theta definition

The sprint must produce an explicit mathematical definition for the proposed
micro-encoder.

The definition must map back to:

R(q) = argmax_{M_k in M} f_theta(q, M_k)

A preferred design may use:

f_theta(q, M_k) = U_hat_theta(M_k | q)

with:

R(q,s) =
argmax_a [
    U_hat_theta(a|q)
    - lambda C(a|s)
]

If action a differs from model M_k because split depths are actions, explain
the notation carefully.

Do not silently change the original equation.

If an extension of notation is needed, explicitly show how it reduces to the
original manuscript formulation.

---

# 10. Training labels

Define exactly how training data can be created.

Distinguish:

- true observed utility
- binary correctness
- benchmark-specific score
- judge score
- teacher-predicted utility
- soft teacher target
- final route label

Investigate whether the core student should predict:

A. binary edge sufficiency
B. multiclass route
C. per-model utility
D. pairwise preference
E. calibrated probability of success

Explain which is most consistent with the original formulation and why.

Do not treat illustrative "good/medium/poor" labels as an experimental definition.

---

# 11. System-cost integration

Keep system cost OUTSIDE the student weights unless strong evidence shows
otherwise.

Define:

C(a | s)

where system state s may include:

- bandwidth
- RTT
- contention
- activation-transfer size
- edge compute latency
- server compute latency
- TTFT
- TPOT
- memory/resource pressure
- operational cost

Investigate practical scalarization options.

Do not blindly add milliseconds + bytes + dollars.

Compare:

S1. normalized weighted scalar cost

S2. latency as online routing penalty, other metrics reported separately

S3. constrained optimization:
    maximize quality subject to latency/bytes/budget threshold

S4. Pareto-front evaluation without forcing all metrics into one number

Recommend a conference-core approach if evidence supports one.

---

# 12. Split-LLM integration

The proposed method must work with a REAL Split-LLM implementation.

Do not treat Split as only a fake cloud API.

Document what is needed from Henry's code:

- model supported
- split-layer interface
- client/server partition
- activation tensor shape
- activation transfer mechanism
- serialization
- network protocol
- server runtime
- edge runtime
- supported hardware
- logging hooks
- TTFT measurement
- TPOT measurement
- bytes transferred
- split-depth control
- batching
- quantization
- repository/license

Produce a checklist to use when Henry provides the code.

Do not guess missing details.

---

# 13. Model-pool design

The advisor indicated that the model-pool question was largely answered during
the presentation, but the student's handwritten notes are incomplete.

Therefore:

- inspect the original manuscript's proposed model pool
- verify every named model exists
- verify parameter sizes and official model names
- flag stale or invalid names
- propose MODEL-SELECTION CRITERIA rather than inventing an advisor decision

Criteria should consider:

- meaningful capability gap
- edge feasibility
- strong-model headroom
- Split compatibility
- licensing
- open weights
- reproducibility
- GPU memory
- inference cost
- enough oracle headroom for routing to matter

Investigate whether too many SLMs make the routing problem unnecessarily complex.

Do not claim an exact final pool unless the evidence/advisor record supports it.

---

# 14. Baselines

The main proposed method is the distilled micro-encoder.

Candidate C / hidden-state self-routing should now be evaluated as a baseline
or comparison.

The baseline plan should include where appropriate:

- TF-IDF + Logistic Regression
- Always-Edge
- Always-Strong/Cloud
- Always-Split
- Random
- Dataset prior
- System-state-only scheduler
- Standard non-distilled micro-encoder
- Hidden-state probe / self-routing SLM (Candidate C)
- relevant published encoder router
- relevant published generative router
- oracle upper bound

Explain what question each baseline answers.

---

# 15. Novelty stress test

The sprint must answer:

What, exactly, could be new here?

Do NOT claim:

"micro-encoder routing is novel"

unless primary literature proves that.

Possible contribution axes to investigate:

N1. Distillation method specifically optimized for utility-aware LLM routing.

N2. Distillation that preserves calibrated per-model utility while greatly
    reducing router size/latency.

N3. Separation of distilled semantic utility prediction from live measured
    edge/Split system cost.

N4. Genuine Split-LLM systems evaluation with measured activation transfer.

N5. Distilled router + network-adaptive decision layer.

N6. Edge deployment / quality-latency-communication trade-off not previously
    measured for comparable routers.

For every possible novelty claim:

- search for closest prior work
- cite the primary source
- state overlap
- state what would need to be experimentally demonstrated
- downgrade or reject the claim if already occupied

No novelty by adjective.

---

# 16. Conference-core architecture

Produce one coherent proposed architecture for the conference paper.

It should include:

TRAINING PHASE

queries
   |
   +--> actual per-model outcome labels
   |
   +--> teacher router/model
             |
             v
       soft utility targets
             |
             v
       student micro-encoder
             |
        KD + task loss

INFERENCE PHASE

query q
   |
   v
student micro-encoder
   |
   v
U_hat(a | q)
   |
   + live measured C(a | s)
   |
   v
argmax [ U_hat - lambda C ]
   |
   +--> EDGE
   +--> SPLIT(d)
   +--> STRONG/CLOUD

Clearly distinguish:

- training-only components
- inference-time components
- learned values
- measured values
- optional components

Produce:
1. text description
2. ASCII diagram
3. publication-quality figure specification
4. if practical, LaTeX/TikZ figure source

Do not claim measured improvements.

---

# 17. Conference experiment plan

Design the MINIMUM experiment set needed to evaluate the proposed method.

The experiment must distinguish:

E1. standard micro-encoder vs distilled micro-encoder

E2. distilled micro-encoder vs simple baselines

E3. distilled micro-encoder vs hidden-state baseline

E4. teacher vs student:
    quality / calibration / parameter count / latency

E5. route quality under changing lambda

E6. route changes under changing bandwidth / RTT

E7. measured Edge vs Split execution:
    TTFT
    TPOT
    e2e p50/p95/p99
    activation bytes
    throughput
    GPU utilization
    memory
    operational cost if defensible

E8. domain-shift/generalization evaluation

For each experiment define:

- hypothesis
- independent variable
- dependent variable
- baseline
- success criterion
- falsification criterion
- hardware requirement
- data requirement

Do NOT run these experiments during this sprint.

---

# 18. Journal-extension track:
# Continual learning

Keep this separate from the conference core.

Investigate continual-learning approaches applicable to the router after
deployment.

Research questions:

- What happens when the edge SLM changes?
- What happens when a new strong model is added?
- What happens when query domains shift?
- Can the router update without full retraining?
- How do we avoid catastrophic forgetting?

Investigate relevant methods such as:

- replay buffers
- rehearsal
- regularization-based continual learning
- adapter-based updates
- online distillation
- teacher-student refresh
- continual calibration
- model-profile updates

Primary-source check all methods.

Produce a JOURNAL EXTENSION PLAN containing:

- motivation
- method options
- additional experiments
- additional contribution beyond conference version
- dependencies on conference architecture

Do not silently put continual learning into the conference architecture.

---

# 19. Publication staging

Do not assume the exact submission order.

Produce two plans:

PLAN A:
Conference core first, then journal extension with continual learning.

PLAN B:
Parallel preparation where journal experiments begin while conference paper is
under preparation/review.

For each state:

- benefits
- risks
- code reuse
- experimental overlap
- what must remain novel/additional in the journal version
- what advisor decision is needed

Do not invent venue deadlines.

---

# 20. Manuscript-ready blue text

Do NOT directly overwrite `source/main-original.tex`.

Create a standalone draft:

`methods-v2/proposed-solution-blue.tex`

It must contain manuscript-ready LaTeX for:

- Proposed Solution overview
- micro-encoder architecture
- definition of f_theta
- knowledge-distillation training
- utility prediction
- runtime cost integration
- inference routing rule
- Split-LLM integration
- training algorithm description
- inference algorithm description
- limitations / design assumptions if appropriate

Wrap newly proposed manuscript prose using an explicit blue convention, for
example:

\textcolor{blue}{...}

or define a macro if cleaner.

Do not invent results.

Do not write:
"experiments demonstrate"
"we outperform"
"our method achieves"

unless actual results exist.

---

# 21. Architecture figure

Create:

`methods-v2/architecture-figure-spec.md`

and if practical:

`methods-v2/architecture-figure.tex`

The figure must clearly show:

TRAINING:
teacher + observed outcomes -> distilled student

INFERENCE:
query -> micro-encoder -> utility
plus
live system state -> cost
then
decision -> Edge / Split / Strong

Use different visual treatment for:

- learned/training-only path
- inference path
- measured system values

The figure should be suitable for later insertion into the paper.

---

# 22. References

Create:

`methods-v2/verified-references.md`

For every source include:

- exact citation
- DOI/arXiv
- venue
- official URL
- official repository URL when available
- what claim it supports
- whether full text was actually inspected
- primary vs secondary source

Also create:

`methods-v2/method-references.bib`

with BibTeX entries for VERIFIED sources only.

Do not fabricate BibTeX.

If a field cannot be verified, omit it or clearly mark unresolved.

---

# 23. Evidence discipline

Use these tags:

[VERIFIED]
primary source directly supports the statement.

[RELATED]
adjacent prior work, not exact precedent.

[PROPOSED]
our design idea.

[OPEN]
requires experiment/advisor confirmation.

[UNSUPPORTED]
claim should not be used.

Any sentence that could become a novelty claim must have a primary-source
basis or be explicitly marked PROPOSED.

---

# 24. Deliverables

Create exactly these files under `methods-v2/`:

00-meeting-decisions-lock.md
01-microencoder-prior-art.md
02-kd-prior-art.md
03-kd-formulations.md
04-teacher-options.md
05-student-architecture.md
06-proposed-method.md
07-training-labels.md
08-system-cost-integration.md
09-split-llm-integration.md
10-model-pool-and-baselines.md
11-novelty-stress-test.md
12-conference-experiment-plan.md
13-journal-continual-learning-extension.md
14-publication-staging.md
15-architecture-figure-spec.md
16-advisor-and-lab-open-questions.md
17-verified-references.md
method-references.bib
proposed-solution-blue.tex
FINAL-SUMMARY.md

If feasible also create:

architecture-figure.tex

Do not modify the original manuscript.

---

# 25. FINAL-SUMMARY requirements

`methods-v2/FINAL-SUMMARY.md` must answer in plain English:

1. What did the advisor approve?
2. What exactly is the proposed micro-encoder architecture?
3. What is f_theta?
4. What does the student predict?
5. What teacher is proposed and why?
6. What exactly is distilled?
7. What training loss is proposed?
8. What remains measured rather than learned?
9. How does Split-LLM enter the system?
10. What is likely already prior art?
11. What potential contribution remains defensible?
12. What would falsify the contribution?
13. What baseline methods are required?
14. What hardware/software details are still unknown?
15. What must be asked of Henry?
16. What belongs in the conference core?
17. What belongs only in the journal continual-learning extension?
18. What manuscript text is ready to insert?
19. Which claims still need advisor approval?
20. What are the next 10 implementation steps after approval?

---

# 26. Hard constraints

DO NOT:

- change the research problem
- return to open-ended A/B/C selection
- make Jacobi a requirement
- claim micro-encoder routing itself is novel without evidence
- assume knowledge distillation is novel
- assume continual learning belongs in the conference paper
- invent hardware names
- invent Henry's code details
- invent final model pool
- run large training jobs
- download huge model checkpoints
- modify source/main-original.tex
- fabricate results
- fabricate references
- fabricate BibTeX
- present estimated latency as measured
- silently turn Split-LLM into a cloud API

DO:

- deeply investigate the approved micro-encoder direction
- verify primary literature
- identify closest prior work
- stress-test KD novelty
- distinguish established vs proposed
- create a precise architecture
- create manuscript-ready blue text
- create verified references/BibTeX
- keep continual learning as a separate journal extension
- identify unresolved advisor/lab questions

---

# 27. Stop condition

Stop when ALL of the following are true:

1. all required deliverables exist;
2. the micro-encoder is specified as an implementable architecture;
3. at least three realistic KD formulations were investigated;
4. one defensible KD formulation is proposed or the evidence concludes KD does
   not add sufficient value;
5. the closest micro-encoder/router prior work has been primary-source checked;
6. the closest KD-for-routing prior work has been primary-source checked;
7. every novelty claim is either sourced or explicitly marked PROPOSED/OPEN;
8. a conference-core architecture is fully specified;
9. continual learning is isolated as a journal extension;
10. a real Split-LLM integration path is specified without inventing Henry's
    missing code details;
11. a baseline and experiment plan exists;
12. verified references and BibTeX exist;
13. manuscript-ready blue Proposed Solution text exists;
14. the architecture figure specification exists;
15. the original manuscript has not been modified;
16. no experimental results have been invented.
