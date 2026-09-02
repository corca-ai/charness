#!/usr/bin/env python3
"""Draft duplicate-ratchet triage from a ratchet report and nose inventory.

The helper does not edit dup-review.json. It turns the hard-block payload into a
small review packet with family locations and a conservative suggested action,
so the operator can decide extract vs intentional without re-running ad hoc
inventory commands.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import runpy
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import emit_yaml  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()


def _load_detail(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    return _parse_detail_payload(raw.decode("utf-8"), str(path))


def _run_detail(script: Path, argv: list[str]) -> dict[str, Any]:
    module = SKILL_RUNTIME.load_local_skill_module(__file__, script.stem)
    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_argv = sys.argv
    try:
        sys.argv = [str(script), *argv]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                returncode = (
                    module.main(argv) if script.stem == "check_dup_ratchet" else module.main()
                )
            except SystemExit as exc:
                returncode = exc.code if isinstance(exc.code, int) else 1
            except Exception:
                traceback.print_exc()
                returncode = 1
    finally:
        sys.argv = previous_argv
    if returncode not in (0, 1):
        raise RuntimeError(f"{script} failed (rc={returncode}): {stderr.getvalue().strip()}")
    return _parse_detail_payload(stdout.getvalue(), " ".join([str(script), *argv]))


def _parse_detail_payload(text: str, source: str) -> dict[str, Any]:
    """Read one `--detail` payload -- JSON fast path first, then YAML.

    Both producers emit YAML through `scripts/yaml_output.render_yaml`, which
    falls back to COMPACT JSON when PyYAML is missing. JSON is valid YAML, so the
    JSON attempt is the cheaper path AND the only one available when PyYAML is
    absent -- which is the same interpreter question for both sides here, since
    these producers run under `sys.executable`.

    This function is why the `--json` -> `--detail` fix is three coupled edits and
    not one. The flag, the parser, and the `--ratchet-report` / `--code-inventory`
    help text all named the same removed mode; migrating the flag alone would have
    turned an exit-2 into a silent JSONDecodeError on YAML, and left an operator
    saving `check_dup_ratchet.py --detail` to a file with a reader that rejects it.

    A YAML payload with no PyYAML to read it is named as such: a clear remedy
    beats a parse traceback from a helper that already handles the JSON case.
    """
    payload: Any
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                f"{source} emitted a YAML `--detail` payload and PyYAML is not importable here; "
                "install PyYAML in this interpreter to read it"
            ) from exc
        try:
            payload = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise RuntimeError(f"{source}: unreadable `--detail` payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{source}: `--detail` payload is not a mapping")
    return payload


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
        return (
            "review-needed",
            "no sampled member locations in the inventory record; inspect the family before classifying",
        )
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
        return (
            "review-needed",
            "the inventory record carries no shared_lines span size; inspect the family before classifying",
        )
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


UNEVALUATED_RATCHET_STATUSES = frozenset(
    {"adapter-invalid", "inert", "write-baseline-failed", "baseline-written"}
)


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
        return (
            f"the ratchet report never evaluated the gate (status={status!r}); nothing was "
            "triaged because the gate rendered no family set"
        )
    if not isinstance(ratchet.get("new_code_families"), list):
        return (
            f"the ratchet report declares no new_code_families list (status={status!r}); "
            "nothing was triaged because the gate rendered no family set"
        )
    degraded_reasons = ratchet.get("degraded_reasons")
    if isinstance(degraded_reasons, list) and degraded_reasons:
        joined = "; ".join(str(reason) for reason in degraded_reasons)
        return (
            f"the ratchet report is DEGRADED ({joined}); its code family set is unestablished, "
            "so this packet is not evidence that there is nothing to triage"
        )
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
            "families": [
                summarize_family(family) for family in _named_families(ratchet, inventory)
            ],
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
    parser.add_argument(
        "--ratchet-report", type=Path, help="Existing check_dup_ratchet --detail payload."
    )
    parser.add_argument(
        "--code-inventory", type=Path, help="Existing inventory_nose_clones --detail payload."
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    ratchet_script = repo_root / "skills/public/quality/scripts/check_dup_ratchet.py"
    inventory_script = repo_root / "skills/public/quality/scripts/inventory_nose_clones.py"
    ratchet = (
        _load_detail(args.ratchet_report)
        if args.ratchet_report
        else _run_detail(ratchet_script, ["--repo-root", str(repo_root), "--detail"])
    )
    inventory = (
        _load_detail(args.code_inventory)
        if args.code_inventory
        else _run_detail(
            inventory_script,
            [
                "--repo-root",
                str(repo_root),
                "--detail",
                "--top",
                "1000000",
                "--baseline",
                str(repo_root / ".charness/nonexistent-nose-baseline.json"),
            ],
        )
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
    emit_yaml(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
