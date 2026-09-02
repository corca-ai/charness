#!/usr/bin/env python3
"""Layout-independent entrypoint for `<authoring-repo>/tools/validate_skills.py` (#478 site 4).

Reachable as `$SKILL_DIR/../../shared/scripts/validate_skills.py` from any skill package, in
both the authoring tree and an installed plugin. See `authoring_script_shim`
for why that prefix is the only one at equal depth in both.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from authoring_script_shim import run  # noqa: E402

TARGET = "validate_skills.py"


def main() -> int:
    return run(TARGET, __file__)


if __name__ == "__main__":
    raise SystemExit(main())
