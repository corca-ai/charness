from __future__ import annotations

import json
from pathlib import Path

from .support import run_script, write_executable


def test_inventory_cli_side_effect_probes_flags_missing_mutation_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract_path = repo / ".agents" / "cli-side-effect-probes.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "node ./bin/ceal apply",
                        "mutating": True,
                        "positional_args": ["instance"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert "mutating_command_missing_help_probe" in finding_types
    assert "mutating_command_missing_option_like_positional_probe" in finding_types
    assert "mutating_command_missing_dry_run_or_plan" in finding_types
    assert "mutating_command_missing_side_effect_watch" in finding_types


def test_inventory_cli_side_effect_probes_accepts_complete_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract_path = repo / "docs" / "cli-side-effect-probes.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "node ./bin/ceal apply",
                        "mutating": True,
                        "positional_args": ["instance"],
                        "help_probe": "node ./bin/ceal apply --help",
                        "option_like_positional_probes": [
                            "node ./bin/ceal apply --help",
                            "node ./bin/ceal apply --not-an-instance",
                        ],
                        "dry_run_probe": "node ./bin/ceal apply --dry-run demo",
                        "side_effect_watch_paths": ["~/.ceal", "/etc/systemd/system"],
                    },
                    {
                        "command": "node ./bin/ceal version",
                        "mutating": False,
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"] == []
    assert payload["contracts"][0]["command_count"] == 2


def test_inventory_cli_side_effect_probes_accepts_dry_run_waiver(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract_path = repo / "cli-side-effect-probes.json"
    repo.mkdir()
    contract_path.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "demo uninstall",
                        "mutating": True,
                        "help_probe": "demo uninstall --help",
                        "dry_run_waiver": "Uninstall only removes an isolated temporary test install.",
                        "side_effect_watch_paths": ["~/.demo"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"] == []


def test_inventory_cli_side_effect_probes_flags_missing_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"][0]["type"] == "cli_side_effect_probe_contract_missing"

    failing_result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--fail-on-findings",
    )
    assert failing_result.returncode == 1


def test_inventory_cli_side_effect_probes_executes_safe_fixture_and_flags_mutation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bin_dir = repo / "bin"
    bin_dir.mkdir(parents=True)
    write_executable(
        bin_dir / "demo",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "apply" && "${2:-}" == "--help" ]]; then',
                "  mkdir -p state",
                "  echo mutated > state/help",
                "  exit 0",
                "fi",
                'if [[ "${1:-}" == "apply" && "${2:-}" == "--not-an-instance" ]]; then',
                "  exit 2",
                "fi",
                'if [[ "${1:-}" == "apply" && "${2:-}" == "--dry-run" ]]; then',
                "  exit 0",
                "fi",
                "exit 0",
                "",
            ]
        ),
    )
    contract_path = repo / "cli-side-effect-probes.json"
    contract_path.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "./bin/demo apply",
                        "mutating": True,
                        "safe_to_execute": True,
                        "positional_args": ["instance"],
                        "help_probe": "./bin/demo apply --help",
                        "option_like_positional_probes": ["./bin/demo apply --not-an-instance"],
                        "dry_run_probe": "./bin/demo apply --dry-run sample",
                        "side_effect_watch_paths": ["state"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_cli_side_effect_probes.py",
        "--repo-root",
        str(repo),
        "--execute-probes",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"][0]["type"] == "probe_changed_side_effect_watch"
    assert payload["findings"][0]["probe_type"] == "help_probe"
