#!/usr/bin/env python3
"""Refuse a raw `sys.modules` eviction in `tests/`: go through `tests/module_eviction.py`.

`monkeypatch.delitem(sys.modules, "scripts.core.x")` restores the `sys.modules`
entry at teardown and nothing else. While the entry is gone the first import
binds a NEW module object and rebinds the parent package's attribute
`scripts.core.x` to it; teardown puts the old object back in `sys.modules` and
leaves the attribute pointing at the new one. From then on, in that worker,
`from scripts.core import x` and `import scripts.core.x` name two different
modules, so a later test that patches one and calls through the other patches
nothing. Whether it fails depends only on which tests the xdist worker ran
first -- the lesson `collection-time-pollution`. That is not theory: the #780
push was refused by exactly this, when `test_batch8`'s eviction happened to run
before `test_git_inventory_discovery` in the same worker.

`tests/module_eviction.py` owns the safe form. `evict_module` pins the parent
attribute for restoration alongside the entry; `evict_new_modules` unbinds what
a by-path load pulled in, parent attributes included. #781 folded the last raw
site onto them, so the baseline record ships EMPTY: any site is a new one.

What is deliberately outside the rule: `monkeypatch.setitem(sys.modules, ...)`,
which ADDS a throwaway name and lets pytest delete it again, is not an eviction
and is not a site; neither is reading `sys.modules`, nor `sys.modules.pop`
inside `tests/module_eviction.py` itself, which is the owner. Files under a
`fixtures` directory are executed as children, not collected as tests, and are
not scanned. An empty matched universe is a refusal (S40), never a pass.

The record format is kept identical to `check_wall_clock_form.py` so the gate
can only ever be loosened by a named, reviewed entry: a file above its recorded
count is red, a file below it is a prompt to lower the record, and
`--write-baseline` refuses to raise any count.
"""

from __future__ import annotations

import argparse
import ast
import json
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

DEFAULT_SCAN_GLOBS = ("tests/*.py", "tests/**/*.py")
DEFAULT_BASELINE_REL = "charness-artifacts/quality/module-eviction-baseline.json"
SKIP_PATH_PARTS = {"__pycache__", "fixtures"}
OWNER_REL = "tests/module_eviction.py"
BASELINE_SCHEMA = "charness.module-eviction-baseline/v1"


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def eviction_sites(source: str, filename: str) -> list[tuple[int, str]]:
    """Every raw `sys.modules` eviction in one module: `(line, spelling)`.

    Three spellings, all resolved through `from sys import modules as m` too, so
    an alias is not a way around the rule: `<anything>.delitem(sys.modules, ...)`
    (the monkeypatch form), `sys.modules.pop(...)`, and `del sys.modules[...]`.
    A string literal that happens to contain one of them is a seeded child's
    body, not an eviction, and is not a site.
    """
    tree = ast.parse(source, filename=filename)
    aliases = {
        alias.asname or alias.name: "sys.modules"
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "sys"
        for alias in node.names
        if alias.name == "modules"
    }

    def is_sys_modules(node: ast.AST) -> bool:
        name = _dotted(node)
        return name == "sys.modules" or aliases.get(name) == "sys.modules"

    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Delete):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and is_sys_modules(target.value):
                    sites.append((node.lineno, "del sys.modules[...]"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "pop" and is_sys_modules(node.func.value):
                sites.append((node.lineno, "sys.modules.pop(...)"))
            elif node.func.attr == "delitem" and node.args and is_sys_modules(node.args[0]):
                sites.append((node.lineno, "delitem(sys.modules, ...)"))
    return sorted(sites)


def _iter_scan_paths(repo_root: Path, *, require_git: bool) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return [
        path
        for path in paths
        if not (set(path.parts) & SKIP_PATH_PARTS)
        and path.relative_to(repo_root).as_posix() != OWNER_REL
    ]


def measure(repo_root: Path, *, require_git: bool) -> tuple[dict[str, list[tuple[int, str]]], int]:
    """Per-file raw eviction sites for every scanned test file, plus the file count."""
    scan_paths = _iter_scan_paths(repo_root, require_git=require_git)
    found: dict[str, list[tuple[int, str]]] = {}
    for path in scan_paths:
        relative = path.relative_to(repo_root).as_posix()
        sites = eviction_sites(path.read_text(encoding="utf-8"), str(path))
        if sites:
            found[relative] = sites
    return found, len(scan_paths)


def load_baseline(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != BASELINE_SCHEMA:
        raise SystemExit(f"{path}: not a {BASELINE_SCHEMA} record")
    files = payload.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(k, str) and isinstance(v, int) and v > 0 for k, v in files.items()
    ):
        raise SystemExit(f"{path}: `files` must map test paths to positive site counts")
    return dict(files)


def judge(
    found: dict[str, list[tuple[int, str]]], baseline: dict[str, int]
) -> tuple[list[str], list[str]]:
    """`(failures, shrink_prompts)` for the measured tree against the record."""
    failures: list[str] = []
    prompts: list[str] = []
    for relative, sites in sorted(found.items()):
        allowed = baseline.get(relative, 0)
        if len(sites) > allowed:
            listed = ", ".join(f"{line} {name}" for line, name in sites)
            failures.append(
                f"{relative}: {len(sites)} raw sys.modules eviction(s), baseline {allowed} "
                f"(sites: {listed}); evict through tests/module_eviction.py "
                "(evict_module / evict_new_modules) so no parent package attribute is stranded"
            )
        elif len(sites) < allowed:
            prompts.append(f"{relative}: {len(sites)} < baseline {allowed}; lower the record")
    for relative, allowed in sorted(baseline.items()):
        if relative not in found:
            prompts.append(f"{relative}: 0 < baseline {allowed}; drop it from the record")
    return failures, prompts


def write_baseline(
    path: Path, found: dict[str, list[tuple[int, str]]], previous: dict[str, int]
) -> None:
    files = {relative: len(sites) for relative, sites in sorted(found.items())}
    raised = [rel for rel, count in files.items() if count > previous.get(rel, 0) and previous]
    if raised:
        raise SystemExit(
            "refusing to raise the module-eviction baseline for: " + ", ".join(raised) + "; "
            "the record only shrinks"
        )
    payload = {"schema": BASELINE_SCHEMA, "files": files, "total": sum(files.values())}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    baseline_path = args.baseline or (repo_root / DEFAULT_BASELINE_REL)
    found, scanned = measure(repo_root, require_git=args.require_git_file_listing)
    if not scanned:
        raise SystemExit(
            "refusing empty matched universe for check_module_eviction_form "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    previous = load_baseline(baseline_path)
    if args.write_baseline:
        write_baseline(baseline_path, found, previous)
        total = sum(len(sites) for sites in found.values())
        print(f"Wrote module-eviction baseline: {total} site(s) in {len(found)} file(s).")
        return 0
    failures, prompts = judge(found, previous)
    for prompt in prompts:
        print(f"ADVISORY: {prompt}", file=sys.stderr)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    total = sum(len(sites) for sites in found.values())
    print(
        f"Validated module-eviction form: {scanned} test file(s) scanned, {total} recorded "
        f"site(s) in {len(found)} file(s), none new."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
