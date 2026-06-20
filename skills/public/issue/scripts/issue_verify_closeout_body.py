"""Body-parsing and ledger-requirement helpers for ``issue verify-closeout``.

Split out of ``issue_verify_closeout.py`` so the main verifier module stays
under the single-file length gate. Pure functions over the carrier body text
and the closing-keyword scanner; no IO and no subprocess.
"""
from __future__ import annotations

import re

_CLOSING_KEYWORD_RE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<number>\d+)\b"
)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<name>.+?)\s*$")
_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(?P<name>[A-Za-z][A-Za-z -]{1,40}):\s*(?P<value>.*)$")
_PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na"}

# Classifications whose carrier has user-facing behavior to confirm. The rung-1
# behavioral-verdict + AI-provenance floors apply only here; question /
# decision-needed carriers have no behavior change and stay exempt (mirroring the
# resolution-critique classification gate).
BEHAVIORAL_VERDICT_CLASSIFICATIONS = ("bug", "feature", "deferred-work")

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
    for match in _CLOSING_KEYWORD_RE.finditer("\n".join(_strip_code_fences(text))):
        qualified_repo = match.group("repo")
        if qualified_repo is not None and qualified_repo.lower() != selected_repo:
            continue
        found.add(int(match.group("number")))
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
