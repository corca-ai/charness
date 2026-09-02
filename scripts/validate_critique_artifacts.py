#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from datetime import date
from functools import partial
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
_adversarial_evidence = import_repo_module(__file__, "scripts.adversarial_evidence")
ValidationError = _artifact_validator.ValidationError
report_validation_failure = _artifact_validator.report_validation_failure
git_changed_paths = _artifact_validator.git_changed_paths
is_valid_followup_tail = _artifact_validator.is_valid_followup_tail
run_changed_artifact_validator = _artifact_validator.run_changed_artifact_validator
run_validation_checks = _artifact_validator.run_validation_checks


validate_adversarial_evidence = partial(
    _adversarial_evidence.validate_for_artifact, error_cls=ValidationError
)

# Cross-surface probe (#408): consulted only when --changed-ref/--changed-path is passed.
_boundary_probe_lib = import_repo_module(__file__, "scripts.boundary_probe_lib")
_critique_adapter_lib = import_repo_module(__file__, "scripts.critique_adapter_lib")
_reviewed_input_binding = import_repo_module(__file__, "scripts.critique_reviewed_input_binding")
_reviewer_evidence = import_repo_module(__file__, "scripts.critique_reviewer_evidence")
# The enforcement-scope concept (which floor was live, over what) lives in one
# module rather than as conditions scattered across this file's use sites.
_scope = import_repo_module(__file__, "scripts.critique_enforcement_scope")
# One home for "the lines of a markdown section": this file carried three copies of
# the same heading walk, each with a slightly different heading matcher.
_sections = import_repo_module(__file__, "scripts.core.markdown_sections")
# The required-fields / unique-id / typed-enum loop over a structured-entry
# section, shared with the ideation `## Structured Questions` floor.
_structured_findings = import_repo_module(__file__, "scripts.critique_structured_findings")
_verification_scope = import_repo_module(__file__, "scripts.critique_verification_scope")
_critique_universe = import_repo_module(__file__, "scripts.critique_artifact_universe")
__getattr__ = _critique_universe.__getattribute__
PACKET_CONSUMED_RE = _scope.PACKET_CONSUMED_RE
critique_observed_date = _scope.critique_observed_date
# Kept as module attributes: `tests/test_validate_critique_artifacts_dates.py`
# pins the calendar-validity behavior of both date channels through this module.
_date_from_filename = _scope.date_from_filename
_date_from_body = _scope.date_from_body
REVIEWER_TIER_HEADING = _reviewer_evidence.REVIEWER_TIER_HEADING
REVIEWER_TIER_REQUIRED_FIELDS = _reviewer_evidence.REVIEWER_TIER_REQUIRED_FIELDS
REVIEWER_TIER_HOST_STATES = _reviewer_evidence.REVIEWER_TIER_HOST_STATES
DELIVERY_STATE_RULE_DATE = _reviewer_evidence.DELIVERY_STATE_RULE_DATE
DELIVERY_STATE_FIELD = _reviewer_evidence.DELIVERY_STATE_FIELD
DELIVERY_STATE_VALUES = _reviewer_evidence.DELIVERY_STATE_VALUES
DELIVERY_STATE_VALUES_SUMMARY = _reviewer_evidence.DELIVERY_STATE_VALUES_SUMMARY
WORKER_REPORT_FIELDS = _reviewer_evidence.WORKER_REPORT_FIELDS

