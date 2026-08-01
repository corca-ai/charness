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
    mask_fences,
    parse_created_date,
    section_body,
)

# Round 1 moved this to 2026-08-02 to arm the floor on a "20 in scope, 0 refused"
# measurement. Round 2 caught what that number was: ALL 20 are artifacts with no
# parseable `Created:` line, in scope only because the grandfather predicate fails
# closed. ZERO dated artifacts were in scope, so "0 refused" was a green over an
# empty denominator — the exact class this floor exists to make visible, committed
# inside the floor. Back to 2026-08-01, which puts real dated artifacts in scope
# and lets the report say something.
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

# What starts a new logical line. Ordered-list markers are here and NOT in the
# shared `join_soft_wraps` starter set, which is why this floor keeps its own.
_BLOCK_START = re.compile(r"^(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|\||>|[A-Z][\w -]{0,40}:\s)")


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
    segments = [segment.strip() for segment in line.split(_SEPARATOR)[1:]]
    short_unbacked: str | None = None
    for segment in segments:
        unbacked = _UNBACKED.match(segment)
        if not unbacked:
            continue
        why = unbacked.group("why").strip()
        if len(why) >= _MIN_UNBACKED_REASON:
            return True, "declared unbacked with a reason"
        # Remember it, do NOT return. Round 2 caught the first cut bailing here,
        # so `— unbacked: n/a — see `x.py`` was refused without ever reaching the
        # segment that cites a real source.
        short_unbacked = why
    # A source ANYWHERE on the line satisfies the floor, not only after the
    # separator. Round 2 measured the separator-mandatory form against the 127
    # dated checked-in artifacts: it refused 90 of them, including lines like
    # "- `bash scripts/run-quality.sh` full: 82 passed, 1 failed" — which cites
    # the exact command that produced the number, on the same line. Demanding a
    # particular PUNCTUATION rather than a citation is the form being wrong about
    # the repo, not the repo being wrong about the form.
    if _SOURCE_TOKEN.search(line):
        return True, "cites a source path, command, or URL"
    if short_unbacked is not None:
        return False, f"`unbacked:` needs a substantive reason (got {short_unbacked!r})"
    if _SEPARATOR not in line:
        return False, "no source cited on the line; add one, or ` — unbacked: <why>`"
    return False, (
        "the line states a figure but cites no path, command, or URL; cite one, or "
        "write `unbacked: <why>`"
    )


def _logical_lines(body: str) -> list[str]:
    """Group physical lines into logical ones, then drop headings and table rows.

    Soft wraps must be joined: `_INLINE_CODE` is single-line by construction, so a
    wrapped command left its continuation with no complete backtick pair and the
    command's ARGUMENTS were read as the author's figures.

    But joining with the shared `join_soft_wraps` alone was wrong in three ways
    round 2 traced, all of them silent PASSES: its block-starter set does not know
    ordered-list markers, so `2. 6515 tests passed` was absorbed into the bullet
    above it and inherited that line's citation; and a heading or table row
    immediately followed by a figure line absorbed it, after which the
    `startswith("#")` / `startswith("|")` skip discarded the figure entirely.
    Splitting on the local starter set first, and filtering AFTER grouping, fixes
    all three: a heading can no longer swallow the line beneath it.
    """
    logical: list[str] = []
    for raw in body.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        # A heading or table row CLOSES its own logical line. Without this the
        # continuation rule absorbs the line beneath a heading into it, and the
        # heading filter below then discards a real figure — the silent pass round
        # 2 traced. Filtering after grouping is not enough; grouping has to stop.
        closed = bool(logical) and (logical[-1].startswith("#") or logical[-1].startswith("|"))
        if not logical or closed or _BLOCK_START.match(stripped):
            logical.append(stripped)
        else:
            logical[-1] = f"{logical[-1]} {stripped}"
    return [line for line in logical if not line.startswith("#") and not line.startswith("|")]


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
    for line in _logical_lines(body):
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
    """Attach the figure-form report. NON-BLOCKING, on a measured denominator.

    This floor was deferred, then armed, then disarmed again, and only the last
    step rests on a number that means anything.

    Round 1 armed it on "20 in scope, 0 refused". Round 2 found that all 20 of
    those artifacts have no parseable `Created:` line — they were in scope only
    because the grandfather predicate fails closed — so ZERO dated artifacts were
    measured and the green was over an empty denominator. Measured properly,
    against all 127 dated checked-in artifacts: the strict form refuses 90, and
    the relaxed form this module now implements still refuses 44. A floor that
    would refuse a third of every closeout this repo has ever written is not
    describing a defect; it is describing a house style it disagrees with, and
    arming it would produce mass false refusals or mass artifact edits.

    So it reports. `ok` answers the form question honestly and `figure_lines`
    publishes the denominator, which is the one thing the armed version never
    did. Arming it needs the corpus to move toward the form, not the rule date to
    move past the corpus.
    """
    result = check(text)
    result["blocking"] = False
    report["final_verification_figure_form"] = result
