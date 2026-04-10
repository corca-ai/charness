#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any


def _coerce_scalar(value: str) -> Any:
    if value == "":
        return ""
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in ("null", "~"):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[Any] | None = None

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key is not None:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(_coerce_scalar(stripped[2:].strip()))
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        current_list = None
        if not value:
            current_key = key
            continue
        if value == "[]":
            result[key] = []
            current_key = key
            continue
        result[key] = _coerce_scalar(value)
        current_key = key

    return result


def load_yaml_file(path: Path) -> dict[str, Any]:
    return load_yaml(path.read_text(encoding="utf-8"))


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_yaml_mapping(items: list[tuple[str, Any]]) -> str:
    lines: list[str] = []
    for key, value in items:
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
                continue
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"- {_yaml_scalar(item)}")
            continue
        lines.append(f"{key}: {_yaml_scalar(value)}")
    return "\n".join(lines) + "\n"


def write_adapter_scaffold(repo_root: Path, output: Path, contents: str, force: bool) -> Path:
    resolved_output = output if output.is_absolute() else repo_root / output
    if resolved_output.exists() and not force:
        raise SystemExit(f"Adapter already exists at {resolved_output}. Use --force to overwrite.")

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(contents, encoding="utf-8")
    return resolved_output
