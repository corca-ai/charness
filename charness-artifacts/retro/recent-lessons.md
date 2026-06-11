# Recent Retro Lessons

## Current Focus

- This retro covers the active 6h quality goal that continued from the user's complaint about low-yield work. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- Closeout retro for `charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md` (6h timebox, operator asleep, Claude host): five quality slices (posture refresh, #350, C2 bootstrap data-loss fix, C4 commit-time handoff pull, C3 scheduled-mutation capacity-advisory reclassification) then the pre-authorized single push + v0.40.0 release lane. (source: `charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`; sources: 27)
- The install-refresh artifact gap was pre-existing but was only surfaced by a reviewer after the split. That was worth fixing in-slice, but it shows the release contract lacked a focused assertion that "recorded" means durable artifact content, not only final JSON payload. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- The release publish split initially fixed the line/function pressure but missed a direct-loader issue on `sys.modules[__name__]`; fresh-eye caught it before commit. The workflow worked, but the parent should have run a direct-loader smoke immediately after introducing the module boundary. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- The run still spent too much effort on repeated validation churn. Some of that was legitimate bundle proof, but the metric window shows repeated `pytest`, `ruff`, markdown/secrets, and VCS probes at a level that should push future goals toward a clearer gate cadence table before implementation starts. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`; sources: 27)
- Carry forward that broad gates are final/bundle proof; slice iteration should rely on focused tests plus surface validators until the bundle boundary. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- The release resilience tests now assert that install-refresh status is recorded in the durable release artifact, not only in the final JSON payload. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- The release resilience tests now include a direct `spec_from_file_location` loader regression for the extracted publish CLI context; future helper extractions should treat this as the local pattern. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)

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
- `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`
