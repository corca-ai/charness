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
#: inert — in every consuming repo. The MATCHING no longer agrees, deliberately:
#: that function compares the raw literal and so returns False against a bolded
#: `**already delegated**`, which is how this repo writes it. Its own repair is
#: tracked separately; do not assume behavioural parity when reading this.
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
#: Words that DENY the delegated token they precede. Matched ONLY in the short
#: window immediately before the token, never anywhere in the value: the corpus's
#: real records are prose sentences that routinely say "no blockers" and "not
#: shipped" while recording a genuine delegation, and a value-wide scan demoted
#: eleven honest post-cutoff artifacts on exactly those words.
_NEGATION_RE = re.compile(r"(?:^|\W)(?:not|no|never|without|failed to)\W+$")
#: An unedited `todo` anywhere in the value is not a delegation, wherever it
#: sits: a scaffold claiming delegation is the same-observer rubber stamp wearing
#: a typed value, which the authoring-side floor also refuses.
_TODO_MARKER = "todo"


def _denies_delegation(normalized: str) -> bool:
    """Whether every occurrence of a delegated token is negated or unedited.

    One un-negated occurrence is a record of a delegation. This floor is
    presence/typed-form only — whether the delegation it records actually
    happened stays reviewer judgment, the same boundary every sibling floor
    holds — so it does not try to adjudicate contrary prose surrounding an
    otherwise plain claim.
    """
    if _TODO_MARKER in normalized:
        return True
    for claim in DELEGATED_VALUES:
        start = normalized.find(claim)
        while start != -1:
            if not _NEGATION_RE.search(normalized[max(0, start - 24) : start]):
                return False
            start = normalized.find(claim, start + 1)
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
                return " ".join(body)
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
        return {"value": value, "disposition": "blocked"}
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


def repo_requires_delegated_observer(repo_root: Path) -> bool:
    """Whether the consuming repo adopted the bounded-review delegation contract.

    A repo that never adopted it still gets the recorded disposition in the
    payload; it just is not refused for a field its conventions never defined.
    """
    agents_path = Path(repo_root) / "AGENTS.md"
    if not agents_path.is_file():
        return False
    try:
        text = agents_path.read_text(encoding="utf-8").lower()
    except OSError:
        return False
    # Markup is REMOVED before matching, not tolerated inside the literal. This
    # repo's own AGENTS.md writes `**already delegated**`, so a plain substring
    # test against the unbolded sentence returned False here — the refusal was
    # inert in the repo it was written for, and nothing said so.
    flattened = re.sub(r"[`*_]+", "", text)
    return all(marker in flattened for marker in DELEGATION_CONTRACT_MARKERS)
