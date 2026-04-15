from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_quality_handoff_reports_missing_fields(tmp_path: Path) -> None:
    artifact = tmp_path / "quality.md"
    artifact.write_text(
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-15",
                "",
                "## Recommended Next Gates",
                "",
                "- passive `NON_AUTOMATABLE`: decide whether the review stays manual because it needs judgment.",
                "",
                "## History",
                "",
                "- [archive](history/demo.md)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/inventory_quality_handoff.py", "--artifact", str(artifact), "--json")

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "advisory"
    assert report["findings"][0]["type"] == "missing_hitl_handoff"
    assert "review_question" in report["findings"][0]["missing_fields"]
    assert "revisit_cadence" in report["findings"][0]["missing_fields"]


def test_inventory_quality_handoff_accepts_hitl_handoff_shape(tmp_path: Path) -> None:
    artifact = tmp_path / "quality.md"
    artifact.write_text(
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-15",
                "",
                "## Recommended Next Gates",
                "",
                "- passive `NON_AUTOMATABLE`: decide rolling digest policy because current behavior is latest-only.",
                "  HITL handoff: target=`recent-lessons.md`; review_question=`Should selected traps persist?`;",
                "  decision_needed=`choose latest-only or rolling`; must_not_auto_decide=`policy`; observation_point=`three retros`; revisit_cadence=`after three retros`; automation_candidate=`digest retention validator`.",
                "",
                "## History",
                "",
                "- [archive](history/demo.md)",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/inventory_quality_handoff.py", "--artifact", str(artifact), "--json")

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["findings"] == []
