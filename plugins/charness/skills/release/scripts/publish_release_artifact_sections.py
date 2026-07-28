from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

# The post-publish verification renderers live in their own module (one concept,
# and this file reached its length cap). Re-exported so existing importers keep
# one import site.
_verification = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_verification_sections.py"))
)
distinct_channel_verification_lines = _verification["distinct_channel_verification_lines"]
published_notes_audit_lines = _verification["published_notes_audit_lines"]
real_host_lines = _verification["real_host_lines"]
release_observer_lines = _verification["release_observer_lines"]


def issue_closeout_lines(issue_closeout: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Issue Closeout", ""]
    if issue_closeout is None:
        return lines + ["- Issue closeout verification: pending or not requested."]
    if issue_closeout.get("status") != "state-verified":
        return lines + [f"- Issue closeout verification: `{issue_closeout.get('status')}`."]
    lines.append(f"- Issue closeout verification: `{issue_closeout.get('status')}`.")
    if repo := issue_closeout.get("repo"):
        lines.append(f"- GitHub repo: `{repo}`")
    for issue in issue_closeout.get("issues", []):
        lines.append(f"- Issue #{issue.get('number')}: `{issue.get('state')}` ({issue.get('url')})")
        lines.append(f"  - carrier: `{issue.get('carrier')}`")
        lines.append(f"  - manual fallback used: `{issue.get('manual_fallback_used')}`")
    return lines


def release_record_lines(release_url: str | None, public_release_verification: str) -> list[str]:
    if release_url and public_release_verification == "verified":
        return [f"- GitHub release record: verified URL `{release_url}`"]
    if release_url and public_release_verification == "failed":
        return [f"- GitHub release record: create returned `{release_url}`, but post-create verification failed"]
    if release_url:
        return [f"- GitHub release record: target URL `{release_url}`; creation runs after the branch/tag push"]
    return ["- GitHub release record: not created by this helper run"]


def release_push_lines(public_release_verification: str) -> list[str]:
    lines = ["- initial release push carried the release branch update and tag from the release helper."]
    if public_release_verification == "verified":
        lines.append("- post-publish artifact push recorded the verified public release state on the release branch.")
    return lines


def review_proof_lines(review_proof: str | None) -> list[str]:
    if review_proof:
        return ["", "## Review Proof", "", f"- Review proof: `{review_proof}`."]
    return ["", "## Review Status", "", "- Review proof: not recorded in this helper invocation."]


def requested_review_lines(payload: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Requested Review Gate", ""]
    if payload is None:
        return lines + ["- Requested-review gate status: not recorded by this helper invocation."]
    lines.append(f"- Requested-review gate status: `{payload.get('status', 'unknown')}`.")
    lines.append(f"- Configuration status: `{payload.get('configuration_status', 'unknown')}`.")
    if policy := payload.get("requested_review_policy"):
        lines.append(f"- Policy: `{policy}`.")
    commands = payload.get("requested_review_commands", [])
    lines.append(f"- Configured command count: `{len(commands) if isinstance(commands, list) else 0}`.")
    for warning in payload.get("warnings", []):
        lines.append(f"- Warning: {warning}")
    return lines


def _pending_payload_section(
    payload: dict[str, Any] | None, *, heading: str, pending: str, status_label: str
) -> tuple[str, list[str]] | None:
    """``(status, opening_lines)`` for a section whose payload may not exist yet,
    or ``None`` once the caller has emitted the pending line.

    Two renderers carried this shape verbatim; shared so a third cannot render a
    status heading over a payload that was never produced.
    """
    lines = ["", heading, ""]
    if payload is None:
        return None, lines + [pending]  # type: ignore[return-value]
    status = str(payload.get("status", "unknown"))
    lines.append(f"- {status_label}: `{status}`.")
    return status, lines


def release_adapter_preflight_lines(payload: dict[str, Any] | None) -> list[str]:
    status, lines = _pending_payload_section(
        payload,
        heading="## Release Adapter Preflight",
        pending="- Release adapter focused preflight: pending helper execution.",
        status_label="Release adapter focused preflight status",
    )
    if status is None:
        return lines
    if reason := payload.get("reason"):
        lines.append(f"- Reason: {reason}")
    if previous_ref := payload.get("previous_ref"):
        lines.append(f"- Previous release ref: `{previous_ref}`")
    adapter_paths = payload.get("adapter_paths", [])
    if adapter_paths:
        lines.append("- Adapter paths in release delta:")
        lines.extend(f"  - `{path}`" for path in adapter_paths)
    changed_fields = payload.get("changed_fields", [])
    if changed_fields:
        lines.append("- Changed adapter fields:")
        lines.extend(f"  - `{field}`" for field in changed_fields)
    commands = payload.get("commands", [])
    if commands:
        lines.append("- Focused preflight commands:")
        lines.extend(f"  - `{' '.join(command)}`" for command in commands)
    else:
        lines.append("- Focused preflight commands: none executed.")
    return lines


def retro_trigger_evaluation_lines(payload: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Retro Trigger Evaluation", ""]
    if payload is None:
        return lines + ["- Retro trigger evaluation: not recorded by this helper invocation."]
    triggered = payload.get("triggered")
    lines.append(f"- Triggered: `{triggered}`.")
    if evaluated_at := payload.get("evaluated_at"):
        lines.append(f"- Evaluated at: `{evaluated_at}`.")
    input_payload = payload.get("input")
    if isinstance(input_payload, dict):
        lines.append(f"- Input mode: `{input_payload.get('mode')}`.")
        if base_ref := input_payload.get("base_ref"):
            lines.append(f"- Base ref: `{base_ref}`.")
        if head_ref := input_payload.get("head_ref"):
            lines.append(f"- Head ref: `{head_ref}`.")
    if reason := payload.get("reason"):
        lines.append(f"- Reason: {reason}")
    closeout = payload.get("closeout")
    if isinstance(closeout, dict):
        lines.append(f"- Closeout status: `{closeout.get('status')}`.")
        if closeout_reason := closeout.get("reason"):
            lines.append(f"- Closeout reason: {closeout_reason}")
        if artifact_path := closeout.get("artifact_path"):
            lines.append(f"- Retro artifact: `{artifact_path}`.")
        if summary_path := closeout.get("summary_path"):
            lines.append(f"- Recent lessons: `{summary_path}`.")
    if configuration_status := payload.get("configuration_status"):
        lines.append(f"- Configuration status: `{configuration_status}`.")
    surface_hits = payload.get("surface_hits", [])
    path_hits = payload.get("path_hits", [])
    changed_paths = payload.get("changed_paths", [])
    lines.append(f"- Surface hits: {len(surface_hits)}.")
    lines.extend(f"  - `{surface}`" for surface in surface_hits)
    lines.append(f"- Path hits: {len(path_hits)}.")
    lines.extend(f"  - `{path}`" for path in path_hits)
    lines.append(f"- Evaluated changed paths: {len(changed_paths)}.")
    lines.extend(f"  - `{path}`" for path in changed_paths[:20])
    if len(changed_paths) > 20:
        lines.append(f"  - ... {len(changed_paths) - 20} more")
    return lines


def post_publish_proof_lines(resolved_tag: str, public_release_verification: str) -> list[str]:
    if public_release_verification != "verified":
        return []
    return ["", "## Post-Publish Proof", "", f"- Public release check: `gh release view {resolved_tag}`."]


def install_refresh_lines(payload: dict[str, Any] | None) -> list[str]:
    status, lines = _pending_payload_section(
        payload,
        heading="## Install Refresh",
        pending="- Post-publish install refresh: pending final publish verification.",
        status_label="Post-publish install refresh status",
    )
    if status is None:
        return lines
    if command := payload.get("command"):
        lines.append(f"- Command: `{command}`")
    if payload.get("returncode") is not None:
        lines.append(f"- Return code: `{payload.get('returncode')}`")
    if payload.get("elapsed_seconds") is not None:
        lines.append(f"- Elapsed seconds: `{payload.get('elapsed_seconds')}`")
    if stdout_tail := payload.get("stdout_tail"):
        lines.append(f"- Stdout tail: `{stdout_tail}`")
    if stderr_tail := payload.get("stderr_tail"):
        lines.append(f"- Stderr tail: `{stderr_tail}`")
    return lines


def public_release_verification_lines(public_release_verification: str, release_url: str | None) -> list[str]:
    lines = ["", "## Public Release Verification", ""]
    if public_release_verification == "verified":
        lines.append("- GitHub release publication: verified by the release backend.")
    elif public_release_verification == "failed":
        lines.append("- GitHub release publication: create returned a result, but post-create verification failed.")
    elif release_url:
        lines.append("- GitHub release publication: expected after branch/tag push; not verified yet.")
    else:
        lines.append("- GitHub release publication: not created by this helper run.")
    return lines


def lifecycle_capture_lines(record: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Lifecycle Usage Capture", ""]
    if not isinstance(record, dict) or not str(record.get("status", "")).strip():
        return lines + ["- Lifecycle capture status: not recorded by this helper invocation."]
    lines.append(f"- Lifecycle capture status: `{record.get('status')}`.")
    lines.append(f"- Local telemetry pair appended: `{bool(record.get('appended', False))}`.")
    if episode_id := record.get("episode_id"):
        lines.append(f"- Delivery episode ID: `{episode_id}`.")
    if feedback_id := record.get("feedback_id"):
        lines.append(f"- Linked feedback ID: `{feedback_id}`.")
    errors = record.get("errors")
    lines.append(f"- Capture error count: `{len(errors) if isinstance(errors, list) else 0}`.")
    lines.append(
        "- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence."
    )
    return lines


def fresh_checkout_lines(fresh_checkout_payload: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Fresh Checkout Probes", ""]
    if fresh_checkout_payload is None:
        return lines + ["- Fresh-checkout probe status: pending release-helper execution."]
    if fresh_checkout_payload.get("status") == "not_configured":
        return lines + ["- No repo-declared fresh checkout probes were configured for this release."]
    lines.append(f"- Fresh-checkout probe status: {fresh_checkout_payload.get('status')}.")
    lines.extend(f"- `{command}`" for command in fresh_checkout_payload.get("fresh_checkout_probes", []))
    return lines


def release_runtime_lines(runtime_entries: list[dict[str, Any]] | None) -> list[str]:
    lines = ["", "## Release Runtime", ""]
    if not runtime_entries:
        return lines + ["- Release helper runtime: not recorded by this helper invocation."]
    for entry in runtime_entries:
        label = entry.get("label", "unknown")
        elapsed = entry.get("elapsed_seconds")
        if isinstance(elapsed, (int, float)):
            lines.append(f"- `{label}`: {elapsed:.3f}s")
        else:
            lines.append(f"- `{label}`: elapsed time unavailable")
    return lines


def baton_reconcile_lines(record: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Baton Reconcile", ""]
    if not isinstance(record, dict) or not str(record.get("status", "")).strip():
        return lines + ["- Baton reconcile observation: not recorded by this helper invocation."]
    status = record.get("status")
    if status == "not_configured":
        return lines + [
            "- No adapter-declared session baton (`post_publish_baton_path`); nothing to reconcile."
        ]
    lines.append(f"- Baton reconcile observation: `{status}` for `{record.get('path')}`.")
    lines.append(f"- Just-published version: `{record.get('target_version')}`.")
    if errors := record.get("errors"):
        lines.extend(
            f"- Observation error: `{error}`; read and reconcile the baton manually." for error in errors
        )
        lines.append(
            "- This is an observation, not completion: the populated record forces the reconcile "
            "question; the release critique/retro reviewers judge the disposition."
        )
        return lines
    versions = record.get("observed_versions") or []
    if versions:
        lines.append(
            "- Versions claimed by the baton's routing sections: "
            + ", ".join(f"`{version}`" for version in versions)
            + "."
        )
    else:
        lines.append("- The baton's routing sections claim no release version.")
    if required_action := record.get("required_action"):
        lines.append(f"- RECONCILE REQUIRED: {required_action}")
    lines.append(
        "- This is an observation, not completion: the populated record forces the reconcile "
        "question; the release critique/retro reviewers judge the disposition."
    )
    return lines


def user_update_lines(update_instructions: list[str]) -> list[str]:
    steps = update_instructions or ["Document the operator-facing refresh path before calling the release fully closed."]
    return ["", "## User Update Steps", "", *(f"- {item}" for item in steps), ""]
