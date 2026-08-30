"""Authorization and byte-preservation checks for Goal Run parent amendments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

PARENT_AMENDMENT_AUTHORIZATION_KIND = "charness.goal-run-parent-amendment/v1"
PARENT_AMENDMENT_AUTHORIZATION_FIELDS = frozenset(
    {
        "kind",
        "parent",
        "binding_sha256",
        "current_body_sha256",
        "desired_body_sha256",
        "approval",
        "reason",
    }
)
PARENT_AMENDMENT_APPROVAL_FIELDS = frozenset({"response", "session_id", "observed_at"})


def _parent_identity(repo: str, number: int) -> dict[str, Any]:
    return {
        "repo": repo,
        "number": number,
        "url": f"https://github.com/{repo}/issues/{number}",
    }


def load_authorization(
    path: Path,
    *,
    binding: dict[str, Any],
    repo: str,
    parent_number: int,
    current_body: str,
    desired_body: str,
    canonical_json_bytes: Callable[[Any], bytes],
) -> dict[str, Any]:
    """Validate a canonical receipt against the exact parent amendment bytes."""
    if not path.is_file():
        raise RuntimeError(f"parent amendment authorization file not found: {path}")
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("parent amendment authorization must be canonical UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError("parent amendment authorization must be a JSON object")
    if set(value) != PARENT_AMENDMENT_AUTHORIZATION_FIELDS:
        raise RuntimeError("parent amendment authorization has the wrong fields")
    if canonical_json_bytes(value) != raw:
        raise RuntimeError("parent amendment authorization bytes are not canonical JSON")
    if value["kind"] != PARENT_AMENDMENT_AUTHORIZATION_KIND:
        raise RuntimeError("parent amendment authorization names an unsupported schema")
    if value["parent"] != _parent_identity(repo, parent_number):
        raise RuntimeError("parent amendment authorization parent differs from the Goal Run parent")
    if value["binding_sha256"] != binding["binding_sha256"]:
        raise RuntimeError(
            "parent amendment authorization binding differs from the immutable Goal Binding"
        )
    expected_hashes = {
        "current_body_sha256": hashlib.sha256(current_body.encode("utf-8")).hexdigest(),
        "desired_body_sha256": hashlib.sha256(desired_body.encode("utf-8")).hexdigest(),
    }
    for field, expected in expected_hashes.items():
        if value[field] != expected:
            raise RuntimeError(
                f"parent amendment authorization {field} does not match the body bytes"
            )
    approval = value["approval"]
    if not isinstance(approval, dict) or set(approval) != PARENT_AMENDMENT_APPROVAL_FIELDS:
        raise RuntimeError("parent amendment authorization approval has the wrong fields")
    if any(
        not isinstance(approval[field], str) or not approval[field].strip() for field in approval
    ):
        raise RuntimeError("parent amendment authorization approval fields must be non-empty text")
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        raise RuntimeError("parent amendment authorization reason must be non-empty text")
    return value


def validate_parent_body_update(
    current_body: str,
    desired_body: str,
    *,
    binding: dict[str, Any],
    repo: str,
    parent_number: int,
    parent_url: str | None,
    guard: Any,
    validate_parent_metadata: Callable[..., dict[str, Any]],
    canonical_json_bytes: Callable[[Any], bytes],
    amendment_authorization_file: Path | None = None,
) -> None:
    """Keep metadata immutable while authorizing explicit human-body changes."""
    current = guard.parse_goal_run_metadata(current_body, context="current Goal Run parent body")
    desired = guard.parse_goal_run_metadata(desired_body, context="desired Goal Run parent body")
    if desired is None:
        raise RuntimeError("parent update must carry complete Goal Run metadata")
    validate_parent_metadata(
        desired,
        binding,
        repo=repo,
        parent_number=parent_number,
        parent_url=parent_url,
    )
    if current is not None:
        validate_parent_metadata(
            current,
            binding,
            repo=repo,
            parent_number=parent_number,
            parent_url=parent_url,
        )
    current_matches = list(guard.BLOCK_RE.finditer(current_body))
    desired_matches = list(guard.BLOCK_RE.finditer(desired_body))
    if len(desired_matches) != 1 or len(current_matches) > 1:
        raise RuntimeError("Goal Run parent metadata must have one replaceable block")
    desired_match = desired_matches[0]
    if not current_matches:
        if amendment_authorization_file is not None:
            raise RuntimeError("parent amendment authorization is not valid during metadata bootstrap")
        if desired_body[: desired_match.start()] != current_body or desired_body[
            desired_match.end() :
        ] not in {"", "\n"}:
            raise RuntimeError(
                "initial parent metadata must append to the exact live human-readable body"
            )
        return
    current_match = current_matches[0]
    current_human = (
        current_body[: current_match.start()],
        current_body[current_match.end() :],
    )
    desired_human = (
        desired_body[: desired_match.start()],
        desired_body[desired_match.end() :],
    )
    if current_human == desired_human:
        return
    if amendment_authorization_file is None:
        raise RuntimeError(
            "parent human-readable Markdown amendment requires an explicit authorization receipt"
        )
    load_authorization(
        amendment_authorization_file,
        binding=binding,
        repo=repo,
        parent_number=parent_number,
        current_body=current_body,
        desired_body=desired_body,
        canonical_json_bytes=canonical_json_bytes,
    )
