from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_cli


def test_goal_run_help_uses_issue_native_identity() -> None:
    result = run_cli("goal", "run", "--help")

    assert result.returncode == 0, result.stderr
    assert "--objective" in result.stdout
    assert "/goal" in result.stdout
    assert "#N" in result.stdout
    assert "local goal-file state" not in result.stdout


def test_goal_check_is_removed_from_the_supported_cli_surface() -> None:
    result = run_cli("goal", "check", "--help")

    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert "goal_run_pickup.py" not in result.stderr
    assert "check_goal_artifact.py" not in result.stderr


def test_goal_run_missing_current_pickup_reports_the_actual_surface(tmp_path: Path) -> None:
    checkout = tmp_path / "charness-checkout"
    manifest = checkout / "packaging" / "charness.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"version": "fixture"}\n', encoding="utf-8")

    result = run_cli(
        "goal",
        "run",
        "--repo-root",
        str(ROOT),
        "--objective",
        "/goal #724",
        "--charness-checkout",
        str(checkout),
    )

    assert result.returncode == 1
    assert "goal_run_pickup.py" in result.stderr
    assert "issue-native Goal Run" in result.stderr
    assert "current pickup helper" in result.stderr
    assert "check_goal_artifact.py" not in result.stderr


def test_goal_run_wrapper_keeps_target_repo_and_objective_in_help_contract() -> None:
    result = run_cli("goal", "run", "--help")

    assert result.returncode == 0, result.stderr
    assert "Target repository containing the Goal Run" in result.stdout
    assert "Exact issue-native objective" in result.stdout
