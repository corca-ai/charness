#!/usr/bin/env python3
"""One owner for "resolve an adjacent script as a module".

Three copies of this existed, with three different answers. Two load the sibling
by path unconditionally; the third -- kept here -- prefers an already-loaded
canonical module when it IS the sibling, and only then falls back to a by-path
load. Its docstring records why that order is load-bearing, and both defects it
names were found in this repo: one by a fresh-eye review, one by the full suite.

A restated loader is the same hazard as any other restated contract. The other
copies are not migrated in this commit -- they run inside git hooks, where a
load-order change is not something to ship alongside a release -- but they are
now duplicates OF a named owner rather than three peers, which is what makes
retiring them a bounded follow-up instead of an archaeology exercise.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


def load_sibling(module_stem: str):
    """Resolve an adjacent owner independently of consumer package state.

    Order is load-bearing: preferring the package import would let any
    already-importable module of that name win, and falling back to a by-path
    load whenever the canonical name is unbound would make the object depend on
    who imported first. Both were real defects here, one found by a fresh-eye
    review and one by the full suite.
    """
    sibling = Path(__file__).resolve().with_name(f"{module_stem}.py")
    canonical = f"scripts.{module_stem}"
    loaded = sys.modules.get(canonical)
    loaded_file = getattr(loaded, "__file__", None)
    if loaded_file is not None and Path(loaded_file).resolve() == sibling:
        return loaded
    if sibling.is_file():
        try:
            spec = importlib.util.find_spec(canonical)
        except (ImportError, ValueError):
            spec = None
        if spec is not None and spec.origin and Path(spec.origin).resolve() == sibling:
            return importlib.import_module(canonical)
        spec = importlib.util.spec_from_file_location(f"charness_{module_stem}", sibling)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    return importlib.import_module(canonical)
