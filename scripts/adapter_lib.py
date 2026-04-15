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
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _next_meaningful_line(lines: list[str], start: int) -> tuple[int, str] | None:
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index, lines[index]
    return None


def _parse_block(lines: list[str], start: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    index = start

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        current_indent = len(raw) - len(raw.lstrip(" "))

        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if current_indent < indent:
            break
        if current_indent > indent:
            index += 1
            continue
        if stripped.startswith("- ") or ":" not in stripped:
            index += 1
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if value:
            if value == "[]":
                result[key] = []
            else:
                result[key] = _coerce_scalar(value)
            index += 1
            continue

        next_item = _next_meaningful_line(lines, index + 1)
        if next_item is None:
            result[key] = {}
            index += 1
            continue

        next_index, next_raw = next_item
        next_stripped = next_raw.strip()
        next_indent = len(next_raw) - len(next_raw.lstrip(" "))
        if next_stripped.startswith("- "):
            if next_indent < current_indent:
                result[key] = {}
                index += 1
                continue
            items: list[Any] = []
            list_index = next_index
            while list_index < len(lines):
                list_raw = lines[list_index]
                list_stripped = list_raw.strip()
                list_indent = len(list_raw) - len(list_raw.lstrip(" "))
                if not list_stripped or list_stripped.startswith("#"):
                    list_index += 1
                    continue
                if list_indent < next_indent:
                    break
                if list_indent == next_indent:
                    if not list_stripped.startswith("- "):
                        break
                    items.append(_coerce_scalar(list_stripped[2:].strip()))
                    list_index += 1
                    continue
                list_index += 1
            result[key] = items
            index = list_index
            continue
        if next_indent <= current_indent:
            result[key] = {}
            index += 1
            continue

        nested, next_after_nested = _parse_block(lines, index + 1, current_indent + 2)
        result[key] = nested
        index = next_after_nested

    return result, index


def load_yaml(text: str) -> dict[str, Any]:
    parsed, _ = _parse_block(text.splitlines(), 0, 0)
    return parsed


def load_yaml_file(path: Path) -> dict[str, Any]:
    return load_yaml(path.read_text(encoding="utf-8"))


def optional_string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def optional_string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        if (
            value == ""
            or value[0] in "*&!@`#{}[],:>|-'\""
            or any(char in value for char in ("\n", ": ", "#", "\\"))
            or value != value.strip()
        ):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
    return str(value)


def _render_yaml_value(lines: list[str], key: str, value: Any, *, indent: int) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        lines.append(f"{prefix}{key}:")
        for nested_key, nested_value in value.items():
            _render_yaml_value(lines, nested_key, nested_value, indent=indent + 2)
        return
    if isinstance(value, list):
        if not value:
            lines.append(f"{prefix}{key}: []")
            return
        lines.append(f"{prefix}{key}:")
        for item in value:
            lines.append(f"{prefix}  - {_yaml_scalar(item)}")
        return
    lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")


def render_yaml_mapping(items: list[tuple[str, Any]]) -> str:
    lines: list[str] = []
    for key, value in items:
        _render_yaml_value(lines, key, value, indent=0)
    return "\n".join(lines) + "\n"


def write_adapter_scaffold(repo_root: Path, output: Path, contents: str, force: bool) -> Path:
    resolved_output = output if output.is_absolute() else repo_root / output
    if resolved_output.exists() and not force:
        raise SystemExit(f"Adapter already exists at {resolved_output}. Use --force to overwrite.")

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(contents, encoding="utf-8")
    return resolved_output
