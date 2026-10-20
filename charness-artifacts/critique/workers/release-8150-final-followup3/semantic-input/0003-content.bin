from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Callable

_DEFAULT_BRANCHES = frozenset({"main", "master", "trunk", "develop"})


def _head_branch(repo_root: Path) -> str | None:
    """The checked-out branch, read from the git files (no process spawn)."""
    dot_git = repo_root / ".git"
    try:
        if dot_git.is_file():
            text = dot_git.read_text(encoding="utf-8").strip()
            if not text.startswith("gitdir:"):
                return None
            git_dir = Path(text[len("gitdir:"):].strip())
            dot_git = git_dir if git_dir.is_absolute() else repo_root / git_dir
        head = (dot_git / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    prefix = "ref: refs/heads/"
    return head[len(prefix):] if head.startswith(prefix) else None


def lane_token(repo_root: Path) -> str | None:
    """A name part no parallel lane shares: the task-run lane id, else the branch.

    Follow-up records were numbered by counting files in the lane's own
    worktree, so parallel lanes picked the same number and their merges
    collided as add/add conflicts. Every non-default branch yields a readable
    slug (the lane id for `task/<lane>`) plus an 8-hex hash of the raw
    branch. The slug alone is lossy (`foo_bar`, `Foo`, and a plain `foo-bar`
    all alias `task/foo-bar`), and any exception for "already a slug" names
    lets a crafted name take another branch's token, so two branches share a
    record only on a hash-prefix collision. On a default branch or a
    detached HEAD there is no lane identity, and the counter stays.
    """
    branch = _head_branch(repo_root)
    if not branch or branch in _DEFAULT_BRANCHES:
        return None
    token = branch[len("task/"):] if branch.startswith("task/") else branch
    slug = re.sub(r"[^a-z0-9]+", "-", token.lower()).strip("-")
    digest = hashlib.sha256(branch.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}" if slug else digest


def resolved_followup_record_payload(
    repo_root: Path,
    *,
    adapter: dict[str, object],
    resolved_title: str,
    artifact_date: Any,
    current_pointer_target_path: str | None,
    reuse_subject_key: str | None = None,
    scaffold_artifact_lib: Any,
    resolve_artifact_path: Any,
    resolution: Callable[[Path], str],
) -> dict[str, object]:
    def record_payload_for(title_text: str) -> dict[str, object]:
        return resolve_artifact_path.payload_for(
            repo_root,
            "debug",
            title_text,
            intent="record",
            artifact_date=artifact_date,
            adapter=adapter,
        )

    current_target = current_pointer_target_path or ""

    def usable(candidate_path: str) -> bool:
        if candidate_path == current_target:
            return False
        if (
            reuse_subject_key is not None
            and scaffold_artifact_lib.record_subject_slug(candidate_path) == reuse_subject_key
            and resolution(repo_root / candidate_path) != "resolved"
        ):
            return True
        return not (repo_root / candidate_path).exists()

    candidate = record_payload_for(resolved_title)
    if usable(str(candidate["write_artifact_path"])):
        return candidate
    token = lane_token(repo_root)
    base = f"followup-{token}" if token else "followup"
    for suffix in (base, f"{base}-2", f"{base}-3", f"{base}-4"):
        candidate = record_payload_for(f"{resolved_title} {suffix}")
        if usable(str(candidate["write_artifact_path"])):
            return candidate
    raise SystemExit(
        "resolved current debug artifact needs a fresh dated follow-up record, but every deterministic "
        "default slug for today already exists; rerun scaffold_debug_artifact.py with --title <specific follow-up title>"
    )
