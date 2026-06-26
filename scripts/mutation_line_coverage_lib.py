"""Shared coverage classification for Cosmic Ray mutation locations."""

from __future__ import annotations

import ast
from pathlib import Path


def statement_nodes(path: Path) -> list[ast.stmt]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [node for node in ast.walk(tree) if isinstance(node, ast.stmt)]


def executable_statement_lines(path: Path) -> set[int]:
    lines: set[int] = set()
    for node in statement_nodes(path):
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant) and isinstance(node.value.value, str):
            continue
        lines.add(int(node.lineno))
    return lines


def covered_statement_spans(path: Path, covered: set[int]) -> list[tuple[int, int]]:
    try:
        statements = statement_nodes(path)
    except (OSError, SyntaxError):
        return []
    spans: list[tuple[int, int]] = []
    for node in statements:
        start = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)
        if start is None:
            continue  # pragma: no cover - ast.stmt nodes have line numbers on supported Python.
        if end is None:
            continue  # pragma: no cover - ast.stmt nodes have end line numbers on supported Python.
        if start == end:
            continue
        span_end = int(end)
        if (suite_start := child_statement_suite_start(node)) is not None:
            span_end = min(span_end, suite_start - 1)
        start = int(start)
        if span_end <= start:
            continue
        if any(start <= line <= span_end for line in covered):
            spans.append((start, span_end))
    return spans


def child_statement_suite_start(node: ast.stmt) -> int | None:
    starts: list[int] = []
    for field in ("body", "orelse", "finalbody", "handlers", "cases"):
        for item in getattr(node, field, None) or []:
            if isinstance(item, (ast.stmt, ast.ExceptHandler)):
                starts.append(item.lineno)
            elif isinstance(item, ast.match_case):
                starts.extend(child.lineno for child in item.body if isinstance(child, ast.stmt))
    return min(starts, default=None)


def mutation_line_is_covered(line_number: int, covered: set[int], spans: list[tuple[int, int]]) -> bool:
    if line_number in covered:
        return True
    return any(start <= line_number <= end for start, end in spans)
