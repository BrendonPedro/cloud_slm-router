# Output of joint_vs_sequential_sim.py (2026-11-07). All throughputs/RTTs/powers are ASSUMPTIONS; quality and token counts are cached LLMRouterBench data. Utility = mean correctness, counting a late answer as 0.

tasks with all models cached: ['aime', 'gpqa', 'livecodebench', 'livemathbench', 'mmlupro']

deployment-oblivious model per task: {'aime': 'Qwen3-8B', 'gpqa': 'deepseek-v3-0324', 'livecodebench': 'Qwen3-8B', 'livemathbench': 'qwen3-235b-a22b-2507', 'mmlupro': 'qwen3-235b-a22b-2507'} 

| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks whose action differs from state-oblivious |
|---|---|---|---|---|---|---|---|
| 15 | 60 | good | joint+live | 0.546 | 0.742 | 178 | 0 |
| 15 | 60 | good | deadline-aware model table, REMOTE-only, live | 0.546 | 0.742 | 178 |  |
| 15 | 60 | good | deadline-aware model table, REMOTE-only, nominal | 0.546 | 0.742 | 178 |  |
| 15 | 60 | good | joint, remote-down -> edge failover only | 0.546 | 0.742 | 178 |  |
| 15 | 60 | good | joint, state-oblivious | 0.546 | 0.742 | 178 |  |
| 15 | 60 | good | oblivious model -> best path | 0.442 | 0.572 | 261 |  |
| 15 | 60 | good | edge-only best model | 0.220 | 0.683 | 4164 |  |
| 15 | 60 | high-RTT | joint+live | 0.546 | 0.742 | 179 | 0 |
| 15 | 60 | high-RTT | deadline-aware model table, REMOTE-only, live | 0.546 | 0.742 | 179 |  |
| 15 | 60 | high-RTT | deadline-aware model table, REMOTE-only, nominal | 0.546 | 0.742 | 179 |  |
| 15 | 60 | high-RTT | joint, remote-down -> edge failover only | 0.546 | 0.742 | 179 |  |
| 15 | 60 | high-RTT | joint, state-oblivious | 0.546 | 0.742 | 179 |  |
| 15 | 60 | high-RTT | oblivious model -> best path | 0.442 | 0.572 | 262 |  |
| 15 | 60 | high-RTT | edge-only best model | 0.220 | 0.683 | 4164 |  |
| 15 | 60 | server-contended | joint+live | 0.332 | 0.525 | 442 | 2 |
| 15 | 60 | server-contended | deadline-aware model table, REMOTE-only, live | 0.332 | 0.525 | 442 |  |
| 15 | 60 | server-contended | deadline-aware model table, REMOTE-only, nominal | 0.316 | 0.428 | 711 |  |
| 15 | 60 | server-contended | joint, remote-down -> edge failover only | 0.316 | 0.428 | 711 |  |
| 15 | 60 | server-contended | joint, state-oblivious | 0.316 | 0.428 | 711 |  |
| 15 | 60 | server-contended | oblivious model -> best path | 0.185 | 0.223 | 6582 |  |
| 15 | 60 | server-contended | edge-only best model | 0.220 | 0.683 | 4164 |  |
| 15 | 60 | remote-down | joint+live | 0.220 | 0.683 | 4164 | 5 |
| 15 | 60 | remote-down | deadline-aware model table, REMOTE-only, live | 0.000 | 0.000 | 0 |  |
| 15 | 60 | remote-down | deadline-aware model table, REMOTE-only, nominal | 0.000 | 0.000 | 0 |  |
| 15 | 60 | remote-down | joint, remote-down -> edge failover only | 0.220 | 0.683 | 4164 |  |
| 15 | 60 | remote-down | joint, state-oblivious | 0.000 | 0.000 | 0 |  |
| 15 | 60 | remote-down | oblivious model -> best path | 0.004 | 0.004 | 11000 |  |
| 15 | 60 | remote-down | edge-only best model | 0.220 | 0.683 | 4164 |  |

