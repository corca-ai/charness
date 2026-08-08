# Issue #565 Resolution Critique
Date: 2026-08-09
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- requested tier: `bounded-reviewer` typed subagent, read-only by definition
- requested spawn fields: inherited parent model and reasoning settings; no
  per-subagent model or effort override requested; both spawned unnamed
- host exposure state: host-defaulted
- envelope note: the spawn envelope exposed Read/Grep/Glob only; both reviewers
  confirmed Bash/Edit/Write/Agent were absent, and round 1 listed the two
  experiments it wanted the parent to run rather than asserting their outcome
- application state: spawn tool accepted both reviewer agent ids; reviewer-tier
  application details are host-hidden
- Delivery state: findings-received

## Decision Under Review

Closing `#565` on `scripts/mutate_and_restore.py` and its 26-test suite, built as
slice 1 of `charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`.

`#565`: a mutation sweep is hand-authored inline per slice and nothing verifies
the sweep's own baseline is a real passing run, so a broken harness reports every
mutant `killed` and reads exactly like a clean sweep. Measured instance:
`python3 -m pytest -q $T` with two space-separated paths in `T`, which zsh does
not word-split, so pytest received ONE nonexistent path, exited non-zero, and all
nine mutants recorded as `killed`. Re-run correctly, three of nine had SURVIVED.
Re-confirmed live during the 2026-08-08 audit, an hour after filing.

The premise was re-measured rather than inherited: the parent hand-rolled the
same harness five times earlier in this same session, including a manual `cp`
restore, and one of those hand-rolls refuted the parent's own hypothesis.

## Failure Angles

- **The tool carrying the class it fixes.** A sweep runner is itself a verdict
  surface; the first place to look is whether it renders a verdict it did not
  earn.
- **Restore that is not actually unconditional.**
- **Tests that pass for a reason other than the one their name claims** — the
  repo's live class, and this suite guards the two properties `#565` names.

## Round 1 — DEFECTIVE, four blockers

1. **The `killed` verdict rested on a bare non-zero exit.** `#565`'s own defect
   one level in: a syntax error introduced by the replacement, a collection
   error, an exit-5, or a crashed runner all exit non-zero with no test having
   caught anything. Round 1 also observed that `baseline.passed` was computed,
   emitted, stored — and never compared to anything, so the advertised property
   was really "the baseline exited 0 and some number was parseable".
2. **`invalidate_bytecode` used `importlib.util.cache_from_source`**, which
   resolves against the SWEEP process's cache tag, while `test_command` is an
   arbitrary interpreter. The just-fixed stale-bytecode defect returned silently
   for any venv or non-`sys.executable` runner.
3. **A window between the write and the bytecode drop** left the tree mutated
   with the pristine bytes in a dead local, and the resulting crash exited 1 —
   colliding with "survivors found".
4. **The test guarding the restore property proved nothing.** It asserted only
   "it raised" and "the file matches the original", both of which hold if the
   mutation never happened. The parent CONFIRMED this by mutation before
   repairing: making `apply_mutation` a no-op left the test green.

Round 1 also found the "unreadable baseline summary" refusal had no test at all;
the parent confirmed that too — deleting the branch left the suite green.

## Round 2 — DEFECTIVE, three more blockers, all inside the repairs

1. **`SURVIVED` still rested on a bare exit byte.** The scope accounting added
   for `KILLED` sat downstream of an early `return SURVIVED` on exit 0. A mutant
   that shrinks collection while staying green would be reported as an uncaught
   survivor, sending the reader after a phantom.
2. **`parse_passed`'s `no tests ran` short-circuit scanned the whole
   transcript** — and this runner's own test file contains that literal, so a
   real kill became a REFUSAL on the very file the sweep was dogfooded against.
   The mirror hazard was live too: a stray `N failed` in echoed source could
   manufacture a kill.
3. **The exit-1 collision was never actually fixed.** `main` caught only
   `SweepError`, so every other crash still exited 1.

Repairs: verdicts now read the runner's SUMMARY LINE only; both `KILLED` and
`SURVIVED` require the run to account for the baseline's test count; the error
check moved AFTER the failure check, because pytest reports a teardown error
alongside a genuine `failed` and refusing that would discard a real kill; crashes
exit 3; containment, missing-key, and no-summary refusals added; the glob stem is
escaped; two invented-string tests were replaced with real end-to-end runs
against actual pytest output (`#569`'s shape, which round 2 named).

Two rounds is the cap. The round-2 repairs above are **accepted-unreviewed**.

## Counterweight Pass

The angle that paid, twice, was "the tool carrying the class it fixes" — and it
paid in the direction the parent did not expect. The parent built a runner whose
premise is "do not trust a bare exit code", and shipped a draft whose own verdict
was a bare exit code. Round 2 then found the same asymmetry surviving on the
other verdict.

The angle that did NOT pay: multi-file and ordering. Round 1 checked whether two
mutants could overlap or perturb each other's `find` text and found the
re-read-per-mutant design sound. Recorded so it is not re-run.

**A finding the suite produced before either reviewer**, worth keeping because it
is not obvious: `a + b` -> `a * b` keeps the source SIZE identical, and CPython
validates a `.pyc` by size plus mtime truncated to whole SECONDS. Inside one
second the stale bytecode stays valid, the unmutated code runs, and a real mutant
reports SURVIVED. The first regression test written for it was itself a false
green — it passed with the guard deleted, for timing reasons — and was replaced
with a call-site assertion.

## Boundary Ownership

- Producer: `scripts/mutate_and_restore.py`, which owns the killed/survived/
  refused verdict and the restore contract.
- Consumer: any slice author running a sweep, and the goal template's
  verification plan, which currently asks authors to remember these properties.
- Owning surface: the producer. `#564`'s remedy was explicitly declined as
  rulebook growth precisely so this tool owns the question instead of prose.
- Verdict: single-surface

Nothing moved across a boundary here; a new owner was created for a rule that
previously had none, which is the point of the slice.

## Will The Class Recur

Reduced, not eliminated, and the residual is named. The runner cannot now report
a kill from a bare exit code, an unreadable summary, a shrunken scope, or an
ambiguous edit, and each of those refusals has been observed FAILING. But it is
pytest-summary-shaped: under `unittest`, `go test`, or `cargo test` every mutant
is REFUSED with a message that misdescribes the cause. And nothing forces a slice
author to use it rather than hand-rolling again — that is slice 2's subject, not
this one's.

## Non-Claims

- One repair is UNPINNED: reordering `restore` to verify bytes before
  invalidating bytecode survives mutation, because every constructible test
  raises the same exception in both orders. It is a diagnostic-quality ordering
  with no distinguishing observable, and it is recorded rather than covered by a
  test written to look like coverage.
- `sys.pycache_prefix` relocates bytecode outside the globbed directory, so the
  stale-bytecode guard does not cover that configuration.
- No claim that the runner is runner-agnostic.
- No claim that existing hand-rolled sweeps have been migrated; none were.
