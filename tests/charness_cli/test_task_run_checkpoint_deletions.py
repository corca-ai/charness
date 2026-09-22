"""WIP checkpoint staging with tracked deletions and renames (#826).

Re-adding an already-staged deletion fails (`pathspec did not match`),
so the checkpoint must skip staging for deletions the index already
carries while still committing them through the commit pathspec.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.task_run import task_run_git
from tests.quality_gates.repo_shapes import install_committed_repo


def _committed_deletions(repo: Path, sha: str) -> list[str]:
    out = task_run_git._git_output(repo, "show", "--name-status", "--format=", sha)
    return [line for line in out.splitlines() if line.startswith("D\t")]


def test_staged_deletion_checkpoints_without_re_adding(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"gone.txt": "bye\n", "kept.txt": "hi\n"})
    (repo / "gone.txt").unlink()
    task_run_git._git(repo, "add", "--", "gone.txt")

    receipt = task_run_git._commit_wip_candidate(repo, ["gone.txt"])

    assert receipt["status"] == "committed"
    assert _committed_deletions(repo, receipt["sha"]) == ["D\tgone.txt"]


def test_unstaged_deletion_is_staged_by_the_checkpoint(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"gone.txt": "bye\n"})
    (repo / "gone.txt").unlink()

    receipt = task_run_git._commit_wip_candidate(repo, ["gone.txt"])

    assert receipt["status"] == "committed"
    assert _committed_deletions(repo, receipt["sha"]) == ["D\tgone.txt"]


def test_rename_commits_both_sides(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"old.txt": "data\n"})
    (repo / "old.txt").rename(repo / "new.txt")

    receipt = task_run_git._commit_wip_candidate(repo, ["old.txt", "new.txt"])

    assert receipt["status"] == "committed"
    out = task_run_git._git_output(repo, "show", "--name-status", "--format=", receipt["sha"])
    assert any("old.txt" in line for line in out.splitlines())
    assert any("new.txt" in line for line in out.splitlines())
    assert "old.txt" not in task_run_git._git_output(repo, "ls-tree", "-r", "--name-only", "HEAD")


def test_unknown_path_still_refuses_with_typed_error(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"kept.txt": "hi\n"})

    with pytest.raises(task_run_git.TaskRunError, match="git add failed"):
        task_run_git._commit_wip_candidate(repo, ["missing.txt"])
