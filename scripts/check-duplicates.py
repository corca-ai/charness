#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

DEFAULT_PATTERNS = (
    "scripts/*.py",
    "skills/public/*/scripts/*.py",
)


def iter_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                files.append(path)
    return sorted(files)


def find_duplicates(root: Path, threshold: float, patterns: tuple[str, ...]) -> list[dict[str, object]]:
    files = iter_files(root, patterns)
    duplicates: list[dict[str, object]] = []
    for index, left in enumerate(files):
        left_text = left.read_text(encoding="utf-8")
        for right in files[index + 1 :]:
            right_text = right.read_text(encoding="utf-8")
            ratio = difflib.SequenceMatcher(None, left_text, right_text).ratio()
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
    parser = argparse.ArgumentParser(description="Detect near-duplicate helper scripts.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--threshold", type=float, default=0.98)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-match", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    duplicates = find_duplicates(root, args.threshold, DEFAULT_PATTERNS)
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
