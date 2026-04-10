#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOC_GLOBS = (
    "README.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/public/**/*.md",
    "skills/support/**/*.md",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class ValidationError(Exception):
    pass


def iter_docs(root: Path) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in DOC_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                files.append(path)
    return sorted(files)


def validate_link(root: Path, doc: Path, raw_target: str) -> None:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return
    if "://" in target or target.startswith("mailto:"):
        return

    if target.startswith("/"):
        path = Path(target)
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"{doc}: foreign absolute link `{target}`") from exc
        if not path.exists():
            raise ValidationError(f"{doc}: broken absolute link `{target}`")
        return

    relative_target = target.split("#", 1)[0]
    candidate = (doc.parent / relative_target).resolve()
    if not candidate.exists():
        raise ValidationError(f"{doc}: broken relative link `{target}`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    for doc in iter_docs(root):
        contents = doc.read_text(encoding="utf-8")
        for target in LINK_RE.findall(contents):
            validate_link(root, doc, target)
    print("Validated markdown links.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
