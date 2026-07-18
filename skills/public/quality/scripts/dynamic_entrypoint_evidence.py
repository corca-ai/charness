#!/usr/bin/env python3

from __future__ import annotations

import ast
from pathlib import Path


def _caller_path(node: ast.AST) -> bool:
    match node:
        case ast.Call(func=ast.Name(id="Path"), args=[ast.Name(id="__file__")]):
            return True
        case ast.Call(func=ast.Attribute(value=value, attr="resolve"), args=[]):
            return _caller_path(value)
        case _:
            return False


def _caller_parent(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "parent" and _caller_path(node.value)


def _sibling_path_matches(node: ast.AST, producer_name: str) -> bool:
    while (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"str", "Path"}
        and len(node.args) == 1
    ):
        node = node.args[0]
    if (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Constant)
        and node.right.value == producer_name
    ):
        return _caller_parent(node.left)
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "with_name"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == producer_name
        and _caller_path(node.func.value)
    )


def _intent_constructor(call: ast.Call) -> bool:
    return isinstance(call.func, ast.Name) and call.func.id.endswith("Intent")


def _module_loader(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Name) and call.func.id in {"import_module", "_import_module"}
    ) or (isinstance(call.func, ast.Attribute) and call.func.attr == "import_module")


def _function_nodes(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _function_default_registries(tree: ast.AST, registries: set[str]) -> dict[int, dict[str, str]]:
    aliases: dict[int, dict[str, str]] = {}
    for function in _function_nodes(tree):
        mapping: dict[str, str] = {}
        positional = function.args.posonlyargs + function.args.args
        for argument, default in zip(positional[-len(function.args.defaults) :], function.args.defaults):
            if isinstance(default, ast.Name) and default.id in registries:
                mapping[argument.arg] = default.id
        for argument, default in zip(function.args.kwonlyargs, function.args.kw_defaults):
            if isinstance(default, ast.Name) and default.id in registries:
                mapping[argument.arg] = default.id
        aliases[id(function)] = mapping
    return aliases


def _loop_registry(
    tree: ast.AST,
    loop: ast.For,
    registries: set[str],
    aliases: dict[int, dict[str, str]],
) -> str | None:
    if not isinstance(loop.iter, ast.Name):
        return None
    if loop.iter.id in registries:
        return loop.iter.id
    for function in _function_nodes(tree):
        if any(child is loop for child in ast.walk(function)):
            return aliases[id(function)].get(loop.iter.id)
    return None


def _runpy_lookup_matches(tree: ast.AST, *, producer: Path, symbol: str, consumer: Path) -> bool:
    if consumer.parent != producer.parent:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript) or not isinstance(node.slice, ast.Constant):
            continue
        call = node.value
        target = call.func if isinstance(call, ast.Call) else None
        if (
            node.slice.value == symbol
            and isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "runpy"
            and target.attr == "run_path"
            and call.args
            and _sibling_path_matches(call.args[0], producer.name)
        ):
            return True
    return False


def _registry_lookup_matches(tree: ast.AST, *, producer: Path, symbol: str) -> bool:
    registry_fields: dict[str, set[str]] = {}
    for assignment in (node for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.AnnAssign))):
        targets = assignment.targets if isinstance(assignment, ast.Assign) else [assignment.target]
        names = [target.id for target in targets if isinstance(target, ast.Name) and target.id.isupper()]
        if not names or not isinstance(assignment.value, (ast.Tuple, ast.List)):
            continue
        fields: set[str] = set()
        for call in (element for element in assignment.value.elts if isinstance(element, ast.Call)):
            if not _intent_constructor(call):
                continue
            values = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg is not None}
            module = values.get("module")
            if not isinstance(module, ast.Constant) or module.value != producer.stem:
                continue
            fields.update(
                field
                for field, value in values.items()
                if field.endswith("_function") and isinstance(value, ast.Constant) and value.value == symbol
            )
        for name in names:
            registry_fields[name] = fields
    aliases = _function_default_registries(tree, set(registry_fields))
    for loop in (node for node in ast.walk(tree) if isinstance(node, ast.For) and isinstance(node.target, ast.Name)):
        registry = _loop_registry(tree, loop, set(registry_fields), aliases)
        registered_fields = registry_fields.get(registry or "", set())
        if not registered_fields:
            continue
        intent_name = loop.target.id
        assignments = {
            target.id
            for node in ast.walk(loop)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and _module_loader(node.value)
            and node.value.args
            and isinstance(node.value.args[0], ast.Attribute)
            and isinstance(node.value.args[0].value, ast.Name)
            and node.value.args[0].value.id == intent_name
            and node.value.args[0].attr == "module"
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in assignments
            and isinstance(node.args[1], ast.Attribute)
            and isinstance(node.args[1].value, ast.Name)
            and node.args[1].value.id == intent_name
            and node.args[1].attr in registered_fields
            for node in ast.walk(loop)
        ):
            return True
    return False


def find_registered_dynamic_entrypoints(
    repo_root: Path,
    candidates: set[tuple[str, str]],
    scan_paths: list[str],
) -> set[tuple[str, str]]:
    """Return candidates backed by both a literal registration and its dispatcher."""
    if not candidates:
        return set()
    matched: set[tuple[str, str]] = set()
    unresolved = {(path, symbol): repo_root / path for path, symbol in candidates}
    for relative in scan_paths:
        consumer = repo_root / relative
        try:
            source = consumer.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relevant = [item for item in unresolved if item[1] in source]
        if not relevant:
            continue
        try:
            tree = ast.parse(source, filename=str(consumer))
        except SyntaxError:
            continue
        for item in relevant:
            producer = unresolved[item]
            if _runpy_lookup_matches(tree, producer=producer, symbol=item[1], consumer=consumer) or (
                consumer.parent == producer.parent
                and _registry_lookup_matches(tree, producer=producer, symbol=item[1])
            ):
                matched.add(item)
                unresolved.pop(item)
        if not unresolved:
            break
    return matched
