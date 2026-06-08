# Recent Retro Lessons

## Current Focus

- `achieve` goal: split `scripts/run_slice_closeout.py` (474/480, in the length warn band) into the orchestrator plus a cohesive reporting module, behavior-preserving, with the plugin mirror byte-synced. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- Goal: `charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`. (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`; sources: 13)
- Low otherwise: coverage is range-independent, so I re-classified the same coverage report over multiple base ranges with `--reuse-coverage` (cheap) instead of re-probing — that reuse avoided ~2 extra full runs. (source: `charness-artifacts/retro/2026-06-08-issue-335-gate-recurrence-and-closeout-preflight.md`)
- New commits invalidated the prior changed-line coverage fingerprint, so the broad gate warned; running the producer over merge-base origin/main..HEAD then flagged one genuinely-uncovered changed line (the preamble-not-found branch), which I covered. A warn->produce->cover round-trip. (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)
- NOT waste: the fresh-eye critiques caught two real defects before they shipped (Slice-3 owner-message enforcer misattribution; release stale update_instructions). That is the intended function, high value. (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`; sources: 13)
- additive contract work on an at-cap SKILL.md, or a new test that subprocesses a top-level `scripts/<x>.py`, trips a no-increase ratchet (core-headroom / boundary-bypass); anticipate by compressing-to-offset or reusing an in-process / in-repo-mirror path from the start. Disposition: applied: persisted to recent-lessons this run as a pre-commit-design signal. (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)
- at a release/bundle boundary where the session added mutation-pool (`scripts/**`, `skills/**`) commits, run `check_changed_line_mutation_coverage.py --write-fresh-marker` over `merge-base origin/main..HEAD` as the FIRST step, before the broad gate, because new commits invalidate the prior fingerprint and deferring it costs a warn->produce->cover round-trip. Disposition: applied: persisted to recent-lessons this run (the next-time checklist) so the precondition is a workflow signal, not memory. (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)
- authoring a critique artifact — the scaffold gives the required SECTIONS but `validate_critique_artifacts` also enforces strict ENUMS (Structured Findings `bin` and `action`, plus the `Host exposure state: applied` <-> `Application state: host-confirmed:` coupling); keep the scaffold's example enum tokens or check the validator's allowed set BEFORE substituting, rather than inventing values (the Slice-2 critique cost 3 validate->fix round-trips). Disposition: applied: persisted to recent-lessons this run as a critique-authoring signal (added post-disposition-review as a self-correction; same `applied` form as the other two). (source: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`)

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
- `charness-artifacts/retro/2026-06-08-issue-335-gate-recurrence-and-closeout-preflight.md`
- `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`
