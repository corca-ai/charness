"""One porcelain-v2 worktree observation.

Several owners asked Git the same question — what is dirty, and which HEAD is
checked out — then each parsed a private dialect. Consumers project views from
this snapshot; they do not parse status records.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Callable, NamedTuple

_GIT_OID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
GitBytes = Callable[..., bytes]


class GitStatusError(ValueError):
    pass


class GitStatusRecord(NamedTuple):
    kind: str
    xy: str
    path: str
    orig_path: str | None = None


class GitStatusSnapshot(NamedTuple):
    head_oid: str | None
    branch: str | None
    records: tuple[GitStatusRecord, ...]

    def dirty_destination_paths(self) -> list[str]:
        return [record.path for record in self.records if record.kind != "ignored"]

    def deleted_paths(self) -> frozenset[str]:
        return frozenset(
            record.path
            for record in self.records
            if record.kind in {"ordinary", "unmerged"} and "D" in record.xy
        )

    def populations(self) -> dict[str, list[str]]:
        tracked: list[str] = []
        untracked: list[str] = []
        ignored: list[str] = []
        for record in self.records:
            if record.kind == "untracked":
                untracked.append(record.path)
            elif record.kind == "ignored":
                ignored.append(record.path)
            else:
                tracked.append(record.path)
                if record.orig_path:
                    tracked.append(record.orig_path)
        return {
            "tracked": sorted(set(tracked)),
            "untracked": sorted(set(untracked)),
            "ignored": sorted(set(ignored)),
        }

    def staged_or_unstaged_dirty(self) -> tuple[bool, bool]:
        staged = unstaged = False
        for record in self.records:
            if record.kind in {"untracked", "ignored"}:
                continue
            xy = record.xy
            if record.kind == "unmerged" or len(xy) != 2:
                return True, True
            staged = staged or xy[0] != "."
            unstaged = unstaged or xy[1] != "."
        return staged, unstaged

    def untracked_paths(self) -> frozenset[str]:
        return frozenset(record.path for record in self.records if record.kind == "untracked")


def status_args(
    *,
    ignored: bool = False,
    branch: bool = True,
    untracked: str = "all",
    no_renames: bool = False,
) -> tuple[str, ...]:
    """Porcelain-v2 observation flags. Consumers vary the question; they do not parse."""
    args = ["status", "--porcelain=v2"]
    if branch:
        args.append("--branch")
    if no_renames:
        args.append("--no-renames")
    args.append(f"--untracked-files={untracked}")
    if ignored:
        args.append("--ignored=matching")
    return (*args, "-z")


def _nul_path(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


def _parse_oid(record: bytes, current: str | None) -> str | None:
    if current is not None:
        raise GitStatusError("git status reported multiple branch OIDs")
    try:
        value = record.removeprefix(b"# branch.oid ").decode("ascii")
    except UnicodeDecodeError as exc:
        raise GitStatusError("git status reported a malformed branch OID") from exc
    if _GIT_OID_RE.fullmatch(value) and set(value) - {"0"}:
        return value
    return current


def _parse_head_name(record: bytes) -> str | None:
    value = record.removeprefix(b"# branch.head ").decode("utf-8", errors="replace").strip()
    return None if value in {"", "(detached)"} else value


def _fixed_record(kind: str, record: bytes, splits: int, path_index: int) -> GitStatusRecord:
    fields = record.split(b" ", splits)
    if len(fields) != splits + 1:
        raise GitStatusError(f"unexpected git status record: {record!r}")
    return GitStatusRecord(
        kind,
        fields[1].decode("ascii", errors="replace"),
        _nul_path(fields[path_index]),
    )


def _parse_entry(
    record: bytes, records: list[bytes], index: int
) -> tuple[GitStatusRecord, int]:
    if record.startswith(b"? "):
        return GitStatusRecord("untracked", "", _nul_path(record[2:])), index
    if record.startswith(b"! "):
        return GitStatusRecord("ignored", "", _nul_path(record[2:])), index
    kind = record[:1]
    if kind == b"1":
        return _fixed_record("ordinary", record, 8, 8), index
    if kind == b"u":
        return _fixed_record("unmerged", record, 10, 10), index
    if kind != b"2":
        raise GitStatusError(f"unexpected git status record: {record!r}")
    fields = record.split(b" ", 9)
    if len(fields) != 10 or index >= len(records) or not records[index]:
        raise GitStatusError(f"unexpected git status record: {record!r}")
    return (
        GitStatusRecord(
            "rename",
            fields[1].decode("ascii", errors="replace"),
            _nul_path(fields[9]),
            _nul_path(records[index]),
        ),
        index + 1,
    )


def parse(payload: bytes) -> GitStatusSnapshot:
    records = payload.split(b"\0")
    parsed: list[GitStatusRecord] = []
    head_oid: str | None = None
    branch: str | None = None
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if record.startswith(b"# branch.oid "):
            head_oid = _parse_oid(record, head_oid)
            continue
        if record.startswith(b"# branch.head "):
            branch = _parse_head_name(record)
            continue
        if record.startswith(b"# "):
            continue
        entry, index = _parse_entry(record, records, index)
        parsed.append(entry)
    return GitStatusSnapshot(head_oid, branch, tuple(parsed))


def capture(
    repo_root: Path,
    *,
    ignored: bool = False,
    branch: bool = True,
    untracked: str = "all",
    no_renames: bool = False,
    env: Mapping[str, str] | None = None,
    git_bytes: GitBytes | None = None,
) -> GitStatusSnapshot:
    args = status_args(
        ignored=ignored, branch=branch, untracked=untracked, no_renames=no_renames
    )
    if git_bytes is not None:
        payload = git_bytes(repo_root, *args)
        return parse(payload if isinstance(payload, bytes) else payload.encode("utf-8"))
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        env=None if env is None else dict(env),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip() or "git status failed"
        raise GitStatusError(detail)
    return parse(result.stdout)
