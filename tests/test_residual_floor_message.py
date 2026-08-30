"""The evidence-residual diagnostic has live callers and executable surfaces."""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.residual_floor_support import (
    MIRROR_SYNC_COMMAND,
    RESIDUAL_COMMAND,
    RESIDUAL_FLOOR_HOME,
    RESIDUAL_FLOOR_MIRROR,
    RESIDUAL_FLOOR_SYMBOL,
    RESIDUAL_MEASURE_SCRIPT,
    RESIDUAL_PROBE,
    RESIDUAL_UPDATE_SURFACES,
    residual_floor_message,
)

ROOT = Path(__file__).resolve().parent.parent


def test_the_live_message_distinguishes_a_finding_from_a_rule_change() -> None:
    message = residual_floor_message("min_residual", kind="markdown_artifacts")

    assert "THE INVARIANT BROKE" in message
    assert "Do NOT lower the floor" in message
    assert "THE FLOOR MOVED" in message
    assert "for the kind `markdown_artifacts`" in message


def test_the_residual_message_does_not_reacquire_inventory_edit_ownership() -> None:
    message = residual_floor_message("min_residual", kind="markdown_artifacts")

    for unrelated_surface in (
        "2026-08-01-inventory-consumption-floor.json",
        "2026-08-01-inventory-marker-rule.json",
        "2026-08-12-inventory-marker-rule-snapshot.json",
        "docs/deferred-decisions.md",
    ):
        assert unrelated_surface not in message


def test_the_message_names_the_actual_floor_owner() -> None:
    home = ROOT / RESIDUAL_FLOOR_HOME
    measure = ROOT / RESIDUAL_MEASURE_SCRIPT

    assert f"{RESIDUAL_FLOOR_SYMBOL} = " in home.read_text(encoding="utf-8")
    assert f"{RESIDUAL_FLOOR_SYMBOL} = " not in measure.read_text(encoding="utf-8")
    message = residual_floor_message("floor")
    assert message.index(RESIDUAL_FLOOR_HOME) < message.index("NOT in")
    assert message.index("NOT in") < message.index(f"`{RESIDUAL_MEASURE_SCRIPT}`")


def test_the_recorded_only_branch_does_not_invent_live_drift() -> None:
    message = residual_floor_message(
        "min_residual", kind="markdown_artifacts", recorded_only=True
    )

    assert "inconsistent WITHIN the recorded probe" in message
    assert "Nothing live took part" in message
    assert "min_residual_path" not in message


def test_the_residual_probe_has_the_shape_the_message_names() -> None:
    payload = json.loads((ROOT / RESIDUAL_PROBE).read_text(encoding="utf-8"))

    assert "_provenance" not in payload
    message = residual_floor_message("min_residual", kind="markdown_artifacts")
    assert "the whole file" in message
    assert "NO `_provenance`" in message
    assert "straight redirect" in message
    kind_keys = {key for kind in payload["kinds"].values() for key in kind}
    for named in re.findall(r"`kinds\[\*\]\.(\w+)`", message):
        assert named in kind_keys


def test_every_figure_bearing_surface_exists() -> None:
    probe = json.loads((ROOT / RESIDUAL_PROBE).read_text(encoding="utf-8"))
    figures = {str(kind["min_residual"]) for kind in probe["kinds"].values()}
    listed = {surface.split(" — ")[0] for surface, _ in RESIDUAL_UPDATE_SURFACES}

    for path in (RESIDUAL_PROBE, RESIDUAL_FLOOR_HOME, RESIDUAL_FLOOR_MIRROR):
        assert path in listed
        assert (ROOT / path).is_file()
    for path in (RESIDUAL_FLOOR_HOME, RESIDUAL_FLOOR_MIRROR):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert any(figure in text for figure in figures)

    paired = dict(RESIDUAL_UPDATE_SURFACES)
    mirror = next(surface for surface in paired if surface.startswith(RESIDUAL_FLOOR_MIRROR))
    assert paired[mirror] == MIRROR_SYNC_COMMAND


def test_the_quality_gate_actually_calls_the_message() -> None:
    site = (ROOT / "tests/quality_gates/test_measure_evidence_residual.py").read_text(
        encoding="utf-8"
    )

    assert site.count("residual_floor_message(") >= 5
    assert "assert code == 0, residual_floor_message(" in site
    assert RESIDUAL_COMMAND in residual_floor_message("exit_code")
