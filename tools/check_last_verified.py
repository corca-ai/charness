#!/usr/bin/env python3
"""Require the exact freshness header on every repository documentation page."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
LAST_VERIFIED_RE = r"^> Last verified: [0-9]{4}-[0-9]{2}-[0-9]{2}$"


def check(repo_root: Path) -> int:
    status = 0
    for path in sorted((repo_root / "docs").glob("*.md")):
        if not path.is_file():
            continue
        has_header = any(
            re.fullmatch(LAST_VERIFIED_RE, line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
        if not has_header:
            relative = path.relative_to(repo_root)
            print(
                f"FAIL check-last-verified: {relative} is missing an exact Last verified header",
                file=sys.stderr,
            )
            status = 1
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return check(args.repo_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
