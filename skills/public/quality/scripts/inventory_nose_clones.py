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
# nose 0.5 makes --mode REPLACE the default channels (syntax,semantic) rather
# than add to them, so every channel we want must be listed explicitly.
# syntax+semantic+near is a superset of the 0.5 default, so this requests
# strictly more coverage, never less — no silent channel drop under 0.5.
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
    min_size: int,
    top: int,
    sort: str,
) -> list[str]:
    return [
        nose_bin,
        "scan",
        *paths,
        "--mode",
        mode,
        "--min-size",
        str(min_size),
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
            "tool_version": "",
        }
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": f"nose emitted invalid JSON: {exc}; stderr: {completed.stderr.strip()}",
            "families": [],
            "tool_version": "",
        }
    families, tool_version = _extract_families(parsed)
    status = "findings" if families else "clean"
    if completed.returncode != 0:
        status = "error"
    return {
        "status": status,
        "exit_code": completed.returncode,
        "stdout": "",
        "stderr": completed.stderr.strip(),
        "families": families,
        "tool_version": tool_version,
    }


def _extract_families(parsed: Any) -> tuple[list[dict[str, Any]], str]:
    """Return (families, tool_version) across nose 0.4 and 0.5 JSON shapes.

    nose 0.5 emits a top-level object ({"families": [...], "tool_version": ...});
    nose 0.4 emitted a bare top-level array. Reading the 0.5 object as a list
    silently yielded zero families, under-reporting the live scan.
    """
    if isinstance(parsed, dict):
        families = parsed.get("families")
        tool_version = str(parsed.get("tool_version") or "")
    elif isinstance(parsed, list):
        families = parsed
        tool_version = ""
    else:
        families = []
        tool_version = ""
    if not isinstance(families, list):
        families = []
    return [family for family in families if isinstance(family, dict)], tool_version


# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): this inference-layer proxy self-declares
# its blind spots and the question the consumer must answer before acting.
INTERPRETATION = {
    "measures": "lexical clone families (near-duplicate code spans) at/above the scan threshold",
    "proxy_for": "refactorable duplication debt that a shared helper could remove",
    "blind_spots": (
        "intentional per-skill-package boilerplate (e.g. resolve_adapter.py copied "
        "for portability) counts as duplication and inflates the line total; "
        "lexical, so it misses semantic duplication and over-counts deliberate copies"
    ),
    "interpretation_question": (
        "which of these families are intentional/portability boilerplate versus "
        "genuinely extractable debt for THIS repo?"
    ),
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
            "tool_version": "",
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
        min_size=args.min_size,
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
        "tool_version": result.get("tool_version", ""),
        "family_count": len(families),
        "total_dup_lines": sum(int(family.get("dup_lines") or 0) for family in families if isinstance(family, dict)),
        "families": [_family_summary(family) for family in families if isinstance(family, dict)],
        "stderr": result["stderr"],
        "interpretation": dict(INTERPRETATION),
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
    version_label = payload.get("tool_version") or "unknown"
    print(
        f"nose clone advisory (nose {version_label}): {status}; {payload['family_count']} families, "
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
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (inference-layer proxy, not a verdict): "
            f"measures {interpretation['measures']}; proxy for "
            f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
            f"Consumer must answer first: {interpretation['interpretation_question']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan; repeatable")
    parser.add_argument("--mode", default=DEFAULT_MODE)
    parser.add_argument("--min-size", type=int, default=24)
    parser.add_argument("--threshold", type=float, default=0.70, help=argparse.SUPPRESS)
    parser.add_argument("--min-lines", type=int, default=18, help=argparse.SUPPRESS)
    parser.add_argument("--min-tokens", dest="min_size", type=int, help=argparse.SUPPRESS)
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
