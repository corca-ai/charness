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
    fences_balanced,
    grandfathered_report,
    is_floor_in_scope,
    join_soft_wraps,
    mask_fences,
    parse_created_date,
    section_body,
)

# 2026-08-02, not 2026-08-01, and the date is the whole reason this floor could be
# ARMED instead of deferred. At 2026-08-01 it refuses 2 of 23 in-scope checked-in
# artifacts, both FROZEN same-day closeouts — and greening those would mean editing
# finished records to satisfy a rule written after them. One day later: 20 in scope,
# 0 refused. Grandfathering the goal that BUILT this floor is the acceptable trade,
# because the floor exists for the goals that come after it.
FIGURE_FORM_RULE_DATE = date(2026, 8, 2)
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

# A bare figure: any digit run, optional thousands groups, optional decimal,
# optional percent. Round 1 caught the first cut writing `\d{1,3}(?:,\d{3})*`,
# which — with no comma group — capped the run at THREE digits and made `1024
# mutants tested` invisible to a floor built to catch exactly that line.
# The lookarounds are the whole point — they exclude the tokens that are
# digits without being figures:
#   `2026-08-01` (date)     -> trailing `-` blocked
#   a bare issue ref        -> leading `#` blocked
#   `v3.0.1` (version)      -> leading `v`/`.` blocked
#   `40.7s` (unit-suffixed) -> trailing word char blocked
#   `scripts/x1.py` (path)  -> leading/trailing `/` and `.` blocked
# Excluding a real figure is the safe direction: a missed line is a floor that
# did not fire, while a false refusal is a gate that makes an honest closeout
# unrecordable and trains people to pad text until it passes.
_FIGURE = re.compile(r"(?<![\w.#/-])\d+(?:,\d{3})*(?:\.\d+)?%?(?![\w./-])")

# The source side. A path, a command, a URL, or a backticked span reads as a
# citation; prose alone does not. `unbacked:` is the explicit opt-out and needs a
# substantive reason, not the bare word.
_UNBACKED = re.compile(r"^unbacked\s*:\s*(?P<why>\S.*)$", re.IGNORECASE)
# Round 1 caught the bare-path arm as `(?:[\w.-]+/)+[\w.-]+`, which any prose
# slash satisfies — `pass/fail`, `2/3`, `and/or` were all certified as "cites a
# source". That is worse than a miss: the line is detected as a figure and then
# affirmatively declared sourced. A bare path now needs a file extension.
_SOURCE_TOKEN = re.compile(
    r"`[^`\n]+`"                             # a backticked path or command
    r"|https?://\S+"                         # a URL (a workflow run, an issue)
    r"|\]\([^)\n]+\)"                        # a markdown link target
    r"|(?:[\w.-]+/)+[\w-]+\.[A-Za-z][\w]*"   # a bare repo-relative path with a suffix
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
    """Return (ok, reason) for a figure line's `<value> — <source>` form.

    EVERY segment after the first separator is checked, not just the last. Round 1
    caught the first cut taking `rsplit(sep, 1)`, which false-refused a line that
    cites a source and then keeps talking:

        - 9 of 9 rows — `charness-artifacts/critique/x.md` — the 10th was out of scope

    Rightmost-wins read that as the prose tail and refused a correctly-sourced
    line. A false refusal is the expensive direction here: it makes an honest
    closeout unrecordable and teaches people to pad text until the gate passes.
    """
    if _SEPARATOR not in line:
        return False, "no ` — ` separator, so the figure names no source"
    segments = [segment.strip() for segment in line.split(_SEPARATOR)[1:]]
    if not any(segments):
        return False, "` — ` present but the source side is empty"
    for segment in segments:
        unbacked = _UNBACKED.match(segment)
        if unbacked:
            why = unbacked.group("why").strip()
            if len(why) < _MIN_UNBACKED_REASON:
                return False, f"`unbacked:` needs a substantive reason (got {why!r})"
            return True, "declared unbacked with a reason"
        if _SOURCE_TOKEN.search(segment):
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
    result: dict[str, Any] = {
        "applies": True,
        "rule_date": FIGURE_FORM_RULE_DATE.isoformat(),
    }
    if not fences_balanced(text):
        # `applies()` fails CLOSED on an undatable goal while `mask_fences` fails
        # OPEN on an unbalanced fence, so without this the two combine into the
        # worst case: forced in scope, with fenced template examples read as real
        # figures. Refusing to render a verdict is the honest answer — and it is
        # not a silent pass, because `evaluated: False` says the floor did not run.
        result["ok"] = True
        result["evaluated"] = False
        result["figure_lines"] = 0
        result["reason"] = (
            "not evaluated: the artifact's code fences are unbalanced, so a fenced "
            "example cannot be told from a stated figure; balance the fences to "
            "get a verdict"
        )
        return result
    body = section_body(mask_fences(text), SECTION)
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
    # Join soft wraps before reading lines. `_INLINE_CODE` is single-line by
    # construction, so a wrapped command (`... --repo-root .` / `--limit 250\``)
    # left its second physical line with no complete backtick pair — nothing was
    # masked, and a command ARGUMENT was read as the author's figure.
    for raw in join_soft_wraps(body).splitlines():
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
    """Attach the figure-form report and refuse the flip when a figure is bare.

    This is ARMED, and the rule date is why. At `2026-08-01` it refused 2 of 23
    in-scope checked-in artifacts, both frozen same-day closeouts, and the only
    way to green those would have been to edit finished records to satisfy a rule
    written after them. The first cut read that as "this floor cannot have teeth"
    and shipped it non-blocking. A bounded round caught the cheaper lever: one day
    later the corpus is 20 in scope and 0 refused, so the floor arms with no
    frozen artifact touched. Grandfathering the goal that built it is the price,
    and it is the right one — the floor exists for the goals that come after.
    """
    result = check(text)
    report["final_verification_figure_form"] = result
    if result["applies"] and not result["ok"]:
        report["ok"] = False
