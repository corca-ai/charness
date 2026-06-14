# Host Log Probe: general-doc-authoring-preflight

Provider-safe metrics block for the goal
`charness-artifacts/goals/2026-06-14-general-doc-authoring-preflight.md`,
rendered by `skills/public/retro/scripts/probe_host_logs.py --format markdown`
(not hand-assembled). Thread-wide, not a per-goal total — no
`Host metric window:` was requested for this short additive goal, so the numbers
below are session pressure shape, not a scoped goal cost.

## Goal Closeout Metrics

- Goal metric window: not_requested — not requested (no --goal-path); signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide, claude session scope)
- session: /home/hwidong/.claude/projects/-home-hwidong-codes-charness/34fced19-9e4b-4324-9119-5227b205b59e.jsonl
- token snapshots: 220 (point-in-time, not a cumulative total)
- function calls: 96
- custom tool calls: 0
- patch applications: 19
- context compactions: 0
- subagent spawn/wait/close: spawn=1 (point-in-time; the resolution-critique reviewer plus the disposition reviewer were spawned at/after this snapshot)

### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: none

### Window filter
- status: not_applied; included 453 of 453 records

### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present

## Interpretation

Measured signals only (no fabricated cost): no repeated broad gates and no
repeated VCS commands — the two commit-boundary slips (forgotten `scripts/`
mirror sync; subprocess no-drift tests) were each caught once by a gate and
fixed in one round, not re-run loops. Cached-input volume is not treated as
waste. Nothing here indicates avoidable thread churn beyond those two
single-round gate corrections.
