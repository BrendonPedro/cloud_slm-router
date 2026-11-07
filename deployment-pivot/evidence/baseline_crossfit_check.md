# baseline_crossfit_check.py output (seed 20261107); edge 8B at 40 tok/s; profiles ASSUMED (see joint_vs_sequential_sim.py). 2-fold cross-fit by query.

| SLO s | state | policy | cross-fit U | in-sample U | Δ(F3 − policy) pt | 95% CI |
|---|---|---|---|---|---|---|
| 60 | good | **F3 joint+live** | 0.544 | 0.546 | — | — |
| 60 | good | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | good | B-route|fixed-placement, live (router over home deployments) | 0.528 | 0.533 | +1.7 | [+0.2, +3.1] |
| 60 | good | B-place|no-routing (one model, live path) | 0.531 | 0.531 | +1.3 | [-0.2, +2.8] |
| 60 | good | B-oblivious route -> live path | 0.448 | 0.442 | +9.6 | [+7.1, +12.2] |
| 60 | good | B-dec REMOTE table(live) + edge failover | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | good | B-best fixed deployment | 0.531 | 0.531 | +1.3 | [-0.2, +2.8] |
| 60 | good | Edge-only (best edge model per task) | 0.278 | 0.278 | +26.6 | [+23.5, +30.0] |
| 60 | good | Remote-only (best remote action per task, live) | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | high-RTT | **F3 joint+live** | 0.544 | 0.546 | — | — |
| 60 | high-RTT | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | high-RTT | B-route|fixed-placement, live (router over home deployments) | 0.528 | 0.533 | +1.7 | [+0.3, +3.1] |
| 60 | high-RTT | B-place|no-routing (one model, live path) | 0.531 | 0.531 | +1.3 | [-0.2, +2.9] |
| 60 | high-RTT | B-oblivious route -> live path | 0.448 | 0.442 | +9.6 | [+7.2, +12.4] |
| 60 | high-RTT | B-dec REMOTE table(live) + edge failover | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | high-RTT | B-best fixed deployment | 0.531 | 0.531 | +1.3 | [-0.2, +2.9] |
| 60 | high-RTT | Edge-only (best edge model per task) | 0.278 | 0.278 | +26.6 | [+23.5, +30.0] |
| 60 | high-RTT | Remote-only (best remote action per task, live) | 0.544 | 0.546 | +0.0 | [+0.0, +0.0] |
| 60 | server-contended | **F3 joint+live** | 0.349 | 0.349 | — | — |
| 60 | server-contended | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.307 | 0.316 | +4.2 | [+2.6, +6.0] |
| 60 | server-contended | B-route|fixed-placement, live (router over home deployments) | 0.349 | 0.349 | +0.0 | [+0.0, +0.0] |
| 60 | server-contended | B-place|no-routing (one model, live path) | 0.319 | 0.319 | +3.0 | [+1.3, +4.8] |
| 60 | server-contended | B-oblivious route -> live path | 0.248 | 0.200 | +10.1 | [+7.8, +12.4] |
| 60 | server-contended | B-dec REMOTE table(live) + edge failover | 0.327 | 0.332 | +2.1 | [+1.0, +3.6] |
| 60 | server-contended | B-best fixed deployment | 0.319 | 0.319 | +3.0 | [+1.3, +4.8] |
| 60 | server-contended | Edge-only (best edge model per task) | 0.278 | 0.278 | +7.1 | [+5.2, +8.9] |
| 60 | server-contended | Remote-only (best remote action per task, live) | 0.327 | 0.332 | +2.1 | [+1.0, +3.6] |
| 60 | remote-down | **F3 joint+live** | 0.278 | 0.278 | — | — |
| 60 | remote-down | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.000 | 0.000 | +27.8 | [+25.2, +30.4] |
| 60 | remote-down | B-route|fixed-placement, live (router over home deployments) | 0.278 | 0.278 | +0.0 | [+0.0, +0.0] |
| 60 | remote-down | B-place|no-routing (one model, live path) | 0.000 | 0.000 | +27.8 | [+25.2, +30.4] |
| 60 | remote-down | B-oblivious route -> live path | 0.027 | 0.027 | +25.1 | [+22.5, +27.7] |
| 60 | remote-down | B-dec REMOTE table(live) + edge failover | 0.278 | 0.278 | +0.0 | [+0.0, +0.0] |
| 60 | remote-down | B-best fixed deployment | 0.000 | 0.000 | +27.8 | [+25.2, +30.4] |
| 60 | remote-down | Edge-only (best edge model per task) | 0.278 | 0.278 | +0.0 | [+0.0, +0.0] |
| 60 | remote-down | Remote-only (best remote action per task, live) | 0.000 | 0.000 | +27.8 | [+25.2, +30.4] |
| 300 | good | **F3 joint+live** | 0.709 | 0.723 | — | — |
| 300 | good | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | good | B-route|fixed-placement, live (router over home deployments) | 0.717 | 0.721 | -0.8 | [-2.2, +0.2] |
| 300 | good | B-place|no-routing (one model, live path) | 0.681 | 0.714 | +2.8 | [+1.2, +4.3] |
| 300 | good | B-oblivious route -> live path | 0.709 | 0.719 | +0.0 | [+0.0, +0.0] |
| 300 | good | B-dec REMOTE table(live) + edge failover | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | good | B-best fixed deployment | 0.681 | 0.714 | +2.8 | [+1.2, +4.3] |
| 300 | good | Edge-only (best edge model per task) | 0.551 | 0.556 | +15.8 | [+12.6, +19.3] |
| 300 | good | Remote-only (best remote action per task, live) | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | high-RTT | **F3 joint+live** | 0.709 | 0.723 | — | — |
| 300 | high-RTT | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | high-RTT | B-route|fixed-placement, live (router over home deployments) | 0.717 | 0.721 | -0.8 | [-2.2, +0.2] |
| 300 | high-RTT | B-place|no-routing (one model, live path) | 0.681 | 0.714 | +2.8 | [+1.2, +4.5] |
| 300 | high-RTT | B-oblivious route -> live path | 0.709 | 0.719 | +0.0 | [+0.0, +0.0] |
| 300 | high-RTT | B-dec REMOTE table(live) + edge failover | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | high-RTT | B-best fixed deployment | 0.681 | 0.714 | +2.8 | [+1.2, +4.5] |
| 300 | high-RTT | Edge-only (best edge model per task) | 0.551 | 0.556 | +15.8 | [+12.2, +19.2] |
| 300 | high-RTT | Remote-only (best remote action per task, live) | 0.709 | 0.723 | +0.0 | [+0.0, +0.0] |
| 300 | server-contended | **F3 joint+live** | 0.593 | 0.600 | — | — |
| 300 | server-contended | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.492 | 0.511 | +10.0 | [+7.6, +12.6] |
| 300 | server-contended | B-route|fixed-placement, live (router over home deployments) | 0.593 | 0.600 | +0.0 | [+0.0, +0.0] |
| 300 | server-contended | B-place|no-routing (one model, live path) | 0.546 | 0.557 | +4.6 | [+2.6, +7.1] |
| 300 | server-contended | B-oblivious route -> live path | 0.550 | 0.559 | +4.2 | [+2.3, +6.2] |
| 300 | server-contended | B-dec REMOTE table(live) + edge failover | 0.558 | 0.573 | +3.5 | [+1.8, +5.5] |
| 300 | server-contended | B-best fixed deployment | 0.464 | 0.557 | +12.8 | [+10.0, +15.7] |
| 300 | server-contended | Edge-only (best edge model per task) | 0.551 | 0.556 | +4.2 | [+2.5, +6.0] |
| 300 | server-contended | Remote-only (best remote action per task, live) | 0.558 | 0.573 | +3.5 | [+1.8, +5.5] |
| 300 | remote-down | **F3 joint+live** | 0.551 | 0.556 | — | — |
| 300 | remote-down | F1 joint, state-oblivious (ECO-LLM/2507.15553 static table) | 0.000 | 0.000 | +55.1 | [+51.7, +58.7] |
| 300 | remote-down | B-route|fixed-placement, live (router over home deployments) | 0.551 | 0.556 | +0.0 | [+0.0, +0.0] |
| 300 | remote-down | B-place|no-routing (one model, live path) | 0.285 | 0.000 | +26.6 | [+23.7, +29.5] |
| 300 | remote-down | B-oblivious route -> live path | 0.154 | 0.190 | +39.7 | [+36.8, +42.7] |
| 300 | remote-down | B-dec REMOTE table(live) + edge failover | 0.551 | 0.556 | +0.0 | [+0.0, +0.0] |
| 300 | remote-down | B-best fixed deployment | 0.000 | 0.000 | +55.1 | [+51.7, +58.7] |
| 300 | remote-down | Edge-only (best edge model per task) | 0.551 | 0.556 | +0.0 | [+0.0, +0.0] |
| 300 | remote-down | Remote-only (best remote action per task, live) | 0.000 | 0.000 | +55.1 | [+51.7, +58.7] |
