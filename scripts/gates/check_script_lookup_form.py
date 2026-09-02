#!/usr/bin/env python3
"""Refuse a by-name search for a repo script outside `scripts/core/repo_layout.py`.

Since the concept packaging (#770) a repo script is flat or packaged, and the
question "where does `<name>.py` live now" has ONE answer, the layout resolver.
Before it existed, the answer was re-derived in six places with a `glob` or an
`rglob` under `scripts/`, each with its own fallback, and a rename sweep with
nothing to ask rewrote five non-repo strings by regex (#777). This form check
makes a seventh lookup a red line.

The rule is structural: a `.glob(...)` or `.rglob(...)` call whose receiver
names a `scripts` tree and whose pattern is a NAME rather than an enumeration.
A name is an f-string (`f"*/{script}"`), a variable (`rglob(real_name)`), or a
constant with no wildcard (`glob("yaml_output.py")`). Enumerations such as
`rglob("*.py")` or `glob("*")` walk the tree without asking where one script
is, and stay allowed. Tests are scanned too: three of the six lookups lived
there. An empty matched universe is a refusal (S40), never a pass.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_repo_file_listing_module = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

DEFAULT_SCAN_GLOBS = (
    "scripts/*.py",
    "scripts/**/*.py",
    "tools/*.py",
    "tools/**/*.py",
    "skills/public/*/scripts/*.py",
    "skills/public/*/scripts/**/*.py",
    "skills/support/*/scripts/*.py",
    "skills/support/*/scripts/**/*.py",
    "skills/shared/scripts/*.py",
    "skills/shared/scripts/**/*.py",
    "tests/*.py",
    "tests/**/*.py",
)
RESOLVER_RELATIVE = "scripts/core/repo_layout.py"
SKIP_PATH_PARTS = {"__pycache__", "vendor", "generated"}
SEARCH_CALLS = frozenset({"glob", "rglob"})
WILDCARDS = ("*", "?", "[")


def _is_name_pattern(node: ast.AST) -> bool:
    """A pattern that names one script rather than enumerating a tree."""
    if isinstance(node, ast.JoinedStr):
        return True
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return not any(mark in node.value for mark in WILDCARDS)
    return isinstance(node, (ast.Name, ast.Attribute))


def _lookup_findings(source: str, tree: ast.AST) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in SEARCH_CALLS or not node.args:
            continue
        receiver = ast.get_source_segment(source, node.func.value) or ""
        if "scripts" not in receiver.lower():
            continue
        if _is_name_pattern(node.args[0]):
            findings.append((node.lineno, ast.get_source_segment(source, node) or node.func.attr))
    return findings


def _iter_scan_paths(repo_root: Path, *, require_git: bool) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return [path for path in paths if not (set(path.parts) & SKIP_PATH_PARTS)]


def check_file(repo_root: Path, path: Path) -> list[str]:
    relative = path.relative_to(repo_root).as_posix()
    if relative == RESOLVER_RELATIVE:
        return []
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [f"{relative}: cannot parse: {exc}"]
    return [
        f"{relative}:{line}: `{form}` searches scripts/ for a script by name outside "
        f"{RESOLVER_RELATIVE}; ask repo_script or find_repo_script instead"
        for line, form in _lookup_findings(source, tree)
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
            "refusing empty matched universe for check_script_lookup_form "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    failures: list[str] = []
    for path in scan_paths:
        failures.extend(check_file(repo_root, path))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"Validated script lookup form: {len(scan_paths)} file(s) ask only the layout resolver.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
