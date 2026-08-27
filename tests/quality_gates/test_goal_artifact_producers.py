from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_artifact_lib.py"
spec = importlib.util.spec_from_file_location("goal_artifact_lib_producers", SCRIPT)
goal_lib = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(goal_lib)


def test_goal_artifact_producer_emits_only_planning_shape(tmp_path: Path) -> None:
    goal_lib.upsert_goal(
        tmp_path,
        date="2026-06-01",
        slug="producer-contract",
        title="Producer Contract",
        goal_body="Exercise the planning writer.",
    )
    text = goal_lib.goal_path(tmp_path, "2026-06-01", "producer-contract").read_text(encoding="utf-8")

    assert goal_lib.check_planning_shape(text)["ok"] is True
    for section in goal_lib.REQUIRED_SECTIONS:
        assert f"## {section}" in text, section
    for removed in (
        "Status:",
        "Activation:",
        "Active Operating Frame",
        "Phase Specifications",
        "Backlog Recount",
        "Operator Decision Queue",
        "Slice Log",
        "Final Verification",
        "Auto-Retro",
    ):
        assert removed not in text