# Public compatibility surface: the scaffold tests and installed consumers have
# historically imported these validator enums directly. Extracting the parser
# must not turn a structural refactor into an API disappearance.
STRUCTURED_BINS = _structured_findings.STRUCTURED_BINS
STRUCTURED_EVIDENCE = _structured_findings.STRUCTURED_EVIDENCE
STRUCTURED_ACTIONS = _structured_findings.STRUCTURED_ACTIONS
STRUCTURED_REQUIRED_FIELDS = _structured_findings.STRUCTURED_REQUIRED_FIELDS
STRUCTURED_FINDING_FORM = _structured_findings.STRUCTURED_FINDING_FORM
FORBIDDEN_SUBAGENT_BLOCKER_PHRASES = (
    "did not explicitly allow subagents",
    "explicit subagent allowance",
    "only permits spawning subagents when",
    "only permits spawning subagents after",
    "current session delegation policy",
    "current developer instruction only permits",
)
DELEGATION_CONTRACT_MARKERS = (
    "subagent delegation",
    "repo-mandated bounded fresh-eye subagent reviews are already delegated",
)
# `delegation signal` added with the authorization ladder (#475). A user who
# DECLINES the standing delegation request at rung 3 is a real, recorded reason
# the review did not run, but it is not a host or tool signal — and the only
# way to satisfy this floor without it was to write a `host signal:` line that
# would be a lie. Widening what this floor ACCEPTS refuses strictly less.
SIGNAL_HEADINGS = ("host signal", "tool signal", "delegation signal")
PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na", "blocked"}

# Distinct-observer presence floor (counterweight-verified: an artifact with no
# `Fresh-eye satisfaction:` line skips every observer check below — the #386
# same-observer rubber stamp in file form). Enforce-from-date mirrors the
# established `disposition_form.DISPOSITION_FORM_RULE_DATE` /
# `validate_retro_artifact.RECURRENCE_LINEAGE_RULE_DATE` shape: this floor lands
# 2026-07-04, so enforcement begins the next day and every artifact dated
# on/before the landing day is grandfathered. Clone-safe: an in-file constant,
# not mtime.
FRESH_EYE_PRESENCE_RULE_DATE = date(2026, 7, 5)
# `nested-delegated` has no downstream evidence-linking check today (unlike
# `parent-delegated` -> Reviewer Tier Evidence, `blocked` -> host/tool signal
# detail) — presence/form-only per this floor's own boundary, so this is a
# known, accepted gap rather than a missed one; adding a required nested-run
# citation is a separate floor-addition call, not folded in here.
FRESH_EYE_TYPED_VALUES = (
    "worker-delivered",
    "parent-delegated",
    "nested-delegated",
    "blocked",
    "accepted-unreviewed-under-round-cap",
)
FRESH_EYE_TYPED_VALUES_SUMMARY = (
    "`worker-delivered` / `parent-delegated` / `nested-delegated` / `blocked <host-signal>` / "
    "`accepted-unreviewed-under-round-cap <cap-signal>`"
)
# Adversarial-review finding: a typed value whose remainder still carries an
# unedited `todo` (e.g. a scaffolded `parent-delegated (TODO confirm ...)`)
# must not satisfy the floor — that is an unedited stub silently claiming
# delegation, the exact same-observer rubber stamp (#386) this floor exists to
# stop. Mirrors this file's own `PLACEHOLDER_VALUES`/`"missing "` treatment.
FRESH_EYE_TODO_MARKER = "todo"
# Boundary-ownership presence floor (#408/#414/#416): every critique artifact
# records a typed `Verdict:` so a producer/consumer ownership decision cannot be
# silently skipped. Presence + typed-value only; correctness stays reviewer
# judgment (same boundary as the fresh-eye floor + the D34 announcement posture).
# `RULE_DATE = landing_day + 1` grandfather shape (lands 2026-07-05, enforced the
# next day). See skills/shared/references/boundary-ownership-brief.md.
BOUNDARY_OWNERSHIP_RULE_DATE = date(2026, 7, 6)
BOUNDARY_OWNERSHIP_HEADING = "## Boundary Ownership"
BOUNDARY_VERDICT_VALUES = tuple("single-surface owned-correctly moved-to-owner escalated-to-issue-spec".split())  # fmt: skip
BOUNDARY_VERDICT_SUMMARY = " / ".join(f"`{value}`" for value in BOUNDARY_VERDICT_VALUES)

