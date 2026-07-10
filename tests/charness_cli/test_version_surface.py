from __future__ import annotations

import json
import os
from pathlib import Path

from .support import ROOT, run_cli


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
    expected = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected


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
