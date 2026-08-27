"""Whether a goal artifact is shaped enough to *pursue* via ``/goal``.

This is the only gate in front of activation, and it is deliberately narrower
than the full ``check_goal`` sweep. Both facts live here together: the readiness
verdict and the statement of what that verdict does NOT establish.

Lives beside ``goal_artifact_lib`` rather than inside it because readiness is its
own concept (marker + section presence + fence readability + operator discussion
+ draft frame + lifecycle and hollow-section refusal).
Every collaborator is INJECTED by the caller -- the required-section tuple, the
artifact status, and the four functions this composes -- so nothing here reaches
back into the artifact library, and this module carries no sibling-loader
boilerplate to duplicate.

Lifecycle token normalization and terminal/shaping applicability are owned by
``goal_artifact_lifecycle``. The public names remain re-exported here so existing
callers keep their import address while readiness composition stays here.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Before-phase placeholder marker the achieve draft leaves until shaping fills
# it; its presence means `/goal` must fail-fast to `/achieve`.
UNSHAPED_MARKER = re.compile(r"to be filled by the achieve before-phase", re.IGNORECASE)

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)

#: What a ``pursue_readiness`` verdict does NOT establish, carried in the payload
#: so the caller reads the answer's scope from the answer instead of re-deriving
#: it from the flag's help text. The full ``check_goal`` sweep is what covers these.
def _load_sibling(module_name: str):
    """Load a sibling by path so this exported skill remains standalone."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside goal_artifact_pursue.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_backlog_floor():
    """Compatibility seam for callers that diagnose the backlog sibling."""
    return _load_sibling("goal_artifact_backlog")


_BACKLOG = _load_backlog_floor()
_LIFECYCLE = _load_sibling("goal_artifact_lifecycle")

NON_SHAPING_STATUSES = _LIFECYCLE.NON_SHAPING_STATUSES
TERMINAL_STATUSES = _LIFECYCLE.TERMINAL_STATUSES
is_shaping_status = _LIFECYCLE.is_shaping_status
status_token = _LIFECYCLE.status_token
is_terminal_status = _LIFECYCLE.is_terminal_status


SCOPE_NOT_CHECKED = (
    "status validity",
    "activation-line shape",
    "closeout evidence",
    "section CONTENT beyond the hollow/template and backlog-recount fields this reads",
)


