# Recent Retro Lessons

## Current Focus

- Closeout of the `achieve` goal `charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md`, run end-to-end this session from `/goal` activation through 5 slices plus the bundled #238 (setup names find-skills as a skill) and #239 (achieve before-phase question + activation clarity). (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- Closeout of a 7-slice achieve-goal run that absorbed the recurring manual cost of chunking residual handoff entries into a generative- sequence routing recommendation for `/achieve`. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)

## Repeat Traps

- A slice-1 self-test assertion broke on a line-wrapped contract phrase (`drive the routed workflow from your\nresult`); fixed by whitespace- normalizing the test. Avoidable had the test normalized from the start. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- Adding `.codex/config.toml` made `config.toml` a unique repo basename, which tripped `check_doc_links` on a pre-existing, unrelated backtick in `docs/deferred-decisions.md` — a side-effect surfaced only at gate time. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- `skills/public/find-skills/SKILL.md` was already sitting at exactly the 200-line conciseness cap, so adding the load-bearing slice-1 routing-drive contract forced several trim/re-edit cycles to claw back under the cap. The contract content was right early; the budget fight cost the iterations. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- **chunked_routing_lib.py grew to 816 lines.** Not a hook gate (check_python_lengths.py is informational), but past the soft 360 cap. The slice-1 plan held it at 292 (parser only); slices 3, 4, 5 added ranker + merger + auto-draft helpers in one file. Splitting would have been a slice in itself; deferred. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)

## Next-Time Checklist

- SKILL.md files sitting exactly at the 200-line cap are a latent tax on every future contract addition (find-skills is back at exactly 200). A pre-edit headroom signal (e.g. validator warns at ~190) would stop a load-bearing contract line from forcing a trimming sub-task. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- the "hook is dumb, skill owns routing" pattern now lives durably in `skills/public/find-skills/references/session-start-routing.md`; the goal artifact + this retro capture the cross-host parity reasoning. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- when a slice adds a new repo file whose basename may collide (`config.toml`, `settings.json`), run `check_doc_links` early in the slice, not only at closeout, so basename-uniqueness side-effects surface immediately. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- **capability**: Add a single-file growth gate for `*_lib.py` modules under `skills/public/*/scripts/`. The repo already has `check_python_lengths.py` at the 360-line line; make it a pre-commit gate (currently informational) so future slice bundles cannot silently grow a lib past the threshold without an explicit splitting slice. (source: `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`
- `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`
