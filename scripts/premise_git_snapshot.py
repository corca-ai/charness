"""One captured-tree Git snapshot for premise preflight validation."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # loaded as a standalone sibling module
    from scripts.core.subprocess_guard import run_process


@dataclass(frozen=True)
class CapturedTreeSnapshot:
    available: bool
    commit_exists: bool
    modes: dict[str, str]
    objects: dict[str, tuple[str, bytes] | None]
    current_head_sha: str | None = None
    current_head_commit: bytes | None = None
    index_objects: dict[str, tuple[str, bytes] | None] = field(default_factory=dict)


def _typed_payload(item: tuple[str, str, bytes] | None) -> tuple[str, bytes] | None:
    if item is None:
        return None
    return (item[1], item[2])


def _parse_batch(payload: bytes, count: int) -> list[tuple[str, str, bytes] | None] | None:
    parsed: list[tuple[str, str, bytes] | None] = []
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
            name = fields[0].decode("ascii")
            object_type = fields[1].decode("ascii")
            size = int(fields[2])
        except (UnicodeDecodeError, ValueError):
            return None
        end = cursor + size
        if end >= len(payload) or payload[end : end + 1] != b"\n":
            return None
        parsed.append((name, object_type, payload[cursor:end]))
        cursor = end + 1
    return parsed if not payload[cursor:] else None


def _batch_objects(
    repo_root: Path, expressions: list[str]
) -> list[tuple[str, str, bytes] | None] | None:
    payload = b"".join(
        expression.encode("utf-8", errors="surrogateescape") + b"\n" for expression in expressions
    )
    with tempfile.TemporaryFile() as source:
        source.write(payload)
        source.seek(0)
        saved_stdin = os.dup(0)
        try:
            os.dup2(source.fileno(), 0)
            result = run_process(
                ["git", "cat-file", "--batch"], cwd=repo_root, timeout_seconds=None
            )
        finally:
            os.dup2(saved_stdin, 0)
            os.close(saved_stdin)
    if result.returncode != 0:
        return None
    return _parse_batch(result.stdout.encode("utf-8", errors="surrogateescape"), len(expressions))


def _tree_modes(repo_root: Path, revision: str, paths: list[str]) -> dict[str, str] | None:
    if not paths:
        return {}
    result = run_process(
        ["git", "ls-tree", "-z", revision, "--", *paths],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        return None
    modes: dict[str, str] = {}
    for record in result.stdout.encode("utf-8", errors="surrogateescape").split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            return None
        path = raw_path.decode("utf-8", errors="surrogateescape")
        modes[path] = fields[0].decode("ascii", errors="strict")
    return modes


def _commit_parents_and_message(payload: bytes) -> tuple[list[str], str]:
    text = payload.decode("utf-8", errors="replace")
    header, separator, message = text.partition("\n\n")
    if not separator:
        return [], ""
    parents = [line[7:].strip() for line in header.splitlines() if line.startswith("parent ")]
    return parents, message


def history_contains_exact_line(
    repo_root: Path,
    head_sha: str,
    head_commit: bytes,
    line: str,
) -> bool | None:
    """Walk HEAD's parent chain from already-read commit bytes.

    Returns None when Git cannot supply a remaining parent object.
    """
    seen = {head_sha}
    queue: list[bytes] = [head_commit]
    while queue:
        parents, message = _commit_parents_and_message(queue.pop())
        if any(entry == line for entry in message.splitlines()):
            return True
        missing = [parent for parent in parents if parent not in seen]
        for parent in missing:
            seen.add(parent)
        if not missing:
            continue
        batched = _batch_objects(repo_root, missing)
        if batched is None:
            return None
        for item in batched:
            if item is None or item[1] != "commit":
                return None
            queue.append(item[2])
    return False


def _head_and_index(
    repo_root: Path, protected_paths: list[str]
) -> tuple[str | None, bytes | None, dict[str, tuple[str, bytes] | None]]:
    expressions = ["HEAD^{commit}", *(f":{path}" for path in protected_paths)]
    batched = _batch_objects(repo_root, expressions)
    if batched is None:
        return None, None, {path: None for path in protected_paths}
    head = batched[0]
    head_sha = head[0] if head is not None and head[1] == "commit" else None
    head_commit = head[2] if head is not None and head[1] == "commit" else None
    index_objects = {path: _typed_payload(item) for path, item in zip(protected_paths, batched[1:])}
    return head_sha, head_commit, index_objects


def _individual_snapshot(
    repo_root: Path,
    revision: str,
    protected_paths: list[str],
    expected_missing: list[str],
) -> CapturedTreeSnapshot:
    commit = run_process(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    modes: dict[str, str] = {}
    objects: dict[str, tuple[str, bytes] | None] = {}
    for path in protected_paths:
        listing = run_process(
            ["git", "ls-tree", revision, "--", path],
            cwd=repo_root,
            timeout_seconds=None,
        )
        fields = listing.stdout.encode("utf-8", errors="surrogateescape").split(maxsplit=1)
        if listing.returncode == 0 and fields:
            modes[path] = fields[0].decode("ascii", errors="ignore")
        expression = f"{revision}:{path}"
        parsed_items = _batch_objects(repo_root, [expression])
        parsed = parsed_items if parsed_items is not None else None
        objects[path] = _typed_payload(parsed[0] if parsed else None)
    for path in expected_missing:
        expression = f"{revision}:{path}"
        result = run_process(
            ["git", "cat-file", "-e", expression],
            cwd=repo_root,
            timeout_seconds=None,
        )
        objects[path] = ("present", b"") if result.returncode == 0 else None
    head_sha, head_commit, index_objects = _head_and_index(repo_root, protected_paths)
    return CapturedTreeSnapshot(
        True,
        commit.returncode == 0,
        modes,
        objects,
        head_sha,
        head_commit,
        index_objects,
    )


def inspect_captured_tree(
    repo_root: Path,
    revision: str,
    protected_paths: list[str],
    expected_missing: list[str],
) -> CapturedTreeSnapshot:
    """Read captured objects, current HEAD, and index blobs in one Git batch."""
    all_paths = [*protected_paths, *expected_missing]
    if any("\n" in path or "\r" in path for path in all_paths):
        return _individual_snapshot(repo_root, revision, protected_paths, expected_missing)
    expressions = [
        f"{revision}^{{commit}}",
        "HEAD^{commit}",
        *(f"{revision}:{path}" for path in all_paths),
        *(f":{path}" for path in protected_paths),
    ]
    objects = _batch_objects(repo_root, expressions)
    modes = _tree_modes(repo_root, revision, protected_paths)
    if objects is None or modes is None:
        return CapturedTreeSnapshot(False, False, {}, {})
    captured = objects[0]
    head = objects[1]
    path_offset = 2
    path_objects = {
        path: _typed_payload(item)
        for path, item in zip(all_paths, objects[path_offset : path_offset + len(all_paths)])
    }
    index_offset = path_offset + len(all_paths)
    index_objects = {
        path: _typed_payload(item) for path, item in zip(protected_paths, objects[index_offset:])
    }
    return CapturedTreeSnapshot(
        True,
        captured is not None and captured[1] == "commit",
        modes,
        path_objects,
        head[0] if head is not None and head[1] == "commit" else None,
        head[2] if head is not None and head[1] == "commit" else None,
        index_objects,
    )
