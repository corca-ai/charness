"""Present-versus-written for required goal sections (#690).

`--pursue-ready` reported a goal as shaped while whole required sections were
bare headings, so "pursue-ready" came to mean "has the right headings". The check
is the thing a session trusts INSTEAD of reading the artifact, which is what made
that failure expensive.

The hard part is not detecting emptiness. It is that the scaffold seeds guidance
prose into every section it creates, so a fresh `## Interview Decisions` is
non-empty and still says nothing about this goal. Hollow is therefore defined
against the template.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT

_ACHIEVE = ROOT / "skills" / "public" / "achieve" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _ACHIEVE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def hollow():
    return _load("goal_artifact_hollow_sections")


@pytest.fixture(scope="module")
def goal_lib():
    return _load("goal_artifact_lib")


@pytest.fixture(scope="module")
def bounds():
    """The contract's ONE owner of the H2 section walk, injected exactly as the
    lib layer injects it. Using it here rather than a local copy is the point: a
    test that walked sections its own way would stop proving the production path
    reads the same bodies."""
    return _load("goal_artifact_markdown").section_bounds_all


_TEMPLATE = (
    "## Goal\n\nWhat outcome this goal exists to reach.\n\n"
    "## Interview Decisions\n\nFor each Before-phase question: options, chosen value.\n"
)


def test_a_bare_heading_is_hollow(hollow, bounds) -> None:
    report = hollow.classify("## Goal\n\n## Interview Decisions\n\nreal content\n", "## Goal\n\n## Interview Decisions\n\nreal content\n", _TEMPLATE,
                             ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["empty"] == ["Goal"]
    assert report["hollow"] == ["Goal"]


def test_a_section_still_carrying_the_template_prose_is_hollow(hollow, bounds) -> None:
    """THE case a non-empty check cannot see, and the reason this compares against
    the template at all. A freshly scaffolded section is non-empty by
    construction, so "require a non-empty body" would have called every fresh
    draft shaped."""
    artifact = (
        "## Goal\n\nCut the proof cost of the changed-line lane.\n\n"
        "## Interview Decisions\n\nFor each Before-phase question: options, chosen value.\n"
    )

    report = hollow.classify(artifact, artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["still_template_text"] == ["Interview Decisions"]
    assert report["empty"] == []


@pytest.mark.parametrize(
    "sections",
    [
        "## Goal\n\nwritten first\n\n## Goal\n",
        "## Goal\n\n## Goal\n\nwritten second\n",
    ],
    ids=["written-then-empty", "empty-then-written"],
)
def test_every_duplicate_occurrence_is_classified(hollow, bounds, sections: str) -> None:
    report = hollow.classify(
        sections, sections, _TEMPLATE, ("Goal",), section_bounds=bounds
    )

    assert report["empty"] == ["Goal"]
    assert report["blocking"] == ["Goal"]


def test_reflowing_the_template_prose_is_still_hollow(hollow, bounds) -> None:
    """Comparison is whitespace-normalized, so rewrapping a paragraph is not
    content. Otherwise the check would be defeated by a formatter."""
    artifact = (
        "## Goal\n\nreal\n\n"
        "## Interview Decisions\n\nFor each Before-phase question:\noptions,\nchosen value.\n"
    )

    report = hollow.classify(artifact, artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert "Interview Decisions" in report["still_template_text"]


def test_written_content_is_not_hollow(hollow, bounds) -> None:
    artifact = "## Goal\n\nreal goal\n\n## Interview Decisions\n\nChose A over B because C.\n"

    report = hollow.classify(artifact, artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []
    assert report["reason"] == ""


def test_an_explicit_n_a_counts_as_written(hollow, bounds) -> None:
    """The escape this contract already documents, needing no new syntax: a goal
    with genuinely nothing for a section keeps the heading and says so."""
    artifact = "## Goal\n\nreal\n\n## Interview Decisions\n\nN/A — no alternatives were considered.\n"

    report = hollow.classify(artifact, artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []


def test_an_absent_section_is_not_reported_as_hollow(hollow, bounds) -> None:
    """The missing-heading floor owns that. Reporting it here too would say the
    same thing twice in two vocabularies."""
    report = hollow.classify("## Goal\n\nreal\n", "## Goal\n\nreal\n", _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []


def test_run_filled_sections_are_reported_but_never_refused(hollow, bounds) -> None:
    """The trap in the fix. Most run-filled sections are template-identical at
    draft time BY DESIGN, so refusing on hollowness alone would refuse every fresh
    draft -- trading one false verdict for another."""
    report = hollow.classify("## Slice Log\n\n## Goal\n\nreal\n", "## Slice Log\n\n## Goal\n\nreal\n", _TEMPLATE,
                             ("Goal", "Slice Log"), section_bounds=bounds)

    assert report["hollow"] == ["Slice Log"]
    assert report["blocking"] == []
    assert report["run_filled_hollow"] == ["Slice Log"]


def test_the_reason_names_which_sections_and_in_which_way(hollow, bounds) -> None:
    """The core ask: report WHICH ones are hollow rather than a single
    ready/not-ready verdict. A caller that only learns `False` has to re-read the
    artifact to find what to fix -- the work the check was supposed to do."""
    artifact = (
        "## Goal\n\n"
        "## Interview Decisions\n\nFor each Before-phase question: options, chosen value.\n"
    )

    reason = hollow.classify(artifact, artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds
    )["reason"]

    assert "present but EMPTY: Goal" in reason
    assert "still the scaffold's own words: Interview Decisions" in reason


# --------------------------------------------------------------------------- #
# Wired into the readiness verdict
# --------------------------------------------------------------------------- #


def _draft_with(goal_lib, hollow_section: str) -> str:
    sections = goal_lib.REQUIRED_SECTIONS + goal_lib.PORTABILITY_SECTIONS
    body = "# Achieve Goal: T\n\nStatus: draft\nCreated: 2026-08-07\nActivation: `/goal @x.md`\n"
    for section in sections:
        body += f"\n## {section}\n"
        if section != hollow_section:
            body += f"{section} fixture value.\n"
    return body


def test_a_hollow_shaping_section_refuses_activation(goal_lib) -> None:
    report = goal_lib.pursue_readiness(_draft_with(goal_lib, "Boundaries"))

    assert report["pursue_ready"] is False
    assert "Boundaries" in report["hollow_blocking_sections"]
    assert "hollow:" in report["reason"]


def test_a_hollow_run_filled_section_does_not_refuse_activation(goal_lib) -> None:
    """`## Slice Log` before any slice runs is the named legitimate case."""
    report = goal_lib.pursue_readiness(_draft_with(goal_lib, "Slice Log"))

    assert report["hollow_blocking_sections"] == []
    assert "Slice Log" in report["hollow_sections"]["hollow"]


def test_the_report_is_published_even_when_nothing_blocks(goal_lib) -> None:
    """Structured, not folded into the boolean: the complaint was that a single
    verdict hid which sections were hollow."""
    report = goal_lib.pursue_readiness(_draft_with(goal_lib, "Slice Log"))

    assert "hollow_sections" in report
    assert set(report["hollow_sections"]) >= {"hollow", "empty", "still_template_text", "blocking"}


def test_active_hollow_shaping_section_refuses_activation(goal_lib) -> None:
    """Active work remains pursuable work and cannot bypass the hollow floor."""
    active = _draft_with(goal_lib, "Boundaries").replace("Status: draft", "Status: active", 1)

    report = goal_lib.pursue_readiness(active)

    assert report["pursue_ready"] is False
    assert report["hollow_sections"]["evaluated"] is True
    assert report["hollow_sections"]["hollow"] == ["Boundaries"]
    assert report["hollow_blocking_sections"] == ["Boundaries"]
    assert report["readiness_blockers"] == [{
        "kind": "hollow_sections",
        "sections": ["Boundaries"],
        "reason": report["hollow_sections"]["reason"],
    }]


def test_active_run_filled_section_is_reported_but_not_refused(goal_lib) -> None:
    active = _draft_with(goal_lib, "Slice Log").replace("Status: draft", "Status: active", 1)

    report = goal_lib.pursue_readiness(active)

    assert report["pursue_ready"] is True
    assert report["hollow_sections"]["evaluated"] is True
    assert report["hollow_blocking_sections"] == []
    assert "Slice Log" in report["hollow_sections"]["run_filled_hollow"]


def test_active_hollow_is_rejected_at_the_checker_cli(goal_lib, tmp_path: Path) -> None:
    goal = tmp_path / "charness-artifacts/goals/active-hollow.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        _draft_with(goal_lib, "Boundaries").replace("Status: draft", "Status: active", 1),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_ACHIEVE / "check_goal_artifact.py"),
            "--repo-root",
            str(tmp_path),
            "--goal-path",
            str(goal),
            "--pursue-ready",
        ],
        capture_output=True,
        text=True,
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1, result.stderr
    assert payload["pursue_ready"] is False
    assert payload["activation_ready"] is False
    assert payload["hollow_blocking_sections"] == ["Boundaries"]
    assert payload["readiness_blockers"][0]["kind"] == "hollow_sections"


def test_duplicate_required_headings_are_rejected_by_full_validation(goal_lib) -> None:
    artifact = _draft_with(goal_lib, "__none__") + "\n## Goal\nsecond copy\n"

    report = goal_lib.check_goal(artifact)

    assert "duplicate sections: Goal" in report["issues"]


# --------------------------------------------------------------------------- #
# Round-2 repairs.
# --------------------------------------------------------------------------- #


def test_the_no_block_sentence_only_names_actually_run_filled_sections(hollow, bounds) -> None:
    """The reason's parenthetical used to be applied to whatever did not block,
    which is how a shaping section came to be called run-filled."""
    report = hollow.classify("## Slice Log\n", "## Slice Log\n", _TEMPLATE,
                             ("Slice Log",), section_bounds=bounds)

    assert "Slice Log: filled by the run" in report["reason"]


def test_a_fenced_body_is_content_not_emptiness(hollow, bounds) -> None:
    """`mask_fences` blanks fenced regions, so a section written entirely as
    fenced command blocks -- the most natural shape for a verification plan --
    normalized to "" and was refused as "present but EMPTY", a statement the code
    had not established. Emptiness is decided on the RAW body now."""
    raw = "## Agent Verification Plan\n\n```\npytest -q tests/\n```\n"
    masked = "## Agent Verification Plan\n\n   \n                 \n   \n"

    report = hollow.classify(masked, raw, _TEMPLATE,
                             ("Agent Verification Plan",), section_bounds=bounds)

    assert report["empty"] == []


def test_a_quotation_of_the_template_is_still_not_content(hollow, bounds) -> None:
    """Identity still reads the MASKED body, so the fenced-body repair above did
    not open the hole masking exists to close."""
    raw = "## Interview Decisions\n\n```\nFor each Before-phase question: options, chosen value.\n```\n"
    masked = "## Interview Decisions\n\n   \n" + " " * 60 + "\n   \n"

    report = hollow.classify(masked, raw, _TEMPLATE,
                             ("Interview Decisions",), section_bounds=bounds)

    assert report["hollow"] == []


def test_an_evaluated_report_says_so(hollow, bounds) -> None:
    """This repo's payload grammar uses `evaluated` to separate a clean run from a
    skipped one. Without it, `hollow: []` reads identically in both states."""
    report = hollow.classify("## Goal\n\nreal\n", "## Goal\n\nreal\n", _TEMPLATE,
                             ("Goal",), section_bounds=bounds)

    assert report["evaluated"] is True


def test_the_wired_path_catches_a_section_left_as_template_text(goal_lib) -> None:
    """The integration gap round 2 named: both wired tests exercised only the
    EMPTY branch, so `elif False` on the identity branch left them green. This one
    uses the REAL scaffold template."""
    import importlib.util as _il

    spec = _il.spec_from_file_location("tpl", _ACHIEVE / "goal_artifact_lib.py")
    lib = _il.module_from_spec(spec)
    spec.loader.exec_module(lib)
    template_boundaries = lib._TEMPLATE.split("## Boundaries\n", 1)[1].split("\n## ", 1)[0]

    body = _draft_with(goal_lib, "__none__").replace(
        "## Boundaries\nBoundaries fixture value.\n",
        f"## Boundaries\n{template_boundaries}\n",
    )
    report = goal_lib.pursue_readiness(body)

    assert "Boundaries" in report["hollow_sections"]["still_template_text"], report["hollow_sections"]