nominal-state joint actions (edge 15 tok/s, SLO 60 s): {'aime': ('qwen3-235b-a22b-2507', 'REMOTE'), 'gpqa': ('qwen3-235b-a22b-2507', 'REMOTE'), 'livecodebench': ('qwen3-235b-a22b-2507', 'REMOTE'), 'livemathbench': ('NVIDIA-Nemotron-Nano-9B-v2', 'REMOTE'), 'mmlupro': ('qwen3-235b-a22b-2507', 'REMOTE')}

| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks differing |
|---|---|---|---|---|---|---|---|
| 15 | 300 | good | joint+live | 0.723 | 0.963 | 247 | 0 |
| 15 | 300 | good | deadline-aware model table, REMOTE-only, live | 0.723 | 0.963 | 247 |  |
| 15 | 300 | good | deadline-aware model table, REMOTE-only, nominal | 0.723 | 0.963 | 247 |  |
| 15 | 300 | good | joint, remote-down -> edge failover only | 0.723 | 0.963 | 247 |  |
| 15 | 300 | good | joint, state-oblivious | 0.723 | 0.963 | 247 |  |
| 15 | 300 | good | oblivious model -> best path | 0.719 | 0.946 | 261 |  |
| 15 | 300 | good | edge-only best model | 0.383 | 0.485 | 19791 |  |
| 15 | 300 | high-RTT | joint+live | 0.723 | 0.963 | 248 | 0 |
| 15 | 300 | high-RTT | deadline-aware model table, REMOTE-only, live | 0.723 | 0.963 | 248 |  |
| 15 | 300 | high-RTT | deadline-aware model table, REMOTE-only, nominal | 0.723 | 0.963 | 248 |  |
| 15 | 300 | high-RTT | joint, remote-down -> edge failover only | 0.723 | 0.963 | 248 |  |
| 15 | 300 | high-RTT | joint, state-oblivious | 0.723 | 0.963 | 248 |  |
| 15 | 300 | high-RTT | oblivious model -> best path | 0.719 | 0.946 | 262 |  |
| 15 | 300 | high-RTT | edge-only best model | 0.383 | 0.485 | 19791 |  |
| 15 | 300 | server-contended | joint+live | 0.573 | 0.752 | 799 | 2 |
| 15 | 300 | server-contended | deadline-aware model table, REMOTE-only, live | 0.573 | 0.752 | 799 |  |
| 15 | 300 | server-contended | deadline-aware model table, REMOTE-only, nominal | 0.511 | 0.649 | 989 |  |
| 15 | 300 | server-contended | joint, remote-down -> edge failover only | 0.511 | 0.649 | 989 |  |
| 15 | 300 | server-contended | joint, state-oblivious | 0.511 | 0.649 | 989 |  |
| 15 | 300 | server-contended | oblivious model -> best path | 0.478 | 0.616 | 1043 |  |
| 15 | 300 | server-contended | edge-only best model | 0.383 | 0.485 | 19791 |  |
| 15 | 300 | remote-down | joint+live | 0.383 | 0.485 | 19791 | 5 |
| 15 | 300 | remote-down | deadline-aware model table, REMOTE-only, live | 0.000 | 0.000 | 0 |  |
| 15 | 300 | remote-down | deadline-aware model table, REMOTE-only, nominal | 0.000 | 0.000 | 0 |  |
| 15 | 300 | remote-down | joint, remote-down -> edge failover only | 0.383 | 0.485 | 19791 |  |
| 15 | 300 | remote-down | joint, state-oblivious | 0.000 | 0.000 | 0 |  |
| 15 | 300 | remote-down | oblivious model -> best path | 0.060 | 0.060 | 11000 |  |
| 15 | 300 | remote-down | edge-only best model | 0.383 | 0.485 | 19791 |  |

