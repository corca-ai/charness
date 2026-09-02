#!/usr/bin/env python3
"""Flat entrypoint kept for the documented session-start command.

AGENTS.md prescribes `python3 scripts/render_lesson_selection_preview.py`; the
implementation lives in `scripts/lessons/` since the concept packaging, and the
router page changes only with the operator's explicit approval, so this shim
runs the packaged module under the same name and arguments.
"""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "lessons" / "render_lesson_selection_preview.py"
    runpy.run_path(str(target), run_name="__main__")
