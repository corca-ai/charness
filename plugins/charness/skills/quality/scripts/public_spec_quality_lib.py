from __future__ import annotations

from pathlib import Path
from typing import Any

IGNORED_PARTS = {".git", ".charness", "__pycache__", "node_modules", "plugins", "evals"}
REVIEW_PROMPTS = [
    "Keep public executable pages reader-facing: current claims first, internal structure second.",
    "Check whether source inventory or implementation pinning became the main proof surface.",
    "Audit proof layering, not only proof presence: duplicated happy paths at the wrong layer create maintenance drag.",
    "Delete repeated public-spec, smoke, or on-demand E2E proof once a narrower layer owns the claim honestly.",
]
SMOKE_KEEP = [
    "the smoke test proves a cross-command flow",
    "the smoke test mutates a repo or artifact boundary",
    "a narrower layer cannot own the seam honestly",
]
SMOKE_DELETE = [
    "the smoke test only repeats the same happy-path claim already owned by a public spec",
    "lower-layer tests already own the behavior and the smoke adds no repo-mutation value",
]
E2E_KEEP = [
    "the E2E path proves an external-consumer or environment-heavy seam",
    "the flow is too expensive or unstable for standing smoke or public-spec ownership",
]
E2E_DELETE = [
    "the E2E path only repeats a cheap happy-path contract already owned by a public spec or smoke test",
]


def visible_paths(repo_root: Path, pattern: str) -> list[Path]:
    return sorted(
        path for path in repo_root.rglob(pattern)
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts)
    )


def recommendation(
    action: str,
    scope: str,
    target: str,
    target_items: list[Any],
    *,
    guidance: str | None = None,
    keep_when: list[str] | None = None,
    delete_when: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "action": action,
        "scope": scope,
        "target": target,
        "target_items": target_items,
    }
    if guidance is not None:
        payload["guidance"] = guidance
    if keep_when is not None:
        payload["keep_when"] = keep_when
    if delete_when is not None:
        payload["delete_when"] = delete_when
    return payload
