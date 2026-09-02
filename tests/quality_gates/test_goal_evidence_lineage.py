from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/issue/goal_lineage.py"


def _load():
    spec = importlib.util.spec_from_file_location("goal_lineage_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lineage = _load()


def _record(*, disposition: str = "goal-bound", child: bool = True) -> dict[str, object]:
    return {
        "kind": lineage.KIND,
        "schema_version": lineage.SCHEMA_VERSION,
        "disposition": disposition,
        "draft": {"path": "charness-artifacts/goals/demo.md", "sha256": "a" * 64}
        if disposition != "not-goal-bound"
        else None,
        "binding": {"path": "charness-artifacts/goals/demo.binding.json", "sha256": "b" * 64}
        if disposition == "goal-bound"
        else None,
        "goal_run": {
            "repo": "corca-ai/charness",
            "number": 724,
            "url": "https://github.com/corca-ai/charness/issues/724",
        }
        if disposition == "goal-bound"
        else None,
        "work_item": {
            "key": "provider",
            "repo": "corca-ai/charness",
            "number": 726,
            "url": "https://github.com/corca-ai/charness/issues/726",
        }
        if disposition == "goal-bound" and child
        else None,
        "reason": "planning is not execution" if disposition != "goal-bound" else None,
    }


def test_complete_goal_lineage_is_canonical_and_hashable(tmp_path: Path) -> None:
    result = lineage.validate_goal_lineage(_record(), repo_root=tmp_path, require_work_item=True)

    assert result["goal_run"]["number"] == 724
    assert len(lineage.lineage_sha256(result)) == 64
    assert lineage.canonical_json_bytes(result).endswith(b"\n")


def test_planning_only_is_explicitly_non_executable() -> None:
    result = lineage.validate_goal_lineage(_record(disposition="planning-only", child=False))

    assert result["disposition"] == "planning-only"
    assert result["goal_run"] is None
    assert result["binding"] is None


def test_not_goal_bound_cannot_smuggle_a_parent_identity() -> None:
    record = _record(disposition="not-goal-bound", child=False)
    record["goal_run"] = {
        "repo": "corca-ai/charness",
        "number": 724,
        "url": "https://github.com/corca-ai/charness/issues/724",
    }

    with pytest.raises(lineage.LineageError) as exc_info:
        lineage.validate_goal_lineage(record)

    assert exc_info.value.code == "lineage-authority-mismatch"


def test_same_path_with_different_draft_hash_refuses() -> None:
    left = _record(child=False)
    right = _record(child=False)
    right["draft"] = {"path": left["draft"]["path"], "sha256": "c" * 64}

    with pytest.raises(lineage.LineageError) as exc_info:
        lineage.require_same_lineage(left, right)

    assert exc_info.value.code == "lineage-mismatch"


def test_same_issue_number_in_another_repository_refuses() -> None:
    record = _record(child=False)
    record["goal_run"] = {
        "repo": "other/project",
        "number": 724,
        "url": "https://github.com/other/project/issues/724",
    }

    with pytest.raises(lineage.LineageError) as exc_info:
        lineage.require_same_lineage(_record(child=False), record)

    assert exc_info.value.code == "lineage-mismatch"


def test_planning_only_cannot_be_consumed_as_goal_bound_proof() -> None:
    with pytest.raises(lineage.LineageError) as exc_info:
        lineage.require_same_lineage(_record(disposition="planning-only", child=False), _record(child=False))

    assert exc_info.value.code == "lineage-mismatch"


def test_selected_evidence_must_name_an_exact_work_item() -> None:
    with pytest.raises(lineage.LineageError) as exc_info:
        lineage.validate_goal_lineage(_record(child=False), require_work_item=True)

    assert exc_info.value.code == "work-item-missing"