VERIFICATION_FAILURE_CLASSIFICATIONS = _verification_scope.FAILURE_CLASSIFICATIONS
VERIFICATION_RETRY_DISPOSITIONS = _verification_scope.RETRY_DISPOSITIONS
# Undatable critique artifacts present when the boundary floor landed — a closed
# allowlist, NOT fail-open (a NEW undatable artifact is still enforced; the
# scaffold always emits a dated filename). Kept separate from the fresh-eye
# allowlist so grandfathering here never weakens that floor's own enforcement.
#
# One entry, not three. `release-0-55-0-full-packet.md` and
# `release-0-55-1-packet.md` are `charness.critique_prepare_packet` documents,
# which `candidate_paths` excludes by content kind in BOTH selection modes, so
# neither name ever reached this check. They read as live grandfather decisions —
# two artifacts this floor had deliberately excused — while excusing nothing, which
# is worse than an empty allowlist: a reader auditing what the floor lets through
# counts three exemptions and can find no way to reach two of them.
BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS = frozenset({"release-0-55-1-critique.md"})
# Reviewer tier evidence is not a new floor — it has been enforced since the
# fresh-eye presence floor landed — but it was enforced only for artifacts the
# run SELECTED, so `--all` (the command `.agents/surfaces.json` declares as this
# validator's verify command) skipped it for every artifact including the ones it
# was written for. Whether an artifact carries the evidence is a property of the
# artifact, not of how the run happened to reach it, so it is now required by
# date in every mode. Sharing the fresh-eye date rather than taking a new one is
# a measured claim: a sweep of all 650 checked-in critique artifacts found zero
# dated on/after it that claim `parent-delegated` without a tier block.
TIER_EVIDENCE_RULE_DATE = FRESH_EYE_PRESENCE_RULE_DATE
# Leading markdown/quote markup stripped before matching a typed token, so a
# backtick-wrapped or bulleted value (`` `parent-delegated`. `` — the observed
# in-corpus convention) still matches; mirrors `disposition_form._MARKDOWN_LEAD`.
_LEADING_MARKUP_RE = re.compile(r"^[\s`*_\"'>\-]+")
# Inline emphasis stripped ANYWHERE in a line before a contract marker is matched
# (#471), not just at the leading edge. Same character class and same spelling as
# `issue_critique_observer`'s flattening step.
_MARKUP_FLATTEN_RE = re.compile(r"[`*_]+")
# Fenced blocks are dropped and whitespace collapsed before matching (#475).
# A fence is documentation, not the repo's own assertion — `setup` ships the
# delegation template inside one for operators to copy — and the 58-character
# marker only fits on one line at the template's current wrap width, so a
# reflow would otherwise drop an adopting repo out of the contract. Same
# spelling as `resolve_subagent_delegation.normalize_contract_text` and
# `issue_critique_observer`; the three are pinned by a shared-fixture parity test.
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_WHITESPACE_COLLAPSE_RE = re.compile(r"\s+")
# Rung 2 of the authorization ladder. A repo may grant the standing delegation
# request here instead of in `AGENTS.md`; see the `Subagent Delegation` block
# and `skills/shared/references/fresh-eye-subagent-review.md`.
DELEGATION_RECORD_RELPATH = ".agents/subagent-delegation.json"
DELEGATION_RECORD_FIELD = "bounded_review_delegation"
DELEGATION_RECORD_GRANTED = "granted"
DELEGATION_RECORD_DECLINED = "declined"


def _record_grants_scope(decision: str | None, scopes: list[str] | None, scope: str) -> bool:
    """A rung-2 grant authorizes `scope` only when it names it (or names none)."""

    if decision != DELEGATION_RECORD_GRANTED:
        return False
    return scopes is None or scope.strip().lower() in scopes


def changed_paths(repo_root: Path) -> list[str]:
    return git_changed_paths(repo_root, artifact_label="critique")


