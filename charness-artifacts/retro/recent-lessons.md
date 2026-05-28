# Recent Retro Lessons

## Current Focus

- Closeout of a 7-slice achieve-goal run that absorbed the recurring manual cost of chunking residual handoff entries into a generative- sequence routing recommendation for `/achieve`. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- Closeout of the #230 + #229 achieve goal at `charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md`. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)

## Repeat Traps

- **chunked_routing_lib.py grew to 816 lines.** Not a hook gate (check_python_lengths.py is informational), but past the soft 360 cap. The slice-1 plan held it at 292 (parser only); slices 3, 4, 5 added ranker + merger + auto-draft helpers in one file. Splitting would have been a slice in itself; deferred. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **Slice 7 trigger implementation surfaced late.** The spec named the trigger rule as "deterministic regex (Python)" in slice 1, but the implementation landed only in slice 7. Slices 2–6 carried the rule in prose alone; the test that pins it deterministically did not exist until closeout. A slice-3 or slice-4 ship of the trigger detector would have surfaced the regex-design edges (Korean variants, polite interrogatives) earlier. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **Three doc-link follow-ups across slices 2, 3, 4.** Each slice created a new script file (parse, ranker packet, propose merges). After committing the file, check_doc_links rejected the spec doc because its backticked-without-link references to the to-be-created file became "unique-basename" hits the moment the file appeared on disk. Three separate amend commits followed. Phase intent was right (slice 1 had to forward-reference files that did not yet exist via `<repo-root>/` placeholders) but the doc-link gate's transition from "missing artifact" to "unique-basename" was repeatable waste. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **200-line SKILL.md budget trap (recurrence, twice)**: edited `skills/public/debug/SKILL.md` while it was already exactly at the `MAX_SKILL_MD_LINES=200` gate without pre-checking, so `validate_skills` failed and forced mid-stream bullet compression — once on the initial wiring and again after the critique's debug-bullet rewrite. `recent-lessons.md` already carries this exact lesson, but scoped to `.py` budgets (480/360 file, 100/150 function, 800 test); it did not transfer to the SKILL.md 200-line gate. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

## Next-Time Checklist

- **capability**: Add a single-file growth gate for `*_lib.py` modules under `skills/public/*/scripts/`. The repo already has `check_python_lengths.py` at the 360-line line; make it a pre-commit gate (currently informational) so future slice bundles cannot silently grow a lib past the threshold without an explicit splitting slice. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **capability:** quiet the pre-commit/pre-push markdown hook (print a file count, not the full 485-path list) so agent context is not flooded each commit; until then redirect that hook's stdout. Candidate issue. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **capability:** the `<repo-root>/` placeholder convention should be auto-applied or pre-checked in spec/doc authoring. Repeat-trap #4 hit three times this run despite already being documented. A small pre-commit fixer (`check_doc_links --autofix-placeholder`) would retire this trap. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)
- **memory**: Record in [recent-lessons.md](recent-lessons.md): doc-link gate transition ("missing artifact" → "unique-basename" on file create) is repeatable waste; the fix-after-create pattern across three slices in one goal is the signal. Either pre-create empty placeholder files in slice 1 OR teach check_doc_links to accept `<repo-root>/...` placeholders for paths that do not yet exist (already partially supported but did not cover the bare-backtick case). (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`
- `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`
- `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`
- `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`
