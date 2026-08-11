#!/usr/bin/env python3

from __future__ import annotations

import ast
from pathlib import Path


def _is_dataclass_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return getattr(target, "id", None) == "dataclass" or getattr(target, "attr", None) == "dataclass"


def _import_bindings(tree: ast.AST, module: str, name: str | None = None) -> set[str]:
    bindings: set[str] = set()
    for node in ast.walk(tree):
        if name is None and isinstance(node, ast.Import):
            bindings.update(alias.asname or alias.name for alias in node.names if alias.name == module)
        elif name is not None and isinstance(node, ast.ImportFrom) and node.module == module:
            bindings.update(alias.asname or alias.name for alias in node.names if alias.name == name)
    return bindings


def _is_bound_attribute(expression: ast.expr, bindings: set[str], attribute: str) -> bool:
    target = expression.func if isinstance(expression, ast.Call) else expression
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id in bindings
        and target.attr == attribute
    )


def _is_bound_name(expression: ast.expr, bindings: set[str]) -> bool:
    target = expression.func if isinstance(expression, ast.Call) else expression
    return isinstance(target, ast.Name) and target.id in bindings


def source_role_locations(path: Path) -> dict[str, set[tuple[int, str]]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {"dataclass_fields": set(), "pytest_fixtures": set(), "visitor_methods": set()}
    pytest_modules = _import_bindings(tree, "pytest")
    fixture_names = _import_bindings(tree, "pytest", "fixture")
    ast_modules = _import_bindings(tree, "ast")
    node_visitor_names = _import_bindings(tree, "ast", "NodeVisitor")
    dataclass_fields = {
        (statement.lineno, statement.target.id)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        and any(_is_dataclass_decorator(decorator) for decorator in class_node.decorator_list)
        for statement in class_node.body
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
    }
    fixture_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            _is_bound_attribute(decorator, pytest_modules, "fixture")
            or _is_bound_name(decorator, fixture_names)
            for decorator in node.decorator_list
        )
    ]
    pytest_fixtures = {
        (line, node.name)
        for node in fixture_nodes
        for line in {node.lineno, *(decorator.lineno for decorator in node.decorator_list)}
    }
    visitor_methods = {
        (method.lineno, method.name)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        and any(
            _is_bound_attribute(base, ast_modules, "NodeVisitor")
            or _is_bound_name(base, node_visitor_names)
            for base in class_node.bases
        )
        for method in class_node.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        and method.name.startswith("visit_")
    }
    return {
        "dataclass_fields": dataclass_fields,
        "pytest_fixtures": pytest_fixtures,
        "visitor_methods": visitor_methods,
    }