def _normalize_contract_text(text: str) -> str:
    """Drop fenced blocks, flatten inline markup, collapse whitespace."""

    kept: list[str] = []
    pending: list[str] = []
    opener: str | None = None
    for line in text.splitlines():
        match = _FENCE_RE.match(line)
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
    flattened = _MARKUP_FLATTEN_RE.sub("", "\n".join(kept).lower())
    return _WHITESPACE_COLLAPSE_RE.sub(" ", flattened)


def _delegation_record_state(repo_root: Path) -> tuple[str | None, list[str] | None]:
    """Rung 2: the recorded decision and the scopes it covers, or `(None, None)`.

    Mirrors `skills/shared/scripts/subagent_delegation_record.py`: a `scopes` key
    that is present but not a non-empty list of strings makes the record
    unreadable rather than widening the grant to every scope.
    """

    path = repo_root / DELEGATION_RECORD_RELPATH
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(data, dict):
        return None, None
    value = data.get(DELEGATION_RECORD_FIELD)
    if not isinstance(value, str):
        return None, None
    decision = value.strip().lower()
    if decision not in (DELEGATION_RECORD_GRANTED, DELEGATION_RECORD_DECLINED):
        return None, None
    scopes: list[str] | None = None
    if "scopes" in data:
        raw_scopes = data.get("scopes")
        if (
            not isinstance(raw_scopes, list)
            or not raw_scopes
            or not all(isinstance(s, str) for s in raw_scopes)
        ):
            return None, None
        scopes = [s.strip().lower() for s in raw_scopes]
    return decision, scopes


def has_repo_delegation_contract(repo_root: Path, *, scope: str = "critique") -> bool:
    """Whether bounded review is AUTHORIZED here for `scope`.

    This walks the same ladder as
    `skills/shared/scripts/resolve_subagent_delegation.py`, because a reader that
    knows only rung 1 goes inert in exactly the repo class the ladder exists to
    serve — the one that never ran `setup` and granted at rung 2. Three states
    the ladder invented are modelled here rather than collapsed to "adopted":

    * a recorded `declined` means NOT authorized, even under an `AGENTS.md`
      block — `setup` WRITES that block, so treating rung 1 as final would let
      it override the user's only recorded "no" and then refuse artifacts in a
      repo whose user said no;
    * a grant narrowed to a scope set that excludes `scope` is not authorization
      for `scope`, or the repo is wedged: refused for not spawning a reviewer
      the ladder told it it may not spawn;
    * an unreadable record is not a grant.
    """

    record_decision, record_scopes = _delegation_record_state(repo_root)
    if record_decision == DELEGATION_RECORD_DECLINED:
        return False
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.is_file():
        return _record_grants_scope(record_decision, record_scopes, scope)
    try:
        text = agents_path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        # Unreadable is NOT adopted. Without this the two readers of one contract
        # disagree on an unreadable `AGENTS.md` (the sibling returns False here),
        # and the OSError escapes as an uncaught traceback rather than a
        # ValidationError, so `main`'s handler never renders it as a validation
        # failure. Same shape as the SurfaceError worry this module already has.
        return _record_grants_scope(record_decision, record_scopes, scope)
    # Markup is REMOVED before matching, not tolerated inside the literal (#471).
    # This repo's own AGENTS.md writes `**already delegated**`, so the plain
    # substring test this replaced returned False HERE — the gate below
    # (`_check_forbidden_blocker_phrases`) had never fired in the repo it was
    # written for, and nothing said so, because no test read the real file. The
    # rule matched the emphasis, not the sentence. Kept character-identical to
    # `issue_critique_observer.repo_requires_delegated_observer` and to
    # `resolve_subagent_delegation.normalize_contract_text`, so the three readers
    # of one contract cannot disagree about whether a repo adopted it.
    if all(marker in _normalize_contract_text(text) for marker in DELEGATION_CONTRACT_MARKERS):
        return True
    # An `AGENTS.md` without the block does not end the ladder — rung 2 still can.
    return _record_grants_scope(record_decision, record_scopes, scope)


