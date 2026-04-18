#!/usr/bin/env python3
"""Convert backtick-wrapped file references in checked-in docs to markdown links.

Only tokens that (a) match `*/*.*` (nested path with extension) or
(b) are root-level tracked files with an extension-like name are rewritten.
Command-invocation backticks (containing whitespace) are preserved so inline
runnable examples keep their literal form.
"""

from __future__ import annotations

import argparse
import re
import sys
from os.path import relpath
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
iter_repo_files = _scripts_repo_file_listing_module.iter_repo_files

DOC_GLOBS = (
    "README.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/public/**/*.md",
    "skills/support/**/*.md",
)
SKIP_DIR_NAMES = {".git", "node_modules", ".pytest_cache", "__pycache__"}
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$")
ROOT_FILE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$")


def iter_known_repo_paths(root: Path) -> set[str]:
    known: set[str] = set()
    for path in iter_repo_files(root):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        known.add(path.relative_to(root).as_posix())
    return known


def is_file_ref(candidate: str, known: set[str]) -> bool:
    if not candidate or any(ch.isspace() for ch in candidate):
        return False
    bare = candidate.split("#", 1)[0]
    if not bare:
        return False
    if PATHY_TOKEN_RE.match(bare):
        return bare in known
    if "/" not in bare and ROOT_FILE_NAME_RE.match(bare):
        return bare in known
    return False


def relative_link(doc_rel: str, target_rel: str) -> str:
    doc_dir = Path(doc_rel).parent.as_posix() or "."
    return relpath(target_rel, doc_dir).replace("\\", "/")


def rewrite_segment(segment: str, doc_rel: str, known: set[str]) -> tuple[str, int]:
    changes = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal changes
        inner = match.group(1)
        if not is_file_ref(inner, known):
            return match.group(0)
        bare = inner.split("#", 1)[0]
        fragment = inner[len(bare) :]
        rel_target = relative_link(doc_rel, bare)
        changes += 1
        return f"[`{inner}`]({rel_target}{fragment})"

    return BACKTICK_SPAN_RE.sub(_replace, segment), changes


def rewrite_line(line: str, doc_rel: str, known: set[str]) -> tuple[str, int]:
    pieces: list[str] = []
    total_changes = 0
    cursor = 0
    for match in MARKDOWN_LINK_RE.finditer(line):
        segment = line[cursor : match.start()]
        rewritten_seg, changes = rewrite_segment(segment, doc_rel, known)
        pieces.append(rewritten_seg)
        total_changes += changes
        pieces.append(match.group(0))
        cursor = match.end()
    tail = line[cursor:]
    rewritten_tail, changes = rewrite_segment(tail, doc_rel, known)
    pieces.append(rewritten_tail)
    total_changes += changes
    return "".join(pieces), total_changes


def rewrite_file(path: Path, root: Path, known: set[str], dry_run: bool) -> int:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    out_lines: list[str] = []
    in_fence = False
    total_changes = 0
    doc_rel = path.relative_to(root).as_posix()
    for raw_line in lines:
        line_no_nl = raw_line[:-1] if raw_line.endswith("\n") else raw_line
        newline = "\n" if raw_line.endswith("\n") else ""
        if FENCE_RE.match(line_no_nl):
            in_fence = not in_fence
            out_lines.append(raw_line)
            continue
        if in_fence:
            out_lines.append(raw_line)
            continue
        rewritten, changes = rewrite_line(line_no_nl, doc_rel, known)
        total_changes += changes
        out_lines.append(rewritten + newline)
    if total_changes and not dry_run:
        path.write_text("".join(out_lines), encoding="utf-8")
    return total_changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    known = iter_known_repo_paths(root)
    docs = iter_matching_repo_files(root, DOC_GLOBS)

    total = 0
    changed_files: list[tuple[str, int]] = []
    for doc in docs:
        changes = rewrite_file(doc, root, known, dry_run=args.dry_run)
        if changes:
            changed_files.append((doc.relative_to(root).as_posix(), changes))
            total += changes

    mode = "would change" if args.dry_run else "changed"
    for doc_rel, changes in changed_files:
        print(f"{mode} {changes:4d}  {doc_rel}")
    print(f"\ntotal: {total} rewrite(s) across {len(changed_files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
