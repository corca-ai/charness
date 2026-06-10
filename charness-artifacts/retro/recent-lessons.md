# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v0.36.0`. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`)
- Release publish triggered a configured automatic session retro for `v0.37.0`. (source: `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`; sources: 23)
- Minor: the goal text's slice-1 command sketch omitted required `verify-closeout` args and used a wrong script path; the activation plan critique caught it and the executed calls were already correct, so cost was ~zero. (source: `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`)
- Observed fact: `probe_host_logs.py`'s measured block on this Claude host aggregates the whole project directory (3270 records / 429 calls — byte-identical to the PRIOR goal's probe), while this goal's own session log held 494 records. Per-goal attribution required manual cross-checking, and the metric-window recorder is Codex-only. Second consecutive goal closeout hitting this (the prior probe artifact carries the same thread-wide caveat) — transferable, filed below. (source: `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`)
- Small and bounded this run. The locked producer run confirmed 0 uncovered changed lines on the FIRST attempt (the W1 repeat trap — producer DISCOVERING uncovered degrade branches at the bundle boundary — did not fire; the trend line 7→4→3→0 closes). (source: `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`; sources: 23)
- capability (filed): per-goal metric scoping for `probe_host_logs.py` on Claude hosts — select the current/named session file instead of the project-dir aggregate, and extend the metric-window recorder beyond `--codex-session-file`. Structural pattern: goal-closeout metrics on Claude hosts cannot be scoped to the goal, so every closeout either hand-writes caveats or risks misattributing thread-wide numbers. Triggering instances: this goal's probe artifact and the prior goal's (`2026-06-10-342-343-goal-host-log-probe.md`), both carrying the same caveat. Destination: issue (recurs). (source: `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`)
- I1 — adapter-vs-integration-schema commit-time validation gap: `issue #342`. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- **I1 (workflow/capability): issue #344** — deterministic closeout nudge when a slice adds a new eligible mutation-pool file, naming the early producer self-check, so confirm-not-discover stops depending on recall. (source: `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