# Claim-reading lives with the enforcement-scope concept: "which claim does this
# artifact actually assert" is the same question as "what did this run establish",
# and the consistency check depends on getting it right.
fresh_eye_satisfaction_status = _scope.fresh_eye_satisfaction_status


def _substantive_signal(value: str) -> bool:
    signal_text = value.strip().strip("-*`._:;,#[](){}<>!/?\\|\"' ")
    normalized = " ".join(value.strip().lower().split())
    return (
        bool(signal_text)
        and any(character.isalnum() for character in signal_text)
        and normalized not in PLACEHOLDER_VALUES
        and not normalized.startswith("missing ")
    )


def has_blocked_signal_detail(text: str) -> bool:
    lines = text.splitlines()
    for raw in lines:
        lowered = raw.strip().lower().lstrip("-*").strip()
        for heading in SIGNAL_HEADINGS:
            marker = f"{heading}:"
            if lowered.startswith(marker) and _substantive_signal(lowered.removeprefix(marker)):
                return True
            # A signal heading also counts INSIDE the line, not only at its start.
            # The typed record is written as one line — `Fresh-eye satisfaction:
            # blocked <value> — <heading>: <signal>` — so a prefix-only match
            # refused every record that follows the contract's own prescribed
            # form while accepting only a form nothing prescribes. That is the
            # inert-rule class: the floor could not fire where it was written to.
            offset = lowered.find(f" {marker}")
            if offset != -1 and _substantive_signal(lowered[offset + len(marker) + 1 :]):
                return True
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower().rstrip(":")
        if lowered.startswith("#"):
            lowered = lowered.lstrip("#").strip()
        if lowered not in SIGNAL_HEADINGS:
            continue
        # The heading matcher here is this floor's own (any `#` depth, optional
        # trailing colon, one of a set of spellings), so only the boundary rule is
        # shared — which is the half that kept being re-derived.
        for following in _sections.lines_until_next_section(lines[index + 1 :]):
            if _substantive_signal(following.strip()):
                return True
    return False


def _is_valid_followup_value(value: str) -> bool:
    """Same grammar as `debug` sibling follow-up: identifier or `deferred <anchor>`.

    Delegates to the shared `artifact_validator.is_valid_followup_tail` so the
    follow-up grammar lives in one place (the Closeout Schema Rule in
    `create-skill/references/portable-authoring.md` requires reusing it).
    """
    return is_valid_followup_tail(value.strip().lower())


_check_finding_followup = _structured_findings._check_finding_followup
validate_structured_findings = _structured_findings.validate_structured_findings


def _section_field_map(text: str, heading: str) -> dict[str, str]:
    return _sections.section_field_map(text, heading)


def _opens_with_typed_value(value: str, allowed: tuple[str, ...]) -> bool:
    """Whether ``value`` opens with one of ``allowed`` (after stripping
    backtick/quote/bullet markup) AND the remainder is not still an unedited
    ``todo`` placeholder. The shared presence/form check behind both the
    fresh-eye and boundary-ownership floors: it proves the artifact committed to
    a falsifiable claim *type*, never whether the claim is true — that stays
    reviewer judgment. The ``todo``-in-remainder rejection is the narrow
    exception: a scaffolded ``<typed> (TODO ...)`` is an unedited stub, not a
    claim, and accepting it would let an unedited default silently satisfy the
    floor (the same-observer rubber stamp, #386, these floors exist to stop)."""
    token = _LEADING_MARKUP_RE.sub("", value.strip().lower())
    matched = next((candidate for candidate in allowed if token.startswith(candidate)), None)
    if matched is None:
        return False
    return FRESH_EYE_TODO_MARKER not in token[len(matched) :]


def validate_reviewer_tier_evidence(path: Path, text: str) -> None:
    _reviewer_evidence.validate_reviewer_tier_evidence(
        path, text, section_field_map=_section_field_map
    )


validate_delivery_state = _reviewer_evidence.validate_delivery_state
validate_reviewed_input_binding = _reviewed_input_binding.validate_reviewed_input_binding


