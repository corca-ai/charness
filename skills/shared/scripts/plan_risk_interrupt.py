#!/usr/bin/env python3
"""Layout-independent entrypoint for `<authoring-repo>/scripts/gates_support/plan_risk_interrupt.py` (#477).

`impl` and `spec` invoked the planner as
`$SKILL_DIR/../../../scripts/plan_risk_interrupt.py`. Three levels up reaches the
repo root from `skills/public/<skill>` and OVERSHOOTS from
`plugins/<pkg>/skills/<skill>`, where the exported scripts sit two levels up — so
the command resolved in the authoring tree and nowhere else, silently, because
both call sites ended in `2>/dev/null || true`.

Reachable as `$SKILL_DIR/../../shared/scripts/plan_risk_interrupt.py` from any
skill package, in both layouts. See `authoring_script_shim` for why.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from authoring_script_shim import run  # noqa: E402

TARGET = "plan_risk_interrupt.py"


def main() -> int:
    return run(TARGET, __file__)


if __name__ == "__main__":
    raise SystemExit(main())
