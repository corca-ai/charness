"""Tests that the cross-floor opt-out census reaches an actual READER.

Split from ``test_goal_coordination_floors.py`` on a real seam: those tests pin
what the floors DECIDE, and ``test_goal_cue_grammar.py`` pins how a cue is read
and counted. These pin the SURFACING -- that the census survives the trip out to
a CLI result, a rendered shape, and the goal-flip return value. Every one of
these exists because a review round found the census computed and then thrown
away, which no verdict-level test can catch.

The fixture helpers are imported from the coordination-floor module rather than
recreated: an independent copy would drift from the artifact shape the floors
actually accept, and would trip the duplicate ratchet for no benefit.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml

_SIBLING = Path(__file__).resolve().parent / "test_goal_coordination_floors.py"
_spec = importlib.util.spec_from_file_location("_coordination_floor_fixtures", _SIBLING)
_fixtures = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixtures)

cga = _fixtures.cga
desc = _fixtures._load("describe_goal_closeout_shape")
_URL_SOURCE = _fixtures._URL_SOURCE
_SCRIPTS = _fixtures._SCRIPTS
_full_goal = _fixtures._full_goal
_seed_other_evidence = _fixtures._seed_other_evidence
gal = _fixtures.gal

_COORDINATION = (
    "Routing: impl — selected from installed metadata\n"
    "Gather: n/a — the external link is background context, never routed\n"
)


def test_a_successful_complete_flip_carries_the_optout_census(tmp_path: Path) -> None:
    """`evidence_report` is attached only to the `refused` branch, so on the
    canonical write path a goal that satisfied every floor -- each by an opt-out
    -- reported nothing. That is precisely the population the census is for."""
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    text = _full_goal(
        created=created,
        context_sources=_URL_SOURCE,
        coordination=(
            "Routing: impl — selected from installed metadata\n"
            "Gather: n/a — the external link is background context, never routed\n"
        ),
    )
    path = gal.goal_path(tmp_path, created, "goal")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    result = gal.upsert_goal(tmp_path, date=created, slug="goal", title="T", status="complete")
    assert result["action"] in {"updated", "unchanged"}, result
    assert "gather" in result["coordination_optout_aggregate"]["opted_out_obligations"]
    assert any("opt-out census" in a for a in result["advisories"])


def test_check_goal_artifact_hoists_the_census_into_advisories(tmp_path: Path) -> None:
    """Nothing pinned the hoist: deleting it left the suite green, which is the
    round-1 defect (computed, never surfaced) recurring one layer up."""
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    text = _full_goal(
        created=created,
        context_sources=_URL_SOURCE,
        coordination=(
            "Routing: impl — selected from installed metadata\n"
            "Gather: n/a — the external link is background context, never routed\n"
        ),
    )
    path = gal.goal_path(tmp_path, created, "goal")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("Status: active", "Status: complete"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_SCRIPTS / "check_goal_artifact.py"),
         "--repo-root", str(tmp_path), "--goal-path", str(path)],
        capture_output=True, text=True,
    )
    payload = yaml.safe_load(proc.stdout)
    # The hoist is deliberately independent of the overall verdict: the census
    # matters on runs the gate PASSES, and this fixture is scoped to the
    # coordination floors rather than the full structural section set.
    assert any("coordination opt-out census" in a for a in payload["advisories"])
    assert "gather" in payload["closeout_evidence"]["coordination_optout_aggregate"][
        "opted_out_obligations"
    ]


def test_describe_shape_renders_the_census_count_not_just_a_title(tmp_path: Path) -> None:
    """The renderer prints `label: detail` for MISSING rows and a bare `label`
    for satisfied ones. This row never refuses, so a detail-carried census
    rendered as a title with the number discarded."""
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    text = _full_goal(
        created=created,
        context_sources=_URL_SOURCE,
        coordination=(
            "Routing: impl — selected from installed metadata\n"
            "Gather: n/a — the external link is background context, never routed\n"
        ),
    )
    path = gal.goal_path(tmp_path, created, "goal")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("Status: active", "Status: complete"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_SCRIPTS / "describe_goal_closeout_shape.py"),
         "--repo-root", str(tmp_path), "--goal-path", str(path)],
        capture_output=True, text=True,
    )
    rendered = proc.stdout
    assert "opt-out census" in rendered
    assert "declined: gather" in rendered  # the COUNT survives rendering


# --- in-process coverage of the two surfaces the subprocess tests cannot reach
# The CLI tests above prove behavior end to end, but they run the scripts in a
# CHILD process, so the parent's coverage never sees those lines and the
# changed-line mutation gate reads them as untested. These drive the same two
# code paths in-process.


def _complete_goal(tmp_path: Path, created: str = "2026-05-31") -> Path:
    _seed_other_evidence(tmp_path, created)
    text = _full_goal(created=created, context_sources=_URL_SOURCE, coordination=_COORDINATION)
    path = gal.goal_path(tmp_path, created, "goal")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("Status: active", "Status: complete"), encoding="utf-8")
    return path


def test_check_goal_artifact_main_emits_the_advisory_in_process(tmp_path, capsys, monkeypatch) -> None:
    path = _complete_goal(tmp_path)
    monkeypatch.setattr(
        sys, "argv",
        ["check_goal_artifact.py", "--repo-root", str(tmp_path), "--goal-path", str(path)],
    )
    cga.main()
    payload = yaml.safe_load(capsys.readouterr().out)
    assert any("coordination opt-out census" in a for a in payload["advisories"])


def test_described_shape_carries_the_declined_obligations_in_process(tmp_path) -> None:
    path = _complete_goal(tmp_path)
    report = desc.goal_conditional_shape(tmp_path, path.read_text(encoding="utf-8"))
    census = [r for r in report["triggered"] if r["floor"] == "coordination_optout_aggregate"]
    assert len(census) == 1
    assert "declined: gather" in census[0]["label"]
    # and it survives RENDERING -- the renderer prints bare `label` for satisfied
    # rows, so a detail-carried census would be discarded here
    rendered = desc.render_goal_conditional(report, "goal.md")
    assert "declined: gather" in rendered
