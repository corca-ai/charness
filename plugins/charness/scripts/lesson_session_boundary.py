"""Parent-owned lesson-session context and worker write fence.

The lesson ledger is durable coordination state, not a per-worker scratch file.
This module is the narrow boundary workers use to consume the parent's frozen
bundle.  It never appends to the ledger and it only permits a write-once receipt
under ``.charness/lesson-lanes/<lane>/receipt.json``.  Its blind class is an
untracked or out-of-process write that happens without a later path inventory;
callers still need the lane acceptance check after the worker exits.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

try:
    from scripts import lesson_evaluation_continuity_lib as continuity
    from scripts.atomic_write_lib import write_once as _atomic_write_once
except ImportError:
    import lesson_evaluation_continuity_lib as continuity
    from atomic_write_lib import write_once as _atomic_write_once

LEDGER_RELATIVE = PurePosixPath("charness-artifacts/retro/lesson-ledger.json")
RECENT_LESSONS_RELATIVE = PurePosixPath("charness-artifacts/retro/recent-lessons.md")
RECEIPTS_PREFIX = PurePosixPath("charness-artifacts/retro/lesson-session-receipts")
LANE_ROOT = PurePosixPath(".charness/lesson-lanes")
LANE_RECEIPT_KIND = "charness.lesson-lane-receipt"
LANE_RECEIPT_VERSION = 1
_LANE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


class LessonSessionBoundaryError(ValueError):
    """A worker cannot prove parent ownership or its permitted write scope."""


@dataclass(frozen=True)
class ParentLessonSession:
    repo_root: Path
    session_id: str
    snapshot_sha256: str
    bundle_path: Path
    receipt_path: Path
    bundle_sha256: str
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "snapshot_sha256": self.snapshot_sha256,
            "bundle_path": self.bundle_path.relative_to(self.repo_root).as_posix(),
            "receipt_path": self.receipt_path.relative_to(self.repo_root).as_posix(),
            "bundle_sha256": self.bundle_sha256,
            "receipt_sha256": self.receipt_sha256,
            "writes_enabled": False,
            "owner": "parent",
        }


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(repo_root: Path, value: Path | str, label: str) -> tuple[Path, PurePosixPath]:
    root = repo_root.resolve()
    candidate = Path(str(value).replace("\\", "/")).expanduser()
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = PurePosixPath(resolved.relative_to(root).as_posix())
    except ValueError as exc:
        raise LessonSessionBoundaryError(f"{label} resolves outside the repository") from exc
    if relative.is_absolute() or ".." in relative.parts:
        raise LessonSessionBoundaryError(f"{label} is not a canonical repository-relative path")
    return resolved, relative


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LessonSessionBoundaryError(f"{label} is not readable JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LessonSessionBoundaryError(f"{label} must contain an object")
    return value


def load_parent_session(
    repo_root: Path,
    *,
    session_id: str | None = None,
    bundle_path: Path | str | None = None,
    receipt_path: Path | str | None = None,
) -> ParentLessonSession:
    """Read and verify the immutable session selected by the parent."""
    root = repo_root.resolve()
    output_dir = root / "charness-artifacts/retro"
    ledger_path = output_dir / "lesson-ledger.json"
    ledger = _read_json(ledger_path, "parent lesson ledger")
    events = ledger.get("session_events")
    if not isinstance(events, list):
        raise LessonSessionBoundaryError("parent lesson ledger has no session_events list")
    sessions = {
        event.get("session_id"): event
        for event in events
        if isinstance(event, dict) and isinstance(event.get("session_id"), str)
    }
    if session_id is None:
        if receipt_path is None:
            raise LessonSessionBoundaryError("worker inheritance requires session_id or receipt_path")
        receipt_candidate, _ = _repo_relative(root, receipt_path, "parent receipt")
        session_id = _read_json(receipt_candidate, "parent lesson receipt").get("session_id")
    try:
        session_id = continuity.validate_session_id(session_id)
    except (TypeError, ValueError) as exc:
        raise LessonSessionBoundaryError(str(exc)) from exc
    event = sessions.get(session_id)
    if event is None:
        raise LessonSessionBoundaryError(f"parent lesson session `{session_id}` is not in the ledger")
    receipt_file, _ = _repo_relative(
        root,
        receipt_path or continuity.receipt_path(output_dir, session_id),
        "parent receipt",
    )
    bundle_file, _ = _repo_relative(
        root,
        bundle_path or continuity.bundle_path(output_dir, session_id),
        "parent bundle",
    )
    receipt = _read_json(receipt_file, "parent lesson receipt")
    try:
        continuity.validate_receipt(receipt, sessions=sessions, output_dir=output_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise LessonSessionBoundaryError(f"parent lesson receipt/bundle is not valid immutable evidence: {exc}") from exc
    if receipt.get("session_id") != session_id:
        raise LessonSessionBoundaryError("parent lesson receipt session_id does not match the requested session")
    if bundle_file != continuity.bundle_path(output_dir, session_id).resolve():
        if not bundle_file.is_file() or _digest(bundle_file) != receipt.get("stdout_sha256"):
            raise LessonSessionBoundaryError("parent lesson bundle is not the receipt-bound immutable bytes")
    if not bundle_file.is_file():
        raise LessonSessionBoundaryError("parent lesson bundle is missing")
    return ParentLessonSession(
        repo_root=root,
        session_id=session_id,
        snapshot_sha256=str(event["snapshot_sha256"]),
        bundle_path=bundle_file,
        receipt_path=receipt_file,
        bundle_sha256=_digest(bundle_file),
        receipt_sha256=_digest(receipt_file),
    )


def lane_receipt_path(repo_root: Path, lane_id: str) -> Path:
    if not isinstance(lane_id, str) or not _LANE_ID.fullmatch(lane_id):
        raise LessonSessionBoundaryError("lane_id must be a path-safe non-empty identifier")
    return repo_root.resolve() / Path(".charness/lesson-lanes") / lane_id / "receipt.json"


def _lane_relative(repo_root: Path, value: Path | str, lane_id: str) -> Path:
    expected = lane_receipt_path(repo_root, lane_id).resolve()
    actual, _ = _repo_relative(repo_root, value, "lane receipt")
    if actual != expected:
        raise LessonSessionBoundaryError(
            f"lane receipt must be exactly `{expected.relative_to(repo_root.resolve()).as_posix()}`"
        )
    return actual


def _write_once(path: Path, payload: dict[str, Any]) -> None:
    path = Path(os.fspath(path))
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        _atomic_write_once(path, body.encode("utf-8"), label="lane receipt")
    except ValueError as exc:
        raise LessonSessionBoundaryError(str(exc)) from exc


def write_lane_receipt(
    context: ParentLessonSession,
    *,
    lane_id: str,
    owner_id: str,
    receipt_path: Path | str | None = None,
) -> Path:
    """Record worker inheritance without touching parent coordination state."""
    if not isinstance(owner_id, str) or not owner_id.strip():
        raise LessonSessionBoundaryError("owner_id must be a non-empty string")
    path = _lane_relative(context.repo_root, receipt_path or lane_receipt_path(context.repo_root, lane_id), lane_id)
    body = {
        "kind": LANE_RECEIPT_KIND,
        "schema_version": LANE_RECEIPT_VERSION,
        "lane_id": lane_id,
        "owner_id": owner_id.strip(),
        "session_id": context.session_id,
        "snapshot_sha256": context.snapshot_sha256,
        "bundle_sha256": context.bundle_sha256,
        "parent_receipt_sha256": context.receipt_sha256,
        "writes_enabled": False,
        "status": "inherited",
    }
    body["receipt_sha256"] = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    _write_once(path, body)
    return path


def validate_lane_writes(
    repo_root: Path,
    changed_paths: Iterable[str],
    *,
    assigned_paths: Iterable[str] = (),
    owner_role: str = "worker",
    lane_id: str | None = None,
) -> dict[str, Any]:
    """Fail closed when a worker mutates global lesson state.

    Global paths may be assigned only to the explicit ``parent`` owner.  A
    worker's sole permitted lesson-state path is its lane-local receipt.
    """
    root = repo_root.resolve()
    changed: set[PurePosixPath] = set()
    raw_changed: dict[PurePosixPath, str] = {}
    for raw in changed_paths:
        try:
            _resolved, relative = _repo_relative(root, str(raw), "changed path")
        except LessonSessionBoundaryError:
            # An uncanonicalizable path is itself a forbidden write. Keep a
            # stable spelling for the refusal rather than allowing a traversal
            # or absolute alias to disappear from the inventory.
            relative = PurePosixPath(str(raw).replace("\\", "/"))
        changed.add(relative)
        raw_changed[relative] = str(raw)
    assigned: set[PurePosixPath] = set()
    for raw in assigned_paths:
        try:
            _resolved, relative = _repo_relative(root, str(raw), "assigned path")
        except LessonSessionBoundaryError as exc:
            raise LessonSessionBoundaryError(str(exc)) from exc
        assigned.add(relative)
    global_paths = {LEDGER_RELATIVE, RECENT_LESSONS_RELATIVE}
    lane_relative = None
    if lane_id is not None:
        lane_relative = PurePosixPath(lane_receipt_path(root, lane_id).resolve().relative_to(root).as_posix())
    forbidden: list[str] = []
    lane_prefix = LANE_ROOT.parts
    for path in sorted(changed, key=str):
        is_lane_path = len(path.parts) >= len(lane_prefix) and path.parts[: len(lane_prefix)] == lane_prefix
        is_receipt = path == LEDGER_RELATIVE or path == RECENT_LESSONS_RELATIVE or (
            len(path.parts) > len(RECEIPTS_PREFIX.parts)
            and path.parts[: len(RECEIPTS_PREFIX.parts)] == RECEIPTS_PREFIX.parts
        )
        if is_lane_path:
            if lane_relative is None or path != lane_relative:
                forbidden.append(path.as_posix())
        elif is_receipt:
            if owner_role != "parent" or path not in assigned:
                forbidden.append(path.as_posix())
        elif lane_relative is not None and path == lane_relative:
            continue
    if forbidden:
        raise LessonSessionBoundaryError(
            "worker write fence refused parent-owned lesson paths: " + ", ".join(forbidden)
        )
    return {
        "ok": True,
        "owner_role": owner_role,
        "lane_id": lane_id,
        "changed_paths": sorted(path.as_posix() for path in changed),
        "parent_owned_paths": sorted(path.as_posix() for path in global_paths),
        "lane_receipt": lane_relative.as_posix() if lane_relative is not None else None,
    }


def validate_lane_receipt(
    repo_root: Path,
    receipt_path: Path | str,
    *,
    lane_id: str,
    owner_id: str,
    session_id: str,
    snapshot_sha256: str,
    bundle_sha256: str,
    parent_receipt_sha256: str,
) -> dict[str, Any]:
    """Validate the worker's immutable lane receipt at the final consumer."""
    path = _lane_relative(repo_root, receipt_path, lane_id)
    payload = _read_json(path, "worker lane receipt")
    expected = {
        "kind": LANE_RECEIPT_KIND,
        "schema_version": LANE_RECEIPT_VERSION,
        "lane_id": lane_id,
        "owner_id": owner_id,
        "session_id": session_id,
        "snapshot_sha256": snapshot_sha256,
        "bundle_sha256": bundle_sha256,
        "parent_receipt_sha256": parent_receipt_sha256,
        "writes_enabled": False,
        "status": "inherited",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            raise LessonSessionBoundaryError(
                f"worker lane receipt {field} does not match the parent lesson binding"
            )
    receipt_hash = payload.get("receipt_sha256")
    body = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    computed = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if receipt_hash != computed:
        raise LessonSessionBoundaryError("worker lane receipt hash is invalid")
    return {"ok": True, "path": path.relative_to(repo_root.resolve()).as_posix(), "receipt_sha256": receipt_hash}


def inherit_worker_session(
    repo_root: Path,
    *,
    bundle_path: Path | str,
    lane_id: str,
    owner_id: str,
    session_id: str | None = None,
    receipt_path: Path | str | None = None,
    lane_receipt_path_value: Path | str | None = None,
) -> tuple[ParentLessonSession, Path]:
    context = load_parent_session(
        repo_root,
        session_id=session_id,
        bundle_path=bundle_path,
        receipt_path=receipt_path,
    )
    return context, write_lane_receipt(
        context,
        lane_id=lane_id,
        owner_id=owner_id,
        receipt_path=lane_receipt_path_value,
    )
