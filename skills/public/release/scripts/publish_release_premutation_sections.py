"""Record sections for what happened BEFORE the release mutation.

One concept, not a length-cap spill (D33): the bump rationale, the version-drift
check, and the focused adapter preflight are the three things the release record
says about the state of the repo before anything irreversible ran. All three were
repaired together by the v6.0.1 claims round, which found that none of them was
bound to what the helper actually did -- the rationale had no field at all, and the
other two rendered a claim whether or not a check produced it. Their sibling module
`publish_release_verification_sections` owns the other end of the same timeline.
"""

from __future__ import annotations

import re
from typing import Any

_HEADING_PREFIX_RE = re.compile(r"^\s*#+\s*")


def demote_headings(text: str) -> list[str]:
    """Operator-supplied prose as lines that cannot become record HEADINGS.

    The record is not just read: `audit_public_release_narrative` locates the
    release-state ledger as the span between `## Release State` and the next `## `
    line, so a `##` line inside operator prose moves where that ledger is judged to
    start and end. Demoted rather than refused -- the value is a human explanation
    supplied after the critique gate, and a refusal there costs a release cycle to
    reword prose. The record-state sentinel is a separate rule refused at argument
    parsing (`assert_no_record_sentinel`), because demoting that one would silently
    change what the operator wrote about release state.
    """
    return [_HEADING_PREFIX_RE.sub("", line.rstrip()) for line in text.strip().splitlines()]


def bump_rationale_lines(bump_rationale: str | None) -> list[str]:
    """Why THIS bump level, in the artifact a reader outside the session gets.

    `version-policy.md` requires a stated rationale whenever the level is debatable,
    and until now this template emitted no field for one: a v6.0.1 preparer's
    patch-vs-minor argument had to live in a separate review artifact because
    re-running the helper could not put it here. An absent rationale gets a sentence
    that says the level is unexplained rather than no section at all -- a reader who
    sees no section infers there was nothing to explain.
    """
    lines = ["", "## Bump Rationale", ""]
    text = (bump_rationale or "").strip()
    if not text:
        return lines + [
            "- Bump rationale: NOT recorded by this helper invocation. `version-policy.md` "
            "requires a stated rationale whenever the bump level is debatable; this record "
            "carries none, so the level above is an unexplained judgment call."
        ]
    return lines + demote_headings(text)


def version_drift_lines(version_drift_check: dict[str, Any] | None) -> list[str]:
    """The no-drift sentence, bound to a check that ran, or the absence of one.

    It used to be an unconditional literal in the `## Verification` list: the record
    read `current_release.py reported no version drift` identically whether the check
    ran, did not run, or found drift. The lanes really do differ -- the resume lane
    that publishes wrote that sentence while calling no such check -- so the unchecked
    state gets its own sentence instead of inheriting the claim.
    """
    if not isinstance(version_drift_check, dict) or not version_drift_check.get("checked_version"):
        return [
            "- Version drift check: NOT recorded by this helper invocation, so this record "
            "makes no no-drift claim about packaging and generated install surfaces."
        ]
    surfaces = version_drift_check.get("surfaces") or []
    scope = f" across {len(surfaces)} read surface(s)" if surfaces else ""
    stage = version_drift_check.get("stage") or "unrecorded stage"
    return [
        f"- `current_release.py` reported no version drift{scope} against target "
        f"`{version_drift_check['checked_version']}`, checked at `{stage}`."
    ]


def pending_payload_section(
    payload: dict[str, Any] | None, *, heading: str, pending: str, status_label: str
) -> tuple[str | None, list[str]]:
    """``(status, opening_lines)`` for a section whose payload may not exist yet.

    ``status`` is ``None`` once the caller has emitted the pending line and has
    nothing further to render. Two renderers carried this shape verbatim; shared so
    a third cannot render a status heading over a payload that was never produced.
    """
    lines = ["", heading, ""]
    if payload is None:
        return None, lines + [pending]
    status = str(payload.get("status", "unknown"))
    lines.append(f"- {status_label}: `{status}`.")
    return status, lines


def labeled_code_list(label: str, values: Any) -> list[str]:
    """``- <label>:`` over backticked children, or nothing when there are none.

    A header with no children below it reads as an empty finding rather than an
    absent one, so the label and its items are emitted together or not at all.
    """
    items = [value for value in values or [] if value]
    return [f"- {label}:", *(f"  - `{value}`" for value in items)] if items else []


def release_adapter_preflight_lines(payload: dict[str, Any] | None) -> list[str]:
    status, lines = pending_payload_section(
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
    lines.extend(labeled_code_list("Adapter paths in release delta", payload.get("adapter_paths", [])))
    lines.extend(labeled_code_list("Changed adapter fields", payload.get("changed_fields", [])))
    commands = payload.get("commands", [])
    if commands:
        lines.append("- Focused preflight commands:")
        lines.extend(f"  - `{' '.join(command)}`" for command in commands)
    else:
        lines.append("- Focused preflight commands: none executed.")
    # `status: required` plus a command list is a PLAN, and the record rendered nothing
    # else: a reader could not tell whether the commands ran, and on the resume lane that
    # publishes they did not. The execution disposition is written by
    # `run_release_adapter_preflight` onto this same payload; its absence is stated rather
    # than left to be read as a satisfied requirement.
    execution = payload.get("execution")
    if not isinstance(execution, dict) or not execution.get("status"):
        lines.append(
            "- Focused preflight execution: NOT recorded by this helper invocation; this "
            "record does not establish that the commands above ran."
        )
        return lines
    lines.append(f"- Focused preflight execution: `{execution.get('status')}`.")
    if reason := execution.get("reason"):
        lines.append(f"  - Reason: {reason}")
    lines.extend(f"  - executed: `{command}`" for command in execution.get("executed_commands", []))
    if failed := execution.get("failed_command"):
        lines.append(f"  - failed: `{failed}`")
    return lines
