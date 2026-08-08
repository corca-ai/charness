"""The operator-queue / blocked-matrix floors read a FLAT `## `-only section.

`goal_artifact_floor_grammar.section_span` says in as many words that these two
floors "keep their own flat `## `-only variant unless a divergence-exposing proof
migrates them". A consolidation slice replaced their hand-rolled walks with the
shared `masked_section_body`; this file is the proof that sentence demanded, and
it pins the three axes on which the shared level-aware walk DIVERGES from the flat
one.

Why it matters, concretely: `section_span` matches `#`..`######`, is
case-insensitive, and tolerates trailing text after the heading name. Under it, an
ordinary `### Operator Decision Queue` block quoted inside a `## Slice Log` becomes
the section — and if that block happens to contain a `- Decision:` line, the
operator-queue floor returns `ok` while the real `## Operator Decision Queue` still
holds seeded scaffold prose. That floor gates the `complete` flip, so it is a false
green at a terminal boundary, latent in every artifact. Round-2 bounded review
caught it before it shipped.
"""
from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


grammar = _load("goal_artifact_floor_grammar")
queue = _load("goal_artifact_operator_queue")
matrix = _load("goal_artifact_blocked_matrix")

# On/after both floors' RULE_DATE so neither is grandfathered off.
_CREATED = "2026-08-08"


def _artifact(section_heading: str, body: str, *, real_section: str = "") -> str:
    return (
        f"# Achieve Goal: t\n\nStatus: active\nCreated: {_CREATED}\n"
        "Activation: `/goal @x.md`\n\n"
        "## Slice Log\n\n"
        f"{section_heading}\n\n{body}\n"
        + real_section
    )


# --- axis 1: heading LEVEL --------------------------------------------------


def test_a_sub_heading_is_not_the_section() -> None:
    """`### Name` inside a slice log must not become the section.

    This is the false-green path: the H3 block carries a `- Decision:` line, so a
    level-tolerant walk reports the operator-queue floor satisfied while the real
    H2 section is absent entirely.
    """
    text = _artifact(
        "### Operator Decision Queue",
        "- Decision: whether to arm the warn tier\n- Owner: operator",
    )
    assert grammar.masked_section_body(text, "Operator Decision Queue") is None
    # ...and the flat walk IS able to find it when it is a real H2.
    real = _artifact("## Operator Decision Queue", "- Decision: whether to arm the warn tier")
    assert grammar.masked_section_body(real, "Operator Decision Queue") is not None


def test_blocked_matrix_lane_inside_a_sub_heading_is_not_the_matrix() -> None:
    text = _artifact(
        "### Remaining Boundary Matrix",
        "- Lane: github publish | classification: approval-required | next: operator approval",
    )
    assert grammar.masked_section_body(text, "Remaining Boundary Matrix") is None


# --- axis 2: CASE -----------------------------------------------------------


def test_the_walk_is_case_sensitive() -> None:
    text = _artifact("## operator decision queue", "- Decision: something")
    assert grammar.masked_section_body(text, "Operator Decision Queue") is None


# --- axis 3: TRAILING TEXT after the heading name ---------------------------


def test_trailing_text_after_the_heading_name_is_a_different_heading() -> None:
    text = _artifact("## Operator Decision Queue (closed)", "- Decision: something")
    assert grammar.masked_section_body(text, "Operator Decision Queue") is None


# --- the divergence is real, not asserted -----------------------------------


def test_the_level_aware_walk_actually_differs_on_all_three_axes() -> None:
    """Pins that these are DIVERGENCES, not properties both walks happen to share.

    Without this, every assertion above would still pass if the two walks were
    identical — and the tests would be proving nothing about the migration.
    """
    for heading, body in (
        ("### Operator Decision Queue", "- Decision: x"),
        ("## operator decision queue", "- Decision: x"),
        ("## Operator Decision Queue (closed)", "- Decision: x"),
    ):
        text = _artifact(heading, body)
        masked = grammar.mask_fences(text)
        assert grammar.section_span(masked, "Operator Decision Queue") is not None, heading
        assert grammar.masked_section_body(text, "Operator Decision Queue") is None, heading


# --- the floors themselves, not just the helper -----------------------------


def test_operator_queue_floor_does_not_pass_on_a_quoted_sub_heading() -> None:
    text = _artifact(
        "### Operator Decision Queue",
        "- Decision: whether to arm the warn tier\n- Owner: operator",
    )
    report = queue.check(text)
    assert report["applies"] is True
    assert report["ok"] is False


def test_blocked_matrix_floor_does_not_pass_on_a_quoted_sub_heading() -> None:
    text = _artifact(
        "### Remaining Boundary Matrix",
        "- Lane: github publish | classification: approval-required | next: operator approval",
    )
    report = matrix.check(text)
    assert report["applies"] is True
    assert report["ok"] is False


def test_rule_dates_are_in_the_past_so_these_cases_are_in_scope() -> None:
    """Guards the whole file: a future RULE_DATE would make every case vacuous."""
    created = date.fromisoformat(_CREATED)
    assert created >= queue.RULE_DATE
    assert created >= matrix.RULE_DATE
