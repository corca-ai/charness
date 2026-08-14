# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py` BEFORE any brief or reviewer
  spawn, then `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you will touch. Why, and where it did not transfer:
  [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md).
- Then invoke `issue` on the closeout cohort below.

## Continuation Capability

- [Session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  — this slice's waste, four review rounds, three new lessons.
- [Ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md)
  — selection, archive/graduation asymmetry, role split. Its Eighth Slice
  supersedes the earlier "archive is automatic" text.
- [Observability contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md)
  — session open/dispose/reconcile, and the deferred SessionStart decision.
- [Draft release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — breaking changes and the `--json` migration.
- [dup-review.json](../charness-artifacts/quality/dup-review.json) family
  `275d5bdd800e9f8c` — why the four-writer ledger transaction was not extracted.
- [#608](https://github.com/corca-ai/charness/issues/608) — release helper cannot
  pause for the claims review.
- [#628](https://github.com/corca-ai/charness/issues/628) — scaffold write-path
  class; the retro's Sibling Search adds a third instance.
- [#617](https://github.com/corca-ai/charness/issues/617) — lesson presentation
  lost across compaction.

## Current State

- [#625](https://github.com/corca-ai/charness/issues/625),
  [#627](https://github.com/corca-ai/charness/issues/627),
  [#626](https://github.com/corca-ai/charness/issues/626) — landed and reviewed;
  closeout not run, issues open.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#624](https://github.com/corca-ai/charness/issues/624)
  — landed previous slice; closeout not run.
- The lesson loop closed end to end for the first time; regenerate with
  `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .`.
- `origin/main` is merged in and the broad gate passes over the integrated tree:
  `python3 scripts/run_standing_pytest.py --repo-root . --mode full --include-release-only`.
- Most seeded lessons carry no anchored evidence yet, so an empty `quality`
  proposal set is the honest state rather than a broken loop; see
  `python3 scripts/render_lesson_lifecycle_review.py --repo-root .`.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) is the digest;
  the ledger is the scored selection surface and the two are not substitutes.

Non-claims: no push, tag, version bump, release, hosted CI, installed-consumer,
or issue closure. Every verdict above is local to this worktree.

## Next Session

1. Push and release, deferred here by the owner. Unpushed set:
   `git log --oneline origin/main..HEAD`.
2. Treat `rule-exists-but-does-not-bind` as a class; the method is yours to
   choose, treating it is not optional. Three hits in one slice — `quality` not
   knowing it owned the lesson lifecycle, the retro persist path never calling
   the seeder, the handoff discipline documented but bound to nothing — and only
   instances were repaired. The retro-to-seeder one is still open and is the
   cheapest probe of any proposed treatment — `grep -rn seed_lesson_transitions skills/public/retro/scripts/`
   returns no caller. Instances and their cost:
   [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md).
3. Run the `issue` closeout floor for both cohorts, post closeout comments, and
   add the retro-family evidence to
   [#628](https://github.com/corca-ai/charness/issues/628).
4. `fresh_checkout_probes` are declared and have never run:
   `python3 skills/public/release/scripts/check_fresh_checkout_probes.py --repo-root .`.

## Discuss

- **Release readiness.** Local proof is green; the release PROCESS is not ready.
  [#608](https://github.com/corca-ai/charness/issues/608) blocks it and closeout
  is unrun. Green is not a grant — the
  [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  records four rounds of claims that passed every gate and were false. Route
  through `quality` and `release`.
- Whether to extract the ledger write transaction shared by four writers; see
  the dup-review family above.
- Whether the widened flags gate should be optimized or its bar re-levelled:
  `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --detail`.

## References

- [Design north star](./design-north-star.md)
- [Operating contract](./conventions/operating-contract.md)
- [Parallel execution](./conventions/parallel-execution.md)