def check_boundary_ownership_typed_presence(
    path: Path, text: str, observed_date: date | None, *, cross_surface_hit: bool = False
) -> None:
    """The boundary-ownership presence floor. Module-level (not a nested closure)
    so it does not add to ``validate_critique_artifact``'s cyclomatic complexity.
    Grandfather mirrors the fresh-eye floor (dated-before-cutoff or legacy-undatable
    allowlist). Typed-presence only — EXCEPT that when ``cross_surface_hit`` is True
    the repo probe matched the changed paths, so a bare ``single-surface`` verdict
    is rejected: the objective path-match overrides the self-assertion (#408)."""
    if observed_date is not None and observed_date < BOUNDARY_OWNERSHIP_RULE_DATE:
        return
    if observed_date is None and path.name in BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS:
        return
    verdict = _section_field_map(text, BOUNDARY_OWNERSHIP_HEADING).get("verdict", "")
    if not verdict:
        raise ValidationError(
            f"{path}: critique artifact has no `## Boundary Ownership` section with a typed "
            f"`Verdict:` line; every critique artifact must record one of {BOUNDARY_VERDICT_SUMMARY} "
            "(run the producer/consumer brief at "
            "skills/shared/references/boundary-ownership-brief.md) — an omitted disposition "
            "silently skips the producer/consumer ownership question (#408)."
        )
    if not _opens_with_typed_value(verdict, BOUNDARY_VERDICT_VALUES):
        raise ValidationError(
            f"{path}: `## Boundary Ownership` verdict `{verdict[:80]}` does not open with one of "
            f"{BOUNDARY_VERDICT_SUMMARY}, or still carries an unedited `todo` after the typed value "
            "— either way it is not a real disposition."
        )
    normalized = _LEADING_MARKUP_RE.sub("", verdict.strip().lower())
    if cross_surface_hit and normalized.startswith("single-surface"):
        raise ValidationError(
            f"{path}: the changed paths match this repo's cross-surface probe, so a bare "
            "`single-surface` boundary verdict is rejected — record `owned-correctly` / "
            "`moved-to-owner` / `escalated-to-issue-spec` (the #408 objective override). See "
            "skills/shared/references/boundary-ownership-brief.md."
        )


