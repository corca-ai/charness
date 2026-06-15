#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SUPPORTED_BLOCK_SCALAR_RE = re.compile(r"^[|>](-)?$")


def _coerce_scalar(value: str) -> Any:
    _reject_unsupported_scalar(value)
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
        return _decode_double_quoted(value[1:-1])
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _is_quoted_scalar(value: str) -> bool:
    return (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))


def _decode_double_quoted(value: str) -> str:
    decoded: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\" or index + 1 >= len(value):
            decoded.append(char)
            index += 1
            continue
        escaped = value[index + 1]
        if escaped == "n":
            decoded.append("\n")
        elif escaped == "r":
            decoded.append("\r")
        elif escaped in {'"', "\\"}:
            decoded.append(escaped)
        else:
            decoded.append("\\")
            decoded.append(escaped)
        index += 2
    return "".join(decoded)


def _reject_unsupported_scalar(value: str) -> None:
    stripped = value.strip()
    if not stripped or _is_quoted_scalar(stripped):
        return
    if stripped.startswith(("*", "&", "!")):
        raise ValueError(f"unsupported YAML construct in scalar: {value!r}")


def _find_mapping_separator(value: str) -> int:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == ":":
            return index
    return -1


def _split_mapping_entry(value: str) -> tuple[str, str] | None:
    separator = _find_mapping_separator(value)
    if separator < 0:
        return None
    key = _coerce_scalar(value[:separator].strip())
    if not isinstance(key, str):
        key = str(key)
    return key, value[separator + 1 :].strip()


def _next_meaningful_line(lines: list[str], start: int) -> tuple[int, str] | None:
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index, lines[index]
    return None


def _parse_list_items(lines: list[str], start: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
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
        if current_indent == indent:
            if not stripped.startswith("- "):
                break
            item_body = stripped[2:].strip()
            if not item_body:
                items.append("")
                index += 1
                continue
            if _is_quoted_scalar(item_body):
                items.append(_coerce_scalar(item_body))
                index += 1
                continue
            separator = _find_mapping_separator(item_body)
            mapping_entry = _split_mapping_entry(item_body)
            has_mapping_separator = separator == len(item_body) - 1 or (
                separator >= 0 and item_body[separator + 1].isspace()
            )
            if mapping_entry is not None and has_mapping_separator and " " not in mapping_entry[0]:
                key, value = mapping_entry
                item: dict[str, Any] = {}
                if value:
                    if value == "[]":
                        item[key] = []
                    elif value.startswith(("|", ">")):
                        item[key], index = _parse_block_scalar(lines, index, indent, value)
                        items.append(item)
                        continue
                    else:
                        item[key] = _coerce_scalar(value)
                    index += 1
                else:
                    item[key], index = _parse_empty_value(lines, index, indent)
                nested, index = _parse_block(lines, index, indent + 2)
                item.update(nested)
                items.append(item)
                continue
            items.append(_coerce_scalar(item_body))
            index += 1
            continue
        index += 1
    return items, index


def _parse_empty_value(lines: list[str], index: int, current_indent: int) -> tuple[Any, int]:
    next_item = _next_meaningful_line(lines, index + 1)
    if next_item is None:
        return {}, index + 1
    next_index, next_raw = next_item
    next_stripped = next_raw.strip()
    next_indent = len(next_raw) - len(next_raw.lstrip(" "))
    if next_stripped.startswith("- "):
        if next_indent < current_indent:
            return {}, index + 1
        return _parse_list_items(lines, next_index, next_indent)
    if next_indent <= current_indent:
        return {}, index + 1
    return _parse_block(lines, index + 1, current_indent + 2)


def _parse_block_scalar(lines: list[str], start: int, current_indent: int, header: str) -> tuple[str, int]:
    if SUPPORTED_BLOCK_SCALAR_RE.fullmatch(header) is None:
        raise ValueError(f"unsupported YAML construct in block scalar header: {header!r}")
    style = header[0]
    strip_final = header.endswith("-")
    index = start + 1
    block_indent: int | None = None
    collected: list[str] = []
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        if stripped and indent <= current_indent:
            break
        if block_indent is None and stripped:
            block_indent = indent
        trim = block_indent if block_indent is not None else current_indent + 2
        collected.append(raw[trim:] if len(raw) >= trim else "")
        index += 1
    if style == ">":
        rendered = " ".join(line.strip() for line in collected if line.strip())
    else:
        rendered = "\n".join(collected)
    if not strip_final:
        rendered += "\n"
    return rendered, index


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
        if stripped.startswith("- "):
            index += 1
            continue

        mapping_entry = _split_mapping_entry(stripped)
        if mapping_entry is None:
            index += 1
            continue
        key, value = mapping_entry

        if value:
            if value == "[]":
                result[key] = []
            elif value.startswith(("|", ">")):
                result[key], index = _parse_block_scalar(lines, index, current_indent, value)
                continue
            else:
                result[key] = _coerce_scalar(value)
            index += 1
            continue

        result[key], index = _parse_empty_value(lines, index, current_indent)

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


def optional_bool(value: Any, field: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        errors.append(f"{field} must be a boolean")
        return None
    return value


def list_field_state(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return "unset"
    value = data.get(field)
    if isinstance(value, list) and len(value) == 0:
        return "explicit-empty"
    return "configured"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        if (
            value == ""
            or value[0] in "*&!@`#{}[],:>|-'\""
            or any(char in value for char in ("\n", "\r", ": ", "#", "\\"))
            or value != value.strip()
        ):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
            return f'"{escaped}"'
    return str(value)


def _yaml_key(value: Any) -> str:
    if isinstance(value, str) and ":" in value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return _yaml_scalar(value)


def _render_yaml_value(lines: list[str], key: str, value: Any, *, indent: int) -> None:
    prefix = " " * indent
    rendered_key = _yaml_key(key)
    if isinstance(value, dict):
        lines.append(f"{prefix}{rendered_key}:")
        for nested_key, nested_value in value.items():
            _render_yaml_value(lines, nested_key, nested_value, indent=indent + 2)
        return
    if isinstance(value, list):
        if not value:
            lines.append(f"{prefix}{rendered_key}: []")
            return
        lines.append(f"{prefix}{rendered_key}:")
        for item in value:
            _render_yaml_list_item(lines, item, indent=indent + 2)
        return
    lines.append(f"{prefix}{rendered_key}: {_yaml_scalar(value)}")


def _render_yaml_list_item(lines: list[str], item: Any, *, indent: int) -> None:
    prefix = " " * indent
    if isinstance(item, dict):
        first = True
        for nested_key, nested_value in item.items():
            item_prefix = f"{prefix}- " if first else f"{prefix}  "
            rendered_key = _yaml_key(nested_key)
            if isinstance(nested_value, dict):
                lines.append(f"{item_prefix}{rendered_key}:")
                for child_key, child_value in nested_value.items():
                    _render_yaml_value(lines, child_key, child_value, indent=indent + 4)
            elif isinstance(nested_value, list):
                if not nested_value:
                    lines.append(f"{item_prefix}{rendered_key}: []")
                else:
                    lines.append(f"{item_prefix}{rendered_key}:")
                    for child in nested_value:
                        _render_yaml_list_item(lines, child, indent=indent + 4)
            else:
                lines.append(f"{item_prefix}{rendered_key}: {_yaml_scalar(nested_value)}")
            first = False
        return
    lines.append(f"{prefix}- {_yaml_scalar(item)}")


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
