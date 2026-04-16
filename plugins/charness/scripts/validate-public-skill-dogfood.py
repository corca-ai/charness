#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.public_skill_dogfood_lib import DOGFOOD_PATH
from scripts.public_skill_dogfood_validation_lib import (
    ValidationError,
    load_registry,
    validate_registry,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry = validate_registry(load_registry(repo_root), repo_root)
    print(
        f"Validated public skill dogfood registry {DOGFOOD_PATH} "
        f"({len(registry['cases'])} cases, {len(registry['review_required_skills'])} required)."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
