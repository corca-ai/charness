Fix mutation changed-line subprocess coverage

Close #354.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #354 Mutation test regression on main.

JTBD: maintainers need scheduled mutation changed-line coverage to report real
coverage gaps, not false negatives caused by test subprocesses escaping the
coverage-instrumented Python interpreter.

Root Cause: quality-gate script tests used `tests/quality_gates/support.py`
`run_script()` to invoke `python3` through caller-provided `PATH`. On GitHub
Actions, tests that prepend fake tool directories can resolve to the system
`/usr/bin/python3` instead of the current coverage-enabled interpreter, so
subprocess coverage for issue scripts is lost while the tests themselves still
pass.

Debug Artifact:
`charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`.

Siblings: literal-`python3` subprocess helpers | decision: fix the
quality-gate helper because it is the #354 failing path, and defer
`tests/control_plane/support.py` because it is outside this issue's changed-line
coverage evidence | proof: causal fresh-eye review plus local changed-line
coverage rerun reported no #354 blockers after the helper fix.

Resolution brief: make the quality-gate subprocess helper invoke
`sys.executable`, add a PATH-shadowing regression test for the helper, and keep
the broader literal-`python3` audit out of scope unless another failing path
requires it.

Implementation: updated `tests/quality_gates/support.py`, added
`test_run_script_uses_current_python_when_path_shadows_python`, updated the
`nose` integration and inventory scanner for the current `nose 0.6.0` command
surface, synced plugin exports, removed stale issue/version anchors from
reusable exported guidance, and added routine medium-effort reviewer policy for
bounded fresh-eye checks.

Prevention: focused tests prove the PATH-shadowing failure mode, local
changed-line coverage over the scheduled run's base/head reports no blockers,
and nose fake-boundary tests now assert `--min-size 24` with removed legacy
flags absent.

Tests: focused issue/nose/control-plane tests passed; broad non-release pytest
passed with `2799 passed, 4 skipped, 26 deselected`; deterministic integration,
skill, packaging, markdown, secret, public-skill, inference-interpretation,
gitignore-scan-hygiene, critique-artifact, and support/tool dry-run validators
passed locally. Remote scheduled mutation proof is not claimed until this
direct commit is pushed and CI runs.

Critique: charness-artifacts/critique/2026-06-11-issue-354-mutation-coverage-resolution.md
