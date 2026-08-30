"""One captured-tree Git snapshot for premise preflight validation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CapturedTreeSnapshot:
    available: bool
    commit_exists: bool
    modes: dict[str, str]
    objects: dict[str, tuple[str, bytes] | None]


def _parse_batch(payload: bytes, count: int) -> list[tuple[str, bytes] | None] | None:
    parsed: list[tuple[str, bytes] | None] = []
    cursor = 0
    for _ in range(count):
        header_end = payload.find(b"\n", cursor)
        if header_end < 0:
            return None
        header = payload[cursor:header_end]
        cursor = header_end + 1
        if header.endswith(b" missing"):
            parsed.append(None)
            continue
        fields = header.rsplit(b" ", 2)
        if len(fields) != 3:
            return None
        try:
            object_type = fields[1].decode("ascii")
            size = int(fields[2])
        except (UnicodeDecodeError, ValueError):
            return None
        end = cursor + size
        if end >= len(payload) or payload[end : end + 1] != b"\n":
            return None
        parsed.append((object_type, payload[cursor:end]))
        cursor = end + 1
    return parsed if not payload[cursor:] else None


def _batch_objects(
    repo_root: Path, expressions: list[str]
) -> list[tuple[str, bytes] | None] | None:
    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=repo_root,
        input=b"".join(expression.encode("utf-8", errors="surrogateescape") + b"\n" for expression in expressions),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return _parse_batch(result.stdout, len(expressions))


def _tree_modes(repo_root: Path, revision: str, paths: list[str]) -> dict[str, str] | None:
    if not paths:
        return {}
    result = subprocess.run(
        ["git", "ls-tree", "-z", revision, "--", *paths],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    modes: dict[str, str] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            return None
        path = raw_path.decode("utf-8", errors="surrogateescape")
        modes[path] = fields[0].decode("ascii", errors="strict")
    return modes


def _individual_snapshot(
    repo_root: Path,
    revision: str,
    protected_paths: list[str],
    expected_missing: list[str],
) -> CapturedTreeSnapshot:
    commit = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    modes: dict[str, str] = {}
    objects: dict[str, tuple[str, bytes] | None] = {}
    for path in protected_paths:
        listing = subprocess.run(
            ["git", "ls-tree", revision, "--", path],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
        fields = listing.stdout.split(maxsplit=1)
        if listing.returncode == 0 and fields:
            modes[path] = fields[0].decode("ascii", errors="ignore")
        expression = f"{revision}:{path}"
        result = subprocess.run(
            ["git", "cat-file", "--batch"],
            cwd=repo_root,
            input=expression.encode("utf-8", errors="surrogateescape") + b"\n",
            capture_output=True,
            check=False,
        )
        parsed = _parse_batch(result.stdout, 1) if result.returncode == 0 else None
        objects[path] = parsed[0] if parsed else None
    for path in expected_missing:
        expression = f"{revision}:{path}"
        result = subprocess.run(
            ["git", "cat-file", "-e", expression],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
        objects[path] = ("present", b"") if result.returncode == 0 else None
    return CapturedTreeSnapshot(True, commit.returncode == 0, modes, objects)


def inspect_captured_tree(
    repo_root: Path,
    revision: str,
    protected_paths: list[str],
    expected_missing: list[str],
) -> CapturedTreeSnapshot:
    """Read commit existence, path modes, and objects without per-path Git calls."""
    all_paths = [*protected_paths, *expected_missing]
    if any("\n" in path or "\r" in path for path in all_paths):
        return _individual_snapshot(repo_root, revision, protected_paths, expected_missing)
    expressions = [f"{revision}^{{commit}}", *(f"{revision}:{path}" for path in all_paths)]
    objects = _batch_objects(repo_root, expressions)
    modes = _tree_modes(repo_root, revision, protected_paths)
    if objects is None or modes is None:
        return CapturedTreeSnapshot(False, False, {}, {})
    commit = objects[0]
    path_objects = dict(zip(all_paths, objects[1:]))
    return CapturedTreeSnapshot(
        True,
        commit is not None and commit[0] == "commit",
        modes,
        path_objects,
    )
