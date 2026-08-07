"""Whether a goal artifact is shaped enough to *pursue* via ``/goal``.

This is the only gate in front of activation, and it is deliberately narrower
than the full ``check_goal`` sweep. Both facts live here together: the readiness
verdict and the statement of what that verdict does NOT establish.

Lives beside ``goal_artifact_lib`` rather than inside it because readiness is its
own concept (marker + section presence + fence readability + operator discussion
+ draft frame).
Every collaborator is INJECTED by the caller -- the required-section tuple, the
artifact status, and the four functions this composes -- so nothing here reaches
back into the artifact library, and this module carries no sibling-loader
boilerplate to duplicate.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Before-phase placeholder marker the handoff auto-draft leaves until shaping
# fills it; its presence means `/goal` must fail-fast to `/achieve`.
UNSHAPED_MARKER = re.compile(r"to be filled by the achieve before-phase", re.IGNORECASE)

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)

# Activation checks only the minimum shape of this plan. It deliberately does
# not judge SHA values, reviewer quality, or proof truth; those stay with the
# closeout evidence and fresh-eye workflows.
CLOSEOUT_PLAN_FIELDS = (
    "Reviewed inputs:",
    "Frozen target:",
    "Fresh-eye:",
    "Verification lock:",
    "Complete flip:",
)

#: What a ``pursue_readiness`` verdict does NOT establish, carried in the payload
#: so the caller reads the answer's scope from the answer instead of re-deriving
#: it from the flag's help text. The full ``check_goal`` sweep is what covers these.
def _load_backlog_floor():
    """The backlog-recount floor, loaded by path like every other sibling here."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "goal_artifact_backlog",
        Path(__file__).resolve().parent / "goal_artifact_backlog.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_backlog.py not found beside goal_artifact_pursue.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BACKLOG = _load_backlog_floor()


SCOPE_NOT_CHECKED = (
    "status validity",
    "activation-line shape",
    "closeout evidence",
    "closeout binding values and final packet identity",
    "section CONTENT (headings are checked; what is under them is not)",
)


def _reason(
    *,
    placeholders: list[str],
    missing_sections: list[str],
    balanced: bool,
    discussion: dict[str, Any],
    discussion_warning: str,
    closeout_plan_missing_fields: list[str],
    closeout_plan_duplicate: bool,
    backlog_recount_missing_fields: list[str],
    activation_ready: bool,
) -> str:
    """Every reason this verdict refuses, not only the first one found.

    The old single-winner chain reported one branch and dropped the rest, so a
    goal that was both unshaped and missing sections read as only one of them and
    a second ``/goal`` attempt discovered the other. Clauses are joined, and each
    keeps its established wording so a caller matching on it still matches.

    The PASS sentence carries its scope too. It used to name only the marker
    fact -- `no Before-phase placeholders remain` -- while standing in for a
    verdict that now covers markers, headings, fences, and operator discussion,
    and that mismatch between a narrow measurement and a wide-sounding green is
    the class this gate was repaired for. The legacy `safe to pursue` substring
    is preserved so an existing matcher still matches.
    """
    if activation_ready:
        return (
            "shaped: no Before-phase placeholders remain, every required/portability heading is present, "
            "and the closeout-plan heading/minimum binding fields are present; safe to pursue via `/goal` -- "
            "field shape only, "
            "section content not checked"
        )
    clauses: list[str] = []
    if not balanced:
        clauses.append(
            "unreadable: an unclosed code fence makes the heading reading unestablished "
            "(fence masking fails open, so fenced headings would count as present) -- "
            "close the fence before `/goal`"
        )
    if placeholders:
        clauses.append(
            f"unshaped: {len(placeholders)} Before-phase placeholder(s) remain -- run "
            "the achieve Before-phase (`/achieve @<file>`) before `/goal`; `/goal` pursues "
            "only and does not shape"
        )
    if missing_sections:
        clauses.append(
            f"incomplete: {len(missing_sections)} required section heading(s) absent "
            "(" + ", ".join(missing_sections) + ") -- an artifact whose sections were never "
            "written carries no placeholder marker either, so run the achieve Before-phase "
            "(`/achieve @<file>`) before `/goal`"
        )
    if closeout_plan_missing_fields:
        clauses.append(
            "incomplete: Closeout Binding Plan field(s) absent or empty ("
            + ", ".join(closeout_plan_missing_fields)
            + ") -- fill the minimum plan fields before `/goal`"
        )
    if closeout_plan_duplicate:
        clauses.append(
            "incomplete: Closeout Binding Plan appears more than once -- keep one unambiguous plan before `/goal`"
        )
    if backlog_recount_missing_fields:
        clauses.append(
            "incomplete: backlog recount absent or empty ("
            + ", ".join(backlog_recount_missing_fields)
            + ") -- recount the tracker and record what this goal claims and does not; "
            "`Claims:`/`Not claimed:` may say `none`, but presence is the floor"
        )
    if discussion_warning:
        clauses.append(
            "operator discussion unresolved: consequential activation decisions are surfaced "
            "but not marked resolved -- resolve or confirm them before offering `/goal`"
        )
    elif not discussion["discussion_ready"]:
        clauses.append(
            "operator discussion required: consequential activation decisions are present "
            "but no non-empty `Discuss before activation:` summary was found"
        )
    return "; ".join(clauses)


