"""Adapter-aware applicability for catalog quality gates."""
from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

COMMAND_FIELDS = (
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)


def _catalog_gate_path(command: str) -> Path | None:
    """Return a repo-relative executable path only for an explicit local command."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return None
    if not argv or not argv[0].startswith("./"):
        return None
    return Path(argv[0])


def applicable_catalog_gates(
    repo_root: Path, raw: dict[str, Any], catalog_gates: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Keep adapter-owned plans from advertising absent repo-native defaults.

    A valid adapter owns its declared commands. A catalog command described as
    repo-native therefore needs filesystem evidence unless the adapter declares
    that exact command. Other ``run_when`` prose stays advisory.
    """
    declared_commands = {
        command.strip()
        for field in COMMAND_FIELDS
        for command in (raw.get(field, []) if isinstance(raw.get(field), list) else [])
        if isinstance(command, str) and command.strip()
    }
    applicable: list[dict[str, Any]] = []
    unavailable: list[dict[str, str]] = []
    for gate in catalog_gates:
        command = gate.get("command")
        run_when = str(gate.get("run_when") or "")
        path = _catalog_gate_path(command) if isinstance(command, str) else None
        requires_native_path = path is not None and "repo-native command" in run_when
        if (
            requires_native_path
            and command not in declared_commands
            and not (repo_root / path).is_file()
        ):
            unavailable.append(
                {
                    "id": str(gate.get("id") or command),
                    "command": command,
                    "reason": f"missing repo-native command {path.as_posix()}",
                }
            )
            continue
        applicable.append(gate)
    return applicable, unavailable
