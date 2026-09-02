"""Tests for the single owner of gate env-bypass truthiness.

The contract these pin used to be restated once per gate, and the restatements
drifted the way restatements do: `bool(os.environ.get(NAME))` reads every
non-empty spelling as "on", so the values an operator uses to say "keep the gate
running" (`0`, `false`, `no`, `off`) switched the gate off instead. That
inversion was found and repaired twice in two copies. A third copy,
`check_staged_reversion`, carried the correct predicate but no test that
constrained it -- a measured mutant replacing it with bare truthiness killed
zero tests in the whole standing suite -- because each copy's tests could only
ever reach that copy.

So the spelling table is pinned ONCE, here, against the shared helper. The
per-gate cases below are deliberately not a fourth copy of the table: each one
asks only "does this gate route through the shared helper", which is the wiring a
future rewrite could break without touching this file's table.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

env_bypass = importlib.import_module("scripts.core.env_bypass")
csr = importlib.import_module("scripts.hooks.check_staged_reversion")
csrc = importlib.import_module("scripts.hooks.check_staged_router_change")
cswc = importlib.import_module("scripts.hooks.check_staged_worktree_consistency")

# The spellings an operator reaches for to say "keep the gate ON". Every one of
# them must leave the bypass off. `"  "` and the unset case are here because a
# whitespace-only value is what a templated `NAME=${FLAG}` expands to when FLAG
# is empty, and that must not disarm a gate either.
OFF_SPELLINGS = ("0", "false", "no", "off", "", "  ", "FALSE", "No", "OFF", "yes-ish", "2")

# Case and surrounding whitespace are insignificant; the four words are not.
ON_SPELLINGS = ("1", "true", "yes", "on", "TRUE", "YES", " on ", "On")

_ENV = "CHARNESS_TEST_BYPASS_PROBE"


@pytest.mark.parametrize("value", OFF_SPELLINGS)
def test_off_spellings_leave_the_bypass_disabled(value: str, monkeypatch) -> None:
    monkeypatch.setenv(_ENV, value)
    assert env_bypass.env_bypass_enabled(_ENV) is False, repr(value)


@pytest.mark.parametrize("value", ON_SPELLINGS)
def test_on_spellings_enable_the_bypass(value: str, monkeypatch) -> None:
    monkeypatch.setenv(_ENV, value)
    assert env_bypass.env_bypass_enabled(_ENV) is True, repr(value)


def test_an_unset_variable_is_not_a_bypass(monkeypatch) -> None:
    monkeypatch.delenv(_ENV, raising=False)
    assert env_bypass.env_bypass_enabled(_ENV) is False


# --- per-gate wiring -----------------------------------------------------------
# One off-spelling and one on-spelling per gate. These fail if a gate stops
# routing through the shared helper, which is the only way the table above can
# stop protecting it.


def test_staged_reversion_env_bypass_routes_through_the_shared_helper(monkeypatch) -> None:
    args = argparse.Namespace(allow_staged_reversion=False)

    monkeypatch.setenv(csr._ENV_BYPASS, "0")
    assert csr._bypassed(args) is False

    monkeypatch.setenv(csr._ENV_BYPASS, "on")
    assert csr._bypassed(args) is True


def test_router_change_env_bypass_routes_through_the_shared_helper(monkeypatch) -> None:
    args = argparse.Namespace(allow_router_change=False)

    monkeypatch.setenv(csrc._ENV_BYPASS, "off")
    assert csrc._bypassed(args) is False

    monkeypatch.setenv(csrc._ENV_BYPASS, "YES")
    assert csrc._bypassed(args) is True


def test_partial_stage_env_bypass_routes_through_the_shared_helper(monkeypatch) -> None:
    monkeypatch.setenv(cswc.ALLOW_ENV, "false")
    assert cswc.allow_partial_stage() is False

    monkeypatch.setenv(cswc.ALLOW_ENV, " on ")
    assert cswc.allow_partial_stage() is True


def test_the_standalone_cli_copy_agrees_with_the_owner_on_every_spelling(monkeypatch) -> None:
    """The one copy that CANNOT import the owner is bound to it by this test.

    The root `charness` CLI is the installed standalone entry point: its
    source-root probe returns None when no charness tree is present, so
    `scripts.core.env_bypass` is not importable in the case that entry point exists to
    serve. Its `bool_env` is therefore a deliberate fifth copy of the table.

    A comment saying "keep these in sync" is the restatement pattern this whole
    slice exists to remove. This drives BOTH implementations over the same
    spellings instead, so the copies cannot drift silently -- the shape the repo
    already uses where a portable script cannot import across its boundary.
    """
    loader = importlib.machinery.SourceFileLoader(
        "charness_cli_under_env_bypass_test", str(ROOT / "charness")
    )
    spec = importlib.util.spec_from_loader("charness_cli_under_env_bypass_test", loader)
    assert spec is not None and spec.loader is not None
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)

    for value in OFF_SPELLINGS + ON_SPELLINGS:
        monkeypatch.setenv(_ENV, value)
        assert cli.bool_env(_ENV) is env_bypass.env_bypass_enabled(_ENV), repr(value)

    monkeypatch.delenv(_ENV, raising=False)
    assert cli.bool_env(_ENV) is env_bypass.env_bypass_enabled(_ENV) is False


def test_the_cli_flag_still_bypasses_without_any_env_value(monkeypatch) -> None:
    """The flag disjunction is per-gate and must survive the consolidation."""
    monkeypatch.delenv(csr._ENV_BYPASS, raising=False)
    monkeypatch.delenv(csrc._ENV_BYPASS, raising=False)

    assert csr._bypassed(argparse.Namespace(allow_staged_reversion=True)) is True
    assert csrc._bypassed(argparse.Namespace(allow_router_change=True)) is True
