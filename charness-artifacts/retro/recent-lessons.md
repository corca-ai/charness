# Recent Retro Lessons

## Current Focus

- Closeout of the achieve goal `2026-05-29-249-248-handoff-chunker-v2`: the handoff chunker now reasons over the live open-issue backlog (#249 input), fires on a bare skill invocation (#249 trigger), composes its stage scripts predictably (#248), and the handoff baton is codified as closeout-only with `## Next Session` reframed as a curation/sequencing memo. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)
- Closeout of the `achieve` goal `charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md`, run end-to-end this session from `/goal` activation through 5 slices plus the bundled #238 (setup names find-skills as a skill) and #239 (achieve before-phase question + activation clarity). (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)

## Repeat Traps

- **#248 defect bit the operator first-hand at session start.** The very first chunker run this session failed on a stage-script flag mismatch (`--repo-root` vs `--entries` vs `--merge-proposal`) — the exact ergonomics defect #248 reports. It became Slice 1's regression seed, so the cost was recovered, but it cost one retry on the opening pickup. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)
- **A real data-loss blocker my own tests missed.** Slice D's second TOML marker exposed that `find_charness_toml_block`'s block-boundary loop broke only on its *own* marker, so uninstalling one charness TOML block would swallow an adjacent one. My Slice C/D tests exercised each hook in isolation; none placed two charness blocks adjacent and uninstalled one. The fresh-eye critique caught it — the per-slice critique earned its cost here. (source: `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`)
- A slice-1 self-test assertion broke on a line-wrapped contract phrase (`drive the routed workflow from your\nresult`); fixed by whitespace- normalizing the test. Avoidable had the test normalized from the start. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)
- Adding `.codex/config.toml` made `config.toml` a unique repo basename, which tripped `check_doc_links` on a pre-existing, unrelated backtick in `docs/deferred-decisions.md` — a side-effect surfaced only at gate time. (source: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`)

## Next-Time Checklist

- **capability:** A "changed-surface broad-gate subset" helper (map a changed path to the gates that uniquely cover it) would let slices shift-left without paying the full ~46s gate each time. Not built this run; logged as a quality posture idea (the goal explicitly declined to expand pre-commit). (source: `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`)
- **capability**: Promote `check_python_lengths.py` from informational to a pre-commit gate (warn-at-~330, fail-at-360 for `skills/public/*/scripts/*.py`). This is the second recorded recurrence of the silent-lib-growth trap; the prior retro already recommended it. The recurrence is the evidence to act now. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)
- **memory**: end-only handoff timing + the over-merge precision lesson are codified (operating-contract, chunked-routing.md) and captured here for the recent-lessons digest. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)
- **memory:** Recorded below in Sibling Search + persisted to recent-lessons: the "scanner correct only because one value existed" trap, the SKILL.md-contract-snippet trap, and the new-helper attention-state trap. (source: `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`
- `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`
- `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`
