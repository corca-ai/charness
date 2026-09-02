"""`scripts/core/repo_layout.py` answers where a repo script lives (#777)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.core import repo_layout


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    scripts = root / "scripts"
    (scripts / "pkg").mkdir(parents=True)
    (scripts / "flat.py").write_text("", encoding="utf-8")
    (scripts / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "pkg" / "packaged.py").write_text("", encoding="utf-8")
    (scripts / "pkg" / "__pycache__").mkdir()
    (scripts / "pkg" / "__pycache__" / "ghost.py").write_text("", encoding="utf-8")
    for owner in ("a", "b"):
        (scripts / owner).mkdir()
        (scripts / owner / "dup.py").write_text("", encoding="utf-8")
    return root


def test_flat_wins_and_a_packaged_script_is_found_by_its_bare_name(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    assert repo_layout.repo_script(root, "flat.py") == root / "scripts" / "flat.py"
    assert repo_layout.repo_script(root, "packaged.py") == root / "scripts" / "pkg" / "packaged.py"
    assert (
        repo_layout.find_repo_script(root, "packaged.py")
        == root / "scripts" / "pkg" / "packaged.py"
    )


def test_a_scripts_relative_path_is_taken_literally_never_searched(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    assert (
        repo_layout.repo_script(root, "pkg/packaged.py") == root / "scripts" / "pkg" / "packaged.py"
    )
    # `a/packaged.py` does not exist; the resolver must not hand back pkg's copy.
    with pytest.raises(repo_layout.RepoScriptMiss):
        repo_layout.repo_script(root, "a/packaged.py")
    assert repo_layout.find_repo_script(root, "a/packaged.py") is None


def test_a_missing_script_is_a_typed_miss_not_a_fallback(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    with pytest.raises(repo_layout.RepoScriptMiss, match="neither flat nor packaged"):
        repo_layout.repo_script(root, "nowhere.py")
    assert repo_layout.find_repo_script(root, "nowhere.py") is None
    # No scripts/ tree at all is the same typed miss.
    with pytest.raises(repo_layout.RepoScriptMiss):
        repo_layout.repo_script(tmp_path / "empty", "flat.py")


def test_two_owners_is_an_ambiguity_from_both_entry_points(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    with pytest.raises(repo_layout.RepoScriptAmbiguity, match="scripts/a/dup.py, scripts/b/dup.py"):
        repo_layout.repo_script(root, "dup.py")
    with pytest.raises(repo_layout.RepoScriptAmbiguity):
        repo_layout.find_repo_script(root, "dup.py")
    assert issubclass(repo_layout.RepoScriptAmbiguity, repo_layout.RepoScriptMiss)


def test_bytecode_caches_are_not_owners(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    assert repo_layout.find_repo_script(root, "ghost.py") is None
