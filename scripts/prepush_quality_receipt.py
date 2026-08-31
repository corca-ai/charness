#!/usr/bin/env python3
"""Issue and validate one-push quality receipts for the release helper."""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "charness.prepush-quality-receipt.v1"
SCOPE = "release-full-superset"
ZERO_SHA = "0" * 40


class ReceiptError(ValueError):
    pass


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ReceiptError(detail)
    return result.stdout.strip()


def _head_and_tree(repo_root: Path) -> tuple[str, str]:
    values = _git(repo_root, "rev-parse", "HEAD", "HEAD^{tree}").splitlines()
    if len(values) != 2:
        raise ReceiptError("git rev-parse returned an incomplete HEAD/tree snapshot")
    return values[0], values[1]


def _quality_command_argv(repo_root: Path, command: str) -> list[str]:
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise ReceiptError(f"quality command is not parseable: {exc}") from exc
    if not argv:
        raise ReceiptError("quality command is empty")
    runner = Path(argv[0])
    resolved = runner if runner.is_absolute() else repo_root / runner
    if resolved.resolve() != (repo_root / "scripts" / "run-quality.sh").resolve():
        raise ReceiptError("quality command is not this repo's run-quality.sh")
    if "--release" not in argv:
        raise ReceiptError("quality command does not cover the release/full queue")
    return argv


def _materialized_digest(repo_root: Path, relative_root: str) -> str:
    materialized_root = (repo_root / relative_root).resolve()
    if not materialized_root.is_relative_to(repo_root) or not materialized_root.is_dir():
        raise ReceiptError("materialized plugin root is absent or escapes the repository")
    digest = hashlib.sha256()
    for path in sorted(
        materialized_root.rglob("*"),
        key=lambda item: item.relative_to(materialized_root).as_posix(),
    ):
        relative = path.relative_to(materialized_root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"link\0" + relative + b"\0" + path.readlink().as_posix().encode("utf-8") + b"\0")
        elif path.is_file():
            digest.update(b"file\0" + relative + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _semantic_receipt(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"semantic quality receipt is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ReceiptError("semantic quality receipt root must be an object")
    details = value.get("details")
    if (
        value.get("surface") != "quality"
        or value.get("status") != "pass"
        or value.get("effective_exit_code") != 0
        or value.get("unproven_subjects") != []
        or not isinstance(details, dict)
        or details.get("release") is not True
        or details.get("full_queue") is not True
    ):
        raise ReceiptError("semantic quality receipt is not an established release/full pass")
    measured = value.get("measured_scope")
    if not isinstance(measured, list) or not measured:
        raise ReceiptError("semantic quality receipt has no measured scope")
    return value, hashlib.sha256(raw).hexdigest()


def seal_receipt(
    repo_root: Path,
    quality_command: str,
    semantic_receipt: Path,
    materialized_root: str,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    _quality_command_argv(repo_root, quality_command)
    semantic, semantic_sha = _semantic_receipt(semantic_receipt)
    if _git(repo_root, "status", "--porcelain", "--untracked-files=all"):
        raise ReceiptError("repository is not clean after release quality")
    head, tree = _head_and_tree(repo_root)
    return {
        "schema_version": SCHEMA,
        "status": "pass",
        "scope": SCOPE,
        "repo_root": str(repo_root),
        "verified_head": head,
        "verified_tree": tree,
        "quality_command": quality_command,
        "semantic_receipt_sha256": semantic_sha,
        "semantic_measured_scope": semantic["measured_scope"],
        "materialized_root": materialized_root,
        "materialized_sha256": _materialized_digest(repo_root, materialized_root),
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }


def _load_receipt(repo_root: Path, receipt_path: Path) -> dict[str, Any]:
    resolved = receipt_path.resolve()
    if resolved.is_relative_to(repo_root.resolve()):
        raise ReceiptError("receipt must be ephemeral and outside the repository")
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"receipt is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ReceiptError("receipt root must be an object")
    return value


def _push_local_shas(push_input: str) -> list[str]:
    local_shas: list[str] = []
    for line_number, raw in enumerate(push_input.splitlines(), start=1):
        fields = raw.split()
        if len(fields) != 4:
            raise ReceiptError(f"push input line {line_number} does not have four fields")
        local_sha = fields[1]
        if local_sha != ZERO_SHA:
            local_shas.append(local_sha)
    if not local_shas:
        raise ReceiptError("push input has no local object to verify")
    return local_shas


def validate_receipt(
    repo_root: Path, receipt_path: Path, push_input: str
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    receipt = _load_receipt(repo_root, receipt_path)
    expected_keys = {
        "schema_version",
        "status",
        "scope",
        "repo_root",
        "verified_head",
        "verified_tree",
        "quality_command",
        "semantic_receipt_sha256",
        "semantic_measured_scope",
        "materialized_root",
        "materialized_sha256",
        "issued_at",
    }
    if set(receipt) != expected_keys:
        raise ReceiptError("receipt fields do not match the closed v1 schema")
    if receipt["schema_version"] != SCHEMA or receipt["status"] != "pass":
        raise ReceiptError("receipt is not a passing v1 receipt")
    if receipt["scope"] != SCOPE or receipt["repo_root"] != str(repo_root):
        raise ReceiptError("receipt scope or repository identity does not match")
    if not isinstance(receipt["issued_at"], str) or not receipt["issued_at"].strip():
        raise ReceiptError("receipt issued_at is missing")
    _quality_command_argv(repo_root, str(receipt["quality_command"]))
    if (
        not isinstance(receipt["semantic_receipt_sha256"], str)
        or len(receipt["semantic_receipt_sha256"]) != 64
        or not isinstance(receipt["semantic_measured_scope"], list)
        or not receipt["semantic_measured_scope"]
    ):
        raise ReceiptError("sealed semantic quality identity is malformed")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=all"):
        raise ReceiptError("repository changed after the quality receipt")
    head, tree = _head_and_tree(repo_root)
    if receipt["verified_head"] != head or receipt["verified_tree"] != tree:
        raise ReceiptError("receipt HEAD/tree is stale")
    if receipt["materialized_sha256"] != _materialized_digest(
        repo_root, str(receipt["materialized_root"])
    ):
        raise ReceiptError("materialized plugin export changed after release quality")
    for local_sha in _push_local_shas(push_input):
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", local_sha, head],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ReceiptError(f"pushed object {local_sha} is not covered by verified HEAD")
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    seal = subparsers.add_parser("seal")
    seal.add_argument("--repo-root", type=Path, required=True)
    seal.add_argument("--quality-command", required=True)
    seal.add_argument("--semantic-receipt", type=Path, required=True)
    seal.add_argument("--materialized-root", required=True)
    seal.add_argument("--output", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--repo-root", type=Path, required=True)
    validate.add_argument("--receipt", type=Path, required=True)
    validate.add_argument("--consume", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "seal":
            output = args.output.resolve()
            if output.is_relative_to(args.repo_root.resolve()):
                raise ReceiptError("receipt output must be outside the repository")
            payload = seal_receipt(
                args.repo_root,
                args.quality_command,
                args.semantic_receipt,
                args.materialized_root,
            )
            output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print(f"sealed pre-push quality receipt for {payload['verified_head']}")
        else:
            payload = validate_receipt(args.repo_root, args.receipt, sys.stdin.read())
            print(f"validated pre-push quality receipt for {payload['verified_head']}")
            if args.consume:
                args.receipt.unlink(missing_ok=True)
    except ReceiptError as exc:
        print(f"pre-push quality receipt: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
