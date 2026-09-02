from __future__ import annotations

from pathlib import Path

from .test_quality_run_planner import _run_plan

ROOT = Path(__file__).resolve().parents[2]


def test_quality_run_plan_uses_declared_consumer_gates_and_skips_tools_rows(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "consumer"
    gate_file = repo / ".agents" / "quality-gates.yaml"
    gate_file.parent.mkdir(parents=True)
    gate_file.write_text(
        (ROOT / "tests/quality_gates/fixtures/consumer-quality-gates.yaml").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    packets = {packet["id"]: packet for packet in _run_plan(repo)["gate_packets"]}

    assert packets["consumer-pytest"]["command"] == "python3 -m pytest tests"
    assert {"authoring-catalog", "authoring-scan"}.isdisjoint(packets)
