from __future__ import annotations

from pathlib import Path

import pytest

from scripts.artifacts.artifact_validator import ValidationError
from scripts.gates.validate_ideation_artifact import validate_structured_questions
from tests.quality_gates.support import run_script

_PRELUDE = "# Demo Ideation\n\n"


def _seed(repo: Path, body: str) -> Path:
    artifact = repo / "charness-artifacts" / "ideation" / "demo.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


def test_validate_ideation_structured_questions() -> None:
    path = Path("demo.md")
    validate_structured_questions(
        path,
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: tenancy decides data model\n"
        + "- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: cache TTL tuned later\n\n",
    )
    validate_structured_questions(path, _PRELUDE + "## Open Questions\n\n- prose only, no schema\n")
    refusals = (
        (
            "- Q1 | urgency: critical | depends-on: null | action: spec | note: bad urgency\n",
            "unknown urgency",
        ),
        (
            "- Q1 | urgency: defer | depends-on: null | action: ship | note: bad action\n",
            "unknown action",
        ),
        (
            "- Q1 | urgency: defer | action: hold | note: missing depends-on\n",
            "missing required field `depends-on`",
        ),
        (
            "- Q1 | urgency: defer | depends-on: null | action: hold | note: first\n"
            "- Q1 | urgency: defer | depends-on: null | action: hold | note: dup\n",
            "duplicate id",
        ),
    )
    for bullet, match in refusals:
        with pytest.raises(ValidationError, match=match):
            validate_structured_questions(path, _PRELUDE + "## Structured Questions\n\n" + bullet + "\n")


def test_validate_ideation_artifact_no_artifacts_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "ideation").mkdir(parents=True)
    result = run_script("scripts/gates/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr
    assert "Validated 0 ideation artifact(s)." in result.stdout


def test_validate_ideation_artifact_uses_changed_path_discovery(tmp_path: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(tmp_path / "repo", {"README.md": "seed\n"})
    _seed(
        repo,
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: defer | depends-on: null | action: hold | note: later\n",
    )

    result = run_script("scripts/gates/validate_ideation_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "Validated 1 ideation artifact(s)." in result.stdout


def test_validate_ideation_reports_every_failing_artifact_in_one_pass(tmp_path: Path) -> None:
    """Two bad artifacts in one batch both get named, not just the first.

    validate_ideation_artifact runs a single rule, so one-pass here is a
    cross-ARTIFACT property: aborting on the first bad file hid the rest of the
    batch behind one edit.
    """
    repo = tmp_path / "repo"
    bad = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: nonsense | depends-on: null | action: spec | note: bad urgency\n\n"
    )
    for name in ("first.md", "second.md"):
        artifact = repo / "charness-artifacts" / "ideation" / name
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(bad, encoding="utf-8")
    result = run_script(
        "scripts/gates/validate_ideation_artifact.py",
        "--repo-root",
        str(repo),
        "--all",
        real_process=True,
    )
    assert result.returncode == 1
    assert "first.md" in result.stderr
    assert "second.md" in result.stderr
    assert "scaffold_ideation_artifact.py" in result.stderr


def test_validate_ideation_fail_fast_stops_at_the_first_failing_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bad = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: nonsense | depends-on: null | action: spec | note: bad urgency\n\n"
    )
    for name in ("first.md", "second.md"):
        artifact = repo / "charness-artifacts" / "ideation" / name
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(bad, encoding="utf-8")
    result = run_script(
        "scripts/gates/validate_ideation_artifact.py", "--repo-root", str(repo), "--all", "--fail-fast"
    )
    assert result.returncode == 1
    assert "second.md" not in result.stderr
