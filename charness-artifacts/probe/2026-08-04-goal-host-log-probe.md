# Goal Host-Log Probe

Date: 2026-08-04
Goal: `charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

Command:

```text
python3 skills/public/retro/scripts/probe_host_logs.py --repo-root . --goal-path charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md --format markdown
```

Observed output:

```text
## Goal Closeout Metrics
- Goal metric window: absent — ABSENT — no `Host metric window:` line; signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide scope)
- token snapshots: 816 (point-in-time, not a cumulative total)
- function calls: 104
- custom tool calls: 708
- patch applications: 92
- context compactions: 8
- subagent spawn/wait/close: spawn=0, wait=0, close=0
### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: none
### Window filter
- status: not_applied; included 3577 of 3577 records
### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present
```

Interpretation and non-claims:

- The probe found no goal metric window, so these are thread-wide pressure
  signals only, not per-goal totals.
- The probe does not attribute host-session usage to this goal and does not
  support a token, turn, tool-count, or cost claim for the goal.
- The proxy signals are activity shape, not measured cost.
- The zero subagent counts are a probe result for this host log source, not a
  claim that the repo's delegated review records were absent.

Persisted: yes: `charness-artifacts/probe/2026-08-04-goal-host-log-probe.md`
