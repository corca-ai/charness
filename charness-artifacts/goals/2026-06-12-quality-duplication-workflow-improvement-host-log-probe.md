# Host Log Probe: Quality Duplication Workflow Improvement
Date: 2026-06-12

Source command:

```text
python3 /home/hwidong/.codex/plugins/cache/local/charness/0.41.0/skills/retro/scripts/probe_host_logs.py --repo-root . --goal-path charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-6h.md --format markdown
```

## Goal Closeout Metrics

- Goal metric window: parsed - applied - signals are scoped to the recorded goal window.
- Window: 2026-06-11T21:13:55Z -> 2026-06-11T23:29:26Z.

## Measured

- Token snapshots: 535 (point-in-time, not a cumulative total).
- Function calls: 967.
- Custom tool calls: 44.
- Patch applications: 43.
- Context compactions: 8.
- Subagent spawn/wait/close: 33/29/27.

## Proxy

- Repeated broad gates: ruff=41, pytest=33, markdown=9, secrets=7.
- Repeated VCS probes: git status=33, git diff=38, git add=13, git log=10, git commit=9.

## Window Filter

- Status: applied.
- Included records: 3795 of 8368.

## Non-Claims

- Token snapshots are point-in-time host records, not a cumulative token total.
- Broad-gate and VCS counts are activity-shape proxies, not measured cost.
