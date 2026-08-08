"""One owner for WHEN broad proof runs.

``## Active Operating Frame``'s ``Gate cadence:`` line owns the answer, and the
achieve scaffold seeds it. When a hand-written ``## User Acceptance`` restates
that answer with a per-slice broad-proof demand, the artifact carries two owners
for one rule -- and the measured behaviour is that an agent reading its own
acceptance criteria obeys the acceptance criteria. One session ran a 12-minute
suite about thirteen times that way, roughly two and a half hours of pure
waiting, because the cadence line said to defer broad pytest until the
verification lock while the acceptance line demanded it every slice.

This floor refuses that pair. It does NOT rewrite the cadence, and it does not
fire on an acceptance section that states outcomes without naming a boundary
frequency -- which is the shape the template now seeds.

Deliberately narrow, because this goal's Non-Goals forbid a gate an operator
would learn to ignore:

- it needs BOTH owners present. An acceptance line with no deferring cadence
  line is one owner stating a rule, not a contradiction, so it passes.
- it recognises deferral by the owner's own vocabulary
  (``--skip-broad-pytest`` / ``--verification-lock``). A cadence that defers in
  words nobody has written yet under-fires rather than guessing.
- it skips ``complete`` artifacts. A terminal record is one nobody is permitted
  to repair, and a validator that reddens on those is the wolf-crier by
  construction.

One deliberate OVER-fire, named rather than hidden. Matching is per logical line,
so a sentence like "``pytest tests/ -q`` reports zero failures AND
``run-quality.sh --read-only`` exits 0 at each slice boundary" is refused even
though the frequency arguably binds only to the second conjunct. That ambiguity
is not innocent: it is the exact sentence a session measurably read as covering
both, and the repair is one splitting of a sentence.

Section slicing and soft-wrap reflow are delegated to ``goal_artifact_markdown``,
and the terminal-status test to ``goal_artifact_pursue.is_terminal_status``,
rather than re-derived here. That is not only hygiene, and in a slice about one
rule having one owner it would be embarrassing to hand-roll a third status
predicate -- which the first cut did, with ``status == "complete"``, and which
the repo's own annotated ``Status: COMPLETE (date) — ...`` house style silently
disarms.

The reflow is load-bearing on BOTH owners: real artifacts wrap mid-command
(``./scripts/run-quality.sh`` on one physical line, ``--read-only`` on the next)
in the acceptance section AND wrap before ``--skip-broad-pytest`` in the cadence
line. A per-physical-line scan misses the contradiction from either side.
"""
from __future__ import annotations

import re
from typing import Any

#: The frame line that OWNS when broad proof runs.
_CADENCE_LABEL = re.compile(r"^[ \t>*\-]*\**[ \t]*Gate cadence[ \t]*:[ \t]*\**(.*)$", re.MULTILINE)

#: Deferral stated in the owner's own vocabulary. See the module docstring on
#: why this is a closed list rather than a paraphrase matcher.
_DEFERS_BROAD_PROOF = re.compile(r"--skip-broad-pytest|--verification-lock")

#: A BROAD-pytest command an acceptance line can demand: a pytest run over the
#: whole tree, or the standing-pytest runner named directly. Optional flags may
#: sit between the verb and the path (``pytest -q tests/``) -- that spelling is
#: as common as the adjacent one, and this floor's whole thesis is that the
#: sentence recurs by idiom.
#:
#: ``run-quality.sh --read-only`` is deliberately ABSENT, and the reason is
#: MEASURED COST, not command scope. (Scope would be the wrong argument: that
#: script queues ``run_standing_pytest.py`` unconditionally -- see
#: ``scripts/run-quality.sh`` -- so the two are not disjoint, and a maintainer
#: who believed they were would "fix" this exclusion.) It is exempt because the
#: predecessor measured it at ~110s AND measured it naming four real defects
#: nothing else caught, so demanding it per slice is a good trade that a
#: deferring cadence does not contradict. Refusing it would be the wolf-crier the
#: goal's Non-Goals forbid.
#:
#: The lookahead keeps a SCOPED run (`pytest tests/quality_gates`) out: it is
#: cheap and a legitimate per-slice check.
_BROAD_PROOF_COMMAND = re.compile(
    r"pytest(?:\s+-{1,2}[A-Za-z0-9][^\s]*)*\s+tests/(?![A-Za-z_])|run_standing_pytest\.py"
)

#: A per-slice boundary frequency. ``at the end`` / ``at closeout`` are absent on
#: purpose: those AGREE with a deferring cadence and must not be refused.
_PER_SLICE_FREQUENCY = re.compile(r"\b(?:every|each)\s+slice\b|\bper[- ]slice\b", re.IGNORECASE)


