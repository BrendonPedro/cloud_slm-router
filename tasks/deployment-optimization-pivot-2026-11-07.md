# Deployment Optimization Pivot Research Sprint — 2026-11-07

## Purpose

The semantic-routing investigation has reached a stopping point.

Controlled evidence now shows:
- direct winner/utility prediction is weak;
- task recognition + lookup captures most recoverable semantic-routing value;
- the factored task-prior + residual router failed its decisive pair-level test;
- on the heterogeneous 20-model pool, query-level semantic routing showed NO HEADROOM over a predicted-task lookup;
- cost-aware query-level routing was only MARGINAL;
- TF-IDF + LinearSVC performs task recognition almost as well as the 7B GTE embedding.

Film has explicitly said that if intelligent routing does not work well enough,
the paper should change its main problem to deployment optimization, with the
router treated as one component.

Your job is to determine exactly what that deployment-optimization paper should be.

Do NOT merely rewrite the existing GO-PIVOT report.
Do NOT assume the current proposed deployment formulation is novel or correct.
Challenge it.

## Source priority

1. New controlled results in this repo and ~/research/LLMRouterBench
2. decision/GO-PIVOT-REPORT.md and E1/E2/E3
3. revised paper and current project mission
4. fresh primary literature
5. older architecture/design notes

Never let old proposed architecture override new controlled evidence.

## Current system frame

The eventual system has three execution choices:

EDGE:
local SLM execution

SPLIT:
a stronger model partitioned across edge/server

REMOTE:
server/cloud execution

Keep two layers separate:

1. semantic/model utility:
   what model or model family is appropriate for this workload/task?

2. systems execution:
   given the model, hardware, network and live state,
   should it run Edge, Split or Remote?

Semantic routing is now a lightweight component, not assumed to be the paper's
main contribution.

## Central research question

Can the paper make a defensible and novel systems contribution by jointly
optimizing model selection / task routing with Edge, Split and Remote execution
under measured latency, energy, memory and network constraints?

If not, say so.

## Critical requirement

Do NOT assume SPLIT is useful.

The first systems experiment must establish whether split execution:
- preserves model output quality,
- is technically feasible for the selected architecture,
- and has any latency / bandwidth / energy regime where it can plausibly beat
  pure EDGE or REMOTE execution.

If this premise fails, the optimizer must not include Split merely because the
paper originally proposed it.

## Research tasks

### A. Verify novelty first

Conduct a fresh primary-source literature review focused on 2025–2026 work.

At minimum investigate:

- RouterWise
- BOute
- Mix-or-Split
- edge-cloud collaborative LLM inference
- split LLM inference
- pipeline/model partitioning across edge and cloud
- layer-wise split placement
- network-aware LLM serving
- energy-aware LLM serving
- joint routing + placement
- joint model selection + serving optimization
- adaptive offloading
- heterogeneous edge/cloud inference
- SLO-aware model serving
- activation-transfer optimization
- early-exit / cascade systems where relevant

Search beyond this list.

For important claims, read the actual paper or authoritative primary source,
not only snippets.

For every central paper record:
- title
- venue / year
- URL
- date read
- system setting
- decision variables
- objective
- hardware
- whether it includes Edge
- whether it includes Split
- whether it includes Remote/cloud
- whether it jointly optimizes routing and placement
- whether it models activation-transfer cost
- what remains different from our proposed system

Explicitly read Mix-or-Split before making a novelty claim.

### B. Attack the proposed contribution

Current tentative proposal:

task recognizer
  -> model/task utility table
  -> execution profiles + live state
  -> optimizer
  -> EDGE / SPLIT / REMOTE

Possible decision variables include:
- chosen model
- execution path
- model placement
- split depth
- memory allocation
- batch/resource allocation
- bandwidth / link state

Possible objectives include:
- utility / quality
- p95 latency
- energy
- memory
- bandwidth
- monetary cost

Do NOT automatically keep all of them.

Determine the MINIMUM formulation that is:
1. novel,
2. experimentally defensible,
3. feasible to implement this semester,
4. clearly motivated by our semantic-routing results.

Compare at least THREE materially different systems formulations.

Examples might include, but are not limited to:

A. task-aware joint placement + Edge/Remote selection

B. split-aware Edge/Split/Remote optimizer

C. dynamic execution optimizer using live bandwidth/resource state

These are examples, not required answers.

Reject unnecessary complexity.

### C. Define the actual optimization problem

For the selected formulation, specify mathematically:

