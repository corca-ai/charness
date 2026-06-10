#!/usr/bin/env python3
"""Advisory (#328) slice-closeout helpers.

Surface likely-broken doc/SKILL test pins and the one-shot skill-surface
preflight BEFORE the broad pytest / mutation-coverage producer pays for the
failure. These never block closeout; they print ``WARN``/``ADVISORY`` lines to
stderr so the fix happens before the expensive cycle, not at minute six of the
broad suite.
"""
from __future__ import annotations

import subprocess
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


def _added_vs_base(repo_root: Path, paths: list[str], base: str = "origin/main") -> list[str]:
    """Paths absent from the base tree — the changed-line gate's range anchor.
    Degrades to no advisory when the anchor ref does not resolve (tmp repos).
    Checks `base:<path>` directly rather than merge-base(base, HEAD): a file
    deleted upstream but present at the merge-base reads as "added" and fires
    a spurious stderr-only advisory — accepted over the extra plumbing."""
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base],
        cwd=repo_root,
        capture_output=True,
    )
    if probe.returncode != 0:
        return []
    added: list[str] = []
    for path in paths:
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{base}:{path}"],
            cwd=repo_root,
            capture_output=True,
        )
        if exists.returncode != 0:
            added.append(path)
    return added


def advise_new_pool_module(repo_root: Path, changed_paths: list[str]) -> None:
    """A slice that ADDS a new mutation-pool module gets no commit-time signal
    that its environment-dependent branches (import fallbacks, dep-missing
    degrades) are uncovered; the first signal otherwise arrives at the bundle
    boundary, where repair costs a full instrumented producer re-run. Surface
    the documented early self-check (implementation-discipline.md) while the
    branch list is still cheap to walk."""
    changed_py = [path for path in changed_paths if path.endswith(".py")]
    if not changed_py:
        return
    sample = import_repo_module(__file__, "scripts.sample_mutation_files")
    eligible = set(sample.list_eligible(repo_root))
    new_pool = sorted(set(_added_vs_base(repo_root, changed_py)) & eligible)
    if not new_pool:
        return
    print(
        "ADVISORY: new mutation-pool module(s) added vs origin/main: "
        + ", ".join(new_pool)
        + "; walk each branch (import fallbacks, dep-missing degrades) into the "
        "introducing slice's tests, then run the early changed-line self-check "
        "(docs/conventions/implementation-discipline.md) so the bundle producer "
        "CONFIRMS instead of discovering: run the --produce-mutation-coverage "
        "closeout, then python3 scripts/check_changed_line_mutation_coverage.py "
        "--repo-root . --base-sha origin/main --reuse-coverage",
        file=sys.stderr,
    )


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
