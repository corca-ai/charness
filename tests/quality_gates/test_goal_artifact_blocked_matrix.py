"""Tests for the pre-block remaining-boundary-matrix floor.

`blocked` is a whole-goal status; before flipping to it a goal must classify
every external/live proof lane so one blocked boundary cannot mark the whole goal
stuck while a runnable lane remains.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_LIB = _ROOT / "skills/public/achieve/scripts/goal_artifact_lib.py"
_MATRIX = _ROOT / "skills/public/achieve/scripts/goal_artifact_blocked_matrix.py"
_CHECKER = _ROOT / "skills/public/achieve/scripts/check_goal_artifact.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gal = _load(_LIB, "goal_artifact_lib")
bm = _load(_MATRIX, "goal_artifact_blocked_matrix")

# A `Created:` date on/after the rule landing date so the floor applies.
POST_RULE = "2026-06-18"
# A `Created:` date before the rule so the goal is grandfathered.
PRE_RULE = "2026-06-06"

_APPROVAL_LANE = "- Lane: github publish | classification: approval-required | next: operator approval to push"
_RUNNABLE_LANE = "- Lane: ceal-dev apply/restart | classification: preauthorized-runnable | next: repo preauthorized apply"


def _matrix_section(*lanes: str) -> str:
    return "\n## Remaining Boundary Matrix\n\n" + "\n".join(lanes) + "\n"


def _scaffold(tmp_path: Path, date: str = POST_RULE) -> Path:
    gal.upsert_goal(tmp_path, date=date, slug="g", title="T")
    return gal.goal_path(tmp_path, date, "g")


def _append(path: Path, addition: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + addition, encoding="utf-8")


# --- check() lib-level -------------------------------------------------------


def test_check_grandfathers_pre_rule_goal() -> None:
    text = f"Created: {PRE_RULE}\n## Goal\n"
    report = bm.check(text)
    assert report["applies"] is False
    assert report["ok"] is True


def test_check_missing_created_fails_closed() -> None:
    report = bm.check("## Goal\nno created line\n")
    assert report["applies"] is True
    assert report["ok"] is False


def test_check_missing_section() -> None:
    report = bm.check(f"Created: {POST_RULE}\n## Goal\n")
    assert report["ok"] is False
    assert "Remaining Boundary Matrix" in report["reason"]


def test_check_section_without_lanes() -> None:
    text = f"Created: {POST_RULE}\n" + _matrix_section("- nothing classified here")
    report = bm.check(text)
    assert report["ok"] is False
    assert report["lanes"] == []


def test_check_invalid_token() -> None:
    text = f"Created: {POST_RULE}\n" + _matrix_section(
        "- Lane: x | classification: maybe-later | next: y"
    )
    report = bm.check(text)
    assert report["ok"] is False
    assert "maybe-later" in report["reason"]


def test_check_runnable_lane_blocks() -> None:
    text = f"Created: {POST_RULE}\n" + _matrix_section(_APPROVAL_LANE, _RUNNABLE_LANE)
    report = bm.check(text)
    assert report["ok"] is False
    assert [lane["classification"] for lane in report["runnable_lanes"]] == ["preauthorized-runnable"]


def test_check_passes_when_all_lanes_settled_or_blocking() -> None:
    text = f"Created: {POST_RULE}\n" + _matrix_section(
        _APPROVAL_LANE,
        "- Lane: provider write | classification: read-only | next: cannot mutate",
        "- Lane: HOTL roundtrip | classification: dispositioned | next: deferred — operator directed",
    )
    report = bm.check(text)
    assert report["ok"] is True
    assert len(report["lanes"]) == 3


def test_check_ignores_fenced_example_lane() -> None:
    fenced = f"Created: {POST_RULE}\n## Remaining Boundary Matrix\n\n```md\n{_RUNNABLE_LANE}\n```\n"
    report = bm.check(fenced)
    # The only lane lives in a fence, so it must not count as a real classified lane.
    assert report["ok"] is False
    assert report["lanes"] == []


# --- flip_refusal ------------------------------------------------------------


def test_flip_refusal_none_when_already_blocked() -> None:
    text = f"Created: {POST_RULE}\n## Goal\n"  # no matrix, but already blocked
    assert bm.flip_refusal(text, "g.md", "blocked") is None


def test_flip_refusal_none_when_clean() -> None:
    text = f"Created: {POST_RULE}\n" + _matrix_section(_APPROVAL_LANE)
    assert bm.flip_refusal(text, "g.md", "active") is None


def test_flip_refusal_builds_payload() -> None:
    text = f"Created: {POST_RULE}\n## Goal\n"
    refusal = bm.flip_refusal(text, "g.md", "active")
    assert refusal is not None
    assert refusal["action"] == "refused"
    assert refusal["requested_status"] == "blocked"
    assert refusal["status"] == "active"
    assert refusal["blocked_matrix_report"]["ok"] is False


# --- upsert_goal end to end --------------------------------------------------


def test_upsert_refuses_blocked_without_matrix(tmp_path: Path) -> None:
    path = _scaffold(tmp_path)
    refusal = gal.upsert_goal(tmp_path, date=POST_RULE, slug="g", title="T", status="blocked")
    assert refusal["action"] == "refused"
    assert refusal["status"] != "blocked"
    assert "Status: blocked" not in path.read_text(encoding="utf-8")
    assert refusal["blocked_matrix_report"]["ok"] is False


def test_upsert_refuses_blocked_with_runnable_lane(tmp_path: Path) -> None:
    path = _scaffold(tmp_path)
    _append(path, _matrix_section(_APPROVAL_LANE, _RUNNABLE_LANE))
    refusal = gal.upsert_goal(tmp_path, date=POST_RULE, slug="g", title="T", status="blocked")
    assert refusal["action"] == "refused"
    assert "Status: blocked" not in path.read_text(encoding="utf-8")
    assert refusal["blocked_matrix_report"]["runnable_lanes"]


def test_upsert_allows_blocked_when_all_lanes_settled(tmp_path: Path) -> None:
    path = _scaffold(tmp_path)
    _append(path, _matrix_section(_APPROVAL_LANE))
    result = gal.upsert_goal(tmp_path, date=POST_RULE, slug="g", title="T", status="blocked")
    assert result["action"] in ("updated", "unchanged")
    assert result["status"] == "blocked"
    assert "Status: blocked" in path.read_text(encoding="utf-8")


def test_upsert_refuses_create_straight_to_blocked(tmp_path: Path) -> None:
    # Creating a brand-new goal directly at `blocked` must not bypass the floor:
    # a fresh template has no matrix, so the create path refuses too.
    refusal = gal.upsert_goal(tmp_path, date=POST_RULE, slug="g", title="T", status="blocked")
    assert refusal["action"] == "refused"
    assert refusal["status"] == "missing"
    assert refusal["blocked_matrix_report"]["ok"] is False
    assert not gal.goal_path(tmp_path, POST_RULE, "g").exists()


def test_upsert_grandfathers_pre_rule_goal(tmp_path: Path) -> None:
    _scaffold(tmp_path, date=PRE_RULE)
    result = gal.upsert_goal(tmp_path, date=PRE_RULE, slug="g", title="T", status="blocked")
    assert result["action"] in ("updated", "unchanged")
    assert result["status"] == "blocked"


# --- check_goal_artifact.py post-flip visibility -----------------------------


def test_checker_surfaces_floor_on_already_blocked_goal(tmp_path: Path) -> None:
    path = _scaffold(tmp_path)
    # Write Status: blocked directly (bypassing the flip gate) to simulate a goal
    # blocked through a path that skipped the matrix; the checker must re-surface it.
    path.write_text(gal.set_status(path.read_text(encoding="utf-8"), "blocked"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_CHECKER), "--repo-root", str(tmp_path), "--goal-path", str(path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["blocked_matrix"]["ok"] is False
    assert any("remaining-boundary-matrix floor" in issue for issue in payload["issues"])


def test_checker_passes_blocked_goal_with_clean_matrix(tmp_path: Path) -> None:
    path = _scaffold(tmp_path)
    _append(path, _matrix_section(_APPROVAL_LANE))
    path.write_text(gal.set_status(path.read_text(encoding="utf-8"), "blocked"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_CHECKER), "--repo-root", str(tmp_path), "--goal-path", str(path)],
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["blocked_matrix"]["ok"] is True
    assert payload["ok"] is True
