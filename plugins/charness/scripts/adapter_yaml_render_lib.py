#!/usr/bin/env python3
"""Data -> YAML text for adapter and bootstrap scaffolds.

Split out of ``scripts/adapter_lib.py``, which had reached its code-line cap while
holding two independent concepts: reading adapter YAML into data (parser plus field
contract validators) and writing data back out as YAML. Only the writer moved, and it
moved whole -- ``adapter_lib`` deliberately does NOT re-export these names, because a
re-exporting companion would leave the cap dodged rather than the concept separated.

The emitter's invariant is round-trip fidelity with ``adapter_lib.load_yaml``: anything
rendered here must reload as the same value. That is what forces the quoting rules below,
and why the round-trip tests import both modules together.
"""
from __future__ import annotations

from typing import Any


def _string_round_trips_bare(value: str) -> bool:
    """Would this string parse back as the same string if emitted without quotes?

    A string like ``"true"`` or ``"123"`` is legal YAML text, but emitted bare it
    reloads as a bool or an int. That silently changes a value's type across a
    write/read cycle, so such a string has to be quoted.
    """
    if value.lower() in ("true", "false", "null", "~"):
        return False
    for parse in (int, float):
        try:
            parse(value)
        except ValueError:
            continue
        return False
    return True


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
            or not _string_round_trips_bare(value)
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
