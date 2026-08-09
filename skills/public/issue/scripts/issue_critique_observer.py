"""Who actually read the resolution critique a close is about to cite.

The resolution-critique floor checks that a `Critique #N: <path>` line exists and
that the cited artifact binds to the issue. It never opens the question that line
is a proxy for: did anyone OTHER than the closing agent read this resolution?

A critique artifact records that answer itself, in its own
`Fresh-eye satisfaction:` line — `parent-delegated` / `nested-delegated` when a
distinct observer ran, `blocked <host-signal>` when the host could not spawn one.
The floor never opened the file. So an artifact recording that NO fresh eye ran
satisfied the floor exactly as well as one recording that a reviewer found four
blockers, at an irreversible public boundary.

This module reads that field and nothing else. It adds no gate: it is an existing
floor consuming a field that already exists, already has a typed contract, and is
already required by `validate_critique_artifacts.py` on the authoring side.

**Portability.** This is a public skill, so it must work in a repo that does not
use this repo's critique conventions. Two rules follow, and the split is the
whole design:

- an ABSENT field is never a refusal in a repo that did not adopt the delegation
  contract. Such a repo's critique artifacts carry no such line, and refusing
  would leave it unable to close any issue at all.
- a PRESENT but undelegated field is a refusal, because it is a positive record
  that no distinct observer read the resolution. The honest escape is not
  deleting the line — it is `blocked <host-signal>`, the same degradation valve
  the closeout body's `Critique: blocked <signal>` already offers, held to the
  same signal floor, which passes here with a loud advisory rather than a
  refusal.

**Under the contract, an absent field IS a refusal, and the reason it has to be
is worth recording.** The first version of this module let absence pass
everywhere, reasoning that `validate_critique_artifacts.py` already refuses an
artifact with no `Fresh-eye satisfaction:` line. A bounded review showed that
rationale is false: that validator runs at the COMMIT boundary, and
`close-with-comment` performs no commit — nothing orders it before the GitHub
mutation, and the cited artifact need not even be tracked. So "delete the line"
was a live bypass of this refusal, guarded by a floor on the wrong side of the
boundary. That is the same defect class this whole lane exists to close, so
absence refuses wherever the contract says the line should have been there.

`repo_requires_delegated_observer` reads the consuming repo's own `AGENTS.md`
for the delegation contract, mirroring
`validate_critique_artifacts.has_repo_delegation_contract`, so a repo that never
adopted the contract is not held to it.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

#: Both values assert a delegation that COMPLETED — a distinct observer read the
#: resolution. Kept in the same order and spelling as the authoring-side typed
#: contract so the two surfaces cannot disagree about what "delegated" means.
DELEGATED_VALUES = ("parent-delegated", "nested-delegated")
#: The degradation valve. A host that genuinely cannot spawn a reviewer records
#: this instead, and the close proceeds with an advisory.
BLOCKED_VALUE = "blocked"
FRESH_EYE_HEADING = "## fresh-eye satisfaction"
#: The same marker TEXT as `validate_critique_artifacts.DELEGATION_CONTRACT_MARKERS`,
#: restated rather than imported: this is a portable public skill, and reaching
#: into the harness repo's `scripts/` would make the guard absent — not merely
#: inert — in every consuming repo. The MATCHING now agrees again: that function
#: compared the raw literal and so returned False against a bolded
#: `**already delegated**` (which is how the AUTHORING repo writes it) until its own
#: repair gave it this same flattening step. The duplication stays deliberate,
#: and so does the drift risk it carries — which is why the authoring repo now
#: pins the parity with a test over its own real `AGENTS.md` rather than leaving
#: it to this comment.
DELEGATION_CONTRACT_MARKERS = (
    "subagent delegation",
    "repo-mandated bounded fresh-eye subagent reviews are already delegated",
)

# Markup is stripped everywhere before matching, never matched around. The
# corpus writes this field five ways — `Fresh-eye satisfaction:`,
# `- **Fresh-Eye Satisfaction**:`, `_Fresh_eye satisfaction_:`, a `##` section,
# and a bullet inside one — and a reader that accepts one spelling is a reader
# that returns "no record" for four honest artifacts and can be defeated by two
# asterisks on the fifth.
_MARKUP_CHARS = "`*_\"'>-"
_LEADING_MARKUP_RE = re.compile(r"^[\s`*_\"'>\-]+")
_KEY_RE = re.compile(r"^fresh[-_ ]eye\s+satisfaction$")
#: Any ATX heading depth. `### Fresh-Eye Satisfaction` is the same record as
#: `##`, and treating it as prose sent the reader to the inline fallback.
_HEADING_RE = re.compile(r"^#{2,}\s")
#: A `blocked` claim with no signal after it is ceremony, not a record. The
#: sibling in-body valve (`Critique: blocked <signal>`) is length-floored for
#: exactly this reason, and the refusal message tells authors to name the host
#: signal — so the cheapest way to comply must not be the bare word.
DEFAULT_MIN_BLOCKED_SIGNAL = 20
#: A `blocked` value that names a DECLINED standing delegation request rather
#: than a host incapacity. Matched narrowly, and narrower than it first looked:
#: only the hyphenated token the ladder's own `next_action` prescribes, or the
#: `delegation signal:` heading. The space form and a bare record-path mention
#: were both dropped because a GENUINE host refusal reads exactly that way —
#: "the spawn API returned 403, delegation declined by the workspace policy" —
#: and misreading a machine incapacity as a user's deliberate "no" is the more
#: damaging direction of the two.
_DECLINED_SIGNAL_RE = re.compile(r"delegation-declined|delegation signal:")
#: Clause boundaries. A CLAUSE is the scope a negation governs, and using it
#: replaces a fitted character window (see `_denies_delegation`). Punctuation is
#: structural, not vocabulary: it needs no word list and works in any language
#: that uses these marks.
_CLAUSE_SPLIT_RE = re.compile(r"[.;:!?\n]|—|--|,\s")
#: Words that DENY the delegated token in their clause. Position-independent
#: within the clause, because a negation governs its clause wherever it sits:
#: "nothing parent-delegated ran" negates from the left, "parent-delegated review
#: never ran" from the right, and a character window catches neither reliably.
#: STILL ENGLISH-ONLY, and that is a known, unfixed limitation stated rather than
#: hidden — a negation written in another language is not detected here, so this
#: floor's refusal is a floor on English records only.
_NEGATION_RE = re.compile(
    r"(?:^|\W)(?:not|no|never|without|nothing|none|failed to|unable to)(?:\W|$)"
)
#: An unedited `todo` anywhere in the value is not a delegation, wherever it
#: sits: a scaffold claiming delegation is the same-observer rubber stamp wearing
#: a typed value, which the authoring-side floor also refuses.
_TODO_MARKER = "todo"


def _denies_delegation(normalized: str) -> bool:
    """Whether every clause naming a delegated token negates it, or it is unedited.

    CLAUSE-SCOPED, NOT WINDOW-SCOPED, and that is a deliberate replacement of what
    stood here. The previous version searched for a hand-written English
    negation list (`not|no|never|without|failed to`) inside a 24-character window
    before the token. Both halves were wrong in the same way: the word list is
    English-only, so a negation in any other language read as a delegation; and
    the window was fitted — this file's own comment recorded that a value-wide
    scan "demoted eleven honest post-cutoff artifacts", so the span was narrowed
    until this repo's corpus looked right. No contract produced 24.

    The measured failure it allowed: `no fresh-eye reviewer was available, so
    nothing parent-delegated ran` returned `delegated`, because the negation sits
    more than 24 characters before the token. A sentence stating that NO
    delegation happened permitted an issue close asserting one did — at an
    irreversible public boundary, in the fail-OPEN direction.

    The replacement scopes the negation to the CLAUSE containing the token, using
    punctuation rather than a character count. A negation governs its clause, so
    position within it does not matter: `nothing parent-delegated ran` negates
    from the left and `parent-delegated review never ran` from the right, and no
    window catches both. Clause scoping also keeps the property the window was
    reaching for — `parent-delegated. Round 2 returned no blockers` stays a
    delegation, because the `no` is in a different clause.

    A LEADING-TOKEN (prefix) test was considered and rejected on evidence: ten
    checked-in artifacts record delegation as `satisfied — parent-delegated ...`,
    and a sibling test pins that form deliberately. Refusing them would put this
    floor's whole cost on honest authors and none on the failure mode.

    WHAT IS STILL WRONG HERE, STATED RATHER THAN HIDDEN. The negation vocabulary
    is English-only. A record that denies delegation in another language reads as
    a delegation, in the fail-OPEN direction, at a boundary that authorizes an
    irreversible public close. Removing the fitted window does not fix that; it
    removes one of the two defects. This is a floor on English records.
    """
    if _TODO_MARKER in normalized:
        return True
    for clause in _CLAUSE_SPLIT_RE.split(normalized):
        if not any(claim in clause for claim in DELEGATED_VALUES):
            continue
        if not _NEGATION_RE.search(clause):
            return False
    return True


def _dekey(raw: str) -> str:
    return raw.strip().strip(_MARKUP_CHARS).strip().lower()


def _split_field(line: str) -> str | None:
    """The value of an inline `Fresh-eye satisfaction:` line, or ``None``.

    Split on the FIRST colon and normalize the key, rather than matching a fixed
    ornament pattern: the key's markup varies across the corpus and the value's
    does not need to be guessed.
    """
    head, separator, tail = line.partition(":")
    if not separator:
        return None
    if not _KEY_RE.match(_dekey(head).replace("_", "-").replace("- ", "-")):
        return None
    return tail.strip()


def _declared_value(lines: list[str]) -> str | None:
    """The artifact's own claim, canonical section first.

    The `## Fresh-Eye Satisfaction` SECTION wins over any earlier inline mention,
    because a sentence in an earlier section that happens to use the phrase would
    otherwise shadow the real record below it. The inline fallback stays: much of
    the corpus writes the claim as a metadata bullet and never opens a section.
    Same precedence as the authoring-side reader, for the same reason.
    """
    for index, line in enumerate(lines):
        stripped = line.strip()
        if _HEADING_RE.match(stripped) and _dekey(stripped.lstrip("#").rstrip(":")) == "fresh-eye satisfaction":
            body: list[str] = []
            for following in lines[index + 1 :]:
                if _HEADING_RE.match(following.strip()):
                    break
                if following.strip():
                    body.append(following.strip())
            if not body:
                return None
            # Scan the WHOLE section body for a typed token, not just its first
            # line. A large slice of the corpus opens this section with a prose
            # verdict — "All three chunk reviewers ran in separate agent contexts
            # and returned ship" — and puts the typed value further down or not at
            # all. Reading only the first line refused six checked-in artifacts
            # that manifestly record a delegation, which is the over-block this
            # reader was already repaired once to avoid.
            joined = " ".join(body).lower()
            if joined.startswith(BLOCKED_VALUE) or any(claim in joined for claim in DELEGATED_VALUES):
                # Joined on NEWLINE, not a space: a paragraph break is a clause
                # boundary, and flattening it merged a typed `parent-delegated`
                # line with the unrelated paragraph below it into one clause --
                # so an artifact reading "parent-delegated" then "The reviewer had
                # no Bash" scored as a denied delegation. `_CLAUSE_SPLIT_RE` reads
                # the newline; nothing else depends on the separator.
                return "\n".join(body)
            # A section whose body is itself the bullet form.
            return _split_field(body[0]) or body[0]
    for line in lines:
        value = _split_field(line.strip().lstrip("-*").strip())
        if value:
            return value
    return None


def observer_disposition(
    text: str, *, strip_code_fences, min_blocked_signal: int = DEFAULT_MIN_BLOCKED_SIGNAL
) -> dict:
    """Classify who read the critique, from the artifact's own record.

    Fences are stripped first so a quoted example inside a code block is not read
    as the artifact's claim — the same trap the authoring-side reader already
    guards. `strip_code_fences` is injected rather than imported so this module
    stays free of sibling-loader wiring and is trivially testable.

    Dispositions: `delegated` (a distinct observer ran), `blocked` (the host
    could not spawn one, and named the signal), `blocked-unsubstantiated`
    (claims the valve without naming anything), `undelegated` (a record that
    positively states none of those), `absent` (no record at all — the
    portability case).

    A delegated token is matched by CONTAINMENT, not prefix, because the corpus's
    honest pre-cutoff form is `satisfied — parent-delegated bounded review
    returned ...`. Ten checked-in artifacts write it that way; a prefix test
    would refuse every one of them while catching no dishonest record, which is
    teeth landing entirely on honest authors. The authoring-side consistency
    check uses containment for the same reason.

    An unedited `todo` after a typed value is NOT a delegation, mirroring the
    authoring floor — a scaffold claiming delegation is the same-observer rubber
    stamp wearing a typed value.
    """
    value = _declared_value(strip_code_fences(text))
    if value is None:
        return {"value": None, "disposition": "absent"}
    normalized = _LEADING_MARKUP_RE.sub("", value).strip().lower()
    if not normalized:
        return {"value": value, "disposition": "absent"}
    # `blocked` is tested FIRST, before containment. A value that leads with
    # `blocked` and then names the delegation it could not perform — "blocked: no
    # parent-delegated reviewer could be spawned", the most natural phrasing of
    # the valve — otherwise reads as a COMPLETED delegation, losing its advisory
    # and slipping past the signal floor in 24 characters. Containment is the
    # right rule for the corpus's honest prose forms and the wrong rule for a
    # value whose first word already types it.
    if normalized.startswith(BLOCKED_VALUE):
        signal = normalized[len(BLOCKED_VALUE) :].strip(" :-*_`")
        if len(signal) < min_blocked_signal:
            return {"value": value, "disposition": "blocked-unsubstantiated"}
        # The valve's documented meaning is "a host that genuinely cannot spawn a
        # reviewer". The authorization ladder added a fourth state that is NOT
        # that: a user who declined the standing delegation request. It
        # reaches this branch as `blocked delegation-declined ...` and would
        # otherwise be reported at an irreversible public boundary as a host
        # incapacity — a user's deliberate "no" laundered into "the machine could
        # not". `blocked_kind` keeps the disposition stable for existing
        # consumers while naming which of the two this actually is.
        kind = "delegation-declined" if _DECLINED_SIGNAL_RE.search(signal) else "host"
        return {"value": value, "disposition": "blocked", "blocked_kind": kind}
    if any(claim in normalized for claim in DELEGATED_VALUES):
        # A value that DENIES or defers the delegation it names is not a record of
        # one. Containment cannot tell "parent-delegated review returned findings"
        # from "no parent-delegated review ran", and the second is the sentence an
        # honest author writes when none did.
        if _denies_delegation(normalized):
            return {"value": value, "disposition": "undelegated"}
        return {"value": value, "disposition": "delegated"}
    return {"value": value, "disposition": "undelegated"}


#: Artifacts written before the typed `Fresh-eye satisfaction:` contract existed
#: record delegation in prose — "All three chunk reviewers ran in separate agent
#: contexts and returned ship" — with no typed token anywhere. They are honest
#: records of a real delegation, and refusing them applies a rule that did not
#: exist when they were written. Mirrors the authoring-side presence floor's own
#: enforce-from date rather than inventing a second cutoff.
OBSERVER_RULE_DATE = date(2026, 7, 5)
_DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
_DATE_LINE_RE = re.compile(r"^\s*[-*]?\s*date\s*:\s*(?P<date>\d{4}-\d{2}-\d{2})", re.IGNORECASE | re.MULTILINE)


def artifact_observed_date(path: Path, text: str) -> date | None:
    """The artifact's own date, from a `Date:` line or a dated filename.

    Body first: a filename can be copied, and the `Date:` line is what the author
    wrote. Returns ``None`` when neither channel offers one — and an UNDATABLE
    artifact is treated as current, never as grandfathered, because a new
    artifact that carries no date is itself the anomaly.
    """
    match = _DATE_LINE_RE.search(text)
    if match is None:
        match = _DATE_RE.match(Path(path).name)
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group("date"))
    except ValueError:
        return None


def predates_typed_contract(path: Path, text: str) -> bool:
    """Whether this artifact is grandfathered out of the REFUSAL.

    Grandfathering is applied to the refusal only, never to the reported
    disposition: the payload keeps saying what the artifact actually records, so
    a grandfathered close is visibly grandfathered rather than silently clean.
    """
    observed = artifact_observed_date(path, text)
    return observed is not None and observed < OBSERVER_RULE_DATE


def _normalize_contract_text(text: str) -> str:
    """Drop fenced blocks, flatten inline markup, collapse whitespace.

    Three normalizations, each closing a way the SAME sentence stopped matching:
    markup is REMOVED not tolerated (this repo writes `**already delegated**`,
    and the plain substring test returned False in the repo that authored the
    contract); whitespace is collapsed because the 58-character marker only fits
    on one line at the template's current wrap width, so a reflow would drop an
    adopting repo out of the contract; and fenced blocks are dropped because a
    fence is documentation, not the repo's own assertion — `setup` ships the
    delegation template inside one for operators to copy.
    """

    kept: list[str] = []
    pending: list[str] = []
    opener: str | None = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if opener is None:
                opener = marker
                pending = []
                continue
            if marker[0] == opener[0] and len(marker) >= len(opener):
                opener = None
                pending = []
                continue
        if opener is None:
            kept.append(line)
        else:
            pending.append(line)
    # An UNCLOSED fence must not swallow the rest of the file. Dropping everything
    # after a stray ``` would silently un-adopt a repo whose contract sits below
    # it -- no failure, no log line, no ticket, which is the class this ladder was
    # built to close. Markdown renderers auto-close at EOF, so the file looks fine
    # to every human. Treat the unterminated tail as content: the error direction
    # is toward matching, which refuses strictly less.
    kept.extend(pending)
    flattened = re.sub(r"[`*_]+", "", "\n".join(kept).lower())
    return re.sub(r"\s+", " ", flattened)


def _delegation_record_state(repo_root: Path) -> tuple[str | None, list[str] | None]:
    """Rung 2 of the authorization ladder: the recorded decision and its scopes.

    A repo may grant the standing delegation request in
    `.agents/subagent-delegation.json` instead of `AGENTS.md` — and that is the
    exact repo class the ladder exists to serve, the one that never ran `setup`.
    Mirrors the record module shipped beside the ladder resolver: a `scopes` key
    that is present but not a non-empty list of strings makes the record
    unreadable rather than widening the grant to every scope.
    """

    path = Path(repo_root) / ".agents/subagent-delegation.json"
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(data, dict):
        return None, None
    value = data.get("bounded_review_delegation")
    if not isinstance(value, str):
        return None, None
    decision = value.strip().lower()
    if decision not in ("granted", "declined"):
        return None, None
    scopes: list[str] | None = None
    if "scopes" in data:
        raw_scopes = data.get("scopes")
        if not isinstance(raw_scopes, list) or not raw_scopes or not all(isinstance(s, str) for s in raw_scopes):
            return None, None
        scopes = [s.strip().lower() for s in raw_scopes]
    return decision, scopes


def _record_grants_scope(decision: str | None, scopes: list[str] | None, scope: str) -> bool:
    """A rung-2 grant authorizes `scope` only when it names it (or names none)."""

    if decision != "granted":
        return False
    return scopes is None or scope.strip().lower() in scopes


def repo_requires_delegated_observer(repo_root: Path, *, scope: str = "issue") -> bool:
    """Whether bounded review is AUTHORIZED in this repo for `scope`.

    Walks the same ladder as the shipped `resolve_subagent_delegation.py`,
    because a reader that knows only `AGENTS.md` goes inert in exactly the repo
    class the ladder exists to serve. Three states are modelled rather than
    collapsed into "adopted": a recorded `declined` is NOT authorization even
    under an `AGENTS.md` block (`setup` writes that block, so rung-1-is-final
    would let it override the user's only recorded "no", and then refuse closes
    in a repo whose user said no); a grant narrowed to a scope set excluding
    `scope` is not authorization for `scope`, or the repo is wedged — refused
    for not spawning a reviewer it has just been told it may not spawn; and an
    unreadable record is not a grant.

    A repo that never adopted it still gets the recorded disposition in the
    payload; it just is not refused for a field its conventions never defined.
    """
    record_decision, record_scopes = _delegation_record_state(repo_root)
    if record_decision == "declined":
        return False
    agents_path = Path(repo_root) / "AGENTS.md"
    if not agents_path.is_file():
        return _record_grants_scope(record_decision, record_scopes, scope)
    try:
        text = agents_path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return _record_grants_scope(record_decision, record_scopes, scope)
    if all(marker in _normalize_contract_text(text) for marker in DELEGATION_CONTRACT_MARKERS):
        return True
    # An `AGENTS.md` without the block does not end the ladder — rung 2 still can.
    return _record_grants_scope(record_decision, record_scopes, scope)
