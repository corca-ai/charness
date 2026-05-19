from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from .support import ROOT, run_script

jsonschema = pytest.importorskip("jsonschema")

SCRIPT = "skills/public/setup/scripts/seed_usage_episodes_adapter.py"


def test_seed_usage_episodes_dry_run_validates_against_manifest_schema() -> None:
    result = run_script(SCRIPT, "--dry-run")

    assert result.returncode == 0, result.stderr
    rendered = yaml.safe_load(result.stdout)
    schema = json.loads(
        (ROOT / "integrations" / "usage-episodes" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(rendered, schema)


def test_seed_usage_episodes_writes_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCRIPT, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    target = repo / ".agents" / "usage-episodes-adapter.yaml"
    assert target.is_file()
    assert "usage_episode" in target.read_text(encoding="utf-8")


def test_seed_usage_episodes_refuses_overwrite_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    first = run_script(SCRIPT, "--repo-root", str(repo))
    assert first.returncode == 0, first.stderr

    second = run_script(SCRIPT, "--repo-root", str(repo))

    assert second.returncode == 1
    assert "force" in second.stderr


def test_seed_usage_episodes_force_overwrites(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / ".agents" / "usage-episodes-adapter.yaml"
    target.parent.mkdir()
    target.write_text("version: 1\nenabled: false\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--force")

    assert result.returncode == 0, result.stderr
    assert "enabled: true" in target.read_text(encoding="utf-8")


def test_usage_episodes_are_skill_level_setup_and_quality_contracts() -> None:
    setup_skill = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    setup_seams = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8")
    quality_skill = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

    assert "bootstrap-seams.md" in setup_skill
    assert "`<repo-root>/.agents/usage-episodes-adapter.yaml`" in setup_seams
    assert "setup implementation uses" in setup_seams
    assert "not a user-facing API" in setup_seams
    assert "run `quality` for the validation gate" in setup_seams
    assert "resolve and run the Charness package-root validator `validate_usage_episodes.py`" in quality_skill
    assert "`no_adapter` and `disabled` are skipped warnings, not failures" in quality_skill
    assert 'queue_selected "validate-usage-episodes" python3 scripts/validate_usage_episodes.py' in run_quality
