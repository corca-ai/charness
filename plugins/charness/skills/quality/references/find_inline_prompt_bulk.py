#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import subprocess
from pathlib import Path


def multiline_string_findings(path: Path, *, min_chars: int) -> list[dict[str, object]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    findings: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value
        if "\n" not in value or len(value) < min_chars:
            continue
        findings.append(
            {
                "path": str(path),
                "line": getattr(node, "lineno", 1),
                "char_count": len(value),
                "preview": value.strip().splitlines()[0][:80],
            }
        )
    return findings


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-glob", action="append", default=[])
    parser.add_argument("--exemption-glob", action="append", default=[])
    parser.add_argument("--min-multiline-chars", type=int, default=400)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    source_globs = args.source_glob or ["**/*.py"]
    exemptions = args.exemption_glob or []
    visible_files = git_visible_repo_files(repo_root)
    findings: list[dict[str, object]] = []
    seen: set[Path] = set()
    for pattern in source_globs:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            if visible_files is not None and path not in visible_files:
                continue
            rendered = str(path.relative_to(repo_root))
            if matches_any(rendered, exemptions):
                continue
            findings.extend(
                {
                    **finding,
                    "path": rendered,
                }
                for finding in multiline_string_findings(path, min_chars=args.min_multiline_chars)
            )

    payload = {
        "repo_root": str(repo_root),
        "source_globs": source_globs,
        "exemption_globs": exemptions,
        "min_multiline_chars": args.min_multiline_chars,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print(f"{finding['path']}:{finding['line']} chars={finding['char_count']} {finding['preview']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
