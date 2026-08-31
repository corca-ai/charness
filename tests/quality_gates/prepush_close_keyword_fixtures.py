from __future__ import annotations

import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def commit(
    repo: Path,
    body: str,
    name: str,
    extra: dict[str, str] | None = None,
) -> str:
    """Commit through ``-F``, preserving leading ``#`` lines verbatim."""
    (repo / name).write_text(name, encoding="utf-8")
    paths = [name]
    for rel, content in (extra or {}).items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        paths.append(rel)
    git(repo, "add", "--", *paths)
    message_file = repo / ".commit-message"
    message_file.write_text(body, encoding="utf-8")
    git(
        repo,
        "-c", "user.email=test@example.com",
        "-c", "user.name=Charness Test",
        "commit", "-F", str(message_file),
    )
    message_file.unlink()
    return head(repo)


def head(repo: Path) -> str:
    """Read the checked-out commit from Git files, not ``rev-parse``."""
    pointer = (repo / ".git" / "HEAD").read_text(encoding="ascii").strip()
    if not pointer.startswith("ref: "):
        return pointer
    return (repo / ".git" / pointer.removeprefix("ref: ")).read_text(encoding="ascii").strip()


def _build_seed(staging: Path) -> None:
    from tests.quality_gates.seeding_support import _install_empty_git_dir

    _install_empty_git_dir(staging, branch="main")
    commit(staging, "chore: base commit\n", "base.txt")


def repo_seed(*, cache_get_or_build=None) -> Path:
    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build
    return cache_get_or_build("prepush-close-keyword-repo-seed", _build_seed)


def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
