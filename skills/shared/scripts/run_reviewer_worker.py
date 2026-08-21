#!/usr/bin/env python3
"""Canonical parent-side runner for the file-backed fresh-eye path.

This is the executable bridge between the critique adapter and the portable
worker. It binds the adapter-selected mode/backend, starts one delivery
attempt, passes all provenance identities to the worker, records the result
hash as the findings identity, and emits the combined worker report. The
typed-subagent mode is an explicit host branch; it is never silently executed
by this file-backed runner and never downgraded to a same-context pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from reviewer_delivery import _read, _write, ledger_lock
    from reviewer_output import emit_yaml
    from reviewer_worker_report import ReportError, build_report
except ImportError:
    from skills.shared.scripts.reviewer_delivery import _read, _write, ledger_lock
    from skills.shared.scripts.reviewer_output import emit_yaml
    from skills.shared.scripts.reviewer_worker_report import ReportError, build_report


def _package_root() -> Path:
    """Find the source or installed plugin root from this script's location."""
    for candidate in Path(__file__).resolve().parents:
        has_schema = (
            (candidate / "shared/references/bounded-review-result.schema.json").is_file()
            or (candidate / "skills/shared/references/bounded-review-result.schema.json").is_file()
        )
        if has_schema and (
            (candidate / "skills/public/critique/scripts/resolve_adapter.py").is_file()
            or (candidate / "skills/critique/scripts/resolve_adapter.py").is_file()
        ):
            return candidate
    raise RuntimeError("cannot locate Charness package root for reviewer runner")


