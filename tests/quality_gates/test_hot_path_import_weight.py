"""Pin the deferred imports that keep hot CLI startups light.

Both deferrals were made from measurement, and both are the kind a later "tidy the
imports to the top" edit silently undoes: nothing fails, the gate just gets slower
again. `python3 -X importtime` is the source for the numbers in the comments.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# module path -> import roots that must NOT be imported at module scope
DEFERRED_IMPORTS = {
    # `urllib.request` pulls http.client + ssl + email.parser: 17ms of this CLI's
    # ~114ms startup, for one network path behind a fixture short-circuit.
    "charness": {"urllib"},
    # `jsonschema` (with `referencing`) was once a measurable startup cost for a
    # commit-boundary consumer; keep this map available for future measured deferrals.
}


def _module_scope_import_roots(source: str) -> set[str]:
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


@pytest.mark.parametrize(("relative_path", "forbidden"), sorted((k, tuple(sorted(v))) for k, v in DEFERRED_IMPORTS.items()))
def test_heavy_imports_stay_out_of_module_scope(relative_path: str, forbidden: tuple[str, ...]) -> None:
    path = ROOT / relative_path
    roots = _module_scope_import_roots(path.read_text(encoding="utf-8"))
    offenders = sorted(set(forbidden) & roots)
    assert not offenders, (
        f"{relative_path} imports {offenders} at module scope again; these were deferred "
        "into their call sites because every invocation of this entry point paid the cost. "
        "Import them inside the function that uses them."
    )


@pytest.mark.parametrize(("relative_path", "forbidden"), sorted((k, tuple(sorted(v))) for k, v in DEFERRED_IMPORTS.items()))
def test_deferred_imports_are_still_actually_used(relative_path: str, forbidden: tuple[str, ...]) -> None:
    """A deferral that no longer has a call site is a stale entry, not a win."""

    source = (ROOT / relative_path).read_text(encoding="utf-8")
    for root in forbidden:
        assert f"import {root}" in source, (
            f"{relative_path} no longer imports {root} anywhere; drop it from DEFERRED_IMPORTS "
            "instead of pinning an import that does not exist."
        )
