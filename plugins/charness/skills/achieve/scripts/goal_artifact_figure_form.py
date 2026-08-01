"""Form floor for figures stated in a goal artifact's `## Final Verification`.

A closeout that says "6 mutants survived" or "94.9% score" is making a claim a
later session will plan against. The recurring defect is not a wrong number; it
is a number with no way to tell whether anyone measured it.

**This floor checks FORM, never honesty.** "Is this number backed" is not
machine-decidable, and a validator that pretended to decide it would ship as a
Goodhart proxy — the exact class this repo refuses. So the rule is the same enum
idiom the other closeout floors use: a figure line must carry a source, or say
in writing that it has none.

    <value> — <source path, command, or URL>
    <value> — unbacked: <why>

Whether the cited source actually says the number stays author judgment plus the
fresh-eye round. What this removes is the silent third option.

Rung-1: presence/parse only, Created-gated like every sibling floor.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import (  # noqa: E402
    grandfathered_report,
    is_floor_in_scope,
    mask_fences,
    parse_created_date,
    section_body,
)

FIGURE_FORM_RULE_DATE = date(2026, 8, 1)
SECTION = "Final Verification"

# Evidence lines with their own floors. They are paths, not figures, and a path
# can contain digits (`v3-0-1-notes.md`); reading them here would double-refuse.
_EVIDENCE_LABEL = re.compile(
    r"^[\s>*-]*(?:Retro|Host[- ]log[- ]probe|Disposition[- ]review|Early[- ]close[- ]report)\s*:",
    re.IGNORECASE,
)

# Spans whose digits are never the author's figure: inline code, markdown link
# targets, and bare URLs. Blanked (length-preserving) before figure detection.
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
_BARE_URL = re.compile(r"https?://\S+")

# A bare figure: 1-6 digits, optional thousands groups, optional decimal, optional
# percent. The lookarounds are the whole point — they exclude the tokens that are
# digits without being figures:
#   `2026-08-01` (date)     -> trailing `-` blocked
#   a bare issue ref        -> leading `#` blocked
#   `v3.0.1` (version)      -> leading `v`/`.` blocked
#   `40.7s` (unit-suffixed) -> trailing word char blocked
#   `scripts/x1.py` (path)  -> leading/trailing `/` and `.` blocked
# Excluding a real figure is the safe direction: a missed line is a floor that
# did not fire, while a false refusal is a gate that makes an honest closeout
# unrecordable and trains people to pad text until it passes.
_FIGURE = re.compile(r"(?<![\w.#/,-])\d{1,3}(?:,\d{3})*(?:\.\d+)?%?(?![\w./,-])")

# The source side. A path, a command, a URL, or a backticked span reads as a
# citation; prose alone does not. `unbacked:` is the explicit opt-out and needs a
# substantive reason, not the bare word.
_UNBACKED = re.compile(r"^unbacked\s*:\s*(?P<why>\S.*)$", re.IGNORECASE)
_SOURCE_TOKEN = re.compile(
    r"`[^`\n]+`"                      # a backticked path or command
    r"|https?://\S+"                  # a URL (a workflow run, an issue)
    r"|\]\([^)\n]+\)"                 # a markdown link target
    r"|(?:[\w.-]+/)+[\w.-]+"          # a bare repo-relative path
)
_MIN_UNBACKED_REASON = 12

# Em dash with surrounding space is the artifact's established separator. A hyphen
# is deliberately NOT accepted: prose uses it mid-sentence constantly, so allowing
# it would make almost any sentence satisfy the floor by accident.
_SEPARATOR = " — "


def applies(text: str) -> bool:
    return is_floor_in_scope(parse_created_date(text), FIGURE_FORM_RULE_DATE)


def _blank_non_figure_spans(line: str) -> str:
    """Blank code/link/URL spans, preserving length so offsets stay usable."""
    masked = line
    for pattern in (_INLINE_CODE, _LINK_TARGET, _BARE_URL):
        masked = pattern.sub(lambda m: " " * len(m.group(0)), masked)
    return masked


def line_carries_figure(line: str) -> bool:
    """True when the line states a figure of its own (outside code/links/URLs)."""
    if _EVIDENCE_LABEL.match(line):
        return False
    return _FIGURE.search(_blank_non_figure_spans(line)) is not None


def line_satisfies_form(line: str) -> tuple[bool, str]:
    """Return (ok, reason) for a figure line's `<value> — <source>` form."""
    if _SEPARATOR not in line:
        return False, "no ` — ` separator, so the figure names no source"
    # Rightmost separator: a value may legitimately contain one ("6 of 9 — see …"
    # is one figure line, not two), and the SOURCE is what trails.
    source = line.rsplit(_SEPARATOR, 1)[1].strip()
    if not source:
        return False, "` — ` present but the source side is empty"
    unbacked = _UNBACKED.match(source)
    if unbacked:
        why = unbacked.group("why").strip()
        if len(why) < _MIN_UNBACKED_REASON:
            return False, f"`unbacked:` needs a substantive reason (got {why!r})"
        return True, "declared unbacked with a reason"
    if _SOURCE_TOKEN.search(source):
        return True, "cites a source path, command, or URL"
    return False, (
        "the source side is prose with no path, command, or URL; cite one, or "
        "write `unbacked: <why>`"
    )


