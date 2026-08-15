"""Artifact and Git commit owner for release-linked issue closeout evidence."""
from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

# The observer-path reader is SHARED, not copied, and read from the module that WRITES
# the field: this module and `commit_post_publish_artifact` both decide whether an
# observer record exists, and a private copy is how they came to disagree about
# `path: None`.
observer_path = runpy.run_path(str(Path(__file__).with_name("release_observer.py")))["observer_path"]


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
    observer = observer_path(payload)
    paths = [artifact_relpath, *([observer] if observer else [])]
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
    # The observer record must EXIST before this commit, because pushing this commit is
    # what auto-closes the issues -- and `safe_write_release_observer` swallows every
    # exception into `status: capture_error, path: None`. Without this refusal a failed
    # observer write let the closes happen with their distinct-channel evidence missing,
    # and then permanently blocked recovery: `_validate_carrier_evidence_tree` refuses a
    # carrier tree that does not carry exactly one observer. So the failure mode was
    # "close everything, record nothing, and make it unrepairable" -- silently.
    #
    # Refused HERE rather than at the observer writer, which is deliberately non-fatal
    # because it also runs on lanes where a capture failure is genuinely advisory. This
    # is the one call site where the next statement is irreversible.
    if not observer_path(payload):
        status = (payload.get("release_observer") or {}).get("status") or "missing"
        raise SystemExit(
            "release issue closeout carrier refused: the release observer record was not written "
            f"(status: {status}), and pushing this commit is what closes "
            "the issues. Repair the observer capture and re-run the closeout resume; a carrier "
            "without exactly one observer record cannot be recovered by --resume either."
        )
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
