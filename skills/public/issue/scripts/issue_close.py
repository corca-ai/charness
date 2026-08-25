from __future__ import annotations

import json
import runpy
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

GH_COMMENT_DEFAULT = [
    "issue",
    "comment",
    "--repo",
    "{repo}",
    "{number}",
    "--body-file",
    "{body_file}",
]

GH_CLOSE_DEFAULT = [
    "issue",
    "close",
    "--repo",
    "{repo}",
    "{number}",
    "--reason",
    "{reason}",
]
GH_VIEW_DEFAULT = [
    "issue",
    "view",
    "--repo",
    "{repo}",
    "{number}",
    "--json",
    "{json_fields}",
]

COMMENT_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "body_file", "reason"})
CLOSE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "reason"})
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})


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

    Extracted so the carrier's verdict can be OBSERVED without mutating GitHub.
    The closeout floor matrix probes this function; probing
    ``evaluate_close_comment_floor`` directly would have measured the floor rather
    than what this carrier's caller gets, and the readback wiring below -- which
    lives here and not in the floor -- is precisely the part that decides whether
    the consolidation facts reach the verdict at all.

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
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    # Ahead of the body read, where it has always been: a caller that asked for
    # `completed` on a consolidation gets the contradiction, not a file-not-found.
    _refuse_completed_consolidation(classification, reason)
    if not body_file.is_file():
        raise RuntimeError(f"close-comment body file not found: {body_file}")
    body = body_file.read_text(encoding="utf-8")
    floor_report = evaluate_close_comment_carrier(
        repo, number, body,
        repo_root=repo_root, classification=classification, backend=backend,
        reason=reason, manual_target_declaration=manual_target_declaration,
    )
    authorization = floor_report["closeout_authorization"]
    if not floor_report["ok"]:
        # floor-addition-restraint: irreversible-boundary P5 floor, presence/form-only
        raise RuntimeError(_CLOSE_COMMENT_FLOOR.format_close_comment_floor_failure(floor_report))
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
    view_argv = None
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "close state verification requires backend commands.view; "
            "comment plus close command success is not issue closeout"
        )
    if backend.get("id", "gh") == "gh" or commands.get("view") is not None:
        # `required=`, which this call omitted. This view is the POST-CLOSE readback -- the
        # evidence that the mutation landed -- so it verifies one issue's state and owes the
        # same identity floor as every other surface that does. `(repo, number)` names an
        # issue; a template spelling only `{number}` drops the repository silently and a
        # repo-agnostic binary confirms ITS OWN issue N as CLOSED. No waiver is offered here:
        # this is the irreversible boundary, and the reader that can afford one is the
        # staleness path, not this.
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
    # This readback is deliberately before the first mutation. An argv containing
    # --repo and number is a request, not proof that the backend answered about that
    # target. The same strict helper is used again after close.
    preflight_state = None
    if view_argv is not None:
        preflight_result = _run_backend(view_argv)
        if preflight_result.returncode != 0:
            raise RuntimeError(
                "pre-mutation issue readback failed; no comment or close was attempted: "
                f"view_exit={preflight_result.returncode} "
                f"view_stderr={preflight_result.stderr.strip()!r}"
            )
        try:
            preflight_state = json.loads(preflight_result.stdout)
        except Exception as exc:
            raise RuntimeError(
                f"pre-mutation issue readback returned invalid JSON: {exc}"
            ) from exc
        require_exact_issue_identity(
            preflight_state,
            expected_repo=repo,
            expected_number=number,
            context="pre-mutation issue readback",
        )
    comment_result = _run_backend(comment_argv)
    if comment_result.returncode != 0:
        raise RuntimeError(
            f"comment failed: exit={comment_result.returncode} stderr={comment_result.stderr.strip()!r}"
        )
    close_result = _run_backend(close_argv)
    if close_result.returncode != 0:
        raise RuntimeError(
            "close failed after comment landed; do not re-comment on retry. "
            f"comment_succeeded=True comment_argv={comment_argv!r} "
            f"close_exit={close_result.returncode} close_stderr={close_result.stderr.strip()!r}"
        )
    verified_state: dict[str, Any] | None = None
    if view_argv is not None:
        view_result = _run_backend(view_argv)
        if view_result.returncode != 0:
            raise RuntimeError(
                "close state verification failed after close command succeeded; "
                f"view_exit={view_result.returncode} view_stderr={view_result.stderr.strip()!r}"
            )
        try:
            verified_state = json.loads(view_result.stdout)
        except Exception as exc:
            raise RuntimeError(f"close state verification returned invalid JSON: {exc}") from exc
        # The other half of the identity, checked against the ANSWER. Requiring `{repo}` in the
        # template means the backend is TOLD which repository to read back; it does not mean it
        # obeyed, and a wrong-repo answer carries the right number and the expected state. The
        # `url` needed to check it was already being fetched and stored, and never read.
        # Silence is not a mismatch: a payload that names no repository yields None here, and
        # refusing those would fail every backend whose payload shape omits one.
        require_exact_issue_identity(
            verified_state,
            expected_repo=repo,
            expected_number=number,
            context="post-mutation issue readback",
        )
        if verified_state.get("state") != "CLOSED":
            raise RuntimeError(
                f"close state verification failed: {repo}#{number} is {verified_state.get('state')!r}"
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
        floor_report.get("resolution_critique", {}).get("review_advisory", []) or []
    )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": comment_argv,
        "close_argv": close_argv,
        "view_argv": view_argv,
        "preflight_state": preflight_state,
        "verified_state": verified_state,
        "reason": reason,
        "closeout_authorization": authorization,
        "review_advisory": review_advisory,
    }
