"""Coordination closeout floors for goal artifacts — gather + release.

Two presence-only closeout-evidence floors that give *teeth* to the two named
boundaries the find-skills routing cue under-serves, because skipping them is
silent and costly:

- **gather floor** — when the goal's ``## Context Sources`` names an external
  source (an ``http(s)://`` URL, which covers Slack / Notion / Google-Docs /
  Drive links and bare web URLs), the run must record a ``gather`` step in
  ``## Coordination Cues``: a ``Gather: <ref>`` line, or an explicit
  ``Gather: n/a — <reason>`` opt-out. ``CLAUDE.md`` mandates routing external
  sources through ``gather``; a goal that shaped from an external URL but never
  gathered it is the gap this closes.
- **release floor** — when the run's *recorded work* touches a release surface
  (a version bump or install-manifest edit, detected by precise path/action
  tokens — never the bare word "release"), the run must record a ``release``
  step: a ``Release: <ref>`` line, or ``Release: n/a — <reason>``. Without it
  ``achieve`` can flip ``complete`` over an unsynced version / manifest.

Both floors mirror the #253 deterministic-floor philosophy exactly:
presence/binding-only (they never classify whether prose is "good enough"),
clone-safe (in-file content, not mtime), block-the-blank at the ``complete``
flip, an explicit min-length opt-out valve, and grandfathered by ``Created``
date so goals shaped before the floors existed are not punished.

Kept a leaf module — self-contained ``_mask_fences`` / ``_section_*`` mirrors and
its own ``Created`` parse, no sibling import, the same convention
``goal_artifact_disposition.py`` follows — so neither it nor
``goal_artifact_closeout_evidence.py`` approaches the single-file line gate.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any

# The floors fire only for goals ``Created`` on or after their landing date. The
# floors land 2026-05-30, but several goals — this floor's own goal plus the
# same-day #253/#255 work — were already shaped that day *before* the floors
# existed, so the cutoff is 2026-05-31: every same-day in-flight goal is
# grandfathered, which is exactly the "not punished for predating the rule"
# intent. Clone-safe (in-file content, not mtime). Fail-CLOSED on a
# missing/malformed ``Created`` (mirrors #253) so a goal cannot dodge the floors
# by corrupting one line.
COORDINATION_FLOOR_RULE_DATE = date(2026, 5, 31)

# Opt-out min length mirrors the #253 disposition opt-out / skip discipline: a
# deliberate "no <step> applies" assertion recorded visibly (the Engelbart
# "say why if you depart" valve), long enough it cannot be a one-word bypass.
MIN_OPTOUT_REASON = 30

# The section that carries the find-skills routing cue and the gather/release
# step lines. Reference + opt-out detection is SCOPED to this section so a goal
# body that merely *describes* a ``Gather:`` / ``Release:`` line in prose (this
# floor's own goal does) cannot falsely satisfy a floor — the poisoning #253 hit
# with its opt-out (round-2 B-2) and solved by section-scoping.
COORDINATION_SECTION = "Coordination Cues"
# The section whose external links the gather floor watches.
CONTEXT_SOURCES_SECTION = "Context Sources"

_CREATED_LINE = re.compile(
    r"^[\s>*-]*Created\s*:\s*(\d{4}-\d{2}-\d{2})\b",
    re.MULTILINE | re.IGNORECASE,
)
# An http(s) URL is the external-source signal: Slack / Notion / Google-Docs /
# Drive links and bare web URLs are all URLs. Local repo paths and bare ``#N``
# issue refs are not, so a goal whose Context Sources lists only those is inert.
_EXTERNAL_URL = re.compile(r"https?://\S", re.IGNORECASE)

# gather/release step lines, anchored at line start (after list / blockquote
# markers) so a mid-line inline example (`Gather: n/a — <reason>` inside
# backticks or prose) is never read as a real line. Scoped to the Coordination
# Cues section on top of that.
_GATHER_REF = re.compile(r"^[\s>*-]*Gather\s*:\s*(\S.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE)
_RELEASE_REF = re.compile(r"^[\s>*-]*Release\s*:\s*(\S.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE)
# An ``n/a — <reason>`` value marks the line as an explicit opt-out rather than a
# reference; the reason must clear MIN_OPTOUT_REASON to count.
_NA_VALUE = re.compile(r"^n/?a\b[ \t]*[—–:-]+[ \t]*(\S.*)$", re.IGNORECASE)

# Release-surface tokens: a version bump or install-manifest edit names one of
# these in the goal's recorded work. Deliberately precise filenames / script
# names, never the bare word "release" (which appears in any goal that merely
# *mentions* the release skill as context — this floor's own goal references
# ``skills/public/release/`` and must not self-trip). All lowercase for a
# case-folded substring scan.
_RELEASE_SURFACE_TOKENS = (
    "bump_version",
    "publish_release",
    "marketplace.json",
    "charness-artifacts/release/",
)


def _mask_fences(text: str) -> str:
    """Blank fenced code-block regions to spaces (length / newlines preserved).

    A self-contained mirror of ``goal_artifact_lib._mask_fences`` so this module
    keeps no sibling import; fenced ``##`` / ``Created:`` / step lines must not be
    read as real artifact content. Unbalanced fences fail open (trust raw text).
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def _section_span(masked: str, heading: str) -> tuple[int, int] | None:
    """Return ``(body_start, body_end)`` offsets for the named section's body in
    ``masked`` (already fence-masked), from just after the heading line to the
    next heading of same-or-higher level, or EOF. ``None`` when the section is
    absent.
    """
    start = re.compile(
        rf"^(#{{1,6}})[ \t]+{re.escape(heading)}\b[^\n]*$",
        re.MULTILINE | re.IGNORECASE,
    ).search(masked)
    if start is None:
        return None
    level = len(start.group(1))
    body_start = masked.find("\n", start.end())
    if body_start == -1:
        return (len(masked), len(masked))
    body_start += 1
    nxt = re.compile(rf"^#{{1,{level}}}[ \t]+\S", re.MULTILINE).search(masked, body_start)
    return (body_start, nxt.start() if nxt else len(masked))


def _section_body(masked: str, heading: str) -> str | None:
    span = _section_span(masked, heading)
    if span is None:
        return None
    return masked[span[0] : span[1]]


def goal_created_date(text: str) -> date | None:
    """Parse the goal's ``Created:`` date; ``None`` when absent or malformed.

    Scoped to the masked body so a fenced example line is not read as the real
    ``Created:``. The caller fails closed (treats ``None`` as in-scope).
    """
    match = _CREATED_LINE.search(_mask_fences(text))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def coordination_floors_apply(text: str) -> bool:
    """Whether the gather/release floors fire for this goal (grandfather-by-
    ``Created``-date). Fail-CLOSED: a missing/malformed ``Created`` is in-scope."""
    created = goal_created_date(text)
    if created is None:
        return True
    return created >= COORDINATION_FLOOR_RULE_DATE


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
    """Attach the gather/release floor verdicts to ``report`` (mutates in place).

    For an in-scope goal (grandfather-by-``Created``): if a floor is *triggered*
    (external source in Context Sources / release-surface token in recorded work)
    and the Coordination Cues section carries no satisfying step line (a real
    ``Gather:``/``Release:`` reference or a ≥30-char ``n/a — <reason>`` opt-out),
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
    section = _section_body(_mask_fences(text), COORDINATION_SECTION)
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

    if missing:
        report["coordination_missing"] = missing
        report["ok"] = False
