"""The lifecycle half the spec assigned to `quality` and nothing wired (#626).

The mechanics existed and validated with test-only callers, and
`skills/public/quality/SKILL.md` did not mention lessons, so the surface named as
owner had no idea it owned anything. These tests pin the wiring AND the failure
mode #626's ordering comment names: proposing on recurrence count selects the
LOUDEST lesson rather than the one whose prose is the problem.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import render_lesson_lifecycle_review as review
from tests.script_loader import load_script_module
from tests.test_lesson_ledger import ROOT, _materialize, _payload, _retro, _session_event

CATALOG = ROOT / "skills/public/quality/references/catalog.yaml"
QUALITY_SKILL = ROOT / "skills/public/quality/SKILL.md"
LEDGER_RELATIVE = "charness-artifacts/retro/lesson-ledger.json"


def _repo(tmp_path: Path, *, score_events: list[dict] | None = None) -> Path:
    """Two lessons: `loud` cited by three retros and never scored, `quiet` scored
    once with an anchor. This is #626's discriminator in miniature."""
    for name, lesson in (
        ("loud-1.md", "loud"),
        ("loud-2.md", "loud"),
        ("loud-3.md", "loud"),
        ("quiet.md", "quiet"),
    ):
        _retro(tmp_path, name, lesson)
    payload = _payload(source="charness-artifacts/retro/loud-1.md")
    payload["transitions"][0]["lesson_id"] = "loud"
    payload["transitions"][0]["transition_id"] = "seed-loud"
    payload["transitions"].append(
        {
            "sequence": 2,
            "transition_id": "seed-quiet",
            "lesson_id": "quiet",
            "source_retro": "charness-artifacts/retro/quiet.md",
        }
    )
    payload["lessons"] = {
        "loud": {
            "source_retro": "charness-artifacts/retro/loud-1.md",
            "transition_id": "seed-loud",
            "score_total": 0,
            "score_count": 0,
            "state": "active",
            "last_lifecycle_event_id": None,
        },
        "quiet": {
            "source_retro": "charness-artifacts/retro/quiet.md",
            "transition_id": "seed-quiet",
            "score_total": 0,
            "score_count": 0,
            "state": "active",
            "last_lifecycle_event_id": None,
        },
    }
    payload["session_events"] = [_session_event(lesson_ids=["loud", "quiet"])]
    payload["score_events"] = copy.deepcopy(score_events or [])
    path = tmp_path / LEDGER_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_materialize(payload)), encoding="utf-8")
    return tmp_path


def _anchored_quiet_score() -> dict:
    return {
        "event_id": "score-quiet",
        "session_id": "session-a",
        "source_retro": "charness-artifacts/retro/quiet.md",
        "lesson_id": "quiet",
        "score": 2,
        "anchor": "Refused the release grant the green gate seemed to authorize.",
    }


def test_the_anchored_lesson_outranks_the_loud_unscored_one(tmp_path: Path) -> None:
    """The whole point of the ordering argument: `loud` has three independent
    sources and no anchor; `quiet` has one source and a recorded moment. A report
    ranked by recurrence would put `loud` first and propose on noise."""
    _repo(tmp_path, score_events=[_anchored_quiet_score()])

    payload = review.build_lifecycle_review(tmp_path)

    assert [item["lesson_id"] for item in payload["lessons"]] == ["quiet", "loud"]
    quiet, loud = payload["lessons"]
    assert quiet["evidence"] == "anchored"
    assert quiet["anchored_score_count"] == 1
    assert loud["evidence"] == "no-score-evidence"
    # And the loud one really is the louder one, so the ordering is a deliberate
    # refusal rather than an artifact of the fixture.
    assert loud["recurrence_context"]["independent_source_count"] > quiet["recurrence_context"][
        "independent_source_count"
    ]


def test_an_unscored_lesson_is_undetermined_and_the_denominator_is_stated(
    tmp_path: Path,
) -> None:
    _repo(tmp_path)

    payload = review.build_lifecycle_review(tmp_path)

    assert payload["anchored_lesson_count"] == 0
    assert sorted(payload["lessons_without_anchored_evidence"]) == ["loud", "quiet"]
    assert all(item["evidence"] == "no-score-evidence" for item in payload["lessons"])


