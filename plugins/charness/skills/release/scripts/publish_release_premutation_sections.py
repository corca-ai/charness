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
    """Operator-supplied prose with every leading heading run removed, to a FIXED POINT.

    One `re.sub` was not enough and the difference was a blocker: the pattern's `#+`
    cannot cross whitespace, so `# ## Release State` lost only the first marker and
    emitted `## Release State` at column 0 -- a real heading, above the genuine one,
    which is where `audit_public_release_narrative` then judged the five-entry ledger
    from. `#\\t##`, `  #  ###` and any deeper nesting had the same shape.

    Belt to the braces of `quote_lines`: the blockquote prefix is what actually keeps
    these lines out of the audit's heading grammar. This runs first so the quoted text
    reads as prose rather than as markers the reader has to discount.
    """
    lines = []
    for raw in text.strip().splitlines():
        line = raw.rstrip()
        while True:
            stripped = _HEADING_PREFIX_RE.sub("", line)
            if stripped == line:
                break
            line = stripped
        lines.append(line)
    return lines


def quote_lines(lines: list[str]) -> list[str]:
    """Operator prose as a blockquote, which is what makes it structurally inert.

    Demotion is a character-prefix filter defending a document-structure invariant,
    and three separate constructs walked past it. Quoting closes the class instead of
    growing the blacklist, because every reader of this record anchors its patterns
    at line start:

    * `_release_state_block` matches `line.strip() == "## Release State"` and
      terminates on `line.startswith("## ")`; `> ## Release State` satisfies neither.
    * `validate_current_pointer_freshness.TARGET_VERSION_RE` anchors
      `^[ \\t]*(?:[-*][ \\t]*)?target version:` -- a `>` prefix does not match, so a
      rationale mentioning a rejected target version can no longer make the record
      "carry disagreeing target-version claims". That gate fires on every later push,
      and on the claims lane the poisoned record is already TAGGED and published.
    * `audit_public_release_narrative._FENCE_RE` anchors ` ``` ` at line start, so an
      unterminated fence in the rationale can no longer blank the rest of the record
      (which suppressed even the blocker that would have explained it).

    What quoting does NOT close is `<!--`: an HTML comment hides everything after it
    from the RENDERED document a human reads on GitHub, while every substring audit
    still passes over the raw bytes. That one is refused at argument time.
    """
    return [f"> {line}" if line else ">" for line in lines]


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
    absent = [
        "- Bump rationale: NOT recorded by this helper invocation. `version-policy.md` "
        "requires a stated rationale whenever the bump level is debatable; this record "
        "carries none, so the level above is an unexplained judgment call."
    ]
    # Absence is decided on the RENDERED body, not on the raw argument. Deciding on the
    # argument meant `--bump-rationale '#'` was truthy, demoted to `""`, and emitted the
    # heading over an empty body with no absence sentence -- inverting this docstring's
    # own guarantee, because a reader who sees the section infers one was supplied.
    body = demote_headings(bump_rationale or "")
    if not any(line.strip() for line in body):
        return lines + absent
    return lines + quote_lines(body)


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
    # `list`, not truthiness: `surfaces` reaching here as an int raised TypeError inside
    # the record writer -- a traceback between the mutation and the record -- and as a
    # STRING it rendered `len("abc")` as "across 3 read surface(s)", a wrong count stated
    # as a measurement. A count is a claim; it is made only over something countable.
    raw_surfaces = version_drift_check.get("surfaces")
    surfaces = raw_surfaces if isinstance(raw_surfaces, (list, tuple)) else []
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
    # Any non-mapping, not just `None`: a list or a string reaching here raised
    # AttributeError inside the record writer, which is a traceback where a section
    # belongs. Unreachable from today's in-process producers; a renderer on this surface
    # should not depend on that staying true.
    if not isinstance(payload, dict):
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
    raw_commands = payload.get("commands")
    commands = raw_commands if isinstance(raw_commands, (list, tuple)) else []
    if commands:
        lines.append("- Focused preflight commands:")
        lines.extend(f"  - `{' '.join(command)}`" for command in commands)
    else:
        lines.append("- Focused preflight commands: none planned.")
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
    # The token is never alone. `claims_review_lines` argues the rule this follows: a
    # reader who sees a status word infers the thing happened, so a status that is NOT a
    # clean execution states its negative property in words. `not_run` and `failed` are
    # both absences of a passing preflight and neither may read as one; an unrecognised
    # status is treated as an absence too, because a backticked token this module cannot
    # interpret would otherwise render as an authoritative verdict.
    status = str(execution.get("status"))
    lines.append(f"- Focused preflight execution: `{status}`.")
    if status != "passed":
        lines.append(
            "- This is a recorded absence, not a passing preflight: no focused adapter "
            "check is claimed to have completed successfully for this release."
        )
    if reason := execution.get("reason"):
        lines.append(f"  - Reason: {reason}")
    raw_executed = execution.get("executed_commands")
    executed = raw_executed if isinstance(raw_executed, (list, tuple)) else []
    lines.extend(f"  - executed: `{command}`" for command in executed)
    if failed := execution.get("failed_command"):
        lines.append(f"  - failed: `{failed}`")
    return lines
