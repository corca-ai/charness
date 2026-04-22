#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

DEFAULT_PATTERNS = (
    "scripts/*.py",
    "skills/public/*/scripts/*.py",
    "skills/support/*/scripts/*.py",
    "docs/*.md",
    "skills/public/*/references/*.md",
    "skills/support/*/references/*.md",
    "skills/public/*/SKILL.md",
    "skills/support/*/SKILL.md",
    "README.md",
)
DEFAULT_MIN_NONEMPTY_LINES = 18


def is_substantive(path: Path, min_nonempty_lines: int) -> bool:
    text = path.read_text(encoding="utf-8")
    nonempty_lines = sum(1 for line in text.splitlines() if line.strip())
    return nonempty_lines >= min_nonempty_lines


def iter_files(root: Path, patterns: tuple[str, ...], min_nonempty_lines: int) -> list[Path]:
    return [path for path in iter_matching_repo_files(root, patterns) if is_substantive(path, min_nonempty_lines)]


def find_duplicates(
    root: Path, threshold: float, patterns: tuple[str, ...], min_nonempty_lines: int
) -> list[dict[str, object]]:
    files = iter_files(root, patterns, min_nonempty_lines)
    texts = {path: path.read_text(encoding="utf-8") for path in files}
    duplicates: list[dict[str, object]] = []
    for index, left in enumerate(files):
        left_text = texts[left]
        for right in files[index + 1 :]:
            right_text = texts[right]
            max_possible_ratio = (2 * min(len(left_text), len(right_text))) / (len(left_text) + len(right_text))
            if max_possible_ratio < threshold:
                continue
            matcher = difflib.SequenceMatcher(None, left_text, right_text)
            if matcher.real_quick_ratio() < threshold:
                continue
            if matcher.quick_ratio() < threshold:
                continue
            ratio = matcher.ratio()
            if ratio >= threshold:
                duplicates.append(
                    {
                        "left": str(left.relative_to(root)),
                        "right": str(right.relative_to(root)),
                        "similarity": round(ratio, 3),
                    }
                )
    return duplicates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect near-duplicate helper code and checked-in documentation."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--threshold", type=float, default=0.98)
    parser.add_argument("--min-nonempty-lines", type=int, default=DEFAULT_MIN_NONEMPTY_LINES)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-match", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    duplicates = find_duplicates(root, args.threshold, DEFAULT_PATTERNS, args.min_nonempty_lines)
    if args.json:
        print(json.dumps(duplicates, indent=2))
    elif duplicates:
        print(f"Found {len(duplicates)} duplicate pair(s) at threshold {args.threshold}:")
        for duplicate in duplicates:
            print(
                f"- {duplicate['left']} <-> {duplicate['right']} "
                f"({duplicate['similarity']})"
            )
    else:
        print(f"No duplicates found at threshold {args.threshold}.")

    if args.fail_on_match and duplicates:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
