# Debug: #274 Mutation Workflow Tokei Dependency
Date: 2026-06-02
Issue: #274

## Problem

The latest scheduled mutation workflow comments on #274 report
`StrykerJS JSON report missing` for runs on `56e9ac59` and `4c3dcbe1`, with no
mutation sample manifest generated.

## Correct Behavior

Given a full scheduled mutation run on `main`, when the workflow selects a
Python mutation sample and then runs the full mutation command, then every
validation binary required by the sampled pytest command must already be on
PATH. If the Python sample fails before the JS command can run, the issue body
should not be read as proof that StrykerJS itself failed.

## Observed Facts

- `gh run view 26799230370 --json ...` shows the latest run failed in
  `Select mutation sample`; `Run mutation` was skipped.
- The workflow log for run `26799230370` shows full pytest failed during the
  test-command coverage probe because `scripts/check_python_lengths.py` could
  not find `tokei` on PATH.
- The same log then ran the summary step, which reported both missing
  `cosmic-ray-dump.jsonl` and missing `reports/mutation/stryker-js.json`. <!-- reproduction-source -->
- `.agents/quality-adapter.yaml` defines `commands.full` as
  `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode full && npm
  run test:mutation:js`, so StrykerJS only runs after the Python full command
  succeeds.
- The checked-in workflow installed Python mutation requirements and JS
  dependencies, but did not install the `tokei` validation binary before
  `sample_mutation_files.py` invoked the coverage probe.
- `integrations/tools/tokei.json` states that Python length gates require
  `tokei` and must fail closed when it is unavailable.
- StrykerJS docs confirm the JSON reporter is enabled by `reporters: ["json"]`
  and `jsonReporter.fileName`; the local `stryker.config.mjs` already sets
  `reports/mutation/stryker-js.json`. <!-- reproduction-source -->
- Local `reports/mutation/stryker-js.log` shows StrykerJS can write <!-- reproduction-source -->
  `reports/mutation/stryker-js.json` when the JS runner actually executes. <!-- reproduction-source -->

## Reproduction

Current remote reproduction is the scheduled workflow run:

```bash
gh run view 26799230370 --json conclusion,headSha,event,status,jobs
gh run view 26799230370 --log
```

The earliest failure is in `Select mutation sample`, before the workflow reaches
the `Run mutation` step.

## Candidate Causes

- Missing validation binary in the GitHub Actions environment.
- StrykerJS JSON reporter misconfigured.
- Summary step misclassifying an upstream sample failure as a JS report failure.

## Hypothesis

If the mutation workflow installs `tokei` before `Select mutation sample`, then
the sampled pytest coverage probe can run the length-gate tests instead of
failing closed before mutation execution. If StrykerJS still fails after that,
the next issue comment should show a true JS runner failure rather than a
missing report caused by skipped execution.

## Verification

- PASS: `python3 -m pytest -q
  tests/quality_gates/test_quality_mutation_testing.py::test_checked_in_mutation_workflow_uses_repo_owned_requirements
  tests/quality_gates/test_quality_mutation_testing.py::test_checked_in_mutation_workflow_installs_length_gate_binary_before_sampling`
  (2 passed).
- PASS: `python3 scripts/check_github_actions.py --repo-root .`.
- PASS: local existing StrykerJS log shows `JsonReporter` wrote
  `reports/mutation/stryker-js.json` in a run where StrykerJS executed. <!-- reproduction-source -->
- NOT RUN: a fresh GitHub scheduled or `workflow_dispatch` mutation run after
  this fix; remote proof remains pending until publication.

## Root Cause

The scheduled mutation workflow was missing a validation dependency that its own
sampled pytest coverage command requires. The `check_python_lengths.py` tests
fail closed without `tokei`, so `sample_mutation_files.py` failed before
producing a sample manifest. Because the full mutation command never ran, the
later missing StrykerJS JSON report was a downstream symptom, not the root
failure.

## Detection Gap

- mutation workflow dependency setup | no test asserted that the checked-in
  workflow installs `tokei` before mutation sampling | added
  `test_checked_in_mutation_workflow_installs_length_gate_binary_before_sampling`.
- issue summary for skipped run step | summary can still report missing JS JSON
  after an upstream sample failure | not fixed in this slice; monitor after the
  dependency fix and consider a separate diagnostic-reporting issue if it
  recurs.

## Sibling Search

- Mental model: mutation workflow setup covered runner dependencies, but not
  validation binaries used by the sampled test command.
- workflow setup axis: Python requirements and npm dependencies were installed;
  decision: add `tokei` install before adapter/sample phase; proof: workflow
  diff and test pin the ordering.
- local gate axis: local machines can already have `tokei`, masking the CI gap;
  decision: make scheduled workflow explicit; proof: run log had missing binary.
- summary axis: `check_mutation_suite_score.py` can emit downstream missing
  report summaries when upstream run phases skipped; decision: defer unless
  dependency fix does not recover #274; proof: current issue body is misleading
  but root failure is earlier.
- Stryker config axis: JSON reporter path might be wrong; decision: not the root
  cause for the current failure; proof: config includes `json` reporter and
  local Stryker run wrote the expected report path.

## Seam Risk

- Interrupt ID: issue-274-mutation-workflow-tokei-dependency
- Risk Class: operator-visible-recovery
- Seam: GitHub Actions runner environment versus local validation environment.
- Disproving Observation: GitHub issue comments reported missing StrykerJS JSON,
  but the workflow log shows the run stopped in mutation sample selection before
  StrykerJS execution.
- What Local Reasoning Cannot Prove: whether the next scheduled or manual
  workflow run fully recovers #274 after publication.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md

## Prevention

Pin workflow-level installation of validation binaries that sampled test
commands require. Do not rely on local operator machines having those binaries
when the scheduled workflow runs the same tests on GitHub-hosted runners.