def test_an_unanchored_score_is_not_counted_as_lifecycle_evidence(tmp_path: Path) -> None:
    """The contract permits an unanchored score at magnitude <= 1. It is a signal,
    but it names no moment, so it cannot discriminate the three dispositions."""
    _repo(
        tmp_path,
        score_events=[
            {
                "event_id": "score-quiet",
                "session_id": "session-a",
                "source_retro": "charness-artifacts/retro/quiet.md",
                "lesson_id": "quiet",
                "score": 1,
            }
        ],
    )

    quiet = next(
        item
        for item in review.build_lifecycle_review(tmp_path)["lessons"]
        if item["lesson_id"] == "quiet"
    )

    assert quiet["evidence"] == "unanchored-scores-only"
    assert quiet["anchored_score_count"] == 0
    assert quiet["score_count"] == 1
    assert "quiet" in review.build_lifecycle_review(tmp_path)["lessons_without_anchored_evidence"]


def test_the_review_names_the_three_dispositions_and_proposes_nothing(
    tmp_path: Path,
) -> None:
    _repo(tmp_path, score_events=[_anchored_quiet_score()])

    payload = review.build_lifecycle_review(tmp_path)

    assert set(payload["dispositions"]) == {"graduate", "rewrite-in-place", "strengthen-binding"}
    joined = " ".join(payload["non_claims"])
    assert "proposes nothing" in joined
    assert "Recurrence is context, not a disposition" in joined
    # No threshold: the ledger contract's Eighth Slice defers calibration, so
    # nothing here may imply a score value triggers a lifecycle event.
    assert "threshold" in joined


def test_cli_is_read_only_and_exits_zero_over_an_unproposed_ledger(tmp_path: Path) -> None:
    """Exit zero on purpose: this is evidence, not a verdict. A nonzero exit would
    make "no graduation proposed" read as a failure."""
    _repo(tmp_path, score_events=[_anchored_quiet_score()])
    before = (tmp_path / LEDGER_RELATIVE).read_bytes()

    command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render_lesson_lifecycle_review.py"),
            "--repo-root",
            str(tmp_path),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert command.returncode == 0, command.stderr
    assert json.loads(command.stdout)["kind"] == "charness.lesson-lifecycle-review"
    assert (tmp_path / LEDGER_RELATIVE).read_bytes() == before


def test_human_output_shows_anchors_and_the_undetermined_group(tmp_path: Path) -> None:
    _repo(tmp_path, score_events=[_anchored_quiet_score()])

    rendered = review._render_human(review.build_lifecycle_review(tmp_path))

    assert "Refused the release grant" in rendered
    assert "No anchored evidence (1): loud" in rendered
    assert "recurrence cannot tell these apart" in rendered


# --- the wiring itself: the owner surface must know it owns this -----------


def test_the_gate_is_filtered_out_of_a_repo_that_has_no_such_command() -> None:
    """The availability guard, EXECUTED rather than asserted in a docstring.

    This is the finding a fresh-eye round caught: the gate was first spelled
    `python3 scripts/render_lesson_lifecycle_review.py`, and
    `_catalog_gate_path` only recognizes a repo-native path when argv[0] starts
    with `./`. So the guard was inert and a charness-local command would have
    shipped into every consuming repo's plan. The catalog is an exported public
    surface, which is what made an unguarded entry there costly.
    """
    from skills.public.quality.scripts import (  # noqa: PLC0415
        quality_catalog_gate_applicability as applicability,
    )

    gate = {
        "id": "lesson-lifecycle-review",
        "command": "./scripts/render_lesson_lifecycle_review.py --repo-root .",
        "run_when": "repo exposes this repo-native command declaring a lesson evaluator",
    }

    # A repo with an adapter that does not declare this command and no such file.
    applicable, unavailable = applicability.applicable_catalog_gates(
        Path("/nonexistent-consumer-repo"), {"gate_commands": []}, [gate]
    )

    assert applicable == []
    assert [item["id"] for item in unavailable] == ["lesson-lifecycle-review"]
    assert "missing repo-native command" in unavailable[0]["reason"]

    # And it IS applicable where the command exists, so the filter is discriminating
    # rather than simply refusing everything.
    applicable, unavailable = applicability.applicable_catalog_gates(
        ROOT, {"gate_commands": []}, [gate]
    )
    assert [item["id"] for item in applicable] == ["lesson-lifecycle-review"]
    assert unavailable == []