def _reason(
    *,
    placeholders: list[str],
    missing_sections: list[str],
    balanced: bool,
    discussion: dict[str, Any],
    discussion_warning: str,
    duplicate_sections: list[str],
    backlog_recount_missing_fields: list[str],
    backlog_state: str,
    activation_ready: bool,
    hollow_reason: str = "",
    terminal_reason: str = "",
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
        # The backlog clause is CONDITIONAL on the floor having run. Saying "the backlog
        # recount is recorded" on a non-draft, where it was skipped entirely, would be the
        # narrow-measurement-in-wide-vocabulary defect this docstring warns about -- and
        # the pass sentence read identically in both cases until round-1 review said so.
        # THREE states, not a boolean. `applies: False` has TWO producers -- the
        # non-shaping-status skip AND the `Created:` grandfather -- and collapsing them
        # made the sentence assert "this artifact is not a draft" about a pre-rule DRAFT.
        # By this floor's own denominators that is 7 of the 8 live drafts, so the false
        # branch was the MAJORITY draft path, not an edge case: a narrow measurement in
        # wrong vocabulary, inside the sentence added to stop exactly that.
        if backlog_state == "recorded":
            backlog_clause = "the backlog recount is recorded"
        elif backlog_state == "status-skipped":
            backlog_clause = "the backlog recount was NOT evaluated (shaping floor; this artifact is not a draft)"
        else:
            backlog_clause = (
                "the backlog recount was NOT evaluated (this artifact's `Created:` date precedes the rule)"
            )
        return (
            "shaped: no Before-phase placeholders remain, every required/portability heading is present, "
            f"{backlog_clause}; safe to pursue via `/goal` -- "
            "field shape only, "
            "section content beyond the hollow/template checks and those fields not checked"
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
    if terminal_reason:
        clauses.append("non-pursuable: " + terminal_reason)
    if hollow_reason:
        clauses.append("hollow: " + hollow_reason)
    if duplicate_sections:
        clauses.append(
            "duplicate sections: " + ", ".join(duplicate_sections)
            + " -- keep one required or portability section before `/goal`"
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
    duplicate_sections: list[str],
    status: str | None,
    deploy_vocab: tuple[str, ...] | list[str] | None,
    mask_fences: Callable[[str], str],
    fences_balanced: Callable[[str], bool],
    discussion_readiness: Callable[..., dict[str, Any]],
    draft_frame_disposition: Callable[..., dict[str, Any]],
    hollow_sections: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Whether a goal is shaped enough to *pursue* via ``/goal``.

    Unshaped = a Before-phase placeholder marker still present (the achieve
    draft state); on it ``/goal`` must fail-fast and route to ``/achieve``
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
    lifecycle = _LIFECYCLE.assess(status)
    terminal = lifecycle["terminal"]
    terminal_status_token = lifecycle["status_token"]
    terminal_reason = lifecycle["terminal_reason"]
    discussion = discussion_readiness(text, deploy_vocab=deploy_vocab)
    disposition = draft_frame_disposition(text, status=status, masked=masked)
    present = {match.group(1).strip() for match in _H2.finditer(masked)}
    missing_sections = [section for section in required_sections if section not in present]
    # PRESENT is not WRITTEN. A bare heading -- or a section still carrying the
    # scaffold's own guidance prose -- passed every heading check while saying
    # nothing about this goal, so `pursue-ready` came to mean "has the right
    # headings". Reported for every required section; refused only for the
    # shaping-time ones, because run-filled sections are template-identical at
    # draft time BY DESIGN and refusing those would trade one false verdict for
    # another. Active work is still pursuable work, so it must not bypass this
    # floor merely because its status is no longer `draft`. Terminal records are
    # kept out of the classifier: lifecycle refusal is their independent reason,
    # and historical hollow/run-filled sections are not re-labeled as blockers
    # on a record nobody may activate.
    hollow_evaluation_applies = lifecycle["hollow_evaluation_applies"]
    hollow_report = (
        hollow_sections(masked, tuple(required_sections))
        if hollow_sections is not None and hollow_evaluation_applies
        else {"hollow": [], "empty": [], "still_template_text": [], "blocking": [],
              "run_filled_hollow": [], "evaluated": False,
              "reason": (
                  "not evaluated: no hollow-section classifier was supplied"
                  if hollow_sections is None
                  else (
                      f"not evaluated: terminal status {terminal_status_token!r} is refused by lifecycle"
                      if terminal
                      else f"not evaluated: hollow-section shaping floor does not apply to status {status!r}"
                  )
              )}
    )
    hollow_blocking = list(hollow_report.get("blocking") or [])
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
    # FAIL CLOSED on the status too, not just on `Created:`. Round-1 review found that
    # `status == "draft"` made the floor removable by deleting the `Status:` line or
    # writing `Status: Draft` -- `read_status` returns None or the raw string, and
    # `--pursue-ready` explicitly does not validate status -- which also disarmed the
    # closeout-plan floor in the same edit. The docstring below claimed the opposite. So
    # the skip is keyed to a RECOGNISED non-shaping status: missing, mis-cased or
    # unrecognised all evaluate.
    backlog_report = (
        _BACKLOG.check(text)
        if lifecycle["shaping_floor_applies"]
        else {"applies": False, "ok": True, "evaluated": False, "missing_fields": [],
              "status_skipped": True,
              "reason": f"not evaluated: backlog recount is a shaping floor and status is {status!r}"}
    )
    backlog_recount_missing_fields = list(backlog_report.get("missing_fields") or [])
    activation_ready = (
        not terminal
        and shape_ready
        and balanced
        and not missing_sections
        and not hollow_blocking
        and not duplicate_sections
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
    readiness_blockers: list[dict[str, Any]] = []
    if terminal:
        readiness_blockers.append({
            "kind": "terminal_status",
            "status": terminal_status_token,
            "reason": terminal_reason,
        })
    if hollow_blocking:
        readiness_blockers.append({
            "kind": "hollow_sections",
            "sections": hollow_blocking,
            "reason": hollow_report.get("reason", ""),
        })
    if duplicate_sections:
        readiness_blockers.append({
            "kind": "duplicate_sections",
            "sections": duplicate_sections,
            "reason": "required or portability H2 section appears more than once",
        })
    return {
        "pursue_ready": activation_ready,
        "shape_ready": shape_ready,
        "sections_complete": not missing_sections,
        "missing_sections": missing_sections,
        "duplicate_sections": duplicate_sections,
        "backlog_recount": backlog_report,
        "backlog_recount_missing_fields": backlog_recount_missing_fields,
        # PRESENT vs WRITTEN. Published as a structured report, not folded into
        # the boolean, because the whole complaint was that a single
        # ready/not-ready verdict made the caller re-read the artifact to find
        # out WHICH sections were hollow.
        "hollow_sections": hollow_report,
        "hollow_blocking_sections": hollow_blocking,
        "lifecycle": {
            "status": lifecycle["status"],
            "status_token": lifecycle["status_token"],
            "terminal": lifecycle["terminal"],
            "pursuit_allowed": lifecycle["pursuit_allowed"],
        },
        "readiness_blockers": readiness_blockers,
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
            duplicate_sections=duplicate_sections,
            backlog_recount_missing_fields=backlog_recount_missing_fields,
            hollow_reason=hollow_report.get("reason", "") if hollow_blocking else "",
            backlog_state=(
                "recorded"
                if backlog_report.get("applies")
                else "status-skipped"
                if backlog_report.get("status_skipped")
                else "pre-rule"
            ),
            activation_ready=activation_ready,
            terminal_reason=terminal_reason,
        ),
        "activation_discussion_warning": discussion_warning,
        "draft_frame_disposition_present": disposition["present"],
        "draft_frame_warning": disposition["warning"],
        **discussion,
    }
