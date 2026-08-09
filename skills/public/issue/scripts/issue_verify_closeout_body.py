"""Body-parsing and ledger-requirement helpers for ``issue verify-closeout``.

Split out of ``issue_verify_closeout.py`` so the main verifier module stays
under the single-file length gate. Pure functions over the carrier body text
and the closing-keyword scanner; no IO and no subprocess.
"""
from __future__ import annotations

import re
import runpy
from pathlib import Path

_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_strip_code_fences = _load_local("issue_markdown_lib").strip_code_fences
_ledger_counts = _load_local("issue_closeout_ledger_counts")
_consolidated = _load_local("issue_consolidated_closeout")

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
# A *targeted* ledger section line — the ``<Name> #N: <value>`` grammar this module
# defines for ``Behavior #N:`` / ``HOTL #N:`` (and the ``Critique #N:`` shorthand they
# mirror). ``_FIELD_RE``'s name class excludes ``#`` and digits, so such a line matched
# nothing and fell through to the continuation branch, where it was appended to the
# PRECEDING field's value — an empty or placeholder field (``Prevention: N/A``) silently
# absorbed the next section's heading and normalized to a substantive value (B5).
# Continuation of genuinely wrapped prose stays intended and untouched; only a line that
# STARTS a new ledger section is excluded from it.
#
# The name is the CLOSED vocabulary above, not an open ``[A-Za-z -]{1,40}`` class. An
# open class turns this fix into a FALSE REFUSAL at an irreversible boundary: a wrapped
# value beginning ``regression tests pin the behavior:`` parses as a new field, leaving
# the preceding ledger field empty and refusing a correct closeout. The narrower form of
# that escape is already on the authoring repo's record -- a wrapped ``Siblings:`` value
# beginning ``proof:`` lost its token, and the operator worked around it by rewriting the
# evidence prose, which is the wrong direction at a close. Nothing in the authoring
# template tells an author to keep an issue ref out of a wrapped value, and a bullet like
# ``- In scope for the CLI: ...`` is ordinary prose, so an open name class is a trap the
# format does not announce.
_TARGETED_SECTION_NAMES = ("behaviour", "behavior", "hotl", "critique", "classification", "issue")
_TARGETED_SECTION_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?P<name>" + "|".join(_TARGETED_SECTION_NAMES) + r")"
    r"\s+(?P<target>#\d+[^:]*?)\s*:\s*(?P<value>.*)$",
    re.IGNORECASE,
)
# Declared in the form an author writes. The comparison happens on
# ``_normalize_field_name`` output, which maps every non-``[a-z0-9]`` run to a
# space — so a literal ``"n/a"`` entry can never be produced by it and sat here
# as unreachable dead code while ``N/A`` passed every ledger floor as a
# substantive value (B1). ``_NORMALIZED_PLACEHOLDER_VALUES`` below is what
# ``_has_substantive_value`` actually tests against; keep additions here and let
# the normalizer project them into the comparison space.
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
_CONSOLIDATED_CLASSIFICATION = "consolidated"


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
    # `consolidated` is NOT floor-exempt, and it still needs this advisory. Bounded
    # review found the two facts had been conflated: staying out of the exempt tuple
    # bought the LABEL "not exempt" while silently forfeiting the line that made a
    # light close legible. A `consolidated` close skips the behavioral-verdict, HOTL,
    # AI-provenance and resolution-critique floors -- one more than `question` does --
    # so printing nothing made it strictly stealthier than the classifications it was
    # designed to avoid becoming.
    if classification not in FLOOR_EXEMPT_CLASSIFICATIONS + (_CONSOLIDATED_CLASSIFICATION,):
        return []
    scope = ""
    if numbers:
        refs = ", ".join(f"#{number}" for number in numbers)
        where = source or "commit-message close keyword"
        scope = f" ({refs} via {where})"
    return [
        # The exempt wording is BYTE-STABLE on purpose: two tests pin it, because
        # that carrier's output was contractually identical before this owner existed.
        # `consolidated` gets its own sentence rather than a reworded shared one.
        f"REVIEW: classification '{classification}'{scope} "
        + (
            "skips the behavioral-verdict, HOTL-disposition, AI-provenance and "
            "resolution-critique floors (source preservation still applies, and it owes "
            "its own `Consolidated into:` destination floor instead)"
            if classification == _CONSOLIDATED_CLASSIFICATION
            else "exempts this close from the behavioral-verdict and resolution-critique "
            "floors (only source preservation still applies)"
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


def _normalize_field_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"`", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


# Projected through the same normalizer the comparison uses, so every declared
# placeholder is reachable (B1). ``n/a`` -> ``n a``; the rest are already fixed
# points. Only a *bare* placeholder collapses to a set member: a value like
# ``n/a — issue was context only`` normalizes to ``n a issue was context only``
# and stays substantive, which is the intended split (a bare dismissal is not an
# answer; a dismissal with a reason is).
_NORMALIZED_PLACEHOLDER_VALUES = {_normalize_field_name(value) for value in _PLACEHOLDER_VALUES}


def _start_field(fields: dict[str, list[str]], match, name_of) -> str | None:
    """Open the field `match` names and seed its inline value; `None` if no match.

    Shared by the plain `Name:` and targeted `Name #N:` branches, which differ only
    in how the key is spelled -- keeping them as two copies is how they drift apart.
    """
    if match is None:
        return None
    key = _normalize_field_name(name_of(match))
    fields.setdefault(key, [])
    value = match.group("value").strip()
    if value:
        fields[key].append(value)
    return key


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
        started = _start_field(fields, _FIELD_RE.match(line), lambda m: m.group("name"))
        if started is None:
            started = _start_field(
                fields,
                _TARGETED_SECTION_RE.match(line),
                lambda m: f"{m.group('name')} {m.group('target')}",
            )
        if started is not None:
            current = started
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
    return normalized not in _NORMALIZED_PLACEHOLDER_VALUES and not normalized.startswith("missing ")


# Carriers whose close is performed by GitHub parsing a close keyword, where no
# `--reason` argv exists. `manual-fallback` and the `close-with-comment` path go
# through `issue_close`, which enforces the reason.
_AUTO_CLOSING_CARRIERS = ("direct-commit", "pr-body")


_classification_ledger = _load_local("issue_closeout_classification_ledger")
_classification_requirements = _classification_ledger.classification_requirements
_CLASSIFICATION_EXTRA_CHECKS = _classification_ledger.build_extra_checks(
    ledger_counts=_ledger_counts,
    consolidated=_consolidated,
    first_field=lambda fields, aliases: _first_field(fields, aliases),
    substantive=lambda value: _has_substantive_value(value),
    # The issue being closed, read from the body's own close keywords. Without this
    # the self-reference refusal never fired on the wired path.
    self_numbers=lambda text: [number for _repo, number in iter_close_keyword_refs(text)],
    strip_fences=lambda text: "\n".join(_strip_code_fences(text)),
    ledger=_classification_ledger,
    auto_closing_carriers=_AUTO_CLOSING_CARRIERS,
)


def _missing_ledger_fields(text: str, classification: str, *, carrier: str | None = None) -> list[str]:
    fields = _body_fields(text)
    missing = [
        field_id
        for field_id, aliases in _classification_requirements(classification)
        if not _has_substantive_value(_first_field(fields, aliases))
    ]
    extra = _CLASSIFICATION_EXTRA_CHECKS.get(classification)
    if extra is not None:
        missing.extend(extra(text, fields, carrier))
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
# ANCHORED to the value's leading token, mirroring the repo's existing disposition
# grammar (``scripts/disposition_form.py`` ``_APPLIED`` / ``_ISSUE_LEAD``). An
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


def evaluate_hotl_dispositions(text: str, classification: str) -> dict:
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
        dispositioned = _has_substantive_value(line["value"]) and _hotl_status_typed(line["value"])
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
