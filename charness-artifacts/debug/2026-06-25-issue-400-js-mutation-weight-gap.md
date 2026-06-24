# Issue 400 JS Mutation Weight Gap Debug
Date: 2026-06-25

## Problem

Issue #400 stayed open because scheduled mutation testing reported the
StrykerJS mutation slice as failing on main.

## Correct Behavior

Given scheduled JS mutation testing runs with a configured mutant workload
budget, when the sampler chooses `MUTATION_JS_TARGETS`, then the selected files
must have known nonzero mutant weights and must not bypass the budget as
zero-cost targets.

## Observed Facts

- GitHub issue #400 latest mutation comment for `07449831` reports Python
  mutation PASS but StrykerJS FAIL: 49.7% reachable score, 473 reachable
  mutants, 238 survived, and 2 timeouts.
- The failing JS sample targeted
  `scripts/agent-runtime/build-skill-execution-observation.mjs`, with survivor
  samples around lines 34, 42, 50, 55, 61, and 63.
- The workflow computed `MUTATION_SAMPLE_SEED` during `Select mutation sample`
  but did not pass that seed to the `Run mutation` step, so
  `scripts/run_js_mutation.py` fell back to `default-js-mutation-seed`.
- At the failing commit, `scripts/run_js_mutation.py` listed mutant weights for
  seven agent-runtime files but omitted
  `scripts/agent-runtime/build-skill-execution-observation.mjs`.
- `select_js_targets()` used `JS_MUTATION_MUTANT_WEIGHTS.get(path, 0)` and only
  enforced the mutant budget when the weight was truthy, so an omitted file was
  treated as free.

## Reproduction

With `build-skill-execution-observation.mjs` omitted from the weight table, the
pre-fix selector admitted that file under `default-js-mutation-seed` because its
unknown weight was treated as `0`. Under the run-specific seed
`28100660350:236774f484978a60564b013afe79053c69ad986f..074498316feb84afedf9ca217da9a5ac71cae114`,
the fixed selector emits only `scripts/agent-runtime/contract-versions.mjs`
under the default 120-mutant budget.

## Candidate Causes

- Missing mutant weight metadata let an oversized JS file bypass the sampler's
  workload budget.
- The scheduled workflow computed a deterministic sample seed but did not pass
  it into the JS mutation runner, so the local reproduction seed and actual
  run seed diverged.
- StrykerJS tests for `build-skill-execution-observation.mjs` were too weak to
  kill enough mutants when that file was deliberately sampled.
- The issue-opening workflow misreported a passing mutation run as failing.

## Hypothesis

The issue was caused by missing JS mutation weight metadata plus a workflow seed
handoff gap, not by issue creation or Python mutation score logic. If the
missing weight is added, full-mode selection refuses unweighted pool targets,
and the workflow passes the scheduled sample seed into the mutation run, the
oversized 473-mutant file should no longer enter a bounded slice as a zero-cost
target and StrykerJS should pass locally.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_js_mutation_tooling.py` passed
  after adding the weight coverage invariant and runtime guard test.
- `tests/quality_gates/test_quality_mutation_testing.py` now requires both the
  workflow template and checked-in workflow to pass `MUTATION_SAMPLE_SEED` into
  the `Run mutation` step as well as `Select mutation sample`.
- `MUTATION_SAMPLE_SEED='28100660350:236774f484978a60564b013afe79053c69ad986f..074498316feb84afedf9ca217da9a5ac71cae114' npm run test:mutation:js`
  exited 0.
- `python3 scripts/check_js_mutation_score.py --repo-root .` reported
  `StrykerJS score: 85.7% threshold: 80% reachable: 7`.

## Root Cause

The JS mutation sampler had a manually maintained mutant-weight table that did
not cover the full mutation pool. Unknown weights were interpreted as `0`, so a
large newly added runtime file could bypass `MUTATION_JS_MAX_MUTANTS`; the
workflow then failed to pass its scheduled seed into the mutation run, so the
runner used the default seed that selected the omitted file.

## Invariant Proof

- Invariant: every full-mode JS mutation target selected by
  `select_js_targets()` must have known mutant-weight metadata before StrykerJS
  runs.
- Producer Proof: `scripts/run_js_mutation.py` now includes
  `build-skill-execution-observation.mjs` in `JS_MUTATION_MUTANT_WEIGHTS` and
  fails full-mode selection on missing or non-positive weights.
- Final-Consumer Proof: `stryker.config.mjs` consumes the emitted
  `MUTATION_JS_TARGETS`; the failing seed now emits only
  `scripts/agent-runtime/contract-versions.mjs`, and the real StrykerJS run
  passes at 85.7%.
- Workflow Proof: `.github/workflows/mutation-tests.yml` and the reusable
  template now pass the same `MUTATION_SAMPLE_SEED` expression to `Run mutation`
  that `Select mutation sample` uses.
- Interface-Shape Sibling Scan: `tests/quality_gates/test_js_mutation_tooling.py`
  now asserts the weight table exactly covers `list_js_targets()`.
- Non-Claims: this does not claim the 473-mutant observation builder file would
  pass if deliberately sampled under a larger JS mutation budget.

## Detection Gap

- JS mutation weight metadata | pool-list/import tests did not require weight
  coverage | add a weight-table coverage test plus full-mode runtime refusal on
  unweighted targets.
- Mutation workflow seed handoff | existing workflow tests checked only that a
  run-id seed existed somewhere | require the seed expression to appear in both
  sample selection and mutation execution.

## Sibling Search

- Mental model: importing every JS runtime module was treated as enough
  mutation readiness, while workload-budget metadata was a separate manual table.
- same layer: `scripts/run_js_mutation.py` weight table | decision: same bug,
  fix now | proof: local payload proof.
- abstraction up: Python mutation sampler computes or filters workload from
  mutation/coverage data rather than treating unknown weight as free | decision:
  intentional stronger boundary | proof: static scan only.
- specialization down: surviving mutants inside
  `build-skill-execution-observation.mjs` | decision: valid follow-up outside
  the slice | proof: static scan only | follow-up: issue #400 close comment
  should explicitly defer broad survivor-killing for a larger deliberate JS
  mutation budget.
- cross-file: `tests/quality_gates/test_js_mutation_tooling.py` now owns the
  sampler metadata invariant.
- workflow: `.github/workflows/mutation-tests.yml` and
  `skills/public/quality/scripts/templates/mutation-tests.yml` now keep sample
  selection and mutation execution on the same seed.

## Seam Risk

- Interrupt ID: issue-400-js-mutation-weight-gap
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep the JS mutation pool, native test import coverage, mutant-weight table, and
workflow seed handoff in focused gates so a future runtime file cannot enter
scheduled mutation as an unbudgeted zero-cost target or be debugged under a
different seed than CI used.

## Related Prior Incidents

- `charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md`:
  another quality gate used stale/churn-sensitive metadata as if it were a
  stable signal; this fix adds an explicit metadata coverage invariant.
