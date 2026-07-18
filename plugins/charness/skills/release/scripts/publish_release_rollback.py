"""Restore a clean release worktree when preparation fails before commit.

The publish CLI refuses dirty input, so the preparation phase owns every
tracked or untracked change it creates.  This module restores tracked paths to
the starting HEAD and quarantines newly created files instead of deleting them.
Once HEAD moves, rollback refuses: that state belongs to the resume contract.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any


def snapshot_clean_head(repo_root: Path, *, run_command) -> dict[str, str]:
    head_sha = run_command(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    status = run_command(["git", "status", "--short"], cwd=repo_root).stdout.strip()
    if status:
        raise SystemExit("release rollback snapshot requires the already-validated clean worktree")
    return {"head_sha": head_sha}


def _nul_paths(result: Any) -> list[str]:
    return sorted({path for path in result.stdout.split("\0") if path})


def _safe_repo_path(repo_root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe rollback path: {relative}")
    return repo_root / path


def _quarantine_new_paths(
    repo_root: Path,
    paths: list[str],
    *,
    quarantine_base: Path,
    tag_name: str,
) -> tuple[str | None, list[str], list[str]]:
    existing = [
        path
        for path in paths
        if (
            _safe_repo_path(repo_root, path).exists()
            or _safe_repo_path(repo_root, path).is_symlink()
        )
    ]
    if not existing:
        return None, [], []
    quarantine = quarantine_base / f"{tag_name}-{time.time_ns()}"
    moved: list[str] = []
    errors: list[str] = []
    for relative in existing:
        source = _safe_repo_path(repo_root, relative)
        target = quarantine / relative
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            moved.append(relative)
        except OSError as exc:
            errors.append(f"{relative}: {exc.__class__.__name__}: {exc}")
    return str(quarantine), moved, errors


def rollback_precommit_changes(
    repo_root: Path,
    snapshot: dict[str, str],
    *,
    tag_name: str,
    run_command,
) -> dict[str, Any]:
    """Rollback helper-owned preparation changes without rewriting a commit."""
    expected_head = snapshot["head_sha"]
    planned_tracked: list[str] = []
    restored: list[str] = []
    quarantined: list[str] = []
    quarantine_root: str | None = None
    quarantine_errors: list[str] = []
    try:
        current_head = run_command(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
        if current_head != expected_head:
            return {
                "status": "refused_head_changed",
                "expected_head": expected_head,
                "current_head": current_head,
                "reason": "HEAD moved; preserve the partial state for the resume contract",
            }

        changed = _nul_paths(
            run_command(
                ["git", "diff", "--no-renames", "--name-only", "-z", expected_head],
                cwd=repo_root,
            )
        )
        untracked = _nul_paths(
            run_command(
                ["git", "ls-files", "--others", "--exclude-standard", "-z"],
                cwd=repo_root,
            )
        )
        created: set[str] = set(untracked)
        staged_created: set[str] = set()
        for relative in changed:
            exists_at_head = run_command(
                ["git", "cat-file", "-e", f"{expected_head}:{relative}"],
                cwd=repo_root,
                check=False,
            ).returncode == 0
            if exists_at_head:
                planned_tracked.append(relative)
            else:
                created.add(relative)
                staged_created.add(relative)

        if planned_tracked:
            run_command(
                [
                    "git",
                    "restore",
                    "--source",
                    expected_head,
                    "--staged",
                    "--worktree",
                    "--",
                    *planned_tracked,
                ],
                cwd=repo_root,
            )
            restored = list(planned_tracked)
        created_paths = sorted(created)
        if staged_created:
            run_command(
                ["git", "restore", "--staged", "--", *sorted(staged_created)],
                cwd=repo_root,
            )
        git_quarantine_path = run_command(
            ["git", "rev-parse", "--git-path", "charness-release-rollbacks"],
            cwd=repo_root,
        ).stdout.strip()
        quarantine_base = Path(git_quarantine_path)
        if not quarantine_base.is_absolute():
            quarantine_base = repo_root / quarantine_base
        quarantine_root, quarantined, quarantine_errors = _quarantine_new_paths(
            repo_root,
            created_paths,
            quarantine_base=quarantine_base,
            tag_name=tag_name,
        )
        remaining = run_command(["git", "status", "--short"], cwd=repo_root).stdout.splitlines()
        return {
            "status": "restored" if not remaining and not quarantine_errors else "partial",
            "head_sha": expected_head,
            "restored_paths": restored,
            "quarantined_paths": quarantined,
            "quarantine_root": quarantine_root,
            "quarantine_errors": quarantine_errors,
            "remaining_status": remaining,
        }
    except BaseException as exc:
        try:
            remaining = run_command(
                ["git", "status", "--short"],
                cwd=repo_root,
                check=False,
            ).stdout.splitlines()
        except BaseException:
            remaining = ["status unavailable after rollback failure"]
        return {
            "status": "failed",
            "expected_head": expected_head,
            "error": f"{exc.__class__.__name__}: {exc}",
            "restored_paths": restored,
            "quarantined_paths": quarantined,
            "quarantine_root": quarantine_root,
            "quarantine_errors": quarantine_errors,
            "remaining_status": remaining,
        }
