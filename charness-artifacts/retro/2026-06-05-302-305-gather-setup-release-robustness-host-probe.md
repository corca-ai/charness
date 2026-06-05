# Host Log Probe — 302-305-gather-setup-release-robustness goal closeout

Goal: 302-305-gather-setup-release-robustness. Provider-safe metrics block
from probe_host_logs.py (thread-wide scope; no per-goal Host metric window was
recorded at shaping, so these are thread pressure signals, not a per-goal total).

## Goal Closeout Metrics

- Goal metric window: not_requested — not requested (no --goal-path); signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide scope)
- token snapshots: 59 (point-in-time, not a cumulative total)
- function calls: 54
- custom tool calls: 17
- patch applications: 13
- context compactions: 0
- subagent spawn/wait/close: spawn=0, wait=0, close=0

### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: git status=3

### Window filter
- status: not_applied; included 464 of 464 records

### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present

Caveat: the probe's subagent spawn/wait/close counter reports 0 because the
Agent-tool fresh-eye spawns are not the event key it counts; the honest count
is four bounded fresh-eye reviewers this run (one per slice: #304, #303, #302, #305).
