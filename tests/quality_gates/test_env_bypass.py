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

import pytest

env_bypass = importlib.import_module("scripts.env_bypass")
csr = importlib.import_module("scripts.check_staged_reversion")
csrc = importlib.import_module("scripts.check_staged_router_change")
cswc = importlib.import_module("scripts.check_staged_worktree_consistency")

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


def test_the_cli_flag_still_bypasses_without_any_env_value(monkeypatch) -> None:
    """The flag disjunction is per-gate and must survive the consolidation."""
    monkeypatch.delenv(csr._ENV_BYPASS, raising=False)
    monkeypatch.delenv(csrc._ENV_BYPASS, raising=False)

    assert csr._bypassed(argparse.Namespace(allow_staged_reversion=True)) is True
    assert csrc._bypassed(argparse.Namespace(allow_router_change=True)) is True