def _inert(reason: str) -> dict[str, Any]:
    """The floor did not evaluate, and says why. Never a silent clean pass.

    `applies: False` alongside a reason is the disclosure: `ok: True` here means
    "not evaluated", not "checked and fine".
    """
    return {"applies": False, "ok": True, "reason": reason, "cadence": None, "findings": []}


def _logical_section(masked: str, section: str, markdown) -> list[tuple[int, str]]:
    """``(artifact line number, joined text)`` for one section's logical lines.

    Both owners are read this way, on purpose. Round-1 review found the first cut
    reading the frame per PHYSICAL line while reading acceptance per logical line
    -- so a `Gate cadence:` value that soft-wrapped before `--skip-broad-pytest`
    (two live corpus instances) disarmed the whole floor, which then reported the
    reassuring "no cadence line that defers broad proof". That sentence was false
    about the artifact. Symmetry is the fix: the wrap argument in this module's
    docstring applies to whichever owner wraps.

    Read from ``masked``, so a FENCED example cannot act as either owner. Outside
    fences it is character-identical to the raw text (masking is length- and
    offset-preserving), so nothing else changes.
    """
    bounds = markdown.section_bounds(masked, section)
    if bounds is None:
        return []
    start, end = bounds
    first_line = masked.count("\n", 0, start) + 1
    return [
        (first_line + offset - 1, value)
        for offset, value in markdown.logical_lines(masked[start:end])
    ]


def _cadence_owner(masked: str, markdown) -> dict[str, Any] | None:
    for line, value in _logical_section(masked, "Active Operating Frame", markdown):
        match = _CADENCE_LABEL.search(value)
        if match is not None:
            return {"line": line, "text": match.group(1).strip()}
    return None


def _acceptance_findings(masked: str, markdown) -> list[dict[str, Any]]:
    return [
        {"line": line, "text": value.strip()}
        for line, value in _logical_section(masked, "User Acceptance", markdown)
        if _BROAD_PROOF_COMMAND.search(value) and _PER_SLICE_FREQUENCY.search(value)
    ]


def check(
    text: str, *, status: str | None, masked: str, markdown, is_terminal, balanced: bool
) -> dict[str, Any]:
    """Refuse an artifact whose acceptance restates a cadence its own frame defers.

    ``markdown`` is the ``goal_artifact_markdown`` module and ``is_terminal`` the
    shared status predicate, both injected so this stays a leaf with no
    sibling-loading of its own. ``text`` is kept in the signature for callers and
    for symmetry; every read goes through ``masked`` (see ``_logical_section``).
    """
    if is_terminal(status):
        return _inert("skipped: terminal record — a `complete` artifact is one nobody may repair")
    if not balanced:
        # `mask_fences` FAILS OPEN on odd fence parity: `masked` is then the raw
        # text, fenced examples included. Every read below would be over a reading
        # nobody established, and this floor's own refusal names LINE NUMBERS --
        # which would point inside a code fence. Say that instead. Round-2 review
        # found this floor was the one new reader consuming a possibly-fail-open
        # mask while claiming fenced examples could not act as an owner.
        return _inert(
            "unestablished: an unclosed code fence makes fence masking fail open, so a "
            "fenced example is indistinguishable from a real `Gate cadence:` or acceptance "
            "line; close the fence and this floor can render a verdict"
        )
    cadence = _cadence_owner(masked, markdown)
    if cadence is None or not _DEFERS_BROAD_PROOF.search(cadence["text"]):
        return {
            "applies": False,
            "ok": True,
            "reason": (
                "not applicable: `## Active Operating Frame` states no `Gate cadence:` line "
                "that defers broad proof, so `## User Acceptance` is not a second owner"
            ),
            "cadence": cadence,
            "findings": [],
        }
    findings = _acceptance_findings(masked, markdown)
    if not findings:
        return {
            "applies": True,
            "ok": True,
            "reason": "one owner: `## User Acceptance` does not restate the gate cadence",
            "cadence": cadence,
            "findings": [],
        }
    return {
        "applies": True,
        "ok": False,
        "reason": (
            "two owners for one rule: `## Active Operating Frame` line "
            f"{cadence['line']} (`Gate cadence:`) DEFERS broad proof, while "
            "`## User Acceptance` line "
            + ", ".join(str(entry["line"]) for entry in findings)
            + " DEMANDS it per slice. An agent reading its own acceptance criteria "
            "obeys the acceptance criteria, so this pair buys re-proof of what is "
            "already green. State the outcome in `## User Acceptance` and leave WHEN "
            "broad proof runs to the `Gate cadence:` line."
        ),
        "cadence": cadence,
        "findings": findings,
    }
