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

import pytest

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
    return _load("goal_artifact_markdown").section_bounds


_TEMPLATE = (
    "## Goal\n\nWhat outcome this goal exists to reach.\n\n"
    "## Interview Decisions\n\nFor each Before-phase question: options, chosen value.\n"
)


def test_a_bare_heading_is_hollow(hollow, bounds) -> None:
    report = hollow.classify("## Goal\n\n## Interview Decisions\n\nreal content\n", _TEMPLATE,
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

    report = hollow.classify(artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["still_template_text"] == ["Interview Decisions"]
    assert report["empty"] == []


def test_reflowing_the_template_prose_is_still_hollow(hollow, bounds) -> None:
    """Comparison is whitespace-normalized, so rewrapping a paragraph is not
    content. Otherwise the check would be defeated by a formatter."""
    artifact = (
        "## Goal\n\nreal\n\n"
        "## Interview Decisions\n\nFor each Before-phase question:\noptions,\nchosen value.\n"
    )

    report = hollow.classify(artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert "Interview Decisions" in report["still_template_text"]


def test_written_content_is_not_hollow(hollow, bounds) -> None:
    artifact = "## Goal\n\nreal goal\n\n## Interview Decisions\n\nChose A over B because C.\n"

    report = hollow.classify(artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []
    assert report["reason"] == ""


def test_an_explicit_n_a_counts_as_written(hollow, bounds) -> None:
    """The escape this contract already documents, needing no new syntax: a goal
    with genuinely nothing for a section keeps the heading and says so."""
    artifact = "## Goal\n\nreal\n\n## Interview Decisions\n\nN/A — no alternatives were considered.\n"

    report = hollow.classify(artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []


def test_an_absent_section_is_not_reported_as_hollow(hollow, bounds) -> None:
    """The missing-heading floor owns that. Reporting it here too would say the
    same thing twice in two vocabularies."""
    report = hollow.classify("## Goal\n\nreal\n", _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds)

    assert report["hollow"] == []


def test_run_filled_sections_are_reported_but_never_refused(hollow, bounds) -> None:
    """The trap in the fix. Most run-filled sections are template-identical at
    draft time BY DESIGN, so refusing on hollowness alone would refuse every fresh
    draft -- trading one false verdict for another."""
    report = hollow.classify("## Slice Log\n\n## Goal\n\nreal\n", _TEMPLATE,
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

    reason = hollow.classify(
        artifact, _TEMPLATE, ("Goal", "Interview Decisions"), section_bounds=bounds
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
    body += "\n## Closeout Binding Plan\n" + "".join(
        f"- {field} fixture value\n" for field in goal_lib.CLOSEOUT_PLAN_FIELDS
    )
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


def test_a_non_shaping_status_is_not_regraded(goal_lib) -> None:
    """An artifact whose scope was set before this rule existed is not re-graded
    against it -- the same scoping the backlog floor already uses."""
    active = _draft_with(goal_lib, "Boundaries").replace("Status: draft", "Status: active", 1)

    report = goal_lib.pursue_readiness(active)

    assert report["hollow_sections"]["hollow"] == []
    assert "not evaluated" in report["hollow_sections"]["reason"]
