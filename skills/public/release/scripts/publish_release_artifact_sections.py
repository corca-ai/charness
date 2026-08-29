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
release_observer_lines = _verification["release_observer_lines"]

# The other end of the same timeline: what the helper established BEFORE the release
# mutation. Same re-export reason as above.
_premutation = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_premutation_sections.py"))
)
bump_rationale_lines = _premutation["bump_rationale_lines"]
release_adapter_preflight_lines = _premutation["release_adapter_preflight_lines"]
version_drift_lines = _premutation["version_drift_lines"]
_pending_payload_section = _premutation["pending_payload_section"]


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


def release_record_lines(release_url: str | None, public_release_verification: str, *, prepared: bool = False) -> list[str]:
    if prepared:
        return ["- GitHub release record: pending independent claims review before creation"]
    if release_url and public_release_verification == "verified":
        return [f"- GitHub release record: verified URL `{release_url}`"]
    if release_url and public_release_verification == "failed":
        return [f"- GitHub release record: create returned `{release_url}`, but post-create verification failed"]
    if release_url and public_release_verification == "unproven":
        return [f"- GitHub release record: backend-visible URL `{release_url}`; distinct-channel verification remained unproven"]
    if release_url:
        return [f"- GitHub release record: target URL `{release_url}`; creation runs after the branch/tag push"]
    return ["- GitHub release record: not created by this helper run"]


def release_push_lines(public_release_verification: str) -> list[str]:
    lines = ["- initial release push carried the release branch update and tag from the release helper."]
    if public_release_verification == "verified":
        lines.append("- post-publish artifact push recorded the verified public release state on the release branch.")
    return lines


def flatten_signal(signal: object) -> str:
    """The recorded distinctness signal as ONE line.

    Owned here, beside its only caller, rather than next to the validator that refuses a
    multi-line signal. Two copies of one rule is the shape this subsystem's own change-set
    classifier warns about -- and the earlier split was worse than a duplicate, because the
    validator-side copy had no production caller at all while the renderer inlined the rule.
    """
    return " ".join(str(signal).split())


def _scope_lines(claims_review: dict[str, Any]) -> list[str]:
    """What the `pass` covered, and what it saw and did NOT block on.

    A record reading `Claims review verdict: pass` with nothing else hides the
    whole point of the scope split. Narrative defects are published as
    known-inaccurate rather than repaired into a new prepared commit -- so the
    record has to NAME them, or "known-inaccurate" is known to nobody. A
    fresh-eye round found these fields validated and then dropped before this
    renderer, which made the design intent untrue at the one surface outside
    readers get.
    """
    scope = claims_review.get("review_scope") or {}
    if not scope:
        return []
    blocking = scope.get("blocking_paths") or []
    advisory = scope.get("advisory_paths") or []
    findings = claims_review.get("advisory_findings") or []
    lines = [
        f"- Verdict scope: {len(blocking)} blocking path(s) gated this tag; "
        f"{len(advisory)} advisory path(s) (session narrative) were reviewed but did not.",
    ]
    completeness = claims_review.get("scope_completeness")
    if isinstance(completeness, dict) and not completeness.get("verified", True):
        # In the RECORD, not only on stderr. A verdict whose scope was never
        # checked for completeness must not render identically to one that was.
        lines.append(
            "- Verdict scope completeness: NOT VERIFIED -- "
            f"{flatten_signal(completeness.get('reason') or 'no reason recorded')}. "
            "The declared scope was classification-checked but not compared against the "
            "release delta, so it may omit changed paths."
        )
    if not findings:
        # Stated, not omitted. An absent line and "none found" read identically,
        # and the split is only honest if "nobody looked" is distinguishable.
        lines.append("- Advisory findings: none recorded by this review.")
        return lines
    lines.append(
        f"- Advisory findings: {len(findings)} defect(s) recorded in the advisory scope and "
        "SHIPPED KNOWN-INACCURATE rather than repaired before this tag:"
    )
    for finding in findings:
        # Flattened at RENDER time as well as refused at the validator, for the
        # same reason `signal` is: a record committed under an earlier build
        # never saw that refusal, and this document is pushed after the tag.
        if isinstance(finding, dict):
            where = flatten_signal(finding.get("file") or "unspecified")
            what = flatten_signal(finding.get("summary") or "no summary recorded")
            lines.append(f"  - `{where}`: {what}")
        else:
            lines.append(f"  - {flatten_signal(finding)}")
    return lines


