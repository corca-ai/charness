"""Presence-only coordination closeout floors for goal artifacts.

The floors cover gather, release, and issue-closeout boundaries. Each is
clone-safe, section-scoped, grandfathered by ``Created``, and satisfied by a
real step line or explicit opt-out in ``## Coordination Cues``.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# The floors landed around 2026-05-30; the cutoff grandfathers same-day in-flight goals.
COORDINATION_FLOOR_RULE_DATE = date(2026, 5, 31)
ISSUE_CLOSEOUT_FLOOR_RULE_DATE = date(2026, 6, 2)

# Long enough that an opt-out cannot be a one-word bypass.
MIN_OPTOUT_REASON = 30

COORDINATION_SECTION = "Coordination Cues"
CONTEXT_SOURCES_SECTION = "Context Sources"
AUTO_RETRO_SECTION = "Auto-Retro"
RECORDED_WORK_SECTIONS = ("Slice Log", "Final Verification")

_EXTERNAL_URL = re.compile(r"https?://\S", re.IGNORECASE)

# Step lines are anchored so inline examples never satisfy a floor.
_GATHER_REF = re.compile(r"^[\s>*-]*Gather\s*:\s*(\S.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE)
_RELEASE_REF = re.compile(r"^[\s>*-]*Release\s*:\s*(\S.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE)
_ISSUE_CLOSEOUT_REF = re.compile(
    r"^[\s>*-]*Issue\s+closeout\s*:\s*(\S.*?)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)
_NA_VALUE = re.compile(r"^n/?a\b[ \t]*[—–:-]+[ \t]*(\S.*)$", re.IGNORECASE)

# Deliberately precise; the bare word "release" would over-trigger.
_RELEASE_SURFACE_TOKENS = (
    "bump_version",
    "publish_release",
    "marketplace.json",
    "charness-artifacts/release/",
)
_TRACKED_ISSUE_CONTEXT = re.compile(
    r"\b(?:"
    r"(?:github\s+)?(?:tracked\s+)?issues?\s+#\d+"
    r"|https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+"
    r"|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+"
    r")\b",
    re.IGNORECASE,
)
_CLOSE_KEYWORD = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+\b",
    re.IGNORECASE,
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import is_floor_in_scope  # noqa: E402
from goal_artifact_floor_grammar import joined_section_body as _joined_section_body  # noqa: E402
from goal_artifact_floor_grammar import parse_created_date as goal_created_date  # noqa: E402
from goal_artifact_floor_grammar import section_body as _section_body  # noqa: E402
from goal_artifact_floor_grammar import section_span as _section_span  # noqa: E402
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402


def coordination_floors_apply(text: str) -> bool:
    """Whether the gather/release floors fire for this goal (grandfather-by-
    ``Created``-date). Fail-CLOSED: a missing/malformed ``Created`` is in-scope."""
    return is_floor_in_scope(goal_created_date(text), COORDINATION_FLOOR_RULE_DATE)


def issue_closeout_floor_applies(text: str) -> bool:
    """Whether the issue-closeout floor fires for this goal."""
    return is_floor_in_scope(goal_created_date(text), ISSUE_CLOSEOUT_FLOOR_RULE_DATE)


def gather_triggered(text: str) -> bool:
    """True when ``## Context Sources`` names an external (http/https) source."""
    body = _section_body(_mask_fences(text), CONTEXT_SOURCES_SECTION)
    if not body:
        return False
    return _EXTERNAL_URL.search(body) is not None


def release_triggered(text: str) -> bool:
    """True when the goal's recorded work names a release-surface token.

    The Coordination Cues span is blanked before the scan so a ``Release:``
    reference value (e.g. ``charness-artifacts/release/...``) or a seeded example
    in that section never counts as release work — only the *rest* of the body
    (Slice Plan / Slice Log / etc., where the run records what it changed) does.
    """
    masked = _mask_fences(text)
    span = _section_span(masked, COORDINATION_SECTION)
    if span is not None:
        masked = masked[: span[0]] + (" " * (span[1] - span[0])) + masked[span[1] :]
    low = masked.lower()
    return any(token in low for token in _RELEASE_SURFACE_TOKENS)


def issue_closeout_triggered(text: str) -> bool:
    """True when the goal records tracked issue resolution work.

    Context Sources can name the tracked issue explicitly. Recorded work can
    also trigger the floor through close keywords in the sections where achieved
    work is archived, not in planning/boundary text.
    """
    masked = _mask_fences(text)
    context = _section_body(masked, CONTEXT_SOURCES_SECTION) or ""
    if _TRACKED_ISSUE_CONTEXT.search(context):
        return True
    work = "\n".join(_section_body(masked, heading) or "" for heading in RECORDED_WORK_SECTIONS)
    return _CLOSE_KEYWORD.search(work) is not None
_SATISFYING = frozenset({"ref", "optout"})


