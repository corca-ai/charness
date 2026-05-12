#!/usr/bin/env python3
"""Flag inline-code spans that wrap across lines in tracked Markdown files.

Inline code spans (single-backtick form) that wrap across a newline render
correctly but break literal substring assertions and grep-driven checks against
the source. CommonMark collapses the inline newline into a space at render
time, so the rendered output looks fine while the source no longer contains
the documented command verbatim. Existing markdownlint-cli2 rules do not
catch this, so this is a repo-owned check that runs alongside the markdown
gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files

FENCE_RE = re.compile(r"^\s*(```|~~~)")
SCAN_GLOBS = ("*.md", "**/*.md")
EXCLUDE_PARTS = {"node_modules", "charness-artifacts", ".charness", ".cautilus", ".pytest_cache"}
EXCLUDE_PREFIXES: tuple[str, ...] = ()


def _strip_fences(text: str) -> str:
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def find_wrapped_inline_code(text: str) -> list[tuple[int, str]]:
    stripped = _strip_fences(text)
    lines = stripped.split("\n")
    violations: list[tuple[int, str]] = []
    open_line: int | None = None
    open_snippet: str = ""
    for index, line in enumerate(lines, start=1):
        column = 0
        while column < len(line):
            char = line[column]
            if char == "\\" and column + 1 < len(line):
                column += 2
                continue
            if char != "`":
                column += 1
                continue
            run_start = column
            while column < len(line) and line[column] == "`":
                column += 1
            run_length = column - run_start
            if run_length != 1:
                continue
            if open_line is None:
                open_line = index
                open_snippet = line[max(0, run_start - 20): min(len(line), run_start + 60)]
            else:
                if open_line != index:
                    violations.append((open_line, open_snippet))
                open_line = None
                open_snippet = ""
    return violations


def _candidate_files(repo_root: Path) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, SCAN_GLOBS)
    selected: list[Path] = []
    for path in paths:
        rel = path.relative_to(repo_root).as_posix()
        if any(part in EXCLUDE_PARTS for part in path.relative_to(repo_root).parts):
            continue
        if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            continue
        selected.append(path)
    return sorted(set(selected))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", type=Path, action="append", default=[])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.path:
        targets = [(repo_root / candidate).resolve() if not candidate.is_absolute() else candidate for candidate in args.path]
    else:
        targets = _candidate_files(repo_root)

    violation_count = 0
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for line_num, snippet in find_wrapped_inline_code(text):
            rel = path.relative_to(repo_root).as_posix() if path.is_relative_to(repo_root) else str(path)
            print(f"{rel}:{line_num}: inline code span wraps across line; collapse so the literal text stays on one line: ...{snippet}...", file=sys.stderr)
            violation_count += 1

    if violation_count:
        print(f"{violation_count} wrapped inline code span(s) found.", file=sys.stderr)
        return 1
    print(f"Validated inline code spans in {len(targets)} markdown file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
