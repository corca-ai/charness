"""Body-parsing and ledger-requirement helpers for ``issue verify-closeout``.

Split out of ``issue_verify_closeout.py`` so the main verifier module stays
under the single-file length gate. Pure functions over the carrier body text
and the closing-keyword scanner; no IO and no subprocess.
"""
from __future__ import annotations

import re

_CLOSING_KEYWORD_LAUNCH_RE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)(?:\s*:\s*|\s+)"
    r"(?P<refs>(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+"
    r"(?:\s*,\s*(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+)*)"
)
_CLOSING_KEYWORD_REF_RE = re.compile(r"(?:(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<number>\d+)")


def iter_close_keyword_refs(text: str) -> list[tuple[str | None, int]]:
    """Every ``(repo_or_None, issue_number)`` a GitHub close keyword references
    in ``text``. This is the single canonical close-keyword scanner; the
    commit-msg checker (``scripts/check_issue_closeout_commit_msg.py``) reuses
    it through the loaded ``issue_verify_closeout`` module rather than keeping
    a second copy, so the two surfaces cannot drift.

    Covers the plain form (``Closes #10``), GitHub's documented colon form
    (``Closes: #10``), and the single-keyword comma-list form GitHub also
    recognizes (``Closes #10, #11, #12``) so a bundled reference is not missed
    just because the keyword was not repeated per issue.
    """
    refs: list[tuple[str | None, int]] = []
    for launch in _CLOSING_KEYWORD_LAUNCH_RE.finditer(text):
        for ref in _CLOSING_KEYWORD_REF_RE.finditer(launch.group("refs")):
            refs.append((ref.group("repo"), int(ref.group("number"))))
    return refs
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<name>.+?)\s*$")
_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(?P<name>[A-Za-z][A-Za-z -]{1,40}):\s*(?P<value>.*)$")
_PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na"}

# Classifications whose carrier has user-facing behavior to confirm. The rung-1
# behavioral-verdict + AI-provenance floors apply only here; question /
# decision-needed carriers have no behavior change and stay exempt (mirroring the
# resolution-critique classification gate).
BEHAVIORAL_VERDICT_CLASSIFICATIONS = ("bug", "feature", "deferred-work")

# Classifications with no live user-facing behavior to confirm — the exact
# complement of BEHAVIORAL_VERDICT_CLASSIFICATIONS within the closeout
# classification set. Single canonical home for BOTH close carriers (the
# ``close-with-comment`` floor and the commit-msg carrier) so the floor-exemption
# advisory and its exempt set cannot drift between them (D36).
FLOOR_EXEMPT_CLASSIFICATIONS = ("question", "decision-needed")


