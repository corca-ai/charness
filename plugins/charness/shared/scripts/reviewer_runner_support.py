"""Collection and lane-path helpers for the canonical reviewer runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable

try:
    from reviewer_delivery import (
        COLLECTION_FAILED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        TIMED_OUT,
        _read,
        _write,
        ledger_lock,
        utc_now,
    )
except ImportError:
    from skills.shared.scripts.reviewer_delivery import (
        COLLECTION_FAILED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        TIMED_OUT,
        _read,
        _write,
        ledger_lock,
        utc_now,
    )


def lesson_paths(repo_root: Path, args: Any) -> tuple[Path | None, Path | None]:
    """Resolve optional parent bundle/lane receipt and enforce all-or-none input."""
    bundle = (
        (repo_root / args.parent_lesson_bundle).resolve()
        if args.parent_lesson_bundle is not None and not args.parent_lesson_bundle.is_absolute()
        else (args.parent_lesson_bundle.resolve() if args.parent_lesson_bundle is not None else None)
    )
    receipt = (
        (repo_root / args.lesson_lane_receipt).resolve()
        if args.lesson_lane_receipt is not None and not args.lesson_lane_receipt.is_absolute()
        else (args.lesson_lane_receipt.resolve() if args.lesson_lane_receipt is not None else None)
    )
    values = (bundle, receipt, args.lesson_session_id, args.lesson_lane_id, args.lesson_owner_id)
    if any(value is not None for value in values) and not all(values):
        raise ValueError(
            "worker lesson inheritance requires parent bundle, lane receipt, lane id, and owner id"
        )
    return bundle, receipt


def _lesson_boundary_module(repo_root: Path) -> Any:
    candidate = repo_root / "scripts" / "lesson_session_boundary.py"
    if not candidate.is_file():
        raise ValueError(f"lesson session boundary helper is unavailable: {candidate}")
    spec = importlib.util.spec_from_file_location("charness_reviewer_lesson_boundary", candidate)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load lesson session boundary helper: {candidate}")
    module = importlib.util.module_from_spec(spec)
    previous_path = list(sys.path)
    previous_module = sys.modules.get(module.__name__)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    sys.modules[module.__name__] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = previous_path
        if previous_module is None:
            sys.modules.pop(module.__name__, None)
        else:
            sys.modules[module.__name__] = previous_module
    return module


def lesson_binding(repo_root: Path, args: Any, bundle: Path | None, receipt: Path | None) -> dict[str, Any] | None:
    """Freeze the parent lesson join before a worker is launched."""
    if bundle is None or receipt is None:
        return None
    boundary = _lesson_boundary_module(repo_root)
    context = boundary.load_parent_session(
        repo_root,
        session_id=args.lesson_session_id,
        bundle_path=bundle,
    )
    return {
        "bundle": bundle,
        "receipt": receipt,
        "lane_receipt": receipt,
        "lane_id": args.lesson_lane_id,
        "owner_id": args.lesson_owner_id,
        "session_id": context.session_id,
        "snapshot_sha256": context.snapshot_sha256,
        "bundle_sha256": context.bundle_sha256,
        "parent_receipt_sha256": context.receipt_sha256,
    }


def _lesson_inventory(repo_root: Path) -> dict[str, str]:
    """Hash lesson-owned files, including ignored lane receipts."""
    root = repo_root.resolve()
    paths: set[Path] = set()
    for relative in ("charness-artifacts/retro/lesson-ledger.json", "charness-artifacts/retro/recent-lessons.md"):
        paths.add(root / relative)
    for relative_root in ("charness-artifacts/retro/lesson-session-receipts", ".charness/lesson-lanes"):
        directory = root / relative_root
        if directory.exists():
            paths.update(path for path in directory.rglob("*") if path.is_file() or path.is_symlink())
    inventory: dict[str, str] = {}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            if path.is_symlink():
                marker = f"symlink:{path.readlink()}"
            else:
                marker = f"file:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        except OSError as exc:
            marker = f"unreadable:{type(exc).__name__}:{exc}"
        inventory[relative] = marker
    return inventory


def lesson_inventory_snapshot(repo_root: Path) -> dict[str, str]:
    return _lesson_inventory(repo_root)


def lesson_inventory_delta(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(
        path for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def append_lesson_args(command: list[str], args: Any, bundle: Path | None, receipt: Path | None, repo_root: Path) -> None:
    if bundle is None or receipt is None:
        return
    command.extend(
        [
            "--parent-lesson-bundle", str(bundle),
            "--lesson-session-id", str(args.lesson_session_id),
            "--lesson-lane-id", str(args.lesson_lane_id),
            "--lesson-owner-id", str(args.lesson_owner_id),
            "--lesson-lane-receipt", str(receipt),
            "--lesson-repo-root", str(repo_root),
        ]
    )


def failure_state(receipt: dict[str, Any] | None) -> str:
    status = receipt.get("status") if isinstance(receipt, dict) else None
    if status == "timed-out":
        return TIMED_OUT
    if status == "interrupted":
        return INTERRUPTED
    if status in {"transport-unestablished", "credential-invalid", "authorization-insufficient"}:
        return HOST_CHANNEL_UNREADABLE
    return NON_DELIVERY_UNKNOWN


def _transition(ledger_path: Path, attempt_id: str, state: str, signal: str, recorded_at: str | None) -> None:
    with ledger_lock(ledger_path):
        ledger = _read(ledger_path)
        attempt = ledger.require(attempt_id)
        attempt.transition(state, signal, recorded_at or utc_now())
        _write(ledger_path, ledger)


def finalize_attempt(
    *,
    receipt_path: Path,
    ledger_path: Path,
    attempt_id: str,
    scope: str,
    packet_identity: str,
    reviewed_input_identity: str,
    parent_receipt_identity: str,
    execution_mode: str,
    build_report: Callable[..., dict[str, Any]],
    repo_root: Path | None = None,
    lesson_binding_data: dict[str, Any] | None = None,
    lesson_before: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Validate collection before changing the attempt to findings-received."""
    receipt: dict[str, Any] | None = None
    receipt_error: Exception | None = None
    try:
        loaded = json.loads(receipt_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("worker receipt must be a JSON object")
        receipt = loaded
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        receipt_error = exc
    pre_report: dict[str, Any] | None = None
    lesson_error: Exception | None = None
    if lesson_binding_data is not None:
        try:
            if repo_root is None or lesson_before is None:
                raise ValueError("lesson-bound reviewer finalization lacks a pre-worker lesson snapshot")
            boundary = _lesson_boundary_module(repo_root)
            changed = lesson_inventory_delta(lesson_before, _lesson_inventory(repo_root))
            boundary.validate_lane_writes(
                repo_root,
                changed,
                lane_id=lesson_binding_data["lane_id"],
                owner_role="worker",
            )
            if receipt is not None and receipt.get("status") == "succeeded":
                boundary.validate_lane_receipt(
                    repo_root,
                    lesson_binding_data["lane_receipt"],
                    lane_id=lesson_binding_data["lane_id"],
                    owner_id=lesson_binding_data["owner_id"],
                    session_id=lesson_binding_data["session_id"],
                    snapshot_sha256=lesson_binding_data["snapshot_sha256"],
                    bundle_sha256=lesson_binding_data["bundle_sha256"],
                    parent_receipt_sha256=lesson_binding_data["parent_receipt_sha256"],
                )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            lesson_error = exc
    if receipt is not None and receipt.get("status") == "succeeded":
        if lesson_error is None:
            try:
                pre_report = build_report(
                    receipt_path=str(receipt_path), ledger_path=str(ledger_path), attempt_id=attempt_id,
                    scope=scope, packet_identity=packet_identity,
                    reviewed_input_identity=reviewed_input_identity,
                    parent_receipt_identity=parent_receipt_identity,
                    expected_execution_mode=execution_mode,
                )
            except (OSError, ValueError, KeyError, TypeError) as exc:
                receipt_error = exc
        else:
            receipt_error = lesson_error
        if pre_report is not None and pre_report.get("collection_ready"):
            with ledger_lock(ledger_path):
                ledger = _read(ledger_path)
                attempt = ledger.require(attempt_id)
                attempt.record_findings(
                    scope=scope, packet_identity=packet_identity,
                    parent_receipt_identity=parent_receipt_identity,
                    findings_identity=receipt.get("output_sha256", ""),
                    recorded_at=receipt.get("finished_at", "") or utc_now(),
                )
                _write(ledger_path, ledger)
        else:
            _transition(
                ledger_path, attempt_id, COLLECTION_FAILED,
                "worker collection validation failed before findings-received: "
                + (str(receipt_error) if receipt_error else str((pre_report or {}).get("reason"))),
                (receipt or {}).get("finished_at"),
            )
    else:
        status = receipt.get("status") if receipt is not None else "missing-receipt"
        failure = COLLECTION_FAILED if lesson_error is not None else failure_state(receipt)
        signal = (
            "lesson-bound worker finalization refused the post-worker write fence: "
            + str(lesson_error)
            if lesson_error is not None
            else f"file-backed worker ended with status {status!r}"
            + (f": {receipt_error}" if receipt_error else "")
        )
        _transition(ledger_path, attempt_id, failure, signal, (receipt or {}).get("finished_at"))
    return build_report(
        receipt_path=str(receipt_path), ledger_path=str(ledger_path), attempt_id=attempt_id,
        scope=scope, packet_identity=packet_identity,
        reviewed_input_identity=reviewed_input_identity,
        parent_receipt_identity=parent_receipt_identity,
        expected_execution_mode=execution_mode,
    )
