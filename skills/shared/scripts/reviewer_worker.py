#!/usr/bin/env python3
"""Run a bounded review backend and publish a typed terminal receipt.

The process and result boundary lives in ``reviewer_worker_runtime``. This
entrypoint deliberately stays small: it parses the portable contract,
serializes every failure, and emits the receipt without interpreting it as a
review approval.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    from reviewer_output import emit_yaml
    from reviewer_worker_capability import failure_receipt_fields
    from reviewer_worker_runtime import (
        SCHEMA_VERSION,
        SUCCESS,
        WorkerError,
        atomic_write_json,
        now,
        preflight,
        resolve,
        run,
    )
except ImportError:
    from skills.shared.scripts.reviewer_output import emit_yaml
    from skills.shared.scripts.reviewer_worker_capability import failure_receipt_fields
    from skills.shared.scripts.reviewer_worker_runtime import (
        SCHEMA_VERSION,
        SUCCESS,
        WorkerError,
        atomic_write_json,
        now,
        preflight,
        resolve,
        run,
    )

DEFAULT_TIMEOUT_SECONDS = 900.0


def _lesson_boundary_module() -> Any:
    """Load the repo/plugin-owned boundary even when this file runs standalone."""
    here = Path(__file__).resolve()
    for ancestor in (here.parent, *here.parents):
        candidate = ancestor / "scripts" / "lesson_session_boundary.py"
        if candidate.is_file() and candidate != here:
            spec = importlib.util.spec_from_file_location("charness_lesson_session_boundary", candidate)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                previous_path = list(sys.path)
                previous_module = sys.modules.get(module.__name__)
                root = candidate.parent.parent
                if str(root) not in sys.path:
                    sys.path.insert(0, str(root))
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
    raise ValueError("lesson session boundary helper is unavailable")


def _failure_receipt(
    args: argparse.Namespace,
    run_id: str,
    started_at: str,
    *,
    status: str,
    exit_code: int | None,
    error: str,
    capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "backend": args.backend,
        "started_at": started_at,
        "finished_at": now(),
        "status": status,
        "terminal": True,
        "exit_code": exit_code,
        "output_fresh": False,
        "attempt_id": args.attempt_id,
        "scope": args.scope,
        "packet_identity": args.packet_identity,
        "reviewed_input_identity": args.reviewed_input_identity,
        "parent_receipt_identity": args.parent_receipt_identity,
        "boundary_fingerprint": args.boundary_fingerprint,
        "execution_mode": args.execution_mode,
        "timeout_seconds": args.timeout_seconds,
        "error": error,
    }
    if capability is not None:
        receipt.update(failure_receipt_fields(capability, status))
    return receipt


def _safe_receipt_path(args: argparse.Namespace) -> Path | None:
    """Return a writable receipt target without overwriting an input or stale file."""
    try:
        receipt = resolve(args.receipt_file, "receipt_file")
        if receipt.exists():
            return None
        inputs = {
            resolve(args.prompt_file, "prompt_file"),
            resolve(args.schema_file, "schema_file"),
            resolve(args.capability_file, "capability_file"),
        }
        if receipt in inputs:
            return None
        return receipt
    except WorkerError:
        return None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded typed review worker.")
    parser.add_argument("--backend", choices=("codex_exec", "claude_p"), required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--schema-file", required=True)
    parser.add_argument("--capability-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--receipt-file", required=True)
    parser.add_argument("--stdout-file")
    parser.add_argument("--stderr-file")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--packet-identity", required=True)
    parser.add_argument("--reviewed-input-identity", required=True)
    parser.add_argument("--parent-receipt-identity", required=True)
    parser.add_argument("--boundary-fingerprint", required=True)
    parser.add_argument(
        "--execution-mode",
        choices=("file-backed-worker", "typed-subagent"),
        default="file-backed-worker",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--parent-lesson-bundle")
    parser.add_argument("--lesson-session-id")
    parser.add_argument("--lesson-lane-id")
    parser.add_argument("--lesson-owner-id")
    parser.add_argument("--lesson-lane-receipt")
    parser.add_argument("--lesson-repo-root")
    return parser


def _inherit_lesson_context(args: argparse.Namespace) -> dict[str, Any]:
    values = (
        args.parent_lesson_bundle,
        args.lesson_lane_id,
        args.lesson_owner_id,
    )
    if not any(value is not None for value in values):
        return {}
    if not all(value for value in values):
        raise ValueError(
            "worker lesson inheritance requires parent bundle, lane id, and owner id"
        )
    boundary = _lesson_boundary_module()
    repo_root = Path(args.lesson_repo_root or args.workspace).resolve()
    context, receipt = boundary.inherit_worker_session(
        repo_root,
        bundle_path=args.parent_lesson_bundle,
        lane_id=args.lesson_lane_id,
        owner_id=args.lesson_owner_id,
        session_id=args.lesson_session_id,
        lane_receipt_path_value=args.lesson_lane_receipt,
    )
    return {
        "lesson_session_id": context.session_id,
        "lesson_bundle_sha256": context.bundle_sha256,
        "lesson_lane_id": args.lesson_lane_id,
        "lesson_lane_receipt": str(receipt),
        "lesson_writes_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    run_id = args.run_id or uuid.uuid4().hex
    started_at = now()
    receipt_path: Path | None = _safe_receipt_path(args)
    lesson_fields: dict[str, Any] = {}
    try:
        lesson_fields = _inherit_lesson_context(args)
        receipt = run(args, preflight(args), run_id, started_at)
    except WorkerError as exc:
        receipt = _failure_receipt(
            args,
            run_id,
            started_at,
            status=exc.status,
            exit_code=exc.exit_code,
            error=str(exc),
            capability=exc.capability,
        )
    except ValueError as exc:
        receipt = _failure_receipt(
            args,
            run_id,
            started_at,
            status="input-invalid",
            exit_code=None,
            error=str(exc),
        )
    except KeyboardInterrupt:
        receipt = _failure_receipt(
            args,
            run_id,
            started_at,
            status="interrupted",
            exit_code=130,
            error="worker interrupted before a successful result was published",
        )
    except Exception as exc:  # pragma: no cover - last-resort typed failure boundary
        receipt = _failure_receipt(
            args,
            run_id,
            started_at,
            status="input-invalid",
            exit_code=None,
            error=f"unexpected worker error: {exc}",
        )
    receipt.update(lesson_fields)
    if receipt_path is not None:
        try:
            atomic_write_json(receipt_path, receipt)
        except OSError:
            # The YAML stream is still the typed observable. Never replace an
            # existing artifact merely to make the file-backed channel look
            # complete; the consumer will fail closed on the missing receipt.
            pass
    emit_yaml(receipt)
    return 0 if receipt.get("status") == SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
