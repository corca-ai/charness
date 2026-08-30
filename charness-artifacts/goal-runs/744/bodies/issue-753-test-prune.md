## Parent

#744

## Depends on

The typed topology core from #746 (`repograph components` test-only-island
and tests-view derivations) being integrated, which it is as of
2026-08-28. Independent of #748 and #749, but its retained-Python findings
should feed #749's role definition.

## Situation

Measured 2026-08-28 on `c2c7c2384` (after the #746/#747 integration, and
notably AFTER a prior deliberate verification-pruning pass that removed
roughly ten thousand lines of over-verification — recent
`refactor(...): delete closeout ceremony` / `drop output ceremony`
commits are part of that pass). The corpus is still over its own
declared bound, so the growth is structural, not incidental:

- `tests/` holds 574 tracked Python files, 183,926 lines.
- Composition: `tests/quality_gates` 126,454 lines (69% of all test
  mass), root behavioral tests 42,005, `tests/charness_cli` 9,046,
  `tests/coverage_debt` 3,665 (the directory name records its own
  purpose: paying a coverage floor).
- `python3 scripts/check_test_production_ratio.py --repo-root .` reports
  `test-production ratio 1.18 exceeds max 1.00`, `status: over-max`
  (currently advisory).

Reproduction commands (no re-measurement session needed; rerun only to
refresh):

```bash
git ls-files 'tests/*.py' | xargs wc -l | tail -1
for d in tests/quality_gates tests/charness_cli tests/coverage_debt; do
  git ls-files "$d/*.py" | xargs wc -l | tail -1; done
python3 scripts/check_test_production_ratio.py --repo-root .
native/repograph/target/release/repograph components --repo-root .
```

## Experience

The 2026-08-28 #746/#747 integration produced a controlled experiment.
The full standing suite caught 32 regressions that focused per-lane
checks had missed. Splitting those 32 by what they bought:

- Genuinely behavioral catches (earned their keep): a stale generated
  plugin export, repo-wide scanners crashing on committed malformed
  sources, a packaged script missing its consumer-catalog decision, a
  test mutating the real checkout instead of a repo copy.
- Change-detector and ceremony failures (taxed an intended change while
  telling the author nothing new): four exact-payload pins raising
  `KeyError` on one intended additive response field (`native_core`);
  critique-artifact format machinery demanding metadata blocks while the
  repo's own recent history deletes ceremony; a skill-contract gate
  requiring prose an intentional refactor had removed (resolved that day
  as a stale gate, not a skill defect); and the same single root cause
  double-reported through `run-evals`.

Meanwhile structural facts of the production tree were invisible to all
184k lines of tests until the native graph landed the same day: six real
two-file static import cycles in `scripts/`, 1,095 validator/test-only
islands, 5,544 rootless components.

## Impact

The meta layer (tests of the checking machinery) grows with the number
of process rules, not with product behavior, and now dominates the
corpus 69:31. Every intended payload or contract change pays a
multi-test update tax to change-detector pins. Marginal test-maintenance
budget is misallocated: it defends exact shapes of internal reports
while no test owned the structural facts above. The repo's own ratio
gate cannot be promoted from advisory to blocking while the corpus it
would enforce is itself over the line.

## Desired outcome

Prune the test corpus with graph and mutation evidence rather than by
hand-waving, without lowering the behavioral proof floor:

- Inventory orphan and island tests from the same typed graph
  (`repograph components` test-only islands; tests whose imported or
  invoked production owner no longer exists).
- Use the existing mutation-testing surfaces (cosmic-ray/stryker) to
  identify tests that never kill a mutant as deletion candidates, and
  require mutation scores not to regress across the prune.
- Convert exact-payload pins on operational responses into
  additive-key-tolerant contract tests, so intended additive fields stop
  breaking N tests.
- Fold duplicate oracles (the `run-evals` representative contract cases
  vs the direct gates they re-run).
- Only after the prune, decide whether `check_test_production_ratio`
  moves from advisory to blocking.

## Non-claims

- This is not a coverage-reduction goal; behavioral coverage of the
  retained Python surface stays, and mutation score is the regression
  guard.
- It does not abolish meta-gates as a concept — the cross-cutting
  invariant gates demonstrably caught real integration errors on
  2026-08-28.
- It does not block #748 or #749, and it does not by itself change the
  ratio gate's enforcement mode.

## Weak direction

Run the island/orphan inventory first and disposition it in one recorded
pass (delete / keep-with-reason), then the mutation-driven pass, then
the pin-to-contract conversions; keep each deletion commit small enough
that `git revert` is the rollback story.

---

<!-- charness-work-item-key: issue-753-test-prune -->
# Work Item #753 — Stop count-driven test pruning

## Purpose and premise

Disposition the remaining pruning campaign from current evidence. The published audit found 358 of 371 quality-gate files load-bearing, while earlier work already removed two prose-only tests, extracted shared seed support, repaired the ratio denominator, and kept the ratio advisory.

## Acceptance and proof

Capture the existing JTBD audit plus a current official `tokei` readback. Treat the original `wc -l` numbers above as historical context only. Close as `not planned`: capability equality and mutation non-regression are not established, so further deletion to move a ratio would violate the North Star. Split a concept or delete only when responsibility evidence warrants it; never shave comments to move a length measurement.

## Non-claims

No mutation non-regression, completion of the eight trim candidates, remaining payload-pin/dedup work, capability improvement, ratio-blocking, line-count target, blanket Git-backed deletion, or test-production gate promotion claim.
