#!/usr/bin/env python3
"""Consistency gate for the per-file skill-runtime bootstrap shim.

The `_load_skill_runtime_bootstrap` helper is intentionally duplicated in every
skill script so each one stays runnable from a source checkout, an installed
plugin cache, or a split support tree (see
skills/shared/references/bootstrap-resolution.md). The duplication is the
portability contract; this gate machine-owns what was previously maintained by
hand: every copy must stay byte-identical to the canonical block below.

`--fix` rewrites drifted module-level copies in place. After fixing exported
skill scripts, re-run `python3 scripts/plugin_export/sync_root_plugin_manifests.py
--repo-root .` so the plugin mirror follows.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import re
from pathlib import Path

try:
    from scripts.core.repo_file_listing import iter_matching_repo_files
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from scripts.core.repo_file_listing import iter_matching_repo_files
    from yaml_output import emit_yaml

SHIM_NAME = "_load_skill_runtime_bootstrap"
CANONICAL_SHIM = """def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))"""
REPO_SHIM_NAME = "_load_repo_runtime_bootstrap"
CANONICAL_REPO_SHIM = """def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))"""
SCAN_PATTERNS = ("skills/**/*.py", "scripts/**/*.py", "tools/**/*.py")
# Every repo script that imports runtime_bootstrap or yaml_output carries the
# root-walking shim: nested scripts need it for their own package, and the flat
# residue needs it because the siblings it imports now live in packages.
REPO_SHIM_SCAN_PATTERN = ("scripts/**/*.py",)
REPO_SHIM_TRIGGER = re.compile(
    r"^\s*(?:from scripts(?:\.|\s+import)|import scripts(?:\.|\s))", re.MULTILINE
)


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


def find_shim_files(
    repo_root: Path, *, require_git: bool = False
) -> dict[Path, list[ast.FunctionDef]]:
    files: dict[Path, list[ast.FunctionDef]] = {}
    for path in iter_matching_repo_files(repo_root, SCAN_PATTERNS, require_git=require_git):
        source = path.read_text(encoding="utf-8")
        if f"def {SHIM_NAME}(" not in source:
            continue
        nodes = _shim_nodes(source)
        if nodes:
            files[path] = nodes
    return files


def _repo_shim_nodes(source: str) -> list[ast.FunctionDef]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == REPO_SHIM_NAME
    ]


def find_repo_shim_files(
    repo_root: Path, *, require_git: bool = False
) -> dict[Path, list[ast.FunctionDef]]:
    files: dict[Path, list[ast.FunctionDef]] = {}
    for path in iter_matching_repo_files(
        repo_root, REPO_SHIM_SCAN_PATTERN, require_git=require_git
    ):
        source = path.read_text(encoding="utf-8")
        if REPO_SHIM_TRIGGER.search(source):
            files[path] = _repo_shim_nodes(source)
    return files


def drifted_copies(source: str, nodes: list[ast.FunctionDef]) -> list[ast.FunctionDef]:
    return [node for node in nodes if ast.get_source_segment(source, node) != CANONICAL_SHIM]


def _shim_required_names() -> set[str]:
    """Module-level names the canonical shim's body loads and does not bind itself.

    DERIVED from `CANONICAL_SHIM`, never listed: the fixer has to guarantee
    whatever the canonical block references *today*, and a hand-kept list goes
    stale the moment someone takes this gate's own documented "edit CANONICAL_SHIM
    first, then --fix to propagate" path.
    """
    return _required_names(CANONICAL_SHIM)


def _repo_shim_required_names() -> set[str]:
    return _required_names(CANONICAL_REPO_SHIM)


def _required_names(canonical: str) -> set[str]:
    function = ast.parse(canonical).body[0]
    stored = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    loaded = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    # `__file__` and friends are module globals the interpreter always provides;
    # builtins need no import. What remains is what the module must supply.
    return {
        name
        for name in loaded - stored
        if not name.startswith("__") and not hasattr(builtins, name)
    }


def _module_level_names(source: str) -> set[str]:
    """Names bound where a module-level `def` can see them.

    Descends into module-level `try`/`if`/`with` because the conditional-import
    idiom (`try: from scripts.x import y / except ModuleNotFoundError: from x
    import y`) is this repo's normal shape. It deliberately does NOT descend into
    a `def` or `class`: an import nested in another function is invisible to the
    shim, which is the whole failure this predicate exists to catch.
    """
    names: set[str] = set()

    def visit(body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                names.update(t.id for t in node.targets if isinstance(t, ast.Name))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
            elif isinstance(node, ast.Try):
                visit(node.body)
                for handler in node.handlers:
                    visit(handler.body)
                visit(node.orelse)
                visit(node.finalbody)
            elif isinstance(node, (ast.If, ast.With)):
                visit(node.body)
                visit(getattr(node, "orelse", []))

    visit(ast.parse(source).body)
    return names


def missing_shim_dependencies(source: str, canonical: str = CANONICAL_SHIM) -> list[str]:
    """Canonical-shim names `source` never binds, so the spliced block would crash."""
    return sorted(_required_names(canonical) - _module_level_names(source))


def repo_shim_drift(source: str, nodes: list[ast.FunctionDef]) -> bool:
    return not nodes or any(
        ast.get_source_segment(source, node) != CANONICAL_REPO_SHIM for node in nodes
    )


def fix_file(path: Path, source: str, nodes: list[ast.FunctionDef]) -> bool:
    fixable = [node for node in drifted_copies(source, nodes) if node.col_offset == 0]
    if not fixable:
        return False
    # Split on real newlines only: ast line numbers count "\n", while
    # str.splitlines also splits on form feeds and unicode separators, which
    # would shift the splice window and corrupt the file.
    lines = source.split("\n")
    for node in sorted(fixable, key=lambda n: n.lineno, reverse=True):
        end = node.end_lineno if node.end_lineno is not None else node.lineno
        lines[node.lineno - 1 : end] = CANONICAL_SHIM.split("\n")
    fixed_source = "\n".join(lines)
    # A drifted copy is often drifted BECAUSE it works around a missing import --
    # `__import__("runpy").run_path(...)` in a module that never imports runpy.
    # Splicing the canonical block over it produced a file that raised NameError on
    # import, and the post-fix check saw a syntactically perfect canonical shim and
    # called it fixed. Writing a broken file is strictly worse than declining, so
    # this refuses and leaves the drift for a human to resolve.
    if missing_shim_dependencies(fixed_source):
        return False
    path.write_text(fixed_source, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrite drifted module-level copies to the canonical block",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    shim_files = find_shim_files(repo_root, require_git=args.require_git_file_listing)
    repo_shim_files = find_repo_shim_files(repo_root, require_git=args.require_git_file_listing)
    drifted: list[str] = []
    fixed: list[str] = []
    unfixable: list[str] = []
    unfixable_reasons: dict[str, str] = {}
    repo_drifted: list[str] = []
    repo_missing_dependencies: dict[str, list[str]] = {}
    for path, nodes in sorted(shim_files.items()):
        source = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        if not drifted_copies(source, nodes):
            continue
        if args.fix:
            if fix_file(path, source, nodes):
                fixed.append(rel)
            new_source = path.read_text(encoding="utf-8")
            new_nodes = _shim_nodes(new_source)
            # A file that had shim defs before --fix and parses to none after
            # is corrupted, not clean; never report that as fixed.
            if not new_nodes or drifted_copies(new_source, new_nodes):
                unfixable.append(rel)
                if rel in fixed:
                    fixed.remove(rel)
                # An `unfixable` path with no stated cause is a problem nobody can
                # act on -- the same shape the empty-scope remedy below exists to
                # avoid. The missing-import case is the one this gate can name.
                if missing := missing_shim_dependencies(new_source):
                    unfixable_reasons[rel] = (
                        f"the canonical shim needs {', '.join(missing)} at module level, and "
                        f"{rel} does not import {'them' if len(missing) > 1 else 'it'}; add the "
                        "import, then re-run --fix"
                    )
        else:
            drifted.append(rel)

    for path, nodes in sorted(repo_shim_files.items()):
        source = path.read_text(encoding="utf-8")
        if not repo_shim_drift(source, nodes):
            missing = missing_shim_dependencies(source, CANONICAL_REPO_SHIM)
            if missing:
                repo_missing_dependencies[path.relative_to(repo_root).as_posix()] = missing
            if not missing:
                continue
        repo_drifted.append(path.relative_to(repo_root).as_posix())
    # A scan that found no shim copies established no scope: it cannot distinguish
    # "every copy matches" from "the root is wrong / the listing came back empty".
    # Report it as its own state so a green line never stands for zero comparisons.
    status = (
        "empty-scope"
        if not shim_files and not repo_shim_files
        else ("ok" if not drifted and not unfixable and not repo_drifted else "drift")
    )
    payload: dict[str, object] = {
        "status": status,
        "scanned_repo_root": str(repo_root),
        "checked_files": len(shim_files),
        "drifted": drifted,
        "fixed": fixed,
        "unfixable": unfixable,
        "unfixable_reasons": unfixable_reasons,
        "repo_checked_files": len(repo_shim_files),
        "repo_drifted": repo_drifted,
        "repo_missing_dependencies": repo_missing_dependencies,
    }
    # Output is unconditionally YAML, so the remedies have to live in the payload.
    # Each of these existed only inside the human branches, and a non-ok status
    # that names no next step is a gate that reports a problem nobody can act on.
    if status == "empty-scope":
        payload["remedies"] = [
            "Nothing was compared: this is not a passing comparison. Check --repo-root "
            "(and --require-git-file-listing if the listing came back empty).",
        ]
    elif status == "drift":
        payload["remedies"] = [
            "Run: python3 -m tools.check_bootstrap_shim_consistency --repo-root . --fix",
            "To evolve the shim deliberately, edit CANONICAL_SHIM in this gate first, then --fix to propagate.",
        ]
        if repo_drifted:
            payload["remedies"].append(
                "Run: python3 -m tools.rewrite_script_preambles --repo-root ."
            )
    emit_yaml(payload)
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