def validate_critique_artifact(
    path: Path,
    *,
    repo_has_delegation_contract: bool,
    require_tier_evidence: bool,
    collect_all: bool = False,
    cross_surface_hit: bool = False,
    check_current_binding: bool = True,
    repo_root: Path | None = None,
    evidence_mode: bool = False,
) -> None:
    text = path.read_text(encoding="utf-8")
    status = fresh_eye_satisfaction_status(text)
    status_lowered = status.lower() if status is not None else ""
    observed_date = critique_observed_date(path, text)

    def _check_fresh_eye_typed_presence() -> None:
        # Grandfather is narrow, not fail-open: a dated artifact before the
        # cutoff is grandfathered, and nothing else. This floor USED to carry its
        # own undatable allowlist naming two artifacts — both
        # `charness.critique_prepare_packet` documents that `candidate_paths`
        # excludes by content kind, so the branch could not fire for either. It
        # is gone rather than emptied: an allowlist that excuses nothing still
        # tells a reader auditing this floor that two artifacts were excused.
        # Every undatable artifact — including a new one that never picks up a
        # `Date:` line or a dated filename — is enforced exactly as if dated
        # post-cutoff, since an undatable NEW artifact is itself the anomaly.
        if observed_date is not None and observed_date < FRESH_EYE_PRESENCE_RULE_DATE:
            return
        # floor-addition-restraint: irreversible-boundary P4 floor, typed-presence-only
        if not status_lowered:
            raise ValidationError(
                f"{path}: critique artifact has no `Fresh-eye satisfaction:` line; every "
                f"critique artifact must record one of {FRESH_EYE_TYPED_VALUES_SUMMARY} — an "
                "omitted line otherwise skips every distinct-observer check below (the #386 "
                "same-observer rubber stamp in file form)."
            )
        if not _opens_with_typed_value(status_lowered, FRESH_EYE_TYPED_VALUES):
            raise ValidationError(
                f"{path}: `Fresh-eye satisfaction` value `{status_lowered[:80]}` does not open with "
                f"one of the typed values {FRESH_EYE_TYPED_VALUES_SUMMARY}, or still carries an "
                "unedited `todo` after the typed value — either way it is not a real record."
            )

    def _check_forbidden_blocker_phrases() -> None:
        if not repo_has_delegation_contract:
            return
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in status_lowered:
                raise ValidationError(
                    f"{path}: `Fresh-eye satisfaction` matched the forbidden phrase `{phrase}`; "
                    "critique artifact must not treat missing explicit subagent delegation "
                    "as the canonical blocker; honor repo `Subagent Delegation` instructions, then cite "
                    "the concrete spawn-tool refusal, missing tool surface, or exhausted host budget if "
                    "delegation is still blocked"
                )

    def _check_blocked_signal_detail() -> None:
        if (
            status_lowered
            and "blocked" in status_lowered
            and "parent-delegated" not in status_lowered
        ):
            if not has_blocked_signal_detail(text):
                raise ValidationError(
                    f"{path}: blocked critique fresh-eye satisfaction must cite `host signal:`, "
                    "`tool signal:`, or — when the user declined the standing delegation request — "
                    "`delegation signal:`. Do not write a host signal that did not occur."
                )

    def _check_reviewer_tier_evidence() -> None:
        # Selection mode OR date: a post-cutoff artifact carries tier evidence
        # whichever way the run reached it, so `--all` can no longer be the mode
        # in which this floor is universally off.
        #
        # `observed_date is None` counts as INTO the floor, matching every sibling
        # here and this module's own stated rule that an undatable artifact is
        # enforced as if post-cutoff. The first cut read `is not None and >=`,
        # which made "no parseable date" a total exemption under `--all` — and
        # becoming undatable is easy and often accidental (an undated filename,
        # or a `Date:` written as `**Date:**` or pushed past line 5). That handed
        # back the whole of C4 through the one input the rule names as never
        # fail-open.
        dated_into_floor = observed_date is None or observed_date >= TIER_EVIDENCE_RULE_DATE
        # `parent-delegated` only, NOT the full completed-delegation set. The
        # consistency check covers `nested-delegated` because it merely reads back
        # fields that are already present; requiring the tier SECTION for a nested
        # claim would be a new floor demanding a new artifact shape, and this
        # module's own comment records the absence of a nested evidence link as a
        # known, accepted boundary. Widening it here would have been a floor
        # addition smuggled in as a fix.
        requires_tier_evidence = (require_tier_evidence or dated_into_floor) and (
            "parent-delegated" in status_lowered or _scope.packet_consumed(text)
        )
        if requires_tier_evidence or _section_field_map(text, REVIEWER_TIER_HEADING):
            validate_reviewer_tier_evidence(path, text)
            _reviewer_evidence.validate_delivery_state(
                path,
                text,
                observed_date,
                section_field_map=_section_field_map,
                opens_with_typed_value=_opens_with_typed_value,
                legacy_undatable=BOUNDARY_LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS,
            )

    checks = (
        lambda: validate_adversarial_evidence(
            text,
            artifact_label="critique artifact",
            evidence_mode=evidence_mode,
            repo_root=repo_root,
        ),
        _check_fresh_eye_typed_presence,
        lambda: check_boundary_ownership_typed_presence(
            path, text, observed_date, cross_surface_hit=cross_surface_hit
        ),
        _check_forbidden_blocker_phrases,
        _check_blocked_signal_detail,
        lambda: validate_structured_findings(path, text),
        lambda: _verification_scope.validate(path, text),
        _check_reviewer_tier_evidence,
        lambda: _reviewer_evidence.validate_delegation_consistency(
            path, text, status_lowered, section_field_map=_section_field_map
        ),
        lambda: _reviewer_evidence.validate_worker_delivery_evidence(
            path,
            text,
            status_lowered,
            section_field_map=_section_field_map,
            repo_root=repo_root,
            artifact_binding_fields=_reviewed_input_binding.reviewed_input_binding_fields(text),
        ),
        lambda: validate_reviewed_input_binding(
            path,
            text,
            observed_date,
            check_current=check_current_binding,
            repo_root=repo_root,
        ),
    )
    run_validation_checks(
        checks,
        collect_all=collect_all,
        artifact_label="critique artifact",
        error_cls=ValidationError,
    )


