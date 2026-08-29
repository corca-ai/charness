from __future__ import annotations

import runpy
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts.current_pointer_writer_lib import write_current_pointer_text

_sections = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_artifact_sections.py")))
)
claims_review_lines = _sections.claims_review_lines
bump_rationale_lines = _sections.bump_rationale_lines
version_drift_lines = _sections.version_drift_lines
issue_closeout_lines = _sections.issue_closeout_lines
release_record_lines = _sections.release_record_lines
release_push_lines = _sections.release_push_lines
review_proof_lines = _sections.review_proof_lines
requested_review_lines = _sections.requested_review_lines
release_adapter_preflight_lines = _sections.release_adapter_preflight_lines
post_publish_proof_lines = _sections.post_publish_proof_lines
install_refresh_lines = _sections.install_refresh_lines
public_release_verification_lines = _sections.public_release_verification_lines
distinct_channel_verification_lines = _sections.distinct_channel_verification_lines
fresh_checkout_lines = _sections.fresh_checkout_lines
release_runtime_lines = _sections.release_runtime_lines
release_observer_lines = _sections.release_observer_lines
published_notes_audit_lines = _sections.published_notes_audit_lines
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
    release_adapter_preflight_payload: dict[str, Any] | None = None,
    fresh_checkout_payload: dict[str, Any] | None = None,
    issue_closeout: dict[str, Any] | None = None,
    install_refresh: dict[str, Any] | None = None,
    quality_status: str = "passed before publish",
    tag_name: str | None = None,
    public_release_verification: str = "not checked by this helper",
    review_proof: str | None = None,
    requested_review_gate: dict[str, Any] | None = None,
    distinct_channel_verification: dict[str, Any] | None = None,
    published_notes_audit: dict[str, Any] | None = None,
    release_runtime: list[dict[str, Any]] | None = None,
    release_observer: dict[str, Any] | None = None,
    claims_review: dict[str, Any] | None = None,
    release_stage: str | None = None,
    bump_rationale: str | None = None,
    version_drift_check: dict[str, Any] | None = None,
) -> str:
    artifact_dir = repo_root / output_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "latest.md"
    resolved_tag = tag_name or f"v{target_version}"
    artifact_relpath = str(artifact_path.relative_to(repo_root))
    prepared = release_stage is not None
    lines = [
        "# Release Surface Check",
        *([f"<!-- {release_stage} -->"] if release_stage else []),
        f"Date: {datetime.now().astimezone().date().isoformat()}",
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
        *version_drift_lines(version_drift_check),
        *([] if prepared else release_push_lines(public_release_verification)),
        "",
        "## Release State",
        "",
        "- local release mutation: complete",
        *( ["- branch/tag push: pending independent claims review."] if release_stage else ["- branch/tag push: complete"] ),
    ]
    lines.extend(release_record_lines(release_url, public_release_verification, prepared=prepared))
    lines.extend(
        [
            f"- public release surface verification: {'pending independent claims review' if prepared else public_release_verification}",
            f"- audit narrative: durable record written to `{artifact_relpath}` and committed with this slice",
        ]
    )
    lines.extend(public_release_verification_lines(public_release_verification, release_url))
    lines.extend(distinct_channel_verification_lines(distinct_channel_verification))
    lines.extend(published_notes_audit_lines(published_notes_audit))
    lines.extend(release_adapter_preflight_lines(release_adapter_preflight_payload))
    lines.extend(review_proof_lines(review_proof))
    # Beside the critique floor it is the stronger sibling of, and deliberately BELOW the
    # `## Release State` ledger: the narrative audit terminates that ledger at the first
    # following `## ` heading and then requires all five of its entries, so a section
    # inserted above `## Public Release Verification` blocks release PREPARATION with four
    # "missing required entry" blockers.
    lines.extend(claims_review_lines(claims_review, prepared=prepared))
    lines.extend(requested_review_lines(requested_review_gate))
    lines.extend(post_publish_proof_lines(resolved_tag, public_release_verification))
    lines.extend(install_refresh_lines(install_refresh))
    lines.extend(release_runtime_lines(release_runtime))
    lines.extend(release_observer_lines(release_observer))
    lines.extend(fresh_checkout_lines(fresh_checkout_payload))
    lines.extend(issue_closeout_lines(issue_closeout))
    lines.extend(user_update_lines(update_instructions))
    # LAST, and that placement is the mechanism rather than a layout preference. This
    # section is the only operator-authored prose in the record, and the whole class of
    # hazard it carries is "an unterminated construct hides everything BELOW it": a raw-text
    # element, a template, an unclosed tag, an HTML comment. With nothing below it, the
    # blast radius of any of them is the rationale itself.
    #
    # This replaces a refusal that tried to enumerate the hazardous constructs. That guard
    # was widened, narrowed, and rebuilt across three review rounds and was wrong in both
    # directions each time, because it decided what a RENDERED document shows while being
    # unable to see any renderer -- and this repo has no renderer dependency to see one
    # with. Position closes the class for every renderer, measured or not, and rewrites
    # none of the operator's bytes. It also cannot go stale.
    #
    # Not above `## Release State`, which was the previous home: the narrative audit reads
    # the five-entry ledger as the span to the next `## `, so a section inside it blocks
    # the publish with four missing-entry blockers.
    lines.extend(bump_rationale_lines(bump_rationale))
    write_current_pointer_text(artifact_path, "\n".join(lines))
    return str(artifact_path.relative_to(repo_root))


