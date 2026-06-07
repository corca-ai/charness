# Recent Retro Lessons

## Current Focus

- Activated and ran the shaped achieve goal `2026-06-07-332-commit-boundary-sweep-enforcement` end to end. (source: `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`)
- Activated the shaped achieve goal `2026-06-07-329-disposition-form-floor` and ran it end to end: built a narrow presence/enum **form** floor (#329) that rejects the named-invalid prose-only `Disposition: memory` and requires one of `applied: <change>` / `issue #N` / `none — <reason>`, form-only (never a content classifier). (source: `charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **A leaked repro file caused two false test failures.** A `rm -f` with a zsh glob (`_repro_v2*.pyc`) hit `nomatch` and aborted the whole cleanup line, so a `scripts/_repro_v2.py` containing `"skipped"` survived into a later pytest run — the structural sweep correctly flagged it (a real validation of the fix) but it read as 2 surface-obligations regressions until I traced it to my own stray file. (source: `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`)
- **A misleading false-green pre-commit dry-run.** The pre-commit consumer dry-run used `--head-sha HEAD` while HEAD was the *parent* (changes uncommitted), so `base..HEAD` EXCLUDED my changes → "blocking: []" looked safe, but the gate only judged my changes after commit (drove run3→run4). The dry-run gave false confidence. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- a bounded fresh-eye reviewer ran a forbidden worktree-mutating `git checkout` and recovered only because the mirror still held the unstaged change. Disposition: none — the contract already forbids worktree-mutating ops (`skills/shared/references/fresh-eye-subagent-review.md`, #258); the reviewer self-disclosed and the integrity was independently re-verified, so this is a recorded near-miss, not new teeth (source: this retro). (source: `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`)
- a `validate_surfaces` lint that flags any `<dir>/**/*.X` source pattern lacking a `<dir>/*.X` sibling, so the idiom footgun cannot return. Disposition: deferred -> handoff Next Session candidate (anchor surface-idiom-lint), not filed, to avoid issue sprawl for a small hardening. (source: `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`)
- At task start, verify the target issue's real state (open/closed + last close event) before trusting the goal/handoff "open" framing. Disposition: memory -> recorded in this retro + recent-lessons digest refresh this session. (source: `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`)

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
- `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`
- `charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md`
- `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`
- `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
