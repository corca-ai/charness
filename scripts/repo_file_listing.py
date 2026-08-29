#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path

try:
    from scripts.repo_layout import support_dir
except ModuleNotFoundError:
    from repo_layout import support_dir


class RepoFileListingError(SystemExit):
    pass


class GeneratedMirrorAbsentError(Exception):
    """The generated plugin mirror is not on disk, so its scope is unestablished."""


# `/plugins/` is gitignored on purpose (6e05e026e): it is derived, and
# `sync_root_plugin_manifests.py` rewrites it byte-identically. That makes the git
# listing the WRONG RULER for it -- `git ls-files --others --exclude-standard`
# honors .gitignore, so every detector scoping through `iter_matching_repo_files`
# saw zero mirror files while 1,045 sat on disk, and still printed "Validated".
GENERATED_MIRROR_DIRNAME = "plugins"


def iter_generated_mirror_files(repo_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    """Scope over the generated plugin mirror, which git deliberately cannot see.

    Raises ``GeneratedMirrorAbsentError`` when the mirror is not on disk rather
    than returning ``[]``. An empty list here would be indistinguishable from a
    mirror that legitimately contains no matching file, and that collapse is the
    whole defect: a caller cannot tell "I examined the mirror and found nothing"
    from "there was no mirror to examine." The producer is unconditional, so
    absence is never a legitimate discovered-empty family -- it means nobody ran
    `scripts/sync_root_plugin_manifests.py`.
    """
    mirror_root = repo_root / GENERATED_MIRROR_DIRNAME
    if not mirror_root.is_dir():
        raise GeneratedMirrorAbsentError(
            f"generated plugin mirror is absent at {mirror_root}; "
            "run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` first"
        )
    matches: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            matches.append(path)
    return sorted(matches)


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def git_list_repo_files(
    repo_root: Path,
    *,
    include_untracked: bool = True,
    require_git: bool = False,
) -> list[Path] | None:
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
        if require_git:
            raise RepoFileListingError(
                "repo file listing failed\n"
                f"command: {' '.join(args)}\n"
                f"exit_code: {result.returncode}\n"
                f"STDOUT:\n{_decode_output(result.stdout)}\n"
                f"STDERR:\n{_decode_output(result.stderr)}"
            )
        return None
    return sorted(repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel)


def iter_repo_files(
    repo_root: Path,
    *,
    include_untracked: bool = True,
    require_git: bool = False,
) -> list[Path]:
    paths = git_list_repo_files(
        repo_root,
        include_untracked=include_untracked,
        require_git=require_git,
    )
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
    require_git: bool = False,
) -> list[Path]:
    standard_patterns, support_subpatterns = _split_support_patterns(patterns)
    support_root = support_dir(repo_root)
    support_is_external = support_root != (repo_root / "skills" / "support").resolve()
    if not support_is_external:
        standard_patterns.extend(_SUPPORT_PATTERN_PREFIX + sub for sub in support_subpatterns)
        support_subpatterns = []

    matches: list[Path] = []
    seen: set[Path] = set()

    git_paths = git_list_repo_files(
        repo_root,
        include_untracked=include_untracked,
        require_git=require_git,
    )
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
