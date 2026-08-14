# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn, then
  `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you will touch. Both flags are REQUIRED — this line named the
  command bare until 2026-08-14, when following it produced a usage error: the
  discipline was written and bound to nothing, which is the class item 2 below
  asks to treat. Why, and where it did not transfer:
  [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md).
- Then invoke `release` on the push-and-close decision in `## Next Session`.

## Continuation Capability

- [Session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md)
  — this slice's waste, four review rounds, three new lessons.
- [Ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md)
  — selection, archive/graduation asymmetry, role split. Its Eighth Slice
  supersedes the earlier "archive is automatic" text.
- [Observability contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md)
  — session open/dispose/reconcile, and the deferred SessionStart decision.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — breaking changes, the `--json` migration, and the known-weak surfaces.
- [dup-review.json](../charness-artifacts/quality/dup-review.json) family
  `d3fea2dbc2463d22` (rotated from `275d5bdd800e9f8c` on 2026-08-14) — why the
  four-writer ledger transaction was not extracted.
- [#608](https://github.com/corca-ai/charness/issues/608) — release helper cannot
  pause for the claims review.
- [#628](https://github.com/corca-ai/charness/issues/628) — scaffold write-path
  class, now measured across all four families rather than argued from one.
- [#617](https://github.com/corca-ai/charness/issues/617) — lesson presentation
  lost across compaction.

## Current State

- [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
  — closeout floor RUN, evidence posted to each, all ten OPEN by decision: the
  carrier is unpushed and `skills/public/issue/SKILL.md:102` refuses a close
  before publication. Three review rounds found defects inside the fixes being closed out; all
  repaired and re-reviewed:
  [critique](../charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md).
- The lesson loop closed end to end for the first time; regenerate with
  `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .`.
- `origin/main` is merged in and the broad gate passes over the integrated tree:
  `python3 scripts/run_standing_pytest.py --repo-root . --mode full --include-release-only`.
- Most seeded lessons carry no anchored evidence yet, so an empty `quality`
  proposal set is the honest state rather than a broken loop; see
  `python3 scripts/render_lesson_lifecycle_review.py --repo-root .`.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) is the digest;
  the ledger is the scored selection surface and the two are not substitutes.

Non-claims: no tag, version bump, release publish, hosted CI, installed-consumer
readback, or issue closure. The 20-commit set IS pushed (`origin/main`
`0a1a53405`, verified by `git ls-remote`); everything after that boundary is
unclaimed.

## Next Session

1. Push, then close #618-#625 with a closeout commit carrying `Closes #N` and the
   classification ledger (the `#614`/`#615`/`#616` carrier shape), then
   `verify-closeout --expect-state CLOSED`. The comment bodies are already on each
   issue and are reusable verbatim. Push is deferred by the owner and is not
   standing-approved. Unpushed set: `git log --oneline origin/main..HEAD`.
   #626/#627 need a scope decision first, not just a push — see their comments.
2. Treat `rule-exists-but-does-not-bind` as a class; the method is yours, treating
   it is not. Now five hits, and the two added on 2026-08-14 were found by
   FOLLOWING this file, not auditing it: its own trigger command was unrunnable,
   and the release fresh-checkout checker reported `configured` at exit 0 while its
   own reason read "declared but were not run" -- both now repaired, the second in
   `353f11b48`. Cheapest probe
   of any treatment — `grep -rn seed_lesson_transitions skills/public/retro/scripts/`
   returns no caller. Cost:
   [session retro](../charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md).
3. Same class, unfinished sibling: three consuming-repo-facing refusals were
   repaired, but `grep -n "python3 scripts/" scripts/recent_lessons_lib.py` still
   returns two. Treated in the lesson-bootstrap files only.

## Discuss

- **Release readiness.** #608 was already fixed by `f149ad0bc` and does not
  block; the handoff carried it as the blocker because nobody read the code. A
  pre-release critique returned DO-NOT-PUBLISH on the NOTES, not the code, and
  its four false claims are repaired. Green is not a grant — the
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
