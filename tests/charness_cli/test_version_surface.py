from __future__ import annotations

import builtins
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, load_cli_module, run_cli

PACKAGING_VERSION = json.loads(
    (ROOT / "packaging" / "charness.json").read_text(encoding="utf-8")
)["version"]


def load_charness_module(module_name: str):
    return load_cli_module(module_name, ROOT / "charness")


def version_state_path(home_root: Path) -> Path:
    return home_root / ".local" / "state" / "charness" / "version-state.json"


def test_top_level_version_alias_matches_version_subcommand() -> None:
    subcommand = run_cli("version")
    alias = run_cli("--version")

    assert subcommand.returncode == 0, subcommand.stderr
    assert alias.returncode == 0, alias.stderr
    assert alias.stdout == subcommand.stdout


def test_source_checkout_version_uses_embedded_packaging_manifest() -> None:
    result = run_cli("--version")

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout) == {"version": PACKAGING_VERSION}


@pytest.mark.boundary_contract(
    reason="-S runs the standalone CLI in a clean interpreter without site packages"
)
def test_standalone_version_falls_back_to_valid_yaml_without_pyyaml() -> None:
    result = subprocess.run(
        [sys.executable, "-S", str(ROOT / "charness"), "version"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout) == {"version": PACKAGING_VERSION}


def test_renderer_falls_back_to_json_yaml_when_pyyaml_is_unavailable(monkeypatch) -> None:
    module = load_charness_module("charness_yaml_renderer_fallback_under_test")
    original_import = builtins.__import__

    def import_without_yaml(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yaml":
            raise ImportError("simulated missing PyYAML")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_yaml)

    rendered = module.render_yaml({"message": "안녕하세요", "items": [1, 2]})

    assert json.loads(rendered) == {"message": "안녕하세요", "items": [1, 2]}
    assert yaml.safe_load(rendered) == {"message": "안녕하세요", "items": [1, 2]}


def test_plain_version_does_not_write_version_state(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    result = run_cli("version", "--home-root", str(home_root))

    assert result.returncode == 0, result.stderr
    assert not version_state_path(home_root).exists()

    alias_home = tmp_path / "alias-home"
    alias = run_cli("--version", env={**os.environ, "HOME": str(alias_home)})

    assert alias.returncode == 0, alias.stderr
    assert not version_state_path(alias_home).exists()

    existing_home = tmp_path / "existing-home"
    existing_state = version_state_path(existing_home)
    existing_state.parent.mkdir(parents=True)
    original = b'{"sentinel":"unchanged"}\n'
    existing_state.write_bytes(original)

    existing = run_cli("version", "--home-root", str(existing_home))

    assert existing.returncode == 0, existing.stderr
    assert existing_state.read_bytes() == original


def test_verbose_version_keeps_recorded_version_state(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    result = run_cli("version", "--home-root", str(home_root), "--verbose")

    assert result.returncode == 0, result.stderr
    assert version_state_path(home_root).is_file()
