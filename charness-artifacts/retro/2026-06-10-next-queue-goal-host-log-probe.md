# Host Log Probe — goal 2026-06-10-push-release-verify-346-metric-scope-348-hotl

Goal: charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md
Probe scope: GOAL-SCOPED — first Claude-host goal closeout with a recorded
`Host metric window:` line (claude_session_file source), dogfooding the
capability this goal's slice 2 shipped. The measured block below derives from
this goal's own session file with named provenance; the recurs-class
aggregate-with-caveat posture of the two prior closeouts is retired. The
window ends at recording time (2026-06-10T10:26:02Z); closeout actions after
that point (disposition-review fold, final commit) are not counted.

## Goal Closeout Metrics

- Goal metric window: parsed — applied — signals below are scoped to the recorded goal window
  - window: 2026-06-10T08:50:14Z -> 2026-06-10T10:26:02Z

### Measured (goal-window, claude session scope)

- session: /home/hwidong/.claude/projects/-home-hwidong-codes-charness/2b6bbcd7-0b78-4787-9a21-bfcb42ebb8b0.jsonl
- token snapshots: 470 (point-in-time, not a cumulative total)
- function calls: 259
- custom tool calls: 0
- patch applications: 86
- context compactions: 0
- subagent spawn/wait/close: spawn=4 (activation plan critique, slice 2
  critique, slice 3 critique, disposition review — wait/close are not
  represented in Claude session logs; only spawns are counted)

### Proxy (activity shape, not measured cost)

- repeated broad gates: ruff=3
- repeated VCS commands: git add=4
- not in the proxy counters but visible in the slice logs: 4 instrumented
  broad-pytest producer runs (1 per mutating slice + 2 fingerprint
  refreshes after critique-driven and coverage-driven changes — the
  twice-paid sequencing waste the retro dispositions address)

### Window filter

- status: applied; included 776 of 1027 records

### Token availability (Claude host)

- available: message.usage.input_tokens/output_tokens present

### Broad-gate attestation (results, not commands)

- final-read-only-quality: PASS (73 passed, 0 failed) @ working tree at
  closeout, post-d257efd2
- changed-line-mutation-coverage consumer: ok=true, 0 uncovered @ d257efd2
  vs origin/main
