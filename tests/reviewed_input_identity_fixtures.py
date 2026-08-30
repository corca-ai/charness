from __future__ import annotations

import subprocess
from pathlib import Path


def _build_seed(seed_root: Path) -> None:
    repo = seed_root / "repo"
    repo.mkdir()
    (repo / "reviewed.txt").write_text("base\n", encoding="utf-8")
    (repo / "unrelated.txt").write_text("base\n", encoding="utf-8")
    for cmd in (
        ["init"],
        ["add", "."],
        ["commit", "-m", "initial"],
    ):
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *cmd],
            cwd=repo,
            check=True,
            capture_output=True,
        )


def repo_seed(*, cache_get_or_build=None) -> Path:
    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build
    return cache_get_or_build("reviewed-input-identity-repo-seed", _build_seed) / "repo"


def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
