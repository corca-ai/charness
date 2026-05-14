#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path

try:
    from scripts.repo_layout import support_dir
except ModuleNotFoundError:
    from repo_layout import support_dir


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


_SUPPORT_PATTERN_PREFIX = "skills/support/"


def _split_support_patterns(patterns: tuple[str, ...]) -> tuple[list[str], list[str]]:
    standard: list[str] = []
    support: list[str] = []
    for pattern in patterns:
        if pattern.startswith(_SUPPORT_PATTERN_PREFIX):
            support.append(pattern.removeprefix(_SUPPORT_PATTERN_PREFIX))
        else:
            standard.append(pattern)
    return standard, support


def iter_matching_repo_files(
    repo_root: Path,
    patterns: tuple[str, ...],
    *,
    include_untracked: bool = True,
) -> list[Path]:
    standard_patterns, support_subpatterns = _split_support_patterns(patterns)
    support_root = support_dir(repo_root)
    support_is_external = support_root != (repo_root / "skills" / "support").resolve()
    if not support_is_external:
        standard_patterns.extend(_SUPPORT_PATTERN_PREFIX + sub for sub in support_subpatterns)
        support_subpatterns = []

    matches: list[Path] = []
    seen: set[Path] = set()

    git_paths = git_list_repo_files(repo_root, include_untracked=include_untracked)
    if git_paths is not None:
        allowed = {path for path in git_paths if path.is_file()}
        for pattern in standard_patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path not in allowed or path in seen:
                    continue
                seen.add(path)
                matches.append(path)
    else:
        for pattern in standard_patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                matches.append(path)

    for sub in support_subpatterns:
        for path in support_root.glob(sub):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            matches.append(path)

    return sorted(matches)
