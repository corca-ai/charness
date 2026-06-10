"""Slice-closeout `--base` committed-range ergonomics.

Post-commit, the closeout's working-tree default collects nothing and the run
no-ops, which forced a manual `--paths` list to cover the committed bundle.
`--base` derives the committed merge-base(<ref>, HEAD)..HEAD range (bare
`--base` auto-detects origin/main — the same anchor the changed-line mutation
gate uses) while the working-tree default stays unchanged.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pytest

from scripts.run_slice_closeout import _build_parser, _resolve_changed_paths
from scripts.surfaces_lib import (
    SurfaceError,
    collect_changed_paths_since_base,
    resolve_base_sha,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _seed_repo(tmp_path: Path) -> Path:
    """A repo whose HEAD is one commit ahead of a local `origin/main` branch
    (a stand-in for the remote-tracking anchor the auto-detect resolves)."""
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "base.txt").write_text("base\n", encoding="utf-8")
    _git(tmp_path, "add", "base.txt")
    _git(tmp_path, "commit", "-m", "base")
    _git(tmp_path, "branch", "origin/main")
    (tmp_path / "committed.txt").write_text("committed\n", encoding="utf-8")
    _git(tmp_path, "add", "committed.txt")
    _git(tmp_path, "commit", "-m", "committed change")
    return tmp_path


def _args(paths: list[str] | None = None, base: str | None = None) -> argparse.Namespace:
    return argparse.Namespace(paths=paths, base=base)


def test_collect_changed_paths_since_base_covers_committed_range_and_worktree(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    assert collect_changed_paths_since_base(repo, "auto") == ["committed.txt", "dirty.txt"]


def test_resolve_base_sha_auto_matches_the_gate_range_anchor(tmp_path: Path) -> None:
    # The changed-line mutation gate anchors at merge-base(origin/main, HEAD);
    # `auto` must resolve the identical SHA so the closeout payload and the
    # gate agree on the committed range.
    repo = _seed_repo(tmp_path)
    expected = _git(repo, "merge-base", "origin/main", "HEAD")

    assert resolve_base_sha(repo, "auto") == expected
    assert resolve_base_sha(repo, "origin/main") == expected


def test_resolve_base_sha_unresolvable_ref_raises_surface_error(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    with pytest.raises(SurfaceError, match="merge-base"):
        resolve_base_sha(repo, "no-such-ref")


def test_resolve_base_sha_empty_merge_base_output_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # git exiting 0 with no output should not silently yield an empty base.
    from scripts import surfaces_lib

    repo = _seed_repo(tmp_path)
    monkeypatch.setattr(surfaces_lib, "_run_git", lambda *a, **k: [])
    with pytest.raises(SurfaceError, match="resolved empty"):
        resolve_base_sha(repo, "auto")


def test_resolve_changed_paths_default_stays_working_tree_only(tmp_path: Path) -> None:
    # Behavior preservation: without --base the post-commit clean tree still
    # collects nothing (noop), while --base picks up the committed range.
    repo = _seed_repo(tmp_path)

    assert _resolve_changed_paths(repo, _args()) == []
    assert _resolve_changed_paths(repo, _args(base="auto")) == ["committed.txt"]


def test_resolve_changed_paths_explicit_paths_stay_the_override(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)

    assert _resolve_changed_paths(repo, _args(paths=["x.md"])) == ["x.md"]


def test_resolve_changed_paths_rejects_base_with_paths(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    with pytest.raises(SurfaceError, match="mutually exclusive"):
        _resolve_changed_paths(repo, _args(paths=["x.md"], base="auto"))


def test_predict_commit_rejects_base(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    from scripts import run_slice_closeout

    monkeypatch.setattr(sys, "argv", ["run_slice_closeout.py", "--predict-commit", "--base", "--json"])
    with pytest.raises(SurfaceError, match="--base is not supported with --predict-commit"):
        run_slice_closeout.main()


def test_build_parser_base_flag_shapes() -> None:
    parser = _build_parser()

    assert parser.parse_args([]).base is None
    assert parser.parse_args(["--base"]).base == "auto"
    assert parser.parse_args(["--base", "v1.2.3"]).base == "v1.2.3"
