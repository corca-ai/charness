# Recent Retro Lessons

## Current Focus

- Issue #208 (scheduled Mutation Tests red on `main` ~2 days) was the only self-fixable open bug (#184/#185 are deferred ideation). (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- Closed the handoff's self-fixable open issues (#198, #202-#206) and RCA'd #207 (by-design) through the design→impl→pattern-scan→RCA→final-critique loop with five bounded fresh-eye subagent passes. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)

## Repeat Traps

- Implemented the full fix before running the file/function length gates, so `sample_mutation_files.py` (already 474/480) and its `main` (already ~99/100) blew past their limits and forced a mid-stream extraction into a new module plus a `main` compaction. Running `check_python_lengths` against a file that is already near its budget before adding to it would have surfaced the need for the new module up front. (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- The added `bump_version` test duplicated ~75 lines of release-repo setup that already existed twice, pushing `test_docs_and_misc.py` past the 800-line test limit; the de-duplication helper that fixed it should have been the first move, not a reaction to the gate. (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- Adding a trap directly to `charness-artifacts/retro/recent-lessons.md` by hand was reverted by `refresh_recent_lessons.py` on the next pre-push run; the digest is generated from the selection index, not authored. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- The #192 commit message used `Add #192` instead of a closing keyword (`Fix`/`Closes`/`Resolves`), so GitHub did not auto-close the issue on push. The sibling #194 commit used `Fix #194` and auto-closed cleanly. Manual `gh issue close 192` recovered, but the cost of one stray PR or closeout review missing the keyword can be a stale OPEN issue for days. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)

## Next-Time Checklist

- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)
- before adding code to a script/test file, check its current line count against the 480/360/800 file and 100/150 function budgets; if it is within ~15 lines of a limit, extract first. (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- when a quality gate is a *selection* heuristic reused as a *blocker*, scope the blocker to the changed surface (changed lines), not the whole artifact; keep the whole-artifact metric advisory. (source: `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`)
- after any push that should auto-close issues, verify each issue's state (`gh issue view <n> --json state`) before declaring closeout done; the check is cheap and catches both this trap and the parent `Add #NNN` trap. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`
- `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`
- `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`
