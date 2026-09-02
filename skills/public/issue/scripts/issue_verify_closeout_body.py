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

_CLOSING_KEYWORD_VERB = r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)(?:\s*:\s*|\s+)"
_CLOSING_KEYWORD_SLUG = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
# THREE spellings GitHub closes on, not one. `#N` was the only form this scanner saw;
# `GH-N` and the full issue URL closed issues that every consumer of this function --
# the commit-msg carrier, `verify_closeout`, the release closeout message -- reported
# nothing about. The pre-push guard carried a private wider copy for exactly this gap;
# widening here is what closes it for the other surfaces.
_CLOSING_KEYWORD_REF = (
    rf"(?:(?:{_CLOSING_KEYWORD_SLUG})?\#\d+|GH-\d+"
    rf"|https?://(?:www\.)?github\.com/{_CLOSING_KEYWORD_SLUG}/issues/\d+)"
)
_CLOSING_KEYWORD_LAUNCH_RE = re.compile(
    _CLOSING_KEYWORD_VERB
    + rf"(?P<refs>{_CLOSING_KEYWORD_REF}(?:\s*,\s*{_CLOSING_KEYWORD_REF})*)"
)
# IGNORECASE, matching the launch pattern's leading `(?i)`. Without it the two halves
# DISAGREE: `closes gh-700` launches, then extracts nothing, and the function returns an
# empty list for a span it just classified as a close. That state was unreachable while
# the only ref literal was `#`, which has no case, and the widening introduced three
# cased literals (`GH-`, `github.com`, `www.`) on one side of the pair only.
_CLOSING_KEYWORD_REF_RE = re.compile(
    rf"(?:https?://(?:www\.)?github\.com/(?P<url_repo>{_CLOSING_KEYWORD_SLUG})/issues/(?P<url_number>\d+)"
    rf"|GH-(?P<gh_number>\d+)"
    rf"|(?P<repo>{_CLOSING_KEYWORD_SLUG})?\#(?P<number>\d+))",
    re.IGNORECASE,
)


def iter_close_keyword_refs(text: str) -> list[tuple[str | None, int]]:
    """Every ``(repo_or_None, issue_number)`` a GitHub close keyword references
    in ``text``. This is the canonical close-keyword scanner for every BLOCKING
    surface. Issue-owned validators may keep narrower private grammars, so
    "canonical" does not mean "the only one"; the
    commit-msg checker (``scripts/gates/check_issue_closeout_commit_msg.py``) reuses
    it through the loaded ``issue_verify_closeout`` module rather than keeping
    a second copy, so the two surfaces cannot drift.

    Covers the plain form (``Closes #10``), GitHub's documented colon form
    (``Closes: #10``), the single-keyword comma-list form GitHub also recognizes
    (``Closes #10, #11, #12``) so a bundled reference is not missed just because
    the keyword was not repeated per issue, and -- since the widening this
    docstring's previous version disclaimed -- the ``GH-<n>`` spelling and the
    full issue-URL spelling (the host, owner/repo, and issue path GitHub itself
    links, as built by the module-level pattern above), each in the plain and
    comma-list positions.

    Not claimed: this models GitHub's close grammar from its documentation, not
    from a measured probe of GitHub's parser. A form GitHub closes on and the
    documentation does not describe is still invisible here, and would be
    invisible identically to every consumer -- which is the property that made
    keeping a second private copy in the pre-push guard worth removing as the
    SOLE detector, not worth removing as a redundant one.
    """
    refs: list[tuple[str | None, int]] = []
    for launch in _CLOSING_KEYWORD_LAUNCH_RE.finditer(text):
        for ref in _CLOSING_KEYWORD_REF_RE.finditer(launch.group("refs")):
            if ref.group("url_number"):
                refs.append((ref.group("url_repo"), int(ref.group("url_number"))))
            elif ref.group("gh_number"):
                refs.append((None, int(ref.group("gh_number"))))
            else:
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


def _missing_ledger_fields(
    text: str,
    classification: str,
    *,
    carrier: str | None = None,
    invoked_numbers: tuple[int, ...] = (),
) -> list[str]:
    fields = _body_fields(text)
    missing = [
        field_id
        for field_id, aliases in _classification_requirements(classification)
        if not _has_substantive_value(_first_field(fields, aliases))
    ]
    extra = _CLASSIFICATION_EXTRA_CHECKS.get(classification)
    if extra is not None:
        if classification == _consolidated.CLASSIFICATION:
            missing.extend(extra(text, fields, carrier, invoked_numbers))
        else:
            missing.extend(extra(text, fields, carrier))
    return missing


def _missing_close_keywords(text: str, numbers: list[int], repo: str) -> list[int]:
    found: set[int] = set()
    selected_repo = repo.lower()
    plain = "\n".join(_strip_code_fences(text))
    for qualified_repo, number in iter_close_keyword_refs(plain):
        if qualified_repo is not None and qualified_repo.lower() != selected_repo:
            continue
        found.add(number)
    return [number for number in numbers if number not in found]
