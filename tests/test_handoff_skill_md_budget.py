"""Slice 6 budget gate: handoff/SKILL.md must not blow past the cap.

The repo's 200-line MAX_SKILL_MD_LINES policy applies to every SKILL.md.
Slice 6 added the conditional-chunked-routing trigger paragraph + a new
reference pointer + one workflow-step bullet. To keep ≥40-line headroom
under the cap (recent-lessons repeat trap #1 — the 200-line gate biting
twice), this slice's plan budgeted handoff/SKILL.md to ≤161 lines.

A regression that creeps SKILL.md prose past 161 lines fails here
before the more general 200-line gate can.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "public" / "handoff" / "SKILL.md"

SLICE_6_BUDGET_LINES = 161