def write_current_artifact(
    repo_root: Path,
    adapter_data: dict[str, Any],
    payload: dict[str, Any],
    *,
    quality_status: str | None = None,
    fresh_checkout_payload: dict[str, Any] | None = None,
    release_url: str | None = None,
    issue_closeout: dict[str, Any] | None = None,
    install_refresh: dict[str, Any] | None = None,
    release_stage: str | None = None,
) -> str:
    # READ IT FROM THE PAYLOAD, like every other field on this call.
    #
    # This function reads `version_drift_check`, `bump_rationale`, `claims_review`
    # and a dozen more from `payload`; `quality_status` alone was a passthrough
    # with a hardcoded default, so a writer that did not name it rendered
    # "passed before publish" whether the gate ran, failed, or never started.
    #
    # Repaired at the OWNER after two call-site repairs each missed a writer: the
    # first reached only the commit-time write, the second added the amend, and a
    # claims round then found `commit_post_publish_artifact` -- the write that
    # produces the record actually pushed to `main` -- still rendering the
    # literal. There are five writers across four modules; patching call sites was
    # always going to lose that race. An explicit argument still wins, for the one
    # caller that legitimately says "queued".
    quality_status = quality_status or payload.get("quality_status") or "passed before publish"
    return write_release_artifact(
        repo_root, output_dir=adapter_data["output_dir"], package_id=adapter_data["package_id"],
        previous_version=payload["previous_version"], target_version=payload["target_version"], remote=payload["remote"],
        branch=payload["branch"], quality_command=adapter_data["quality_command"], release_url=release_url,
        update_instructions=adapter_data["update_instructions"],
        release_adapter_preflight_payload=payload.get("release_adapter_preflight"),
        fresh_checkout_payload=fresh_checkout_payload, issue_closeout=issue_closeout, quality_status=quality_status,
        install_refresh=install_refresh or payload.get("install_refresh"), tag_name=payload["tag_name"],
        public_release_verification=payload.get("public_release_verification", "not checked by this helper"),
        review_proof=payload.get("critique_artifact"), requested_review_gate=payload.get("requested_review_gate"),
        distinct_channel_verification=payload.get("distinct_channel_verification"),
        published_notes_audit=payload.get("published_notes_audit"),
        release_runtime=payload.get("release_runtime"),
        release_observer=payload.get("release_observer"), claims_review=payload.get("claims_review"),
        release_stage=release_stage or payload.get("release_stage"),
        bump_rationale=payload.get("bump_rationale"),
        version_drift_check=payload.get("version_drift_check"),
    )