def _make_run_hooks():
    """`(validate_factory, on_complete)` sharing this run's resolved probe scope.

    A pair rather than two independent hooks because the scope record must report
    the SAME probe resolution the artifacts were judged against; re-resolving it
    for the report would let the two disagree, which is exactly the shape of
    defect this surface exists to catch.
    """
    resolved: dict[str, object] = {}

    def validate_factory(run):
        return _validate_factory(run, resolved)

    def on_complete(run, artifacts) -> None:
        _scope.report_enforcement_scope(
            run, artifacts, resolved.get("cross_surface"), resolved.get("disagreements", [])
        )

    return validate_factory, on_complete


def _validate_factory(run, resolved: dict[str, object] | None = None):
    """Bind the per-run inputs the shared runner does not model itself.

    The cross-surface probe (which shells out to git) and the delegation-contract
    lookup (which reads AGENTS.md) are resolved ONCE per run, not once per
    artifact: a 100-artifact `--all` sweep would otherwise pay for both 100
    times. Neither reads the artifact, so hoisting cannot change a verdict.
    `require_tier_evidence` stays per artifact because it keys off whether THAT
    path was selected.
    """
    cross_surface = _scope.resolve_cross_surface_scope(
        run.repo_root,
        run.args.changed_ref,
        run.args.changed_path,
        probe_lib=_boundary_probe_lib,
        adapter_lib=_critique_adapter_lib,
        include_worktree=getattr(run.args, "include_worktree", False),
    )
    if resolved is not None:
        resolved["cross_surface"] = cross_surface
    repo_has_delegation = has_repo_delegation_contract(run.repo_root)
    require_tier_paths = set(run.selected_paths)

    def validate(artifact: Path) -> None:
        relpath = artifact.relative_to(run.repo_root).as_posix()
        pair = _scope.date_channel_disagreement(artifact, artifact.read_text(encoding="utf-8"))
        if pair is not None and resolved is not None:
            resolved.setdefault("disagreements", []).append(
                f"{artifact.name} (body {pair[0]} vs filename {pair[1]})"
            )
        validate_critique_artifact(
            artifact,
            repo_has_delegation_contract=repo_has_delegation,
            require_tier_evidence=run.explicit_paths or relpath in require_tier_paths,
            collect_all=run.collect_all,
            cross_surface_hit=cross_surface.overrides,
            check_current_binding=not run.args.all,
            repo_root=run.repo_root,
            evidence_mode=run.args.evidence_mode,
        )

    return validate


def _add_validator_args(parser) -> None:
    _scope.add_cross_surface_args(parser)
    parser.add_argument(
        "--evidence-led",
        dest="evidence_mode",
        action="store_true",
        help="Require and validate the typed evidence-led sections.",
    )


def main() -> int:
    validate_factory, on_complete = _make_run_hooks()
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked critique artifact.",
        artifact_label="critique artifact",
        changed_paths_fn=changed_paths,
        candidate_paths_fn=_critique_universe.candidate_paths,
        validate_factory=validate_factory,
        on_complete=on_complete,
        extra_args=_add_validator_args,
        fail_fast_help=(
            "Stop at the first rule violation instead of reporting every violation in one pass."
        ),
        owned_prefix=_critique_universe.prefix,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        raise SystemExit(report_validation_failure(str(exc), artifact_type="critique"))
