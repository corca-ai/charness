from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_plugin_preamble_json_output_includes_hints_and_readiness() -> None:
    result = run_script("scripts/plugin_preamble.py", "--repo-root", str(ROOT), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["runtime_self_update"] is False
    assert payload["root_install_surface"]["ok"] is True
    assert payload["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."
    assert payload["update_hints"]["codex"] == (
        "Run `charness init` or `charness update`; both try Codex's official plugin/install path when the Codex CLI is available. "
        "Restart Codex only if the host state still needs to reload the installed plugin."
    )
    assert isinstance(payload["readiness"], list)
    assert any(entry["tool_id"] == "agent-browser" for entry in payload["readiness"])


def test_plugin_preamble_reports_vendored_copy_warning(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    (consumer / ".claude" / "skills" / "charness").mkdir(parents=True)
    result = run_script(
        "scripts/plugin_preamble.py",
        "--repo-root",
        str(ROOT),
        "--consumer-root",
        str(consumer),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["warnings"]
    assert "vendored charness copy detected" in payload["warnings"][0]
