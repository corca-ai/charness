"""The `issue_source_capture` adapter capability.

Split out of `resolve_adapter.py` as its own cohesive unit rather than spilled into a
generic `_lib` companion: this is one named capability with its own contract, defaults,
and refusal semantics, and it is consumed by exactly one caller outside the resolver
(`scripts/issue/capture_issue_source.py`).

The contract answers a question `issue view` cannot: *is this capture complete?* A
backend proves that only by naming how it enumerates (cursor or page), how many items
it returns per request, which field reports that another page exists, which field
resumes from, which field carries the total, and how responses normalize. A backend
that cannot name all of those has an unknown enumeration, and an unknown enumeration
cannot support a completeness claim.
"""

from __future__ import annotations

from typing import Any

ENUMERATION_MODES = ("cursor", "page")
NORMALIZATION_POLICIES = ("github-issue-v1",)
STRING_FIELDS = ("has_next_field", "cursor_field", "total_count_field", "normalization")


def default_source_capture() -> dict[str, Any]:
    """The contract the built-in `gh` backend satisfies.

    The default GitHub adapter meets the same bar it demands of others rather than
    being exempt from it — an exempt default is how the contract quietly becomes
    something only third parties have to satisfy.
    """
    return {
        "enumeration": "cursor",
        "page_size": 100,
        "has_next_field": "hasNextPage",
        "cursor_field": "endCursor",
        "total_count_field": "totalCount",
        "normalization": "github-issue-v1",
        "declared": False,
        "supported": True,
        "unsupported_reason": None,
    }


def _undeclared_for_backend(backend_id: str) -> dict[str, Any]:
    """A non-`gh` backend with no declared capability: unsupported, not invalid.

    Marked and REPORTED rather than raised as an adapter error. Capture is one
    operation among many; failing the whole adapter would break `read`, `close`, and
    `verify` for every consumer on a non-`gh` backend over a capability they may never
    invoke. The refusal belongs on the operation whose claim would be unprovable —
    `capture_issue_source.py` — not on the issue lane as a whole.
    """
    capability = default_source_capture()
    capability["supported"] = False
    capability["unsupported_reason"] = (
        f"issue_backend.id={backend_id} did not declare issue_source_capture; a non-gh "
        "backend must name its enumeration/page-size/has-next/cursor/normalization "
        "contract before a source capture can claim completeness"
    )
    return capability


def parse_source_capture(
    raw: Any,
    backend: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    string_field: Any,
) -> dict[str, Any]:
    """Parse the adapter's `issue_source_capture` block.

    `string_field` is the resolver's shared `(value, field, errors) -> str | None`
    checker, passed in so this module reports field errors in exactly the same shape
    as the rest of the adapter rather than growing a second dialect of them.
    """
    backend_id = backend.get("id", "gh")
    if raw is None:
        return default_source_capture() if backend_id == "gh" else _undeclared_for_backend(backend_id)
    if not isinstance(raw, dict):
        errors.append("issue_source_capture must be a mapping")
        return default_source_capture()

    parsed = default_source_capture()
    parsed["declared"] = True
    enumeration = raw.get("enumeration")
    if enumeration is not None:
        if enumeration not in ENUMERATION_MODES:
            errors.append("issue_source_capture.enumeration must be one of: " + ", ".join(ENUMERATION_MODES))
        else:
            parsed["enumeration"] = enumeration
    page_size = raw.get("page_size")
    if page_size is not None:
        if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1:
            errors.append("issue_source_capture.page_size must be a positive integer")
        else:
            parsed["page_size"] = page_size
    for field in STRING_FIELDS:
        value = string_field(raw.get(field), f"issue_source_capture.{field}", errors)
        if value is not None:
            parsed[field] = value
    if parsed["normalization"] not in NORMALIZATION_POLICIES:
        errors.append(
            "issue_source_capture.normalization must be one of: " + ", ".join(NORMALIZATION_POLICIES)
        )
    if backend_id != "gh" and not (backend.get("commands") or {}).get("source_capture"):
        warnings.append(
            f"issue_backend.id={backend_id} declared issue_source_capture without "
            "commands.source_capture; capture_issue_source.py will refuse until the command "
            "template exists"
        )
    return parsed
