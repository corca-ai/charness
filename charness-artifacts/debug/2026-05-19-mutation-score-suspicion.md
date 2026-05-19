# Mutation Score Suspicion Debug
Date: 2026-05-19

## Problem

Scheduled mutation testing is reporting success with a very high reachable
score, which makes the run look suspiciously weak for a mutation-test gate.

## Correct Behavior

Given a full mutation workflow runs on `main`, when it reports success, then it
should have mutated a representative configured sample, executed tests against
reachable mutants, and failed closed when no reachable mutants were executed or
when sampled mutants have no matching tests.

## Observed Facts

- The latest local summary reported `90.1%` reachable score: 456 total, 282
  killed, 31 survived, and 143 skipped annotation-only union mutants.
- Every dump record targeted `scripts/control_plane_lib.py`; no other module
  appeared in the current report.
- `.agents/quality-adapter.yaml` had `mutation_testing.commands.sample: ""`,
  so scheduled full runs skipped `scripts/sample_mutation_files.py`.
- `check_mutation_score.mutation_metrics()` returned PASS with `100.0%` when
  `killed + survived == 0`, including all-pending or all-skipped dumps.

## Reproduction

- `gh run list --repo corca-ai/charness --workflow mutation-tests.yml --limit 10`
  showed recent scheduled runs all succeeding.
- Parsing `reports/mutation/cosmic-ray-dump.jsonl` <!-- reproduction-source --> showed
  `modules {'scripts/control_plane_lib.py': 456}`.
- Directly calling `mutation_metrics()` with ten pending mutants returned
  `score: 100.0` and `passed: True`.

## Candidate Causes

- Measurement scope was too narrow because the sample command was disabled in
  the adapter.
- The summary gate treated an empty reachable denominator as perfect success.
- Same-SHA scheduled runs could reuse the same sample seed, weakening the
  intended rotation when `main` was idle.

## Hypothesis

If mutation score validity is undermined by disabled sampling and zero-reachable
PASS behavior, then enabling the sample command, rotating the workflow seed by
run id, and failing zero-reachable summaries should make the gate harder to
misread.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py tests/quality_gates/test_quality_bootstrap.py`
  passed.
- `ruff check scripts/check_mutation_score.py tests/quality_gates/test_quality_mutation_testing.py`
  passed.
- `python3 scripts/validate_adapters.py --repo-root .` passed.
- `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run`
  completed baseline/init/filter and confirmed 456 initialized mutants with 143
  filtered low-signal mutants.
- Unit regressions now cover active adapter sample wiring, checked-in workflow
  run-id sample seeding, sample script config/manifest rewriting, zero-reachable
  summary failure, and no-tests scope-gap failure.

## Root Cause

The mutation workflow was honestly executing Cosmic Ray, but the configured
full run was a one-file dogfood target rather than a rotating sample. The score
checker also had fail-open summary rules for runs that produced no reachable
mutants or sampled mutants outside the configured test scope.

## Detection Gap

- `check_mutation_score.py` | zero reachable or no-tests mutants could report
  PASS | add regressions that fail closed.
- `.agents/quality-adapter.yaml` | sample helper existed but was disabled |
  make the configured command explicit.
- `.github/workflows/mutation-tests.yml` | same-SHA schedules reused the same
  seed | include `github.run_id` in `MUTATION_SAMPLE_SEED`.

## Sibling Search

- Mental model: a green mutation workflow means the mutation surface is broad
  enough unless the score is low.
- Same layer: mutation summary denominator handling | decision: fix now |
  proof: direct `mutation_metrics()` call.
- Adjacent operation: scheduled sample selection | decision: fix now | proof:
  adapter `commands.sample` was empty and workflow seed lacked run id.
- Non-instance: ordinary pytest and closeout gates | decision: not the same
  class | proof: they do not claim mutation-test representativeness.

## Seam Risk

- Interrupt ID: mutation-score-suspicion
- Risk Class: contract-freeze-risk
- Seam: scheduled GitHub mutation workflow versus local score interpretation
- Disproving Observation: repeated green scheduled runs targeted only
  `scripts/control_plane_lib.py`.
- What Local Reasoning Cannot Prove: the next GitHub scheduled run's selected
  sample until the workflow executes on the pushed config.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Enable the repo-owned sample command in the quality adapter, include
`github.run_id` in the workflow seed for scheduled rotation, and make
zero-reachable or no-tests mutation summaries fail with explicit blocking
signals.
