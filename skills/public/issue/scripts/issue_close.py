from __future__ import annotations

import json
import runpy
from functools import partial
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BACKEND = _load_local("issue_backend", "issue_close_backend")
_run_backend = _BACKEND.run_backend
_resolve_op = _BACKEND.resolve_op
answer_repo = _BACKEND.answer_repo
require_exact_issue_identity = _BACKEND.require_exact_issue_identity
BACKEND_TIMEOUT_SECONDS = _BACKEND.BACKEND_TIMEOUT_SECONDS
_CLOSE_COMMENT_FLOOR = _load_local("issue_close_comment_floor")
# Bound directly rather than reached through `_CLOSE_COMMENT_FLOOR._BODY`: a
# three-deep private chain across two module boundaries becomes an AttributeError
# on the carrier that writes to GitHub the moment either module is split.
_strip_code_fences = _load_local("issue_markdown_lib").strip_code_fences
_AUTHZ = _load_local("issue_closeout_authorization")
_consolidated = _load_local("issue_consolidated_closeout")
_consolidation_readback = _load_local("issue_consolidation_readback")
_state_readback = _load_local("issue_state_readback")
_goal_run_guard = _load_local("issue_goal_run_guard")
_COMMANDS = _load_local("issue_close_commands")
_MUTATION = _load_local("issue_close_mutation", "issue_close_mutation_stages")
_RETRY = _load_local("issue_close_retry", "issue_close_retry_carrier")
_PREPARE = _load_local("issue_close_prepare", "issue_close_prepare_carrier")
GH_COMMENT_DEFAULT = _COMMANDS.GH_COMMENT_DEFAULT
GH_CLOSE_DEFAULT = _COMMANDS.GH_CLOSE_DEFAULT
GH_VIEW_DEFAULT = _COMMANDS.GH_VIEW_DEFAULT
GH_VIEW_TARGET_DEFAULT = _COMMANDS.GH_VIEW_TARGET_DEFAULT
COMMENT_PLACEHOLDERS = _COMMANDS.COMMENT_PLACEHOLDERS
CLOSE_PLACEHOLDERS = _COMMANDS.CLOSE_PLACEHOLDERS
VIEW_PLACEHOLDERS = _COMMANDS.VIEW_PLACEHOLDERS


CloseMutationError = _MUTATION.CloseMutationError


def _authorize_direct_close(
    *, repo: str, number: int, repo_root: Path, body: str, manual_target_declaration: str | None
) -> dict[str, Any]:
    """Authorize the manual close carrier before any backend call.

    The manual declaration is required only when a PROTECTED target is in play. Asking
    every consumer's ordinary `close-with-comment` for a new mandatory flag would be a
    global floor change smuggled in as a scoped fix, so the permissive probe runs
    first and the declaration is demanded only once the gate says it applies.
    """
    probe = _AUTHZ.authorize(
        invoked_targets=[{"repository": repo, "issue_number": number, "source": "cli-target"}],
        carrier_targets=[],
        carrier_source="close-with-comment",
        repo_root=repo_root,
    )
    if not probe.get("applies"):
        return probe
    if probe.get("refusal") not in (None, "matrix_incomplete", "missing_invoked_target"):
        # The probe already knows the definitive answer (a foreign repository, an
        # out-of-scope carrier, a consumer-owned row). Demanding a manual declaration
        # first would send the operator to supply a flag that cannot possibly help, so
        # the real refusal is surfaced instead of being replaced by our own error text.
        raise RuntimeError(_AUTHZ.refusal_message(probe))
    declared = _AUTHZ.parse_manual_declaration(manual_target_declaration, repo, number)
    return _AUTHZ.enforce(
        invoked_targets=declared,
        carrier_targets=[{"repository": repo, "issue_number": number, "source": "cli-target"}],
        carrier_source="close-with-comment",
        repo_root=repo_root,
    )


def _refuse_completed_consolidation(classification: str, reason: str) -> None:
    """A `consolidated` close claims nothing about the defect, so it must not land on
    the tracker as `completed`. Bounded review found this unwired: the module that
    owns the disposition declared `REQUIRED_CLOSE_REASON = "not planned"` and nothing
    read it, so twenty closes asserting "moved" would have rendered publicly as
    "completed" -- the repair claim the disposition refuses in prose, asserted on the
    one channel outside this repo's prose. Refused rather than silently corrected: a
    caller that asked for `completed` on a consolidation has a contradiction to
    resolve, not a default to inherit.

    One owner called from BOTH the carrier evaluation and `close_with_comment`. The
    second call is not a duplicate check: it preserves this refusal's position ahead
    of the body-file read, which is where it has always been, while still guarding
    the extracted evaluation for any caller that enters there.
    """
    if classification != _consolidated.CLASSIFICATION:
        return
    required = _consolidated.REQUIRED_CLOSE_REASON
    if reason != required:
        raise RuntimeError(
            f"classification `{classification}` requires --reason {required!r} "
            f"(got {reason!r}): a consolidated close claims nothing about the defect, "
            "so the tracker must not render it as a completed close"
        )


