"""Own release tag history and the unreleased change-set scope.

The publish helper also exposes command and backend utilities, but deciding the
previous semantic version and the diff base is one cohesive scope calculation.
This module keeps that calculation independent while callers inject the helper
runner and delta collector so existing failure behavior remains unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

SEMVER_TAG_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


def _semver_tuple(version: str) -> tuple[int, int, int] | None:
    tag = version if version.startswith("v") else f"v{version}"
    match = SEMVER_TAG_RE.fullmatch(tag)
    if match is None:
        return None
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


def _tag_version(tag_ref: str) -> str | None:
    tag = tag_ref.rsplit("/", 1)[-1]
    return tag.removeprefix("v") if SEMVER_TAG_RE.fullmatch(tag) else None


def _release_tag_versions(
    repo_root: Path,
    *,
    remote: str,
    run_command: Callable[..., Any],
) -> set[str]:
    versions: set[str] = set()
    local = run_command(
        ["git", "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"], cwd=repo_root, check=False
    )
    if local.returncode != 0:
        raise SystemExit(
            "release tag discovery failed while resolving previous release version\n"
            "source: local tags\n"
            "command: git tag --list v[0-9]*.[0-9]*.[0-9]*\nexit_code: "
            f"{local.returncode}\nSTDOUT:\n{local.stdout}\nSTDERR:\n{local.stderr}"
        )
    versions.update(
        filter(None, (_tag_version(line.strip()) for line in local.stdout.splitlines()))
    )
    remote_result = run_command(
        ["git", "ls-remote", "--tags", remote, "refs/tags/v[0-9]*"], cwd=repo_root, check=False
    )
    if remote_result.returncode != 0:
        raise SystemExit(
            "release tag discovery failed while resolving previous release version\n"
            "source: remote tags\n"
            "command: git ls-remote --tags "
            f"{remote} refs/tags/v[0-9]*\nexit_code: {remote_result.returncode}\n"
            f"STDOUT:\n{remote_result.stdout}\nSTDERR:\n{remote_result.stderr}"
        )
    for line in remote_result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not parts[1].endswith("^{}"):
            version = _tag_version(parts[1])
            if version:
                versions.add(version)
    return versions


def latest_previous_release_version(
    repo_root: Path,
    *,
    target_version: str,
    remote: str,
    release_tag_versions: Callable[..., set[str]],
) -> str | None:
    target = _semver_tuple(target_version)
    if target is None:
        return None
    candidates: list[tuple[tuple[int, int, int], str]] = []
    for version in release_tag_versions(repo_root, remote=remote):
        parsed = _semver_tuple(version)
        if parsed is not None and parsed < target:
            candidates.append((parsed, version))
    return max(candidates)[1] if candidates else None


def release_previous_version(
    repo_root: Path,
    publish_current: bool,
    current_version: str,
    target_version: str,
    remote: str,
    latest_previous: Callable[..., str | None],
) -> str:
    if not publish_current:
        return current_version
    return (
        latest_previous(repo_root, target_version=target_version, remote=remote) or current_version
    )


def _release_base_ref(
    repo_root: Path,
    *,
    previous_version: str | None,
    remote: str,
    branch: str,
    run_command: Callable[..., Any],
) -> str:
    if previous_version:
        tag_ref = f"refs/tags/v{previous_version}"
        tag_result = run_command(
            ["git", "rev-parse", "--verify", "--quiet", tag_ref],
            cwd=repo_root,
            check=False,
        )
        if tag_result.returncode == 0:
            return tag_ref
        remote_tag_result = run_command(
            ["git", "ls-remote", "--tags", remote, tag_ref],
            cwd=repo_root,
            check=False,
        )
        if remote_tag_result.returncode != 0:
            raise SystemExit(
                "release base ref lookup failed while computing unreleased paths\n"
                f"tag_ref: {tag_ref}\n"
                f"command: git ls-remote --tags {remote} {tag_ref}\n"
                f"exit_code: {remote_tag_result.returncode}\n"
                f"STDOUT:\n{remote_tag_result.stdout}\nSTDERR:\n{remote_tag_result.stderr}"
            )
        if remote_tag_result.returncode == 0 and remote_tag_result.stdout.strip():
            fetch_result = run_command(
                ["git", "fetch", "--quiet", remote, f"{tag_ref}:{tag_ref}"],
                cwd=repo_root,
                check=False,
            )
            if fetch_result.returncode == 0:
                return tag_ref
            raise SystemExit(
                "release base ref fetch failed while computing unreleased paths\n"
                f"tag_ref: {tag_ref}\n"
                f"command: git fetch --quiet {remote} {tag_ref}:{tag_ref}\n"
                f"exit_code: {fetch_result.returncode}\n"
                f"STDOUT:\n{fetch_result.stdout}\nSTDERR:\n{fetch_result.stderr}"
            )
    return f"{remote}/{branch}"


def unreleased_paths(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
    unreleased_scope: Callable[..., dict[str, Any]],
) -> list[str]:
    return unreleased_scope(
        repo_root,
        remote=remote,
        branch=branch,
        previous_version=previous_version,
    )["changed_paths"]


def unreleased_scope(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
    run_command: Callable[..., Any],
    collect_delta: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    base_ref = _release_base_ref(
        repo_root,
        previous_version=previous_version,
        remote=remote,
        branch=branch,
        run_command=run_command,
    )
    try:
        delta = collect_delta(repo_root, base_ref)
    except ValueError as exc:
        raise SystemExit(
            "release diff failed while computing unreleased paths\n"
            f"base_ref: {base_ref}\n"
            f"error: {exc}"
        ) from exc
    return {
        "base_ref": base_ref,
        **delta,
    }
