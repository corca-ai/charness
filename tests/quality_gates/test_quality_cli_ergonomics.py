from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/quality/scripts/inventory_cli_ergonomics.py"
SPEC = importlib.util.spec_from_file_location("inventory_cli_ergonomics", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
inventory_cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory_cli)


def run_inventory(*args: str) -> dict[str, object]:
    old_argv = sys.argv[:]
    stdout = io.StringIO()
    try:
        sys.argv = [str(SCRIPT), *args]
        with contextlib.redirect_stdout(stdout):
            assert inventory_cli.main() == 0
    finally:
        sys.argv = old_argv
    return json.loads(stdout.getvalue())


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

    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--json",
    )
    assert payload["findings"][0]["type"] == "flat_help_without_grouping"
    assert payload["findings"][0]["command_count"] == 12


def test_inventory_cli_ergonomics_reports_unconfigured_when_nothing_to_scan(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--json",
    )
    assert payload["status"] == "unconfigured"
    assert payload["registries"] == []
    assert payload["archetype_contracts"] == []


def test_inventory_cli_ergonomics_skips_vendored_registries(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    vendored = repo / "packages" / "official-skills" / "charness-public" / "internal" / "cli"
    vendored.mkdir(parents=True)
    (vendored / "command-registry.json").write_text(
        json.dumps({"commands": [{"path": [f"command-{i}"]} for i in range(20)]}) + "\n",
        encoding="utf-8",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--json",
    )
    assert payload["status"] == "unconfigured"
    assert payload["registries"] == []


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

    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--json",
    )
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert "cross_archetype_schema_overlap" in finding_types
    assert "fixture_schema_namespace_mismatch" in finding_types


def test_committed_cli_ergonomics_inputs_are_scanned_clean() -> None:
    payload = run_inventory(
        "--repo-root",
        str(ROOT),
        "--json",
    )
    assert payload["status"] == "clean"
    assert payload["scope_classification"] == "scanned"
    assert [registry["path"] for registry in payload["registries"]] == [
        ".agents/command-registry.json"
    ]
    assert [contract["path"] for contract in payload["archetype_contracts"]] == [
        ".agents/command-archetypes.json"
    ]
    assert payload["findings"] == []
