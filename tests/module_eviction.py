"""Evict a module for one test WITHOUT leaving its parent package pointing elsewhere.

`monkeypatch.delitem(sys.modules, "scripts.core.x")` restores the `sys.modules`
entry at teardown and nothing else. While the entry is gone, the first import
binds a NEW module object and, through the import machinery, rebinds the parent
package's attribute `scripts.core.x` to it. Teardown puts the old object back
into `sys.modules` but the package attribute keeps the new one, so from then on
`from scripts.core import x` and `from scripts.core.x import Thing` name two
different modules in the same worker. A later test that patches one and calls
through the other patches nothing, and whether it fails depends on which tests
the xdist worker ran first (`collection-time-pollution`; the #779 push was
refused by exactly this in `test_git_inventory_discovery.py`).

This helper evicts the entry AND pins the parent attribute for restoration, so
the identity split cannot outlive the test that needed the eviction.
"""

from __future__ import annotations

import sys
from collections.abc import Set as AbstractSet

import pytest


def evict_module(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    parent_name, _, attribute = name.rpartition(".")
    parent = sys.modules.get(parent_name) if parent_name else None
    if parent is not None and hasattr(parent, attribute):
        # `raising=False` is deliberate: the attribute is restored to today's
        # object at teardown, whatever the evicted import rebinds it to.
        monkeypatch.setattr(parent, attribute, getattr(parent, attribute), raising=False)
    monkeypatch.delitem(sys.modules, name, raising=False)


def evict_new_modules(before: AbstractSet[str]) -> None:
    """Drop every module imported since `before` WITHOUT stranding a parent attribute.

    A test that loads a script by path, or re-imports one under a blocked
    `scripts` package, leaves whatever that import pulled in behind. Dropping
    only the `sys.modules` entries repeats the split `evict_module` exists to
    prevent, one level down: the import bound the new object on its parent
    package too, so `from scripts.core import x` would keep answering with a
    module that `import scripts.core.x` no longer has. Deepest name first, so a
    parent is still resolvable while its children are being unbound.
    """
    for name in sorted(set(sys.modules) - set(before), reverse=True):
        module = sys.modules.pop(name, None)
        parent_name, _, attribute = name.rpartition(".")
        parent = sys.modules.get(parent_name) if parent_name else None
        if parent is not None and getattr(parent, attribute, None) is module:
            delattr(parent, attribute)
