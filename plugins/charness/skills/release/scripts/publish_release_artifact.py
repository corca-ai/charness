from __future__ import annotations

import runpy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts.current_pointer_writer_lib import write_current_pointer_text

_sections = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_artifact_sections.py")))
)
issue_closeout_lines = _sections.issue_closeout_lines
release_record_lines = _sections.release_record_lines
release_push_lines = _sections.release_push_lines
review_proof_lines = _sections.review_proof_lines
requested_review_lines = _sections.requested_review_lines
release_adapter_preflight_lines = _sections.release_adapter_preflight_lines
retro_trigger_evaluation_lines = _sections.retro_trigger_evaluation_lines
post_publish_proof_lines = _sections.post_publish_proof_lines
install_refresh_lines = _sections.install_refresh_lines
public_release_verification_lines = _sections.public_release_verification_lines
distinct_channel_verification_lines = _sections.distinct_channel_verification_lines
real_host_lines = _sections.real_host_lines
fresh_checkout_lines = _sections.fresh_checkout_lines
release_runtime_lines = _sections.release_runtime_lines
user_update_lines = _sections.user_update_lines


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
    requested_review_gate: dict[str, Any] | None = None,
    retro_trigger_evaluation: dict[str, Any] | None = None,
    distinct_channel_verification: dict[str, Any] | None = None,
    release_runtime: list[dict[str, Any]] | None = None,
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
    lines.extend(distinct_channel_verification_lines(distinct_channel_verification))
    lines.extend(release_adapter_preflight_lines(release_adapter_preflight_payload))
    lines.extend(retro_trigger_evaluation_lines(retro_trigger_evaluation))
    lines.extend(real_host_lines(real_host_payload, install_refresh=install_refresh))
    lines.extend(review_proof_lines(review_proof))
    lines.extend(requested_review_lines(requested_review_gate))
    lines.extend(post_publish_proof_lines(resolved_tag, public_release_verification))
    lines.extend(install_refresh_lines(install_refresh))
    lines.extend(release_runtime_lines(release_runtime))
    lines.extend(fresh_checkout_lines(fresh_checkout_payload))
    lines.extend(issue_closeout_lines(issue_closeout))
    lines.extend(user_update_lines(update_instructions))
    write_current_pointer_text(artifact_path, "\n".join(lines))
    return str(artifact_path.relative_to(repo_root))
