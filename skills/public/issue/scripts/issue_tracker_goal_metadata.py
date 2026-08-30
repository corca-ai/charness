"""Validation and preservation rules for Goal Run metadata in issue bodies."""

from __future__ import annotations

import json
import re
from typing import Any

GOAL_RUN_MARKER_RE = re.compile(r"<!--\s*charness-goal-run:(?P<version>[^\s]+)")
GOAL_RUN_BLOCK_RE = re.compile(
    r"<!-- charness-goal-run:v1\s*\n(?P<payload>\{.*?\})\s*\n-->", re.DOTALL
)
GOAL_RUN_IMMUTABLE_FIELDS = (
    "binding_schema",
    "binding_path",
    "binding_sha256",
    "draft_path",
    "draft_sha256",
    "initial_graph_sha256",
    "parent_identity",
)
GOAL_RUN_TERMINAL_FIELDS = (
    "terminal_observation_path",
    "terminal_observation_sha256",
)


def goal_run_block(body: str, *, context: str) -> dict[str, Any] | None:
    markers = list(GOAL_RUN_MARKER_RE.finditer(body))
    matches = list(GOAL_RUN_BLOCK_RE.finditer(body))
    if not markers:
        return None
    versions = [match.group("version") for match in markers]
    unsupported = sorted(set(versions) - {"v1"})
    if unsupported:
        raise RuntimeError(
            f"{context} has unsupported Goal Run metadata version(s): {unsupported!r}"
        )
    if len(markers) != 1 or len(matches) != 1:
        raise RuntimeError(f"{context} has duplicate or malformed Goal Run metadata")
    try:
        payload = json.loads(matches[0].group("payload"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{context} Goal Run metadata is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{context} Goal Run metadata must be a JSON object")
    return payload


def guard_goal_run_metadata(
    current_body: str,
    desired_body: str,
    *,
    terminal_metadata_update: bool = False,
    allow_human_amendment: bool = False,
) -> None:
    """Enforce metadata identity while preserving human Markdown by default."""
    current = goal_run_block(current_body, context="current body")
    desired = goal_run_block(desired_body, context="desired body")
    if current is not None and desired is None:
        raise RuntimeError("tracker update refused to strip Goal Run metadata")
    if current is None:
        if desired is None:
            return
        if allow_human_amendment:
            return
        desired_matches = list(GOAL_RUN_BLOCK_RE.finditer(desired_body))
        if len(desired_matches) != 1:
            raise RuntimeError("desired Goal Run metadata must have one replaceable block")
        desired_match = desired_matches[0]
        if desired_body[: desired_match.start()] != current_body or desired_body[
            desired_match.end() :
        ] not in {"", "\n"}:
            raise RuntimeError(
                "tracker update refused to replace the live human-readable body during metadata bootstrap"
            )
        return
    if desired is None:
        return
    changed = [
        field for field in GOAL_RUN_IMMUTABLE_FIELDS if current.get(field) != desired.get(field)
    ]
    if changed:
        raise RuntimeError(
            f"tracker update refused to alter immutable Goal Run identity fields: {changed!r}"
        )
    missing = object()
    terminal_changed = [
        field
        for field in GOAL_RUN_TERMINAL_FIELDS
        if current.get(field, missing) != desired.get(field, missing)
    ]
    if terminal_changed and not terminal_metadata_update:
        raise RuntimeError(
            "tracker update refused to alter terminal Goal Run metadata outside the "
            f"dedicated close ingress: {terminal_changed!r}"
        )
    if allow_human_amendment:
        return
    current_matches = list(GOAL_RUN_BLOCK_RE.finditer(current_body))
    desired_matches = list(GOAL_RUN_BLOCK_RE.finditer(desired_body))
    if len(current_matches) != 1 or len(desired_matches) != 1:
        raise RuntimeError("Goal Run metadata must have one replaceable block")
    current_match = current_matches[0]
    desired_match = desired_matches[0]
    if (
        current_body[: current_match.start()],
        current_body[current_match.end() :],
    ) != (
        desired_body[: desired_match.start()],
        desired_body[desired_match.end() :],
    ):
        raise RuntimeError(
            "tracker update refused to amend human-readable Goal Run Markdown; "
            "use the bound parent amendment capability"
        )
