# Host-Log Probe — run_slice_closeout module-split goal

- Goal: `charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md`
- Date: 2026-06-08
- Producer: `skills/.../retro/scripts/probe_host_logs.py --repo-root . --format markdown`
- Scope note: goal metric window `not_requested` (short same-day goal; no
  `Host metric window:` line was configured), so the signals below are
  thread-wide pressure, not a per-goal cumulative total. Provider-safe:
  measured counts vs proxy activity-shape, no provider CLI strings embedded.

## Goal Closeout Metrics

- Goal metric window: not_requested — not requested (no --goal-path); signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide scope)
- token snapshots: 434 (point-in-time, not a cumulative total)
- function calls: 429
- custom tool calls: 149
- patch applications: 139
- context compactions: 4
- subagent spawn/wait/close: spawn=4, wait=3, close=3

### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: git status=26, git -C=3, git log=4, git diff=6, git add=5, git commit=3

### Window filter
- status: not_applied; included 3270 of 3270 records

### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present