def _classify_step(value: str) -> tuple[str, str]:
    """Classify one step-line value: ``"ref"`` (a real reference), ``"optout"``
    (a valid ``n/a — <reason>`` ≥ MIN_OPTOUT_REASON), or ``"optout_short"`` (an
    opt-out below the floor — present but not satisfying)."""
    na = _NA_VALUE.match(value)
    if na is not None:
        reason = na.group(1).strip()
        return ("optout" if len(reason) >= MIN_OPTOUT_REASON else "optout_short"), reason
    return "ref", value


def _parse_step(section_body: str | None, ref_re: "re.Pattern[str]") -> tuple[str | None, str | None]:
    """Classify the gather/release step line(s) inside the Coordination Cues body.

    Returns ``(kind, value)`` — ``None`` when no step line exists at all. When
    several step lines are present the **first satisfying** one wins (a real
    ``ref`` or a valid ``optout``), so a stray short opt-out above a real
    reference does not shadow it into a false refusal; only when none satisfies
    does the first non-satisfying classification surface (for the diagnostic).
    Presence-only: a real reference is never inspected further.
    """
    if not section_body:
        return None, None
    first: tuple[str | None, str | None] = (None, None)
    for match in ref_re.finditer(section_body):
        kind, value = _classify_step(match.group(1).strip())
        if kind in _SATISFYING:
            return kind, value
        if first[0] is None:
            first = (kind, value)
    return first


def apply_coordination_floors(report: dict[str, Any], text: str) -> None:
    """Attach the gather/release/issue floor verdicts to ``report``.

    For an in-scope goal (grandfather-by-``Created``): if a floor is *triggered*
    (external source / release-surface token / issue-closeout signal)
    and the Coordination Cues section carries no satisfying step line (a real
    reference or a ≥30-char ``n/a — <reason>`` opt-out),
    refuse the flip. Presence/binding-only — a real reference's content is never
    judged. Grandfathered goals are inert.
    """
    created = goal_created_date(text)
    in_scope = coordination_floors_apply(text)
    report["coordination_scope"] = {
        "in_scope": in_scope,
        "created": created.isoformat() if created else None,
        "rule_date": COORDINATION_FLOOR_RULE_DATE.isoformat(),
        "reason": (
            "Created >= rule date (or undatable; fail-closed): coordination floors apply"
            if in_scope
            else "Created < rule date: grandfathered, coordination floors inert"
        ),
    }
    if not in_scope:
        return
    # Joined section body so a `Gather:`/`Release:`/`Issue closeout:` step whose
    # value wrapped onto a continuation line is matched, not false-rejected.
    section = _joined_section_body(text, COORDINATION_SECTION)
    missing: list[dict[str, str]] = []

    g_trig = gather_triggered(text)
    g_kind, _ = _parse_step(section, _GATHER_REF)
    g_ok = (not g_trig) or g_kind in _SATISFYING
    report["gather_floor"] = {"triggered": g_trig, "satisfied": g_ok, "evidence": g_kind}
    if g_trig and not g_ok:
        reason = (
            "`## Context Sources` names an external source (a URL — Slack/Notion/Docs/Drive "
            "links and bare web URLs all qualify) but `## Coordination Cues` records no "
            "`Gather: <ref>` step and no `Gather: n/a — <reason>` opt-out (>=30 chars); route "
            "the external source through `gather` or record the opt-out before flipping to complete"
        )
        report["gather_floor"]["reason"] = reason
        missing.append({"floor": "gather", "reason": reason})

    r_trig = release_triggered(text)
    r_kind, _ = _parse_step(section, _RELEASE_REF)
    r_ok = (not r_trig) or r_kind in _SATISFYING
    report["release_floor"] = {"triggered": r_trig, "satisfied": r_ok, "evidence": r_kind}
    if r_trig and not r_ok:
        reason = (
            "this run's recorded work names a release surface (a version bump or install-manifest "
            "edit) but `## Coordination Cues` records no `Release: <ref>` step and no "
            "`Release: n/a — <reason>` opt-out (>=30 chars); cut or verify the release through "
            "`release` or record the opt-out before flipping to complete"
        )
        report["release_floor"]["reason"] = reason
        missing.append({"floor": "release", "reason": reason})

    i_scope = issue_closeout_floor_applies(text)
    i_trig = i_scope and issue_closeout_triggered(text)
    i_kind, _ = _parse_step(section, _ISSUE_CLOSEOUT_REF)
    i_ok = (not i_trig) or i_kind in _SATISFYING
    report["issue_closeout_floor"] = {
        "in_scope": i_scope,
        "rule_date": ISSUE_CLOSEOUT_FLOOR_RULE_DATE.isoformat(),
        "triggered": i_trig,
        "satisfied": i_ok,
        "evidence": i_kind,
    }
    if i_trig and not i_ok:
        reason = (
            "this goal names tracked issue closeout work but `## Coordination Cues` records no "
            "`Issue closeout: <ref>` step and no `Issue closeout: n/a — <reason>` opt-out "
            "(>=30 chars); stage the close through `issue` and record the verifier proof before "
            "flipping to complete"
        )
        report["issue_closeout_floor"]["reason"] = reason
        missing.append({"floor": "issue_closeout", "reason": reason})

    if missing:
        report["coordination_missing"] = missing
        report["ok"] = False
