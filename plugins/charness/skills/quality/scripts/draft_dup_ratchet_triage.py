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


def _unsampled_member_count(family: dict[str, Any], files: list[str]) -> int | None:
    """How many of the family's declared members the sampled locations do NOT cover, or
    ``None`` when the record declares no member count.

    ``None`` is NOT zero. Returning 0 for an absent `members` field made a record that
    never said how many members it has indistinguishable from one that is fully sampled,
    and the permissive branch won — the S27 shape again, and the opposite of how the
    sibling field `shared_lines` is treated three lines further down."""
    members = family.get("members")
    if not isinstance(members, int) or isinstance(members, bool):
        return None
    return max(0, members - len(files))


def suggest_action(family: dict[str, Any]) -> tuple[str, str]:
    """Suggested triage action for one inventory family record.

    Every branch here must rest on evidence the record actually carries. An empty
    `sample_locations` made `basenames <= {adapter copies}` vacuously true and an absent
    `shared_lines` coerced to 0 made the small-idiom branch fire, so a family with NO
    established evidence was suggested `intentional` — the one class that writes a
    permanent accept into dup-review.json (triage sweep S27). Absent evidence is now
    `review-needed`, which drafts as `unreviewed`.
    """
    files = _member_files(family)
    basenames = _basename_set(files)
    shared_lines = family.get("shared_lines")
    if not isinstance(shared_lines, int) or isinstance(shared_lines, bool):
        shared_lines = None
    if not files:
        return "review-needed", "no sampled member locations in the inventory record; inspect the family before classifying"
    if _same_file(files):
        return "extract", "all sampled spans are in one file; look for a local helper first"
    if basenames <= {"resolve_adapter.py", "init_adapter.py"}:
        # `sample_locations` is capped at 6 by nose_report_lib.family_summary, so on a
        # larger family this subset rules on 6 of N members. Suggesting the permanent
        # accept from a truncated member set is the same unestablished-scope call as
        # suggesting it from an empty one.
        unsampled = _unsampled_member_count(family, files)
        if unsampled is None:
            return "review-needed", (
                "the sampled spans are portable adapter copies but the inventory record does not say how "
                f"many members this family has, so the {len(files)} sampled ones establish no coverage; "
                "confirm the member set before classifying"
            )
        if unsampled:
            return "review-needed", (
                f"the inventory record samples only {len(files)} of {len(files) + unsampled} members and the "
                "sampled ones are portable adapter copies; confirm the unsampled members before classifying"
            )
        return "intentional", "portable per-skill adapter/bootstrap copies are expected"
    if shared_lines is None:
        return "review-needed", "the inventory record carries no shared_lines span size; inspect the family before classifying"
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


def _named_families(ratchet: dict[str, Any], inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """Inventory records for the families an unestablished ratchet payload still named."""
    by_id = _inventory_by_id(inventory)
    named = ratchet.get("new_code_families")
    if not isinstance(named, list):
        return []
    return [by_id[family_id] for family_id in named if family_id in by_id]


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


UNEVALUATED_RATCHET_STATUSES = frozenset({"adapter-invalid", "inert", "write-baseline-failed", "baseline-written"})


def unestablished_ratchet_reason(ratchet: dict[str, Any]) -> str | None:
    """Why this ratchet payload's code-family set is not established, else ``None``.

    A payload that never evaluated the gate (invalid adapter, inert, a rebaseline-mode run)
    carries no `new_code_families` list, and `... or []` turned that into "0 families to
    triage" with ok/exit 0 — "nothing to triage" claimed over a gate that could not judge.
    `_run_json` accepts exit 1, so this is reachable in practice.

    A DEGRADED payload is the same claim one step subtler, and it is the shape this
    subsystem now produces most: every code-arm degrade (unreadable inventory, unrecognized
    nose report, non-scan status) leaves `evaluate` with an empty live id set, so the
    verdict carries `new_code_families: []` with `status: "degraded"`, `ok: true`, exit 0.
    The gate is right to treat that as advisory — it must never false-block — but this
    drafter is a WRITER: its output drafts a permanent `intentional` accept, so reading a
    degraded gate as "no new families" is the writing-side harm.
    """
    status = ratchet.get("status")
    if status in UNEVALUATED_RATCHET_STATUSES:
        return (f"the ratchet report never evaluated the gate (status={status!r}); nothing was "
                "triaged because the gate rendered no family set")
    if not isinstance(ratchet.get("new_code_families"), list):
        return (f"the ratchet report declares no new_code_families list (status={status!r}); "
                "nothing was triaged because the gate rendered no family set")
    degraded_reasons = ratchet.get("degraded_reasons")
    if isinstance(degraded_reasons, list) and degraded_reasons:
        joined = "; ".join(str(reason) for reason in degraded_reasons)
        return (f"the ratchet report is DEGRADED ({joined}); its code family set is unestablished, "
                "so this packet is not evidence that there is nothing to triage")
    return None


def build_report(ratchet: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    unestablished = unestablished_ratchet_reason(ratchet)
    if unestablished:
        return {
            "ok": False,
            "ratchet_status": ratchet.get("status"),
            "family_count": 0,
            "missing_from_inventory": [],
            # Whatever the degraded payload DID name is still listed, so the refusal hides
            # nothing the operator could have acted on.
            "families": [summarize_family(family) for family in _named_families(ratchet, inventory)],
            "unestablished_reason": unestablished,
            "non_claim": "Suggestions are triage hints only; the operator still owns extraction vs intentional classification.",
        }
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
        if report.get("unestablished_reason"):
            lines.append(f"REFUSED: {report['unestablished_reason']}")
        lines.extend(
            f"- {family['id']}: {family['suggested_action']} -- {family['reason']}"
            for family in report["families"]
        )
        output = "\n".join(lines)
    print(output)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
