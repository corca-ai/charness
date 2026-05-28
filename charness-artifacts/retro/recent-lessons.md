# Recent Retro Lessons

## Current Focus

- Closeout of a 7-slice achieve-goal run that absorbed the recurring manual cost of chunking residual handoff entries into a generative- sequence routing recommendation for `/achieve`. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- Closeout of the #230 + #229 achieve goal at `charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md`. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)

## Repeat Traps

- **chunked_routing_lib.py grew to 816 lines.** Not a hook gate (check_python_lengths.py is informational), but past the soft 360 cap. The slice-1 plan held it at 292 (parser only); slices 3, 4, 5 added ranker + merger + auto-draft helpers in one file. Splitting would have been a slice in itself; deferred. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **Slice 7 trigger implementation surfaced late.** The spec named the trigger rule as "deterministic regex (Python)" in slice 1, but the implementation landed only in slice 7. Slices 2–6 carried the rule in prose alone; the test that pins it deterministically did not exist until closeout. A slice-3 or slice-4 ship of the trigger detector would have surfaced the regex-design edges (Korean variants, polite interrogatives) earlier. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- The chunked-routing goal (slices 1–7, ~12 commits) shipped procedural code that re-implements three agent-judgment tasks. The full pipeline could be invoked conversationally on the parsed handoff entries — the parser is genuinely code-shaped, but merger + trigger + auto-draft are agents doing inference on natural-language context. (source: `charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md`)
- The mid-session split into 5 modules (this push) cleared the length gate but did not address the layering miss; it locked in the procedural design rather than challenging it. (source: `charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md`)

## Next-Time Checklist

- **capability**: Add a single-file growth gate for `*_lib.py` modules under `skills/public/*/scripts/`. The repo already has `check_python_lengths.py` at the 360-line line; make it a pre-commit gate (currently informational) so future slice bundles cannot silently grow a lib past the threshold without an explicit splitting slice. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)
- **capability**: add an advisory pre-impl scan in `impl`'s Before phase that surfaces new `*_lib.py` files in `skills/public/*/scripts/` and flags whichever ones match the verb pattern above. Output is a single pre-impl note: "consider whether <function> is judgment-shaped". Not a gate, a prompt. (source: `charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md`)
- **capability:** quiet the pre-commit/pre-push markdown hook (print a file count, not the full 485-path list) so agent context is not flooded each commit; until then redirect that hook's stdout. Candidate issue. (source: `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`)
- **capability:** the `<repo-root>/` placeholder convention should be auto-applied or pre-checked in spec/doc authoring. Repeat-trap #4 hit three times this run despite already being documented. A small pre-commit fixer (`check_doc_links --autofix-placeholder`) would retire this trap. (source: `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`
- `charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md`
- `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`
- `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`
