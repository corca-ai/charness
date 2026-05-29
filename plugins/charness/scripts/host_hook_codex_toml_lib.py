"""TOML serialization and block-scan helpers for the Codex SessionStart hook.

Carved out of `host_hook_install_lib.py` to keep file lengths under the
repo's Python-length budget. Behavior contract stays identical to what
`install_codex_hook` / `uninstall_codex_hook` had inline.
"""

from __future__ import annotations

import json
import os
import shlex
from pathlib import Path
from typing import Any

CHARNESS_MARKER = "charness:usage-episodes"


def script_basename(command: str) -> str | None:
    """Logical identity of a charness hook command = its `.py` script basename.

    The same charness hook installed from two checkouts has different absolute
    paths but the same basename; dedup matches on this so a second checkout does
    not double-install (corca-ai/charness#245).
    """
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    for part in parts:
        if part.endswith(".py"):
            return Path(part).name
    return None


def _toml_command_value(stripped_line: str) -> str | None:
    """Parse the value of a `command = "..."` TOML line, or None."""
    if not stripped_line.startswith("command ="):
        return None
    try:
        value = json.loads(stripped_line.split("=", 1)[1].strip())
    except (json.JSONDecodeError, IndexError):
        return None
    return value if isinstance(value, str) else None


def codex_toml_block(command: str, marker: str = CHARNESS_MARKER) -> str:
    return "\n".join(
        [
            f"# {marker}",
            "[[hooks.SessionStart]]",
            "[[hooks.SessionStart.hooks]]",
            'type = "command"',
            f"command = {json.dumps(command, ensure_ascii=False)}",
            "",
        ]
    )


def read_text_or_empty(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def find_charness_toml_block(text: str, command: str, marker: str = CHARNESS_MARKER) -> tuple[int, int] | None:
    """Return (start, end) char offsets of a charness-marked TOML block, or None.

    A charness-marked block is `# <marker>` immediately followed (optionally with
    blank lines) by `[[hooks.SessionStart]]` plus a `command = ...` line whose
    script basename matches the recorded command's (#245: a second checkout
    installs the same hook at a different absolute path — logical identity, not
    the exact path, is what dedups).
    """
    lines = text.splitlines(keepends=True)
    target_identity = script_basename(command)
    expected_command_line = f"command = {json.dumps(command, ensure_ascii=False)}"
    index = 0
    while index < len(lines):
        if lines[index].strip() == f"# {marker}":
            start = index
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip() == "":
                cursor += 1
            if cursor < len(lines) and lines[cursor].strip() == "[[hooks.SessionStart]]":
                block_end = cursor + 1
                seen_command = False
                while block_end < len(lines):
                    stripped = lines[block_end].strip()
                    # Stop at the start of ANY charness block, not just this
                    # marker's — once a second distinct marker exists
                    # (find-skills vs usage-episodes, #244/#245), breaking only
                    # on the own marker would run past the next charness block's
                    # header and swallow it, so uninstalling one block would
                    # destroy the adjacent one.
                    if stripped.startswith("# charness:"):
                        break
                    if stripped.startswith("[") and not stripped.startswith("[[hooks.SessionStart"):
                        break
                    if stripped == expected_command_line:
                        seen_command = True
                    elif target_identity is not None:
                        existing = _toml_command_value(stripped)
                        if existing is not None and script_basename(existing) == target_identity:
                            seen_command = True
                    block_end += 1
                if seen_command:
                    while block_end > 0 and lines[block_end - 1].strip() == "":
                        block_end -= 1
                    while block_end < len(lines) and lines[block_end].strip() == "":
                        block_end += 1
                    char_start = sum(len(item) for item in lines[:start])
                    char_end = sum(len(item) for item in lines[:block_end])
                    return char_start, char_end
        index += 1
    return None


def install_codex_toml_block(settings_path: Path, command: str, marker: str = CHARNESS_MARKER) -> dict[str, Any]:
    existing = read_text_or_empty(settings_path)
    if find_charness_toml_block(existing, command, marker) is not None:
        return {"settings_path": str(settings_path), "action": "noop"}
    block = codex_toml_block(command, marker)
    if existing and not existing.endswith("\n\n"):
        if not existing.endswith("\n"):
            existing += "\n"
        existing += "\n"
    write_text_atomic(settings_path, existing + block)
    return {"settings_path": str(settings_path), "action": "installed"}


def uninstall_codex_toml_block(settings_path: Path, command: str, marker: str = CHARNESS_MARKER) -> dict[str, Any]:
    existing = read_text_or_empty(settings_path)
    if not existing:
        return {"settings_path": str(settings_path), "action": "absent"}
    span = find_charness_toml_block(existing, command, marker)
    if span is None:
        return {"settings_path": str(settings_path), "action": "not_installed"}
    start, end = span
    new_text = (existing[:start] + existing[end:]).rstrip("\n")
    if new_text:
        new_text += "\n"
    write_text_atomic(settings_path, new_text)
    return {"settings_path": str(settings_path), "action": "removed"}
