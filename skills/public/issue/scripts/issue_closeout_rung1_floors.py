#!/usr/bin/env python3
"""The rung-1 presence floors a closeout carrier body must clear, and their gates.

Split from ``issue_verify_closeout_body`` on a concept boundary the repo had already
named in its tests: that module answers "how do I read a field out of markdown", and
this one answers "what must the body carry, and for which classification". Four
floors -- source preservation, behavioral verdict, HOTL disposition, AI provenance --
plus the advisory that makes a light close legible.

EVERY floor here is PRESENCE/FORM ONLY (rung-1). Each refuses silence or malformation
and none judges whether the content is honest; that is the fresh-eye resolution
critique (rung-2). A floor that starts judging substance belongs somewhere else.

ONE WARNING WORTH THE SPLIT. Three of these four once shared a single classification
gate, ``BEHAVIORAL_VERDICT_CLASSIFICATIONS``, whose reason ("this classification has
no user-facing behavior to confirm") is sound for exactly one of them. Reusing it for
authorship and for loop disposition imported a reason that does not transfer, and a
behavioral matrix over every closeout carrier measured the result: two floors that
could be silently skipped on the carrier that writes to GitHub itself. Each gate below
now states its OWN reason.
"""
from __future__ import annotations

import re
import runpy
from pathlib import Path

_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_BODY = _load_local("issue_verify_closeout_body")
_strip_code_fences = _BODY._strip_code_fences
_body_fields = _BODY._body_fields
_first_field = _BODY._first_field
_has_substantive_value = _BODY._has_substantive_value


# Classifications whose carrier has user-facing behavior to confirm. This gates the
# behavioral-verdict floor ONLY. It once also gated AI-provenance and HOTL, which was
# a reason that did not transfer: neither authorship nor loop disposition is a fact
# about behavior change. Do not reuse this tuple for a third floor without asking
# whether "no behavior to confirm" is really that floor's reason.
BEHAVIORAL_VERDICT_CLASSIFICATIONS = ("bug", "feature", "deferred-work")

# Classifications with no live user-facing behavior to confirm — the exact
# complement of BEHAVIORAL_VERDICT_CLASSIFICATIONS within the closeout
# classification set. Single canonical home for BOTH close carriers (the
# ``close-with-comment`` floor and the commit-msg carrier) so the floor-exemption
# advisory and its exempt set cannot drift between them (D36).
FLOOR_EXEMPT_CLASSIFICATIONS = ("question", "decision-needed")
_CONSOLIDATED_CLASSIFICATION = "consolidated"

def review_advisory_for_classification(
    classification: str,
    *,
    numbers: list[int] | None = None,
    source: str | None = None,
) -> list[str]:
    """REVIEW-severity advisory for a close whose classification exempts it from
    the behavioral-verdict and resolution-critique floors.

    Those two, and no longer four: the AI-provenance and HOTL floors used to share the
    behavioral-verdict tuple and now apply to every classification, so a light close is
    lighter by two fewer floors than this advisory once had to report.

    Carrier-neutral single owner (D36). ``close-with-comment`` calls it with just
    a ``classification`` (single close, no scope suffix — the historical form, so
    that carrier's output is byte-identical to before). The commit-msg carrier
    passes the issue ``numbers`` and the staged-artifact ``source`` (or ``None``
    for a bare commit-message close keyword) so the same advisory names which
    close it applies to.

    Mirrors ``scripts/skill_cut_safety_advisory.py``'s pattern: forces a question
    for whoever reads the close output, never fails the command. The
    classification is caller-supplied with no independent check on it, so a
    ``question`` / ``decision-needed`` close still bypasses the behavioral-verdict and
    resolution-critique floors; this line makes that bypass visible instead of silent
    on BOTH carriers (advisory only, never blocks).
    """
    # `consolidated` is NOT floor-exempt, and it still needs this advisory. Bounded
    # review found the two facts had been conflated: staying out of the exempt tuple
    # bought the LABEL "not exempt" while silently forfeiting the line that made a
    # light close legible.
    if classification not in FLOOR_EXEMPT_CLASSIFICATIONS + (_CONSOLIDATED_CLASSIFICATION,):
        return []
    scope = ""
    if numbers:
        refs = ", ".join(f"#{number}" for number in numbers)
        where = source or "commit-message close keyword"
        scope = f" ({refs} via {where})"
    return [
        # The exempt wording is PINNED by tests, and it moved once -- deliberately.
        # It used to end "(only source preservation still applies)", which stopped being
        # true when the AI-provenance and HOTL floors lost their classification gate.
        # Byte-stability protects a carrier's output from drifting by accident; it does
        # not license an advisory that misreports which floors ran.
        # `consolidated` gets its own sentence rather than a reworded shared one.
        f"REVIEW: classification '{classification}'{scope} "
        + (
            "skips the behavioral-verdict and resolution-critique floors, and refuses "
            "a HOTL entry outright as a repair claim (source preservation and "
            "AI-provenance still apply, and it owes its own `Consolidated into:` "
            "destination floor instead)"
            if classification == _CONSOLIDATED_CLASSIFICATION
            else "exempts this close from the behavioral-verdict and resolution-critique "
            "floors (source preservation, AI-provenance and HOTL disposition still apply)"
        )
        + "; confirm the classification is correct before treating this issue as "
        "resolved (advisory only, never blocks)."
    ]


