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
from goal_artifact_markdown import join_soft_wraps, mask_fences  # noqa: E402

# Permissive ``Created:`` line: tolerant of a leading ``>``/``-``/``*`` prefix,
# surrounding whitespace, and case, so a blockquoted or list-item ``Created:`` line
# is still read as the real date rather than silently treated as undatable. The
# canonical form three of the five floors already used; the operator-queue and
# blocked-matrix floors are migrated onto it (a deliberate, tested relaxation that
# grandfathers a correctly-dated pre-rule goal whose date sat behind a prefix).
_CREATED_LINE = re.compile(
    r"^[\s>*-]*Created\s*:\s*(\d{4}-\d{2}-\d{2})\b",
    re.MULTILINE | re.IGNORECASE,
)


def parse_created_date(text: str) -> date | None:
    """Parse the goal's ``Created:`` date; ``None`` when absent or malformed.

    Scoped to the fence-masked body so a fenced example line is not read as the
    real ``Created:``. Callers fail closed (treat ``None`` as in-scope).
    """
    match = _CREATED_LINE.search(mask_fences(text))
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group(1))
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
