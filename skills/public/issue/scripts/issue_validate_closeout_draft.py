from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_PROOF_MISMATCH = None


def _load_proof_mismatch():
    """Load the portable proof-mismatch floor (``scripts/proof_mismatch.py``) via
    the skill-runtime repo-module loader, so its ``from scripts.`` imports resolve
    in the issue skill context. Cached; reuses the same module the achieve
    closeout wires."""
    global _PROOF_MISMATCH
    if _PROOF_MISMATCH is not None:
        return _PROOF_MISMATCH
    bootstrap = next(
        (a / "skill_runtime_bootstrap.py" for a in Path(__file__).resolve().parents if (a / "skill_runtime_bootstrap.py").is_file()),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
    _PROOF_MISMATCH = runtime.load_repo_module_from_skill_script(__file__, "scripts.proof_mismatch")
    return _PROOF_MISMATCH


def validate_closeout_draft(
    *,
    verifier: Any,
    repo_root: Path,
    repo: str,
    numbers: list[int],
    classification: str,
    body_file: Path | None,
    backend: dict[str, Any],
    carrier: str,
    commit_message_file: Path | None = None,
    manual_fallback_reason: str | None = None,
) -> dict[str, Any]:
    """Validate a closeout body before it mutates GitHub.

    This intentionally reuses ``verify_closeout`` with no ``expect_state`` so
    the same ledger, critique, close-keyword, and manual-fallback checks run
    before a PR body/comment/commit body is applied.
    """
    verification_carrier = "pr-body" if carrier == "direct-commit" else carrier
    verification_body_file = commit_message_file if carrier == "direct-commit" else body_file
    if carrier == "direct-commit" and verification_body_file is None:
        raise RuntimeError("direct-commit draft requires --commit-message-file")
    if verification_body_file is None:
        raise RuntimeError(f"{carrier} draft requires --body-file")

    result = verifier.verify_closeout(
        repo_root=repo_root,
        repo=repo,
        numbers=numbers,
        classification=classification,
        carrier=verification_carrier,
        backend=backend,
        body_file=verification_body_file,
        manual_fallback_reason=manual_fallback_reason,
        expect_state=None,
    )
    # The portable proof-mismatch floor: if the closeout body declares a
    # `## Proof Ledger`, block before publication when a proof gap is left
    # undispositioned. Inert when no ledger is present (no over-fire), so existing
    # issue closeouts are unchanged.
    body_text = verification_body_file.read_text(encoding="utf-8", errors="ignore")
    _load_proof_mismatch().apply_proof_mismatch_floor(result, repo_root, body_text)

    result["carrier"] = carrier
    result["body_file"] = str(body_file) if body_file is not None else None
    result["commit_message_file"] = (
        str(commit_message_file) if commit_message_file is not None else None
    )
    result["draft"] = True
    result["status"] = "draft_verified" if result["ok"] else "draft_failed"
    result["publication_status"] = (
        "ready_to_commit_push" if carrier == "direct-commit" else "ready_to_publish"
    )
    return result


def command_validate_closeout_draft(args: Any, *, resolve_backend: Any, emit: Any, verifier: Any) -> int:
    resolved = resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = validate_closeout_draft(
            verifier=verifier,
            repo_root=args.repo_root.resolve(),
            repo=args.repo,
            numbers=args.number,
            classification=args.classification,
            body_file=args.body_file.resolve() if args.body_file else None,
            backend=resolved["backend"],
            carrier=args.carrier,
            commit_message_file=(
                args.commit_message_file.resolve() if args.commit_message_file else None
            ),
            manual_fallback_reason=args.manual_fallback_reason,
        )
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    emit(result)
    return 0 if result["ok"] else 2


def register_validate_closeout_draft_subparser(
    subparsers: Any,
    cwd_default: Path,
    *,
    resolve_backend: Any,
    emit: Any,
    verifier: Any,
) -> None:
    parser = subparsers.add_parser(
        "validate-closeout-draft",
        help="Validate an issue closeout body before posting, merging, or closing anything",
    )
    parser.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    parser.add_argument("--number", action="append", type=int, required=True, help="Issue number; repeat for bundles")
    parser.add_argument(
        "--classification",
        choices=("bug", "feature", "deferred-work", "question", "decision-needed"),
        required=True,
    )
    parser.add_argument("--body-file", type=Path, help="Draft closeout body to validate")
    parser.add_argument(
        "--commit-message-file",
        type=Path,
        help="Proposed direct-commit subject/body to rehearse before commit or push",
    )
    parser.add_argument(
        "--carrier",
        choices=("direct-commit", "pr-body", "manual-fallback"),
        default="pr-body",
    )
    parser.add_argument(
        "--manual-fallback-reason",
        choices=(
            "auto-close-unsupported",
            "auto-close-failed-after-remote-verification",
            "operator-directed-manual-close",
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    parser.set_defaults(
        func=lambda args: command_validate_closeout_draft(
            args,
            resolve_backend=resolve_backend,
            emit=emit,
            verifier=verifier,
        )
    )
