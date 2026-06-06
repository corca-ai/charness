# Recent Retro Lessons

## Current Focus

- Landed the changed-line mutation-coverage producer (slice 2, lever A+B), pushed, and released v0.25.0. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- This session built the changed-line mutation-coverage premerge-gate (spec + slice 1 consumer + slice 2 producer mechanism) as a **charness-repo-local** capability. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`; sources: 10)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **A misleading false-green pre-commit dry-run.** The pre-commit consumer dry-run used `--head-sha HEAD` while HEAD was the *parent* (changes uncommitted), so `base..HEAD` EXCLUDED my changes → "blocking: []" looked safe, but the gate only judged my changes after commit (drove run3→run4). The dry-run gave false confidence. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **Serial discovery behind a 6-min gate.** Each run surfaced one new issue; I fixed one, paid another ~6 min, found the next. 2-3 of the four runs were avoidable with earlier/batched detection. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`; sources: 10)
- **capability:** explore a deterministic nudge — flag a newly-added repo-root `scripts/*.py` that implements a generalizable capability and ask whether it belongs in a skill. Classification stays judgment, but a prompt-level tripwire in the impl/quality contract is feasible and cheap. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- **capability:** the consumer's verdict is silently misleading when `--head-sha` excludes the worktree. Add a `check_changed_line_mutation_coverage.py` warning when the analyzed head == `HEAD` and the worktree has uncommitted mutation-pool changes, or a documented worktree-range dry-run. Cheap tripwire, kills the false-green. (follow-up:changed-line-gate-worktree-dryrun-warning) (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **memory:** this lesson, persisted here + refreshed into recent-lessons. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)

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
- `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
