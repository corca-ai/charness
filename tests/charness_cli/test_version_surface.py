from __future__ import annotations

import json

from .support import ROOT, run_cli


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