# Per-issue behavioral-verdict line grammar, mirroring the ``Critique #N:`` /
# ``Critique:`` shorthand: ``Behavior #N: <distinct-channel or disposition>`` per
# issue, with a single-issue ``Behavior: <…>`` shorthand.
_BEHAVIOR_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?Behaviou?r(?:\s+(?P<target>[^:]+?))?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)
_ISSUE_REF_RE = re.compile(r"#(\d+)\b")

# AI-provenance marker: an agent-posted GitHub write must be legible as
# agent-authored to the distinct (rung-2) observer. Presence is rung-1; whether
# the human-audit claim is real is rung-2.
_PROVENANCE_ALIASES = ("ai provenance", "provenance")


_SOURCE_ORIGIN_ALIASES = ("source origin",)
_SOURCE_TEXT_ALIASES = ("source text", "source context")
_REREAD_ALIASES = ("re read obligation", "re read requirement", "reread obligation")
_DEGRADED_ALIASES = ("source degraded reason", "degraded reason")
_PRESERVATION_ALIASES = ("source preservation", "preservation")


def evaluate_source_preservation(text: str) -> dict:
    """Provider-neutral source-preservation check for an issue/closeout body.

    `axis: external-source-provider` — Slack is one adapter instance, not the
    schema. The body is *externally sourced* iff it carries a substantive
    ``Source origin:`` marker (internal-only issues omit it and stay exempt).

    When externally sourced, the contract requires at least one auditable
    preservation form: (1) ``Source text:`` (verbatim-enough excerpt), (2) ``Re-read
    obligation:`` (stable identity + explicit re-read-before-resolve duty), or
    (3) ``Source degraded reason:`` (the source was inaccessible — say so).

    Presence-only by design, mirroring the ledger checks: a present-but-thin
    value passes; only a missing form on an external-sourced body fails. The
    reviewer judges substance.
    """
    fields = _body_fields(text)
    origin = _first_field(fields, _SOURCE_ORIGIN_ALIASES)
    external_sourced = _has_substantive_value(origin)
    preservation_declared = _first_field(fields, _PRESERVATION_ALIASES)
    forms_present: list[str] = []
    if _has_substantive_value(_first_field(fields, _SOURCE_TEXT_ALIASES)):
        forms_present.append("source-text")
    if _has_substantive_value(_first_field(fields, _REREAD_ALIASES)):
        forms_present.append("re-read-required")
    if _has_substantive_value(_first_field(fields, _DEGRADED_ALIASES)):
        forms_present.append("degraded")
    missing = external_sourced and not forms_present
    return {
        "external_sourced": external_sourced,
        "origin": origin if external_sourced else None,
        "preservation_declared": preservation_declared,
        "forms_present": forms_present,
        "missing": missing,
        "ok": not missing,
    }


def _behavior_lines(text: str) -> list[dict]:
    plain = "\n".join(_strip_code_fences(text))
    lines: list[dict] = []
    for match in _BEHAVIOR_LINE_RE.finditer(plain):
        target = (match.group("target") or "").strip()
        value = match.group("value").strip()
        lines.append(
            {
                "target": target or None,
                "value": value,
                "target_numbers": [int(raw) for raw in _ISSUE_REF_RE.findall(target)],
            }
        )
    return lines


