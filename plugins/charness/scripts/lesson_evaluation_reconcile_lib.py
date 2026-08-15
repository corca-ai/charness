"""Reconcile authored retro dispositions against the ledger they claim.

SPLIT FROM `lesson_evaluation_continuity_lib` (S3, 2026-08-15) because the two
halves answer different questions and the file had reached its length bar with
the #631 repair still to land. The other half owns AUTHORING and INTEGRITY -- the
disposition grammar, the emission receipt, the frozen session bundle. This half
owns AGREEMENT: given those records, does what a retro CLAIMS match what the
ledger HOLDS. Nothing here reads or writes a file.

`violation` stays in the other half: the receipt collector raises it too, and a
reconciler that owned the row shape would make the collector import agreement
logic to report an unreadable file.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable

from scripts import lesson_score_outcome_lib as outcome_lib
from scripts.lesson_evaluation_continuity_lib import (
    ACTIVATION_DATE,
    AGGREGATE_VIOLATION_IDS,
    REASONS,
    STATUSES,
    violation,
)
from scripts.lesson_ledger_lib import RESERVED_SESSION_ID


def _reconcile_retro_row(
    *,
    path: str,
    disposition: dict[str, Any],
    sessions: dict[str, dict[str, Any]],
    score_events: list[dict[str, Any]],
    receipts: dict[str, dict[str, Any]],
    recurrence_sources: dict[str, set[str]],
) -> list[dict[str, str]]:
    status = disposition["status"]
    session_id = disposition["session_id"]
    if session_id not in sessions:
        return [
            violation(
                "foreign-session",
                path=path,
                session_id=session_id,
                detail="disposition names no ledger session",
            )
        ]
    # OWNERSHIP, not string equality (#631). Which scores this disposition speaks
    # for depends on which citation contract each event was written under, and
    # `outcome_lib` owns that distinction -- reading legacy events under the
    # outcome rule is what made a two-origin session unclearable by any retro.
    matching = outcome_lib.scores_owned_by(score_events, session_id=session_id, path=path)
    foreign = outcome_lib.foreign_scores(score_events, session_id=session_id, path=path)
    session_scores = [event for event in score_events if event.get("session_id") == session_id]
    has_receipt = session_id in receipts
    rows: list[dict[str, str]] = []
    if len(matching) != disposition["score_event_count"]:
        rows.append(
            violation(
                "score-count-mismatch",
                path=path,
                session_id=session_id,
                detail=f"declared {disposition['score_event_count']}, observed {len(matching)}",
            )
        )
    if foreign:
        rows.append(
            violation(
                "foreign-score-source",
                path=path,
                session_id=session_id,
                detail=f"session has {len(foreign)} encounter score(s) citing another retro path",
            )
        )
    for identifier, detail in outcome_lib.binding_violations(
        score_events, session_id=session_id, path=path, recurrence_sources=recurrence_sources
    ):
        rows.append(violation(identifier, path=path, session_id=session_id, detail=detail))
    if status in {"effect-recorded", "no-effect"} and not has_receipt:
        rows.append(
            violation(
                "emission-unproven",
                path=path,
                session_id=session_id,
                detail=f"{status} requires a valid emission receipt",
            )
        )
    if status == "effect-recorded" and not matching:
        rows.append(
            violation(
                "effect-recorded-without-score",
                path=path,
                session_id=session_id,
                detail="effect-recorded requires at least one matching score",
            )
        )
    if status == "no-effect" and matching:
        rows.append(
            violation(
                "no-effect-with-score",
                path=path,
                session_id=session_id,
                detail="no-effect requires zero matching scores",
            )
        )
    reason = disposition.get("reason")
    if status == "not-evaluated" and reason == "emission-unproven" and has_receipt:
        rows.append(
            violation(
                "unexpected-emission-proof",
                path=path,
                session_id=session_id,
                detail="emission-unproven cannot cite a valid receipt",
            )
        )
    if status == "not-evaluated" and reason == "presentation-unproven" and not has_receipt:
        rows.append(
            violation(
                "emission-unproven",
                path=path,
                session_id=session_id,
                detail="presentation-unproven requires a valid emission receipt",
            )
        )
    if not has_receipt and session_scores:
        rows.append(
            violation(
                "score-without-emission-proof",
                path=path,
                session_id=session_id,
                detail="receiptless session has score events",
            )
        )
    return rows


def receipt_emitted_date(receipt: dict[str, Any]) -> date:
    return datetime.fromisoformat(receipt["emitted_at"].replace("Z", "+00:00")).date()


def unclaimed_receipted_sessions(
    *, receipts: dict[str, dict[str, Any]], references: dict[str, list[str]],
    since: date = ACTIVATION_DATE, before: date | None = None,
) -> list[str]:
    """Receipted sessions in the cohort that no retro disposition claims.

    ONE membership rule read two opposite ways: ``reconcile_records`` passes
    ``before=as_of`` and raises ``unclaimed-emission``; the retro run planner
    passes ``before=None`` and routes the author to the session that still owes a
    score (rationale at ``lesson_evaluation_records_lib.lesson_session_routing``).
    A second spelling would let the router skip a session the gate fails over.
    """
    end = before if before is not None else date.max
    return sorted(
        key for key, receipt in receipts.items()
        if key not in references and since <= receipt_emitted_date(receipt) < end
    )


def _is_missing_start(disposition: dict[str, Any]) -> bool:
    """The one disposition entitled to spell the reserved sentinel."""
    return (
        disposition["status"] == "not-evaluated"
        and disposition.get("reason") == "missing-start"
    )


def reconcile_records(
    *,
    retros: Iterable[tuple[str, dict[str, Any]]],
    sessions: dict[str, dict[str, Any]],
    score_events: list[dict[str, Any]],
    receipts: dict[str, dict[str, Any]],
    receipt_violations: list[dict[str, str]],
    as_of: date,
    # `lesson_id -> retros carrying its `recurrence-class:` bullet`. Required
    # rather than defaulted: a default of `{}` would make every `not-consulted`
    # precondition fire, and a default of "skip the check" would make it silently
    # inert -- the failure mode the repo has already recorded as a green verdict
    # over a loop that never closed.
    recurrence_sources: dict[str, set[str]],
) -> dict[str, Any]:
    """Pure reconciliation core used by the CLI and seeded matrix tests."""
    retro_rows = list(retros)
    violations = list(receipt_violations)
    references: dict[str, list[str]] = {}
    status_counts = {status: 0 for status in sorted(STATUSES)}
    total_scores = len(score_events)

    for path, disposition in retro_rows:
        status = disposition["status"]
        session_id = disposition["session_id"]
        if session_id == RESERVED_SESSION_ID and not _is_missing_start(disposition):
            # A disposition claiming the reserved sentinel under any other status
            # is VOID, so it is refused before it is counted. #633 names three
            # harms -- the row "parses, increments `completed_evaluation_count`,
            # and skips every reconciler check" -- and the first version of this
            # repair fixed only the third: the increment sat above this guard, so
            # an `effect-recorded` row claiming seven scores against `none` still
            # raised the very metric the surface exists to protect, while a
            # comment here narrated it as repaired. A round-1 reviewer caught
            # that. Counting a void row by the status it falsely claims is how a
            # green-looking number survives a red verdict.
            violations.append(
                violation(
                    "reserved-session-id",
                    path=path,
                    session_id=session_id,
                    detail=(
                        f"status `{status}` cannot claim the reserved session_id "
                        f"`{RESERVED_SESSION_ID}`; only `not-evaluated`/`missing-start` may"
                    ),
                )
            )
            continue
        status_counts[status] += 1
        if session_id == RESERVED_SESSION_ID:
            # The one disposition entitled to the sentinel. It counts (it is a
            # real `not-evaluated`/`missing-start` claim) and it skips
            # reconciliation, because there is no session to reconcile against.
            # The skip is re-derived here rather than trusted from the parser:
            # `reconcile_records` is a PURE core that the seeded matrix tests and
            # any future caller reach without going through `parse_disposition`,
            # and a skip that trusts an upstream check is not a check.
            continue
        references.setdefault(session_id, []).append(path)
        violations.extend(
            _reconcile_retro_row(
                path=path,
                disposition=disposition,
                sessions=sessions,
                score_events=score_events,
                receipts=receipts,
                recurrence_sources=recurrence_sources,
            )
        )

    for session_id, paths in references.items():
        if len(paths) > 1:
            violations.append(violation("duplicate-session-reference", session_id=session_id, detail=f"session is cited by {len(paths)} retros: {', '.join(sorted(paths))}"))
    for session_id in unclaimed_receipted_sessions(
        receipts=receipts, references=references, before=as_of
    ):
        emitted = receipt_emitted_date(receipts[session_id])
        violations.append(violation("unclaimed-emission", session_id=session_id, detail=f"receipt from {emitted.isoformat()} has no in-cohort retro disposition"))

    completed = status_counts["effect-recorded"] + status_counts["no-effect"]
    aggregate_violation_counts = {
        identifier: sum(item["id"] == identifier for item in violations)
        for identifier in AGGREGATE_VIOLATION_IDS
    }
    not_evaluated_reasons = {reason: 0 for reason in sorted(REASONS)}
    for _, disposition in retro_rows:
        # Same exclusion as `status_counts` above, for the same reason: a
        # `not-evaluated`/`presentation-unproven` row claiming the reserved
        # sentinel is void, and counting its reason would put a void claim into a
        # published tally beside a red verdict.
        if disposition["session_id"] == RESERVED_SESSION_ID and not _is_missing_start(disposition):
            continue
        if disposition["status"] == "not-evaluated":
            not_evaluated_reasons[disposition["reason"]] += 1
    return {
        "kind": "charness.lesson-evaluation-continuity-report",
        "schema_version": 1,
        "activation_date": ACTIVATION_DATE.isoformat(),
        "as_of": as_of.isoformat(),
        "denominator_label": "eligible durable retros",
        "eligible_retro_count": len(retro_rows),
        "disposition_count": len(retro_rows),
        "completed_evaluation_count": completed,
        "status_counts": status_counts,
        "not_evaluated_reason_counts": not_evaluated_reasons,
        "score_event_count": total_scores,
        "aggregate_violation_counts": aggregate_violation_counts,
        "violation_count": len(violations),
        "violations": sorted(violations, key=lambda item: (item["id"], item.get("path", ""), item.get("session_id", ""))),
        "ok": not violations,
    }
