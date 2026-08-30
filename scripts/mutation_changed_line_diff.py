"""Git diff batching primitives for changed-line mutation classification."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path


def _parse_changed_line_diff(output: str, requested: set[str]) -> dict[str, set[int]]:
    """Parse zero-context added-line hunks from one multi-path Git diff."""
    changed: dict[str, set[int]] = {path: set() for path in requested}
    current: str | None = None
    for line in output.splitlines():
        if line.startswith("+++ "):
            candidate = line[4:]
            if candidate.startswith("b/"):
                candidate = candidate[2:]
            current = candidate if candidate in requested else None
            continue
        if current is None:
            continue
        match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        changed[current].update(range(start, start + count))
    return changed


def changed_line_numbers_for_paths(
    repo_root: Path,
    base_sha: str,
    head_sha: str,
    paths: list[str],
    single_path_loader: Callable[[Path, str, str, str], set[int]],
) -> dict[str, set[int]]:
    """Return changed new-file lines for several paths in one Git invocation.

    Git quotes unusual path names in patch headers, so those names use the
    original per-path implementation to preserve its behavior rather than
    risking a parser under-approximation.
    """
    requested = set(paths)
    if not requested or not base_sha:
        return {path: set() for path in requested}
    if any(not re.fullmatch(r"[A-Za-z0-9_./-]+", path) for path in requested):
        return {
            path: single_path_loader(repo_root, base_sha, head_sha, path)
            for path in requested
        }
    head = head_sha or "HEAD"
    command = [
        "git",
        "diff",
        "-U0",
        "--no-renames",
        f"{base_sha}..{head}",
        "--",
        *sorted(requested),
    ]
    result = subprocess.run(command, cwd=repo_root, check=True, text=True, capture_output=True)
    return _parse_changed_line_diff(result.stdout, requested)
