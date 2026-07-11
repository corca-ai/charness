#!/usr/bin/env python3
"""Draft duplicate-ratchet triage from a ratchet report and nose inventory.

The helper does not edit dup-review.json. It turns the hard-block payload into a
small review packet with family locations and a conservative suggested action,
so the operator can decide extract vs intentional without re-running ad hoc
inventory commands.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{path}: invalid JSON: {exc}") from exc


def _run_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise RuntimeError(f"{' '.join(cmd)} failed (rc={result.returncode}): {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{' '.join(cmd)} did not emit JSON: {exc}") from exc


def _member_files(family: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for loc in family.get("sample_locations") or []:
        if isinstance(loc, dict) and isinstance(loc.get("file"), str):
            files.append(loc["file"])
    return files


def _same_file(files: list[str]) -> bool:
    return bool(files) and len(set(files)) == 1


def _same_directory(files: list[str]) -> bool:
    dirs = {Path(path).parent.as_posix() for path in files}
    return bool(dirs) and len(dirs) == 1


def _basename_set(files: list[str]) -> set[str]:
    return {Path(path).name for path in files}


def suggest_action(family: dict[str, Any]) -> tuple[str, str]:
    files = _member_files(family)
    basenames = _basename_set(files)
    shared_lines = int(family.get("shared_lines") or 0)
    if _same_file(files):
        return "extract", "all sampled spans are in one file; look for a local helper first"
    if basenames <= {"resolve_adapter.py", "init_adapter.py"}:
        return "intentional", "portable per-skill adapter/bootstrap copies are expected"
    if _same_directory(files) and shared_lines >= 8:
        return "extract", "sampled spans share an owning directory and enough common body"
    if shared_lines <= 5:
        return "intentional", "small idiom-sized span; shared helper may add coupling"
    return "review-needed", "mixed ownership or medium-sized span; inspect before classifying"


def summarize_family(family: dict[str, Any]) -> dict[str, Any]:
    action, reason = suggest_action(family)
    files = _member_files(family)
    identity = family.get("family_fingerprint") or family.get("family_id")
    return {
        "id": identity,
        "suggested_action": action,
        "reason": reason,
        "shared_lines": family.get("shared_lines"),
        "members": family.get("members"),
        "sample_files": files,
        "sample_locations": family.get("sample_locations") or [],
        "draft_dup_review_entry": {
            "surface": "code",
            "id": identity,
            "class": "intentional" if action == "intentional" else "unreviewed",
            "note": reason,
            "reviewed_at": "YYYY-MM-DD",
        },
    }


def _inventory_by_id(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = inventory.get("families") or []
    result: dict[str, dict[str, Any]] = {}
    for family in families:
        if not isinstance(family, dict):
            continue
        for key in ("family_fingerprint", "family_id"):
            value = family.get(key)
            if isinstance(value, str) and value:
                result[value] = family
    return result


def build_report(ratchet: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    by_id = _inventory_by_id(inventory)
    missing: list[str] = []
    families: list[dict[str, Any]] = []
    for family_id in ratchet.get("new_code_families") or []:
        family = by_id.get(family_id)
        if family is None:
            missing.append(family_id)
            continue
        families.append(summarize_family(family))
    return {
        "ok": not missing,
        "ratchet_status": ratchet.get("status"),
        "family_count": len(families),
        "missing_from_inventory": missing,
        "families": families,
        "non_claim": "Suggestions are triage hints only; the operator still owns extraction vs intentional classification.",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft a duplicate-ratchet triage packet.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root used to locate ratchet and inventory inputs.",
    )
    parser.add_argument("--ratchet-report", type=Path, help="Existing check_dup_ratchet --json payload.")
    parser.add_argument("--code-inventory", type=Path, help="Existing inventory_nose_clones --json payload.")
    parser.add_argument("--json", action="store_true", help="Emit the triage packet as JSON.")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    ratchet = _load_json(args.ratchet_report) if args.ratchet_report else _run_json(
        [
            sys.executable,
            str(repo_root / "skills/public/quality/scripts/check_dup_ratchet.py"),
            "--repo-root",
            str(repo_root),
            "--json",
        ]
    )
    inventory = _load_json(args.code_inventory) if args.code_inventory else _run_json(
        [
            sys.executable,
            str(repo_root / "skills/public/quality/scripts/inventory_nose_clones.py"),
            "--repo-root",
            str(repo_root),
            "--json",
            "--top",
            "1000000",
            "--baseline",
            str(repo_root / ".charness/nonexistent-nose-baseline.json"),
        ]
    )
    return build_report(ratchet, inventory)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report: dict[str, Any]
    try:
        report = run(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        lines = [f"dup-ratchet triage: {report['family_count']} family(ies)"]
        lines.extend(
            f"- {family['id']}: {family['suggested_action']} -- {family['reason']}"
            for family in report["families"]
        )
        output = "\n".join(lines)
    print(output)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
