from __future__ import annotations

from pathlib import Path

from tests.quality_gates.support import run_script

_PRELUDE = "# Demo Ideation\n\n"


def _seed(repo: Path, body: str) -> Path:
    artifact = repo / "charness-artifacts" / "ideation" / "demo.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


def test_validate_ideation_structured_questions_accepts_well_formed_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: tenancy decides data model\n"
        + "- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: cache TTL tuned later\n\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_validate_ideation_structured_questions_rejects_unknown_urgency(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: critical | depends-on: null | action: spec | note: bad urgency\n\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "unknown urgency" in result.stderr


def test_validate_ideation_structured_questions_rejects_unknown_action(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: defer | depends-on: null | action: ship | note: bad action\n\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "unknown action" in result.stderr


def test_validate_ideation_structured_questions_rejects_missing_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: defer | action: hold | note: missing depends-on\n\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "missing required field `depends-on`" in result.stderr


def test_validate_ideation_structured_questions_rejects_duplicate_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Structured Questions\n\n"
        + "- Q1 | urgency: defer | depends-on: null | action: hold | note: first\n"
        + "- Q1 | urgency: defer | depends-on: null | action: hold | note: dup\n\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "duplicate id" in result.stderr


def test_validate_ideation_structured_questions_section_is_opt_in(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = _PRELUDE + "## Open Questions\n\n- prose only, no schema\n"
    _seed(repo, body)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_validate_ideation_artifact_no_artifacts_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "ideation").mkdir(parents=True)
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
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

    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo))

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
    result = run_script("scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all")
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
        "scripts/validate_ideation_artifact.py", "--repo-root", str(repo), "--all", "--fail-fast"
    )
    assert result.returncode == 1
    assert "second.md" not in result.stderr
