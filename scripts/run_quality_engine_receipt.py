#!/usr/bin/env python3
"""Runtime aggregate and proof-receipt handoff for the quality engine."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from run_quality_engine_output import Ledger, format_elapsed
from run_quality_engine_runtime import RuntimeContext, record_runtime_single, timestamp


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _guard.run_process

_receipt = import_repo_module(__file__, "scripts.evidence.proof_receipt")
render_not_run_note = _receipt.render_not_run_note


def _index_tree(repo_root: Path) -> str:
    result = run_process(["git", "write-tree"], cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _last_release_receipt_path(repo_root: Path) -> Path:
    return repo_root / ".charness" / "quality" / "last-release-receipt.json"


def _bind_receipt_outputs(
    args: list[str], *, repo_root: Path, status: str, release: bool, full_queue: bool, receipt_json: str
) -> tuple[list[str], Path | None, str]:
    """Return argv, optional copy-destination, and the json path actually written."""
    index_tree = _index_tree(repo_root)
    if index_tree:
        args = [*args, "--index-tree", index_tree]
    last_receipt = _last_release_receipt_path(repo_root)
    write_last = status == "pass" and release and full_queue
    if receipt_json:
        args = [*args, "--json-path", receipt_json]
        return args, last_receipt if write_last else None, receipt_json
    if write_last:
        last_receipt.parent.mkdir(parents=True, exist_ok=True)
        args = [*args, "--json-path", str(last_receipt)]
    return args, None, receipt_json


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
    not_run: tuple[tuple[str, str], ...] = (),
) -> None:
    import time

    elapsed_ms = max(0, round((time.monotonic() - started_at) * 1000))
    status = "fail" if overall_rc else ("unestablished" if ledger.unestablished else "pass")
    if not labels:
        aggregate = f"run-quality-{mode}{'-release' if release else ''}"
        record_runtime_single(context, aggregate, elapsed_ms, status, timestamp())
    args = [
        "python3",
        "scripts/evidence/proof_receipt.py",
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
    for label, reason in not_run:
        args.extend(("--not-run", f"{label}:{reason}"))
    args, copy_to, written = _bind_receipt_outputs(
        args,
        repo_root=context.repo_root,
        status=status,
        release=release,
        full_queue=full_queue,
        receipt_json=receipt_json,
    )
    result = run_process(args, cwd=context.repo_root, env=context.environment, timeout_seconds=None)
    if copy_to is not None and written and result.returncode == 0:
        copy_to.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(written, copy_to)
        except OSError:
            pass
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0 and not result.stdout:
        note = render_not_run_note({"label": label, "reason": reason} for label, reason in not_run)
        print(
            f"Quality summary: {ledger.passed} passed, {ledger.failed} failed{note}, "
            f"total {format_elapsed(elapsed_ms)}"
        )
