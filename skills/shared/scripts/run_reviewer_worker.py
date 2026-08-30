#!/usr/bin/env python3
"""Run the canonical file-backed fresh-eye review worker.

This executable bridges the critique adapter and portable worker. It owns the
attempt lifecycle; path, adapter, and argument parsing helpers live in the
adjacent support module.
"""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

try:
    from reviewer_capability import load_capability_file
    from reviewer_delivery import RUNNING, _read, _write, ledger_lock, utc_now
    from reviewer_delivery_fields import boundary_binding
    from reviewer_output import emit_yaml
    from reviewer_runner_support import finalize_attempt
    from reviewer_worker_report import ReportError, build_report
    from reviewer_worker_runner_support import (
        DEFAULT_SCHEMA,
        WORKER,
    )
    from reviewer_worker_runner_support import (
        atomic_write_yaml as _atomic_write_yaml,
    )
    from reviewer_worker_runner_support import (
        parser as _parser,
    )
    from reviewer_worker_runner_support import (
        repo_path as _repo_path,
    )
    from reviewer_worker_runner_support import (
        select_runner as _select_runner,
    )
    from reviewer_worker_runner_support import (
        sha256 as _sha256,
    )
except ImportError:
    from skills.shared.scripts.reviewer_capability import load_capability_file
    from skills.shared.scripts.reviewer_delivery import RUNNING, _read, _write, ledger_lock, utc_now
    from skills.shared.scripts.reviewer_delivery_fields import boundary_binding
    from skills.shared.scripts.reviewer_output import emit_yaml
    from skills.shared.scripts.reviewer_runner_support import finalize_attempt
    from skills.shared.scripts.reviewer_worker_report import ReportError, build_report
    from skills.shared.scripts.reviewer_worker_runner_support import (
        DEFAULT_SCHEMA,
        WORKER,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        atomic_write_yaml as _atomic_write_yaml,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        parser as _parser,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        repo_path as _repo_path,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        select_runner as _select_runner,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        sha256 as _sha256,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    report_target: Path | None = None
    try:
        mode, backend, timeout = _select_runner(args, repo_root)
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

        boundary_mode, boundary_fingerprint = boundary_binding(
            args.boundary_mode, args.boundary_fingerprint
        )
        prompt = _repo_path(repo_root, args.prompt_file)
        capability_file = _repo_path(repo_root, args.capability_file)
        schema = _repo_path(repo_root, args.schema_file)
        ledger_path = _repo_path(repo_root, args.ledger_file)
        output_path = _repo_path(repo_root, args.output_file)
        receipt_path = _repo_path(repo_root, args.receipt_file)
        report_target = _repo_path(repo_root, args.report_file)
        stdout_path = _repo_path(repo_root, args.stdout_file or Path(f"{output_path}.stdout"))
        stderr_path = _repo_path(repo_root, args.stderr_file or Path(f"{output_path}.stderr"))
        producer_run_id = args.run_id or uuid.uuid4().hex
        if _sha256(schema) != _sha256(DEFAULT_SCHEMA):
            raise ValueError("file-backed reviewer runner requires the canonical bounded-review result schema")
        launch_capability = load_capability_file(capability_file, attempt_id=args.attempt_id, require_ready=True)
        all_paths = (
            prompt, capability_file, schema, ledger_path, output_path, receipt_path,
            report_target, stdout_path, stderr_path,
        )
        for path in all_paths:
            try:
                path.relative_to(repo_root)
            except ValueError as exc:
                raise ValueError(f"runner path resolves outside --repo-root: {path}") from exc
        if len({str(path) for path in all_paths}) != len(all_paths):
            raise ValueError("runner input and output paths must resolve to distinct files")
        stale_targets = [
            path for path in (output_path, receipt_path, report_target, stdout_path, stderr_path)
            if path is not None and path.exists()
        ]
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
                boundary_fingerprint=boundary_fingerprint,
                boundary_mode=boundary_mode,
                execution_mode=mode,
                backend=backend,
                prompt_sha256=prompt_sha,
                schema_sha256=schema_sha,
                capability_launch_envelope_sha256=launch_capability.envelope_sha256,
                output_file=str(output_path),
                receipt_file=str(receipt_path),
                producer_run_id=producer_run_id,
            )
            ledger.require(args.attempt_id).transition(
                RUNNING,
                "reviewer worker process launched",
                utc_now(),
            )
            _write(ledger_path, ledger)

        worker_command = [
            sys.executable, str(WORKER), "--backend", backend, "--workspace", str(repo_root),
            "--prompt-file", str(prompt), "--schema-file", str(schema),
            "--capability-file", str(capability_file), "--output-file", str(output_path),
            "--receipt-file", str(receipt_path), "--execution-mode", mode,
            "--attempt-id", args.attempt_id, "--scope", args.scope,
            "--packet-identity", args.packet_identity,
            "--reviewed-input-identity", args.reviewed_input_identity,
            "--parent-receipt-identity", args.parent_receipt_identity,
        ]
        worker_command.extend(["--boundary-mode", boundary_mode])
        if boundary_fingerprint is not None:
            worker_command.extend(["--boundary-fingerprint", boundary_fingerprint])
        worker_command.extend(["--stdout-file", str(stdout_path), "--stderr-file", str(stderr_path)])
        worker_command.extend(["--timeout-seconds", str(timeout), "--run-id", producer_run_id])
        worker = subprocess.run(worker_command, cwd=repo_root, check=False, capture_output=True, text=True)
        if worker.stderr:
            sys.stderr.write(worker.stderr)

        report = finalize_attempt(
            receipt_path=receipt_path,
            ledger_path=ledger_path,
            attempt_id=args.attempt_id,
            scope=args.scope,
            packet_identity=args.packet_identity,
            reviewed_input_identity=args.reviewed_input_identity,
            parent_receipt_identity=args.parent_receipt_identity,
            execution_mode=mode,
            build_report=build_report,
        )
        _atomic_write_yaml(report_target, report)
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
