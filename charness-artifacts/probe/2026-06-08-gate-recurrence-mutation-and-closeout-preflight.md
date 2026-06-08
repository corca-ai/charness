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
