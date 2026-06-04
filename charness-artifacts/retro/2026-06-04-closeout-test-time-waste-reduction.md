# Closeout Test-Time Waste Reduction Retro

## Mode

session

## Context

This retro covers the follow-up after the portable skill quality closeout
exposed a roughly five-minute broad pytest cost and a brittle handoff parser
test. The work unit trimmed the default repo-python closeout command and
replaced a live-state-sensitive handoff pipeline assertion with a deterministic
fixture-based assertion.

## Evidence Summary

- Prior locked closeout evidence in `docs/handoff.md`: broad pytest passed in
  297.5s.
- Measured split during this follow-up: release-only lifecycle tests contributed
  68.59s when explicitly included.
- New standing broad pytest proof:
  `2134 passed, 4 skipped, 6 deselected in 215.91s`.
- Focused proof for changed tests:
  `6 passed in 3.16s`.
- Fresh-eye critique found no ship blockers and agreed the failed handoff test
  was live-state sensitive rather than a stable unit contract.

## Waste

- The standing repo-python gate included release-only install/update lifecycle
  tests even though `run-quality.sh` already treats `release_only` as opt-in.
  That made ordinary closeout pay release verification cost and hid the true
  default-vs-release boundary.
- The failed handoff test asserted that every current live candidate had issue
  references. That coupled a unit test to GitHub/open-issue state and broke
  when a valid non-issue-only pickup candidate entered the live queue.
- The remaining 216s baseline is still heavy. The current top offenders are
  cumulative subprocess-heavy quality/release tests rather than one isolated
  easy fix.

## Critical Decisions

- Exclude `release_only` from the standing repo-python closeout command and
  leave release/package/tool-lifecycle changes responsible for opting into the
  release gate.
- Replace the live `--with-issues` handoff assertion with fixture-fed
  `propose_merges.py` coverage that proves issue-linked candidates are still
  preserved without asserting that all candidates must be issue-linked.
- Keep #295 open as the broader affected-test/closeout policy issue instead of
  creating a duplicate issue for the same waste pattern.

## Expert Counterfactuals

- Gary Klein would have separated the failure mode into two decision points
  earlier: "what proof is required before mutation is locked?" and "what proof
  is required for release lifecycle behavior?" That would have exposed the
  release-only leakage before paying the full broad cost.
- Daniel Kahneman would have treated the failed live handoff test as a base-rate
  problem: tests that depend on current external state will eventually fail for
  irrelevant reasons, so the default should be fixtures unless the test is
  explicitly an integration check.

## Next Improvements

- workflow: Use the new default closeout command for ordinary repo-python
  slices; run release-only tests only for release, packaging, install/update, or
  tool lifecycle changes.
- capability: #295 should still make broad-vs-focused closeout selection more
  explicit for pre-lock slice proof versus final verification-lock proof.
- memory: Treat live handoff + issue union checks as pickup/integration behavior;
  stable unit tests should use fixtures or stubs.

## Sibling Search

- release-only leakage: searched `.agents`, `tests`, `scripts`, `skills`, and
  `docs` for the old broad command, `test_tool_lifecycle`, and `release_only`.
  The default closeout command now appears only with `-m 'not release_only'`;
  the remaining release-only tests are marked and belong to opt-in release
  surfaces.
- live-state handoff assertions: searched for `--with-issues`,
  `current_handoff_pipeline`, and `referenced_issues`. Deterministic
  `--with-issues` coverage remains in fixture/tmp-repo tests; the removed test
  was the live current-state assertion.

## Persisted

yes: `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`
