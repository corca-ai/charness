# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py` BEFORE writing any brief or
  spawning any reviewer. The previous session read its lessons after briefing
  three reviewers, so they arrived after the decisions they should have shaped.
- Then run
  `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you are about to touch, before designing. Skipping this was
  the previous session's largest failure.
- Then invoke `issue` on the release-blocking cohort below. Push, tag, version
  bump, and release publish are WITHDRAWN by the repo owner until the
  retro/lesson/quality loop is complete.

## Continuation Capability

- [Observability contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md)
  — owns the session open/dispose/reconcile stages, and the DEFERRED decision on
  auto-opening a session from the host `SessionStart` hook. A hook that declares
  the command is not the deferred thing; one that opens or appends is. Read its
  Deferred Decisions and Non-Goals before redesigning anything here.
- [Ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md)
  — owns the 3/3/3/1 selection, the archive/graduation asymmetry, and the role
  split (`retro` scores and cites, `quality` proposes graduation).
- [Debug record](../charness-artifacts/debug/2026-08-14-issue-cohort-618-624-causal-analysis.md)
  — owns the causal analysis for the #618-#624 cohort and its sibling search.
- [Draft release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — owns the breaking changes and the `--json` migration for the next release.
- [#608](https://github.com/corca-ai/charness/issues/608) — owns why the release
  helper cannot satisfy the pre-publication claims review today.
- [#625](https://github.com/corca-ai/charness/issues/625),
  [#626](https://github.com/corca-ai/charness/issues/626),
  [#627](https://github.com/corca-ai/charness/issues/627) — own the three gaps
  that keep the lesson loop from meaning anything.
- [#617](https://github.com/corca-ai/charness/issues/617) — owns lesson
  presentation lost across context compaction.
- [#586](https://github.com/corca-ai/charness/issues/586),
  [#605](https://github.com/corca-ai/charness/issues/605) — own the
  guards-no-test-reaches class this slice hit twice.
- [#546](https://github.com/corca-ai/charness/issues/546) — owns the
  unenforceable-bar class, live now for the widened flags gate.

## Current State

- [#618](https://github.com/corca-ai/charness/issues/618),
  [#620](https://github.com/corca-ai/charness/issues/620),
  [#622](https://github.com/corca-ai/charness/issues/622),
  [#623](https://github.com/corca-ai/charness/issues/623),
  [#624](https://github.com/corca-ai/charness/issues/624) — fixes landed and
  independently verified; closeout not yet run.
- [#619](https://github.com/corca-ai/charness/issues/619) — seven residue sites
  migrated and the flags gate widened to non-markdown carriers; regenerate its
  verdict with `python3 scripts/check_documented_command_flags.py --repo-root .`.
- The session-start lesson wiring landed and was verified against the
  [observability contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md);
  two spec violations were found and repaired during that verification.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) is the digest;
  the ledger is the real selection surface and the two are not substitutes.
  Regenerate the real one with
  `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed <seed>`.

Non-claims: no push, tag, version bump, release, hosted CI, or issue closure is
claimed. The broad gate including `release_only` was NOT run for this slice at
the owner's direction, so this commit carries lane-scoped proof only.

## Next Session

1. [#625](https://github.com/corca-ai/charness/issues/625) then
   [#626](https://github.com/corca-ai/charness/issues/626) — these two are what
   "the loop works" means.
2. [#627](https://github.com/corca-ai/charness/issues/627) — once a
   solicitation path exists, record the previous session's miss as an anchored
   score; it is the first real test of whether the loop changes anything.
3. Run `python3 scripts/run_standing_pytest.py --repo-root . --mode full
   --include-release-only` and the closeout floor before asking for a fresh
   push/release grant.

## Discuss

- Whether the widened flags gate should be optimized or its bar re-levelled;
  regenerate the cost with
  `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --detail`.
  It is a `quality` routing decision, not a unilateral bar edit.

## References

- [Design north star](./design-north-star.md)
- [Operating contract](./conventions/operating-contract.md)
- [Parallel execution](./conventions/parallel-execution.md)
