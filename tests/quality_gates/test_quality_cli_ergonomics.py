from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_cli_ergonomics_flags_flat_help_registry(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry_path = repo / "internal" / "cli" / "command-registry.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        json.dumps(
            {
                "commands": [{"path": [f"command-{index}"]} for index in range(12)],
                "usage": [f"demo command-{index}" for index in range(12)],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"][0]["type"] == "flat_help_without_grouping"
    assert payload["findings"][0]["command_count"] == 12


def test_inventory_cli_ergonomics_flags_cross_archetype_contract_overlap(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract_path = repo / "docs" / "command-archetypes.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "subcommand": "demo scenario normalize skill",
                        "accepted_schema_ids": [
                            "demo.skill_inputs.v1",
                            "demo.workflow_inputs.v1",
                        ],
                        "example_fixtures": [
                            "fixtures/chatbot-input.json",
                        ],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert "cross_archetype_schema_overlap" in finding_types
    assert "fixture_schema_namespace_mismatch" in finding_types
