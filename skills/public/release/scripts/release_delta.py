from __future__ import annotations

import hashlib
import os
import re
import shlex
import sys
from pathlib import Path

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from scripts.core.subprocess_guard import run_process

_FULL_OBJECT_ID_RE = re.compile(r"^[0-9a-f]+$")
_RESOLVED_OBJECT_ID_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")


def _git(repo_root: Path, *args: str, text: bool = True, input_data=None):
    command: list[str] = ["git", *args]
    if input_data is not None:
        if not isinstance(input_data, str):
            raise ValueError("git input must be text")
        command_text = f"printf '%s' {shlex.quote(input_data)} | {shlex.join(command)}"
        result = run_process(command_text, cwd=repo_root, shell=True, timeout_seconds=None)
    else:
        result = run_process(command, cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        raise ValueError(
            f"git {' '.join(args)} failed\nexit_code: {result.returncode}\n{result.stderr.strip()}"
        )
    return result.stdout if text else result.stdout.encode("utf-8")


def resolve_full_commit(repo_root: Path, ref: str) -> str:
    return _git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()


def _resolve_release_commits(repo_root: Path, base_ref: str, head_ref: str) -> tuple[str, str]:
    refs = (("base", base_ref), ("head", head_ref))
    expressions = [f"{ref}^{{commit}}" for _, ref in refs]
    output = _git(
        repo_root,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype)",
        input_data="\n".join(expressions) + "\n",
    )
    if not isinstance(output, str):
        raise ValueError("git cat-file returned non-text ref resolution output")

    records = output.splitlines()
    resolved: list[str] = []
    for index, (label, ref) in enumerate(refs):
        if index >= len(records):
            raise ValueError(
                f"could not resolve {label} ref {ref!r}: git cat-file returned missing output"
            )
        fields = records[index].split()
        if (
            len(fields) != 2
            or not _RESOLVED_OBJECT_ID_RE.fullmatch(fields[0])
            or fields[1] != "commit"
        ):
            detail = (
                "git cat-file reported the object as missing"
                if records[index].endswith(" missing")
                else f"malformed git cat-file output {records[index]!r}"
            )
            raise ValueError(f"could not resolve {label} ref {ref!r}: {detail}")
        resolved.append(fields[0])

    if len(records) != len(refs):
        raise ValueError(
            "git cat-file returned unexpected extra ref resolution output for "
            f"base ref {base_ref!r} and head ref {head_ref!r}"
        )
    return resolved[0], resolved[1]


def path_list_sha256(paths: list[str]) -> str:
    payload = b"".join(os.fsencode(path) + b"\0" for path in paths)
    return hashlib.sha256(payload).hexdigest()


def _collect_resolved_range(repo_root: Path, base_sha: str, head_sha: str) -> dict[str, object]:
    changed_range = f"{base_sha}..{head_sha}"
    raw_paths = _git(repo_root, "diff", "--name-only", "-z", changed_range, text=False)
    encoded_paths = (
        raw_paths[:-1].split(b"\0") if raw_paths.endswith(b"\0") else raw_paths.split(b"\0")
    )
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
    if len(endpoints) != 2 or not all(_FULL_OBJECT_ID_RE.fullmatch(item) for item in endpoints):
        raise ValueError("--changed-range requires immutable full lowercase object IDs: BASE..HEAD")
    base_sha, head_sha = endpoints
    if (
        resolve_full_commit(repo_root, base_sha) != base_sha
        or resolve_full_commit(repo_root, head_sha) != head_sha
    ):
        raise ValueError("--changed-range requires immutable full lowercase object IDs: BASE..HEAD")
    return _collect_resolved_range(repo_root, base_sha, head_sha)


def collect_release_delta(
    repo_root: Path, base_ref: str, head_ref: str = "HEAD"
) -> dict[str, object]:
    base_sha, head_sha = _resolve_release_commits(repo_root, base_ref, head_ref)
    return _collect_resolved_range(repo_root, base_sha, head_sha)
