#!/usr/bin/env python3
"""What a debug artifact actually DECLARES, and whether the planner could read it.

Split out of `plan_debug_run.py` (D33: a cohesive concept, not a mechanical spill
to dodge the length cap). Everything here answers one question the planner must
not answer for itself: is the author's `## Seam Risk` declaration something this
process READ, or something it merely failed to find?

The distinction is the whole point, because both directions were live defects:

* a debug artifact routinely QUOTES the scaffold template (`- Risk Class: none`)
  inside a fence above its real section, and reading that quote as the author's
  declaration made the planner emit a no-interrupt verdict over a declaration it
  never read;
* ignoring fenced content then created the mirror image -- an UNCLOSED fence makes
  every later line fenced, dropping the REAL declaration, which fell through to the
  legacy "artifact has no risk line" carve-out and emitted the same silent continue.

`validate_debug_artifact` is byte-blind to fencing and passes both shapes clean, so
nothing downstream catches either one. `risk_scope_established` is what lets the
planner refuse instead of guessing.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# `risk_interrupt_lib` is a REPO module, not a skill sibling, and this package is
# vendored into consuming repos where the two are resolved by different loaders.
# Taking it as a parameter keeps that resolution the caller's job -- the caller
# already holds it -- instead of duplicating a bootstrap that would drift.


_FENCE_MARKERS = ("```", "~~~")


def _prose_lines(text: str) -> list[str]:
    """Artifact lines outside fenced code blocks.

    A debug artifact routinely QUOTES the scaffold template (`- Risk Class: none`)
    inside a fence above its real `## Seam Risk` section. Reading the quoted example
    as the author's declaration made the planner render a no-interrupt verdict over a
    declaration it never read, so fenced content is not author state.

    An UNCLOSED fence makes every later line fenced, which drops the real declaration
    with it -- the same escape wearing the opposite coat, and `validate_debug_artifact`
    is byte-blind to fencing so nothing downstream catches it. `dropped_field_lines`
    below is what lets the caller tell "no risk line" from "a risk line I could not
    see", instead of falling into the legacy no-line carve-out.
    """
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        marker = next((candidate for candidate in _FENCE_MARKERS if stripped.startswith(candidate)), None)
        if fence is None:
            if marker is not None:
                fence = marker
                continue
            lines.append(line)
        elif marker == fence:
            fence = None
    return lines


def _dropped_field_lines(text: str, label: str) -> bool:
    """True when a `- <label>:` line exists in the RAW text but not outside fences.

    Only reachable through an unclosed fence (or a template quote that is the only
    occurrence). Either way the planner did not read the author's declaration, and
    must not report the scope as established.
    """
    prefix = f"- {label}:"
    raw = any(line.strip().startswith(prefix) for line in text.splitlines())
    prose = any(line.strip().startswith(prefix) for line in _prose_lines(text))
    return raw and not prose


def parse_field(text: str, label: str) -> str | None:
    prefix = f"- {label}:"
    for line in _prose_lines(text):
        stripped = line.strip()
        if stripped.startswith(prefix):
            value = stripped[len(prefix) :].strip()
            return value or None
    return None


def _recovered_risk_classes(raw_value: str, risk_interrupt_lib: Any) -> tuple[str, ...]:
    """Recognized risk classes from a `Risk Class` line the strict parser rejected."""
    parts = tuple(part.strip() for part in raw_value.split(",") if part.strip())
    return tuple(part for part in parts if part in risk_interrupt_lib.ALLOWED_RISK_CLASSES)


def risk_summary(path: Path, risk_interrupt_lib: Any) -> dict[str, Any]:
    if not path.is_file():
        return {
            "risk_classes": [],
            "next_step": None,
            "requires_interrupt": False,
            "risk_scope_established": True,
        }
    text = path.read_text(encoding="utf-8")
    risk_class_raw = parse_field(text, "Risk Class")
    next_step = parse_field(text, "Next Step")
    generalization_pressure = parse_field(text, "Generalization Pressure")
    try:
        risk_classes = risk_interrupt_lib._parse_risk_classes(risk_class_raw or "")
        risk_parse_error = None
    except risk_interrupt_lib.ValidationError as exc:
        # A declared forced class must still interrupt when the rest of the line is
        # unparseable: dropping every class on one bad token silently downgrades a
        # declared `external-seam` to "no risk". The strict taxonomy stays enforced by
        # `validate_debug_artifact.py`, so recovery here never softens that gate.
        risk_classes = _recovered_risk_classes(risk_class_raw or "", risk_interrupt_lib)
        risk_parse_error = str(exc)
    forced = bool(
        set(risk_classes) & risk_interrupt_lib.FORCED_RISK_CLASSES
        or generalization_pressure == "factor-now"
    )
    return {
        "risk_classes": list(risk_classes),
        "risk_parse_error": risk_parse_error,
        "generalization_pressure": generalization_pressure,
        "next_step": next_step,
        "requires_interrupt": forced,
        # The risk scope is established only when the planner actually READ the
        # author's declaration and understood it. Three ways it did not, and the
        # third is the one the first cut got wrong: `risk_class_raw is None` was
        # written to mean "legacy artifact with no risk line", and an unclosed fence
        # made it silently also mean "the line is there and I could not see it".
        "risk_scope_established": (
            not _dropped_field_lines(text, "Risk Class")
            and (risk_parse_error is None or forced or risk_class_raw is None)
        ),
    }
