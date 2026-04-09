#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_manifests


class ValidationError(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    try:
        manifests = load_manifests(args.repo_root.resolve())
    except Exception as exc:  # pragma: no cover - surfaced via CLI tests
        raise ValidationError(str(exc)) from exc
    print(f"Validated {len(manifests)} integration manifests.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
