from __future__ import annotations

import re

FULL_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def single_remote_object_id(stdout: str, *, expected_ref: str) -> str:
    """Return one exact remote ref's full object id, or fail on ambiguity."""

    if not stdout.strip():
        return ""
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1 or len(lines[0]) != 2:
        raise SystemExit(f"remote tag lookup returned ambiguous records for `{expected_ref}`")
    object_id, returned_ref = lines[0]
    if returned_ref != expected_ref:
        raise SystemExit(
            f"remote tag lookup returned `{returned_ref}` while resolving `{expected_ref}`"
        )
    if FULL_OBJECT_ID_RE.fullmatch(object_id) is None:
        raise SystemExit(f"remote tag lookup returned an invalid full object id for `{expected_ref}`")
    return object_id.lower()
