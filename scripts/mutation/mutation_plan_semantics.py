"""Validate mutation plan edits and classify deleted call sites."""

from __future__ import annotations

import ast
from collections import Counter


class MutationPlanError(Exception):
    """The requested textual edit cannot identify one attributable mutation."""


def mutation_bytes(original: bytes, find: str, replace: str) -> bytes:
    """Return the exact bytes a valid one-occurrence mutation would write."""
    if find == replace:
        raise MutationPlanError(
            "mutation text equals its replacement; a no-op mutant can only ever be "
            "reported SURVIVED, which is a verdict about code that was never changed"
        )
    text = original.decode("utf-8")
    occurrences = text.count(find)
    if occurrences == 0:
        raise MutationPlanError(
            "mutation text not found; the mutant would be a no-op reported as killed"
        )
    if occurrences > 1:
        raise MutationPlanError(
            f"mutation text occurs {occurrences} times; an ambiguous edit produces a kill "
            "nobody can attribute to a line"
        )
    return text.replace(find, replace, 1).encode("utf-8")


def _called_names(source: bytes) -> Counter[str] | None:
    """Every call expression in source, by callee name, or None if unparseable."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    names: Counter[str] = Counter()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names[func.id] += 1
        elif isinstance(func, ast.Attribute):
            names[func.attr] += 1
        else:
            names["<computed>"] += 1
    return names


def removed_calls(original: bytes, mutated: bytes) -> tuple[str, ...] | None:
    """Return callees the mutation deleted, or None when either side will not parse.

    Attribute calls are keyed by attribute, and computed callees are bucketed,
    so spelling changes do not manufacture removals and dispatch-table calls do
    not disappear from the evidence.
    """
    before, after = _called_names(original), _called_names(mutated)
    if before is None or after is None:
        return None
    return tuple(sorted((before - after).elements()))
