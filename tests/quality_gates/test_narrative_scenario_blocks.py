from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_narrative_skill_carries_scenario_block_guidance() -> None:
    skill_text = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(encoding="utf-8")
    scenario_blocks = (
        ROOT / "skills" / "public" / "narrative" / "references" / "scenario-blocks.md"
    ).read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "narrative" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")

    assert "scenario_surfaces" in skill_text
    assert "checked-in fixtures" in skill_text
    assert "define it inline at first use" in skill_text
    assert "What you bring" in scenario_blocks
    assert "Input (CLI)" in scenario_blocks
    assert "Input (For Agent)" in scenario_blocks
    assert "What comes back" in scenario_blocks
    assert "Next action" in scenario_blocks
    assert "Do not fabricate a CLI slot" in scenario_blocks
    assert "scenario_block_template" in adapter_contract


def test_narrative_skill_carries_landing_rewrite_contract() -> None:
    skill_text = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(encoding="utf-8")
    landing_loop = (
        ROOT / "skills" / "public" / "narrative" / "references" / "landing-rewrite-loop.md"
    ).read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "narrative" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")

    assert "primary reader context" in skill_text
    assert "claim-to-acceptance/spec matrix" in skill_text
    assert "Compression" in skill_text
    assert "review_adapter.py" in skill_text
    assert "comparables" in landing_loop
    assert "Tension And Decision Logs" in landing_loop
    assert "narrative -> operator acceptance -> executable spec -> implementation" in landing_loop
    assert "Do any two sections assert contradictory requirements?" in landing_loop
    assert "Adapter Fitness Review" in adapter_contract
    assert "present adapter" in adapter_contract
    assert "not automatically a good adapter" in adapter_contract


def test_narrative_resolve_adapter_preserves_scenario_surface_fields(tmp_path: Path) -> None:
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

    result = run_script("skills/public/narrative/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["data"]["scenario_surfaces"] == ["Chatbot Regression", "Workflow Recovery"]
    assert payload["data"]["scenario_block_template"] == [
        "What You Bring",
        "Input (CLI)",
        "What Comes Back",
        "Next Action",
    ]


def test_narrative_review_adapter_reports_missing_adapter_for_first_touch_work(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = run_script("skills/public/narrative/scripts/review_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
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
                "- docs/handoff.md",
                "- docs/user-test/260422/internal-ios-trial.md",
                "mutable_documents:",
                "- README.md",
                "- docs/handoff.md",
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

    result = run_script("skills/public/narrative/scripts/review_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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


def test_narrative_init_adapter_does_not_seed_handoff_as_default_source(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    result = run_script("skills/public/narrative/scripts/init_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    adapter_text = (repo / ".agents" / "narrative-adapter.yaml").read_text(encoding="utf-8")
    assert "README.md" in adapter_text
    assert "docs/roadmap.md" in adapter_text
    assert "docs/handoff.md" not in adapter_text
