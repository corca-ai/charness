"""Git range semantics shared by reviewed-input patch and preimage capture."""

from __future__ import annotations

from pathlib import Path
from typing import Callable


class UnresolvableRange(ValueError):
    """A symmetric range whose endpoints have no merge base."""


def is_range(changed_ref: str) -> bool:
    return ".." in changed_ref


def range_endpoints(
    repo_root: Path,
    changed_ref: str,
    git_bytes_optional: Callable[..., bytes | None],
) -> tuple[str | None, str]:
    """Return ``(start, target)`` for a range or ``(None, commit)`` for a commit."""
    if "..." in changed_ref:
        left_raw, right_raw = changed_ref.split("...", 1)
        left = left_raw or "HEAD"
        right = right_raw or "HEAD"
        merge_base = git_bytes_optional(repo_root, "merge-base", left, right)
        if merge_base is None:
            raise UnresolvableRange(
                f"changed ref `{changed_ref}` has no merge base for `{left}` and `{right}`"
            )
        return merge_base.decode().strip(), right
    if ".." in changed_ref:
        left, right = changed_ref.split("..", 1)
        return (left or "HEAD"), (right or "HEAD")
    return None, changed_ref


def preimage_refs(
    repo_root: Path,
    changed_ref: str | None,
    git_bytes_optional: Callable[..., bytes | None],
) -> list[str]:
    if not changed_ref:
        return []
    start_ref, target_ref = range_endpoints(repo_root, changed_ref, git_bytes_optional)
    if start_ref is not None:
        return [start_ref]
    raw = git_bytes_optional(repo_root, "rev-list", "--parents", "-n", "1", target_ref)
    if not raw:
        return []
    return raw.decode("utf-8", errors="surrogateescape").split()[1:]