def pursue_readiness(
    text: str,
    *,
    required_sections: tuple[str, ...],
    status: str | None,
    deploy_vocab: tuple[str, ...] | list[str] | None,
    mask_fences: Callable[[str], str],
    fences_balanced: Callable[[str], bool],
    discussion_readiness: Callable[..., dict[str, Any]],
    draft_frame_disposition: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Whether a goal is shaped enough to *pursue* via ``/goal``.

    Unshaped = a Before-phase placeholder marker still present (the handoff
    auto-draft state); on it ``/goal`` must fail-fast and route to ``/achieve``
    rather than shape. Shaping is the Before-phase's job; pursuing is ``/goal``'s.

    ``deploy_vocab`` (an achieve adapter's ``discussion_deploy_vocab``) is passed
    through to the discussion gate so the consumer-axis deploy vocabulary is
    adapter-provided, not a charness hardcode; ``None`` keeps the English default.

    **Section presence is part of the verdict.** "No placeholder marker" is not
    the same fact as "shaped", and phrasing the narrow answer in the wide
    vocabulary is how an artifact missing nine of its section headings was activated
    with `safe to pursue`. An artifact whose sections were never WRITTEN carries
    no placeholder markers either, so marker-absence was being read as
    shaping-presence. The sections this would otherwise skip (`Boundaries`,
    `Slice Plan`, `User Acceptance`) are what bound an autonomous run, so the
    fact gets teeth here rather than a warning beside a green. ``required_sections``
    is a strict subset of what ``check_goal`` already requires, so nothing
    pursuable under the old rule is refused unless those headings are genuinely
    absent.

    ``fences_balanced`` is required for the same reason the heading check is.
    ``mask_fences`` FAILS OPEN on odd fence parity and returns the raw text, so on
    an unbalanced document every fenced ``## Heading`` counts as present -- an
    artifact with 14 headings inside one unclosed fence and no real sections would
    otherwise read `sections_complete: true`. ``check_goal`` already refuses an
    unbalanced document; this gate refuses it too rather than rendering a heading
    verdict over a reading nobody established.
    """
    masked = mask_fences(text)
    balanced = fences_balanced(text)
    placeholders = UNSHAPED_MARKER.findall(masked)
    discussion = discussion_readiness(text, deploy_vocab=deploy_vocab)
    disposition = draft_frame_disposition(text, status=status, masked=masked)
    present = {match.group(1).strip() for match in _H2.finditer(masked)}
    missing_sections = [section for section in required_sections if section not in present]
    closeout_plan_missing_fields: list[str] = []
    closeout_plan_duplicate = False
    if "Closeout Binding Plan" in required_sections:
        headings = list(_H2.finditer(masked))
        closeout_headings = [
            heading
            for heading in headings
            if heading.group(1).strip() == "Closeout Binding Plan"
        ]
        closeout_plan_duplicate = len(closeout_headings) > 1
        if len(closeout_headings) == 1:
            heading = closeout_headings[0]
            index = headings.index(heading)
            section_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
            body = masked[heading.end():section_end]
            for field in CLOSEOUT_PLAN_FIELDS:
                field_pattern = re.compile(
                    rf"^[ \t>*-]*[`*_~]*{re.escape(field)}[`*_~]*[ \t]+(.+)$",
                    re.MULTILINE,
                )
                match = field_pattern.search(body)
                if match is None or not re.sub(r"[\s`*_~\[\](){}<>#|:-]+", "", match.group(1)):
                    closeout_plan_missing_fields.append(field)
    # `shape_ready` keeps its established meaning (no Before-phase marker) so the
    # placeholder signal stays readable on its own; completeness is a separate
    # dimension that gates activation alongside it.
    shape_ready = not placeholders
    # DRAFT ONLY, exactly like the closeout-binding-plan floor above, and for the same
    # reason: this is a SHAPING floor. `/goal` pursues a draft, so the recount belongs to
    # the phase that decides scope. Grading an already-`active`/`blocked`/`complete`
    # artifact against it would be retroactive -- the artifact's scope was set before the
    # rule existed and cannot be re-decided now -- and it is what made three legacy
    # heading-compatibility fixtures refuse.
    #
    # The date grandfather inside `check` covers DATED pre-rule drafts; this covers the
    # undated legacy ones. Both are needed: `applies` fails CLOSED on a missing `Created:`
    # so the floor cannot be removed by deleting one line, which is right for a draft and
    # wrong for a historical record.
    backlog_report = (
        _BACKLOG.check(text)
        if status == "draft"
        else {"applies": False, "ok": True, "evaluated": False, "missing_fields": [],
              "reason": f"not evaluated: backlog recount is a shaping floor and status is {status!r}"}
    )
    backlog_recount_missing_fields = list(backlog_report.get("missing_fields") or [])
    activation_ready = (
        shape_ready
        and balanced
        and not missing_sections
        and not closeout_plan_missing_fields
        and not closeout_plan_duplicate
        and not backlog_recount_missing_fields
        and discussion["discussion_ready"]
    )
    discussion_warning = (
        "Consequential activation decisions are surfaced but unresolved. "
        "Resolve or explicitly ask about them in the transcript before offering `/goal`, "
        "then mark the summary `RESOLVED`, `CONFIRMED`, or `APPROVED`."
        if discussion["discussion_required"] and discussion["discussion_summary_present"] and not discussion["discussion_resolved"]
        else ""
    )
    return {
        "pursue_ready": activation_ready,
        "shape_ready": shape_ready,
        "sections_complete": not missing_sections,
        "missing_sections": missing_sections,
        "closeout_plan_missing_fields": closeout_plan_missing_fields,
        "closeout_plan_duplicate": closeout_plan_duplicate,
        "backlog_recount": backlog_report,
        "backlog_recount_missing_fields": backlog_recount_missing_fields,
        # False means the heading facts above were read from a FAIL-OPEN mask (the
        # raw text, fenced examples included), so they are not established.
        "sections_reading_established": balanced,
        "fences_balanced": balanced,
        "scope_not_checked": SCOPE_NOT_CHECKED,
        "activation_ready": activation_ready,
        "placeholder_count": len(placeholders),
        "reason": _reason(
            placeholders=placeholders,
            missing_sections=missing_sections,
            balanced=balanced,
            discussion=discussion,
            discussion_warning=discussion_warning,
            closeout_plan_missing_fields=closeout_plan_missing_fields,
            closeout_plan_duplicate=closeout_plan_duplicate,
            backlog_recount_missing_fields=backlog_recount_missing_fields,
            activation_ready=activation_ready,
        ),
        "activation_discussion_warning": discussion_warning,
        "draft_frame_disposition_present": disposition["present"],
        "draft_frame_warning": disposition["warning"],
        **discussion,
    }
