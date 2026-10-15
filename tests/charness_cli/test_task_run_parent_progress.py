from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from scripts.task_run import task_run_evidence

from .test_task_run_fixtures import _codex, _repo, _run


def _parent_commit(repo: Path, edit: str) -> str:
    root = shlex.quote(str(repo))
    return (
        f"{edit}\n"
        f"git -C {root} add --all\n"
        f"git -C {root} -c user.email=test@example.com "
        "-c user.name=test commit -m parent"
    )


def test_whole_tree_scope_accepts_disjoint_committed_parent_progress(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    notes = shlex.quote(str(repo / "notes.txt"))
    parent_commit = _parent_commit(repo, f"printf 'parent\\n' > {notes}")
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > child.py\n{parent_commit}",
    )

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    progress = payload["parent"]["progress"]
    assert payload["status"] == "completed", payload
    assert payload["scope"]["changed_paths"] == ["child.py"]
    assert progress["classification"] == "concurrent-parent-progress"
    assert progress["committed_paths"] == ["notes.txt"]
    assert progress["overlap_paths"] == []


@pytest.mark.parametrize(
    ("parent_change", "committed_paths"),
    [
        ("update", ["module.py"]),
        ("delete", ["module.py"]),
        ("rename", ["module.py", "renamed.py"]),
    ],
)
def test_committed_parent_overlap_with_candidate_blocks(
    tmp_path: Path,
    parent_change: str,
    committed_paths: list[str],
) -> None:
    repo = _repo(tmp_path)
    module = shlex.quote(str(repo / "module.py"))
    renamed = shlex.quote(str(repo / "renamed.py"))
    edit = {
        "update": f"printf 'PARENT = 2\\n' > {module}",
        "delete": f"rm {module}",
        "rename": f"mv {module} {renamed}",
    }[parent_change]
    parent_commit = _parent_commit(repo, edit)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\n{parent_commit}",
    )

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    progress = payload["parent"]["progress"]
    assert payload["status"] == "validated-partial-result", payload
    assert payload["approval_eligibility"] == "ineligible"
    assert progress["classification"] == "writer-conflict"
    assert progress["committed_paths"] == committed_paths
    assert progress["overlap_paths"] == ["module.py"]


def test_dirty_parent_ownership_of_candidate_still_blocks(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    parent_module = shlex.quote(str(repo / "module.py"))
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'PARENT = 2\\n' > {parent_module}",
    )

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    progress = payload["parent"]["progress"]
    assert payload["status"] == "validated-partial-result", payload
    assert payload["approval_eligibility"] == "ineligible"
    assert progress["classification"] == "writer-conflict"
    assert progress["dirty"]["tracked"]["added"] == ["module.py"]
    assert progress["overlap_paths"] == ["module.py"]


@pytest.mark.parametrize(
    (
        "candidate_change",
        "staged",
        "parent_change",
        "changed_paths",
        "status",
        "overlap_paths",
        "approval_eligibility",
    ),
    [
        (
            "delete",
            False,
            "original",
            ["module.py"],
            "validated-partial-result",
            ["module.py"],
            "ineligible",
        ),
        ("delete", False, "disjoint", ["module.py"], "completed", [], "eligible"),
        (
            "rename",
            False,
            "original",
            ["module.py", "renamed.py"],
            "validated-partial-result",
            ["module.py"],
            "ineligible",
        ),
        (
            "rename",
            False,
            "target",
            ["module.py", "renamed.py"],
            "validated-partial-result",
            ["renamed.py"],
            "ineligible",
        ),
        (
            "rename",
            False,
            "disjoint",
            ["module.py", "renamed.py"],
            "completed",
            [],
            "eligible",
        ),
        (
            "rename",
            True,
            "original",
            ["module.py", "renamed.py"],
            "validated-partial-result",
            ["module.py"],
            "ineligible",
        ),
        (
            "rename",
            True,
            "target",
            ["module.py", "renamed.py"],
            "validated-partial-result",
            ["renamed.py"],
            "ineligible",
        ),
        (
            "rename",
            True,
            "disjoint",
            ["module.py", "renamed.py"],
            "completed",
            [],
            "eligible",
        ),
    ],
)
def test_candidate_deletion_and_rename_paths_drive_parent_conflicts(
    tmp_path: Path,
    candidate_change: str,
    staged: bool,
    parent_change: str,
    changed_paths: list[str],
    status: str,
    overlap_paths: list[str],
    approval_eligibility: str,
) -> None:
    repo = _repo(tmp_path)
    module = shlex.quote(str(repo / "module.py"))
    renamed = shlex.quote(str(repo / "renamed.py"))
    notes = shlex.quote(str(repo / "notes.txt"))
    lane_change = {"delete": "rm module.py", "rename": "mv module.py renamed.py"}[candidate_change]
    parent_edit = {
        "original": f"printf 'PARENT = 2\\n' > {module}",
        "target": f"printf 'PARENT = 2\\n' > {renamed}",
        "disjoint": f"printf 'parent\\n' > {notes}",
    }[parent_change]
    parent_commit = _parent_commit(repo, parent_edit)
    if staged:
        lane_change += "\ngit add --all"
    executable = _codex(tmp_path, f"{lane_change}\n{parent_commit}")

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    progress = payload["parent"]["progress"]
    assert payload["scope"]["changed_paths"] == changed_paths
    assert payload["status"] == status, payload
    assert payload["approval_eligibility"] == approval_eligibility
    assert progress["overlap_paths"] == overlap_paths
    assert progress["classification"] == (
        "writer-conflict" if overlap_paths else "concurrent-parent-progress"
    )


def test_missing_candidate_path_evidence_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    notes = shlex.quote(str(repo / "notes.txt"))
    parent_commit = _parent_commit(repo, f"printf 'parent\\n' > {notes}")
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\n{parent_commit}",
    )
    original_scope_result = task_run_evidence._scope_result

    def omit_candidate_paths(*args, **kwargs):
        scope = original_scope_result(*args, **kwargs)
        scope["changed_paths"] = None
        return scope

    monkeypatch.setattr(task_run_evidence, "_scope_result", omit_candidate_paths)

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    assert payload["status"] == "failed"
    assert payload["error"] == (
        "task lifecycle failed: candidate path evidence is unavailable for parent "
        "progress classification"
    )
    assert payload["approval_eligibility"] == "ineligible"
