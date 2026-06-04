# Goal Closeout Metrics

- Goal metric window: absent — ABSENT — no `Host metric window:` line; signals
  below are thread-wide pressure, not a per-goal total

## Measured (thread-wide scope)

- token snapshots: 228 (point-in-time, not a cumulative total)
- function calls: 353
- custom tool calls: 62
- patch applications: 60
- context compactions: 2
- subagent spawn/wait/close: spawn=1, wait=0, close=0

## Proxy (activity shape, not measured cost)

- repeated broad gates: `./scripts/check-markdown.sh=3`, `pytest=18`,
  `ruff=16`
- repeated VCS commands: `git status=15`, `git log=7`, `git diff=4`,
  `git add=5`

## Window Filter

- status: not_applied; included 1993 of 1993 records

## Token Availability

- Claude host: message usage input/output token snapshots are available.

## Non-Claims

- This is not a per-goal total because no `Host metric window:` line was
  recorded before the goal started.
- Token snapshots are point-in-time values, not cumulative total usage.
