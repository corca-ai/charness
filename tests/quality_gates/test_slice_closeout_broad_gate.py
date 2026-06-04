from __future__ import annotations

import json

from .support import ROOT, run_script


def test_broad_pytest_detector_matches_repo_python_closeout_command() -> None:
    from scripts.slice_closeout_broad_gate import is_broad_pytest_command

    assert is_broad_pytest_command(
        "pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    )
    assert not is_broad_pytest_command("pytest -q tests/quality_gates/test_goal_artifact_lib.py")


def test_run_slice_closeout_requires_lock_before_broad_pytest() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["verification_lock_required"] is True
    assert payload["executed_commands"] == []
    assert "broad pytest closeout requires" in payload["error"]


def test_run_slice_closeout_skip_broad_pytest_rehearsal_filters_pytest() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--skip-broad-pytest",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["skipped_broad_pytest_commands"]
    planned = [item["command"] for item in payload["planned_commands"]]
    assert not any(command.startswith("pytest -q tests/quality_gates tests/control_plane") for command in planned)


def test_run_slice_closeout_skip_broad_pytest_text_names_skipped_command() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--skip-broad-pytest",
        "--plan-only",
    )

    assert result.returncode == 0, result.stderr
    assert "Skipped broad pytest commands:" in result.stdout
    assert "pytest -q -m 'not release_only' tests/quality_gates tests/control_plane" in result.stdout


def test_run_slice_closeout_verification_lock_keeps_broad_pytest_in_plan() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--verification-lock",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert "verification_lock_required" not in payload
    planned = [item["command"] for item in payload["planned_commands"]]
    assert any(
        command.startswith("pytest -q -m 'not release_only' tests/quality_gates tests/control_plane")
        for command in planned
    )