def test_the_quality_planner_routes_the_review_as_a_gate_packet() -> None:
    """Routed through the catalog rather than the repo adapter: `review_commands`
    is pinned by `validate_adapters.py` to exactly the standing gate."""
    # In-process, not a subprocess: this asserts ordinary routing behavior through
    # rendered output, and the boundary-bypass ratchet reserves spawns for tests
    # that prove packaging, exit code, stderr, or process environment. The exit-code
    # tests above are the ones that legitimately keep their boundary.
    planner = load_script_module(
        "plan_quality_run_for_lesson_review",
        ROOT / "skills/public/quality/scripts/plan_quality_run.py",
    )
    plan = planner.build_plan(ROOT)
    rendered = planner.format_human(plan)

    assert "lesson-lifecycle-review" in rendered
    # A `command:` line is emitted only under gate_packets; the unavailable path
    # renders `GAP ...` with no command, so this cannot be satisfied by a
    # declared-unavailable row.
    assert "./scripts/render_lesson_lifecycle_review.py --repo-root ." in rendered
    assert "lesson-lifecycle-review" in {
        packet.get("id") for packet in plan["gate_packets"]
    }


def test_the_gate_command_is_executable_in_both_trees() -> None:
    """The `./` spelling is load-bearing and its exec bit was unguarded.

    Applicability is proven by `is_file()`, never by executability, so a copy that
    lost its mode would be reported applicable and then die on `Permission
    denied`. The mode must hold on the export too: `packaging_lib` copies with
    `copy2`/`copytree`, which carry mode, and `helper_provenance_lib` compares
    digests only, so nothing else would notice a divergence.
    """
    for path in (
        ROOT / "scripts/render_lesson_lifecycle_review.py",
        ROOT / "plugins/charness/scripts/render_lesson_lifecycle_review.py",
    ):
        assert path.is_file(), path
        assert os.access(path, os.X_OK), f"{path} is not executable; the catalog gate runs it as ./"
        assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"), path


def test_the_catalog_gate_declares_evidence_not_a_verdict() -> None:
    text = " ".join(CATALOG.read_text(encoding="utf-8").split())

    assert "id: lesson-lifecycle-review" in text
    assert "evidence only, never a verdict" in text
    assert "recurrence cannot discriminate the three dispositions" in text
    # The exit contract, stated precisely. It said "exits zero always", which is
    # false: a missing or unreplayable ledger exits 1 through the entrypoint.
    assert "a nonzero exit is a refusal to render" in text
    assert "never a finding about a lesson" in text


def test_a_refusal_names_this_command_not_the_module_it_reuses(tmp_path: Path) -> None:
    """The reused helpers raise through the selection preview's `_fail`, so an
    unrepaired refusal would name a command the operator never ran.

    Exercised through the real freeze hazard rather than a missing file: a seeded
    lesson whose cited retro lost its `recurrence-class:` tag. That is the
    unrepairable state `seed_lesson_transitions.py` documents, and the surface
    named in the message is the operator's only lead.
    """
    _repo(tmp_path, score_events=[_anchored_quiet_score()])
    assert review.build_lifecycle_review(tmp_path)["lesson_count"] == 2

    tag = tmp_path / "charness-artifacts/retro/quiet.md"
    tag.write_text(tag.read_text(encoding="utf-8").replace(" (recurrence-class: quiet)", ""), encoding="utf-8")

    with pytest.raises(ValueError, match="lesson lifecycle review cannot render") as raised:
        review.build_lifecycle_review(tmp_path)
    # The underlying diagnosis survives the re-prefix rather than being replaced.
    assert "recurrence-class" in str(raised.value)


def test_the_cli_refuses_an_unreadable_ledger_nonzero(tmp_path: Path) -> None:
    command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render_lesson_lifecycle_review.py"),
            "--repo-root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert command.returncode == 1
    assert command.stdout == ""


def test_the_quality_skill_claims_the_lifecycle_and_forbids_ranking_on_recurrence() -> None:
    """Before this slice the skill did not mention lessons at all, so the surface
    the spec named as owner had no idea it owned anything."""
    # Whitespace-normalized: the skill body is hard-wrapped, and a claim assertion
    # that breaks on a reflow tests the line width rather than the contract.
    text = " ".join(QUALITY_SKILL.read_text(encoding="utf-8").split())

    assert "lesson evaluator" in text
    assert "graduate, rewrite in place, or strengthen its binding" in text
    assert "Judge on ANCHORS" in text
    assert "never on recurrence count" in text
    assert "no anchored evidence is undetermined, not a candidate" in text
    assert "no score value triggers either automatically" in text
