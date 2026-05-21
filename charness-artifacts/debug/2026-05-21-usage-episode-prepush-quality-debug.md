# Usage Episode Pre-Push Quality Debug
Date: 2026-05-21

## Problem

`git push origin main` failed in the pre-push quality gate after the #188
commit because two repo quality contracts caught missed consequences of the
new usage-episode closeout emitter:

- `validate-attention-state-visibility`: `scripts/run_slice_closeout.py:
  declared states ['disabled'] do not match detected states ['disabled',
  'no_adapter']`.
- `check-python-lengths`: `scripts/run_slice_closeout.py: file length 519
  exceeds limit 480`.

After extracting the emitter, the same length contract also caught the enlarged
test file: `tests/quality_gates/test_surface_obligations.py: file length 965
exceeds limit 800`.

## Correct Behavior

Given a task-completing slice changes closeout behavior, when pre-push runs,
then attention-state no-op outcomes must be declared as visible, production
and test files must stay below the file length ceiling, and the plugin export
must keep parity with the root implementation.

## Observed Facts

- The earlier `run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
  passed because the closeout surface set did not include
  `validate-attention-state-visibility` or `check-python-lengths`.
- Full pre-push ran `./scripts/run-quality.sh --read-only` and failed at
  `validate-attention-state-visibility` and `check-python-lengths`.
- The new emitter added a `no_adapter` exit-zero state and about 174 lines to
  `run_slice_closeout.py`.
- Moving the emitter into `scripts/slice_closeout_usage_episode.py` reduced
  `run_slice_closeout.py` to 366 lines, but the moved tests still left
  `tests/quality_gates/test_surface_obligations.py` above its 800-line limit.

## Reproduction

1. Add the usage-episode emitter directly to `scripts/run_slice_closeout.py`.
2. Add four tests directly to
   `tests/quality_gates/test_surface_obligations.py`.
3. Run `git push origin main` or the equivalent read-only quality gate.
4. Observe attention-state and Python length failures.

## Candidate Causes

- The emitter introduced a new attention-state term without updating the
  visibility declaration.
- The implementation belonged in a helper module, not the closeout
  orchestrator.
- The test cases belonged in a focused usage-episode test file, not the broad
  surface-obligation test module.
- The closeout validator surface was narrower than pre-push and therefore did
  not exercise the full local quality contract before commit.

## Hypothesis

If the failure is contract drift caused by oversized orchestration/test files
and an undeclared attention state, then extracting the emitter, declaring the
helper states, splitting the tests, and syncing the plugin export should make
the targeted gates pass without relaxing any validator.

## Verification

- `python3 scripts/validate_attention_state_visibility.py --repo-root .`
  passed and reported 49 declared files.
- `python3 scripts/check_python_lengths.py --repo-root .` passed and reported
  508 files.
- `pytest -q tests/quality_gates/test_slice_closeout_usage_episode.py
  tests/quality_gates/test_surface_obligations.py::test_run_slice_closeout_executes_sync_then_verify`
  passed.
- `ruff check scripts/run_slice_closeout.py
  scripts/slice_closeout_usage_episode.py
  plugins/charness/scripts/run_slice_closeout.py
  plugins/charness/scripts/slice_closeout_usage_episode.py
  tests/quality_gates/test_slice_closeout_usage_episode.py
  tests/quality_gates/test_surface_obligations.py` passed.

## Root Cause

The implementation treated the existing closeout gate as sufficient proof for
pre-push quality, but the change also crossed two standing repository-wide
contracts: attention-state visibility and Python file length. The emitter was
functionally correct but placed in the wrong module shape, and its new
`no_adapter` state had not been declared as a visible closeout payload state.

## Detection Gap

The standing pre-push gate caught the issue before publication. The narrower
slice closeout gate did not include the length and attention-state checks for
this changed path set, so the defect was detected one phase later than ideal.

## Sibling Search

- Mental model: a passing slice closeout means the commit is pre-push-ready.
- Same pattern: new exit-zero no-op states such as `no_adapter`, `disabled`,
  and `skipped` need visibility declarations. Decision: added a declaration
  for `scripts/slice_closeout_usage_episode.py`; proof: attention-state gate.
- Same pattern: adding a feature directly to an orchestrator can cross file
  length ceilings. Decision: moved emitter behavior into a helper module;
  proof: length gate.
- Same pattern: broad test modules can silently absorb unrelated feature
  tests. Decision: split usage-episode tests into
  `tests/quality_gates/test_slice_closeout_usage_episode.py`; proof: length
  gate.
- Export sibling: root helper modules used by plugin scripts need checked-in
  plugin copies. Decision: copied both closeout modules into
  `plugins/charness/scripts/`; proof: ruff and closeout sync.

## Seam Risk

- Interrupt ID: usage-episode-prepush-quality
- Risk Class: contract-freeze-risk
- Seam: slice closeout proof versus full pre-push proof.
- Disproving Observation: targeted attention-state, length, focused pytest,
  and ruff gates pass after the repair.
- What Local Reasoning Cannot Prove: that every future closeout path will select
  the same quality gates as pre-push for newly added helper files.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep the validators as-is. For future closeout or telemetry changes, check
attention-state visibility and file length before commit when adding new
exit-zero states or more than a small helper block to an existing orchestrator
or broad test module.

## Related Prior Incidents

- [2026-05-19 issue 175 advisory recurrence](./2026-05-19-issue-175-advisory-recurrence.md):
  prior recurrence behind attention-state visibility enforcement.
