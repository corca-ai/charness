"""Artifact and Git commit owner for release-linked issue closeout evidence."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _write_and_stage(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload["issue_closeout"],
    )
    observer_path = str((payload.get("release_observer") or {}).get("path", "")).strip()
    paths = [artifact_relpath, *([observer_path] if observer_path else [])]
    run(["git", "add", *paths], cwd=repo_root)


def commit_issue_closeout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run,
) -> None:
    _write_and_stage(
        repo_root, write_artifact=write_artifact, payload=payload,
        fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url, run=run,
    )
    run(["git", "commit", "-m", f"Record release issue closeout for {payload['tag_name']}"], cwd=repo_root)
    run(["git", "push", remote, branch], cwd=repo_root)
    payload["issue_closeout_commit_sha"] = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()


def commit_issue_closeout_carrier_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run,
) -> None:
    """Persist observer evidence in the commit whose push may auto-close issues."""
    paragraphs = payload.get("issue_closeout_draft_validation", {}).get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        raise SystemExit("release issue closeout carrier paragraphs are missing after preflight validation")
    preflight = payload.get("issue_closeout_preflight", {})
    payload["issue_closeout"] = {
        "status": "carrier-pending-state-verification",
        "repo": preflight.get("repo"),
        "issues": preflight.get("issues", []),
    }
    _write_and_stage(
        repo_root, write_artifact=write_artifact, payload=payload,
        fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url, run=run,
    )
    command = ["git", "commit"]
    for paragraph in paragraphs:
        command.extend(["-m", str(paragraph)])
    run(command, cwd=repo_root)
    run(["git", "push", remote, branch], cwd=repo_root)
    payload["issue_closeout_carrier_commit_sha"] = run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root
    ).stdout.strip()
