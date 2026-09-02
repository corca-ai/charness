"""Regression coverage for the installed retro planner command carrier (#686)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.boundary_contract(
    reason="prove the generated retro planner runs from the installed layout"
)
def _run(planner: Path, *args: str) -> SimpleNamespace:
    if "plugins" in planner.parts:
        return subprocess.run(
            [sys.executable, str(planner), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    module_name = (
        "retro_planner_" + ("plugin" if "plugins" in planner.parts else "source") + "_for_test"
    )
    module = load_script_module(module_name, planner)
    previous_cwd = Path.cwd()
    try:
        import os

        os.chdir(ROOT)
        return run_loaded_script_main(str(planner), module, *args)
    finally:
        os.chdir(previous_cwd)


@pytest.mark.parametrize(
    "planner",
    [
        ROOT / "skills/public/retro/scripts/plan_retro_run.py",
        ROOT / "plugins/charness/skills/retro/scripts/plan_retro_run.py",
    ],
    ids=["authoring-layout", "exported-layout"],
)
def test_auto_trigger_packet_uses_installed_skill_root(planner: Path, tmp_path: Path) -> None:
    result = _run(
        planner,
        "--repo-root",
        str(tmp_path),
        "--changed-paths",
        "scripts/example.ts",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    packet = next(item for item in payload["gate_packets"] if item["id"] == "auto-session-trigger")

    assert packet["command"] == (
        'python3 "$SKILL_DIR/scripts/check_auto_trigger.py" --repo-root . '
        "--paths scripts/example.ts"
    )
    assert packet["path"] == "scripts/check_auto_trigger.py"
    assert packet["path_base"] == "skill-dir"
    assert packet["required"] is True
    assert packet["available"] is True
    assert "skills/public/retro" not in packet["command"]
    assert packet["trigger_scope"] == ["scripts/example.ts"]
    assert packet["trigger_scope_source"] == "explicit_paths"
    assert payload["trigger_scope"] == ["scripts/example.ts"]
    assert payload["trigger_scope_source"] == "explicit_paths"
    assert payload["trigger_scope_status"] == "established"


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
