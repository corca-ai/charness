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


def _abnormal_next_step(
    *,
    resolved_target: Path,
    candidate: Mapping[str, object],
    execution_status: str,
    result_kind: str,
    approval: str,
    location: str,
) -> str | None:
    candidate_state = candidate.get("state")
    state_known = candidate.get("state_known")
    if (
        execution_status == "interrupted"
        and candidate_state == "interrupted-before-edit"
        and state_known
    ):
        return (
            f"Inspect the retained worktree in {resolved_target}; "
            f"candidate_state={candidate_state}; state_known=true; "
            f"result_kind={result_kind}; approval_eligibility={approval}. "
            "Clean up the retained worktree if needed, or retry with a corrected scope."
        )
    if execution_status == "interrupted" and candidate_state is None:
        return (
            f"Inspect or clean up the retained worktree in {resolved_target}; "
            f"result_kind={result_kind}; approval_eligibility={approval}. "
            "Retry with a corrected scope if needed."
        )
    if execution_status != "timed-out":
        return None

    commit = candidate.get("commit")
    if isinstance(commit, Mapping) and commit.get("status") == "committed":
        correctness = commit.get("correctness_verified")
        state_text = (
            "interrupted mid-edit — state unknown"
            if candidate_state == "interrupted-mid-edit" and state_known is False
            else f"candidate_state={candidate_state}; state_known={str(state_known).lower()}"
        )
        correctness_text = (
            "; the commit is not a correctness claim" if correctness is False else ""
        )
        return (
            f"Inspect the committed WIP candidate {location}; "
            f"{state_text}; correctness_verified={str(correctness).lower()}; "
            f"result_kind={result_kind}; approval_eligibility={approval}"
            f"{correctness_text}."
        )
    if isinstance(commit, Mapping) and commit.get("status") == "skipped":
        return (
            f"Inspect the retained worktree in {resolved_target}; "
            "no WIP candidate commit was created "
            f"(candidate_commit_status={commit.get('status')}); "
            f"candidate_state={candidate_state}; state_known={str(state_known).lower()}; "
            f"result_kind={result_kind}; approval_eligibility={approval}."
        )
    return (
        f"Inspect the retained worktree in {resolved_target}; "
        f"candidate_state={candidate_state}; state_known={str(state_known).lower()}; "
        f"result_kind={result_kind}; approval_eligibility={approval}."
    )


def _blocked_next_step(
    payload: Mapping[str, object],
    *,
    location: str,
    candidate: Mapping[str, object],
    blockers: list[str],
    result_kind: str,
    approval: str,
) -> str:
    step = (
        f"Inspect the retained candidate {location} and captured logs; "
        + "; ".join(blockers)
        + f". result_kind={result_kind}; approval_eligibility={approval}."
    )
    persisted = candidate.get("persist")
    if isinstance(persisted, Mapping) and persisted.get("after_block"):
        correctness = persisted.get("correctness_verified")
        correctness_text = (
            "correctness verified"
            if correctness is True
            else "correctness unverified"
            if correctness is False
            else "correctness status unrecorded"
        )
        step += (
            " Candidate persisted for review: persistence="
            + str(persisted.get("status"))
            + f"; {correctness_text} "
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
        result_kind = "unrecorded"
    approval = payload.get("approval_eligibility")
    if not isinstance(approval, str):
        approval = "unrecorded"
    location = _candidate_location(payload, resolved_target, candidate)
    abnormal_step = _abnormal_next_step(
        resolved_target=resolved_target,
        candidate=candidate,
        execution_status=execution_status,
        result_kind=result_kind,
        approval=approval,
        location=location,
    )
    if abnormal_step is not None:
        return abnormal_step
    if blockers:
        return _blocked_next_step(
            payload,
            location=location,
            candidate=candidate,
            blockers=blockers,
            result_kind=result_kind,
            approval=approval,
        )
    if result_state == "validated-partial-result":
        return (
            f"Review the candidate {location}; candidate_useful="
            f"{str(candidate.get('useful') is True).lower()}; "
            f"result_kind={result_kind}; approval_eligibility={approval}."
        )
    if result_state == "completed-needs-review":
        return (
            f"Review or re-scope the candidate {location}; "
            f"review_required={payload.get('review_required', [])}; "
            f"result_kind={result_kind}; approval_eligibility={approval}; "
            f"status={result_state}; relaunch would repeat finished work."
        )
    suffix = "; the typed result is approval-eligible." if approval == "eligible" else "."
    return (
        f"Review the candidate {location}; result_kind={result_kind}; "
        f"approval_eligibility={approval}" + suffix
    )
