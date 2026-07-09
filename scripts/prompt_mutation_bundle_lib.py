"""Shared readers for prompt-mutation preserved bundle evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def iter_jsonl_dicts(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        try:
            record = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            yield record


def tool_input_strings(record: dict[str, Any]) -> list[str]:
    message = record.get("message") if isinstance(record.get("message"), dict) else record
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        block_input = block.get("input")
        if not isinstance(block_input, dict):
            continue
        for value in block_input.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.append(" ".join(v for v in value if isinstance(v, str)))
    return parts


def stream_command_blob(stream_path: Path) -> str:
    """Every string tool-call input value across a stream.jsonl."""
    return "\n".join(
        value
        for event in iter_jsonl_dicts(stream_path)
        for value in tool_input_strings(event)
    )
