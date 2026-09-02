#!/usr/bin/env python3
"""One way to name a path in operator output.

`Path.relative_to` raises for any path outside the root, so a validator that formats its
verdict with it dies with a traceback instead of rendering the verdict — a false RED, and
one that also blocks writing regression tests against fixtures outside the repo. Two
surfaces had independently grown the same three-line guard; this is that guard, once.
"""
from __future__ import annotations

from pathlib import Path


def display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative when the path is under ``repo_root``, absolute otherwise."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)
