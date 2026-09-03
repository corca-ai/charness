"""The release planner names the charness tree that answered (#788).

Inside the authoring repo a host may hand a session the installed plugin's copy of
a skill script; a plan that does not say which copy produced it cannot be read
against the checkout. The planner is read-only, so it reports rather than refuses;
the publish helper's entrypoint guard is the refusal.
"""

from __future__ import annotations

from pathlib import Path

from tests.script_main import load_script_module

from .support import ROOT

PLANNER = ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run.py"
_PLANNER = load_script_module("plan_release_run_script_origin_for_test", PLANNER)


def test_the_planner_run_from_the_checkout_reports_the_same_tree() -> None:
    origin = _PLANNER._script_origin(ROOT)
    assert origin["status"] == "same-tree"
    assert origin["script"] == str(PLANNER)
    assert origin["target_root"] == str(ROOT)


def test_the_planner_run_against_a_consuming_repo_reports_that_and_nothing_else(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    origin = _PLANNER._script_origin(consumer)
    assert origin["status"] == "consuming-repo"
    assert origin["own_root"] == str(ROOT)
    assert origin["checkout_script"] is None
