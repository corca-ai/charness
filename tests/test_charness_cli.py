from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "charness"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_charness_init_exports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugin_root"] == str(home_root / ".codex" / "plugins" / "charness")
    assert payload["cli_path"] == str(home_root / ".local" / "bin" / "charness")
    assert payload["claude_wrapper_path"] == str(home_root / ".local" / "bin" / "claude-charness")
    assert payload["checkout"]["repo_root"] == str(ROOT)
    assert (
        payload["next_steps"]["codex"]
        == "Restart Codex from the home root so it reloads the personal marketplace. If `charness` is still unavailable, install or enable it from Plugin Directory."
    )
    marketplace = json.loads((home_root / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    plugin_entry = marketplace["plugins"][0]
    assert plugin_entry["name"] == "charness"
    assert plugin_entry["source"]["path"] == "./.codex/plugins/charness"
    assert (home_root / ".local" / "bin" / "charness").is_file()
    assert (home_root / ".local" / "bin" / "claude-charness").is_file()


def test_charness_doctor_reports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
    )
    assert init_result.returncode == 0, init_result.stderr

    doctor_result = run_cli(
        "doctor",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--json",
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["checkout_present"] is True
    assert payload["plugin_root_present"] is True
    assert payload["cli_present"] is True
    assert payload["claude_wrapper_present"] is True
    assert payload["codex_marketplace_entry"]["name"] == "charness"
    assert payload["codex_marketplace_entry"]["source"]["path"] == "./.codex/plugins/charness"
    assert payload["codex_host_guidance"]["status"] == "needs-host-install"
    assert payload["codex_host_guidance"]["manual_action_required"] is True
    assert (
        payload["codex_host_guidance"]["message"]
        == "Restart Codex from the home directory that owns "
        f"`{home_root / '.agents' / 'plugins' / 'marketplace.json'}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
    )
    assert payload["plugin_preamble"]["update_hints"]["claude"] == "Run `charness update`, then re-enter Claude through `claude-charness`."