def evaluate_behavioral_verdict(text: str, classification: str, numbers: list[int]) -> dict:
    """Rung-1 block-the-silent presence floor for the per-issue behavioral verdict.

    A ``bug`` / ``feature`` / ``deferred-work`` carrier must carry, per closed
    issue, a substantive ``Behavior #N: <…>`` line (single-issue shorthand
    ``Behavior: <…>``) whose value either names the distinct evidence channel the
    user-facing behavior was confirmed through, or records a typed non-``verified``
    disposition (a HOTL status, or ``local-only-by-contract``).

    **Presence/form only — this is rung-1.** It refuses *silence* (no line for an
    issue), never declaring completion: ``status: verified`` stays necessary-not-
    sufficient. A typed non-``verified`` disposition satisfies it exactly as a
    confirmation does, so it renders the per-issue question without ever gating the
    close on an aggregate "all confirmed". Whether the named channel is genuinely
    distinct from ``CLOSED``/the carrier — or the disposition is real — is the
    fresh-eye reviewer's judgment (rung-2), never this floor's.
    """
    if classification not in BEHAVIORAL_VERDICT_CLASSIFICATIONS:
        return {"applies": False, "ok": True, "missing": [], "skipped_classification": classification}
    bound: set[int] = set()
    lines = _behavior_lines(text)
    for line in lines:
        if not _has_substantive_value(line["value"]):
            continue
        targets = [number for number in line["target_numbers"] if number in numbers]
        if not targets and line["target"] is None and len(numbers) == 1:
            targets = [numbers[0]]
        bound.update(targets)
    missing = [number for number in numbers if number not in bound]
    return {
        "applies": True,
        "ok": not missing,
        "missing": missing,
        "lines": [{"target": line["target"], "value": line["value"]} for line in lines],
    }


# WS-2 (Direction-3): the typed HOTL disposition vocabulary
# (``hotl/references/ledger-and-dispositions.md`` §Statuses) plus the
# ``local-only-by-contract`` escape the behavioral-verdict floor already names.
# ANCHORED to the value's leading token, mirroring the repo's existing disposition
# grammar (``scripts/core/disposition_form.py`` ``_APPLIED`` / ``_ISSUE_LEAD``). An
# unanchored search over the same vocabulary accepts a status's own NEGATION
# ("not verified", "could not be verified; no readback available") and incidental
# English prose ("a known issue with the provider") — so the floor rubber-stamped
# exactly the undispositioned entries it exists to refuse. Mirrored rather than
# imported: this public skill script stays portable and never imports repo-internal
# ``scripts/``. The mirror covers ``_APPLIED``/``_ISSUE_LEAD``'s leading-token shape
# only, NOT ``_NONE``/``_ACCEPTED_RISK``/``_OUT_OF_SCOPE``'s additional
# separator-plus-reason requirement: whether a status carries a real reason is the
# resolution critique's judgment (rung-2), never this presence floor's.
# Longest alternants first so a prefix cannot shadow a longer token.
_HOTL_STATUS_LEAD = re.compile(
    r"(?i)^(?:blocked-needs-(?:operator|capability)|deferred-by-operator|accepted-risk"
    r"|out-of-scope|local-only-by-contract|verified)\b"
)
# ``issue`` is the one status whose bare token is also an ordinary English word, so
# it must carry the tracker ref its own contract requires ("the entry links the
# tracker ref"). Same shape as ``disposition_form``'s ``_ISSUE_LEAD`` + ``_ISSUE_NUM``.
_HOTL_ISSUE_LEAD = re.compile(r"(?i)^(?:issues?\b|#\d)")
_HOTL_ISSUE_REF = re.compile(r"#\d+")
# Leading bullet/emphasis/quote/code markers stripped before judging. Backticks are
# in the class because the contract renders the vocabulary AS code (``verified``,
# ``blocked-needs-operator``), so an author copying the reference's own rendering
# writes a backticked status; ``_normalize_field_name`` already strips them for the
# sibling floors. ``#`` stays OUT: a leading ``#`` here is a tracker ref (``#77``),
# not a heading marker.
_HOTL_VALUE_LEAD = re.compile(r"^[ \t\-\*>`]+")


def _hotl_status_typed(value: str) -> bool:
    """True when the value *leads* with a typed HOTL status, not merely mentions one."""
    cleaned = _HOTL_VALUE_LEAD.sub("", value.strip()).strip().strip("*`").strip()
    if _HOTL_STATUS_LEAD.match(cleaned):
        return True
    return bool(_HOTL_ISSUE_LEAD.match(cleaned) and _HOTL_ISSUE_REF.search(cleaned))
