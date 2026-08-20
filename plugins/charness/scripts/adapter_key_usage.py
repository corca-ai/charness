#!/usr/bin/env python3
"""Classify structural adapter-key usage inside one Python reader module.

The adapter-key registry owns resolution policy and reader association; this module
owns the AST question of whether a Python module actually consumes a value, refuses a
value, or merely mentions it. Keeping that seam explicit prevents the registry from
becoming a second parser and gives future reader shapes one focused classifier to
extend.
"""
from __future__ import annotations

import ast
from pathlib import Path

_KEY_USAGE_CACHE: dict[Path, tuple[set[str], set[str]]] = {}


def _string_values(node: ast.AST) -> set[str]:
    return {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}


def _key_value(node: ast.AST, aliases: dict[str, str]) -> set[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.Name) and node.id in aliases:
        return {aliases[node.id]}
    return set()


def _loop_bound_reads(nodes: list[ast.AST], aliases: dict[str, str]) -> set[str]:
    """Resolve literal field loops consumed by ``data.get(field)`` or ``data[field]``."""
    reads: set[str] = set()
    for node in nodes:
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        values = _string_values(node.iter)
        if not values:
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Subscript) and child is not node:
                if isinstance(child.slice, ast.Name) and child.slice.id == node.target.id:
                    reads.update(values)
                else:
                    reads.update(_key_value(child.slice, aliases))
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr in {"get", "pop", "setdefault"}
                and child.args
                and isinstance(child.args[0], ast.Name)
                and child.args[0].id == node.target.id
            ):
                reads.update(values)
    return reads


def _intent_reader_keys(nodes: list[ast.AST], aliases: dict[str, str]) -> set[str]:
    """Resolve adapter sections routed through the shared host-hook accessor."""
    reads: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.FunctionDef) and node.name == "_intent_for":
            defaults = list(node.args.defaults)
            positional = node.args.args[-len(defaults) :] if defaults else []
            for argument, default in zip(positional, defaults):
                if argument.arg == "section":
                    reads.update(_key_value(default, aliases))
            for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                if argument.arg == "section" and default is not None:
                    reads.update(_key_value(default, aliases))
        if isinstance(node, ast.Call):
            function_name = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else node.func.id
                if isinstance(node.func, ast.Name)
                else None
            )
            if function_name == "_intent_for":
                reads.update(
                    key
                    for keyword in node.keywords
                    if keyword.arg == "section"
                    for key in _key_value(keyword.value, aliases)
                )
    return reads


def key_usage(path: Path) -> tuple[set[str], set[str]]:
    """Return ``(refusal candidates, structural value reads)`` for one module."""
    cached = _KEY_USAGE_CACHE.get(path)
    if cached is not None:
        return cached
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        _KEY_USAGE_CACHE[path] = (set(), set())
        return _KEY_USAGE_CACHE[path]

    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets, value = (node.targets, node.value) if isinstance(node, ast.Assign) else ((node.target,), node.value)
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            for target in targets:
                for name in (item.id for item in ast.walk(target) if isinstance(item, ast.Name)):
                    aliases[name] = value.value

    nodes = list(ast.walk(tree))
    field_registry_values: set[str] = set()
    field_registry_names: set[str] = set()
    for node in nodes:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets, value = (node.targets, node.value) if isinstance(node, ast.Assign) else ((node.target,), node.value)
        names = {
            name.id
            for target in targets
            for name in ast.walk(target)
            if isinstance(name, ast.Name) and (name.id.endswith("_FIELDS") or name.id == "FIELDS")
        }
        non_retired_names = {name for name in names if not name.upper().startswith("RETIRED")}
        field_registry_names.update(non_retired_names)
        if non_retired_names:
            field_registry_values.update(_string_values(value))

    refused = {
        key
        for node in nodes
        if isinstance(node, ast.Compare)
        and any(isinstance(operator, (ast.In, ast.NotIn)) for operator in node.ops)
        for operand in (node.left, *node.comparators)
        for key in _key_value(operand, aliases)
    }
    refused.update(
        key
        for node in nodes
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for targets, value in ((node.targets, node.value) if isinstance(node, ast.Assign) else ((node.target,), node.value),)
        if any(
            name.id.upper().startswith("RETIRED")
            for target in targets
            for name in ast.walk(target)
            if isinstance(name, ast.Name)
        )
        for key in _string_values(value)
    )
    reads = {
        key for node in nodes if isinstance(node, ast.Subscript) for key in _key_value(node.slice, aliases)
    }
    reads.update(
        key
        for node in nodes
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"get", "pop", "setdefault"}
        for argument in node.args[:1]
        for key in _key_value(argument, aliases)
    )
    reads.update(_loop_bound_reads(nodes, aliases))
    reads.update(_intent_reader_keys(nodes, aliases))
    if any(
        isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in field_registry_names
        for node in nodes
    ):
        reads.update(field_registry_values)
    reads.update(
        key
        for node in nodes
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "list_field_state"
        for argument in node.args[1:2]
        for key in _key_value(argument, aliases)
    )

    _KEY_USAGE_CACHE[path] = (refused, reads)
    return _KEY_USAGE_CACHE[path]
