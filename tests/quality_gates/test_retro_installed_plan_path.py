"""Regression coverage for the installed retro planner command carrier (#686)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "planner",
    [
        ROOT / "skills/public/retro/scripts/plan_retro_run.py",
        ROOT / "plugins/charness/skills/retro/scripts/plan_retro_run.py",
    ],
    ids=["authoring-layout", "exported-layout"],
)
def test_auto_trigger_packet_uses_installed_skill_root(planner: Path, tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            str(planner),
            "--repo-root",
            str(tmp_path),
            "--changed-paths",
            "scripts/example.ts",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    packet = next(item for item in payload["gate_packets"] if item["id"] == "auto-session-trigger")

    assert packet["command"] == 'python3 "$SKILL_DIR/scripts/check_auto_trigger.py" --repo-root .'
    assert packet["path"] == "scripts/check_auto_trigger.py"
    assert packet["path_base"] == "skill-dir"
    assert packet["required"] is True
    assert packet["available"] is True
    assert "skills/public/retro" not in packet["command"]


def test_missing_required_skill_packet_is_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy

    module = runpy.run_path(str(ROOT / "skills/public/retro/scripts/plan_retro_run.py"))
    monkeypatch.setitem(
        module["_skill_script_command"].__globals__,
        "SKILL_ROOT",
        ROOT / ".charness" / "missing-skill-package",
    )

    plan = module["build_plan"](ROOT, changed_paths=["scripts/example.ts"])

    assert plan["ok"] is False
    assert plan["readiness"] == {
        "status": "not-ready",
        "blocking_packets": ["auto-session-trigger"],
        "adapter_valid": True,
    }
