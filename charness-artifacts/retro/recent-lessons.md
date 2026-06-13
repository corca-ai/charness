# Recent Retro Lessons

## Current Focus

- **S1 (A2, `e6d1a59a`)** — made `describe_goal_closeout_shape.py` goal-aware via `--goal-path`: it reads the in-progress goal and emits only the floors *that* goal triggers (and which are missing), folding the dry `check_goal_artifact.py` preview into one call. Closes the residual Problem-1 churn the D closeout-floor audit named on the runtime-conditional `keep` floors a static catalog cannot. (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)
- **S2 (`c75de40f`)** — gave the prose Floor-Addition Restraint checklist non-blocking teeth: `advise_floor_addition_restraint` flags a new blocking floor (new `report["ok"] = False` site / new `REQUIRED_*` member) added without a recorded restraint call. Resolves `follow-up:floor-addition-restraint-nudge`. (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`; sources: 34)
- Slice 2 briefly created superseded critique packet files before the final stable packet slug was regenerated. That did not affect committed state, but it added cleanup work. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)
- Slice 3 initially wrote a critique artifact that said no counterweight was spawned. The repo contract required the counterweight, so the artifact had to be corrected after spawning it. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)
- The final closeout first used `origin/main` as the base, which pulled unrelated older local commits into the proof range and created avoidable Cautilus/public-skill review noise. The correct goal base was `b300c8bf`. (source: `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`; sources: 34)
- **memory — repo-root `scripts/*.py` mirror into `plugins/charness/scripts/`**, not just skill surfaces; sync before the commit gate, not after a rejection. (The staged-mirror-drift gate already enforces this deterministically; the lesson is to sync proactively.) (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)
- **workflow — stage explicit paths, not `git add -A`, when untracked/off-goal files may be present.** The closeout proof and commit should cover only the goal's own changed set; `git add -A` couples in concurrent WIP. (Transferable — see Sibling Search.) (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)
- **workflow — the A2 `--goal-path` describe is now the right first closeout step**; it surfaced this goal's exact missing set first-try. Use it instead of the static catalog + separate dry check going forward (the SKILL.md/lifecycle wiring now points there). (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)

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
- `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`
- `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-42-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-43-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-44-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-45-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`
