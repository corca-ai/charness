from __future__ import annotations

from typing import Any


def default_release_backend() -> dict[str, Any]:
    return {"id": "gh", "binary": "gh", "commands": None}


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def parse_release_backend(raw: Any, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    if raw is None:
        return default_release_backend()
    if not isinstance(raw, dict):
        errors.append("release_backend must be a mapping")
        return default_release_backend()
    backend_id = _string(raw.get("id"), "release_backend.id", errors) or "gh"
    binary = _string(raw.get("binary"), "release_backend.binary", errors) or backend_id
    commands: dict[str, list[str]] | None = None
    raw_commands = raw.get("commands")
    if raw_commands is not None:
        if not isinstance(raw_commands, dict):
            errors.append("release_backend.commands must be a mapping")
        else:
            commands = {}
            for op, argv in raw_commands.items():
                if not isinstance(argv, list) or not all(isinstance(part, str) for part in argv):
                    errors.append(f"release_backend.commands.{op} must be a list of strings")
                    continue
                commands[op] = list(argv)
    if backend_id != "gh" and not commands:
        warnings.append(
            f"release_backend.id={backend_id} declared without commands; "
            "agent must follow the host-documented command shape until commands templates are filled in"
        )
    return {"id": backend_id, "binary": binary, "commands": commands}
