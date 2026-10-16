#!/usr/bin/env python3
"""Run the canonical file-backed fresh-eye review worker.

This executable bridges the critique adapter and portable worker. It owns the
attempt lifecycle; path, adapter, and argument parsing helpers live in the
adjacent support module.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

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
        require_distinct_runner_paths as _require_distinct_runner_paths,
    )
    from reviewer_worker_runner_support import (
        require_prompt_binding as _require_prompt_binding,
    )
    from reviewer_worker_runner_support import (
        resolve_runner_path as _resolve_runner_path,
    )
    from reviewer_worker_runner_support import (
        reviewer_worker_arguments as _reviewer_worker_arguments,
    )
    from reviewer_worker_runner_support import (
        select_runner as _select_runner,
    )
    from reviewer_worker_runner_support import (
        sha256 as _sha256,
    )
    from reviewer_worker_runner_support import (
        validate_owned_run_reference as _validate_owned_run_reference,
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
        require_distinct_runner_paths as _require_distinct_runner_paths,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        require_prompt_binding as _require_prompt_binding,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        resolve_runner_path as _resolve_runner_path,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        reviewer_worker_arguments as _reviewer_worker_arguments,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        select_runner as _select_runner,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        sha256 as _sha256,
    )
    from skills.shared.scripts.reviewer_worker_runner_support import (
        validate_owned_run_reference as _validate_owned_run_reference,
    )


def _runtime():
    bootstrap = next(
        (
            ancestor / "scripts" / "runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    runtime_environment = dict(os.environ)
    report_target: Path | None = None
    try:
        mode, backend, timeout, reviewer = _select_runner(args, repo_root)
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
        owner, owner_plan = _validate_owned_run_reference(
            repo_root,
            owner_run_id=args.owner_run_id,
            owner_receipt_file=args.owner_receipt_file,
            attempt_id=args.attempt_id,
            scope=args.scope,
            packet_identity=args.packet_identity,
            reviewed_input_identity=args.reviewed_input_identity,
            parent_receipt_identity=args.parent_receipt_identity,
            backend=backend,
            boundary_mode=boundary_mode,
            boundary_fingerprint=args.boundary_fingerprint,
            runtime_environment=runtime_environment,
        )
        prompt = _resolve_runner_path(repo_root, args.prompt_file, label="prompt file", owner=owner)
        capability_file = _resolve_runner_path(
            repo_root, args.capability_file, label="capability file", owner=owner
        )
        schema = _resolve_runner_path(repo_root, args.schema_file, label="schema file", owner=owner)
        ledger_path = _resolve_runner_path(
            repo_root, args.ledger_file, label="delivery ledger", owner=owner
        )
        output_path = _resolve_runner_path(repo_root, args.output_file, label="output file", owner=owner)
        receipt_path = _resolve_runner_path(
            repo_root, args.receipt_file, label="receipt file", owner=owner
        )
        report_target = _resolve_runner_path(
            repo_root, args.report_file, label="report file", owner=owner
        )
        stdout_path = _resolve_runner_path(
            repo_root,
            args.stdout_file or Path(f"{output_path}.stdout"),
            label="stdout file",
            owner=owner,
        )
        stderr_path = _resolve_runner_path(
            repo_root,
            args.stderr_file or Path(f"{output_path}.stderr"),
            label="stderr file",
            owner=owner,
        )
        producer_run_id = args.run_id or uuid.uuid4().hex
        if _sha256(schema) != _sha256(DEFAULT_SCHEMA):
            raise ValueError(
                "file-backed reviewer runner requires the canonical bounded-review result schema"
            )
        launch_capability = load_capability_file(
            capability_file, attempt_id=args.attempt_id, require_ready=True
        )
        if owner_plan is not None and (
            owner_plan.get("schema_sha256") != _sha256(schema)
            or owner_plan.get("capability_envelope_sha256") != launch_capability.envelope_sha256
        ):
            raise ValueError("owned scratch schema or capability identity does not match the run plan")
        all_paths = (
            prompt,
            capability_file,
            schema,
            ledger_path,
            output_path,
            receipt_path,
            report_target,
            stdout_path,
            stderr_path,
        )
        for path in all_paths:
            try:
                path.relative_to(repo_root)
            except ValueError as exc:
                if owner is None:
                    raise ValueError(f"runner path resolves outside --repo-root: {path}") from exc
                try:
                    path.relative_to(owner.path)
                except ValueError as owner_exc:
                    raise ValueError(f"runner path resolves outside the exact owned scratch root: {path}") from owner_exc
        _require_distinct_runner_paths(all_paths)
        stale_targets = [
            path
            for path in (output_path, receipt_path, report_target, stdout_path, stderr_path)
            if path is not None and path.exists()
        ]
        if stale_targets:
            raise ValueError(
                "refusing stale runner artifacts: " + ", ".join(str(path) for path in stale_targets)
            )
        prompt_sha = _sha256(prompt)
        schema_sha = _sha256(schema)
        _require_prompt_binding(owner_plan, prompt_sha)
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

        worker_argv = [
            "--backend",
            backend,
            "--workspace",
            str(repo_root),
            "--prompt-file",
            str(prompt),
            "--schema-file",
            str(schema),
            "--capability-file",
            str(capability_file),
            "--output-file",
            str(output_path),
            "--receipt-file",
            str(receipt_path),
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
        worker_argv.extend(
            _reviewer_worker_arguments(
                tier=reviewer["tier"],
                model=reviewer["model"],
                reasoning_effort=reviewer["reasoning_effort"],
                unsupported_fields=reviewer["unsupported_fields"],
            )
        )
        worker_argv.extend(["--boundary-mode", boundary_mode])
        if boundary_fingerprint is not None:
            worker_argv.extend(["--boundary-fingerprint", boundary_fingerprint])
        worker_argv.extend(["--stdout-file", str(stdout_path), "--stderr-file", str(stderr_path)])
        worker_argv.extend(["--timeout-seconds", str(timeout), "--run-id", producer_run_id])
        worker_module = _runtime().load_path_module("charness_reviewer_worker_in_process", WORKER)
        worker_stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(worker_stderr):
            worker_returncode = worker_module.main(worker_argv)
        if worker_stderr.getvalue():
            sys.stderr.write(worker_stderr.getvalue())

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
            expected_targets=args.expected_target,
        )
        _atomic_write_yaml(report_target, report)
        emit_yaml(report)
        return 0 if worker_returncode == 0 and report["approval_eligible"] else 1
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
