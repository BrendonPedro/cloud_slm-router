# Advisor Review Note

## Purpose

This repository contains my current research work on adaptive routing for
edge, split, and remote LLM inference.

I am sharing the repository at this stage for advisor review of the research
direction, method formulation, and next experimental steps. It should not be
treated as a finalized paper or a validated proposed method.

## Current Manuscript

The current advisor-discussion manuscript is:

`paper/main-revised.tex`

This manuscript is intentionally conservative.

As documented in `paper/README.md`:

- the proposed router has not yet been trained or evaluated;
- the Results and Discussion section remains a placeholder;
- only the Stage-0 baseline measurements currently have experimental evidence;
- planned experiments and unresolved advisor decisions remain marked as TODOs.

The original manuscript is preserved separately at:

`source/main-original.tex`

## Subsequent Method Development

After preparing `paper/main-revised.tex`, I carried out several additional
research and method-development sprints.

The latest material is primarily under:

`methods-v3/`

Useful entry points are:

- `methods-v3/FINAL-SUMMARY-v3.md`
- `methods-v3/proposed-solution-blue-v3.tex`
- `methods-v3/architecture-figure-v3.tex`
- `methods-v3/13-experiments-v3.md`
- `methods-v3/16-citation-audit.md`
- `methods-v3/17-verified-references-v3.md`

These files explore a more specific formulation based on model-level utility,
query-conditioned routing, system cost, and an E0-gated treatment of Split-LLM
execution.

They have not automatically been incorporated into `paper/main-revised.tex`.
I have kept the manuscript separate so that exploratory ideas are not presented
as accepted contributions before advisor review and experimental validation.

## AI / Agentic Workflow Disclosure

A substantial portion of the later method exploration was developed with heavy
assistance from an agentic AI workflow.

I used the workflow to:

- study and organize related literature;
- compare possible routing formulations;
- challenge assumptions and identify weaknesses;
- propose alternative mathematical formulations;
- develop and critique experimental plans;
- inspect citation support;
- iterate on architecture and method descriptions;
- generate candidate research directions for further human review.

Accordingly, the material in `methods-v2/` and `methods-v3/` should be viewed as
AI-assisted research exploration and proposed working hypotheses, not as claims
that I independently established every formulation or that the method has
already been experimentally validated.

My intention in sharing these materials is to be transparent about how they
were developed and to obtain advisor feedback on which parts are scientifically
sound, useful, and worth carrying forward into the manuscript.

## Baseline Training Work

I have also begun the hands-on baseline training work suggested by Film using
LLMRouterBench.

That work is maintained separately in my LLMRouterBench fork:

https://github.com/BrendonPedro/LLMRouterBench

The baseline work currently includes:

- query-level model-pair headroom analysis;
- a TF-IDF + logistic-regression learning baseline;
- reproduction of the AvengersPro semantic-clustering baseline;
- a controlled DeepSeek/Qwen3 comparison;
- multi-seed AvengersPro experiments;
- reproducible scripts and CSV result tables.

The purpose of the baseline work is to understand the benchmark and failure
modes before finalizing the proposed routing method.

## What I Would Most Like Feedback On

At this stage I would especially appreciate feedback on:

1. Whether the model-utility routing formulation is a reasonable direction.
2. Whether separating model utility from execution action is conceptually sound.
3. Whether the E0-gated treatment of Split-LLM is appropriate.
4. Whether knowledge distillation should remain outside the conference core.
5. Which parts of the methods-v3 proposal are worth transferring into the
   revised manuscript.
6. Whether the current baseline experiments are sufficient groundwork before
   implementing the proposed router.

