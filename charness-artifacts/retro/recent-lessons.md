# Recent Retro Lessons

## Current Focus

- Landed the changed-line mutation-coverage producer (slice 2, lever A+B), pushed, and released v0.25.0. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- One pursue session of the `2026-06-07-324-325-322-handoff-orchestrator` goal: B1 (#324 source-preservation contract + v0.26.0 release — pushed/tagged/published, #324 CLOSED), B2 (handoff-4 false-green warning), and B3/B4 shaped as child `/achieve` goals. (source: `charness-artifacts/retro/2026-06-07-324-release-325-322-shaping-session.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`; sources: 10)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **A misleading false-green pre-commit dry-run.** The pre-commit consumer dry-run used `--head-sha HEAD` while HEAD was the *parent* (changes uncommitted), so `base..HEAD` EXCLUDED my changes → "blocking: []" looked safe, but the gate only judged my changes after commit (drove run3→run4). The dry-run gave false confidence. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **Authoring-preflight skip for new skill-package files.** I authored new `skills/public/quality/scripts/*.py` + `references/*.md` without first running `check_skill_surface_preflight.py` / skimming `authoring-preflight.md`, so the issue-anchor / dated-incident / author-cite / attention-state-declaration constraints bit after the fact — the #308-class trap already in recent-lessons. (source: `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`; sources: 10)
- **capability:** explore a deterministic nudge — flag a newly-added repo-root `scripts/*.py` that implements a generalizable capability and ask whether it belongs in a skill. Classification stays judgment, but a prompt-level tripwire in the impl/quality contract is feasible and cheap. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- **capability:** Extend `check_skill_surface_preflight.py` (or a sibling) to run the portable-package gate set as a single pre-author/pre-closeout tripwire that reports ALL findings at once — its current scope missed attention-state declaration coverage, ownership-overlap, and author-repo cites together. Disposition: scope-extension comment posted to the existing `issue #328` (authoring-preflight prose-pin pre-check) recording these additional gates on the destination, so a future build covers the whole set. (source: `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`)
- **capability — prose-pin pre-check + authoring-preflight prompt (the real tooling gap):** a cheap check that, given changed doc/SKILL paths, greps `tests/` for literal-string assertions referencing them (catches prose-pin breakage before broad pytest), plus a lighter prompt to run `check_skill_surface_preflight.py` / `authoring-preflight.md` before editing a gated surface. **Disposition: `issue #328`** (https://github.com/corca-ai/charness/issues/328) — filed off-goal; decide there whether it folds into the #325 child goal or stands alone. (source: `charness-artifacts/retro/2026-06-07-324-release-325-322-shaping-session.md`)

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
- `charness-artifacts/retro/2026-06-07-324-release-325-322-shaping-session.md`
- `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`
- `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
