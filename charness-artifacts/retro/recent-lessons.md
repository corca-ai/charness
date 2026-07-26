# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- The operator closed the five-item handoff slice, read the waste list, and asked the question the waste list could not answer: *"비슷한 얘기를 계속 듣고 있고, 전수를 잘 고친 줄 알았는데. (source: `charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md`)

## Repeat Traps

- Diagnosing it cost three of those attempts because the gate's message — "index is stale; run `--write`" — points at a fix that CANNOT work here: `--write` emits the new schema, and the next publish overwrites it with the old one again. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- **Four failed publish attempts** (~20 min) to one root cause: I ran the release helper from the INSTALLED plugin (`~/.agents/src/charness/plugins/...`) instead of the repo's own `skills/public/release/scripts/`. Installed charness was 2.11.0, whose `recent_lessons_lib` predates this repo's `independent_source_count` change, so the helper wrote an old-schema lesson index that the repo's own gate then rejected as stale. `bootstrap-resolution.md` already says to use the repo copy inside the source tree; I did not read it before reaching for a path I already had. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- Two rounds of budget-bar rewriting: I sized bars from the post-change slice, then learned from review that enforcement reads the full-window median, then had to run the windows to convergence and rewrite every number and comment a second time. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- Wrote a version floor (`MIN_XDIST_FOR_SCHED_CHUNK = (2, 3)`) from inference and shipped it into a commit before checking; the real answer is 3.2.0. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)

## Next-Time Checklist

- a counted limit (line caps, size budgets) is a planning input, not a retry loop. Read the reported deficit and make one edit. (source: `charness-artifacts/retro/2026-07-26-session-retro.md`)
- a version floor, an upstream mechanism, and a precedent's scope are all CLAIMS ABOUT THE WORLD. Check each against its source in the same edit that writes it; this session shipped one of each from inference and a reviewer caught all three. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- **capability:** a recurrence-class that has bitten K times must carry a mechanism or an explicit refusal. The data to enforce it will exist once the concept identity does; the north star's own frame says the harness *briefs* a capable judge, and a briefing that selects 4 of 1596 lessons by recency is a defective briefing, not a disciplined reader's failure. (source: `charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md`)
- **capability:** give lessons a concept identity. `normalized_key` is surface text, so recurrence is unmeasurable; add an explicit recurrence-class tag to retro Waste/Next-Improvement bullets (authored, validated, and grouped by the index) so `independent_source_count` counts what its name claims. Then re-derive `LESSON_SELECTION_ALPHA_BASE` and the 14-day half-life against the live 1596-candidate corpus, with a back-test asserting that a class recurring 5x over 50 days outranks a 0-day one-off. Both halves are needed: the count is useless while the weighting cannot act on it, and vice versa. (source: `charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md`
- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
