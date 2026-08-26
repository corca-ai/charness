"""Small ingress guard shared by generic issue close and Goal Run close."""

from __future__ import annotations

import json
import re
from typing import Any

MARKER_RE = re.compile(r"<!--\s*charness-goal-run:(?P<version>[^\s]+)")
BLOCK_RE = re.compile(
    r"<!--\s*charness-goal-run:v1\s*\n(?P<payload>\{.*?\})\s*\n\s*-->", re.DOTALL
)


def parse_goal_run_metadata(body: Any, *, context: str = "issue body") -> dict[str, Any] | None:
    """Return the managed block, or refuse malformed/unknown blocks."""
    if not isinstance(body, str):
        return None
    markers = list(MARKER_RE.finditer(body))
    if not markers:
        return None
    versions = sorted({match.group("version") for match in markers})
    if versions != ["v1"]:
        raise RuntimeError(f"{context} has unsupported Goal Run metadata version(s): {versions!r}")
    blocks = list(BLOCK_RE.finditer(body))
    if len(markers) != 1 or len(blocks) != 1:
        raise RuntimeError(f"{context} has duplicate or malformed Goal Run metadata")
    try:
        payload = json.loads(blocks[0].group("payload"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{context} Goal Run metadata is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{context} Goal Run metadata must be a JSON object")
    return payload


def refuse_generic_close(body: Any, *, context: str = "issue body") -> None:
    """Generic close ingress cannot close a Goal Run."""
    if parse_goal_run_metadata(body, context=context) is not None:
        raise RuntimeError(
            "goal-run-close-required: generic issue close cannot close a Goal Run; "
            "use the dedicated guarded Goal Run close operation"
        )
