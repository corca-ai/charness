from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

jsonschema = pytest.importorskip("jsonschema")

SCRIPT = "skills/public/setup/scripts/seed_usage_episodes_adapter.py"
TEMPLATE = (
    ROOT
    / "skills"
    / "public"
    / "setup"
    / "scripts"
    / "templates"
    / "usage_episodes_adapter.yaml"
)
_seed_usage_episodes = import_repo_module(
    ROOT / SCRIPT,
    "skills.public.setup.scripts.seed_usage_episodes_adapter",
)


def run_seed_usage_episodes(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["seed_usage_episodes_adapter.py", *args])
    returncode = _seed_usage_episodes.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_seed_usage_episodes_dry_run_validates_against_manifest_schema(monkeypatch, capsys) -> None:
    result = run_seed_usage_episodes(monkeypatch, capsys, "--dry-run")

    assert result.returncode == 0, result.stderr
    assert result.stdout == TEMPLATE.read_text(encoding="utf-8")
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
    assert target.read_text(encoding="utf-8") == TEMPLATE.read_text(encoding="utf-8")
    assert "usage_episode" in target.read_text(encoding="utf-8")


def test_seed_usage_episodes_creates_nested_parent_directories(monkeypatch, tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "seed_usage_episodes_adapter_under_test",
        ROOT / SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    repo = tmp_path / "repo"
    repo.mkdir()
    nested_target = Path(".agents") / "nested" / "usage-episodes-adapter.yaml"
    monkeypatch.setattr(module, "DEFAULT_TARGET", nested_target)
    monkeypatch.setattr(
        "sys.argv",
        ["seed_usage_episodes_adapter.py", "--repo-root", str(repo)],
    )

    assert module.main() == 0
    assert (repo / nested_target).is_file()


def test_seed_usage_episodes_refuses_overwrite_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    first = run_script(SCRIPT, "--repo-root", str(repo))
    assert first.returncode == 0, first.stderr

    second = run_script(SCRIPT, "--repo-root", str(repo))

    assert second.returncode == 1
    assert "force" in second.stderr


def test_seed_usage_episodes_force_overwrites(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / ".agents" / "usage-episodes-adapter.yaml"
    target.parent.mkdir()
    target.write_text("version: 1\nenabled: false\n", encoding="utf-8")

    result = run_seed_usage_episodes(monkeypatch, capsys, "--repo-root", str(repo), "--force")

    assert result.returncode == 0, result.stderr
    assert "enabled: true" in target.read_text(encoding="utf-8")


def test_usage_episodes_are_skill_level_setup_and_quality_contracts() -> None:
    setup_skill = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    setup_seams = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8")
    quality_skill = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    catalog = (
        ROOT / "skills" / "public" / "quality" / "references" / "catalog.yaml"
    ).read_text(encoding="utf-8")
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

    assert "bootstrap-seams.md" in setup_skill
    assert "`<repo-root>/.agents/usage-episodes-adapter.yaml`" in setup_seams
    assert "setup implementation uses" in setup_seams
    assert "not a user-facing API" in setup_seams
    assert "run `quality` for the\nvalidation/report gate" in setup_seams
    assert "Run applicable `gate_packets` as report-first evidence" in quality_skill
    assert "id: read-only-quality" in catalog
    assert 'queue_selected "validate-usage-episodes" python3 scripts/validate_usage_episodes.py' in run_quality
    assert 'queue_selected "report-usage-episodes" python3 scripts/report_usage_episodes.py' in run_quality
