#!/usr/bin/env python3
"""Advisory (#328) slice-closeout helpers.

Surface likely-broken doc/SKILL test pins and the one-shot skill-surface
preflight BEFORE the broad pytest / mutation-coverage producer pays for the
failure. These never block closeout; they print ``WARN``/``ADVISORY`` lines to
stderr so the fix happens before the expensive cycle, not at minute six of the
broad suite.
"""
from __future__ import annotations

import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module


def advise_prose_pin(repo_root: Path, changed_paths: list[str]) -> None:
    """Point at tests/ assertions that pin doc/SKILL prose or paths the slice
    changed. Reads the working-tree diff directly; the substring/path match is a
    heuristic, so it stays advisory."""
    if not any(path.endswith(".md") for path in changed_paths):
        return
    lib = import_repo_module(__file__, "scripts.check_prose_pin")
    report = lib.build_report(repo_root, paths=None, test_roots=[repo_root / "tests"])
    if report["status"] == "findings":
        print(lib.format_human(report), file=sys.stderr)


def advise_skill_surface_preflight(repo_root: Path, changed_paths: list[str]) -> None:
    """When the slice edits a gated skill package, point at the one-shot
    portable-package preflight so the serial gate round-trips (ergonomics,
    ownership-overlap, attention-state, length headroom) surface in one pass
    instead of one commit-time gate failure at a time."""
    edited = [
        path
        for path in changed_paths
        if path.startswith(("skills/public/", "skills/support/"))
        and (path.endswith("/SKILL.md") or "/references/" in path)
    ]
    if not edited:
        return
    print(
        "ADVISORY: edited gated skill surface(s); run the one-shot portable-package "
        "preflight to surface all findings at once: "
        f"python3 scripts/check_skill_surface_preflight.py --path {edited[0]} --run-checks",
        file=sys.stderr,
    )
