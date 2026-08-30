"""The changed-path binding and narrative must select one subject."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import reviewed_input_identity, surfaces_lib


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=Test",
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _seed_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "base.txt")
    _git(repo, "commit", "-q", "-m", "base")


def _assert_changed_path_agreement(
    identity_paths: list[str],
    surface_paths: list[str],
) -> None:
    if identity_paths != surface_paths:
        raise AssertionError(
            "changed-path enumerators disagree: "
            f"identity={identity_paths!r}, surfaces={surface_paths!r}"
        )


def test_identity_and_surfaces_use_one_changed_path_owner() -> None:
    assert reviewed_input_identity._changed_path_owner is surfaces_lib


def test_worktree_matrix_keeps_changed_path_consumers_in_agreement(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _git(tmp_path, "config", "core.quotepath", "true")
    for name in ("rename-me.txt", "staged-delete.txt", "worktree-delete.txt"):
        (tmp_path / name).write_text(f"{name}\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")

    upstream = tmp_path / "upstream"
    _seed_repo(upstream)
    _git(
        tmp_path,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        "-q",
        str(upstream),
        "sub",
    )
    _git(tmp_path, "commit", "-q", "-m", "add submodule")

    _git(tmp_path, "mv", "rename-me.txt", "renamed.txt")
    _git(tmp_path, "rm", "-q", "staged-delete.txt")
    (tmp_path / "worktree-delete.txt").unlink()
    (tmp_path / "staged-then-removed.txt").write_text("staged\n", encoding="utf-8")
    _git(tmp_path, "add", "staged-then-removed.txt")
    (tmp_path / "staged-then-removed.txt").unlink()
    (tmp_path / "한글.txt").write_text("non-ascii\n", encoding="utf-8")

    (upstream / "next.txt").write_text("next\n", encoding="utf-8")
    _git(upstream, "add", "next.txt")
    _git(upstream, "commit", "-q", "-m", "next")
    _git(tmp_path / "sub", "fetch", "-q", "origin")
    _git(tmp_path / "sub", "checkout", "-q", "FETCH_HEAD")

    identity_paths = reviewed_input_identity._auto_paths(tmp_path, None)
    surface_paths = surfaces_lib.collect_changed_paths(tmp_path)
    _assert_changed_path_agreement(identity_paths, surface_paths)
    assert {
        "renamed.txt",
        "staged-delete.txt",
        "worktree-delete.txt",
        "staged-then-removed.txt",
        "한글.txt",
        "sub",
    } <= set(identity_paths)


def test_merge_matrix_keeps_changed_path_consumers_in_agreement(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _git(tmp_path, "branch", "-M", "trunk")
    _git(tmp_path, "checkout", "-q", "-b", "side")
    (tmp_path / "side.txt").write_text("side\n", encoding="utf-8")
    _git(tmp_path, "add", "side.txt")
    _git(tmp_path, "commit", "-q", "-m", "side")
    _git(tmp_path, "checkout", "-q", "trunk")
    (tmp_path / "trunk.txt").write_text("trunk\n", encoding="utf-8")
    _git(tmp_path, "add", "trunk.txt")
    _git(tmp_path, "commit", "-q", "-m", "trunk")
    _git(tmp_path, "merge", "--no-ff", "-q", "-m", "merge side", "side")

    identity_paths = reviewed_input_identity._auto_paths(tmp_path, "HEAD")
    surface_paths = surfaces_lib.collect_changed_paths_for_ref(tmp_path, "HEAD")
    _assert_changed_path_agreement(identity_paths, surface_paths)
    assert {"side.txt", "trunk.txt"} <= set(identity_paths)


def test_agreement_check_rejects_a_deliberately_divergent_enumerator() -> None:
    try:
        _assert_changed_path_agreement(["bound.txt"], ["narrated.txt"])
    except AssertionError as exc:
        assert "changed-path enumerators disagree" in str(exc)
    else:
        raise AssertionError("a divergent enumerator must fail the agreement check")
