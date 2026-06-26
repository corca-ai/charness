#!/usr/bin/env python3
"""Report standing sentinel coverage for release-only pytest files."""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

SENTINEL_RE = re.compile(
    r"(sentinel|smoke|guard|gate|dry_run|fail|block|reject|refuse|validate|"
    r"waiver|no_trigger|without|does_not|required|allows|warns)"
)


def _name_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_name_parts(node.value), node.attr]
    if isinstance(node, ast.Call):
        return _name_parts(node.func)
    return []


def _is_release_only_marker(node: ast.AST) -> bool:
    parts = _name_parts(node)
    return len(parts) >= 3 and parts[-3:] == ["pytest", "mark", "release_only"]


def _module_release_only(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if "pytestmark" not in targets:
            continue
        if _is_release_only_marker(node.value):
            return True
        if isinstance(node.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(item) for item in node.value.elts):
                return True
    return False


def _class_release_only(node: ast.ClassDef) -> bool:
    if any(_is_release_only_marker(decorator) for decorator in node.decorator_list):
        return True
    for item in node.body:
        if not isinstance(item, ast.Assign):
            continue
        targets = [target.id for target in item.targets if isinstance(target, ast.Name)]
        if "pytestmark" in targets and _is_release_only_marker(item.value):
            return True
        if "pytestmark" in targets and isinstance(item.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(marker) for marker in item.value.elts):
                return True
    return False


def _function_release_only(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_is_release_only_marker(decorator) for decorator in node.decorator_list)


def _iter_tests(tree: ast.Module) -> list[tuple[str, bool]]:
    module_release_only = _module_release_only(tree)
    tests: list[tuple[str, bool]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            tests.append((node.name, module_release_only or _function_release_only(node)))
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            class_release_only = module_release_only or _class_release_only(node)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                    tests.append(
                        (
                            f"{node.name}.{item.name}",
                            class_release_only or _function_release_only(item),
                        )
                    )
    return tests


def inventory_file(path: Path, *, repo_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    tests = _iter_tests(tree)
    release_only = [name for name, marked in tests if marked]
    standing = [name for name, marked in tests if not marked]
    sentinels = [name for name in standing if SENTINEL_RE.search(name)]
    findings: list[dict[str, str]] = []
    if release_only and not sentinels:
        findings.append(
            {
                "severity": "advisory",
                "type": "missing_standing_sentinel",
                "message": "release_only tests exist but no obvious standing sentinel name was found",
            }
        )
    return {
        "path": str(path.relative_to(repo_root)),
        "test_count": len(tests),
        "release_only_count": len(release_only),
        "standing_count": len(standing),
        "release_only_test_names": release_only,
        "standing_test_names": standing,
        "standing_sentinel_names": sentinels,
        "findings": findings,
    }


def _default_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted((repo_root / "tests").rglob("test*.py")):
        try:
            if "release_only" in path.read_text(encoding="utf-8"):
                paths.append(path)
        except UnicodeDecodeError:
            continue
    return paths


def inventory(repo_root: Path, paths: list[Path] | None = None) -> dict[str, Any]:
    selected = paths or _default_paths(repo_root)
    files = [inventory_file(path.resolve(), repo_root=repo_root) for path in selected]
    findings = [
        {"path": item["path"], **finding}
        for item in files
        for finding in item["findings"]
    ]
    return {
        "file_count": len(files),
        "release_only_file_count": sum(1 for item in files if item["release_only_count"]),
        "release_only_test_count": sum(item["release_only_count"] for item in files),
        "standing_test_count": sum(item["standing_count"] for item in files),
        "files": files,
        "findings": findings,
    }


def summarize(payload: dict[str, Any], *, sample_limit: int = 10) -> dict[str, Any]:
    files = payload["files"]
    release_only_files = [item["path"] for item in files if item["release_only_count"]]
    sentinel_files = [item["path"] for item in files if item["standing_sentinel_names"]]
    missing_sentinel_files = [finding["path"] for finding in payload["findings"]]
    return {
        "summary_note": "summary is triage output; use --json for full per-test attribution",
        "file_count": payload["file_count"],
        "release_only_file_count": payload["release_only_file_count"],
        "release_only_test_count": payload["release_only_test_count"],
        "standing_test_count": payload["standing_test_count"],
        "release_only_files_sample": release_only_files[:sample_limit],
        "standing_sentinel_file_count": len(sentinel_files),
        "standing_sentinel_files_sample": sentinel_files[:sample_limit],
        "missing_standing_sentinel_file_count": len(missing_sentinel_files),
        "missing_standing_sentinel_files_sample": missing_sentinel_files[:sample_limit],
        "findings": payload["findings"][:sample_limit],
    }


def _print_text(payload: dict[str, Any]) -> None:
    print(f"files: {payload['file_count']}")
    print(f"release_only tests: {payload['release_only_test_count']}")
    print(f"standing tests: {payload['standing_test_count']}")
    for item in payload["files"]:
        if not item["release_only_count"]:
            continue
        print(
            f"{item['path']}: release_only={item['release_only_count']} "
            f"standing={item['standing_count']} "
            f"sentinels={len(item['standing_sentinel_names'])}"
        )
        if item["standing_sentinel_names"]:
            print("  standing sentinels: " + ", ".join(item["standing_sentinel_names"]))
    for finding in payload["findings"]:
        print(f"{finding['severity'].upper()} {finding['path']}: {finding['message']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--path",
        action="append",
        type=Path,
        default=[],
        help="Selected pytest file to inspect; repeatable. Defaults to tests containing release_only.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Emit compact JSON counts and samples instead of full per-test attribution.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = [(repo_root / path).resolve() for path in args.path]
    payload = inventory(repo_root, paths or None)
    if args.summary:
        print(json.dumps(summarize(payload), ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
