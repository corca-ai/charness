from __future__ import annotations

import shlex
from pathlib import Path

RISKY_AGENT_BROWSER_COMMANDS = {
    "open",
    "wait",
    "get",
    "network",
    "snapshot",
    "screenshot",
    "pdf",
    "click",
    "type",
    "fill",
    "eval",
    "connect",
}


def _agent_browser_parts(parts: list[str]) -> list[str] | None:
    for index, part in enumerate(parts):
        if Path(part).name == "agent-browser":
            return parts[index:]

    shell = Path(parts[0]).name if parts else ""
    shell_command_flags = {"-c", "-lc", "-cl"}
    flag_indexes = [index for index, part in enumerate(parts) if part in shell_command_flags]
    if shell in {"bash", "sh", "zsh"} and flag_indexes:
        index = flag_indexes[-1] + 1
        if index < len(parts):
            try:
                nested = shlex.split(parts[index])
            except ValueError:
                return None
            return _agent_browser_parts(nested)
    return None


def _runtime_tokens(parts: list[str]) -> list[str]:
    tokens: list[str] = []
    skip_next = False
    for part in parts[1:]:
        if skip_next:
            skip_next = False
            continue
        if part == "--session":
            skip_next = True
            continue
        if part.startswith("--session="):
            continue
        tokens.append(part)
    return tokens


def unsafe_agent_browser_probe_reason(command: str) -> str | None:
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    agent_browser_parts = _agent_browser_parts(parts)
    if agent_browser_parts is None:
        return None

    tokens = _runtime_tokens(agent_browser_parts)
    if any(token in {"--help", "-h"} for token in tokens):
        return (
            "direct `agent-browser --help` probe can warm browser runtime state; "
            "use the repo runtime guard or `agent-browser --version`"
        )

    for token in tokens:
        if token in RISKY_AGENT_BROWSER_COMMANDS:
            return (
                f"direct `agent-browser {token}` probe can leave browser runtime state; "
                "route it through a lifecycle-owned support script"
            )
    return None
