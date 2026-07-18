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
import subprocess
from pathlib import Path
from typing import Any

VERSION_TIMEOUT_SECONDS = 30
NOSE_TIMEOUT_SECONDS = 180
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def _completed_result(completed: subprocess.CompletedProcess[str], **extra: Any) -> dict[str, Any]:
    """Normalize fields shared by every completed Nose subprocess."""
    result = {
        "status": "ok" if completed.returncode == 0 else "error",
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr.strip(),
    }
    result.update(extra)
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
        completed = subprocess.run(
            [nose_bin, "--version"], check=False, capture_output=True, text=True,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "exit_code": 124, "stdout": "", "stderr": "", "version": None}
    except OSError:
        return {"status": "error", "exit_code": 1, "stdout": "", "stderr": "", "version": None}
    return _completed_result(completed, version=parse_nose_version(completed.stdout or ""))


def version_text(version: tuple[int, int, int] | None) -> str:
    """Return the canonical dotted form, or an empty stamp when unknown."""
    return ".".join(str(part) for part in version) if version is not None else ""


def run_json_query(repo_root: Path, command: list[str], *, timeout: int = NOSE_TIMEOUT_SECONDS) -> dict[str, Any]:
    """Run a JSON-emitting Nose command with a stable raw transport contract.

    ``payload`` is present whenever stdout parses, even for a nonzero exit. This
    lets schema owners preserve diagnostic details without re-running a command.
    """
    try:
        completed = subprocess.run(
            command, cwd=repo_root, check=False, capture_output=True, text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error", "exit_code": 124, "stdout": str(exc.stdout or ""),
            "stderr": "", "payload": None, "error_kind": "timeout",
        }
    except OSError as exc:
        return {
            "status": "error", "exit_code": 1, "stdout": "", "stderr": "",
            "payload": None, "error_kind": "oserror", "error": str(exc),
        }
    try:
        payload = json.loads(completed.stdout) if completed.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {
            "status": "error", "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr.strip(),
            "payload": None, "error_kind": "invalid-json", "error": str(exc),
        }
    return _completed_result(
        completed,
        payload=payload,
        error_kind="nonzero" if completed.returncode else None,
    )
