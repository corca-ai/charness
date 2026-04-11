#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path


def git_list_repo_files(repo_root: Path, *, include_untracked: bool = True) -> list[Path] | None:
    args = ["git", "ls-files", "-z", "--cached"]
    if include_untracked:
        args.extend(["--others", "--exclude-standard"])
    result = subprocess.run(
        args,
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return sorted(repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel)


def iter_repo_files(repo_root: Path, *, include_untracked: bool = True) -> list[Path]:
    paths = git_list_repo_files(repo_root, include_untracked=include_untracked)
    if paths is not None:
        return [path for path in paths if path.is_file()]

    candidates: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_file():
            candidates.append(path)
    return sorted(candidates)


def iter_matching_repo_files(
    repo_root: Path,
    patterns: tuple[str, ...],
    *,
    include_untracked: bool = True,
) -> list[Path]:
    git_paths = git_list_repo_files(repo_root, include_untracked=include_untracked)
    if git_paths is not None:
        allowed = {path for path in git_paths if path.is_file()}
        matches: list[Path] = []
        seen: set[Path] = set()
        for pattern in patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path not in allowed or path in seen:
                    continue
                seen.add(path)
                matches.append(path)
        return sorted(matches)

    matches: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            matches.append(path)
    return sorted(matches)
