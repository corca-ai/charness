# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py` BEFORE writing any brief or
  spawning any reviewer, then
  `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you are about to touch. Both steps earned their place again:
  the reads changed three decisions before any code was written, and the
  [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  records where the same discipline did NOT transfer.
- Then invoke `quality` on the release-readiness question below. Push, tag,
  version bump, and release publish remain WITHDRAWN pending an explicit
  phase-scoped grant.

## Continuation Capability

- [Ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md)
  — owns the 3/3/3/1 selection, the archive/graduation asymmetry, and the role
  split. Read its Eighth Slice before proposing any lifecycle threshold: it
  supersedes the earlier "archive is automatic" text and defers calibration.
- [Observability contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md)
  — owns session open/dispose/reconcile and the DEFERRED SessionStart decision.
- [Session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  — owns this slice's waste, the four review rounds, and the three new lessons.
- [Draft release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — owns the breaking changes and the `--json` migration for the next release.
- [#608](https://github.com/corca-ai/charness/issues/608) — owns why the release
  helper cannot satisfy the pre-publication claims review today.
- [#628](https://github.com/corca-ai/charness/issues/628) — owns the scaffold
  write-path class; the retro's Sibling Search adds a third instance.
- [#617](https://github.com/corca-ai/charness/issues/617) — owns lesson
  presentation lost across context compaction.

## Current State

- [#625](https://github.com/corca-ai/charness/issues/625),
  [#627](https://github.com/corca-ai/charness/issues/627),
  [#626](https://github.com/corca-ai/charness/issues/626) — fixes landed and
  independently reviewed; closeout comments not yet posted, issues not closed.
- The lesson loop closed end to end for the first time: a lesson entered the
  ledger by command, was presented, solicited, and anchored-scored. Regenerate
  with `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .` and
  `python3 scripts/render_lesson_lifecycle_review.py --repo-root .`.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) is the
  generated digest; the ledger is the scored selection surface and the two are
  not substitutes. Regenerate with
  `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed <seed>`.
- The two failures inherited from the previous slice's skipped broad gate are
  repaired, and `origin/main` is merged in, so the broad gate now passes over the
  integrated tree; the
  [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  owns what they were. Regenerate with:

  ```bash
  python3 scripts/run_standing_pytest.py --repo-root . --mode full --include-release-only
  ```

- [#618](https://github.com/corca-ai/charness/issues/618)-[#624](https://github.com/corca-ai/charness/issues/624)
  — fixes landed in the previous slice; closeout still not run.

Non-claims: no push, tag, version bump, release, hosted CI, installed-consumer,
or issue closure is claimed. Every verdict above is local to this worktree.

## Next Session

1. Push and release were deferred by the owner to this session. Confirm the
   unpushed set with `git log --oneline origin/main..HEAD`.
2. Nothing binds a retro that TAGS a new recurrence class to seeding it: this
   session missed its own two new lessons on the slice that built the seeder.
   Confirm with `grep -rn seed_lesson_transitions skills/public/retro/scripts/`
   (no caller) and decide where the binding belongs.
3. Run the `issue` closeout floor for the #625/#627/#626 cohort and the older
   #618-#624 cohort, then post closeout comments. Closing is standing-approved
   only after that floor. Comment the retro-family evidence on
   [#628](https://github.com/corca-ai/charness/issues/628) while there.
4. Take the release-readiness decision below to `quality` before requesting any
   grant; [#608](https://github.com/corca-ai/charness/issues/608) is the blocking
   half, and `fresh_checkout_probes` are declared but have never been run.

## Discuss

- **Release readiness.** The broad gate is green and the release-blocking cohort
  is fixed, but green is not a grant and this slice proved the gap: four review
  rounds found claims that passed every gate and were still false. The
  unresolved half is [#608](https://github.com/corca-ai/charness/issues/608) —
  the release helper cannot satisfy the pre-publication claims review — plus the
  unrun closeout on two issue cohorts. Route through `quality` and `release`, not
  through a unilateral read of a green gate.
- Whether the widened flags gate should be optimized or its bar re-levelled;
  regenerate the cost with
  `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --detail`.

## References

- [Design north star](./design-north-star.md)
- [Operating contract](./conventions/operating-contract.md)
- [Parallel execution](./conventions/parallel-execution.md)
