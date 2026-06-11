# Recent Retro Lessons

## Current Focus

- Closeout retro for `charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md` (6h timebox, operator asleep, Claude host): five quality slices (posture refresh, #350, C2 bootstrap data-loss fix, C4 commit-time handoff pull, C3 scheduled-mutation capacity-advisory reclassification) then the pre-authorized single push + v0.40.0 release lane. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- Release publish triggered a configured automatic session retro for `v0.41.0`. (source: `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`; sources: 27)
- First disposition of the red mutation run was "flake" from same-SHA greens; reading the workflow's base/seed mechanism flipped it to real-by-design within slice 1. Pattern-matching red->green->flake without reading the selection mechanism is the trap. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- Slice-log timestamps were written as estimates and drifted ~2.5h fast; corrected in a dedicated bundle-boundary commit. `date` at each boundary costs nothing. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- The adapter parser fix initially over-refused real workflow-style block scalars; broad tests caught that, but the round trip cost came from treating unsupported YAML refusal and current workflow compatibility as one decision. (source: `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`; sources: 27)
- adapter_lib renderer hygiene — filed as issue #353. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)
- before locking a direct-commit closeout carrier that covers multiple issues or classifications, run `describe_closeout_draft_shape.py` and validate the exact commit-message file for each issue-specific classification before final artifact edits. (source: `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md`)
- record that `proof:`-style continuation lines inside issue closeout draft fields can be parsed as new fields; use semicolon or same-field prose when a field requires both decision and proof. (source: `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md`)

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
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`
- `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md`
