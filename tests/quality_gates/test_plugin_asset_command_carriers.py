from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT

_gate = import_repo_module(
    ROOT / "tools" / "check_plugin_asset_command_carriers.py",
    "tools.check_plugin_asset_command_carriers",
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


def test_scalar_asset_values_are_ignored_by_recursive_string_walk(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"enabled": True, "retries": 2, "command": "python3 <plugin-dir>/skills/quality/scripts/run.py"}),
    )

    assert _gate.scan_assets(repo) == (1, [])


def test_unsupported_authoring_target_is_defensive_failure() -> None:
    with pytest.raises(AssertionError, match="unsupported authoring target"):
        _gate._source_and_shipped("skills/shared/scripts/helper.py")


def test_main_emits_success_and_finding_verdicts(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _repo(tmp_path)
    _write(
        repo / "plugins/charness/integrations/tools/tool.json",
        json.dumps({"command": "python3 skills/public/quality/scripts/run.py"}),
    )

    monkeypatch.setattr(sys, "argv", ["check_plugin_asset_command_carriers.py", "--repo-root", str(repo)])
    assert _gate.main() == 1
    captured = capsys.readouterr()
    assert "Unreachable command carriers" in captured.err
    assert "authoring-only kind-bearing layout" in captured.err

    # An empty mirror is a real discovered-empty answer: the tree was there and
    # held no structured asset. It still passes, and it still says "0".
    clean_repo = tmp_path / "clean"
    (clean_repo / "plugins").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["check_plugin_asset_command_carriers.py", "--repo-root", str(clean_repo)])
    assert _gate.main() == 0
    assert "Validated 0 shipped JSON/YAML asset(s)" in capsys.readouterr().out


def test_an_absent_mirror_is_unestablished_scope_not_a_clean_verdict(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The asymmetry the gate lacked: no mirror is not the same as an empty one.

    While `/plugins/` was gitignored and this gate scoped through the git listing,
    it reported "Validated 0 shipped JSON/YAML asset(s)" and exit 0 against a
    complete 58-asset mirror. A verdict that cannot tell a full subject from an
    absent one is not a verdict, so absence must refuse.
    """
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.setattr(sys, "argv", ["check_plugin_asset_command_carriers.py", "--repo-root", str(bare)])

    assert _gate.main() == 1
    captured = capsys.readouterr()
    assert "status: unestablished" in captured.err
    assert "sync_root_plugin_manifests.py" in captured.err
    assert "Validated" not in captured.out


def test_script_entrypoint_exits_with_main_status(tmp_path: Path, monkeypatch) -> None:
    clean_repo = tmp_path / "clean"
    (clean_repo / "plugins").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["check_plugin_asset_command_carriers.py", "--repo-root", str(clean_repo)])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(ROOT / "tools" / "check_plugin_asset_command_carriers.py"), run_name="__main__")
    assert raised.value.code == 0
