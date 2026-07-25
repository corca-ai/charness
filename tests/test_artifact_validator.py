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

def test_scaffold_hint_names_the_owning_scaffold_command() -> None:
    # A violation report that names only WHAT is wrong makes the author rediscover
    # the shape one failed run at a time; the hint names the command that emits it.
    for artifact_type, scaffold in (
        ("debug", "skills/public/debug/scripts/scaffold_debug_artifact.py"),
        ("critique", "skills/public/critique/scripts/scaffold_critique_artifact.py"),
        ("retro", "skills/public/retro/scripts/scaffold_retro_artifact.py"),
        ("ideation", "skills/public/ideation/scripts/scaffold_ideation_artifact.py"),
    ):
        hint = _artifact_validator.scaffold_hint(artifact_type)
        assert hint is not None
        assert f"python3 {scaffold} --repo-root ." in hint


def test_scaffold_hint_is_absent_for_an_unregistered_type() -> None:
    assert _artifact_validator.scaffold_hint("not-a-registered-artifact-type") is None


def test_report_validation_failure_emits_the_hint_once(capsys) -> None:
    code = _artifact_validator.report_validation_failure(
        "2 debug artifact rule violation(s):\n- a\n- b", artifact_type="debug"
    )
    err = capsys.readouterr().err
    assert code == 1  # hint only; the verdict and exit code are unchanged
    assert err.count("hint: start from the owning scaffold") == 1


def test_validate_max_lines_points_at_the_scaffold_budget() -> None:
    with pytest.raises(_artifact_validator.ValidationError) as excinfo:
        _artifact_validator.validate_max_lines(
            ["x"] * 240, max_lines=180, artifact_label="debug artifact", artifact_type="debug"
        )
    assert "`size_budget.max_lines`" in str(excinfo.value)
