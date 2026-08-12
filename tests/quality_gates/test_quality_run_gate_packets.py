from __future__ import annotations

import importlib.util
from pathlib import Path

from .support import ROOT


def _load_plan():
    path = ROOT / "skills/public/quality/scripts/plan_quality_run.py"
    spec = importlib.util.spec_from_file_location("quality_plan_gate_packets", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quality_run_plan_reports_gate_packet_cost_and_trust(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    plan = _load_plan().build_plan(repo)

    packets = plan["gate_packets"]
    read_only = next(packet for packet in packets if packet["id"] == "read-only-quality")
    assert read_only["cost_tier"] == "broad"
    assert read_only["parallel_group"] == "serial-critical"
    assert "advisory" in read_only["trust_model"]
    assert "repo-native command" in read_only["run_when"]
    skill_ergonomics = next(packet for packet in packets if packet["id"] == "skill-ergonomics")
    assert "--summary" in skill_ergonomics["command"]
    assert "--json" not in skill_ergonomics["command"]
