from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

RESOLVE_SCRIPT = "skills/public/narrative/scripts/resolve_adapter.py"
REVIEW_SCRIPT = "skills/public/narrative/scripts/review_adapter.py"
INIT_SCRIPT = "skills/public/narrative/scripts/init_adapter.py"
_resolve_adapter = import_repo_module(ROOT / RESOLVE_SCRIPT, "skills.public.narrative.scripts.resolve_adapter")
_review_adapter = import_repo_module(ROOT / REVIEW_SCRIPT, "skills.public.narrative.scripts.review_adapter")
_init_adapter = import_repo_module(ROOT / INIT_SCRIPT, "skills.public.narrative.scripts.init_adapter")


def run_narrative_resolve_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [RESOLVE_SCRIPT, *args])
    code = _resolve_adapter.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def run_narrative_review_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [REVIEW_SCRIPT, *args])
    code = _review_adapter.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def run_narrative_init_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [INIT_SCRIPT, *args])
    code = _init_adapter.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_narrative_resolve_adapter_preserves_scenario_surface_fields(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "narrative-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/narrative",
                "source_documents:",
                "- README.md",
                "mutable_documents:",
                "- README.md",
                "brief_template:",
                "- One-Line Summary",
                "scenario_surfaces:",
                "- Chatbot Regression",
                "- Workflow Recovery",
                "scenario_block_template:",
                "- What You Bring",
                "- Input (CLI)",
                "- What Comes Back",
                "- Next Action",
                "remote_name: origin",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_narrative_resolve_adapter(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["data"]["scenario_surfaces"] == ["Chatbot Regression", "Workflow Recovery"]
    assert payload["data"]["scenario_block_template"] == [
        "What You Bring",
        "Input (CLI)",
        "What Comes Back",
        "Next Action",
    ]


def test_narrative_review_adapter_reports_missing_adapter_for_first_touch_work(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = run_narrative_review_adapter(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "needs-repair"
    assert payload["adapter"]["found"] is False
    assert any(finding["type"] == "missing_adapter" for finding in payload["findings"])


def test_narrative_review_adapter_flags_volatile_and_missing_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "guides").mkdir()
    (repo / "docs" / "user-test" / "260422").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Index\n", encoding="utf-8")
    (repo / "docs" / "guides" / "missing-guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "user-test" / "260422" / "internal-ios-trial.md").write_text(
        "# Internal Trial\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "narrative-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/narrative",
                "source_documents:",
                "- README.md",
                "- docs/index.md",
                "- docs/user-test/260422/internal-ios-trial.md",
                "mutable_documents:",
                "- README.md",
                "- docs/index.md",
                "- docs/user-test/260422/internal-ios-trial.md",
                "brief_template:",
                "- One-Line Summary",
                "special_entrypoints:",
                "- docs/missing-guide.md",
                "- docs/guides/missing-guide.md",
                "remote_name: origin",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(REVIEW_SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert payload["status"] == "needs-repair"
    assert "missing_adapter_path" in finding_types
    assert "volatile_source_document" in finding_types
    assert "volatile_mutable_document" in finding_types
    assert "entrypoint_not_in_sources" in finding_types
    volatile_paths = {
        finding["path"] for finding in payload["findings"] if finding["type"] == "volatile_source_document"
    }
    assert "docs/user-test/260422/internal-ios-trial.md" in volatile_paths
    missing_path_finding = next(finding for finding in payload["findings"] if finding["type"] == "missing_adapter_path")
    assert "Closest existing path: `docs/guides/missing-guide.md`" in missing_path_finding["recommended_action"]


def test_narrative_init_adapter_does_not_seed_docs_index_as_default_source(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    result = run_narrative_init_adapter(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    adapter_text = (repo / ".agents" / "narrative-adapter.yaml").read_text(encoding="utf-8")
    assert "README.md" in adapter_text
    assert "docs/roadmap.md" in adapter_text
