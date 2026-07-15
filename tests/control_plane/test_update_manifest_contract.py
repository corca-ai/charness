from __future__ import annotations

import json
from pathlib import Path

from scripts.install_provenance_lib import package_manager_update_action

ROOT = Path(__file__).resolve().parents[2]


def load_manifest(tool_id: str) -> dict[str, object]:
    return json.loads((ROOT / "integrations" / "tools" / f"{tool_id}.json").read_text(encoding="utf-8"))


def test_updates_do_not_guess_an_unrecognized_path_installer() -> None:
    for tool_id in ("gitleaks", "ruff", "specdown"):
        manifest = load_manifest(tool_id)
        assert manifest["lifecycle"]["update"]["mode"] == "manual"
        assert package_manager_update_action(
            manifest,
            {"status": "detected", "install_method": "path"},
        ) is None


def test_gitleaks_go_update_uses_its_canonical_module_path() -> None:
    action = package_manager_update_action(
        load_manifest("gitleaks"),
        {"status": "detected", "install_method": "go"},
    )

    assert action == {
        "mode": "package_manager",
        "package_manager": "go",
        "package_name": "github.com/zricethezav/gitleaks/v8",
        "commands": ["go install github.com/zricethezav/gitleaks/v8@latest"],
        "notes": [
            "The upstream Go module keeps the historical `github.com/zricethezav/gitleaks/v8` module path."
        ],
    }


def test_gitleaks_install_does_not_upgrade_a_path_discovered_homebrew_package() -> None:
    command = load_manifest("gitleaks")["lifecycle"]["install"]["commands"][0]

    assert "brew install gitleaks" in command
    assert "brew upgrade" not in command
