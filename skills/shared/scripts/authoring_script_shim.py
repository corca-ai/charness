#!/usr/bin/env python3
"""Reach an authoring-repo script from a path that resolves in BOTH layouts.

A repo-level script lives at `<repo>/scripts/X.py` in the authoring tree and at
`<plugin-root>/scripts/X.py` once exported. Those sit at DIFFERENT depths from a
skill package — three levels up versus two — so no single `$SKILL_DIR/../../../`
count reaches it in both. #477 was exactly that: a command correct here and
broken in every installed plugin, silently.

`$SKILL_DIR/../../shared/scripts/` is the one prefix at equal depth in both
layouts, because the exporter flattens `skills/<kind>/<skill>` to
`skills/<skill>` and the package-to-tier-root distance is the same either way.
So a thin shim here is reachable by one spelling, and the layout ambiguity is
resolved ONCE in code with tests instead of once per call site in prose.

This module is the shared half. Each shim is a few lines naming its target, so
adding one does not copy this resolution logic again.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def locate(name: str, caller: Path) -> Path:
    """The nearest ancestor's ``scripts/<name>``, never the caller itself.

    Walking up from the CALLER lands on `<repo>/scripts/` in the authoring tree
    and `<plugin-root>/scripts/` in the shipped one without either depth being
    hard-coded. The self-skip is load-bearing: a shim named `X.py` living in
    `skills/shared/scripts/` is itself an `<ancestor>/scripts/X.py`, so an
    unguarded walk finds itself and recurses until the interpreter dies.
    """
    origin = caller.resolve()
    for ancestor in origin.parents:
        candidate = ancestor / "scripts" / name
        if candidate.is_file() and candidate.resolve() != origin:
            return candidate
    raise FileNotFoundError(
        f"no ancestor of {origin} contains scripts/{name}; "
        "this shim must ship alongside the authoring-repo script it fronts"
    )


def load(script_path: Path) -> ModuleType:
    """Import the target with its OWN directory importable.

    Repo scripts use bare `from yaml_output import ...` / `from runtime_bootstrap
    import ...`, which only resolve when their own directory is on `sys.path`.
    Running one directly gets that for free; loading it from here does not.
    """
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location(f"{script_path.stem}_entrypoint", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(name: str, caller: str) -> int:
    """Locate, load, and delegate to the target's own ``main()``.

    The target's `__main__` guard stays false, so its exit code comes back as a
    return value rather than a `SystemExit` raised through this frame.
    """
    return load(locate(name, Path(caller))).main()
