from __future__ import annotations

from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_artifact_validator = import_repo_module(
    ROOT / "scripts" / "artifact_validator.py",
    "scripts.artifact_validator",
)


def test_validate_max_lines_reports_actual_count_and_overage() -> None:
    # An over-budget artifact must name the actual line count and the overage so a
    # run trims in one pass instead of a manual wc-l loop against an unseen ceiling.
    with pytest.raises(_artifact_validator.ValidationError) as excinfo:
        _artifact_validator.validate_max_lines(["x"] * 205, max_lines=180, artifact_label="debug artifact")
    message = str(excinfo.value)
    assert "should stay concise" in message  # substring other gates match on
    assert "205 lines" in message
    assert "under 180" in message
    assert "cut ~25" in message


def test_validate_max_lines_accepts_within_budget() -> None:
    _artifact_validator.validate_max_lines(["x"] * 180, max_lines=180, artifact_label="debug artifact")
