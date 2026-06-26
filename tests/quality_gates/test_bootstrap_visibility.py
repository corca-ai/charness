from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import load_path_module

from .support import ROOT, run_script

FIND_SKILLS_SCRIPT = "skills/public/find-skills/scripts/resolve_adapter.py"
ANNOUNCEMENT_SCRIPT = "skills/public/announcement/scripts/resolve_adapter.py"
_find_skills_resolve_adapter = load_path_module(
    "skills.public.find_skills.scripts.resolve_adapter",
    ROOT / FIND_SKILLS_SCRIPT,
)
_announcement_resolve_adapter = load_path_module(
    "skills.public.announcement.scripts.resolve_adapter",
    ROOT / ANNOUNCEMENT_SCRIPT,
)


def run_resolve_adapter(monkeypatch, capsys, script: str, module: object, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [script, *args])
    code = module.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_narrative_resolve_adapter_fallback_prefers_richer_truth_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "master-plan.md").write_text("# Master Plan\n", encoding="utf-8")
    (repo / "docs" / "specs" / "index.spec.md").write_text("# Specs\n", encoding="utf-8")
    (repo / "docs" / "specs" / "current-product.spec.md").write_text("# Current Product\n", encoding="utf-8")
    (repo / "docs" / "consumer-readiness.md").write_text("# Consumer Readiness\n", encoding="utf-8")
    (repo / "docs" / "external-consumer-onboarding.md").write_text("# Onboarding\n", encoding="utf-8")

    result = run_script("skills/public/narrative/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["data"]["source_documents"][:5] == [
        "README.md",
        "docs/master-plan.md",
        "docs/specs/index.spec.md",
        "docs/specs/current-product.spec.md",
        "docs/consumer-readiness.md",
    ]
    assert "charness-artifacts/narrative/latest.md" in payload["warnings"][1]
    assert "pin .agents/narrative-adapter.yaml" in payload["warnings"][2]


def test_find_skills_resolve_adapter_explains_local_first_boundary(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_resolve_adapter(
        monkeypatch,
        capsys,
        FIND_SKILLS_SCRIPT,
        _find_skills_resolve_adapter,
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/find-skills/latest.md"
    assert "local-first capability inventory" in payload["bootstrap_expectations"]["what_you_get_after_one_run"]
    assert "does not search arbitrary external registries" in payload["bootstrap_expectations"]["what_this_does_not_do"]
    assert "stays inside this repo" in payload["warnings"][2]


def test_announcement_resolve_adapter_explains_draft_only_defaults(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_resolve_adapter(
        monkeypatch,
        capsys,
        ANNOUNCEMENT_SCRIPT,
        _announcement_resolve_adapter,
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/announcement/latest.md"
    assert payload["record_path"] == ".charness/announcement/announcements.jsonl"
    assert "visible draft artifact" in payload["warnings"][1]
    assert "delivery_kind defaults to `none`" in payload["warnings"][3]
    assert "draft-only" in payload["bootstrap_expectations"]["what_this_does_not_do"]
