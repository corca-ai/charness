from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    from scripts.core.subprocess_guard import run_process

_PROOF_MISMATCH = None


def _resolve_bootstrap() -> Path | None:
    """The nearest ``skill_runtime_bootstrap.py`` above this file, or ``None``."""
    return next(
        (
            a / "skill_runtime_bootstrap.py"
            for a in Path(__file__).resolve().parents
            if (a / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )


def _load_proof_mismatch():
    """Load the portable proof-mismatch floor (``scripts/evidence/proof_mismatch.py``) via
    the skill-runtime repo-module loader, so its ``from scripts.`` imports resolve
    in the issue skill context. Cached; reuses the same module the achieve closeout
    wires."""
    global _PROOF_MISMATCH
    if _PROOF_MISMATCH is None:
        bootstrap = _resolve_bootstrap()
        if bootstrap is None:
            raise ImportError("skill_runtime_bootstrap.py not found")
        runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
        _PROOF_MISMATCH = runtime.load_repo_module_from_skill_script(
            __file__, "scripts.evidence.proof_mismatch"
        )
    return _PROOF_MISMATCH


def sync_confirmation_line(result: dict[str, Any]) -> None:
    """Clear ``confirmation["line"]`` whenever the verdict is not ok.

    One direction only, deliberately: nothing in this repo flips ``ok`` back to True after
    the fact, and restoring a line would mean re-deriving the verb rule here, a second
    place for it to drift from the one in ``verify_closeout``. A future caller that does
    flip upward must render the line itself.

    Sweep row S23: the line is built inside ``verify_closeout`` with an ``if ok`` guard,
    and the proof-mismatch fold runs AFTER, flipping ``ok`` to False and ``status`` to
    ``failed`` without touching it. The result then carried
    ``ok: False, status: failed`` alongside
    ``confirmation.line: "carrier-checked: ... (carrier-checks-only)"`` — a rendered
    confirmation over a refused verdict, which is what downstream handoffs quote.

    Making it a function rather than one more line inside the fold is deliberate: the
    defect is that a post-hoc verdict flip and the sentence describing that verdict were
    maintained in two places. Any future fold calls this and the invariant holds.
    """
    confirmation = result.get("confirmation")
    if not isinstance(confirmation, dict):
        return
    if result.get("ok"):
        return
    confirmation["line"] = None


def _fold_proof_mismatch(result: dict[str, Any], repo_root: Path, body: str) -> None:
    """Fold the portable proof-mismatch floor into a verify_closeout result: a
    ``## Proof Ledger`` gap left undispositioned flips ``ok`` False and ``status``
    to ``failed``. Inert when the body declares no proof ledger (no over-fire), so
    both validate-closeout-draft (which reuses this) and post-publication
    verify-closeout enforce it identically."""
    _load_proof_mismatch().apply_proof_mismatch_floor(result, repo_root, body)
    if result.get("proof_mismatch"):
        result["status"] = "failed"
    sync_confirmation_line(result)


_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
ISSUE_CLOSE = _load_local("issue_close", "issue_verify_issue_close")
_BODY = _load_local("issue_verify_closeout_body")
_CLASSIFICATION = _load_local("issue_closeout_classification_ledger")
# The rung-1 floors moved to their own module when the body reader hit its length
# gate; the seam is real (what a body MUST CARRY vs how a field is read out of it).
_FLOORS = _load_local("issue_closeout_rung1_floors")
_CRITIQUE = _load_local("issue_resolution_critique", "issue_resolution_critique")
# The identity parse lives in the backend owner, not here: which repository a payload says it
# describes is the same question the handoff staleness reader asks, and a second copy of it is
# the defect the backend consolidation removed.
_ISSUE_BACKEND = _load_local("issue_backend", "issue_verify_issue_backend")
_ANSWER_REPO = _ISSUE_BACKEND.answer_repo
_ISSUE_IDENTITY_MISMATCHES = _ISSUE_BACKEND.issue_identity_mismatches
GIT_TIMEOUT_SECONDS = 10
_CARRIER = _load_local("issue_verify_closeout_carrier")
_AUTHORIZATION = _load_local("issue_verify_closeout_authorization")

CARRIERS = _CARRIER.CARRIERS
CLASSIFICATIONS = _CLASSIFICATION.KNOWN_CLASSIFICATIONS
MANUAL_FALLBACK_REASONS = _CARRIER.MANUAL_FALLBACK_REASONS

_body_fields = _BODY._body_fields
_first_field = _BODY._first_field
_has_substantive_value = _BODY._has_substantive_value
_missing_ledger_fields = _BODY._missing_ledger_fields
_ledger_counts = _load_local("issue_closeout_ledger_counts")
_consolidated = _load_local("issue_consolidated_closeout")
_consolidation_readback = _load_local("issue_consolidation_readback")
# The backend state read moved to its own module: two consumers need it and this
# file was at its length ceiling, which a proof surface should not spend on a
# subprocess wrapper.
_view_issue_state = _load_local("issue_state_readback").view_issue_state
_missing_close_keywords = _BODY._missing_close_keywords
iter_close_keyword_refs = _BODY.iter_close_keyword_refs
evaluate_source_preservation = _FLOORS.evaluate_source_preservation
evaluate_behavioral_verdict = _FLOORS.evaluate_behavioral_verdict
evaluate_hotl_dispositions = _FLOORS.evaluate_hotl_dispositions
evaluate_ai_provenance = _FLOORS.evaluate_ai_provenance
FLOOR_EXEMPT_CLASSIFICATIONS = _FLOORS.FLOOR_EXEMPT_CLASSIFICATIONS
review_advisory_for_classification = _FLOORS.review_advisory_for_classification
strip_code_fences = _BODY._strip_code_fences
resolve_classifications = _CLASSIFICATION.resolve_classifications


def _resolve_closeout_classifications(body, numbers, classification, supplied=None):
    return _CLASSIFICATION.resolve_closeout_classifications(
        body, numbers, classification, supplied, strip_fences=strip_code_fences,
    )


def resolve_closeout_invocation(body, artifacts, bare_numbers):
    return _CLASSIFICATION.resolve_closeout_invocation(
        body, artifacts, bare_numbers, strip_fences=strip_code_fences,
    )


def _read_carrier_body(
    repo_root: Path, *, carrier: str, commit_ref: str | None, body_file: Path | None
) -> str:
    return _CARRIER.read_carrier_body(
        repo_root,
        carrier=carrier,
        commit_ref=commit_ref,
        body_file=body_file,
        run_process=run_process,
        timeout_seconds=GIT_TIMEOUT_SECONDS,
    )


_manual_comment_found = _CARRIER.manual_comment_found


_validate_verify_inputs = _CARRIER.validate_verify_inputs


def _authorization_record(
    repo_root: Path, repo: str, numbers: list[int], carrier: str
) -> dict[str, Any]:
    return _AUTHORIZATION.authorization_record(
        repo_root,
        repo,
        numbers,
        carrier,
        bootstrap=_resolve_bootstrap(),
        caller_file=__file__,
    )


def _ledger_field_reasons(body: str, missing_fields: list[str]) -> list[str]:
    """`<finding id>: <reason>` for each finding whose owner can explain itself."""
    siblings = _BODY._first_field(_body_fields(body), ("siblings", "sibling search"))
    reasons = []
    for finding_id in missing_fields:
        reason = _ledger_counts.rule_reason(siblings, finding_id.rsplit(":", 1)[-1])
        if reason:
            reasons.append(f"{finding_id}: {reason}")
    return reasons


def verify_closeout(
    *,
    repo_root: Path,
    repo: str,
    numbers: list[int],
    carrier: str,
    backend: dict[str, Any],
    classification: str | None = None,
    classifications: dict[int, str] | None = None,
    commit_ref: str | None = None,
    body_file: Path | None = None,
    manual_fallback_reason: str | None = None,
    expect_state: str | None = None,
) -> dict[str, Any]:
    _validate_verify_inputs(
        numbers=numbers,
        classification=classification,
        carrier=carrier,
        manual_fallback_reason=manual_fallback_reason,
        expect_state=expect_state,
    )
    body = _read_carrier_body(
        repo_root, carrier=carrier, commit_ref=commit_ref, body_file=body_file
    )
    resolved_classifications = _resolve_closeout_classifications(
        body, numbers, classification, classifications
    )
    groups: dict[str, list[int]] = {}
    for number in numbers:
        groups.setdefault(resolved_classifications[number], []).append(number)
    # Citation scope is the complete invocation; only the bug group is required
    # to have a resolution critique. This prevents a bundled bug+feature carrier
    # from satisfying the bug obligation with a citation that names only the
    # feature issue.
    bug_numbers = [number for number in numbers if resolved_classifications[number] == "bug"]
    resolution_critique_check = _CRITIQUE.check_resolution_critique(
        repo_root=repo_root,
        body=body,
        classification="bug" if bug_numbers else next(iter(resolved_classifications.values())),
        numbers=numbers,
        repository=repo,
        required_numbers=bug_numbers,
    )
    missing_close_keywords = (
        [] if carrier == "manual-fallback" else _missing_close_keywords(body, numbers, repo)
    )
    source_preservation = evaluate_source_preservation(body)
    missing_fields: list[str] = []
    classification_reports: dict[str, dict[str, Any]] = {}
    consolidation_readback: list[dict[str, Any]] = []
    behavioral_groups: list[dict[str, Any]] = []
    hotl_groups: list[dict[str, Any]] = []
    provenance_groups: list[dict[str, Any]] = []
    for group, group_numbers in groups.items():
        group_missing = _missing_ledger_fields(
            body, group, carrier=carrier, invoked_numbers=tuple(group_numbers)
        )
        # Prefix findings in a mixed bundle so the operator can identify the
        # failing issue; preserve the historical ids for homogeneous calls.
        missing_fields.extend(
            group_missing
            if len(groups) == 1
            else [f"#{number}:{field}" for number in group_numbers for field in group_missing]
        )
        behavioral = evaluate_behavioral_verdict(body, group, group_numbers, invocation_numbers=numbers)
        hotl = evaluate_hotl_dispositions(body, group, group_numbers, invocation_numbers=numbers)
        provenance = evaluate_ai_provenance(body, group)
        behavioral_groups.append(behavioral)
        hotl_groups.append(hotl)
        provenance_groups.append(provenance)
        group_readback = _consolidation_readback.readbacks_for_closeout(
            numbers=group_numbers,
            destinations=_consolidated.destinations("\n".join(strip_code_fences(body))),
            fetch=lambda dest: _view_issue_state(
                repo_root, repo=repo, number=dest, backend=backend,
                json_fields="number,state,url,body",
            ),
            applies=group == _consolidated.CLASSIFICATION,
            expected_repo=repo,
            answer_repo=_ANSWER_REPO,
        )
        consolidation_readback.extend(group_readback)
        for readback in group_readback:
            missing_fields.extend(
                f"consolidation:{problem}" for problem in readback["problems_to_surface"]
            )
        classification_reports[group] = {
            "numbers": group_numbers,
            "missing_fields": group_missing,
            "behavioral_verdict": behavioral,
            "hotl_dispositions": hotl,
            "ai_provenance": provenance,
            "consolidation_readback": group_readback,
        }
    homogeneous = len(groups) == 1
    effective_classification = next(iter(groups)) if homogeneous else None
    behavioral_verdict = behavioral_groups[0] if homogeneous else {
        "ok": all(item.get("ok", False) for item in behavioral_groups),
        "groups": behavioral_groups,
    }
    hotl_disposition = hotl_groups[0] if homogeneous else {
        "ok": all(item.get("ok", False) for item in hotl_groups),
        "groups": hotl_groups,
    }
    ai_provenance = provenance_groups[0] if homogeneous else {
        "ok": all(item.get("ok", False) for item in provenance_groups),
        "groups": provenance_groups,
    }

    verified_state: list[dict[str, Any]] = []
    state_mismatches: list[dict[str, Any]] = []
    manual_comment_missing: list[int] = []
    if expect_state is not None:
        expected = expect_state.upper()
        for number in numbers:
            json_fields = (
                "number,state,url,comments" if carrier == "manual-fallback" else "number,state,url"
            )
            state_payload = _view_issue_state(
                repo_root, repo=repo, number=number, backend=backend, json_fields=json_fields
            )
            verified_state.append(state_payload)

            # Three facts are checked against one answer -- the issue's number, the issue's
            # REPOSITORY, and its state -- and each records the same mismatch shape. Built by
            # one helper rather than three literal dicts: the duplicate ratchet caught the
            # third copy the moment it was added, and it was right, because a field added to
            # two of three records is exactly how a mismatch report starts lying.
            def mismatch(*, expected_value, actual_value, field=None):
                record = {
                    "number": number,
                    "expected": expected_value,
                    "actual": actual_value,
                    "url": state_payload.get("url"),
                }
                if field is not None:
                    record["field"] = field
                state_mismatches.append(record)

            for identity_mismatch in _ISSUE_IDENTITY_MISMATCHES(
                state_payload, expected_repo=repo, expected_number=number
            ):
                mismatch(
                    expected_value=identity_mismatch["expected"],
                    actual_value=identity_mismatch["actual"],
                    field=identity_mismatch["field"],
                )
            actual = str(state_payload.get("state", "")).upper()
            if actual != expected:
                mismatch(expected_value=expected, actual_value=state_payload.get("state"))
            if carrier == "manual-fallback" and not _manual_comment_found(body, state_payload):
                manual_comment_missing.append(number)

    critique_ok = resolution_critique_check.get("ok", True)
    ok = (
        critique_ok
        and not missing_close_keywords
        and not missing_fields
        and not state_mismatches
        and not manual_comment_missing
        and not source_preservation["missing"]
        and behavioral_verdict["ok"]
        and hotl_disposition["ok"]
        and ai_provenance["ok"]
    )
    status = (
        "verified" if ok and expect_state is not None else "carrier_verified" if ok else "failed"
    )
    # Additive migration: the bare status tokens sound terminal,
    # but each is only this observer's checks passing over its channel.
    # `confirmation` names observer/channel/scope so downstream handoffs render
    # `confirmed: <observer> via <channel> (<scope>)` instead of re-claiming a
    # bare `verified` as an endpoint. Status tokens stay unchanged for existing
    # consumers; artifacts that recorded bare statuses are grandfathered.
    observer = f"issue_verify_closeout@{backend.get('id', 'gh')}"
    channel = "backend-state-readback" if expect_state is not None else "carrier-body-checks"
    scope = "state-and-carrier-checks-only" if expect_state is not None else "carrier-checks-only"
    # The verb tracks the scope so a pre-publication pass never renders the
    # stronger claim: `confirmed` only for the final state-checked verdict.
    verb = "confirmed" if expect_state is not None else "carrier-checked"
    confirmation = {
        "observer": observer,
        "channel": channel,
        "scope": scope,
        "line": f"{verb}: {observer} via {channel} ({scope})" if ok else None,
    }
    # Surfaced at the top level, not only three levels down under
    # `resolution_critique_check`, and on the same key `close-with-comment` and
    # the commit-msg carrier already use. A skipped fresh-eye critique produces a
    # top-level verdict byte-identical to an executed one (`ok: True`,
    # `status: carrier_verified`), so burying the one line that says otherwise
    # made this carrier the quiet path (B2).
    # Only the critique-skip advisory: the classification-exemption advisory is
    # already owned and surfaced by each carrier (`issue_close.py`, the commit-msg
    # hook), and duplicating it here would double-report it.
    review_advisory = list(resolution_critique_check.get("review_advisory", []))
    # Its OWN key, not appended to `review_advisory`. That list is documented three lines
    # up as carrying the critique-skip advisory ONLY, and widening it would both break the
    # contract its own tests assert and bury the critique line this carrier exists to keep
    # visible -- which is the exact defect (B2) the comment above records paying for.
    result = {
        "ok": ok,
        "status": status,
        "confirmation": confirmation,
        "review_advisory": review_advisory,
        "repo": repo,
        "numbers": numbers,
        "classification": effective_classification,
        "classifications": resolved_classifications,
        "carrier": carrier,
        "commit_ref": commit_ref,
        "body_file": str(body_file) if body_file is not None else None,
        "manual_fallback_reason": manual_fallback_reason,
        "expect_state": expect_state,
        "missing_close_keywords": missing_close_keywords,
        "missing_fields": missing_fields,
        # The author-facing REASON behind each shape finding, not only its id.
        # The library builds a full diagnosis and the blocking commit-msg carrier
        # had nothing to print; round-1 review found an author stopped at the
        # pre-commit boundary got one unexplained snake_case token.
        "missing_field_reasons": _ledger_field_reasons(body, missing_fields),
        # What the parser actually SAW, emitted only when a field is missing. A
        # bare `missing_fields: ["prevention"]` is unexplainable to an author
        # looking at a body whose `Prevention:` line is right there: the value
        # was swallowed by, or split off into, a neighbouring line. Naming the
        # parsed keys turns that into a one-read diagnosis instead of a refusal
        # the operator can only work around by rewriting the evidence prose.
        "parsed_ledger_fields": sorted(_body_fields(body)) if missing_fields else [],
        "state_mismatches": state_mismatches,
        "manual_comment_missing": manual_comment_missing,
        "resolution_critique_check": resolution_critique_check,
        "source_preservation": source_preservation,
        "behavioral_verdict": behavioral_verdict,
        "hotl_dispositions": hotl_disposition,
        "ai_provenance": ai_provenance,
        "verified_state": verified_state,
        # Empty for every other classification. Present and per (source, destination)
        # for `consolidated`, so an operator can see WHICH of the four tracker facts
        # was checked and what it found, rather than a bare pass.
        "consolidation_readback": consolidation_readback,
        "classification_reports": classification_reports,
    }
    _fold_proof_mismatch(result, repo_root, body)
    result["closeout_authorization"] = _authorization_record(repo_root, repo, numbers, carrier)
    return result
