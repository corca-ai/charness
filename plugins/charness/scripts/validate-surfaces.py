#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.surfaces_lib import SURFACES_PATH, SurfaceError, load_surfaces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    args = parser.parse_args()

    manifest = load_surfaces(args.repo_root.resolve(), surfaces_path=args.surfaces_path)
    assert manifest is not None
    print(
        f"Validated surfaces manifest with {len(manifest['surfaces'])} surface(s) from {manifest['path']}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
