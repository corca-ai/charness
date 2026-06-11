from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.current_pointer_writer_lib import write_current_pointer_text


def issue_closeout_lines(issue_closeout: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Issue Closeout", ""]
    if issue_closeout is None:
        return lines + ["- Issue closeout verification: pending or not requested."]
    if issue_closeout.get("status") != "verified":
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


def release_adapter_preflight_lines(payload: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Release Adapter Preflight", ""]
    if payload is None:
        return lines + ["- Release adapter focused preflight: pending helper execution."]
    status = payload.get("status", "unknown")
    lines.append(f"- Release adapter focused preflight status: `{status}`.")
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
    lines = ["", "## Install Refresh", ""]
    if payload is None:
        return lines + ["- Post-publish install refresh: pending final publish verification."]
    status = payload.get("status", "unknown")
    lines.append(f"- Post-publish install refresh status: `{status}`.")
    if command := payload.get("command"):
        lines.append(f"- Command: `{command}`")
    if payload.get("returncode") is not None:
        lines.append(f"- Return code: `{payload.get('returncode')}`")
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


def real_host_lines(real_host_payload: dict[str, Any]) -> list[str]:
    lines = ["", "## Real-Host Verification", ""]
    if real_host_payload.get("required"):
        lines.append(
            "- This slice still requires configured real-host verification before the release is fully closed."
        )
        lines.extend(["", "## Real-Host Proof", "", "- Release-time real-host proof is required for this slice."])
        lines.extend(f"- {item}" for item in real_host_payload.get("checklist", []))
        return lines
    lines.append("- No configured release-time real-host verification trigger matched this slice.")
    lines.extend(["", "## Real-Host Proof", "", "- No configured release-time real-host proof trigger matched this slice."])
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


def user_update_lines(update_instructions: list[str]) -> list[str]:
    steps = update_instructions or ["Document the operator-facing refresh path before calling the release fully closed."]
    return ["", "## User Update Steps", "", *(f"- {item}" for item in steps), ""]


def write_release_artifact(
    repo_root: Path,
    *,
    output_dir: str,
    package_id: str,
    previous_version: str,
    target_version: str,
    remote: str,
    branch: str,
    quality_command: str,
    release_url: str | None,
    update_instructions: list[str],
    real_host_payload: dict[str, Any],
    release_adapter_preflight_payload: dict[str, Any] | None = None,
    fresh_checkout_payload: dict[str, Any] | None = None,
    issue_closeout: dict[str, Any] | None = None,
    install_refresh: dict[str, Any] | None = None,
    quality_status: str = "passed before publish",
    tag_name: str | None = None,
    public_release_verification: str = "not checked by this helper",
    review_proof: str | None = None,
    retro_trigger_evaluation: dict[str, Any] | None = None,
) -> str:
    artifact_dir = repo_root / output_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "latest.md"
    resolved_tag = tag_name or f"v{target_version}"
    artifact_relpath = str(artifact_path.relative_to(repo_root))
    lines = [
        "# Release Surface Check",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        "",
        "## Scope",
        "",
        f"Advanced `{package_id}` toward release `{target_version}` (tag `{resolved_tag}`) through the repo-owned release helper.",
        "",
        "## Current Version",
        "",
        f"- previous version: `{previous_version}`",
        f"- target version: `{target_version}`",
        f"- git branch: `{branch}`",
        f"- git remote: `{remote}`",
        "",
        "## Verification",
        "",
        f"- `{quality_command}` {quality_status}.",
        "- `current_release.py` reported no version drift across packaging and generated install surfaces.",
        *release_push_lines(public_release_verification),
        "",
        "## Release State",
        "",
        "- local release mutation: complete",
        "- branch/tag push: complete",
    ]
    lines.extend(release_record_lines(release_url, public_release_verification))
    lines.extend(
        [
            f"- public release surface verification: {public_release_verification}",
            f"- audit narrative: durable record written to `{artifact_relpath}` and committed with this slice",
        ]
    )
    lines.extend(public_release_verification_lines(public_release_verification, release_url))
    lines.extend(release_adapter_preflight_lines(release_adapter_preflight_payload))
    lines.extend(retro_trigger_evaluation_lines(retro_trigger_evaluation))
    lines.extend(real_host_lines(real_host_payload))
    lines.extend(review_proof_lines(review_proof))
    lines.extend(post_publish_proof_lines(resolved_tag, public_release_verification))
    lines.extend(install_refresh_lines(install_refresh))
    lines.extend(fresh_checkout_lines(fresh_checkout_payload))
    lines.extend(issue_closeout_lines(issue_closeout))
    lines.extend(user_update_lines(update_instructions))
    write_current_pointer_text(artifact_path, "\n".join(lines))
    return str(artifact_path.relative_to(repo_root))
