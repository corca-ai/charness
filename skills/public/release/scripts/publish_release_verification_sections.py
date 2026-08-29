"""Post-publish verification sections of the release artifact.

One concept, split out of `publish_release_artifact_sections.py` (which reached
its length cap): the sections that report what the release CONFIRMED after
publishing, and — the part these defects were all about — what it did not.

Every renderer here refuses to assert more than its record supports:
`distinct_channel_verification_lines` keys distinctness on the same-proxy guard
rather than the status (D8), and `published_notes_audit_lines` exists so a
post-create advisory reaches a reader at all (D2).
"""
from __future__ import annotations

from typing import Any


def _distinct_channel_qualifier(status: str, channel: str, guard: str | None) -> str:
    """How to describe the verdict, honestly.

    Distinctness is a property of the same-proxy GUARD, not of the status.
    Branching on status alone left two escapes: a probe of literally
    `gh release view v1` reaches `confirmed` when the caller omits
    `backend`/`backend_command` so the guard never runs, and an
    `inconclusive-degenerate-release-view-template` guard coexists with
    `confirmed`. In both, the guard did not establish distinctness and the
    artifact asserted it anyway — D8's exact failure mode.
    """
    if status == "same-proxy-flagged":
        # This status covers every cause the guard could not rule out: a token-shape
        # match, an unparseable command, a probe nested past the unwrap budget, and
        # (S93) one that unwraps to no command at all. Naming only the first sent the
        # auditor to fix a same-proxy probe that does not exist — the artifact
        # asserting one cause it did not establish, which is the failure mode above.
        return (
            "**NOT a distinct channel** — the configured probe did not establish a channel "
            "distinct from this backend's own `release_view` command, and was refused before "
            "running; see the disposition reason for which cause"
        )
    if status == "skipped":
        return "**no distinct channel ran**"
    established = guard == "evaluated" if channel == "adapter-probe" else guard in (None, "evaluated")
    if status != "confirmed":
        if not established:
            return (
                "distinctness NOT established — the same-proxy guard reported "
                f"`{guard or 'not-run'}`, so this probe did NOT confirm this release"
            )
        return "a channel distinct from `gh release view`, which did NOT confirm this release"
    if established:
        return "a channel distinct from `gh release view`"
    return (
        "distinctness NOT established — the same-proxy guard reported "
        f"`{guard or 'not-run'}`, so this probe was never checked against the backend's own "
        "`release_view` command"
    )


def _status_section(record: Any, heading: str) -> tuple[str, list[str]] | None:
    """``(status, opening_lines)`` for a status-bearing record, or ``None`` when
    the record carries no status to render.

    Four section renderers repeated this guard verbatim. Shared so a future
    section cannot render a heading over a record it never checked."""
    if not isinstance(record, dict) or not str(record.get("status", "")).strip():
        return None
    return str(record["status"]), ["", heading, ""]


def distinct_channel_verification_lines(record: dict[str, Any] | None) -> list[str]:
    section = _status_section(record, "## Distinct-Channel Verification")
    if section is None:
        return []
    status, lines = section
    channel = record.get("channel", "unknown")
    # The distinctness claim is a CLAIM, and it was appended unconditionally —
    # including on `same-proxy-flagged` records, whose own observer field says
    # the probe was the same proxy, and on `skipped` records where no channel ran
    # at all (D8). The parenthetical now describes what actually happened.
    guard = record.get("same_proxy_guard")
    qualifier = _distinct_channel_qualifier(status, channel, guard)
    lines.append(f"- Rung-2 distinct-channel verdict: `{status}` via `{channel}` ({qualifier}).")
    if guard is not None:
        lines.append(f"- Same-proxy guard: `{guard}`")
    if (expected := record.get("expected_content")) and status == "confirmed":
        lines.append(f"- Response content checked for: `{expected}`")
    if establishes := record.get("establishes"):
        lines.append(f"- What this confirms: {establishes}")
    if not_established := record.get("does_not_establish"):
        lines.append(f"- What it does NOT confirm: {not_established}")
    if (fetched := record.get("fetched_url")) and fetched != record.get("url"):
        lines.append(f"- Redirected to: `{fetched}`")
    if observer := record.get("observer"):
        lines.append(f"- Observer identity: {observer}")
    if url := record.get("url"):
        lines.append(f"- Channel URL: `{url}`")
    if command := record.get("command"):
        lines.append(f"- Probe command: `{command}`")
    if (http_status := record.get("http_status")) is not None:
        lines.append(f"- HTTP status: `{http_status}`")
    if reason := record.get("reason"):
        lines.append(f"- Disposition reason: {reason}")
    lines.append(
        "- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was "
        "not silent; the honesty of this verdict is the human rung-2 disposition review."
    )
    return lines


def published_notes_audit_lines(record: dict[str, Any] | None) -> list[str]:
    """The post-create audit of the PUBLISHED release body.

    Rendered here because an advisory nobody reads is the same silent path the
    distinct-channel section exists to close: it previously lived only in the
    publish run's stdout JSON, which nothing re-reads after a release.
    """
    section = _status_section(record, "## Published Notes Audit")
    if section is None:
        return []
    status, lines = section
    lines.append(f"- Published release body audit: `{status}` (advisory; never blocks a publish).")
    if status == "advisory":
        lines.append(
            "- The published notes point at content that can change after publication. "
            "`gh release edit` is the remedy; the release itself is unaffected."
        )
        for advisory in record.get("advisories", []):
            lines.append(f"  - {advisory}")
    elif status == "clean":
        lines.append(f"- No mutable source-tree pointers found ({record.get('body_len', 0)} body bytes).")
    elif status == "unauthored":
        # Distinct from the not-audited statuses below, which mean the audit
        # could not LOOK. Here it looked: the release shipped a body with nothing
        # authored in it, and the remedy is the operator's, not the tooling's.
        lines.append(
            f"- The published body carries no authored notes ({record.get('body_len', 0)} body bytes) — "
            "this release shipped with a generated changelog line and nothing else. "
            "`gh release edit` is the remedy; the release itself is unaffected."
        )
        for advisory in record.get("advisories", []):
            lines.append(f"  - {advisory}")
    else:
        lines.append(
            "- The body was NOT audited, so this release's notes carry no pointer verdict at all."
        )
    if reason := record.get("reason"):
        lines.append(f"- Disposition reason: {reason}")
    return lines


def release_observer_lines(observer: dict[str, Any] | None) -> list[str]:
    section = _status_section(observer, "## Release Observer Record")
    if section is None:
        return []
    _status, lines = section
    if path := str(observer.get("path", "") or "").strip():
        lines.append(f"- Durable observer record: `{path}`.")
    else:
        lines.append("- Durable observer record: unavailable; see the capture disposition below.")
    lines.append(f"- Installed readback disposition: `{observer.get('status', 'unknown')}`.")
    if reason := observer.get("reason"):
        lines.append(f"- Capture disposition: {reason}")
    lines.append(
        "- Verdict ownership: this record embeds `distinct_channel_verification`; "
        "it does not declare a second release-success verdict."
    )
    return lines
