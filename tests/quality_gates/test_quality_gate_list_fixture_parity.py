"""The R3 gate-list fixture stays aligned with the canonical shell label reader."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "quality_gates" / "fixtures" / ".agents" / "quality-gates.yaml"
CAPTURED = (
    ROOT
    / "native"
    / "repograph"
    / "fixtures"
    / "carriers"
    / "expected"
    / "quality_label_universe.yaml"
)


def test_declared_fixture_and_captured_universe_match_shell_reader_in_process() -> None:
    """The data fixture was extracted from the queue-call regex, not hand-curated."""
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    universe = load_script_module(
        "quality_label_universe_for_gate_list_fixture",
        scripts / "quality_label_universe.py",
    )
    declared = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    rows = [gate for phase in declared["phases"] for gate in phase["gates"]]
    assert rows
    assert all(isinstance(gate["command"], list) and gate["command"] for gate in rows)
    declared_labels = list(dict.fromkeys(gate["label"] for gate in rows))
    # The shell queue is gone (#769 R2b): the declared list is the source, so the
    # fixture is compared with the live declaration through the same reader.
    live = universe.quality_gate_rows(ROOT) or []
    live_labels = list(dict.fromkeys(row["label"] for row in live))
    assert set(declared_labels).symmetric_difference(live_labels) == set()
    assert declared_labels == live_labels

    captured = yaml.safe_load(CAPTURED.read_text(encoding="utf-8"))
    assert captured["sources"]["queue_call_sites"] == declared_labels
