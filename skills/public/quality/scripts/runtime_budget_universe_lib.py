"""Read a consumer-owned runtime-label universe for budget reconciliation.

The runner is repository-specific: Charness cannot infer labels from an npm
script, Makefile, workflow, or another project's dispatcher.  An optional
adapter command therefore owns that discovery and emits one label per line.
This reader only reconciles the result with the adapter's budget union; it
never infers whether a conditional label actually ran.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from runtime_profile_lib import budgeted_label_union

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

COMMAND_TIMEOUT_SECONDS = 30


def _result(
    *,
    configured: bool,
    status: str,
    command: str | None = None,
    labels: list[str] | None = None,
    missing_labels: list[str] | None = None,
    unbudgeted_labels: list[str] | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "configured": configured,
        "status": status,
        "command": command,
        "labels": labels or [],
        "missing_labels": missing_labels or [],
        "unbudgeted_labels": unbudgeted_labels or [],
        "errors": errors or [],
    }


def _parse_labels(stdout: str) -> tuple[list[str], list[str]]:
    labels: list[str] = []
    seen: set[str] = set()
    errors: list[str] = []
    for line_number, raw_line in enumerate(stdout.splitlines(), start=1):
        label = raw_line.strip()
        if not label:
            continue
        if label in seen:
            errors.append(
                f"runtime_budget_universe.command emitted duplicate label `{label}` on line {line_number}"
            )
            continue
        seen.add(label)
        labels.append(label)
    if not labels:
        errors.append(
            "runtime_budget_universe.command emitted no labels; the runner universe is not established"
        )
    return sorted(labels), errors


def read(
    repo_root: Path,
    adapter_data: dict[str, Any],
    budgeted_labels: dict[str, list[str]],
) -> dict[str, Any]:
    """Resolve the optional consumer command and compare every budgeted label.

    An absent command is deliberately ``not-declared`` and non-blocking.  Once
    declared, command failure, empty output, duplicate labels, and budget labels
    absent from the returned universe are configuration failures: a partial
    universe cannot honestly support a green reconciliation.
    """
    if not budgeted_labels:
        return _result(
            configured=False,
            status="not-applicable",
        )
    config = adapter_data.get("runtime_budget_universe")
    if not config:
        return _result(configured=False, status="not-declared")
    if not isinstance(config, dict):
        return _result(
            configured=True,
            status="unestablished",
            errors=["runtime_budget_universe must be a mapping"],
        )
    command = config.get("command")
    if not isinstance(command, str) or not command.strip():
        return _result(
            configured=True,
            status="unestablished",
            errors=["runtime_budget_universe.command must be a non-empty string"],
        )
    command = command.strip()
    try:
        result = run_process(
            command,
            cwd=repo_root,
            shell=True,
            timeout_seconds=COMMAND_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        return _result(
            configured=True,
            status="unestablished",
            command=command,
            errors=[f"runtime_budget_universe.command could not run: {type(exc).__name__}: {exc}"],
        )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        return _result(
            configured=True,
            status="unestablished",
            command=command,
            errors=[f"runtime_budget_universe.command exited {result.returncode}{suffix}"],
        )
    labels, errors = _parse_labels(result.stdout)
    if errors:
        return _result(
            configured=True,
            status="unestablished",
            command=command,
            labels=labels,
            errors=errors,
        )
    known = set(labels)
    budgeted = set(budgeted_labels)
    missing = sorted(budgeted - known)
    unbudgeted = sorted(known - budgeted)
    mismatch_errors = []
    if missing:
        mismatch_errors.append(
            "runtime_budget_universe is missing budgeted label(s): " + ", ".join(missing)
        )
    return _result(
        configured=True,
        status="mismatch" if mismatch_errors else "resolved",
        command=command,
        labels=labels,
        missing_labels=missing,
        unbudgeted_labels=unbudgeted,
        errors=mismatch_errors,
    )


def read_for_adapter(repo_root: Path, adapter_data: dict[str, Any]) -> dict[str, Any]:
    """Read the adapter's optional command against every budget block."""
    return read(repo_root, adapter_data, budgeted_label_union(adapter_data))
