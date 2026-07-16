from __future__ import annotations

import json
from pathlib import Path

from scripts.install_provenance_lib import package_manager_update_action

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / "integrations" / "tools"


def load_manifest(tool_id: str) -> dict[str, object]:
    return json.loads((MANIFEST_DIR / f"{tool_id}.json").read_text(encoding="utf-8"))


def iter_manifests() -> list[dict[str, object]]:
    manifests = []
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        if path.name == "manifest.schema.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data.get("lifecycle"), dict):
            manifests.append(data)
    return manifests


def test_updates_do_not_guess_an_unrecognized_path_installer() -> None:
    for tool_id in ("gitleaks", "ruff", "specdown", "glow", "tokei", "vulture"):
        manifest = load_manifest(tool_id)
        assert manifest["lifecycle"]["update"]["mode"] == "manual"
        assert package_manager_update_action(
            manifest,
            {"status": "detected", "install_method": "path"},
        ) is None


def test_no_script_update_branches_on_whichever_installer_is_on_path() -> None:
    """The docs/control-plane.md contract: an update never guesses an installer
    from whatever other package manager happens to be on PATH. A script-mode
    update may run one canonical command; it may not `command -v`-branch
    across managers."""
    script_updates = []
    for manifest in iter_manifests():
        update = manifest["lifecycle"].get("update", {})
        if update.get("mode") != "script":
            continue
        script_updates.append(manifest["tool_id"])
        for command in update.get("commands", []):
            assert "command -v" not in command, (
                f"{manifest['tool_id']} update script guesses an installer from PATH: {command}"
            )
    # The known canonical single-command script updates; growth here is fine,
    # but a tool moving back from manual to script deserves a deliberate look.
    assert set(script_updates) <= {"agent-browser", "defuddle", "nose"}


def test_recognized_provenance_still_routes_glow_and_tokei_updates() -> None:
    glow_action = package_manager_update_action(
        load_manifest("glow"), {"status": "detected", "install_method": "go"}
    )
    assert glow_action is not None
    assert glow_action["commands"] == ["go install github.com/charmbracelet/glow/v2@latest"]

    tokei_action = package_manager_update_action(
        load_manifest("tokei"), {"status": "detected", "install_method": "cargo"}
    )
    assert tokei_action is not None
    assert tokei_action["commands"] == ["cargo install tokei --force"]


def test_vulture_update_is_manual_always_because_uv_pipx_pip_are_not_provenance_keys() -> None:
    manifest = load_manifest("vulture")
    for install_method in ("path", "uv", "pipx", "pip", "npm", "cargo", "go"):
        assert package_manager_update_action(
            manifest, {"status": "detected", "install_method": install_method}
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
