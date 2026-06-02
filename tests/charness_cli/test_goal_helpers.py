from __future__ import annotations

import json
import shutil
from pathlib import Path

from .support import (
    ROOT,
    run_cli,
)

GOAL_PATH = "charness-artifacts/goals/2026-06-02-enforce-recent-lessons-broad-gate-lock.md"


def test_goal_check_uses_stable_cli_surface_for_achieve_helper() -> None:
    result = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(ROOT),
        "--goal-path",
        GOAL_PATH,
        "--pursue-ready",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pursue_ready"] is True
    assert payload["path"].endswith(GOAL_PATH)


def test_goal_check_resolves_relative_goal_path_under_target_repo(tmp_path: Path) -> None:
    target_repo = tmp_path / "target"
    target_goal = target_repo / "charness-artifacts" / "goals" / "relative-only.md"
    target_goal.parent.mkdir(parents=True)
    shutil.copy2(ROOT / GOAL_PATH, target_goal)

    result = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(target_repo),
        "--goal-path",
        "charness-artifacts/goals/relative-only.md",
        "--charness-checkout",
        str(ROOT),
        "--pursue-ready",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pursue_ready"] is True
    assert payload["path"] == str(target_goal.resolve())


def test_goal_check_help_names_stable_helper_surface() -> None:
    result = run_cli("goal", "check", "--help")

    assert result.returncode == 0, result.stderr
    assert "--charness-checkout" in result.stdout
    assert "goal artifact" in result.stdout


def test_goal_check_missing_helper_error_names_stable_search_path(tmp_path: Path) -> None:
    checkout = tmp_path / "charness-checkout"
    manifest = checkout / "packaging" / "charness.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"version": "fixture"}\n', encoding="utf-8")

    result = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(ROOT),
        "--goal-path",
        GOAL_PATH,
        "--charness-checkout",
        str(checkout),
    )

    assert result.returncode == 1
    assert "check_goal_artifact.py" in result.stderr
    assert "searched stable source checkout" in result.stderr
    assert "--charness-checkout <path>" in result.stderr
    assert "plugins/cache/local/charness" not in result.stderr
