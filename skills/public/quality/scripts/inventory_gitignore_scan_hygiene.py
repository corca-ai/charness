#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import fnmatch
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_quality_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_adapter_lib"
)
_quality_universes = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_universes_lib"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_inventory_lib import GitFileListingError, visible_repo_files  # noqa: E402
from summary_output_lib import add_output_args, emit_selected  # noqa: E402

GIT_AWARE_MARKERS = (
    "git ls-files",
    "git_visible_repo_files",
    "_git_visible_repo_files",
    "visible_repo_files",
    "git_list_repo_files",
    "iter_repo_files",
    "iter_matching_repo_files",
    # The repo's own listing owner, and the spelling three flagged call sites
    # actually use. `RepoFileSnapshot.list_files` delegates to
    # `git_list_repo_files` -- already trusted above -- but this check reads the
    # ENCLOSING FUNCTION's source text, where only the class name appears. So a
    # function that lists through the snapshot and keeps `rglob` as its guarded
    # fallback read as having no gitignore-aware source at all.
    "RepoFileSnapshot",
    "--exclude-standard",
    "check-ignore",
    "pathspec",
)
# Back-compat for callers that imported the former gate constant. The source of
# truth is the shared universes table; this alias intentionally owns no default.
DEFAULT_PATH_GLOBS = tuple(_quality_universes.DEFAULT_UNIVERSES["scanner_globs"])
REPO_ROOT_NAMES = {"repo_root", "root", "REPO_ROOT"}


class InventoryError(SystemExit):
    pass


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def candidate_files(
    repo_root: Path,
    universe,
    *,
    require_git: bool = False,
) -> list[Path]:
    if require_git:
        try:
            visible_repo_files(
                repo_root,
                require_git=True,
                context="gitignore scan hygiene file listing",
            )
        except GitFileListingError as exc:
            raise InventoryError(str(exc)) from exc
    candidates = _quality_universes.matching_files(repo_root, universe)
    # Two empties, two answers: a NAMED --path-glob that matches nothing is a
    # configured scope resolving to nothing and refuses; the default globs
    # matching nothing is a consumer repo with no scanners, a discovered empty
    # set the inventory reports in its payload.
    refusal = _quality_universes.refuse_if_declared_and_empty(
        universe, candidates, "inventory-gitignore-scan-hygiene"
    )
    if refusal:
        raise InventoryError(refusal)
    return candidates


def _is_repo_root_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id in REPO_ROOT_NAMES


def _first_call_arg(node: ast.Call) -> ast.AST | None:
    return node.args[0] if node.args else None


def _call_label(node: ast.Call, source: str) -> str:
    segment = ast.get_source_segment(source, node)
    return segment or f"line {getattr(node, 'lineno', 1)}"


def _is_repo_wide_glob(node: ast.Call) -> bool:
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr == "rglob":
        return _is_repo_root_name(node.func.value)
    if node.func.attr != "glob" or not _is_repo_root_name(node.func.value):
        return False
    arg = _first_call_arg(node)
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return "**" in arg.value
    return isinstance(arg, ast.Name)


def _is_repo_walk(node: ast.Call) -> bool:
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "walk":
        return False
    if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
        return bool(node.args and _is_repo_root_name(node.args[0]))
    return False


def _parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    return {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def _git_aware_context(node: ast.AST, parents: dict[ast.AST, ast.AST], source: str) -> bool:
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            segment = ast.get_source_segment(source, current) or ""
            return any(marker in segment for marker in GIT_AWARE_MARKERS)
    segment = ast.get_source_segment(source, node) or ""
    return any(marker in segment for marker in GIT_AWARE_MARKERS)


def analyze_file(path: Path, repo_root: Path) -> list[dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    parents = _parent_map(tree)
    findings: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (_is_repo_wide_glob(node) or _is_repo_walk(node)):
            continue
        if _git_aware_context(node, parents, source):
            continue
        findings.append(
            {
                "path": str(path.relative_to(repo_root)),
                "line": getattr(node, "lineno", 1),
                "call": _call_label(node, source),
                "reason": "repo-wide filesystem traversal without an obvious gitignore-aware file source",
                "recommendation": (
                    "Prefer `git ls-files --cached --others --exclude-standard` or "
                    "`scripts.repo_file_listing.iter_matching_repo_files` before scanning."
                ),
            }
        )
    return findings


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    findings = payload.get("findings", [])
    return {
        "summary_note": "summary is triage output; use --detail for all scan-hygiene findings",
        "repo_root": payload["repo_root"],
        "path_globs": payload["path_globs"],
        "exclude_globs": payload["exclude_globs"],
        "finding_count": len(findings) if isinstance(findings, list) else 0,
        "findings_sample": findings[:sample_limit] if isinstance(findings, list) else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root for the gitignore scan-hygiene inventory",
    )
    parser.add_argument(
        "--path-glob",
        action="append",
        default=[],
        help="Glob of Python scanners to inspect (repeatable; defaults applied if omitted)",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=[],
        help="Glob of paths to exclude from the inventory (repeatable)",
    )
    parser.add_argument(
        "--require-empty",
        action="store_true",
        help="Exit non-zero when any non-git-aware repo traversal is found",
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML finding counts and samples for triage",
        detail_help="Emit the full gitignore scan-hygiene inventory as YAML",
    )
    parser.add_argument(
        "--require-git-file-listing",
        action="store_true",
        help="Fail when git ls-files is unavailable for scanner discovery",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.path_glob:
        universe = _quality_universes.Universe(tuple(args.path_glob), True, "adapter")
    else:
        adapter = _quality_adapter_lib.load_quality_adapter(repo_root)
        universe = _quality_universes.resolve_universe(
            adapter,
            "scanner_globs",
            default=_quality_universes.DEFAULT_UNIVERSES["scanner_globs"],
        )
    path_globs = universe.patterns
    exclude_globs = tuple(args.exclude_glob or ())
    findings: list[dict[str, object]] = []
    for path in candidate_files(repo_root, universe, require_git=args.require_git_file_listing):
        rendered = str(path.relative_to(repo_root))
        if matches_any(rendered, exclude_globs):
            continue
        findings.extend(analyze_file(path, repo_root))

    payload = {
        "repo_root": str(repo_root),
        "path_globs": list(path_globs),
        "exclude_globs": list(exclude_globs),
        "findings": findings,
    }
    if not emit_selected(payload, args, summarize=summarize):
        for finding in findings:
            print(f"{finding['path']}:{finding['line']} {finding['reason']}")
            print(f"  call: {finding['call']}")
            print(f"  next: {finding['recommendation']}")
    return 1 if args.require_empty and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
