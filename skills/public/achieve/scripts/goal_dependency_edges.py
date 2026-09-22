"""Dependency edge kinds shared by Goal Binding freeze and Goal Run pickup.

An edge is ``hard`` (blocks start; the default that preserves legacy
semantics), ``soft`` (shared paths or merge-conflict risk that the operator
may trade for speed), or ``integration-gate`` (blocks integration, not
start). Only hard edges gate readiness, cycles, and rank order. The ready
frontier is derived, never stored.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

EDGE_KINDS = frozenset({"hard", "soft", "integration-gate"})
_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def kind_of(item: Mapping[str, Any], dependency: str) -> str:
    """Edge kind for one dependency; absent means ``hard``."""
    kinds = item.get("dependency_kinds")
    if not isinstance(kinds, dict):
        return "hard"
    kind = kinds.get(dependency, "hard")
    return kind if isinstance(kind, str) else "hard"


def hard_dependencies(item: Mapping[str, Any]) -> list[str]:
    """Dependencies that gate start; ``soft`` and ``integration-gate`` never do."""
    return [dep for dep in item.get("dependencies", []) if kind_of(item, dep) == "hard"]


def ready_frontier(
    items: list[Mapping[str, Any]], closed_keys: set[str] | frozenset[str]
) -> list[str]:
    """Keys whose hard dependencies are all closed (derived, never stored)."""
    closed = set(closed_keys)
    return sorted(
        item["key"]
        for item in items
        if isinstance(item.get("key"), str) and set(hard_dependencies(item)) <= closed
    )


def validate_edge_kinds(
    kinds: Any, dependencies: list[str], *, context: str, error: Any, code: str
) -> None:
    """Shared shape check; ``error`` is a ``(code, message)`` exception factory."""
    if kinds is None:
        return
    if not isinstance(kinds, dict) or any(
        not isinstance(dep, str) or not _KEY_RE.fullmatch(dep) for dep in kinds
    ):
        raise error(code, f"{context} dependency_kinds are invalid")
    unknown = sorted(set(kinds) - set(dependencies))
    if unknown:
        raise error(code, f"{context} kinds name unknown dependencies")
    bad = sorted({kind for kind in kinds.values() if kind not in EDGE_KINDS})
    if bad:
        raise error(code, f"{context} has unknown edge kinds {bad!r}")
