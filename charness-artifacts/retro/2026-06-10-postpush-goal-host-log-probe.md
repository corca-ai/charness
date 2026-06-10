# Host Log Probe — goal 2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror

Goal: charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md
Probe scope: NOT attributable to this goal — see caveat. No per-goal
`Host metric window:` line exists (the window recorder requires a Codex
session file; this goal ran on a Claude host), and the probe's measured
block aggregates beyond this goal's session: the goal's own session log
(`33308bbc...jsonl`) held 494 records at probe time while the probe
reported 3270 records / 429 function calls — numbers identical to the
PRIOR goal's probe artifact, i.e. dominated by older sessions in the same
project directory. Recording those numbers as this goal's cost would be
fabrication; they are omitted from any per-goal claim.

## Goal Closeout Metrics

- Goal metric window: unsupported on this host — `record_metric_window.py`
  requires `--codex-session-file`; no Codex session exists for this goal.

### Measured (this goal's session, from its own log + repo state)

- session log records at probe time: 494 (one session, no context
  compactions observed in this goal's session file)
- commits: 3 on local main (activation+slice 1, slice 2, slice 3 record)
  + 1 branch commit squash-merged as 39ff5432 via PR 345
- bounded reviewer subagents: 3 (activation plan critique, slice 2
  critique, slice 3 post-hoc critique) — all returned verdicts
- broad/locked proof runs: 1 rehearsal (`--skip-broad-pytest`), 1 locked
  producer run (instrumented broad pytest, PASS), 1 consumer confirm
  (ok=true, 0 uncovered), 1 `run-quality.sh --read-only` (73 passed, 0
  failed) — no repeated broad gates

### Proxy (activity shape, not measured cost)

- remote CI consumed read-only: 2 push runs + 1 scheduled mutation run
  (slice 1) + 1 PR run with 2 jobs (slice 3); one `gh run watch` poll
- no wasted producer re-run: the changed-line consumer CONFIRMED 0
  uncovered on first locked run (the W1 repeat-trap did not fire)

### Token availability (Claude host)

- available in the session log but not aggregated per-goal here; the
  project-dir-wide aggregate is recorded as unattributable above.