def claims_review_lines(claims_review: dict[str, Any] | None, *, prepared: bool = False) -> list[str]:
    """The claims-review verdict, in the document readers outside the session actually get.

    The stronger of the two release floors used to reach the release record not at all: the
    critique artifact was recorded here while the claims verdict lived only in a separate
    JSON, a stderr warning, and a stdout payload, none of which survive into what an outside
    reader reads. `verdict: unproven` is a first-class state whose entire purpose is to be
    visible, and it was the least visible thing the release produced.

    One FIXED heading, never a data-dependent one: a heading whose name varies is what makes
    a downstream substring check silently no-op, and this is a section other tools will grow
    to read. The body varies instead.

    The signal is flattened onto one line at render time as well as refused at the
    validator, because a record committed under an earlier build never saw that refusal.
    """
    lines = ["", "## Claims Review", ""]
    if prepared:
        return lines + [
            "- Claims review: not yet performed -- THIS record is the subject of the pending "
            "independent review, and publication is stopped until that review is committed.",
        ]
    if not claims_review:
        return lines + [
            "- Claims review: not recorded by this helper invocation. This release did not "
            "publish through the claims-review lane, so no distinct-observer property is claimed.",
        ]
    verdict = claims_review.get("verdict")
    distinctness = claims_review.get("observer_distinctness") or {}
    signal = flatten_signal(distinctness.get("signal", ""))
    # `not recorded` rather than a literal `None`, on every field. The validator populates
    # all of them today, so this is a rendering guarantee rather than a live branch -- but
    # a record section whose worst output is the word `None` is a section that can report
    # an absent field as a present one.
    def _named(value: object) -> str:
        return f"`{value}`" if isinstance(value, str) and value else "not recorded"

    lines.append(f"- Claims review record: {_named(claims_review.get('path'))}.")
    if verdict == "pass":
        lines.append("- Claims review verdict: `pass`.")
        lines.append(f"- Observer distinctness: {_named(distinctness.get('kind'))}.")
        lines.append(f"- Recorded signal: {signal}")
        lines.append(f"- Review narrative: {_named(distinctness.get('review_artifact'))}.")
        lines.extend(_scope_lines(claims_review))
        return lines
    # Not `- verdict: unproven.` and nothing else. A reader scanning headings sees a
    # "Claims Review" section and infers a review happened; the token alone reproduces, in a
    # new place, the exact fail-quiet this section exists to close. State the NEGATIVE
    # property, in the same words the boundary warning uses.
    # An `unproven` release that recorded advisory findings used to publish a
    # record showing none: `_scope_lines` was called only on the `pass` branch.
    # The findings are evidence either way.
    lines.extend(_scope_lines(claims_review))
    lines.append(
        f"- Claims review verdict: `{verdict}` -- the distinct-observer property was NOT "
        "established for this release."
    )
    lines.append(
        "- This is a recorded absence, not a passing review: no observer independent of the "
        "release preparer is claimed to have reviewed the claims in this record."
    )
    lines.append(f"- Recorded signal: {signal}")
    lines.append("- Review narrative: none. A `pass` carries the product of its review; this does not.")
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
    elif public_release_verification == "unproven":
        lines.append("- GitHub release publication: backend-visible, but the required distinct-channel readback did not confirm it.")
    elif release_url:
        lines.append("- GitHub release publication: expected after branch/tag push; not verified yet.")
    else:
        lines.append("- GitHub release publication: not created by this helper run.")
    return lines


def fresh_checkout_lines(fresh_checkout_payload: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Fresh Checkout Probes", ""]
    if fresh_checkout_payload is None:
        return lines + ["- Fresh-checkout probe status: pending release-helper execution."]
    if fresh_checkout_payload.get("status") == "not_configured":
        return lines + ["- No repo-declared fresh checkout probes were configured for this release."]
    if fresh_checkout_payload.get("status") == "not_established":
        # The word alone is not enough in the artifact a human audit reads: the
        # previous status here was `configured`, which described the ADAPTER and
        # read as a satisfied probe run. Say what was and was not established.
        lines.append(
            "- Fresh-checkout probes are DECLARED but were not run by this invocation, so no "
            "probe verdict was established here."
        )
        lines.extend(f"- `{command}`" for command in fresh_checkout_payload.get("fresh_checkout_probes", []))
        return lines
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


def user_update_lines(update_instructions: list[str]) -> list[str]:
    """The adapter's refresh steps, each flattened onto ONE line.

    The record's other free-text inlet, and it was rendered raw while its sibling was
    being hardened. `update_instructions` is an unconstrained string list in the release
    adapter, so a YAML entry containing a newline puts its second line at column 0 of the
    published record -- reopening the `- target version:` and unterminated-fence class
    that the bump rationale's quoting closes, on the same document. `flatten_signal` is
    the in-repo precedent for exactly this, and a well-formed single-line instruction is
    unchanged by it.
    """
    steps = update_instructions or ["Document the operator-facing refresh path before calling the release fully closed."]
    return ["", "## User Update Steps", "", *(f"- {flatten_signal(item)}" for item in steps), ""]
