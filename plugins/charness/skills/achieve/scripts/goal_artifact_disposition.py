"""Improvement-disposition closeout gate — the deterministic rung.

Gives the After-phase disposition rule teeth without a prose word-list (round-2
critique proved a classifier over-fires or passes pure narration). This module
is the **deterministic floor** (rung 1):

- **1a block-the-blank** — refuse the ``complete`` flip when the cited retro
  lists actionable improvements but the goal's ``## Auto-Retro`` is blank and no
  opt-out is recorded. Emptiness/structure only; never classifies prose.
- **1b review-ran evidence** — require a bound ``Disposition review:`` line so a
  fresh-eye review provably ran (presence/binding-only BY DESIGN — wired in via
  ``CLOSEOUT_EVIDENCE_NAMES`` by the closeout-evidence wrapper, gated here by
  scope).

The substantive per-improvement judgment (*did the Auto-Retro genuinely dispose
each improvement?*) is **rung 2** — a fresh-eye subagent that records a verdict a
human audits. Determinism categorically cannot make that call, so this module
never tries; a deterministic false-positive trains token-theater and is worse
than a false-negative, so the teeth stay narrow and ungameable.

Kept a leaf module (no sibling imports) so it stays self-contained and neither it
nor ``goal_artifact_closeout_evidence.py`` approaches the single-file line gate.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

# Both rungs fire only for goals Created on or after the disposition rule's
# landing date (commit 73d2d34, 2026-05-30, inclusive). A goal shaped before the
# rule existed had no chance to plan its Auto-Retro/review around it, so
# Created-keying grandfathers exactly those in-flight goals; completion-keying
# would punish them. Clone-safe: the date is in-file content, not mtime.
DISPOSITION_RULE_DATE = date(2026, 5, 30)

# The Auto-Retro opt-out: a deliberate "no improvement needs active disposition"
# assertion, recorded visibly (the Engelbart "say why if you depart" valve, not a
# silent skip). A min-length floor mirrors the skip discipline so it cannot be a
# one-word bypass; rung 2 can falsify a false "none".
MIN_OPTOUT_REASON = 30

_CREATED_LINE = re.compile(
    r"^[\s>*-]*Created\s*:\s*(\d{4}-\d{2}-\d{2})\b",
    re.MULTILINE | re.IGNORECASE,
)
_DISPOSITION_OPTOUT = re.compile(
    r"^[\s>*-]*Retro dispositions\s*:\s*none\b[ \t]*[—–:-]+[ \t]*(\S.*?)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)
_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S")

# The goal-artifact template seeds a visible ``Retro dispositions: TODO — …``
# placeholder under ``## Auto-Retro`` so an active run sees the disposition
# obligation from the start. An *untouched* placeholder line must still read as
# blank-equivalent, else seeding it would silently disable rung 1a
# (block-the-blank) for any goal that fills the disposition-review line but never
# replaces the TODO. The line is treated as content only once the ``TODO`` is
# replaced by a real disposition (``Retro dispositions: none — …`` opt-out or an
# ``applied:``/``issue …`` per-improvement record).
_DISPOSITION_PLACEHOLDER = re.compile(
    r"^[\s>*-]*Retro dispositions\s*:\s*(?:TODO|TBD|<[^>]*>|FIXME)\b[^\n]*$",
    re.MULTILINE | re.IGNORECASE,
)


def _mask_fences(text: str) -> str:
    """Blank fenced code-block regions to spaces (length/newlines preserved).

    A self-contained mirror of ``goal_artifact_lib._mask_fences`` so this module
    keeps no sibling import; fenced ``##`` / ``Created:`` / opt-out lines must not
    be read as real artifact content.
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


def goal_created_date(text: str) -> date | None:
    """Parse the goal's ``Created:`` date; ``None`` when absent or malformed.

    Scoped to the masked body so a fenced example line cannot be read as the
    real ``Created:``. The caller fails closed (treats ``None`` as in-scope).
    """
    match = _CREATED_LINE.search(_mask_fences(text))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def disposition_gate_applies(text: str) -> bool:
    """Whether the disposition rungs fire for this goal (grandfather-by-
    ``Created``-date). Fail-CLOSED: a missing/malformed ``Created:`` is treated
    as in-scope, so a goal cannot dodge both rungs by corrupting one line."""
    created = goal_created_date(text)
    if created is None:
        return True
    return created >= DISPOSITION_RULE_DATE


