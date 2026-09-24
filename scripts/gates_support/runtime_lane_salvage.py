"""Preserve dirty finished-lane content before runtime retention removes a worktree."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path
from typing import Any, Callable

SALVAGE_PATCH = "uncommitted.patch"
SALVAGE_TAR = "uncommitted-untracked.tar"
SALVAGE_RECORD = "uncommitted.json"


def salvage_uncommitted(
    worktree: Path, record: Path, *, git: Callable[..., Any], dry_run: bool = False
) -> dict[str, Any]:
    """Save tracked and untracked edits beside a finished lane's result.

    Returns ``unverified`` when the saved patch or archive cannot be read back,
    so the caller can keep the only remaining copy in the worktree.
    """
    if not (worktree / ".git").exists():
        return {"status": "not-a-worktree"}
    head = git(worktree, "rev-parse", "HEAD")
    if head.returncode != 0:
        return {"status": "unverified", "error": f"rev-parse HEAD failed: {head.stderr.strip()}"}
    status = git(worktree, "status", "--porcelain", "-z", "--untracked-files=all")
    if status.returncode != 0:
        return {"status": "unverified", "error": f"status failed: {status.stderr.strip()}"}
    lines = porcelain_z_entries(status.stdout)
    if not lines:
        return {"status": "clean", "head": head.stdout.strip()}
    tracked = [line for line in lines if not line.startswith("??")]
    untracked = [line[3:] for line in lines if line.startswith("??")]
    result: dict[str, Any] = {"status": "salvaged", "head": head.stdout.strip(), "files": []}
    if dry_run:
        result.update(status="would-salvage", tracked=len(tracked), untracked=len(untracked))
        return result
    if tracked:
        diff = git(worktree, "diff", "HEAD", "--binary")
        if diff.returncode != 0:
            return {"status": "unverified", "error": f"diff failed: {diff.stderr.strip()}"}
        patch = record / SALVAGE_PATCH
        patch.write_text(diff.stdout, encoding="utf-8")
        check = git(worktree, "apply", "--check", "-R", str(patch))
        if check.returncode != 0:
            return {
                "status": "unverified",
                "error": f"apply --check -R refused the salvaged patch: {check.stderr.strip()[-400:]}",
            }
        result["files"].append(str(patch))
        result["patch_verified"] = True
    if untracked:
        archive = record / SALVAGE_TAR
        missing = [rel for rel in untracked if not (worktree / rel).exists()]
        if missing:
            return {
                "status": "unverified",
                "error": f"untracked path(s) reported by git are not on disk: {', '.join(missing[:5])}",
            }
        with tarfile.open(archive, "w") as tar:
            for rel in untracked:
                tar.add(worktree / rel, arcname=rel)
        with tarfile.open(archive) as tar:
            members = set(tar.getnames())
        absent = [rel for rel in untracked if rel not in members and rel.rstrip("/") not in members]
        if absent:
            return {
                "status": "unverified",
                "error": f"salvage archive is missing {len(absent)} untracked path(s): {', '.join(absent[:5])}",
            }
        result["files"].append(str(archive))
        result["archive_members"] = len(members)
    (record / SALVAGE_RECORD).write_text(
        json.dumps(
            {"head": result["head"], "tracked": tracked, "untracked": untracked, "files": result["files"]},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result["files"].append(str(record / SALVAGE_RECORD))
    return result


def porcelain_z_entries(stdout: str) -> list[str]:
    """Parse ``git status --porcelain -z``, discarding rename source records."""
    records = stdout.split("\0")
    entries: list[str] = []
    skip_next = False
    for record in records:
        if skip_next:
            skip_next = False
            continue
        if not record:
            continue
        entries.append(record)
        if record[:1] in {"R", "C"} or record[1:2] in {"R", "C"}:
            skip_next = True
    return entries
