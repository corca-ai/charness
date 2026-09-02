from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_plugin_preamble = import_repo_module(__file__, "scripts.plugin_export.plugin_preamble")


def test_plugin_preamble_payload_includes_hints_and_readiness() -> None:
    payload = _plugin_preamble.build_payload(ROOT, ROOT)
    assert payload["package_id"] == "charness"
    assert payload["runtime_self_update"] is False
    # The deleted `print_text` was the only place the operator-facing
    # "RUNTIME_SELF_UPDATE: disabled" state was spelled; it is a payload key now.
    assert payload["runtime_self_update_attention"] == "RUNTIME_SELF_UPDATE: disabled"
    assert payload["root_install_surface"]["ok"] is True
    assert payload["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."
    assert payload["update_hints"]["codex"] == (
        "Run `charness init` or `charness update`; both try Codex's official plugin/install path when the Codex CLI is available. "
        "Restart Codex only if the host state still needs to reload the installed plugin."
    )
    assert payload["update_hints"]["grok"] == (
        "Run `charness update`, then restart Grok Build. Grok loads `~/.grok/plugins/charness` when `[plugins].enabled` lists `charness`. No marketplace step."
    )
    assert isinstance(payload["readiness"], list)
    assert any(entry["tool_id"] == "agent-browser" for entry in payload["readiness"])


def test_plugin_preamble_reports_vendored_copy_warning(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    (consumer / ".claude" / "skills" / "charness").mkdir(parents=True)
    payload = _plugin_preamble.build_payload(ROOT, consumer)
    assert payload["warnings"]
    assert "vendored charness copy detected" in payload["warnings"][0]


def test_plugin_preamble_cli_emits_the_payload_as_yaml(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["plugin_preamble.py", "--repo-root", str(ROOT)])

    assert _plugin_preamble.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["package_id"] == "charness"
    assert payload["runtime_self_update_attention"] == "RUNTIME_SELF_UPDATE: disabled"
    assert payload["update_hints"]["claude"]
    assert payload["readiness"]


def test_plugin_preamble_cli_rejects_a_json_flag(monkeypatch) -> None:
    """`--json` was removed outright, so it must fail loudly, not be ignored."""
    monkeypatch.setattr(sys, "argv", ["plugin_preamble.py", "--repo-root", str(ROOT), "--json"])

    with pytest.raises(SystemExit) as excinfo:
        _plugin_preamble.main()
    assert excinfo.value.code == 2
