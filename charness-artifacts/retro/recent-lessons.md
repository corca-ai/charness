# Recent Retro Lessons

## Current Focus

- This session built the changed-line mutation-coverage premerge-gate (spec + slice 1 consumer + slice 2 producer mechanism) as a **charness-repo-local** capability. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- Closeout review of the `2026-06-06-306-316-open-followups` achieve goal: resolve six open follow-ups (#306, #311, #314, #315, #316, #317) via a sequential dynamic workflow, then a release. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`; sources: 9)
- The gate logic lives in repo-root `scripts/check_changed_line_mutation_coverage.py` and is wired into charness's `run-quality.sh`; the transferable doctrine (stale-coverage freshness guard, the producer-cost lesson) was never written to `skills/public/quality/references/mutation-testing.md`. Other repos adopting the `quality` skill therefore inherit none of it. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- The miss was caught by the **user**, not by any gate or self-check — the portability principle (CLAUDE.md "keep the harness portable") relied on the agent remembering it mid-defect-repair, and it did not fire. Unrecorded, the lesson would have rotted. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- **Minor:** a markdown inline-code span wrapped across a line in `lifecycle.md`, caught by `check-markdown` in the same broad-gate failure as the anchors. (source: `charness-artifacts/retro/2026-06-06-318-319-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`; sources: 9)
- **capability:** explore a deterministic nudge — flag a newly-added repo-root `scripts/*.py` that implements a generalizable capability and ask whether it belongs in a skill. Classification stays judgment, but a prompt-level tripwire in the impl/quality contract is feasible and cheap. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- **memory:** this lesson (recorded here + refreshed into recent-lessons). The concrete instance follow-up — promote the gate's lessons to `quality`'s mutation-testing reference — is already captured as handoff Next Session #3 and in the premerge-gate spec "Skill portability". (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)
- **workflow:** at `spec`/`impl` closeout in this harness repo, when a slice adds a NEW reusable mechanism (repo-root script, gate, or generalizable pattern), require a one-line classification — `host-local` vs `skill-capability` — before closeout. Make the portability question a checkpoint, not a principle. Owner: `docs/conventions/implementation-discipline.md`. (source: `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`)

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
- `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`
- `charness-artifacts/retro/2026-06-06-318-319-closeout.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`
