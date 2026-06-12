#!/usr/bin/env python3
"""Consistency gate for the per-file skill-runtime bootstrap shim.

The `_load_skill_runtime_bootstrap` helper is intentionally duplicated in every
skill script so each one stays runnable from a source checkout, an installed
plugin cache, or a split support tree (see
skills/shared/references/bootstrap-resolution.md). The duplication is the
portability contract; this gate machine-owns what was previously maintained by
hand: every copy must stay byte-identical to the canonical block below.

`--fix` rewrites drifted module-level copies in place. After fixing exported
skill scripts, re-run `python3 scripts/sync_root_plugin_manifests.py
--repo-root .` so the plugin mirror follows.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

try:
    from scripts.repo_file_listing import iter_matching_repo_files
except ModuleNotFoundError:
    from repo_file_listing import iter_matching_repo_files

SHIM_NAME = "_load_skill_runtime_bootstrap"
CANONICAL_SHIM = '''def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))'''
SCAN_PATTERNS = ("skills/**/*.py", "scripts/**/*.py")


def _shim_nodes(source: str) -> list[ast.FunctionDef]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == SHIM_NAME
    ]


def find_shim_files(repo_root: Path, *, require_git: bool = False) -> dict[Path, list[ast.FunctionDef]]:
    files: dict[Path, list[ast.FunctionDef]] = {}
    for path in iter_matching_repo_files(repo_root, SCAN_PATTERNS, require_git=require_git):
        source = path.read_text(encoding="utf-8")
        if f"def {SHIM_NAME}(" not in source:
            continue
        nodes = _shim_nodes(source)
        if nodes:
            files[path] = nodes
    return files


def drifted_copies(source: str, nodes: list[ast.FunctionDef]) -> list[ast.FunctionDef]:
    return [
        node
        for node in nodes
        if ast.get_source_segment(source, node) != CANONICAL_SHIM
    ]


def fix_file(path: Path, source: str, nodes: list[ast.FunctionDef]) -> bool:
    fixable = [node for node in drifted_copies(source, nodes) if node.col_offset == 0]
    if not fixable:
        return False
    lines = source.splitlines(keepends=True)
    for node in sorted(fixable, key=lambda n: n.lineno, reverse=True):
        end = node.end_lineno if node.end_lineno is not None else node.lineno
        lines[node.lineno - 1 : end] = [CANONICAL_SHIM + "\n"]
    path.write_text("".join(lines), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--fix", action="store_true", help="rewrite drifted module-level copies to the canonical block")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    shim_files = find_shim_files(repo_root, require_git=args.require_git_file_listing)
    drifted: list[str] = []
    fixed: list[str] = []
    unfixable: list[str] = []
    for path, nodes in sorted(shim_files.items()):
        source = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        if not drifted_copies(source, nodes):
            continue
        if args.fix:
            if fix_file(path, source, nodes):
                fixed.append(rel)
            new_source = path.read_text(encoding="utf-8")
            if drifted_copies(new_source, _shim_nodes(new_source)):
                unfixable.append(rel)
        else:
            drifted.append(rel)

    status = "ok" if not drifted and not unfixable else "drift"
    if args.json:
        print(
            json.dumps(
                {
                    "status": status,
                    "checked_files": len(shim_files),
                    "drifted": drifted,
                    "fixed": fixed,
                    "unfixable": unfixable,
                },
                indent=2,
            )
        )
    elif status == "ok":
        note = f"; rewrote {len(fixed)}" if fixed else ""
        print(f"bootstrap-shim consistency: {len(shim_files)} copies match the canonical block{note}")
    else:
        print(f"FAIL: {len(drifted) + len(unfixable)} bootstrap shim copy(ies) drift from the canonical block:", file=sys.stderr)
        for rel in drifted + unfixable:
            print(f"- {rel}", file=sys.stderr)
        print("Run: python3 scripts/check_bootstrap_shim_consistency.py --repo-root . --fix", file=sys.stderr)
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
