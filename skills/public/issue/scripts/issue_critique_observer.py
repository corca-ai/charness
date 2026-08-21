"""Who actually read the resolution critique a close is about to cite.

The resolution-critique floor checks that a `Critique #N: <path>` line exists and
that the cited artifact binds to the issue. It also opens the question that line
is a proxy for: did anyone OTHER than the closing agent read this resolution?

A critique artifact records that answer itself, in its own
`Fresh-eye satisfaction:` line — `parent-delegated` / `nested-delegated` when a
distinct observer ran, `blocked <host-signal>` when the host could not spawn one.
The floor never opened the file. So an artifact recording that NO fresh eye ran
satisfied the floor exactly as well as one recording that a reviewer found four
blockers, at an irreversible public boundary.

For the default file-backed path, the field is only a claim: this module also
reads the shared worker report carrier and joins its packet/input identities to
the artifact's Reviewed Input Identity. Typed-subagent claims remain a separate
optional branch; they are never silently treated as file-backed approval.

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

import importlib.util
import re
from pathlib import Path

#: These values assert a delegation that COMPLETED — a distinct observer read the
#: resolution. `worker-delivered` additionally requires the durable report
#: carrier; the two typed-subagent values describe the optional host branch.
DELEGATED_VALUES = ("worker-delivered", "parent-delegated", "nested-delegated")
WORKER_DELIVERED_VALUE = "worker-delivered"
ROUND_CAP_VALUE = "accepted-unreviewed-under-round-cap"
#: The degradation valve. A host that genuinely cannot spawn a reviewer records
#: this instead, and the close proceeds with an advisory.
BLOCKED_VALUE = "blocked"
FRESH_EYE_HEADING = "## fresh-eye satisfaction"


def _load_worker_carrier():
    """Load the package-owned worker carrier without importing a consumer repo.

    The issue skill is public and may run from either the development tree or a
    collapsed plugin export.  Walking only the package's bounded ancestors keeps
    a consuming repository's arbitrary ``skills/shared`` or ``scripts`` from
    becoming an accidental implementation dependency.
    """
    here = Path(__file__).resolve()
    candidates: list[Path] = []
    for ancestor in list(here.parents)[:6]:
        candidates.extend(
            (
                ancestor / "shared" / "scripts" / "reviewer_worker_carrier.py",
                ancestor / "skills" / "shared" / "scripts" / "reviewer_worker_carrier.py",
            )
        )
    for candidate in candidates:
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location("charness_reviewer_worker_carrier", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


_worker_carrier = _load_worker_carrier()
_SUPPORT_SPEC = importlib.util.spec_from_file_location(
    "charness_issue_critique_observer_support",
    Path(__file__).resolve().with_name("issue_critique_observer_support.py"),
)
if _SUPPORT_SPEC is None or _SUPPORT_SPEC.loader is None:
    raise ImportError("issue critique observer support is unavailable")
_SUPPORT = importlib.util.module_from_spec(_SUPPORT_SPEC)
_SUPPORT_SPEC.loader.exec_module(_SUPPORT)

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
DELEGATION_CONTRACT_MARKERS = _SUPPORT.DELEGATION_CONTRACT_MARKERS
OBSERVER_RULE_DATE = _SUPPORT.OBSERVER_RULE_DATE
artifact_observed_date = _SUPPORT.artifact_observed_date
predates_typed_contract = _SUPPORT.predates_typed_contract
repo_requires_delegated_observer = _SUPPORT.repo_requires_delegated_observer

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
# DENIAL words, which negate the delegation itself wherever they sit in the clause.
_DENIAL_RE = re.compile(r"(?:^|\W)(?:not|never|without|nothing|failed to|unable to)(?:\W|$)")
# `no` / `none` are different: they usually govern an OBJECT, not the delegation.
# `parent-delegated bounded review found no blockers` is the commonest way a reviewer
# writes a clean result, and treating it as a denial refused an honest close with a
# message quoting a value that contains `parent-delegated` — an arbitrary refusal at an
# irreversible boundary, which is how a gate earns a route-around. So these count only
# when they sit BEFORE the token, where they negate the review rather than its findings:
# `no parent-delegated review ran` denies; `found no blockers` does not.
_OBJECT_NEGATION_RE = re.compile(r"(?:^|\W)(?:no|none)(?:\W|$)")
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
        positions = [clause.find(claim) for claim in DELEGATED_VALUES if claim in clause]
        if not positions:
            continue
        if _DENIAL_RE.search(clause):
            continue
        before = clause[: min(positions)]
        if _OBJECT_NEGATION_RE.search(before):
            continue
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


def _strip_fenced_lines(text: str) -> list[str]:
    """Keep only artifact content outside Markdown fences."""
    kept: list[str] = []
    opener: str | None = None
    indented_code = False
    for line in text.splitlines():
        leading = len(line) - len(line.lstrip(" "))
        if opener is None:
            if leading >= 4:
                indented_code = True
                continue
            if indented_code and not line.strip():
                continue
            indented_code = False
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if opener is None and marker is not None:
            opener = marker.group(1)
            continue
        if opener is not None and marker is not None:
            candidate = marker.group(1)
            leading = len(line) - len(line.lstrip(" "))
            trailing = line[leading + len(candidate) :].strip()
            if (
                candidate[0] == opener[0]
                and len(candidate) >= len(opener)
                and not trailing
            ):
                opener = None
                continue
        if opener is None:
            kept.append(line)
    # An unclosed fence does not turn its body into artifact metadata. Returning
    # only the already-kept prefix makes a malformed fenced carrier fail closed
    # instead of letting a quoted example satisfy the approval fields.
    return kept


def _section_fields(text: str, heading: str) -> dict[str, str]:
    """Read simple ``Field: value`` bullets from one named artifact section."""
    lines = _strip_fenced_lines(text)
    wanted = re.sub(r"[^a-z0-9]+", " ", heading.lower()).strip()
    fields: dict[str, str] = {}
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            current = re.sub(r"[^a-z0-9]+", " ", stripped.lstrip("#").lower()).strip()
            if current == wanted:
                inside = True
                continue
            if inside:
                break
        if not inside:
            continue
        head, separator, tail = stripped.partition(":")
        if not separator:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", head.strip(" -*_`>\"").lower()).strip()
        if key:
            fields[key] = tail.strip().strip("`")
    return fields


def _worker_carrier_disposition(
    repo_root: Path,
    text: str,
    *,
    required_issue_numbers: list[int] | None = None,
    required_repository: str | None = None,
) -> dict[str, object]:
    """Verify a ``worker-delivered`` claim through its durable report carrier."""
    if _worker_carrier is None:
        return {
            "disposition": "carrier-unverified",
            "carrier_verified": False,
            "carrier_reason": "the package's shared worker carrier validator is unavailable",
        }
    fields = _section_fields(text, "Reviewer Tier Evidence")
    binding = _section_fields(text, "Reviewed Input Identity")
    try:
        _worker_carrier.validate_worker_report_carrier(
            artifact_label="issue-resolution-critique",
            fields=fields,
            repo_root=repo_root,
            artifact_binding_fields=binding,
            require_delivery_chain=True,
            required_issue_numbers=required_issue_numbers,
            required_repository=required_repository,
            required_scope_prefix="issue-resolution",
        )
    except _worker_carrier.WorkerCarrierError as exc:
        return {
            "disposition": "carrier-unverified",
            "carrier_verified": False,
            "carrier_reason": str(exc),
        }
    return {"disposition": "delegated", "carrier_verified": True, "carrier": "worker-report"}


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
    if ROUND_CAP_VALUE in normalized:
        return {
            "value": value,
            "disposition": "round-cap-unreviewed",
            "round_cap": True,
        }
    if any(claim in normalized for claim in DELEGATED_VALUES):
        # A value that DENIES or defers the delegation it names is not a record of
        # one. Containment cannot tell "parent-delegated review returned findings"
        # from "no parent-delegated review ran", and the second is the sentence an
        # honest author writes when none did.
        if _denies_delegation(normalized):
            return {"value": value, "disposition": "undelegated"}
        return {"value": value, "disposition": "delegated"}
    return {"value": value, "disposition": "undelegated"}
