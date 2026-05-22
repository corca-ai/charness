"""TOML serialization and block-scan helpers for the Codex SessionStart hook.

Carved out of `host_hook_install_lib.py` to keep file lengths under the
repo's Python-length budget. Behavior contract stays identical to what
`install_codex_hook` / `uninstall_codex_hook` had inline.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CHARNESS_MARKER = "charness:usage-episodes"


def codex_toml_block(command: str) -> str:
    return "\n".join(
        [
            f"# {CHARNESS_MARKER}",
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


def find_charness_toml_block(text: str, command: str) -> tuple[int, int] | None:
    """Return (start, end) char offsets of a charness-marked TOML block, or None.

    A charness-marked block is `# charness:usage-episodes` immediately followed
    (optionally with blank lines) by `[[hooks.SessionStart]]` plus a
    `command = ...` line whose value equals the recorded command.
    """
    lines = text.splitlines(keepends=True)
    expected_command_line = f"command = {json.dumps(command, ensure_ascii=False)}"
    index = 0
    while index < len(lines):
        if lines[index].strip() == f"# {CHARNESS_MARKER}":
            start = index
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip() == "":
                cursor += 1
            if cursor < len(lines) and lines[cursor].strip() == "[[hooks.SessionStart]]":
                block_end = cursor + 1
                seen_command = False
                while block_end < len(lines):
                    stripped = lines[block_end].strip()
                    if stripped.startswith("#") and CHARNESS_MARKER in stripped:
                        break
                    if stripped.startswith("[") and not stripped.startswith("[[hooks.SessionStart"):
                        break
                    if stripped == expected_command_line:
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


def install_codex_toml_block(settings_path: Path, command: str) -> dict[str, Any]:
    existing = read_text_or_empty(settings_path)
    if find_charness_toml_block(existing, command) is not None:
        return {"settings_path": str(settings_path), "action": "noop"}
    block = codex_toml_block(command)
    if existing and not existing.endswith("\n\n"):
        if not existing.endswith("\n"):
            existing += "\n"
        existing += "\n"
    write_text_atomic(settings_path, existing + block)
    return {"settings_path": str(settings_path), "action": "installed"}


def uninstall_codex_toml_block(settings_path: Path, command: str) -> dict[str, Any]:
    existing = read_text_or_empty(settings_path)
    if not existing:
        return {"settings_path": str(settings_path), "action": "absent"}
    span = find_charness_toml_block(existing, command)
    if span is None:
        return {"settings_path": str(settings_path), "action": "not_installed"}
    start, end = span
    new_text = (existing[:start] + existing[end:]).rstrip("\n")
    if new_text:
        new_text += "\n"
    write_text_atomic(settings_path, new_text)
    return {"settings_path": str(settings_path), "action": "removed"}
