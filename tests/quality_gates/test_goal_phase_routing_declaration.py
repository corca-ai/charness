"""The phase-routing floor's DECLARATION contract.

Split out of ``test_goal_coordination_floors.py`` when that file hit its length
cap: this is one floor's one question -- does the goal say which phases its work
crossed, and is every declared phase routed -- rather than the gather/release
floor set the parent file owns.

The floor used to answer that question by matching words in the goal's prose.
These tests are the contract that replaced it, and several of them were written
BEFORE the swap on purpose: the risk in trading a guess for a declaration is a
floor that quietly stops refusing anything, which is invisible if the only
evidence is "the new code passes the new tests".
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pr = _load("goal_artifact_phase_routing")


def test_recorded_work_with_no_routing_at_all_is_still_refused() -> None:
    """THE case this floor exists to catch, and the one a weakened replacement
    would silently drop: a goal that recorded real work and routed none of it."""
    text = (
        "Created: 2026-07-20\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: rewrote the parser and shipped it\n\n"
        "## Coordination Cues\n\n(none)\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["ok"] is False
    assert report["phase_routing_floor"]["satisfied"] is False


def test_a_reasonless_optout_cannot_buy_off_the_floor() -> None:
    """The declaration's escape hatch has to cost a real sentence, or the swap
    hands every author a one-word bypass the guess never offered."""
    text = (
        "Created: 2026-07-20\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: rewrote the parser and shipped it\n\n"
        "## Coordination Cues\n\nRouting: n/a\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["ok"] is False


def test_a_routed_goal_passes() -> None:
    """Control, so the tests above cannot be satisfied by a floor that refuses
    everything."""
    text = (
        "Created: 2026-07-20\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: rewrote the parser and shipped it\n\n"
        "## Coordination Cues\n\n"
        "Phases: impl\n"
        "Routing: impl — selected from installed skill metadata for the code change\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["ok"] is True


def test_the_declaration_is_read_as_a_list_not_searched_as_prose() -> None:
    """The repair's own first draft had the disease it replaced: it searched the
    declaration's VALUE for phase names, so a sentence saying a phase was NOT
    entered declared it. Caught by dogfooding this floor on its own goal."""
    text = (
        "Created: 2026-08-09\nStatus: complete\n\n"
        "## Slice Log\n\n- Recorded work happened here\n\n"
        "## Coordination Cues\n\n"
        "Phases: quality — the gate boundary; no debug phase was entered in this run\n"
    )
    kind, phases, _value = pr.declared_phases(text)

    assert kind == "ref"
    assert phases == ["quality"], "prose after the separator must not declare a phase"


def test_the_declaration_accepts_the_ordinary_list_forms() -> None:
    for value, expected in (
        ("debug, quality", ["debug", "quality"]),
        ("debug and quality", ["debug", "quality"]),
        ("quality", ["quality"]),
        ("n/a", []),
    ):
        text = (
            "Created: 2026-08-09\nStatus: complete\n\n"
            "## Slice Log\n\n- work\n\n"
            f"## Coordination Cues\n\nPhases: {value}\n"
        )
        assert pr.declared_phases(text)[1] == expected, value


def test_a_goal_that_records_work_and_declares_nothing_is_refused() -> None:
    """The forced question. Without it, replacing the guess with an OPTIONAL
    declaration would hand every author a silent bypass."""
    text = (
        "Created: 2026-08-09\nStatus: complete\n\n"
        "## Slice Log\n\n- Recorded work happened here\n\n"
        "## Coordination Cues\n\nRouting: impl — routed per installed metadata\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["ok"] is False
    assert "no `Phases:` line" in report["phase_routing_floor"]["reason"]


def test_a_goal_created_before_the_declaration_rule_owes_no_declaration() -> None:
    """Grandfathering, so a dated contract change does not retroactively refuse
    every goal shaped against the old floor."""
    text = (
        "Created: 2026-07-01\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: something real\n\n"
        "## Coordination Cues\n\nRouting: impl — routed per installed metadata\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["phase_routing_floor"]["declaration_owed"] is False
    assert report["ok"] is True


def test_an_empty_slice_log_owes_no_declaration_yet() -> None:
    """Nothing recorded is nothing to declare; asking earlier is ceremony."""
    text = (
        "Created: 2026-08-09\nStatus: active\n\n"
        "## Slice Log\n\n## Coordination Cues\n\n(none)\n"
    )
    assert pr.declaration_required(text) is False


def test_prose_no_longer_decides_which_phases_a_goal_crossed() -> None:
    """The word `pytest` in a verification note used to DEMAND a quality route.

    The trigger now reads the author's declaration, so the same sentence requires
    nothing until someone says it crossed that boundary. This is the intended
    weakening, recorded here rather than left to be discovered: measured over the
    185 checked-in goal artifacts, the old quality guess fired on 157 of them,
    mostly on the word "gate".
    """
    text = "## Slice Log\n\n- Targeted verification: regression suite passed under pytest\n"
    assert pr.phase_route_triggers(text) == {
        "impl": False,
        "debug": False,
        "quality": False,
        "issue": False,
    }

    declared = text + "\n## Coordination Cues\n\nPhases: quality\n"
    assert pr.phase_route_triggers(declared)["quality"] is True


def test_the_airport_gate_metaphor_no_longer_demands_a_quality_route() -> None:
    """A recorded false positive: `gate` matched the quality guess wherever it
    appeared, including in prose that has nothing to do with a repo gate."""
    text = "## Slice Log\n\n- Explained the boarding rule with an airport gate example\n"
    assert pr.phase_route_triggers(text)["quality"] is False


def test_plain_english_debug_work_is_declarable_where_the_guess_missed_it() -> None:
    """The other direction, and the worse one: real debug work written without the
    vocabulary never triggered at all, so the floor let it through silently."""
    text = "## Slice Log\n\n- Traced the failure to an off-by-one in the window bound\n"
    assert pr.phase_route_triggers(text)["debug"] is False

    declared = text + "\n## Coordination Cues\n\nPhases: debug\n"
    assert pr.phase_route_triggers(declared)["debug"] is True