# A HOTL ledger entry in the carrier body: ``HOTL #N: <disposition>`` per issue,
# single-issue shorthand ``HOTL: <disposition>`` — mirrors the ``Behavior #N:`` grammar.
_HOTL_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?HOTL(?:\s+(?P<target>[^:]+?))?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)


def _hotl_lines(text: str) -> list[dict]:
    plain = "\n".join(_strip_code_fences(text))
    return [
        {"target": (m.group("target") or "").strip() or None, "value": m.group("value").strip()}
        for m in _HOTL_LINE_RE.finditer(plain)
    ]


def evaluate_hotl_dispositions(text: str, classification: str, numbers: list[int]) -> dict:
    """Rung-1 refuse-on-undispositioned-HOTL-entry presence floor (WS-2 / Direction-3).

    **Presence-gated.** A carrier that presents NO ``HOTL`` entry is inert (no live
    HOTL loop to dispose), exactly like ``evaluate_source_preservation``'s
    ``Source origin:`` gate — internal / no-live closes stay exempt. When a
    ``HOTL #N:`` entry (single-issue shorthand ``HOTL:``) IS presented, its value
    must **lead with** one of the typed HOTL statuses
    (``hotl/references/ledger-and-dispositions.md``) **or** ``local-only-by-contract``;
    an entry that merely *mentions* one — including its negation ("not verified") —
    is *undispositioned* and refused.

    **Presence/form only — rung-1.** It refuses *silence/malformation* on the typed
    status (an empty/placeholder/untyped value); it NEVER judges whether the chosen
    disposition is *honest* — that is the resolution critique (rung-2). The
    behavioral-verdict floor accepts a HOTL status only as an opaque value; this is
    the FIRST typed HOTL-status recognizer. Reads the carrier body — never a fixed
    ledger path (the HOTL ledger schema/path is adapter-owned), so it stays
    adapter-portable. An untyped entry fails closed.

    **No classification gate.** Whether a human loop was DISPOSITIONED is not a fact
    about whether the close changes user-facing behavior, so the behavioral-verdict
    tuple that used to gate this imported a reason that does not transfer. The
    PRESENCE gate below is the real one and always was: a body with no ``HOTL`` entry
    stays inert, so a close that never had a live loop gains no obligation.
    ``classification`` is reported, never gating. `HOTL #N:` is bound to an
    issue the carrier closes, just like `Behavior #N:`; quoted or copied entries
    for other issues are not this carrier's disposition. `HOTL:` stays the
    single-issue shorthand and is judged only when exactly one number is closed.
    """
    lines = _hotl_lines(text)
    bound_lines: list[dict] = []
    for line in lines:
        targets = [int(raw) for raw in _ISSUE_REF_RE.findall(line["target"] or "")]
        if targets:
            if not any(number in numbers for number in targets):
                continue
        elif len(numbers) != 1:
            continue
        bound_lines.append(line)
    if not bound_lines:
        return {"applies": False, "ok": True, "undispositioned": [], "lines": []}
    undispositioned: list[dict] = []
    parsed: list[dict] = []
    for line in bound_lines:
        dispositioned = _has_substantive_value(line["value"]) and _hotl_status_typed(line["value"])
        parsed.append({"target": line["target"], "value": line["value"], "dispositioned": dispositioned})
        if not dispositioned:
            undispositioned.append({"target": line["target"], "value": line["value"]})
    return {
        "applies": True, "ok": not undispositioned, "undispositioned": undispositioned,
        "lines": parsed, "classification": classification, "numbers": numbers,
    }


def evaluate_ai_provenance(text: str, classification: str) -> dict:
    """Rung-1 presence floor for the AI-provenance marker on an agent-posted
    closeout carrier, for EVERY classification.

    Presence/form only: an ``AI-provenance:`` marker must be present so the
    irreversible external write is legible as agent-authored to the distinct
    (rung-2) observer. Whether the human-audit claim it makes is real is rung-2.

    **No classification gate.** Provenance is a fact about WHO AUTHORED the text: an
    agent-posted ``question`` close comment is exactly as agent-authored as a ``bug``
    one. The behavioral-verdict tuple that used to gate this carried a sound reason
    for ITS floor ("no user-facing behavior to confirm") that does not transfer here.
    ``classification`` is reported, never gating.
    """
    marker = _first_field(_body_fields(text), _PROVENANCE_ALIASES)
    present = _has_substantive_value(marker)
    return {
        "applies": True, "ok": present, "missing": not present,
        "marker": marker if present else None, "classification": classification,
    }
