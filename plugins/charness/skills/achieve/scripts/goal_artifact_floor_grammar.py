"""Shared rung-1 floor grammar for the Created-gated goal-artifact closeout floors.

The deterministic closeout floors (operator-queue, blocked-matrix, coordination,
phase-routing, disposition) each cloned the same three parse primitives:

- ``parse_created_date`` — read the goal's ``Created:`` date over the fence-masked
  body;
- ``is_floor_in_scope`` — the Created-gated grandfather predicate (fail-closed on
  an undatable goal);
- ``section_span`` / ``section_body`` — the level-aware ``## Section`` body slice.

This is the single substrate they now share. A pure leaf — it imports only
``goal_artifact_markdown`` (``mask_fences``) and mutates no report, so importing it
standalone never pulls in any floor's verdict logic.

**Rung-1 only.** These are presence/parse primitives, never honesty classifiers
(the rung-1/rung-2 split). The per-concept ``RULE_DATE`` constants, each floor's
narrow trigger predicate, the verdict/orchestration functions, and the
first-satisfying-wins logic stay in their own modules — only the cloned grammar
is collapsed here.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_markdown import (  # noqa: E402
    fences_balanced,
    join_soft_wraps,
    mask_fences,
    section_bounds,
)

# Permissive ``Created:`` line: tolerant of a leading ``>``/``-``/``*`` prefix,
# surrounding whitespace, and case, so a blockquoted or list-item ``Created:`` line
# is still read as the real date rather than silently treated as undatable. The
# canonical form three of the five floors already used; the operator-queue and
# blocked-matrix floors are migrated onto it (a deliberate, tested relaxation that
# grandfathers a correctly-dated pre-rule goal whose date sat behind a prefix).
_CREATED_LINE = re.compile(
    r"^(?P<prefix>[\s>*-]*)Created\s*:\s*(?P<value>\d{4}-\d{2}-\d{2})\b",
    re.MULTILINE | re.IGNORECASE,
)
_QUOTED_PREFIX = re.compile(r"[>*-]")


def parse_created_date(text: str) -> date | None:
    """Parse the goal's ``Created:`` date; ``None`` when absent or malformed.

    Scoped to the fence-masked body so a fenced example line is not read as the
    real ``Created:``. Callers fail closed (treat ``None`` as in-scope).

    Two disambiguation rules, because first-match-wins let a body that *quotes*
    another artifact's date line above its own silence every Created-gated floor
    at once:

    - **Plain lines outrank quoted/list ones.** A bare ``Created: <date>`` is the
      goal's own field; a ``> Created: …`` / ``- Created: …`` is as likely to be
      quoted-from-elsewhere. Only when no plain line exists do prefixed lines
      stay eligible, so the tested relaxation that grandfathers a correctly-dated
      goal whose only date sits behind a prefix is preserved.
    - **Conflicting dates inside the winning tier fail closed** (``None`` ->
      in-scope). Nothing in the text says which one is the artifact's own, so the
      surface must not pick one and render a scope verdict on it.

    An UNBALANCED fence fails closed for the same reason and is the sharper case:
    ``mask_fences`` fails open there, so a fenced template's ``Created:`` is
    indistinguishable from the goal's own field, and the earlier date silently
    took every Created-gated floor out of scope at once. Failing closed runs the
    floors; the goal is then refused with a message naming the unclosed fence
    rather than passing on a reading nobody established.
    """
    if not fences_balanced(text):
        return None
    plain: list[str] = []
    prefixed: list[str] = []
    for match in _CREATED_LINE.finditer(mask_fences(text)):
        target = prefixed if _QUOTED_PREFIX.search(match.group("prefix")) else plain
        target.append(match.group("value"))
    candidates = plain or prefixed
    if not candidates or len(set(candidates)) > 1:
        return None
    try:
        return date.fromisoformat(candidates[0])
    except ValueError:
        return None


def is_floor_in_scope(created: date | None, rule_date: date) -> bool:
    """Created-gated grandfather predicate with fail-closed semantics.

    A goal ``Created`` on/after ``rule_date`` is in-scope; an earlier goal is
    grandfathered out. A missing/malformed ``Created`` (``None``) is treated as
    in-scope, so a goal cannot dodge a floor by corrupting one line. Clone-safe:
    it reads in-file content, never mtime.
    """
    return created is None or created >= rule_date


def grandfathered_report(text: str, rule_date: date, concept: str) -> dict:
    """The out-of-scope payload every Created-gated floor returns identically.

    Grandfathering must never read as a satisfied floor, so the payload discloses
    its basis rather than reporting a bare ``ok``: ``evaluated: False`` plus the
    observed ``created`` date and the ``rule_date`` that excluded it. ``ok`` stays
    ``True`` because the floor is non-blocking out of scope, and ``applies``
    ``False`` is what says the check never ran.

    Extracted here rather than cloned again: the floors that share this shape are
    the reason this substrate module exists, and a fourth verbatim copy is the
    duplication the ratchet is right to refuse.
    """
    created = parse_created_date(text)
    return {
        "applies": False,
        "ok": True,
        "evaluated": False,
        "created": created.isoformat() if created else None,
        "rule_date": rule_date.isoformat(),
        # `self-declared` is load-bearing, not decoration: the scope verdict comes
        # from a line the artifact's own author wrote, with no corroborating
        # channel, and a reason that hid that basis would read as an established
        # fact. Carried by the shared helper so every floor keeps the disclosure
        # instead of one floor having it and the rest quietly not.
        "reason": (
            "not evaluated: self-declared `Created: "
            + (created.isoformat() if created else "?")
            + f"` precedes the {concept} rule date {rule_date.isoformat()}, so the "
            "floor is grandfathered off (not satisfied)"
        ),
    }


# Inline markup must never HIDE a correctly-filled cue. The step-line matchers
# each anchored on `^[\s>*-]*`, which tolerates a list/blockquote prefix but not
# the backticks, bold, or quotes authors actually write, so a `` `Routing: impl` ``
# line was invisible to the floor and a filled cue was refused outright. The repo
# already reads markup-tolerantly elsewhere (`validate_critique_artifacts.
# _LEADING_MARKUP_RE`); this is that same tolerance, shared by every cue.
_CUE_PREFIX_CHARS = r"\s`*_\"'>-"
# Value-side stripping deliberately omits `-` and `>`: those are PREFIX markers,
# and a cue value is free to start with neither. Stripping them from the value
# would eat real content for no gain.
_LEADING_CUE_MARKUP = re.compile(r"^[\s`*_\"']+")
_TRAILING_CUE_MARKUP = re.compile(r"[\s`*_\"']+$")


def cue_pattern(label: str) -> "re.Pattern[str]":
    """Compile the anchored ``<Label>: <value>`` coordination step-line matcher.

    ``label`` is a regex FRAGMENT, not a literal, so a multi-word cue passes its
    own separator (``r"Issue\\s+closeout"``). Anchored per physical line so an
    inline example never satisfies a floor — the property the original patterns
    had and this must keep.

    Every ``## Coordination Cues`` cue compiles through here so the prefix
    grammar cannot drift back apart: the backtick blindness this fixes was
    present in all five matchers identically, because all five were cloned.
    """
    return re.compile(
        rf"^[{_CUE_PREFIX_CHARS}]*{label}\s*:\s*(\S.*?)[ \t]*$",
        re.MULTILINE | re.IGNORECASE,
    )


# A cue value that is still the TEMPLATE PLACEHOLDER never satisfies anything.
# This guard is what makes markup tolerance safe: the old `^[\s>*-]*` prefix
# rejected a backticked `` `Gather: n/a — <reason>` `` seed line only as a side
# effect of being blind to backticks, so widening the prefix to fix the real
# false refusal simultaneously exposed every documentation example that happens
# to start a physical line. Anchoring alone cannot tell a seeded example from a
# filled cue; the unreplaced `<...>` can, and it is the honest discriminator.
# CONTAINS, not EQUALS. A first cut anchored this to the whole value, which two
# real shapes walked straight through:
#   - the template's own seeded cue form is TWO placeholders joined by prose
#     (`Successor goal: <path-or-ref> — <why none was designed>`), and
#   - `joined_section_body` folds a continuation line into the value, so
#     `` `Gather: <ref>` `` + "(still deciding which artifact to point at)" became
#     a value that merely *started* with a placeholder.
# Both then classified as a real `ref` and SATISFIED a floor while saying in plain
# English that they were unfilled. An unreplaced `<...>` anywhere in a cue value
# means the author did not fill it in, wherever it sits.
# A first cut spelled the token body as an explicit character class. It was
# simultaneously too PERMISSIVE and too NARROW, and both directions were live
# defects: `/` and `.` in the class swallowed an autolinked artifact path
# (`<charness-artifacts/goals/2026-08-09-next.md>`) and a generic in an opt-out
# reason (`Dict<str, int>`) into false REFUSALS — the very bug this slice exists
# to fix — while `:` and `(` missing from it let `<TBD: the next goal>` and
# `<link to the thread (if any)>` classify as real references and SATISFY a floor.
# The body is therefore permissive, with two targeted exclusions instead:
#   - it must START WITH A LETTER, so `... from <5 items to > 30` is prose, and
#   - it must not be preceded by an identifier character, so `Dict<str, int>` and
#     `List<String>` are generics, not placeholders.
_ANGLE_TOKEN = re.compile(r"(?<![A-Za-z0-9_])<([A-Za-z][^<>\n]{0,79})>")
# A markdown AUTOLINK is a filled value, not a placeholder: a path (contains `/`),
# a scheme, or a bare filename with an extension. Checked on the token body so
# `<charness-artifacts/goals/2026-08-09-next.md>` reads as the reference it is.
_AUTOLINK_BODY = re.compile(
    r"^(?:[a-z][a-z0-9+.-]*://\S+|mailto:\S+|[^\s]*/[^\s]*|[^\s]+\.[A-Za-z0-9]{1,8})$",
    re.IGNORECASE,
)


def has_unfilled_placeholder(value: str) -> bool:
    """True when the value still carries an unreplaced ``<placeholder>``.

    CONTAINS, not EQUALS. An equals-the-whole-value check let two real shapes
    through: the template's own seeded cue form is TWO placeholders joined by
    prose (``<path-or-ref> — <why none was designed>``), and
    ``joined_section_body`` folds a continuation line into the value, so
    `` `Gather: <ref>` `` plus "(still deciding which artifact to point at)"
    merely *started* with a placeholder. Both then classified as a real ``ref``
    and satisfied a floor while saying in plain English that they were unfilled.
    """
    return any(
        not _AUTOLINK_BODY.match(match.group(1))
        for match in _ANGLE_TOKEN.finditer(value)
    )


def strip_cue_markup(value: str) -> str:
    """Strip wrapping inline markup from a matched cue value.

    ``` `Routing: impl` ``` captures a trailing backtick and ``**Routing:** impl``
    captures a leading ``**``; both are markup the author wrapped the cue in, not
    the value. Left in place they corrupt two decisions: the ``n/a — <reason>``
    opt-out length measured against ``MIN_OPTOUT_REASON`` (markup would pad a
    short reason over the floor), and the value echoed back in a refusal reason.
    """
    return _TRAILING_CUE_MARKUP.sub("", _LEADING_CUE_MARKUP.sub("", value)).strip()


# Long enough that an opt-out cannot be a one-word bypass.
MIN_OPTOUT_REASON = 30
# A cue is satisfied by a real reference or a valid opt-out; `optout_short` is
# present-but-not-satisfying, which is a near-miss worth reporting back.
SATISFYING_CUE_KINDS = frozenset({"ref", "optout"})
# ONE pattern for every opt-out, reasoned or not. Enumerating the separators
# (`[—–:-]`) was the wrong shape twice over: a REASONLESS `n/a` fell through to
# `ref` and SATISFIED the floor — making the emptiest possible opt-out the
# strongest one, while a one-word reason was correctly refused — and any
# separator outside the enumerated four did the same, so `n/a, nope` satisfied
# while `n/a — nope` was refused, a one-character bypass of MIN_OPTOUT_REASON.
# The separator run is therefore optional and open, the reason is optional, and
# `n\s*/?\s*a` accepts `na` / `N/A` / `n / a`. The trailing `\b` keeps `national`
# and `n/august` out.
_NA_CUE_VALUE = re.compile(
    r"^n\s*/?\s*a\b[ \t]*[—–:;.,()\[\]/\\-]*[ \t]*(.*)$",
    re.IGNORECASE,
)


def classify_cue_step(value: str) -> tuple[str, str]:
    """Classify one cue value: ``"ref"``, ``"optout"``, or ``"optout_short"``.

    Rung-1: this is parse + a FORM floor (is the opt-out reason long enough to be
    a sentence), never an honesty judgment about whether the reason is *true*.
    That judgment stays with the author and the fresh-eye round.

    Shared rather than cloned because the coordination and phase-routing floors
    carried this function verbatim, down to the constant — exactly the third-copy
    shape this substrate module exists to absorb. The first-satisfying-wins LOOP
    stays in each floor, per this module's rung-1 boundary: routing additionally
    requires the routed skill to be NAMED, so the two loops are genuinely
    different policies over this one shared classifier.
    """
    na = _NA_CUE_VALUE.match(value)
    if na is not None:
        reason = na.group(1).strip()
        return ("optout" if len(reason) >= MIN_OPTOUT_REASON else "optout_short"), reason
    return "ref", value


CONTEXT_SOURCES_SECTION = "Context Sources"
RECORDED_WORK_SECTIONS = ("Slice Log", "Final Verification")
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


def issue_closeout_triggered(text: str) -> bool:
    """True when the goal records tracked issue resolution work.

    Context Sources can name the tracked issue explicitly. Recorded work can also
    trigger through close keywords in the sections where achieved work is
    archived, not in planning/boundary text.

    This is the ONE trigger predicate that lives here rather than in a floor.
    The module header says each floor's narrow trigger predicate stays in its own
    module, and that rule holds where the floors ask different questions — but
    the coordination floor and the phase-routing floor asked THIS one identically,
    down to the regexes, in two verbatim copies. Two floors consuming one shared
    answer is the substrate case; two floors with their own questions is not.
    """
    masked = mask_fences(text)
    context = section_body(masked, CONTEXT_SOURCES_SECTION) or ""
    if _TRACKED_ISSUE_CONTEXT.search(context):
        return True
    work = "\n".join(section_body(masked, heading) or "" for heading in RECORDED_WORK_SECTIONS)
    return _CLOSE_KEYWORD.search(work) is not None


def classify_cue_line(raw: str) -> tuple[str | None, str]:
    """Full per-line cue classification, shared by every floor's match loop.

    ``strip_cue_markup`` -> ``classify_cue_step`` -> demote inert values. Returns
    ``(None, "")`` when the line is not a step line at all.

    Two inert shapes, separated because they are different authoring facts and
    the author deserves the right diagnostic for each:

    - **A left-in ``<placeholder>``** — on either side of the opt-out grammar —
      means the author never filled this cue. It is not a step line. The seeded
      template lines are exactly this shape, and calling them a near-miss would
      tell an author their opt-out reason is too short when they never wrote one.
    - **A reasonless ``n/a``** (``n/a``, ``n/a —``) IS a step line: the author
      typed the cue and declined it, they just gave no reason. It stays
      ``optout_short`` — non-satisfying, which is what the floor acts on, while
      keeping the actionable message ("your opt-out has no reason").

    An empty REFERENCE (`` `Successor goal:` `` stripped to ``""``) is the first
    shape, not the second: a bare label is not a decision.

    Shared here rather than written into each loop: the two loops already had to
    be collapsed once for the duplicate ratchet, and this is the exact seam that
    would re-diverge.
    """
    kind, value = classify_cue_step(strip_cue_markup(raw))
    if has_unfilled_placeholder(value):
        return None, ""
    if kind == "ref" and not value.strip():
        return None, ""
    return kind, value


def section_span(masked: str, heading: str) -> tuple[int, int] | None:
    """Return ``(body_start, body_end)`` offsets for the named section's body in
    ``masked`` (already fence-masked), from just after the heading line to the
    next heading of same-or-higher level, or EOF. ``None`` when the section is
    absent (vs an empty span when present-but-empty).

    Level-aware: a ``### Subsection`` inside the scoped ``## Section`` does not end
    the body. This is the variant coordination / phase-routing / disposition all
    shared verbatim; the operator-queue / blocked-matrix floors keep their own
    flat ``## ``-only variant unless a divergence-exposing proof migrates them.
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


