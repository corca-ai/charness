"""Refusals owned by `scripts/task_run_git.py`.

Split out of `test_task_run.py` when that file crossed its 800 code-line limit.
The cohesive boundary is the module under test: every case here drives
`task_run_git` directly and asserts the typed refusal and the human-actionable
detail it carries, rather than the lane wiring the sibling file covers.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import task_run, task_run_git

from .test_task_run_fixtures import _repo


def test_git_output_refusal_preserves_the_human_actionable_detail(
    monkeypatch, tmp_path: Path
) -> None:
    cases = (
        ("fatal: bad revision\n", "ignored\n", "fatal: bad revision"),
        ("", "git said no\n", "git said no"),
        ("", "", "git command failed"),
    )
    for stderr, stdout, detail in cases:
        monkeypatch.setattr(
            task_run_git,
            "_git",
            lambda *_args, stderr=stderr, stdout=stdout: subprocess.CompletedProcess(
                ["git"], 1, stdout=stdout, stderr=stderr
            ),
        )
        with pytest.raises(task_run.TaskRunError, match=f"git status failed: {detail}"):
            task_run_git._git_output(tmp_path, "status")


def test_require_git_root_refuses_a_subdirectory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    subdirectory = repo / "subdirectory"
    subdirectory.mkdir()

    with pytest.raises(task_run.TaskRunError, match="must be the Git worktree root"):
        task_run_git._require_git_root(subdirectory)


@pytest.mark.parametrize(
    ("base", "message"),
    [
        ("", "--base is required and must resolve to a commit"),
        ("missing-base", "ref is not resolvable: missing-base"),
    ],
)
def test_base_resolution_refuses_missing_commit(tmp_path: Path, base: str, message: str) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(task_run.TaskRunError, match=message):
        task_run_git._resolve_base_sha(repo, base)


def test_git_administration_paths_require_directories(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "missing-common\n")
    with pytest.raises(task_run.TaskRunError, match="Git common directory is not a directory"):
        task_run_git._git_common_dir(repo)

    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: ".git\n")
    assert task_run_git._git_dir(repo) == (repo / ".git").resolve()

    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "missing-git\n")
    with pytest.raises(task_run.TaskRunError, match="Git directory is not a directory"):
        task_run_git._git_dir(repo)


def test_branch_validation_refuses_syntactically_invalid_names(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(task_run.TaskRunError, match="not a valid named branch"):
        task_run_git._validate_branch(repo, "bad..branch")


def test_branch_validation_preserves_git_refusal_detail(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(
        task_run_git,
        "_git",
        lambda *_args: subprocess.CompletedProcess(
            ["git"], 1, stdout="", stderr="git rejected branch\n"
        ),
    )

    with pytest.raises(task_run.TaskRunError, match="git rejected branch"):
        task_run_git._validate_branch(repo, "valid-ish//branch")


def test_worktree_validation_refuses_inside_and_existing_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inside = repo / "nested"
    with pytest.raises(task_run.TaskRunError, match="must be outside the repository"):
        task_run_git._validate_worktree_path(repo, inside)

    existing = tmp_path / "existing-worktree"
    existing.mkdir()
    with pytest.raises(task_run.TaskRunError, match="worktree path already exists"):
        task_run_git._validate_worktree_path(repo, existing)


def test_collect_populations_refuses_malformed_and_tracks_rename_destination(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "x\0")
    with pytest.raises(task_run.TaskRunError, match="unexpected git status record"):
        task_run_git._collect_populations(repo)

    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "R  old.py\0new.py\0")
    assert task_run_git._collect_populations(repo) == {
        "tracked": ["new.py", "old.py"],
        "untracked": [],
        "ignored": [],
    }
