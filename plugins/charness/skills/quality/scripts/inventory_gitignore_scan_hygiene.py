#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import subprocess
from pathlib import Path

GIT_AWARE_MARKERS = (
    "git ls-files",
    "git_list_repo_files",
    "iter_repo_files",
    "iter_matching_repo_files",
    "--exclude-standard",
    "check-ignore",
    "pathspec",
)
DEFAULT_PATH_GLOBS = (
    "skills/public/quality/scripts/*.py",
    "skills/public/quality/references/*.py",
    "scripts/*inventory*.py",
    "scripts/*quality*.py",
    "scripts/*scan*.py",
)
REPO_ROOT_NAMES = {"repo_root", "root", "REPO_ROOT"}


def git_visible_repo_files(repo_root: Path) -> set[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def candidate_files(repo_root: Path, path_globs: tuple[str, ...]) -> list[Path]:
    visible_files = git_visible_repo_files(repo_root)
    candidates: list[Path] = []
    seen: set[Path] = set()
    for pattern in path_globs:
        for path in repo_root.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            if visible_files is not None and path not in visible_files:
                continue
            candidates.append(path)
    return sorted(candidates)


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


def analyze_file(path: Path, repo_root: Path) -> list[dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    if any(marker in source for marker in GIT_AWARE_MARKERS):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    findings: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (_is_repo_wide_glob(node) or _is_repo_walk(node)):
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path-glob", action="append", default=[])
    parser.add_argument("--exclude-glob", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    path_globs = tuple(args.path_glob or DEFAULT_PATH_GLOBS)
    exclude_globs = tuple(args.exclude_glob or ())
    findings: list[dict[str, object]] = []
    for path in candidate_files(repo_root, path_globs):
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
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print(f"{finding['path']}:{finding['line']} {finding['reason']}")
            print(f"  call: {finding['call']}")
            print(f"  next: {finding['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
