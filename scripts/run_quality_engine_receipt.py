#!/usr/bin/env python3
"""Runtime aggregate and proof-receipt handoff for the quality engine."""

from __future__ import annotations

import sys

from run_quality_engine_output import Ledger, format_elapsed
from run_quality_engine_runtime import RuntimeContext, record_runtime_single, timestamp

from runtime_bootstrap import import_repo_module

_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _guard.run_process


def finish(
    context: RuntimeContext,
    ledger: Ledger,
    *,
    started_at: float,
    mode: str,
    release: bool,
    full_queue: bool,
    non_claim: str,
    receipt_json: str,
    labels: str,
    overall_rc: int,
) -> None:
    import time

    elapsed_ms = max(0, round((time.monotonic() - started_at) * 1000))
    status = "fail" if overall_rc else ("unestablished" if ledger.unestablished else "pass")
    if not labels:
        aggregate = f"run-quality-{mode}{'-release' if release else ''}"
        record_runtime_single(context, aggregate, elapsed_ms, status, timestamp())
    args = [
        "python3",
        "scripts/proof_receipt.py",
        "quality",
        "--status",
        status,
        "--effective-exit-code",
        str(overall_rc),
        "--passed",
        str(ledger.passed),
        "--failed",
        str(ledger.failed),
        "--elapsed",
        format_elapsed(elapsed_ms),
        "--execution-mode",
        mode,
    ]
    if release:
        args.append("--release")
    if full_queue:
        args.append("--full-queue")
    if non_claim:
        args.extend(("--non-claim", non_claim))
    for label in ledger.measured_scope:
        args.extend(("--measured-scope", label))
    for subject, recovery in zip(ledger.adverse_subjects, ledger.recoveries):
        args.extend(("--adverse-subject", subject, "--recovery", recovery))
    for subject in ledger.unestablished:
        args.extend(("--unproven-subject", subject))
    if receipt_json:
        args.extend(("--json-path", receipt_json))
    result = run_process(args, cwd=context.repo_root, env=context.environment, timeout_seconds=None)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0 and not result.stdout:
        print(
            f"Quality summary: {ledger.passed} passed, {ledger.failed} failed, total {format_elapsed(elapsed_ms)}"
        )
