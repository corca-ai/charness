from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_PROOF_MISMATCH = None


def _resolve_bootstrap() -> Path | None:
    """The nearest ``skill_runtime_bootstrap.py`` above this file, or ``None``."""
    return next(
        (a / "skill_runtime_bootstrap.py" for a in Path(__file__).resolve().parents if (a / "skill_runtime_bootstrap.py").is_file()),
        None,
    )


def _load_proof_mismatch():
    """Load the portable proof-mismatch floor (``scripts/proof_mismatch.py``) via
    the skill-runtime repo-module loader, so its ``from scripts.`` imports resolve
    in the issue skill context. Cached; reuses the same module the achieve closeout
    wires."""
    global _PROOF_MISMATCH
    if _PROOF_MISMATCH is None:
        bootstrap = _resolve_bootstrap()
        if bootstrap is None:
            raise ImportError("skill_runtime_bootstrap.py not found")
        runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
        _PROOF_MISMATCH = runtime.load_repo_module_from_skill_script(__file__, "scripts.proof_mismatch")
    return _PROOF_MISMATCH


def _fold_proof_mismatch(result: dict[str, Any], repo_root: Path, body: str) -> None:
    """Fold the portable proof-mismatch floor into a verify_closeout result: a
    ``## Proof Ledger`` gap left undispositioned flips ``ok`` False and ``status``
    to ``failed``. Inert when the body declares no proof ledger (no over-fire), so
    both validate-closeout-draft (which reuses this) and post-publication
    verify-closeout enforce it identically."""
    _load_proof_mismatch().apply_proof_mismatch_floor(result, repo_root, body)
    if result.get("proof_mismatch"):
        result["status"] = "failed"


_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
ISSUE_CLOSE = _load_local("issue_close", "issue_verify_issue_close")
_BODY = _load_local("issue_verify_closeout_body")
_CRITIQUE = _load_local("issue_resolution_critique", "issue_resolution_critique")
GIT_TIMEOUT_SECONDS = 10

CARRIERS = ("direct-commit", "pr-body", "manual-fallback")
CLASSIFICATIONS = ("bug", "feature", "deferred-work", "question", "decision-needed")
MANUAL_FALLBACK_REASONS = (
    "auto-close-unsupported",
    "auto-close-failed-after-remote-verification",
    "operator-directed-manual-close",
)

_body_fields = _BODY._body_fields
_first_field = _BODY._first_field
_has_substantive_value = _BODY._has_substantive_value
_missing_ledger_fields = _BODY._missing_ledger_fields
_missing_close_keywords = _BODY._missing_close_keywords
evaluate_source_preservation = _BODY.evaluate_source_preservation
evaluate_behavioral_verdict = _BODY.evaluate_behavioral_verdict
evaluate_ai_provenance = _BODY.evaluate_ai_provenance


