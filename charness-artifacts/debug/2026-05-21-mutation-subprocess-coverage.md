# Mutation Subprocess Coverage Debug
Date: 2026-05-21

## Problem

Open issue #189 reported another scheduled mutation failure on main. The sampled
run had a failing reachable score and also reported changed mutation-pool files
excluded before mutation by coverage, mutation-line, or budget filters.

## Correct Behavior

Given a scheduled mutation run with changed Python mutation-pool files, when the
repo's pytest command covers those files through subprocess-driven CLI tests,
then the sampler should see that subprocess coverage instead of classifying the
changed files as uncovered.

## Observed Facts

- Issue #189 reported `FAIL` at `71.6%` reachable score with `21` surviving
  Python mutants and `9` changed files excluded before mutation.
- A narrow local Cosmic Ray run over `scripts/worktree_doctor_state.py` and
  `scripts/eval_registry.py` initially failed at `64.6%` with `17` survivors.
- After test hardening, the same narrow local run passed at `93.2%` with
  `44/44` executed mutants.
- Simulating the next sample from base `b882398068a47ad39b9ef954dc4d071b089bac9d`
  initially failed during coverage because plugin export drift was present; after
  sync, the sample ran but still excluded the current-pointer slice's changed
  files.
- After subprocess coverage support, the `b882398..HEAD` coverage run passed
  (`1308 passed`) and changed scripts had non-empty test contexts, but every
  changed file still missed the full mutation-line eligibility threshold.
- After diagnostic splitting, the `b882398..HEAD` sample selected
  `scripts/worktree_doctor_state.py` and separated remaining exclusions into
  file coverage floor versus mutation-line coverage buckets.
- The sampler-only rcfile suppresses Coverage.py's `dynamic-conflict` warning
  because subprocess context switching is intentional and warning text must not
  contaminate helper subprocess output.

## Reproduction

1. Run a narrow mutation config for `scripts/worktree_doctor_state.py` and
   `scripts/eval_registry.py` with the relevant tests. Before test hardening,
   `scripts/check_mutation_score.py` reports `64.6%` and `FAIL`; after the fix,
   it reports `93.2%` and `PASS`.
2. Run `scripts/sample_mutation_files.py` with
   `MUTATION_BASE_SHA=b882398068a47ad39b9ef954dc4d071b089bac9d` and
   `MUTATION_HEAD_SHA=HEAD`. Before subprocess coverage support, changed script
   files exercised via `run_script`-style subprocesses lacked selectable test
   context. After the fix, they have contexts, but still have uncovered mutable
   lines.

## Candidate Causes

- The sampled survivor score was a real testability gap in worktree doctor state
  helpers and eval registry immutability.
- Mutation coverage collection only traced the pytest parent process, so
  subprocess-tested CLI scripts looked uncovered to the sampler.
- Some changed files from the prior current-pointer slice still lack enough
  direct/mutation-line coverage to be selected under the configured threshold.

## Hypothesis

If the survivor gap is addressed with focused contract tests and mutation
coverage starts subprocess coverage with inherited pytest context, then the
targeted survivor sample should pass and subprocess-tested files should be
visible to nodeid selection.

## Verification

- `python3 -m pytest -q tests/test_worktree_doctor_state.py tests/quality_gates/test_packaging_validation.py -m 'not release_only'` passed.
- `python3 -m pytest -q tests/quality_gates/test_quality_mutation_sampling.py::test_mutation_coverage_tracks_python_subprocesses tests/quality_gates/test_quality_mutation_sampling.py::test_mutation_coverage_drops_stale_parallel_shards` passed.
- Narrow Cosmic Ray verification over `scripts/worktree_doctor_state.py` and
  `scripts/eval_registry.py` passed with `score: 93.2% threshold: 80% executed:
  44/44 status: PASS`.
- The `b882398..HEAD` sample after subprocess context propagation ran the full
  test command successfully and produced coverage contexts for changed files,
  but selected `0` changed files because their mutable-line coverage is still
  incomplete.
- A later `b882398..HEAD` sample after manifest diagnostic splitting ran
  `1310` tests, selected `scripts/worktree_doctor_state.py`, reported `6`
  changed files below the file coverage floor, and reported `3` changed files
  with incomplete mutation-line coverage.

## Root Cause

The scheduled mutation workflow combined two issues: real surviving mutants in a
small sampled fill set, and a coverage blind spot for code exercised through
Python subprocesses. The latter made script-level tests invisible to mutation
sampling even when the tests existed and passed.

## Detection Gap

- mutation survivor score | focused local tests did not kill representative
  worktree/eval-registry mutants | add contract tests and verify with a narrow
  Cosmic Ray run.
- subprocess-tested scripts | coverage sampling did not start coverage with
  inherited pytest context | add sampler subprocess startup/context switching.
- changed-file mutation eligibility | scheduled workflow found exclusions only
  after main advanced | still needs a pre-merge or closeout decision; current
  slice makes the subprocess portion visible and splits exclusion causes, but
  does not eliminate all eligibility gaps.

## Sibling Search

- Mental model: pytest coverage of tests implies mutation sampler visibility.
- Same axis: subprocess-tested root scripts | decision: fix now | proof:
  subprocess coverage fixture and `b882398..HEAD` coverage contexts.
- Same axis: worktree/eval-registry survivor contracts | decision: fix now |
  proof: narrow Cosmic Ray pass.
- Adjacent axis: release proof suppression | decision: defer to next slice |
  proof: fresh-eye scan found concrete release paths unrelated to this mutation
  repair.
- Adjacent axis: lowercase advisory quiet-pass | decision: defer | proof:
  current repo has no live advisory, and the fix is a prefix normalization.

## Seam Risk

- Interrupt ID: mutation-subprocess-coverage
- Risk Class: operator-visible-recovery
- Seam: scheduled GitHub mutation workflow versus local pytest/subprocess coverage
- Disproving Observation: next scheduled run closes the open mutation issue with
  no changed-file exclusions.
- What Local Reasoning Cannot Prove: the exact GitHub base SHA chosen by the
  next scheduled workflow and whether all current ahead commits are mutation
  eligible once pushed.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

- Added focused tests for worktree doctor state status aggregation, tail
  truncation, timeout defaults, dataclass output shape, and eval registry
  immutability.
- Added subprocess coverage startup and inherited pytest context switching so
  CLI/script tests spawned from pytest can contribute selectable nodeids.
- Keep changed-file mutation eligibility on the watch list until a full
  `b882398..HEAD` sample reports zero changed exclusions.
- Split changed-file exclusion diagnostics so file coverage floor misses and
  mutation-line misses are no longer both only labeled `uncovered_changed_files`.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-20-mutation-test-command-mismatch.md`: the
  sampler and Cosmic Ray config disagreed on which tests exercised sampled code.
- `charness-artifacts/debug/2026-05-21-mutation-scope-gap-testability.md`: issue
  #183 stayed open because sampled mutable lines were not covered by the selected
  test command.
- `charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md`: current
  sibling scan explicitly deferred mutation sample/test-command coupling.
