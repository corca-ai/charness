"""Argument grammar for the issue-tracker command family."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _add_observation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--attempt-id", required=True, help="Unique immutable provider-attempt identity"
    )
    parser.add_argument("--draft-sha256", required=True, help="Frozen Goal Draft SHA-256")
    parser.add_argument("--binding-sha256", required=True, help="Immutable Goal Binding SHA-256")
    parser.add_argument(
        "--observation-dir",
        type=Path,
        required=True,
        help="Repo-contained directory for immutable started/terminal observations",
    )


def register_subparsers(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    cwd_default: Path,
    *,
    handlers: dict[str, Any],
) -> None:
    preflight = subparsers.add_parser(
        "tracker-preflight", help="Check every parent/sub-issue operation"
    )
    preflight.add_argument(
        "--repo", required=True, help="Exact parent repository in owner/repo form"
    )
    preflight.add_argument(
        "--number", type=int, required=True, help="Existing parent issue used for readiness"
    )
    preflight.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    preflight.set_defaults(func=handlers["command_tracker_preflight"])

    update = subparsers.add_parser("update", help="Replace an issue body and verify exact readback")
    update.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    update.add_argument("--number", type=int, required=True, help="Issue number to update")
    update.add_argument(
        "--goal-run-parent",
        type=int,
        required=True,
        help="Goal Run parent identity for readiness and observation binding",
    )
    update.add_argument(
        "--work-item-key", required=True, help="Stable Work Item key owning this body"
    )
    update.add_argument(
        "--body-file",
        type=Path,
        required=True,
        help="UTF-8 file containing the complete replacement body",
    )
    update.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    _add_observation_args(update)
    update.set_defaults(func=handlers["command_update"])

    create = subparsers.add_parser(
        "create-or-reuse-child", help="Create or exactly reuse one managed child"
    )
    create.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    create.add_argument(
        "--parent-number", type=int, required=True, help="Goal Run parent issue number"
    )
    create.add_argument("--work-item-key", required=True, help="Stable managed Work Item key")
    create.add_argument("--title", required=True, help="Exact desired child issue title")
    create.add_argument(
        "--body-file",
        type=Path,
        required=True,
        help="Exact desired body containing the Work Item key marker",
    )
    create.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    _add_observation_args(create)
    create.set_defaults(func=handlers["command_create_or_reuse_child"])

    listing = subparsers.add_parser(
        "list-sub-issues", help="Read and verify real sub-issue relationships"
    )
    listing.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    listing.add_argument("--number", type=int, required=True, help="Parent issue number")
    expected = listing.add_mutually_exclusive_group()
    expected.add_argument(
        "--expect-child",
        action="append",
        type=int,
        help="Expected child issue number; repeat for short ad hoc checks",
    )
    expected.add_argument(
        "--expect-child-file",
        type=Path,
        help="Source-bound JSON file containing the exact expected child set",
    )
    listing.add_argument(
        "--expect-all-closed",
        action="store_true",
        help="Refuse while any linked child remains open",
    )
    listing.add_argument(
        "--repo-root",
        type=Path,
        default=cwd_default,
        help="Repo root used to resolve the issue adapter",
    )
    listing.set_defaults(func=handlers["command_list_sub_issues"])

    for command, help_text, handler in (
        (
            "add-sub-issue",
            "Link one existing issue as a real sub-issue",
            handlers["command_add_sub_issue"],
        ),
        (
            "remove-sub-issue",
            "Remove one real sub-issue relationship",
            handlers["command_remove_sub_issue"],
        ),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument("--repo", required=True, help="Target repository in owner/repo form")
        child.add_argument("--number", type=int, required=True, help="Parent issue number")
        child.add_argument(
            "--sub-issue-number", type=int, required=True, help="Existing child issue number"
        )
        child.add_argument(
            "--work-item-key",
            required=True,
            help="Stable Work Item key for the relationship target",
        )
        child.add_argument(
            "--repo-root",
            type=Path,
            default=cwd_default,
            help="Repo root used to resolve the issue adapter",
        )
        _add_observation_args(child)
        child.set_defaults(func=handler)
