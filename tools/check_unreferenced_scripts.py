#!/usr/bin/env python3
"""Report script files that have no live reader in the repository.

The graph is intentionally a conservative inventory: an uncertain reference is
kept rather than turning a valid helper into an orphan. ``--strict`` makes an
unreferenced node a blocking finding. The node roots are the source trees that
ship or run scripts; generated ``plugins/`` files are not nodes.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

from runtime_bootstrap import import_repo_module
from yaml_output import emit_yaml

_ROOT = Path(__file__).resolve().parents[1]
_LISTING = import_repo_module(__file__, "scripts.repo_file_listing")
_SKILL_REFS = import_repo_module(__file__, "tools.inventory_skill_script_references")
_EXPORT = import_repo_module(__file__, "tools.export_self_sufficiency_lib")

NODE_GLOBS = (
    "scripts/**",
    "tools/**",
    "skills/public/*/scripts/**",
    "skills/support/*/scripts/**",
    "skills/shared/scripts/**",
)
_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])((?:scripts|tools|skills)/[A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|txt))(?![A-Za-z0-9_./-])"
)
_MODULE_RE = re.compile(r"^(scripts|tools)\.([A-Za-z0-9_]+)$")
_SURFACE_PREFIXES = (
    ".agents/",
    ".claude/",
    "docs/",
    "presets/",
    "profiles/",
    "integrations/",
    "packaging/",
)
_ABS_INDEXES: dict[int, dict[str, str]] = {}


class ScopeRefusal(RuntimeError):
    """The checker did not establish a script universe."""


def _relative(root: Path, path: Path) -> str | None:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return None


def _is_node(relative: str) -> bool:
    parts = relative.split("/")
    if parts[0] == "scripts":
        return len(parts) > 1
    if parts[0] == "tools":
        return len(parts) > 1
    if len(parts) >= 4 and parts[:2] in (["skills", "public"], ["skills", "support"]):
        return parts[2] != "" and parts[3] == "scripts"
    return len(parts) >= 3 and parts[:3] == ["skills", "shared", "scripts"]


def _nodes(repo_root: Path) -> dict[str, Path]:
    paths = _LISTING.iter_repo_files(repo_root, include_untracked=True)
    nodes = {
        relative: path
        for path in paths
        if (relative := _relative(repo_root, path)) is not None and _is_node(relative)
    }
    if not nodes:
        raise ScopeRefusal(
            "refusing empty matched script universe; nothing was checked "
            f"(globs: {', '.join(NODE_GLOBS)})."
        )
    return dict(sorted(nodes.items()))


def _path_target(token: str, nodes: dict[str, Path]) -> str | None:
    token = token.removeprefix("./").replace("\\", "/")
    if token in nodes:
        return token
    if token.startswith("/"):
        index = _ABS_INDEXES.setdefault(
            id(nodes), {str(path): relative for relative, path in nodes.items()}
        )
        return index.get(token)
    return None


def _node_relative(path: Path, nodes: dict[str, Path]) -> str:
    index = _ABS_INDEXES.setdefault(
        id(nodes), {str(item): relative for relative, item in nodes.items()}
    )
    return index.get(str(path), path.as_posix())


def _module_target(value: str, nodes: dict[str, Path]) -> str | None:
    match = _MODULE_RE.fullmatch(value)
    if match:
        return _path_target(f"{match.group(1)}/{match.group(2)}.py", nodes)
    return None


def _literal_strings(node: ast.AST) -> list[str]:
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]


def _local_targets(path: Path, text: str, nodes: dict[str, Path]) -> set[str]:
    by_name = defaultdict(list)
    for relative in nodes:
        by_name[Path(relative).name].append(relative)
    parent = str(Path(_node_relative(path, nodes)).parent)
    targets: set[str] = set()
    quoted = re.findall(
        r"['\"]([A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|txt|md|yaml|yml|html))['\"]",
        text,
    )
    quoted += re.findall(
        r"(?:_?load_[A-Za-z0-9_]+)"
        r"\(\s*['\"]([A-Za-z0-9_./-]+)['\"]",
        text,
    )
    quoted += re.findall(
        r"load_local_skill_module\([^,]+,\s*['\"]([A-Za-z0-9_./-]+)['\"]",
        text,
    )
    for value in quoted:
        value = value.replace("\\", "/").removeprefix("./")
        candidates = [value]
        if value.isidentifier():
            candidates.extend((f"{value}.py", f"{parent}/{value}.py"))
        if "/" not in value:
            candidates.append(f"{parent}/{value}")
        for candidate in candidates:
            target = _path_target(candidate, nodes)
            if target:
                targets.add(target)
        if "/" not in value:
            matches = by_name.get(value, [])
            if len(matches) == 1:
                targets.add(matches[0])
    for value in re.findall(r"['\"]((?:scripts|tools|skills)/[A-Za-z0-9_./-]+)['\"]", text):
        target = _path_target(value, nodes)
        if target:
            targets.add(target)
    for directory, name in re.findall(
        r"['\"]([A-Za-z0-9_.-]+)['\"]\s*/\s*"
        r"['\"]([A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|txt|md|yaml|yml|html))['\"]",
        text,
    ):
        target = _path_target(f"{parent}/{directory}/{name}", nodes)
        if target:
            targets.add(target)
    return targets


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _import_targets(path: Path, tree: ast.AST, nodes: dict[str, Path]) -> set[str]:
    targets: set[str] = set()
    relative = _node_relative(path, nodes)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = _module_target(alias.name, nodes)
                if target is None and "." not in alias.name:
                    sibling = f"{Path(relative).parent}/{alias.name}.py"
                    target = (
                        _path_target(sibling, nodes)
                        or _path_target(f"scripts/{alias.name}.py", nodes)
                        or _path_target(f"tools/{alias.name}.py", nodes)
                    )
                if target:
                    targets.add(target)
        elif isinstance(node, ast.ImportFrom) and not node.level:
            module = node.module or ""
            target = _module_target(module, nodes)
            if target:
                targets.add(target)
            elif module in {"scripts", "tools"}:
                for alias in node.names:
                    target = _path_target(f"{module}/{alias.name}.py", nodes)
                    if target:
                        targets.add(target)
            elif module and "." not in module:
                target = _path_target(f"{Path(relative).parent}/{module}.py", nodes)
                if target:
                    targets.add(target)
    return targets


def _dynamic_targets(tree: ast.AST, nodes: dict[str, Path]) -> set[str]:
    targets: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name in {"import_repo_module", "load_repo_module_from_skill_script"}:
            values = (value for argument in node.args for value in _literal_strings(argument))
            for value in values:
                target = _module_target(value, nodes)
                if target:
                    targets.add(target)
        elif name == "run_path":
            for argument in node.args:
                for value in _literal_strings(argument):
                    for token in _PATH_RE.findall(value):
                        target = _path_target(token, nodes)
                        if target:
                            targets.add(target)
    return targets


def _python_targets(path: Path, nodes: dict[str, Path]) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    return (
        _local_targets(path, text, nodes)
        | _import_targets(path, tree, nodes)
        | _dynamic_targets(tree, nodes)
    )


def _text_targets(text: str, nodes: dict[str, Path]) -> set[str]:
    text = (
        text.replace("./scripts/", "scripts/")
        .replace("./tools/", "tools/")
        .replace("./skills/", "skills/")
    )
    targets = {
        target
        for token in _PATH_RE.findall(text)
        if (target := _path_target(token, nodes)) is not None
    }
    for module in re.findall(
        r"\b(?:python3|python)\s+-m\s+((?:scripts|tools)\.[A-Za-z0-9_]+)", text
    ):
        target = _module_target(module, nodes)
        if target:
            targets.add(target)
    return targets


def _relative_targets(source: str, text: str, nodes: dict[str, Path]) -> set[str]:
    parent = str(Path(source).parent)
    targets: set[str] = set()
    for token in re.findall(
        r"(?<![A-Za-z0-9_./-])(\./[A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|txt))(?![A-Za-z0-9_./-])",
        text,
    ):
        target = _path_target(f"{parent}/{token.removeprefix('./')}", nodes)
        if target:
            targets.add(target)
    return targets


def _source_class(relative: str) -> str:
    if relative.startswith("tests/"):
        return "tests-only"
    if relative.startswith("skills/"):
        return "skill"
    if relative.startswith("scripts/"):
        return "quality-lane"
    if relative.startswith("tools/"):
        return "quality-lane"
    return "surface"


def _surface_file(relative: str) -> bool:
    return relative in {"README.md", "charness"} or relative.startswith(_SURFACE_PREFIXES)


def _add_edges(edges: dict[str, set[str]], source: str, targets: set[str]) -> None:
    for target in targets:
        if source != target:
            edges[target].add(_source_class(source))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _seed_intrinsic_edges(nodes: dict[str, Path]) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = defaultdict(set)
    for relative, path in nodes.items():
        if relative == "tools/__init__.py":
            # The empty package marker is required by the tools module carrier;
            # it is not itself a runnable or referenceable gate.
            edges[relative].add("surface")
        elif relative.startswith("skills/"):
            edges[relative].add("skill")
        elif not relative.endswith((".py", ".sh")):
            edges[relative].add("surface")
        elif relative.startswith(("scripts/", "tools/")) and "__name__" in _read_text(path):
            edges[relative].add("surface")
    return edges


def _scan_file(
    relative: str, path: Path, nodes: dict[str, Path], edges: dict[str, set[str]]
) -> None:
    text = _read_text(path)
    if relative.endswith(".py") and (
        relative.startswith("scripts/")
        or relative.startswith("tools/")
        or relative.startswith("skills/")
        or relative.startswith("tests/")
    ):
        _add_edges(edges, relative, _python_targets(path, nodes) | _text_targets(text, nodes))
    if relative == "charness":
        _add_edges(edges, relative, _python_targets(path, nodes))
    if relative.startswith(("scripts/", "tools/", "skills/")):
        _add_edges(edges, relative, _relative_targets(relative, text, nodes))
    if relative.endswith(".sh") and relative.startswith(("scripts/", "tools/")):
        _add_edges(edges, relative, _text_targets(text, nodes))
    if relative.startswith("tests/") or relative.startswith("skills/") or _surface_file(relative):
        _add_edges(edges, relative, _text_targets(text, nodes))


def _add_parser_edges(repo_root: Path, nodes: dict[str, Path], edges: dict[str, set[str]]) -> None:
    """Reuse the repository's existing skill/reference parsers."""
    for row in _SKILL_REFS.classify_references(repo_root):
        found_at = row.get("found_at")
        doc = row.get("doc")
        if isinstance(found_at, str) and isinstance(doc, str):
            target = _path_target(found_at, nodes)
            if target:
                edges[target].add("skill")

    for row in _EXPORT.repo_root_instruction_findings(repo_root):
        name = row.get("script")
        doc = row.get("doc")
        if isinstance(name, str) and isinstance(doc, str):
            target = _path_target(f"scripts/{name}", nodes) or _path_target(f"tools/{name}", nodes)
            if target:
                edges[target].add(_source_class(doc))


