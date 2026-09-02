from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TIMEOUT_EXIT_CODE = _subprocess_guard.TIMEOUT_EXIT_CODE

_state = import_repo_module(__file__, "scripts.worktree.worktree_doctor_state")
CheckResult = _state.CheckResult
DEFAULT_DOCTOR_TIMEOUT_SECONDS = _state.DEFAULT_DOCTOR_TIMEOUT_SECONDS
FAIL = _state.FAIL
PASS = _state.PASS
tail = _state.tail


def _run_manifest_doctor_command(entry: dict[str, Any], repo_root: Path) -> CheckResult:
    check_id = entry.get("id")
    argv = list(entry.get("argv") or [])
    timeout = int(entry.get("timeout_seconds") or DEFAULT_DOCTOR_TIMEOUT_SECONDS)
    expect_exit = int(entry.get("expect_exit_code", 0))
    next_hint = entry.get("next_action_hint")
    try:
        result = run_process(argv, cwd=repo_root, timeout_seconds=timeout)
    except FileNotFoundError as exc:
        return CheckResult(
            id=check_id,
            status=FAIL,
            detail=f"command not found: {exc.filename or argv[0]}",
            next_step=next_hint,
            source="manifest",
        )
    if result.returncode == TIMEOUT_EXIT_CODE:
        return CheckResult(
            id=check_id,
            status=FAIL,
            detail=f"command timed out after {timeout}s: {argv}",
            next_step=next_hint,
            source="manifest",
        )
    if result.returncode == expect_exit:
        return CheckResult(
            id=check_id,
            status=PASS,
            detail=f"exit_code={result.returncode}",
            source="manifest",
        )
    last = tail((result.stderr or result.stdout or "").strip())
    return CheckResult(
        id=check_id,
        status=FAIL,
        detail=f"exit_code={result.returncode} (expected {expect_exit}); tail: {last}",
        next_step=next_hint,
        source="manifest",
    )


def run_manifest_doctor_checks(repo_root: Path, manifest: dict[str, Any]) -> list[CheckResult]:
    doctor = manifest.get("doctor") or {}
    checks = doctor.get("checks") or []
    return [_run_manifest_doctor_command(entry, repo_root) for entry in checks]
