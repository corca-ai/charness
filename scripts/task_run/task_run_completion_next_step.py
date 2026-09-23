"""Render operator-facing next steps for completed task-run candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


def _candidate_location(
    payload: Mapping[str, object], resolved_target: Path, candidate: Mapping[str, object]
) -> str:
    if candidate.get("head_is_complete") and payload.get("target_branch") and payload.get("target_sha"):
        return f"on branch {payload['target_branch']} at {payload['target_sha']}"
    return f"in {resolved_target}"


def _next_step(
    payload: Mapping[str, object],
    *,
    resolved_target: Path,
    candidate: Mapping[str, object],
    execution_status: str,
    result_state: str,
    blockers: list[str],
) -> str:
    receipt_candidate = payload.get("candidate")
    if isinstance(receipt_candidate, Mapping):
        candidate = receipt_candidate
    receipt_execution = payload.get("execution")
    if isinstance(receipt_execution, Mapping) and isinstance(
        receipt_execution.get("status"), str
    ):
        execution_status = receipt_execution["status"]
    if isinstance(payload.get("status"), str):
        result_state = payload["status"]
    receipt_blockers = payload.get("blockers")
    if isinstance(receipt_blockers, list) and all(
        isinstance(item, str) for item in receipt_blockers
    ):
        blockers = receipt_blockers
    result_kind = payload.get("result_kind")
    if not isinstance(result_kind, str):
        from scripts.task_run.task_run_state import result_kind_for_status

        result_kind = result_kind_for_status(result_state).value
    approval = payload.get("approval_eligibility")
    if not isinstance(approval, str):
        approval = "eligible" if result_kind == "success" and not blockers else "ineligible"
    location = _candidate_location(payload, resolved_target, candidate)
    if execution_status == "interrupted" and (candidate.get("commit") or {}).get(
        "status"
    ) == "skipped":
        suffix = f"; {'; '.join(blockers)}." if blockers else "."
        return (
            f"No scoped changes were retained from the interrupted lane — it stopped "
            f"before its first edit, so there is no partial candidate to salvage; "
            f"clean up the retained worktree in {resolved_target} or retry with a "
            f"corrected scope"
            + suffix
        )
    if execution_status == "timed-out":
        suffix = f"; {'; '.join(blockers)}." if blockers else "."
        if (candidate.get("commit") or {}).get("status") != "committed":
            return (
                f"No scoped changes were retained from the timed-out lane — no WIP "
                f"candidate commit was created; inspect the retained worktree in "
                f"{resolved_target}"
                + suffix
            )
        return (
            f"Review the committed WIP candidate in {resolved_target}; "
            "interrupted mid-edit — state unknown; the commit is not a correctness claim"
            + suffix
        )
    if blockers:
        step = (
            f"Inspect the retained candidate {location}, typed result {result_kind}, "
            f"approval eligibility {approval}, and captured logs; "
            + "; ".join(blockers)
            + "."
        )
        persisted = candidate.get("persist")
        if isinstance(persisted, Mapping) and persisted.get("after_block"):
            correctness = persisted.get("correctness_verified") is True
            correctness_label = "verified" if correctness else "unverified"
            step += (
                " Candidate persisted for review: persistence="
                + str(persisted.get("status"))
                + f"; correctness {correctness_label} "
                + f"(correctness_verified={str(correctness).lower()}); "
                + f"approval_eligibility={approval}."
            )
        extension = payload.get("scope_extension_request")
        if isinstance(extension, dict) and extension.get("requested_paths"):
            step += (
                " The lane reported a scope mismatch naming "
                + ", ".join(str(path) for path in extension["requested_paths"])
                + ": approve or refuse that explicit addition, then re-validate "
                "the same candidate with the expanded scope instead of relaunching."
            )
        return step
    if result_state == "validated-partial-result":
        return (
            f"Review the validated candidate {location}; "
            "it is useful but not approval-eligible."
        )
    if result_state == "completed-needs-review":
        return (
            f"Merge or re-scope the finished candidate {location}; "
            f"review_required={payload.get('review_required', [])}; "
            f"approval_eligibility={approval}; relaunch would repeat finished work."
        )
    return (
        f"Review the candidate {location}; result_kind={result_kind}; "
        f"approval_eligibility={approval}; the typed result is approval-eligible."
    )