def build_graph(repo_root: Path) -> tuple[dict[str, Path], dict[str, set[str]]]:
    nodes = _nodes(repo_root)
    edges = _seed_intrinsic_edges(nodes)
    all_files = _LISTING.iter_repo_files(repo_root, include_untracked=True)
    for path in all_files:
        relative = _relative(repo_root, path)
        if relative is None:
            continue
        _scan_file(relative, path, nodes, edges)
    _add_parser_edges(repo_root, nodes, edges)
    return nodes, edges


def report(repo_root: Path, *, strict: bool) -> dict[str, object]:
    nodes, edges = build_graph(repo_root.resolve())
    rows = []
    for relative in nodes:
        classes = sorted(edges.get(relative, {"unreferenced"}))
        rows.append({"path": relative, "referenced_by": classes})
    unreferenced = [row["path"] for row in rows if row["referenced_by"] == ["unreferenced"]]
    tests_only = [row["path"] for row in rows if row["referenced_by"] == ["tests-only"]]
    return {
        "schema": "check-unreferenced-scripts/v1",
        "repo_root": str(repo_root),
        "globs": list(NODE_GLOBS),
        "counts": {
            "nodes": len(rows),
            "unreferenced": len(unreferenced),
            "tests_only": len(tests_only),
        },
        "files": rows,
        "unreferenced": unreferenced,
        "tests_only": tests_only,
        "verdict": "fail" if strict and unreferenced else "ok",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--strict", action="store_true", help="Fail when any node is unreferenced.")
    args = parser.parse_args()
    try:
        payload = report(args.repo_root, strict=args.strict)
    except ScopeRefusal as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    emit_yaml(payload)
    if payload["unreferenced"] and args.strict:
        print(f"ERROR: {len(payload['unreferenced'])} unreferenced script file(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
