#!/usr/bin/env python3
"""Build Corca-internal usage product-review packets from usage episodes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import jsonschema
import yaml
from report_usage_episodes import (
    DEFAULT_ADAPTER,
    _disabled_payload,
    _load_adapter,
    _load_json,
    _missing_adapter_payload,
    _no_records_payload,
    _portable_path,
    _read_valid_records,
    _resolve_records_path,
    _schema_root,
)
from usage_episode_product_review import (
    REVIEW_NON_CLAIMS,
    build_review_payload,
    execute_comments,
    parse_optional_time,
    print_review_result,
)

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
ATTENTION_STATES = ("no_adapter", "disabled", "no_records")
ATTENTION_EVIDENCE_TERMS = (
    "usage_episodes_adapter_missing",
    "usage_episodes_no_records",
    "product-review report unavailable",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--records-path", type=Path)
    parser.add_argument("--window-start")
    parser.add_argument("--window-end")
    parser.add_argument("--release-version", default="unknown")
    parser.add_argument(
        "--update-prompt-state",
        default="unknown",
        choices=["unknown", "not_prompted", "prompted", "accepted", "declined"],
    )
    parser.add_argument("--corca-internal", action="store_true")
    parser.add_argument("--repo-ref")
    parser.add_argument("--user-ref")
    parser.add_argument("--friction-threshold", type=int)
    parser.add_argument("--missed-detection-threshold", type=int)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--github-repo")
    parser.add_argument("--issue-number", type=int)
    parser.add_argument("--gh-bin", default="gh")
    parser.add_argument(
        "--include-target-refs-in-comments",
        action="store_true",
        help="Include repo/user refs in mutating GitHub comments; default redacts them.",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.repo_ref and not args.corca_internal:
        raise SystemExit("--repo-ref requires --corca-internal")
    if args.user_ref and not args.corca_internal:
        raise SystemExit("--user-ref requires --corca-internal")
    for name in ("friction_threshold", "missed_detection_threshold"):
        value = getattr(args, name)
        if value is not None and value <= 0:
            raise SystemExit(f"--{name.replace('_', '-')} must be positive")
    if args.execute and (not args.github_repo or args.issue_number is None):
        raise SystemExit("--execute requires --github-repo and --issue-number")


def _invalid_payload(
    status: str,
    repo_root: Path,
    adapter_path: Path,
    errors: list[str],
    *,
    records_path: Path | None = None,
) -> dict:
    payload = {
        "status": status,
        "valid": False,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "errors": errors,
        "warnings": [],
        "non_claims": REVIEW_NON_CLAIMS,
    }
    if records_path is not None:
        payload["records_path"] = _portable_path(repo_root, records_path)
    return payload


def main() -> int:
    args = _parse_args()
    _validate_args(args)
    repo_root = args.repo_root.resolve()
    adapter_path = args.adapter_path or repo_root / DEFAULT_ADAPTER
    if not adapter_path.is_absolute():
        adapter_path = repo_root / adapter_path
    schema_root = _schema_root(repo_root)
    manifest_schema = _load_json(schema_root / "manifest.schema.json")
    episode_schema = _load_json(schema_root / "episode.schema.json")

    if not adapter_path.is_file():
        print_review_result(_missing_adapter_payload(repo_root, adapter_path), as_json=args.json)
        return 0
    try:
        adapter = _load_adapter(adapter_path)
        jsonschema.validate(adapter, manifest_schema)
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        payload = _invalid_payload("invalid_adapter", repo_root, adapter_path, [str(exc)])
        print_review_result(payload, as_json=args.json)
        return 1
    if not adapter.get("enabled", False):
        print_review_result(_disabled_payload(repo_root, adapter_path), as_json=args.json)
        return 0

    records_path = _resolve_records_path(repo_root, adapter, args.records_path)
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        payload = _invalid_payload(
            "invalid_records_path",
            repo_root,
            adapter_path,
            ["records_path must stay under repo_root"],
            records_path=records_path,
        )
        print_review_result(payload, as_json=args.json)
        return 1
    if not records_path.is_file():
        print_review_result(_no_records_payload(repo_root, adapter_path, records_path), as_json=args.json)
        return 0

    records, errors = _read_valid_records(records_path, episode_schema)
    if errors:
        payload = _invalid_payload(
            "invalid_records",
            repo_root,
            adapter_path,
            errors,
            records_path=records_path,
        )
        payload["valid_count"] = len(records)
        print_review_result(payload, as_json=args.json)
        return 1
    try:
        window_start = parse_optional_time(args.window_start)
        window_end = parse_optional_time(args.window_end)
    except ValueError as exc:
        payload = _invalid_payload("invalid_window", repo_root, adapter_path, [str(exc)], records_path=records_path)
        print_review_result(payload, as_json=args.json)
        return 2
    if window_start is not None and window_end is not None and window_start > window_end:
        payload = _invalid_payload(
            "invalid_window",
            repo_root,
            adapter_path,
            ["--window-start must be before or equal to --window-end"],
            records_path=records_path,
        )
        print_review_result(payload, as_json=args.json)
        return 2

    payload = build_review_payload(
        records,
        window_start=window_start,
        window_end=window_end,
        release_version=args.release_version,
        update_prompt_state=args.update_prompt_state,
        corca_internal=args.corca_internal,
        repo_ref=args.repo_ref,
        user_ref=args.user_ref,
        friction_threshold=args.friction_threshold,
        missed_detection_threshold=args.missed_detection_threshold,
        execute=args.execute,
    )
    return_code = 0
    if args.execute:
        return_code = execute_comments(
            payload,
            gh_bin=args.gh_bin,
            github_repo=args.github_repo,
            issue_number=args.issue_number,
            include_target_refs=args.include_target_refs_in_comments,
        )
    print_review_result(payload, as_json=args.json)
    return return_code


if __name__ == "__main__":
    sys.exit(main())
