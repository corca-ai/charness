# Recent Retro Lessons

## Current Focus

- Operator-approved 8h autonomous goal (`charness-artifacts/goals/2026-06-12-autonomous-structural-quality-bundle.md`, proof base `c1f7b581`): two new quality gates (bootstrap-shim consistency, public-doc coupling), the clone-advisory structural-signal taxonomy, a log-backed contract-effectiveness cautilus fixture, second-machine release-proof retirement, plus a mid-run operator instruction to resolve the newly opened issues #356/#357 (meaningful-slice cadence and quality-signal scorecard references). (source: `charness-artifacts/retro/2026-06-12-autonomous-structural-quality-bundle.md`)
- Release publish triggered a configured automatic session retro for `v0.41.1`. (source: `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`; sources: 31)
- Slice 2 briefly created superseded critique packet files before the final stable packet slug was regenerated. That did not affect committed state, but it added cleanup work. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)
- Slice 3 initially wrote a critique artifact that said no counterweight was spawned. The repo contract required the counterweight, so the artifact had to be corrected after spawning it. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)
- The final closeout first used `origin/main` as the base, which pulled unrelated older local commits into the proof range and created avoidable Cautilus/public-skill review noise. The correct goal base was `b300c8bf`. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`; sources: 31)
- Before final/bundle closeout on a multi-goal branch, record the intended proof base in the goal artifact before running `run_slice_closeout.py --base`. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)
- Carry forward that broad gates are final/bundle proof; slice iteration should rely on focused tests plus surface validators until the bundle boundary. (source: `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`)
- For advisory duplicate cleanup, keep using a family label that names the shape and owner surface, such as "adapter scalar helper-shaped", instead of a narrow function-name label. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)

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
- `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-autonomous-structural-quality-bundle.md`
- `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`
- `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`
- `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-42-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-43-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`
