# 421 test-hardening bundle (slices 3+5)
Date: 2026-07-08

## Decision Under Review

The #421 goal's test-hardening bundle: 6 test files changed (proof-target
coverage for `scripts/boundary_probe_lib.py` + `check_boundary_escalation.py`
CLI, plus 8 mutant kills across 4 test surfaces), zero production changes,
before the goal closeout commit.

## Failure Angles

- Overfitting a foreign-owned message string: the stderr detail assertion
  pinned a sentence owned by `grade_skill_outcome.validate_assertion_set`,
  so a legitimate reword there would break the mutant-kill test spuriously.
- False coverage via live-config coupling: the `__main__`-guard test runs the
  real `resolve_hit` against the live critique adapter; a future
  `boundary_cross_surface_surfaces` addition (`repo-markdown` already declares
  `docs/*.md`) would flip `triggered` and fail the test for the wrong reason.
- Fragile monkeypatch seams (private `_surfaces_lib` attr), missed cheap
  mutant kills among the accepts, and style drift from host-file conventions
  were probed and dismissed (see counterweight).

## Counterweight Pass

- Real (folded before ship): the foreign-owned-string assertion was decoupled
  to `"  - " in err and "non-empty list" in err` (prefix owned by the file
  under test, semantic fragment stable); the live-config coupling is now
  documented in the test docstring with the exact remediation (isolated
  tmp-repo adapter) if the dormant condition ever fires.
- Over-worry (not folded): monkeypatch seams fail loud (AttributeError), the
  safe failure mode; the `indent=2` mutant is deliberately unpinned
  (json.loads decouples cosmetics); JS equivalents were proven equivalent
  empirically (differential fuzzer + scoped Stryker rerun), so no cheap win
  was left; additions match each host file's idiom (fixtures, ImportError
  forcing, runpy `__main__` pattern, deliberate co-location for the shared
  adapter fixture).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: tests/test_validate_outcome_assertions.py:81 | action: fix | note: exact stderr sentence was owned by grade_skill_outcome, not the file under test; decoupled to prefix + stable fragment (applied in this bundle).
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_critique_boundary_ownership_presence.py:300 | action: document | note: __main__-guard test depends on the live adapter's empty surfaces list; dormant repo-markdown/docs-glob coupling documented in the docstring with the tmp-repo remediation.
- F3 | bin: over-worry | evidence: strong | ref: tests/test_boundary_probe.py | action: defer | note: monkeypatching `boundary_probe_lib._surfaces_lib` patches the exact production call site and fails loud on rename — safe failure mode, no action.
- F4 | bin: over-worry | evidence: strong | ref: skills/public/impl/scripts/check_boundary_escalation.py:64 | action: defer | note: indent=2 cosmetic mutant intentionally unpinned (json.loads assertion decouples layout); pinning would overfit.
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md | action: document | note: the two #421 artifacts (debug + goal) are repo state per phase rules and ship in the same closeout commit as this bundle.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent, separate context, read-only in
  the shared worktree.
- Requested spawn fields: subagent_type=general-purpose, named reviewer,
  bounded packet (6-file diff scope, intent invariants, verify commands,
  review angles a–e).
- Host exposure state: applied
- Application state: host-confirmed: reviewer transcript recorded under the
  session subagents directory; independent verify results returned (61
  Python + 59 JS tests green, both proof-target files independently measured
  at 100% coverage, live probe config reproduced).

## Fresh-Eye Satisfaction

parent-delegated — the bounded reviewer ran in a separate subagent context
and returned findings the parent then folded (F1 fix, F2 documentation);
verification of the folds re-ran green (33 passed, ruff clean).

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the goal's test slices (subagent-authored tests) producing
  coverage/mutant-kill evidence for their subject scripts.
- Consumer: the mutation gate (sampler baseline + changed-line classifier +
  Stryker slice) consuming that coverage on the next scheduled run.
- Owning surface: repo-owned test suite beside each subject script
  (`tests/`, `tests/quality_gates/`, `tests/agent-runtime/`) — tests target
  repo source, not the generated `plugins/` mirrors.
- Verdict: owned-correctly
