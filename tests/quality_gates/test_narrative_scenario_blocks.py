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


def test_narrative_resolve_adapter_preserves_scenario_surface_fields(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "narrative-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: skill-outputs/narrative",
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
