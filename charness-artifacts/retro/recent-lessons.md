# Recent Retro Lessons

## Current Focus

- Closeout retro for the activated goal `charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md` (2.5h timebox, Claude host): slice 1 consumed the operator-executed third 2026-06-10 push + v0.39.0 release lane read-only (fourth iteration of the deferred-proof pattern), and slice 2 resolved #349 with a deliberate frozen-contract `preserve` edit to the at-cap hitl skill core. (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)
- Goal: charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md Closeout retro for the 2026-06-10 next-queue goal (push/release-lane verification + #346 Claude-host metric scoping + #348 portable hotl skill), run as three independently closed-out slices inside a 4h timebox on a Claude host. (source: `charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`; sources: 25)
- A small fold-then-revert cycle on `hitl` SKILL.md: the reciprocal boundary line hit the 200/200 total-line ceiling; reverted deliberately and routed as #349 instead of trimming reviewed prose under time pressure. (source: `charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md`)
- A zsh `===` separator in a compound verify command expanded via `=cmd` lookup and aborted the second call; one rerun. (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)
- Carrier drafting took three `validate-closeout-draft` rounds (missing `resolution_critique`, then missing the labeled Boundary/Resolution-brief/Implementation/Prevention fields) because the draft was hand-shaped from memory. The issue skill ships `describe_closeout_draft_shape.py`; one consult would have produced the full required shape in a single pass. (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`; sources: 25)
- at-cap adjacent-skill propagation recurrence guards (create-skill checklist line + near-cap preflight warning) — filed as issue #350. (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)
- before hand-drafting any structured closeout body or carrier, run the owning skill's `describe_*_shape` helper and fill its printed field list (this retro is the source; lands in recent-lessons via the refresh below). (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)
- capability (filed): per-goal metric scoping for `probe_host_logs.py` on Claude hosts — select the current/named session file instead of the project-dir aggregate, and extend the metric-window recorder beyond `--codex-session-file`. Structural pattern: goal-closeout metrics on Claude hosts cannot be scoped to the goal, so every closeout either hand-writes caveats or risks misattributing thread-wide numbers. Triggering instances: this goal's probe artifact and the prior goal's (`2026-06-10-342-343-goal-host-log-probe.md`), both carrying the same caveat. Destination: issue (recurs). (source: `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`)

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
- `charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
