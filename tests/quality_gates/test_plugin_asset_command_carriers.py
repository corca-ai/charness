from __future__ import annotations

import json
from pathlib import Path

from runtime_bootstrap import import_repo_module

from .support import ROOT

_gate = import_repo_module(
    ROOT / "scripts" / "check_plugin_asset_command_carriers.py",
    "scripts.check_plugin_asset_command_carriers",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo(tmp_path: Path, *, export: bool = True) -> Path:
    repo = tmp_path / "repo"
    _write(repo / "skills/public/quality/scripts/run.py", "# source\n")
    _write(repo / "skills/public/issue/scripts/issue_tool.py", "# source\n")
    if export:
        _write(repo / "plugins/charness/skills/quality/scripts/run.py", "# shipped\n")
        _write(repo / "plugins/charness/skills/issue/scripts/issue_tool.py", "# shipped\n")
    return repo


def test_json_and_yaml_carriers_reject_authoring_layout(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"commands": ["python3 skills/public/quality/scripts/run.py --repo-root ."]}),
    )
    _write(
        repo / "plugins/charness/skills/achieve/adapter.example.yaml",
        'command: "python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft"\n',
    )

    count, findings = _gate.scan_assets(repo)

    assert count == 2
    assert len(findings) == 2
    assert any("$.commands[0]" in finding for finding in findings)
    assert any("$.command" in finding for finding in findings)


def test_interpreter_options_do_not_hide_authoring_layout(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps(
            {
                "short_option": "python3 -u skills/public/quality/scripts/run.py",
                "long_option": "python3 --isolated skills/public/issue/scripts/issue_tool.py",
            }
        ),
    )

    count, findings = _gate.scan_assets(repo)

    assert count == 1
    assert len(findings) == 2
    assert any("$.short_option" in finding for finding in findings)
    assert any("$.long_option" in finding for finding in findings)


def test_explicit_plugin_carriers_pass(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"commands": ["python3 <plugin-dir>/skills/quality/scripts/run.py"]}),
    )
    _write(
        repo / "plugins/charness/skills/achieve/adapter.example.yaml",
        'command: "python3 <plugin-dir>/skills/issue/scripts/issue_tool.py"\n',
    )

    assert _gate.scan_assets(repo) == (2, [])


def test_missing_export_is_reported_without_silencing_the_carrier(tmp_path: Path) -> None:
    repo = _repo(tmp_path, export=False)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"command": "python3 skills/public/quality/scripts/run.py"}),
    )

    count, findings = _gate.scan_assets(repo)

    assert count == 1
    assert len(findings) == 1
    assert "export missing" in findings[0]


def test_missing_authoring_source_is_reported_without_silencing_the_carrier(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "skills/public/quality/scripts/run.py").unlink()
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"command": "python3 skills/public/quality/scripts/run.py"}),
    )

    count, findings = _gate.scan_assets(repo)

    assert count == 1
    assert len(findings) == 1
    assert "authoring source missing" in findings[0]


def test_asset_outside_a_plugin_package_is_a_gate_finding(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo / "plugins/orphan.json", json.dumps({"ok": True}))

    count, findings = _gate.scan_assets(repo)

    assert count == 1
    assert len(findings) == 1
    assert "unsupported plugin asset layout" in findings[0]


def test_malformed_structured_asset_is_a_gate_finding(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo / "plugins/charness/integrations/tools/bad.yaml", "command: [\n")

    count, findings = _gate.scan_assets(repo)

    assert count == 1
    assert len(findings) == 1
    assert "cannot parse structured asset" in findings[0]
