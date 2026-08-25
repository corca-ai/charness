from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/scaffold_goal_specs.py"
spec = importlib.util.spec_from_file_location("scaffold_goal_specs", SCRIPT)
scaffold = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(scaffold)


def _goal(tmp_path: Path) -> Path:
    path = tmp_path / "charness-artifacts/goals/2026-08-25-demo.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Achieve Goal: Demo\n\n"
        "## Goal\n\nKeep this compact.\n\n"
        "## Phase Specifications\n\n- Phase specs: pending decomposition\n\n"
        "## Non-Goals\n\nNone.\n",
        encoding="utf-8",
    )
    return path


def _phase_input(tmp_path: Path) -> Path:
    path = tmp_path / "phases.json"
    path.write_text(
        json.dumps(
            {
                "phases": [
                    {
                        "slug": "shape",
                        "title": "Shape the contract",
                        "objective": "Make the phase boundary explicit.",
                        "scope_in": ["goal artifact"],
                        "scope_out": ["implementation"],
                        "dependencies": ["user intent"],
                        "completion": ["the phase spec is linked"],
                        "verification": ["check the link and receipt"],
                        "non_claims": ["no implementation is claimed"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def test_scaffold_creates_phase_spec_and_goal_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    goal = _goal(tmp_path)
    phases = _phase_input(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--goal-path",
            str(goal),
            "--specs-file",
            str(phases),
        ],
    )

    assert scaffold.main() == 0

    phase = tmp_path / "charness-artifacts/specs/demo/phase-01-shape/spec.md"
    assert phase.is_file()
    phase_text = phase.read_text(encoding="utf-8")
    assert "Goal: [demo](../../../goals/2026-08-25-demo.md)" in phase_text
    assert "## Completion Criteria" in phase_text
    assert "5-whys" in phase_text
    goal_text = goal.read_text(encoding="utf-8")
    assert "Phase 1: [Shape the contract](../specs/demo/phase-01-shape/spec.md)" in goal_text
    assert "Phase specs: pending decomposition" not in goal_text


def test_scaffold_refuses_to_overwrite_changed_phase_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    goal = _goal(tmp_path)
    phases = _phase_input(tmp_path)
    argv = [
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal),
        "--specs-file",
        str(phases),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    scaffold.main()
    phase = tmp_path / "charness-artifacts/specs/demo/phase-01-shape/spec.md"
    phase.write_text(phase.read_text(encoding="utf-8") + "manual change\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="refusing to overwrite"):
        scaffold.main()


def test_load_specs_requires_all_completion_and_verification_fields(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"phases": [{"slug": "shape", "title": "Shape"}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="missing required fields"):
        scaffold._load_specs(path)