- inputs
- decision variables
- constraints
- objective
- offline measurements
- runtime measurements
- what is predicted
- what is looked up
- what is optimized online
- what is optimized offline

Separate model utility from system cost.

Do not hide semantic accuracy inside a vague scalar unless justified.

### D. Define the routing component after the pivot

Use the new evidence honestly.

Determine whether the deployed semantic component should be:

- task lookup with TF-IDF recognizer,
- task/sub-task lookup,
- small encoder only if robustness requires it,
- or something else.

Do not resurrect a sophisticated semantic router without new evidence.

Specify exactly what information it sends to the systems optimizer.

### E. Design E0: Split viability

This is the FIRST hardware/system question.

E0 must answer:

Does splitting the SAME model across edge/server preserve model quality and
produce any useful execution regime relative to Edge-only and Remote-only?

Design the smallest valid E0.

Specify:
- candidate model(s)
- legal split points
- edge hardware
- server hardware
- dataset/query sample
- generation settings
- deterministic controls
- output-quality equivalence criterion
- latency measurement
- activation-transfer volume
- bandwidth sweep or controlled link conditions
- energy if feasible
- repetition count
- pass/fail criterion

Do not run E0 unless the necessary hardware is already locally accessible.
This sprint is primarily research and experimental design.

### F. Hardware plan

We potentially have:
- local desktop / laptop-class edge hardware
- Asus / edge machine
- DGX / server-class hardware

Do not assume exact capabilities without checking repository documentation.

Define:
- minimum hardware required
- what must be measured on each machine
- which measurements can be collected independently
- which require both endpoints simultaneously
- expected experimental matrix

Avoid an enormous benchmark campaign.

### G. Baselines

Select strong, meaningful baselines.

At minimum consider:
- best fixed deployment
- routing with fixed placement
- placement optimization without intelligent routing
- deployment-oblivious routing
- Edge-only
- Remote-only
- Split-only where viable
- relevant RouterWise/BOute/Mix-or-Split-style baseline if implementable

Do not create weak strawman baselines.

### H. Falsification

Pre-register what would make the deployment pivot fail.

Examples:
- Split has no useful regime.
- Joint optimization does not outperform independent routing + placement.
- Network state does not materially change the optimal path.
- The selected formulation duplicates existing work.
- Gains disappear under realistic hardware measurements.

State what the paper becomes if the systems hypothesis fails.

## What NOT to do

- Do not run more semantic classifier sweeps.
- Do not revisit Jacobi.
- Do not rent GPUs.
- Do not start a large hardware benchmark suite.
- Do not optimize code before the problem is defined.
- Do not claim novelty from unread papers.
- Do not use search snippets as final evidence when the paper is accessible.
- Do not force Split into the design.
- Do not change the semantic-routing experimental conclusions.

## Deliverables

Create:

deployment-pivot/LIT-REVIEW.md
deployment-pivot/PROBLEM-FORMULATION.md
deployment-pivot/E0-SPLIT-VIABILITY.md
deployment-pivot/BASELINES.md
deployment-pivot/HARDWARE-PLAN.md
deployment-pivot/GO-NOGO-REPORT.md
deployment-pivot/WEEK-EXECUTION-PLAN.md

GO-NOGO-REPORT.md must answer:

1. What exactly is the new paper problem?
2. Why is it not already solved by RouterWise, BOute, Mix-or-Split, or another
   recent paper?
3. What is our single main contribution?
4. What role does the lightweight router now play?
5. Is Split actually necessary to the contribution?
6. What is E0?
7. What result makes us abandon Split?
8. What result makes us abandon the entire deployment-optimization thesis?
9. What is the minimum experiment set needed for a paper?
10. What should Brendon physically do next?

WEEK-EXECUTION-PLAN.md must prioritize work by information gain, not by how easy
it is to run.

The first 2–3 days should resolve the highest-risk assumptions before any large
benchmarking effort.

## Final decision standard

Do not stop because a plausible architecture has been written down.

Stop only when:

- the important competing 2025–2026 papers have been checked against primary
  sources;
- Mix-or-Split has been read;
- at least three materially different deployment formulations were compared;
- one formulation was selected or all were rejected;
- the exact novelty gap is stated;
- the optimization problem is explicit;
- E0 has frozen pass/fail criteria;
- the required hardware measurements are known;
- strong baselines are selected;
- the deployment thesis itself has a falsification criterion;
- and there is a concrete GO / MODIFY / ABANDON recommendation.

Do not optimize for document length.
Optimize for making the next research decision correctly and quickly.