def section_body(masked: str, heading: str) -> str | None:
    """The body of the named section (heading excluded), or ``None`` when absent.

    ``masked`` must already be fence-masked. Thin wrapper over ``section_span``.
    """
    span = section_span(masked, heading)
    if span is None:
        return None
    return masked[span[0] : span[1]]


def masked_section_body(text: str, heading: str) -> str | None:
    """Fence-masked, stripped body of one section; ``None`` when absent.

    Locate the section on the masked copy AND parse the masked slice, so an
    illustrative line inside a code fence cannot satisfy a floor.

    Built on ``section_bounds`` -- the FLAT, exact-name, case-SENSITIVE ``## ``
    walk -- and deliberately NOT on ``section_body``/``section_span``. The
    operator-queue and blocked-matrix floors are its callers, and ``section_span``
    above says in as many words that those two keep the flat variant "unless a
    divergence-exposing proof migrates them". A first cut of this helper routed
    them through ``section_span`` anyway: that would have widened them to
    ``#``..``######``, made them case-insensitive, and made them accept trailing
    text after the heading name -- so an ordinary ``### Operator Decision Queue``
    block quoted inside a slice log could satisfy a ``complete``-state floor while
    the real H2 section still held scaffold prose. A false green at a terminal
    boundary, latent in every artifact. Round-2 review caught it.

    ``None`` and ``""`` stay distinct: "no such heading" and "heading present but
    empty" are different facts, and callers branch on it.
    """
    masked = mask_fences(text)
    bounds = section_bounds(masked, heading)
    return None if bounds is None else masked[bounds[0]:bounds[1]].strip()


def joined_section_body(text: str, heading: str) -> str | None:
    """``section_body`` over fence-masked ``text`` with soft-wraps joined.

    The step-line coordination floors match ``Routing:``/``Gather:``/``Release:``/
    ``Issue closeout:`` per *physical* line; joining first means a correct value
    whose tail wrapped onto a continuation line is read whole. This is the one
    seam both step-line floors share, so the mask + slice + join lives here rather
    than copied into each floor. ``None`` when the section is absent.
    """
    body = section_body(mask_fences(text), heading)
    return join_soft_wraps(body) if body is not None else None
