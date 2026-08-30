from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import yaml

from .seeding_support import load_module, write_quality_adapter

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/quality/scripts/inventory_cli_ergonomics.py"
inventory_cli = load_module("inventory_cli_ergonomics", SCRIPT)
VisibleRepoFilesSnapshot = sys.modules["git_inventory_lib"].VisibleRepoFilesSnapshot


def run_inventory(*args: str, real_inventory: bool = False) -> dict[str, object]:
    old_argv = sys.argv[:]
    stdout = io.StringIO()
    original_capture = inventory_cli.capture_visible_repo_files
    if not real_inventory:
        # Matrix fixtures are uncommitted; use the explicit non-git fallback view
        # and reserve one test for the real inventory boundary.
        inventory_cli.capture_visible_repo_files = lambda _repo: VisibleRepoFilesSnapshot(None)
    try:
        sys.argv = [str(SCRIPT), *args]
        with contextlib.redirect_stdout(stdout):
            assert inventory_cli.main() == 0
    finally:
        inventory_cli.capture_visible_repo_files = original_capture
        sys.argv = old_argv
    return yaml.safe_load(stdout.getvalue())


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
        "--detail",
    )
    assert payload["findings"][0]["type"] == "flat_help_without_grouping"
    assert payload["findings"][0]["command_count"] == 12


def test_inventory_cli_ergonomics_reports_unconfigured_when_nothing_to_scan(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--detail",
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
    write_quality_adapter(
        repo,
        [
            "vendored_paths:",
            "  - packages/official-skills/charness-public",
        ],
    )

    payload = run_inventory(
        "--repo-root",
        str(repo),
        "--detail",
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
        "--detail",
    )
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert "cross_archetype_schema_overlap" in finding_types
    assert "fixture_schema_namespace_mismatch" in finding_types


def test_committed_cli_ergonomics_inputs_are_scanned_clean() -> None:
    payload = run_inventory(
        "--repo-root",
        str(ROOT),
        "--detail",
        real_inventory=True,
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
