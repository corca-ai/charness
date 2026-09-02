"""Compatibility surface for release orchestration helpers.

Command execution and release scope now each have a focused owner. This module
keeps the names consumed by the publish scripts while retaining their original
dependency injection points for tests and callers.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_COMMANDS = runpy.run_path(str(Path(__file__).with_name("publish_release_commands.py")))
RELEASE_VIEW_PLACEHOLDERS = _COMMANDS["RELEASE_VIEW_PLACEHOLDERS"]
RELEASE_CREATE_PLACEHOLDERS = _COMMANDS["RELEASE_CREATE_PLACEHOLDERS"]
OP_PLACEHOLDERS = _COMMANDS["OP_PLACEHOLDERS"]
COMMAND_TIMEOUT_SECONDS = _COMMANDS["COMMAND_TIMEOUT_SECONDS"]
PROGRESS_INTERVAL_ENV = _COMMANDS["PROGRESS_INTERVAL_ENV"]
_PLACEHOLDER_RE = _COMMANDS["_PLACEHOLDER_RE"]
_refuse = _COMMANDS["_refuse"]
_single_remote_object_id = _COMMANDS["_single_remote_object_id"]
_TAG_IDENTITY = _COMMANDS["_TAG_IDENTITY"]
run = _COMMANDS["run"]
run_shell = _COMMANDS["run_shell"]
run_phase = _COMMANDS["run_phase"]
git_status = _COMMANDS["git_status"]
current_branch = _COMMANDS["current_branch"]
tag_exists = _COMMANDS["tag_exists"]
backend_command = _COMMANDS["backend_command"]
release_exists = _COMMANDS["release_exists"]
create_release = _COMMANDS["create_release"]
expected_github_release_url = _COMMANDS["expected_github_release_url"]

_SCOPE = runpy.run_path(str(Path(__file__).with_name("publish_release_scope.py")))
SEMVER_TAG_RE = _SCOPE["SEMVER_TAG_RE"]
_semver_tuple = _SCOPE["_semver_tuple"]
_tag_version = _SCOPE["_tag_version"]

_RELEASE_DELTA = runpy.run_path(str(Path(__file__).with_name("release_delta.py")))
# Read from the module that WRITES the field, never re-spelled here: the two readers of
# `release_observer.path` disagreed about `None` once already.
observer_path = runpy.run_path(str(Path(__file__).with_name("release_observer.py")))[
    "observer_path"
]
collect_release_delta = _RELEASE_DELTA["collect_release_delta"]
path_list_sha256 = _RELEASE_DELTA["path_list_sha256"]


def _release_tag_versions(repo_root: Path, *, remote: str) -> set[str]:
    return _SCOPE["_release_tag_versions"](
        repo_root,
        remote=remote,
        run_command=run,
    )


def latest_previous_release_version(
    repo_root: Path, *, target_version: str, remote: str
) -> str | None:
    return _SCOPE["latest_previous_release_version"](
        repo_root,
        target_version=target_version,
        remote=remote,
        release_tag_versions=_release_tag_versions,
    )


def release_previous_version(
    repo_root: Path,
    publish_current: bool,
    current_version: str,
    target_version: str,
    remote: str,
) -> str:
    return _SCOPE["release_previous_version"](
        repo_root,
        publish_current,
        current_version,
        target_version,
        remote,
        latest_previous_release_version,
    )


def ensure_release_target_available(
    repo_root: Path, *, tag_name: str, remote: str, backend: dict[str, Any]
) -> None:
    tag_state = tag_exists(repo_root, tag_name, remote=remote)
    if tag_state["local"] or tag_state["remote"]:
        raise SystemExit(f"tag `{tag_name}` already exists locally or on `{remote}`")
    if release_exists(repo_root, tag_name, backend):
        raise SystemExit(f"GitHub release `{tag_name}` already exists")


def changed_paths(repo_root: Path) -> list[str]:
    return [line[3:] for line in git_status(repo_root) if len(line) >= 4]


def _release_base_ref(
    repo_root: Path,
    *,
    previous_version: str | None,
    remote: str,
    branch: str,
) -> str:
    return _SCOPE["_release_base_ref"](
        repo_root,
        previous_version=previous_version,
        remote=remote,
        branch=branch,
        run_command=run,
    )


def unreleased_paths(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
) -> list[str]:
    return _SCOPE["unreleased_paths"](
        repo_root,
        remote=remote,
        branch=branch,
        previous_version=previous_version,
        unreleased_scope=unreleased_scope,
    )


def unreleased_scope(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
) -> dict[str, Any]:
    return _SCOPE["unreleased_scope"](
        repo_root,
        remote=remote,
        branch=branch,
        previous_version=previous_version,
        run_command=run,
        collect_delta=collect_release_delta,
    )


def amend_fresh_checkout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    fresh_checkout_payload: dict[str, Any],
    release_url: str | None,
    artifact_relpath: str,
    tag_name: str,
    notes_file: Path | None,
    run_narrative_audit,
    run_command=run,
) -> None:
    write_artifact(fresh_checkout_payload=fresh_checkout_payload, release_url=release_url)
    run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    run_command(["git", "add", artifact_relpath], cwd=repo_root)
    run_command(["git", "commit", "--amend", "--no-edit"], cwd=repo_root)


def commit_post_publish_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run_command=run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload.get("issue_closeout"),
    )
    observer = observer_path(payload)
    tracked_paths = [artifact_relpath, *([observer] if observer else [])]
    diff_result = run_command(
        ["git", "diff", "--quiet", "--", *tracked_paths], cwd=repo_root, check=False
    )
    if diff_result.returncode == 0 and observer:
        untracked = run_command(
            ["git", "ls-files", "--error-unmatch", observer], cwd=repo_root, check=False
        )
        if untracked.returncode != 0:
            diff_result = untracked
    if diff_result.returncode == 0:
        return
    run_command(["git", "add", *tracked_paths], cwd=repo_root)
    run_command(
        ["git", "commit", "-m", f"Record release verification for {payload['tag_name']}"],
        cwd=repo_root,
    )
    run_command(["git", "push", remote, branch], cwd=repo_root)
    payload["post_publish_artifact_commit_sha"] = run_command(
        ["git", "rev-parse", "HEAD"], cwd=repo_root
    ).stdout.strip()
