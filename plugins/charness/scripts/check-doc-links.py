#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os.path
import re
import sys
from collections import defaultdict
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files
iter_repo_files = _scripts_repo_file_listing_module.iter_repo_files

DOC_GLOBS = (
    "README.md",
    "AGENTS.md",
    "INSTALL.md",
    "UNINSTALL.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/public/**/*.md",
    "skills/support/**/*.md",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
PATH_TOKEN_RE = re.compile(r"\b(?:README\.md|(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.md)(?:#[A-Za-z0-9._-]+)?\b")
BACKTICK_CONTENT_RE = re.compile(r"`([^`\n]+)`")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$")
EXTENSION_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.-]+\.[A-Za-z][A-Za-z0-9]{0,5}$")
SKIP_DIR_NAMES = {".git", "node_modules", ".pytest_cache", "__pycache__"}


class ValidationError(Exception):
    pass


def iter_docs(root: Path) -> list[Path]:
    return iter_matching_repo_files(root, DOC_GLOBS)


def iter_known_markdown_paths(root: Path) -> set[str]:
    known: set[str] = set()
    for path in iter_repo_files(root):
        if path.suffix != ".md":
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        known.add(path.relative_to(root).as_posix())
    return known


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


def strip_inline_markup(line: str) -> str:
    without_links = MARKDOWN_LINK_RE.sub("", line)
    return INLINE_CODE_RE.sub("", without_links)


def strip_markdown_links(line: str) -> str:
    return MARKDOWN_LINK_RE.sub("", line)


def iter_bare_internal_doc_refs(root: Path, doc: Path, known_markdown_paths: set[str]) -> list[str]:
    matches: list[str] = []
    in_fence = False
    for line in doc.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        scrubbed = strip_inline_markup(line)
        for match in PATH_TOKEN_RE.findall(scrubbed):
            candidate = match.split("#", 1)[0]
            if candidate in known_markdown_paths:
                matches.append(match)
    return matches


def classify_backtick_token(
    candidate: str,
    known_repo_paths: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
) -> str | None:
    """Return a short reason tag if the backticked token must become a markdown link.

    - "pathy": contains "/" with a valid extension-bearing tail and resolves to a tracked file.
    - "prefix": starts with "./" or "../" and resolves to a tracked file or directory; the
      backtick form is never correct when the target exists, since renames silently break it.
    - "unique-basename": bare filename whose basename is unique among tracked files.

    Returns None when the token should be allowed as-is (concept, ambiguous basename, whitespace
    command invocation, version string, dotted property path, domain-like token, `./`-prefixed
    token that does not resolve to a real repo path, etc.).
    """
    if not candidate or any(ch.isspace() for ch in candidate):
        return None

    if candidate.startswith("./") or candidate.startswith("../"):
        stripped = candidate.rstrip("/")
        while stripped.startswith("./"):
            stripped = stripped[2:]
        if stripped in known_repo_paths or stripped in known_directories:
            return "prefix"
        return None

    if PATHY_TOKEN_RE.match(candidate) and candidate in known_repo_paths:
        return "pathy"

    if "/" in candidate:
        return None

    if not EXTENSION_TOKEN_RE.match(candidate):
        return None

    if candidate in known_repo_paths:
        return "pathy"

    if candidate in unique_basename_index:
        return "unique-basename"

    return None


def iter_backticked_file_refs(
    doc: Path,
    known_repo_paths: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
) -> list[tuple[int, str, str]]:
    matches: list[tuple[int, str, str]] = []
    in_fence = False
    for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        scrubbed = strip_markdown_links(line)
        for match in BACKTICK_CONTENT_RE.finditer(scrubbed):
            candidate = match.group(1).split("#", 1)[0].strip()
            reason = classify_backtick_token(
                candidate, known_repo_paths, unique_basename_index, known_directories
            )
            if reason is not None:
                matches.append((lineno, candidate, reason))
    return matches


def validate_link(root: Path, doc: Path, raw_target: str) -> None:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return
    if "://" in target or target.startswith("mailto:"):
        return

    if target.startswith("/"):
        raise ValidationError(f"{doc}: absolute link `{target}`; use relative links")

    if not (target.startswith("./") or target.startswith("../")):
        raise ValidationError(
            f"{doc}: relative link `{target}` must start with `./` or `../` so file references "
            "are distinguishable from concept tokens at a glance"
        )

    relative_target = target.split("#", 1)[0]
    candidate = (doc.parent / relative_target).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(
            f"{doc}: relative link `{target}` escapes repo root; keep markdown links inside "
            "repo-owned paths"
        ) from exc
    if not candidate.exists():
        raise ValidationError(f"{doc}: broken relative link `{target}`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    known_markdown_paths = iter_known_markdown_paths(root)
    known_repo_paths = iter_known_repo_paths(root)
    unique_basename_index = build_unique_basename_index(known_repo_paths)
    known_directories = build_known_directories(known_repo_paths)
    for doc in iter_docs(root):
        contents = doc.read_text(encoding="utf-8")
        for target in LINK_RE.findall(contents):
            validate_link(root, doc, target)
        bare_refs = iter_bare_internal_doc_refs(root, doc, known_markdown_paths)
        if bare_refs:
            refs = ", ".join(f"`{ref}`" for ref in bare_refs[:3])
            if len(bare_refs) > 3:
                refs += ", ..."
            raise ValidationError(
                f"{doc}: bare internal markdown reference(s) {refs}; use markdown links in prose"
            )
        backticked = iter_backticked_file_refs(
            doc, known_repo_paths, unique_basename_index, known_directories
        )
        if backticked:
            refs = ", ".join(f"`{cand}` (line {ln}, {reason})" for ln, cand, reason in backticked[:3])
            if len(backticked) > 3:
                refs += ", ..."
            raise ValidationError(
                f"{doc}: backticked file reference(s) {refs}; use markdown links so renames do not rot"
            )
    print("Validated markdown links.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
