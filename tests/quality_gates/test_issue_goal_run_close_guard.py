from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUARD = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_goal_run_guard.py")
)

MENTION = "the body file must already contain the `<!-- charness-goal-run:v1 ... -->` block"


def _real_block() -> str:
    return (
        "<!-- charness-goal-run:v1\n"
        + json.dumps({"binding_schema": "charness.goal-binding/v1"})
        + "\n-->"
    )


def test_inline_code_marker_mention_does_not_block_close() -> None:
    GUARD["refuse_generic_close"](
        f"## Situation\n\n{MENTION}, which eight fields it needs.\n",
        context="target issue body",
    )


def test_fenced_marker_mention_does_not_block_close() -> None:
    body = f"## Evidence\n\n```text\n{MENTION}\n```\n\nPlain prose after the fence.\n"
    GUARD["refuse_generic_close"](body, context="target issue body")


def test_real_block_still_requires_goal_run_close() -> None:
    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        GUARD["refuse_generic_close"](
            f"Human prose.\n\n{_real_block()}\n", context="target issue body"
        )


def test_real_block_is_found_beside_a_code_mention() -> None:
    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        GUARD["refuse_generic_close"](
            f"{MENTION}\n\n{_real_block()}\n", context="target issue body"
        )


def test_bare_malformed_marker_still_refuses() -> None:
    with pytest.raises(RuntimeError, match="duplicate or malformed"):
        GUARD["refuse_generic_close"](
            "Human prose with a bare <!-- charness-goal-run:v1 fragment.\n",
            context="target issue body",
        )


def test_non_string_body_is_not_a_goal_run() -> None:
    GUARD["refuse_generic_close"](None, context="target issue body")
