from __future__ import annotations

from .support import run_cli


def test_top_level_version_alias_matches_version_subcommand() -> None:
    subcommand = run_cli("version")
    alias = run_cli("--version")

    assert subcommand.returncode == 0, subcommand.stderr
    assert alias.returncode == 0, alias.stderr
    assert alias.stdout == subcommand.stdout
