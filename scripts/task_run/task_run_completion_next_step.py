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
        return (
            f"Inspect the retained candidate {location}, typed result, and captured logs; "
            + "; ".join(blockers)
            + "."
        )
    if result_state == "validated-partial-result":
        return (
            f"Review the validated candidate {location}; "
            "it is useful but not approval-eligible."
        )
    if result_state == "completed-needs-review":
        return (
            f"Merge or re-scope the finished candidate {location}; the agent "
            "completed its work but a gate needs review, so relaunching would "
            "repeat finished work."
        )
    return f"Review the candidate {location}; the typed result is approval-eligible."