ROOT = _package_root()
WORKER = Path(__file__).resolve().with_name("reviewer_worker.py")
DEFAULT_SCHEMA = next(
    path
    for path in (
        ROOT / "shared/references/bounded-review-result.schema.json",
        ROOT / "skills/shared/references/bounded-review-result.schema.json",
    )
    if path.is_file()
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
    import os
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".pending", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(yaml.safe_dump(payload, sort_keys=False))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _adapter(repo_root: Path) -> dict[str, Any]:
    adapter_scripts = (
        ROOT / "skills/public/critique/scripts/resolve_adapter.py",
        ROOT / "skills/critique/scripts/resolve_adapter.py",
    )
    resolver = next((path for path in adapter_scripts if path.is_file()), None)
    if resolver is None:
        raise ValueError("cannot locate critique adapter resolver in the installed package")
    result = subprocess.run(
        [sys.executable, str(resolver), "--repo-root", str(repo_root)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "critique adapter resolution failed")
    payload = yaml.safe_load(result.stdout) or {}
    if not isinstance(payload, dict) or payload.get("valid") is not True:
        raise ValueError("critique adapter is invalid")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one canonical file-backed review attempt.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--packet-identity", required=True)
    parser.add_argument("--reviewed-input-identity", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--parent-receipt-identity", required=True)
    parser.add_argument("--boundary-fingerprint", required=True)
    parser.add_argument("--ledger-file", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, required=True)
    parser.add_argument("--receipt-file", type=Path, required=True)
    parser.add_argument("--report-file", type=Path, required=True)
    parser.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--stdout-file", type=Path)
    parser.add_argument("--stderr-file", type=Path)
    parser.add_argument("--backend", choices=("codex_exec", "claude_p"))
    parser.add_argument("--execution-mode", choices=("file-backed-worker", "typed-subagent"))
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--run-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    report_target: Path | None = None
    try:
        adapter = _adapter(repo_root)
        adapter_data = adapter.get("data") or {}
        runner = adapter_data.get("reviewer_runner") or {}
        configured_mode = runner.get("mode", "file-backed-worker")
        if args.execution_mode is not None and args.execution_mode != configured_mode:
            raise ValueError(
                f"adapter reviewer_runner.mode={configured_mode!r} is authoritative; "
                f"caller requested {args.execution_mode!r}"
            )
        mode = configured_mode
        configured_backend = runner.get("backend")
        if configured_backend == "host-defaulted":
            backend = args.backend
        else:
            if args.backend is not None and args.backend != configured_backend:
                raise ValueError(
                    f"adapter reviewer_runner.backend={configured_backend!r} is authoritative; "
                    f"caller requested {args.backend!r}"
                )
            backend = configured_backend
        configured_timeout = runner.get("timeout_seconds")
        if configured_timeout is not None and args.timeout_seconds is not None and args.timeout_seconds != configured_timeout:
            raise ValueError(
                f"adapter reviewer_runner.timeout_seconds={configured_timeout!r} is authoritative; "
                f"caller requested {args.timeout_seconds!r}"
            )
        timeout = configured_timeout if configured_timeout is not None else (
            args.timeout_seconds if args.timeout_seconds is not None else 900
        )
        if mode == "typed-subagent":
            emit_yaml(
                {
                    "schema_version": "charness.reviewer_runner.v1",
                    "execution_mode": "typed-subagent",
                    "approval_eligible": False,
                    "status": "typed-subagent-selected",
                    "reason": (
                        "adapter selected typed-subagent; use the host spawn branch and deliver findings "
                        "to the parent context, never this file-backed runner"
                    ),
                }
            )
            return 2
        if backend not in {"codex_exec", "claude_p"}:
            raise ValueError("file-backed runner requires adapter reviewer_runner.backend")

        prompt = args.prompt_file.resolve()
        schema = args.schema_file.resolve()
        ledger_path = args.ledger_file.resolve()
        output_path = args.output_file.resolve()
        receipt_path = args.receipt_file.resolve()
        report_target = args.report_file.resolve()
        stdout_path = (args.stdout_file or Path(f"{output_path}.stdout")).resolve()
        stderr_path = (args.stderr_file or Path(f"{output_path}.stderr")).resolve()
        all_paths = (prompt, schema, ledger_path, output_path, receipt_path, report_target, stdout_path, stderr_path)
        if len({str(path) for path in all_paths}) != len(all_paths):
            raise ValueError("runner input and output paths must resolve to distinct files")
        stale_targets = [path for path in (output_path, receipt_path, report_target, stdout_path, stderr_path) if path.exists()]
        if stale_targets:
            raise ValueError("refusing stale runner artifacts: " + ", ".join(str(path) for path in stale_targets))
        prompt_sha = _sha256(prompt)
        schema_sha = _sha256(schema)
        with ledger_lock(ledger_path):
            ledger = _read(ledger_path)
            ledger.start(
                attempt_id=args.attempt_id,
                scope=args.scope,
                packet_identity=args.packet_identity,
                reviewed_input_identity=args.reviewed_input_identity,
                parent_receipt_identity=args.parent_receipt_identity,
                boundary_fingerprint=args.boundary_fingerprint,
                execution_mode=mode,
                backend=backend,
                prompt_sha256=prompt_sha,
                schema_sha256=schema_sha,
            )
            _write(ledger_path, ledger)

        worker_command = [
            sys.executable,
            str(WORKER),
            "--backend",
            backend,
            "--workspace",
            str(repo_root),
            "--prompt-file",
            str(prompt),
            "--schema-file",
            str(schema),
            "--output-file",
            str(args.output_file.resolve()),
            "--receipt-file",
            str(args.receipt_file.resolve()),
            "--execution-mode",
            mode,
            "--attempt-id",
            args.attempt_id,
            "--scope",
            args.scope,
            "--packet-identity",
            args.packet_identity,
            "--reviewed-input-identity",
            args.reviewed_input_identity,
            "--parent-receipt-identity",
            args.parent_receipt_identity,
        ]
        worker_command.extend(["--stdout-file", str(stdout_path), "--stderr-file", str(stderr_path)])
        worker_command.extend(["--timeout-seconds", str(timeout)])
        if args.run_id:
            worker_command.extend(["--run-id", args.run_id])
        worker = subprocess.run(worker_command, cwd=repo_root, check=False)

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        with ledger_lock(ledger_path):
            ledger = _read(ledger_path)
            attempt = ledger.require(args.attempt_id)
            if receipt.get("status") == "succeeded":
                attempt.record_findings(
                    scope=args.scope,
                    packet_identity=args.packet_identity,
                    parent_receipt_identity=args.parent_receipt_identity,
                    findings_identity=receipt.get("output_sha256", ""),
                    recorded_at=receipt.get("finished_at", ""),
                )
            else:
                attempt.transition(
                    "timed-out" if receipt.get("status") == "timed-out" else "non-delivery-unknown",
                    f"file-backed worker ended with status {receipt.get('status')!r}",
                    receipt.get("finished_at", ""),
                )
            _write(ledger_path, ledger)

        report = build_report(
            receipt_path=str(args.receipt_file.resolve()),
            ledger_path=str(ledger_path),
            attempt_id=args.attempt_id,
            scope=args.scope,
            packet_identity=args.packet_identity,
            reviewed_input_identity=args.reviewed_input_identity,
            parent_receipt_identity=args.parent_receipt_identity,
            expected_execution_mode=mode,
        )
        _atomic_write_yaml(args.report_file.resolve(), report)
        emit_yaml(report)
        return 0 if worker.returncode == 0 and report["approval_eligible"] else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError, ReportError) as exc:
        if report_target is not None and not report_target.exists():
            try:
                _atomic_write_yaml(
                    report_target,
                    {
                        "schema_version": "charness.reviewer_worker_report.v1",
                        "execution_mode": "file-backed-worker",
                        "approval_eligible": False,
                        "receipt_ok": False,
                        "ledger_ok": False,
                        "provenance_ok": False,
                        "reason": f"runner did not produce an approval-eligible carrier: {exc}",
                    },
                )
            except OSError:
                pass
        emit_yaml(
            {
                "schema_version": "charness.reviewer_runner.v1",
                "execution_mode": "file-backed-worker",
                "approval_eligible": False,
                "status": "runner-invalid",
                "error": str(exc),
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
