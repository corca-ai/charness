"""Goal Run parent-body validation: metadata identity against the immutable binding.

Split from `issue_goal_run_binding.py` (#773 follow-up): the binding module owns
Work Item identity; this module owns what a parent body update may change.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_LOCAL_IMPORT = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))
_load_local = _LOCAL_IMPORT["sibling_loader"](__file__)
BINDING = _LOCAL_IMPORT["load_achieve"](
    "goal_binding", "issue_goal_run_parent_body_binding", caller_file=__file__
)
PICKUP = _LOCAL_IMPORT["load_achieve"](
    "goal_run_pickup_contract", "issue_goal_run_parent_body_pickup", caller_file=__file__
)
AMENDMENT = _load_local("issue_goal_run_parent_amendment", "issue_goal_run_parent_body_amendment")


def _parent_identity(repo: str, number: int) -> dict[str, Any]:
    return {
        "repo": repo,
        "number": number,
        "url": f"https://github.com/{repo}/issues/{number}",
    }


def validate_parent_metadata(
    metadata: dict[str, Any],
    binding: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    parent_url: str | None = None,
) -> dict[str, Any]:
    """Validate Goal Run metadata against one complete binding, not a Work Item."""
    try:
        PICKUP.validate_metadata(
            metadata,
            repo=repo,
            parent_number=parent_number,
            parent_url=parent_url or _parent_identity(repo, parent_number)["url"],
        )
    except PICKUP.PickupError as exc:
        raise RuntimeError(str(exc)) from exc
    if metadata["binding_schema"] != binding["kind"]:
        raise RuntimeError(
            "Goal Run metadata binding schema differs from the immutable Goal Binding"
        )
    if metadata["binding_sha256"] != binding["binding_sha256"]:
        raise RuntimeError("Goal Run metadata binding hash differs from the immutable Goal Binding")
    if metadata["draft_sha256"] != binding["draft_sha256"]:
        raise RuntimeError("Goal Run metadata draft hash differs from the immutable Goal Binding")
    if metadata["initial_graph_sha256"] != binding["approved_work_items_sha256"]:
        raise RuntimeError(
            "Goal Run metadata initial graph differs from the immutable Goal Binding"
        )
    if metadata["parent_identity"] != binding["parent"]:
        raise RuntimeError("Goal Run metadata parent differs from the immutable Goal Binding")
    return metadata


def validate_parent_body_update(
    current_body: str,
    desired_body: str,
    *,
    binding: dict[str, Any],
    repo: str,
    parent_number: int,
    parent_url: str | None,
    guard: Any,
    amendment_authorization_file: Path | None = None,
) -> None:
    AMENDMENT.validate_parent_body_update(
        current_body,
        desired_body,
        binding=binding,
        repo=repo,
        parent_number=parent_number,
        parent_url=parent_url,
        guard=guard,
        validate_parent_metadata=validate_parent_metadata,
        canonical_json_bytes=BINDING.canonical_json_bytes,
        amendment_authorization_file=amendment_authorization_file,
    )


def parent_body_validator(
    binding: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    guard: Any,
    amendment_authorization_file: Path | None = None,
) -> Any:
    def validate(current_body: str, desired_body: str) -> None:
        validate_parent_body_update(
            current_body,
            desired_body,
            binding=binding,
            repo=repo,
            parent_number=parent_number,
            parent_url=f"https://github.com/{repo}/issues/{parent_number}",
            guard=guard,
            amendment_authorization_file=amendment_authorization_file,
        )

    return validate
