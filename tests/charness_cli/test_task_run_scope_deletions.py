"""Scope attribution for deletions around target merges and symlinks."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.task_run import task_run_carrier, task_run_scope
from tests.charness_cli.test_task_run_fixtures import _commit, _git, _merge, _repo


@pytest.mark.parametrize("delete_during_merge", [False, True], ids=["after-merge", "resolution"])
def test_lane_owned_deletion_of_merge_introduced_file_is_proven(
    tmp_path: Path, delete_during_merge: bool
) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "anchor.py").write_text("VALUE = 1\n", encoding="utf-8")
    _commit(repo, "add scope anchor", "pkg/anchor.py")
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()

    _git(repo, "checkout", "-b", "lane/work")
    (repo / "pkg" / "anchor.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "lane edit", "pkg/anchor.py")
    _git(repo, "checkout", "main")
    (repo / "pkg" / "item.py").write_text("VALUE = 3\n", encoding="utf-8")
    _commit(repo, "target adds item", "pkg/item.py")
    _git(repo, "checkout", "lane/work")

    if delete_during_merge:
        _merge(repo, "--no-commit", "--no-ff", "main")
        _git(repo, "rm", "-f", "--", "pkg/item.py")
        _git(
            repo,
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=test",
            "commit",
            "-m",
            "merge resolution deletes item",
        )
    else:
        _merge(repo, "--no-ff", "main", "-m", "merge main")
        _git(repo, "rm", "--", "pkg/item.py")
        _git(
            repo,
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=test",
            "commit",
            "-m",
            "delete target item",
        )

    scope = task_run_scope._scope_result(
        repo, base, [{"path": "pkg", "kind": "directory"}], require_change=False
    )

    assert "pkg/item.py" in scope["changed_paths"]
    assert scope["disallowed_paths"] == []
    assert scope["verdict"] == task_run_scope.PASS


def test_merge_inherited_target_deletion_is_not_a_lane_deletion(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "anchor.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "pkg" / "item.py").write_text("VALUE = 3\n", encoding="utf-8")
    _commit(repo, "add scope files", "pkg")
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()

    _git(repo, "checkout", "-b", "lane/work")
    (repo / "pkg" / "anchor.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "lane edit", "pkg/anchor.py")
    _git(repo, "checkout", "main")
    _git(repo, "rm", "--", "pkg/item.py")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "target deletes item",
    )
    _git(repo, "checkout", "lane/work")
    _merge(repo, "--no-ff", "main", "-m", "merge main")

    candidate = task_run_carrier._candidate_carrier(repo, base)

    assert "pkg/item.py" not in candidate["changed_paths"]


def test_modified_dangling_symlink_is_present_in_the_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "link.py").symlink_to("module.py")
    _commit(repo, "add link", "link.py")
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "link.py").unlink()
    (repo / "link.py").symlink_to("missing-target.py")

    scope = task_run_scope._scope_result(
        repo, base, [{"path": "link.py", "kind": "exact"}], require_change=False
    )

    assert scope["changed_paths"] == ["link.py"]
    assert scope["disallowed_paths"] == []
    assert scope["verdict"] == task_run_scope.PASS


def test_merged_target_changes_are_not_lane_changes(tmp_path: Path) -> None:
    """Merging an advanced main must not flag its paths as lane changes (#875)."""
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "-b", "lane/work")
    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "lane change", "module.py")
    _git(repo, "checkout", "main")
    (repo / "other.py").write_text("O = 1\n", encoding="utf-8")
    _commit(repo, "main change", "other.py")
    _git(repo, "checkout", "lane/work")
    _merge(repo, "main", "-m", "merge main")

    carrier = task_run_carrier._candidate_carrier(repo, base)

    assert carrier["carrier_kind"] == "commit-only"
    assert carrier["committed_paths"] == ["module.py"]
    assert carrier["changed_paths"] == ["module.py"]


def test_lane_edit_in_merge_resolution_stays_a_lane_change(tmp_path: Path) -> None:
    """A lane edit inside the merge resolution is still reported (#875)."""
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "-b", "lane/work")
    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "lane change", "module.py")
    _git(repo, "checkout", "main")
    (repo / "other.py").write_text("O = 1\n", encoding="utf-8")
    _commit(repo, "main change", "other.py")
    _git(repo, "checkout", "lane/work")
    _merge(repo, "--no-commit", "--no-ff", "main")
    (repo / "other.py").write_text("O = 2\n", encoding="utf-8")
    _commit(repo, "merge main with resolution", "other.py")

    carrier = task_run_carrier._candidate_carrier(repo, base)

    assert carrier["carrier_kind"] == "commit-only"
    assert carrier["committed_paths"] == ["module.py", "other.py"]
    assert carrier["changed_paths"] == ["module.py", "other.py"]
