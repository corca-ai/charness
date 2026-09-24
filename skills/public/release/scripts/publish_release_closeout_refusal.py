"""Refuse post-publication closeout when the published release is not visible.

The pre-publication lane refuses an unverified release before issue closeout
(`fail_after_post_create_verification`). The recovery lanes recorded
`release_verified: False` and CONTINUED into the closeout tail -- the same
floor must hold on the path an operator reaches for after a failed close.
The verification record is committed first (mirroring that lane) so the next
resume classifies against a record that says what actually happened, then the
refusal names the retry: re-run --resume once the release is visible again.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _commit_and_refuse_unverified_release(
    repo_root: Path,
    *,
    args: Any,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    verify: Any,
    cli: Any,
) -> None:
    """Stop closeout when the published release is no longer visible.

    The pre-publication lane refuses exactly here (`fail_after_post_create_
    verification`): closing issues over a release even the publisher cannot see
    would record success against an unverified external fact. These recovery
    lanes recorded `release_verified: False` and CONTINUED into issue closeout
    -- the same floor must hold on the path an operator reaches for after a
    failed close. The artifact is committed first (mirroring that lane) so the
    next resume classifies against a record that says what actually happened,
    then the refusal names the retry: re-run --resume once the release is
    visible again.
    """
    cli.commit_final_release_artifact(
        repo_root,
        adapter_data=adapter_data,
        payload=payload,
        fresh_checkout_payload=fresh_checkout_payload,
        artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url,
        remote=args.remote,
        branch=plan["branch"],
        has_issue_closeout=False,
    )
    cli.fail_after_post_create_verification(payload, verification_result=verify)