nominal-state joint actions (edge 15 tok/s, SLO 300 s): {'aime': ('qwen3-235b-a22b-2507', 'REMOTE'), 'gpqa': ('deepseek-v3-0324', 'REMOTE'), 'livecodebench': ('Qwen3-8B', 'REMOTE'), 'livemathbench': ('qwen3-235b-a22b-2507', 'REMOTE'), 'mmlupro': ('qwen3-235b-a22b-2507', 'REMOTE')}

| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks differing |
|---|---|---|---|---|---|---|---|
| 40 | 60 | good | joint+live | 0.546 | 0.742 | 178 | 0 |
| 40 | 60 | good | deadline-aware model table, REMOTE-only, live | 0.546 | 0.742 | 178 |  |
| 40 | 60 | good | deadline-aware model table, REMOTE-only, nominal | 0.546 | 0.742 | 178 |  |
| 40 | 60 | good | joint, remote-down -> edge failover only | 0.546 | 0.742 | 178 |  |
| 40 | 60 | good | joint, state-oblivious | 0.546 | 0.742 | 178 |  |
| 40 | 60 | good | oblivious model -> best path | 0.442 | 0.572 | 261 |  |
| 40 | 60 | good | edge-only best model | 0.278 | 0.535 | 4764 |  |
| 40 | 60 | high-RTT | joint+live | 0.546 | 0.742 | 179 | 0 |
| 40 | 60 | high-RTT | deadline-aware model table, REMOTE-only, live | 0.546 | 0.742 | 179 |  |
| 40 | 60 | high-RTT | deadline-aware model table, REMOTE-only, nominal | 0.546 | 0.742 | 179 |  |
| 40 | 60 | high-RTT | joint, remote-down -> edge failover only | 0.546 | 0.742 | 179 |  |
| 40 | 60 | high-RTT | joint, state-oblivious | 0.546 | 0.742 | 179 |  |
| 40 | 60 | high-RTT | oblivious model -> best path | 0.442 | 0.572 | 262 |  |
| 40 | 60 | high-RTT | edge-only best model | 0.278 | 0.535 | 4764 |  |
| 40 | 60 | server-contended | joint+live | 0.349 | 0.543 | 1425 | 2 |
| 40 | 60 | server-contended | deadline-aware model table, REMOTE-only, live | 0.332 | 0.525 | 442 |  |
| 40 | 60 | server-contended | deadline-aware model table, REMOTE-only, nominal | 0.316 | 0.428 | 711 |  |
| 40 | 60 | server-contended | joint, remote-down -> edge failover only | 0.316 | 0.428 | 711 |  |
| 40 | 60 | server-contended | joint, state-oblivious | 0.316 | 0.428 | 711 |  |
| 40 | 60 | server-contended | oblivious model -> best path | 0.200 | 0.237 | 4438 |  |
| 40 | 60 | server-contended | edge-only best model | 0.278 | 0.535 | 4764 |  |
| 40 | 60 | remote-down | joint+live | 0.278 | 0.535 | 4764 | 5 |
| 40 | 60 | remote-down | deadline-aware model table, REMOTE-only, live | 0.000 | 0.000 | 0 |  |
| 40 | 60 | remote-down | deadline-aware model table, REMOTE-only, nominal | 0.000 | 0.000 | 0 |  |
| 40 | 60 | remote-down | joint, remote-down -> edge failover only | 0.278 | 0.535 | 4764 |  |
| 40 | 60 | remote-down | joint, state-oblivious | 0.000 | 0.000 | 0 |  |
| 40 | 60 | remote-down | oblivious model -> best path | 0.027 | 0.027 | 4129 |  |
| 40 | 60 | remote-down | edge-only best model | 0.278 | 0.535 | 4764 |  |

nominal-state joint actions (edge 40 tok/s, SLO 60 s): {'aime': ('qwen3-235b-a22b-2507', 'REMOTE'), 'gpqa': ('qwen3-235b-a22b-2507', 'REMOTE'), 'livecodebench': ('qwen3-235b-a22b-2507', 'REMOTE'), 'livemathbench': ('NVIDIA-Nemotron-Nano-9B-v2', 'REMOTE'), 'mmlupro': ('qwen3-235b-a22b-2507', 'REMOTE')}

| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks differing |
|---|---|---|---|---|---|---|---|
| 40 | 300 | good | joint+live | 0.723 | 0.963 | 247 | 0 |
| 40 | 300 | good | deadline-aware model table, REMOTE-only, live | 0.723 | 0.963 | 247 |  |
| 40 | 300 | good | deadline-aware model table, REMOTE-only, nominal | 0.723 | 0.963 | 247 |  |
| 40 | 300 | good | joint, remote-down -> edge failover only | 0.723 | 0.963 | 247 |  |
| 40 | 300 | good | joint, state-oblivious | 0.723 | 0.963 | 247 |  |
| 40 | 300 | good | oblivious model -> best path | 0.719 | 0.946 | 261 |  |
| 40 | 300 | good | edge-only best model | 0.556 | 0.712 | 7180 |  |
| 40 | 300 | high-RTT | joint+live | 0.723 | 0.963 | 248 | 0 |
| 40 | 300 | high-RTT | deadline-aware model table, REMOTE-only, live | 0.723 | 0.963 | 248 |  |
| 40 | 300 | high-RTT | deadline-aware model table, REMOTE-only, nominal | 0.723 | 0.963 | 248 |  |
| 40 | 300 | high-RTT | joint, remote-down -> edge failover only | 0.723 | 0.963 | 248 |  |
| 40 | 300 | high-RTT | joint, state-oblivious | 0.723 | 0.963 | 248 |  |
| 40 | 300 | high-RTT | oblivious model -> best path | 0.719 | 0.946 | 262 |  |
| 40 | 300 | high-RTT | edge-only best model | 0.556 | 0.712 | 7180 |  |
| 40 | 300 | server-contended | joint+live | 0.600 | 0.777 | 3867 | 3 |
| 40 | 300 | server-contended | deadline-aware model table, REMOTE-only, live | 0.573 | 0.752 | 799 |  |
| 40 | 300 | server-contended | deadline-aware model table, REMOTE-only, nominal | 0.511 | 0.649 | 989 |  |
| 40 | 300 | server-contended | joint, remote-down -> edge failover only | 0.511 | 0.649 | 989 |  |
| 40 | 300 | server-contended | joint, state-oblivious | 0.511 | 0.649 | 989 |  |
| 40 | 300 | server-contended | oblivious model -> best path | 0.559 | 0.703 | 4438 |  |
| 40 | 300 | server-contended | edge-only best model | 0.556 | 0.712 | 7180 |  |
| 40 | 300 | remote-down | joint+live | 0.556 | 0.712 | 7180 | 5 |
| 40 | 300 | remote-down | deadline-aware model table, REMOTE-only, live | 0.000 | 0.000 | 0 |  |
| 40 | 300 | remote-down | deadline-aware model table, REMOTE-only, nominal | 0.000 | 0.000 | 0 |  |
| 40 | 300 | remote-down | joint, remote-down -> edge failover only | 0.556 | 0.712 | 7180 |  |
| 40 | 300 | remote-down | joint, state-oblivious | 0.000 | 0.000 | 0 |  |
| 40 | 300 | remote-down | oblivious model -> best path | 0.190 | 0.201 | 4129 |  |
| 40 | 300 | remote-down | edge-only best model | 0.556 | 0.712 | 7180 |  |

nominal-state joint actions (edge 40 tok/s, SLO 300 s): {'aime': ('qwen3-235b-a22b-2507', 'REMOTE'), 'gpqa': ('deepseek-v3-0324', 'REMOTE'), 'livecodebench': ('Qwen3-8B', 'REMOTE'), 'livemathbench': ('qwen3-235b-a22b-2507', 'REMOTE'), 'mmlupro': ('qwen3-235b-a22b-2507', 'REMOTE')}

| edge tok/s | SLO s | state | policy | utility (acc, 0 if late) | SLO attain | device J/query | #tasks differing |
|---|---|---|---|---|---|---|---|
