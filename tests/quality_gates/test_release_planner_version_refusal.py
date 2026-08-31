"""The release planner refuses an unspeakable adapter version at its own read site, not
by inheritance from a callee.

This row is deliberately recorded as WEAKER than the three gate rows it follows. Measured
at `dd5b6dee9`, the planner did not go silent under a refused version: it printed
`next_action=repair_adapter: Release adapter is invalid.` at exit 0 and left the two
`valid`-gated evidence packets null. What it emitted anyway was a plan asserting
`package_id: <the temp directory's own name>`, two paths under `packaging/` and `plugins/`
that do not exist, and `blockers: []`.

The row for `current_release` ALONE already made this exit 1, by inheritance:
`build_release_payload` runs before the three unconditional `data` reads and its
`SystemExit` escapes the `except Exception` around it. The refusal is positional:
`test_the_refusal_is_this_file_s_own_not_inherited_from_a_callee` is the test
that separates the two, by proving the refusal survives a callee that does not refuse.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.quality_gates.git_fixture_support import init_git_repo

from .support import ROOT

PLANNER = ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run.py"

# `output_dir`, NOT `release_record_path`. The latter is what this row's probe record first
# declared and it is a key NO adapter consumer reads -- `plan_release_prepared_stop` and
# `publish_release_claims_review` both DERIVE the record path from `output_dir`, so a second
# copy of the constant cannot drift. `check_probe_record --replay-stimulus` refused the
# record for it; this fixture carried the same dead key one commit longer, which is the
# record-and-test-disagree shape this family has now produced in both directions.
DECLARED = 'output_dir: charness-artifacts/release-mine\n'


def _repo(tmp_path: Path, adapter: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    # The planner asks git for the current branch on the arm that reaches a plan. Without
    # a repo here the speakable-version control would fail on git rather than on the
    # behavior it exists to pin — and a control that fails for the wrong reason proves
    # nothing about the refusal above it.
    init_git_repo(repo)
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLANNER), "--repo-root", str(repo)], capture_output=True, text=True
    )


def test_an_unspeakable_version_refuses_instead_of_planning_from_defaults(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "next_action" not in result.stdout


def test_a_speakable_but_otherwise_invalid_adapter_still_plans(tmp_path: Path) -> None:
    """The affordance this planner exists for is preserved.

    The refusal is narrow to a version this reader cannot speak — the one case where the
    planner cannot know what the repo declared. An adapter that is speakable but broken in
    some other way still gets a plan and its own next action, which is what an operator
    runs this command to obtain.
    """
    # `output_dir: 12345` is genuinely invalid (`output_dir must be a string`). The earlier
    # `release_record_path: 12345` was not invalid at all -- the resolver drops the unknown
    # key and reports zero errors -- so this test asserted its premise rather than testing it.
    result = _run(_repo(tmp_path, "version: 1\noutput_dir: 12345\n"))
    assert result.returncode == 0, result.stderr
    assert "next_action=" in result.stdout


def test_the_refusal_is_this_file_s_own_not_inherited_from_a_callee(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutation this row is actually about.

    `build_release_payload` is called near the top of `build_plan` and already refuses,
    so the CLI test above passes with or without the guard in this file. Replacing that
    callee with one that does NOT refuse isolates the guard: with it, `build_plan` still
    raises; without it, the planner falls through to the three unconditional `data` reads
    and plans from charness defaults.

    The Namespace comes from the planner's OWN `parse_args`, not hand-built. A hand-built
    one made the mutant die on a missing attribute — a kill for the wrong reason, which
    would have let a later refactor break this proof without failing it.
    """
    from tests.script_main import load_script_module

    # A UNIQUE module name, and the stubs installed through monkeypatch so they are undone.
    # The first cut used `plan_release_run_for_guard_test` — the same name
    # `test_requested_review_gate_version_refusal.py` loads the planner under — and stubbed
    # the module in place. That made the sibling's `plan_release_run` case DID NOT RAISE
    # whenever this file ran first: a green suite in one order and red in another, which
    # the standing lane missed and the changed-line producer's xdist run caught.
    module = load_script_module("plan_release_run_for_own_guard_isolation_test", PLANNER)
    monkeypatch.setattr(
        module, "build_release_payload",
        lambda repo_root: {"surface_versions": {"packaging_manifest": "1.2.3"}},
    )
    monkeypatch.setattr(
        module, "build_review_gate_payload", lambda repo_root, run_commands=True: {}
    )
    repo = _repo(tmp_path, "version: 9\n" + DECLARED)
    monkeypatch.setattr(sys, "argv", ["plan_release_run.py", "--repo-root", str(repo)])
    args = module.parse_args()
    with pytest.raises(SystemExit) as excinfo:
        module.build_plan(args)
    assert "does not speak" in str(excinfo.value)
