from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from tests.seed_cache import get_or_build


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _build_seed(staging: Path) -> None:
    repo = staging / "repo"
    (repo / "scripts").mkdir(parents=True)
    git(repo, "init", "-q")
    foo = repo / "scripts" / "foo.py"
    foo.write_text("def a():\n    return 1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    foo.write_text(
        "def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "head")
    head = git(repo, "rev-parse", "HEAD")
    (staging / "refs.json").write_text(
        json.dumps({"base": base, "head": head}), encoding="utf-8"
    )


def _seed() -> tuple[Path, str, str]:
    seed = get_or_build("changed-line-mutation-coverage-repo-seed", _build_seed)
    refs = json.loads((seed / "refs.json").read_text(encoding="utf-8"))
    return seed / "repo", refs["base"], refs["head"]


def seed_repo_with_changed_pool_file(tmp_path: Path) -> tuple[Path, str, str]:
    source, base, head = _seed()
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    return repo, base, head
