"""Git range semantics shared by reviewed-input patch and preimage capture."""

from __future__ import annotations

from pathlib import Path
from typing import Callable


class UnresolvableRange(ValueError):
    """A symmetric range whose endpoints have no merge base."""


def is_range(changed_ref: str) -> bool:
    return ".." in changed_ref


def pin_changed_ref(
    repo_root: Path,
    changed_ref: str,
    git_bytes_optional: Callable[..., bytes | None],
) -> str:
    """Replace symbolic endpoints with object ids so a stored ref cannot move.

    `a...b` stays a three-dot range; `a..b` stays two-dot; a single commit
    becomes that commit's object id. Endpoints are resolved before the packet
    is written so later `HEAD` motion cannot change the reviewed set.
    """
    range_endpoints(repo_root, changed_ref, git_bytes_optional)

    def resolve(ref: str) -> str:
        raw = git_bytes_optional(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
        if raw is None:
            raise UnresolvableRange(f"changed ref `{changed_ref}` does not resolve `{ref}`")
        return raw.decode().strip()

    if "..." in changed_ref:
        left, right = changed_ref.split("...", 1)
        return f"{resolve(left or 'HEAD')}...{resolve(right or 'HEAD')}"
    if ".." in changed_ref:
        left, right = changed_ref.split("..", 1)
        return f"{resolve(left or 'HEAD')}..{resolve(right or 'HEAD')}"
    return resolve(changed_ref)


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
