#!/usr/bin/env python3
"""Migrate checked-in docs to the explicit-file-reference convention.

Two conversions run in sequence on every DOC_GLOBS markdown file:

1. Backtick-wrapped file references become markdown links. A backticked token
   counts as a file reference when it is one of:
   - a path-like token (contains `/`) that resolves to a tracked file,
   - a bare filename that matches exactly one tracked file (unique basename),
   - a token starting with `./` or `../` (which is never correct as a bare
     backtick, even when the remainder is a concept name).
   Command-invocation backticks (containing whitespace) stay literal so inline
   runnable examples keep their form.

2. Existing relative markdown link targets that do not already start with
   `./`, `../`, `#`, or a URL scheme get a `./` prefix so every file reference
   is visually distinguishable from a concept token.
"""

from __future__ import annotations

import argparse
import os.path
import re
import sys
from collections import defaultdict
from os.path import relpath
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
iter_repo_files = _scripts_repo_file_listing_module.iter_repo_files

DOC_GLOBS = (
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/public/**/*.md",
    "skills/support/**/*.md",
)
SKIP_DIR_NAMES = {".git", "node_modules", ".pytest_cache", "__pycache__"}
PORTABLE_SKILL_KINDS = {"public", "support"}
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK_RE = re.compile(r"(\[[^\]]+\])\(([^)]+)\)")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$")
EXTENSION_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.-]+\.[A-Za-z][A-Za-z0-9]{0,5}$")


def iter_known_repo_paths(root: Path) -> set[str]:
    known: set[str] = set()
    for path in iter_repo_files(root):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        known.add(path.relative_to(root).as_posix())
    return known


def build_unique_basename_index(known_repo_paths: set[str]) -> dict[str, str]:
    groups: dict[str, list[str]] = defaultdict(list)
    for rel_path in known_repo_paths:
        groups[os.path.basename(rel_path)].append(rel_path)
    return {name: paths[0] for name, paths in groups.items() if len(paths) == 1}


def build_known_directories(known_repo_paths: set[str]) -> set[str]:
    dirs: set[str] = set()
    for rel_path in known_repo_paths:
        parent = os.path.dirname(rel_path)
        while parent:
            dirs.add(parent)
            parent = os.path.dirname(parent)
    return dirs


def is_portable_skill_body(root: Path, path: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    parts = rel.parts
    return (
        len(parts) >= 3
        and parts[0] == "skills"
        and parts[1] in PORTABLE_SKILL_KINDS
        and root.joinpath(*parts[:3]).is_dir()
    )


def classify_token(
    candidate: str,
    known_repo_paths: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
) -> tuple[str, bool] | None:
    """Resolve a backticked token to (target_rel_path, is_directory) or None if it's not a file ref."""
    if not candidate or any(ch.isspace() for ch in candidate):
        return None
    bare = candidate.split("#", 1)[0]
    if not bare:
        return None
    if bare.startswith("./") or bare.startswith("../"):
        stripped = bare.rstrip("/")
        while stripped.startswith("./"):
            stripped = stripped[2:]
        if stripped in known_repo_paths:
            return stripped, False
        if stripped in known_directories:
            return stripped, True
        return None
    if PATHY_TOKEN_RE.match(bare) and bare in known_repo_paths:
        return bare, False
    if "/" in bare:
        return None
    if not EXTENSION_TOKEN_RE.match(bare):
        return None
    if bare in known_repo_paths:
        return bare, False
    if bare in unique_basename_index:
        return unique_basename_index[bare], False
    return None


def relative_link_with_prefix(doc_rel: str, target_rel: str) -> str:
    doc_dir = Path(doc_rel).parent.as_posix() or "."
    rel = relpath(target_rel, doc_dir).replace("\\", "/")
    if rel.startswith("./") or rel.startswith("../"):
        return rel
    return f"./{rel}"


def prefix_existing_target(target: str) -> str:
    stripped = target.strip()
    if not stripped:
        return target
    if stripped.startswith(("./", "../", "#", "/")) or "://" in stripped or stripped.startswith("mailto:"):
        return target
    return f"./{target}"


def rewrite_backticks_in_segment(
    segment: str,
    doc_rel: str,
    known: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
) -> tuple[str, int]:
    changes = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal changes
        inner = match.group(1)
        classified = classify_token(inner, known, unique_basename_index, known_directories)
        if classified is None:
            return match.group(0)
        target_rel, is_dir = classified
        bare = inner.split("#", 1)[0]
        fragment = inner[len(bare) :]
        rel_target = relative_link_with_prefix(doc_rel, target_rel)
        if is_dir and not rel_target.endswith("/"):
            rel_target = f"{rel_target}/"
        changes += 1
        return f"[`{inner}`]({rel_target}{fragment})"

    return BACKTICK_SPAN_RE.sub(_replace, segment), changes


def rewrite_line(
    line: str,
    doc_rel: str,
    known: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
) -> tuple[str, int]:
    pieces: list[str] = []
    total_changes = 0
    cursor = 0
    for match in MARKDOWN_LINK_RE.finditer(line):
        segment = line[cursor : match.start()]
        rewritten_seg, changes = rewrite_backticks_in_segment(
            segment, doc_rel, known, unique_basename_index, known_directories
        )
        pieces.append(rewritten_seg)
        total_changes += changes
        label, target = match.group(1), match.group(2)
        new_target = prefix_existing_target(target)
        if new_target != target:
            total_changes += 1
        pieces.append(f"{label}({new_target})")
        cursor = match.end()
    tail = line[cursor:]
    rewritten_tail, changes = rewrite_backticks_in_segment(
        tail, doc_rel, known, unique_basename_index, known_directories
    )
    pieces.append(rewritten_tail)
    total_changes += changes
    return "".join(pieces), total_changes


def rewrite_file(
    path: Path,
    root: Path,
    known: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
    dry_run: bool,
) -> int:
    if is_portable_skill_body(root, path):
        return 0
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
        rewritten, changes = rewrite_line(line_no_nl, doc_rel, known, unique_basename_index, known_directories)
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
    unique_basename_index = build_unique_basename_index(known)
    known_directories = build_known_directories(known)
    docs = iter_matching_repo_files(root, DOC_GLOBS)

    total = 0
    changed_files: list[tuple[str, int]] = []
    for doc in docs:
        changes = rewrite_file(doc, root, known, unique_basename_index, known_directories, dry_run=args.dry_run)
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