def _refuse_goal_run_target(
    *, repo: str, number: int, backend: dict[str, Any]
) -> None:
    """Read the target body before generic close can emit any side effect."""
    target_view_argv = _resolve_op(
        backend,
        "view",
        GH_VIEW_TARGET_DEFAULT,
        VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number"}),
        repo=repo,
        number=str(number),
        json_fields="number,state,url,body",
    )
    target_result = _run_backend(target_view_argv)
    if target_result.returncode != 0:
        raise RuntimeError(
            "target issue body readback failed; no comment or close was attempted: "
            f"view_exit={target_result.returncode} "
            f"view_stderr={target_result.stderr.strip()!r}"
        )
    try:
        target_state = json.loads(target_result.stdout)
    except Exception as exc:
        raise RuntimeError(f"target issue body readback returned invalid JSON: {exc}") from exc
    require_exact_issue_identity(
        target_state,
        expected_repo=repo,
        expected_number=number,
        context="target issue body readback",
    )
    _goal_run_guard.refuse_generic_close(target_state.get("body"), context="target issue body")


def _check_goal_run_target(
    *, repo: str, number: int, backend: dict[str, Any], authorized: bool
) -> None:
    if not authorized:
        _refuse_goal_run_target(repo=repo, number=number, backend=backend)


def evaluate_close_comment_carrier(
    repo: str,
    number: int,
    body: str,
    *,
    repo_root: Path,
    classification: str,
    backend: dict[str, Any],
    reason: str = "completed",
    manual_target_declaration: str | None = None,
) -> dict[str, Any]:
    """Everything the BODY AND TARGET decide before `close_with_comment` mutates.

    Extracted so the carrier's verdict can be tested without mutating GitHub.
    The readback wiring below lives here rather than in the floor, so tests call
    this carrier boundary when they need the complete pre-mutation verdict.

    NOT everything `close_with_comment` decides before its first irreversible act.
    These refusals deliberately stay with the caller, because they are about the
    BACKEND rather than the closeout body, and an `ok` verdict here does not clear
    any of them: the body-file existence check; the `comment`, `close` and `view`
    `_resolve_op` template validations, including the `required={repo, number}`
    identity floor on the view template; and the refusal of a non-`gh` backend that
    declares no `commands.view` -- "comment plus close command success is not issue
    closeout". A caller that posts and closes on the strength of this report alone
    drops all five.
    """
    _refuse_completed_consolidation(classification, reason)
    # Authorization runs before BOTH backend mutations, not just the close. A comment
    # posted on the wrong issue is already an external side effect that cannot be
    # taken back, and this function's own error path documents that the close can fail
    # after the comment has landed — so "authorize before the close" would be a check
    # placed after the first irreversible act.
    authorization = _authorize_direct_close(
        repo=repo, number=number, repo_root=repo_root, body=body,
        manual_target_declaration=manual_target_declaration,
    )
    # The four TRACKER readbacks, performed BEFORE the floor and therefore before the
    # comment and the close. A consolidated close is required to use this carrier, so
    # this is the last point at which "the destination exists, is open, and names this
    # issue" can still be checked while it is a question rather than a regret.
    readback = _consolidation_readback.readbacks_for_closeout(
        numbers=[number],
        destinations=_consolidated.destinations(
            "\n".join(_strip_code_fences(body))
        ),
        fetch=lambda dest: _state_readback.view_issue_state(
            repo_root, repo=repo, number=dest, backend=backend,
            json_fields="number,state,url,body",
        ),
        applies=classification == _consolidated.CLASSIFICATION,
        expected_repo=repo,
        answer_repo=_BACKEND.answer_repo,
    )
    floor_report = _CLOSE_COMMENT_FLOOR.evaluate_close_comment_floor(
        repo_root=repo_root,
        body=body,
        classification=classification,
        number=number,
        repo=repo,
        consolidation_readback=readback,
    )
    floor_report["closeout_authorization"] = authorization
    return floor_report


