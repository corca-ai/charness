"""Top-level issue command grammar and family composition."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def build_parser(*, modules: dict[str, Any], handlers: dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    cwd_default = Path.cwd()
    preflight = subparsers.add_parser(
        "preflight", help="Inspect the issue adapter and host readiness before invoking the backend"
    )
    preflight.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    preflight.set_defaults(func=handlers["preflight"])

    modules["plan"].register_plan_subparser(
        subparsers,
        cwd_default,
        adapter_module=modules["adapter"],
        runtime_module=modules["runtime"],
        brief_module=modules["brief"],
        backend_module=modules["backend"],
        resolve_backend=handlers["resolve_backend"],
        emit=handlers["emit"],
    )

    target = subparsers.add_parser(
        "resolve-target",
        help="Resolve an issue target selector (owner/repo[#number]) against the adapter",
    )
    target.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    target.add_argument(
        "--target",
        help="Target selector (owner/repo or owner/repo#number); defaults to current repo",
    )
    target.set_defaults(func=handlers["resolve_target"])

    invocation = subparsers.add_parser(
        "resolve-invocation",
        help="Interpret raw skill invocation values into a structured target and selector",
    )
    invocation.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    invocation.add_argument("values", nargs="*", help="Raw skill invocation values to interpret")
    invocation.set_defaults(func=handlers["resolve_invocation"])

    select = subparsers.add_parser(
        "select", help="Select one or more issues by number, comma list, or newest-open default"
    )
    select.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    select.add_argument(
        "--selector", help="Issue selector (number, comma list, or omit to pick newest open)"
    )
    select.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    select.set_defaults(func=handlers["select"])

    read = subparsers.add_parser(
        "read", help="Read an issue body and comments through the selected backend"
    )
    read.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    read.add_argument("--number", type=int, required=True, help="Issue number to read")
    read.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    read.set_defaults(func=handlers["read"])

    modules["tracker_cli"].register_subparsers(subparsers, cwd_default)

    close = subparsers.add_parser(
        "close-with-comment", help="Close an issue with a comment body sourced from --body-file"
    )
    close.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    close.add_argument("--number", type=int, required=True, help="Issue number to close")
    close.add_argument(
        "--body-file", type=Path, required=True, help="Path to the closing comment body file"
    )
    close.add_argument(
        "--classification",
        choices=modules["verify"].CLASSIFICATIONS,
        required=True,
        help="Fix-unit classification recorded for the closeout; selects the applicable "
        "behavior, critique, and source-preservation checks before any GitHub mutation",
    )
    close.add_argument(
        "--reason",
        default="completed",
        help="Close reason passed to the backend (default: completed)",
    )
    close.add_argument(
        "--manual-target-declaration",
        default=None,
        help="Explicit repository-qualified close target (owner/repo#number). Required only "
        "when closing an issue protected by the evidence-boundary crosswalk: this carrier's "
        "body has no close keyword, so --number would otherwise authorize itself",
    )
    close.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    close.set_defaults(func=handlers["close_with_comment"])

    verify = subparsers.add_parser(
        "verify-closeout",
        help="Verify a closeout's classification, carrier, and backend state for one or more issues",
    )
    verify.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    verify.add_argument(
        "--number",
        action="append",
        type=int,
        required=True,
        help="Issue number to verify; repeat for multiple issues",
    )
    verify.add_argument(
        "--classification",
        choices=modules["verify"].CLASSIFICATIONS,
        required=True,
        help="Fix-unit classification recorded for the closeout",
    )
    verify.add_argument(
        "--carrier",
        choices=modules["verify"].CARRIERS,
        required=True,
        help="Carrier that delivered the fix (direct-commit, pr-body, or manual-fallback)",
    )
    verify.add_argument(
        "--commit-ref", help="Commit ref carrying the fix when carrier is commit-based"
    )
    verify.add_argument(
        "--body-file", type=Path, help="Path to the closing comment body file used for verification"
    )
    verify.add_argument(
        "--manual-fallback-reason",
        choices=modules["verify"].MANUAL_FALLBACK_REASONS,
        help="Reason code when falling back to a manual closeout carrier",
    )
    verify.add_argument(
        "--expect-state", choices=("CLOSED",), help="Expected backend issue state after closeout"
    )
    verify.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    verify.set_defaults(func=handlers["verify_closeout"])

    modules["validate_draft"].register_validate_closeout_draft_subparser(
        subparsers,
        cwd_default,
        resolve_backend=handlers["resolve_backend"],
        emit=handlers["emit"],
        verifier=modules["verify"],
        run_backend_command=handlers["run_backend_command"],
    )

    source = subparsers.add_parser(
        "check-source-preservation",
        help="Check a created issue body / artifact for the provider-neutral source-preservation contract",
    )
    source.add_argument(
        "--body-file",
        type=Path,
        required=True,
        help="Path to the issue body or local artifact to check",
    )
    source.add_argument(
        "--require-external",
        action="store_true",
        help="Fail when no `Source origin:` marker is present (assert the issue is externally sourced)",
    )
    source.set_defaults(func=handlers["check_source_preservation"])

    brief = subparsers.add_parser(
        "brief-path", help="Print the durable brief path for an issue number on the given date"
    )
    brief.add_argument(
        "--number", type=int, required=True, help="Issue number whose brief path should be returned"
    )
    brief.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    brief.add_argument("--date", help="ISO date (YYYY-MM-DD); defaults to today")
    brief.set_defaults(func=handlers["brief_path"])

    milestone = subparsers.add_parser(
        "resolve-milestone",
        help="Decide whether a requested milestone is assignable from the repo's existing milestones (never invents one)",
    )
    milestone.add_argument(
        "--requested", help="Milestone title the operator asked for; omit when none was requested"
    )
    milestone.add_argument(
        "--existing",
        action="append",
        help="An existing repository milestone title (fetch via the backend, e.g. `gh api repos/{repo}/milestones`); repeat per milestone",
    )
    milestone.set_defaults(func=handlers["resolve_milestone"])

    modules["create"].register_create_subparser(subparsers, cwd_default)
    return parser
