"""Authoring boundary for durable debug artifacts.

The seam-risk index deliberately audits a corpus.  It is too late to be the
first shape checker for a record just authored, so this helper writes through
the exact scaffold-selected path, runs that path through the strict validator,
and rolls the write back when the validator refuses it.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any


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
    previous = target.read_bytes() if target.exists() and target.is_file() else None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown_text.rstrip() + "\n", encoding="utf-8")
    command = shlex.split(validator_command)
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    validation = {
        "command": validator_command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "path": relative,
    }
    if completed.returncode != 0:
        if previous is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(previous)
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

