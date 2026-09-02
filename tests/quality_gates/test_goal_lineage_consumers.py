from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.issue.goal_lineage import LineageError, load_goal_lineage_file, not_goal_bound_lineage


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed_lineage(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    draft = repo / "charness-artifacts" / "goals" / "draft.md"
    binding = repo / "charness-artifacts" / "goals" / "draft.binding.json"
    draft.parent.mkdir(parents=True)
    draft.write_text("# Draft\n", encoding="utf-8")
    binding.write_text("{\"kind\": \"binding\"}\n", encoding="utf-8")
    lineage_path = repo / ".charness" / "lineage.json"
    lineage_path.parent.mkdir()
    lineage_path.write_text(
        json.dumps(
            {
                "kind": "charness.goal-lineage",
                "schema_version": 1,
                "disposition": "goal-bound",
                "draft": {"path": "charness-artifacts/goals/draft.md", "sha256": _sha(draft)},
                "binding": {"path": "charness-artifacts/goals/draft.binding.json", "sha256": _sha(binding)},
                "goal_run": {
                    "repo": "acme/project",
                    "number": 10,
                    "url": "https://github.com/acme/project/issues/10",
                },
                "work_item": {
                    "key": "implementation",
                    "repo": "acme/project",
                    "number": 11,
                    "url": "https://github.com/acme/project/issues/11",
                },
                "reason": None,
            }
        ),
        encoding="utf-8",
    )
    return repo, lineage_path


def test_loader_verifies_the_complete_lineage_and_immutable_files(tmp_path: Path) -> None:
    repo, lineage_path = _seed_lineage(tmp_path)

    result = load_goal_lineage_file(repo, lineage_path, require_work_item=True)

    assert result["disposition"] == "goal-bound"
    assert result["work_item"]["number"] == 11

    draft = repo / result["draft"]["path"]
    draft.write_text("changed\n", encoding="utf-8")
    with pytest.raises(LineageError) as caught:
        load_goal_lineage_file(repo, lineage_path, require_work_item=True)
    assert caught.value.code == "lineage-reference-hash-mismatch"


def test_loader_rejects_a_lineage_file_outside_repo(tmp_path: Path) -> None:
    repo, _lineage_path = _seed_lineage(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(LineageError) as caught:
        load_goal_lineage_file(repo, outside)

    assert caught.value.code == "lineage-path-invalid"


def test_loader_rejects_a_symlinked_lineage_input(tmp_path: Path) -> None:
    repo, lineage_path = _seed_lineage(tmp_path)
    linked = repo / ".charness" / "lineage-link.json"
    linked.symlink_to(lineage_path.name)

    with pytest.raises(LineageError) as caught:
        load_goal_lineage_file(repo, linked)

    assert caught.value.code == "lineage-path-invalid"


def test_loader_rejects_symlinked_reference_components(tmp_path: Path) -> None:
    repo, lineage_path = _seed_lineage(tmp_path)
    alias = repo / "alias"
    alias.symlink_to(repo / "charness-artifacts" / "goals", target_is_directory=True)
    value = json.loads(lineage_path.read_text(encoding="utf-8"))
    value["draft"]["path"] = "alias/draft.md"
    value["binding"]["path"] = "alias/draft.binding.json"
    lineage_path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LineageError) as caught:
        load_goal_lineage_file(repo, lineage_path)

    assert caught.value.code == "lineage-path-invalid"


def test_unbound_evidence_is_explicit_not_an_empty_or_fake_identity() -> None:
    result = not_goal_bound_lineage("standalone evidence has no Goal Run")

    assert result == {
        "kind": "charness.goal-lineage",
        "schema_version": 1,
        "disposition": "not-goal-bound",
        "draft": None,
        "binding": None,
        "goal_run": None,
        "work_item": None,
        "reason": "standalone evidence has no Goal Run",
    }