def _section_body(masked: str, heading: str) -> str | None:
    """Return the body of the named section (heading line excluded), from the
    heading to the next heading of the same-or-higher level, or EOF.

    ``masked`` must already be fence-masked. Returns ``None`` when the section is
    absent (vs ``""`` when present-but-empty).
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
        return ""
    body_start += 1
    nxt = re.compile(rf"^#{{1,{level}}}[ \t]+\S", re.MULTILINE).search(masked, body_start)
    return masked[body_start : nxt.start() if nxt else len(masked)]


def auto_retro_is_blank(text: str) -> bool:
    """True when the goal's ``## Auto-Retro`` section is absent, whitespace-only,
    or carries only the untouched ``Retro dispositions: TODO — …`` scaffold
    placeholder (scanned over the Auto-Retro span only, fences masked). This is
    the only content judgment the deterministic rung makes — emptiness, never
    substance. Treating the seeded placeholder as blank-equivalent keeps rung 1a
    (block-the-blank) live: seeding a visible TODO must not silently disable it.
    """
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if body is None or not body.strip():
        return True
    residual = _DISPOSITION_PLACEHOLDER.sub("", body)
    return not residual.strip()


def retro_lists_improvements(retro_text: str) -> bool:
    """True when the retro's ``## Next Improvements`` section carries ≥1 list item.

    Presence/structure only — never classifies the prose (the round-2 word-list
    trap). An absent or renamed section is inert (returns False), so block-the-
    blank cannot fire without a structurally-identifiable improvement to dispose.
    """
    body = _section_body(_mask_fences(retro_text), "Next Improvements")
    if body is None:
        return False
    return any(_LIST_ITEM.match(line) for line in body.splitlines())


def find_disposition_optout(text: str) -> str | None:
    """Return the opt-out reason when a valid ``Retro dispositions: none — <reason>``
    line (≥ ``MIN_OPTOUT_REASON`` chars) sits in the Auto-Retro span, else ``None``.

    Auto-Retro-scoped on purpose: a full-text scan is poisoned — real goal bodies
    describe the marker while specifying it (round-2 B-2), which would falsely
    exempt them.
    """
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if not body:
        return None
    match = _DISPOSITION_OPTOUT.search(body)
    if match is None:
        return None
    reason = match.group(1).strip()
    return reason if len(reason) >= MIN_OPTOUT_REASON else None


def _bound_retro_path(report: dict[str, Any]):
    """The path of the satisfied + bound ``retro_artifact`` evidence file, if any.

    A retro whose F1 binding failed is excluded (it is already an ok=False
    binding failure; block-the-blank must not read an unbound retro's body).
    """
    blocked = {entry["name"] for entry in report.get("binding_failures", [])}
    found = None
    for entry in report["satisfied"]:
        if (
            entry["name"] == "retro_artifact"
            and entry.get("via") == "evidence"
            and entry["name"] not in blocked
        ):
            found = entry["path"]
    return found


def apply_disposition_rungs(report: dict[str, Any], text: str, in_scope: bool) -> None:
    """Attach the disposition-gate verdict to ``report`` (mutates in place).

    Rung 1a (block-the-blank): refuse the flip when the bound retro lists ≥1
    improvement, the goal's ``## Auto-Retro`` is blank, and no opt-out is
    recorded. Fires independently of any rung-1b ``disposition_review`` skip
    (host portability: a subagent-blocked host degrades to rung 1 only, and the
    blank check must still fire). The substantive per-improvement judgment is
    rung 2's job — recorded for a human, never scored here.
    """
    created = goal_created_date(text)
    report["disposition_scope"] = {
        "in_scope": in_scope,
        "created": created.isoformat() if created else None,
        "rule_date": DISPOSITION_RULE_DATE.isoformat(),
        "reason": (
            "Created >= rule date (or undatable; fail-closed): disposition gate applies"
            if in_scope
            else "Created < rule date: grandfathered, disposition gate inert"
        ),
    }
    optout = find_disposition_optout(text)
    if optout is not None:
        report["disposition_optout"] = {"reason": optout}
    if not in_scope:
        return
    retro_path = _bound_retro_path(report)
    has_improvements = False
    if retro_path is not None:
        try:
            retro_text = Path(retro_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            retro_text = ""
        has_improvements = retro_lists_improvements(retro_text)
    blank = auto_retro_is_blank(text)
    report["retro_improvements_present"] = has_improvements
    report["auto_retro_blank"] = blank
    if has_improvements and blank and optout is None:
        report["disposition_blank"] = {
            "reason": (
                "the cited retro lists actionable `## Next Improvements` but the goal's "
                "`## Auto-Retro` is blank and no `Retro dispositions: none — <reason>` opt-out "
                "is recorded; disposition each improvement (`applied: <what>` or `issue <id>`) "
                "or record the opt-out before flipping to complete"
            )
        }
        report["ok"] = False
