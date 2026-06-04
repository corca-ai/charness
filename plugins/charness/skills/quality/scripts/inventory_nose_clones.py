#!/usr/bin/env python3
"""Run the advisory nose clone-family inventory for quality review."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_PATHS = ("scripts", "skills/public", "skills/support")
DEFAULT_MODE = "syntax,semantic,near"
NOSE_TIMEOUT_SECONDS = 180


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def resolve_nose_bin() -> str | None:
    override = os.environ.get("NOSE_BIN")
    if override:
        return override
    return shutil.which("nose")


def build_command(
    nose_bin: str,
    paths: list[str],
    *,
    mode: str,
    threshold: float,
    min_lines: int,
    min_tokens: int,
    top: int,
    sort: str,
) -> list[str]:
    return [
        nose_bin,
        "scan",
        *paths,
        "--mode",
        mode,
        "--threshold",
        str(threshold),
        "--min-lines",
        str(min_lines),
        "--min-tokens",
        str(min_tokens),
        "--sort",
        sort,
        "--top",
        str(top),
        "--format",
        "json",
    ]


def _family_summary(family: dict[str, Any]) -> dict[str, Any]:
    locations = family.get("locations", [])
    files = []
    if isinstance(locations, list):
        for location in locations[:6]:
            if not isinstance(location, dict):
                continue
            file = location.get("file")
            if not isinstance(file, str):
                continue
            start = location.get("start_line")
            end = location.get("end_line")
            files.append(
                {
                    "file": file,
                    "start_line": start,
                    "end_line": end,
                    "name": location.get("name"),
                    "kind": location.get("kind"),
                }
            )
    return {
        "value": family.get("value"),
        "members": family.get("members"),
        "files": family.get("files"),
        "modules": family.get("modules"),
        "languages": family.get("languages"),
        "mean_score": family.get("mean_score"),
        "dup_lines": family.get("dup_lines"),
        "shared_lines": family.get("shared_lines"),
        "params": family.get("params"),
        "sample_locations": files,
    }


def run_nose(repo_root: Path, command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=NOSE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": str(exc.stdout or ""),
            "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s",
            "families": [],
        }
    try:
        families = json.loads(completed.stdout) if completed.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": f"nose emitted invalid JSON: {exc}; stderr: {completed.stderr.strip()}",
            "families": [],
        }
    status = "findings" if families else "clean"
    if completed.returncode != 0:
        status = "error"
    return {
        "status": status,
        "exit_code": completed.returncode,
        "stdout": "",
        "stderr": completed.stderr.strip(),
        "families": families if isinstance(families, list) else [],
    }


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    roots = [str(path) for path in (args.path or DEFAULT_PATHS)]
    nose_bin = resolve_nose_bin()
    if nose_bin is None:
        return {
            "status": "missing",
            "advisory": True,
            "repo_root": str(repo_root),
            "paths": roots,
            "family_count": 0,
            "families": [],
            "notes": [
                "nose is missing; install per integrations/tools/nose.json to run the clone-family advisory.",
                "Document near-copy detection remains covered by check_doc_near_duplicates.py.",
            ],
        }
    command = build_command(
        nose_bin,
        roots,
        mode=args.mode,
        threshold=args.threshold,
        min_lines=args.min_lines,
        min_tokens=args.min_tokens,
        top=args.top,
        sort=args.sort,
    )
    result = run_nose(repo_root, command)
    families = result["families"]
    return {
        "status": result["status"],
        "advisory": True,
        "repo_root": str(repo_root),
        "paths": roots,
        "command": " ".join(command),
        "exit_code": result["exit_code"],
        "family_count": len(families),
        "total_dup_lines": sum(int(family.get("dup_lines") or 0) for family in families if isinstance(family, dict)),
        "families": [_family_summary(family) for family in families if isinstance(family, dict)],
        "stderr": result["stderr"],
        "notes": [
            "nose findings are refactoring candidates, not standing quality failures.",
            "Review only extractable non-bootstrap families before changing code; do not chase every reported family.",
        ],
    }


def print_human(payload: dict[str, Any]) -> None:
    status = payload["status"]
    if status == "missing":
        print("ADVISORY: nose missing; clone-family inventory skipped. Install per integrations/tools/nose.json.")
        return
    if status == "error":
        print(f"ADVISORY: nose inventory error; review manually. {payload.get('stderr', '')}")
        return
    print(
        f"nose clone advisory: {status}; {payload['family_count']} families, "
        f"{payload['total_dup_lines']} duplicated lines in reported families."
    )
    for index, family in enumerate(payload["families"][:5], start=1):
        samples = ", ".join(
            f"{item['file']}:{item['start_line']}-{item['end_line']}"
            for item in family["sample_locations"][:3]
        )
        print(
            f"ADVISORY: nose family #{index}: members={family['members']} "
            f"dup_lines={family['dup_lines']} shared_lines={family['shared_lines']} "
            f"params={family['params']} samples={samples}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan; repeatable")
    parser.add_argument("--mode", default=DEFAULT_MODE)
    parser.add_argument("--threshold", type=float, default=0.70)
    parser.add_argument("--min-lines", type=int, default=18)
    parser.add_argument("--min-tokens", type=int, default=24)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--sort", default="extractability", choices=("extractability", "value", "sites"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = payload_for_args(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
