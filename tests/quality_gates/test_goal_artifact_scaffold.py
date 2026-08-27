from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_artifact_scaffold.py"
spec = importlib.util.spec_from_file_location("goal_artifact_scaffold", SCRIPT)
scaffold = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(scaffold)


def test_scaffold_is_the_planning_writer_shape() -> None:
    rendered = scaffold.render_goal_template(
        scaffold.TEMPLATE,
        title="A goal",
        date="2026-05-27",
        goal_rel_path="charness-artifacts/goals/2026-05-27-a-goal.md",
        goal_body="An outcome.",
    )

    assert rendered.startswith("# Achieve Goal: A goal\n")
    assert "Planning record: mutable until Goal Binding" in rendered
    assert "An outcome." in rendered
    assert "## Discuss Before Activation" in rendered
    assert "Status:" not in rendered
    assert "Activation:" not in rendered
    assert "## Slice Log" not in rendered
    assert "## Auto-Retro" not in rendered


def test_scaffold_does_not_add_secondary_files(tmp_path: Path) -> None:
    rendered = scaffold.render_goal_template(
        scaffold.TEMPLATE,
        title="A goal",
        date="2026-05-27",
        goal_rel_path="goal.md",
        goal_body="",
    )
    assert "Phase Specifications" not in rendered
    assert list(tmp_path.iterdir()) == []
