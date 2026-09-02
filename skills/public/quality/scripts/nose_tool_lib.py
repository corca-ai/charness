"""Shared process transport for Nose-backed quality inventories.

This module owns only facts supplied by the ``nose`` executable: binary
resolution, version probing/normalization, and a JSON-producing subprocess
result.  Callers retain their query grammar and schema interpretation.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess

VERSION_TIMEOUT_SECONDS = 30
NOSE_TIMEOUT_SECONDS = 180
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def _completed_result(completed, **extra: Any) -> dict[str, Any]:
    """Normalize fields shared by every completed Nose subprocess."""
    result = {
        "status": "ok" if completed.returncode == 0 else "error",
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr.strip(),
    }
    result.update(extra)
    return result


def _unreadable_result(completed, error_kind: str, **extra: Any) -> dict[str, Any]:
    """A completed run whose stdout carries no readable report. ``status`` is forced to
    ``error`` regardless of the exit code — an exit-0 run that printed nothing readable is
    still a run whose report the caller must not treat as a result — so no consumer can
    pair ``status == "ok"`` with ``payload: None``."""
    result = _completed_result(completed, payload=None, error_kind=error_kind, **extra)
    result["status"] = "error"
    return result


def resolve_nose_bin() -> str | None:
    """Honor ``NOSE_BIN`` before falling back to the executable on ``PATH``."""
    return os.environ.get("NOSE_BIN") or shutil.which("nose")


def parse_nose_version(text: str) -> tuple[int, int, int] | None:
    """Extract the first three-part numeric version from Nose output."""
    match = _VERSION_RE.search(text)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def probe_nose_version(nose_bin: str) -> dict[str, Any]:
    """Best-effort ``nose --version`` result, including a normalized version."""
    try:
        completed = run_process(
            [nose_bin, "--version"], cwd=Path.cwd(), timeout_seconds=VERSION_TIMEOUT_SECONDS
        )
    except OSError:
        return {"status": "error", "exit_code": 1, "stdout": "", "stderr": "", "version": None}
    if completed.returncode == 124 and completed.stderr.startswith("timed out after "):
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": completed.stdout,
            "stderr": "",
            "version": None,
        }
    return _completed_result(completed, version=parse_nose_version(completed.stdout or ""))


def version_text(version: tuple[int, int, int] | None) -> str:
    """Return the canonical dotted form, or an empty stamp when unknown."""
    return ".".join(str(part) for part in version) if version is not None else ""


def run_json_query(
    repo_root: Path, command: list[str], *, timeout: int = NOSE_TIMEOUT_SECONDS
) -> dict[str, Any]:
    """Run a JSON-emitting Nose command with a stable raw transport contract.

    ``payload`` is present whenever stdout parses, even for a nonzero exit. This
    lets schema owners preserve diagnostic details without re-running a command.
    ``payload`` is ``None`` only on an ``error_kind`` result (``timeout``,
    ``oserror``, ``invalid-json``, ``empty-output``), and every one of those
    carries ``status: "error"`` — so a caller may read ``payload`` as a report
    whenever ``status`` is ``ok``.
    """
    try:
        completed = run_process(command, cwd=repo_root, timeout_seconds=timeout)
    except OSError as exc:
        return {
            "status": "error",
            "exit_code": 1,
            "stdout": "",
            "stderr": "",
            "payload": None,
            "error_kind": "oserror",
            "error": str(exc),
        }
    if completed.returncode == 124 and completed.stderr.startswith("timed out after "):
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": completed.stdout,
            "stderr": "",
            "payload": None,
            "error_kind": "timeout",
        }
    if not completed.stdout.strip():
        # No output is NOT an empty result set: a `--format json` query always emits a
        # report object (probed 2026-07-28 — a scope root with no supported files still
        # prints `{"families":[],...,"summary":{"families":0,...}}` and exits 0), so blank
        # stdout is a died/produced-nothing run. Substituting `[]` here let a code-clone
        # consumer read it as a clean scan (triage sweep S34's sibling); the doc consumer
        # had to re-detect it from `stdout` instead.
        return _unreadable_result(completed, "empty-output")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return _unreadable_result(completed, "invalid-json", error=str(exc))
    return _completed_result(
        completed,
        payload=payload,
        error_kind="nonzero" if completed.returncode else None,
    )
