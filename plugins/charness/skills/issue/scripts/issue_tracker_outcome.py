"""Typed outcomes for provider mutations whose final state is unresolved."""

from __future__ import annotations

from typing import Any


def unverified_mutation(
    operation: str,
    *,
    repo: str,
    parent_number: int,
    error: str,
    before: dict[str, Any] | None = None,
    sub_issue_number: int | None = None,
    exit_code: int | None = None,
    work_item_key: str | None = None,
    unresolved_targets: list[dict[str, Any]] | None = None,
    provider_return: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "status": "unverified-write",
        "outcome": "unverified-write",
        "operation": operation,
        "mutation_invoked": True,
        "repo": repo,
        "parent_number": parent_number,
        "error": error,
        "next_action": "stop-and-read-current-provider-state",
    }
    if before is not None:
        result["before"] = before
    if sub_issue_number is not None:
        result["sub_issue_number"] = sub_issue_number
    if exit_code is not None:
        result["provider_exit_code"] = exit_code
    if work_item_key is not None:
        result["work_item_key"] = work_item_key
    if unresolved_targets is not None:
        result["unresolved_targets"] = unresolved_targets
    if provider_return is not None:
        result["provider_return"] = provider_return
    return result
