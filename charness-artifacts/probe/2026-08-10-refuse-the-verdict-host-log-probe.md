# Host log probe — refuse-the-verdict-a-surface-never-earned closeout

Goal: `charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`
Command: `python3 skills/public/retro/scripts/probe_host_logs.py --repo-root . --format markdown`

Regenerate rather than cite: these counts move while the session runs, and an
earlier draft of the closeout retro quoted figures this file already contradicted.

## Goal Closeout Metrics

- Goal metric window: not_requested — not requested (no --goal-path); signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide, claude session scope)
- session: /home/hwidong/.claude/projects/-home-hwidong-codes-charness/a1d25bb0-6fc3-4c7f-bd76-39ffda62b959.jsonl
- token snapshots: 489 (point-in-time, not a cumulative total)
- function calls: 314
- custom tool calls: 0
- patch applications: 47
- context compactions: 0
- subagent spawn/wait/close: spawn=8

### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: git status=3, git show=3, git log=3, git add=9, git push=3

### Window filter
- status: not_applied; included 1176 of 1176 records

### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present
