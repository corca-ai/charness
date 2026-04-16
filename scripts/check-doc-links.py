#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
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
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
PATH_TOKEN_RE = re.compile(r"\b(?:README\.md|(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.md)(?:#[A-Za-z0-9._-]+)?\b")
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


def strip_inline_markup(line: str) -> str:
    without_links = MARKDOWN_LINK_RE.sub("", line)
    return INLINE_CODE_RE.sub("", without_links)


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


def validate_link(root: Path, doc: Path, raw_target: str) -> None:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return
    if "://" in target or target.startswith("mailto:"):
        return

    if target.startswith("/"):
        raise ValidationError(f"{doc}: absolute link `{target}`; use relative links")

    relative_target = target.split("#", 1)[0]
    candidate = (doc.parent / relative_target).resolve()
    if not candidate.exists():
        raise ValidationError(f"{doc}: broken relative link `{target}`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    known_markdown_paths = iter_known_markdown_paths(root)
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
    print("Validated markdown links.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