def check(text: str) -> dict[str, Any]:
    if not applies(text):
        return grandfathered_report(text, FIGURE_FORM_RULE_DATE, "figure-form")
    # `section_body` requires a fence-masked body: an illustrative figure inside a
    # code fence (this section's own template shows the accepted forms) is the
    # author demonstrating the shape, not stating a number.
    body = section_body(mask_fences(text), SECTION)
    result: dict[str, Any] = {
        "applies": True,
        "rule_date": FIGURE_FORM_RULE_DATE.isoformat(),
    }
    if body is None:
        # The section's presence is another floor's question; this one has
        # nothing to read and says so rather than reporting a satisfied form.
        result["ok"] = True
        result["evaluated"] = False
        result["figure_lines"] = 0
        result["reason"] = f"no `## {SECTION}` section to read"
        return result
    offenders: list[dict[str, str]] = []
    figure_lines = 0
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        if not line_carries_figure(line):
            continue
        figure_lines += 1
        ok, reason = line_satisfies_form(line)
        if not ok:
            offenders.append({"line": line, "reason": reason})
    result["figure_lines"] = figure_lines
    result["offenders"] = offenders
    result["ok"] = not offenders
    if offenders:
        result["reason"] = (
            f"{len(offenders)} figure line(s) in `## {SECTION}` state a number with no "
            "checkable source; use `<value> — <source path or command>` or "
            "`<value> — unbacked: <why>`"
        )
    else:
        result["reason"] = f"{figure_lines} figure line(s) carry a source or an explicit unbacked reason"
    return result


def apply_figure_form_floor(report: dict[str, Any], text: str) -> None:
    """Attach the figure-form report. Deliberately NON-BLOCKING — see below.

    This shipped as a captured observable rather than a refusal, and the reason is
    a measurement, not caution. Armed as a blocker with its rule date, it refuses
    2 of the 23 in-scope checked-in goal artifacts — both of them FROZEN
    same-day closeouts. Date granularity cannot separate "this goal" from "a goal
    completed this morning", so the only way to green them is to edit finished
    artifacts to satisfy a rule written after them. That is the Goodhart move this
    repo's validators exist to refuse, and it is a named stop condition of the
    goal that built this floor.

    Narrowing the trigger does not rescue it: the refused lines are real figures
    (`82 passed, 1 failed`, `9 of 9 rows`), not parser noise, so any predicate
    honest enough to catch a bare figure catches theirs too. The blocker is
    deferred as its own decision rather than forced through here.

    `ok` on this fragment therefore reports the FORM QUESTION's answer, and the
    caller's `report["ok"]` is untouched. It is not a green: it never reports a
    pass over something it did not read, and `figure_lines` publishes the
    denominator so a reader can see what it examined.
    """
    result = check(text)
    result["blocking"] = False
    report["final_verification_figure_form"] = result
