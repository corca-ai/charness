"""Inspect and reclaim Charness-owned runtime scratch roots."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any


def _root_status(
    core: ModuleType,
    path: Path,
    owner: dict[str, Any] | None,
    *,
    repo_root: Path,
    max_entries: int,
    worktrees: list[Path],
    worktree_inventory_ok: bool,
    now: datetime,
) -> dict[str, Any]:
    entries, size, truncated = core._tree_inventory(path, max_entries=max_entries)
    if owner is None or owner.get("schema") != core.SCHEMA:
        return {
            "path": str(path),
            "status": "unknown",
            "disposition": "refuse-unknown-owner",
            "entries": entries,
            "bytes": size,
            "truncated": truncated,
        }
    retention = owner.get("retention")
    state = owner.get("state")
    expected_producer = path.parent.name
    expected_run_id = path.name
    ownership_shape_ok = (
        owner.get("owner") == "charness"
        and isinstance(owner.get("producer"), str)
        and isinstance(owner.get("run_id"), str)
        and owner.get("producer") == expected_producer
        and owner.get("run_id") == expected_run_id
    )
    if not ownership_shape_ok:
        return {
            "path": str(path),
            "status": "unknown",
            "disposition": "refuse-owner-identity",
            "entries": entries,
            "bytes": size,
            "truncated": truncated,
        }
    expected_identity = core._repo_identity(repo_root)
    owner_root = owner.get("repo_root")
    owner_identity = owner.get("repo_identity")
    repo_matches = (
        owner_identity == expected_identity
        and isinstance(owner_root, str)
        and Path(owner_root).expanduser().resolve() == repo_root.resolve()
    )
    active_lock = core._lock_is_active(path / core.OWNER_LOCK_NAME)
    active_pid = (
        core._pid_is_alive(owner.get("pid"))
        or core._pid_is_alive(owner.get("runner_pid"))
        if state == "active"
        else False
    )
    # A scratch root under the repository is not itself a registered worktree.
    # The old bidirectional containment check treated the repository worktree as
    # the scratch root's owner, so repo-local runtime roots could never recover.
    registered = (
        any(
            worktree.resolve() == path.resolve() or core._contains_path(path, worktree)
            for worktree in worktrees
        )
        if worktree_inventory_ok
        else False
    )
    expires_at = owner.get("expires_at")
    expired = False
    if isinstance(expires_at, str):
        try:
            expired = datetime.fromisoformat(expires_at.replace("Z", "+00:00")) <= now
        except ValueError:
            pass
    reasons: list[str] = []
    if not repo_matches:
        reasons.append("repo-mismatch")
    if not worktree_inventory_ok:
        reasons.append("worktree-inventory-error")
    if active_lock or active_pid:
        reasons.append("active")
    if registered:
        reasons.append("registered-worktree")
    if retention != "scratch":
        reasons.append("retention")
    if state not in core.TERMINAL_STATES:
        reasons.append("non-terminal")
    if not expired:
        reasons.append("unexpired")
    orphaned = (
        repo_matches
        and worktree_inventory_ok
        and state == "active"
        and not active_lock
        and not active_pid
        and not registered
        and expired
    )
    if orphaned:
        reasons.append("orphaned")
    return {
        "path": str(path),
        "status": "owned",
        "producer": owner.get("producer"),
        "repo_root": owner.get("repo_root"),
        "repo_identity": owner.get("repo_identity"),
        "repo_matches": repo_matches,
        "run_id": owner.get("run_id"),
        "state": state,
        "retention": retention,
        "created_at": owner.get("created_at"),
        "expires_at": expires_at,
        "active_lock": active_lock,
        "active_pid": active_pid,
        "registered_worktree": registered,
        "entries": entries,
        "bytes": size,
        "truncated": truncated,
        "orphaned": orphaned,
        "disposition": "refuse-" + ",".join(reasons) if reasons else "eligible",
    }


def inspect_scratch_roots(
    core: ModuleType,
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    root = (
        Path(runtime_root_path).expanduser().resolve()
        if runtime_root_path is not None
        else core.runtime_root(Path(repo_root).expanduser().resolve())
    ) / core.SCRATCH_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    resolved_repo = Path(repo_root).expanduser().resolve()
    worktree_inventory_error = None
    try:
        worktrees = core._registered_worktrees(resolved_repo)
    except core.ScratchError as exc:
        # A failed worktree inventory is a safety stop. We still report the
        # roots so an operator can diagnose them, but none can become eligible
        # for removal while the inventory is unknown.
        worktrees = []
        worktree_inventory_error = str(exc)
    children: list[Path] = []
    for producer in sorted(root.iterdir()):
        if not producer.is_dir() or producer.is_symlink():
            continue
        children.extend(
            path
            for path in sorted(producer.iterdir())
            if path.is_dir() and not path.is_symlink()
        )
    truncated_roots = len(children) > max_roots
    children = children[:max_roots]
    now = core._utc_now()
    roots = [
        _root_status(
            core,
            path,
            core._read_owner(path / core.OWNER_RECEIPT_NAME),
            repo_root=resolved_repo,
            max_entries=max_entries,
            worktrees=worktrees,
            worktree_inventory_ok=worktree_inventory_error is None,
            now=now,
        )
        for path in children
    ]
    return {
        "schema": "charness.runtime-scratch-inspection/v1",
        "repo_root": str(resolved_repo),
        "scratch_root": str(root),
        "roots": roots,
        "root_count": len(roots),
        "truncated": truncated_roots,
        "max_roots": max_roots,
        "max_entries": max_entries,
        "ok": worktree_inventory_error is None,
        "worktree_inventory_error": worktree_inventory_error,
    }


def gc_scratch_roots(
    core: ModuleType,
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    dry_run: bool = True,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    report = inspect_scratch_roots(
        core,
        repo_root,
        runtime_root_path=runtime_root_path,
        max_roots=max_roots,
        max_entries=max_entries,
    )
    reclaimed_entries = 0
    reclaimed_bytes = 0
    for item in report["roots"]:
        if item.get("disposition") != "eligible":
            continue
        path = Path(item["path"])
        if dry_run:
            item["disposition"] = "would-remove"
            continue
        if not path.is_dir() or path.is_symlink():
            item["disposition"] = "refuse-path-changed"
            continue
        core._rmtree_writable(path)
        reclaimed_entries += int(item.get("entries", 0))
        reclaimed_bytes += int(item.get("bytes", 0))
        item["disposition"] = "removed"
    report.update(
        {
            "schema": "charness.runtime-scratch-gc/v1",
            "dry_run": dry_run,
            "reclaimed_entries": reclaimed_entries,
            "reclaimed_bytes": reclaimed_bytes,
        }
    )
    return report


def recover_scratch_roots(
    core: ModuleType,
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    dry_run: bool = True,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    """Mark only expired, identity-matching orphan owners as failed.

    Recovery is deliberately separate from GC: it preserves the retained bytes
    and only makes a dead owner terminal, after which the ordinary GC policy can
    inspect and remove it. A second read and lock check closes the race between
    inspection and recovery.
    """
    report = inspect_scratch_roots(
        core,
        repo_root,
        runtime_root_path=runtime_root_path,
        max_roots=max_roots,
        max_entries=max_entries,
    )
    recovered = 0
    for item in report["roots"]:
        if not item.get("orphaned"):
            continue
        path = Path(item["path"])
        if dry_run:
            item["disposition"] = "would-recover-orphan"
            continue
        if not path.is_dir() or path.is_symlink():
            item["disposition"] = "refuse-path-changed"
            continue
        owner_path = path / core.OWNER_RECEIPT_NAME
        owner = core._read_owner(owner_path)
        if owner is None or owner.get("state") != "active":
            item["disposition"] = "refuse-owner-changed"
            continue
        if core._lock_is_active(path / core.OWNER_LOCK_NAME) or core._pid_is_alive(owner.get("pid")):
            item["disposition"] = "refuse-owner-active"
            continue
        if owner.get("repo_identity") != core._repo_identity(Path(repo_root).expanduser().resolve()):
            item["disposition"] = "refuse-repo-mismatch"
            continue
        hold_out_recovery = _restore_hold_out_paths(core, Path(repo_root).expanduser().resolve(), path, owner)
        if hold_out_recovery.get("status") == "refused":
            item["hold_out_recovery"] = hold_out_recovery
            item["disposition"] = "refuse-hold-out-restore"
            continue
        now = core._utc_now()
        owner["state"] = "failed"
        owner["retention"] = "retained-evidence"
        owner["hold_out_recovery"] = hold_out_recovery
        owner["recovered_at"] = core._iso(now)
        owner["recovery_reason"] = "expired owner process and lock are both inactive"
        owner["updated_at"] = core._iso(now)
        core._write_json(owner_path, owner)
        item["state"] = "failed"
        item["retention"] = "retained-evidence"
        item["orphaned"] = False
        item["disposition"] = "recovered-orphan"
        recovered += 1
    report.update({"schema": "charness.runtime-scratch-recovery/v1", "dry_run": dry_run, "recovered": recovered})
    return report


def _restore_hold_out_paths(
    core: ModuleType, repo_root: Path, owner_path: Path, owner: dict[str, Any]
) -> dict[str, Any]:
    """Restore hold-out moves recorded before an owner process disappeared."""
    raw_entries = owner.get("hold_out_paths")
    if raw_entries is None:
        return {"status": "not-present"}
    if not isinstance(raw_entries, list):
        return {"status": "refused", "reason": "hold-out mapping is not a list"}

    mappings: list[tuple[dict[str, Any], Path, Path]] = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            return {"status": "refused", "reason": "hold-out mapping entry is not an object"}
        raw_source = entry.get("source")
        raw_staged = entry.get("staged")
        if not isinstance(raw_source, str) or not isinstance(raw_staged, str):
            return {"status": "refused", "reason": "hold-out mapping has no source and staged paths"}
        source = _safe_relative_path(repo_root, raw_source)
        staged = _safe_relative_path(owner_path, raw_staged)
        if source is None or staged is None or source == repo_root or staged == owner_path:
            return {"status": "refused", "reason": "hold-out mapping escaped its owner boundary"}
        mappings.append((entry, source, staged))

    restored: list[str] = []
    untouched: list[str] = []
    for entry, source, staged in mappings:
        source_present = source.exists() or source.is_symlink()
        staged_present = staged.exists() or staged.is_symlink()
        if source_present and staged_present:
            return {
                "status": "refused",
                "reason": "hold-out source and staged paths both exist",
                "source": str(source),
                "staged": str(staged),
            }
        if staged_present and not source_present:
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staged), str(source))
            entry["state"] = "restored"
            restored.append(str(source.relative_to(repo_root)))
        else:
            entry["state"] = "already-restored" if source_present else "not-moved"
            untouched.append(str(source.relative_to(repo_root)))
    owner["hold_out_paths"] = raw_entries
    return {
        "status": "restored",
        "restored": restored,
        "untouched": untouched,
    }


def _safe_relative_path(base: Path, raw: str) -> Path | None:
    candidate = base / Path(raw)
    if Path(raw).is_absolute():
        return None
    try:
        resolved = candidate.resolve()
        resolved.relative_to(base.resolve())
    except (OSError, ValueError):
        return None
    return resolved
