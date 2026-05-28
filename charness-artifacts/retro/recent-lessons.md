# Recent Retro Lessons

## Current Focus

- Reviewing the #226 `achieve` run (centralize a portable fresh-eye reviewer-tier policy) — and specifically the user catching that the run's mandated Auto-Retro and efficiency report were never actually produced. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- Issue #208 (scheduled Mutation Tests red on `main` ~2 days) was the only self-fixable open bug (#184/#185 are deferred ideation). (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)

## Repeat Traps

- **200-line SKILL.md budget trap (recurrence, twice)**: edited `skills/public/debug/SKILL.md` while it was already exactly at the `MAX_SKILL_MD_LINES=200` gate without pre-checking, so `validate_skills` failed and forced mid-stream bullet compression — once on the initial wiring and again after the critique's debug-bullet rewrite. `recent-lessons.md` already carries this exact lesson, but scoped to `.py` budgets (480/360 file, 100/150 function, 800 test); it did not transfer to the SKILL.md 200-line gate. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)
- A pre-commit mutation sample using `MUTATION_HEAD_SHA=HEAD` proved only the previous committed window, not the current uncommitted patch. This repeated the same verification-window trap already documented in the mutation debug artifacts. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- Directly editing `recent-lessons.md` was waste because the file is generated from the retro lesson index. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- **doc-link backtick trap (minor)**: the new reference's path-like backticks (`scripts/record_rca_event.py`, the ledger path) tripped `check_doc_links`; resolved with `<repo-root>/` placeholders. Gate-caught fast, low cost. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

## Next-Time Checklist

- **capability:** quiet the pre-commit/pre-push markdown hook (print a file count, not the full 485-path list) so agent context is not flooded each commit; until then redirect that hook's stdout. Candidate issue. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **memory:** this artifact + #229 capture the "lighter self-substitution" pattern for the next session. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **workflow:** when a skill phase says "run `<skill>`", invoke that skill; do not inline-substitute its output. Flip an achieve goal to `complete` only after the After-phase items (retro run, metrics reported) are executed. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`
- `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`
- `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`
- `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`
