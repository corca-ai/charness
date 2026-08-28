from __future__ import annotations

from pathlib import Path

from .support import ROOT
from .seeding_support import load_module


def _load_plan():
    path = ROOT / "skills/public/quality/scripts/plan_quality_run.py"
    return load_module("quality_plan_gate_packets", path)


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
