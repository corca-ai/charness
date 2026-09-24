"""Bind pre-push gate validation evidence to what the resume lane pushes.

The gates run against the worktree/HEAD as it stands; everything after them
(receipt promotion, probe follow-ups, the artifact refresh commit) can move
it. This module snapshots what the gates saw (`_record_validation_binding`),
snapshots what the push is about to carry (`_seal_push_binding`), and
re-verifies the seal at push time (`_verify_push_binding`), aborting on drift
no step of the flow can explain.

Loaded by path (like the other resume-lane modules) and driven through the
caller's ``cli`` command boundary, so tests can drive it against a real
repository with a recording fake.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _git_head_and_tree(cli: Any, repo_root: Path) -> tuple[str, str]:
    """HEAD commit and tree digests through the caller's command boundary."""
    head = cli.run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    tree = cli.run(["git", "rev-parse", "HEAD^{tree}"], cwd=repo_root).stdout.strip()
    if not head or not tree:
        raise SystemExit(
            "--resume: could not resolve HEAD and its tree for the push binding; "
            "refusing to push state that cannot be bound to validation evidence."
        )
    return head, tree


def _record_validation_binding(cli: Any, repo_root: Path, payload: dict[str, Any]) -> None:
    """Snapshot what the pre-push gates validated.

    The gates run against the worktree/HEAD as it stands; everything after them
    (receipt promotion, probe follow-ups, the artifact refresh commit) can move
    it. Recording the digest here is what lets the push-time check tell
    "what the gates saw" from "what is about to be pushed".
    """
    head, tree = _git_head_and_tree(cli, repo_root)
    payload["push_binding"] = {"validated_head": head, "validated_tree": tree}


def _seal_push_binding(cli: Any, repo_root: Path, payload: dict[str, Any]) -> None:
    """Snapshot what the push is about to carry, after the final artifact commit.

    The names of files changed between validation and seal are evidence, not a
    refusal: the artifact refresh commit is SUPPOSED to move the tree, and its
    content is the release record this same flow just wrote. The refusal lives
    at push time (`_verify_push_binding`), where any further movement is drift
    no step of this flow can explain.
    """
    head, tree = _git_head_and_tree(cli, repo_root)
    binding = payload.setdefault("push_binding", {})
    binding["push_head"] = head
    binding["push_tree"] = tree
    validated = binding.get("validated_head")
    if validated and validated != head:
        changed = cli.run(
            ["git", "diff", "--name-only", validated, head], cwd=repo_root
        ).stdout.splitlines()
        binding["validated_to_push_changes"] = [line for line in changed if line.strip()]
    else:
        binding["validated_to_push_changes"] = []


def _verify_push_binding(
    cli: Any,
    repo_root: Path,
    payload: dict[str, Any],
    *,
    tag_name: str,
    expected_tag_commit: str | None,
) -> dict[str, Any]:
    """Re-verify the sealed digest/tree at push time; abort on drift.

    Called first inside `publish()`, so no push runs on a HEAD that moved after
    the seal. The tag target is BOUND (recorded beside the expectation) rather
    than refused: tag identity was already classified by `resumable_state` and
    `assert_resumable`, which own that state -- re-refusing it here would
    duplicate that owner.
    """
    binding = payload.get("push_binding") or {}
    sealed_head = binding.get("push_head")
    sealed_tree = binding.get("push_tree")
    if not sealed_head or not sealed_tree:
        raise SystemExit(
            "--resume: refusing to push without a sealed push binding; "
            "re-run --resume so the pre-push gates re-validate and seal the current HEAD."
        )
    head, tree = _git_head_and_tree(cli, repo_root)
    if head != sealed_head or tree != sealed_tree:
        raise SystemExit(
            "--resume: HEAD moved between the sealed pre-push state and the push "
            f"(sealed {sealed_head}, now {head}); refusing to push state the "
            "gates did not validate. Re-run --resume to re-validate and seal the current HEAD."
        )
    resolved = cli.run(
        ["git", "rev-list", "-n", "1", tag_name], cwd=repo_root, check=False
    )
    target = resolved.stdout.strip() if resolved.returncode == 0 else ""
    binding["pushed_head"] = head
    binding["pushed_tree"] = tree
    binding["expected_tag_commit"] = expected_tag_commit
    binding["tag_target"] = target if target else None
    return binding
