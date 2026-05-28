# Recent Retro Lessons

## Current Focus

- Closeout of the #230 + #229 achieve goal at `charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md`. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)
- Reviewing the #226 `achieve` run (centralize a portable fresh-eye reviewer-tier policy) — and specifically the user catching that the run's mandated Auto-Retro and efficiency report were never actually produced. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)

## Repeat Traps

- **200-line SKILL.md budget trap (recurrence, twice)**: edited `skills/public/debug/SKILL.md` while it was already exactly at the `MAX_SKILL_MD_LINES=200` gate without pre-checking, so `validate_skills` failed and forced mid-stream bullet compression — once on the initial wiring and again after the critique's debug-bullet rewrite. `recent-lessons.md` already carries this exact lesson, but scoped to `.py` budgets (480/360 file, 100/150 function, 800 test); it did not transfer to the SKILL.md 200-line gate. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)
- A pre-commit mutation sample using `MUTATION_HEAD_SHA=HEAD` proved only the previous committed window, not the current uncommitted patch. This repeated the same verification-window trap already documented in the mutation debug artifacts. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- Directly editing `recent-lessons.md` was waste because the file is generated from the retro lesson index. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- **doc-link backtick trap (minor)**: the new reference's path-like backticks (`scripts/record_rca_event.py`, the ledger path) tripped `check_doc_links`; resolved with `<repo-root>/` placeholders. Gate-caught fast, low cost. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

## Next-Time Checklist

- **capability:** quiet the pre-commit/pre-push markdown hook (print a file count, not the full 485-path list) so agent context is not flooded each commit; until then redirect that hook's stdout. Candidate issue. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **capability:** the `<repo-root>/` placeholder convention should be auto-applied or pre-checked in spec/doc authoring. Repeat-trap #4 hit three times this run despite already being documented. A small pre-commit fixer (`check_doc_links --autofix-placeholder`) would retire this trap. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)
- **memory:** this artifact + #229 capture the "lighter self-substitution" pattern for the next session. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **memory:** this artifact captures the closed-loop achievement — the goal aimed at #230 + #229 also produces its own proof artifacts (retro file + host-log probe + 3 subagent critiques). Future achieve runs inherit the gate by default; no separate enforcement needed. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`
- `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`
- `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`
- `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`
