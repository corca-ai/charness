#!/usr/bin/env python3
"""Refuse a child-process call outside `scripts/subprocess_guard.py`.

This repo has exactly one spawn primitive (#768). A production module that
calls `subprocess.run`, `Popen`, `check_output`, `check_call`, `call`,
`getoutput`, `getstatusoutput`, or `os.system` / `os.popen` directly has
opted out of the guard's timeout-as-result, session-group kill, and heartbeat
contract, and the opt-out is invisible until an operator sits in front of a
silent 30-minute child. The form check makes the opt-out a red line instead.

Test files are not scanned: a test that crosses a real process boundary
declares it with the `boundary_contract` marker, which is the test-side rule.
An empty matched universe is a refusal (S40), never a pass.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

DEFAULT_SCAN_GLOBS = (
    "scripts/*.py",
    "scripts/**/*.py",
    "skills/public/*/scripts/*.py",
    "skills/public/*/scripts/**/*.py",
    "skills/support/*/scripts/*.py",
    "skills/support/*/scripts/**/*.py",
    "skills/shared/scripts/*.py",
    "skills/shared/scripts/**/*.py",
)
GUARD_RELATIVE = "scripts/subprocess_guard.py"
SKIP_PATH_PARTS = {"__pycache__", "vendor", "generated"}
SUBPROCESS_SPAWNS = frozenset(
    {"run", "Popen", "check_output", "check_call", "call", "getoutput", "getstatusoutput"}
)
OS_SPAWNS = frozenset({"system", "popen", "spawnl", "spawnv", "spawnlp", "spawnvp"})


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def _direct_spawn_findings(tree: ast.AST) -> list[tuple[int, str]]:
    """Return (line, form) for every direct spawn in one module."""
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                if alias.name in SUBPROCESS_SPAWNS:
                    imported_names.add(alias.asname or alias.name)
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _dotted(node.func)
        head, _, tail = name.rpartition(".")
        if head == "subprocess" and tail in SUBPROCESS_SPAWNS:
            findings.append((node.lineno, name))
        elif head == "os" and tail in OS_SPAWNS:
            findings.append((node.lineno, name))
        elif not head and name in imported_names:
            findings.append((node.lineno, f"subprocess.{name} (imported name)"))
    return findings


def _iter_scan_paths(repo_root: Path, *, require_git: bool) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return [path for path in paths if not (set(path.parts) & SKIP_PATH_PARTS)]


def check_file(repo_root: Path, path: Path) -> list[str]:
    relative = path.relative_to(repo_root).as_posix()
    if relative == GUARD_RELATIVE:
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [f"{relative}: cannot parse: {exc}"]
    return [
        f"{relative}:{line}: `{form}` spawns outside scripts/subprocess_guard.py; "
        "use run_process (short probe) or run_monitored_phase (long phase)"
        for line, form in _direct_spawn_findings(tree)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    scan_paths = _iter_scan_paths(repo_root, require_git=args.require_git_file_listing)
    if not scan_paths:
        raise SystemExit(
            "refusing empty matched universe for check_subprocess_form "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    failures: list[str] = []
    for path in scan_paths:
        failures.extend(check_file(repo_root, path))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(
        f"Validated subprocess form: {len(scan_paths)} production file(s) spawn only through the guard."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
