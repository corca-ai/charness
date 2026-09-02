"""Authoring boundary for durable debug artifacts.

The seam-risk index deliberately audits a corpus.  It is too late to be the
first shape checker for a record just authored, so this helper writes through
the exact scaffold-selected path, runs that path through the strict validator,
and rolls the write back when the validator refuses it.
"""

from __future__ import annotations

import shlex
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
run_monitored_phase = _subprocess_guard.run_monitored_phase

VALIDATOR_TIMEOUT_SECONDS = 60.0


def _rollback(target: Path, previous: bytes | None) -> None:
    if previous is None:
        target.unlink(missing_ok=True)
    else:
        target.write_bytes(previous)


def persist_debug_artifact(
    *,
    repo_root: Path,
    artifact_path: Path,
    markdown_text: str,
    validator_command: str,
) -> dict[str, Any]:
    """Persist ``markdown_text`` only when the exact path-scoped validator passes.

    The target is backed up before the probe, so a malformed replacement cannot
    destroy an existing current pointer.  The returned refusal is structured so
    callers can preserve an explicit incomplete state instead of treating a
    nonzero validator as an unexplained process failure.
    """
    root = repo_root.resolve()
    target = artifact_path if artifact_path.is_absolute() else root / artifact_path
    try:
        relative = target.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("debug artifact path must stay inside --repo-root") from exc
    if target.is_symlink():
        raise ValueError("debug artifact path must be a lexical record path, not a symlink pointer")
    if target.exists() and target.is_file() and target.stat().st_nlink > 1:
        raise ValueError("debug artifact path must not be a hardlink with another name")
    previous = target.read_bytes() if target.exists() and target.is_file() else None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown_text.rstrip() + "\n", encoding="utf-8")
    command = shlex.split(validator_command)
    try:
        completed = run_monitored_phase(
            command,
            cwd=root,
            phase="debug-artifact-validator",
            timeout_seconds=VALIDATOR_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        _rollback(target, previous)
        return {
            "action": "refused",
            "artifact_path": relative,
            "status": "incomplete",
            "validated": False,
            "validation": {
                "command": validator_command,
                "returncode": None,
                "stdout": getattr(exc, "stdout", "") or "",
                "stderr": getattr(exc, "stderr", "") or "",
                "path": relative,
                "error_type": type(exc).__name__,
            },
            "reason": "debug artifact validator did not complete; write was rolled back",
        }
    if completed.timed_out:
        _rollback(target, previous)
        return {
            "action": "refused",
            "artifact_path": relative,
            "status": "incomplete",
            "validated": False,
            "validation": {
                "command": validator_command,
                "returncode": None,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "path": relative,
                "error_type": "TimeoutExpired",
            },
            "reason": "debug artifact validator did not complete; write was rolled back",
        }
    validation = {
        "command": validator_command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "path": relative,
    }
    if completed.returncode != 0:
        _rollback(target, previous)
        return {
            "action": "refused",
            "artifact_path": relative,
            "status": "incomplete",
            "validated": False,
            "validation": validation,
            "reason": "debug artifact failed exact path-scoped validation; write was rolled back",
        }
    return {
        "action": "persisted",
        "artifact_path": relative,
        "status": "complete",
        "validated": True,
        "validation": validation,
    }