def _resolve_close_commands(
    backend: dict[str, Any],
    *,
    repo: str,
    number: int,
    body_file: Path,
    reason: str,
) -> tuple[list[str], list[str], list[str] | None]:
    comment_argv = _resolve_op(
        backend,
        "comment",
        GH_COMMENT_DEFAULT,
        COMMENT_PLACEHOLDERS,
        repo=repo,
        number=str(number),
        body_file=str(body_file),
        reason=reason,
    )
    close_argv = _resolve_op(
        backend,
        "close",
        GH_CLOSE_DEFAULT,
        CLOSE_PLACEHOLDERS,
        repo=repo,
        number=str(number),
        reason=reason,
    )
    commands = backend.get("commands") or {}
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "close state verification requires backend commands.view; "
            "comment plus close command success is not issue closeout"
        )
    view_argv = None
    if backend.get("id", "gh") == "gh" or commands.get("view") is not None:
        view_argv = _resolve_op(
            backend,
            "view",
            GH_VIEW_DEFAULT,
            VIEW_PLACEHOLDERS,
            required=frozenset({"repo", "number"}),
            repo=repo,
            number=str(number),
            json_fields="number,state,url",
        )
    return comment_argv, close_argv, view_argv


def _read_preflight_state(
    view_argv: list[str],
    *,
    repo: str,
    number: int,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    if existing is None:
        result = _run_backend(view_argv)
        if result.returncode != 0:
            raise RuntimeError(
                "pre-mutation issue readback failed; no comment or close was attempted: "
                f"view_exit={result.returncode} view_stderr={result.stderr.strip()!r}"
            )
        try:
            existing = json.loads(result.stdout)
        except Exception as exc:
            raise RuntimeError(f"pre-mutation issue readback returned invalid JSON: {exc}") from exc
    require_exact_issue_identity(
        existing,
        expected_repo=repo,
        expected_number=number,
        context="pre-mutation issue readback",
    )
    return existing


_prepare_close_mutation = partial(
    _PREPARE.prepare,
    evaluate=evaluate_close_comment_carrier,
    resolve_commands=_resolve_close_commands,
    read_preflight=_read_preflight_state,
    check_target=_check_goal_run_target,
    format_failure=_CLOSE_COMMENT_FLOOR.format_close_comment_floor_failure,
    guard_body=_goal_run_guard.refuse_generic_close,
    refuse_reason=_refuse_completed_consolidation,
)


def close_with_comment(
    repo: str,
    number: int,
    body_file: Path,
    *,
    repo_root: Path,
    classification: str,
    backend: dict[str, Any] | None = None,
    reason: str = "completed",
    manual_target_declaration: str | None = None,
    goal_run_authorized: bool = False,
    preflight_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    prepared = _prepare_close_mutation(
        repo,
        number,
        body_file,
        repo_root=repo_root,
        classification=classification,
        backend=backend,
        reason=reason,
        manual_target_declaration=manual_target_declaration,
        goal_run_authorized=goal_run_authorized,
        preflight_state=preflight_state,
    )
    verified_state = _MUTATION.comment_close(
        prepared["comment_argv"],
        prepared["close_argv"],
        prepared["view_argv"],
        repo=repo,
        number=number,
        run_backend=_run_backend,
        require_identity=require_exact_issue_identity,
    )
    # floor-addition-restraint: irreversible-boundary P5, forces-question-only --
    # advisory only (exit stays 0); a question/decision-needed close has nothing
    # live to confirm, so the only obligation is surfacing that the
    # classification-driven exemption applied, never blocking on it.
    review_advisory = _CLOSE_COMMENT_FLOOR.review_advisory_for_classification(classification)
    # The floor report is only FORMATTED on failure, so a close that passed while
    # its critique recorded `blocked` or carried no fresh-eye line said so nowhere
    # the closing operator would see. `verify-closeout` already surfaces these;
    # the carrier that writes to GitHub itself did not.
    review_advisory = review_advisory + list(
        prepared["floor_report"].get("resolution_critique", {}).get("review_advisory", []) or []
    )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": prepared["comment_argv"],
        "close_argv": prepared["close_argv"],
        "view_argv": prepared["view_argv"],
        "preflight_state": prepared["preflight_state"],
        "verified_state": verified_state,
        "reason": reason,
        "closeout_authorization": prepared["authorization"],
        "review_advisory": review_advisory,
    }


close_after_verified_comment = partial(
    _RETRY.close_after_verified_comment,
    prepare=_prepare_close_mutation,
    mutation=_MUTATION,
    run_backend=_run_backend,
    require_identity=require_exact_issue_identity,
)
