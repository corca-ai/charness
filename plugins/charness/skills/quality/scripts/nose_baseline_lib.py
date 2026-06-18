#!/usr/bin/env python3
"""Baseline resolution + write-mode helpers for the nose clone advisory.

Split out of `inventory_nose_clones.py` so that entrypoint stays under its length
cap: baseline handling (accept the intentional/portability clone mass so the
advisory reports only new/changed drift) is its own concern.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

# Canonical standing baseline of already-accepted (intentional/portability) clone
# families. When present, the advisory reads it by default so it surfaces only
# NEW/changed duplication (drift) rather than re-flagging deliberate per-skill
# bootstrap boilerplate every run. Re-baseline per scanner version with
# --write-baseline (see the advisory-interpretation contract).
DEFAULT_BASELINE_REL = "charness-artifacts/quality/nose-baseline.json"
NOSE_TIMEOUT_SECONDS = 180


def resolve_baseline(*, write_baseline: bool, baseline: str | None, repo_root: Path) -> str | None:
    """Resolve the baseline path nose should use (relative to repo root).

    Write mode falls back to the canonical default so re-baselining is a flagless
    `--write-baseline`. Read mode uses an explicit `--baseline`, else the
    canonical default only when it already exists (so a fresh repo stays
    un-baselined rather than erroring on a missing file).
    """
    if write_baseline:
        return baseline or DEFAULT_BASELINE_REL
    if baseline:
        return baseline
    if (repo_root / DEFAULT_BASELINE_REL).is_file():
        return DEFAULT_BASELINE_REL
    return None


def run_write_baseline(repo_root: Path, command: list[str], baseline: str) -> dict[str, Any]:
    (repo_root / baseline).parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=NOSE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "exit_code": 124, "stdout": "", "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s"}
    return {
        "status": "baseline-written" if completed.returncode == 0 else "error",
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def write_baseline_payload(repo_root: Path, command: list[str], baseline: str | None, roots: list[str]) -> dict[str, Any]:
    result = run_write_baseline(repo_root, command, baseline or DEFAULT_BASELINE_REL)
    return {
        "status": result["status"],
        "advisory": True,
        "repo_root": str(repo_root),
        "paths": roots,
        "baseline": baseline,
        "command": shlex.join(command),
        "exit_code": result["exit_code"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "notes": [
            "Baseline accepts today's intentional/portability families so the advisory reports only new/changed duplication.",
            "Re-baseline per scanner version; never treat the accepted count as a reduction target.",
        ],
    }
