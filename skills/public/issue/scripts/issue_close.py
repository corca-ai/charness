from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BACKEND = _load_local("issue_backend", "issue_close_backend")
_run_backend = _BACKEND.run_backend
_resolve_op = _BACKEND.resolve_op
BACKEND_TIMEOUT_SECONDS = _BACKEND.BACKEND_TIMEOUT_SECONDS
_CLOSE_COMMENT_FLOOR = _load_local("issue_close_comment_floor")
_AUTHZ = _load_local("issue_closeout_authorization")

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


def _capture_lifecycle(repo_root: Path, *, repo: str, number: int) -> dict[str, Any]:
    """Best-effort shared usage capture after the issue state readback."""

    helper_path = next(
        (
            parent / "scripts" / "lifecycle_usage_capture.py"
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "lifecycle_usage_capture.py").is_file()
        ),
        None,
    )
    if helper_path is None:
        return {"status": "capture_error", "appended": False, "errors": ["lifecycle capture helper unavailable"]}
    try:
        capture = runpy.run_path(str(helper_path))["capture_lifecycle_outcome"]
        return capture(
            repo_root=repo_root,
            lifecycle_kind="issue_close",
            evidence_locator=f"{repo}#{number}",
        )
    except Exception as exc:  # telemetry must never undo a completed close
        return {"status": "capture_error", "appended": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}


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
    if not body_file.is_file():
        raise RuntimeError(f"close-comment body file not found: {body_file}")
    body = body_file.read_text(encoding="utf-8")
    # Authorization runs before BOTH backend mutations, not just the close. A comment
    # posted on the wrong issue is already an external side effect that cannot be
    # taken back, and this function's own error path documents that the close can fail
    # after the comment has landed — so "authorize before the close" would be a check
    # placed after the first irreversible act.
    authorization = _authorize_direct_close(
        repo=repo, number=number, repo_root=repo_root, body=body,
        manual_target_declaration=manual_target_declaration,
    )
    floor_report = _CLOSE_COMMENT_FLOOR.evaluate_close_comment_floor(
        repo_root=repo_root, body=body, classification=classification, number=number
    )
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
        view_argv = _resolve_op(
            backend,
            "view",
            GH_VIEW_DEFAULT,
            VIEW_PLACEHOLDERS,
            repo=repo,
            number=str(number),
            json_fields="number,state,url",
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
    lifecycle_capture = _capture_lifecycle(repo_root, repo=repo, number=number)
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": comment_argv,
        "close_argv": close_argv,
        "view_argv": view_argv,
        "verified_state": verified_state,
        "reason": reason,
        "closeout_authorization": authorization,
        "review_advisory": review_advisory,
        "lifecycle_capture": lifecycle_capture,
    }
