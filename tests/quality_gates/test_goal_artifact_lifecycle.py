"""Direct contract tests for the goal-artifact lifecycle owner."""
from __future__ import annotations

import importlib.util

import pytest

from .support import ROOT

_MODULE_PATH = ROOT / "skills/public/achieve/scripts/goal_artifact_lifecycle.py"


@pytest.fixture(scope="module")
def lifecycle():
    spec = importlib.util.spec_from_file_location("goal_artifact_lifecycle_test", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("draft", "draft"),
        (" COMPLETE (2026-08-24) — checked", "complete"),
        ("SUPERSEDED!", "superseded"),
        ("complete-ish", "complete-ish"),
        ("historical complete", "historical"),
        (None, ""),
    ],
)
def test_status_token_owns_annotation_boundaries(lifecycle, status: str | None, expected: str) -> None:
    assert lifecycle.status_token(status) == expected


@pytest.mark.parametrize("status", ["complete", "COMPLETE!", "superseded;", "SUPERSEDED (handoff)"])
def test_terminal_status_accepts_annotated_terminal_tokens(lifecycle, status: str) -> None:
    assert lifecycle.is_terminal_status(status) is True


@pytest.mark.parametrize("status", [None, "", "Draft", "active — slice 2", "complete-ish"])
def test_shaping_status_fails_closed_for_unknown_or_in_flight_values(lifecycle, status: str | None) -> None:
    assert lifecycle.is_shaping_status(status) is True


def test_assess_publishes_one_lifecycle_policy_for_terminal_status(lifecycle) -> None:
    decision = lifecycle.assess("SUPERSEDED (2026-08-24) — folded into successor")

    assert decision == {
        "status": "SUPERSEDED (2026-08-24) — folded into successor",
        "status_token": "superseded",
        "terminal": True,
        "pursuit_allowed": False,
        # Shaping is deliberately fail-closed on the raw status line; terminal
        # refusal is the separate normalized-token decision.
        "shaping_floor_applies": True,
        "hollow_evaluation_applies": False,
        "terminal_reason": "terminal status 'superseded' is historical and cannot be activated",
    }


def test_assess_keeps_active_work_pursuable_and_hollow_checked(lifecycle) -> None:
    decision = lifecycle.assess("active — slice 2 in flight")

    assert decision["terminal"] is False
    assert decision["pursuit_allowed"] is True
    # The raw annotation is not a recognised exact non-shaping value, but the
    # normalized token still makes active work eligible for hollow evaluation.
    assert decision["shaping_floor_applies"] is True
    assert decision["hollow_evaluation_applies"] is True