def review_advisory_for_classification(
    classification: str,
    *,
    numbers: list[int] | None = None,
    source: str | None = None,
) -> list[str]:
    """REVIEW-severity advisory for a close whose classification exempts it from
    the behavioral-verdict and resolution-critique floors.

    Carrier-neutral single owner (D36). ``close-with-comment`` calls it with just
    a ``classification`` (single close, no scope suffix — the historical form, so
    that carrier's output is byte-identical to before). The commit-msg carrier
    passes the issue ``numbers`` and the staged-artifact ``source`` (or ``None``
    for a bare commit-message close keyword) so the same advisory names which
    close it applies to.

    Mirrors ``scripts/skill_cut_safety_advisory.py``'s pattern: forces a question
    for whoever reads the close output, never fails the command. The
    classification is caller-supplied with no independent check on it, so a
    ``question`` / ``decision-needed`` close silently bypasses two of the three
    floor checks; this line makes that bypass visible instead of silent on BOTH
    carriers (advisory only, never blocks).
    """
    if classification not in FLOOR_EXEMPT_CLASSIFICATIONS:
        return []
    scope = ""
    if numbers:
        refs = ", ".join(f"#{number}" for number in numbers)
        where = source or "commit-message close keyword"
        scope = f" ({refs} via {where})"
    return [
        f"REVIEW: classification '{classification}'{scope} exempts this close from the "
        "behavioral-verdict and resolution-critique floors (only source preservation still "
        "applies); confirm the classification is correct before treating this issue as "
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
AI_PROVENANCE_MARKER = (
    "AI-provenance: agent-drafted via charness issue resolve; "
    "human-audited per the resolution critique"
)


def has_ai_provenance_marker(text: str) -> bool:
    """True when the body carries a substantive ``AI-provenance:`` marker.

    Presence/form only. Enforced by the closeout floor (``verify-closeout`` /
    ``validate-closeout-draft``) on the agent-authored carrier — for a
    manual-fallback close that carrier *is* the comment body, and the documented
    flow runs ``validate-closeout-draft`` before ``close_with_comment``, so an
    agent-posted comment cannot be published unmarked without bypassing the
    draft-validation step.
    """
    return _has_substantive_value(_first_field(_body_fields(text), _PROVENANCE_ALIASES))


def _strip_code_fences(text: str) -> list[str]:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return lines


def _normalize_field_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"`", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _body_fields(text: str) -> dict[str, str]:
    lines = _strip_code_fences(text)
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        heading = _HEADING_RE.match(line)
        if heading:
            current = _normalize_field_name(heading.group("name"))
            fields.setdefault(current, [])
            continue
        inline = _FIELD_RE.match(line)
        if inline:
            current = _normalize_field_name(inline.group("name"))
            fields.setdefault(current, [])
            value = inline.group("value").strip()
            if value:
                fields[current].append(value)
            continue
        if current is not None and line.strip():
            fields[current].append(line.strip())
    return {key: "\n".join(value).strip() for key, value in fields.items()}


def _first_field(fields: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    normalized_aliases = {_normalize_field_name(alias) for alias in aliases}
    for name, value in fields.items():
        if name in normalized_aliases:
            return value
    return None


def _has_substantive_value(value: str | None) -> bool:
    if value is None:
        return False
    normalized = _normalize_field_name(value)
    return normalized not in _PLACEHOLDER_VALUES and not normalized.startswith("missing ")


def _classification_requirements(classification: str) -> list[tuple[str, tuple[str, ...]]]:
    if classification == "bug":
        return [
            ("jtbd", ("jtbd",)),
            ("root_cause", ("root cause",)),
            ("debug_artifact", ("debug artifact",)),
            ("siblings", ("siblings", "sibling search")),
            ("prevention", ("prevention",)),
        ]
    if classification in {"feature", "deferred-work"}:
        return [
            ("jtbd", ("jtbd",)),
            ("boundary", ("boundary",)),
            ("resolution_brief", ("resolution brief",)),
            ("implementation", ("implementation",)),
            ("prevention", ("prevention",)),
        ]
    return [
        ("jtbd", ("jtbd",)),
        ("answer_or_decision", ("answer", "decision", "recorded decision")),
    ]


def _missing_ledger_fields(text: str, classification: str) -> list[str]:
    fields = _body_fields(text)
    missing: list[str] = []
    for field_id, aliases in _classification_requirements(classification):
        if not _has_substantive_value(_first_field(fields, aliases)):
            missing.append(field_id)
    if classification == "bug":
        siblings = _first_field(fields, ("siblings", "sibling search"))
        if siblings and not (
            re.search(r"(?i)\bdecision\b", siblings) and re.search(r"(?i)\bproof\b", siblings)
        ):
            missing.append("siblings_decision_and_proof")
    return missing


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


def _missing_close_keywords(text: str, numbers: list[int], repo: str) -> list[int]:
    found: set[int] = set()
    selected_repo = repo.lower()
    plain = "\n".join(_strip_code_fences(text))
    for qualified_repo, number in iter_close_keyword_refs(plain):
        if qualified_repo is not None and qualified_repo.lower() != selected_repo:
            continue
        found.add(number)
    return [number for number in numbers if number not in found]


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
# Longest alternants first so a prefix cannot shadow a longer typed token.
_HOTL_STATUS_RE = re.compile(
    r"(?i)\b(?:blocked-needs-(?:operator|capability)|deferred-by-operator|accepted-risk"
    r"|out-of-scope|local-only-by-contract|verified|issue)\b"
)
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


def evaluate_hotl_dispositions(text: str, classification: str) -> dict:
    """Rung-1 refuse-on-undispositioned-HOTL-entry presence floor (WS-2 / Direction-3).

    **Presence-gated.** A carrier that presents NO ``HOTL`` entry is inert (no live
    HOTL loop to dispose), exactly like ``evaluate_source_preservation``'s
    ``Source origin:`` gate — internal / no-live closes stay exempt. When a
    ``HOTL #N:`` entry (single-issue shorthand ``HOTL:``) IS presented, its value
    must carry one of the typed HOTL statuses
    (``hotl/references/ledger-and-dispositions.md``) **or** ``local-only-by-contract``;
    an entry present **without** one is *undispositioned* and refused.

    **Presence/form only — rung-1.** It refuses *silence/malformation* on the typed
    status (an empty/placeholder/untyped value); it NEVER judges whether the chosen
    disposition is *honest* — that is the resolution critique (rung-2). The
    behavioral-verdict floor accepts a HOTL status only as an opaque value; this is
    the FIRST typed HOTL-status recognizer. ``bug``/``feature``/``deferred-work`` only;
    ``question``/``decision-needed`` carry no live behavior. Reads the carrier body —
    never a fixed ledger path (the HOTL ledger schema/path is adapter-owned), so it
    stays adapter-portable. An untyped entry fails closed.
    """
    if classification not in BEHAVIORAL_VERDICT_CLASSIFICATIONS:
        return {"applies": False, "ok": True, "undispositioned": [], "skipped_classification": classification}
    lines = _hotl_lines(text)
    if not lines:
        return {"applies": False, "ok": True, "undispositioned": [], "lines": []}
    undispositioned: list[dict] = []
    parsed: list[dict] = []
    for line in lines:
        dispositioned = _has_substantive_value(line["value"]) and bool(_HOTL_STATUS_RE.search(line["value"]))
        parsed.append({"target": line["target"], "value": line["value"], "dispositioned": dispositioned})
        if not dispositioned:
            undispositioned.append({"target": line["target"], "value": line["value"]})
    return {"applies": True, "ok": not undispositioned, "undispositioned": undispositioned, "lines": parsed}


def evaluate_ai_provenance(text: str, classification: str) -> dict:
    """Rung-1 presence floor for the AI-provenance marker on an agent-posted
    closeout carrier (``bug`` / ``feature`` / ``deferred-work``).

    Presence/form only: an ``AI-provenance:`` marker must be present so the
    irreversible external write is legible as agent-authored to the distinct
    (rung-2) observer. Whether the human-audit claim it makes is real is rung-2.
    """
    if classification not in BEHAVIORAL_VERDICT_CLASSIFICATIONS:
        return {"applies": False, "ok": True, "marker": None, "skipped_classification": classification}
    marker = _first_field(_body_fields(text), _PROVENANCE_ALIASES)
    present = _has_substantive_value(marker)
    return {"applies": True, "ok": present, "missing": not present, "marker": marker if present else None}
