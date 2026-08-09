from __future__ import annotations

import json
from pathlib import Path

import pytest

from .support import ROOT, run_script

SOURCE = "scripts/check_title_slug_drift.py"
SOURCE_SHARED = "skills/shared/scripts/check_title_slug_drift.py"
PLUGIN = "plugins/charness/scripts/check_title_slug_drift.py"
PLUGIN_SHARED = "plugins/charness/shared/scripts/check_title_slug_drift.py"


@pytest.mark.parametrize("script", [SOURCE, SOURCE_SHARED, PLUGIN, PLUGIN_SHARED])
def test_deprecated_title_slug_entrypoints_preserve_advisory_invocation(
    tmp_path: Path, script: str
) -> None:
    matching = tmp_path / "matching-title.md"
    matching.write_text("# Matching title\n", encoding="utf-8")

    result = run_script(str(ROOT / script), str(matching), "--include-skill-prose")

    assert result.returncode == 0
    assert "no title-slug drift observed in 1 files" in result.stdout
    assert "DEPRECATED:" in result.stderr


@pytest.mark.parametrize("script", [SOURCE, PLUGIN])
def test_deprecated_title_slug_entrypoint_preserves_structured_clean_shape(
    tmp_path: Path, script: str
) -> None:
    matching = tmp_path / "matching-title.md"
    matching.write_text("# Matching title\n", encoding="utf-8")

    result = run_script(str(ROOT / script), str(matching), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {
        "status": "deprecated",
        "verdict": "no-finding-observed",
        "checked": 1,
        "drift": [],
        "roots": [str(matching)],
        "replacement": "bounded rename/title coherence review",
    }


@pytest.mark.parametrize("script", [SOURCE, SOURCE_SHARED, PLUGIN, PLUGIN_SHARED])
def test_deprecated_title_slug_entrypoints_preserve_strict_verdict(
    tmp_path: Path, script: str
) -> None:
    drifted = tmp_path / "mismatched-slug.md"
    drifted.write_text("# Entirely Different\n", encoding="utf-8")

    result = run_script(str(ROOT / script), str(drifted), "--strict")

    assert result.returncode == 1
    assert "title-slug drift in 1 of 1 files" in result.stdout
    assert "DEPRECATED:" in result.stderr


def test_deprecated_title_slug_default_scope_includes_goal_records(tmp_path: Path) -> None:
    goal = tmp_path / "charness-artifacts" / "goals" / "mismatched-slug.md"
    goal.parent.mkdir(parents=True)
    goal.write_text("# Entirely Different\n", encoding="utf-8")

    result = run_script(str(ROOT / SOURCE), "--strict", cwd=tmp_path)

    assert result.returncode == 1
    assert str(goal.relative_to(tmp_path)) in result.stdout


def test_deprecated_title_slug_checker_is_not_wired_into_live_gates() -> None:
    for path in (
        ROOT / "scripts" / "run-quality.sh",
        ROOT / "scripts" / "staged_commit_gate_plan.py",
        ROOT / ".githooks" / "pre-push",
    ):
        assert "check-title-slug-drift" not in path.read_text(encoding="utf-8")


def test_deprecated_title_slug_source_and_plugin_mirrors_match() -> None:
    assert (ROOT / SOURCE).read_bytes() == (ROOT / PLUGIN).read_bytes()
    assert (ROOT / SOURCE_SHARED).read_bytes() == (ROOT / PLUGIN_SHARED).read_bytes()
