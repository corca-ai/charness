# Debug: #273 Mutation Gate Helper Coverage
Date: 2026-06-01
Issue: #273

## Problem

The scheduled mutation gate opened #273 because overall mutation status failed
even though the reachable mutation score passed. The latest issue comment named
changed-line coverage blockers in `scripts/host_log_probe_lib.py` and survivor
samples in `scripts/portable_artifact_lib.py`.

## Correct Behavior

Changed helper branches that are part of the mutation pool should have local
coverage at their exact branch/line boundaries, and sampled survivor shapes
should either be killed by tests or removed by simpler equivalent code.

## Observed Facts

- The latest #273 comment named `scripts/host_log_probe_lib.py` changed-line
  targets for goal-window parsing and Codex session path handling.
- The same comment named `scripts/portable_artifact_lib.py` survivor samples in
  path-key/list handling and home-path sanitization.
- Broad quality had passed before the scheduled mutation issue exposed this
  exact branch proof gap.

## Reproduction

Use the scheduled failure range with mutation-gate coverage:

```bash
python3 scripts/check_changed_line_mutation_coverage.py --repo-root . \
  --base-sha dbd9f8a449119451df6e30c201811ef6ce940551 \
  --head-sha aff563f17b204ee120bde875cec9a0524d0ba27a
```

## Candidate Causes

- Helper branch behavior was only indirectly covered through broader feature
  tests.
- The latest sampled survivor shapes in `portable_artifact_lib.py` reflected
  redundant branch structure rather than useful separate behavior.
- Local read-only quality does not run scheduled mutation sampling.

## Hypothesis

If the exact host-log goal-window branches are asserted directly and the
portable-artifact path sanitizer is simplified around its real distinctions,
then the mutation gate's changed-line classifier will no longer report blockers
for the latest #273 range.

## Verification

- PASS: `python3 -m pytest -q tests/test_portable_artifact_lib.py
  tests/quality_gates/test_retro_host_log_probe.py` (17 passed).
- PASS: `python3 scripts/check_changed_line_mutation_coverage.py --repo-root .
  --base-sha 36b2c7880331a4942dbd7521dc9cdfbc1d5f95c3 --head-sha 8dbfdae`
  reported `blocking: []`.
- PASS: `python3 scripts/check_changed_line_mutation_coverage.py --repo-root .
  --base-sha dbd9f8a449119451df6e30c201811ef6ce940551 --head-sha
  aff563f17b204ee120bde875cec9a0524d0ba27a --reuse-coverage` reported
  `blocking: []`.

## Root Cause

Bug: a standing quality gate on `main` reported a real changed-line proof
failure.

Support-helper branches were covered by broad behavior tests but not pinned at
the exact branch and mutant-observable boundaries used by the mutation gate:

- goal metric window parsing branches for missing, absent, malformed, and
  non-string Codex session path states;
- portable path sanitization branches for path-key detection, path-list versus
  ordinary-list handling, and root-home path replacement.

## Detection Gap

- host metric window parsing | missing focused tests for missing/absent/invalid
  path states | added direct tests in `test_retro_host_log_probe.py`.
- portable artifact sanitization | missing focused tests for key classification
  and root-home guard | added direct tests in `test_portable_artifact_lib.py`.
- scheduled mutation sampling | not part of the standing local read-only gate |
  verified with `check_changed_line_mutation_coverage.py`.

## Sibling Search

Mental model: "feature-level tests plus broad quality are enough for helper
branches." Structural siblings are support helpers with CLI/error/path branches,
subprocess-only entrypoints, duplicated parser helpers, or sampler nodeid
selection.

Scanned/considered siblings:

- `scripts/host_log_probe_lib.py`: bundled through focused tests.
- `scripts/portable_artifact_lib.py`: bundled through focused tests and branch
  simplification.
- `scripts/report_usage_episodes.py`, `scripts/check_symbol_residue.py`, and
  handoff chunker CLI helpers: not in the latest #273 blocker after coverage was
  refreshed; defer until sampled again.
- `goal_artifact_closeout_evidence.py` and
  `goal_artifact_coordination_floors.py`: covered by the #261 disposition path;
  remaining survivor policy stays open in #261.

## Seam Risk

- Interrupt ID: issue-273-mutation-gate-helper-coverage
- Risk Class: none
- Seam: scheduled GitHub mutation workflow samples changed helpers after local
  commits have passed normal read-only quality.
- Disproving Observation: local changed-line classifier returns `blocking: []`
  for the same base/head range once the refreshed coverage report includes the
  helper branches.
- What Local Reasoning Cannot Prove: the next remote scheduled run will execute
  on the pushed commit and close the issue automatically.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md

## Fix

Added focused tests for the latest `host_log_probe_lib.py` changed-line targets
and simplified `portable_artifact_lib.py` branch shapes so the sampled survivors
no longer represent untested behavior.

## Prevention

When mutation reports name changed-line blockers, bind the fix to the exact
helper branches and re-run the gate-owned changed-line classifier. Do not treat
plain broad quality as proof for this class.
