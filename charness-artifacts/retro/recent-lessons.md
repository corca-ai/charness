# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- Release publish triggered a configured automatic session retro for `v2.10.0`. (source: `charness-artifacts/retro/2026-07-26-v2-10-0-release-auto-retro.md`)

## Repeat Traps

- Diagnosing it cost three of those attempts because the gate's message — "index is stale; run `--write`" — points at a fix that CANNOT work here: `--write` emits the new schema, and the next publish overwrites it with the old one again. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- **Four failed publish attempts** (~20 min) to one root cause: I ran the release helper from the INSTALLED plugin (`~/.agents/src/charness/plugins/...`) instead of the repo's own `skills/public/release/scripts/`. Installed charness was 2.11.0, whose `recent_lessons_lib` predates this repo's `independent_source_count` change, so the helper wrote an old-schema lesson index that the repo's own gate then rejected as stale. `bootstrap-resolution.md` already says to use the repo copy inside the source tree; I did not read it before reaching for a path I already had. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- Two rounds of budget-bar rewriting: I sized bars from the post-change slice, then learned from review that enforcement reads the full-window median, then had to run the windows to convergence and rewrite every number and comment a second time. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- Wrote a version floor (`MIN_XDIST_FOR_SCHED_CHUNK = (2, 3)`) from inference and shipped it into a commit before checking; the real answer is 3.2.0. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)

## Next-Time Checklist

- a counted limit (line caps, size budgets) is a planning input, not a retry loop. Read the reported deficit and make one edit. (source: `charness-artifacts/retro/2026-07-26-session-retro.md`)
- a version floor, an upstream mechanism, and a precedent's scope are all CLAIMS ABOUT THE WORLD. Check each against its source in the same edit that writes it; this session shipped one of each from inference and a reviewer caught all three. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- the installed helper should refuse, or loudly warn, when `--repo-root` resolves to the charness source tree and the installed version differs from the repo's — the gate caught this, but its message misdirects toward a fix that cannot work. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`)
- the standing direction's third clause — **test/code speed** — went unaddressed. Budget bars are regression *detection*, not speed; nothing this session made a gate or a test faster. Recorded as a handoff item so the gap is a tracked choice rather than a silent omission. (source: `charness-artifacts/retro/2026-07-26-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-v2-10-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
