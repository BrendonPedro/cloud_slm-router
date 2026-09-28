Implement and execute Stage 1 of the pre-registered experiment.

Goal:
Determine whether a learned router provides meaningful value beyond
simple baselines before investing in the Split-LLM testbed.

Implement:
1. DeBERTa/ModernBERT discriminative router
2. Tiny generative router
3. simple baselines
4. calibration
5. 5-seed in-domain evaluation
6. leave-one-dataset-out evaluation
7. bootstrap confidence intervals

Use the frozen Stage-0 splits and labels already in the repository.

Do not change hypotheses or thresholds after seeing test results.

Store:
- configs
- seeds
- logs
- checkpoints
- predictions
- raw metrics
- environment information

Generate results tables directly from raw outputs.

Then update main-revised.tex ONLY with results actually produced.

If H1 or H2 fails, document the negative result rather than optimizing
until the hypothesis passes.


Then if Stage 1 indicates the idea is worth continuing, you move to the expensive part:

Stage 2:
real Edge → Split-LLM → Cloud system

And that probably requires discussion with your professor about available GPUs, edge hardware, server access and network setup.