from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

_FULL_OBJECT_ID_RE = re.compile(r"^[0-9a-f]+$")


def _git(repo_root: Path, *args: str, text: bool = True):
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=text,
    )
    if result.returncode != 0:
        stderr = result.stderr if text else os.fsdecode(result.stderr)
        raise ValueError(
            f"git {' '.join(args)} failed\nexit_code: {result.returncode}\n{stderr.strip()}"
        )
    return result.stdout


def resolve_full_commit(repo_root: Path, ref: str) -> str:
    return _git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()


def path_list_sha256(paths: list[str]) -> str:
    payload = b"".join(os.fsencode(path) + b"\0" for path in paths)
    return hashlib.sha256(payload).hexdigest()


def _collect_resolved_range(
    repo_root: Path, base_sha: str, head_sha: str
) -> dict[str, object]:
    changed_range = f"{base_sha}..{head_sha}"
    raw_paths = _git(
        repo_root, "diff", "--name-only", "-z", changed_range, text=False
    )
    encoded_paths = raw_paths[:-1].split(b"\0") if raw_paths.endswith(b"\0") else raw_paths.split(b"\0")
    paths = [os.fsdecode(path) for path in encoded_paths if path]
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_paths": paths,
        "path_count": len(paths),
        "paths_sha256": hashlib.sha256(raw_paths).hexdigest(),
    }


def collect_immutable_range(repo_root: Path, changed_range: str) -> dict[str, object]:
    endpoints = changed_range.split("..")
    if len(endpoints) != 2 or not all(
        _FULL_OBJECT_ID_RE.fullmatch(item) for item in endpoints
    ):
        raise ValueError(
            "--changed-range requires immutable full lowercase object IDs: BASE..HEAD"
        )
    base_sha, head_sha = endpoints
    if (
        resolve_full_commit(repo_root, base_sha) != base_sha
        or resolve_full_commit(repo_root, head_sha) != head_sha
    ):
        raise ValueError(
            "--changed-range requires immutable full lowercase object IDs: BASE..HEAD"
        )
    return _collect_resolved_range(repo_root, base_sha, head_sha)


def collect_release_delta(repo_root: Path, base_ref: str, head_ref: str = "HEAD") -> dict[str, object]:
    base_sha = resolve_full_commit(repo_root, base_ref)
    head_sha = resolve_full_commit(repo_root, head_ref)
    return _collect_resolved_range(repo_root, base_sha, head_sha)
