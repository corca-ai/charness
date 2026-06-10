# Recent Retro Lessons

## Current Focus

- Closeout retro for `charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md` (6h timebox, operator asleep, Claude host): five quality slices (posture refresh, #350, C2 bootstrap data-loss fix, C4 commit-time handoff pull, C3 scheduled-mutation capacity-advisory reclassification) then the pre-authorized single push + v0.40.0 release lane. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- Closeout retro for the activated goal `charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md` (2.5h timebox, Claude host): slice 1 consumed the operator-executed third 2026-06-10 push + v0.39.0 release lane read-only (fourth iteration of the deferred-proof pattern), and slice 2 resolved #349 with a deliberate frozen-contract `preserve` edit to the at-cap hitl skill core. (source: `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`; sources: 26)
- First disposition of the red mutation run was "flake" from same-SHA greens; reading the workflow's base/seed mechanism flipped it to real-by-design within slice 1. Pattern-matching red->green->flake without reading the selection mechanism is the trap. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- Slice-log timestamps were written as estimates and drifted ~2.5h fast; corrected in a dedicated bundle-boundary commit. `date` at each boundary costs nothing. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- validate-quality-artifact's 140-line cap took ~6 trim edit rounds because trimming and field-engagement requirements interact; the scaffold prints the skeleton but not a per-section line budget. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`; sources: 26)
- adapter_lib renderer hygiene — filed as issue #353. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- refresh `charness-artifacts/retro/recent-lessons.md` sourcing this retro (repo-loader-as-oracle; date-at-boundary; read-the-mechanism before CI-flap disposition). (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- when a quality artifact must satisfy both a line cap and field-engagement minima, draft sections against the cap from the start instead of trimming post-hoc. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)

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
- `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`
