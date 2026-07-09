# Quality Review
Date: 2026-07-09

## Scope

Target boundary: autonomous follow-up on repo bugs, code quality, and test speed
after the broader quality repair.

Ambient repo findings: standing pytest remained under budget; release-only CLI
tests are the expensive path, while the actionable bug was incomplete A/B live
run config validation.

## Current Gates

- Healthy: focused A/B harness tests passed after the schema follow-up.
- Healthy: standing pytest passed before the final critique artifact was added,
  then exposed an invalid draft critique packet rather than a code failure.
- Weak: broad validation must be rerun after this artifact lands, because the
  previous standing run failed on an intentionally removed packet draft.
- Deferred: no live Cautilus or `cautilus evaluate` command was run; this was
  deterministic local validation.

## Runtime Signals

- runtime source: timing capture is missing for a dedicated runtime-signals
  refresh in this follow-up; direct command measurements from this turn provide
  the local evidence.
- runtime hot spots: timing capture is missing for structured runtime hot-spot
  reporting in this follow-up; targeted command observations are recorded under
  Advisory and Commands Run.
- coverage gate: focused A/B harness pytest passed, and standing pytest will be
  rerun after artifact validation.
- evaluator depth: deterministic gates only; no evaluator-backed behavior proof
  was needed for the local CLI pre-spend validation bug.

## Healthy

- `scripts/run_skill_efficiency_ab.py` is now 400/480 Python code lines after
  extracting validation, up from a riskier monolith posture.
- `tests/test_skill_efficiency_ab.py` passed 59 tests in 1.28s after the
  follow-up.
- Packaging source/mirror validation passed after `sync_root_plugin_manifests.py`.

## Weak

- The worker commit initially left a `--out-dir` path where invalid config
  `name` could reach selftest; fresh-eye review caught it and the follow-up fixed
  it.
- Test-speed risk is concentrated in release-only install/update lifecycle tests,
  not in the standing gate. Direct `pytest tests/charness_cli` is a misleading
  speed proxy unless release markers are respected.

## Missing

- Missing: no safe pruning of release-only lifecycle tests was attempted; the
  measured bottleneck is real but outside the standing local gate.
- Missing: no remote CI or pushed-branch proof; this branch remains local.

## Deferred

- Deferred: broader helper API simplification for
  `run_skill_efficiency_ab_validation.py`; current CLI contract is covered.
- Deferred: Cautilus local install is behind latest per `update_tools.py`
  advisory, but tool upgrades are outside this code-quality slice.

## Advisory

- structural review result: evidence: command
  `python3 scripts/check_changed_surfaces.py --repo-root . --json --paths ...`;
  the quality planner still points to repo-python, plugin export, and
  integration/control-plane checks for this slice; those surfaces were synced
  and verified.
- prose review result: evidence: artifact
  [critique record](../critique/2026-07-09-ab-schema-validation-followup-critique.md);
  code critique found one real CLI bypass, one defensive default-path order
  test, and no remaining ship blocker after counterweight.
- active measurement note — command evidence: pytest module runner with
  `not release_only` marker over `tests/charness_cli` and duration reporting;
  evidence: 95 passed, 46 deselected, 14.06s.
- active measurement note — command evidence: pytest module runner over
  `tests/charness_cli` with duration reporting; evidence: 141 passed, 174.73s,
  showing release-only tests dominate the misleading direct subset timing.

## Delegated Review

- Delegated Review: executed — worker implemented the helper extraction and
  initial validation tests; two fresh-eye reviewers and one counterweight
  reviewer inspected the code.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  executed — release-only tests were measured separately from the standing
  runner, preventing a false speed optimization.

## Commands Run

- command: pytest module runner over `tests/charness_cli` with duration reporting.
- command: pytest module runner over `tests/charness_cli` with `not release_only` marker and duration reporting.
- command: pytest module runner over `tests/test_skill_efficiency_ab.py`.
- command: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- command: `python3 scripts/validate_packaging.py --repo-root .`
- command: `python3 scripts/validate_packaging_committed.py --repo-root .`
- command: `python3 scripts/check_python_lengths.py --repo-root . --headroom --paths scripts/run_skill_efficiency_ab.py scripts/run_skill_efficiency_ab_validation.py`
- command: `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`

## Recommended Next Quality Moves

- active final-closeout-rerun — capability_needed=honest green closeout; next_center=current diff plus artifacts; transformation=rerun artifact validators and standing closeout after this record lands; proof_boundary=validator and closeout output; enforcement_posture=advisory.
- passive release-only-cli-speed because it is outside the standing local gate; capability_needed=faster release confidence; next_center=managed install/update lifecycle fixtures; transformation=separate a small binary smoke from repeated contract checks; proof_boundary=release-only duration report plus release gate; enforcement_posture=no-gate until scoped.
- passive cautilus-update-advisory because tool update is machine-local and outside this patch; capability_needed=current evaluator binary; next_center=operator tool update; transformation=manual Cautilus 0.19.0 update when evaluator work resumes; proof_boundary=`update_tools.py --json`; enforcement_posture=no-gate.

## History

- [2026-07-03 pytest suite audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
