from __future__ import annotations

import json
import shutil
from pathlib import Path

from .support import (
    ROOT,
    run_cli,
)

GOAL_PATH = "charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md"


def _write_discussion_goal(repo: Path) -> Path:
    goal = repo / "charness-artifacts" / "goals" / "discussion-warning.md"
    goal.parent.mkdir(parents=True, exist_ok=True)
    goal.write_text(
        "# Achieve Goal: Discussion warning\n\n"
        "Status: draft\n"
        "Activation: `/goal @charness-artifacts/goals/discussion-warning.md`\n\n"
        "## Non-Goals\n\nDo not close #279 until proof-bearing closeout.\n\n"
        "Discuss before activation: confirm issue closeout timing first.\n\n",
        encoding="utf-8",
    )
    return goal


def _write_generic_draft_frame_goal(repo: Path) -> Path:
    goal = repo / "charness-artifacts" / "goals" / "generic-draft-frame.md"
    goal.parent.mkdir(parents=True, exist_ok=True)
    goal.write_text(
        "# Achieve Goal: Generic draft frame\n\n"
        "Status: draft\n"
        "Activation: `/goal @charness-artifacts/goals/generic-draft-frame.md`\n\n"
        "## Active Operating Frame\n\n"
        "- Current slice: before activation.\n"
        "- Next action: activate with `/goal @charness-artifacts/goals/generic-draft-frame.md`.\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n\n"
        "## Agent Verification Plan\n\nRun the suite; assert Z.\n",
        encoding="utf-8",
    )
    return goal


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


def test_goal_check_blocks_unresolved_activation_discussion(tmp_path: Path) -> None:
    target_repo = tmp_path / "target"
    target_goal = _write_discussion_goal(target_repo)

    result = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(target_repo),
        "--goal-path",
        "charness-artifacts/goals/discussion-warning.md",
        "--charness-checkout",
        str(ROOT),
        "--pursue-ready",
        "--json",
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pursue_ready"] is False
    assert payload["activation_ready"] is False
    assert payload["shape_ready"] is True
    assert payload["discussion_resolved"] is False
    assert payload["path"] == str(target_goal.resolve())
    assert "unresolved" in payload["activation_discussion_warning"]
    assert "not marked resolved" in payload["reason"]

    concise = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(target_repo),
        "--goal-path",
        "charness-artifacts/goals/discussion-warning.md",
        "--charness-checkout",
        str(ROOT),
        "--pursue-ready",
    )

    assert concise.returncode == 1, concise.stderr
    assert "PURSUE_READY: no" in concise.stdout
    assert "REASON:" in concise.stdout
    assert "not marked resolved" in concise.stdout


def test_goal_check_concise_output_surfaces_draft_frame_warning(tmp_path: Path) -> None:
    target_repo = tmp_path / "target"
    target_goal = _write_generic_draft_frame_goal(target_repo)

    json_result = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(target_repo),
        "--goal-path",
        "charness-artifacts/goals/generic-draft-frame.md",
        "--charness-checkout",
        str(ROOT),
        "--pursue-ready",
        "--json",
    )

    assert json_result.returncode == 0, json_result.stderr
    payload = json.loads(json_result.stdout)
    assert payload["path"] == str(target_goal.resolve())
    assert payload["draft_frame_disposition_present"] is False
    assert "lacks lifecycle disposition" in payload["draft_frame_warning"]

    concise = run_cli(
        "goal",
        "check",
        "--repo-root",
        str(target_repo),
        "--goal-path",
        "charness-artifacts/goals/generic-draft-frame.md",
        "--charness-checkout",
        str(ROOT),
        "--pursue-ready",
    )

    assert concise.returncode == 0, concise.stderr
    assert "PURSUE_READY: yes" in concise.stdout
    assert "WARNING: draft Active Operating Frame lacks lifecycle disposition" in concise.stdout


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
