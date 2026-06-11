# YouTube gather and adapter renderer host-log probe

Goal: `charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`

## Goal Closeout Metrics

- Goal metric window: absent — ABSENT — no `Host metric window:` line; signals
  below are thread-wide pressure, not a per-goal total

### Measured (thread-wide scope)

- token snapshots: 150 (point-in-time, not a cumulative total)
- function calls: 235
- custom tool calls: 34
- patch applications: 34
- context compactions: 2
- subagent spawn/wait/close: spawn=3, wait=3, close=3

### Proxy (activity shape, not measured cost)

- repeated broad gates: `./scripts/check-markdown.sh=3`,
  `./scripts/check-secrets.sh=3`, `ruff=5`, `pytest=3`
- repeated VCS commands: `git status=6`, `git diff=6`

### Window Filter

- status: not_applied; included 1085 of 1085 records

### Token Availability (Claude host)

- available: `message.usage.input_tokens/output_tokens` present
