#!/usr/bin/env python3
"""Layout-independent compatibility entrypoint for the retired title/slug checker."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from authoring_script_shim import run  # noqa: E402

TARGET = "check_title_slug_drift.py"


def main() -> int:
    return run(TARGET, __file__)


if __name__ == "__main__":
    raise SystemExit(main())
