# Mutation Coverage Probe Debug
Date: 2026-05-25

## Problem

GitHub issue #215 stayed open after the original Python mutation score failure
because the latest scheduled mutation run on `3873a73` failed before mutation
execution. The `Select mutation sample` step ran the full pytest coverage probe
and then `coverage json` failed with `No source for code:
/tmp/pytest-of-runner/.../repo/scripts/agent_browser_runtime_guard.py`; because
the sample step failed, neither `cosmic-ray-dump.jsonl` nor
`stryker-js.json` was produced.

## Correct Behavior

Given mutation sample selection wraps the repo test command in coverage, when
tests execute copied or generated helper files outside the repo root and those
temporary files disappear before `coverage json`, then mutation sampling should
ignore those outside-repo sources and still emit the mutation coverage JSON.
<!-- reproduction-source -->
Given the sample step succeeds, the workflow can continue to Python and JS
mutation execution and report real survivor scores instead of a missing-report
placeholder.

## Observed Facts

- `gh issue view 215` showed the original body at `6afea153` failed Python
  mutation score, `79.3%` versus the `80%` threshold.
- Later issue comments from GitHub Actions showed the current failure on
  `3873a73`: `StrykerJS JSON report missing` with no sample manifest.
- `gh run view 26373389015 --log-failed` showed the earlier step failed with
  `No source for code: '/tmp/pytest-of-runner/.../repo/scripts/agent_browser_runtime_guard.py'`
  and `test-command coverage probe failed with exit 1`.
- `run_test_coverage` wrote a temporary coverage rcfile without a `source`
  boundary, so coverage tried to include files executed by tests even when they
  lived under volatile pytest temp repos outside `/home/hwidong/codes/charness`.
- A local sample run after adding `source = <repo_root>` completed the coverage
  json step and printed `Wrote JSON report to .../reports/mutation/test-coverage.json`.

## Reproduction

- Failing hosted reproduction: GitHub Actions mutation run
  `26373389015` on commit `3873a73`.
- Local focused reproduction: a regression test creates a repo source, executes
  and deletes an outside temp Python file during a pytest run, then calls
  `run_test_coverage`; before the fix this shape could make `coverage json`
  chase deleted non-repo source.
- Local workflow reproduction after the fix:
  `MUTATION_BASE_SHA=6ad879dc3c98fda9c71e36d826b2c6095c734d7b MUTATION_HEAD_SHA=HEAD ... python3 scripts/sample_mutation_files.py --repo-root .`
  completed successfully.

## Candidate Causes

- Coverage source boundary was absent, so temporary fixture repos became part of
  the mutation coverage data.
- The JS mutation runner was healthy but never reached because sample selection
  failed first.
- Python survivor tests were too broad and did not kill branch/format mutants
  from the original #215 body.

## Hypothesis

If mutation coverage collection sets `source = <repo_root>` in its generated
rcfile, then coverage will ignore deleted temp sources outside the repository
and sample selection will reach manifest generation. If survivor-adjacent tests
also pin runtime profile branch selection, setup parent creation, and GitHub
Actions JSON formatting, the original weak mutation surface improves without
turning the fix into a broad refactor.

## Verification

- Focused tests passed:
  `python3 -m pytest -q tests/quality_gates/test_mutation_coverage_probe.py ...`
  reported `7 passed`.
- Local sample selection completed after the fix:
  `1524 passed, 4 skipped, 57 deselected`, `Combined 1186 files, skipped 596`,
  `Wrote JSON report to .../reports/mutation/test-coverage.json`, and
  `sample (5/5): ...`.
- `npm run test:mutation:js:dry-run` passed and wrote the StrykerJS dry-run log;
  this proves the runner/report path is locally reachable in dry-run mode, not
  that the hosted full mutation step has already rerun.
- `./scripts/run-quality.sh --read-only` passed: `68 passed, 0 failed`.

## Root Cause

The mutation sampler assumed the full pytest coverage probe only needed to
collect repository-owned source. In practice, repo tests execute copied helper
scripts inside pytest temp repos; those temp files can disappear before
`coverage json`. Without an explicit coverage `source` boundary, coverage
recorded those outside-repo paths and later failed when it could not read them.
That turned a recoverable outside-repo fixture detail into a blocking mutation
workflow failure and prevented the JS mutation report from being generated.

## Detection Gap

- mutation sample coverage probe | deleted outside-repo temp sources could
  break `coverage json` | add a regression that executes and deletes an
  outside-repo Python file while verifying only repo-owned files enter the
  mutation coverage JSON.
- original Python survivor surface | CLI smoke tests did not pin branch and
  format contracts | add direct tests for runtime profile default/named
  branches, nested setup parent creation, and stable UTF-8 sorted JSON output.
- plugin packaging surface | script change can drift from plugin mirror | run
  `sync_root_plugin_manifests.py` before validation and keep preamble test in
  the closeout proof.

## Sibling Search

- Mental model: "the pytest command is repo-scoped, so coverage output is
  effectively repo-scoped." Decision: same bug, fixed now for mutation coverage
  probe. Proof: #215 run log and outside-repo deleted-source regression.
- Same layer: other coverage consumers that read coverage JSON already call
  `_coverage_relative_path` and drop outside repo paths after JSON exists.
  Decision: diagnostic-only for this slice. Proof: failure happened before JSON
  could be produced.
- Abstraction up: generated probe rcfiles that lack source/include boundaries.
  Decision: same class, inspect when adding new probe helpers. Proof: this fix
  is in the shared mutation sampling rcfile writer.
- Specialization down: setup seed scripts that rely on `parents=True`, runtime
  profile default/named branch selection, and machine-readable JSON formatting.
  Decision: bundle cheap survivor tests now. Proof: #215 survivor sample and
  focused tests.

## Seam Risk

- Interrupt ID: issue-215-mutation-coverage-probe-source-boundary
- Risk Class: contract-freeze-risk
- Seam: GitHub Actions scheduled mutation workflow plus local pytest temp
  lifecycle
- Disproving Observation: local sample selection now reaches coverage JSON and
  manifest generation.
- What Local Reasoning Cannot Prove: the next hosted scheduled mutation run on
  GitHub Actions.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

Keep generated coverage probes explicitly repo-scoped, and add branch-level
tests when mutation survivors show that broad CLI smoke tests are observing the
right end state without pinning the contract that matters.
