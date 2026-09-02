"""Read consumer-health packets from a repository's declared quality gates."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any, Callable

QUALITY_GATES_PATH = Path(".agents") / "quality-gates.yaml"
TOOLS_OWNERSHIP = {
    "tools",
    "repo-only",
    "authoring",
    "authoring-repo",
}  # export-guard: classifies declared rows as repo-only; never executes them
SHIP_OWNERSHIP = {"ship", "consumer", "consumer-facing"}
PACKET_METADATA = ("lane", "condition", "variant_of", "timing_layer", "note")


def _tokens(command: object) -> list[str]:
    if isinstance(command, list):
        return [str(token) for token in command]
    if not isinstance(command, str):
        return []
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _is_tools_command(command: object) -> bool:
    """Recognize checks whose implementation is carried by the authoring tools/."""
    tokens = _tokens(command)
    for index, token in enumerate(tokens):
        normalized = token.replace("\\", "/")
        if token.startswith("tools.") or normalized.startswith("tools/"):
            return True
        if "/tools/" in normalized or normalized.endswith(
            "/tools.py"
        ):  # export-guard: classifies declared rows as repo-only; never executes them
            return True
        if (
            index and tokens[index - 1] == "-m" and token.startswith("tools")
        ):  # export-guard: classifies declared rows as repo-only; never executes them
            return True
    return False


def _is_consumer_gate(row: dict[str, Any]) -> bool:
    ownership = next(
        (
            str(row[field]).strip().lower()
            for field in ("scope", "classification", "consumer_scope")
            if row.get(field) is not None
        ),
        "",
    )
    lane = str(row.get("lane") or "").strip().lower()
    if ownership in TOOLS_OWNERSHIP or lane == "tools":
        return False
    if ownership in SHIP_OWNERSHIP or lane in SHIP_OWNERSHIP:
        return not _is_tools_command(row.get("command"))
    # The current declaration schema uses execution lanes (core/standard/etc.);
    # until it grows an ownership field, the tools/ command carrier is its marker.
    return not _is_tools_command(row.get("command"))


def _source_rows(raw: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    phases = raw.get("phases")
    if isinstance(phases, list):
        for phase in phases:
            if not isinstance(phase, dict) or not isinstance(phase.get("gates"), list):
                continue
            phase_id = str(phase.get("id") or "")
            rows.extend((phase_id, row) for row in phase["gates"] if isinstance(row, dict))
        return rows
    gates = raw.get("gates")
    if isinstance(gates, list):
        rows.extend(("", row) for row in gates if isinstance(row, dict))
    return rows


def read_consumer_gate_packets(
    repo_root: Path, load_yaml: Callable[[Path], dict[str, Any]]
) -> list[dict[str, Any]] | None:
    """Return declared ship packets, or ``None`` for the discovery fallback."""
    path = repo_root / QUALITY_GATES_PATH
    if not path.is_file():
        return None
    raw = load_yaml(path)
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: declared quality gates must be a mapping")

    packets: list[dict[str, Any]] = []
    for phase_id, row in _source_rows(raw):
        label = row.get("label")
        command = row.get("command")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"{path}: declared gate is missing a non-empty `label`")
        if not isinstance(command, (str, list)) or not _tokens(command):
            raise ValueError(f"{path}: declared gate `{label}` is missing `command`")
        if not _is_consumer_gate(row):
            continue
        command_text = command if isinstance(command, str) else " ".join(map(str, command))
        packet: dict[str, Any] = {
            "id": label,
            "command": command_text,
            "purpose": f"execute declared consumer-repo health gate `{label}`",
            "trust_model": (
                "repo-declared route; planner inclusion proves reachability only, "
                "and execution remains not-run until a later receipt says otherwise"
            ),
            "cost_tier": "unknown",
            "parallel_group": f"declared:{phase_id}" if phase_id else "declared",
            "run_after": "required-primer",
            "run_when": "declared in .agents/quality-gates.yaml",
        }
        if phase_id:
            packet["phase_id"] = phase_id
        for key in PACKET_METADATA:
            if key in row:
                packet[key] = row[key]
        packets.append(packet)
    return packets