def _read_carrier_body(repo_root: Path, *, carrier: str, commit_ref: str | None, body_file: Path | None) -> str:
    if carrier == "direct-commit":
        if not commit_ref:
            raise RuntimeError("direct-commit carrier requires --commit-ref")
        try:
            result = subprocess.run(
                ["git", "show", "-s", "--format=%B", commit_ref],
                cwd=repo_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(
                ["git", "show", "-s", "--format=%B", commit_ref],
                124,
                str(exc.stdout or ""),
                f"timed out after {GIT_TIMEOUT_SECONDS}s",
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"unable to read commit body for {commit_ref!r}: {result.stderr.strip()!r}"
            )
        return result.stdout
    if body_file is None:
        raise RuntimeError(f"{carrier} carrier requires --body-file")
    if not body_file.is_file():
        raise RuntimeError(f"carrier body file not found: {body_file}")
    return body_file.read_text(encoding="utf-8")


def _view_issue_state(
    repo_root: Path,
    *,
    repo: str,
    number: int,
    backend: dict[str, Any],
    json_fields: str = "number,state,url",
) -> dict[str, Any]:
    commands = backend.get("commands") or {}
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "closeout state verification requires backend commands.view; "
            "carrier text alone is not issue closeout"
        )
    argv = ISSUE_CLOSE._resolve_op(
        backend,
        "view",
        ISSUE_CLOSE.GH_VIEW_DEFAULT,
        ISSUE_CLOSE.VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number"}),
        repo=repo,
        number=str(number),
        json_fields=json_fields,
    )
    try:
        result = subprocess.run(
            argv,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=ISSUE_CLOSE.BACKEND_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        raise RuntimeError(f"issue state verification command failed to start: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            argv,
            124,
            str(exc.stdout or ""),
            f"timed out after {ISSUE_CLOSE.BACKEND_TIMEOUT_SECONDS}s",
        )
    if result.returncode != 0:
        raise RuntimeError(
            f"issue state verification failed for {repo}#{number}: "
            f"exit={result.returncode} stderr={result.stderr.strip()!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        raise RuntimeError(f"issue state verification returned invalid JSON: {exc}") from exc
    return payload


def _manual_comment_found(body: str, state_payload: dict[str, Any]) -> bool:
    expected = body.strip()
    comments = state_payload.get("comments")
    if not isinstance(comments, list):
        return False
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        comment_body = str(comment.get("body", "")).strip()
        if comment_body == expected:
            return True
    return False


def _validate_verify_inputs(
    *, numbers: list[int], classification: str, carrier: str,
    manual_fallback_reason: str | None, expect_state: str | None,
) -> None:
    if not numbers:
        raise RuntimeError("verify-closeout requires at least one --number")
    if classification not in CLASSIFICATIONS:
        raise RuntimeError(f"unknown classification: {classification}")
    if carrier not in CARRIERS:
        raise RuntimeError(f"unknown carrier: {carrier}")
    if carrier == "manual-fallback" and manual_fallback_reason not in MANUAL_FALLBACK_REASONS:
        raise RuntimeError(
            "manual-fallback carrier requires --manual-fallback-reason "
            f"one of {', '.join(MANUAL_FALLBACK_REASONS)}"
        )
    if carrier != "manual-fallback" and manual_fallback_reason is not None:
        raise RuntimeError("--manual-fallback-reason is only valid with --carrier manual-fallback")
    if expect_state is not None and expect_state.upper() != "CLOSED":
        raise RuntimeError("final closeout verification requires --expect-state CLOSED")


def verify_closeout(
    *,
    repo_root: Path,
    repo: str,
    numbers: list[int],
    classification: str,
    carrier: str,
    backend: dict[str, Any],
    commit_ref: str | None = None,
    body_file: Path | None = None,
    manual_fallback_reason: str | None = None,
    expect_state: str | None = None,
) -> dict[str, Any]:
    _validate_verify_inputs(
        numbers=numbers, classification=classification, carrier=carrier,
        manual_fallback_reason=manual_fallback_reason, expect_state=expect_state,
    )
    body = _read_carrier_body(repo_root, carrier=carrier, commit_ref=commit_ref, body_file=body_file)
    resolution_critique_check = _CRITIQUE.check_resolution_critique(
        repo_root=repo_root, body=body, classification=classification, numbers=numbers
    )
    missing_close_keywords = [] if carrier == "manual-fallback" else _missing_close_keywords(body, numbers, repo)
    missing_fields = _missing_ledger_fields(body, classification)
    source_preservation = evaluate_source_preservation(body)
    behavioral_verdict = evaluate_behavioral_verdict(body, classification, numbers)
    ai_provenance = evaluate_ai_provenance(body, classification)
    if carrier == "manual-fallback":
        reason_value = _first_field(_body_fields(body), ("manual close reason", "manual fallback reason"))
        if not _has_substantive_value(reason_value):
            missing_fields.append("manual_fallback_reason")

    verified_state: list[dict[str, Any]] = []
    state_mismatches: list[dict[str, Any]] = []
    manual_comment_missing: list[int] = []
    if expect_state is not None:
        expected = expect_state.upper()
        for number in numbers:
            json_fields = "number,state,url,comments" if carrier == "manual-fallback" else "number,state,url"
            state_payload = _view_issue_state(
                repo_root, repo=repo, number=number, backend=backend, json_fields=json_fields
            )
            verified_state.append(state_payload)
            returned_number = state_payload.get("number")
            if returned_number != number:
                state_mismatches.append(
                    {
                        "number": number,
                        "expected": number,
                        "actual": returned_number,
                        "field": "number",
                        "url": state_payload.get("url"),
                    }
                )
            actual = str(state_payload.get("state", "")).upper()
            if actual != expected:
                state_mismatches.append(
                    {
                        "number": number,
                        "expected": expected,
                        "actual": state_payload.get("state"),
                        "url": state_payload.get("url"),
                    }
                )
            if carrier == "manual-fallback" and not _manual_comment_found(body, state_payload):
                manual_comment_missing.append(number)

    critique_ok = resolution_critique_check.get("ok", True)
    ok = (
        critique_ok
        and not missing_close_keywords
        and not missing_fields
        and not state_mismatches
        and not manual_comment_missing
        and not source_preservation["missing"]
        and behavioral_verdict["ok"]
        and ai_provenance["ok"]
    )
    status = "verified" if ok and expect_state is not None else "carrier_verified" if ok else "failed"
    result = {
        "ok": ok,
        "status": status,
        "repo": repo,
        "numbers": numbers,
        "classification": classification,
        "carrier": carrier,
        "commit_ref": commit_ref,
        "body_file": str(body_file) if body_file is not None else None,
        "manual_fallback_reason": manual_fallback_reason,
        "expect_state": expect_state,
        "missing_close_keywords": missing_close_keywords,
        "missing_fields": missing_fields,
        "state_mismatches": state_mismatches,
        "manual_comment_missing": manual_comment_missing,
        "resolution_critique_check": resolution_critique_check,
        "source_preservation": source_preservation,
        "behavioral_verdict": behavioral_verdict,
        "ai_provenance": ai_provenance,
        "verified_state": verified_state,
    }
    _fold_proof_mismatch(result, repo_root, body)
    return result
