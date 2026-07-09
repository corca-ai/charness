"""Skill path and file-discovery helpers for prompt-mutant tooling."""

from __future__ import annotations

import subprocess
from pathlib import Path


def skill_plugin_root(skill: str) -> str:
    return f"plugins/charness/skills/{skill}"


def skill_public_root(skill: str) -> str:
    return f"skills/public/{skill}"


def _pair_public_skill_files(
    plugin_root: str,
    public_root: str,
    relpaths: list[str],
    *,
    public_exists,
) -> list[tuple[str, str | None]]:
    result = []
    for relpath in relpaths:
        suffix = relpath[len(plugin_root) + 1 :]
        candidate_public = f"{public_root}/{suffix}"
        result.append((relpath, candidate_public if public_exists(candidate_public) else None))
    return result


def list_skill_files_worktree(repo_root: Path, skill: str) -> list[tuple[str, str | None]]:
    """(plugin_relpath, public_relpath_or_None) pairs from the checked-out
    worktree: SKILL.md first, then references/*.md sorted by name."""
    plugin_root = skill_plugin_root(skill)
    public_root = skill_public_root(skill)
    relpaths: list[str] = []
    if (repo_root / plugin_root / "SKILL.md").is_file():
        relpaths.append(f"{plugin_root}/SKILL.md")
    refs_dir = repo_root / plugin_root / "references"
    if refs_dir.is_dir():
        relpaths.extend(
            f"{plugin_root}/references/{path.name}" for path in sorted(refs_dir.glob("*.md"))
        )
    return _pair_public_skill_files(
        plugin_root,
        public_root,
        relpaths,
        public_exists=lambda candidate_public: (repo_root / candidate_public).is_file(),
    )


def read_worktree_file(repo_root: Path, relpath: str) -> str | None:
    try:
        return (repo_root / relpath).read_text(encoding="utf-8")
    except OSError:
        return None


def _git_ls_tree_paths(repo_root: Path, ref: str, path: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-tree", "-r", "--name-only", ref, "--", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {line for line in result.stdout.splitlines() if line}


def list_skill_files_at_ref(repo_root: Path, ref: str, skill: str) -> list[tuple[str, str | None]]:
    """Ref-aware sibling of `list_skill_files_worktree`: enumerates files via
    `git ls-tree` at `ref` instead of globbing the checkout, so callers can
    match unit ids to a baseline commit even when it differs from the checked-
    out worktree."""
    plugin_root = skill_plugin_root(skill)
    public_root = skill_public_root(skill)
    plugin_paths = _git_ls_tree_paths(repo_root, ref, plugin_root)
    public_paths = _git_ls_tree_paths(repo_root, ref, public_root)
    relpaths: list[str] = []
    skill_md = f"{plugin_root}/SKILL.md"
    if skill_md in plugin_paths:
        relpaths.append(skill_md)
    refs_prefix = f"{plugin_root}/references/"
    relpaths.extend(
        sorted(p for p in plugin_paths if p.startswith(refs_prefix) and p.endswith(".md"))
    )
    return _pair_public_skill_files(
        plugin_root,
        public_root,
        relpaths,
        public_exists=lambda candidate_public: candidate_public in public_paths,
    )


def read_file_at_ref(repo_root: Path, ref: str, relpath: str) -> str | None:
    """Read `relpath` at `ref` via `git show`, decoding the captured bytes as
    UTF-8 explicitly."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{relpath}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")
