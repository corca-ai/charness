# Recent Retro Lessons

## Current Focus

- Issue #208 (scheduled Mutation Tests red on `main` ~2 days) was the only self-fixable open bug (#184/#185 are deferred ideation). (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- Reviewing the session that landed RCA ledger slice 2 (commit `a67675c`): wiring `record_rca_event.py` into the `debug`/`issue`/`retro` closeout prompts via a presence-gated shared reference, flipping `AUTO_APPEND_WIRED=True`, syncing truth surfaces, and a 4-angle + 1-counterweight fresh-eye critique. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

## Repeat Traps

- **200-line SKILL.md budget trap (recurrence, twice)**: edited `skills/public/debug/SKILL.md` while it was already exactly at the `MAX_SKILL_MD_LINES=200` gate without pre-checking, so `validate_skills` failed and forced mid-stream bullet compression — once on the initial wiring and again after the critique's debug-bullet rewrite. `recent-lessons.md` already carries this exact lesson, but scoped to `.py` budgets (480/360 file, 100/150 function, 800 test); it did not transfer to the SKILL.md 200-line gate. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)
- A pre-commit mutation sample using `MUTATION_HEAD_SHA=HEAD` proved only the previous committed window, not the current uncommitted patch. This repeated the same verification-window trap already documented in the mutation debug artifacts. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- Directly editing `recent-lessons.md` was waste because the file is generated from the retro lesson index. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- **doc-link backtick trap (minor)**: the new reference's path-like backticks (`scripts/record_rca_event.py`, the ledger path) tripped `check_doc_links`; resolved with `<repo-root>/` placeholders. Gate-caught fast, low cost. (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

## Next-Time Checklist

- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)
- after any changed-line or changed-path gate fix, commit first, then rerun the sampler against the committed `base..HEAD` window before claiming the scheduled gate is repaired. (source: `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`)
- before adding code to a script/test file, check its current line count against the 480/360/800 file and 100/150 function budgets; if it is within ~15 lines of a limit, extract first. (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- **capability (immediate next slice)**: decouple AC4/AC7 from the live committed ledger — assert the seed-only/empty-baseline guarantees against synthetic fixtures so the committed ledger is free to accrue live events. This unblocks the wiring; until then the auto-append cannot fire. Once decoupled, this retro's own RCA event becomes the first live append (the proper dogfood). (source: `charness-artifacts/retro/2026-05-24-rca-ledger-slice2-wiring.md`)

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
