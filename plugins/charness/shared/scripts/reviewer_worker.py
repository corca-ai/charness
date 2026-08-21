#!/usr/bin/env python3
"""Run a bounded review backend and publish a typed terminal receipt.

The process and result boundary lives in ``reviewer_worker_runtime``. This
entrypoint deliberately stays small: it parses the portable contract,
serializes every failure, and emits the receipt without interpreting it as a
review approval.
"""

from __future__ import annotations

import argparse
import uuid
from pathlib import Path
from typing import Any

try:
    from reviewer_output import emit_yaml
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


def _failure_receipt(
    args: argparse.Namespace,
    run_id: str,
    started_at: str,
    *,
    status: str,
    exit_code: int | None,
    error: str,
) -> dict[str, Any]:
    return {
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
        "execution_mode": args.execution_mode,
        "error": error,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded typed review worker.")
    parser.add_argument("--backend", choices=("codex_exec", "claude_p"), required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--schema-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--receipt-file", required=True)
    parser.add_argument("--stdout-file")
    parser.add_argument("--stderr-file")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--attempt-id")
    parser.add_argument("--scope")
    parser.add_argument("--packet-identity")
    parser.add_argument("--reviewed-input-identity")
    parser.add_argument(
        "--execution-mode",
        choices=("file-backed-worker", "typed-subagent"),
        default="file-backed-worker",
    )
    parser.add_argument("--run-id", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    run_id = args.run_id or uuid.uuid4().hex
    started_at = now()
    receipt_path: Path | None = None
    try:
        receipt_path = resolve(args.receipt_file, "receipt_file")
        receipt = run(args, preflight(args), run_id, started_at)
    except WorkerError as exc:
        receipt = _failure_receipt(
            args, run_id, started_at, status=exc.status, exit_code=exc.exit_code, error=str(exc)
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
    if receipt_path is not None and not receipt_path.exists():
        atomic_write_json(receipt_path, receipt)
    emit_yaml(receipt)
    return 0 if receipt.get("status") == SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
