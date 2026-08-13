"""Adapter-owned test-file discovery for the standing-test-economics inventory.

Split out of test_standing_test_economics.py: these cover the graded-fallback
discovery contract (built-in defaults incl .mjs -> adapter patterns -> adapter
authoritative command) and its degraded-surfacing, a cohesive concern distinct
from the inventory's bucket/footprint accounting.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"


def _run_inventory_cli(*args: str, env: dict[str, str] | None = None):
    return run_loaded_script_main(
        "inventory_standing_test_economics.py",
        load_script_module("inventory_standing_test_economics_for_discovery_test", SCRIPT),
        *args,
        env=env,
    )


def _write_discovery_adapter(repo: Path, test_file_discovery: dict) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "repo": "fixture",
                "language": "en",
                "output_dir": "charness-artifacts/quality",
                "test_file_discovery": test_file_discovery,
            }
        ),
        encoding="utf-8",
    )


def _run_discovery_cli(repo: Path, tmp_path: Path, *args: str):
    # Isolate the pytest-temp probe to the fixture's own temp root so a machine's
    # retained failed sessions cannot add an environmental finding.
    return _run_inventory_cli(
        "--repo-root", str(repo), *args, env={**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    )


def test_standing_test_economics_counts_mjs_test_files_and_nested_cli(tmp_path: Path) -> None:
    # Regression for #447: Node ESM test files must contribute to the extension
    # counts AND the nested-CLI fan-out scan, not be invisible to the declared
    # standing-test-surface measurement. The pytest bucket split stays Python-only
    # by design (same as the already-included .ts/.js), so .mjs is asserted on the
    # fan-out scan, not on the pytest-marker buckets.
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "unit.test.mjs").write_text(
        "import { spawnSync } from 'node:child_process';\nspawnSync('true');\n", encoding="utf-8"
    )
    (repo / "tests" / "flow.spec.mjs").write_text("export const value = 1;\n", encoding="utf-8")
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["test_file_count"] == 3
    assert payload["test_files_by_extension"].get(".mjs") == 2
    assert "tests/unit.test.mjs" in payload["nested_cli_files"]
    assert payload["test_discovery"] == {
        "source": "default",
        "command_status": None,
        "degraded": False,
        "error": None,
    }


def test_standing_test_economics_extends_discovery_with_adapter_patterns(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "custom.integration.mjs").write_text("export const value = 1;\n", encoding="utf-8")
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"patterns": ["*.integration.mjs"], "patterns_mode": "extend"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    # extend keeps the built-in defaults (the .py file) AND adds the adapter glob.
    assert payload["test_discovery"]["source"] == "adapter-patterns"
    assert payload["test_file_count"] == 2
    assert payload["test_files_by_extension"].get(".mjs") == 1
    assert payload["test_files_by_extension"].get(".py") == 1


def test_standing_test_economics_replaces_discovery_with_adapter_patterns(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "only.spec.custom").write_text("export const value = 1;\n", encoding="utf-8")
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"patterns": ["*.spec.custom"], "patterns_mode": "replace"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    # replace drops the built-in defaults: the default .py match is excluded.
    assert payload["test_discovery"]["source"] == "adapter-patterns"
    assert payload["test_file_count"] == 1
    assert ".custom" in payload["test_files_by_extension"]
    assert ".py" not in payload["test_files_by_extension"]


def test_standing_test_economics_consumes_adapter_discovery_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "only_via_command.node").write_text(
        "import { spawnSync } from 'node:child_process';\nspawnSync('true');\n", encoding="utf-8"
    )
    # A default-glob match the authoritative command deliberately does NOT list,
    # proving the command is the source of truth (not merged with the defaults).
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"command": "echo tests/only_via_command.node"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["test_discovery"]["source"] == "command"
    assert payload["test_discovery"]["command_status"] == "ok"
    assert payload["test_discovery"]["degraded"] is False
    assert payload["test_file_count"] == 1
    assert "tests/only_via_command.node" in payload["nested_cli_files"]
    assert ".py" not in payload["test_files_by_extension"]


def test_standing_test_economics_marks_degraded_when_discovery_command_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"command": "false"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    # A broken authoritative lister must surface as a degraded measurement, not a
    # silent undercount: fall back to defaults but flag degraded with the error.
    assert payload["test_discovery"]["degraded"] is True
    assert payload["test_discovery"]["command_status"] == "failed"
    assert payload["test_discovery"]["source"] == "default"
    assert payload["test_discovery"]["error"]
    assert payload["test_file_count"] == 1

    plain = _run_discovery_cli(repo, tmp_path)
    assert plain.returncode == 0, plain.stderr
    assert "DEGRADED" in plain.stdout


def test_standing_test_economics_flags_empty_authoritative_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    # A default glob match exists, but the authoritative command lists nothing.
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"command": "true"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    # An empty authoritative surface is a degraded measurement, not a clean zero,
    # and must NOT silently fall back to the default globs (which would re-create
    # the divergence the adapter command exists to eliminate).
    assert payload["test_discovery"]["source"] == "command"
    assert payload["test_discovery"]["command_status"] == "empty"
    assert payload["test_discovery"]["degraded"] is True
    assert payload["test_file_count"] == 0

    plain = _run_discovery_cli(repo, tmp_path)
    assert plain.returncode == 0, plain.stderr
    assert "DEGRADED" in plain.stdout


def test_standing_test_economics_discovery_command_non_utf8_degrades_without_crash(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    # A lister emitting a non-UTF-8 byte must degrade, never crash the inventory
    # (UnicodeDecodeError is a ValueError, outside the subprocess-error catch).
    _write_discovery_adapter(repo, {"command": "printf '\\377\\n'"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["test_discovery"]["source"] == "command"
    assert payload["test_discovery"]["degraded"] is True


def test_standing_test_economics_surfaces_invalid_discovery_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_py.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _write_discovery_adapter(repo, {"patterns_mode": "bogus"})

    result = _run_discovery_cli(repo, tmp_path, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["adapter_valid"] is False
    assert any("patterns_mode" in error for error in payload["adapter_errors"])
    # inventory still runs on validated defaults rather than going dark.
    assert payload["test_file_count"] == 1

    plain = _run_discovery_cli(repo, tmp_path)
    assert plain.returncode == 0, plain.stderr
    assert "adapter=invalid" in plain.stdout


def test_standing_test_economics_adapter_discovery_is_documented() -> None:
    contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    example = (ROOT / "skills" / "public" / "quality" / "adapter.example.yaml").read_text(encoding="utf-8")

    assert "test_file_discovery" in contract
    assert "graded fallback" in contract
    assert "degraded" in contract
    assert "test_file_discovery" in example
